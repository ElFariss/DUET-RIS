#!/usr/bin/env python3
"""Merge cross-city unit or pool outputs into the schema of rr3_test_summary.json.

Usage: collect_crosscity_20261114.py LABEL OUT_PREFIX DIR [DIR ...]
Each DIR holds metrics.json, verdicts.json and either run_record.json (one unit) or pool_record.json (a pool).
Writes OUT_PREFIX.json, OUT_PREFIX_metrics.csv, OUT_PREFIX.md.
"""
import csv
import json
import sys
from pathlib import Path

FAMILY = ("H1", "H2", "H5", "C6", "C7")
NAMES = {"H1": "b35−pair", "H2": "b35−ME-GA", "H5": "b35−NSGA-II", "C6": "pair−NSGA-II", "C7": "pair−ME-GA"}
label, prefix, dirs = sys.argv[1], sys.argv[2], [Path(d) for d in sys.argv[3:]]
out = {"label": label, "family": {h: NAMES[h] for h in FAMILY}, "arrays": {}}
rows = []
for d in dirs:
    m = json.load(open(d / "metrics.json")); v = json.load(open(d / "verdicts.json"))
    a = m["cells"][0]["array"]
    ent = {"dir": str(d), "rows": m["meta"]["rows"], "trajectories": v.get("trajectories"), "metrics": m["cells"],
           "verdicts": v["verdicts"], "family_size": v["family_size"], "descriptive_contrasts_95": v.get("descriptive_contrasts_95")}
    if (d / "run_record.json").is_file():
        rec = json.load(open(d / "run_record.json"))
        flags = json.load(open(d / "flags.json")) if (d / "flags.json").is_file() else {}
        cs = json.load(open(d / "cpu_samples_summary.json")) if (d / "cpu_samples_summary.json").is_file() else None
        ent.update(host=rec.get("hostname"), cpu=rec["args"]["cpu"], cpu_affinity=rec.get("cpu_affinity"),
                   cpu_model=rec.get("cpu_model"), numpy=rec.get("numpy"), city=rec["args"].get("city"),
                   channel_file_sha256=rec.get("channel_file_sha256"), ready_file_sha256=rec.get("ready_file_sha256"),
                   check_passed_arrays=rec.get("check_passed_arrays"), seeds=rec["args"]["seeds"],
                   trajectories_used=rec.get("trajectories_used"), missing_indices=rec.get("missing_indices"),
                   nsga2_sha256=(rec.get("nsga2_ready") or {}).get("sha256"), resumes=rec.get("resumes"),
                   frames_flagged=sum(1 for x in flags.values() if x.get("flagged")), frames_checked=len(flags),
                   cpu_samples_summary=cs)
    if (d / "pool_record.json").is_file():
        ent["pool"] = json.load(open(d / "pool_record.json"))
    out["arrays"][str(a)] = ent
    rows += m["cells"]
json.dump(out, open(prefix + ".json", "w"), indent=1)
keys = ["array", "budget_ms", "method", "calls", "trajectories", "M1_rate_mean", "M2_latency_ms_mean", "M2_latency_ms_p95",
        "M3_budget_ms", "M3_evaluations_mean", "M3_evaluations_median", "M3_evaluations_p95", "miss_fraction_search_clock",
        "excluded_by_0p5pct_rule", "latency_with_rescore_ms_mean"]
with open(prefix + "_metrics.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
L = [f"# {label}", "", "## Primary metrics (M1 bit/s/Hz, M2 search_elapsed_ms mean/p95, M3 budget + evaluations)", "",
     "| Array | Budget ms | Method | M1 | M2 mean | M2 p95 | M3 evals mean | Miss % | Excl. |", "|---:|---:|---|---:|---:|---:|---:|---:|---|"]
for c in rows:
    L.append(f"| {c['array']} | {c['budget_ms']:g} | {c['method']} | {c['M1_rate_mean']:.4f} | {c['M2_latency_ms_mean']:.2f} | "
             f"{c['M2_latency_ms_p95']:.2f} | {c['M3_evaluations_mean']:.0f} | {100*c['miss_fraction_search_clock']:.2f} | "
             f"{'YES' if c['excluded_by_0p5pct_rule'] else ''} |")
fmt = lambda d: (f"{d['diff']:+.4f} [{d['ci'][0]:+.4f}, {d['ci'][1]:+.4f}] **{d['verdict']}**" if "diff" in d else d["verdict"])
L += ["", "## Contrasts (99% Bonferroni intervals, family 5; 50 ms primary)", "",
      "| Array | Budget | N traj | " + " | ".join(f"{h} {NAMES[h]}" for h in FAMILY) + " |", "|---:|---:|---:|" + "---|" * len(FAMILY)]
for a, s in out["arrays"].items():
    for v in s["verdicts"]:
        n = v["H1"].get("n", "")
        L.append(f"| {a} | {v['budget_ms']:g}{' (primary)' if v['primary'] else ''} | {n} | " + " | ".join(fmt(v[h]) for h in FAMILY) + " |")
L += ["", "## Provenance", ""]
for a, s in out["arrays"].items():
    if "pool" in s:
        L.append(f"- {a}: pool of {s['pool'].get('cities')} ({s['rows']} rows)")
    else:
        L.append(f"- {a}: {s.get('city')} on {s.get('host')} CPU {s.get('cpu')} ({s.get('cpu_model')}), seeds {len(s.get('seeds') or [])}, "
                 f"trajectories {s.get('trajectories_used')} (missing {s.get('missing_indices')}), flagged {s.get('frames_flagged')}/"
                 f"{s.get('frames_checked')}, resumes {len(s.get('resumes') or [])}, rows {s['rows']}")
open(prefix + ".md", "w").write("\n".join(L) + "\n")
print("\n".join(L[:4]))
