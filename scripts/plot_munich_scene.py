#!/usr/bin/env python3
"""Render the verified local Munich scene mesh and original specular trajectories.

The output is a geometry/context illustration for the independent-cell specular
track. It contains no ray paths, NEC-coupled results, or hybrid-control claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
ACQ = ROOT / "data/raw/acquisition/munich_specular_v3"
EXPORT = ROOT / "data/raw/deepmimo_scenarios/munich_specular_v3_ris_16_fullpaths"
DEFAULT_OUT = ROOT / "paper/manuscript/figures"
SPLIT_COLORS = {"train": "#31688e", "validation": "#d9822b", "pilot": "#3b8d62"}
SCENE_COLOR = "#b8c3cf"
TERRAIN_COLOR = "#e4e8ec"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_inputs():
    scenario_path = ACQ / "scenario.json"
    layout_path = ACQ / "layout.json"
    objects_path = EXPORT / "objects.json"
    vertices_path = EXPORT / "vertices.npz"
    params_path = EXPORT / "params.json"
    for p in (scenario_path, layout_path, objects_path, vertices_path, params_path):
        if not p.is_file():
            raise FileNotFoundError(f"Required local verified scene export is missing: {p}")
    scenario = json.loads(scenario_path.read_text())
    layout = json.loads(layout_path.read_text())
    objects = json.loads(objects_path.read_text())
    params = json.loads(params_path.read_text())
    with np.load(vertices_path, allow_pickle=False) as data:
        vertices = np.asarray(data["vertices"], dtype=float)
    users = np.asarray(layout["users"], dtype=float)
    trajectory = np.asarray(layout["trajectory"], dtype=int)
    splits = np.asarray(layout["split"], dtype=str)
    if users.shape != (96, 2, 3) or trajectory.shape != (96,) or splits.shape != (96,):
        raise ValueError("Original specular layout must contain 24 trajectories x 4 steps x 2 users")
    if len(set(trajectory.tolist())) != 24:
        raise ValueError("Unexpected source trajectory count")
    if not (layout.get("chosen_before_channels") is True
            and scenario.get("untouched_final_test_generated") is False):
        raise ValueError("Source metadata does not match the declared original independent-cell split")
    if scenario.get("source") != "Sionna built-in Munich, newly ray traced, DeepMIMO export":
        raise ValueError("Unexpected scene source metadata")
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("Scene vertex export has an unexpected shape")
    if not objects or any(o.get("label") not in {"buildings", "terrain"} for o in objects):
        raise ValueError("Scene object export has unexpected geometry labels")
    if max((max(face) for obj in objects for face in obj.get("face_vertex_idxs", []) if face), default=-1) >= len(vertices):
        raise ValueError("Scene object references a vertex outside vertices.npz")
    return scenario, layout, objects, vertices, params


def object_bounds(vertices: np.ndarray, obj: dict):
    ids = sorted({int(i) for face in obj.get("face_vertex_idxs", []) if len(face) >= 3 for i in face})
    if not ids:
        return None, None, []
    pts = vertices[ids]
    return pts.min(axis=0), pts.max(axis=0), ids


def clip_face(face: np.ndarray, bounds: tuple[float, ...]) -> np.ndarray:
    """Clip a source polygon to the displayed box, preventing giant off-view faces from bleeding in."""
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    polygon = [np.asarray(p, dtype=float) for p in face]
    planes = ((0, xmin, True), (0, xmax, False), (1, ymin, True),
              (1, ymax, False), (2, zmin, True), (2, zmax, False))
    for axis, edge, keep_greater in planes:
        if not polygon:
            break
        output = []
        prev = polygon[-1]
        prev_inside = prev[axis] >= edge if keep_greater else prev[axis] <= edge
        for curr in polygon:
            curr_inside = curr[axis] >= edge if keep_greater else curr[axis] <= edge
            if curr_inside != prev_inside:
                denom = curr[axis] - prev[axis]
                if abs(denom) > 1e-12:
                    fraction = (edge - prev[axis]) / denom
                    output.append(prev + fraction * (curr - prev))
            if curr_inside:
                output.append(curr)
            prev, prev_inside = curr, curr_inside
        polygon = output
    return np.asarray(polygon, dtype=float)


def mesh_faces(objects: list[dict], vertices: np.ndarray, bounds: tuple[float, ...]):
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    building_faces, terrain_faces = [], []
    shown_objects = {"buildings": 0, "terrain": 0}
    face_counts = {"buildings": 0, "terrain": 0}
    for obj in objects:
        lo, hi, _ = object_bounds(vertices, obj)
        if lo is None or not (hi[0] >= xmin and lo[0] <= xmax and hi[1] >= ymin and lo[1] <= ymax
                              and hi[2] >= zmin and lo[2] <= zmax):
            continue
        cls = obj["label"]
        target = terrain_faces if cls == "terrain" else building_faces
        obj_face_count = 0
        for face in obj.get("face_vertex_idxs", []):
            if len(face) < 3:
                continue
            pts = vertices[np.asarray(face, dtype=int)]
            lo_face, hi_face = pts.min(axis=0), pts.max(axis=0)
            if not (hi_face[0] >= xmin and lo_face[0] <= xmax and hi_face[1] >= ymin
                    and lo_face[1] <= ymax and hi_face[2] >= zmin and lo_face[2] <= zmax):
                continue
            clipped = clip_face(pts, bounds)
            if len(clipped) < 3:
                continue
            target.append(clipped)
            obj_face_count += 1
        if obj_face_count:
            shown_objects[cls] += 1
            face_counts[cls] += obj_face_count
    return building_faces, terrain_faces, shown_objects, face_counts


def draw_mesh(ax, objects, vertices, bounds, alpha=0.12):
    buildings, terrain, shown, faces = mesh_faces(objects, vertices, bounds)
    if terrain:
        ax.add_collection3d(Poly3DCollection(terrain, facecolors=TERRAIN_COLOR,
                            edgecolors="none", alpha=0.10, zsort="average", zorder=0))
    if buildings:
        ax.add_collection3d(Poly3DCollection(buildings, facecolors=SCENE_COLOR,
                            edgecolors="#82909d", linewidths=0.10, alpha=alpha, zsort="average", zorder=0))
    return shown, faces


def draw_sites(ax, layout, label=True, s=35):
    bs = np.asarray(layout["bs"], dtype=float)
    cells = np.asarray(layout["cells"], dtype=float)
    center = np.asarray(layout["ris_center"], dtype=float)
    ax.scatter(bs[:, 0], bs[:, 1], bs[:, 2], marker="^", c="#1b2430", s=s,
               depthshade=False, edgecolors="white", linewidths=0.45, zorder=10)
    ax.scatter(cells[:, 0], cells[:, 1], cells[:, 2], marker="s", c="#e0a629", s=max(5, s * .25),
               depthshade=False, edgecolors="#5a4520", linewidths=0.25, zorder=11)
    if label:
        ax.text(*bs.mean(axis=0), "  BS", color="#18212a", fontsize=8, weight="bold")
        ax.text(*(center + np.array([2.0, 1.0, 2.2])), "RIS", color="#704c00", fontsize=8, weight="bold")


def draw_tracks(ax, layout, trajectory_filter=None, detail=False):
    users = np.asarray(layout["users"], dtype=float)
    track_ids = np.asarray(layout["trajectory"], dtype=int)
    splits = np.asarray(layout["split"], dtype=str)
    for tid in np.unique(track_ids):
        idx = np.flatnonzero(track_ids == tid)
        if trajectory_filter is not None and not trajectory_filter(idx):
            continue
        # Source rows are recorded in temporal order. Assert instead of silently sorting.
        if len(idx) != 4:
            raise ValueError(f"Trajectory {tid} does not have four original samples")
        split = splits[idx[0]]
        if any(splits[idx] != split):
            raise ValueError(f"Trajectory {tid} crosses split labels")
        color = SPLIT_COLORS.get(split)
        if color is None:
            raise ValueError(f"Unknown source split {split}")
        for user_id, marker in ((0, "o"), (1, "D")):
            pts = users[idx, user_id]
            ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=color,
                    linewidth=1.05 if detail else 0.65, alpha=0.92 if detail else 0.68,
                    solid_capstyle="round", zorder=6)
            ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], color=color, marker=marker,
                       s=13 if detail else 6.5, alpha=0.95, depthshade=False,
                       edgecolors="white", linewidths=0.22, zorder=7)


def draw_track_plan(ax, layout):
    users = np.asarray(layout["users"], dtype=float)
    track_ids = np.asarray(layout["trajectory"], dtype=int)
    splits = np.asarray(layout["split"], dtype=str)
    for tid in np.unique(track_ids):
        idx = np.flatnonzero(track_ids == tid)
        split = splits[idx[0]]
        color = SPLIT_COLORS[split]
        for user_id, marker in ((0, "o"), (1, "D")):
            pts = users[idx, user_id]
            ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=1.0, alpha=0.8, zorder=3)
            ax.scatter(pts[:, 0], pts[:, 1], color=color, marker=marker, s=16,
                       edgecolors="white", linewidths=0.25, zorder=4)


def draw_plan_footprints(ax, objects, vertices, bounds):
    """Show only actual horizontal bottom faces from the exported hull geometry."""
    xmin, xmax, ymin, ymax = bounds
    shown = 0
    for obj in objects:
        if obj.get("label") != "buildings":
            continue
        ids = {int(i) for face in obj.get("face_vertex_idxs", []) if len(face) >= 3 for i in face}
        if not ids:
            continue
        object_zmin = float(vertices[list(ids), 2].min())
        for face in obj.get("face_vertex_idxs", []):
            if len(face) < 3:
                continue
            pts = vertices[np.asarray(face, dtype=int)]
            if np.ptp(pts[:, 2]) > 1e-3 or abs(float(pts[:, 2].mean()) - object_zmin) > 1e-2:
                continue
            xy = pts[:, :2]
            if not (xy[:, 0].max() >= xmin and xy[:, 0].min() <= xmax
                    and xy[:, 1].max() >= ymin and xy[:, 1].min() <= ymax):
                continue
            clipped = clip_face(np.column_stack((xy, np.zeros(len(xy)))),
                                (xmin, xmax, ymin, ymax, -1.0, 1.0))[:, :2]
            if len(clipped) >= 3:
                closed = np.vstack([clipped, clipped[0]])
                ax.plot(closed[:, 0], closed[:, 1], color="#99a5b0", linewidth=0.42,
                        alpha=0.55, zorder=1)
                shown += 1
    return shown


def set_axes(ax, bounds, elev=24, azim=-55, zoom=False):
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_zlim(zmin, zmax)
    ax.set_box_aspect((xmax - xmin, ymax - ymin, zmax - zmin))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("x (m)", labelpad=3, fontsize=8)
    ax.set_ylabel("y (m)", labelpad=3, fontsize=8)
    ax.set_zlabel("z (m)", labelpad=2, fontsize=8)
    ax.tick_params(labelsize=7, pad=1)
    ax.grid(color="#d9dee3", linewidth=0.35, alpha=0.55)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
        axis.pane.set_edgecolor("#dce1e6")


def render(out_dir: Path):
    scenario, layout, objects, vertices, params = load_inputs()
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path, png_path, provenance_path = (out_dir / "munich_scene.pdf",
                                            out_dir / "munich_scene.png",
                                            out_dir / "munich_scene.json")
    for path in (pdf_path, png_path, provenance_path):
        if path.exists():
            raise FileExistsError(f"Preserving existing figure artifact: {path}")

    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42,
                         "ps.fonttype": 42, "savefig.facecolor": "white"})
    fig = plt.figure(figsize=(10.7, 4.65), constrained_layout=False)
    ax_full = fig.add_axes([0.035, 0.17, 0.59, 0.73], projection="3d", computed_zorder=False)
    ax_detail = fig.add_axes([0.68, 0.21, 0.29, 0.63])
    full_bounds = (-235.0, 78.0, 5.0, 113.0, 0.0, 112.0)
    detail_bounds = (12.0, 76.0, 6.0, 53.0)

    full_counts, full_faces = draw_mesh(ax_full, objects, vertices, full_bounds, alpha=0.12)
    draw_tracks(ax_full, layout)
    draw_sites(ax_full, layout, label=True, s=33)
    set_axes(ax_full, full_bounds, elev=24, azim=-56)
    ax_full.set_title("(a) 3D scene overview", loc="left", fontsize=10, pad=1, weight="bold")

    detail_footprints = draw_plan_footprints(ax_detail, objects, vertices, detail_bounds)
    draw_track_plan(ax_detail, layout)
    cells = np.asarray(layout["cells"], dtype=float)
    center = np.asarray(layout["ris_center"], dtype=float)
    ax_detail.scatter(cells[:, 0], cells[:, 1], marker="s", c="#e0a629", s=12,
                      edgecolors="#5a4520", linewidths=0.25, zorder=5, label="RIS cells")
    ax_detail.scatter([center[0]], [center[1]], marker="+", c="#704c00", s=35,
                      linewidths=1.1, zorder=6)
    ax_detail.set_xlim(detail_bounds[0], detail_bounds[1])
    ax_detail.set_ylim(detail_bounds[2], detail_bounds[3])
    ax_detail.set_aspect("equal", adjustable="box")
    ax_detail.set_xlabel("x (m)", fontsize=8)
    ax_detail.set_ylabel("y (m)", fontsize=8)
    ax_detail.tick_params(labelsize=7)
    ax_detail.grid(color="#d9dee3", linewidth=0.4, alpha=0.7)
    ax_detail.set_title("(b) Top-down receiver-track detail", loc="left", fontsize=9, pad=7, weight="bold")
    ax_detail.text(center[0] + 1.0, center[1] + 1.0, "RIS", color="#704c00", fontsize=7, weight="bold")

    split_counts = {}
    trajectory_splits = {}
    tids = np.asarray(layout["trajectory"], dtype=int)
    split_array = np.asarray(layout["split"], dtype=str)
    for tid in np.unique(tids):
        vals = np.unique(split_array[tids == tid])
        if len(vals) != 1:
            raise ValueError(f"Trajectory {tid} has multiple split assignments")
        trajectory_splits[str(int(tid))] = str(vals[0])
        split_counts[str(vals[0])] = split_counts.get(str(vals[0]), 0) + 1
    legend = [
        Line2D([0], [0], color=SPLIT_COLORS[s], lw=2.0,
               label=f"{s.title()} trajectories (n={split_counts[s]})")
        for s in ("train", "validation", "pilot")
    ] + [
        Line2D([0], [0], marker="^", color="none", markerfacecolor="#1b2430",
               markeredgecolor="white", markersize=7, label="BS (4 antennas)"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#e0a629",
               markeredgecolor="#5a4520", markersize=6, label="RIS (64 cells)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#65717c",
               markeredgecolor="white", markersize=5.5, label="UE-1"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#65717c",
               markeredgecolor="white", markersize=5.0, label="UE-2"),
        Line2D([0], [0], color=SCENE_COLOR, lw=5, label="Exported scene hulls"),
        Line2D([0], [0], color="#99a5b0", lw=1, label="Exported ground-level boundary"),
    ]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.51, 0.047),
               ncol=4, frameon=False, fontsize=7.0, columnspacing=1.35, handlelength=1.8)
    fig.text(0.5, 0.012,
             "Independent-cell specular dataset. Scene geometry only; no ray paths, NEC-coupled results, or hybrid-control outcomes are shown.",
             ha="center", va="bottom", fontsize=7.1, color="#49545f")
    fig.savefig(pdf_path, dpi=300, bbox_inches="tight", pad_inches=0.06,
                metadata={"Title": "Munich scene and receiver trajectories",
                          "Creator": "scripts/plot_munich_scene.py",
                          "CreationDate": None, "ModDate": None})
    fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)

    source_files = [ACQ / "scenario.json", ACQ / "layout.json", ACQ / "all_exports_verified.json",
                    ACQ / "free_space_check.json", EXPORT / "objects.json", EXPORT / "vertices.npz",
                    EXPORT / "params.json", ROOT / "scripts/trace_munich.py", Path(__file__).resolve()]
    scene_mesh_hashes = scenario.get("scene_sha256", {})
    source_record = {
        "figure": "munich_scene",
        "title": "Munich scene and receiver trajectories for the independent-cell specular evaluation",
        "depiction_scope": {
            "source": "Sionna built-in Munich scene export generated for the registered DeepMIMO acquisition",
            "scene_geometry": "DeepMIMO-exported hull approximation in vertices.npz and objects.json, not the original full-resolution ray-tracing mesh or material-faithful render; the original source mesh hashes are carried from acquisition scenario.json",
            "trajectory_metadata": "original acquisition layout.json, selected before channel computation",
            "not_shown": ["ray paths", "NEC-coupled network outputs", "validated hybrid-control results"],
            "rendering_note": "neutral building tint is for legibility and does not encode source material properties",
            "footprint_note": "projected bottom faces from the exported hulls are visual boundaries only and do not classify a trajectory point as indoor or outdoor",
        },
        "versions": scenario.get("versions", {}),
        "deepmimo_export_scene": params.get("scene", {}),
        "frequency_hz": scenario.get("frequency_hz"),
        "ray_parameters": scenario.get("ray_parameters", {}),
        "source_mesh_sha256_count": len(scene_mesh_hashes),
        "source_mesh_sha256_manifest": scene_mesh_hashes,
        "source_mesh_manifest_sha256": hashlib.sha256(json.dumps(scene_mesh_hashes, sort_keys=True,
                                                                    separators=(",", ":")).encode()).hexdigest(),
        "layout_summary": {
            "bs_antennas": len(layout["bs"]), "ris_cells": len(layout["cells"]),
            "trajectories": len(trajectory_splits), "trajectory_counts_by_split": split_counts,
            "trajectory_split_by_id": trajectory_splits,
            "steps_per_trajectory": 4, "users_per_step": 2,
            "chosen_before_channels": layout.get("chosen_before_channels"),
            "split_labels_from_original_layout": True,
        },
        "mesh_summary": {
            "export_representation": params.get("scene", {}).get("representation"),
            "visual_representation_note": "DeepMIMO exported hull approximation, not original RT mesh",
            "vertices": int(len(vertices)), "objects": len(objects),
            "objects_by_source_label": {label: sum(o.get("label") == label for o in objects)
                                         for label in sorted({o.get("label") for o in objects})},
            "triangular_faces_from_export_params": params.get("scene", {}).get("n_triangular_faces"),
            "panel_a_bounds_m": list(full_bounds), "panel_b_xy_bounds_m": list(detail_bounds),
            "panel_a_visible_objects_by_label": full_counts, "panel_a_visible_polygon_faces_by_label": full_faces,
            "panel_b_ground_level_boundaries_drawn": detail_footprints,
        },
        "inputs_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in source_files},
        "render": {"matplotlib": matplotlib.__version__,
                   "panel_projection": {"panel_a": "3D exported hull overview", "panel_b": "top-down XY"},
                   "camera_elevation_deg": {"panel_a": 24, "panel_b": None},
                   "camera_azimuth_deg": {"panel_a": -56, "panel_b": None},
                   "pdf_sha256": sha256(pdf_path), "png_sha256": sha256(png_path)},
    }
    provenance_path.write_text(json.dumps(source_record, indent=2, sort_keys=True) + "\n")
    return pdf_path, png_path, provenance_path, source_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    pdf_path, png_path, provenance_path, record = render(Path(args.out_dir).resolve())
    print(json.dumps({"pdf": str(pdf_path), "png": str(png_path), "provenance": str(provenance_path),
                      "trajectories": record["layout_summary"]["trajectory_counts_by_split"],
                      "mesh_vertices": record["mesh_summary"]["vertices"]}, sort_keys=True))


if __name__ == "__main__":
    main()
