"""Tests for the ME-GA / GA-RISC reimplementation (src/atomwise_ris/optimization/me_ga.py)."""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock
from time import perf_counter_ns

import numpy as np

from atomwise_ris.evaluation.evaluator import Evaluator
from atomwise_ris.physics.network import CoupledNetwork
from atomwise_ris.optimization import me_ga, coupled_search
from atomwise_ris.optimization.me_ga import (MEGAParams, CoupledPopulation, SpecularPopulation, run_me_ga,
    adaptive_rates, replacement_fraction, effectiveness, store_probability, restore_probability,
    population_variance, make_children)
from atomwise_ris.optimization.search import (Memory, search, GA_METHODS, ME_GA_METHODS, variant_spec)

ROOT = Path(__file__).resolve().parents[1]


def specular_fixture(n=16, seed=5):
    r = np.random.default_rng(seed); k = 2
    return Evaluator(r.normal(size=(k, k)) + 1j * r.normal(size=(k, k)),
                     (r.normal(size=(n, k, k)) + 1j * r.normal(size=(n, k, k))) / n,
                     np.array([-.55 - .09j, .80 + .13j]), .1, r.normal(size=(n, 3)))


def coupled_fixture(n=12, seed=9):
    r = np.random.default_rng(seed); m = n + 6
    v = r.normal(size=(m, m)); x = r.normal(size=(m, m))
    z = v @ v.T + 10 * np.eye(m) + 1j * (x + x.T)
    return CoupledNetwork(z, np.array([10 + 60j, 10 - 60j]))


def small(**kw):
    base = dict(gamma=20, V=6, chunk=8)
    base.update(kw); return MEGAParams(**base)


def direct_coupled(ev, bits):
    return float(ev.score(ev.state(np.asarray(bits, dtype=np.int8)).field))


class FakeClockPop:
    """Population evaluator on a fake clock: each score() call advances time by `cost_ns`."""
    def __init__(self, n, clock, cost_ns=1_000_000, slow_call=None):
        self.n = n; self.clock = clock; self.cost = cost_ns; self.calls = 0; self.slow_call = slow_call; self.kind = 'fake'
    def score(self, bits, base=None):
        self.calls += 1
        self.clock[0] += 100_000_000 if self.calls == self.slow_call else self.cost
        return np.asarray(bits, dtype=float).sum(axis=1) + 1.0
GOLDEN = {
 "specular:memory_ga:3": [
  "11011000100011001000",
  "1.6259094126090214",
  900,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:memory_ga:11": [
  "11011000100011001000",
  "1.6259094126090214",
  940,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:uniform_ga:3": [
  "11011000100011001000",
  "1.6259094126090219",
  900,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:uniform_ga:11": [
  "11011000100010100000",
  "1.6858882985893677",
  1218,
  [
   "11011000100010100000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:analytical_ga:3": [
  "11011000100011001000",
  "1.6259094126090214",
  900,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:analytical_ga:11": [
  "11011000100011001000",
  "1.6259094126090214",
  940,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:analytical_no_memory_ga:3": [
  "11011000100011001000",
  "1.6259094126090214",
  898,
  [
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:analytical_no_memory_ga:11": [
  "11011000100011001000",
  "1.6259094126090214",
  938,
  [
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:mlp_ga:3": [
  "11011000100011001000",
  "1.6259094126090214",
  900,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "specular:mlp_ga:11": [
  "11011000100011001000",
  "1.6259094126090214",
  940,
  [
   "11011000100011001000",
   "10010010001001000110",
   "11001101010111011010"
  ]
 ],
 "coupled:memory_ga:3": [
  "00000000000000000000",
  "17.141480280192926",
  2597
 ],
 "coupled:memory_ga:11": [
  "00000000000000000000",
  "17.141480280192926",
  2497
 ],
 "coupled:uniform_ga:3": [
  "00000000000000000000",
  "17.141480280193104",
  2637
 ],
 "coupled:uniform_ga:11": [
  "00000000000000000000",
  "17.141480280192972",
  2297
 ],
 "coupled:analytical_ga:3": [
  "00000000000000000000",
  "17.141480280192926",
  2597
 ],
 "coupled:analytical_ga:11": [
  "00000000000000000000",
  "17.141480280192926",
  2497
 ],
 "coupled:analytical_no_memory_ga:3": [
  "00000000000000000000",
  "17.141480280192926",
  1115
 ],
 "coupled:analytical_no_memory_ga:11": [
  "00000000000000000000",
  "17.141480280192926",
  1015
 ],
 "coupled:mlp_ga:3": [
  "00000000000000000000",
  "17.141480280192926",
  2597
 ],
 "coupled:mlp_ga:11": [
  "00000000000000000000",
  "17.141480280192926",
  2497
 ]
}


class OperatorRangeTests(unittest.TestCase):
    def test_adaptive_rates_stay_in_declared_ranges(self):
        p = MEGAParams()
        for sigma in np.linspace(-0.5, 2.0, 51):
            rho, psi = adaptive_rates(sigma, p)
            self.assertTrue(p.rho[0] - 1e-12 <= rho <= p.rho[1] + 1e-12)
            self.assertTrue(p.psi[0] - 1e-12 <= psi <= p.psi[1] + 1e-12)
            self.assertTrue(0 <= replacement_fraction(sigma, p) <= p.nu_max + 1e-12)
        np.testing.assert_allclose(adaptive_rates(1.0, p), (p.rho[0], p.psi[1]), atol=1e-15)   # diverse population: little mutation, much crossover
        np.testing.assert_allclose(adaptive_rates(0.0, p), (p.rho[1], p.psi[0]), atol=1e-15)
        self.assertEqual(replacement_fraction(1.0, p), 0.0)
        self.assertAlmostEqual(replacement_fraction(0.0, p), p.nu_max)

    def test_normalised_binary_variance(self):
        rng = np.random.default_rng(0)
        self.assertAlmostEqual(population_variance(np.zeros((10, 8))), 0.0)
        self.assertAlmostEqual(population_variance(np.vstack([np.zeros((5, 8)), np.ones((5, 8))])), 1.0)
        self.assertLess(abs(population_variance(rng.integers(0, 2, (5000, 40))) - 1.0), 0.02)

    def test_effectiveness_eq15(self):
        phi = [4., 3., 2., 2.]
        self.assertAlmostEqual(effectiveness(phi, 3, 3), (2 - 2) / 2 + (2 - 3) / 4 + (2 - 4) / 8)
        self.assertAlmostEqual(effectiveness(phi, 1, 3), (3 - 4) / 2)       # v < W: window truncated
        self.assertAlmostEqual(effectiveness([1., 2.], 1, 3), 0.5)          # worsening best gives Theta > 0

    def test_probabilities_stay_in_range_for_every_theta_history(self):
        rng = np.random.default_rng(3)
        for rule in ('magnitude', 'negative_extreme', 'literal_clipped'):
            p = MEGAParams(kappa_rule=rule)
            for _ in range(300):
                thetas = list(rng.normal(size=int(rng.integers(1, 12))) * 10.0 ** rng.integers(-4, 2))
                if rng.random() < 0.2: thetas[0] = 0.0
                th = thetas[-1]
                if th >= 0:
                    self.assertTrue(0 <= store_probability(th, max(thetas), p) <= p.beta_max)
                else:
                    k = restore_probability(th, thetas, p)
                    self.assertTrue(0 <= k <= p.kappa_max, (rule, thetas, k))
        p = MEGAParams()
        self.assertEqual(store_probability(0.0, 0.0, p), 0.0)               # theta_max = 0: documented 0
        self.assertAlmostEqual(store_probability(2.0, 2.0, p), p.beta_max)
        self.assertAlmostEqual(store_probability(1.0, 2.0, p), p.beta_max / 2)
        self.assertAlmostEqual(restore_probability(-1.0, [3.0, -1.0], p), p.kappa_max / 3)   # |theta| / max|theta|
        self.assertAlmostEqual(restore_probability(-3.0, [-1.0, -3.0], p), p.kappa_max)      # Eq.17 literal would give 3 kappa_max

    def test_run_records_rates_in_range(self):
        ev = specular_fixture(); p = MEGAParams(gamma=40, V=15, stagnation_stop=False)
        out = run_me_ga(SpecularPopulation(ev), 4, p, Memory(), True)
        info = out['info']; self.assertEqual(info['generations'], 15)
        self.assertTrue(all(p.rho[0] <= r <= p.rho[1] for r in info['rho']))
        self.assertTrue(all(p.psi[0] <= r <= p.psi[1] for r in info['psi']))
        self.assertTrue(all(0 <= b <= p.beta_max and 0 <= k <= p.kappa_max for b, k in zip(info['beta'], info['kappa'])))
        self.assertTrue(all(b == 0 for b, t in zip(info['beta'], info['theta']) if t < 0))
        self.assertTrue(all(k == 0 for k, t in zip(info['kappa'], info['theta']) if t >= 0))

    def test_children_are_binary_and_shape_preserved(self):
        rng = np.random.default_rng(1); pop = rng.integers(0, 2, (21, 10), dtype=np.int8)   # odd Gamma
        kids = make_children(pop, rng.random(21), 0.05, 0.9, rng)
        self.assertEqual(kids.shape, pop.shape); self.assertTrue(set(np.unique(kids)) <= {0, 1})


class SensitivityVariantTests(unittest.TestCase):
    def test_literal_running_best_makes_theta_nonpositive_so_learning_is_dead(self):
        ev = specular_fixture(); p = MEGAParams(gamma=40, V=12, stagnation_stop=False, theta_series='running')
        out = run_me_ga(SpecularPopulation(ev), 3, p, Memory(), True)
        self.assertTrue(all(t <= 1e-15 for t in out['info']['theta']))       # why the per-iteration reading is the default
        self.assertEqual(out['info']['stored'], 0)

    def test_iteration_best_theta_takes_both_signs_without_elitism(self):
        ev = coupled_fixture(14, seed=3); signs = set()
        for seed in range(6):
            out = run_me_ga(CoupledPopulation(ev), seed, MEGAParams(gamma=40, V=20, stagnation_stop=False), Memory(), True)
            signs |= {t >= 0 for t in out['info']['theta']}
        self.assertEqual(signs, {True, False})

    def test_elitism_option_keeps_iteration_best_monotone_and_skips_reevaluating_elites(self):
        ev = specular_fixture(); G = 30
        out = run_me_ga(SpecularPopulation(ev), 3, MEGAParams(gamma=G, V=6, stagnation_stop=False, elitism=2), None, False)
        self.assertTrue(all(t <= 1e-15 for t in out['info']['theta']))
        self.assertEqual(out['evaluations'], G + sum(G - 2 + k for k in out['info']['nu_count']))


class MemoryBranchTests(unittest.TestCase):
    def setUp(self):
        self.ev = specular_fixture(10, seed=2)
        bits = ((np.arange(1024)[:, None] >> np.arange(10)) & 1).astype(np.int8)
        vals = self.ev.score(bits); self.opt = bits[int(np.argmax(vals))]; self.optv = float(vals.max())

    def test_learning_branch_stores_iteration_best_with_probability_beta(self):
        # Force Theta = +1 every generation and beta_max = 1: ratio 1 -> the store event always fires.
        p = small(beta_max=1.0, kappa_max=1.0, stagnation_stop=False, V=5); mem = Memory()
        with mock.patch.object(me_ga, 'effectiveness', return_value=1.0):
            out = run_me_ga(SpecularPopulation(self.ev), 1, p, mem, True)
        self.assertEqual(out['info']['stored'], 5); self.assertEqual(out['info']['restored'], 0)
        self.assertTrue(all(e == 'stored' for e in out['info']['event']))
        self.assertTrue(all(b == 1.0 for b in out['info']['beta'])); self.assertEqual(len(mem.patterns), 5)
        # beta_max = 0: never stores
        mem0 = Memory()
        with mock.patch.object(me_ga, 'effectiveness', return_value=1.0):
            run_me_ga(SpecularPopulation(self.ev), 1, small(beta_max=0.0, V=5, stagnation_stop=False), mem0, True)
        self.assertEqual(mem0.patterns, [])

    def test_memory_enabled_call_without_external_memory_still_learns_locally(self):
        # Public adapters may omit cross-frame state; fresh within-call Psi must still run.
        p = small(beta_max=1.0, V=3, stagnation_delta=None)
        seen = []
        original = Memory.remember

        def record(mem, bits):
            seen.append(np.asarray(bits, dtype=np.int8).copy())
            return original(mem, bits)

        with mock.patch.object(me_ga, 'effectiveness', return_value=1.0), \
             mock.patch.object(Memory, 'remember', new=record):
            out = run_me_ga(SpecularPopulation(self.ev), 1, p, memory=None, use_memory=True)
        self.assertEqual(out['info']['stored'], 3)
        self.assertEqual(len(seen), 3)
        self.assertGreaterEqual(out['info']['psi_size_end'], 1)
        self.assertLessEqual(out['info']['psi_size_end'], 3)

    def test_memory_capacity_parameter_applies_to_local_memory(self):
        p = small(capacity=2, beta_max=1.0, V=4, stagnation_delta=None)
        with mock.patch.object(me_ga, 'effectiveness', return_value=1.0):
            out = run_me_ga(SpecularPopulation(self.ev), 3, p, memory=None, use_memory=True)
        self.assertEqual(out['info']['psi_size_end'], 2)

    def test_search_adapter_creates_memory_when_omitted(self):
        seen = []
        original = Memory.remember

        def record(mem, bits):
            seen.append(np.asarray(bits, dtype=np.int8).copy())
            return original(mem, bits)

        with mock.patch.object(me_ga, 'effectiveness', return_value=1.0), \
             mock.patch.object(me_ga, 'store_probability', return_value=1.0), \
             mock.patch.object(Memory, 'remember', new=record):
            result = search(self.ev, 'me_ga', 5000.0, 13)
        self.assertGreaterEqual(result.evaluations, 100)
        self.assertGreater(len(seen), 0)

    def test_remembering_branch_restores_best_of_psi_rescored_on_current_channel(self):
        mem = Memory(); mem.remember(np.zeros(10, dtype=np.int8)); mem.remember(self.opt)   # a poor and the optimum
        p = small(beta_max=1.0, kappa_max=1.0, stagnation_stop=False, V=4)
        with mock.patch.object(me_ga, 'effectiveness', return_value=-1.0):
            out = run_me_ga(SpecularPopulation(self.ev), 5, p, mem, True)
        info = out['info']
        self.assertEqual(info['restored'], 4); self.assertEqual(info['stored'], 0)
        self.assertAlmostEqual(out['value'], self.optv, places=12)                 # the restored optimum was found in Psi
        np.testing.assert_array_equal(out['bits'], self.opt)
        # Psi (2 entries) is rescored once, on the first remembering event; every evaluation is counted.
        expected = p.gamma + sum(p.gamma + k for k in info['nu_count']) + 2
        self.assertEqual(out['evaluations'], expected)
        self.assertEqual(len(mem.patterns), 2)                                     # remembering never writes

    def test_remembering_with_empty_psi_is_a_noop(self):
        mem = Memory()
        with mock.patch.object(me_ga, 'effectiveness', return_value=-1.0):
            out = run_me_ga(SpecularPopulation(self.ev), 5, small(kappa_max=1.0, stagnation_stop=False), mem, True)
        self.assertEqual(out['info']['restored'], 0); self.assertEqual(mem.patterns, [])

    def test_memory_is_not_used_for_initialisation(self):
        # Eq. (12): with Psi holding the optimum but remembering switched off, the initial population is still random.
        mem = Memory(); mem.remember(self.opt)
        a = run_me_ga(SpecularPopulation(self.ev), 7, small(V=1, kappa_max=0.0, beta_max=0.0), mem, True)
        b = run_me_ga(SpecularPopulation(self.ev), 7, small(V=1, kappa_max=0.0, beta_max=0.0), Memory(), True)
        np.testing.assert_array_equal(a['bits'], b['bits']); self.assertEqual(a['evaluations'], b['evaluations'])


class GaRiscMemoryIsolationTests(unittest.TestCase):
    class Trap(Memory):
        @property
        def patterns(self): raise AssertionError('GA-RISC read memory')
        @patterns.setter
        def patterns(self, value): pass
        def remember(self, *a, **k): raise AssertionError('GA-RISC wrote memory')
        def enter(self, *a, **k): raise AssertionError('GA-RISC touched memory')

    def test_ga_risc_never_reads_or_writes_memory(self):
        trap = self.Trap()
        r = search(specular_fixture(), 'ga_risc', 40.0, 3, memory=trap)
        self.assertGreaterEqual(r.evaluations, 1)
        ev = coupled_fixture()
        coupled_search.search(ev, 'ga_risc', perf_counter_ns() + 40_000_000, 3, memory=trap)
        out = run_me_ga(SpecularPopulation(specular_fixture()), 3, small(), trap, use_memory=False)
        self.assertEqual(out['info']['stored'] + out['info']['restored'], 0)

    def test_ga_risc_keeps_theta_and_replacement_but_no_memory_events(self):
        out = run_me_ga(SpecularPopulation(specular_fixture()), 3, small(V=6, stagnation_stop=False), None, False)
        self.assertEqual(len(out['info']['theta']), 6); self.assertGreater(sum(out['info']['nu_count']), 0)
        self.assertTrue(all(e is None for e in out['info']['event']))

    def test_me_ga_and_ga_risc_share_the_random_stream_until_a_memory_event(self):
        ev = specular_fixture(); p = small(V=1, stagnation_stop=False)
        a = run_me_ga(SpecularPopulation(ev), 12, p, Memory(), True); b = run_me_ga(SpecularPopulation(ev), 12, p, None, False)
        np.testing.assert_array_equal(a['bits'], b['bits']); self.assertEqual(a['evaluations'], b['evaluations'])


class ValueConsistencyTests(unittest.TestCase):
    def test_specular_value_equals_full_reevaluation(self):
        ev = specular_fixture(32, seed=8)
        for method in ME_GA_METHODS:
            for seed in (1, 2, 3):
                r = search(ev, method, 400.0, seed, memory=Memory())
                self.assertAlmostEqual(r.value, float(ev.score(r.bits)), places=11, msg=(method, seed))
                self.assertAlmostEqual(r.value, float(ev.score_field(ev.full_field(r.bits))), places=11)
                self.assertTrue(set(np.unique(r.bits)) <= {0, 1})
                self.assertEqual(r.trace[-1][1], r.value)

    def test_coupled_value_equals_full_reevaluation(self):
        ev = coupled_fixture(14, seed=3)
        for method in ME_GA_METHODS:
            for seed in (1, 2):
                trace = []
                bits, v, count, bd = coupled_search.search(ev, method, perf_counter_ns() + 400_000_000, seed,
                                                           memory=Memory(), trace=trace)
                self.assertAlmostEqual(v, direct_coupled(ev, bits), places=10, msg=(method, seed))
                self.assertAlmostEqual(v, float(ev.score(ev.channel(bits) @ ev.w)), places=10)
                self.assertEqual(trace[-1][1], v); self.assertEqual(trace[-1][2] <= count, True)
                self.assertTrue({'features_ms', 'inference_ms', 'memory_ms'} <= set(bd))

    def test_method_ids_do_not_leak_into_the_matched_registry(self):
        self.assertEqual(GA_METHODS, ('memory_ga', 'uniform_ga', 'analytical_ga', 'analytical_no_memory_ga', 'mlp_ga',
                                      'attention_ga', 'attention_no_memory_ga', 'attention_no_physics_ga',
                                      'attention_no_conditioning_ga'))
        self.assertEqual(ME_GA_METHODS, ('me_ga', 'ga_risc', 'me_ga_paper'))
        for m in ME_GA_METHODS:
            with self.assertRaises(ValueError): variant_spec(m)
        protocol = json.loads((ROOT / 'configs' / 'experiments' / 'matched_v1.json').read_text())
        names = list(protocol['methods']['baselines']) + [k for k in protocol['methods'] if k != 'baselines']
        self.assertTrue(set(names).isdisjoint(ME_GA_METHODS))


class DeadlineTests(unittest.TestCase):
    def run_fake(self, deadline_ms, slow_call=None, G=100):
        clock = [0]; pop = FakeClockPop(16, clock, slow_call=slow_call)
        with mock.patch.object(me_ga, 'perf_counter_ns', lambda: clock[0]):
            out = run_me_ga(pop, 1, MEGAParams(gamma=G, chunk=25, stagnation_stop=False), Memory(), True, deadline_ns=int(deadline_ms * 1e6), start_ns=0)
        return out, clock[0], pop

    def test_never_runs_past_deadline_and_counts_only_completed_work(self):
        for deadline_ms in (3, 12, 25, 60):
            out, now, pop = self.run_fake(deadline_ms)
            self.assertLessEqual(now, deadline_ms * 1e6, deadline_ms)
            self.assertTrue(all(t <= deadline_ms for t, _, _ in out['trace']))
            self.assertEqual(out['info']['stop'], 'deadline')
            # 1 mandatory single + chunks of <=25: every counted individual came from a call that completed in time
            self.assertLessEqual(out['evaluations'], pop.calls * 25)
            self.assertIsNotNone(out['bits'])                       # best-so-far is always returned

    def test_late_chunk_is_discarded_not_counted(self):
        out, now, pop = self.run_fake(60, slow_call=3)              # third scoring call takes 100 ms
        self.assertEqual(out['info']['chunks_discarded'], 1)
        self.assertEqual(out['info']['stop'], 'deadline')
        self.assertEqual(out['evaluations'], 1 + 8)                 # mandatory single + 8-individual calibration chunk; the late chunk is dropped
        self.assertTrue(all(t <= 60 for t, _, _ in out['trace']))

    def test_tiny_budget_still_returns_a_valid_scored_configuration(self):
        ev = specular_fixture(); r = search(ev, 'me_ga', 0.0001, 1, memory=Memory())
        self.assertGreaterEqual(r.evaluations, 1); self.assertAlmostEqual(r.value, float(ev.score(r.bits)), places=12)
        self.assertTrue(r.deadline_missed in (True, False))

    def test_paper_mode_ignores_deadline_and_reports_true_runtime(self):
        ev = specular_fixture(); r = search(ev, 'me_ga_paper', 0.0001, 1, memory=Memory())
        self.assertIsNone(r.deadline_missed)                        # not a deadline-bound controller
        self.assertGreater(r.evaluations, 100); self.assertGreater(r.elapsed_ms, 0.0001)
        c = coupled_search.search(coupled_fixture(), 'me_ga_paper', perf_counter_ns() - 1, 1, memory=Memory())
        self.assertGreater(c[2], 100)

    def test_paper_mode_runs_full_gamma_times_v_budget_without_stagnation_stop(self):
        ev = specular_fixture(); p = MEGAParams(gamma=30, V=9, stagnation_stop=False)
        out = run_me_ga(SpecularPopulation(ev), 2, p, None, False)
        self.assertEqual(out['info']['generations'], 9); self.assertEqual(out['info']['stop'], 'V')
        self.assertEqual(out['evaluations'], 30 + sum(30 + k for k in out['info']['nu_count']))

    def test_stagnation_stop_fires_before_V_when_best_stops_improving(self):
        ev = specular_fixture(8, seed=1)
        # Default stagnation_delta=None uses published V cap only
        out_default = run_me_ga(SpecularPopulation(ev), 2, MEGAParams(gamma=60, V=100), Memory(), True)
        self.assertEqual(out_default['info']['stop'], 'V')
        self.assertEqual(out_default['info']['generations'], 100)
        # Explicit stagnation_delta stops early when best stops improving
        out = run_me_ga(SpecularPopulation(ev), 2, MEGAParams(gamma=60, V=100, stagnation_delta=1e-4), Memory(), True)
        self.assertEqual(out['info']['stop'], 'stagnation'); self.assertLess(out['info']['generations'], 100)


class EvaluatorEquivalenceTests(unittest.TestCase):
    def check(self, ev, seed):
        rng = np.random.default_rng(seed); n = ev.n
        base = rng.integers(0, 2, n, dtype=np.int8)
        bits = np.where(rng.random((40, n)) < rng.choice([0.05, 0.2, 0.5, 0.9], (40, 1)), 1 - base, base).astype(np.int8)
        bits[0] = base; bits[1] = 1 - base            # zero-distance and all-flipped children
        direct = np.array([ev.state(b).field for b in bits])
        pop = CoupledPopulation(ev, 'solve')
        np.testing.assert_allclose(pop.fields_solve(bits), direct, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(pop.fields_inverse(bits), direct, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(pop.fields_woodbury(bits, base), direct, rtol=1e-8, atol=1e-11)
        ref = np.array([float(ev.score(f)) for f in direct])
        for method in ('solve', 'inverse', 'woodbury', 'auto'):
            got = CoupledPopulation(ev, method, m_max=6, min_children=3).score(bits, base)   # mixed near/far children
            np.testing.assert_allclose(got, ref, rtol=1e-9, atol=1e-11, err_msg=method)

    def test_fixture_matches_direct_state(self):
        for seed in range(3): self.check(coupled_fixture(12, seed=seed), seed)

    def test_woodbury_is_used_for_near_children_and_solve_for_far(self):
        ev = coupled_fixture(12); pop = CoupledPopulation(ev, 'woodbury', m_max=3)
        rng = np.random.default_rng(0); base = rng.integers(0, 2, 12, dtype=np.int8)
        near = np.tile(base, (5, 1)); near[np.arange(5), np.arange(5)] ^= 1
        far = 1 - near[:2]
        pop.score(np.vstack([near, far]), base)
        self.assertEqual(pop.woodbury_children, 5); self.assertEqual(pop.solved_children, 2)

    def test_real_validation_frame_if_available(self):
        data = ROOT / 'data' / 'processed' / 'coupled_wire_v1' / 'dataset.npz'
        gate = ROOT / 'outputs' / 'runs' / 'matched_coupled_v1' / 'physics_gate.json'
        if not (data.exists() and gate.exists()): self.skipTest('validation frame not present')
        d = np.load(data); g = json.loads(gate.read_text())
        loads = np.array(g['loads_real_ohm']) + 1j * np.array(g['loads_imag_ohm'])
        idx = int(np.flatnonzero(d['split'] == 'validation')[0])
        ev = CoupledNetwork(d['z'][idx], loads); self.check(ev, 0)
        bits, v, c, _ = coupled_search.search(ev, 'me_ga_paper', 0, 1, memory=Memory())
        self.assertAlmostEqual(v, direct_coupled(ev, bits), places=9)

    def test_specular_batched_score_matches_full_field(self):
        ev = specular_fixture(64); bits = np.random.default_rng(1).integers(0, 2, (50, 64), dtype=np.int8)
        np.testing.assert_allclose(SpecularPopulation(ev).score(bits), ev.score_field(ev.full_field(bits)), atol=1e-12)


class PersistenceAndDeterminismTests(unittest.TestCase):
    def force_store(self, ev, mem, seed=1):
        with mock.patch.object(me_ga, 'effectiveness', return_value=1.0):
            return run_me_ga(SpecularPopulation(ev), seed, small(beta_max=1.0, V=3, stagnation_stop=False), mem, True)

    def test_memory_persists_within_trajectory_and_resets_between_trajectories(self):
        ev = specular_fixture(); mem = Memory(); mem.enter(0)
        self.force_store(ev, mem)
        stored = len(mem.patterns); self.assertGreater(stored, 0)
        mem.enter(0)                                                   # next frame, same trajectory: Psi kept
        self.assertEqual(len(mem.patterns), stored)
        again = run_me_ga(SpecularPopulation(ev), 2, small(V=2, stagnation_stop=False), mem, True)
        self.assertEqual(again['info']['psi_size_start'], stored)      # the controller sees last frame's Psi
        mem.enter(1)                                                   # new trajectory: reset
        self.assertEqual(mem.patterns, [])
        fresh = run_me_ga(SpecularPopulation(ev), 2, small(V=2, stagnation_stop=False), mem, True)
        self.assertEqual(fresh['info']['psi_size_start'], 0)

    def test_psi_capacity_and_fifo_eviction(self):
        ev = specular_fixture(); mem = Memory()
        self.force_store(ev, mem)
        for i in range(30):
            self.force_store(ev, mem, seed=i)
        self.assertLessEqual(len(mem.patterns), MEGAParams().capacity)

    def test_coupled_benchmark_policy_does_not_overwrite_psi(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            from scripts.benchmark_coupled import should_store_memory
        except ImportError:
            self.skipTest('benchmark_coupled needs torch')
        for m in ME_GA_METHODS: self.assertFalse(should_store_memory(m), m)
        self.assertTrue(should_store_memory('memory_ga'))

    def test_same_seed_same_result_different_seed_differs(self):
        ev = specular_fixture(24, seed=4); cev = coupled_fixture(14, seed=2)
        for method in ME_GA_METHODS:
            def run(seed):
                r = search(ev, method if method != 'me_ga' else 'me_ga_paper', 1e6, seed, memory=Memory())
                c = coupled_search.search(cev, method if method != 'me_ga' else 'me_ga_paper', 0, seed, memory=Memory())
                return r, c
            (a, ca), (b, cb) = run(5), run(5)
            np.testing.assert_array_equal(a.bits, b.bits); self.assertEqual((a.value, a.evaluations), (b.value, b.evaluations))
            np.testing.assert_array_equal(ca[0], cb[0]); self.assertEqual((ca[1], ca[2]), (cb[1], cb[2]))
            (d, _), _ = run(6), None
            self.assertFalse(np.array_equal(a.bits, d.bits) and a.evaluations == d.evaluations)

    def test_memory_state_is_deterministic_too(self):
        ev = specular_fixture(); m1, m2 = Memory(), Memory()
        for m in (m1, m2):
            for frame in range(3):
                run_me_ga(SpecularPopulation(ev), 100 + frame, small(V=8, beta_max=1.0, stagnation_stop=False), m, True)
        self.assertEqual([p.tobytes() for p in m1.patterns], [p.tobytes() for p in m2.patterns])


class ExistingMethodsRegressionTests(unittest.TestCase):
    """Golden values recorded from the unmodified search.py/coupled_search.py (git HEAD f4a8797)."""
    def test_existing_ga_variants_are_bit_identical_to_pre_change_results(self):
        sev = specular_fixture(n=20, seed=5); cev = coupled_fixture(n=20, seed=9)
        r = np.random.default_rng
        mem_bits = [r(1).integers(0, 2, 20, dtype=np.int8), r(2).integers(0, 2, 20, dtype=np.int8)]
        bitstr = lambda b: ''.join(map(str, np.asarray(b).tolist()))
        for key, gold in GOLDEN.items():
            kind, method, seed = key.split(':'); seed = int(seed)
            if kind == 'specular':
                mem = Memory(capacity=12)
                for b in mem_bits: mem.remember(b)
                res = search(sev, method, 60000., seed, memory=mem)
                self.assertEqual(bitstr(res.bits), gold[0], key); self.assertEqual(res.evaluations, gold[2], key)
                self.assertAlmostEqual(res.value, float(gold[1]), places=10, msg=key)
                self.assertEqual([bitstr(p) for p in mem.patterns], gold[3], key)
            else:
                bits, v, c, _ = coupled_search.search(cev, method, perf_counter_ns() + 60_000_000_000, seed,
                                                      memory=[b.copy() for b in mem_bits])
                self.assertEqual(bitstr(bits), gold[0], key); self.assertEqual(c, gold[2], key)
                self.assertAlmostEqual(v, float(gold[1]), places=10, msg=key)

    def test_time_bounded_baselines_still_dispatch_unchanged(self):
        ev = specular_fixture()
        for m in ('greedy', 'pair', 'random', 'population_ga'):
            res = search(ev, m, 15.0, 3, memory=None if m != 'population_ga' else Memory())
            self.assertAlmostEqual(res.value, float(ev.score(res.bits)), places=11)


if __name__ == '__main__':
    unittest.main()
