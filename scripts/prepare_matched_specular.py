"""Assemble the untouched Munich specular test Scenario (matched_v1) from raw traces. NO labels or rates.

Reads data/raw/acquisition/munich_specular_test_v1 (layout.json, channels.npz from scripts/trace_munich_test.py),
verifies stack/scene identity with munich_specular_v3 metadata, and writes scenario.npz + scenario.json
(atomwise_ris Scenario format, split label 'test') and hashes.json.
"""
import argparse, json, importlib.metadata
from pathlib import Path
import numpy as np
import sionna.rt as rt
from atomwise_ris.core import Scenario, sha256, write_json, source_versions

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', default='data/raw/acquisition/munich_specular_test_v1')
    ap.add_argument('--out', default='data/processed/munich_specular_test_v1')
    ap.add_argument('--v3', default='data/processed/munich_specular_v3')
    a = ap.parse_args(); raw, out, v3 = Path(a.raw), Path(a.out), Path(a.v3)
    lay = json.loads((raw / 'layout.json').read_text()); ch = np.load(raw / 'channels.npz')
    old = json.loads((v3 / 'scenario.json').read_text()); oldlay = json.loads((v3 / 'layout.json').read_text())
    pos = np.array(lay['users']); traj = np.array(lay['trajectory']); split = np.array(lay['split'])
    if set(split) != {'test'} or len(np.unique(traj)) != 30 or len(pos) != 120: raise RuntimeError('unexpected layout')
    if not (np.allclose(lay['bs'], oldlay['bs']) and np.allclose(lay['cells'], oldlay['cells'])): raise RuntimeError('BS/cells differ from v3')
    versions = {n: importlib.metadata.version(n) for n in ['numpy', 'torch', 'sionna-rt', 'deepmimo', 'mitsuba', 'drjit']}
    scene_path = Path(rt.scene.munich)
    scene_hashes = {str(p.relative_to(scene_path.parent)): sha256(p) for p in sorted(scene_path.parent.rglob('*')) if p.is_file()}
    if versions != old['versions']: raise RuntimeError(f"Version mismatch {versions} vs {old['versions']}")
    if scene_hashes != old['scene_sha256']: raise RuntimeError('Scene files differ from v3')
    ts = json.loads((raw / 'trace_summary.json').read_text())
    if ts['ray_parameters'] != old['ray_parameters']: raise RuntimeError('Ray parameters differ from v3')
    g, h, d = ch['G'], ch['H'], ch['D']
    # coefficient-integrity checks only (no rates)
    integrity = {'finite': bool(all(np.isfinite(x).all() for x in (g, h, d))), 'shapes': {'G': list(g.shape), 'H': list(h.shape), 'D': list(d.shape)},
                 'nonzero_fraction': {'G': float(np.mean(g != 0)), 'H': float(np.mean(h != 0)), 'D': float(np.mean(d != 0))},
                 'G_equals_v3_G_max_abs': float(np.abs(g - np.load(v3 / 'scenario.npz')['G']).max()),
                 'front_side_cosine_min': float(np.min(lay['front_side_cosines'])), 'rear_side_users': int(np.sum(np.array(lay['front_side_cosines']) <= 0))}
    if not integrity['finite'] or integrity['rear_side_users'] or integrity['nonzero_fraction']['G'] < 1 or integrity['nonzero_fraction']['H'] < 1:
        raise RuntimeError(f'Integrity failure {integrity}')
    meta = {k: old[k] for k in ['frequency_hz', 'power_w', 'noise_w', 'noise_bandwidth_hz', 'noise_figure_db', 'cell_area_m2', 'source', 'response_approximation',
                                'aperture_normalization', 'phase_convention', 'precoder', 'diffuse_reflection', 'reason']}
    meta.update(versions=versions, scene_sha256=scene_hashes, ray_parameters=ts['ray_parameters'], split_unit='Disjoint spatial block containing entire two-user trajectory',
                pilot_is_development=False, untouched_final_test_generated=True, matched_v1_test=True, rng_seed=lay['rng_seed'],
                layout_sha256=sha256(raw / 'layout.json'), channels_sha256=sha256(raw / 'channels.npz'),
                represented_frequency_hz=old['represented_frequency_hz'], deepmimo_export_completed=False,
                coefficient_origin='Sionna CIR from scripts/trace_munich_test.py (same code path as trace_munich.py); no DeepMIMO export',
                integrity=integrity, source_sha256=source_versions(),
                note='Test frames: no labels, rates or controller outputs computed. Receiver trajectories sampled with seed 20261106 at least 4 m from every v3 block.')
    out.mkdir(parents=True, exist_ok=True)
    Scenario(g, h, d, pos, np.array(lay['cells']), traj, split, meta).save(out / 'scenario.npz')
    Scenario.load(out / 'scenario.npz')  # round-trip validation
    write_json(out / 'layout.json', lay)
    extra = {n: sha256(p) for n, p in {'raw/channels.npz': raw / 'channels.npz', 'raw/layout.json': raw / 'layout.json',
             'raw/trace_summary.json': raw / 'trace_summary.json'}.items()}
    hashes = {'scenario.npz': sha256(out / 'scenario.npz'), 'scenario.json': sha256(out / 'scenario.json'), 'layout.json': sha256(out / 'layout.json'),
              'arrays_sha256_note': 'sha256 of the saved scenario.npz file', 'raw': extra, 'integrity': integrity}
    for f in ['integrity_check_traj0.json', 'integrity_check_traj-1.json']:
        for p in raw.glob(f'check_traj*/{f}'): hashes['raw/' + p.parent.name + '/' + f] = sha256(p)
    write_json(out / 'hashes.json', hashes); print(json.dumps(hashes, indent=1))

if __name__ == '__main__': main()
