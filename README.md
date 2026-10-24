# Atom-wise RIS

Simulation-only feasibility study of **physically conditioned, learned bit edits** for a 1-bit reconfigurable intelligent surface. The controller tries to improve the weakest user's rate within a complete CPU runtime budget.

**Current evidence:** the completed exact-export pilot favors cached analytical pair/greedy search over learned mutation. At the validation-selected **10 ms** budget, mean worst-user spectral efficiency was **6.14836** for pair search, **6.12007** for the MLP and **6.11687 bit/s/Hz** for attention. All three had zero observed deadline misses at that budget. These are six-trajectory development results, not a final paper test. See the [report](outputs/runs/specular_v5/REPORT.md) and [claim boundaries](docs/claim-evidence.md).

**Coupling extension in progress:** a separate NEC-2 3D wire reference, exact multiport evaluator, mesh checks and moving-receiver generator are now implemented. The new spatial/temporal campaign has no completed controller result yet. See [physical scope and status](docs/coupled-reference.md).

## Scientific pipeline

Munich geometry → Sionna propagation at nominal 5.53 GHz → verified DeepMIMO path export → measured-surface-informed binary response → fixed-precoder evaluator → timed RIS controller.

- 64 cells, 4 BS antennas, 2 users; 24 spatially split trajectories, 4 snapshots each.
- Train / validation / development pilot: 12 / 6 / 6 whole trajectories.
- Objective: minimum user spectral efficiency with interference and thermal noise.
- Shared MLP, compact two-layer attention, five analytical/stochastic baselines, and three ablations.
- Three seeds, 1/5/10/50/100 ms CPU budgets. Validation selects the primary feasible budget before pilot evaluation.
- Surface measurements are extrapolated to independent mixed-state cells. This is **measurement-informed simulation**, not a calibrated EM model or hardware validation.

## Layout

```text
configs/                  dataset identity, method jobs, experiment protocol
src/atomwise_ris/
  data/                   scenario interface and split checks
  responses/              complex ON/OFF response and provenance
  channels/               fixed reference precoder
  evaluation/             physical channel combination and cached exact scores
  optimization/           timed search and causal configuration memory
  models/                 shared MLP and compact attention edit policies
  physics/                NEC-2 reference and exact coupled-network updates
  utils/                  hashes and provenance
scripts/                  acquisition, audits, training, evaluation, reproduction
experiments/              hypotheses and matched comparison definitions
data/raw/                source figures, ray paths, DeepMIMO exports
data/processed/          frozen channel arrays and digitized response tables
outputs/runs/<run>/        configs, checkpoints, histories, timings, reports, figures
paper/                    existing IEEE proposal archive and generated figures
docs/                    assumptions, evidence, provenance, repository decisions
tests/                   numerical, leakage, and policy checks
archives/                 preserved historical code and pre-migration source
```

Each run keeps its checkpoints and evidence together. `responses/` contains the historical independent-cell approximation. `physics/` contains the separate thin-wire electromagnetic reference; it does not calibrate the OpenSourceRIS PCB.

## Install and numerical checks

Python 3.12 is the reference environment. With [uv](https://docs.astral.sh/uv/):

```bash
uv sync --frozen --extra training
uv run --frozen --extra training python -m unittest discover -s tests -v
```

For ray tracing and DeepMIMO conversion, include `--extra simulation`. The training lock uses PyTorch 2.9.1/CUDA 12.8; GPU training needs a compatible NVIDIA driver. CPU-only CI installs the same PyTorch version from the CPU index. `requirements-lock.txt` records the original remote environment; `uv.lock` is the dependency-resolution lock for this repository.

## Reproduce from frozen channels

Large channel arrays, raw paths, checkpoints, and individual timing records are retained in the workspace and lab mirror, excluded from normal Git. Read [data/README.md](data/README.md) before trying a fresh clone. This is not yet a publicly released dataset.

```bash
.venv/bin/python scripts/reproduce.py --run outputs/runs/my_reproduction --device cuda
```

This checks input hashes, snapshots source/configuration/environment, audits the scenario, computes pair headroom, trains only if the gate passes, benchmarks validation, freezes the budget, evaluates the development pilot, and writes sensitivity analysis/report/figures. It refuses to overwrite completed experiment artifacts. `--stage prepare|train|validate|pilot|report` supports separated execution of stages; use the same configuration and source for an existing run. Failed-stage logs are preserved; inspect them before choosing a new run.

For postprocessing an existing completed run:

```bash
.venv/bin/python scripts/analyze.py --run outputs/runs/specular_v5
```

The models are small. One GPU is sufficient for this bounded campaign; CPU timing must run alone on a quiet CPU, not alongside training. The harness binds to one available core and sets Torch/BLAS thread counts to one. CPU-specific latency must not be presented as microcontroller performance.

## Regenerate propagation

The frozen arrays are required for exact dataset identity. Re-tracing the scene is an independent simulation and is not bitwise repeatable across devices. Follow [data/README.md](data/README.md) for acquisition commands, the exporter path-cap repair, carrier phase, coordinate matching, and convergence limitations.

## Evidence and limitations

The later paper still needs an untouched final evaluation set, a stronger physical-response validation, and substantially more independent trajectories/seeds. Adding attention or combining data sources alone does not establish novelty. See [docs/physical-model.md](docs/physical-model.md), [experiments/README.md](experiments/README.md), and [THIRD_PARTY.md](THIRD_PARTY.md).

No permissive license has been selected for original research code. Third-party material retains its own terms; see [LICENSE](LICENSE). `CITATION.cff` describes an unpublished repository, not an accepted paper.
