import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import profile_pair_v2 as profile


class TinyNetwork:
    n = 3
    pairs = np.array([[0, 1], [0, 2], [1, 2]])

    def state(self, bits):
        return np.asarray(bits, dtype=np.int8)

    def score(self, fields):
        return np.asarray(fields).sum(axis=-1)

    def moves(self, state, pairs=False, subset=None):
        n = 2 if pairs else self.n
        return np.arange(n, dtype=float)

    def flip(self, state, indices):
        out = state.copy()
        out[np.asarray(indices, dtype=int)] ^= 1
        return out


class PairProfileTests(unittest.TestCase):
    def test_observer_counts_scores_candidates_scans_flips_and_restarts(self):
        observed = profile.TimedNetwork(TinyNetwork())
        observed.state([0, 0, 0])
        observed.moves(np.zeros(3), pairs=False)
        observed.moves(np.zeros(3), pairs=True)
        observed.score(np.ones((4, 2, 2)))
        observed.flip(np.zeros(3, dtype=np.int8), [1])
        observed.state([1, 0, 1])
        counts = observed.summary()
        self.assertEqual(counts["calls"]["state"], 2)
        self.assertEqual(counts["restart_state_calls"], 1)
        self.assertEqual(counts["calls"]["single_scan"], 1)
        self.assertEqual(counts["candidate_counts"]["single_scan"], 3)
        self.assertEqual(counts["candidate_counts"]["pair_scan"], 3)
        self.assertEqual(counts["candidate_counts"]["objective_candidates_scored"], 4)
        self.assertEqual(counts["calls"]["flip"], 1)
        self.assertTrue(all(v >= 0 for v in counts["inclusive_time_ms"].values()))

    def test_only_registered_development_frame_manifest_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data/processed/coupled_wire_dev_v1"
            data.mkdir(parents=True)
            scenario = {"development_set": True, "split_label": "dev", "untouched_test": False,
                        "segments": 81, "set_name": "coupled_wire_dev_v1",
                        "rows": [{"index": 2, "split": "dev", "trajectory": 1, "step": 2}]}
            (data / "scenario.json").write_text(json.dumps(scenario))
            frame = data / "frame_0002.npz"
            np.savez(frame, z=np.eye(2, dtype=np.complex128))
            digest = hashlib.sha256(frame.read_bytes()).hexdigest()
            (data / "frame_0002.json").write_text(json.dumps({
                "index": 2, "trajectory": 1, "step": 2, "split": "dev",
                "segments_per_wire": 81, "sha256": digest,
            }))
            with patch.object(profile, "ROOT", root):
                loaded, metas, readiness_hash = profile._verify_dev_directory(data)
            self.assertEqual(loaded["split_label"], "dev")
            self.assertEqual(list(metas), [2])
            self.assertIsNone(readiness_hash)
            sidecar = data / "frame_0002.json"
            metadata = json.loads(sidecar.read_text())
            metadata["trajectory"] = 4
            sidecar.write_text(json.dumps(metadata))
            with patch.object(profile, "ROOT", root), self.assertRaisesRegex(ValueError, "identity differs"):
                profile._verify_dev_directory(data)
            scenario["split_label"] = "test"
            (data / "scenario.json").write_text(json.dumps(scenario))
            with patch.object(profile, "ROOT", root), self.assertRaisesRegex(ValueError, "development_set"):
                profile._verify_dev_directory(data)

    def test_indices_are_explicit_unique_and_nonnegative(self):
        self.assertEqual(profile.csv_ints("1,4,8"), [1, 4, 8])
        for value in ("", "1,1", "-1,2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                profile.csv_ints(value)

    def test_profile_uses_matched_config_not_legacy_dispatch(self):
        config = object()
        with patch.object(profile, "CoupledNetwork", return_value=TinyNetwork()), \
                patch.object(profile, "coupled_search", return_value=(np.array([0, 1]), 2.5, 9, {})) as search:
            result, _ = profile._profile_once(np.zeros((1, 1)), np.zeros(2), 10.0, 7, config, True)
        self.assertEqual(result["reported_search_evaluations"], 9)
        self.assertFalse(search.call_args.kwargs["legacy"])
        self.assertIs(search.call_args.kwargs["config"], config)
        self.assertEqual(search.call_args.kwargs["memory"], ())


if __name__ == "__main__":
    unittest.main()
