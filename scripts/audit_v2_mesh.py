"""Rescore frozen spatial validation actions on 161-segment coupled-wire data.

This audit never optimizes actions. It compares each selected 50 ms validation
action on the original coarse frame with (1) the 161-segment frame under that
frame's original coarse all-OFF RZF precoder and (2) the same 161-segment frame
under a single common 161-segment all-OFF RZF precoder. The first contrast
isolates the impedance-mesh response; the second is a protocol sensitivity that
also recomputes the reference precoder. No test or pilot split is read.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atomwise_ris.physics.network import CoupledNetwork  # noqa: E402


METHOD_SOURCE_FILES = (
    "src/atomwise_ris/physics/network.py",
    "src/atomwise_ris/channels/precoding.py",
    "src/atomwise_ris/physics/nec.py",
)
EXPECTED_PRIMARY_MS = 50
EXPECTED_PREFERRED_MS = 10


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_json_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_json(path: Path):
    return json.loads(Path(path).read_text())


def load_switch_loads(gate):
    """Read the gate's OFF/ON state impedances shared by all 64 RIS cells."""
    real = np.asarray(gate["loads_real_ohm"], dtype=float)
    imag = np.asarray(gate["loads_imag_ohm"], dtype=float)
    if real.shape != (2,) or imag.shape != (2,) or not np.isfinite(real).all() or not np.isfinite(imag).all():
        raise ValueError("physics gate must define finite OFF/ON impedances shared by the 64 switches")
    return real + 1j * imag


def validate_frozen_artifacts(rows, metadata, selection, protocol, protocol_hash,
                              validation_jsonl_hash, expected_indices):
    """Fail closed on stale identity, split, budget, row, or action coverage."""
    methods = list(protocol["methods"]["baselines"]) + [
        k for k in protocol["methods"] if k != "baselines"
    ]
    seeds = [int(x) for x in protocol["seeds"]]
    budgets = [float(x) for x in protocol["budgets_ms"]]
    if protocol_hash != metadata.get("protocol_sha256") or protocol_hash != selection.get("protocol_sha256"):
        raise ValueError("protocol hash differs across current protocol, metadata, and selection")
    if int(protocol["primary_budget_ms"]) != EXPECTED_PRIMARY_MS:
        raise ValueError("protocol primary is not the predeclared locked 50 ms")
    if float(selection.get("selected_ms", -1)) != EXPECTED_PRIMARY_MS:
        raise ValueError("frozen selector did not select 50 ms")
    if int(selection.get("protocol_primary_ms", -1)) != EXPECTED_PRIMARY_MS:
        raise ValueError("selection's locked primary is not 50 ms")
    if float(selection.get("protocol_preferred_ms", -1)) != EXPECTED_PREFERRED_MS:
        raise ValueError("selection's preferred budget is not the predeclared 10 ms")
    if selection.get("input_hashes", {}).get("benchmark_spatial_validation.jsonl") != validation_jsonl_hash:
        raise ValueError("validation JSONL hash differs from its immutable budget selection")
    if selection.get("code_sha256") != metadata.get("frozen_code_sha256"):
        raise ValueError("code snapshot differs between sidecar and selection")
    if selection.get("checkpoint_sha256") != metadata.get("checkpoint_sha256"):
        raise ValueError("checkpoint snapshot differs between sidecar and selection")
    args = metadata.get("args", {})
    if args.get("split") != "validation" or args.get("mode") != "spatial":
        raise ValueError("source benchmark is not spatial validation")
    if args.get("test_data") or metadata.get("conditional_pair_policy"):
        raise ValueError("source run includes test input or conditional-pair development policy")
    if metadata.get("data_sha256") is None or metadata.get("physics_gate_sha256") is None:
        raise ValueError("source metadata lacks data or physics-gate provenance")
    if not selection.get("budget_lock"):
        raise ValueError("selection is missing the predeclared budget lock evidence")

    expected_indices = set(map(int, expected_indices))
    expected = {
        (method, seed, float(budget), index)
        for method, seed, budget, index in itertools.product(methods, seeds, budgets, expected_indices)
    }
    seen = set()
    for row in rows:
        if row.get("split") != "validation" or row.get("mode") != "spatial":
            raise ValueError("JSONL contains a non-spatial or non-validation row")
        key = (row.get("method"), int(row.get("seed", -1)), float(row.get("budget_ms", -1)), int(row.get("index", -1)))
        if key not in expected:
            raise ValueError(f"unexpected validation grid key: {key}")
        if key in seen:
            raise ValueError(f"duplicate validation grid key: {key}")
        seen.add(key)
        bits = row.get("bits")
        if not isinstance(bits, list) or len(bits) != 64 or any(b not in (0, 1) for b in bits):
            raise ValueError(f"invalid 64-bit action at {key}")
    if seen != expected:
        missing = len(expected - seen)
        extra = len(seen - expected)
        raise ValueError(f"validation grid is incomplete or unexpected (missing={missing}, extra={extra})")
    primary_rows = [r for r in rows if float(r["budget_ms"]) == EXPECTED_PRIMARY_MS]
    expected_primary_count = len(methods) * len(seeds) * len(expected_indices)
    if len(primary_rows) != expected_primary_count:
        raise ValueError(f"selected 50 ms action count {len(primary_rows)} != expected {expected_primary_count}")
    return methods, seeds, sorted(expected_indices), primary_rows


def _average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: (values[i], i))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = rank
        i = j
    return ranks


def _spearman(xs, ys):
    if len(xs) < 2:
        return None
    rx, ry = _average_ranks(xs), _average_ranks(ys)
    ax, ay = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((x - ax) * (y - ay) for x, y in zip(rx, ry))
    vx = sum((x - ax) ** 2 for x in rx)
    vy = sum((y - ay) ** 2 for y in ry)
    return cov / (vx * vy) ** 0.5 if vx > 0 and vy > 0 else None


def summarize(records, methods, bootstrap_samples=20000, bootstrap_seed=661):
    """Summarize paired shifts with trajectory as the resampling unit."""
    rng = np.random.default_rng(bootstrap_seed)
    by_method = {}
    per_method_values = {}
    trajectories = sorted({int(r["trajectory"]) for r in records})
    for method in methods:
        subset = [r for r in records if r["method"] == method]
        traj_means = {}
        for traj in trajectories:
            vals = [r["delta_fixed_w_bpshz"] for r in subset if int(r["trajectory"]) == traj]
            if vals:
                traj_means[traj] = float(np.mean(vals))
        if set(traj_means) != set(trajectories):
            raise ValueError(f"method {method} lacks paired rows in one or more trajectories")
        cluster_values = np.array([traj_means[t] for t in trajectories], dtype=float)
        draws = rng.choice(cluster_values, size=(bootstrap_samples, len(cluster_values)), replace=True).mean(axis=1)
        delta = np.array([r["delta_fixed_w_bpshz"] for r in subset], dtype=float)
        delta_recomputed = np.array([r["delta_fine_w_bpshz"] for r in subset], dtype=float)
        on_counts = [int(r["on_count"]) for r in subset]
        by_method[method] = {
            "n_actions": len(subset),
            "mean_on_count": float(np.mean(on_counts)),
            "mean_delta_fixed_w_bpshz": float(np.mean(delta)),
            "median_delta_fixed_w_bpshz": float(np.median(delta)),
            "trajectory_mean_delta_fixed_w_bpshz": {str(k): v for k, v in traj_means.items()},
            "trajectory_cluster_bootstrap_95pct": [float(x) for x in np.quantile(draws, [0.025, 0.975])],
            "n_independent_trajectory_clusters": len(trajectories),
            "spearman_on_count_vs_delta_fixed_w_by_trajectory": {
                str(t): _spearman(
                    [int(r["on_count"]) for r in subset if int(r["trajectory"]) == t],
                    [float(r["delta_fixed_w_bpshz"]) for r in subset if int(r["trajectory"]) == t],
                ) for t in trajectories
            },
            "spearman_on_count_vs_delta_fixed_w_pooled_descriptive": _spearman(on_counts, delta.tolist()),
            "mean_delta_fine_recomputed_w_bpshz": float(np.mean(delta_recomputed)),
            "trajectory_mean_delta_fine_recomputed_w_bpshz": {
                str(t): float(np.mean([r["delta_fine_w_bpshz"] for r in subset if int(r["trajectory"]) == t]))
                for t in trajectories
            },
        }
        per_method_values[method] = subset

    means_coarse = {m: float(np.mean([r["coarse_rate_bpshz"] for r in per_method_values[m]])) for m in methods}
    means_fixed = {m: float(np.mean([r["fine_fixed_w_rate_bpshz"] for r in per_method_values[m]])) for m in methods}
    means_recomputed = {m: float(np.mean([r["fine_recomputed_w_rate_bpshz"] for r in per_method_values[m]])) for m in methods}
    rank_coarse = _average_ranks([means_coarse[m] for m in methods])
    rank_fixed = _average_ranks([means_fixed[m] for m in methods])
    rank_recomputed = _average_ranks([means_recomputed[m] for m in methods])
    method_ranks = {
        m: {"coarse_rank": rank_coarse[i], "fine_fixed_w_rank": rank_fixed[i],
            "fine_recomputed_w_rank": rank_recomputed[i], "coarse_mean_bpshz": means_coarse[m],
            "fine_fixed_w_mean_bpshz": means_fixed[m], "fine_recomputed_w_mean_bpshz": means_recomputed[m]}
        for i, m in enumerate(methods)
    }

    contexts = {}
    for r in records:
        contexts.setdefault((int(r["seed"]), int(r["index"])), {})[r["method"]] = r
    reversals = 0
    pair_comparisons = 0
    reversal_by_trajectory = {str(t): [0, 0] for t in trajectories}
    for pair in itertools.combinations(methods, 2):
        for context in contexts.values():
            a, b = context[pair[0]], context[pair[1]]
            coarse_diff = a["coarse_rate_bpshz"] - b["coarse_rate_bpshz"]
            fine_diff = a["fine_fixed_w_rate_bpshz"] - b["fine_fixed_w_rate_bpshz"]
            if coarse_diff != 0 and fine_diff != 0:
                pair_comparisons += 1
                if (coarse_diff > 0) != (fine_diff > 0):
                    reversals += 1
                    bucket = reversal_by_trajectory[str(a["trajectory"])]
                    bucket[0] += 1
                reversal_by_trajectory[str(a["trajectory"])][1] += 1
    return {
        "methods": by_method,
        "method_mean_rate_ranks": method_ranks,
        "pairwise_order_reversals_fixed_w": {
            "reversals": reversals, "non_tied_comparisons": pair_comparisons,
            "fraction": reversals / pair_comparisons if pair_comparisons else None,
            "by_trajectory_counts": {k: {"reversals": v[0], "comparisons": v[1],
                                        "fraction": v[0] / v[1] if v[1] else None}
                                     for k, v in reversal_by_trajectory.items()},
        },
        "trajectory_clusters": trajectories,
    }


def run_audit(validation_jsonl: Path, metadata_path: Path, selection_path: Path,
              protocol_path: Path, coarse_data_path: Path, coarse_scenario_path: Path,
              fine_scenario_path: Path, fine_dir: Path, physics_gate_path: Path,
              output_path: Path):
    protocol = load_json(protocol_path)
    protocol_hash = sha256_file(protocol_path)
    metadata, selection = load_json(metadata_path), load_json(selection_path)
    raw_hash = sha256_file(validation_jsonl)
    rows = [json.loads(line) for line in validation_jsonl.read_text().splitlines() if line.strip()]
    coarse_scenario, fine_scenario = load_json(coarse_scenario_path), load_json(fine_scenario_path)
    if fine_scenario.get("fine_mesh_split") != "validation" or int(fine_scenario.get("segments", -1)) != 161:
        raise ValueError("fine dataset is not the declared 161-segment validation mesh")
    if fine_scenario.get("source_scenario_sha256") != sha256_file(coarse_scenario_path):
        raise ValueError("fine mesh geometry does not bind to the current coarse scenario")
    frame_rows = fine_scenario.get("rows", [])
    frame_map = {int(r["index"]): r for r in frame_rows}
    declared_indices = set(map(int, fine_scenario.get("fine_mesh_indices", [])))
    if declared_indices != set(frame_map) or len(frame_map) != 48:
        raise ValueError("fine scenario does not declare exactly its 48 validation frames")
    methods, seeds, indices, primary_rows = validate_frozen_artifacts(
        rows, metadata, selection, protocol, protocol_hash, raw_hash, declared_indices)

    source_hashes = metadata.get("frozen_code_sha256", {})
    method_code_identity = {}
    for rel in METHOD_SOURCE_FILES:
        captured = source_hashes.get(rel)
        current = sha256_file(ROOT / rel)
        if captured != current:
            raise ValueError(f"physics evaluator source is not the frozen version: {rel}")
        method_code_identity[rel] = current

    coarse_npz = np.load(coarse_data_path, allow_pickle=False)
    z_coarse = coarse_npz["z"]
    splits = coarse_npz["split"]
    trajectories = coarse_npz["trajectory"]
    steps = coarse_npz["step"]
    if sha256_file(coarse_data_path) != metadata["data_sha256"]:
        raise ValueError("coarse dataset hash differs from the source benchmark sidecar")
    if sha256_file(physics_gate_path) != metadata["physics_gate_sha256"]:
        raise ValueError("physics-gate hash differs from the source benchmark sidecar")
    gate = load_json(physics_gate_path)
    loads = load_switch_loads(gate)
    for index, frow in frame_map.items():
        if str(splits[index]) != "validation" or int(trajectories[index]) != int(frow["trajectory"]) or int(steps[index]) != int(frow["step"]):
            raise ValueError(f"coarse/fine validation frame identity differs at index {index}")

    selected_by_frame = {i: [] for i in indices}
    for row in primary_rows:
        selected_by_frame[int(row["index"])].append(row)
    records = []
    for index in indices:
        coarse_z = z_coarse[index]
        fine_path = fine_dir / f"frame_{index:04d}.npz"
        if not fine_path.is_file():
            raise FileNotFoundError(f"missing declared validation fine mesh {fine_path}")
        with np.load(fine_path, allow_pickle=False) as loaded:
            fine_z = loaded["z"].copy()
        if coarse_z.shape != (70, 70) or fine_z.shape != (70, 70):
            raise ValueError(f"unexpected impedance matrix shape at validation index {index}")
        coarse_reference = CoupledNetwork(coarse_z, loads)
        fine_reference = CoupledNetwork(fine_z, loads)
        coarse_w = coarse_reference.w
        fine_w = fine_reference.w
        coarse_eval = CoupledNetwork(coarse_z, loads, w=coarse_w)
        fine_fixed_eval = CoupledNetwork(fine_z, loads, w=coarse_w)
        fine_recomputed_eval = CoupledNetwork(fine_z, loads, w=fine_w)
        cache = {}
        for row in selected_by_frame[index]:
            bits = np.asarray(row["bits"], dtype=np.int8)
            key = bits.tobytes()
            scored = cache.get(key)
            if scored is None:
                coarse_rate = float(coarse_eval.score(coarse_eval.channel(bits) @ coarse_w))
                fine_fixed_rate = float(fine_fixed_eval.score(fine_fixed_eval.channel(bits) @ coarse_w))
                fine_recomputed_rate = float(fine_recomputed_eval.score(fine_recomputed_eval.channel(bits) @ fine_w))
                scored = (coarse_rate, fine_fixed_rate, fine_recomputed_rate)
                cache[key] = scored
            coarse_rate, fine_fixed_rate, fine_recomputed_rate = scored
            if abs(coarse_rate - float(row["rate"])) > 1e-7:
                raise ValueError(
                    f"coarse action/evaluator mismatch at method={row['method']} seed={row['seed']} index={index}: "
                    f"recomputed={coarse_rate:.12g} row={row['rate']:.12g}"
                )
            records.append({
                "method": row["method"], "seed": int(row["seed"]), "budget_ms": int(row["budget_ms"]),
                "index": index, "trajectory": int(row["trajectory"]), "step": int(row["step"]),
                "on_count": int(bits.sum()), "action_sha256": hashlib.sha256(bits.tobytes()).hexdigest(),
                "coarse_rate_bpshz": coarse_rate,
                "fine_fixed_w_rate_bpshz": fine_fixed_rate,
                "delta_fixed_w_bpshz": fine_fixed_rate - coarse_rate,
                "fine_recomputed_w_rate_bpshz": fine_recomputed_rate,
                "delta_fine_w_bpshz": fine_recomputed_rate - coarse_rate,
            })

    if len(records) != len(methods) * len(seeds) * len(indices):
        raise ValueError("rescore output did not preserve exact selected action coverage")
    summary = summarize(records, methods)
    result = {
        "audit": "C1 spatial validation fixed-action mesh rescore",
        "status": "descriptive_validation_only",
        "claims_limit": "This is a validation-only mesh sensitivity, not the protocol's conditional held-out test audit and it cannot satisfy that gate. The v1 contract predeclares 81 versus 161 segments with a 0.015 bit/s/Hz criterion for that separate test action audit. The 161-segment validation matrix is not demonstrated converged; do not infer population fidelity or substitute a universal margin. Further mesh convergence would need a separate predeclared design.",
        "split": "validation",
        "method_scope": "12 frozen spatial methods; temporal and held-out test paths are excluded",
        "selected_budget_ms": EXPECTED_PRIMARY_MS,
        "preferred_budget_ms": EXPECTED_PREFERRED_MS,
        "n_methods": len(methods), "n_seeds": len(seeds), "n_frames": len(indices),
        "n_actions": len(records), "n_trajectory_clusters": len(summary["trajectory_clusters"]),
        "fixed_w_definition": "Each frame's original 81-segment all-OFF RZF precoder is held fixed for both coarse and 161-segment action evaluation; this isolates impedance-mesh response.",
        "recomputed_w_definition": "Sensitivity only: the common frame precoder is recomputed once from the 161-segment all-OFF channel, then used for every method on that frame.",
        "rescore_action_grid_sha256": canonical_json_hash([
            [r["method"], r["seed"], r["index"], r["action_sha256"]]
            for r in sorted(records, key=lambda x: (x["method"], x["seed"], x["index"]))
        ]),
        "inputs": {
            "validation_jsonl": {"path": str(validation_jsonl), "sha256": raw_hash},
            "selection": {"path": str(selection_path), "sha256": sha256_file(selection_path), "protocol_sha256": selection["protocol_sha256"]},
            "benchmark_metadata": {"path": str(metadata_path), "sha256": sha256_file(metadata_path),
                                   "frozen_code_sha256": metadata["frozen_code_sha256"],
                                   "checkpoint_sha256": metadata["checkpoint_sha256"]},
            "protocol": {"path": str(protocol_path), "sha256": protocol_hash},
            "coarse_data": {"path": str(coarse_data_path), "sha256": sha256_file(coarse_data_path),
                            "scenario_sha256": sha256_file(coarse_scenario_path)},
            "fine_scenario": {"path": str(fine_scenario_path), "sha256": sha256_file(fine_scenario_path),
                              "source_scenario_sha256": fine_scenario["source_scenario_sha256"]},
            "fine_frame_sha256": {str(i): sha256_file(fine_dir / f"frame_{i:04d}.npz") for i in indices},
            "physics_gate": {"path": str(physics_gate_path), "sha256": sha256_file(physics_gate_path)},
            "physics_evaluator_code_sha256": method_code_identity,
            "audit_script_sha256": sha256_file(Path(__file__)),
        },
        "summary": summary,
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-jsonl", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=ROOT / "configs/experiments/matched_v1.json")
    parser.add_argument("--coarse-data", type=Path, default=ROOT / "data/processed/coupled_wire_v1/dataset.npz")
    parser.add_argument("--coarse-scenario", type=Path, default=ROOT / "data/processed/coupled_wire_v1/scenario.json")
    parser.add_argument("--fine-scenario", type=Path, default=ROOT / "data/processed/coupled_wire_validation_fine161/scenario.json")
    parser.add_argument("--fine-dir", type=Path, default=ROOT / "data/processed/coupled_wire_validation_fine161")
    parser.add_argument("--physics-gate", type=Path, default=ROOT / "outputs/runs/coupled_wire_v1/physics_gate.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(args.validation_jsonl, args.metadata, args.selection, args.protocol,
                       args.coarse_data, args.coarse_scenario, args.fine_scenario,
                       args.fine_dir, args.physics_gate, args.output)
    print(json.dumps({k: result[k] for k in ("status", "selected_budget_ms", "n_actions", "n_trajectory_clusters", "rescore_action_grid_sha256")}, sort_keys=True))


if __name__ == "__main__":
    main()
