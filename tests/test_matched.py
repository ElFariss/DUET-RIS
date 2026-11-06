import json
import subprocess
import sys
import tempfile
import time
import unittest
from itertools import count
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from atomwise_ris.core import Evaluator
from atomwise_ris.physics.network import CoupledNetwork
import atomwise_ris.optimization.search as ss
import atomwise_ris.optimization.coupled_search as cs
from atomwise_ris.optimization.search import Memory, SearchConfig, load_search_config, variant_spec, GA_METHODS
import analyze_matched as am
import select_matched_budget as sel

PROTOCOL = json.loads((ROOT / 'configs' / 'experiments' / 'matched_v1.json').read_text())
GA = ['memory_ga', 'uniform_ga', 'analytical_ga', 'analytical_no_memory_ga', 'mlp_ga', 'attention_ga',
      'attention_no_memory_ga', 'attention_no_physics_ga']
BIG_MS = 1e4


def spec_fixture(n=64, k=3, seed=1):
    r = np.random.default_rng(seed)
    return Evaluator(r.normal(size=(k, k)) + 1j * r.normal(size=(k, k)),
                     (r.normal(size=(n, k, k)) + 1j * r.normal(size=(n, k, k))) / n,
                     np.array([-.55 - .09j, .80 + .13j]), .1, r.normal(size=(n, 3)))


def cpl_fixture(n=16, seed=2):
    """Block-structured passive network where the RIS actually moves the rate (random dense z is dominated by the direct path)."""
    r = np.random.default_rng(seed)

    def sym(k, s):
        m = r.normal(size=(k, k)) * s + 1j * r.normal(size=(k, k)) * s
        return (m + m.T) / 2
    c = (r.normal(size=(n, 6)) + 1j * r.normal(size=(n, 6))) * 40
    z = np.block([[sym(n, 4) + (40 + 20j) * np.eye(n), c], [c.T, sym(6, .3) + 50 * np.eye(6)]])
    return CoupledNetwork(z, np.array([10 + 60j, 10 - 60j]))


def spec_run(method, seed=3, memory=None, policy=None, ev=None, budget=BIG_MS, **kw):
    return ss.search(ev or spec_fixture(), method, budget, seed, memory=memory, policy=policy, **kw)


def cpl_run(method, seed=3, memory=(), policy=None, ev=None, ms=2000., trace=None, **kw):
    trace = [] if trace is None else trace
    out = cs.search(ev or cpl_fixture(), method, time.perf_counter_ns() + int(ms * 1e6), seed, memory=memory, policy=policy,
                    trace=trace, **kw)
    return out, trace


def spec_sig(r):
    return (r.bits.tolist(), r.value, r.evaluations, [(v, e) for _, v, e in r.trace])


def cpl_sig(out, trace):
    return (out[0].tolist(), out[1], out[2], [(v, e) for _, v, e in trace])


class FakeClock:
    """Deterministic perf_counter_ns so time-dependent baselines become reproducible."""
    def __init__(self, step=3000):
        self.t = count(0, step)

    def __call__(self):
        return next(self.t)


class SharedConfig(unittest.TestCase):
    def test_config_matches_protocol_file(self):
        for name in ('small', 'medium', 'large'):
            c = load_search_config(name)
            self.assertEqual(c.specular, PROTOCOL['shared_search_config']['specular'][name])
            self.assertEqual(c.coupled, PROTOCOL['shared_search_config']['coupled'][name])
            self.assertEqual(c.shared, PROTOCOL['shared_search_config']['all_variants'])
        self.assertEqual(load_search_config().name, 'medium')
        self.assertAlmostEqual(load_search_config().specular_limits(10)['t_cap_ms'], 3.8)
        self.assertAlmostEqual(load_search_config().specular_limits(100)['t_cap_ms'], 58.)
        with self.assertRaises(ValueError):
            load_search_config('huge')
        baselines = PROTOCOL['method_naming_and_baselines']
        self.assertIn('population_ga', PROTOCOL['methods']['baselines'])
        self.assertIn('population_ga', baselines['baseline_memory_policy'])
        self.assertIn('supplies none', baselines['population_ga'])
        self.assertIn('all-OFF plus seeded random', baselines['population_ga'])

    def test_variants_differ_only_in_ranking_and_memory(self):
        specs = {m: variant_spec(m) for m in GA}
        self.assertEqual({m: s['memory'] for m, s in specs.items()},
                         {m: not m.endswith('no_memory_ga') for m in GA})
        self.assertEqual({s['ranking'] for s in specs.values()}, {'uniform', 'memory', 'analytical', 'neural'})
        with self.assertRaises(ValueError):
            variant_spec('pair')

    def test_every_ga_variant_reads_the_same_limits(self):
        cfg = load_search_config('medium')
        calls = []
        orig = SearchConfig.specular_limits
        origc = SearchConfig.coupled_limits

        def spy(self, b):
            out = orig(self, b)
            calls.append(('s', b, out))
            return out

        def spyc(self):
            out = origc(self)
            calls.append(('c', None, out))
            return out

        with mock.patch.object(SearchConfig, 'specular_limits', spy), mock.patch.object(SearchConfig, 'coupled_limits', spyc):
            for m in GA:
                spec_run(m, budget=20., config=cfg)
                cpl_run(m, ms=20., config=cfg)
        for kind in 'sc':
            got = [c for c in calls if c[0] == kind]
            self.assertEqual(len(got), len(GA))
            self.assertTrue(all(c == got[0] for c in got))

    def test_matched_runs_cannot_reach_legacy_limits(self):
        cfg = load_search_config('medium')
        with self.assertRaises(ValueError):
            ss.search(spec_fixture(), 'analytical_ga', 10, 1, config=cfg, legacy=True)
        with self.assertRaises(ValueError):
            cs.search(cpl_fixture(), 'analytical_ga', time.perf_counter_ns() + 10**7, 1, config=cfg, legacy=True)
        boom = mock.Mock(side_effect=AssertionError('legacy reached'))
        with mock.patch.object(ss, '_search_legacy', boom), mock.patch.object(cs, '_search_legacy', boom):
            for m in GA:
                spec_run(m, budget=20., config=cfg)
                cpl_run(m, ms=20., config=cfg)
        self.assertFalse(boom.called)

    def test_search_config_changes_the_limits_for_everyone(self):
        small, large = load_search_config('small'), load_search_config('large')
        a = spec_run('analytical_ga', config=small)
        b = spec_run('analytical_ga', config=large)
        self.assertNotEqual(spec_sig(a), spec_sig(b))
        a, ta = cpl_run('analytical_ga', config=small)
        b, tb = cpl_run('analytical_ga', config=large)
        self.assertNotEqual(cpl_sig(a, ta), cpl_sig(b, tb))


class RankingIsTheOnlyDifference(unittest.TestCase):
    def test_fixtures_are_nontrivial(self):
        r = spec_run('analytical_ga')
        self.assertGreater(len(r.trace), 3)
        out, trace = cpl_run('analytical_ga')
        self.assertGreaterEqual(len(trace), 1)
        self.assertAlmostEqual(trace[-1][1], out[1], places=12)

    def test_specular_policy_returning_analytical_equals_analytical(self):
        used = {'n': 0}

        def zero_residual(x, g):
            used['n'] += 1
            return np.asarray(g).copy()
        for seed in (1, 2):
            ev = spec_fixture(seed=seed)
            base = spec_run('analytical_ga', ev=ev)
            for m in ('mlp_ga', 'attention_ga', 'attention_no_physics_ga'):
                got = spec_run(m, ev=ev, policy=zero_residual, memory=Memory())
                np.testing.assert_array_equal(got.bits, base.bits, err_msg=m)
                self.assertAlmostEqual(got.value, ev.score(base.bits), places=12, msg=m)
            got = spec_run('attention_no_memory_ga', ev=ev, policy=zero_residual)
            ref = spec_run('analytical_no_memory_ga', ev=ev)
            np.testing.assert_array_equal(got.bits, ref.bits)
            self.assertAlmostEqual(got.value, ev.score(ref.bits), places=12)
        self.assertGreater(used['n'], 4)

    def test_specular_memory_ga_with_empty_memory_equals_analytical(self):
        ev = spec_fixture(seed=2)
        a = spec_run('memory_ga', ev=ev, memory=Memory())
        b = spec_run('analytical_ga', ev=ev, memory=Memory())
        np.testing.assert_array_equal(a.bits, b.bits)
        self.assertAlmostEqual(a.value, ev.score(b.bits), places=12)

    def test_coupled_policy_returning_analytical_equals_analytical(self):
        used = {'n': 0}

        def ident(x, g):
            used['n'] += 1
            return g
        for seed in (2, 4):
            ev = cpl_fixture(seed=seed)
            base = cpl_run('analytical_ga', ev=ev)[0]
            for m in ('mlp_ga', 'attention_ga', 'attention_no_physics_ga'):
                got = cpl_run(m, ev=ev, policy=ident)[0]
                np.testing.assert_array_equal(got[0], base[0], err_msg=m)
                self.assertAlmostEqual(got[1], base[1], places=12, msg=m)
            got = cpl_run('attention_no_memory_ga', ev=ev, policy=ident)[0]
            ref = cpl_run('analytical_no_memory_ga', ev=ev)[0]
            np.testing.assert_array_equal(got[0], ref[0])
            self.assertAlmostEqual(got[1], ref[1], places=12)
        self.assertGreater(used['n'], 4)   # the neural path really ran

    def test_coupled_memory_ga_with_empty_memory_equals_analytical(self):
        ev = cpl_fixture(seed=2)
        a, b = cpl_run('memory_ga', ev=ev)[0], cpl_run('analytical_ga', ev=ev)[0]
        np.testing.assert_array_equal(a[0], b[0])
        self.assertAlmostEqual(a[1], b[1], places=12)

    def test_memory_ga_ranking_uses_pattern_spread(self):
        # Two disagreeing remembered patterns create a per-bit std bias that changes the ranking signal.
        ev = spec_fixture(seed=2)
        rng = np.random.default_rng(0)
        m1, m2 = Memory(), Memory()
        pats = [rng.integers(0, 2, 64).astype(np.int8) for _ in range(6)]
        for m in (m1, m2):
            for p in pats:
                m.remember(p)
        base = load_search_config('medium')
        strong = SearchConfig(base.name, base.specular, base.coupled, {**base.shared, 'memory_bias_weight': 100.}, base.protocol_sha256)
        a = spec_sig(spec_run('memory_ga', ev=ev, memory=m1, config=strong))
        b = spec_sig(spec_run('analytical_ga', ev=ev, memory=m2, config=strong))
        self.assertNotEqual(a, b)
        evc = cpl_fixture(seed=4)
        cm = [rng.integers(0, 2, evc.n).astype(np.int8) for _ in range(6)]
        self.assertNotEqual(cpl_sig(*cpl_run('memory_ga', ev=evc, memory=cm, config=strong)), cpl_sig(*cpl_run('analytical_ga', ev=evc, memory=cm, config=strong)))

    def test_uniform_ga_differs_by_ranking_and_depends_on_seed(self):
        differs = 0
        for fx in (1, 2, 3):
            ev = spec_fixture(seed=fx)
            u = spec_sig(spec_run('uniform_ga', ev=ev))
            self.assertEqual(u, spec_sig(spec_run('uniform_ga', ev=ev)))   # reproducible from the seeded rng
            differs += u != spec_sig(spec_run('analytical_ga', ev=ev))
        self.assertGreaterEqual(differs, 1)
        ev = cpl_fixture(seed=2)
        sigs = {repr(cpl_sig(*cpl_run('uniform_ga', ev=ev, seed=s))) for s in (1, 2, 3, 4)}
        self.assertGreater(len(sigs), 1)
        self.assertNotEqual(cpl_sig(*cpl_run('uniform_ga', ev=ev)), cpl_sig(*cpl_run('analytical_ga', ev=ev)))

    def test_no_memory_variants_ignore_supplied_memory(self):
        rng = np.random.default_rng(5)
        pats = [rng.integers(0, 2, 64).astype(np.int8) for _ in range(5)]
        ev = spec_fixture(seed=2)
        mem = Memory()
        for p in pats:
            mem.remember(p)
        before = [p.copy() for p in mem.patterns]
        for m, ref in (('analytical_no_memory_ga', 'analytical_no_memory_ga'), ('attention_no_memory_ga', 'attention_no_memory_ga')):
            pol = (lambda x, g: np.zeros_like(g)) if 'attention' in m else None
            self.assertEqual(spec_sig(spec_run(m, ev=ev, memory=mem, policy=pol)), spec_sig(spec_run(ref, ev=ev, memory=None, policy=pol)))
        for a, b in zip(before, mem.patterns):
            np.testing.assert_array_equal(a, b)
        self.assertEqual(len(before), len(mem.patterns))   # nothing was written either
        evc = cpl_fixture(seed=2)
        cmem = [rng.integers(0, 2, evc.n).astype(np.int8) for _ in range(5)]
        for m in ('analytical_no_memory_ga', 'attention_no_memory_ga'):
            pol = (lambda x, g: g) if 'attention' in m else None
            self.assertEqual(cpl_sig(*cpl_run(m, ev=evc, memory=cmem, policy=pol)), cpl_sig(*cpl_run(m, ev=evc, memory=(), policy=pol)))
        # and memory really is consumed by memory-enabled variants
        self.assertNotEqual(cpl_sig(*cpl_run('analytical_ga', ev=evc, memory=cmem)), cpl_sig(*cpl_run('analytical_ga', ev=evc, memory=())))

    def test_neural_overhead_respects_calibrated_cost(self):
        calls = {'n': 0}

        def pol(x, g):
            calls['n'] += 1
            return np.zeros_like(g)

        pol.expected_ms = 1e6          # far more than any budget: must never be invoked
        spec_run('attention_ga', budget=20., policy=pol)
        self.assertEqual(calls['n'], 0)
        cpl_run('attention_ga', ms=20., policy=lambda x, g: calls.__setitem__('n', calls['n'] + 1) or g)
        self.assertGreater(calls['n'], 0)
        calls['n'] = 0

        def pol2(x, g):
            calls['n'] += 1
            return g

        pol2.expected_ms = 1e6
        cpl_run('attention_ga', ms=20., policy=pol2)
        self.assertEqual(calls['n'], 0)


class TraceAndCounting(unittest.TestCase):
    def check_trace(self, trace, value, evals_total):
        self.assertGreaterEqual(len(trace), 1)
        self.assertEqual(trace[0][2], 1)
        for p in trace:
            self.assertEqual(len(p), 3)
        for a, b in zip(trace, trace[1:]):
            self.assertGreaterEqual(b[0], a[0])
            self.assertGreaterEqual(b[1], a[1])
            self.assertGreaterEqual(b[2], a[2])
        self.assertAlmostEqual(trace[-1][1], value, places=12)
        self.assertLessEqual(trace[-1][2], evals_total)

    def test_specular_trace_all_methods(self):
        for m in list(GA) + ['greedy', 'pair', 'random']:
            r = spec_run(m, budget=30. if m in GA else 15., policy=None)
            self.check_trace(r.trace, r.value, r.evaluations)

    def test_coupled_trace_all_methods(self):
        for m in list(GA) + ['greedy', 'pair', 'random']:
            out, trace = cpl_run(m, ms=40.)
            self.check_trace(trace, out[1], out[2])

    def test_every_improvement_is_traced_including_inline_ones(self):
        out, trace = cpl_run('analytical_ga', memory=[np.zeros(16, np.int8)])
        self.assertAlmostEqual(trace[-1][1], out[1], places=12)
        self.assertEqual(trace[-1][2], 1) if len(trace) == 1 else self.assertGreater(trace[-1][2], 1)

    def test_baselines_keep_behaviour_specular(self):
        ev = spec_fixture(seed=2)
        for m in ('greedy', 'pair', 'random'):
            with mock.patch.object(ss, 'perf_counter_ns', FakeClock()):
                a = ss.search(ev, m, 6., 5)
            with mock.patch.object(ss, 'perf_counter_ns', FakeClock()):
                b = ss.search(ev, m, 6., 5, legacy=True)
            self.assertEqual(spec_sig(a), spec_sig(b))

    def test_baselines_keep_behaviour_coupled_and_fix_double_count(self):
        ev = cpl_fixture(seed=2)
        for m in ('greedy', 'pair', 'random'):
            flips = []
            orig = ev.flip

            def spy(st, ix, orig=orig):
                flips.append(1)
                return orig(st, ix)
            res = {}
            for legacy in (True, False):
                flips.clear()
                with mock.patch.object(cs, 'perf_counter_ns', FakeClock(20000)), mock.patch.object(ev, 'flip', spy):
                    d = cs.perf_counter_ns() + 5_000_000
                    res[legacy] = (cs.search(ev, m, d, 5, legacy=legacy), len(flips))
            (la, lf), (ma, mf) = res[True], res[False]
            np.testing.assert_array_equal(la[0], ma[0])
            self.assertEqual(la[1], ma[1])
            # Legacy counted every flipped candidate a second time; matched counting does not.
            self.assertEqual(la[2] - ma[2], lf if m != 'random' else 0)
            if m != 'random':
                self.assertGreater(lf, 0)

    def test_coupled_neural_policy_outputs_are_fully_scored(self):
        ident = lambda x, g: g
        ev = cpl_fixture(seed=2)
        for m in ('mlp_ga', 'attention_ga'):
            out = cpl_run(m, ev=ev, policy=ident)[0]
            full_score = ev.score(ev.state(out[0]).field)
            self.assertAlmostEqual(out[1], float(full_score), places=10)
            self.assertGreater(out[2], 0)


class Statistics(unittest.TestCase):
    def rows(self, effects, T=30, frames=2, seeds=(1, 2), budget=10., noise=0.002):
        rng = np.random.default_rng(11)
        base = {t: 6 + 0.3 * rng.normal() for t in range(T)}
        out = []
        for m in am.protocol_methods(PROTOCOL):
            for t in range(T):
                for f in range(frames):
                    ref_idx = t * frames + f
                    for s in seeds:
                        rate = base[t] + effects.get(m, 0.) + noise * rng.normal()
                        out.append({'method': m, 'budget_ms': budget, 'index': ref_idx, 'trajectory': t, 'seed': s, 'split': 'test',
                                    'rate': rate, 'elapsed_ms': 5. + rng.random(), 'deadline_missed': m == 'pair' and s == 1 and f == 0 and t < 3,
                                    'evaluations': 100, 'breakdown_ms': {'scenario_preparation': 1.0},
                                    'trace': [[0.1, rate - 0.5, 1], [2.0 + rng.random(), rate, 50]]})
        return out

    def test_holm_known_values(self):
        np.testing.assert_allclose(am.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        np.testing.assert_allclose(am.holm([0.5]), [0.5])
        np.testing.assert_allclose(am.holm([0.4, 0.4]), [0.8, 0.8])

    def test_decision_rule(self):
        self.assertEqual(am.decide(0.02, 0.05, 0.015), 'improved')
        self.assertEqual(am.decide(0.01, 0.05, 0.015), 'inconclusive')
        self.assertEqual(am.decide(-0.01, 0.01, 0.015), 'equivalent')
        self.assertEqual(am.decide(-0.02, 0.01, 0.015), 'inconclusive')
        self.assertEqual(am.decide(-0.05, -0.02, 0.015), 'inconclusive')

    def test_known_differences_and_decisions(self):
        effects = {'attention_ga': 0.06, 'mlp_ga': 0.0, 'analytical_ga': 0.0, 'memory_ga': 0.0, 'pair': -0.2,
                   'attention_no_memory_ga': 0.0, 'analytical_no_memory_ga': 0.0, 'uniform_ga': -0.001}
        s = am.analyse(self.rows(effects), PROTOCOL, 10.)
        by = {c['contrast']: c for c in s['contrasts']}
        self.assertEqual(len(by), len(PROTOCOL['statistics']['contrasts']))
        self.assertAlmostEqual(by['attention_ga - memory_ga']['difference'], 0.06, delta=0.002)
        self.assertEqual(by['attention_ga - memory_ga']['decision'], 'improved')
        self.assertEqual(by['attention_ga - analytical_ga']['decision'], 'improved')
        self.assertEqual(by['mlp_ga - memory_ga']['decision'], 'equivalent')
        self.assertEqual(by['analytical_ga - uniform_ga']['decision'], 'equivalent')
        self.assertEqual(by['memory_ga - pair']['decision'], 'improved')
        self.assertLess(by['attention_ga - memory_ga']['p_holm_zero'], 0.05)
        for c in s['contrasts']:
            lo, hi = c['interval_bonferroni_simultaneous']
            self.assertLessEqual(lo, c['difference'])
            self.assertGreaterEqual(hi, c['difference'])
            self.assertGreaterEqual(c['p_holm_zero'], c['p_value_zero_centered_bootstrap'])
            self.assertNotIn('interval_corrected', c)
            self.assertEqual(c['n_trajectories'], 30)

    def test_bootstrap_is_reproducible_and_seeded(self):
        rows = self.rows({'attention_ga': 0.05})
        a = am.analyse(rows, PROTOCOL, 10.)['contrasts']
        b = am.analyse(rows, PROTOCOL, 10.)['contrasts']
        self.assertEqual(a, b)
        per = {m: am.trajectory_means([r for r in rows if r['method'] == m]) for m in am.protocol_methods(PROTOCOL)}
        c = am.contrast_statistics(per, PROTOCOL['statistics']['contrasts'], 8251, 10000, 0.015)
        d = am.contrast_statistics(per, PROTOCOL['statistics']['contrasts'], 1, 10000, 0.015)
        self.assertEqual(c, a)
        self.assertNotEqual(c[0]['interval_bonferroni_simultaneous'], d[0]['interval_bonferroni_simultaneous'])

    def test_constant_difference_has_degenerate_interval(self):
        per = {'a': {t: float(t) + 1.0 for t in range(10)}, 'b': {t: float(t) for t in range(10)}}
        out = am.contrast_statistics(per, ['a - b'], 8251, 10000, 0.015)[0]
        self.assertEqual(out['interval_bonferroni_simultaneous'], [1.0, 1.0])
        self.assertEqual(out['decision'], 'improved')
        self.assertLess(out['p_value_zero_centered_bootstrap'], 0.001)

    def test_coupled_improvement_requires_matching_preselected_action_audit(self):
        rows = self.rows({'attention_ga': 0.06})
        protocol_hash = 'a' * 64
        without = am.analyse(rows, PROTOCOL, 10., experiment='coupled', protocol_hash=protocol_hash)
        self.assertIsNone(without['mesh_audit_passed'])
        c = next(c for c in without['contrasts'] if c['contrast'] == 'attention_ga - memory_ga')
        self.assertEqual(c['decision'], 'numerically_unresolved')
        audit = {'protocol_sha256': protocol_hash, 'preselected_before_test_evaluation': True, 'split': 'test',
                 'segment_count_coarse': 81, 'segment_count_fine': 161,
                 'audited_action_count': sum(r['budget_ms'] == 10 for r in rows),
                 'rate_difference_abs_max_bit_s_hz': 0.001, 'resolution_criterion_bit_s_hz': 0.01,
                 'criterion_passed': True}
        with_audit = am.analyse(rows, PROTOCOL, 10., experiment='coupled', protocol_hash=protocol_hash, mesh_audit=audit)
        self.assertTrue(with_audit['mesh_audit_passed'])
        c = next(c for c in with_audit['contrasts'] if c['contrast'] == 'attention_ga - memory_ga')
        self.assertEqual(c['decision'], 'improved')
        audit['audited_action_count'] -= 1
        with self.assertRaises(ValueError):
            am.analyse(rows, PROTOCOL, 10., experiment='coupled', protocol_hash=protocol_hash, mesh_audit=audit)

    def test_cell_metrics_time_to_target_and_misses(self):
        rows = self.rows({'attention_ga': 0.06})
        ref = am.frame_references(rows)
        cells = {(c['method'], c['budget_ms']): c for c in am.analyse(rows, PROTOCOL, 10.)['cells']}
        c = cells[('attention_ga', 10.)]
        self.assertEqual(c['target_reached_fraction'], 1.0)                 # final trace point equals the run's rate; best method defines refs
        self.assertGreater(c['time_to_target_median_ms'], 3.0)              # preparation (1 ms) + trace time (>=2 ms)
        self.assertEqual(c['evaluations_to_target_mean'], 50)
        self.assertEqual(cells[('pair', 10.)]['deadline_misses'], 3)
        self.assertEqual(cells[('attention_ga', 10.)]['deadline_misses'], 0)
        # a run whose trace stops short of the reference margin is counted as not reached
        r = dict(rows[0])
        r['trace'] = [[0.1, ref[r['index']] - 1.0, 1]]
        self.assertIsNone(am.target_hit(r, ref[r['index']], 0.015))
        r['trace'] = [[0.1, ref[r['index']] - 0.01, 7]]
        self.assertEqual(am.target_hit(r, ref[r['index']], 0.015), (1.1, 7))
        with self.assertRaises(ValueError):
            am.target_hit({'trace': [[0.1, 1.0]], 'breakdown_ms': {}}, 1.0, 0.015)

    def test_report_contains_required_statements(self):
        s = am.analyse(self.rows({'attention_ga': 0.06}), PROTOCOL, 10.)
        with tempfile.TemporaryDirectory() as d:
            am.write_report(Path(d) / 'R.md', s, {'experiment': 'specular', 'split': 'test', 'protocol_sha256': 'a' * 64})
            text = (Path(d) / 'R.md').read_text().lower()
        self.assertIn('simulation only', text)
        self.assertIn('adaptation', text)
        self.assertIn('not a reproduction', text)
        self.assertIn('same scene', text)
        self.assertIn('not a held-out environment', text)


class BudgetSelectionAndRefusal(unittest.TestCase):
    def rows(self, misses):
        methods = sel.protocol_methods(PROTOCOL)
        return [{'method': m, 'budget_ms': b, 'deadline_missed': (b, m) in misses} for b in (1, 5, 10, 50, 100) for m in methods for _ in range(2)]

    def test_rule(self):
        methods = sel.protocol_methods(PROTOCOL)
        self.assertEqual(sel.choose(sel.feasibility(self.rows(set()), methods)), 10)
        self.assertEqual(sel.choose(sel.feasibility(self.rows({(10, 'pair')}), methods)), 50)
        self.assertEqual(sel.choose(sel.feasibility(self.rows({(10, 'pair'), (50, 'attention_ga')}), methods)), 100)
        self.assertIsNone(sel.choose(sel.feasibility(self.rows({(10, 'pair'), (50, 'pair'), (100, 'pair')}), methods)))
        incomplete = [r for r in self.rows(set()) if not (r['budget_ms'] == 10 and r['method'] == 'random')]
        self.assertEqual(sel.choose(sel.feasibility(incomplete, methods)), 50)   # a missing method is never feasible

    def test_test_split_requires_frozen_selection(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)
            with self.assertRaises(FileNotFoundError):
                sel.require_frozen_selection(run)
            (run / 'budget_selection.json').write_text(json.dumps({'selected_ms': None}))
            with self.assertRaises(RuntimeError):
                sel.require_frozen_selection(run)
            good = {'selected_ms': 10, 'code_sha256': sel.frozen_code_hashes(), 'checkpoint_sha256': {}}
            (run / 'budget_selection.json').write_text(json.dumps(good))
            self.assertEqual(sel.require_frozen_selection(run)['selected_ms'], 10)
            bad = dict(good, code_sha256={**good['code_sha256'], 'src/atomwise_ris/optimization/search.py': '0' * 64})
            (run / 'budget_selection.json').write_text(json.dumps(bad))
            with self.assertRaises(RuntimeError):
                sel.require_frozen_selection(run)
            (run / 'models' / 'x').mkdir(parents=True)
            (run / 'models' / 'x' / 'best.pt').write_bytes(b'changed')
            (run / 'budget_selection.json').write_text(json.dumps(good))
            with self.assertRaises(RuntimeError):
                sel.require_frozen_selection(run)

    def run_cli(self, script, *extra):
        with tempfile.TemporaryDirectory() as d:
            env = {'PYTHONPATH': str(ROOT / 'src'), 'PATH': '/usr/bin:/bin'}
            p = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), '--run', d, *extra], capture_output=True, text=True,
                               env=env, cwd=ROOT, timeout=300)
        return p

    def test_benchmarks_refuse_test_without_selection(self):
        for script, extra in (('benchmark.py', ()), ('benchmark_coupled.py', ('--mode', 'spatial'))):
            p = self.run_cli(script, '--matched', '--split', 'test', '--test-data', '/nonexistent/test', *extra)
            self.assertNotEqual(p.returncode, 0, script)
            self.assertIn('budget_selection.json', p.stderr, script)
            p = self.run_cli(script, '--split', 'test', *extra)          # legacy mode has no test split
            self.assertNotEqual(p.returncode, 0, script)
            self.assertIn('--matched', p.stderr, script)


if __name__ == '__main__':
    unittest.main()
