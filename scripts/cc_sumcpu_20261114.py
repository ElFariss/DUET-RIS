#!/usr/bin/env python3
"""Summarise a sample_cpu_load.py log: per watched CPU mean/max busy, samples above 5%, foreign processes."""
import json
import sys

S = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
w = [str(x) for x in S[0]["watched_cpus"]] if S else []
out = {"samples": len(S), "first": S[0]["utc"] if S else None, "last": S[-1]["utc"] if S else None, "watched": w}
for k in w:
    v = [s["cpu_busy"].get("cpu" + k, 0) for s in S]
    out["cpu" + k] = {"mean": sum(v) / len(v), "max": max(v), "n_over_5pct": sum(x > 0.05 for x in v)}
fp = [(s["utc"], p["comm"], p["user"], p["psr"], p["cpu_percent"]) for s in S for p in s.get("watched_processes", [])
      if p.get("user") != "faris"]
out["foreign_process_samples"] = len(fp)
out["foreign_examples"] = fp[:5]
out["loadavg_max"] = max(s["loadavg_1min"] for s in S) if S else None
print(json.dumps(out))
