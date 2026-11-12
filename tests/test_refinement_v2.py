"""Pure-contract checks for the predeclared 201-segment stress diagnostic."""
import unittest

from scripts.audit_refinement_v2 import (
    COARSE_SCORE_ABS_TOL_BPSHZ,
    SELECTED_INDICES,
    action_hash,
    mesh_ratio,
    summarize,
)


class TestRefinementV2(unittest.TestCase):
    def test_preselected_frames_and_exact_coarse_reproduction_tolerance(self):
        self.assertEqual(SELECTED_INDICES, (32, 96, 160, 174))
        self.assertEqual(COARSE_SCORE_ABS_TOL_BPSHZ, 1e-7)

    def test_201_segments_satisfies_stated_ek_ratio_but_241_does_not(self):
        safe = mesh_ratio(0.024, 0.00005, 201)
        too_fine_for_stated_ratio = mesh_ratio(0.024, 0.00005, 241)
        self.assertGreater(safe["segment_length_to_radius"], 2.0)
        self.assertLess(too_fine_for_stated_ratio["segment_length_to_radius"], 2.0)
        self.assertAlmostEqual(safe["segment_length_to_radius"], 480 / 201)

    def test_action_hash_requires_a_binary_64_cell_action(self):
        self.assertEqual(len(action_hash([0] * 64)), 64)
        with self.assertRaises(ValueError):
            action_hash([0] * 63)
        with self.assertRaises(ValueError):
            action_hash([2] + [0] * 63)

    def test_summarizer_reports_paired_shifts_without_pass_threshold(self):
        rows = []
        frame_trajectory = {32: 2, 96: 6, 160: 10, 174: 10}
        for index, trajectory in frame_trajectory.items():
            for method, coarse, fine161, fine201 in (
                ("a", 1.0, 1.1, 1.0),
                ("b", 2.0, 1.9, 2.1),
            ):
                rows.append({
                    "method": method, "seed": 7, "index": index, "trajectory": trajectory,
                    "action_sha256": method, "on_count": int(method == "b"),
                    "coarse_rate_bpshz": coarse, "rate_161_bpshz": fine161,
                    "rate_201_bpshz": fine201, "delta_81_to_161_bpshz": fine161 - coarse,
                    "delta_161_to_201_bpshz": fine201 - fine161,
                    "delta_81_to_201_bpshz": fine201 - coarse,
                    "abs_delta_81_to_161_bpshz": abs(fine161 - coarse),
                    "abs_delta_161_to_201_bpshz": abs(fine201 - fine161),
                })
        result = summarize(rows)
        self.assertEqual(result["n_trajectory_clusters"], 3)
        self.assertEqual(result["paired_method_order_reversals"]["161_vs_201"]["reversals"], 0)
        self.assertAlmostEqual(result["max_abs_161_to_201_bpshz"], 0.2)
        self.assertEqual(result["per_frame"]["161_to_201"]["32"]["n_unique_actions"], 2)
        self.assertIn("scope_note", result)


if __name__ == "__main__":
    unittest.main()
