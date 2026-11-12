#!/usr/bin/env python3
"""Export one registered coupled-RIS geometry snapshot as an Xnec2c NEC deck.

This deck is for visual inspection and a single driven snapshot. It is not a
full multiport extraction and is not claimed numerically identical to PyNEC.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DATA = ROOT / "data/processed/coupled_wire_dev_v1"
DEFAULT_GATE = ROOT / "outputs/runs/coupled_wire_v1/physics_gate.json"
DEFAULT_OUTPUT = ROOT / "outputs/geometry/nec_view/frame_0109_alloff_161.nec"
FRAME_COUNT = 480


def load_inputs(data_dir: Path, gate_path: Path, frame: int, segments: int):
    if data_dir.resolve() != DEFAULT_DATA.resolve():
        raise ValueError(f"data path must be the canonical registered DEV root: {DEFAULT_DATA}")
    if not 0 <= frame < FRAME_COUNT:
        raise ValueError(f"frame must be in registered DEV range [0,{FRAME_COUNT - 1}]")
    if segments < 3 or segments % 2 != 1:
        raise ValueError("segments must be an odd integer >= 3")
    sidecar = json.loads((data_dir / f"frame_{frame:04d}.json").read_text())
    scenario = json.loads((data_dir / "scenario.json").read_text())
    if sidecar.get("split") != "dev" or scenario.get("split_label") != "dev":
        raise ValueError("only a registered development frame can be exported")
    if sidecar.get("index") != frame or sidecar.get("segments_per_wire") != 81:
        raise ValueError("source frame identity/mesh does not match registered DEV data")
    if scenario.get("seed") != 20261107 or scenario.get("trajectories") != 30:
        raise ValueError("scenario is not the registered DEV seed/trajectory set")
    rows = scenario.get("rows", [])
    if len(rows) != FRAME_COUNT or rows[frame].get("index") != frame:
        raise ValueError("scenario does not contain the registered 480-frame index table")
    row = rows[frame]
    for key in ("trajectory", "step", "split", "users_m"):
        if sidecar.get(key) != row.get(key):
            raise ValueError(f"frame sidecar {key} differs from the registered scenario row")
    npz_path = data_dir / f"frame_{frame:04d}.npz"
    npz_digest = hashlib.sha256(npz_path.read_bytes()).hexdigest()
    if sidecar.get("sha256") != npz_digest:
        raise ValueError("frame sidecar SHA-256 does not match the registered NPZ bytes")
    arrays = np.load(npz_path)
    centers = np.asarray(arrays["centers"], dtype=float)
    lengths = np.asarray(arrays["lengths"], dtype=float)
    if centers.shape != (70, 3) or lengths.shape != (70,):
        raise ValueError(f"expected 70 registered wires; got {centers.shape}, {lengths.shape}")
    if not np.all(np.isfinite(centers)) or not np.all(np.isfinite(lengths)):
        raise ValueError("wire geometry contains non-finite values")
    if not np.allclose(lengths, 0.024, rtol=0, atol=1e-12):
        raise ValueError("wire lengths differ from the registered 24 mm model")
    radius = float(sidecar["radius_m"])
    frequency = float(sidecar["frequency_hz"])
    if not np.isclose(radius, 50e-6, rtol=0, atol=1e-12):
        raise ValueError("wire radius differs from the registered 50 um model")
    if not np.isclose(frequency, 5.53e9, rtol=0, atol=1):
        raise ValueError("frequency differs from the registered 5.53 GHz model")
    gate = json.loads(gate_path.read_text())
    if not gate.get("passed"):
        raise ValueError("physics gate is not marked passed")
    loads = np.asarray(gate["loads_real_ohm"], dtype=float) + 1j * np.asarray(
        gate["loads_imag_ohm"], dtype=float
    )
    if loads.shape != (2,) or not np.all(np.isfinite(loads)):
        raise ValueError("expected the registered two-state RIS load table")
    return centers, lengths, radius, frequency, loads, sidecar, scenario


def render_deck(centers, lengths, radius, frequency, loads, segments, bits, frame):
    """Return a NEC-2 deck using source code's port/wire ordering."""
    if segments < 3 or segments % 2 != 1:
        raise ValueError("segments must be an odd integer >= 3")
    if len(centers) != 70 or len(lengths) != 70 or len(loads) != 2:
        raise ValueError("deck expects 64 RIS, four BS, two UE wires, and two states")
    bits = np.asarray(bits, dtype=np.int8)
    if bits.shape != (64,) or not np.isin(bits, [0, 1]).all():
        raise ValueError("bits must contain exactly 64 binary RIS states")
    mid = segments // 2 + 1  # NEC segment numbers are one-based.
    lines = [
        f"CM Atom-wise RIS DEV frame {frame}; Xnec2c inspection snapshot",
        "CM 64 RIS wires, 4 BS wires, 2 UE wires; one BS gap source only",
        "CM Free-space PEC thin-wire model. Not a calibrated RIS or full multiport run.",
        "CE",
    ]
    for tag, (center, length) in enumerate(zip(centers, lengths), start=1):
        x, y, z = map(float, center)
        half = float(length) / 2
        lines.append(
            f"GW {tag:3d} {segments:3d} {x:.15g} {y:.15g} {z-half:.15g} "
            f"{x:.15g} {y:.15g} {z+half:.15g} {radius:.15g}"
        )
    lines.extend(["GE 0", "EK 0", f"FR 0 1 {frequency / 1e6:.15g} 0 0 0"])
    for i, state in enumerate(bits):
        load = loads[int(state)]
        lines.append(
            f"LD 4 {i+1:3d} {mid:3d} {mid:3d} {load.real:.15g} {load.imag:.15g} 0"
        )
    # The network evaluator terminates all six non-RIS ports in 50 ohms.
    # This driven view uses the same port loads, with a voltage-gap source at BS 1.
    for tag in range(65, 71):
        lines.append(f"LD 4 {tag:3d} {mid:3d} {mid:3d} 50 0 0")
    lines.extend([f"EX 0 65 {mid} 0 1 0 0 0 0 0", "XQ", "EN"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--physics-gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--frame", type=int, default=109)
    parser.add_argument("--segments", type=int, default=161)
    parser.add_argument("--bits", default="0" * 64,
                        help="64-character string; 0/1 map to the registered load-state index")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    centers, lengths, radius, frequency, loads, sidecar, scenario = load_inputs(
        args.data, args.physics_gate, args.frame, args.segments
    )
    if len(args.bits) != 64 or set(args.bits) - {"0", "1"}:
        parser.error("--bits must be exactly 64 characters of 0 or 1")
    bits = np.fromiter((int(c) for c in args.bits), dtype=np.int8)
    deck = render_deck(centers, lengths, radius, frequency, loads, args.segments, bits, args.frame)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(deck)
    metadata = {
        "artifact": args.output.name,
        "purpose": "Xnec2c geometry and single-source inspection snapshot",
        "frame": args.frame,
        "split": "dev",
        "trajectory": sidecar["trajectory"],
        "step": sidecar["step"],
        "scenario_seed": scenario["seed"],
        "segments_per_wire": args.segments,
        "wire_count": 70,
        "ris_bits": args.bits,
        "bit_mapping": {"0": "all-OFF registered load state 0", "1": "all-ON registered load state 1"},
        "load_states_ohm": [[float(v.real), float(v.imag)] for v in loads],
        "frequency_hz": frequency,
        "wire_radius_m": radius,
        "source": {"tag": 65, "segment": args.segments // 2 + 1, "voltage_v": [1, 0]},
        "matched_50ohm_loads_on_tags": list(range(65, 71)),
        "source_geometry_npz": str(args.data / f"frame_{args.frame:04d}.npz"),
        "source_sidecar": str(args.data / f"frame_{args.frame:04d}.json"),
        "input_sha256": {
            "frame_npz": hashlib.sha256((args.data / f"frame_{args.frame:04d}.npz").read_bytes()).hexdigest(),
            "frame_sidecar": hashlib.sha256((args.data / f"frame_{args.frame:04d}.json").read_bytes()).hexdigest(),
            "scenario": hashlib.sha256((args.data / "scenario.json").read_bytes()).hexdigest(),
            "physics_gate": hashlib.sha256(args.physics_gate.read_bytes()).hexdigest(),
        },
        "limitations": [
            "One single-excitation NEC snapshot, not a 70-port impedance-matrix extraction.",
            "Not demonstrated numerically equal to the PyNEC multi-excitation evaluator.",
            "Free-space PEC thin wires; excludes RIS substrate, diode package, conductors, and radiation calibration.",
            "Mesh segmentation is set to the requested view mesh and is not a convergence claim.",
        ],
    }
    metadata["deck_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    meta_path = args.output.with_suffix(".json")
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"wrote {args.output}")
    print(f"wrote {meta_path}")


if __name__ == "__main__":
    main()
