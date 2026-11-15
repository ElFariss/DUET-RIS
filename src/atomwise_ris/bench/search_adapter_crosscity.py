"""Sealing, readiness and frame helpers for the cross-city held-out test (NEW module, 2026-11-14).

Declaration: paper-a-ris-physics/docs/crosscity-search-declaration-20261114.md. Earlier adapters are not changed.
Cities: munich, maastricht, utrecht, berlin. Ids <city>-<tag>-NNNN, 48 per city: check 0000-0011, test 0012-0047 (SEALED).
The test split of a city x array opens only with (a) the freeze token and (b) READY.json stating that array's check PASSED.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

import numpy as np

from .search_adapter import BenchSearchNetwork, _as_complex  # noqa: F401

CITIES = ("munich", "maastricht", "utrecht", "berlin")
ID_RE = re.compile(r"^(munich|maastricht|utrecht|berlin)-([a-z0-9]+)-(\d{4})$")
SPLITS = {"check": range(0, 12), "test": range(12, 48)}
DECLARATION = "docs/crosscity-search-declaration-20261114.md"
FREEZE_FILE = "docs/crosscity-search-declaration-20261114.freeze.sha256"
ARRAYS = (64, 128, 256)


def parse_id(tid: str) -> Tuple[str, str, int]:
    m = ID_RE.match(str(tid).strip())
    if not m or int(m.group(3)) >= 48:
        raise PermissionError(f"{tid!r} is not a cross-city trajectory id")
    return m.group(1), m.group(2), int(m.group(3))


def split_of(tid: str) -> str:
    i = parse_id(tid)[2]
    for name, rng in SPLITS.items():
        if i in rng:
            return name
    raise PermissionError(f"{tid!r}: no split")


def freeze_token(root: Union[str, Path]) -> Optional[str]:
    p = Path(root) / FREEZE_FILE
    return p.read_text().strip().lower() if p.is_file() else None


def _verdict(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().upper()
        return True if s in ("PASS", "PASSED", "OK", "TRUE") else (False if s in ("FAIL", "FAILED", "FALSE") else None)
    if isinstance(v, dict):
        for k in ("check_passed", "passed", "pass", "ok", "promoted"):
            if isinstance(v.get(k), bool):
                return v[k]
        for k in ("check", "verdict", "status", "result"):
            if isinstance(v.get(k), (str, bool, dict)):
                r = _verdict(v[k])
                if r is not None:
                    return r
    return None


def check_passed_arrays(ready_file: Union[str, Path, None], city: Optional[str] = None) -> Set[int]:
    """Arrays whose check PASSED according to READY.json. Raises ValueError if absent, ambiguous or inconsistent."""
    if ready_file is None or not Path(ready_file).is_file():
        raise ValueError(f"no READY.json at {ready_file}")
    d = json.loads(Path(ready_file).read_text())
    if city is not None:
        named = d.get("city") or d.get("map") or d.get("map_id")
        if named is not None and str(named).lower() != city:
            raise ValueError(f"{ready_file}: names city {named!r}, expected {city!r}")
    readings = []
    for key in ("check_passed_arrays", "passed_arrays", "ready_arrays", "promoted", "promoted_arrays"):
        if isinstance(d.get(key), list):
            readings.append({int(x) for x in d[key]})
    for cont_key in ("arrays", "per_array", "check", "checks", "cells", "by_array", None):
        cont = d if cont_key is None else d.get(cont_key)
        if not isinstance(cont, dict):
            continue
        vals = {a: _verdict(cont.get(str(a), cont.get(a))) for a in ARRAYS if str(a) in cont or a in cont}
        if vals and all(v is not None for v in vals.values()):
            readings.append({a for a, v in vals.items() if v})
    if not readings:
        raise ValueError(f"{ready_file}: no per-array check verdict found")
    if any(r != readings[0] for r in readings):
        raise ValueError(f"{ready_file}: inconsistent per-array verdicts {readings}")
    return readings[0]


def test_unlocked(root, token, ready_file, city: str, array: int) -> bool:
    expected = freeze_token(root)
    if not expected or not token or str(token).strip().lower() != expected:
        return False
    try:
        return int(array) in check_passed_arrays(ready_file, city)
    except Exception:
        return False


def group_root(h5, city: str, array):
    for path in (f"{city}/{array}", f"{array}"):
        if path in h5:
            return path
    raise KeyError(f"no group for {city} at array {array}")


def trajectory_list(h5, city: str, array, split: str, root=".", token=None, ready_file=None) -> Tuple[List[str], List[int]]:
    """Sorted ids of `city` x `array` in `split` (by index), and the missing indices of that split."""
    if city not in CITIES:
        raise PermissionError(f"unknown city {city!r}")
    if split not in SPLITS:
        raise PermissionError(f"unknown split {split!r}")
    if split == "test" and not test_unlocked(root, token, ready_file, city, array):
        raise PermissionError(f"{city} test split sealed for array {array}")
    names = [k for k in h5[group_root(h5, city, array)].keys() if ID_RE.match(k)]
    mine = [k for k in names if parse_id(k)[0] == city]
    tags = {parse_id(k)[1] for k in mine}
    if len(tags) > 1:
        raise ValueError(f"{city}: more than one id tag {tags}")
    ids = sorted(k for k in mine if parse_id(k)[2] in SPLITS[split])
    have = {parse_id(k)[2] for k in ids}
    return ids, [i for i in SPLITS[split] if i not in have]


def frame_group(h5, array, tid: str):
    city = parse_id(tid)[0]
    for path in (f"{city}/{array}/{tid}", f"{array}/{tid}"):
        if path in h5:
            return path, h5[path]
    raise KeyError(f"no group for {tid} at array {array}")


def sorted_frame_keys(grp) -> List[str]:
    return sorted(grp.keys(), key=lambda x: int(x) if x.isdigit() else x)


def network_from_group(g, grid_width: int) -> BenchSearchNetwork:
    z = _as_complex(g["Z_effective"])
    ci, co, hd = (_as_complex(g[k]) for k in ("C_in", "C_out", "H_direct"))
    loads = _as_complex(g["loads"])
    if loads.shape == (z.shape[0], 2):
        loads = loads[0]
    w = _as_complex(g["precoder"])
    return BenchSearchNetwork(z, co, ci, hd, loads, w=w, noise=float(g.attrs["noise"]), grid_width=grid_width)


def pathless_users(ev: BenchSearchNetwork) -> np.ndarray:
    hd = ev.d
    r0 = ev.channel(np.zeros(ev.n, int)) - hd
    return (np.linalg.norm(hd, axis=1) == 0.0) & (np.linalg.norm(r0, axis=1) == 0.0)
