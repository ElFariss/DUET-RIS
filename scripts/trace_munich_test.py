"""Untouched Munich specular TEST traces (matched_v1): 30 new two-user trajectories x 4 steps.

Same scene, 5.53 GHz, BS, RIS cells, ray-tracing parameters and outdoor/front-side selection rules as
scripts/trace_munich.py / munich_specular_v3 (functions are imported from that script, not copied).
Only the receiver trajectories differ. No labels, rates or controller output are produced.

Modes:
  layout  sample the 30 blocks (CPU is enough) and write layout.json
  trace   BS -> (cells + test users) and RIS cells (batches of 8) -> test users; restartable
  check   re-trace ONE existing v3 trajectory with identical code and compare with v3 scenario.npz

Block sampling (seed 20261106, numpy default_rng): a pool of continuous-uniform candidate centres over the
bounding box of the original candidate grid is drawn first; each is accepted, in draw order, if
  (a) the original outdoor rule holds at the four original corner positions (downward ray hits ground < .5 m)
      and the panel-front dot product is positive, plus all 8 user positions are outdoor,
  (b) its rectangle is >= GUARD_EXISTING m (Euclidean) from every existing v3 user position block, and
  (c) it is >= GUARD_NEW m from every previously accepted test block.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mitsuba as mi
import sionna.rt as rt
from trace_munich import base_scene, trace, free_space_check, asarray
from atomwise_ris.core import C0, write_json, sha256

SEED = 20261106
V3 = Path('data/processed/munich_specular_v3')
GUARD_EXISTING, GUARD_NEW = 4.0, 2.0
BOX_X, BOX_Y = (18.0, 58.0), (12.0, 84.0)  # bounds of the original candidate grid: 18+8j (j<6), 12+8i (i<10)
POOL = 20000
RAY_PARAMS = dict(max_depth=3, los=True, specular_reflection=True, diffuse_reflection=False, diffraction=False,
                  refraction=False, samples_per_src=5000000, max_num_paths_per_src=1000000,
                  synthetic_array=False, seed=7)  # identical to v3 scenario.json ray_parameters


def fixed_design():
    bs = np.array([-210., 73., 105.]) + np.column_stack([np.zeros(4), (np.arange(4) - 1.5) * (C0 / 5.53e9) / 2, np.zeros(4)])
    center = np.array([65., 20., 3.])
    normal = np.array([-210., 73., 0.]) - np.array([65., 20., 0.]); normal /= np.linalg.norm(normal)
    tangent = np.array([-normal[1], normal[0], 0.])
    cells = np.array([center + (j - 3.5) * .020 * tangent + (i - 3.5) * .013 * np.array([0., 0., 1.]) for i in range(8) for j in range(8)])
    return bs, center, normal, cells


def block_users(c, steps=4):
    return np.array([[c + [-1.2, (s - (steps - 1) / 2) * .15, 0], c + [1.2, (s - (steps - 1) / 2) * .15 + .7, 0]] for s in range(steps)])


def outdoor_many(scene, P):
    P = np.asarray(P, float).reshape(-1, 3); n = len(P)
    ray = mi.Ray3f(mi.Point3f(mi.Float(P[:, 0].astype(np.float32)), mi.Float(P[:, 1].astype(np.float32)), mi.Float(np.full(n, 1000, np.float32))),
                   mi.Vector3f(0, 0, -1))
    hit = scene.mi_scene.ray_intersect(ray)
    return np.asarray(hit.is_valid()).astype(bool) & (np.asarray(hit.p.z) < .5)


def rect(users):  # users [steps,2,3] -> (xmin,xmax,ymin,ymax)
    u = np.asarray(users).reshape(-1, 3)
    return u[:, 0].min(), u[:, 0].max(), u[:, 1].min(), u[:, 1].max()


def rect_gap(a, b):
    dx = max(a[0] - b[1], b[0] - a[1], 0.); dy = max(a[2] - b[3], b[2] - a[3], 0.)
    return float(np.hypot(dx, dy))


def make_layout(out, nt, steps):
    bs, center, normal, cells = fixed_design()
    old = json.loads((V3 / 'layout.json').read_text())
    if not (np.allclose(old['bs'], bs, atol=1e-9) and np.allclose(old['cells'], cells, atol=1e-9) and np.allclose(old['ris_center'], center)):
        raise RuntimeError('Fixed design differs from v3 layout')
    old_users = np.array(old['users']); old_tr = np.array(old['trajectory'])
    old_rects = [rect(old_users[old_tr == t]) for t in range(old_tr.max() + 1)]
    scene = base_scene()
    if not outdoor_many(scene, center[None])[0]: raise RuntimeError('RIS centre not outdoors')
    rng = np.random.default_rng(SEED)
    pool = np.column_stack([rng.uniform(*BOX_X, POOL), rng.uniform(*BOX_Y, POOL), np.full(POOL, 1.5)])
    # original rule: four corners at offset 0, outdoor and in front of the panel
    corner_off = np.array([[-1.2, -.3, 0], [-1.2, .3, 0], [1.2, .4, 0], [1.2, 1., 0]])
    corners = (pool[:, None, :] + corner_off[None]).reshape(-1, 3)
    ok_c = outdoor_many(scene, corners).reshape(POOL, 4) & (((pool[:, None, :] + corner_off[None]) - center) @ normal > 0)
    users_all = np.array([block_users(c, steps) for c in pool])  # [POOL,steps,2,3]
    ok_u = outdoor_many(scene, users_all.reshape(-1, 3)).reshape(POOL, -1).all(1)
    accepted, rejected, rects = [], {'not_outdoor_or_rear': 0, 'too_close_to_existing': 0, 'too_close_to_new': 0}, []
    for k in range(POOL):
        if not (ok_c[k].all() and ok_u[k]): rejected['not_outdoor_or_rear'] += 1; continue
        r = rect(users_all[k])
        if min(rect_gap(r, o) for o in old_rects) < GUARD_EXISTING: rejected['too_close_to_existing'] += 1; continue
        if rects and min(rect_gap(r, o) for o in rects) < GUARD_NEW: rejected['too_close_to_new'] += 1; continue
        accepted.append(k); rects.append(r)
        if len(accepted) == nt: break
    if len(accepted) < nt: raise RuntimeError(f'Only {len(accepted)} valid test blocks from pool {POOL}')
    centers = pool[accepted]; pos = users_all[accepted].reshape(nt * steps, 2, 3)
    traj = np.repeat(np.arange(nt), steps)
    # disjointness from the existing 24 trajectories
    d_exist = float(min(rect_gap(r, o) for r in rects for o in old_rects))
    pt = np.linalg.norm(pos.reshape(-1, 3)[:, None] - old_users.reshape(-1, 3)[None], axis=-1).min()
    layout = {'bs': bs.tolist(), 'ris_center': center.tolist(), 'panel_normal': normal.tolist(), 'cells': cells.tolist(),
              'users': pos.tolist(), 'trajectory': traj.tolist(), 'split': ['test'] * len(traj),
              'chosen_before_channels': True, 'rng_seed': SEED, 'guard_existing_m': GUARD_EXISTING, 'guard_new_m': GUARD_NEW,
              'candidate_box_x': BOX_X, 'candidate_box_y': BOX_Y, 'candidate_pool_size': POOL, 'accepted_pool_indices': accepted,
              'rejection_counts_before_30th_accept': rejected,
              'outdoor_selection': 'Original rule (downward ray hits ground below 0.5 m at four original corner positions; positive panel-front dot product) plus all 8 user positions outdoor',
              'block_centers': centers.tolist(),
              'front_side_cosines': ((pos - center) @ normal / np.linalg.norm(pos - center, axis=-1)).tolist(),
              'min_block_gap_to_existing_m': d_exist, 'min_user_point_distance_to_existing_users_m': float(pt),
              'min_gap_between_test_blocks_m': float(min(rect_gap(a, b) for i, a in enumerate(rects) for b in rects[i + 1:])),
              'disjoint_from_existing_24': bool(d_exist >= GUARD_EXISTING)}
    out.mkdir(parents=True, exist_ok=True); write_json(out / 'layout.json', layout)
    print(json.dumps({k: layout[k] for k in ['rejection_counts_before_30th_accept', 'min_block_gap_to_existing_m', 'min_gap_between_test_blocks_m',
                                             'min_user_point_distance_to_existing_users_m', 'disjoint_from_existing_24']}), flush=True)
    print('block_centers', np.round(centers[:, :2], 1).tolist(), flush=True)


def gpu_note():
    try:
        return subprocess.run(['nvidia-smi', '--query-gpu=index,memory.used,memory.total,utilization.gpu', '--format=csv,noheader'],
                              capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        return str(e)


def full_trace(bs, cells, pos, out, source_batch, tag):
    """Identical call structure to trace_munich.main: BS -> cells+users, then cell batches -> users."""
    print(tag, 'gpu before:', gpu_note().replace('\n', ' | '), flush=True)
    t0 = time.perf_counter()
    f = out / 'bs' / 'trace.json'
    if f.exists(): gd = np.load(out / 'bs' / 'paths.npz')['channel']
    else: gd = trace(bs, np.vstack([cells, pos.reshape(-1, 3)]), out / 'bs', RAY_PARAMS, export=False)
    g = gd[:64]; direct = gd[64:].reshape(len(pos), 2, 4); hs = []
    for j in range(0, 64, source_batch):
        d = out / f'ris_{j:02}'
        hs.append(np.load(d / 'paths.npz')['channel'] if (d / 'trace.json').exists()
                  else trace(cells[j:j + source_batch], pos.reshape(-1, 3), d, RAY_PARAMS, export=False))
    h = np.concatenate(hs, axis=1).reshape(len(pos), 2, 64)
    print(tag, 'seconds', time.perf_counter() - t0, flush=True)
    return g, h, direct, time.perf_counter() - t0


def rel(a, b):
    nb = np.linalg.norm(b)
    return float(np.linalg.norm(a - b) / nb) if nb > 0 else (0.0 if np.linalg.norm(a) == 0 else None)


def check_existing(out, k, source_batch):
    sc = np.load(V3 / 'scenario.npz'); lay = json.loads((V3 / 'layout.json').read_text())
    bs, center, normal, cells = fixed_design()
    sel = np.where(np.array(lay['trajectory']) == k)[0] if k >= 0 else np.arange(len(lay['trajectory'])); pos = np.array(lay['users'])[sel]
    g, h, d, secs = full_trace(bs, cells, pos, out, source_batch, f'check_traj{k}')
    ref = dict(G=sc['G'], H=sc['H'][sel], D=sc['D'][sel])
    new = dict(G=g, H=h, D=d)
    res = {'trajectory': k, 'samples': sel.tolist(), 'seconds': secs, 'ray_parameters': RAY_PARAMS,
           'relative_l2_error': {n: rel(new[n], ref[n]) for n in new},
           'max_abs_error': {n: float(np.abs(new[n] - ref[n]).max()) for n in new},
           'max_abs_error_relative_to_max_abs_reference': {n: (float(np.abs(new[n] - ref[n]).max() / np.abs(ref[n]).max()) if np.abs(ref[n]).max() > 0 else None) for n in new},
           'reference_norm': {n: float(np.linalg.norm(ref[n])) for n in new}, 'new_norm': {n: float(np.linalg.norm(new[n])) for n in new},
           'nonzero_fraction_reference': {n: float(np.mean(ref[n] != 0)) for n in new}, 'nonzero_fraction_new': {n: float(np.mean(new[n] != 0)) for n in new},
           'zero_pattern_identical': {n: bool(np.array_equal(ref[n] != 0, new[n] != 0)) for n in new},
           'bit_identical': {n: bool(np.array_equal(new[n], ref[n])) for n in new}}
    alt = Path('data/processed/munich_specular_compute_v3/scenario.npz')
    if alt.exists():  # independent earlier run of same parameters: indicates the intrinsic run-to-run floor
        a = np.load(alt)
        res['floor_independent_run_compute_v3_vs_v3_same_trajectory'] = {
            'relative_l2_error': {'G': rel(a['G'], sc['G']), 'H': rel(a['H'][sel], sc['H'][sel]), 'D': rel(a['D'][sel], sc['D'][sel])}}
    if k < 0:  # per-trajectory breakdown of the full original receiver set
        tr = np.array(lay['trajectory'])
        res['per_trajectory_relative_l2'] = {str(t): {n: rel(new[n][tr == t] if n != 'G' else new[n], ref[n][tr == t] if n != 'G' else ref[n]) for n in ('H', 'D')} for t in range(tr.max() + 1)}
    write_json(out / f'integrity_check_traj{k}.json', res); print(json.dumps(res, indent=1), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['layout', 'trace', 'check'])
    ap.add_argument('--out', default='data/raw/acquisition/munich_specular_test_v1')
    ap.add_argument('--trajectories', type=int, default=30); ap.add_argument('--steps', type=int, default=4)
    ap.add_argument('--source-batch', type=int, default=8); ap.add_argument('--check-trajectory', type=int, default=0)
    a = ap.parse_args(); out = Path(a.out)
    if a.mode == 'layout': make_layout(out, a.trajectories, a.steps); return
    out.mkdir(parents=True, exist_ok=True)
    if a.mode == 'check':
        out = out / f'check_traj{a.check_trajectory}'; out.mkdir(exist_ok=True)
        if not (out / 'free_space_check.json').exists(): free_space_check(out)
        check_existing(out, a.check_trajectory, a.source_batch); return
    if not (out / 'free_space_check.json').exists(): free_space_check(out)
    lay = json.loads((out / 'layout.json').read_text())
    bs, center, normal, cells = fixed_design()
    pos = np.array(lay['users'])
    g, h, d, secs = full_trace(bs, cells, pos, out, a.source_batch, 'test')
    np.savez_compressed(out / 'channels.npz', G=g, H=h, D=d)
    write_json(out / 'trace_summary.json', {'seconds': secs, 'ray_parameters': RAY_PARAMS, 'samples': int(len(pos)),
                                            'channels_sha256': sha256(out / 'channels.npz'), 'layout_sha256': sha256(out / 'layout.json')})
    print('TRACE_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
