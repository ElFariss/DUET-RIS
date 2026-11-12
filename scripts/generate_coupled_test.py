"""Untouched coupled-wire TEST frames (matched_v1). Physics identical to
generate_coupled_reference.py; only trajectories differ. No labels, rates or controller output.

Sampling (frozen in configs/experiments/matched_v1.json):
  rng = default_rng(20261106); for each trajectory tr in 0..29 draw, in this order,
    start    ~ U(box) of shape (2,3), box = per-user per-axis [min,max] of the step-0 positions
               returned by generate_coupled_reference.trajectories() (computed from its outputs);
    velocity ~ U(declared velocity range of that function) of shape (2,3).
  The sinusoidal term is unchanged: y += .006*sin(2*pi*2*t + tr) * [1,-1].
Restartable: finished frames are kept; incomplete or hash-mismatched ones are removed on start.

Defaults (seed 20261106, output coupled_wire_test_v1, split label 'test') reproduce the frozen matched_v1 test
set byte-for-byte in scenario.json. Further sets reuse the identical sampling with other fixed seeds (see
KNOWN_SETS); their seeds are registered here and must not be changed after any rate has been seen.
Every set is checked against ALL others: the 12 reference trajectories (train/validation/pilot) and every
registered set. `--fine-from` instead re-extracts an existing dataset's frames of one split at a finer mesh.
"""
import argparse, json, hashlib, importlib.util, os, platform, sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_coupled_reference import trajectories as existing_trajectories, work

SEED = 20261106
# Registered coupled-wire trajectory sets. Seeds are fixed in advance and must never be altered.
_LEGACY_KNOWN_SETS = {'coupled_wire_test_v1': {'seed': 20261106, 'split': 'test'},
                      'coupled_wire_dev_v1': {'seed': 20261107, 'split': 'dev'},
                      'coupled_wire_test_v2': {'seed': 20261108, 'split': 'test'}}
# New training data is an in-memory trajectory set. Register its seed before
# generating labels, but keep legacy scenario schemas byte-identical.
KNOWN_SETS = _LEGACY_KNOWN_SETS | {'coupled_wire_train_v2': {'seed': 20261109, 'split': 'train'}}
FINE_SOURCE_SETS = {'coupled_wire_v1', 'coupled_wire_dev_v1'}
N_TRAJ, N_STEP, DT = 30, 16, 0.02
VEL_LO, VEL_HI = [-.15, -.7, -.04], [.15, .7, .04]  # literal arguments of rng.uniform in trajectories()


def existing_box():
    rows = existing_trajectories()
    pos = np.array([r['users_m'] for r in rows])
    step = np.array([r['step'] for r in rows])
    starts = pos[step == 0]  # (12,2,3), actual outputs
    return rows, starts.min(0), starts.max(0)


def test_trajectories(seed=SEED, split='test', box=None):
    old, lo, hi = box if box is not None else existing_box()
    rng = np.random.default_rng(seed)
    result, draws = [], []
    for tr in range(N_TRAJ):
        base = rng.uniform(lo, hi, size=(2, 3))
        vel = rng.uniform(VEL_LO, VEL_HI, size=(2, 3))
        draws.append({'trajectory': tr, 'start_m': base.tolist(), 'velocity_m_s': vel.tolist()})
        for step in range(N_STEP):
            t = step * DT
            pos = base + vel * t
            pos[:, 1] += .006 * np.sin(2 * np.pi * 2 * t + tr) * np.array([1., -1.])
            result.append({'index': tr * N_STEP + step, 'trajectory': tr, 'step': step, 'time_s': t,
                           'split': split, 'users_m': pos.tolist()})
    return old, lo, hi, draws, result


def overlap_checks(old, rows):
    o = np.array([r['users_m'] for r in old]); n = np.array([r['users_m'] for r in rows])
    ostart = o[np.array([r['step'] for r in old]) == 0]
    nstart = n[np.array([r['step'] for r in rows]) == 0]
    d_start = np.abs(nstart[:, None] - ostart[None]).max(-1).min(-1).min(-1)  # chebyshev, nearest existing start
    d_all = np.linalg.norm(n[:, None] - o[None], axis=-1).max(-1).min()  # worst-case-user nearest frame
    # wires are z-oriented 24 mm; separations used only to rule out wire collisions
    sep = np.linalg.norm(n[:, 0] - n[:, 1], axis=-1).min()
    return {'min_chebyshev_start_distance_to_existing_m': float(d_start.min()),
            'duplicate_start': bool(d_start.min() < 1e-9),
            'min_frame_distance_to_existing_m_max_over_users': float(d_all),
            'duplicate_frame': bool(d_all < 1e-9),
            'min_inter_user_distance_m': float(sep),
            'z_extent_users_m': [float(n[..., 2].min()), float(n[..., 2].max())]}


def pairwise_checks(a_rows, b_rows):
    """Disjointness of two row lists: duplicate starts and duplicate frames (chebyshev / worst-user distance)."""
    a = np.array([r['users_m'] for r in a_rows]); b = np.array([r['users_m'] for r in b_rows])
    ast = a[np.array([r['step'] for r in a_rows]) == 0]; bst = b[np.array([r['step'] for r in b_rows]) == 0]
    d_start = np.abs(ast[:, None] - bst[None]).max(-1).min(-1).min(-1)
    d_all = np.linalg.norm(a[:, None] - b[None], axis=-1).max(-1).min()
    return {'min_chebyshev_start_distance_m': float(d_start.min()), 'duplicate_start': bool(d_start.min() < 1e-9),
            'min_frame_distance_m_max_over_users': float(d_all), 'duplicate_frame': bool(d_all < 1e-9)}


def cross_set_checks(name, seed, rows, box):
    """Check `rows` (seed `seed`) against every registered set other than itself."""
    result = {}
    # Historical test/dev scenarios are frozen by exact bytes. They retain
    # their original three-set disjointness schema; the newly registered train
    # set checks against every prior registered generator in memory.
    sets_to_check = KNOWN_SETS if name == 'coupled_wire_train_v2' else _LEGACY_KNOWN_SETS
    for other, spec in sets_to_check.items():
        if other == name or spec['seed'] == seed:
            continue
        orows = test_trajectories(spec['seed'], spec['split'], box)[4]
        result[other] = pairwise_checks(rows, orows) | {'seed': spec['seed']}
    return result


def check_registered(name, seed, split):
    """Require an exact pre-registered name/seed/split tuple; never infer a split from a seed."""
    if name not in KNOWN_SETS:
        raise ValueError(f"Unregistered trajectory set {name!r}; add it to KNOWN_SETS before generation")
    spec = KNOWN_SETS[name]
    if spec['seed'] != seed:
        raise ValueError(f"Set {name} is registered with seed {spec['seed']}, not {seed}")
    if spec['split'] != split:
        raise ValueError(f"Set {name} is registered for split {spec['split']!r}, not {split!r}")
    return spec


def _atomic_json(path, value):
    tmp = path.with_name(path.name + f'.tmp-{os.getpid()}')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def identity_hash(identity):
    return hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def generation_identity(out, protocol_bytes, segments, source_scenario_sha256=None):
    here = Path(__file__).resolve()
    reference = here.with_name('generate_coupled_reference.py')
    physics = here.parent.parent / 'src' / 'atomwise_ris' / 'physics' / 'nec.py'
    pynec_spec = importlib.util.find_spec('PyNEC')
    pynec_path = Path(pynec_spec.origin).resolve() if pynec_spec and pynec_spec.origin else None
    return {'set_name': out.name, 'segments': segments,
            'protocol_sha256': hashlib.sha256(protocol_bytes).hexdigest(),
            'generator_sha256': hashlib.sha256(here.read_bytes()).hexdigest(),
            'reference_generator_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
            'physics_kernel_sha256': hashlib.sha256(physics.read_bytes()).hexdigest(),
            'python_version': platform.python_version(), 'numpy_version': np.__version__,
            'pynec_module_path': str(pynec_path) if pynec_path else None,
            'pynec_module_sha256': hashlib.sha256(pynec_path.read_bytes()).hexdigest() if pynec_path else None,
            'source_scenario_sha256': source_scenario_sha256}


def validate_frame(path, row, segments, generation_sha256):
    meta_path = path.with_suffix('.json')
    try:
        meta = json.loads(meta_path.read_text())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if meta.get('sha256') != digest:
            return False, 'npz_sha256_mismatch', None
        if meta.get('generation_identity_sha256') != generation_sha256:
            return False, 'generation_identity_mismatch', None
        if meta.get('segments_per_wire') != segments:
            return False, 'mesh_mismatch', None
        if not all(meta.get(k) == row.get(k) for k in ('index', 'trajectory', 'step', 'time_s', 'split', 'users_m')):
            return False, 'frame_metadata_mismatch', None
        zfile = np.load(path, allow_pickle=False)
        with zfile as data:
            z = data['z']
            centers = data['centers']
            lengths = data['lengths']
            if z.shape != (70, 70) or not np.isfinite(z).all():
                return False, 'impedance_matrix_shape_or_finiteness', None
            if centers.shape != (70, 3) or lengths.shape != (70,) or not np.isfinite(centers).all() or not np.isfinite(lengths).all():
                return False, 'wire_geometry_shape_or_finiteness', None
        rmin = float(meta['minimum_resistance_eigenvalue_ohm'])
        smax = float(meta['maximum_scattering_singular_value'])
        reciprocity = float(meta['reciprocity_relative'])
        if not np.isfinite([rmin, smax, reciprocity]).all():
            return False, 'nonfinite_physics_diagnostic', None
        if rmin < -1e-6 or smax > 1.0001:
            return False, 'passivity_gate_failed', None
        return True, None, {'sha256': digest, 'minimum_resistance_eigenvalue_ohm': rmin,
                            'maximum_scattering_singular_value': smax,
                            'reciprocity_relative': reciprocity}
    except (OSError, ValueError, TypeError, KeyError):
        return False, 'unreadable_frame_or_sidecar', None


def frame_is_valid(path, row, segments, generation_sha256):
    return validate_frame(path, row, segments, generation_sha256)[0]


def clean(out, rows, segments, generation_sha256):
    expected = {r['index']: r for r in rows}
    removed = []
    for p in sorted(out.glob('frame_*.npz')):
        try:
            index = int(p.stem.split('_')[1])
        except (IndexError, ValueError):
            index = -1
        if index not in expected or not frame_is_valid(p, expected[index], segments, generation_sha256):
            p.unlink(); p.with_suffix('.json').unlink(missing_ok=True); removed.append(p.name)
    for p in out.glob('frame_*.json'):
        if not p.with_suffix('.npz').exists():
            p.unlink(); removed.append(p.name)
    return removed


def fine_protocol(src, split, segments):
    """Same frames (users_m, index) as an existing dataset's split, extracted at a finer mesh."""
    src = Path(src)
    if split == 'test':
        # Allowed only for the frozen matched_v2 test, after its protocol freeze. Generates physics only.
        frozen = Path(__file__).resolve().parents[1] / 'configs/experiments/matched_v2.json'
        spec = json.loads(frozen.read_text()) if frozen.is_file() else {}
        held = spec.get('data', {}).get('held_out_test', {})
        if (spec.get('status') != 'frozen' or src.name != 'coupled_wire_test_v2' or held.get('coarse_scenario_sha256')
                != hashlib.sha256((src / 'scenario.json').read_bytes()).hexdigest()):
            raise ValueError('Fine-mesh extraction from test data needs the frozen matched_v2 protocol and its test set')
    elif split not in {'train', 'validation', 'pilot', 'dev'}:
        raise ValueError(f'Fine-mesh split {split!r} is not an approved development/validation split')
    if src.name not in FINE_SOURCE_SETS and split != 'test':
        raise ValueError(f'Fine-mesh source {src.name!r} is not registered for development/validation extraction')
    sc = json.loads((src / 'scenario.json').read_text())
    rows = [r for r in sc['rows'] if r['split'] == split]
    if not rows:
        raise ValueError(f'No source rows for split {split!r}')
    if segments <= sc.get('segments', 0):
        raise ValueError('Fine-mesh segment count must exceed the source mesh')
    protocol = {k: v for k, v in sc.items() if k != 'rows'} | {
        'segments': segments, 'fine_mesh_of': str(src), 'fine_mesh_split': split,
        'fine_mesh_frames': len(rows), 'fine_mesh_indices': [r['index'] for r in rows],
        'source_scenario_sha256': hashlib.sha256((src / 'scenario.json').read_bytes()).hexdigest(),
        'untouched_test': split == 'test', 'development_set': split != 'test',
        'note': 'Geometry and frame definitions identical to the source dataset; only segments per wire differ. '
                'No labels, rates or controller output.', 'rows': rows}
    return protocol, rows


def _work_with_identity(args):
    row, out_str, segments, identity = args
    out = Path(out_str)
    p = out / f"frame_{row['index']:04d}.npz"
    ihash = identity_hash(identity)
    if p.exists() and frame_is_valid(p, row, segments, ihash):
        return {'index': row['index'], 'status': 'existing'}
    result = work((row, out_str, segments))
    meta_path = p.with_suffix('.json')
    meta = json.loads(meta_path.read_text())
    meta['generation_identity_sha256'] = ihash
    meta['generation_identity'] = identity
    _atomic_json(meta_path, meta)
    return result


def _read_status(path, identity, expected_indices):
    if path.exists():
        status = json.loads(path.read_text())
        if status.get('identity') != identity or status.get('expected_indices') != expected_indices:
            raise ValueError('Existing generation manifest identity/expected frames differ; refusing resume')
        return status
    existing = list(path.parent.glob('frame_*.npz')) + list(path.parent.glob('frame_*.json'))
    if existing:
        raise ValueError('Existing frame artifacts have no matching generation manifest; refusing unsafe adoption')
    return {'format_version': 1, 'identity': identity, 'expected_indices': expected_indices,
            'status': 'not_started', 'started_unix': time.time()}


def _verified_frames(out, rows, segments, identity):
    ihash = identity_hash(identity)
    verified, invalid, hashes, diagnostics = [], [], {}, []
    for row in rows:
        path = out / f"frame_{row['index']:04d}.npz"
        if not path.exists():
            continue
        ok, reason, details = validate_frame(path, row, segments, ihash)
        if ok:
            verified.append(row['index'])
            hashes[str(row['index'])] = details['sha256']
            diagnostics.append(details)
        else:
            invalid.append({'index': row['index'], 'reason': reason})
    physics = None
    if diagnostics:
        physics = {'frames_checked': len(diagnostics),
                   'minimum_resistance_eigenvalue_ohm_min': min(x['minimum_resistance_eigenvalue_ohm'] for x in diagnostics),
                   'maximum_scattering_singular_value_max': max(x['maximum_scattering_singular_value'] for x in diagnostics),
                   'reciprocity_relative_max': max(x['reciprocity_relative'] for x in diagnostics),
                   'passivity_gate': 'minimum_resistance_eigenvalue_ohm >= -1e-6 and maximum_scattering_singular_value <= 1.0001'}
    return verified, invalid, hashes, physics


def run(todo, workers, out, *, expected_rows, segments, identity):
    expected_indices = [r['index'] for r in expected_rows]
    status_path = out / 'generation_status.json'
    status = _read_status(status_path, identity, expected_indices)
    ihash = identity_hash(identity)
    removed = clean(out, expected_rows, segments, ihash)
    if removed: print(json.dumps({'removed_incomplete': removed}), flush=True)
    status.update({'status': 'running', 'last_started_unix': time.time(),
                   'source_identity_sha256': ihash})
    _atomic_json(status_path, status)
    selected = {r['index'] for r, _, _, _ in todo}
    with ProcessPoolExecutor(workers) as pool:
        for res in pool.map(_work_with_identity, todo):
            print(json.dumps(res), flush=True)
    verified, invalid, frame_hashes, physics = _verified_frames(out, expected_rows, segments, identity)
    missing = sorted(set(expected_indices) - set(verified))
    complete = not missing and not invalid
    status.update({'status': 'complete' if complete else ('validation_failed' if invalid else 'partial'),
                   'verified_frame_indices': verified, 'missing_frame_indices': missing,
                   'invalid_frames': invalid, 'frame_npz_sha256': frame_hashes,
                   'physics_validation': physics,
                   'ready_for_development_evaluation': complete,
                   'last_finished_unix': time.time(), 'last_selected_indices': sorted(selected)})
    _atomic_json(status_path, status)
    if complete:
        print('GENERATION_COMPLETE', flush=True)
    else:
        print(f"GENERATION_{'VALIDATION_FAILED' if invalid else 'PARTIAL'} {len(missing)} missing, {len(invalid)} invalid of {len(expected_indices)} expected frames", flush=True)
    return status


def select_rows(rows, pick):
    if pick is None:
        return rows
    known = {r['index'] for r in rows}
    invalid = sorted(pick - known)
    if invalid:
        raise ValueError(f'--only-indices contains indices outside this protocol: {invalid}')
    return [r for r in rows if r['index'] in pick]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/processed/coupled_wire_test_v1')
    ap.add_argument('--segments', type=int, default=81)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--seed', type=int, default=SEED, help='trajectory RNG seed (registered in KNOWN_SETS)')
    ap.add_argument('--split-name', default='test', help="value of the 'split' field of every row")
    ap.add_argument('--protocol-only', action='store_true')
    ap.add_argument('--only-indices', default=None, help='comma list of frame indices (timing / smoke runs)')
    ap.add_argument('--fine-from', default=None, help='existing dataset dir whose split is re-extracted')
    ap.add_argument('--fine-split', default='validation')
    a = ap.parse_args()
    out = Path(a.out)
    pick = None if a.only_indices is None else {int(i) for i in a.only_indices.split(',')}
    if a.segments < 1:
        raise ValueError('--segments must be positive')
    if not a.fine_from:
        check_registered(out.name, a.seed, a.split_name)
    elif out.resolve() == Path(a.fine_from).resolve():
        raise ValueError('Fine-mesh output must be separate from its source dataset')
    out.mkdir(parents=True, exist_ok=True)
    if a.fine_from:
        protocol, rows = fine_protocol(a.fine_from, a.fine_split, a.segments)
        dest = out / 'scenario.json'
        if dest.exists() and json.loads(dest.read_text()) != protocol:
            raise ValueError('Existing protocol differs')
        dest.write_text(json.dumps(protocol, indent=2) + '\n')
        protocol_bytes = dest.read_bytes()
        identity = generation_identity(out, protocol_bytes, a.segments,
                                       protocol.get('source_scenario_sha256'))
        print(json.dumps({'fine_mesh_frames': len(rows)}), flush=True)
        if a.protocol_only:
            return
        chosen = select_rows(rows, pick)
        run([(r, str(out), a.segments, identity) for r in chosen], a.workers, out,
            expected_rows=rows, segments=a.segments, identity=identity)
        return
    name = out.name
    box = existing_box()
    old, lo, hi, draws, rows = test_trajectories(a.seed, a.split_name, box)
    checks = overlap_checks(old, rows)
    cross = cross_set_checks(name, a.seed, rows, box)
    bad = checks['duplicate_start'] or checks['duplicate_frame'] or checks['min_inter_user_distance_m'] < .03 \
        or any(c['duplicate_start'] or c['duplicate_frame'] for c in cross.values())
    if bad:
        raise RuntimeError(f'Trajectories fail disjointness/collision checks: {checks} {cross}')
    default = name == 'coupled_wire_test_v1' and a.seed == SEED and a.split_name == 'test'
    protocol = {'model': 'PEC thin-wire NEC-2, free space, no substrate/ground/human blockers',
                'frequency_hz': 5.53e9, 'cells': 64, 'bs_antennas': 4, 'users': 2, 'segments': a.segments,
                'wire_length_m': .024, 'wire_radius_m': .00005, 'cell_pitch_yz_m': [.028, .030],
                'dt_s': DT, 'frames_per_trajectory': N_STEP, 'trajectories': N_TRAJ, 'test': N_TRAJ,
                'seed': a.seed, 'split_label': a.split_name, 'pilot_is_development': False, 'untouched_test': True,
                'sampling': {'start_box_lo_m': lo.tolist(), 'start_box_hi_m': hi.tolist(),
                             'start_box_source': 'per-user per-axis min/max of step-0 positions of generate_coupled_reference.trajectories()',
                             'velocity_lo_m_s': VEL_LO, 'velocity_hi_m_s': VEL_HI,
                             'velocity_source': 'declared uniform range in generate_coupled_reference.trajectories()',
                             'draw_order': 'per trajectory: start (2,3) then velocity (2,3), default_rng(seed)',
                             'sinusoid': '.006*sin(2*pi*2*t+trajectory)*[1,-1] added to y, as in the existing generator',
                             'z_start_box_is_degenerate': True},
                'draws': draws, 'disjointness': checks, 'rows': rows}
    if not default:  # extra keys only for new sets; the frozen v1 scenario.json must stay byte-identical
        protocol |= {'set_name': name, 'disjointness_vs_other_sets': cross,
                     'untouched_test': a.split_name == 'test',
                     'development_set': a.split_name != 'test'}
        protocol.pop('test')
        protocol[a.split_name] = N_TRAJ
    dest = out / 'scenario.json'
    if dest.exists() and json.loads(dest.read_text()) != protocol:
        raise ValueError('Existing protocol differs')
    dest.write_text(json.dumps(protocol, indent=2) + '\n')
    protocol_bytes = dest.read_bytes()
    print(json.dumps({'disjointness': checks, 'disjointness_vs_other_sets': cross}), flush=True)
    if a.protocol_only:
        return
    chosen = select_rows(rows, pick)
    identity = generation_identity(out, protocol_bytes, a.segments)
    run([(r, str(out), a.segments, identity) for r in chosen], a.workers, out,
        expected_rows=rows, segments=a.segments, identity=identity)


if __name__ == '__main__':
    main()
