import unittest
import numpy as np
import torch
from atomwise_ris.models.coupled_policy import CoupledPolicy,LinkGRU
from atomwise_ris.models.forecast import passive_reciprocal,predict

class CoupledLearning(unittest.TestCase):
    def test_atom_permutation_equivariance(self):
        torch.manual_seed(4);torch.set_num_threads(1)
        x=torch.randn(2,8,16);x[:,:,-1]=0;x[:,2,-1]=1;g=torch.randn(2,8);p=torch.randperm(8)
        for kind in ['mlp','attention']:
            m=CoupledPolicy(kind=kind).eval()
            with torch.inference_mode():np.testing.assert_allclose(m(x[:,p],g[:,p]),m(x,g)[:,p],atol=1e-6)
    def test_forecast_reciprocal_passive_projection(self):
        rng=np.random.default_rng(4);z=rng.normal(size=(8,8))+1j*rng.normal(size=(8,8));q=passive_reciprocal(z)
        np.testing.assert_allclose(q,q.T,atol=1e-10)
        self.assertGreaterEqual(np.linalg.eigvalsh(q.real).min(),0.)
        s=np.linalg.solve((q+50*np.eye(8)).T,(q-50*np.eye(8)).T).T
        self.assertLessEqual(np.linalg.svd(s,compute_uv=False)[0],1.+1e-10)
    def test_temporal_constant_and_ramp(self):
        h=np.array([(60+t)*np.eye(4,dtype=complex) for t in range(4)])
        np.testing.assert_allclose(predict(h,'persistence'),h[-1])
        np.testing.assert_allclose(predict(h,'linear'),64*np.eye(4),atol=1e-12)
        with self.assertRaises(ValueError):predict(h[:3],'linear')
if __name__=='__main__':unittest.main()
