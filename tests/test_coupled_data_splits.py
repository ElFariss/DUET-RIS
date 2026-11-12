"""Disjointness and default-reproduction checks for the coupled-wire trajectory sets (no NEC-2 needed)."""
import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import generate_coupled_test as g
from generate_coupled_reference import trajectories as reference_trajectories

BOX = g.existing_box()
SETS = {n: g.test_trajectories(s['seed'], s['split'], BOX)[4] for n, s in g.KNOWN_SETS.items()}
REF = reference_trajectories()
FROZEN_V1_PROTOCOL_SHA256 = '65b00fd76a5fc28e2d05603dfd98e61efda413835947f71e28dac2156758776b'


def frames(rows):
    return np.array([r['users_m'] for r in rows])


class SplitTests(unittest.TestCase):
    def test_seeds_registered_and_distinct(self):
        seeds = {n: s['seed'] for n, s in g.KNOWN_SETS.items()}
        self.assertEqual(seeds, {'coupled_wire_test_v1': 20261106, 'coupled_wire_dev_v1': 20261107,
                                 'coupled_wire_test_v2': 20261108, 'coupled_wire_train_v2': 20261109})
        self.assertEqual(len(set(seeds.values())), 4)

    def test_sizes(self):
        for n, rows in SETS.items():
            self.assertEqual(len(rows), 30 * 16, n)
            self.assertEqual(sorted({r['trajectory'] for r in rows}), list(range(30)))

    def test_disjoint_from_reference_splits_and_each_other(self):
        groups = {f'ref_{sp}': [r for r in REF if r['split'] == sp] for sp in ('train', 'validation', 'pilot')}
        groups |= SETS
        names = list(groups)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                c = g.pairwise_checks(groups[a], groups[b])
                self.assertFalse(c['duplicate_start'], (a, b, c))
                self.assertFalse(c['duplicate_frame'], (a, b, c))
                self.assertGreater(c['min_frame_distance_m_max_over_users'], 1e-4, (a, b))

    def test_no_wire_collisions(self):
        for n, rows in SETS.items():
            x = frames(rows)
            self.assertGreater(np.linalg.norm(x[:, 0] - x[:, 1], axis=-1).min(), .03, n)

    def test_cross_set_helper_covers_all_other_sets(self):
        for n, s in g.KNOWN_SETS.items():
            cross = g.cross_set_checks(n, s['seed'], SETS[n], BOX)
            expected = (set(g.KNOWN_SETS) - {n} if n == 'coupled_wire_train_v2'
                        else set(g._LEGACY_KNOWN_SETS) - {n})
            self.assertEqual(set(cross), expected)

    def test_seed_registry_is_enforced(self):
        with self.assertRaises(ValueError):
            g.check_registered('coupled_wire_test_v1', 1, 'test')
        with self.assertRaises(ValueError):
            g.check_registered('something_else', 20261107, 'dev')
        with self.assertRaises(ValueError):
            g.check_registered('coupled_wire_dev_v1', 20261107, 'test')
        with self.assertRaises(ValueError):
            g.check_registered('coupled_wire_test_v2', 20261107, 'test')
        self.assertEqual(g.check_registered('coupled_wire_dev_v1', 20261107, 'dev')['split'], 'dev')

    def test_no_labels_in_rows(self):
        for rows in SETS.values():
            self.assertEqual(set(rows[0]), {'index', 'trajectory', 'step', 'time_s', 'split', 'users_m'})

    def test_default_protocol_only_has_frozen_v1_byte_hash(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / 'coupled_wire_test_v1'
            subprocess.run([sys.executable, str(ROOT / 'scripts/generate_coupled_test.py'), '--out', str(out),
                            '--protocol-only'], check=True, capture_output=True, cwd=ROOT,
                           env={'PYTHONPATH': str(ROOT / 'src'), 'PATH': '/usr/bin:/bin'})
            digest = hashlib.sha256((out / 'scenario.json').read_bytes()).hexdigest()
            self.assertEqual(digest, FROZEN_V1_PROTOCOL_SHA256)

    def test_only_indices_outside_protocol_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside this protocol'):
            g.select_rows(SETS['coupled_wire_dev_v1'][:2], {0, 999})

    def test_fine_mesh_rejects_test_split(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / 'coupled_wire_test_v2'
            src.mkdir()
            (src / 'scenario.json').write_text(json.dumps({'segments': 81, 'rows': SETS['coupled_wire_test_v2']}))
            with self.assertRaisesRegex(ValueError, 'needs the frozen matched_v2 protocol'):
                g.fine_protocol(src, 'test', 161)

    def test_fine_mesh_rejects_empty_split(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / 'coupled_wire_v1'
            src.mkdir()
            (src / 'scenario.json').write_text(json.dumps({'segments': 81, 'rows': SETS['coupled_wire_dev_v1']}))
            with self.assertRaisesRegex(ValueError, 'No source rows'):
                g.fine_protocol(src, 'validation', 161)

    def test_fine_output_cannot_alias_source_directory(self):
        source = ROOT / 'data/processed/coupled_wire_dev_v1'
        scenario = source / 'scenario.json'
        before = hashlib.sha256(scenario.read_bytes()).hexdigest()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_coupled_test.py'),
                                 '--out', str(source), '--fine-from', str(source), '--fine-split', 'dev',
                                 '--segments', '161'], capture_output=True, text=True, cwd=ROOT,
                                env={'PYTHONPATH': str(ROOT / 'src'), 'PATH': '/usr/bin:/bin'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must be separate', result.stderr)
        self.assertEqual(hashlib.sha256(scenario.read_bytes()).hexdigest(), before)
        self.assertFalse((source / 'generation_status.json').exists())

    def test_partial_generation_is_not_complete_and_resumes_exactly(self):
        class InlinePool:
            def __init__(self, workers):
                self.workers = workers
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def map(self, fn, items):
                return map(fn, items)

        calls = []
        def fake_work(args):
            row, out_str, segments = args
            out = Path(out_str)
            p = out / f"frame_{row['index']:04d}.npz"
            with p.open('wb') as f:
                np.savez_compressed(f, z=np.zeros((70, 70)), centers=np.zeros((70, 3)), lengths=np.ones(70))
            meta = row | {'segments_per_wire': segments, 'minimum_resistance_eigenvalue_ohm': 0.1,
                          'maximum_scattering_singular_value': 0.9, 'reciprocity_relative': 1e-10,
                          'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
            p.with_suffix('.json').write_text(json.dumps(meta))
            calls.append(row['index'])
            return {'index': row['index'], 'status': 'generated'}

        rows = [{'index': i, 'trajectory': i, 'step': 0, 'time_s': 0.0,
                 'split': 'dev', 'users_m': [[float(i), 0., 0.], [0., 0., 0.]]}
                for i in range(3)]
        identity = {'set_name': 'unit_test_set', 'segments': 81, 'protocol_sha256': 'protocol-A'}
        with tempfile.TemporaryDirectory() as t, \
             patch.object(g, 'ProcessPoolExecutor', InlinePool), patch.object(g, 'work', fake_work):
            out = Path(t)
            first = [(rows[0], str(out), 81, identity)]
            status = g.run(first, 1, out, expected_rows=rows, segments=81, identity=identity)
            self.assertEqual(status['status'], 'partial')
            self.assertEqual(status['missing_frame_indices'], [1, 2])
            self.assertEqual((out / 'generation_status.json').exists(), True)
            second = [(r, str(out), 81, identity) for r in rows]
            status = g.run(second, 1, out, expected_rows=rows, segments=81, identity=identity)
            self.assertEqual(status['status'], 'complete')
            self.assertEqual(status['verified_frame_indices'], [0, 1, 2])
            self.assertEqual(calls, [0, 1, 2])  # frame 0 was reused after hash and identity checks

    def test_resume_rejects_changed_protocol_identity_without_deleting_frames(self):
        class InlinePool:
            def __init__(self, workers): pass
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def map(self, fn, items): return map(fn, items)

        row = {'index': 0, 'trajectory': 0, 'step': 0, 'time_s': 0.0,
               'split': 'dev', 'users_m': [[0., 0., 0.], [1., 0., 0.]]}
        identity = {'set_name': 'unit_test_set', 'segments': 81, 'protocol_sha256': 'protocol-A'}
        def fake_work(args):
            r, out_str, segments = args
            p = Path(out_str) / 'frame_0000.npz'
            with p.open('wb') as f: np.savez_compressed(f, z=np.zeros((70, 70)), centers=np.zeros((70, 3)), lengths=np.ones(70))
            p.with_suffix('.json').write_text(json.dumps(r | {'segments_per_wire': segments,
                'minimum_resistance_eigenvalue_ohm': 0.1,
                'maximum_scattering_singular_value': 0.9, 'reciprocity_relative': 1e-10,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}))
            return {'index': 0}

        with tempfile.TemporaryDirectory() as t, \
             patch.object(g, 'ProcessPoolExecutor', InlinePool), patch.object(g, 'work', fake_work):
            out = Path(t)
            g.run([(row, str(out), 81, identity)], 1, out,
                  expected_rows=[row], segments=81, identity=identity)
            artifact = out / 'frame_0000.npz'
            before = artifact.read_bytes()
            changed = identity | {'protocol_sha256': 'protocol-B'}
            with self.assertRaisesRegex(ValueError, 'identity/expected frames differ'):
                g.run([], 1, out, expected_rows=[row], segments=81, identity=changed)
            self.assertEqual(artifact.read_bytes(), before)

    def test_resume_rejects_valid_hash_with_wrong_mesh_metadata(self):
        class InlinePool:
            def __init__(self, workers): pass
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def map(self, fn, items): return map(fn, items)

        calls = []
        row = {'index': 0, 'trajectory': 0, 'step': 0, 'time_s': 0.0,
               'split': 'dev', 'users_m': [[0., 0., 0.], [1., 0., 0.]]}
        identity = {'set_name': 'unit_test_set', 'segments': 161, 'protocol_sha256': 'protocol-A'}
        def fake_work(args):
            r, out_str, segments = args
            p = Path(out_str) / 'frame_0000.npz'
            with p.open('wb') as f: np.savez_compressed(f, z=np.zeros((70, 70)), centers=np.zeros((70, 3)), lengths=np.ones(70))
            p.with_suffix('.json').write_text(json.dumps(r | {'segments_per_wire': segments,
                'minimum_resistance_eigenvalue_ohm': 0.1,
                'maximum_scattering_singular_value': 0.9, 'reciprocity_relative': 1e-10,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}))
            calls.append(segments)
            return {'index': 0}

        with tempfile.TemporaryDirectory() as t, \
             patch.object(g, 'ProcessPoolExecutor', InlinePool), patch.object(g, 'work', fake_work):
            out = Path(t)
            g.run([(row, str(out), 161, identity)], 1, out,
                  expected_rows=[row], segments=161, identity=identity)
            sidecar = out / 'frame_0000.json'
            wrong_mesh = json.loads(sidecar.read_text())
            wrong_mesh['segments_per_wire'] = 81  # valid NPZ checksum, invalid source/mesh metadata
            sidecar.write_text(json.dumps(wrong_mesh))
            status = g.run([(row, str(out), 161, identity)], 1, out,
                           expected_rows=[row], segments=161, identity=identity)
            self.assertEqual(status['status'], 'complete')
            self.assertEqual(calls, [161, 161])


if __name__ == '__main__':
    unittest.main()
