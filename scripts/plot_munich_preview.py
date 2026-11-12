"""Munich (Sionna RT -> DeepMIMO export) preview: scene geometry, which BS-to-user links have LOS, and how strong the
RIS path is compared with the direct path. Reads the DeepMIMO export and the processed scenario; computes no rates.

Usage: python3 scripts/plot_munich_preview.py <out_dir>
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
D = ROOT / "data/raw/deepmimo_scenarios/munich_specular_v3_bs_fullpaths"
verts = np.load(D / "vertices.npz")["vertices"]
objects = json.loads((D / "objects.json").read_text())
layout = json.loads((ROOT / "data/raw/acquisition/munich_specular_v3/layout.json").read_text())
sc = np.load(ROOT / "data/processed/munich_specular_v3/scenario.npz")
inter = np.load(D / "inter_t000_tx000_r001.npz")["inter"]          # rx x paths; 0 = LOS, 1/11/111 = reflections
rx = np.load(D / "rx_pos_t000_tx000_r001.npz")["rx_pos"]
bs, ris = np.array(layout["bs"]), np.array(layout["cells"])

# Footprints: the lowest face of each building object, projected to x-y.
polys = []
for o in objects:
    if o.get("label") != "buildings":
        continue
    faces = [np.asarray(f) for f in o["face_vertex_idxs"]]
    f = min(faces, key=lambda f: verts[f, 2].mean())
    if len(f) >= 3:
        polys.append(verts[f, :2])

users = rx[64:]
user_inter = inter[64:]
has_any = ~np.isnan(user_inter).all(1)
has_los = (user_inter == 0).any(1)
cls = np.where(has_los, "LOS", np.where(has_any, "NLOS (reflections only)", "no path"))

fig, ax = plt.subplots(1, 2, figsize=(15, 7))
for a, (xl, yl, title) in zip(ax, [((-260, 140), (-120, 200), "Munich scene, top view"),
                                    ((20, 110), (-25, 65), "Around the RIS")]):
    a.add_collection(PolyCollection(polys, facecolor="#ced4da", edgecolor="#868e96", lw=.3))
    for name, col in (("LOS", "#2f9e44"), ("NLOS (reflections only)", "#e8590c"), ("no path", "#adb5bd")):
        m = cls == name
        a.scatter(users[m, 0], users[m, 1], s=9, c=col, label=f"user position, BS link {name} ({m.sum()})")
    a.scatter(bs[:, 0], bs[:, 1], s=70, marker="^", c="#7048e8", label="BS (4 antennas, 105 m high)")
    a.scatter(ris[:, 0], ris[:, 1], s=25, marker="s", c="#1971c2", label="RIS (64 cells, 3 m high)")
    a.set(xlim=xl, ylim=yl, xlabel="x (m)", ylabel="y (m)", title=title)
    a.set_aspect("equal")
ax[0].legend(fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(out / "4_munich_scene.png", dpi=130); plt.close(fig)

# Direct vs RIS-path strength per processed user frame (BS antenna sum; ideal coherent RIS phase as an upper bound).
G, H, Dd = sc["G"], sc["H"], sc["D"]
p_direct = (np.abs(Dd) ** 2).sum(-1)                                   # frames x users
p_ris_coherent = (np.abs(H) @ np.abs(G)).__pow__(2).sum(-1)            # sum over BS antennas of (sum_n |h||g|)^2
no_direct = p_direct == 0
ratio_db = 10 * np.log10(p_ris_coherent[~no_direct] / p_direct[~no_direct])
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(ratio_db, bins=40, color="#1971c2")
ax.axvline(0, c="k", lw=.8)
ax.set(xlabel="best-case RIS path power / direct path power (dB)", ylabel="user frames",
       title=f"Munich: {no_direct.sum()} of {no_direct.size} user frames have no direct path at all\n"
             f"(not shown); of the rest, RIS path stronger in {(ratio_db > 0).mean():.0%}")
fig.tight_layout(); fig.savefig(out / "5_munich_ris_vs_direct.png", dpi=130); plt.close(fig)

print(json.dumps({"user_positions": int(len(users)), "LOS": int(has_los.sum()), "NLOS_reflections_only":
                  int((has_any & ~has_los).sum()), "no_path": int((~has_any).sum()),
                  "user_frames": int(no_direct.size), "user_frames_without_direct_path": int(no_direct.sum()),
                  "ris_vs_direct_db_median_where_direct_exists": float(np.median(ratio_db)), "ris_stronger_fraction": float((ratio_db > 0).mean()),
                  "bs_to_ris_distance_m": float(np.linalg.norm(bs.mean(0) - ris.mean(0))),
                  "ris_to_user_distance_m_range": [float(np.linalg.norm(sc["positions"] - ris.mean(0), axis=-1).min()),
                                                   float(np.linalg.norm(sc["positions"] - ris.mean(0), axis=-1).max())]}, indent=1))
