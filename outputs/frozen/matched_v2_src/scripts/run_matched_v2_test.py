"""Single held-out matched_v2 test run (Paper 1: b35 vs exact pair search).

Runs only after configs/experiments/matched_v2.json is frozen. Refuses to start unless every frozen source hash,
the frozen protocol hash, the 161-segment test data manifest and the paired 81-segment test frames all verify.
Timed search uses the 161-segment network. Each returned action is rescored, outside the timed section, on the
81-segment network of the same frame (mesh rule). Writes one JSONL of rows and a JSON run record; refuses to
overwrite either, so the test cannot be run twice into the same place.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atomwise_ris.optimization.pair_plus import ALL_METHODS, search  # noqa: E402
from atomwise_ris.optimization.coupled_search import search as coupled_search  # noqa: E402
from atomwise_ris.optimization.search import ME_GA_METHODS, Memory, load_search_config  # noqa: E402
from atomwise_ris.physics.network import CoupledNetwork  # noqa: E402

PROTOCOL = ROOT / "configs/experiments/matched_v2.json"


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify_frozen(protocol):
    if protocol.get("status") != "frozen":
        raise SystemExit("matched_v2.json is not frozen")
    bad = {p: h for p, h in protocol["frozen_source_sha256"].items() if sha256_file(ROOT / p) != h}
    if bad:
        raise SystemExit(f"frozen source hash mismatch: {sorted(bad)}")


def load_frames(protocol):
    t = protocol["data"]["held_out_test"]
    fine, coarse = ROOT / t["fine_path"], ROOT / t["coarse_path"]
    if sha256_file(coarse / "scenario.json") != t["coarse_scenario_sha256"]:
        raise SystemExit("81-segment test scenario hash differs from the frozen protocol")
    scenario = json.loads((fine / "scenario.json").read_text())
    status = json.loads((fine / "generation_status.json").read_text())
    if Path(scenario.get("fine_mesh_of", "")).name != coarse.name or int(scenario.get("segments", -1)) != 161:
        raise SystemExit("fine test scenario is not the 161-segment extraction of the frozen test set")
    if scenario.get("source_scenario_sha256") != t["coarse_scenario_sha256"]:
        raise SystemExit("fine test scenario is bound to a different source scenario")
    if status.get("status") != "complete":
        raise SystemExit(f"fine test generation is not complete: {status.get('status')}")
    hashes = status["frame_npz_sha256"]
    frames = []
    for row in scenario["rows"]:
        if row["split"] != "test":
            raise SystemExit("non-test row in the test scenario")
        i = int(row["index"])
        fp, cp = fine / f"frame_{i:04d}.npz", coarse / f"frame_{i:04d}.npz"
        if sha256_file(fp) != hashes[str(i)]:
            raise SystemExit(f"fine frame {i} hash mismatch")
        cmeta = json.loads(cp.with_suffix(".json").read_text())
        if cmeta.get("sha256") != sha256_file(cp) or int(cmeta.get("segments_per_wire", -1)) != 81:
            raise SystemExit(f"coarse frame {i} hash or mesh mismatch")
        frames.append((i, int(row["trajectory"]), int(row["step"]), fp, cp))
    if len(frames) != t["frames"]:
        raise SystemExit(f"expected {t['frames']} frames, found {len(frames)}")
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--cpu", type=int, required=True)
    ap.add_argument("--smoke-dev", action="store_true",
                    help="bounded dry run on 2 development frames only; checks the code path, never reads test data")
    a = ap.parse_args()
    raw = PROTOCOL.read_bytes()
    protocol = json.loads(raw)
    run = protocol["run"]
    out = Path(a.output)
    if out.exists() or out.with_suffix(".json").exists():
        raise FileExistsError(f"refusing to overwrite {out}")
    os.sched_setaffinity(0, {a.cpu})
    try:
        import threadpoolctl
        threadpoolctl.threadpool_limits(limits=1)
    except ImportError:
        pass
    gate = json.loads((ROOT / run["physics_gate"]).read_text())
    loads = np.asarray(gate["loads_real_ohm"], float) + 1j * np.asarray(gate["loads_imag_ohm"], float)
    cfg = load_search_config("medium", ROOT / run["search_config_protocol"])
    if a.smoke_dev:
        dev = ROOT / "data/processed/coupled_wire_dev_fine161"
        frames = []
        for i in (0, 1):
            m = json.loads((dev / f"frame_{i:04d}.json").read_text())
            frames.append((i, int(m["trajectory"]), int(m["step"]), dev / f"frame_{i:04d}.npz",
                           ROOT / f"data/processed/coupled_wire_dev_v1/frame_{i:04d}.npz"))
        split = "development_smoke"
    else:
        verify_frozen(protocol)
        frames = load_frames(protocol)
        split = "test"
    methods, budgets, seeds = run["methods"], run["budgets_ms"], run["seeds"]
    record = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "hostname": platform.node(),
        "python": sys.version, "numpy": np.__version__, "cpu_affinity": sorted(os.sched_getaffinity(0)),
        "split": split, "protocol_sha256": hashlib.sha256(raw).hexdigest(), "methods": methods,
        "budgets_ms": budgets, "seeds": seeds, "frames": len(frames),
        "data_manifest_sha256": hashlib.sha256("\n".join(
            f"{i}:{sha256_file(fp)}:{sha256_file(cp)}" for i, _, _, fp, cp in frames).encode()).hexdigest(),
        "timing_includes": ["CoupledNetwork construction", "search", "returned-action full verification"],
        "timing_excludes": ["data loading", "warm-up pass", "81-segment rescoring", "disk writes"],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")

    memories, last = {}, {}
    for m in methods:
        for s in seeds:
            for b in budgets:
                memories[m, s, b] = Memory() if m in ME_GA_METHODS else []
                last[m, s, b] = None
    with np.load(frames[0][3], allow_pickle=False) as d:
        warm_z = np.asarray(d["z"], np.complex128)
    for m in methods:  # discarded warm-up pass, declared in timing_excludes
        ev = CoupledNetwork(warm_z, loads)
        dl = time.perf_counter_ns() + 20_000_000
        if m in ALL_METHODS:
            search(ev, m, dl, 1, memory=None, trace=[])
        else:
            coupled_search(ev, m, dl, 1, memory=Memory() if m in ME_GA_METHODS else [], config=cfg, trace=[])
    with out.open("x") as f:
        for index, trajectory, step, fp, cp in frames:
            with np.load(fp, allow_pickle=False) as d:
                z = np.asarray(d["z"], np.complex128)
            with np.load(cp, allow_pickle=False) as d:
                coarse = CoupledNetwork(np.asarray(d["z"], np.complex128), loads)
            for b in budgets:
                for s in seeds:
                    for m in methods:
                        key = (m, s, b)
                        memory = memories[key]
                        start = time.perf_counter_ns()
                        if hasattr(memory, "enter"):
                            memory.enter(trajectory)
                        elif last[key] != trajectory:
                            memory.clear()
                        last[key] = trajectory
                        deadline = start + int(b * 1e6)
                        ev = CoupledNetwork(z, loads)
                        trace = []
                        if m in ALL_METHODS:
                            bits, value, evals, bd = search(ev, m, deadline, s * 1000003 + index, memory=None, trace=trace)
                        else:
                            bits, value, evals, bd = coupled_search(ev, m, deadline, s * 1000003 + index,
                                                                    memory=memory, config=cfg, trace=trace)
                        full = float(ev.score(ev.channel(bits) @ ev.w))
                        elapsed = (time.perf_counter_ns() - start) / 1e6
                        if abs(full - value) > 1e-7:
                            raise AssertionError("returned action failed direct full-network rescore")
                        rate81 = float(coarse.score(coarse.channel(bits) @ coarse.w))
                        f.write(json.dumps({
                            "split": split, "method": m, "seed": s, "budget_ms": b, "index": index,
                            "trajectory": trajectory, "step": step, "rate": full, "rate_81": rate81,
                            "elapsed_ms": elapsed,
                            "deadline_missed": elapsed > b or bool(bd.get("deadline_missed", False)),
                            "evaluations": evals, "on_bits": int(np.sum(bits)),
                            "bits": np.asarray(bits, int).tolist(), "breakdown": bd,
                        }, separators=(",", ":")) + "\n")
                        f.flush()
    print(json.dumps({"status": "complete", "rows": len(frames) * len(budgets) * len(seeds) * len(methods)}))


if __name__ == "__main__":
    main()
