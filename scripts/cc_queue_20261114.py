#!/usr/bin/env python3
"""Cross-city queue for one machine and one array size (declaration crosscity-search-declaration-20261114.md s.6-9).

comm3: --array 128 --root <cross-city workspace on comm3>; also stages each READY city for comm2 under --stage-dir
(symlink to the channel file + READY.json + one-line sha256 list) behind a LAN-only http server until the cutoff.
comm2: --array 64 --stage-url http://10.34.0.213:18765 --data-dir ~/crosscity-data; fetches staged cities and verifies.
Each city x array test runs once, on the first free slot whose core and sibling are idle (< 10% over 30 s).
State: $W/runs/queue_a<A>.log, $W/runs/units/<city>_a<A>.json, test outputs $W/runs/test/<city>/a<A>/.
Env: W, PY, PYDEPS.
"""
import argparse
import calendar
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

W = Path(os.environ["W"]); PY = os.environ["PY"]; PYDEPS = os.environ.get("PYDEPS", "")
sys.path.insert(0, str(W / "src"))
for _d in reversed([x for x in PYDEPS.split(":") if x]):
    sys.path.insert(0, _d)
from atomwise_ris.bench import search_adapter_crosscity as rr  # noqa: E402

SEEDS_TEST = "7,19,43,3,11,23,31,59,67,83"
R = W / "runs"; U = R / "units"; U.mkdir(parents=True, exist_ok=True)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(a, msg):
    with open(R / f"queue_a{a}.log", "a") as f:
        f.write(f"[{now()}] {msg}\n")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def tmux_alive(name):
    return subprocess.run(["tmux", "-L", "cc", "has-session", "-t", name], capture_output=True).returncode == 0


def tmux_start(name, cmd):
    subprocess.run(["tmux", "-L", "cc", "new-session", "-d", "-s", name, cmd], check=True)


def busy(cpus, secs=30):
    def rd():
        out = {}
        for line in open("/proc/stat"):
            p = line.split()
            if p[0].startswith("cpu") and p[0] != "cpu":
                t = list(map(int, p[1:])); out[int(p[0][3:])] = (sum(t) - t[3] - t[4], sum(t))
        return out
    a = rd(); time.sleep(secs); b = rd()
    return {c: (b[c][0] - a[c][0]) / max(1, b[c][1] - a[c][1]) for c in cpus}


def locate(city_dir):
    """(channel_file, sums_file) for one city directory, or raise ValueError."""
    chans = sorted({p.resolve() for p in city_dir.rglob("channel_realizations.h5")})
    pk = [p for p in chans if p.parent.name == "channels" and p.parent.parent.name == "package"]
    chans = pk or chans
    if len(chans) != 1:
        raise ValueError(f"{city_dir}: {len(chans)} channel files")
    ch = chans[0]
    for s in sorted(city_dir.rglob("*sha256sums*")) + sorted(city_dir.rglob("*.sha256")):
        try:
            for line in s.read_text().splitlines():
                if line.strip() and (s.parent / line.split(None, 1)[1].strip().lstrip("*")).resolve() == ch:
                    return ch, s.resolve()
        except Exception:
            continue
    raise ValueError(f"{city_dir}: no sha256 list covers {ch}")


def fetch(url, dst):
    tmp = Path(str(dst) + ".part")
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as o:
        shutil.copyfileobj(r, o, 1 << 22)
    tmp.replace(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--array", type=int, required=True, choices=[64, 128])
    ap.add_argument("--slots", required=True, help="e.g. 4:10,5:11")
    ap.add_argument("--root", default=None)
    ap.add_argument("--stage-dir", default=None)
    ap.add_argument("--stage-bind", default="10.34.0.213:18765")
    ap.add_argument("--stage-url", default=None)
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--cutoff", default="2026-11-15T02:00:00Z")
    ap.add_argument("--min-run-min", type=float, default=40.0)
    ap.add_argument("--yield-to", type=int, default=None,
                    help="fallback mode: start a unit only when no unit of this other array is eligible-pending on this machine")
    a = ap.parse_args()
    A = a.array
    slots = [tuple(map(int, s.split(":"))) for s in a.slots.split(",")]
    cutoff = calendar.timegm(time.strptime(a.cutoff, "%Y-%m-%dT%H:%M:%SZ"))
    token = rr.freeze_token(W)
    assert token, "freeze token missing"
    log(A, f"queue start slots={slots} root={a.root} stage_url={a.stage_url} cutoff={a.cutoff}")
    smoke_done = (R / f"SMOKE_OK_a{A}").is_file()
    while True:
        t = time.time()
        # --- comm3: stage READY cities for comm2 and keep the LAN server up
        if a.stage_dir and a.root:
            sd = Path(a.stage_dir); sd.mkdir(parents=True, exist_ok=True)
            for city in rr.CITIES:
                rf = Path(a.root) / city / "READY.json"
                if not rf.is_file() or (sd / city / "index.json").is_file():
                    continue
                try:
                    ch, sums = locate(Path(a.root) / city)
                    line = [l for l in sums.read_text().splitlines() if l.strip() and (sums.parent / l.split(None, 1)[1].strip().lstrip("*")).resolve() == ch][0]
                    c = sd / city; c.mkdir(exist_ok=True)
                    (c / "channel_realizations.h5").unlink(missing_ok=True); (c / "channel_realizations.h5").symlink_to(ch)
                    shutil.copy(rf, c / "READY.json")
                    (c / "sums_one.txt").write_text(f"{line.split()[0]}  channel_realizations.h5\n")
                    (c / "index.json").write_text(json.dumps({"staged_utc": now(), "source_channel": str(ch), "source_sums": str(sums),
                                                              "ready_sha256": sha(c / "READY.json"), "channel_sha256": line.split()[0]}) + "\n")
                    log(A, f"staged {city} for comm2 ({ch})")
                except Exception as e:  # noqa: BLE001
                    log(A, f"stage {city} not possible yet: {e}")
            if t < cutoff and not tmux_alive("cchttp"):
                host, port = a.stage_bind.split(":")
                tmux_start("cchttp", f"timeout {int(cutoff - t) + 600} python3 -m http.server {port} --bind {host} --directory {sd}")
                log(A, "stage http server started")
        # --- comm2 mode: if comm3 has taken over the 64 units (declared fallback), never start anything here
        if a.stage_url:
            try:
                urllib.request.urlopen(f"{a.stage_url}/FALLBACK_64_ON_COMM3.json", timeout=20).read()
                log(A, "FALLBACK_64_ON_COMM3 published by comm3: this queue stops without starting units")
                (R / f"QUEUE_YIELDED_a{A}").write_text(now() + "\n")
                return 0
            except Exception:
                pass
        # --- eligibility per city
        units = {}
        for city in rr.CITIES:
            st_path = U / f"{city}_a{A}.json"
            st = json.loads(st_path.read_text()) if st_path.is_file() else {"city": city, "array": A, "state": "waiting"}
            if st["state"] in ("waiting", "needs_reading"):
                old_state, old_reason = st["state"], st.get("reason")
                try:
                    if a.root:
                        rf = Path(a.root) / city / "READY.json"
                        if rf.is_file():
                            passed = rr.check_passed_arrays(rf, city)
                            if A not in passed:
                                st.update(state="check_failed", ready=str(rf), passed=sorted(passed), utc=now())
                            else:
                                ch, sums = locate(Path(a.root) / city)
                                st.update(state="eligible", ready=str(rf), channel=str(ch), sums=str(sums), eligible_utc=now())
                    else:
                        idx_url = f"{a.stage_url}/{city}/index.json"
                        try:
                            idx = json.loads(urllib.request.urlopen(idx_url, timeout=30).read())
                        except Exception:
                            idx = None
                        if idx:
                            dd = Path(a.data_dir) / city; dd.mkdir(parents=True, exist_ok=True)
                            fetch(f"{a.stage_url}/{city}/READY.json", dd / "READY.json")
                            if sha(dd / "READY.json") != idx["ready_sha256"]:
                                raise ValueError("READY.json transfer hash")
                            passed = rr.check_passed_arrays(dd / "READY.json", city)
                            if A not in passed:
                                st.update(state="check_failed", ready=str(dd / "READY.json"), passed=sorted(passed), utc=now())
                            else:
                                fetch(f"{a.stage_url}/{city}/sums_one.txt", dd / "sums_one.txt")
                                fetch(f"{a.stage_url}/{city}/channel_realizations.h5", dd / "channel_realizations.h5")
                                ok = subprocess.run(["sha256sum", "-c", "--quiet", "sums_one.txt"], cwd=dd).returncode == 0
                                if not ok:
                                    (dd / "channel_realizations.h5").unlink(missing_ok=True)
                                    raise ValueError("channel file hash mismatch after transfer")
                                st.update(state="eligible", ready=str(dd / "READY.json"), channel=str(dd / "channel_realizations.h5"),
                                          sums=str(dd / "sums_one.txt"), eligible_utc=now(), source=idx)
                except ValueError as e:
                    st.update(state="needs_reading", reason=str(e))
                if (st["state"], st.get("reason")) != (old_state, old_reason):
                    log(A, f"{city}: {st['state']} {st.get('reason', '')}")
                st_path.write_text(json.dumps(st, indent=1) + "\n")
            units[city] = st
        # --- completion / resume
        for city, st in units.items():
            if st["state"] == "running":
                out = Path(st["out"])
                if (out / "PASS_DONE").is_file():
                    st.update(state="done", done_utc=now()); log(A, f"{city}: done")
                elif (out / "PASS_FAILED").is_file():
                    st.update(state="failed", reason=(out / "PASS_FAILED").read_text().strip(), utc=now()); log(A, f"{city}: FAILED {st['reason']}")
                elif not tmux_alive(st["session"]):
                    st.setdefault("resumes", []).append(now()); tmux_start(st["session"], st["cmd"])
                    log(A, f"{city}: session gone without marker; resumed on CPU {st['cpu']} (declaration s.7)")
                (U / f"{city}_a{A}.json").write_text(json.dumps(st, indent=1) + "\n")
        # --- start new units
        busy_slots = {u["cpu"] for u in units.values() if u["state"] == "running"}
        pending = sorted([u for u in units.values() if u["state"] == "eligible"], key=lambda u: (u["eligible_utc"], u["city"]))
        yield_block = False
        if a.yield_to is not None:
            yield_block = any(json.loads(f.read_text()).get("state") == "eligible" for f in U.glob(f"*_a{a.yield_to}.json"))
        for cpu, sib in slots:
            if not pending or cpu in busy_slots or tmux_alive(f"cc{cpu}") or yield_block:
                continue
            if t > cutoff - a.min_run_min * 60:
                for u in pending:
                    u.update(state="not_started_cutoff", utc=now()); (U / f"{u['city']}_a{A}.json").write_text(json.dumps(u, indent=1) + "\n")
                    log(A, f"{u['city']}: not started (cutoff)")
                pending = []
                break
            b = busy([cpu, sib])
            if max(b.values()) >= 0.10:
                log(A, f"slot {cpu}/{sib} busy {b}; waiting"); continue
            u = pending.pop(0); city = u["city"]
            env = f"W={W} PY={PY} PYDEPS={PYDEPS}"
            if not smoke_done:
                with __import__("h5py").File(u["channel"], "r") as h5:
                    chk, _ = rr.trajectory_list(h5, city, A, "check")
                so = R / "smoke" / f"{city}_a{A}"
                cmd = (f"{env} bash {W}/scripts/cc_timed_pass_20261114.sh {city} check {A} {cpu} {u['channel']} {u['sums']} {u['ready']} "
                       f"{so} 7 --trajectories {chk[0]} --frames 0,8")
                log(A, f"smoke on {chk[0]} CPU {cpu}")
                rc = subprocess.run(["bash", "-c", cmd]).returncode
                if rc != 0 or not (so / "PASS_DONE").is_file():
                    log(A, f"SMOKE FAILED rc={rc}"); (R / f"QUEUE_FAILED_a{A}").write_text(f"smoke failed {now()}\n"); return 1
                (R / f"SMOKE_OK_a{A}").write_text(now() + "\n"); smoke_done = True
            out = R / "test" / city / f"a{A}"
            cmd = (f"{env} bash {W}/scripts/cc_timed_pass_20261114.sh {city} test {A} {cpu} {u['channel']} {u['sums']} {u['ready']} "
                   f"{out} {SEEDS_TEST} --freeze-token {token}")
            u.update(state="running", cpu=cpu, sibling=sib, session=f"cc{cpu}", out=str(out), cmd=cmd, started_utc=now(), idle_check=b)
            tmux_start(u["session"], cmd)
            (U / f"{city}_a{A}.json").write_text(json.dumps(u, indent=1) + "\n")
            log(A, f"{city}: TEST started on CPU {cpu} (sibling {sib} idle: {b})")
            busy_slots.add(cpu)
        states = [u["state"] for u in json_units(A)]
        final = {"done", "failed", "check_failed", "not_started_cutoff"}
        if all(s in final for s in states) or (time.time() > cutoff and "running" not in states):
            (R / f"QUEUE_DONE_a{A}").write_text(json.dumps({"utc": now(), "states": states}) + "\n"); log(A, f"QUEUE_DONE {states}")
            return 0
        time.sleep(60)


def json_units(A):
    return [json.loads((U / f"{c}_a{A}.json").read_text()) if (U / f"{c}_a{A}.json").is_file() else {"state": "waiting"} for c in rr.CITIES]


if __name__ == "__main__":
    sys.exit(main())
