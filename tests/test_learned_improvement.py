import unittest
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

from atomwise_ris.models import EditPolicy
from atomwise_ris.models.coupled_policy import CoupledPolicy
from atomwise_ris.models.forecast import predict
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from train_improvement import is_better, selection_value
from train_coupled_improvement import recover_stages


class ConstantResidual(nn.Module):
    def forward(self, x):
        result = torch.zeros((len(x), 2), dtype=x.dtype, device=x.device)
        result[:, 0] = 1.
        return result


class LearnedImprovement(unittest.TestCase):
    def test_checkpoint_selection_is_strict_and_deterministic(self):
        ranking = {'all': {'top5_target_mass': .2},
                   'first': {'top5_target_mass': .3},
                   'second': {'top5_target_mass': .1}}
        self.assertAlmostEqual(selection_value('balanced_top5_target_mass', 4., ranking), .2)
        self.assertAlmostEqual(selection_value('validation_top5_target_mass', 4., ranking), .2)
        self.assertEqual(selection_value('validation_cross_entropy', 4., ranking), 4.)
        self.assertFalse(is_better('balanced_top5_target_mass', .2, .2))
        self.assertFalse(is_better('balanced_top5_target_mass', .19, .2))
        self.assertTrue(is_better('balanced_top5_target_mass', .21, .2))
        self.assertFalse(is_better('validation_cross_entropy', 4., 4.))
        self.assertTrue(is_better('validation_cross_entropy', 3.9, 4.))

    def test_coupled_stage_recovery_requires_weight_marker_mask_agreement(self):
        x = np.zeros((2, 8, 16), dtype=np.float32)
        mask = np.zeros((2, 8), dtype=bool)
        weight = np.array([1., .25], dtype=np.float32)
        x[1, 3, -1] = 1.
        mask[1, 3] = True
        np.testing.assert_array_equal(recover_stages(x, mask, weight), ['first', 'conditional'])
        mask[1, 3] = False
        with self.assertRaises(ValueError):
            recover_stages(x, mask, weight)

    def test_new_policies_start_at_analytical_ranking(self):
        torch.set_num_threads(1)
        torch.manual_seed(11)
        for kind in ('mlp', 'attention'):
            x = torch.randn(2, 8, 30)
            analytical = torch.randn(2, 8)
            model = EditPolicy(30, kind).eval()
            coupled = CoupledPolicy(kind=kind).eval()
            coupled_x = torch.randn(2, 8, 16)
            with torch.inference_mode():
                torch.testing.assert_close(model(x, analytical), analytical)
                torch.testing.assert_close(coupled(coupled_x, analytical), analytical)
            infer = model.callable_cpu()
            np.testing.assert_allclose(infer(x[0].numpy(), analytical[0].numpy()),
                                       analytical[0].numpy(), atol=0., rtol=0.)

    def test_temporal_forecast_adds_diagonal_residual_once(self):
        history = np.zeros((4, 2, 2), dtype=np.complex128)
        original = history.copy()
        upper = np.triu_indices(2)
        scaling = (np.zeros(3), np.ones(3), upper, np.ones(3, dtype=bool))
        forecast = predict(history, 'gru', ConstantResidual(), scaling)
        expected = np.ones((2, 2), dtype=np.complex128)
        np.testing.assert_allclose(forecast, expected, atol=1e-6)
        np.testing.assert_array_equal(history, original)


if __name__ == '__main__':
    unittest.main()
