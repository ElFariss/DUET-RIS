import unittest
import numpy as np
from atomwise_ris.core import Evaluator, Scenario, ResponseModel, precoder, C0
from atomwise_ris.optimization.search import local_optimum, Memory, search

def fixture(n=8,k=2,seed=7):
    r=np.random.default_rng(seed)
    return Evaluator(r.normal(size=(k,k))+1j*r.normal(size=(k,k)),
                     (r.normal(size=(n,k,k))+1j*r.normal(size=(n,k,k)))/n,
                     np.array([-.55-.09j,.80+.13j]),.1,r.normal(size=(n,3)))

class Correctness(unittest.TestCase):
    def test_cached_flips_pairs_full(self):
        e=fixture(64);b=np.random.default_rng(1).integers(2,size=64,dtype=np.int8)
        np.testing.assert_allclose(e.field(b),e.full_field(b),atol=1e-14)
        singles=np.tile(b,(64,1));singles[np.arange(64),np.arange(64)]^=1
        np.testing.assert_allclose(e.flip_fields(b),e.full_field(singles),atol=1e-14)
        pairbits=np.tile(b,(2016,1));pairbits[np.arange(2016)[:,None],e.pairs]^=1
        np.testing.assert_allclose(e.pair_fields(b),e.full_field(pairbits),atol=1e-14)
        self.assertEqual(len(e.pairs),2016)

    def test_exhaustive_small_array(self):
        e=fixture();bits=((np.arange(256)[:,None]>>np.arange(8))&1).astype(np.int8)
        a=e.score(bits);b=e.score_field(e.full_field(bits))
        np.testing.assert_allclose(a,b,atol=1e-13)
        self.assertEqual(int(a.argmax()),int(b.argmax()))
        q,v=local_optimum(e,bits[0],pairs=True)
        self.assertLessEqual(v,float(a.max())+1e-12)
        self.assertTrue(np.all(e.score_field(e.flip_fields(q))<=v+1e-12))
        self.assertTrue(np.all(e.score_field(e.pair_fields(q))<=v+1e-12))

    def test_single_path_aperture(self):
        f=5.53e9;lam=C0/f;area=.020*.013;d1=20.;d2=4.;gamma=.7*np.exp(.8j)
        leg=lambda d:lam/(4*np.pi*d)*np.exp(-2j*np.pi*d/lam)
        cascade=leg(d1)*leg(d2)*4*np.pi*area/lam**2*gamma
        analytical=area/(4*np.pi*d1*d2)*np.exp(-2j*np.pi*(d1+d2)/lam)*gamma
        np.testing.assert_allclose(cascade,analytical,rtol=1e-11)
        e=Evaluator(np.zeros((1,1)),np.array([[[cascade/gamma]]]),np.array([gamma,gamma]),1e-12,np.zeros((1,3)))
        self.assertAlmostEqual(float(e.score([0])),np.log2(1+abs(analytical)**2/1e-12),places=12)

    def test_precoder_power(self):
        d=np.array([[1,2j,3,4],[1j,2,0,2]])
        self.assertAlmostEqual(float(np.sum(abs(precoder(d,.1))**2)),.1,places=12)

    def test_blocked_direct_uses_reference_ris_path(self):
        s=Scenario(np.eye(2,dtype=complex),np.eye(2,dtype=complex)[None],np.zeros((1,2,2),complex),
                   np.zeros((1,2,3)),np.zeros((2,3)),np.array([0]),np.array(['train']),
                   {'frequency_hz':5.53e9,'power_w':.1,'cell_area_m2':.00026,'noise_w':.01})
        e=Evaluator.from_scenario(s,0,ResponseModel(5.53e9,np.array([.7,-.7]),{}))
        self.assertGreater(float(e.score([0,0])),0.)
        self.assertAlmostEqual(e.metadata['precoder_power_w'],.1,places=12)

    def test_memory_and_budget(self):
        m=Memory();m.enter('a');m.remember([0,1]);m.enter('a');self.assertEqual(len(m.patterns),1)
        m.enter('b');self.assertEqual(len(m.patterns),0)
        e=fixture();r=search(e,'pair',5,7)
        self.assertAlmostEqual(r.value,float(e.score(r.bits)),places=12)
        self.assertTrue(all(t<=5 for t,v in r.trace[1:]))

    def test_harmful_first_pair(self):
        # Opposite-signed perturbations: either single move harms the useful field,
        # but their joint residual enhances it. Explicit non-additive supervision.
        e=Evaluator(np.array([[1+0j,1+0j],[1+0j,1+0j]]),
                    np.array([[[.5,1.],[1.,.5]],[[-.4,-1.],[-1.,-.4]]]),
                    np.array([0.,1.]),.1,np.zeros((2,3)))
        self.assertLess(float(e.score([1,0])),float(e.score([0,0])))
        self.assertGreater(float(e.score([1,1])),float(e.score([0,0])))

if __name__=='__main__':unittest.main()
