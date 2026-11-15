#!/usr/bin/env python3
"""Timed search runner for the cross-city held-out test (NEW, 2026-11-14; derived from
paper-b-neural-pair-search/scripts/run_bench_search_ris_relevant_v3.py, timed section unchanged).

Declaration: paper-a-ris-physics/docs/crosscity-search-declaration-20261114.md. Changes from the v3 runner: city ids and
split by index (check 0-11, test 12-47) via search_adapter_crosscity; the test list is enumerated from the channel file;
readiness per array from READY.json; channel file and checksum file given explicitly; one-shot guard per city x array;
rows carry the city as `map`.
"""
import os
import sys

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import argparse
import hashlib
import json
from pathlib import Path
import platform
import time
from typing import Dict, Set, Tuple

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "scripts"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from atomwise_ris.bench.search_adapter import BenchSearchNetwork, _as_complex, run_search  # noqa: E402
from atomwise_ris.bench import search_adapter_crosscity as rr  # noqa: E402
from atomwise_ris.bench import search_adapter_nsga2  # noqa: E402
from atomwise_ris.optimization import me_ga, pair_select  # noqa: E402
from atomwise_ris.optimization.search import Memory, load_search_config, PROTOCOL_PATH  # noqa: E402

DECLARED_SHA256 = {  # full hashes; equal to the files of the natural search run (prefixes as declared)
    "src/atomwise_ris/optimization/coupled_search.py": "0b4d863c7a34009e91ed3769156b96040c5e9b042ba926c583c85aaf61874423",
    "src/atomwise_ris/optimization/search.py": "7bc38bb183a50b267e118cab57bcc41f46a26b7bb7ca39296f1d34d55a5ad633",
    "src/atomwise_ris/optimization/me_ga.py": "7858402e81f9c89b78aaabd4ce94c7d8e830282e1bd49e0c5af947d59094ed48",
    "src/atomwise_ris/optimization/pair_plus.py": "a8de796614a379874001bbcbc9b3c9d491fd4cf8a0e4ebdc2c76e79250a4d2d6",
    "src/atomwise_ris/optimization/pair_select.py": "a957d94332ad61722709d9ef4fee495b214a89b37dea987f80f4a764d2b7db37",
    "src/atomwise_ris/hybrid/operator.py": "d0e3485065a1dfa27bcd89172a60f349b282eefe036f3b7cc72051afbf4c7e13",
    "src/atomwise_ris/bench/search_adapter.py": "af5f51217801527ace1d319bfaf08969860938e38829c33bd9f443aee1900886",
    "src/atomwise_ris/optimization/nsga2.py": "fec0a3d7321c2f3287ffc562271b0f448cfeed2db3310fe86480895be9337260",
    "src/atomwise_ris/bench/search_adapter_nsga2.py": "3d6c16b1cda33922c9140431847e4c657152834533ecd733869a2231428b62d8",
}
MATCHED_V1_SHA = "77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sanitize(v):
    if isinstance(v, dict):
        return {k: sanitize(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [sanitize(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def resolve_heads(lock_path: Path, arrays, head_root: Path = None):
    """Return ({array: (path, sha)}, report) from the checkpoint lock (declaration section 8)."""
    head_root = Path(head_root) if head_root else lock_path.parent
    report = {"lock": str(lock_path), "head_root": str(head_root), "present": lock_path.is_file()}
    heads = {}
    if not lock_path.is_file():
        return heads, report
    report["lock_sha256"] = sha256_file(lock_path)
    lock = json.loads(lock_path.read_text())
    chosen = lock.get("chosen", lock)
    report["per_array"] = {}
    for a in arrays:
        ent = chosen.get(str(a)) if isinstance(chosen, dict) else None
        if not isinstance(ent, dict) or not ent.get("sha256"):
            report["per_array"][a] = "no entry with sha256 in lock"
            continue
        want = str(ent["sha256"]).lower()
        cands = []
        for k in ("path", "file", "npz"):
            if ent.get(k):
                p = Path(ent[k])
                if not p.is_absolute():
                    p = head_root / p
                elif not p.is_file() and "heads" in p.parts:  # lock written on another machine: same file under head_root
                    i = len(p.parts) - 1 - p.parts[::-1].index("heads")
                    p = head_root.joinpath(*p.parts[i + 1:])
                cands.append(p)
        if not cands:
            cands = [p for p in head_root.rglob("*.npz") if sha256_file(p) == want]
            if len(cands) != 1:
                report["per_array"][a] = f"{len(cands)} npz files under heads/ match the lock sha256"
                continue
        p = cands[0]
        if not p.is_file() or sha256_file(p) != want:
            report["per_array"][a] = f"file {p} missing or sha256 mismatch"
            continue
        try:
            pair_select.NumpyFactoredPairHead.from_npz(p)
        except Exception as e:  # noqa: BLE001
            report["per_array"][a] = f"from_npz failed: {e}"
            continue
        heads[a] = (p, want)
        report["per_array"][a] = {"path": str(p), "sha256": want, "config": ent.get("config")}
    return heads, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True, choices=list(rr.CITIES))
    ap.add_argument("--channel-file", required=True, help="channel_realizations.h5 of the city")
    ap.add_argument("--sums-file", required=True, help="sha256 list that covers the channel file (sha256sum format)")
    ap.add_argument("--split", required=True, choices=["check", "test"])
    ap.add_argument("--nsga2-ready", default=None, help="NSGA2_READY.json; required when 'nsga2' is a method")
    ap.add_argument("--arrays", required=True)
    ap.add_argument("--methods", required=True)
    ap.add_argument("--budgets-ms", required=True)
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--cpu", type=int, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--freeze-token", default=None)
    ap.add_argument("--ready-file", default=None, help="<workspace>/<city>/READY.json")
    ap.add_argument("--head-lock", default=None, help="not used in the cross-city test")
    ap.add_argument("--head-root", default=None, help="not used in the cross-city test")
    ap.add_argument("--trajectories", default=None, help="check smoke only")
    ap.add_argument("--frames", default=None, help="check smoke only")
    args = ap.parse_args()

    if args.head_lock:
        raise ValueError("no heads in the cross-city test (declaration s.3)")
    arrays_req = [int(x) for x in args.arrays.split(",") if x.strip()]
    if len(arrays_req) != 1:
        raise PermissionError("one array size per process (declaration s.6)")
    if args.split == "test" and (args.trajectories or args.frames):
        raise PermissionError("the test pass runs on the whole split")
    if args.split == "test" and not rr.test_unlocked(ROOT, args.freeze_token, args.ready_file, args.city, arrays_req[0]):
        raise PermissionError(f"{args.city} test split sealed for array {arrays_req[0]}: token or check PASS missing")

    os.sched_setaffinity(0, {args.cpu})
    try:
        import threadpoolctl
        threadpoolctl.threadpool_limits(limits=1)
    except ImportError:
        pass

    channel_file = Path(args.channel_file).resolve()
    sums_file = Path(args.sums_file).resolve()
    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.split == "test":  # one-shot guard (declaration section 9.6)
        guard = ROOT / "runs" / f"TEST_ONCE_{args.city}_a{arrays_req[0]}.json"
        guard.parent.mkdir(parents=True, exist_ok=True)
        if guard.is_file():
            g = json.loads(guard.read_text())
            if g.get("output_dir") != str(out_dir):
                raise PermissionError(f"test pass already started elsewhere: {g}")
        else:
            guard.write_text(json.dumps({"output_dir": str(out_dir),
                                         "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")

    running, done, failed = out_dir / "RUNNING", out_dir / "DONE", out_dir / "FAILED"
    running.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
    if failed.is_file():
        failed.unlink()
    try:
        # hashes: package against output_sha256sums, sources against the declaration
        sums = {}
        for line in sums_file.read_text().splitlines():
            if not line.strip():
                continue
            h, f = line.split(None, 1)
            sums[(sums_file.parent / f.strip().lstrip("*")).resolve()] = h
        ch_sha = sha256_file(channel_file)
        sp_sha = sha256_file(sums_file)
        if sums.get(channel_file) != ch_sha:
            raise RuntimeError("channel file hash missing from or different in the sums file")
        src_hashes = {}
        for rel, want in DECLARED_SHA256.items():
            h = sha256_file(ROOT / rel)
            if h != want:
                raise RuntimeError(f"source hash of {rel} differs from the declaration: {h}")
            src_hashes[rel] = h
        for rel in ("src/atomwise_ris/bench/search_adapter_crosscity.py", "scripts/run_bench_search_crosscity.py"):
            src_hashes[rel] = sha256_file(ROOT / rel)
        if sha256_file(PROTOCOL_PATH) != MATCHED_V1_SHA:
            raise RuntimeError("matched_v1.json hash differs")
        cfg = load_search_config("medium", PROTOCOL_PATH)
        decl_sha = sha256_file(ROOT / rr.DECLARATION)
        nsga2_ready = None
        if "nsga2" in [m.strip() for m in args.methods.split(",")]:
            if not args.nsga2_ready:
                raise ValueError("--nsga2-ready is required for method nsga2")
            nsga2_ready = json.loads(Path(args.nsga2_ready).read_text())
            if nsga2_ready.get("status") != "ready" or nsga2_ready.get("sha256") != src_hashes["src/atomwise_ris/optimization/nsga2.py"]:
                raise RuntimeError("nsga2 module hash differs from NSGA2_READY.json")

        arrays = [int(x) for x in args.arrays.split(",") if x.strip()]
        methods = [m.strip() for m in args.methods.split(",") if m.strip()]
        budgets_ms = [float(b) for b in args.budgets_ms.split(",") if b.strip()]
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
        if "head" in methods:
            raise ValueError("'head' is added from --head-lock, not listed")

        heads, head_report = ({}, {"lock": None})
        if args.head_lock:
            heads, head_report = resolve_heads(Path(args.head_lock), arrays, args.head_root)
        head_models = {a: pair_select.NumpyFactoredPairHead.from_npz(p) for a, (p, _) in heads.items()}

        with h5py.File(channel_file, "r") as _h5:
            traj_all, missing_idx = rr.trajectory_list(_h5, args.city, arrays_req[0], args.split, ROOT,
                                                       args.freeze_token, args.ready_file)
        if not traj_all:
            raise RuntimeError(f"no {args.split} trajectories for {args.city} at array {arrays_req[0]}")
        canon = {t: i for i, t in enumerate(traj_all)}
        selected = list(traj_all)
        if args.trajectories:
            keep = {t.strip() for t in args.trajectories.split(",")}
            selected = [t for t in selected if t in keep]
        target_frames = [int(f) for f in args.frames.split(",")] if args.frames else None

        normalized = {"channel_file": str(channel_file), "sums_file": str(sums_file), "city": args.city, "split": args.split, "nsga2_ready": args.nsga2_ready, "arrays": arrays, "methods": methods,
                      "budgets_ms": budgets_ms, "seeds": seeds, "cpu": args.cpu, "trajectories": args.trajectories,
                      "frames": args.frames, "head_lock": args.head_lock, "head_root": args.head_root}
        record = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "hostname": platform.node(),
                  "python": sys.version, "numpy": np.__version__, "cpu_affinity": sorted(os.sched_getaffinity(0)),
                  "args": normalized, "channel_file_sha256": ch_sha, "split_file_sha256": sp_sha, "sums_file_sha256": sp_sha,
                  "trajectories_used": len(traj_all), "missing_indices": missing_idx,
                  "declaration_sha256_now": decl_sha, "freeze_token": rr.freeze_token(ROOT),
                  "nsga2_ready": nsga2_ready, "check_passed_arrays": sorted(rr.check_passed_arrays(args.ready_file, args.city)) if args.ready_file else None,
                  "cpu_model": next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), None),
                  "ready_file": args.ready_file, "ready_file_sha256": sha256_file(Path(args.ready_file)) if args.ready_file else None,
                  "search_config_protocol_sha256": MATCHED_V1_SHA, "source_files_sha256": src_hashes,
                  "heads": {str(a): {"path": str(p), "sha256": s} for a, (p, s) in heads.items()},
                  "head_report": sanitize(head_report), "resumes": []}
        rec_path = out_dir / "run_record.json"
        if rec_path.is_file():
            old = json.loads(rec_path.read_text())
            for k in ("args", "channel_file_sha256", "split_file_sha256", "source_files_sha256", "heads", "freeze_token"):
                if old.get(k) != record.get(k):
                    raise RuntimeError(f"cannot resume: {k} differs")
            old.setdefault("resumes", []).append({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            rec_path.write_text(json.dumps(old, indent=2) + "\n")
        else:
            rec_path.write_text(json.dumps(record, indent=2) + "\n")

        completed: Dict[int, Set[Tuple[str, int]]] = {}
        for a in arrays:
            p = out_dir / f"rows_{a}.jsonl"
            comp = set()
            if p.is_file():
                lines = p.read_text().splitlines(keepends=True)
                last = -1
                for i, line in enumerate(lines):
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if d.get("frame_done"):
                        last = i
                        comp.add((d["trajectory"], int(d["frame"])))
                p.write_text("".join(lines[:last + 1]) if last >= 0 else "")
            completed[a] = comp

        flags_path = out_dir / "flags.json"
        flags = json.loads(flags_path.read_text()) if flags_path.is_file() else {}
        frames_done = sum(len(c) for c in completed.values())

        with h5py.File(channel_file, "r") as h5:
            for a in arrays:
                gw = 8 if a == 64 else 16
                ms = methods + (["head"] if a in head_models else [])
                rows_path = out_dir / f"rows_{a}.jsonl"
                # warm-up (20 ms) per method on the first frame of the first trajectory, discarded
                if selected:
                    _, g0 = rr.frame_group(h5, a, selected[0])
                    wf = g0[rr.sorted_frame_keys(g0)[0]]
                    for m in ms:
                        w_ev = rr.network_from_group(wf, gw)
                        dl = time.perf_counter_ns() + 20_000_000
                        try:
                            if m == "me_ga":
                                me_ga.search_coupled(w_ev, "me_ga", dl, 1, memory=Memory(), trace=[])
                            elif m == "nsga2":
                                search_adapter_nsga2.run_search(w_ev, "nsga2", dl, 1)
                            elif m == "head":
                                run_search(w_ev, "neural_head", dl, 1, head=head_models[a])
                            elif m in ("greedy", "pair"):
                                run_search(w_ev, m, dl, 1, config=cfg)
                            else:
                                run_search(w_ev, m, dl, 1)
                        except Exception:
                            pass
                for tid in selected:
                    gpath, grp = rr.frame_group(h5, a, tid)
                    fkeys = rr.sorted_frame_keys(grp)
                    if len(fkeys) != 16:
                        raise RuntimeError(f"{gpath}: {len(fkeys)} frames")
                    memories = {(s, b): Memory() for s in seeds for b in budgets_ms}
                    for mem in memories.values():
                        mem.enter(tid)
                    for fpos, fk in enumerate(fkeys):
                        if target_frames is not None and fpos not in target_frames:
                            continue
                        fg = grp[fk]
                        z = _as_complex(fg["Z_effective"]); ci = _as_complex(fg["C_in"]); co = _as_complex(fg["C_out"])
                        hd = _as_complex(fg["H_direct"]); loads = _as_complex(fg["loads"])
                        if loads.shape == (z.shape[0], 2):
                            loads = loads[0]
                        w = _as_complex(fg["precoder"]); noise = float(fg.attrs["noise"])
                        # declared exclusion (untimed): pathless served user -> frame flagged, skipped
                        fkey = f"{a}/{tid}/{fpos}"
                        if fkey not in flags:
                            pl = rr.pathless_users(BenchSearchNetwork(z, co, ci, hd, loads, w=w, noise=noise, grid_width=gw))
                            flags[fkey] = {"frame_key": fk, "pathless_users": pl.astype(int).tolist(), "flagged": bool(pl.any())}
                            flags_path.write_text(json.dumps(flags, indent=1) + "\n")
                        if flags[fkey]["flagged"]:
                            continue
                        if (tid, fpos) in completed[a]:
                            continue
                        frame_row_index = canon[tid] * 16 + fpos
                        k_users = int(co.shape[0])
                        frame_rows = []
                        for budget_ms in budgets_ms:
                            for seed in seeds:
                                for method in ms:
                                    search_seed = int(seed) * 1000003 + int(frame_row_index)
                                    t_start = time.perf_counter_ns()
                                    deadline_ns = t_start + int(budget_ms * 1_000_000)
                                    ev = BenchSearchNetwork(z, co, ci, hd, loads, w=w, noise=noise, grid_width=gw)
                                    if method == "me_ga":
                                        bits, reported_val, evals, bd = me_ga.search_coupled(
                                            ev, "me_ga", deadline_ns, search_seed, memory=memories[(seed, budget_ms)], trace=[])
                                    elif method == "nsga2":
                                        bits, reported_val, evals, bd = search_adapter_nsga2.run_search(
                                            ev, "nsga2", deadline_ns, search_seed)
                                    elif method == "head":
                                        bits, reported_val, evals, bd = run_search(
                                            ev, "neural_head", deadline_ns, search_seed, head=head_models[a])
                                    elif method in ("greedy", "pair"):
                                        bits, reported_val, evals, bd = run_search(ev, method, deadline_ns, search_seed, config=cfg)
                                    else:
                                        bits, reported_val, evals, bd = run_search(ev, method, deadline_ns, search_seed)
                                    t_search_end = time.perf_counter_ns()
                                    state = ev.state(bits)
                                    rescored = float(ev.score(state.field))
                                    t_end = time.perf_counter_ns()
                                    elapsed_ms = (t_end - t_start) / 1e6
                                    search_elapsed_ms = (t_search_end - t_start) / 1e6
                                    if abs(rescored - reported_val) > 1e-7:
                                        raise AssertionError(f"rescore error {method} {tid} {fpos}: {reported_val} vs {rescored}")
                                    frame_rows.append({
                                        "split": args.split, "scope": "crosscity", "map": args.city, "array": a, "trajectory": tid,
                                        "frame": fpos, "frame_key": fk, "frame_row_index": frame_row_index,
                                        "users": k_users, "k": k_users, "method": method, "seed": int(seed),
                                        "budget_ms": float(budget_ms), "rate": rescored, "elapsed_ms": elapsed_ms,
                                        "deadline_missed": bool(elapsed_ms > budget_ms or bd.get("deadline_missed", False)),
                                        "search_elapsed_ms": search_elapsed_ms,
                                        "deadline_missed_search_clock": bool(search_elapsed_ms > budget_ms or bd.get("deadline_missed", False)),
                                        "evaluations": int(evals), "on_bits": int(np.sum(bits)),
                                        "bits": np.asarray(bits, dtype=int).tolist(), "breakdown": sanitize(bd),
                                    })
                        with open(rows_path, "a", encoding="utf-8") as wf:
                            for r in frame_rows:
                                wf.write(json.dumps(r, separators=(",", ":")) + "\n")
                            wf.write(json.dumps({"frame_done": True, "array": a, "trajectory": tid, "frame": fpos,
                                                 "frame_row_index": frame_row_index}, separators=(",", ":")) + "\n")
                        completed[a].add((tid, fpos))
                        frames_done += 1
                        (out_dir / "heartbeat.json").write_text(json.dumps({
                            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "array": a,
                            "frames_done": frames_done}) + "\n")
        done.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
        running.unlink(missing_ok=True)
        print(json.dumps({"status": "complete", "frames_done": frames_done,
                          "flagged": sum(v["flagged"] for v in flags.values())}))
    except Exception as e:
        failed.write_text(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}: {e}\n")
        running.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
