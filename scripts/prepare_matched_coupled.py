"""Assemble the untouched coupled test set (matched_v1): dataset.npz + manifest. NO labels, rates or controller output.

Checks per frame: sha256 against the frame json, passivity (largest scattering singular value <= 1.0001,
smallest resistance eigenvalue >= -1e-6), finiteness, shape, geometry identical to the reference
panel/BS, user positions equal to scenario.json rows, segments=81, split label 'test'.
Only physics diagnostics are recomputed; no rate is computed.
"""
import argparse, json, hashlib
from pathlib import Path
import numpy as np
from atomwise_ris.physics.nec import diagnostics, geometry

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data/processed/coupled_wire_test_v1')
    ap.add_argument('--existing', default='data/processed/coupled_wire_v1')
    a = ap.parse_args(); data = Path(a.data)
    scen = json.loads((data / 'scenario.json').read_text()); rows = scen['rows']
    if len(rows) != scen['trajectories'] * scen['frames_per_trajectory']: raise ValueError('row count')
    zs, manifest, fails = [], [], []
    ref_fixed = geometry(8, np.array(rows[0]['users_m'])).centers[:68]
    for row in rows:
        p = data / f"frame_{row['index']:04d}.npz"; meta = json.loads(p.with_suffix('.json').read_text())
        d = sha(p)
        f = np.load(p); z = f['z']
        diag = diagnostics(z)
        problems = []
        if d != meta['sha256']: problems.append('hash')
        if z.shape != (70, 70) or not np.isfinite(z).all(): problems.append('shape/finite')
        if diag['maximum_scattering_singular_value'] > 1.0001: problems.append('nonpassive_S')
        if diag['minimum_resistance_eigenvalue_ohm'] < -1e-6: problems.append('negative_resistance')
        if diag['reciprocity_relative'] > 1e-6: problems.append('reciprocity')
        if meta['segments_per_wire'] != scen['segments'] or meta['split'] != 'test': problems.append('protocol')
        if not np.allclose(f['centers'][:68], ref_fixed) or not np.allclose(f['centers'][68:], row['users_m']): problems.append('geometry')
        if abs(diag['maximum_scattering_singular_value'] - meta['maximum_scattering_singular_value']) > 1e-9: problems.append('diag_mismatch')
        if problems: fails.append({'index': row['index'], 'problems': problems})
        zs.append(z)
        manifest.append({'path': str(p), 'sha256': d, 'index': row['index'], 'trajectory': row['trajectory'],
                         'step': row['step'], 'seconds': meta['seconds'],
                         'max_scattering_singular_value': diag['maximum_scattering_singular_value'],
                         'min_resistance_eigenvalue_ohm': diag['minimum_resistance_eigenvalue_ohm'],
                         'reciprocity_relative': diag['reciprocity_relative'], 'hostname': meta['hostname']})
    if fails: raise RuntimeError(f'Frame validation failed: {fails}')
    # disjointness from the existing positions (all frames), re-verified from the stored frames
    ex = Path(a.existing); exc = np.array([np.load(ex / f"frame_{i:04d}.npz")['centers'][68:] for i in range(192)])
    new = np.array([np.load(data / f"frame_{r['index']:04d}.npz")['centers'][68:] for r in rows])
    min_frame = float(np.linalg.norm(new[:, None] - exc[None], axis=-1).max(-1).min())
    min_start = float(np.abs(new[[r['step'] == 0 for r in rows]][:, None] - exc[::16][None]).max((-1, -2)).min())
    if min_frame < 1e-9: raise RuntimeError('Test frame duplicates an existing frame')
    z = np.array(zs)
    out = data / 'dataset.npz'
    np.savez_compressed(out, z=z, split=np.array([r['split'] for r in rows]),
                        trajectory=np.array([r['trajectory'] for r in rows]), step=np.array([r['step'] for r in rows]),
                        users_m=np.array([r['users_m'] for r in rows]), time_s=np.array([r['time_s'] for r in rows]))
    secs = np.array([m['seconds'] for m in manifest])
    summary = {'frames': len(rows), 'trajectories': scen['trajectories'], 'frames_per_trajectory': scen['frames_per_trajectory'],
               'segments': scen['segments'], 'seed': scen['seed'], 'split': 'test', 'labels_present': False,
               'dataset': str(out), 'dataset_sha256': sha(out), 'z_array_sha256': hashlib.sha256(np.ascontiguousarray(z).tobytes()).hexdigest(),
               'scenario_json_sha256': sha(data / 'scenario.json'),
               'max_scattering_singular_value': max(m['max_scattering_singular_value'] for m in manifest),
               'min_resistance_eigenvalue_ohm': min(m['min_resistance_eigenvalue_ohm'] for m in manifest),
               'seconds_per_frame_mean': float(secs.mean()), 'seconds_per_frame_median': float(np.median(secs)),
               'seconds_per_frame_max': float(secs.max()), 'hostnames': sorted({m['hostname'] for m in manifest}),
               'all_frames_passed_hash_and_passivity': True,
               'min_frame_distance_to_existing_m_max_over_users': min_frame,
               'min_chebyshev_start_distance_to_existing_m': min_start,
               'disjoint_from_existing_192_frames': True}
    (data / 'manifest.json').write_text(json.dumps({'summary': summary, 'frames': manifest}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__': main()
