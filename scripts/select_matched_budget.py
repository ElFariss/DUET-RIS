"""Freeze the protocol's primary budget using its locked validation fallback rule.

The protocol's preferred budget and locked primary may differ after a previously
declared fallback. The primary remains selected when feasible; otherwise the first
feasible larger listed budget is selected. No feasible budget means infeasibility
is reported and no speed claim may be made.

Also hosts the small provenance helpers shared with the benchmark scripts.
"""
import argparse
import datetime
import hashlib
import json
import os
import platform
from pathlib import Path
import itertools

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'configs' / 'experiments' / 'matched_v1.json'
CANDIDATES = (10, 50, 100)
# Files whose content defines the method under test. Data-preparation scripts and analysis are excluded on purpose.
CODE_GLOBS = ('src/atomwise_ris/**/*.py', 'scripts/benchmark.py', 'scripts/benchmark_coupled.py',
              'configs/experiments/matched_v1.json', 'configs/experiments/coupled_wire_v1.json')
EXPERIMENT_INPUT = {'specular': 'benchmark_validation.jsonl', 'coupled': 'benchmark_spatial_validation.jsonl'}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_protocol(path=None):
    p = Path(path) if path else PROTOCOL
    return json.loads(p.read_text()), sha256_file(p)


def protocol_methods(protocol):
    m = protocol['methods']
    return list(m['baselines']) + [k for k in m if k != 'baselines']


def frozen_code_hashes(root=ROOT):
    files = sorted({p for g in CODE_GLOBS for p in Path(root).glob(g) if '__pycache__' not in p.parts})
    return {str(p.relative_to(root)): sha256_file(p) for p in files}


def checkpoint_hashes(run):
    run = Path(run)
    files = sorted(run.glob('models/*/best.pt')) + sorted(run.glob('models/*/scaling.npz'))
    if (run / 'feature_scaling.npz').exists():
        files.append(run / 'feature_scaling.npz')
    return {str(p.relative_to(run)): sha256_file(p) for p in files}


def host_state():
    try:
        load = list(os.getloadavg())
    except OSError:
        load = None
    return {'hostname': platform.node(), 'loadavg_1_5_15': load}


def feasibility(rows, methods, budgets=(1, 5, 10, 50, 100)):
    """Per budget: deadline misses per method, coverage, and whether every method is miss-free."""
    out = {}
    for budget in budgets:
        sel = [r for r in rows if r['budget_ms'] == budget]
        counts = {m: sum(bool(r['deadline_missed']) for r in sel if r['method'] == m) for m in methods}
        rows_per = {m: sum(r['method'] == m for r in sel) for m in methods}
        complete = len(set(rows_per.values())) == 1 and min(rows_per.values()) > 0
        out[str(budget)] = {'misses_by_method': counts, 'rows_by_method': rows_per, 'complete_coverage': complete,
                            'feasible': complete and all(v == 0 for v in counts.values())}
    return out


def choose(feasible):
    return next((b for b in CANDIDATES if feasible[str(b)]['feasible']), None)


def selection_rule_text(preferred_budget, primary_budget, budgets):
    preferred=float(preferred_budget);primary=float(primary_budget)
    larger=sorted(float(b) for b in budgets if float(b)>primary)
    suffix=', '.join(f'{b:g} ms' for b in larger) or 'none'
    if preferred==primary:
        return (f'Preferred and primary budget is {primary:g} ms; select it when every method is miss-free, '
                f'otherwise select the first feasible larger listed budget ({suffix}). No feasible budget means no speed claim.')
    return (f'Preferred budget {preferred:g} ms is recorded; locked primary budget {primary:g} ms preserves the '
            f'previously declared fallback decision. Select the locked primary when every method is miss-free, '
            f'otherwise select the first feasible larger listed budget ({suffix}). Lower budgets remain secondary; '
            'no feasible budget means no speed claim.')


_UNSET = object()

def validate_exact_validation_grid(rows, methods, seeds, budgets, expected_indices,
                                   primary_budget, selected_budget=_UNSET):
    """Validate every exact frame cell, then apply the predeclared primary/fallback rule.

    The primary is preferred when feasible. Otherwise choose the first feasible
    listed budget above it. Deadline misses at the primary remain in the input
    rows and are recorded in the returned feasibility map.
    """
    expected = set(map(int, expected_indices))
    methods = tuple(methods); seeds = tuple(map(int, seeds)); budgets = tuple(map(float, budgets))
    if not expected or not methods or not seeds or not budgets:
        raise RuntimeError('Validation freeze requires nonempty methods, seeds, budgets, and frame indices')
    grouped = {key: [] for key in itertools.product(methods, seeds, budgets)}
    for row in rows:
        if row.get('split') != 'validation' or row.get('search_config') != 'medium':
            raise RuntimeError('Validation freeze includes non-validation or non-primary-config rows')
        if row.get('conditional_pair_policy', False):
            raise RuntimeError('Conditional-pair development rows cannot freeze the registered test protocol')
        try:
            key = (row['method'], int(row['seed']), float(row['budget_ms']))
            index = int(row['index'])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError('Validation freeze contains a malformed method/seed/budget/frame row') from exc
        if key not in grouped:
            raise RuntimeError(f'Validation freeze contains an unregistered method/seed/budget: {key}')
        grouped[key].append(index)
    for key, indices in grouped.items():
        if len(indices) != len(expected) or set(indices) != expected:
            raise RuntimeError(f'Validation freeze requires every exact frame once for {key}')

    feasibility = {}
    for budget in budgets:
        misses = {m: sum(bool(row.get('deadline_missed')) for row in rows
                         if row['method'] == m and float(row['budget_ms']) == budget)
                  for m in methods}
        feasibility[str(float(budget))] = {
            'rows_by_method': {m: sum(len(grouped[(m, seed, budget)]) for seed in seeds) for m in methods},
            'misses_by_method': misses,
            'complete_coverage': True,
            'complete': True,
            'feasible': all(value == 0 for value in misses.values()),
        }
    primary = float(primary_budget)
    if primary not in budgets:
        raise RuntimeError('Configured primary budget is absent from the validation grid')
    order = [primary] + sorted(b for b in budgets if b > primary)
    chosen = next((b for b in order if feasibility[str(float(b))]['feasible']), None)
    if selected_budget is not _UNSET:
        supplied = None if selected_budget is None else float(selected_budget)
        if supplied != chosen:
            raise RuntimeError(f'Frozen selected budget {supplied} does not match validation rule result {chosen}')
    return chosen, feasibility


def require_frozen_selection(run, root=ROOT):
    """Raise unless a feasible budget was frozen and the code and checkpoints are unchanged since."""
    path = Path(run) / 'budget_selection.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} missing: freeze the validation budget before the test benchmark')
    sel = json.loads(path.read_text())
    if sel.get('selected_ms') is None:
        raise RuntimeError('No feasible validation budget was frozen; report infeasibility, do not run a speed claim')
    for name, now in (('code_sha256', frozen_code_hashes(root)), ('checkpoint_sha256', checkpoint_hashes(run))):
        if sel.get(name) != now:
            changed = sorted(set(sel.get(name, {})) ^ set(now) | {k for k in now if sel.get(name, {}).get(k) != now[k]})
            raise RuntimeError(f'{name} differs from the frozen selection: {changed[:5]}')
    return sel


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--experiment', choices=['specular', 'coupled'], required=True)
    p.add_argument('--protocol', default=str(PROTOCOL))
    p.add_argument('--run', default=None)
    p.add_argument('--input', default=None, help='validation benchmark JSONL; default depends on experiment')
    p.add_argument('--data', default=None, help='train/validation dataset used to verify the complete frame grid')
    a = p.parse_args()
    protocol, protocol_hash = load_protocol(a.protocol)
    run = Path(a.run or protocol['experiments'][a.experiment]['run'])
    src = run / (a.input or EXPERIMENT_INPUT[a.experiment])
    rows = [json.loads(line) for line in src.read_text().splitlines()]
    if not rows:
        raise ValueError('Empty validation benchmark')
    if any(r['split'] != 'validation' for r in rows):
        raise ValueError('Budget selection uses the validation split only')
    if any(r.get('search_config', 'medium') != 'medium' for r in rows):
        raise ValueError('Budget selection uses the primary (medium) search configuration only')
    methods = protocol_methods(protocol)
    data = Path(a.data or ('data/processed/munich_specular_v3/scenario.npz' if a.experiment == 'specular'
                           else 'data/processed/coupled_wire_v1/dataset.npz'))
    import numpy as np
    with np.load(data, allow_pickle=False) as frames:
        if 'split' not in frames:
            raise ValueError(f'Validation dataset has no split field: {data}')
        expected_indices = np.flatnonzero(frames['split'] == 'validation')
    chosen, feasible = validate_exact_validation_grid(rows, methods, protocol['seeds'],
        protocol['budgets_ms'], expected_indices, protocol['primary_budget_ms'])
    preferred=float(protocol.get('preferred_budget_ms',protocol['primary_budget_ms']))
    out = run / 'budget_selection.json'
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps({
        'experiment': a.experiment, 'selected_ms': chosen, 'protocol_primary_ms': protocol['primary_budget_ms'],
        'protocol_preferred_ms': preferred,
        'budget_lock': protocol.get('budget_lock'),
        'validation_feasibility': feasible,
        'rule': selection_rule_text(preferred,protocol['primary_budget_ms'],protocol['budgets_ms']),
        'protocol_sha256': protocol_hash, 'input_hashes': {src.name: sha256_file(src)},
        'code_sha256': frozen_code_hashes(), 'checkpoint_sha256': checkpoint_hashes(run),
        'frozen_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), **host_state()}, indent=2) + '\n')
    print('Primary budget', chosen)


if __name__ == '__main__':
    main()
