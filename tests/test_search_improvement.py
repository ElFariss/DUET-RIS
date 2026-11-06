import unittest
from time import perf_counter_ns
from unittest import mock

import numpy as np

from atomwise_ris.evaluation.evaluator import Evaluator
from atomwise_ris.optimization.search import (Memory, search,_conditional_pair_proposals,
    _analytical_residual_rank,_score_completed_by_deadline)
from atomwise_ris.optimization import coupled_search
from atomwise_ris.physics.network import CoupledNetwork


def specular_fixture(n=8, seed=31):
    rng = np.random.default_rng(seed)
    k = 2
    return Evaluator(
        rng.normal(size=(k, k)) + 1j * rng.normal(size=(k, k)),
        (rng.normal(size=(n, k, k)) + 1j * rng.normal(size=(n, k, k))) / n,
        np.array([-.55 - .09j, .80 + .13j]), .1, rng.normal(size=(n, 3)))


def coupled_fixture(n=8, seed=37):
    rng = np.random.default_rng(seed)
    m = n + 6
    v = rng.normal(size=(m, m)); x = rng.normal(size=(m, m))
    z = v @ v.T + 10 * np.eye(m) + 1j * (x + x.T)
    return CoupledNetwork(z, np.array([10 + 60j, 10 - 60j]))


class PopulationSearchTests(unittest.TestCase):
    def test_zero_residual_is_exact_analytical_noop(self):
        analytical=np.array([-.3,.2,.7,-.1])
        rank=_analytical_residual_rank(analytical,analytical.copy(),1.15)
        np.testing.assert_array_equal(rank,analytical)
        base_pairs=np.array([[0,1],[0,2],[1,3]])
        proposed=_conditional_pair_proposals(0,analytical,np.zeros_like(analytical),
                                              existing=base_pairs,limit=4,n=4)
        self.assertEqual(proposed.shape,(0,2))
        np.testing.assert_array_equal(base_pairs[np.argmax([4.,3.,2.])],base_pairs[0])

    def test_zero_residual_conditional_search_preserves_partner_selection_and_bounds_calls(self):
        class ZeroResidualPolicy:
            expected_ms=0.
            def __init__(self):self.rows=[]
            def __call__(self,x,analytical):
                self.rows.append(np.asarray(x).copy())
                return np.asarray(analytical).copy()
        ev=specular_fixture(n=8)
        off=search(ev,'attention_ga',80,4,policy=ZeroResidualPolicy(),conditional_pair_policy=False)
        policy=ZeroResidualPolicy()
        on=search(ev,'attention_ga',80,4,policy=policy,conditional_pair_policy=True)
        np.testing.assert_array_equal(on.bits,off.bits)
        self.assertAlmostEqual(on.value,off.value,places=12)
        self.assertEqual(on.evaluations,off.evaluations)
        self.assertLessEqual(len(policy.rows),2)
        self.assertTrue(any(np.count_nonzero(x[:,-5])==1 for x in policy.rows))

    def test_coupled_zero_residual_conditional_search_is_a_noop(self):
        class ZeroResidualPolicy:
            expected_ms=0.
            def __init__(self):self.rows=[]
            def __call__(self,x,analytical):
                self.rows.append(np.asarray(x).copy())
                return np.asarray(analytical).copy()
        ev=coupled_fixture(n=8)
        off=coupled_search.search(ev,'attention_ga',perf_counter_ns()+80_000_000,2,
                                  policy=ZeroResidualPolicy(),conditional_pair_policy=False)
        policy=ZeroResidualPolicy()
        on=coupled_search.search(ev,'attention_ga',perf_counter_ns()+80_000_000,2,
                                 policy=policy,conditional_pair_policy=True)
        np.testing.assert_array_equal(on[0],off[0])
        self.assertAlmostEqual(on[1],off[1],places=12)
        self.assertEqual(on[2],off[2])
        marked=[x for x in policy.rows if np.count_nonzero(x[:,-1])==1]
        self.assertEqual(len(marked),1)

    def test_conditioned_features_keep_parent_gains_and_mark_first(self):
        ev=specular_fixture(n=5)
        bits=np.array([0,1,0,1,0],dtype=np.int8);u=ev.field(bits)
        gains=ev.score_field(ev.flip_fields(bits,u))-ev.score_field(u)
        with mock.patch.object(ev,'flip_fields',wraps=ev.flip_fields) as flips:
            x,returned=ev.features(bits,u,first=2,gains=gains)
        flips.assert_not_called()
        np.testing.assert_allclose(returned,gains)
        np.testing.assert_array_equal(x[:,-5],np.array([0,0,1,0,0],dtype=np.float32))

    def test_conditioned_pair_proposal_finds_exact_beneficial_harmful_first_pair(self):
        ev=Evaluator(np.array([[1+0j,1+0j],[1+0j,1+0j]]),
            np.array([[[.5,1.],[1.,.5]],[[-.4,-1.],[-1.,-.4]]]),
            np.array([0.,1.]),.1,np.zeros((2,3)))
        parent=np.zeros(2,dtype=np.int8);u=ev.field(parent);base=float(ev.score_field(u))
        singles=ev.score_field(ev.flip_fields(parent,u))-base
        self.assertLess(float(singles[0]),0.)
        scores=np.array([0.,1.]);residual=np.array([0.,1.])
        pairs=_conditional_pair_proposals(0,scores,residual,limit=4,n=2)
        np.testing.assert_array_equal(pairs,np.array([[0,1]]))
        exact=float(ev.score_field(ev.pair_fields(parent,u)[0]))
        self.assertGreater(exact,base)

    def test_conditioned_partner_proposals_have_a_hard_size_bound(self):
        n=100;scores=np.arange(n,dtype=float);residual=np.ones(n)
        pairs=_conditional_pair_proposals(37,scores,residual,limit=3,n=n)
        self.assertEqual(pairs.shape,(3,2))
        self.assertTrue(np.all(pairs[:,0]==37))
        self.assertTrue(np.all(pairs[:,1]!=37))
        self.assertEqual(len({tuple(sorted(x)) for x in pairs}),3)

    def test_late_completed_candidate_is_not_count_eligible(self):
        deadline=10_000
        self.assertTrue(_score_completed_by_deadline(deadline,deadline))
        self.assertFalse(_score_completed_by_deadline(deadline+1,deadline))

    def test_coupled_rate_keeps_weak_interference_at_high_snr(self):
        ev = coupled_fixture(n=4)
        field = np.array([[1., 1.e-8], [1.e-8, 1.]], dtype=complex)
        rate = ev.score(field)
        expected = np.log2(1. + 1. / (ev.noise + 1.e-16))
        self.assertAlmostEqual(float(rate), float(expected), places=10)
        self.assertLess(float(rate), float(np.log2(1. + 1. / ev.noise)))

    def test_coupled_features_reuse_precomputed_flip_gains(self):
        ev = coupled_fixture()
        state = ev.state(np.zeros(ev.n, dtype=np.int8))
        gains = ev.moves(state) - ev.score(state.field)
        with mock.patch.object(ev, 'moves', wraps=ev.moves) as moves:
            x, returned = ev.features(state, gains=gains)
        self.assertEqual(x.shape[0], ev.n)
        np.testing.assert_allclose(returned, gains)
        moves.assert_not_called()

    def test_specular_population_uses_full_score_and_seed(self):
        ev = specular_fixture()
        mem = Memory(capacity=8)
        mem.remember([1, 0, 1, 0, 0, 1, 0, 1])
        a = search(ev, 'population_ga', 30, 11, memory=mem)
        b = search(ev, 'population_ga', 30, 11, memory=mem)
        np.testing.assert_array_equal(a.bits, b.bits)
        self.assertAlmostEqual(a.value, float(ev.score(a.bits)), places=12)
        self.assertGreaterEqual(a.evaluations, 1)
        self.assertTrue(all(t <= 30 for t, _, _ in a.trace))

    def test_coupled_population_and_multi_flip_update_match_full_rescore(self):
        ev = coupled_fixture()
        bits = np.array([1, 0, 1, 1, 0, 0, 1, 0], dtype=np.int8)
        state = ev.state(bits)
        changed = ev.flip(state, [0, 3, 6])
        direct = ev.state(changed.bits)
        np.testing.assert_allclose(changed.field, direct.field, rtol=1e-11, atol=1e-11)
        trace = []
        deadline = perf_counter_ns() + 30_000_000
        found, value, count, _ = coupled_search.search(
            ev, 'population_ga', deadline, 17, memory=[bits], trace=trace)
        self.assertAlmostEqual(value, float(ev.score(ev.state(found).field)), places=11)
        self.assertGreaterEqual(count, 1)
        self.assertTrue(all(t <= 30 for t, _, _ in trace))


if __name__ == '__main__':
    unittest.main()
