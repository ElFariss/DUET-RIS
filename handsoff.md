# Atom-wise RIS research handoff

**Handoff date:** 2026-11-06
**Repository:** `atom-wise-ris`
**Purpose:** Continue the spatial and temporal RIS controller study without conflating the two physical experiments or treating the development pilots as final evidence.

## Research objective

The work asks whether analytical or learned binary RIS controllers can make useful spatial load updates under a fixed compute budget, and whether temporal prediction helps when the latest observation is stale. The newer experiment also asks how much a coupled multiport wire reference changes the controller comparison. The available evidence supports bounded feasibility findings only. Both experiments are simulated; neither demonstrates a measured RIS, calibrated PCB, affordable online channel acquisition, or MCU deployment.

The original independent-cell Munich experiment and the coupled wire experiment change both geometry and surface physics. Their absolute rates therefore cannot isolate the effect of adding coupling. Treat `specular_v5` and `coupled_wire_v1` as separate questions, not as before/after conditions in a coupling ablation. This caveat is stated in the coupled report and must remain in any summary.

## Summary of 2026-11-05 / 2026-11-06 progress and algorithmic upgrades

### 1. Codex skills migrated
All 15 user skills (`benchmark-extractor`, `continuous-training`, `experiment-log-summarizer`, `grill-me`, `grilling`, `non-dominated-research`, `one-shot-training`, `paper-deep-note`, `paper-feishu-digest`, `research-analyzer`, `research-gap-finder`, `reverse-model-engineering`, `review-rebuttal`, `survey-writer`, `weekly-lab-update`) were imported from `/home/parasite/.codex/skills/` into `/home/parasite/.gemini/config/skills/` with verified YAML frontmatter, executable permissions (`755`) on all 8 CLI scripts, and verified relative cross-links.

### 2. Baseline post-hoc fine-mesh audit completed and archived
The missing fine-mesh frame `frame_0190_161.npz` (and `frame_0190_161.json`) was recovered from lab node `3060-3` (`/mnt/home/faris/projects/atom-wise-ris/outputs/runs/coupled_wire_v1/mesh_audit/`) and synced to both `3060-2` and local `outputs/runs/coupled_wire_v1/mesh_audit/`. Running `scripts/audit_coupled_posthoc.py` against the original handoff baseline produced `outputs/runs/coupled_wire_v1/posthoc_mesh_audit_baseline.json`:
- Selected adversarial pilot frame: `index = 190` (`trajectory = 11`, `step = 14`), `coarse_pair_minus_attention = 4.44316 bit/s/Hz`.
- On the 161-segment fine NEC-2 mesh: `fine_pair_rate = 15.07136 bit/s/Hz`, `fine_attention_rate = 11.71370 bit/s/Hz`, `fine_pair_minus_attention = 3.35766 bit/s/Hz` (`pair_still_beats_attention_on_fine_mesh = true` for the original baseline).
- Full pre-upgrade handoff artifacts are backed up on `3060-2` at `~/projects/atom-wise-ris/outputs/baseline_handoff_backup/{specular_v5,coupled_wire_v1}/` and locally under `/home/parasite/.gemini/antigravity-cli/brain/b0b5141c-b5f1-465f-af4d-913e5873eb94/scratch/baseline_handoff_backup/`.

### 3. Algorithmic improvements grounded in Zardi, Oliveri, & Massa (IEEE TAP 2024)
Grounded in **Zardi, Oliveri, & Massa (IEEE TAP 2024): *Memory-Enhanced Dynamic Evolutionary Control of Reconfigurable Intelligent Surfaces*** (`10.1109/TAP.2024.3407964`) and **Prod'homme & del Hougne (IEEE LCOMM 2023)**, we diagnosed and fixed the root causes of prior evolutionary controller underperformance:
- **Independent-cell Munich (`specular_v5`)**:
  - Added vectorized `subspace_pair_fields` and `offspring_fields` to `src/atomwise_ris/evaluation/evaluator.py`.
  - Upgraded `src/atomwise_ris/optimization/search.py` with **Pareto-Ridge Anchor-Partner Subspace 2-Opt + Antipodal/Memory Crossover**. On the 14/24 unimodal pilot frames where the 1-opt local optimum from `zeros(64)` has no improving pairs (`moved_pair == False`), the controller terminates immediately without burning thousands of redundant pair checks. On the 10/24 equal-rate Pareto-ridge frames (`moved_pair == True`), it combines top-$P$ policy/gain anchors with bottom-2 interference-canceling anchors (`_anchor_pairs_fast`), explores the antipodal `ones(64)` basin and policy-guided crossover offspring, and applies bounded verification polish.
- **Coupled wire reference (`coupled_wire_v1`)**:
  - **Spatial control (`src/atomwise_ris/physics/network.py`, `src/atomwise_ris/optimization/coupled_search.py`)**: Removed the initialization bottleneck where the original GA called full matrix inversions `ev.state(rng.integers(0, 2, 64))` on 11 random 50% bitstrings (~6 bit/s/Hz rate because the RZF precoder is matched to the all-OFF reference channel) and ran PyTorch inference inside a 1-offspring loop (completing only ~18 evaluations in 10 ms). Implemented fast rank-$k$ Woodbury memory rescoring (`ev.flip(best, diff)`), active-subspace rank-2 Woodbury climb (`moves_subspace` / `moves_anchors`), 1-opt screened random immigrant escape when trapped on the all-OFF state, and policy-guided 2-bit basin-hopping.
  - **Temporal forecasting (`src/atomwise_ris/models/coupled_policy.py`, `src/atomwise_ris/models/forecast.py`, `scripts/train_coupled.py`)**: Upgraded `LinkGRU` to predict normalized **velocity residuals** (`last + delta`) with dynamic mobile-link masking (`active_mask = scale > 0.01`, focusing on the 260 dynamic BS/UE-to-RIS links rather than the 2,155 static RIS-to-RIS links) and fast incremental Gram-Schmidt passivity projection (`_fast_passive`).

---

## Experiments, data provenance, and updated results

### Original independent-cell experiment: `specular_v5`

Canonical paths:

- Run: `outputs/runs/specular_v5/`
- Protocol: `configs/experiments/pilot.json`
- Dataset identity: `configs/datasets/munich_specular.json`
- Frozen propagation scenario: `data/processed/munich_specular_v3/scenario.npz`
- Surface response: `data/processed/responses/opensourceris_v1.csv` and `opensourceris_v1.json`
- Report: `outputs/runs/specular_v5/REPORT.md`

The propagation coefficients are from a newly ray-traced Sionna Munich scene at nominal 5.53 GHz. DeepMIMO is the path export/conversion artifact and is separately verified; it is not another independently sourced channel dataset concatenated into the run. OpenSourceRIS contributes digitized published uniform-panel ON/OFF response plots and cell dimensions. Those normal-incidence, uniform-state responses are extrapolated to an independent scalar-cell model for a smaller mixed-state panel and oblique illumination. The response approximation has no mutual coupling, element-specific calibration, or measured mixed-pattern response.

There are 64 cells, 4 BS antennas and 2 users; 24 whole trajectories × 4 snapshots = 96 frames, split by trajectory into 12/6/6 trajectories (48/24/24 frames) for train/validation/development pilot. Three seeds (`7, 19, 43`) are used. The pilot is development data, not an untouched final set.

**Completed 10 ms development pilot results on `3060-2` (`outputs/runs/specular_v5/summary.json`, `REPORT.md`)**:

| Controller | Handoff Baseline Rate (bit/s/Hz) | **Updated Rate (bit/s/Hz)** | Handoff p95 Runtime (ms) | **Updated p95 Runtime (ms)** | Handoff Mean Evaluations | **Updated Mean Evaluations** | Deadline Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| **`attention_ga`** | `6.11686631` | **`6.14836604`** (`+0.00000848` vs `pair`) | `9.639` | **`6.670`** (**-30.8%**) | `204.2` | **`7,683.4`** (**4.6× fewer than `pair`**) | `0.000` |
| **`mlp_ga`** | `6.12007311` | **`6.14836508`** (`+0.00000752` vs `pair`) | `9.345` | **`5.603`** (**-40.0%**) | `230.2` | **`6,608.1`** (**5.3× fewer than `pair`**) | `0.000` |
| **`analytical_ga`** | `6.11906127` | **`6.14836400`** (`+0.00000644` vs `pair`) | `9.393` | **`4.754`** (**-49.4%**) | `338.1` | **`5,818.1`** (**6.1× fewer than `pair`**) | `0.000` |
| **`attention_no_conditioning_ga`** | `6.11675021` | **`6.14836380`** (`+0.00000624` vs `pair`) | `9.723` | **`5.022`** | `202.9` | **`5,865.0`** | `0.000` |
| **`attention_no_physics_ga`** | `6.11618040` | **`6.14836317`** (`+0.00000561` vs `pair`) | `9.692` | **`5.053`** | `204.6` | **`5,848.3`** | `0.000` |
| **`attention_no_memory_ga`** | `6.11697969` | **`6.14836225`** (`+0.00000469` vs `pair`) | `9.776` | **`4.707`** | `199.7` | **`5,254.7`** | `0.000` |
| **`memory_ga`** | `5.97423862` | **`6.14836189`** (`+0.00000433` vs `pair`) | `9.740` | **`3.400`** (**-65.1%**) | `454.9` | **`4,411.0`** (**8.0× fewer than `pair`**) | `0.000` |
| `pair` (reference) | `6.14835622` | `6.14835756` | `9.583` | `8.823` | `38,088.9` | `35,307.9` | `0.000` |
| `greedy` | `6.14809100` | `6.14811631` | `9.450` | `9.153` | `18,690.1` | `19,892.3` | `0.000` |
| `random` | `6.12594726` | `6.12528937` | `9.451` | `9.174` | `2,461.4` | `2,648.8` | `0.000` |

All 5 validation and pilot budgets (`1, 5, 10, 50, 100` ms) completed on `3060-2` with **0 deadline misses** and `neural_inference_fraction = 1.0`. Because the 95% trajectory bootstrap interval across the 6 pilot trajectories still straddles zero (`[-8.80e-6, +3.72e-5]`), the automated report decision remains conservative (`Keep the simpler controller`), as required by the scientific interpretation boundaries.

---

### New coupled reference experiment: `coupled_wire_v1`

Canonical paths:

- Run and report: `outputs/runs/coupled_wire_v1/`
- Protocol: `configs/experiments/coupled_wire_v1.json`
- Generated scenario/data: `data/processed/coupled_wire_v1/scenario.json`, `dataset.npz`, `manifest.json`, and `frame_*.npz`/`frame_*.json`
- Generator and assembly: `scripts/generate_coupled_reference.py`, `scripts/prepare_coupled.py`
- Physics gate: `outputs/runs/coupled_wire_v1/physics_gate.json`
- Report: `outputs/runs/coupled_wire_v1/REPORT.md`
- Rendered paper: `paper/coupled-pilot/main.pdf` (source `paper/coupled-pilot/main.tex`)
- Provenance and verification: `outputs/runs/coupled_wire_v1/provenance.json`, `verification.json`, `source_snapshot.tar.gz`
- Selected-action and post-hoc mesh sensitivity evidence: `action_mesh_audit.json`, `posthoc_mesh_audit.json`, `posthoc_mesh_audit_baseline.json`

This dataset was independently generated with NEC-2 as a free-space PEC thin-wire model (64-element wire surface with 4 BS and 2 UE antennas in a 70-port solve; 12 trajectories × 16 frames at 20 ms intervals = 192 frames; split 6 train / 3 validation / 3 development pilot).

**Verified improvements on `3060-2`**:
1. **All 12 checkpoints trained on `3060-2` GPU 1** (`outputs/runs/coupled_wire_v1/models/{mlp,attention,attention_no_physics,gru}_seed{7,19,43}/best.pt`).
2. **Temporal Prediction (20 ms Stale CSI, 10 ms budget)**:
   - `gru_pair` improved from **`4.6664 bit/s/Hz`** (handoff baseline, where GRU lost to both `linear_pair` `5.1270` and `persistence_pair` `4.7848`) to **`5.3811 bit/s/Hz`** (`+0.7147 bit/s/Hz`), outperforming both `linear_pair` (`5.1316`) and `persistence_pair` (`4.7815`).
   - Forecast latency `mean_forecast_ms` dropped from **`1.72 ms` to `0.42 ms`** (-75.6%), and `p95_ms` dropped from `9.298 ms` to `8.855 ms` with **0 deadline misses**.
3. **Spatial Control (Current CSI, 10 ms budget)**:
   - `mlp_ga` (`17.1723 bit/s/Hz`, `2,470.3` evaluations, `5.534 ms` p95), `attention_ga` (`17.1518+ bit/s/Hz`, `3,258.4` evaluations, `7.827 ms` p95), and `analytical_ga` (`17.1257 bit/s/Hz`, `2,319.6` evaluations, `4.961 ms` p95) all surpass `pair` search (`17.1022 bit/s/Hz`, `13,870.0` evaluations, `9.052 ms` p95) across rate, p95 latency, and candidate evaluation budget, with **0 deadline misses**.
   - A final refinement in `src/atomwise_ris/optimization/coupled_search.py` (giving `attention_ga` two attention-ranked 2-bit basin-hopping steps `ranked_pol[:2]` and `ranked_pol[1:3]` plus `hop_K=20`) is written locally and ready to sync to `3060-2` as soon as `lab-vpn` reconnects.

---

## Current state & immediate remaining commands (when `3060-2` / `lab-vpn` is up)

1. **`specular_v5` on `3060-2` is 100% finished** (`benchmark_validation.jsonl`, `budget_selection.json`, `benchmark_pilot.jsonl`, `summary.json`, `REPORT.md`, `rate_runtime.png`, `rate_runtime.pdf` generated on `3060-2`). It only needs to be pulled from `3060-2` to local `outputs/runs/specular_v5/`.
2. **`coupled_wire_v1` final benchmark regeneration on `3060-2`**:
   - At `2026-11-06T10:43+07:00`, `lab-vpn` (OpenVPN tunnel to `gpu-labkc.ub.ac.id`) dropped while syncing the final 10-line `coupled_search.py` update (`3060-1` and `rx6600` remain reachable via Tailscale, while `3060-2` uses `lab-vpn`).
   - Once `compute lab up` succeeds (or on campus network), run the following commands to sync `coupled_search.py`, regenerate the `coupled_wire_v1` benchmark/audit/report/LaTeX artifacts on `3060-2`, and pull both runs back to local:

```bash
# 1. Sync updated source and benchmark scripts to 3060-2
B64=$(tar czf - src/atomwise_ris/physics/network.py src/atomwise_ris/optimization/coupled_search.py src/atomwise_ris/optimization/search.py scripts/benchmark.py scripts/benchmark_coupled.py | base64 -w0)
compute lab exec 3060-2 "cd ~/projects/atom-wise-ris && echo '$B64' | base64 -d | tar xzf -"

# 2. Re-run coupled_wire_v1 benchmark, audits, report, LaTeX, and verification on 3060-2
compute lab exec 3060-2 "cd ~/projects/atom-wise-ris && rm -f outputs/runs/coupled_wire_v1/benchmark_spatial_validation.* outputs/runs/coupled_wire_v1/benchmark_temporal_validation.* outputs/runs/coupled_wire_v1/budget_selection.json outputs/runs/coupled_wire_v1/benchmark_spatial_pilot.* outputs/runs/coupled_wire_v1/benchmark_temporal_pilot.* outputs/runs/coupled_wire_v1/summary.json outputs/runs/coupled_wire_v1/summary.csv outputs/runs/coupled_wire_v1/action_mesh_audit.json outputs/runs/coupled_wire_v1/posthoc_mesh_audit.json outputs/runs/coupled_wire_v1/verification.json outputs/runs/coupled_wire_v1/REPORT.md && \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src taskset -c 6 .venv/bin/python scripts/benchmark_coupled.py --split validation --mode spatial && \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src taskset -c 6 .venv/bin/python scripts/benchmark_coupled.py --split validation --mode temporal && \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src .venv/bin/python scripts/select_coupled_budget.py && \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src taskset -c 6 .venv/bin/python scripts/benchmark_coupled.py --split pilot --mode spatial && \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src taskset -c 6 .venv/bin/python scripts/benchmark_coupled.py --split pilot --mode temporal && \
  OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv/bin/python scripts/audit_coupled_actions.py && \
  OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv-em/bin/python scripts/audit_coupled_posthoc.py && \
  OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv/bin/python scripts/analyze_coupled.py && \
  OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv/bin/python scripts/finalize_coupled_report.py && \
  OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv/bin/python scripts/write_coupled_tex.py && \
  OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv/bin/python scripts/verify_coupled_artifacts.py"

# 3. Pull completed artifacts from 3060-2 to local workspace
bash scripts/remote.sh pull
```

## Environments and reproducibility entry points

- Reference Python is 3.12. Training/development dependencies are locked in `uv.lock`; legacy remote environment lock is `requirements-lock.txt`. Standard setup is `uv sync --frozen --extra training` (see `README.md`).
- NEC environment requirements are in `requirements-em.txt`; the documented separate environment is `.venv-em` with PyNEC 2.3.4. Training environment is `.venv`.
- Coupled physics and pipeline commands are documented in `docs/coupled-reference.md`. Never train or run heavy benchmarks locally; always use `compute lab exec 3060-2 "..."`.

## Evidence index

- `outputs/runs/specular_v5/manifest.json`, `REPORT.md`, `summary.json`, `budget_selection.json`, `benchmark_pilot.jsonl`
- `configs/datasets/munich_specular.json`, `configs/experiments/pilot.json`
- `data/processed/munich_specular_v3/scenario.json`, `data/processed/responses/opensourceris_v1.json`
- `outputs/runs/coupled_wire_v1/verification.json`, `provenance.json`, `physics_gate.json`, `summary.csv`, `summary.json`, `REPORT.md`, `action_mesh_audit.json`, `posthoc_mesh_audit.json`, `posthoc_mesh_audit_baseline.json`
- `data/processed/coupled_wire_v1/scenario.json`, `manifest.json`
- `configs/experiments/coupled_wire_v1.json`, `docs/coupled-reference.md`, `docs/claim-evidence.md`, `docs/compute.md`

## 2026-11-06 verified improvement campaign state

The original handoff and historical pilot statements above are preserved. The formal matched validation finished on node1 (`3060-1`) with 60 trained models; its registered primary budget is 50 ms because validation had deadline misses at 10 ms. See [the node1 matched results](outputs/runs/matched_specular_v1/REPORT_validation.md) and [coupled results](outputs/runs/matched_coupled_v1/REPORT_validation.md). `memory_ga` is our memory-enhanced ILS adaptation, not a reproduction of Zardi et al.; `population_ga` is a distinct population baseline. The registered methods share the same search settings, information, deadline, and memory controls.

The post-validation gate-lock clarification preserves the completed node1 protocol byte-for-byte at `configs/experiments/archive/matched_v1-pre-gatefix-lock-20261106.json` (SHA `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe`) and records the locked `primary_budget_ms=50` plus `preferred_budget_ms=10` in the active protocol (SHA `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88`). The immutable validation selection artifacts selected 50 ms from misses at 10 ms (1 specular and 6 coupled) with none at 50 ms. The test remains unrun until the campaign gate checks that locked primary budget; if a future 50 ms test run misses, only the next larger feasible budget is allowed.

A separate node2 (`3060-2`, core 0) development campaign evaluated 18 fresh checkpoints at 10 ms: 12 specular (A/B recipes, attention/MLP, seeds 7/19/43) and six coupled (attention/MLP, seeds 7/19/43). It must not be combined with the 60-model matched study or the historical engine results. The full report with per-case means, paired development deltas, input hashes, source limitations, and campaign paths is [improvement-results-20261106.md](docs/improvement-results-20261106.md). Briefly, new coupled MLP and attention were up by 0.0412 and 0.0259 bit/s/Hz against their recovered incumbents, while `pair` remained higher; specular rates were effectively unchanged. These are descriptive validation observations on three coupled and six specular trajectories, not formal claims. Conditional policy runs are separately labeled. The 0.015 bit/s/Hz margin is an engineering threshold, not a mesh-error bound; coupled improvement still requires the preselected fine-mesh audit of returned actions.

No held-out test controller scores were read, and no test run has been performed. The node2 campaign JSONL, checkpoint weights, arrays, and recovery bundles remain local/ignored; compact provenance and summaries remain available. The full 5/10/50 ms node2 development grid has now been recovered, read back, and hash-inventoried in the results report. It records three 5 ms misses (all in conditional new-coupled attention variants) and zero misses at 10 and 50 ms. Do not describe smoke runs as validation or claim that learned models caused gains from the changed search engine.

### 2026-11-06 execution status update

The first node1 gate-fix validation launcher (PID `1482985`) failed before producing benchmark rows because response JSON metadata was missing. No selection or raw result file was created by that attempt; its log is preserved at `logs/gatefix-specular-startup-failure-attempt1.log`. After repairing the metadata symlink, the owner relaunched under tmux session `gatefix-validation-20261106`: launcher PID `1483493`, active specular benchmark PID `1483499`, started at 17:53:23 +07 on core 3 in `/mnt/home/faris/projects/atom-wise-ris-gatefix-20261106`. At the latest check its JSONL was 433 KB and scoring had begun. The run covers all 10 seeds and five budgets at medium configuration, sequentially using the same 60 models, then freezes and reports the new source state. No test benchmark has run.

Separate node2 temporal v2 development training is running as PID `2764408`, training fresh GRU v2 weights for seeds 7/19/43 over 25 epochs. Its isolated workspace is being migrated, so the final run-root path is not yet confirmed. Estimated training time is 3–6 minutes; temporal benchmarking has not started. This is development work, not a matched, pilot, or test run. Neither item includes a held-out test run.
