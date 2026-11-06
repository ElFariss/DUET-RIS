import sys
import tempfile
import unittest
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_improvement_campaign import campaign_source_identity, validate_validation_rows
from atomwise_ris.models.forecast import require_forecast_checkpoint
import select_matched_budget as selection


class CampaignValidationGate(unittest.TestCase):
    def rows(self):
        return [
            {'method': method, 'seed': seed, 'budget_ms': budget, 'index': index,
             'split': 'validation', 'search_config': 'medium', 'deadline_missed': False}
            for method in ('greedy', 'population_ga')
            for seed in (7, 19)
            for budget in (1.0, 5.0, 10.0, 50.0, 100.0)
            for index in (2, 4)
        ]

    def test_exact_method_seed_budget_and_frame_grid_passes(self):
        validate_validation_rows(self.rows(), ('greedy', 'population_ga'), (7, 19),
                                 (1, 5, 10, 50, 100), (2, 4), 10, selected_budget=10)

    def test_missing_seed_frame_or_duplicate_frame_is_rejected(self):
        rows = self.rows()
        with self.assertRaises(RuntimeError):
            validate_validation_rows(rows[:-1], ('greedy', 'population_ga'), (7, 19),
                                     (1, 5, 10, 50, 100), (2, 4), 10)
        duplicate = rows + [dict(rows[0])]
        with self.assertRaises(RuntimeError):
            validate_validation_rows(duplicate, ('greedy', 'population_ga'), (7, 19),
                                     (1, 5, 10, 50, 100), (2, 4), 10)

    def test_primary_misses_preserved_and_clean_50ms_fallback_is_selected(self):
        rows = self.rows()
        for row in rows:
            if row['budget_ms'] == 10.0:
                row['deadline_missed'] = True
        selected, feasibility = validate_validation_rows(
            rows, ('greedy', 'population_ga'), (7, 19), (1, 5, 10, 50, 100), (2, 4), 10,
            selected_budget=50)
        self.assertEqual(selected, 50.0)
        self.assertTrue(feasibility['10.0']['misses_by_method']['greedy'])
        self.assertFalse(feasibility['50.0']['misses_by_method']['greedy'])
        self.assertTrue(all(row['deadline_missed'] for row in rows if row['budget_ms'] == 10.0))

    def test_50ms_miss_rejects_50_selection_and_chooses_clean_100ms(self):
        rows = self.rows()
        for row in rows:
            if row['budget_ms'] in (10.0, 50.0):
                row['deadline_missed'] = True
        with self.assertRaisesRegex(RuntimeError, 'does not match validation rule'):
            validate_validation_rows(rows, ('greedy', 'population_ga'), (7, 19),
                                     (1, 5, 10, 50, 100), (2, 4), 10, selected_budget=50)
        selected, _ = validate_validation_rows(rows, ('greedy', 'population_ga'), (7, 19),
            (1, 5, 10, 50, 100), (2, 4), 10, selected_budget=100)
        self.assertEqual(selected, 100.0)

    def test_wrong_selected_budget_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'does not match validation rule'):
            validate_validation_rows(self.rows(), ('greedy', 'population_ga'), (7, 19),
                (1, 5, 10, 50, 100), (2, 4), 10, selected_budget=50)

    def test_locked_50ms_primary_cannot_fall_back_to_clean_10ms(self):
        rows=self.rows()
        with self.assertRaisesRegex(RuntimeError,'does not match validation rule'):
            validate_validation_rows(rows,('greedy','population_ga'),(7,19),
                (1,5,10,50,100),(2,4),50,selected_budget=10)
        selected,feasible=validate_validation_rows(rows,('greedy','population_ga'),(7,19),
            (1,5,10,50,100),(2,4),50,selected_budget=50)
        self.assertEqual(selected,50.0)
        self.assertTrue(feasible['10.0']['feasible'])

    def test_locked_50ms_primary_falls_forward_to_100ms_on_miss(self):
        rows=self.rows()
        for row in rows:
            if row['budget_ms']==50.0:row['deadline_missed']=True
        with self.assertRaisesRegex(RuntimeError,'does not match validation rule'):
            validate_validation_rows(rows,('greedy','population_ga'),(7,19),
                (1,5,10,50,100),(2,4),50,selected_budget=50)
        selected,_=validate_validation_rows(rows,('greedy','population_ga'),(7,19),
            (1,5,10,50,100),(2,4),50,selected_budget=100)
        self.assertEqual(selected,100.0)

    def test_selection_rule_text_records_preferred_and_locked_primary(self):
        text=selection.selection_rule_text(10,50,(1,5,10,50,100))
        self.assertIn('Preferred budget 10 ms',text)
        self.assertIn('locked primary budget 50 ms',text)
        self.assertIn('100 ms',text)

    def test_partial_budget_grid_is_rejected(self):
        rows = [row for row in self.rows() if row['budget_ms'] != 50.0]
        with self.assertRaises(RuntimeError):
            validate_validation_rows(rows, ('greedy', 'population_ga'), (7, 19),
                (1, 5, 10, 50, 100), (2, 4), 10)

    def test_campaign_identity_tracks_checkpoint_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / 'train-validation.npz'
            data.write_bytes(b'data')
            model = root / 'models' / 'mlp_seed7' / 'best.pt'
            model.parent.mkdir(parents=True)
            model.write_bytes(b'weights-a')
            before = campaign_source_identity('coupled', 'a' * 64, data, root)
            model.write_bytes(b'weights-b')
            after = campaign_source_identity('coupled', 'a' * 64, data, root)
            self.assertNotEqual(before['checkpoint_sha256'], after['checkpoint_sha256'])

    def test_forecast_checkpoint_semantics_fail_closed(self):
        with self.assertRaises(RuntimeError):
            require_forecast_checkpoint({'state_dict': {}})
        with self.assertRaises(RuntimeError):
            require_forecast_checkpoint({'architecture_version': 'legacy_incremental_residual'})
        self.assertIsNone(require_forecast_checkpoint({'architecture_version': 'linear_velocity_residual_v2'}))

    def test_direct_test_benchmarks_reject_one_row_per_method_freeze(self):
        protocol, protocol_hash = selection.load_protocol()
        methods = selection.protocol_methods(protocol)
        for script, extra, filename in (
            ('benchmark.py', (), 'benchmark_validation.jsonl'),
            ('benchmark_coupled.py', ('--mode', 'spatial'), 'benchmark_spatial_validation.jsonl'),
        ):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                run = Path(temp)
                rows = [{'method': m, 'seed': 7, 'budget_ms': 10.0, 'index': 0,
                         'trajectory': 0, 'split': 'validation', 'search_config': 'medium',
                         'deadline_missed': False} for m in methods]
                val = run / filename
                val.write_text(''.join(json.dumps(row) + '\n' for row in rows))
                checkpoint_hash = selection.checkpoint_hashes(run)
                sidecar = {
                    'protocol_sha256': protocol_hash,
                    'conditional_pair_policy': False,
                    'selection_helper_sha256': selection.sha256_file(ROOT / 'scripts' / 'select_matched_budget.py'),
                    'campaign_script_sha256': selection.sha256_file(ROOT / 'scripts' / 'run_improvement_campaign.py'),
                    'frozen_code_sha256': selection.frozen_code_hashes(),
                    'checkpoint_sha256': checkpoint_hash,
                }
                if script == 'benchmark.py':
                    sidecar['scenario_sha256'] = selection.sha256_file(ROOT / 'data/processed/munich_specular_v3/scenario.npz')
                    sidecar['response_sha256'] = selection.sha256_file(ROOT / 'data/processed/responses/opensourceris_v1.csv')
                else:
                    sidecar['data_sha256'] = selection.sha256_file(ROOT / 'data/processed/coupled_wire_v1/dataset.npz')
                    sidecar['physics_gate_sha256'] = selection.sha256_file(ROOT / 'outputs/runs/coupled_wire_v1/physics_gate.json')
                (run / filename.replace('.jsonl', '.json')).write_text(json.dumps(sidecar))
                (run / 'budget_selection.json').write_text(json.dumps({
                    'selected_ms': protocol['primary_budget_ms'], 'protocol_sha256': protocol_hash,
                    'protocol_primary_ms': protocol['primary_budget_ms'],
                    'protocol_preferred_ms': protocol.get('preferred_budget_ms', protocol['primary_budget_ms']),
                    'budget_lock': protocol.get('budget_lock'),
                    'input_hashes': {filename: selection.sha256_file(val)},
                    'code_sha256': selection.frozen_code_hashes(),
                    'checkpoint_sha256': checkpoint_hash,
                    'validation_feasibility': {'10.0': {'complete_coverage': True, 'feasible': True}},
                }))
                env = dict(os.environ, PYTHONPATH=str(ROOT / 'src') + ':' + str(ROOT / 'scripts'))
                cmd = [sys.executable, str(ROOT / 'scripts' / script), '--matched', '--split', 'test',
                       '--run', temp, '--test-data', str(run / 'not-yet-created-test-data')]
                cmd += list(extra)
                completed = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=60)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn('every exact frame once', completed.stderr)


if __name__ == '__main__':
    unittest.main()
