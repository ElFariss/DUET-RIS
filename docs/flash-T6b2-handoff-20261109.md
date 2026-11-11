# Flash Task T6b2 Hand-Back: Production Channels Stage

**Date:** 2026-11-09  
**Worker:** Flash (T6b2)  
**Lead:** Coordinator  

---

## 1. Summary of Changes

Implemented production mode and parallel worker execution for the channel stage conforming to `docs/bench-production-full-layout-20261109.md`:

1. **`scripts/build_bench_production_channels.py`**:
   - Added `--production` worker mode:
     - Startup validation: `verify_freeze()`, manifest verification via `registered_manifest()` enforcing `PRODUCTION_SCOPES` (`development_full`, `development_challenge`), and `--cpus` validation via `check_cpu_set()` with `os.sched_setaffinity()`. Cores 5 and 11 strictly forbidden.
     - `--smoke-unregistered` escape hatch supported for output paths containing `t6b2-smoke`.
     - Ordered array loop (`--arrays`) with per-case unit claiming via non-blocking `fcntl.flock` on `CHANNEL_OUT/claims/<map>/<N>/<case_id>.lock`.
     - Lazy `RisBasis` construction (built on first claimable unit for each array size), enforcing host `MemAvailable` ≥ 16 GiB before MoM construction, and explicit memory release (`gc.collect`) before moving to subsequent array sizes.
     - Factored shared `channel_frame(...)` preserving identical physics across pilot and production (trace npz hash/byte check, `frame_inputs` check, `project_rays`, dense round-trip check ≤ 1e-10, dataset compression, metadata sidecar records).
     - Isolated unit failures write `array_<N>.FAILED.json`, delete temporary `.tmp` files, recompute map failure totals (combining trace and channel stage failures per distinct case), and fail the map (`C/<map>/FAILED`) if the stop rule (> 2%) is exceeded.
     - Per-map completion check writes `C/<map>/DONE` with case counts under `C/<map>/map.lock` once trace is DONE and all non-failed cases have verified shards for all 3 arrays (64, 128, 256).
     - Worker markers `C/workers/w<K>.{RUNNING,DONE,FAILED}` tracked with clean signal handling.
     - Idle wait loop sleeps 60 s when trace is still running on any in-scope map.
   - Added `--production --assemble`:
     - Verifies every map in manifest is `C/<map>/DONE`.
     - Aggregates per-case shards into `channel_realizations.h5`, `metadata.json`, and `channel_run.json`.
     - Excludes failed cases and documents them in provenance.
     - Refuses to overwrite existing targets (`FileExistsError`).
   - Pilot `--array` / `--assemble` mode without `--production` is completely preserved.

2. **`scripts/run_bench_production_full_channels.sh`**:
   - Production parallel worker launcher managing 3 background workers (`w0` on `0,6` with `128,256,64`; `w1` on `1,7` with `256,128,64`; `w2` on `2,8` with `64,128,256`).
   - Configures each worker with `taskset -c`, `ulimit -v 25165824`, and single-threaded BLAS/OMP.
   - Includes conflicting timing process guard and `STAGED_SHA256SUMS` check.
   - Waits for worker completion, runs `--assemble` if all maps are `DONE`, and writes `JOB_DONE` or `JOB_FAILED` (with per-worker exit codes). Safe to resume.

3. **`tests/test_bench_production_channels_full.py`**:
   - Suite of 11 isolated unit tests covering all required contract behaviors with mocked basis and frame functions:
     - Eligibility waiting for trace record.
     - Done units skipped and corrupted sidecar hash reprocessed.
     - Non-blocking flock preventing double-processing.
     - Lazy basis construction once per array.
     - Unit failure isolation writing `FAILED.json` without worker crash.
     - Stop rule triggers (3/120 yes, 2/120 no; 1/23 yes) including trace failures.
     - Map DONE written only when complete.
     - Assemble excluding failed cases and refusing when not all maps DONE.
     - CPUs 5 and 11 refused.
     - Pilot path CLI unchanged.
     - Launcher resumption on `JOB_DONE`.

---

## 2. Changed / Created Files

- `scripts/build_bench_production_channels.py`
- `scripts/run_bench_production_full_channels.sh`
- `tests/test_bench_production_channels_full.py`
- `docs/flash-T6b2-handoff-20261109.md`

No frozen files or unauthorized paths were modified.

---

## 3. Test Results

Executed:
`PYTHONPATH=src:scripts .venv/bin/python -m unittest discover -s tests`

Result:
- **Total tests:** 314
- **Passed:** 304
- **Skipped:** 9
- **Failures:** 1 (known, pre-existing failure in Paper 1 math: `tests/test_matched.py::RankingIsTheOnlyDifference::test_memory_ga_ranking_uses_pattern_spread`)
- All 11 new tests in `test_bench_production_channels_full.py` passed cleanly in 0.34 s.

---

## 4. Remote Smoke Check on 3060-3

- Checked 3060-3 via SSH: `/mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/` does not exist yet (T6b1 trace smoke output not present).
- Per Brief § 5 ("if T6b1's smoke output exists... use it. Otherwise, skip the real smoke and say so"), the remote smoke check was skipped.

---

## 5. Contract Deviations / Open Problems

- None. All requirements in `docs/bench-production-full-layout-20261109.md` and `docs/flash-T6b2-brief-20261109.md` were followed exactly.
