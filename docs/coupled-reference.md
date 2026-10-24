# Coupled spatial and temporal extension — work in progress

## Status (2026-10-24)

The independent-cell `specular_v5` results are complete and preserved. The new
coupled pilot is also complete: 192 electromagnetic frames, 12 trained checkpoints,
23,040 validation/pilot controller trials, and a validation-selected 10 ms budget.
The 64-element reference mesh check and direct loaded-response checks passed.
The current attention policy did not outperform analytical pair search. For
moving receivers, linear forecasting plus pair search had the highest mean among
the causal methods at 10 ms. Numerical rate sensitivity and only three pilot
trajectories limit the strength of these conclusions.

See [the full report](../outputs/runs/coupled_wire_v1/REPORT.md) and
[the IEEE-style PDF](../paper/coupled-pilot/main.pdf). No measured hardware
validation, real PCB calibration or microcontroller result is claimed.

## What changes physically

The reference is a **separate free-space PEC wire surface**, not a calibrated
OpenSourceRIS PCB. NEC-2 (PyNEC 2.3.4) solves the wire currents with a thin-wire
method of moments. All 64 RIS elements, four transmitting antennas and two
receiving antennas are in one 70-port geometry. Each wire is 24 mm long, with
50 micrometre radius. RIS horizontal/vertical pitches are 28/30 mm. Frequency
is 5.53 GHz. The production mesh has 81 segments per wire; a 161-segment mesh
is the independent refinement check. This does not model substrate, ground
plane, real switches, conductor loss, Munich buildings or moving human bodies.

A complete impedance matrix is extracted from unit port-voltage excitations.
The two binary loads have 1 ohm resistance and reactances centered on the
isolated-wire resonance with +/-70 ohm offsets. All source/receiver references
are real 50 ohms. The channel maps incident source power waves to received
power waves; the 0.1 W constraint is incident source-wave power, not a claim
that all power is radiated. Source mismatch and mutual coupling are retained.

The exact Schur complement terminates the external ports. Sherman-Morrison /
Woodbury updates evaluate single and paired binary load changes without
re-solving the entire network. These speedups are available to analytical
search and learned controllers alike. `tests/test_coupled_network.py` compares
all bit patterns and every pair of a small passive network with full solves.

## Numerical gate

Before training: reciprocal impedance residual <1e-7, largest scattering
singular value <1.0001, loaded-current relative error <1e-5 and maximum loaded
channel change <1% under mesh refinement. The final gate checks 103 binary
patterns at the reference geometry; dataset passivity is checked per frame.
Earlier unsuccessful mesh trials are retained with their actual failed flags.
The 1% check is numerical convergence, not measured hardware accuracy.

Short, strongly resonant 11 mm wires required very fine meshes and were not
selected for the first moving-user campaign. A fixed-feed discretization also
failed its checks. These are development trials, not hidden successful runs.

## Spatial versus temporal comparison

Spatial learning concerns which elements to change together. Temporal learning
concerns prediction from past channel observations when current CSI is stale.
The two should be tested separately and jointly, with analytical search,
shared MLP and attention receiving matched information. Perfect-current-CSI
controls must be identified as oracles in delayed-CSI comparisons.

The registered initial trajectory generator uses 12 complete trajectories,
16 frames each at 20 ms intervals, split before simulation into 6 training,
3 validation and 3 development-pilot trajectories. These are moving receivers
in a fixed free-space scene, not human-blockage simulation. The dataset is a
bounded feasibility pilot; it cannot support claims about city-scale channel
generalization. A later final study still needs an untouched, larger test set.

## Literature

The Consensus research document and independently checked DOI metadata are in
`docs/literature/coupling-temporal/`. The live matrix now contains 28 entries:
17 added references and the existing coupling-validation entry updated to its
published version. Existing reading statuses are preserved. Traffic forecasting
and beyond-diagonal hardware are explicitly distinguished from CSI prediction
and ordinary mutual coupling.

## Reproduce the physics checks

```bash
uv venv .venv-em --python 3.12
uv pip install --python .venv-em/bin/python -r requirements-em.txt
OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv-em/bin/python \
  scripts/validate_coupled_physics.py --side 8 --segments 21,41,81 \
  --out outputs/runs/coupling_halfwave64_v1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=src .venv-em/bin/python \
  scripts/gate_coupled_campaign.py
```

The first command preserves coarse-mesh failures. The campaign gate compares
81 and 161 segments using the selected loads and writes `physics_gate.json`.
Do not start a training campaign unless its `passed` field is true.

## Reproduce the complete pilot in a separate workspace

```bash
.venv/bin/python scripts/reproduce_coupled.py \
  --workspace /absolute/path/to/new-coupled-reproduction \
  --em-python /absolute/path/to/atom-wise-ris/.venv-em/bin/python \
  --train-python /absolute/path/to/atom-wise-ris/.venv/bin/python \
  --workers 2
```

The destination must not exist. The driver copies source/configuration and runs
physics checks, generation, labels, all models, validation budget selection, pilot
benchmarks, mesh audits and reporting. This wrapper is syntax checked; the
underlying stages were executed separately for the reported run. The archived
source snapshot identifies the code used before the full benchmark.
