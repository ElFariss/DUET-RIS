# Coupled-Wire Trajectory Datasets v2 & Mesh Refinement Verification

## 1. Overview & Objective

This document records the provenance, generation environment, verification results, SHA-256 digests, and disjointness properties of the expanded NEC-2 coupled-wire datasets generated for the `atom-wise-ris` project on 2026-11-06.

### Dataset Roster

| Dataset Directory | Split / Role | Seed | Trajectories | Steps / Traj | Total Frames | Segments / Wire | Host | Generation Status | Local Disk Usage |
|---|---|---|---|---|---|---|---|---|---|
| `data/processed/coupled_wire_v1/` | train / validation / pilot | fixed | 12 | 16 | 192 | 81 | baseline | Frozen reference | 29 MiB |
| `data/processed/coupled_wire_test_v1/` | untouched test | 20261106 | 30 | 16 | 480 | 81 | `labkc-comm1` | Byte-identical, verified | 72 MiB |
| `data/processed/coupled_wire_dev_v1/` | algorithm development | 20261107 | 30 | 16 | 480 | 81 | `rx6600` | Complete, verified | 38 MiB |
| `data/processed/coupled_wire_validation_fine161/` | fine-mesh gate audit | N/A (re-extracted) | 3 | 16 | 48 | 161 | `rx6600` | Complete, verified | 3.6 MiB |
| `data/processed/coupled_wire_test_v2/` | untouched future test | 20261108 | 30 | 16 | 480 | 81 | `rx6600` | Complete, verified | 38 MiB |

---

## 2. Host, Software, & Hardware Environment

All generation of `coupled_wire_dev_v1`, `coupled_wire_validation_fine161`, and `coupled_wire_test_v2` was executed on node `rx6600` (`labkc1-amd`) via SSH over Tailscale.

- **Node Alias / Hostname**: `rx6600` / `labkc1-amd` (`100.89.211.119`)
- **CPU**: AMD Ryzen 7 8700G w/ Radeon 780M Graphics (8 physical cores, 16 threads, base clock 4.2 GHz)
- **RAM**: 64 GB DDR5 (live readback: `/proc/meminfo` `MemTotal=63416480 kB`; `free -h` reports 60 GiB total)
- **OS / Kernel**: Linux `6.14.0-33-generic #33~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC` x86_64
- **Working Directory**: `/var/tmp/atomwise-ris-gen-20261106` (isolated non-NFS NVMe filesystem, `/` partition with 25 GB free space)
- **Virtual Environment**: `/var/tmp/atomwise-ris-gen-20261106/.venv-em`
- **Software Versions**:
  - Python: `3.12.3` (GCC 13.3.0)
  - NumPy: `2.2.6`
  - SciPy: `1.15.3`
  - PyNEC: `2.3.4` (NEC-2 thin-wire method-of-moments engine)
- **Environment Settings**: `PYTHONPATH=$PWD/src`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`
- **Execution Manager**: `tmux` session `coupled_gen` driven by sequential script `logs/driver.sh`

---

## 3. Disjointness & Collision Verification

All trajectory draws are sampled from the per-user bounding box derived from the actual step-0 coordinates in `generate_coupled_reference.trajectories()`:
- User 0 start box: $x \in [-0.43, -0.38]$, $y \in [0.20, 0.30747271091145056]$, $z = 0.98$ (degenerate z plane)
- User 1 start box: $x \in [-0.56, -0.52]$, $y \in [0.27454421543904595, 0.3909999412393042]$, $z = 1.05$ (degenerate z plane)
- Velocity ranges: $v_x \in [-0.15, 0.15]$, $v_y \in [-0.7, 0.7]$, $v_z \in [-0.04, 0.04]$ m/s
- Sinusoidal y-displacement: $y(t) = y_0 + v_y t + 0.006 \sin(2\pi \cdot 2 t + \text{traj}) \cdot [1, -1]^\top$
- Inter-frame time step: $\Delta t = 0.02$ s (16 frames spanning 0.30 s per trajectory)

All pairwise comparisons across all splits show strict disjointness (no shared start positions, no shared trajectory frames) and strict safety against inter-wire collisions (> 30 mm minimum separation between users):

| Split / Set A | Split / Set B | Min Chebyshev Start Dist (m) | Min Worst-User Frame Dist (m) | Disjoint? | Collision Free? |
|---|---|---|---|---|---|
| `ref_train` | `ref_validation` | 0.0200 | 0.0068 | **Yes** | **Yes** (> 0.03 m) |
| `ref_train` | `ref_pilot` | 0.0200 | 0.0136 | **Yes** | **Yes** (> 0.03 m) |
| `ref_train` | `coupled_wire_test_v1` | 0.0036 | 0.0072 | **Yes** | **Yes** (> 0.03 m) |
| `ref_train` | `coupled_wire_dev_v1` | 0.0011 | 0.0058 | **Yes** | **Yes** (> 0.03 m) |
| `ref_train` | `coupled_wire_test_v2` | 0.0026 | 0.0056 | **Yes** | **Yes** (> 0.03 m) |
| `ref_validation` | `ref_pilot` | 0.0200 | 0.0150 | **Yes** | **Yes** (> 0.03 m) |
| `ref_validation` | `coupled_wire_test_v1` | 0.0018 | 0.0148 | **Yes** | **Yes** (> 0.03 m) |
| `ref_validation` | `coupled_wire_dev_v1` | 0.0017 | 0.0137 | **Yes** | **Yes** (> 0.03 m) |
| `ref_validation` | `coupled_wire_test_v2` | 0.0079 | 0.0068 | **Yes** | **Yes** (> 0.03 m) |
| `ref_pilot` | `coupled_wire_test_v1` | 0.0047 | 0.0097 | **Yes** | **Yes** (> 0.03 m) |
| `ref_pilot` | `coupled_wire_dev_v1` | 0.0010 | 0.0068 | **Yes** | **Yes** (> 0.03 m) |
| `ref_pilot` | `coupled_wire_test_v2` | 0.0035 | 0.0096 | **Yes** | **Yes** (> 0.03 m) |
| `coupled_wire_test_v1` | `coupled_wire_dev_v1` | 0.0006 | 0.0037 | **Yes** | **Yes** (> 0.03 m) |
| `coupled_wire_test_v1` | `coupled_wire_test_v2` | 0.0002 | 0.0030 | **Yes** | **Yes** (> 0.03 m) |
| `coupled_wire_dev_v1` | `coupled_wire_test_v2` | 0.0003 | 0.0030 | **Yes** | **Yes** (> 0.03 m) |

Unit tests in `tests/test_coupled_data_splits.py` (9/9 tests passing) formalize and gate these invariants.

---

## 4. `coupled_wire_dev_v1` Verification

- **Command**:
  ```bash
  .venv-em/bin/python scripts/generate_coupled_test.py \
    --out data/processed/coupled_wire_dev_v1 \
    --seed 20261107 \
    --split-name dev \
    --workers 8
  ```
- **Execution Timestamps**:
  - Start: `2026-11-06T19:56:55+07:00`
  - Completion: `2026-11-06T20:37:10+07:00` (Exit code: 0)
  - Wall Clock Time: 40 minutes 15 seconds (2,415 s)
- **Per-Frame Runtime (81 segments, 8 workers)**:
  - Mean: 40.204 s
  - Min: 34.106 s
  - Max: 40.986 s
- **Local Verification Results**:
  - Frame count: 480 (`frame_0000.npz` to `frame_0479.npz`)
  - All matrices finite: **True** (all $70 \times 70$ complex impedance matrices finite)
  - Passivity (Scattering): Maximum singular value $\sigma_{\max}(S) = 0.986637 \le 1.0001$ (**Strictly passive**)
  - Resistance Positivity: Minimum eigenvalue $\lambda_{\min}(R) = 0.541932\ \Omega > 0$ (**Strictly positive definite**)
  - Reciprocity: Maximum relative reciprocity $\|Z - Z^\top\| / \|Z\| = 5.74 \times 10^{-8} \le 10^{-6}$
  - SHA-256 Integrity: 100% exact match across all 961 remote files vs local copies
  - `scenario.json` SHA-256: `e78ddb7f5c551133efb271e968f2c49c5742391f43ba8178cbb0334fc43426cf`
  - Disk Footprint: 38 MiB

---

## 5. `coupled_wire_validation_fine161` Verification & Mesh Planning

- **Command**:
  ```bash
  .venv-em/bin/python scripts/generate_coupled_test.py \
    --out data/processed/coupled_wire_validation_fine161 \
    --fine-from data/processed/coupled_wire_v1 \
    --fine-split validation \
    --segments 161 \
    --workers 4
  ```
- **Execution Timestamps**:
  - Start: `2026-11-06T20:37:10+07:00`
  - Completion: `2026-11-06T21:26:20+07:00` (Exit code: 0)
  - Wall Clock Time: 49 minutes 10 seconds (2,950 s)
- **Per-Frame Runtime (161 segments, 4 workers)**:
  - Mean: 245.404 s (~4.09 minutes per frame)
  - Min: 242.979 s
  - Max: 248.787 s
  - Ratio vs 81-segment mesh: $\approx 6.1 \times$ CPU time increase ($O(N^3)$ matrix inversion scaling: $(161/81)^3 \approx 7.85$)
- **Local Verification Results**:
  - Frame count: 48 frames (validation indices 32..47, 96..111, 160..175 matching `coupled_wire_v1`)
  - All matrices finite: **True** (all $70 \times 70$ complex impedance matrices finite)
  - Passivity (Scattering): Maximum singular value $\sigma_{\max}(S) = 0.986644 \le 1.0001$ (**Strictly passive**)
  - Resistance Positivity: Minimum eigenvalue $\lambda_{\min}(R) = 0.539996\ \Omega > 0$ (**Strictly positive definite**)
  - Reciprocity: Maximum relative reciprocity $\|Z - Z^\top\| / \|Z\| = 9.83 \times 10^{-9} \le 10^{-6}$
  - SHA-256 Integrity: 100% exact match across all 97 remote files vs local copies
  - `scenario.json` SHA-256: `410429f3a943721b92044acd99782ed3c4d8a2db47c21e33f36719d307ab554d`
  - Disk Footprint: 3.6 MiB

### Dev-Set Fine-Mesh (161-Segment) Planning Analysis

Generating a corresponding fine-mesh network dataset for the full development set (`coupled_wire_dev_v1`, 480 frames) would require:
- **Total CPU core computation time**: $480 \times 245.404\text{ s} = 117,794\text{ seconds} \approx 32.72\text{ core-hours}$.
- **Projected Wall Clock Time**:
  - On 8 workers (Ryzen 7 8700G, 8 dedicated physical cores): $\approx 14,724\text{ seconds} \approx \mathbf{4.09\text{ hours}}$ (~4 h 5 m).
  - On 4 workers: $\approx 29,448\text{ seconds} \approx \mathbf{8.18\text{ hours}}$ (~8 h 11 m).
- **Projected Disk Footprint**: $\approx 38\text{ MiB}$ (480 `.npz` files + 480 `.json` metadata files).

---

## 6. `coupled_wire_test_v2` Verification

- **Command**:
  ```bash
  .venv-em/bin/python scripts/generate_coupled_test.py \
    --out data/processed/coupled_wire_test_v2 \
    --seed 20261108 \
    --split-name test \
    --workers 8
  ```
- **Execution Timestamps**:
  - Start: `2026-11-06T21:26:20+07:00`
  - Completion: `2026-11-06T22:06:49+07:00` (Exit code: 0)
  - Wall Clock Time: 40 minutes 29 seconds (2,429 s)
- **Per-Frame Runtime (81 segments, 8 workers)**:
  - Mean: 40.436 s
  - Min: 39.801 s
  - Max: 41.301 s
- **Local Verification Results**:
  - Frame count: 480 (`frame_0000.npz` to `frame_0479.npz`)
  - All matrices finite: **True** (all $70 \times 70$ complex impedance matrices finite)
  - Passivity (Scattering): Maximum singular value $\sigma_{\max}(S) = 0.986636 \le 1.0001$ (**Strictly passive**)
  - Resistance Positivity: Minimum eigenvalue $\lambda_{\min}(R) = 0.541970\ \Omega > 0$ (**Strictly positive definite**)
  - Reciprocity: Maximum relative reciprocity $\|Z - Z^\top\| / \|Z\| = 5.75 \times 10^{-8} \le 10^{-6}$
  - SHA-256 Integrity: 100% exact match across all 961 remote files vs local copies
  - `scenario.json` SHA-256: `de08a1495d295946bcc7b39b952c3523efd006e90527a3802252375f5147bb58`
  - Disk Footprint: 38 MiB

---

## 7. Target Data Format & Strict Hygiene

### Format Standard
The canonical format for all generated electromagnetic datasets is **frame-level `.npz` + `.json` sidecars + root `scenario.json`**:
- `frame_XXXX.npz`: Contains array `'z'` (shape $70 \times 70$, complex128) and array `'centers'` (shape $70 \times 3$, float64).
- `frame_XXXX.json`: Records per-frame diagnostics (`sha256`, `seconds`, `maximum_scattering_singular_value`, `minimum_resistance_eigenvalue_ohm`, `reciprocity_relative`, `hostname`, `users_m`, `split`, `segments_per_wire`).
- `scenario.json`: Contains full simulation metadata, sampling boundaries, trajectory draws, row definitions, and disjointness certificates.

Monolithic `dataset.npz` / `manifest.json` assembly (e.g. via `scripts/prepare_coupled.py`) is intentionally omitted here:
1. `scripts/prepare_coupled.py` generates greedy controller labels and beamforming headroom, which violates untouched test protocol standards.
2. Downstream benchmark and evaluation routines consume frame-level datasets directly or assemble matched protocols on demand without pre-computing labels.

### Strict Hygiene Principle
Under zero circumstances may any controller action, SNR, channel rate, beamforming weight, or supervision label be computed on `coupled_wire_test_v2`. It remains an untouched held test split.

---

## 8. Remote Workspace Footprint & Node Retention

The remote generation workspace is located on node `rx6600`:
- **Remote Directory**: `/var/tmp/atomwise-ris-gen-20261106`
- **Total Workspace Footprint**: 280 MiB
- **Host Root Filesystem Availability**: 25 GiB free out of 70 GiB (64% used)
- **Node Policy**: The directory `/var/tmp/atomwise-ris-gen-20261106` was left intact on `rx6600` because disk availability on `/` is generous (25 GiB free vs. 280 MiB used), providing a verifiable remote replica and run logs (`logs/dev.log`, `logs/fine.log`, `logs/test2.log`, `logs/driver.log`).
