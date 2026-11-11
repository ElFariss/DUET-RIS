# Flash task T6b3: production mode for package and gate, plus a progress checker

Read `docs/flash-common-rules-20261109.md` first, then the contract `docs/bench-production-full-layout-20261109.md` (sections "Package and gate" and "Channels" for the input layout). Then read the declaration `docs/bench-production-full-20261109.md` §3, §4 and §6, including the challenge amendment at the end. Two other Flash workers are editing other files at the same time:
- the trace script (T6b1);
- the channel script (T6b2).

Touch only the files listed below.

## Files you may change
- `scripts/package_bench_production.py`
- `scripts/verify_bench_production_gate.py`
- a new `scripts/check_bench_production_progress.py`
- the loader template that the package writes to `examples/load_dataset.py`, if it needs to handle the production layout
- new tests: `tests/test_bench_production_package_full.py`, `tests/test_bench_production_gate_full.py`, `tests/test_bench_production_progress.py`

Do not change `src/atomwise_ris/bench/production_run.py` or `production_pilot.py`; import from them.

## Task
**Without `--production`, the pilot behaviour of package and gate must stay exactly the same.**

1. **Package `--production`:**
   - Arguments: `--production --manifest M --channels C/channel_realizations.h5 --metadata C/metadata.json --channel-run C/channel_run.json --output C/package`.
   - Validate the scope with `registered_manifest`; it must be in `PRODUCTION_SCOPES`. The channel_run `case_manifest_sha256` must equal the manifest hash.
   - Exclude every case in `channel_run["maps"][map]["failed_cases"]`, and list them in `provenance.json`.
   - **Labels** exactly as the contract and declaration §3 state:
     - labelled frames are positions `[0, 5, 10, 15]` of each case's frame list;
     - parents are all-OFF and single greedy (`greedy_depth` as in the pilot);
     - 64 and 128 get all pairs;
     - 256 gets 4,096 deterministic sampled pairs per parent, with the same pair-seed rule as the pilot, except all 32,640 pairs for the all-OFF parent on the first labelled frame when the trajectory index (the 4-digit id suffix) satisfies `i % 10 == 0`;
     - unlabelled frames still appear in `trajectories.parquet` with `labelled = False`.
   - **`trajectories.parquet`** adds the columns `kind`, `scenario` (null for natural), `trajectory_index`, `labelled` and `split`.
   - **Splits:**
     - `development_full`: within each map, index 0–83 `train`, 84–101 `validation`, 102–119 `test`. Write `splits/within_map_trajectory.json` with exactly those lists, and `splits/leave_environment_out.json` with the three folds of declaration §4.1.
     - `development_challenge`: split `challenge` for every row, and `splits/challenge.json` with `"evaluation_only_never_mixed": true`. No folds.
   - `package_role` is `"production_development"` or `"production_challenge"`.
   - Labelling cost: at full size, labels are a few minutes (the pilot measured ~0.1 s per array-frame). A single process is fine.
2. **Gate `--production`:** `verify_bench_production_gate.py --production --manifest M --trace-out T --channel-run C/channel_run.json --metadata C/metadata.json --package C/package --output C/production_gate.json`. Apply declaration §6.1 per case and per map:
   - **Schema:** every included case has 16 frames × 3 arrays in the channel HDF5. The labels exist for exactly the labelled frames and parents, with the full or sampled coverage the plan requires.
   - **Finite:** all channel datasets and labels are finite.
   - **Loader:** using the packaged loader, the recomputed dense rate equals `stored_rate_bps_hz` within 1e-10 for **every** array-frame.
   - **LOS sanity:** the traced BS–RIS link is LOS for every included case. Binary LOS agreement between traced classes and geometry labels, over served users (both the BS and RIS agreement lists in metadata), is ≥ 75% per map.
   - **Mesh preflight:** every included case's trace record `geometry` has `preflight_checks.all_passed == true`.
   - **Stop rule (§6.2):** for each map, `stop_rule_exceeded(failed, total)` must be false.
   - The output has `status` `pass` or `fail`, per-map counts, per-check results, and the list of failing cases with reasons. It **fails closed** on any missing input. Do not loosen any threshold.
3. **`scripts/check_bench_production_progress.py --manifest M --trace-out T --channel-out C [--verify-finished]`:** works on partial outputs at any time while production runs. It is read-only, except for writing its JSON to stdout.
   - Per map, it reports: total cases; trace records / trace FAILED; per array, channel shards done / FAILED; distinct failed cases; `stop_rule_exceeded`; and the DONE/FAILED markers for trace and channel. Worker markers come from `C/workers/`.
   - **`--verify-finished`:** for every case with all 3 shards, re-run the per-case checks:
     - sidecar sha256;
     - finite datasets;
     - the dense rate within 1e-10 via `HybridCoupledNetwork`, rebuilt the way the packaged loader does;
     - trace mesh preflight passed;
     - BS–RIS LOS.

     Print per-case pass/fail with reasons.
   - Optional `--maps` and `--max-cases` limit the work.
4. **Tests** with tiny synthetic inputs, no real data. Reuse the synthetic pattern that existing package tests use (look in `tests/` for the pilot package tests). Cover:
   - the label-frame positions and the audit rule (`i % 10 == 0` → full 32,640 at 256 on the all-OFF parent and the first labelled frame only);
   - failed cases excluded;
   - natural vs challenge splits, and that challenge never appears in the natural split files;
   - each gate check fails on a crafted defect: a missing frame, a NaN, a rate off by 1e-9, a preflight false, BS–RIS NLOS, LOS agreement of 74%, a stop-rule breach;
   - the progress script on a partial layout.

   Synthetic tests may use small arrays (for example N=4) through injectable parameters, but the production defaults must be the declared values. Run the full suite.

## Do not
- run anything on 3060-3;
- edit the trace or channel scripts.

## Hand-back
`docs/flash-T6b3-handoff-20261109.md`, with:
- the changed files and test result;
- the exact gate checks and thresholds as implemented, with line references;
- anything in the contract you could not follow.
