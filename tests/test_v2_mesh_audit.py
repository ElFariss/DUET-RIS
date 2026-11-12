import unittest
import json
from pathlib import Path

from scripts.audit_v2_mesh import load_switch_loads, summarize, validate_frozen_artifacts


class FrozenGridTests(unittest.TestCase):
    def _fixture(self):
        protocol = {
            "methods": {"baselines": ["base"], "variant": "synthetic test method"},
            "seeds": [3], "budgets_ms": [50], "primary_budget_ms": 50,
        }
        metadata = {
            "protocol_sha256": "p", "frozen_code_sha256": {"x": "c"},
            "checkpoint_sha256": {"m": "k"}, "args": {
                "split": "validation", "mode": "spatial", "test_data": None,
            }, "data_sha256": "d", "physics_gate_sha256": "g",
        }
        selection = {
            "protocol_sha256": "p", "selected_ms": 50,
            "protocol_primary_ms": 50, "protocol_preferred_ms": 10,
            "input_hashes": {"benchmark_spatial_validation.jsonl": "raw"},
            "code_sha256": {"x": "c"}, "checkpoint_sha256": {"m": "k"},
            "budget_lock": {"locked_utc": "predeclared"},
        }
        rows = [
            {"mode": "spatial", "split": "validation", "method": m,
             "seed": 3, "budget_ms": 50, "index": i, "bits": [0] * 64}
            for m in ("base", "variant") for i in (2, 7)
        ]
        return rows, metadata, selection, protocol

    def test_exact_selected_grid_passes(self):
        rows, metadata, selection, protocol = self._fixture()
        methods, seeds, indices, selected = validate_frozen_artifacts(
            rows, metadata, selection, protocol, "p", "raw", [2, 7])
        self.assertEqual(methods, ["base", "variant"])
        self.assertEqual(seeds, [3])
        self.assertEqual(indices, [2, 7])
        self.assertEqual(len(selected), 4)

    def test_duplicate_and_wrong_split_are_rejected(self):
        rows, metadata, selection, protocol = self._fixture()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_frozen_artifacts(rows + [rows[0]], metadata, selection, protocol, "p", "raw", [2, 7])
        rows[0]["split"] = "test"
        with self.assertRaisesRegex(ValueError, "non-spatial or non-validation"):
            validate_frozen_artifacts(rows, metadata, selection, protocol, "p", "raw", [2, 7])

    def test_fallback_and_hash_mismatches_fail_closed(self):
        rows, metadata, selection, protocol = self._fixture()
        selection["selected_ms"] = 10
        with self.assertRaisesRegex(ValueError, "did not select 50"):
            validate_frozen_artifacts(rows, metadata, selection, protocol, "p", "raw", [2, 7])
        selection["selected_ms"] = 50
        with self.assertRaisesRegex(ValueError, "hash differs"):
            validate_frozen_artifacts(rows, metadata, selection, protocol, "p", "wrong", [2, 7])


class SummaryTests(unittest.TestCase):
    def test_cluster_summary_and_paired_rank_reversal_are_reported(self):
        records = []
        # Each frame/seed pairs both methods. Fine-mesh scoring reverses the
        # coarse ordering while retaining three explicit trajectory clusters.
        for trajectory, index in [(2, 32), (6, 96), (10, 160)]:
            for seed in (3, 7):
                for method, coarse, fine, on in (
                    ("base", 5.0, 4.0, 12), ("variant", 4.0, 5.0, 28),
                ):
                    records.append({
                        "method": method, "seed": seed, "index": index,
                        "trajectory": trajectory, "on_count": on,
                        "coarse_rate_bpshz": coarse,
                        "fine_fixed_w_rate_bpshz": fine,
                        "delta_fixed_w_bpshz": fine - coarse,
                        "fine_recomputed_w_rate_bpshz": fine + 0.1,
                        "delta_fine_w_bpshz": fine + 0.1 - coarse,
                    })
        summary = summarize(records, ["base", "variant"], bootstrap_samples=100, bootstrap_seed=2)
        self.assertEqual(summary["trajectory_clusters"], [2, 6, 10])
        self.assertEqual(summary["pairwise_order_reversals_fixed_w"]["fraction"], 1.0)
        self.assertEqual(summary["methods"]["base"]["n_independent_trajectory_clusters"], 3)
        self.assertEqual(summary["methods"]["base"]["trajectory_mean_delta_fixed_w_bpshz"]["2"], -1.0)
        self.assertEqual(summary["methods"]["variant"]["mean_delta_fixed_w_bpshz"], 1.0)


class PhysicsGateTests(unittest.TestCase):
    def test_current_gate_encodes_two_shared_switch_states(self):
        root = Path(__file__).resolve().parents[1]
        gate = json.loads((root / "outputs/runs/coupled_wire_v1/physics_gate.json").read_text())
        loads = load_switch_loads(gate)
        self.assertEqual(loads.shape, (2,))
        self.assertTrue((loads.real == [1.0, 1.0]).all())
        self.assertEqual(loads.imag.shape, (2,))

    def test_gate_must_not_be_misread_as_per_cell_load_table(self):
        gate = {"loads_real_ohm": [1.0] * 64, "loads_imag_ohm": [0.0] * 64}
        with self.assertRaisesRegex(ValueError, "OFF/ON"):
            load_switch_loads(gate)


if __name__ == "__main__":
    unittest.main()
