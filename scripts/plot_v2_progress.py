#!/usr/bin/env python3
"""Plot an actual coupled-wire V2 development frame; never loads test outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data/processed/coupled_wire_dev_v1"
DEFAULT_OUT = ROOT / "outputs/figures/v2-20261106"
C1_AUDIT = ROOT / "outputs/audits/v2-20261106/c1_spatial_validation_mesh161.attempt2.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--frame", type=int, default=109,
                        help="zero-based frame index from coupled_wire_dev_v1 only")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if args.data.resolve() != DEFAULT_DATA.resolve():
        raise SystemExit("This progress figure is restricted to the registered V2 development set.")
    npz_path = args.data / f"frame_{args.frame:04d}.npz"
    row_path = args.data / f"frame_{args.frame:04d}.json"
    scenario_path = args.data / "scenario.json"
    if not all(p.is_file() for p in (npz_path, row_path, scenario_path)):
        raise SystemExit(f"Missing development-frame input for frame {args.frame}.")

    frame = json.loads(row_path.read_text())
    scenario = json.loads(scenario_path.read_text())
    if frame.get("split") != "dev" or scenario.get("split_label") != "dev":
        raise SystemExit("Refusing to plot a frame not explicitly marked development.")
    data = np.load(npz_path)
    centers = np.asarray(data["centers"], dtype=float)
    if centers.shape != (70, 3) or not np.isfinite(centers).all():
        raise SystemExit(f"Unexpected or invalid port-center array: {centers.shape}")
    users = np.asarray(frame["users_m"], dtype=float)
    if users.shape != (2, 3) or not np.isfinite(users).all():
        raise SystemExit(f"Unexpected or invalid user coordinates: {users.shape}")

    ris = centers[:64]
    bs = centers[64:68]
    length = float(scenario["wire_length_m"])
    fig = plt.figure(figsize=(8.4, 6.4), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")
    # The coordinates are the actual NEC center-port coordinates from this dev frame.
    for x, y, z in ris:
        ax.plot([x, x], [y, y], [z - length / 2, z + length / 2],
                color="#2563eb", linewidth=1.25, alpha=0.78)
    ax.scatter(*bs.T, marker="^", s=58, color="#dc2626", label="4 BS antenna ports")
    ax.scatter(*users.T, marker="o", s=54, color=["#15803d", "#9333ea"],
               edgecolor="white", linewidth=0.6, label="2 UE antenna ports")
    for i, p in enumerate(users, start=1):
        ax.text(*p, f" UE{i}", fontsize=8, color="#202020")
    ax.set_xlabel("x (m)", labelpad=8)
    ax.set_ylabel("y (m)", labelpad=8)
    ax.set_zlabel("z (m)", labelpad=7)
    ax.set_title(f"Coupled-wire development scene · frame {args.frame:04d}\n"
                 f"Trajectory {frame['trajectory']}, step {frame['step']} · physical port geometry")
    ax.view_init(elev=22, azim=-54)
    ax.set_box_aspect((1.0, 1.2, 0.8))
    ax.legend(loc="upper left", frameon=True, fontsize=8)
    ax.text2D(0.02, 0.02,
              f"NEC thin-wire discretization context: 81 segments/wire (coarse) · "
              f"161 segments/wire (fine audit). Center geometry shown; mesh elements not to scale.",
              transform=ax.transAxes, fontsize=8, color="#334155")

    args.out.mkdir(parents=True, exist_ok=True)
    png_path = args.out / f"dev_frame_{args.frame:04d}_geometry.png"
    pdf_path = args.out / f"dev_frame_{args.frame:04d}_geometry.pdf"
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)

    # C1 summary visualization: each method mean is accompanied by its three
    # trajectory means. The right panel keeps the three trajectory-level
    # within-trajectory rank associations separate; no action-level CI is used.
    if not C1_AUDIT.is_file():
        raise SystemExit(f"Missing completed C1 audit input: {C1_AUDIT}")
    audit = json.loads(C1_AUDIT.read_text())
    stats = audit["summary"]["methods"]
    clusters = [str(x) for x in audit["summary"]["trajectory_clusters"]]
    order = [
        "random", "population_ga", "greedy", "uniform_ga",
        "analytical_no_memory_ga", "attention_no_memory_ga",
        "attention_no_physics_ga", "memory_ga", "analytical_ga",
        "mlp_ga", "attention_ga", "pair",
    ]
    colors = {clusters[0]: "#2563eb", clusters[1]: "#d97706", clusters[2]: "#15803d"}
    fig2, (ax_shift, ax_corr) = plt.subplots(1, 2, figsize=(13.5, 8.0), sharey=True)
    y = np.arange(len(order))
    jitter = np.linspace(-0.17, 0.17, len(clusters))
    for i, method in enumerate(order):
        item = stats[method]
        per_traj = item["trajectory_mean_delta_fixed_w_bpshz"]
        for j, traj in enumerate(clusters):
            ax_shift.scatter(per_traj[traj], y[i] + jitter[j], s=24,
                             color=colors[traj], alpha=0.9,
                             label=f"Trajectory {traj}" if i == 0 else None,
                             zorder=3)
        ax_shift.scatter(item["mean_delta_fixed_w_bpshz"], y[i], marker="D",
                         s=45, color="#111827", label="Mean across actions" if i == 0 else None,
                         zorder=4)
        correlations = item["spearman_on_count_vs_delta_fixed_w_by_trajectory"]
        for j, traj in enumerate(clusters):
            value = correlations.get(traj)
            if value is not None:
                ax_corr.scatter(value, y[i] + jitter[j], s=24,
                                color=colors[traj], zorder=3)

    ax_shift.axvline(0, color="#64748b", linewidth=0.9, linestyle="--")
    ax_shift.set_yticks(y, order)
    ax_shift.invert_yaxis()
    ax_shift.set_xlabel("Mean fine − coarse rate change (bit/s/Hz)\n"
                        "81 vs 161 segments/wire; fixed 81-mesh precoder")
    ax_shift.set_title("Returned-action score shifts")
    ax_shift.grid(axis="x", color="#cbd5e1", linewidth=0.6, alpha=0.7)
    ax_corr.axvline(0, color="#64748b", linewidth=0.9, linestyle="--")
    ax_corr.set_xlim(-1.05, 1.05)
    ax_corr.set_xlabel("Within-trajectory Spearman correlation\nON-bit count vs rate change")
    ax_corr.set_title("ON-count association by trajectory")
    ax_corr.grid(axis="x", color="#cbd5e1", linewidth=0.6, alpha=0.7)
    fig2.suptitle(
        "C1 mesh sensitivity · validation only · 5,760 actions nested in 3 trajectories\n"
        "|Δ| max 3.163 bit/s/Hz · 95th percentile 0.670 · 5,450 exceed 0.015 · "
        "14.15% non-tied pairwise rank reversals",
        fontsize=12,
    )
    handles, labels = ax_shift.get_legend_handles_labels()
    fig2.legend(handles, labels, loc="lower center", ncol=4, frameon=False,
                bbox_to_anchor=(0.5, 0.025))
    fig2.text(0.5, 0.005,
              "Points on the left are the three trajectory means and the overall action mean; "
              "right-panel correlations are descriptive. Independent n = 3 trajectories, not 5,760 actions.",
              ha="center", va="bottom", fontsize=8, color="#334155")
    fig2.tight_layout(rect=(0, 0.095, 1, 0.92))
    c1_png = args.out / "c1_mesh_sensitivity_81_vs_161.png"
    c1_pdf = args.out / "c1_mesh_sensitivity_81_vs_161.pdf"
    fig2.savefig(c1_png, dpi=220, bbox_inches="tight")
    fig2.savefig(c1_pdf, bbox_inches="tight")
    plt.close(fig2)

    manifest = {
        "status": "development-frame geometry visualization; not a channel or performance result",
        "split": "dev",
        "frame_index": args.frame,
        "trajectory": frame["trajectory"],
        "step": frame["step"],
        "input_sha256": {
            npz_path.name: sha256(npz_path),
            row_path.name: sha256(row_path),
            scenario_path.name: sha256(scenario_path),
        },
        "output_sha256": {
            png_path.name: sha256(png_path),
            pdf_path.name: sha256(pdf_path),
        },
        "mesh_context": "81 segments/wire coarse; 161 segments/wire fine audit; plotted centerline geometry is the same physical layout",
        "c1_audit": {
            "path": str(C1_AUDIT.relative_to(ROOT)),
            "sha256": sha256(C1_AUDIT),
            "png_sha256": sha256(c1_png),
            "pdf_sha256": sha256(c1_pdf),
            "status": "descriptive validation sensitivity; 3 independent trajectory clusters; not a convergence result",
        },
    }
    manifest_path = args.out / f"dev_frame_{args.frame:04d}_geometry.provenance.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
