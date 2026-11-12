# Paper A: physics of coupled binary RIS control

How do blockage, user motion, an unseen city, mutual coupling and array size (64/128/256) change the worst-user rate, and the value of pair moves, for a 1-bit RIS? The channels are calibrated hybrid ray-tracing + NEC-2 channels from [GeoRIS-Bench](../GeoRIS-Bench/README.md).

This repository continues the original **atom-wise-ris** project. Its finished free-space b35 study (Paper 1) becomes one section of Paper A.

## Part 1, finished and frozen: free-space b35 study (Paper 1)

- **Setup:** a thin-wire RIS bench in free space (NEC-2, 81- and 161-segment meshes), with 2 users, 4 base-station antennas and a fixed precoder.
- **Held-out test:** the single run of the frozen protocol `configs/experiments/matched_v2.json` on `coupled_wire_test_v2`: 30 trajectories, 480 frames, CPU 5 pinned. Results are in `docs/matched-v2-test-results-20261108.md`.
- **Result at the 50 ms primary budget:**
  - b35 beats pair by **+0.085 bit/s/Hz** [+0.047, +0.128] on 161 segments, winning 27 of 30 trajectories.
  - b35 also beats b3, b5 and ME-GA. All four contrasts are supported on both meshes.
- **Scope:** it holds only for that setup, a 1 m bench with no obstacles where users always see the base station.
- **Earlier pilots** (Munich specular measurement-informed pilot `specular_v5`, coupled spatial/temporal pilot `coupled_wire_v1`, ladder v2) are kept with their reports in `outputs/runs/` and `docs/`. The manuscript is in `paper/`.

**Frozen files** (do not edit): `outputs/frozen/`, `configs/experiments/matched_v2.json`, `configs/experiments/matched_v1.json`.

## Part 2, in progress: physics study on GeoRIS-Bench

The questions:
1. a user blocked by a building;
2. a moving user;
3. an unseen city (leave one map out);
4. whether coupling matters in a real scene (optimize with full vs diagonal Z, rescore with full Z);
5. array size 64/128/256.

Secondary: RIS placement, and more or closer users. The methods are no RIS, all OFF, greedy, exact pair, b35, ME-GA and geometric phase-gradient steering.

**First evidence (2026-11-12, natural-scope validation frames only).** It is in Paper B's `docs/bench-ris-leverage-diagnostic-20261112.md`:
- A 0.2–0.45 m facade RIS about 112 m from the base station changes the worst-user rate by a median of under 0.05 bit/s/Hz.
- Its path is 40–60 dB below the base station's own paths.
- About half of the frames have a served user with no traced path.

So in this deployment geometry the RIS barely matters. That is a Paper A finding in its own right. It also motivates a RIS-relevant scope, with the RIS near the base station or near the users.

## Layout

```text
src/atomwise_ris/   core.py, data/, models/ (MLP, attention, forecast), responses/, utils/
                    (the physics, channel and solver modules come from GeoRIS-Bench)
scripts/            Paper 1 pipeline: prepare, train, benchmark*, analyze*, reproduce*, ladder and matched runs
configs/            datasets, methods, experiment protocols (matched_v1, matched_v2)
experiments/        hypotheses and matched comparison definitions
data/               free-space wire bench (coupled_wire_*), Munich specular arrays, responses, raw sources
outputs/            runs (reports, checkpoints, timings), frozen protocol, figures, audits
paper/              manuscripts and figures
docs/               protocols, results, evidence and limitations
archives/           preserved historical code
tests/              numerical, leakage and protocol checks
```

The test splits `coupled_wire_test_v1`, `coupled_wire_test_v2` and `coupled_wire_test_v2_fine161` are **sealed**: Paper 1's single test run used them, and they are not for design.

## Setup and tests

This repository expects `../GeoRIS-Bench` next to it. Use the shared workspace venv, or install both into your own:

```bash
pip install -e ../GeoRIS-Bench[dataset] -e .[training]
PYTHONPATH=src:scripts python -m unittest discover -s tests
```

**Known failure:** `test_matched…test_memory_ga_ranking_uses_pattern_spread` fails. It failed before the 2026-11-12 split too.

`uv.lock` and `pyproject.toml` still describe the old single repository. They have not been re-locked since the split.

## Git

- `origin` is **github.com/ElFariss/GeoRIS-Physics**.
- The history is the original atom-wise-ris history. That repository's remote is kept as **`atom-wise-ris-paper1`** (github.com/ElFariss/atom-wise-ris, the published Paper 1 code); push only to `origin`.
- Files that moved to GeoRIS-Bench or Paper B show as deleted here. The full map is `../workspace-notes/split-manifest-20261112.json`.

No permissive license has been chosen for the original research code (see `LICENSE` and `THIRD_PARTY.md`).
