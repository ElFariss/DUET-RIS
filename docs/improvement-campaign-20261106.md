# Improvement campaign runner (2026-11-06)

The campaign runner evaluates the matched search methods against the unchanged
TRAIN/VALIDATION artifacts. Its first pass is validation-only: three registered
seeds (7, 19, 43), 5/10/50 ms, and the preselected `medium` search config. Optional
`small` and `large` sensitivity runs also use validation and never alter the
primary config. `population_ga` is a separate model-free population baseline;
the legacy `*_ga` method IDs remain shared-step ranked ILS hybrids. Greedy, pair,
random, and population baselines receive no remembered patterns in either
benchmark.

An experimental paired-action query policy can be run for development
comparisons with `--conditional-pair-policy`. This flag is recorded in every
row and metadata sidecar, cannot be used on test, and makes the run ineligible
for the registered test freeze.

## Run and restart

From the repository root, start a fresh campaign with:

```sh
PYTHONPATH=src python scripts/run_improvement_campaign.py \
  --experiment coupled --stage validation \
  --out outputs/campaigns/coupled-dev-20261106
```

Use `--experiment specular` for the independent specular experiment. The default
primary run covers seeds 7, 19, 43 and budgets 5, 10, 50 ms. To include validation
sensitivity configurations, use `--configs small,medium,large`. Restart an
interrupted campaign with the same arguments plus `--resume`; the runner skips
units with both a JSONL result and metadata sidecar. It does not replace existing
files. Incomplete units are left for inspection and require a new campaign path
after they are diagnosed. `campaign.json`, `commands.log`, per-unit metadata, and
incrementally flushed JSONL results preserve provenance and progress. Each row
records elapsed time, deadline misses, evaluation count, and search trace.

For a one-frame validation smoke (not a result suitable for inference):

```sh
PYTHONPATH=src python scripts/run_improvement_campaign.py \
  --experiment coupled --stage validation --run outputs/runs/coupled_wire_v1 \
  --seeds 7 --budgets 10 --limit 1 \
  --out /tmp/ris-coupled-smoke
```

## Freeze and development

After complete medium validation coverage at 10 and 50 ms, the runner writes
`<experiment>_validation_freeze.json`. It selects 10 ms if every method has zero
observed misses, otherwise 50 ms if every method has zero misses there; if
neither is feasible, it records no selection. With the initial three-seed run,
the artifact supports development only. It is marked test-eligible only after
the full registered seed and budget protocol has completed on validation with
medium as the sole config. The artifact never replaces the canonical
`budget_selection.json` consumed by the established matched-test gate.

An optional development/pilot run requires that freeze:

```sh
PYTHONPATH=src python scripts/run_improvement_campaign.py \
  --experiment coupled --stage development \
  --freeze outputs/campaigns/coupled-dev-20261106/coupled_validation_freeze.json \
  --out outputs/campaigns/coupled-pilot-20261106
```

The pilot stage runs only the frozen medium config and validation-selected
budget. It remains development data and cannot change the freeze or support a
test claim. The benchmark's existing pilot guard also expects its canonical
`budget_selection.json` under the artifact root.

## Held-out test boundary

The runner refuses test data in validation/development. Test requires the
explicit `--stage test`, a feasible matching validation freeze, `--test-data`,
and no frame limit. It then calls the matched benchmark, which independently
requires the canonical `budget_selection.json` and verifies frozen code and
checkpoint hashes. Example (only after the canonical matched freeze and held-out
dataset are ready):

```sh
PYTHONPATH=src python scripts/run_improvement_campaign.py \
  --experiment coupled --stage test --test-data data/processed/coupled_wire_test_v1 \
  --freeze outputs/campaigns/coupled-dev-20261106/coupled_validation_freeze.json \
  --out outputs/campaigns/coupled-test-20261106
```

No test-generation or test benchmark was launched during implementation. The
runner verifies protocol and TRAIN/VALIDATION data hashes; the benchmark sidecar
records checkpoint, implementation, physics-gate, and held-out frame hashes.
For comparable CPU timings, run campaigns sequentially on the designated pinned
core with the registered single-thread settings and without concurrent jobs.

## Implementation notes and limits

The benchmark CLIs retain their existing defaults. `--output` accepts an absolute
path, allowing the runner to keep immutable per-unit results outside the model
artifact root. The runner does not train models, regenerate data, or modify the
registered protocol. It assumes the protocol's checkpoint artifacts, feature
scaling, labels, and coupled physics gate already exist. It requires Python with
NumPy and PyTorch available. The repository `.venv-em` currently has
PyNEC/NumPy/SciPy but no Torch, so use the installed CPU Torch interpreter (or
another environment containing both) for the benchmark run.
