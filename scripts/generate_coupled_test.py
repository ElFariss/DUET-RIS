"""Untouched coupled-wire TEST frames (matched_v1). Physics identical to
generate_coupled_reference.py; only trajectories differ. No labels, rates or controller output.

Sampling (frozen in configs/experiments/matched_v1.json):
  rng = default_rng(20261106); for each trajectory tr in 0..29 draw, in this order,
    start    ~ U(box) of shape (2,3), box = per-user per-axis [min,max] of the step-0 positions
               returned by generate_coupled_reference.trajectories() (computed from its outputs);
    velocity ~ U(declared velocity range of that function) of shape (2,3).
  The sinusoidal term is unchanged: y += .006*sin(2*pi*2*t + tr) * [1,-1].
Restartable: finished frames are kept; incomplete or hash-mismatched ones are removed on start.
"""
import argparse, json, hashlib, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_coupled_reference import trajectories as existing_trajectories, work

SEED = 20261106
N_TRAJ, N_STEP, DT = 30, 16, 0.02
VEL_LO, VEL_HI = [-.15, -.7, -.04], [.15, .7, .04]  # literal arguments of rng.uniform in trajectories()


def existing_box():
    rows = existing_trajectories()
    pos = np.array([r['users_m'] for r in rows])
    step = np.array([r['step'] for r in rows])
    starts = pos[step == 0]  # (12,2,3), actual outputs
    return rows, starts.min(0), starts.max(0)


def test_trajectories():
    old, lo, hi = existing_box()
    rng = np.random.default_rng(SEED)
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
                           'split': 'test', 'users_m': pos.tolist()})
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


def clean(out):
    removed = []
    for p in sorted(out.glob('frame_*.npz')):
        j = p.with_suffix('.json')
        ok = False
        if j.exists():
            try:
                ok = json.loads(j.read_text())['sha256'] == hashlib.sha256(p.read_bytes()).hexdigest()
            except Exception:
                ok = False
        if not ok:
            p.unlink(); j.unlink(missing_ok=True); removed.append(p.name)
    for p in out.glob('frame_*.json'):
        if not p.with_suffix('.npz').exists():
            p.unlink(); removed.append(p.name)
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/processed/coupled_wire_test_v1')
    ap.add_argument('--segments', type=int, default=81)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--protocol-only', action='store_true')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    old, lo, hi, draws, rows = test_trajectories()
    checks = overlap_checks(old, rows)
    if checks['duplicate_start'] or checks['duplicate_frame'] or checks['min_inter_user_distance_m'] < .03:
        raise RuntimeError(f'Test trajectories fail disjointness/collision checks: {checks}')
    protocol = {'model': 'PEC thin-wire NEC-2, free space, no substrate/ground/human blockers',
                'frequency_hz': 5.53e9, 'cells': 64, 'bs_antennas': 4, 'users': 2, 'segments': a.segments,
                'wire_length_m': .024, 'wire_radius_m': .00005, 'cell_pitch_yz_m': [.028, .030],
                'dt_s': DT, 'frames_per_trajectory': N_STEP, 'trajectories': N_TRAJ, 'test': N_TRAJ,
                'seed': SEED, 'split_label': 'test', 'pilot_is_development': False, 'untouched_test': True,
                'sampling': {'start_box_lo_m': lo.tolist(), 'start_box_hi_m': hi.tolist(),
                             'start_box_source': 'per-user per-axis min/max of step-0 positions of generate_coupled_reference.trajectories()',
                             'velocity_lo_m_s': VEL_LO, 'velocity_hi_m_s': VEL_HI,
                             'velocity_source': 'declared uniform range in generate_coupled_reference.trajectories()',
                             'draw_order': 'per trajectory: start (2,3) then velocity (2,3), default_rng(seed)',
                             'sinusoid': '.006*sin(2*pi*2*t+trajectory)*[1,-1] added to y, as in the existing generator',
                             'z_start_box_is_degenerate': True},
                'draws': draws, 'disjointness': checks, 'rows': rows}
    dest = out / 'scenario.json'
    if dest.exists() and json.loads(dest.read_text()) != protocol:
        raise ValueError('Existing protocol differs')
    dest.write_text(json.dumps(protocol, indent=2) + '\n')
    print(json.dumps({'disjointness': checks}), flush=True)
    if a.protocol_only:
        return
    removed = clean(out)
    if removed: print(json.dumps({'removed_incomplete': removed}), flush=True)
    todo = [(r, str(out), a.segments) for r in rows]
    with ProcessPoolExecutor(a.workers) as pool:
        for res in pool.map(work, todo):
            print(json.dumps(res), flush=True)
    print('GENERATION_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
