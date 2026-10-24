from dataclasses import dataclass
from pathlib import Path
import json,numpy as np
from atomwise_ris.utils.provenance import sha256


@dataclass
class ResponseModel:
    frequency_hz: float
    gamma: np.ndarray
    metadata: dict

    @classmethod
    def from_table(cls, path, frequency_hz):
        a = np.genfromtxt(path, delimiter=",", names=True)
        f = frequency_hz / 1e9
        if not a['frequency_ghz'].min() <= f <= a['frequency_ghz'].max():
            raise ValueError('Response extrapolation is prohibited')
        g = []
        for state in ('off', 'on'):
            db = np.interp(f, a['frequency_ghz'], a[state+'_db'])
            ph = np.interp(f, a['frequency_ghz'], np.unwrap(np.deg2rad(a[state+'_deg'])))
            g.append(10**(db/20) * np.exp(1j*ph))
        meta = json.loads(Path(path).with_suffix('.json').read_text())
        return cls(frequency_hz, np.asarray(g), meta | {'table_sha256': sha256(path)})
