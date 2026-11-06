import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from atomwise_ris.models.coupled_policy import LinkGRU
from atomwise_ris.models.forecast import predict, require_forecast_checkpoint
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import benchmark_temporal_forecast as bench


class FakeNetwork:
    def __init__(self, z, loads, w=None):
        self.z = np.asarray(z)
        self.w = np.eye(4, dtype=np.complex128) if w is None else w

    def channel(self, bits):
        return np.eye(4, dtype=np.complex128) * (1 + int(np.sum(bits)))

    def score(self, fields):
        return float(np.real(np.trace(fields)))


class LinearForecastModel(torch.nn.Module):
    def forward(self, x):
        return 2 * x[:, -1] - x[:, -2]


class TemporalForecastTests(unittest.TestCase):
    def test_velocity_residual_zero_init_is_linear_and_does_not_mutate_input(self):
        torch.set_num_threads(1)
        torch.manual_seed(4)
        model = LinkGRU().eval()
        history = torch.arange(5 * 6 * 2, dtype=torch.float32).reshape(5, 6, 2)
        original = history.clone()
        with torch.inference_mode():
            prediction = model(history)
        torch.testing.assert_close(prediction, 2 * history[:, -1] - history[:, -2], atol=0., rtol=0.)
        torch.testing.assert_close(history, original, atol=0., rtol=0.)

    def test_causal_forecasts_leave_history_unchanged_and_persistence_is_last_observation(self):
        upper = np.triu_indices(2)
        history = np.zeros((4, 2, 2), dtype=np.complex128)
        history[:, 0, 0] = np.arange(4)
        history[:, 1, 1] = np.arange(4) * 2
        original = history.copy()
        persistence = predict(history, "persistence")
        np.testing.assert_array_equal(persistence, history[-1])
        linear = predict(history, "linear")
        np.testing.assert_array_equal(linear, 2 * history[-1] - history[-2])
        np.testing.assert_array_equal(history, original)
        # Earlier context may vary, but no future matrix is an input to the causal API.
        changed_old = history.copy()
        changed_old[0] += 100
        np.testing.assert_array_equal(predict(history, "linear"), predict(changed_old, "linear"))

    def test_forecast_guard_requires_explicit_v2_provenance(self):
        require_forecast_checkpoint({"architecture_version": LinkGRU.architecture_version})
        with self.assertRaises(RuntimeError):
            require_forecast_checkpoint({"state_dict": {}})
        with self.assertRaises(RuntimeError):
            require_forecast_checkpoint({"architecture_version": "legacy_gru"})
        checkpoint = {"architecture_version": LinkGRU.architecture_version, "kind": "gru", "seed": 19}
        bench.validate_gru_checkpoint(checkpoint, 19)
        with self.assertRaises(RuntimeError):
            bench.validate_gru_checkpoint({**checkpoint, "kind": "mlp"}, 19)
        with self.assertRaises(RuntimeError):
            bench.validate_gru_checkpoint(checkpoint, 7)

    def test_validation_history_is_contiguous_and_stays_in_trajectory(self):
        ds = {"z": np.zeros((8, 2, 2)), "trajectory": np.array([0] * 4 + [1] * 4),
              "step": np.array([0, 1, 2, 3, 0, 1, 2, 3])}
        with self.assertRaises(ValueError):
            bench.validate_history_rows(ds, [5])
        ds["trajectory"][:] = 0
        ds["step"][:] = np.arange(8)
        rows = bench.validate_history_rows(ds, [4, 5])
        self.assertEqual(rows[0]["history_indices"], [0, 1, 2, 3])

    def test_all_forecasts_share_stale_precoder_and_empty_memory_pair_search(self):
        calls = []

        def fake_search(ev, method, deadline, seed, **kwargs):
            calls.append((ev.w, method, kwargs["memory"], kwargs["policy"]))
            bits = np.zeros(4, dtype=np.int8)
            value = ev.score(ev.channel(bits) @ ev.w)
            return bits, value, 1, {"pair": 0.01}

        z = np.repeat(np.eye(10, dtype=np.complex128)[None], 5, axis=0)
        z[4] *= 2
        upper = np.triu_indices(10)
        scaling = (np.zeros(len(upper[0])), np.ones(len(upper[0])), upper,
                   np.ones(len(upper[0]), dtype=bool))
        for forecast in bench.FORECASTS:
            bench.timed_action(z, 4, forecast, LinearForecastModel(), scaling,
                               np.ones(4), 100., 7, object(),
                               network_factory=FakeNetwork, search_fn=fake_search)
        self.assertEqual(len(calls), len(bench.FORECASTS))
        self.assertEqual({method for _, method, _, _ in calls}, {"pair"})
        self.assertTrue(all(memory == () and policy is None for _, _, memory, policy in calls))
        first_w = calls[0][0]
        for w, *_ in calls[1:]:
            np.testing.assert_array_equal(w, first_w)


if __name__ == "__main__":
    unittest.main()
