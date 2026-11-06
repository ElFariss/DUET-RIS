"""Development-only causal forecast comparison on the coupled validation split."""
import argparse
import hashlib
import json
import os
import platform
import time
from pathlib import Path

import numpy as np
import torch

from atomwise_ris.models.coupled_policy import LinkGRU
from atomwise_ris.models.forecast import passive_reciprocal, predict, require_forecast_checkpoint
from atomwise_ris.optimization.coupled_search import search
from atomwise_ris.optimization.search import load_search_config
from atomwise_ris.physics.network import CoupledNetwork
from atomwise_ris.core import sha256


FORECASTS = ("persistence", "linear", "gru", "oracle")


def validate_history_rows(dataset, indices):
    """Require exactly four contiguous observations from the same trajectory."""
    z, trajectory, step = dataset["z"], dataset["trajectory"], dataset["step"]
    rows = []
    for raw_idx in indices:
        idx = int(raw_idx)
        if idx < 4:
            raise ValueError(f"Validation frame {idx} has fewer than four history frames")
        history = np.arange(idx - 4, idx)
        if not np.all(trajectory[history] == trajectory[idx]):
            raise ValueError(f"Frame {idx} history crosses a trajectory boundary")
        if not np.array_equal(step[history], np.arange(int(step[idx]) - 4, int(step[idx]))):
            raise ValueError(f"Frame {idx} history is not four contiguous prior steps")
        if z.shape[0] <= idx:
            raise IndexError(idx)
        rows.append({"index": idx, "trajectory": int(trajectory[idx]), "step": int(step[idx]),
                     "history_indices": history.tolist()})
    return rows


def forecast_from_history(history, forecast, model=None, scaling=None, current_truth=None):
    """Causal predictors consume only history; oracle is an unavailable current-CSI reference."""
    if forecast == "oracle":
        if current_truth is None:
            raise ValueError("Oracle forecast requires the current truth reference")
        return passive_reciprocal(np.asarray(current_truth).copy())
    if forecast == "persistence":
        return passive_reciprocal(np.asarray(history[-1]).copy())
    return predict(history, forecast, model, scaling)


def array_hash(value):
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8)).hexdigest()


def timed_action(z, idx, forecast, model, scaling, loads, budget_ms, seed, config,
                 network_factory=CoupledNetwork, search_fn=search):
    """Time stale-reference construction, forecast preparation, and a shared memory-free pair search."""
    started = time.perf_counter_ns()
    # Recompute this deterministic reference per candidate so its construction cost is timed equally.
    reference = network_factory(z[idx - 1], loads)
    w = reference.w.copy()
    history = z[idx - 4:idx]  # the slice is deliberately inside the timed region
    forecast_started = time.perf_counter_ns()
    belief = forecast_from_history(history, forecast, model, scaling,
                                   current_truth=z[idx] if forecast == "oracle" else None)
    forecast_ms = (time.perf_counter_ns() - forecast_started) / 1e6
    belief_network = network_factory(belief, loads, w=w)
    deadline = started + int(budget_ms * 1e6)
    bits, belief_rate, evaluations, search_breakdown = search_fn(
        belief_network, "pair", deadline, seed, memory=(), policy=None, scaling=None, config=config)
    elapsed_ms = (time.perf_counter_ns() - started) / 1e6

    # These checks are explicitly outside the timed action.
    cached_full = float(belief_network.score(belief_network.channel(bits) @ w))
    if abs(cached_full - float(belief_rate)) > 1e-7:
        raise AssertionError("Cached and full belief-network score disagree")
    truth_network = network_factory(z[idx], loads, w=w)
    truth_rate = float(truth_network.score(truth_network.channel(bits) @ w))
    forecast_mse = float(np.mean(np.abs(belief - z[idx]) ** 2))
    return {
        "bits": np.asarray(bits, dtype=np.int8).tolist(),
        "initial_state": "all_off",
        "search": "pair",
        "memory_length": 0,
        "belief_rate": float(belief_rate),
        "truth_rate": truth_rate,
        "forecast_mse": forecast_mse,
        "cached_full_score": cached_full,
        "cached_full_score_error": abs(cached_full - float(belief_rate)),
        "elapsed_ms": elapsed_ms,
        "deadline_missed": elapsed_ms > budget_ms,
        "evaluations": int(evaluations),
        "precoder_sha256": array_hash(w),
        "forecast_ms": forecast_ms,
        "search_breakdown_ms": search_breakdown,
    }


def load_gru(run, seed, device):
    model_dir = Path(run) / "models" / f"gru_seed{seed}"
    checkpoint = torch.load(model_dir / "best.pt", map_location=device, weights_only=True)
    validate_gru_checkpoint(checkpoint, seed)
    model = LinkGRU().to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    scaling_archive = np.load(model_dir / "scaling.npz")
    scaling = (scaling_archive["mean"], scaling_archive["scale"],
               np.asarray(scaling_archive["upper"]),
               scaling_archive["active_mask"] if "active_mask" in scaling_archive else None)
    return model, scaling, checkpoint


def validate_gru_checkpoint(checkpoint, seed):
    require_forecast_checkpoint(checkpoint)
    if checkpoint.get("kind") != "gru" or int(checkpoint.get("seed", -1)) != int(seed):
        raise RuntimeError(f"Forecast checkpoint kind/seed mismatch for requested GRU seed {seed}")


def summarize(records):
    """Return per-trajectory clusters and paired forecast deltas for descriptive validation."""
    summary = {}
    for budget in sorted({float(row["budget_ms"]) for row in records}):
        summary[str(budget)] = {}
        for forecast in FORECASTS:
            group = [r for r in records if float(r["budget_ms"]) == budget and r["forecast"] == forecast]
            metrics = ("elapsed_ms", "deadline_missed", "evaluations", "truth_rate", "belief_rate", "forecast_mse")
            per_traj = {}
            for trajectory in sorted({int(r["trajectory"]) for r in group}):
                rows = [r for r in group if int(r["trajectory"]) == trajectory]
                per_traj[str(trajectory)] = {metric: float(np.mean([float(r[metric]) for r in rows]))
                                             for metric in metrics}
                per_traj[str(trajectory)]["n"] = len(rows)
            macro = {metric: float(np.mean([value[metric] for value in per_traj.values()]))
                     for metric in metrics}
            macro["trajectory_sd"] = {
                metric: float(np.std([value[metric] for value in per_traj.values()], ddof=1))
                for metric in metrics
            }
            summary[str(budget)][forecast] = {"n_trajectories": len(per_traj),
                                              "n_rows": len(group), "per_trajectory": per_traj,
                                              "trajectory_macro_mean": macro}
        baseline = summary[str(budget)]["persistence"]["per_trajectory"]
        for forecast in ("linear", "gru", "oracle"):
            candidate = summary[str(budget)][forecast]["per_trajectory"]
            paired = {}
            for trajectory in candidate:
                paired[trajectory] = {
                    metric: candidate[trajectory][metric] - baseline[trajectory][metric]
                    for metric in ("truth_rate", "belief_rate", "forecast_mse", "elapsed_ms", "deadline_missed", "evaluations")
                }
            summary[str(budget)][forecast]["paired_vs_persistence_per_trajectory"] = paired
            summary[str(budget)][forecast]["paired_vs_persistence_macro_mean"] = {
                metric: float(np.mean([row[metric] for row in paired.values()]))
                for metric in next(iter(paired.values()))
            }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="fresh v2 run root containing gru_seed7/19/43")
    parser.add_argument("--data", required=True, help="immutable coupled dataset.npz")
    parser.add_argument("--out", default="benchmark_temporal_v2_validation.jsonl")
    parser.add_argument("--budgets-ms", type=float, nargs="+", default=[5., 10., 50.])
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 19, 43])
    parser.add_argument("--expected-frames", type=int, default=36)
    parser.add_argument("--search-config", choices=["small", "medium", "large"], default="medium")
    args = parser.parse_args()

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    cpu = min(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpu})
    run, dataset_path = Path(args.run), Path(args.data)
    out = run / args.out
    if out.exists() or out.with_suffix(".json").exists():
        raise FileExistsError(out)
    gate_path = run / "physics_gate.json"
    gate = json.loads(gate_path.read_text())
    if not gate.get("passed"):
        raise RuntimeError("Coupled physics gate did not pass")
    dataset_npz = np.load(dataset_path)
    dataset = {key: dataset_npz[key] for key in dataset_npz.files}
    indices = np.flatnonzero((dataset["split"] == "validation") & (dataset["step"] >= 4))
    rows = validate_history_rows(dataset, indices)
    trajectories = sorted({row["trajectory"] for row in rows})
    if len(indices) != args.expected_frames or len(trajectories) != 3:
        raise ValueError(f"Expected {args.expected_frames} rows from 3 validation trajectories; got {len(indices)} / {len(trajectories)}")
    config = load_search_config(args.search_config)
    loads = np.asarray(gate["loads_real_ohm"]) + 1j * np.asarray(gate["loads_imag_ohm"])
    models = {seed: load_gru(run, seed, "cpu") for seed in args.seeds}
    weight_hashes = {}
    records = []
    start_all = time.perf_counter()
    for budget in args.budgets_ms:
        if budget <= 0:
            raise ValueError("Budgets must be positive")
        for seed in args.seeds:
            model, scaling, _checkpoint = models[seed]
            for row in rows:
                idx = row["index"]
                for forecast in FORECASTS:
                    result = timed_action(dataset["z"], idx, forecast, model, scaling, loads,
                                          budget, seed * 10000 + idx, config)
                    prior_hash = weight_hashes.setdefault(idx, result["precoder_sha256"])
                    if prior_hash != result["precoder_sha256"]:
                        raise AssertionError("A forecast method changed the shared stale precoder")
                    records.append({
                        "forecast": forecast,
                        "seed": seed,
                        "budget_ms": budget,
                        **row,
                        **result,
                    })
        print(f"completed budget={budget:g}ms rows={len(records)}", flush=True)

    input_hash = sha256(dataset_path)
    checkpoint_meta = {}
    for seed in args.seeds:
        model_dir = run / "models" / f"gru_seed{seed}"
        ckpath = model_dir / "best.pt"
        checkpoint_meta[str(seed)] = {
            "checkpoint_sha256": sha256(ckpath),
            "scaling_sha256": sha256(model_dir / "scaling.npz"),
            "metadata_sha256": sha256(model_dir / "metadata.json"),
            "architecture_version": models[seed][2]["architecture_version"],
            "kind": models[seed][2]["kind"],
            "seed": models[seed][2]["seed"],
            "epoch": models[seed][2]["epoch"],
            "best_validation": json.loads((model_dir / "metadata.json").read_text())["best_validation"],
        }
    metadata = {
        "purpose": "development-only fresh-v2 causal forecast comparison; not a matched or held-out test",
        "args": vars(args),
        "hostname": platform.node(),
        "cpu_affinity": [cpu],
        "threads": 1,
        "torch": torch.__version__,
        "numpy": np.__version__,
        "data_sha256": input_hash,
        "physics_gate_sha256": sha256(gate_path),
        "architecture_version": LinkGRU.architecture_version,
        "model_source_sha256": sha256(Path(__file__).resolve().parents[1] / "src/atomwise_ris/models/coupled_policy.py"),
        "forecast_source_sha256": sha256(Path(__file__).resolve().parents[1] / "src/atomwise_ris/models/forecast.py"),
        "benchmark_source_sha256": sha256(Path(__file__).resolve()),
        "trainer_source_sha256": sha256(Path(__file__).with_name("train_coupled.py")),
        "search_source_sha256": sha256(Path(__file__).resolve().parents[1] / "src/atomwise_ris/optimization/coupled_search.py"),
        "physics_network_source_sha256": sha256(Path(__file__).resolve().parents[1] / "src/atomwise_ris/physics/network.py"),
        "search_config_sha256": config.protocol_sha256,
        "checkpoints": checkpoint_meta,
        "forecast_methods": list(FORECASTS),
        "reference_precoder": "all-OFF RZF from z[idx-1], recomputed and timed per method; identical hash checked for every forecast at each frame",
        "controller": "same matched-medium pair search, no memory, initial all-OFF state",
        "timing_includes": ["stale-reference network and RZF precoder", "four-frame history slice", "forecast/passivity projection", "belief network setup", "pair search"],
        "timing_excludes": ["model loading", "truth-network exact-rate evaluation", "cached-full-score consistency check", "JSONL write"],
        "selection": "none; report all validation rows, seeds, and budgets",
        "oracle": "uses current impedance only as an unavailable current-CSI reference; not a guaranteed per-frame upper bound because pair search is heuristic",
        "n_validation_frames": len(rows),
        "validation_trajectories": trajectories,
        "wall_seconds": time.perf_counter() - start_all,
    }
    out.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    with out.open("x") as stream:
        for record in records:
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
    out.with_name(out.stem + ".summary.json").write_text(json.dumps({
        "raw_results": str(out),
        "metadata": str(out.with_suffix(".json")),
        "cluster_unit": "validation trajectory; seed/frame means are averaged within each of three trajectories",
        "n_clusters": 3,
        "results": summarize(records),
    }, indent=2) + "\n")
    print(json.dumps({"output": str(out), "metadata": str(out.with_suffix('.json')),
                      "records": len(records), "wall_seconds": metadata["wall_seconds"]}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
