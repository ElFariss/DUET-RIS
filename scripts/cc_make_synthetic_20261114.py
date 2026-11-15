#!/usr/bin/env python3
"""SYNTHETIC data for the cross-city pipeline dry run only (random operators, no city geometry). Never analysed.
Usage: cc_make_synthetic_20261114.py ROOT CITY [ARRAYS=64,128] [PASS=64,128]
Writes ROOT/CITY/channels/package/channels/channel_realizations.h5, ROOT/CITY/channels/output_sha256sums, ROOT/CITY/READY.json.
Trajectories: check 0000, 0001 and test 0012, 0013; 16 frames each.
"""
import hashlib
import json
import sys
from pathlib import Path

import h5py
import numpy as np

from atomwise_ris.hybrid.operator import HybridCoupledNetwork

root, city = Path(sys.argv[1]), sys.argv[2]
arrays = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "64,128").split(",")]
passed = [int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else "64,128").split(",")]
rng = np.random.default_rng(abs(hash(city)) % 2**32)
d = root / city / "channels" / "package" / "channels"; d.mkdir(parents=True, exist_ok=True)
h5p = d / "channel_realizations.h5"
with h5py.File(h5p, "w") as f:
    f.attrs["SYNTHETIC"] = "dry run only"
    for a in arrays:
        for i in (0, 1, 12, 13):
            tid = f"{city}-syn-{i:04d}"
            for fr in range(16):
                g = f.create_group(f"{city}/{a}/{tid}/{fr * 7}")
                n, m, k = a, 4, 3
                A_ = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
                Z = (A_ + A_.T) * 0.05 + np.eye(n) * (50 + 20j)
                ci = rng.normal(size=(n, m)) + 1j * rng.normal(size=(n, m))
                co = (rng.normal(size=(k, n)) + 1j * rng.normal(size=(k, n))) * 0.5
                hd = rng.normal(size=(k, m)) + 1j * rng.normal(size=(k, m))
                ld = np.array([1 + 5j, 1 - 40j])
                ev = HybridCoupledNetwork(Z, co, ci, hd, ld, noise=1.0)
                g["Z_effective"] = Z; g["C_in"] = ci; g["C_out"] = co; g["H_direct"] = hd; g["loads"] = ld
                g["precoder"] = ev.w; g.attrs["noise"] = 1.0
sh = hashlib.sha256(h5p.read_bytes()).hexdigest()
(root / city / "channels" / "output_sha256sums").write_text(f"{sh}  package/channels/channel_realizations.h5\n")
(root / city / "READY.json").write_text(json.dumps({"city": city, "SYNTHETIC": True,
    "per_array": {str(a): {"check": "PASS" if a in passed else "FAIL"} for a in arrays}}, indent=1) + "\n")
print(city, h5p, sh[:12])
