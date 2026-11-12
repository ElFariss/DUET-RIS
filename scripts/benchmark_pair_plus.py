"""Run the development-only pair-plus ablation ladder on coupled-wire frames.

This runner deliberately has no test-split option. Full comparisons require
the complete source-bound 161-segment development dataset. The 81-segment data
and incomplete fine generation are available only through explicitly bounded
smoke modes. It writes new JSONL output and source/data hashes.
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

from atomwise_ris.optimization.pair_plus import ALL_METHODS, METHODS, M1_METHODS, PairPlusMemory, search
from atomwise_ris.optimization.pair_select import NumpyPairMLP
from atomwise_ris.optimization.coupled_search import search as coupled_search
from atomwise_ris.optimization.search import ME_GA_METHODS, Memory, load_search_config
from atomwise_ris.physics.network import CoupledNetwork


MEMORY_METHODS = ("pair_plus_l6", "pair_plus_b6")


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _csv_values(value, cast, label):
    result = [cast(item.strip()) for item in value.split(",") if item.strip()]
    if not result:
        raise ValueError(f"{label} must contain at least one value")
    if len(set(result)) != len(result):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def _validate_registered_data_path(data_dir, root):
    canonical = (root / "data/processed" / data_dir.name).resolve()
    if data_dir.resolve() != canonical:
        raise ValueError(f"--data must resolve to the registered project dataset: {canonical}")


def _validate_sidecar_row(meta, scenario_rows):
    try:
        index = int(meta["index"])
        trajectory = int(meta["trajectory"])
        step = int(meta["step"])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"frame sidecar has incomplete index/trajectory/step fields: {meta}")
    row = scenario_rows.get(index)
    if (row is None or meta.get("split") != "dev"
            or row.get("split") != "dev"
            or trajectory != int(row["trajectory"])
            or step != int(row["step"])):
        raise ValueError(f"frame sidecar {index} disagrees with its registered development scenario row")
    return index


def _nested_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _nested_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _nested_strings(item)


def _validate_fine_binding(scenario, ready, scenario_sha256, source_scenario_sha256, canonical_dev_indices):
    """Validate mesh identity, all-frame readiness, hash inventory and physics gate."""
    referenced_path = Path(str(scenario.get("fine_mesh_of", "")))
    fine_rows = scenario.get("rows", [])
    fine_indices = {int(row["index"]) for row in fine_rows if row.get("split") == "dev"}
    if (scenario.get("fine_mesh_split") != "dev" or scenario.get("segments") != 161
            or referenced_path.name != "coupled_wire_dev_v1"
            or scenario.get("source_scenario_sha256") != source_scenario_sha256):
        raise ValueError("fine scenario is not bound to the canonical 161-segment dev source")
    if (not fine_rows or len(fine_rows) != len(fine_indices)
            or any(row.get("split") != "dev" for row in fine_rows)
            or fine_indices != canonical_dev_indices):
        raise ValueError("fine scenario must contain exactly the canonical development indices and no other split")
    expected = list(range(480))
    physics = ready.get("physics_validation", {})
    try:
        minimum_eigenvalue = float(physics.get("minimum_resistance_eigenvalue_ohm_min", float("nan")))
        maximum_scattering = float(physics.get("maximum_scattering_singular_value_max", float("nan")))
        reciprocity_max = float(physics.get("reciprocity_relative_max", float("nan")))
    except (TypeError, ValueError):
        minimum_eigenvalue = maximum_scattering = reciprocity_max = float("nan")
    identity = ready.get("identity", {})
    if (ready.get("status") != "complete" or ready.get("ready_for_development_evaluation") is not True
            or ready.get("expected_indices") != expected
            or ready.get("verified_frame_indices") != expected
            or ready.get("missing_frame_indices") != [] or ready.get("invalid_frames") != []
            or physics.get("frames_checked") != 480
            or not np.isfinite(minimum_eigenvalue) or minimum_eigenvalue < -1e-6
            or not np.isfinite(maximum_scattering) or maximum_scattering > 1.0001
            or not np.isfinite(reciprocity_max)
            or identity.get("protocol_sha256") != scenario_sha256
            or identity.get("source_scenario_sha256") != source_scenario_sha256
            or not isinstance(ready.get("source_identity_sha256"), str)
            or ready.get("source_identity_sha256") != _identity_sha256(identity)):
        raise ValueError("fine readiness manifest is incomplete, unbound or failed its declared mesh/passivity checks")
    frame_hashes = ready.get("frame_npz_sha256", {})
    if set(frame_hashes) != {str(i) for i in expected}:
        raise ValueError("fine readiness manifest does not contain hashes for all 480 frame files")
    return frame_hashes, physics


def _identity_sha256(identity):
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _validate_fine_smoke_binding(scenario, ready, scenario_sha256, source_scenario_sha256,
                                 canonical_dev_indices):
    """Validate source/identity binding for bounded frames during generation."""
    rows = scenario.get("rows", [])
    indices = {int(row["index"]) for row in rows}
    identity = ready.get("identity", {})
    if (ready.get("status") not in {"running", "complete"}
            or scenario.get("fine_mesh_split") != "dev"
            or scenario.get("segments") != 161
            or Path(str(scenario.get("fine_mesh_of", ""))).name != "coupled_wire_dev_v1"
            or scenario.get("source_scenario_sha256") != source_scenario_sha256
            or indices != canonical_dev_indices or len(rows) != len(indices)
            or any(row.get("split") != "dev" for row in rows)
            or identity.get("protocol_sha256") != scenario_sha256
            or identity.get("source_scenario_sha256") != source_scenario_sha256
            or ready.get("source_identity_sha256") != _identity_sha256(identity)):
        raise ValueError("fine smoke manifest/scenario identity is incomplete or not source-bound")
    return identity, ready.get("source_identity_sha256")


def _validate_fine_smoke_frame(meta, npz_path, identity, identity_sha256):
    try:
        minimum_eigenvalue = float(meta["minimum_resistance_eigenvalue_ohm"])
        maximum_scattering = float(meta["maximum_scattering_singular_value"])
        reciprocity = float(meta["reciprocity_relative"])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"fine smoke frame {meta.get('index')} has incomplete physics diagnostics")
    if (meta.get("split") != "dev" or int(meta.get("segments_per_wire", -1)) != 161
            or meta.get("generation_identity_sha256") != identity_sha256
            or meta.get("generation_identity") != identity
            or meta.get("sha256") != sha256_file(npz_path)
            or not np.isfinite(minimum_eigenvalue) or minimum_eigenvalue < -1e-6
            or not np.isfinite(maximum_scattering) or maximum_scattering > 1.0001
            or not np.isfinite(reciprocity)):
        raise ValueError(f"fine smoke frame {meta.get('index')} failed its hash, identity or physics gate")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data/processed/coupled_wire_dev_fine161",
                    help="complete, source-bound coupled_wire_dev_fine161 for full runs")
    ap.add_argument("--physics-gate", default="outputs/runs/coupled_wire_v1/physics_gate.json")
    ap.add_argument("--protocol", default="configs/experiments/matched_v1.json",
                    help="source of the shared medium controller configuration")
    ap.add_argument("--mlp-run", default="outputs/runs/matched_coupled_v1",
                    help="frozen MLP checkpoint/scaling root")
    ap.add_argument("--output", required=True, help="new JSONL output path")
    ap.add_argument("--budgets", default="10,50,100", help="comma-separated milliseconds")
    ap.add_argument("--seeds", default="7,19,43", help="comma-separated deterministic seeds")
    ap.add_argument("--indices", default=None, help="optional comma-separated development frame indices")
    ap.add_argument("--fine-smoke", action="store_true",
                    help="allow at most 3 individually verified fine-dev frames before full readiness")
    ap.add_argument("--coarse-smoke", action="store_true",
                    help="allow at most 3 coarse-81 dev frames for explicitly non-result diagnostics")
    ap.add_argument("--methods", default=None,
                    help="comma-separated timed methods; default is the registered controls plus L1-L6. "
                         "Also accepts any pair_plus method, including the b35 selector methods "
                         "pair_plus_b35_m0_k{8,32,128,512} and pair_plus_b35_rand_k{32,128}")
    ap.add_argument("--neural-weights", default=None,
                    help="M1 NumPy-exported weights required by pair_plus_b35_m1_k* methods")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--cpu", type=int, default=None, help="optional single CPU affinity for controlled timing")
    ap.add_argument("--skip-me-ga-paper", action="store_true",
                    help="omit the full Gamma x V, no-deadline ME-GA reference (not a matched-budget run)")
    a = ap.parse_args()

    data_dir = Path(a.data).resolve()
    fine = data_dir.name == "coupled_wire_dev_fine161"
    coarse = data_dir.name == "coupled_wire_dev_v1"
    if not (fine or coarse) or "test" in data_dir.parts:
        raise SystemExit("--data must resolve to a registered development dataset; test paths are forbidden")
    _validate_registered_data_path(data_dir, ROOT)
    if a.fine_smoke and (not fine or a.coarse_smoke):
        raise SystemExit("--fine-smoke applies only to fine-161 data and cannot be combined with --coarse-smoke")
    if a.coarse_smoke and (not coarse or a.fine_smoke):
        raise SystemExit("--coarse-smoke applies only to coarse-81 data and cannot be combined with --fine-smoke")
    if coarse and not a.coarse_smoke:
        raise SystemExit("81-segment data is smoke-only after the C1 resolution stop rule; pass --coarse-smoke")
    if a.indices and not (a.fine_smoke or a.coarse_smoke):
        raise SystemExit("--indices is restricted to explicitly bounded smoke modes")
    out = Path(a.output).resolve()
    if data_dir in out.parents or out == data_dir:
        raise SystemExit("output must be outside the development data directory")
    if out.exists() or out.with_suffix(".json").exists():
        raise FileExistsError(f"preserving existing output: {out}")
    paper_out = out.with_name(out.stem + ".me-ga-paper.jsonl")
    if not a.skip_me_ga_paper and paper_out.exists():
        raise FileExistsError(f"preserving existing full-paper reference: {paper_out}")
    gate_path = Path(a.physics_gate).resolve()
    gate = json.loads(gate_path.read_text())
    if not gate.get("passed"):
        raise ValueError("coupled physics gate has not passed")
    loads = np.asarray(gate["loads_real_ohm"], dtype=float) + 1j * np.asarray(gate["loads_imag_ohm"], dtype=float)
    budgets = _csv_values(a.budgets, float, "budgets")
    seeds = _csv_values(a.seeds, int, "seeds")
    if any(x <= 0 for x in budgets):
        raise ValueError("budgets must be positive")
    if a.threads < 1:
        raise ValueError("threads must be positive")
    if a.cpu is not None:
        available = os.sched_getaffinity(0)
        if a.cpu not in available:
            raise ValueError(f"CPU {a.cpu} is outside the process affinity mask {sorted(available)}")
        os.sched_setaffinity(0, {a.cpu})

    protocol_path = Path(a.protocol).resolve()
    protocol_raw = protocol_path.read_bytes()
    protocol = json.loads(protocol_raw)
    cfg = load_search_config("medium", protocol_path)
    mlp_root = Path(a.mlp_run).resolve()
    policies = {}
    mlp_hashes = {}
    feature_scale = None
    requested_methods = _csv_values(a.methods, str, "methods") if a.methods else None
    needs_legacy_mlp = requested_methods is None or "mlp_ga" in requested_methods
    if needs_legacy_mlp:
        mlp_scaling_path = mlp_root / "feature_scaling.npz"
        if not mlp_scaling_path.is_file():
            raise FileNotFoundError(f"frozen MLP scaling is missing: {mlp_scaling_path}")
        try:
            import torch
            from atomwise_ris.models.coupled_policy import CoupledPolicy
        except ImportError as exc:
            raise RuntimeError("the frozen MLP comparator requires PyTorch") from exc
        torch.set_num_threads(a.threads)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
        scaling_npz = np.load(mlp_scaling_path, allow_pickle=False)
        feature_scale = (scaling_npz["mean"], scaling_npz["std"])
        for seed in seeds:
            model_dir = mlp_root / "models" / f"mlp_seed{seed}"
            checkpoint = model_dir / "best.pt"
            meta_path = model_dir / "metadata.json"
            if not checkpoint.is_file() or not meta_path.is_file():
                raise FileNotFoundError(f"frozen MLP artifacts are incomplete for seed {seed}: {model_dir}")
            ck = torch.load(checkpoint, map_location="cpu", weights_only=True)
            model = CoupledPolicy(kind="mlp")
            model.load_state_dict(ck["state_dict"])
            model.eval()

            def policy_call(x, g, m=model):
                with torch.inference_mode():
                    return m(torch.as_tensor(x, dtype=torch.float32)[None],
                             torch.as_tensor(g, dtype=torch.float32)[None])[0].cpu().numpy()

            policies[seed] = policy_call
            mlp_hashes[str(seed)] = {
                "checkpoint_sha256": sha256_file(checkpoint),
                "metadata_sha256": sha256_file(meta_path),
            }

    canonical_dev = ROOT / "data/processed/coupled_wire_dev_v1"
    canonical_scenario_path = canonical_dev / "scenario.json"
    if not canonical_scenario_path.is_file():
        raise FileNotFoundError(f"canonical coarse development scenario is missing: {canonical_scenario_path}")
    canonical_scenario = json.loads(canonical_scenario_path.read_text())
    canonical_dev_indices = {
        int(row["index"]) for row in canonical_scenario.get("rows", [])
        if row.get("split") == "dev"
    }
    if fine:
        scenario_path = data_dir / "scenario.json"
        readiness_path = data_dir / "generation_status.json"
        if not scenario_path.is_file() or not readiness_path.is_file():
            raise FileNotFoundError("fine development requires scenario.json and generation_status.json")
        scenario = json.loads(scenario_path.read_text())
        ready = json.loads(readiness_path.read_text())
        source_hash = sha256_file(canonical_scenario_path)
        if a.fine_smoke:
            identity, identity_hash = _validate_fine_smoke_binding(
                scenario, ready, sha256_file(scenario_path), source_hash, canonical_dev_indices)
            frame_hashes = ready.get("frame_npz_sha256", {})
            physics = ready.get("physics_validation", {})
        else:
            frame_hashes, physics = _validate_fine_binding(
                scenario, ready, sha256_file(scenario_path), source_hash, canonical_dev_indices)
    else:
        scenario = canonical_scenario
        if int(scenario.get("segments", -1)) != 81:
            raise ValueError("coarse development source must be the registered 81-segment dataset")
        if any(row.get("split") != "dev" for row in scenario.get("rows", [])):
            raise ValueError("coarse development scenario contains a non-development row")
        ready = None
        frame_hashes = None
    scenario_rows = {int(row["index"]): row for row in scenario.get("rows", [])}

    metas = []
    for meta_path in sorted(data_dir.glob("frame_*.json")):
        meta = json.loads(meta_path.read_text())
        if meta.get("split") != "dev":
            continue
        index = _validate_sidecar_row(meta, scenario_rows)
        data_path = meta_path.with_suffix(".npz")
        if not data_path.is_file() or meta.get("sha256") != sha256_file(data_path):
            raise ValueError(f"development frame missing or hash mismatch: {meta_path.name}")
        if data_dir.name == "coupled_wire_dev_fine161":
            if int(meta.get("segments_per_wire", -1)) != 161:
                raise ValueError(f"fine frame disagrees with its source/readiness provenance: {meta_path.name}")
            if not a.fine_smoke and frame_hashes.get(str(int(meta["index"]))) != sha256_file(data_path):
                raise ValueError(f"fine frame disagrees with its source/readiness provenance: {meta_path.name}")
        elif int(meta.get("segments_per_wire", -1)) != 81:
            raise ValueError(f"coarse frame has unexpected mesh resolution: {meta_path.name}")
        metas.append((index, int(meta["trajectory"]), int(meta["step"]), data_path, meta_path))
    present_indices = {item[0] for item in metas}
    if not present_indices.issubset(canonical_dev_indices):
        raise ValueError("frame sidecars contain indices outside the canonical development split")
    if fine and a.fine_smoke:
        if not present_indices:
            raise ValueError("fine smoke requires at least one present development frame")
    elif present_indices != canonical_dev_indices or len(metas) != len(canonical_dev_indices):
        raise ValueError("full development data must contain every canonical dev index exactly once")
    if a.indices:
        selected = set(_csv_values(a.indices, int, "indices"))
        missing = selected - {x[0] for x in metas}
        if missing:
            raise ValueError(f"indices are not verified development frames: {sorted(missing)}")
        metas = [x for x in metas if x[0] in selected]
    if not metas:
        raise ValueError("no verified development frames selected")
    if (a.fine_smoke or a.coarse_smoke) and len(metas) > 3:
        raise ValueError("smoke modes are capped at 3 development frames")
    if a.fine_smoke:
        for index, _, _, frame_path, meta_path in metas:
            meta = json.loads(meta_path.read_text())
            _validate_fine_smoke_frame(meta, frame_path, identity, identity_hash)
            manifest_hash = frame_hashes.get(str(index))
            if manifest_hash is not None and manifest_hash != sha256_file(frame_path):
                raise ValueError(f"fine smoke frame {index} hash differs from readiness manifest")

    os.environ.setdefault("OMP_NUM_THREADS", str(a.threads))
    try:
        import threadpoolctl
        threadpoolctl.threadpool_limits(limits=a.threads)
    except ImportError:
        pass

    data_manifest = hashlib.sha256("\n".join(
        f"{i}:{sha256_file(npz)}:{sha256_file(meta)}" for i, _, _, npz, meta in metas
    ).encode()).hexdigest()
    timed_methods = ["greedy", "pair", "me_ga", "ga_risc", "mlp_ga", *METHODS]
    if a.methods:
        timed_methods = _csv_values(a.methods, str, "methods")
        unknown = set(timed_methods) - {"greedy", "pair", "me_ga", "ga_risc", "mlp_ga", *ALL_METHODS}
        if unknown:
            raise ValueError(f"unknown methods: {sorted(unknown)}")
    neural_model = NumpyPairMLP.from_npz(a.neural_weights) if a.neural_weights else None
    if set(timed_methods) & set(M1_METHODS) and neural_model is None:
        raise ValueError("M1 methods require --neural-weights")
    meta_out = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hostname": platform.node(), "python": sys.version,
        "numpy": np.__version__, "threads": a.threads,
        "cpu_affinity": sorted(os.sched_getaffinity(0)),
        "m1_weights_sha256": sha256_file(a.neural_weights) if a.neural_weights else None,
        "m1_cascade_shortlist": 256 if neural_model is not None else None,
        "split": "development", "data_dir": str(data_dir),
        "evaluation_class": "coarse_smoke_non_result" if a.coarse_smoke else (
            "fine_smoke_non_result" if a.fine_smoke else "full_fine161_development_comparison"),
        "smoke_mode": bool(a.fine_smoke or a.coarse_smoke),
        "frame_count": len(metas), "frame_indices": [x[0] for x in metas],
        "trajectories": sorted({x[1] for x in metas}),
        "methods": timed_methods, "separate_untimed_method": None if a.skip_me_ga_paper else "me_ga_paper",
        "budgets_ms": budgets, "seeds": seeds,
        "protocol_path": str(protocol_path), "protocol_sha256": hashlib.sha256(protocol_raw).hexdigest(),
        "mlp_run": str(mlp_root), "mlp_feature_scaling_sha256": sha256_file(mlp_scaling_path) if needs_legacy_mlp else None,
        "mlp_checkpoint_hashes": mlp_hashes,
        "algorithm_parameters": {
            "l2_screen_margin_bit_s_hz": 0.50,
            "l3_restart_densities": [18.0 / 64.0, 0.5],
            "l4_tabu_tenure": 5, "l4_max_escape_moves_per_basin": 8,
            "l5_elite_capacity": 8, "l6_memory_capacity": 4,
            "l6_max_rank_k_flip_count": 20,
        },
        "data_manifest_sha256": data_manifest,
        "mesh_segments": 161 if data_dir.name == "coupled_wire_dev_fine161" else 81,
        "fine_readiness_manifest_sha256": sha256_file(data_dir / "generation_status.json") if ready is not None else None,
        "fine_physics_validation": ready.get("physics_validation") if ready is not None else None,
        "physics_gate_path": str(gate_path), "physics_gate_sha256": sha256_file(gate_path),
        "source_sha256": {
            "pair_plus.py": sha256_file(ROOT / "src/atomwise_ris/optimization/pair_plus.py"),
            "pair_select.py": sha256_file(ROOT / "src/atomwise_ris/optimization/pair_select.py"),
            "benchmark_pair_plus.py": sha256_file(Path(__file__)),
            "coupled_network.py": sha256_file(ROOT / "src/atomwise_ris/physics/network.py"),
            "precoding.py": sha256_file(ROOT / "src/atomwise_ris/channels/precoding.py"),
            "coupled_search.py": sha256_file(ROOT / "src/atomwise_ris/optimization/coupled_search.py"),
            "search.py": sha256_file(ROOT / "src/atomwise_ris/optimization/search.py"),
            "me_ga.py": sha256_file(ROOT / "src/atomwise_ris/optimization/me_ga.py"),
            "coupled_policy.py": sha256_file(ROOT / "src/atomwise_ris/models/coupled_policy.py"),
        },
        "timing_includes": ["CoupledNetwork construction", "frame-local search", "memory retrieval and rescoring",
                            "candidate feature/evaluation operations", "returned-action full verification"],
        "timing_excludes": ["data loading", "one-time Python/import warmup", "disk writes"],
        "scope": "development tuning only; no test data or held-out evaluation",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(meta_out, indent=2, sort_keys=True) + "\n")

    memories = {}
    for method in timed_methods:
        for seed in seeds:
            for budget in budgets:
                if method in MEMORY_METHODS:
                    memories[method, seed, budget] = PairPlusMemory()
                elif method in ME_GA_METHODS:
                    memories[method, seed, budget] = Memory()
                else:
                    memories[method, seed, budget] = []
    last_trajectory = {key: None for key in memories}
    # One discarded pass per method so lazy imports and first-call costs are not charged to the first
    # recorded rows (declared in timing_excludes). Uses empty memory; no result from it is kept.
    with np.load(metas[0][3], allow_pickle=False) as data:
        warm_z = np.asarray(data["z"], dtype=np.complex128)
    for method in timed_methods:
        warm_ev = CoupledNetwork(warm_z, loads)
        warm_deadline = time.perf_counter_ns() + 20_000_000
        if method in ALL_METHODS:
            search(warm_ev, method, warm_deadline, 1,
                   memory=PairPlusMemory() if method in MEMORY_METHODS else None, trace=[],
                   selector_model=neural_model)
        else:
            warm_policy = policies[seeds[0]] if method == "mlp_ga" else None
            coupled_search(warm_ev, method, warm_deadline, 1,
                           memory=Memory() if method in ME_GA_METHODS else [], policy=warm_policy,
                           scaling=feature_scale if warm_policy else None, config=cfg, trace=[])
    with out.open("x") as f:
        for index, trajectory, step, frame_path, _ in metas:
            with np.load(frame_path, allow_pickle=False) as data:
                z = np.asarray(data["z"], dtype=np.complex128)
            for budget in budgets:
                for seed in seeds:
                    for method in timed_methods:
                        key = (method, seed, budget)
                        memory = memories[key]
                        start = time.perf_counter_ns()
                        if hasattr(memory, "enter"):
                            memory.enter(trajectory)
                        elif last_trajectory[key] != trajectory:
                            memory.clear()
                        last_trajectory[key] = trajectory
                        deadline = start + int(budget * 1e6)
                        ev = CoupledNetwork(z, loads)
                        trace = []
                        if method in ALL_METHODS:
                            bits, value, evaluations, breakdown = search(
                                ev, method, deadline, seed * 1000003 + index,
                                memory=memory if method in MEMORY_METHODS else None,
                                trace=trace, selector_model=neural_model)
                        else:
                            policy = policies[seed] if method == "mlp_ga" else None
                            bits, value, evaluations, breakdown = coupled_search(
                                ev, method, deadline, seed * 1000003 + index,
                                memory=memory, policy=policy, scaling=feature_scale if policy else None,
                                config=cfg, trace=trace)
                            if method == "mlp_ga":
                                memory.insert(0, np.asarray(bits, dtype=np.int8).copy())
                                del memory[12:]
                        full_value = float(ev.score(ev.channel(bits) @ ev.w))
                        elapsed = (time.perf_counter_ns() - start) / 1e6
                        if abs(full_value - value) > 1e-7:
                            raise AssertionError("returned action failed direct full-network rescore")
                        row = {
                            "split": "development", "method": method, "seed": seed,
                            "budget_ms": budget, "index": index, "trajectory": trajectory,
                            "step": step, "rate": full_value, "elapsed_ms": elapsed,
                            "deadline_missed": elapsed > budget or bool(breakdown.get("deadline_missed", False)),
                            "evaluations": evaluations, "on_bits": int(np.sum(bits)),
                            "bits": np.asarray(bits, dtype=int).tolist(), "trace": trace,
                            "breakdown": breakdown,
                        }
                        f.write(json.dumps(row, separators=(",", ":")) + "\n")
                        f.flush()
    if not a.skip_me_ga_paper:
        paper_memories = {seed: Memory() for seed in seeds}
        with paper_out.open("x") as f:
            for index, trajectory, step, frame_path, _ in metas:
                with np.load(frame_path, allow_pickle=False) as data:
                    z = np.asarray(data["z"], dtype=np.complex128)
                for seed in seeds:
                    start = time.perf_counter_ns()
                    ev = CoupledNetwork(z, loads)
                    memory = paper_memories[seed]
                    memory.enter(trajectory)
                    trace = []
                    bits, value, evaluations, breakdown = coupled_search(
                        ev, "me_ga_paper", start + 1, seed * 1000003 + index,
                        memory=memory, config=cfg, trace=trace)
                    full_value = float(ev.score(ev.channel(bits) @ ev.w))
                    elapsed = (time.perf_counter_ns() - start) / 1e6
                    if abs(full_value - value) > 1e-7:
                        raise AssertionError("ME-GA-paper action failed direct full-network rescore")
                    f.write(json.dumps({
                        "split": "development", "method": "me_ga_paper", "deadline_applicable": False,
                        "deadline_missed": None, "seed": seed, "budget_ms": None,
                        "index": index, "trajectory": trajectory, "step": step,
                        "rate": full_value, "elapsed_ms": elapsed, "evaluations": evaluations,
                        "on_bits": int(np.sum(bits)), "bits": np.asarray(bits, dtype=int).tolist(),
                        "trace": trace, "breakdown": breakdown,
                    }, separators=(",", ":")) + "\n")
                    f.flush()
    print(json.dumps({"status": "complete", "output": str(out), "frames": len(metas),
                      "rows": len(metas) * len(budgets) * len(seeds) * len(timed_methods),
                      "paper_rows": 0 if a.skip_me_ga_paper else len(metas) * len(seeds),
                      "source_sha256": meta_out["source_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()

