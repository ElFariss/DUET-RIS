"""Restart-safe, split-gated runner for the matched RIS improvement campaign.

This orchestration layer writes each (config, budget, seed) benchmark to a
separate immutable result pair. A completed unit is skipped on restart; partial
JSONL units are preserved and must be resumed/reviewed manually, never replaced.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from select_matched_budget import (load_protocol, protocol_methods, sha256_file,
                                   frozen_code_hashes, checkpoint_hashes,
                                   validate_exact_validation_grid,selection_rule_text)


def atomic_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def parse_csv(text, cast):
    return [cast(x.strip()) for x in text.split(',') if x.strip()]


_SELECTION_UNSPECIFIED = object()

def validate_validation_rows(rows, methods, seeds, budgets, expected_indices, primary_budget,
                             selected_budget=_SELECTION_UNSPECIFIED):
    """Validate the exact validation grid and, when supplied, its selected fallback."""
    if selected_budget is _SELECTION_UNSPECIFIED:
        return validate_exact_validation_grid(rows, methods, seeds, budgets, expected_indices, primary_budget)
    return validate_exact_validation_grid(rows, methods, seeds, budgets, expected_indices,
                                          primary_budget, selected_budget=selected_budget)


def campaign_source_identity(experiment, protocol_hash, data, artifact_root, response=None, physics_gate=None):
    identity = {'protocol_sha256': protocol_hash, 'data_sha256': sha256_file(data), 'experiment': experiment,
                'artifact_root': str(Path(artifact_root).resolve()), 'python': sys.version,
                'code_sha256': frozen_code_hashes(), 'checkpoint_sha256': checkpoint_hashes(artifact_root),
                'campaign_script_sha256': sha256_file(Path(__file__)),
                'selection_helper_sha256': sha256_file(ROOT/'scripts'/'select_matched_budget.py')}
    if response: identity['response_sha256'] = sha256_file(response)
    if physics_gate: identity['physics_gate_sha256'] = sha256_file(physics_gate)
    return identity


def unit_sidecar_matches(sidecar, identity):
    expected_data_key = 'scenario_sha256' if identity['experiment'] == 'specular' else 'data_sha256'
    checks = {'protocol_sha256': identity['protocol_sha256'],
              'frozen_code_sha256': identity['code_sha256'],
              'checkpoint_sha256': identity['checkpoint_sha256'],
              expected_data_key: identity['data_sha256']}
    if 'response_sha256' in identity: checks['response_sha256'] = identity['response_sha256']
    if 'physics_gate_sha256' in identity: checks['physics_gate_sha256'] = identity['physics_gate_sha256']
    checks['selection_helper_sha256'] = identity['selection_helper_sha256']
    checks['campaign_script_sha256'] = identity['campaign_script_sha256']
    checks['conditional_pair_policy'] = identity.get('conditional_pair_policy', False)
    return all(sidecar.get(key) == value for key, value in checks.items())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', choices=['specular', 'coupled'], required=True)
    p.add_argument('--stage', choices=['validation', 'development', 'test'], default='validation')
    p.add_argument('--protocol', default='configs/experiments/matched_v1.json')
    p.add_argument('--run', help='artifact/checkpoint root; defaults to the protocol run')
    p.add_argument('--data', help='train/validation dataset; defaults to the protocol dataset')
    p.add_argument('--response', default='data/processed/responses/opensourceris_v1.csv')
    p.add_argument('--physics-gate')
    p.add_argument('--test-data', help='required only for explicit --stage test')
    p.add_argument('--freeze', help='validation freeze JSON; required before development or test')
    p.add_argument('--out', required=True, help='new campaign directory, or existing directory with --resume')
    p.add_argument('--resume', action='store_true')
    p.add_argument('--configs', default='medium', help='validation only: comma-separated small,medium,large')
    p.add_argument('--seeds', default='7,19,43')
    p.add_argument('--budgets', default='5,10,50')
    p.add_argument('--limit', type=int, default=0, help='validation/development smoke limit; forbidden for test')
    p.add_argument('--conditional-pair-policy', action='store_true',
                   help='development-only paired first-action policy; never eligible for test selection')
    a = p.parse_args()
    protocol, phash = load_protocol(a.protocol)
    exp = protocol['experiments'][a.experiment]
    artifact_root = Path(a.run or exp['run'])
    data = a.data or ('data/processed/munich_specular_v3/scenario.npz' if a.experiment == 'specular' else 'data/processed/coupled_wire_v1/dataset.npz')
    gate_path = (Path(a.physics_gate) if a.physics_gate else
                 artifact_root/'physics_gate.json' if (artifact_root/'physics_gate.json').exists() else
                 Path('outputs/runs/coupled_wire_v1/physics_gate.json'))
    source = campaign_source_identity(a.experiment, phash, data, artifact_root,
                                      response=a.response if a.experiment == 'specular' else None,
                                      physics_gate=gate_path if a.experiment == 'coupled' else None)
    source['protocol_path'] = str(Path(a.protocol))
    source['conditional_pair_policy'] = bool(a.conditional_pair_policy)
    out = Path(a.out).resolve()
    if out.exists() and not a.resume:
        raise SystemExit(f'Campaign path exists; use a fresh --out or explicit --resume: {out}')
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / 'campaign.json'
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        for key, value in source.items():
            if old.get(key) != value:
                raise SystemExit(f'Resume refused: {key} changed ({old.get(key)!r} != {value!r})')
        if not a.resume:
            raise SystemExit('Campaign already initialized; use --resume')
    else:
        if a.resume:
            raise SystemExit('--resume requested but campaign.json is missing')
        atomic_json(manifest_path, {'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(), **source,
                                   'status': 'running', 'units': [],
                                   'policy': 'development/validation results only; test requires explicit stage and validation freeze'})

    if a.stage == 'test':
        if a.conditional_pair_policy:
            raise SystemExit('Conditional-pair policy is development-only and cannot run on test')
        if not a.test_data or not a.freeze or a.limit:
            raise SystemExit('Test requires --test-data, --freeze and no --limit')
        freeze = json.loads(Path(a.freeze).read_text())
        if (freeze.get('experiment') != a.experiment or freeze.get('protocol_sha256') != phash
                or freeze.get('selected_ms') is None or not freeze.get('test_eligible')):
            raise SystemExit('Test freeze must be a feasible validation freeze for this experiment and protocol')
        if freeze.get('source_identity') != source:
            raise SystemExit('Test freeze source/data/checkpoint/script identity differs from current artifacts')
        canonical_path = artifact_root / 'budget_selection.json'
        if not canonical_path.exists():
            raise SystemExit('Test requires the canonical budget_selection.json under --run as a second freeze gate')
        canonical = json.loads(canonical_path.read_text())
        if (canonical.get('selected_ms') != freeze['selected_ms'] or canonical.get('protocol_sha256') != phash
                or canonical.get('protocol_primary_ms') != protocol['primary_budget_ms']
                or canonical.get('protocol_preferred_ms') != protocol.get('preferred_budget_ms',protocol['primary_budget_ms'])
                or canonical.get('budget_lock') != protocol.get('budget_lock')
                or freeze.get('primary_budget_ms') != protocol['primary_budget_ms']
                or freeze.get('preferred_budget_ms') != protocol.get('preferred_budget_ms',protocol['primary_budget_ms'])
                or freeze.get('budget_lock') != protocol.get('budget_lock')):
            raise SystemExit('Campaign freeze and canonical matched budget selection disagree')
        # The benchmark performs the second gate against its canonical frozen selection,
        # current implementation hashes, and checkpoint hashes. This runner adds an
        # explicit, matching validation-freeze requirement before it can reach test.
        if a.experiment == 'specular':
            cmd = [sys.executable, 'scripts/benchmark.py', '--matched', '--split', 'test', '--test-data', a.test_data,
                   '--scenario', data, '--response', a.response, '--run', str(artifact_root), '--protocol', a.protocol,
                   '--search-config', 'medium', '--output', str(out / 'test_medium.jsonl')]
        else:
            cmd = [sys.executable, 'scripts/benchmark_coupled.py', '--matched', '--mode', 'spatial', '--split', 'test',
                   '--test-data', a.test_data, '--data', data, '--run', str(artifact_root), '--protocol', a.protocol,
                   '--search-config', 'medium', '--output', str(out / 'test_medium.jsonl')]
            if a.physics_gate: cmd += ['--physics-gate', a.physics_gate]
        env = dict(os.environ, PYTHONPATH=str(ROOT / 'src') + os.pathsep + os.environ.get('PYTHONPATH', ''))
        with (out / 'commands.log').open('a') as log:
            log.write(' '.join(cmd) + '\n'); log.flush()
            subprocess.run(cmd, cwd=ROOT, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
        return

    configs = parse_csv(a.configs, str)
    seeds = parse_csv(a.seeds, int)
    budgets = parse_csv(a.budgets, float)
    if not seeds or not budgets or any(x not in protocol['seeds'] for x in seeds):
        raise SystemExit('Use nonempty seeds/budgets; seeds must be registered in the protocol')
    if a.stage == 'validation':
        if a.test_data or a.freeze:
            raise SystemExit('Validation cannot consume test data or a freeze artifact')
        if any(c not in {'small', 'medium', 'large'} for c in configs): raise SystemExit('Unknown search config')
        split = 'validation'
    else:
        if not a.freeze or a.test_data:
            raise SystemExit('Development requires --freeze and cannot consume test data')
        freeze = json.loads(Path(a.freeze).read_text())
        if freeze.get('experiment') != a.experiment or freeze.get('protocol_sha256') != phash or freeze.get('selected_ms') is None:
            raise SystemExit('Development requires a feasible validation freeze for this experiment and protocol')
        if freeze.get('source_identity') != source: raise SystemExit('Development freeze source/data/checkpoint/script identity mismatch')
        split = 'pilot'
        configs = [freeze['search_config']]
        budgets = [float(freeze['selected_ms'])]
    if a.stage == 'validation' and a.experiment not in {'specular', 'coupled'}: raise SystemExit('Invalid experiment')

    manifest = json.loads(manifest_path.read_text())
    methods = protocol_methods(protocol)
    for config in configs:
        for budget in budgets:
            for seed in seeds:
                tag = f'{a.experiment}_{split}_{config}_b{budget:g}_s{seed}'
                if a.conditional_pair_policy: tag += '_conditional_pair'
                dest = out / f'{tag}.jsonl'
                meta = dest.with_suffix('.json')
                if dest.exists() or meta.exists():
                    recorded = next((u for u in manifest['units'] if u['path'] == dest.name), None)
                    if dest.exists() and meta.exists() and a.resume and recorded and recorded.get('sha256') == sha256_file(dest):
                        sidecar = json.loads(meta.read_text())
                        if recorded.get('metadata_sha256') != sha256_file(meta) or not unit_sidecar_matches(sidecar, source):
                            raise SystemExit(f'Resume refused: unit metadata/source identity changed: {dest}')
                        continue
                    if not a.resume:
                        raise SystemExit(f'Preserving existing/incomplete unit {tag}; use --resume or a fresh campaign')
                    # Keep an interrupted JSONL and its sidecar for diagnosis; a
                    # new attempt gets a distinct path so no partial evidence is lost.
                    attempt = 2
                    while True:
                        candidate = out / f'{tag}_attempt{attempt:02d}.jsonl'
                        if not candidate.exists() and not candidate.with_suffix('.json').exists():
                            dest, meta = candidate, candidate.with_suffix('.json')
                            break
                        attempt += 1
                if a.experiment == 'specular':
                    cmd = [sys.executable, 'scripts/benchmark.py', '--matched', '--split', split, '--scenario', data,
                           '--response', a.response, '--run', str(artifact_root), '--protocol', a.protocol,
                           '--search-config', config, '--seeds', str(seed), '--budgets', f'{budget:g}',
                           '--output', str(dest)]
                else:
                    cmd = [sys.executable, 'scripts/benchmark_coupled.py', '--matched', '--mode', 'spatial', '--split', split,
                           '--data', data, '--run', str(artifact_root), '--protocol', a.protocol,
                           '--search-config', config, '--seeds', str(seed), '--budgets', f'{budget:g}',
                           '--output', str(dest)]
                    if a.physics_gate: cmd += ['--physics-gate', a.physics_gate]
                if a.limit: cmd += ['--limit', str(a.limit)]
                if a.conditional_pair_policy: cmd += ['--conditional-pair-policy']
                live_identity=campaign_source_identity(a.experiment, phash, data, artifact_root,
                                                       response=a.response if a.experiment == 'specular' else None,
                                                       physics_gate=gate_path if a.experiment == 'coupled' else None)
                live_identity['conditional_pair_policy']=bool(a.conditional_pair_policy)
                if live_identity != {k:v for k,v in source.items() if k!='protocol_path'}:
                    raise SystemExit('Campaign source/checkpoint identity changed before benchmark unit')
                env = dict(os.environ, PYTHONPATH=str(ROOT / 'src') + os.pathsep + os.environ.get('PYTHONPATH', ''))
                with (out / 'commands.log').open('a') as log:
                    log.write(' '.join(cmd) + '\n'); log.flush()
                    subprocess.run(cmd, cwd=ROOT, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
                sidecar = json.loads(meta.read_text())
                if not unit_sidecar_matches(sidecar, source):
                    raise RuntimeError(f'Benchmark metadata does not match frozen source identity: {meta}')
                rows = [json.loads(line) for line in dest.read_text().splitlines() if line.strip()]
                if not rows or any(r.get('split') != split or int(r.get('seed', -1)) != seed or float(r.get('budget_ms', -1)) != budget for r in rows):
                    raise RuntimeError(f'Unexpected output identity in {dest}')
                if set(r['method'] for r in rows) != set(methods): raise RuntimeError(f'Incomplete method coverage in {dest}')
                manifest['units'].append({'path': dest.name, 'sha256': sha256_file(dest),
                                          'metadata_sha256': sha256_file(meta), 'rows': len(rows),
                                          'split': split, 'config': config, 'budget_ms': budget, 'seed': seed,
                                          'methods': methods})
                atomic_json(manifest_path, manifest)
    live_identity = campaign_source_identity(a.experiment, phash, data, artifact_root,
                                             response=a.response if a.experiment == 'specular' else None,
                                             physics_gate=gate_path if a.experiment == 'coupled' else None)
    live_identity['conditional_pair_policy']=bool(a.conditional_pair_policy)
    if live_identity != {k:v for k,v in source.items() if k!='protocol_path'}:
        raise SystemExit('Campaign source/checkpoint identity changed before validation freeze')
    manifest['status'] = 'complete'
    atomic_json(manifest_path, manifest)
    if (a.stage == 'validation' and 'medium' in configs and not a.limit and not a.conditional_pair_policy
            and {10.0, 50.0} <= set(budgets)):
        primary = [u for u in manifest['units'] if u['split'] == 'validation' and u['config'] == 'medium' and u['seed'] in seeds]
        if set(float(u['budget_ms']) for u in primary) >= {10.0}:
            all_rows = [json.loads(line) for u in primary for line in (out / u['path']).read_text().splitlines() if line.strip()]
            # Freeze only after method coverage has been checked for every budget.
            selected = None
            feasible = {}
            for b in sorted(set(float(x) for x in budgets)):
                br = [r for r in all_rows if float(r['budget_ms']) == b]
                rows_by = {m: sum(r['method'] == m for r in br) for m in methods}
                misses = {m: sum(r['method'] == m and r['deadline_missed'] for r in br) for m in methods}
                complete = len(set(rows_by.values())) == 1 and min(rows_by.values(), default=0) > 0
                feasible[str(b)] = {'rows_by_method': rows_by, 'misses_by_method': misses, 'complete': complete,
                                    'feasible': complete and all(v == 0 for v in misses.values())}
            primary = float(protocol['primary_budget_ms'])
            preferred=float(protocol.get('preferred_budget_ms',primary))
            selection_order = [primary] + sorted(float(b) for b in budgets if float(b) > primary)
            selected = next((b for b in selection_order
                             if feasible.get(str(float(b)), {}).get('feasible', False)), None)
            try:
                with __import__('numpy').load(data) as frames:
                    expected_indices = __import__('numpy').flatnonzero(frames['split'] == 'validation')
                    expected_rows = int(len(expected_indices)) * len(seeds)
            except (KeyError, ValueError):
                expected_indices = ()
                expected_rows = -1
            full_grid = (not a.limit and set(seeds) == set(protocol['seeds'])
                         and set(float(x) for x in budgets) == set(float(x) for x in protocol['budgets_ms'])
                         and configs == ['medium'])
            complete_grid = full_grid and expected_rows > 0 and all(
                str(float(b)) in feasible and feasible[str(float(b))]['complete']
                and all(n == expected_rows for n in feasible[str(float(b))]['rows_by_method'].values())
                for b in protocol['budgets_ms'])
            if complete_grid:
                validate_validation_rows(all_rows, methods, seeds, protocol['budgets_ms'],
                                         expected_indices, primary, selected_budget=selected)
            primary_passed = feasible.get(str(primary), {}).get('feasible', False)
            freeze = {'experiment': a.experiment, 'split': 'validation', 'protocol_sha256': phash,
                      'data_sha256': sha256_file(data), 'search_config': 'medium', 'seeds': seeds,
                      'selected_ms': selected, 'feasibility': feasible,
                      'preferred_budget_ms': preferred, 'primary_budget_ms': primary,
                      'budget_lock': protocol.get('budget_lock'),
                      'rule': selection_rule_text(preferred,primary,protocol['budgets_ms']),
                      'validation_only': True,
                      'primary_budget_ms': primary, 'primary_budget_passed': bool(primary_passed),
                      'expected_rows_per_method_budget': expected_rows,
                      'complete_protocol_validation_grid': bool(complete_grid),
                      'source_identity': source,
                      'test_eligible': bool(complete_grid and selected is not None
                                            and not a.conditional_pair_policy),
                      'created_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
            atomic_json(out / f'{a.experiment}_validation_freeze.json', freeze)


if __name__ == '__main__': main()
