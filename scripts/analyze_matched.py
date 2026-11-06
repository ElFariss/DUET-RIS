"""Metrics and statistics of the registered matched protocol (configs/experiments/matched_v1.json).

Reads a matched benchmark JSONL and writes summary.json, summary.csv and REPORT.md into the run
directory. Nothing here is tuned: margins, seeds, resamples and contrasts come from the protocol.

Time to target: a run reaches the target at the first trace point whose value is within
`target_margin` of the frame reference (best rate on that frame by any method, seed and budget in
the analysed file). The preparation time that precedes the search (scenario/network setup) is
added so that the figure is on the same clock as the complete runtime.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from select_matched_budget import load_protocol, protocol_methods, EXPERIMENT_INPUT

PREP_KEYS = ('scenario_preparation', 'preparation_ms')
LIMITS = ['Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.',
          'memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.',
          'Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.',
          'Spatial control only; temporal forecasting is out of scope for this comparison.']


def load_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def prep_ms(row):
    b = row.get('breakdown_ms', {})
    return next((float(b[k]) for k in PREP_KEYS if k in b), 0.)


def frame_references(rows):
    ref = {}
    for r in rows:
        k = r['index']
        ref[k] = max(ref.get(k, -np.inf), r['rate'])
    return ref


def target_hit(row, ref, margin):
    """(time_ms, evaluations) at first trace point within `margin` of ref, else None."""
    for point in row['trace']:
        if len(point) < 3:
            raise ValueError('Trace lacks the evaluation count (third element); rerun with the matched benchmark scripts')
        if point[1] >= ref - margin:
            return prep_ms(row) + point[0], point[2]
    return None


def cell_metrics(rows, ref, margin):
    hits = [target_hit(r, ref[r['index']], margin) for r in rows]
    reached = [h for h in hits if h is not None]
    q = lambda v, p: float(np.percentile(v, p)) if len(v) else None
    return {'n_runs': len(rows), 'rate_mean': float(np.mean([r['rate'] for r in rows])),
            'p95_elapsed_ms': q([r['elapsed_ms'] for r in rows], 95),
            'time_to_target_median_ms': q([h[0] for h in reached], 50), 'time_to_target_p95_ms': q([h[0] for h in reached], 95),
            'target_reached_fraction': len(reached) / len(rows),
            'evaluations_mean': float(np.mean([r['evaluations'] for r in rows])),
            'evaluations_to_target_mean': float(np.mean([h[1] for h in reached])) if reached else None,
            'evaluations_to_target_median': q([h[1] for h in reached], 50),
            'deadline_misses': int(sum(bool(r['deadline_missed']) for r in rows)),
            'deadline_miss_fraction': float(np.mean([bool(r['deadline_missed']) for r in rows]))}


def trajectory_means(rows):
    """Mean rate per trajectory (seeds and frames averaged within trajectory)."""
    acc = defaultdict(list)
    for r in rows:
        acc[r['trajectory']].append(r['rate'])
    return {t: float(np.mean(v)) for t, v in acc.items()}


def holm(p):
    """Holm step-down adjusted p-values, returned in input order."""
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty(len(p))
    running = 0.
    for rank, i in enumerate(order):
        running = max(running, min(1., (len(p) - rank) * p[i]))
        adj[i] = running
    return adj


def decide(lo, hi, margin):
    if lo > margin:
        return 'improved'
    if lo >= -margin and hi <= margin:
        return 'equivalent'
    return 'inconclusive'


def contrast_statistics(per_method, contrasts, seed, resamples, margin, alpha=0.05):
    """Paired trajectory bootstrap with Bonferroni simultaneous CIs and separate Holm p-values.

    The CI family is Bonferroni over contrasts (two-sided percentile limits at alpha/M).
    The two-sided null-of-zero p-values use the centered bootstrap error distribution and
    are Holm-adjusted separately. Decisions use only the simultaneous CI and practical
    margin; a Holm p-value is never converted into a confidence interval.
    """
    names = [c.replace(' ', '').split('-') for c in contrasts]
    trajs = sorted(set.intersection(*[set(per_method[m]) for pair in names for m in pair]))
    if not trajs:
        raise ValueError('No trajectories shared by the contrast methods')
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(trajs), (resamples, len(trajs)))
    out = []
    for c, (a, b) in zip(contrasts, names):
        d = np.array([per_method[a][t] - per_method[b][t] for t in trajs])
        boots = d[idx].mean(axis=1)
        estimate = float(d.mean())
        errors = boots - estimate
        # Centered bootstrap null test for a zero mean difference.
        tail_lo = (np.sum(errors <= -abs(estimate)) + 1) / (resamples + 1)
        tail_hi = (np.sum(errors >= abs(estimate)) + 1) / (resamples + 1)
        out.append({'contrast': c, 'difference': estimate, 'n_trajectories': len(trajs),
                    'p_value_zero_centered_bootstrap': float(min(1., 2 * min(tail_lo, tail_hi))),
                    '_boots': boots})
    adjusted = holm([o['p_value_zero_centered_bootstrap'] for o in out])
    ci_alpha = alpha / len(out)
    for o, p_holm in zip(out, adjusted):
        boots = o.pop('_boots')
        lo, hi = np.percentile(boots, [100 * ci_alpha / 2, 100 * (1 - ci_alpha / 2)])
        improved, deteriorated = lo > margin, hi < -margin
        equivalent = lo >= -margin and hi <= margin
        decision = ('improved' if improved else 'deteriorated' if deteriorated else
                    'equivalent' if equivalent else 'inconclusive')
        o.update({'interval_bonferroni_simultaneous': [float(lo), float(hi)],
                  'simultaneous_ci_family_alpha': alpha, 'simultaneous_ci_contrast_count': len(out),
                  'p_holm_zero': float(p_holm), 'practical_margin': margin, 'decision': decision})
    return out


def analyse(rows, protocol, budget_ms, search_config='medium', experiment='specular', protocol_hash=None, mesh_audit=None):
    methods = protocol_methods(protocol)
    missing_methods = sorted(set(methods) - {r['method'] for r in rows})
    if missing_methods:
        raise ValueError(f'Benchmark is missing protocol methods: {missing_methods}')
    margin = protocol['statistics'].get('practical_margin_by_experiment', {}).get(experiment, {}).get(
        'bit_s_hz', protocol['statistics']['practical_margin_bit_s_hz'])
    ref = frame_references(rows)
    budgets = sorted({r['budget_ms'] for r in rows})
    cells = []
    for b in budgets:
        for m in methods:
            sel = [r for r in rows if r['method'] == m and r['budget_ms'] == b]
            if sel:
                cells.append({'method': m, 'budget_ms': b, **cell_metrics(sel, ref, margin)})
    st = protocol['statistics']
    primary = [r for r in rows if r['budget_ms'] == budget_ms]
    if not primary:
        raise ValueError(f'No rows at primary budget {budget_ms} ms')
    per_method = {m: trajectory_means([r for r in primary if r['method'] == m]) for m in methods}
    needed = {m for c in st['contrasts'] for m in c.replace(' ', '').split('-')}
    missing = needed - set(per_method)
    if missing:
        raise ValueError(f'Methods missing for contrasts: {sorted(missing)}')
    contrasts = contrast_statistics(per_method, st['contrasts'], st['interval']['seed'], st['interval']['resamples'],
                                    margin, st.get('familywise_alpha', 0.05))
    mesh_ok = None
    if experiment == 'coupled' and mesh_audit is not None:
        required = ('protocol_sha256', 'preselected_before_test_evaluation', 'split', 'segment_count_coarse',
                    'segment_count_fine', 'audited_action_count', 'rate_difference_abs_max_bit_s_hz',
                    'resolution_criterion_bit_s_hz', 'criterion_passed')
        if any(k not in mesh_audit for k in required):
            raise ValueError(f'mesh audit missing required fields: {required}')
        if (mesh_audit['protocol_sha256'] != protocol_hash or mesh_audit['preselected_before_test_evaluation'] is not True or
                mesh_audit['split'] != 'test' or mesh_audit['segment_count_coarse'] != 81 or
                mesh_audit['segment_count_fine'] != 161 or mesh_audit['audited_action_count'] != len(primary)):
            raise ValueError('mesh audit provenance, mesh sizes, or action count does not match the primary test rows')
        delta, criterion = mesh_audit['rate_difference_abs_max_bit_s_hz'], mesh_audit['resolution_criterion_bit_s_hz']
        if (not isinstance(delta, (int, float)) or not isinstance(criterion, (int, float)) or
                not np.isfinite(delta) or not np.isfinite(criterion) or delta < 0 or criterion <= 0):
            raise ValueError('mesh audit requires finite nonnegative maximum error and positive predeclared criterion')
        mesh_ok = delta <= criterion and mesh_audit['criterion_passed'] is True
    if experiment == 'coupled' and not mesh_ok:
        for c in contrasts:
            if c['decision'] == 'improved':
                c['statistical_decision_before_mesh_audit'] = 'improved'
                c['decision'] = 'numerically_unresolved'
    return {'experiment_scope': LIMITS, 'search_config': search_config, 'primary_budget_ms': budget_ms,
            'target_margin_bit_s_hz': margin, 'mesh_audit_passed': mesh_ok, 'n_rows': len(rows), 'n_frames': len(ref),
            'n_trajectories': len({r['trajectory'] for r in rows}), 'methods': methods, 'cells': cells, 'contrasts': contrasts}


def write_csv(path, cells):
    with open(path, 'x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0]))
        w.writeheader()
        w.writerows(cells)


def fmt(x, nd=4):
    return '-' if x is None else f'{x:.{nd}f}'


def write_report(path, s, meta):
    L = [f"# Matched comparison report ({meta['experiment']}, {meta['split']}, search config {s['search_config']})", '',
         '## Scope and limits', ''] + [f'- {x}' for x in LIMITS] + ['',
         f"Primary budget: {s['primary_budget_ms']:g} ms. Frames: {s['n_frames']}; trajectories: {s['n_trajectories']}; runs: {s['n_rows']}. "
         f"Target margin {s['target_margin_bit_s_hz']} bit/s/Hz. Protocol sha256 {meta['protocol_sha256'][:16]}.", '',
         '## Primary budget', '', '| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |',
         '|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in s['cells']:
        if c['budget_ms'] == s['primary_budget_ms']:
            L.append(f"| {c['method']} | {c['rate_mean']:.5f} | {fmt(c['p95_elapsed_ms'], 3)} | {fmt(c['time_to_target_median_ms'], 3)} / {fmt(c['time_to_target_p95_ms'], 3)} | "
                     f"{c['target_reached_fraction']:.3f} | {c['evaluations_mean']:.1f} | {fmt(c['evaluations_to_target_mean'], 1)} | {c['deadline_misses']}/{c['n_runs']} |")
    L += ['', '## Contrasts (primary budget, rate)', '',
          'Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin '
          f"{s['contrasts'][0]['practical_margin']} bit/s/Hz.", '',
          '| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |', '|---|---:|---|---:|---|']
    for c in s['contrasts']:
        lo, hi = c['interval_bonferroni_simultaneous']
        L.append(f"| {c['contrast']} | {c['difference']:.5f} | [{lo:.5f}, {hi:.5f}] | {c['p_holm_zero']:.4f} | {c['decision']} |")
    L += ['', 'Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.',
          '', '## All budgets', '', '| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |', '|---|---:|---:|---:|---:|---:|---:|']
    for c in s['cells']:
        L.append(f"| {c['method']} | {c['budget_ms']:g} | {c['rate_mean']:.5f} | {fmt(c['p95_elapsed_ms'], 3)} | {c['target_reached_fraction']:.3f} | {c['evaluations_mean']:.1f} | {c['deadline_misses']}/{c['n_runs']} |")
    Path(path).write_text('\n'.join(L) + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--experiment', choices=['specular', 'coupled'], required=True)
    p.add_argument('--protocol', default='configs/experiments/matched_v1.json')
    p.add_argument('--run', default=None)
    p.add_argument('--input', default=None, help='benchmark JSONL inside the run dir (default: the validation file; pass the test file explicitly)')
    p.add_argument('--budget', type=float, default=None, help='primary budget; default: frozen budget_selection.json, else the protocol primary')
    p.add_argument('--tag', default=None, help='suffix for the output files, e.g. test or validation_small')
    p.add_argument('--mesh-audit', default=None, help='preselected coupled test returned-action fine-mesh audit JSON')
    a = p.parse_args()
    protocol, protocol_hash = load_protocol(a.protocol)
    run = Path(a.run or protocol['experiments'][a.experiment]['run'])
    src = run / (a.input or EXPERIMENT_INPUT[a.experiment])
    rows = load_rows(src)
    splits = {r['split'] for r in rows}
    configs = {r.get('search_config', 'medium') for r in rows}
    if len(splits) != 1 or len(configs) != 1:
        raise ValueError(f'Mixed splits/configs in input: {splits} {configs}')
    budget = a.budget
    if budget is None:
        sel = run / 'budget_selection.json'
        budget = json.loads(sel.read_text())['selected_ms'] if sel.exists() else protocol['primary_budget_ms']
        if budget is None:
            raise RuntimeError('Frozen selection found no feasible budget: report infeasibility, no speed claim')
    audit = json.loads(Path(a.mesh_audit).read_text()) if a.mesh_audit else None
    s = analyse(rows, protocol, float(budget), configs.pop(), a.experiment, protocol_hash, audit)
    tag = f'_{a.tag}' if a.tag else ''
    meta = {'experiment': a.experiment, 'split': splits.pop(), 'protocol_sha256': protocol_hash, 'input': src.name}
    s['meta'] = meta
    out_json, out_csv, out_md = run / f'summary{tag}.json', run / f'summary{tag}.csv', run / f'REPORT{tag}.md'
    for o in (out_json, out_csv, out_md):
        if o.exists():
            raise FileExistsError(f'{o} exists; choose a new --tag')
    out_json.write_text(json.dumps(s, indent=2) + '\n')
    write_csv(out_csv, s['cells'])
    write_report(out_md, s, meta)
    print(f'Wrote {out_json.name}, {out_csv.name}, {out_md.name}')


if __name__ == '__main__':
    main()
