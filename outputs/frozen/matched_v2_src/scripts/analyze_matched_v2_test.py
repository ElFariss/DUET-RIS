"""Analyze the single matched_v2 test run with the rules frozen in configs/experiments/matched_v2.json.

Per budget: cells (rate on the 161-segment mesh, rate rescored on the 81-segment mesh, p95, misses), the miss rule,
and the frozen contrast family by paired trajectory bootstrap (frames and seeds averaged within a trajectory),
Bonferroni within the budget. A contrast is supported only if its interval excludes zero on both meshes and
neither method is excluded by the miss rule. The primary budget is the confirmatory result; others are secondary.
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
a = ap.parse_args()
protocol = json.loads((ROOT / "configs/experiments/matched_v2.json").read_text())
st = protocol["statistics"]
inp = Path(a.input)
rows = [json.loads(line) for line in inp.open()]
M = np.array([r["method"] for r in rows])
B = np.array([r["budget_ms"] for r in rows], float)
T = np.array([r["trajectory"] for r in rows])
R = {"161": np.array([r["rate"] for r in rows]), "81": np.array([r["rate_81"] for r in rows])}
E = np.array([r["elapsed_ms"] for r in rows])
X = np.array([r["deadline_missed"] for r in rows], bool)
trajectories = np.unique(T)
rng = np.random.default_rng(st["bootstrap_seed"])
idx = rng.integers(0, len(trajectories), (st["bootstrap_resamples"], len(trajectories)))
family = [tuple(c) for c in st["contrasts"]]
alpha = st["alpha"] / len(family)
out = {"input": str(inp), "primary_budget_ms": protocol["run"]["primary_budget_ms"], "cells": [], "contrasts": []}
excluded = set()
for m in protocol["run"]["methods"]:
    for b in protocol["run"]["budgets_ms"]:
        k = (M == m) & (B == b)
        miss = float(X[k].mean())
        if miss > st["max_miss_fraction"]:
            excluded.add((m, b))
        out["cells"].append(dict(method=m, budget_ms=b, n=int(k.sum()), rate=float(R["161"][k].mean()),
                                 rate_81=float(R["81"][k].mean()), mesh_shift=float((R["81"][k] - R["161"][k]).mean()),
                                 p95_ms=float(np.percentile(E[k], 95)), misses=int(X[k].sum()), miss_fraction=miss,
                                 excluded_by_miss_rule=(m, b) in excluded))
for b in protocol["run"]["budgets_ms"]:
    for x, y in family:
        c = dict(a=x, b=y, budget_ms=b, primary=b == out["primary_budget_ms"])
        ok = (x, b) not in excluded and (y, b) not in excluded
        for mesh, rate in R.items():
            per = lambda m: np.array([rate[(M == m) & (B == b) & (T == t)].mean() for t in trajectories])
            d = per(x) - per(y)
            lo, hi = np.percentile(d[idx].mean(1), [100 * alpha / 2, 100 * (1 - alpha / 2)])
            c[mesh] = dict(diff=float(d.mean()), lo=float(lo), hi=float(hi), wins=int((d > 0).sum()), n=len(trajectories))
            ok = ok and lo > 0
        c["supported"] = bool(ok)
        out["contrasts"].append(c)
dest = inp.with_name("analysis_" + inp.stem + ".json")
dest.write_text(json.dumps(out, indent=1) + "\n")
for c in out["cells"]:
    print("%-16s %5g  rate %.3f  r81 %.3f  shift %+.3f  p95 %.2f  miss %d%s" % (
        c["method"], c["budget_ms"], c["rate"], c["rate_81"], c["mesh_shift"], c["p95_ms"], c["misses"],
        "  EXCLUDED" if c["excluded_by_miss_rule"] else ""))
for c in out["contrasts"]:
    print("%s%5g %s - %s  161: %+.3f [%+.3f, %+.3f] %d/%d   81: %+.3f [%+.3f, %+.3f]  %s" % (
        "*" if c["primary"] else " ", c["budget_ms"], c["a"], c["b"], c["161"]["diff"], c["161"]["lo"], c["161"]["hi"],
        c["161"]["wins"], c["161"]["n"], c["81"]["diff"], c["81"]["lo"], c["81"]["hi"],
        "SUPPORTED" if c["supported"] else "not supported"))
print("written", dest)
