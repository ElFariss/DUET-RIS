"""Data preview figures: geometry of one frame, user trajectories per split, and one impedance matrix.

Usage: python3 scripts/plot_data_preview.py <train_v2_dir> <out_dir>
Reads scenario.json files (positions only) and one frame NPZ from training and test sets. Computes no rates.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
train_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
sets = {
    "train_v2 (fit M1)": (train_dir / "scenario.json", "#2a78c2"),
    "dev_v1 (design)": (ROOT / "data/processed/coupled_wire_dev_v1/scenario.json", "#2f9e44"),
    "test_v2 (Paper 1 test)": (ROOT / "data/processed/coupled_wire_test_v2/scenario.json", "#d9480f"),
}
rows = {name: json.loads(p.read_text())["rows"] for name, (p, _) in sets.items()}

frame = np.load(ROOT / "data/processed/coupled_wire_test_v2/frame_0000.npz")
c, z = frame["centers"], frame["z"]
ris, bs, ue = c[:64], c[64:68], c[68:70]

# 1. Geometry of one frame
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
ax[0].scatter(ris[:, 1] * 100, ris[:, 2] * 100, s=40, marker="|", c="#555", label="64 RIS wires (z-directed)")
ax[0].set(xlabel="y (cm)", ylabel="z (cm)", title="RIS face (8×8, 28×30 mm pitch)")
ax[0].set_aspect("equal"); ax[0].legend(loc="upper right", fontsize=8)
ax[1].scatter(ris[:, 0], ris[:, 1], s=8, c="#555", label="RIS")
ax[1].scatter(bs[:, 0], bs[:, 1], s=60, marker="^", c="#7048e8", label="4 BS antennas")
ax[1].scatter(ue[:, 0], ue[:, 1], s=60, marker="o", c="#d9480f", label="2 users (this frame)")
ax[1].set(xlabel="x (m)", ylabel="y (m)", title="Top view of test_v2 frame 0")
ax[1].set_aspect("equal"); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(out / "1_geometry.png", dpi=130); plt.close(fig)

# 2. User trajectories per split (top view and height)
fig, ax = plt.subplots(1, 3, figsize=(16, 5), sharex=True, sharey=True)
for a, (name, rs) in zip(ax, rows.items()):
    col = sets[name][1]
    trajs = sorted({r["trajectory"] for r in rs})
    for t in trajs:
        pts = np.array([r["users_m"] for r in rs if r["trajectory"] == t])  # steps × users × xyz
        for u, ls in ((0, "-"), (1, "--")):
            a.plot(pts[:, u, 0], pts[:, u, 1], ls, c=col, lw=1, alpha=.7)
            a.plot(pts[0, u, 0], pts[0, u, 1], "o", c=col, ms=2.5)
    a.scatter(ris[:, 0], ris[:, 1], s=4, c="#555")
    a.scatter(bs[:, 0], bs[:, 1], s=40, marker="^", c="#7048e8")
    a.set(title=f"{name}: {len(trajs)} trajectories, {len(rs)} frames", xlabel="x (m)")
    a.set_aspect("equal")
ax[0].set_ylabel("y (m)")
fig.suptitle("User paths (solid = user 1, dashed = user 2; dot = start; 16 steps of 20 ms). RIS grey, BS purple.")
fig.tight_layout(); fig.savefig(out / "2_trajectories.png", dpi=130); plt.close(fig)

# 3. Impedance matrix of one frame
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
im = ax[0].imshow(np.log10(np.abs(z)), cmap="viridis")
for b in (64, 68):
    ax[0].axhline(b - .5, c="w", lw=.8); ax[0].axvline(b - .5, c="w", lw=.8)
ax[0].set(title="log10 |Z| (Ω), test_v2 frame 0: RIS 0-63, BS 64-67, UE 68-69")
fig.colorbar(im, ax=ax[0], shrink=.8)
d = np.hypot(*(ris[:, None, 1:] - ris[None, :, 1:]).transpose(2, 0, 1)).ravel()
m = np.abs(z[:64, :64]).ravel()
off = d > 0
ax[1].scatter(d[off] * 100, m[off], s=3, alpha=.4)
ax[1].set(xscale="log", yscale="log", xlabel="distance between RIS wires (cm)", ylabel="|Z_ij| (Ω)",
          title="RIS mutual coupling falls with distance")
fig.tight_layout(); fig.savefig(out / "3_impedance.png", dpi=130); plt.close(fig)

summary = {name: {"trajectories": len({r["trajectory"] for r in rs}), "frames": len(rs),
                  "x_range_m": [min(u[0] for r in rs for u in r["users_m"]), max(u[0] for r in rs for u in r["users_m"])],
                  "y_range_m": [min(u[1] for r in rs for u in r["users_m"]), max(u[1] for r in rs for u in r["users_m"])],
                  "z_range_m": [min(u[2] for r in rs for u in r["users_m"]), max(u[2] for r in rs for u in r["users_m"])]}
           for name, rs in rows.items()}
print(json.dumps(summary, indent=1))
