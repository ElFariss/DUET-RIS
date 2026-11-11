"""Production watcher (lead, 2026-11-10); replaces first_case_watch.py. Read-only on production outputs.
Every 10 min:
 1. first-case verification: for each scope and map, once a case has all 3 channel shards, run
    check_bench_production_progress.py --verify-finished on ONE case -> first_case_checks/<scope>-<map>.json;
    FIRST_CASES_OK when all six pass, FIRST_CASES_FAILED on any non-pass.
 2. liveness: writes LIVENESS.json every round; writes LIVENESS_ALERT (and keeps it) when production is not
    PRODUCTION_DONE and any of: PRODUCTION_FAILED exists; tmux session cris-channels is gone; a map/worker/job
    FAILED marker exists; a channel stage is active and nothing (shard sidecar, transient record, worker log,
    chain log) changed for more than 60 min.
Exits when PRODUCTION_DONE exists or after 96 h."""
import json, subprocess, sys, time
from pathlib import Path
V = Path("/var/tmp/atomwise-bench-production-full-20261109")
B = Path("/mnt/home/faris/projects/bench-production-full-20261109")
PY = "/mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python"
M = V / "outputs/runs/bench_production_full_20261109"
SCOPES = {"natural": (M / "cases.json", B / "trace-natural", V / "channels-natural"),
          "challenge": (M / "challenge_cases.json", B / "trace-challenge", V / "channels-challenge")}
MAPS = ("munich", "rotterdam", "maastricht")
STALE_S = 3600
out = V / "first_case_checks"; out.mkdir(exist_ok=True)
env = {"PYTHONPATH": f"{V}/deps:{V}/src:{V}/scripts", "PATH": "/usr/bin:/bin", "OMP_NUM_THREADS": "1"}
now_s = lambda: time.strftime("%FT%TZ", time.gmtime())
def write(p, obj):
    t = p.with_name(p.name + ".tmp"); t.write_text(json.dumps(obj, indent=2) + "\n"); t.replace(p)
def first_cases():
    pending = []
    for scope, (man, tr, ch) in SCOPES.items():
        for m in MAPS:
            res = out / f"{scope}-{m}.json"
            if res.exists():
                continue
            if not any(ch.glob(f"{m}/cases/*/array_*.json")):
                pending.append(f"{scope}-{m}"); continue
            p = subprocess.run([PY, str(V / "scripts/check_bench_production_progress.py"), "--manifest", str(man),
                                "--trace-out", str(tr), "--channel-out", str(ch), "--verify-finished",
                                "--maps", m, "--max-cases", "1"], cwd=V, env=env, capture_output=True, text=True)
            try:
                d = json.loads(p.stdout)
            except Exception:
                print(now_s(), scope, m, "progress error", p.returncode, p.stderr[-500:], flush=True)
                pending.append(f"{scope}-{m}"); continue
            v = {k: x for k, x in d.get("verified_cases", {}).items() if x.get("map_id") == m}
            if v:
                write(res, {"checked_utc": now_s(), "verified_cases": v, "map_summary": d["maps"].get(m)})
                print(now_s(), scope, m, {k: x["status"] for k, x in v.items()}, flush=True)
            else:
                pending.append(f"{scope}-{m}")
    results = [json.loads(f.read_text()) for f in out.glob("*-*.json")]
    bad = [k for r in results for k, x in r["verified_cases"].items() if x.get("status") != "pass"]
    if bad:
        (V / "FIRST_CASES_FAILED").write_text(json.dumps(bad) + "\n")
    elif not pending and not (V / "FIRST_CASES_OK").exists():
        (V / "FIRST_CASES_OK").write_text(now_s() + "\n")
    return pending, bad
def liveness():
    reasons, info = [], {}
    if (V / "PRODUCTION_FAILED").exists():
        reasons.append("PRODUCTION_FAILED: " + (V / "PRODUCTION_FAILED").read_text().replace("\n", " "))
    if subprocess.run(["tmux", "has-session", "-t", "=cris-channels"], capture_output=True).returncode != 0:
        reasons.append("tmux session cris-channels is not running")
    newest = (V / "production_chain.log").stat().st_mtime if (V / "production_chain.log").exists() else 0.0
    channel_stage_active = False
    for scope, (_, _, ch) in SCOPES.items():
        if not ch.exists():
            continue
        for p in list(ch.glob("*/FAILED")) + list(ch.glob("workers/*.FAILED")) + list(ch.glob("JOB_FAILED")):
            reasons.append(f"{scope}: marker {p.relative_to(V)}")
        shards = list(ch.glob("*/cases/*/array_*.json"))
        done = [s for s in shards if not s.name.endswith((".FAILED.json", ".transient.json"))]
        info[scope] = {"shards_done": len(done),
                       "unit_failed": sum(s.name.endswith(".FAILED.json") for s in shards),
                       "unit_transient_waiting": sum(s.name.endswith(".transient.json") for s in shards),
                       "job_done": (ch / "JOB_DONE").exists()}
        if any(ch.glob("workers/*.RUNNING")):
            channel_stage_active = True
        for p in shards + list(ch.glob("workers/*.log")):
            try:
                newest = max(newest, p.stat().st_mtime)
            except OSError:
                pass
    age = time.time() - newest
    info["seconds_since_last_change"] = round(age)
    if channel_stage_active and age > STALE_S:
        reasons.append(f"no shard, transient record or log change for {age/60:.0f} min during a channel stage")
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            info["mem_available_gib"] = round(int(line.split()[1]) / 1024 ** 2, 1)
    return reasons, info
deadline = time.time() + 96 * 3600
while time.time() < deadline:
    if (V / "PRODUCTION_DONE").exists():
        write(V / "LIVENESS.json", {"checked_utc": now_s(), "status": "done"})
        (V / "LIVENESS_ALERT").unlink(missing_ok=True)
        print(now_s(), "PRODUCTION_DONE; watcher exits", flush=True); sys.exit(0)
    try:
        pending, bad = first_cases()
        reasons, info = liveness()
    except Exception as e:  # the watcher must not die silently
        pending, bad, reasons, info = [], [], [f"watcher error: {type(e).__name__}: {e}"], {}
    if bad:
        reasons.append(f"first-case verification failed: {bad}")
    status = "alert" if reasons else "ok"
    write(V / "LIVENESS.json", {"checked_utc": now_s(), "status": status, "reasons": reasons,
                                "first_cases_pending": pending, **info})
    if reasons:
        write(V / "LIVENESS_ALERT", {"raised_utc": now_s(), "reasons": reasons})
    print(now_s(), status, reasons, "pending", pending, info, flush=True)
    time.sleep(600)
write(V / "LIVENESS_ALERT", {"raised_utc": now_s(), "reasons": ["watcher 96 h cap reached without PRODUCTION_DONE"]})
sys.exit(2)
