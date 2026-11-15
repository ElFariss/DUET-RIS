#!/usr/bin/env python3
"""Verdicts for the cross-city test (declaration paper-a-ris-physics/docs/crosscity-search-declaration-20261114.md s.5).

Input: JSON of the unchanged analyze_bench_search.py (--clock search --family-size 5, contrasts H1 H2 H5 C6 C7) and,
optionally, the descriptive-contrast JSON (family size 1). Writes PREFIX.json and PREFIX.md.
Usage: verdicts_crosscity.py ANALYSIS.json [DESCRIPTIVE.json] PREFIX
"""
import json
import sys

B35, PAIR, MEGA, NSGA = "pair_plus_b35", "pair", "me_ga", "nsga2"
FAMILY = {"H1": (B35, PAIR), "H2": (B35, MEGA), "H5": (B35, NSGA), "C6": (PAIR, NSGA), "C7": (PAIR, MEGA)}
EVO = {MEGA, NSGA}

an = json.load(open(sys.argv[1]))
desc = json.load(open(sys.argv[2])) if len(sys.argv) > 3 else None
prefix = sys.argv[-1]
cells = {(c["array"], c["budget_ms"], c["method"]): c for c in an["cells"]}
con = {(c["array"], c["budget_ms"], c["method_a"], c["method_b"]): c for c in an["contrasts"]}
arrays = sorted({c["array"] for c in an["cells"]})
budgets = sorted({c["budget_ms"] for c in an["cells"]})
out = {"family_size": an["summary"]["family_size"], "bonferroni_alpha": an["summary"]["bonferroni_alpha"],
       "trajectories": an["summary"]["trajectories_count"], "verdicts": []}
for a in arrays:
    for b in budgets:
        v = {"array": a, "budget_ms": b, "primary": b == 50.0}
        excl = lambda m: bool(cells.get((a, b, m), {}).get("excluded_by_miss_rule", False))
        for h, (x, y) in FAMILY.items():
            c = con.get((a, b, x, y))
            if c is None:
                v[h] = {"verdict": "not run"}
                continue
            evo = [m for m in (x, y) if m in EVO]
            if evo and excl(evo[0]):
                verdict = "not testable at this budget"
            elif excl(x) or excl(y):
                verdict = "FAIL (excluded by miss rule)"
            elif c["ci_lo"] > 0:
                verdict = "PASS"
            elif c["ci_hi"] < 0:
                verdict = "FAIL (below 0)"
            else:
                verdict = "FAIL"
            v[h] = {"contrast": f"{x} - {y}", "diff": c["diff"], "ci": [c["ci_lo"], c["ci_hi"]],
                    "wlt": [c["wins"], c["losses"], c["ties"]], "n": c["n_trajectories"], "verdict": verdict,
                    "excluded": {x: excl(x), y: excl(y)}}
        out["verdicts"].append(v)
if desc:
    out["descriptive_contrasts_95"] = desc["contrasts"]
json.dump(out, open(prefix + ".json", "w"), indent=1)
fmt = lambda d: (f"{d['diff']:+.4f} [{d['ci'][0]:+.4f}, {d['ci'][1]:+.4f}] {d['verdict']}" if "diff" in d else d["verdict"])
L = [f"# Cross-city verdicts (search clock, Bonferroni family {out['family_size']}, {out['trajectories']} trajectories)", "",
     "| Array | Budget | H1 b35-pair | H2 b35-ME-GA | H5 b35-NSGA-II | C6 pair-NSGA-II | C7 pair-ME-GA |",
     "|---|---|---|---|---|---|---|"]
for v in out["verdicts"]:
    L.append(f"| {v['array']} | {v['budget_ms']:g}{' (primary)' if v['primary'] else ''} | " + " | ".join(fmt(v[h]) for h in FAMILY) + " |")
open(prefix + ".md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
