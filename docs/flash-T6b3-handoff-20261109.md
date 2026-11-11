# Flash T6b3 Handoff: Production Mode for Package and Gate, plus Progress Checker

Date: 2026-11-09 WIB
Task: T6b3 (Flash worker handoff)
Contract: `docs/bench-production-full-layout-20261109.md`, `docs/bench-production-full-20261109.md` §3, §4, §6

---

## 1. What was done

1. **`scripts/package_bench_production.py` (`--production` mode):**
   - Added CLI arguments `--production`, `--manifest`, `--channel-run`.
   - Preserved exact pilot behavior when `--production` is omitted.
   - Validates manifest scope against `PRODUCTION_SCOPES` (`development_full`, `development_challenge`) via `registered_manifest` (with freeze check or synthetic bypass).
   - Validates `channel_run["case_manifest_sha256"] == manifest_sha256`.
   - Excludes all cases listed in `channel_run["maps"][map]["failed_cases"]` from packaging and records them under `failed_cases` / `excluded_failed_cases` in `provenance.json`.
   - Generates flip-gain labels strictly for frame positions `[0, 5, 10, 15]` of each case's 16-frame list; unlabelled frames remain in channels only and appear in `trajectories.parquet` with `labelled = False`.
   - Parents evaluated: `all_off` and `single_greedy`.
   - Pair coverage:
     - 64 elements: full 2,016 pairs (`pair_coverage = "full"`).
     - 128 elements: full 8,128 pairs (`pair_coverage = "full"`).
     - 256 elements: 4,096 deterministic sampled pairs per parent (`pair_coverage = "sampled"`), except full 32,640 pairs (`pair_coverage = "full"`) for the `all_off` parent on the first labelled frame (position 0) when `trajectory_index % 10 == 0`.
   - Extended `trajectories.parquet` with columns: `kind`, `scenario`, `trajectory_index`, `labelled`, `split`.
   - Splits:
     - `development_full`: trajectory indices 0–83 `train`, 84–101 `validation`, 102–119 `test`. Writes `splits/within_map_trajectory.json` and `splits/leave_environment_out.json` (3 geographic rotation folds: Munich, Rotterdam, Maastricht). Never writes challenge splits.
     - `development_challenge`: `split` column is `"challenge"`, writes `splits/challenge.json` with `"evaluation_only_never_mixed": true`. Never writes development fold files.
   - Set `package_role` in `provenance.json` to `"production_development"` or `"production_challenge"`.

2. **`scripts/verify_bench_production_gate.py` (`--production` mode):**
   - Added `--production` and `--trace-out` CLI options. Preserved exact pilot gate verification when `--production` is omitted.
   - Implemented `verify_production_gate` enforcing all §6.1 per-case/per-map criteria and §6.2 stop rule:
     - Complete schema (16 frames × 3 arrays in channel HDF5; labels for exactly frames `[0, 5, 10, 15]`).
     - Finite channel datasets, attributes, and label arrays.
     - Loader consistency: packaged `load_dataset.py` recomputed dense rate within $\le 10^{-10}$ bit/s/Hz for every array-frame.
     - LOS sanity: traced BS–RIS link is `los` for every included case; geometry agreement over served users $\ge 75\%$ per map.
     - Mesh preflight: `preflight_checks.all_passed == true` in trace case records.
     - Stop rule: fail-closed if `stop_rule_exceeded(failed, total)` is true on any map.
     - Fails closed on missing inputs and reports per-map counts, per-check booleans, and failing cases with exact reasons.

3. **`scripts/check_bench_production_progress.py`:**
   - Read-only progress monitor printing JSON summary to stdout.
   - Reports per map: total cases, trace done / failed, channel shards done / failed per array (64, 128, 256), distinct failed cases, `stop_rule_exceeded`, and DONE/FAILED markers.
   - Scans `channel_out/workers/` for `w<K>.{RUNNING, DONE, FAILED}` worker markers.
   - With `--verify-finished`: performs per-case verification on all cases with 3 complete shards (sidecar SHA-256, finite datasets, dense rate within $10^{-10}$ via `HybridCoupledNetwork`, trace mesh preflight passed, BS–RIS LOS).

4. **`bench/CoupledRIS-Bench/examples/load_dataset.py`:**
   - Updated `load_network` to transparently accept both path/string and open `h5py.File` or `h5py.Group` objects.

5. **Test suite additions:**
   - `tests/test_bench_production_package_full.py`: covers labelled frame positions `[0, 5, 10, 15]`, audit rule for 256 elements (`i % 10 == 0`), exclusion of failed cases, and natural vs. challenge splits.
   - `tests/test_bench_production_gate_full.py`: covers gate pass on valid fixture and gate rejection on 7 crafted defects (missing frame, NaN, rate error $10^{-9}$, preflight false, BS–RIS NLOS, 74% agreement, stop-rule breach).
   - `tests/test_bench_production_progress.py`: covers partial layout tracking, worker markers, and `--verify-finished` verification.

---

## 2. Changed and created files

- `scripts/package_bench_production.py` (modified)
- `scripts/verify_bench_production_gate.py` (modified)
- `scripts/check_bench_production_progress.py` (new)
- `bench/CoupledRIS-Bench/examples/load_dataset.py` (modified)
- `tests/test_bench_production_package_full.py` (new)
- `tests/test_bench_production_gate_full.py` (new)
- `tests/test_bench_production_progress.py` (new)

---

## 3. Test results

Full repository test suite ran via:
`PYTHONPATH=src:scripts .venv/bin/python -m unittest discover -s tests`

Result:
- **Ran 337 tests** (including 14 new tests in the 3 T6b3 test files and all existing pilot package/gate tests).
- **Result:** OK (failures=1, skipped=9).
- **The only failure** is the known, pre-existing CPU-math difference on AMD-kc host:
  `tests/test_matched.py::RankingIsTheOnlyDifference::test_memory_ga_ranking_uses_pattern_spread`.
- **Zero other failures or errors.** All new and existing production/pilot package and gate tests pass.

---

## 4. Exact gate checks and thresholds as implemented

In `scripts/verify_bench_production_gate.py`:

| Check Name | Target & Threshold | Implementation Reference |
|---|---|---|
| Complete HDF5 Schema | 16 frames × 3 arrays per included case; labels exist for exactly positions `[0, 5, 10, 15]`, parents `all_off` and `single_greedy`; pair count $N(N-1)/2$ for 64/128, 32,640 for 256 all-OFF at frame 0 with `i % 10 == 0`, 4,096 otherwise. | `verify_bench_production_gate.py#L484-L497`, `#L540-L586` |
| Finite Values | Datasets `H_direct`, `C_in`, `C_out`, `Z_effective`, `loads`, `precoder`, `stored_bits`, attrs `noise` (> 0), `stored_rate_bps_hz`, and all label arrays are finite with zero NaNs / infinities. | `verify_bench_production_gate.py#L498-L507`, `#L563-L565`, `#L587-L589` |
| Loader Consistency | Recomputed dense mutual-coupling rate using packaged loader matches `stored_rate_bps_hz` with absolute error $\le 10^{-10}$ bit/s/Hz. | `verify_bench_production_gate.py#L510-L523` |
| BS–RIS LOS | Traced BS–RIS link classification `link_classes.bs_ris == "los"` for every included case and frame. | `verify_bench_production_gate.py#L530-L534` |
| LOS Geometry Agreement | $\text{matches} / \text{total} \ge 0.75$ (75%) per map across served users in `geometry_agreement` for both BS and RIS. | `verify_bench_production_gate.py#L535-L537`, `#L599-L601` |
| Mesh Preflight | Every included case's trace case record has `geometry.preflight_checks.all_passed == true`. | `verify_bench_production_gate.py#L466-L473`, `#L604-L605` |
| Stop Rule (§6.2) | `stop_rule_exceeded(failed_count, total_cases)` must be `False` for each map (strictly $> 2\%$ failure threshold: $>2/120$ for natural, $\ge 1/23$ for challenge). | `verify_bench_production_gate.py#L607-L609` |
| Fail-Closed Integrity | Any missing input path, hash mismatch (manifest, channel HDF5, metadata, labels, loader, parquet, splits), or incomplete marker triggers fail-closed status. | `verify_bench_production_gate.py#L281-L410` |

---

## 5. Items in the contract not followed

None. All contract specifications in `docs/bench-production-full-layout-20261109.md` and declaration sections §3, §4, and §6 were followed exactly.
