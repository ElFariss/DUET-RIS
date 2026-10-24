import unittest
import numpy as np
import torch
from atomwise_ris.models import EditPolicy
from test_core import fixture

class Learning(unittest.TestCase):
    def test_permutation_equivariance_and_shape(self):
        torch.set_num_threads(1);ev=fixture(8);x,g=ev.features(np.zeros(8,dtype=np.int8),first=3)
        perm=np.array([5,7,0,2,1,4,6,3])
        for kind in ['attention','mlp']:
            model=EditPolicy(x.shape[-1],kind).eval()
            with torch.inference_mode():
                original=model(torch.from_numpy(x)[None],torch.from_numpy(g.astype(np.float32))[None])[0].numpy()
                permuted=model(torch.from_numpy(x[perm])[None],torch.from_numpy(g[perm].astype(np.float32))[None])[0].numpy()
            np.testing.assert_allclose(original[perm],permuted,atol=1e-6)

    def test_condition_marker(self):
        e=fixture();x,_=e.features(np.zeros(8,dtype=np.int8),first=3)
        self.assertEqual(int(x[:,-5].sum()),1);self.assertEqual(x[3,-5],1)

if __name__=='__main__':unittest.main()
