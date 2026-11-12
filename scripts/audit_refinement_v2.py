#!/usr/bin/env python3
"""Descriptive 81/161/201 fixed-action mesh stress diagnostic on C1 validation.

This rescores four preselected physical validation frames, never searches or
changes actions, and makes no population-level convergence claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from atomwise_ris.physics.network import CoupledNetwork  # noqa: E402

SELECTED_INDICES = (32, 96, 160, 174)
PRIMARY_BUDGET_MS = 50.0
COARSE_SCORE_ABS_TOL_BPSHZ = 1e-7
EVALUATOR_SOURCES = (
    "src/atomwise_ris/physics/network.py",
    "src/atomwise_ris/channels/precoding.py",
    "src/atomwise_ris/physics/nec.py",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def action_hash(bits: list[int]) -> str:
    arr = np.asarray(bits, dtype=np.int8)
    if arr.shape != (64,) or not np.isin(arr, (0, 1)).all():
        raise ValueError("frozen action must contain exactly 64 binary entries")
    return hashlib.sha256(arr.tobytes()).hexdigest()


def mesh_ratio(length_m: float, radius_m: float, segments: int) -> dict[str, float]:
    if length_m <= 0 or radius_m <= 0 or segments <= 0:
        raise ValueError("wire dimensions and segment count must be positive")
    segment_length = length_m / segments
    return {
        "segment_length_m": segment_length,
        "segment_length_to_radius": segment_length / radius_m,
    }


def select_frozen_actions(rows: list[dict[str, Any]], c1_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select C1's unchanged 50 ms validation actions on the prespecified frames."""
    allowed = set(SELECTED_INDICES)
    selected = [
        row for row in rows
        if row.get("split") == "validation"
        and row.get("mode") == "spatial"
        and float(row.get("budget_ms", -1)) == PRIMARY_BUDGET_MS
        and int(row.get("index", -1)) in allowed
    ]
    if len(selected) != 480:
        raise ValueError(f"expected 480 frozen actions (12 methods x 10 seeds x 4 frames), got {len(selected)}")
    keys = [(row["method"], int(row["seed"]), int(row["index"])) for row in selected]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate method/seed/frame action rows")
    grid = {(m, s, i) for m, s, i in keys}
    methods = sorted({m for m, _, _ in keys})
    seeds = sorted({s for _, s, _ in keys})
    expected = set(itertools.product(methods, seeds, SELECTED_INDICES))
    if grid != expected or len(methods) != 12 or len(seeds) != 10:
        raise ValueError("selected action grid does not match the prespecified C1 coverage")

    c1_map = {
        (record["method"], int(record["seed"]), int(record["index"])): record
        for record in c1_records
        if int(record["index"]) in allowed
    }
    if set(c1_map) != grid:
        raise ValueError("selected action grid differs from accepted C1 rescore records")
    for row in selected:
        key = (row["method"], int(row["seed"]), int(row["index"]))
        if action_hash(row["bits"]) != c1_map[key].get("action_sha256"):
            raise ValueError(f"frozen action differs from C1 at {key}")
    return sorted(selected, key=lambda row: (int(row["index"]), row["method"], int(row["seed"])))


def validate_mesh_case(
    *, index: int, segments: int, mesh_dir: Path, scenario: dict[str, Any],
    scenario_source_hash: str, coarse_scenario_path: Path,
    source_row: dict[str, Any], reference_frame_path: Path,
) -> tuple[np.ndarray, dict[str, Any]]:
    if scenario.get("fine_mesh_split") != "validation":
        raise ValueError("201-segment scenario is not validation-only")
    if int(scenario.get("segments", -1)) != segments:
        raise ValueError(f"expected {segments} segments, found {scenario.get('segments')}")
    if scenario.get("source_scenario_sha256") != scenario_source_hash:
        raise ValueError("201-segment scenario is not bound to the original coupled scenario")
    scenario_rows = {int(item["index"]): item for item in scenario.get("rows", [])}
    if not set(SELECTED_INDICES).issubset(scenario_rows):
        raise ValueError("201-segment scenario omits one or more preselected validation frames")
    if scenario_rows[index] != source_row:
        raise ValueError(f"201 geometry/frame row differs from source scenario at index {index}")

    npz_path = mesh_dir / f"frame_{index:04d}.npz"
    sidecar_path = npz_path.with_suffix(".json")
    if not npz_path.is_file() or not sidecar_path.is_file():
        raise FileNotFoundError(f"incomplete 201-segment case for frame {index}")
    sidecar = load_json(sidecar_path)
    if int(sidecar.get("segments_per_wire", -1)) != segments:
        raise ValueError(f"wrong segment count in frame {index} sidecar")
    if sha256_file(npz_path) != sidecar.get("sha256"):
        raise ValueError(f"NPZ/sidecar SHA-256 mismatch at frame {index}")
    if int(sidecar.get("index", -1)) != index or sidecar.get("split") != "validation":
        raise ValueError(f"frame sidecar identity mismatch at frame {index}")
    minimum_resistance = float(sidecar.get("minimum_resistance_eigenvalue_ohm", np.nan))
    maximum_scattering = float(sidecar.get("maximum_scattering_singular_value", np.nan))
    reciprocity = float(sidecar.get("reciprocity_relative", np.nan))
    if not np.isfinite([minimum_resistance, maximum_scattering, reciprocity]).all():
        raise ValueError(f"missing/nonfinite generation diagnostics at frame {index}")
    if minimum_resistance < -1e-6 or maximum_scattering > 1.0001:
        raise ValueError(f"201-segment passivity diagnostic failed at frame {index}")
    with np.load(npz_path, allow_pickle=False) as archive:
        z = archive["z"].copy()
        centers = archive["centers"].copy()
        lengths = archive["lengths"].copy()
    if z.shape != (70, 70) or not np.isfinite(z).all():
        raise ValueError(f"invalid 201 impedance matrix at frame {index}")
    if centers.shape != (70, 3) or lengths.shape != (70,) or not np.isfinite(centers).all() or not np.isfinite(lengths).all():
        raise ValueError(f"invalid physical geometry arrays at frame {index}")
    with np.load(reference_frame_path, allow_pickle=False) as archive:
        expected_centers = archive["centers"]
        expected_lengths = archive["lengths"]
    if not np.array_equal(centers, expected_centers) or not np.array_equal(lengths, expected_lengths):
        raise ValueError(f"201 geometry does not exactly match the paired reference mesh at frame {index}")
    return z, {
        "npz": npz_path, "sidecar": sidecar_path,
        "minimum_resistance_eigenvalue_ohm": minimum_resistance,
        "maximum_scattering_singular_value": maximum_scattering,
        "reciprocity_relative": reciprocity,
        "generation_identity_sha256": sidecar.get("generation_identity_sha256"),
    }


def _load_z(path: Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as archive:
        z = archive["z"].copy()
    if z.shape != (70, 70) or not np.isfinite(z).all():
        raise ValueError(f"invalid impedance matrix: {path}")
    return z


def score_fixed_actions(
    selected_rows: list[dict[str, Any]], coarse_data: np.lib.npyio.NpzFile,
    loads: np.ndarray, fine161_dir: Path, fine201_dir: Path,
    fine201_scenario: dict[str, Any], fine201_scenario_source_hash: str,
    coarse_scenario_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    coarse_scenario = load_json(coarse_scenario_path)
    scenario_rows = {int(item["index"]): item for item in coarse_scenario["rows"]}
    records = []
    mesh201_diagnostics: dict[str, dict[str, Any]] = {}
    for index in SELECTED_INDICES:
        coarse_z = coarse_data["z"][index]
        z161_path = fine161_dir / f"frame_{index:04d}.npz"
        z161 = _load_z(z161_path)
        z201, generation_diagnostics = validate_mesh_case(
            index=index, segments=201, mesh_dir=fine201_dir,
            scenario=fine201_scenario, scenario_source_hash=fine201_scenario_source_hash,
            coarse_scenario_path=coarse_scenario_path, source_row=scenario_rows[index],
            reference_frame_path=z161_path,
        )
        mesh201_diagnostics[str(index)] = {
            key: value for key, value in generation_diagnostics.items()
            if key not in {"npz", "sidecar"}
        }
        if coarse_z.shape != (70, 70) or not np.isfinite(coarse_z).all():
            raise ValueError(f"invalid coarse impedance matrix at frame {index}")
        reference = CoupledNetwork(coarse_z, loads)
        fixed_w = reference.w
        evaluators = {
            "81": CoupledNetwork(coarse_z, loads, w=fixed_w),
            "161": CoupledNetwork(z161, loads, w=fixed_w),
            "201": CoupledNetwork(z201, loads, w=fixed_w),
        }
        cache: dict[bytes, dict[str, float]] = {}
        for row in (item for item in selected_rows if int(item["index"]) == index):
            bits = np.asarray(row["bits"], dtype=np.int8)
            key = bits.tobytes()
            rates = cache.get(key)
            if rates is None:
                rates = {
                    mesh: float(net.score(net.channel(bits) @ fixed_w))
                    for mesh, net in evaluators.items()
                }
                cache[key] = rates
            if abs(rates["81"] - float(row["rate"])) > COARSE_SCORE_ABS_TOL_BPSHZ:
                raise ValueError(
                    f"frozen action/coarse score mismatch at {(row['method'], row['seed'], index)}: "
                    f"{rates['81']:.12g} vs {row['rate']:.12g}"
                )
            records.append({
                "method": row["method"], "seed": int(row["seed"]), "index": index,
                "trajectory": int(row["trajectory"]), "step": int(row["step"]),
                "action_sha256": action_hash(row["bits"]), "on_count": int(bits.sum()),
                "coarse_rate_bpshz": rates["81"], "rate_161_bpshz": rates["161"],
                "rate_201_bpshz": rates["201"],
                "delta_81_to_161_bpshz": rates["161"] - rates["81"],
                "delta_161_to_201_bpshz": rates["201"] - rates["161"],
                "delta_81_to_201_bpshz": rates["201"] - rates["81"],
                "abs_delta_81_to_161_bpshz": abs(rates["161"] - rates["81"]),
                "abs_delta_161_to_201_bpshz": abs(rates["201"] - rates["161"]),
            })
    if len(records) != 480:
        raise ValueError(f"expected 480 rescored actions, got {len(records)}")
    return records, mesh201_diagnostics


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    def stats(rows: list[dict[str, Any]], field: str) -> dict[str, float | int]:
        d = np.array([row[field] for row in rows])
        absolute = np.abs(d)
        return {
            "n_actions": int(len(rows)),
            "n_unique_actions": len({row["action_sha256"] for row in rows}) if rows and "action_sha256" in rows[0] else None,
            "n_all_off_actions": sum(int(row.get("on_count", -1)) == 0 for row in rows),
            "mean_signed_delta_bpshz": float(d.mean()),
            "median_signed_delta_bpshz": float(np.median(d)),
            "max_abs_delta_bpshz": float(absolute.max()),
            "p95_abs_delta_bpshz": float(np.quantile(absolute, 0.95)),
        }

    contrasts = {
        "81_to_161": "delta_81_to_161_bpshz",
        "161_to_201": "delta_161_to_201_bpshz",
        "81_to_201": "delta_81_to_201_bpshz",
    }
    per_frame = {
        name: {str(index): stats([row for row in records if row["index"] == index], field)
               for index in SELECTED_INDICES}
        for name, field in contrasts.items()
    }
    trajectory_ids = sorted({int(row["trajectory"]) for row in records})
    per_trajectory = {
        name: {str(trajectory): stats([row for row in records if row["trajectory"] == trajectory], field)
               for trajectory in trajectory_ids}
        for name, field in contrasts.items()
    }
    methods = sorted({row["method"] for row in records})
    contexts: dict[tuple[int, int], dict[str, dict[str, Any]]] = {}
    for row in records:
        contexts.setdefault((int(row["seed"]), int(row["index"])), {})[row["method"]] = row

    order_reversals = {}
    for name, field in (("81_vs_161", "rate_161_bpshz"), ("161_vs_201", "rate_201_bpshz")):
        coarse_field = "coarse_rate_bpshz" if name == "81_vs_161" else "rate_161_bpshz"
        reversals = comparisons = 0
        for context in contexts.values():
            for left, right in itertools.combinations(methods, 2):
                a, b = context[left], context[right]
                before, after = a[coarse_field] - b[coarse_field], a[field] - b[field]
                if before != 0.0 and after != 0.0:
                    comparisons += 1
                    reversals += int((before > 0) != (after > 0))
        order_reversals[name] = {
            "reversals": reversals, "non_tied_comparisons": comparisons,
            "fraction": reversals / comparisons if comparisons else None,
            "scope": "paired method-rate orderings within the selected seed/frame contexts; descriptive only",
        }
    return {
        "scope_note": "Four preselected validation frames over three trajectories; descriptive stress diagnostic only, not a population bound or global mesh-convergence claim.",
        "n_actions": len(records),
        "n_selected_frames": len(SELECTED_INDICES),
        "n_trajectory_clusters": len(trajectory_ids),
        "overall": {name: stats(records, field) for name, field in contrasts.items()},
        "per_frame": per_frame,
        "per_trajectory": per_trajectory,
        "max_abs_81_to_161_bpshz": max(row["abs_delta_81_to_161_bpshz"] for row in records),
        "max_abs_161_to_201_bpshz": max(row["abs_delta_161_to_201_bpshz"] for row in records),
        "max_abs_81_to_201_bpshz": max(abs(row["delta_81_to_201_bpshz"]) for row in records),
        "paired_method_order_reversals": order_reversals,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    c1 = load_json(args.c1_audit)
    metadata_path = args.metadata
    selection_path = args.selection
    validation_path = args.validation_jsonl
    protocol_path = args.protocol
    coarse_data_path = args.coarse_data
    coarse_scenario_path = args.coarse_scenario
    fine161_dir = args.fine161_dir
    fine161_scenario_path = args.fine161_scenario
    fine201_dir = args.fine201_dir
    fine201_scenario_path = args.fine201_scenario
    gate_path = args.physics_gate

    if c1.get("status") != "descriptive_validation_only" or c1.get("split") != "validation":
        raise ValueError("accepted C1 artifact is not validation-only")
    if c1.get("n_actions") != 5760 or c1.get("selected_budget_ms") != 50:
        raise ValueError("C1 source does not match locked validation action grid")
    audit_hashes = c1["inputs"]
    if sha256_file(validation_path) != audit_hashes["validation_jsonl"]["sha256"]:
        raise ValueError("validation JSONL hash differs from the accepted C1 audit")
    if sha256_file(metadata_path) != audit_hashes["benchmark_metadata"]["sha256"]:
        raise ValueError("benchmark metadata differs from the accepted C1 audit")
    if sha256_file(selection_path) != audit_hashes["selection"]["sha256"]:
        raise ValueError("budget selection differs from the accepted C1 audit")
    if sha256_file(protocol_path) != audit_hashes["protocol"]["sha256"]:
        raise ValueError("protocol differs from the accepted C1 audit")
    if sha256_file(coarse_data_path) != audit_hashes["coarse_data"]["sha256"]:
        raise ValueError("coarse dataset differs from the accepted C1 audit")
    if sha256_file(gate_path) != audit_hashes["physics_gate"]["sha256"]:
        raise ValueError("physics gate differs from the accepted C1 audit")

    metadata, selection, protocol = load_json(metadata_path), load_json(selection_path), load_json(protocol_path)
    if metadata.get("args", {}).get("split") != "validation" or metadata.get("args", {}).get("mode") != "spatial" or metadata.get("args", {}).get("test_data"):
        raise ValueError("benchmark metadata is not spatial validation-only")
    if selection.get("selected_ms") != 50 or metadata.get("data_sha256") != sha256_file(coarse_data_path):
        raise ValueError("selection or data provenance does not match locked C1 source")
    if sha256_file(protocol_path) != metadata.get("protocol_sha256"):
        raise ValueError("protocol hash differs from benchmark metadata")
    for rel, frozen in c1["inputs"]["physics_evaluator_code_sha256"].items():
        if sha256_file(ROOT / rel) != frozen:
            raise ValueError(f"physics evaluator source has drifted: {rel}")

    source_scenario_hash = sha256_file(coarse_scenario_path)
    if source_scenario_hash != audit_hashes["coarse_data"]["scenario_sha256"]:
        raise ValueError("source scenario differs from accepted C1 audit")
    fine161_scenario = load_json(fine161_scenario_path)
    if sha256_file(fine161_scenario_path) != audit_hashes["fine_scenario"]["sha256"]:
        raise ValueError("161-segment scenario differs from accepted C1 audit")
    if fine161_scenario.get("source_scenario_sha256") != source_scenario_hash:
        raise ValueError("161-segment scenario is not bound to source scenario")
    if int(fine161_scenario.get("segments", -1)) != 161:
        raise ValueError("C1 reference mesh is not 161 segments")
    for index in SELECTED_INDICES:
        expected_hash = audit_hashes["fine_frame_sha256"][str(index)]
        if sha256_file(fine161_dir / f"frame_{index:04d}.npz") != expected_hash:
            raise ValueError(f"161-segment frame hash mismatch at index {index}")

    fine201_scenario = load_json(fine201_scenario_path)
    fine201_scenario_hash = sha256_file(fine201_scenario_path)
    fine201_manifest_path = fine201_dir / "generation_status.json"
    fine201_manifest = load_json(fine201_manifest_path)
    coarse_scenario = load_json(coarse_scenario_path)
    if Path(str(fine201_scenario.get("fine_mesh_of", ""))).name != "coupled_wire_v1":
        raise ValueError("201-segment source dataset is not the frozen coupled_wire_v1 dataset")
    if (fine201_manifest.get("status") != "partial"
            or fine201_manifest.get("ready_for_development_evaluation") is not False
            or fine201_manifest.get("verified_frame_indices") != list(SELECTED_INDICES)
            or fine201_manifest.get("last_selected_indices") != list(SELECTED_INDICES)
            or len(fine201_manifest.get("missing_frame_indices", [])) != 44):
        raise ValueError("201-segment generation manifest does not describe the exact partial four-frame diagnostic")
    identity = fine201_manifest.get("identity", {})
    if (int(identity.get("segments", -1)) != 201
            or identity.get("source_scenario_sha256") != source_scenario_hash
            or identity.get("protocol_sha256") != fine201_scenario_hash):
        raise ValueError("201-segment generation identity does not match scenario and source hashes")

    with np.load(coarse_data_path, allow_pickle=False) as coarse_data:
        if sha256_file(coarse_data_path) != metadata["data_sha256"]:
            raise ValueError("coarse data changed while loading")
        splits, trajectories, steps = coarse_data["split"], coarse_data["trajectory"], coarse_data["step"]
        frame_rows = {int(row["index"]): row for row in coarse_scenario["rows"]}
        for index in SELECTED_INDICES:
            row = frame_rows[index]
            if str(splits[index]) != "validation" or int(trajectories[index]) != int(row["trajectory"]) or int(steps[index]) != int(row["step"]):
                raise ValueError(f"selected frame {index} is not the declared validation source row")

        rows = [json.loads(line) for line in validation_path.read_text().splitlines() if line.strip()]
        selected = select_frozen_actions(rows, c1["records"])
        gate = load_json(gate_path)
        loads = np.asarray(gate["loads_real_ohm"], dtype=float) + 1j * np.asarray(gate["loads_imag_ohm"], dtype=float)
        records, mesh201_diagnostics = score_fixed_actions(
            selected, coarse_data, loads, fine161_dir, fine201_dir,
            fine201_scenario, source_scenario_hash, coarse_scenario_path,
        )

    expected_ratio = mesh_ratio(float(coarse_scenario["wire_length_m"]), float(coarse_scenario["wire_radius_m"]), 201)
    result = {
        "audit": "preselected C1 validation fixed-action 81/161/201 mesh stress diagnostic",
        "status": "descriptive_validation_only",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(),
        "scope": "Frames 32, 96, 160 (first frame of each validation trajectory) plus frame 174 (C1 81-to-161 maximum); same frozen 50 ms spatial actions; validation only.",
        "claims_limit": "Four selected frames across three trajectories are a stress diagnostic, not a population confidence bound or global mesh-convergence proof. 161 segments are a reference mesh, not ground truth. No optimizer, training, pilot, or test action is used.",
        "predeclared_checks": {
            "selected_indices": list(SELECTED_INDICES),
            "selected_budget_ms": PRIMARY_BUDGET_MS,
            "expected_action_grid": "12 methods x 10 seeds x 4 frames = 480 exact C1 action rows",
            "coarse_rate_reproduction_abs_tolerance_bpshz": COARSE_SCORE_ABS_TOL_BPSHZ,
            "no_81_to_161_or_161_to_201_delta_threshold": True,
            "mesh_ratio_201": expected_ratio,
            "extended_kernel_condition_note": "NEC-2 manual reports the extended thin-wire kernel approximation error below 1% for Δ/a > 2 under stated assumptions; 201 segments gives Δ/a > 2 for this wire geometry. This is not a global channel/rate-error guarantee.",
        },
        "fixed_precoder": "For each frame, compute its original 81-segment all-OFF RZF precoder once and use that identical W for 81, 161, and 201 action scoring; this isolates impedance-mesh changes.",
        "summary": summarize(records),
        "fine201_generation_diagnostics": mesh201_diagnostics,
        "records": records,
        "inputs": {
            "c1_audit": {"path": str(args.c1_audit), "sha256": sha256_file(args.c1_audit)},
            "validation_jsonl": {"path": str(validation_path), "sha256": sha256_file(validation_path)},
            "benchmark_metadata": {"path": str(metadata_path), "sha256": sha256_file(metadata_path)},
            "selection": {"path": str(selection_path), "sha256": sha256_file(selection_path)},
            "protocol": {"path": str(protocol_path), "sha256": sha256_file(protocol_path)},
            "coarse_data": {"path": str(coarse_data_path), "sha256": sha256_file(coarse_data_path)},
            "coarse_scenario": {"path": str(coarse_scenario_path), "sha256": source_scenario_hash},
            "physics_gate": {"path": str(gate_path), "sha256": sha256_file(gate_path)},
            "fine161_scenario": {"path": str(fine161_scenario_path), "sha256": sha256_file(fine161_scenario_path)},
            "fine161_frames": {str(index): sha256_file(fine161_dir / f"frame_{index:04d}.npz") for index in SELECTED_INDICES},
            "fine201_scenario": {"path": str(fine201_scenario_path), "sha256": fine201_scenario_hash},
            "fine201_generation_manifest": {"path": str(fine201_manifest_path), "sha256": sha256_file(fine201_manifest_path)},
            "fine201_frames": {str(index): sha256_file(fine201_dir / f"frame_{index:04d}.npz") for index in SELECTED_INDICES},
            "fine201_frame_sidecars": {str(index): sha256_file(fine201_dir / f"frame_{index:04d}.json") for index in SELECTED_INDICES},
            "physics_evaluator_code_sha256": {rel: sha256_file(ROOT / rel) for rel in EVALUATOR_SOURCES},
            "audit_script_sha256": sha256_file(Path(__file__)),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c1-audit", type=Path, default=ROOT / "outputs/audits/v2-20261106/c1_spatial_validation_mesh161.attempt2.json")
    parser.add_argument("--validation-jsonl", type=Path, default=ROOT / "outputs/recovered/20261106/3060-1/fresh-gatefix-validation/coupled/benchmark_spatial_validation.jsonl")
    parser.add_argument("--metadata", type=Path, default=ROOT / "outputs/recovered/20261106/3060-1/fresh-gatefix-validation/coupled/benchmark_spatial_validation.json")
    parser.add_argument("--selection", type=Path, default=ROOT / "outputs/recovered/20261106/3060-1/fresh-gatefix-validation/coupled/budget_selection.json")
    parser.add_argument("--protocol", type=Path, default=ROOT / "configs/experiments/matched_v1.json")
    parser.add_argument("--coarse-data", type=Path, default=ROOT / "data/processed/coupled_wire_v1/dataset.npz")
    parser.add_argument("--coarse-scenario", type=Path, default=ROOT / "data/processed/coupled_wire_v1/scenario.json")
    parser.add_argument("--physics-gate", type=Path, default=ROOT / "outputs/runs/coupled_wire_v1/physics_gate.json")
    parser.add_argument("--fine161-scenario", type=Path, default=ROOT / "data/processed/coupled_wire_validation_fine161/scenario.json")
    parser.add_argument("--fine161-dir", type=Path, default=ROOT / "data/processed/coupled_wire_validation_fine161")
    parser.add_argument("--fine201-scenario", type=Path, required=True)
    parser.add_argument("--fine201-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/audits/v2-20261106/c1_spatial_validation_mesh201_stress.json")
    args = parser.parse_args()
    result = run(args)
    print(json.dumps({"status": result["status"], "n_actions": result["summary"]["n_actions"], "summary": result["summary"]["overall"]["161_to_201"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
