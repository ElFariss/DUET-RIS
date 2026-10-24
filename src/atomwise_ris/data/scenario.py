from dataclasses import dataclass
from pathlib import Path
import json,numpy as np
from atomwise_ris.utils.provenance import write_json


@dataclass
class Scenario:
    G: np.ndarray                  # [N,M], same BS and panel for all samples
    H: np.ndarray                  # [samples,K,N]
    D: np.ndarray                  # [samples,K,M]
    positions: np.ndarray          # [samples,K,3]
    cell_positions: np.ndarray     # [N,3]
    trajectory: np.ndarray         # [samples]
    split: np.ndarray              # train/validation/pilot; no final test generated
    metadata: dict

    def validate(self):
        s,k,n = self.H.shape
        assert self.G.shape[0] == n and self.D.shape == (s,k,self.G.shape[1])
        assert self.positions.shape == (s,k,3) and self.cell_positions.shape == (n,3)
        assert len(self.trajectory) == len(self.split) == s
        for tid in np.unique(self.trajectory):
            assert len(set(self.split[self.trajectory == tid])) == 1, 'Trajectory split leakage'
        for a in (self.G,self.H,self.D):
            assert np.isfinite(a).all()
        assert self.metadata['frequency_hz'] == 5.53e9

    def save(self, path):
        self.validate(); p = Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(p, **{k:getattr(self,k) for k in ('G','H','D','positions','cell_positions','trajectory','split')})
        write_json(p.with_suffix('.json'),self.metadata)

    @classmethod
    def load(cls,path):
        z=np.load(path,allow_pickle=False)
        obj=cls(**dict(z), metadata=json.loads(Path(path).with_suffix('.json').read_text()))
        obj.validate(); return obj
