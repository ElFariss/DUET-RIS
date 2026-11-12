#!/usr/bin/env python3
"""Descriptive cProfile instrumentation for the matched-v1 coupled pair search.

This tool is development-only. cProfile changes timing and may change the
deadline-limited search path; its rates and runtime must never be used for
method selection or reported as official benchmark timing.
"""
from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import os
import platform
import pstats
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from time import perf_counter_ns

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from atomwise_ris.optimization.coupled_search import search as coupled_search
from atomwise_ris.optimization.search import load_search_config
from atomwise_ris.physics.network import CoupledNetwork

ALLOWED_DATASETS = {"coupled_wire_dev_v1", "coupled_wire_dev_fine161"}
MAX_PROFILE_BUDGET_MS = 100.0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_ints(text: str) -> list[int]:
    values = [int(x.strip()) for x in text.split(",") if x.strip()]
    if not values or len(values) != len(set(values)) or min(values) < 0:
        raise ValueError("--indices must be a nonempty comma-separated list of distinct nonnegative indices")
    return values


def _verify_dev_directory(data_dir: Path) -> tuple[dict, dict[int, tuple[int, int, Path, Path]], str | None]:
    """Accept only registered DEV frame directories and verify frame provenance."""
    if data_dir.name not in ALLOWED_DATASETS or "test" in data_dir.parts:
        raise ValueError(f"data directory must be one of {sorted(ALLOWED_DATASETS)} and outside any test path")
    scenario_path = data_dir / "scenario.json"
    if not scenario_path.is_file():
        raise FileNotFoundError(f"missing development scenario manifest: {scenario_path}")
    scenario_bytes = scenario_path.read_bytes()
    scenario = json.loads(scenario_bytes)
    if scenario.get("development_set") is not True or scenario.get("split_label") != "dev" or scenario.get("untouched_test") is not False:
        raise ValueError("scenario manifest must explicitly mark development_set=true, split_label=dev, untouched_test=false")
    expected_segments = 81 if data_dir.name == "coupled_wire_dev_v1" else 161
    if int(scenario.get("segments", -1)) != expected_segments:
        raise ValueError(f"{data_dir.name} requires {expected_segments} segments")

    canonical = ROOT / "data/processed/coupled_wire_dev_v1"
    expected_rows: dict[int, dict] = {}
    readiness_sha256 = None
    if data_dir.name == "coupled_wire_dev_v1":
        if data_dir.resolve() != canonical.resolve() or scenario.get("set_name") != "coupled_wire_dev_v1":
            raise ValueError("coarse profiling is limited to the registered canonical coupled_wire_dev_v1 directory")
        rows = scenario.get("rows", [])
        if not rows or any(row.get("split") != "dev" for row in rows):
            raise ValueError("canonical coarse scenario must contain only DEV rows")
        expected_rows = {int(row["index"]): row for row in rows}
        if len(expected_rows) != len(rows):
            raise ValueError("coarse scenario contains duplicate development indices")
        source_indices = {int(row["index"]) for row in rows}
        frame_hashes = None
    else:
        canonical_fine = ROOT / "data/processed/coupled_wire_dev_fine161"
        if data_dir.resolve() != canonical_fine.resolve():
            raise ValueError("fine profiling is limited to canonical coupled_wire_dev_fine161 directory")
        source_scenario = canonical / "scenario.json"
        readiness_path = data_dir / "generation_status.json"
        if not source_scenario.is_file() or not readiness_path.is_file():
            raise ValueError("fine 161-segment profiling requires source and generation readiness manifests")
        if (scenario.get("fine_mesh_split") != "dev"
                or Path(str(scenario.get("fine_mesh_of", ""))).name != "coupled_wire_dev_v1"
                or scenario.get("source_scenario_sha256") != sha256_file(source_scenario)):
            raise ValueError("fine mesh scenario is not hash-bound to canonical coarse DEV scenario")
        source = json.loads(source_scenario.read_text())
        source_indices = {int(row["index"]) for row in source.get("rows", []) if row.get("split") == "dev"}
        fine_rows = scenario.get("rows", [])
        expected_rows = {int(row["index"]): row for row in fine_rows}
        fine_indices = {int(row["index"]) for row in fine_rows if row.get("split") == "dev"}
        ready = json.loads(readiness_path.read_text())
        readiness_sha256 = sha256_file(readiness_path)
        expected = sorted(source_indices)
        if (len(fine_rows) != len(fine_indices) or any(row.get("split") != "dev" for row in fine_rows)
                or fine_indices != source_indices or ready.get("status") != "complete"
                or ready.get("ready_for_development_evaluation") is not True
                or ready.get("verified_frame_indices") != expected or ready.get("expected_indices") != expected
                or ready.get("missing_frame_indices") != [] or ready.get("invalid_frames") != []):
            raise ValueError("fine readiness manifest must verify exactly all canonical development indices")
        frame_hashes = ready.get("frame_npz_sha256", {})

    metas: dict[int, tuple[int, int, Path, Path]] = {}
    for meta_path in sorted(data_dir.glob("frame_*.json")):
        meta = json.loads(meta_path.read_text())
        if meta.get("split") != "dev":
            continue
        idx = int(meta["index"])
        npz_path = meta_path.with_suffix(".npz")
        if (not npz_path.is_file() or sha256_file(npz_path) != meta.get("sha256")
                or int(meta.get("segments_per_wire", -1)) != expected_segments):
            raise ValueError(f"development frame hash or mesh mismatch: {meta_path.name}")
        if frame_hashes is not None and frame_hashes.get(str(idx)) != sha256_file(npz_path):
            raise ValueError(f"fine readiness hash mismatch for {meta_path.name}")
        if idx in metas:
            raise ValueError(f"duplicate frame index {idx}")
        expected_row = expected_rows.get(idx)
        if (expected_row is None or expected_row.get("split") != "dev"
                or int(expected_row.get("trajectory", -1)) != int(meta["trajectory"])
                or int(expected_row.get("step", -1)) != int(meta["step"])):
            raise ValueError(f"frame identity differs from scenario row for index {idx}")
        metas[idx] = (int(meta["trajectory"]), int(meta["step"]), npz_path, meta_path)
    if set(metas) != source_indices:
        raise ValueError("verified frame sidecars must exactly match the registered DEV indices")
    return scenario, metas, readiness_sha256


class TimedNetwork:
    """Duck-typed observer; delegates to CoupledNetwork without changing it."""
    def __init__(self, network):
        self._network = network
        self.n = network.n
        self.pairs = network.pairs
        self.calls = Counter()
        self.ns = Counter()
        self.candidates = Counter()

    def __getattr__(self, name):
        return getattr(self._network, name)

    def state(self, bits):
        t = perf_counter_ns()
        try:
            return self._network.state(bits)
        finally:
            self.calls["state"] += 1
            self.ns["state_inclusive"] += perf_counter_ns() - t

    def score(self, fields):
        t = perf_counter_ns()
        try:
            return self._network.score(fields)
        finally:
            arr = np.asarray(fields)
            count = int(arr.shape[0]) if arr.ndim >= 3 else 1
            self.calls["score"] += 1
            self.candidates["objective_candidates_scored"] += count
            self.ns["score_inclusive"] += perf_counter_ns() - t

    def moves(self, state, pairs=False, subset=None):
        t = perf_counter_ns()
        try:
            return self._network.moves(state, pairs=pairs, subset=subset)
        finally:
            name = "pair_scan" if pairs else "single_scan"
            self.calls[name] += 1
            self.candidates[name] += (len(self.pairs) if pairs else self.n) if subset is None else (
                len(np.asarray(subset)) if not pairs else len(np.asarray(subset)) * (len(np.asarray(subset)) - 1) // 2)
            self.ns[name + "_inclusive"] += perf_counter_ns() - t

    def flip(self, state, indices):
        t = perf_counter_ns()
        try:
            return self._network.flip(state, indices)
        finally:
            self.calls["flip"] += 1
            self.ns["flip_inclusive"] += perf_counter_ns() - t

    def summary(self) -> dict:
        # Matched pair's first state is the all-OFF initial reference; subsequent
        # full state builds occur only for random restarts (memory is disabled).
        return {
            "calls": dict(self.calls),
            "candidate_counts": dict(self.candidates),
            "inclusive_time_ms": {k: v / 1e6 for k, v in self.ns.items()},
            "initial_state_calls": min(1, self.calls["state"]),
            "restart_state_calls": max(0, self.calls["state"] - 1),
            "inverse_calls_inferred_from_unchanged_network_contract": {
                "constructor_external_block": 1,
                "state_builds_including_initial": self.calls["state"],
                "flip_updates_use_small_solve_not_inverse": self.calls["flip"],
            },
            "state_build_and_inverse_inclusive_ms": self.ns["state_inclusive"] / 1e6,
            "timing_note": "method timers are inclusive; moves includes its nested score call, so components are not additive",
        }


def _profile_once(z: np.ndarray, loads: np.ndarray, budget_ms: float, seed: int, config,
                  capture_profile: bool) -> tuple[dict, cProfile.Profile | None]:
    start = perf_counter_ns()
    deadline = start + int(budget_ms * 1e6)
    profiler = cProfile.Profile() if capture_profile else None
    if profiler:
        profiler.enable()
    init_start = perf_counter_ns()
    network = CoupledNetwork(z, loads)
    init_ns = perf_counter_ns() - init_start
    observer = TimedNetwork(network)
    search_start = perf_counter_ns()
    bits, rate, reported_evaluations, breakdown = coupled_search(
        observer, "pair", deadline, seed, memory=(), config=config, legacy=False)
    search_ns = perf_counter_ns() - search_start
    if profiler:
        profiler.disable()
    elapsed_ns = perf_counter_ns() - start
    return ({
        "elapsed_ms": elapsed_ns / 1e6,
        "network_initialization_ms": init_ns / 1e6,
        "search_ms": search_ns / 1e6,
        "best_rate": float(rate),
        "reported_search_evaluations": int(reported_evaluations),
        "profiled_component_calls": observer.summary(),
        "breakdown": breakdown,
        "bits_sha256": hashlib.sha256(np.asarray(bits, dtype=np.uint8).tobytes()).hexdigest(),
        "missed_budget": elapsed_ns > int(budget_ms * 1e6),
    }, profiler)


def _profile_top(profiler: cProfile.Profile, limit: int = 40) -> list[dict]:
    stats = pstats.Stats(profiler)
    rows = []
    for (filename, line, function), (primitive_calls, calls, total, cumulative, _callers) in sorted(
        stats.stats.items(), key=lambda item: item[1][3], reverse=True
    )[:limit]:
        rows.append({"file": filename, "line": line, "function": function,
                     "primitive_calls": primitive_calls, "calls": calls,
                     "total_seconds": total, "cumulative_seconds": cumulative})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data/processed/coupled_wire_dev_v1")
    ap.add_argument("--physics-gate", default="outputs/runs/coupled_wire_v1/physics_gate.json")
    ap.add_argument("--protocol", default="configs/experiments/matched_v1.json",
                    help="frozen matched-v1 protocol providing the shared pair-controller configuration")
    ap.add_argument("--indices", required=True, help="explicit comma-separated DEV frame indices")
    ap.add_argument("--budget-ms", type=float, default=100.0)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--cpu", type=int, required=True, help="pin the complete process to this allowed CPU")
    ap.add_argument("--output", required=True, help="new JSONL file; existing outputs are preserved")
    ap.add_argument("--top-functions", type=int, default=40)
    args = ap.parse_args(argv)
    if not 0 < args.budget_ms <= MAX_PROFILE_BUDGET_MS:
        raise ValueError(f"budget must be in (0, {MAX_PROFILE_BUDGET_MS}] ms")
    if args.top_functions < 1:
        raise ValueError("--top-functions must be positive")
    output = Path(args.output).resolve()
    if output.exists() or output.with_suffix(".json").exists():
        raise FileExistsError(f"preserving existing profiling output: {output}")
    data_dir = Path(args.data).resolve()
    scenario, metas, readiness_sha256 = _verify_dev_directory(data_dir)
    indices = csv_ints(args.indices)
    if not set(indices) <= set(metas):
        raise ValueError(f"indices are not verified development frames: {sorted(set(indices)-set(metas))}")
    if len(indices) > 10:
        raise ValueError("profiling is limited to at most 10 explicitly selected DEV frames per run")
    affinity = os.sched_getaffinity(0)
    if args.cpu not in affinity:
        raise ValueError(f"CPU {args.cpu} is outside current affinity {sorted(affinity)}")
    os.sched_setaffinity(0, {args.cpu})
    try:
        from threadpoolctl import threadpool_info, threadpool_limits
        threadpool_limits(limits=1)
        native_threadpools = threadpool_info()
    except ImportError:
        native_threadpools = None
    gate_path = Path(args.physics_gate).resolve()
    protocol_path = Path(args.protocol).resolve()
    gate = json.loads(gate_path.read_text())
    if not gate.get("passed"):
        raise ValueError("coupled physics gate has not passed")
    loads = np.asarray(gate["loads_real_ohm"], dtype=float) + 1j * np.asarray(gate["loads_imag_ohm"], dtype=float)
    protocol_raw = protocol_path.read_bytes()
    config = load_search_config("medium", protocol_path)

    source_paths = [ROOT / "src/atomwise_ris/optimization/coupled_search.py",
                    ROOT / "src/atomwise_ris/optimization/search.py",
                    ROOT / "src/atomwise_ris/physics/network.py",
                    ROOT / "src/atomwise_ris/channels/precoding.py",
                    Path(__file__).resolve()]
    source_hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in source_paths}
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx in indices:
        trajectory, step, frame_path, sidecar = metas[idx]
        if sha256_file(frame_path) != json.loads(sidecar.read_text())["sha256"]:
            raise ValueError(f"frame changed after manifest verification: {idx}")
        with np.load(frame_path, allow_pickle=False) as frame:
            z = np.asarray(frame["z"], dtype=np.complex128)
        profile_result, profiler = _profile_once(z, loads, args.budget_ms, args.seed, config, True)
        baseline_result, _ = _profile_once(z, loads, args.budget_ms, args.seed, config, False)
        pstats_rows = _profile_top(profiler, args.top_functions)
        trajectory_indices = [i for i, row in metas.items() if row[0] == trajectory]
        rows.append({
            "record_type": "profiled_frame",
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "scope": "development_only_descriptive_profile_not_for_method_selection",
            "dataset": data_dir.name,
            "split": "dev",
            "segments": int(scenario["segments"]),
            "index": idx,
            "trajectory": trajectory,
            "step": step,
            "trajectory_selected_n": len([i for i in indices if metas[i][0] == trajectory]),
            "trajectory_available_n": len(trajectory_indices),
            "frame_sha256": sha256_file(frame_path),
            "sidecar_sha256": sha256_file(sidecar),
            "scenario_sha256": sha256_file(data_dir / "scenario.json"),
            "generation_readiness_sha256": readiness_sha256,
            "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
            "source_sha256": source_hashes,
            "physics_gate_sha256": sha256_file(gate_path),
            "seed": args.seed,
            "budget_ms": args.budget_ms,
            "cpu_affinity": sorted(os.sched_getaffinity(0)),
            "host": {"hostname": platform.node(), "platform": platform.platform(),
                     "python": sys.version, "numpy": np.__version__,
                     "processor": platform.processor(), "cpu_count": os.cpu_count(),
                     "native_threadpools": native_threadpools,
                     "native_thread_limit": 1 if native_threadpools is not None else "uncontrolled; threadpoolctl unavailable"},
            "profiled": profile_result,
            "unprofiled_companion": baseline_result,
            "cprofile_overhead_proxy_ratio": (profile_result["elapsed_ms"] / baseline_result["elapsed_ms"]
                                                if baseline_result["elapsed_ms"] > 0 else None),
            "cprofile_top_functions": pstats_rows,
            "timing_caveat": "cProfile adds overhead and can change deadline-limited search path; these rates/timings are descriptive only",
        })
    with output.open("x", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"output": str(output), "rows": len(rows), "indices": indices,
                      "grouped_trajectory_selected_n": dict(Counter(metas[i][0] for i in indices)),
                      "scope": "development descriptive profile only"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
