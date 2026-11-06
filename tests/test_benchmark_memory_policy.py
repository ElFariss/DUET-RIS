import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.benchmark_coupled import should_store_memory


class CoupledBenchmarkMemoryPolicyTests(unittest.TestCase):
    def test_baselines_and_no_memory_ablations_never_write_memory(self):
        for method in (
            'greedy', 'pair', 'random', 'blind_pair', 'population_ga',
            'analytical_no_memory_ga', 'attention_no_memory_ga',
        ):
            with self.subTest(method=method):
                self.assertFalse(should_store_memory(method))

    def test_memory_enabled_controllers_keep_memory_updates(self):
        for method in ('memory_ga', 'analytical_ga', 'mlp_ga', 'attention_ga',
                       'attention_no_physics_ga'):
            with self.subTest(method=method):
                self.assertTrue(should_store_memory(method))


if __name__ == '__main__':
    unittest.main()
