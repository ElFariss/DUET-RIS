# Flash task T6b2: production mode for the channel stage (parallel workers, resume, stop rule)

Read `docs/flash-common-rules-20261109.md` first, then the contract `docs/bench-production-full-layout-20261109.md` (section "Channels"). Follow the contract exactly; other tasks depend on it. Two other Flash workers are editing other files at the same time:
- the trace script (T6b1);
- the package, gate and progress scripts (T6b3).

Touch only the files listed below.

## Files you may change
- `scripts/build_bench_production_channels.py`
- a new `scripts/run_bench_production_full_channels.sh` (launches the workers)
- a new `tests/test_bench_production_channels_full.py`

Do not change `src/atomwise_ris/bench/production_run.py`, `production_pilot.py` or `production_channel.py`; import from them.

## Task
Add a `--production` mode to `scripts/build_bench_production_channels.py` for the scopes `development_full` and `development_challenge`. **Without `--production`, the pilot `--array` / `--assemble` behaviour must stay exactly the same.**

1. **Worker mode:** `--production --manifest M --trace-out T --out C --physics P --worker-id K --arrays 128,256,64 --cpus 0,6`.
   - On start: `verify_freeze()`, `registered_manifest()` (the scope must be in `PRODUCTION_SCOPES`), and `check_cpu_set(--cpus)`. Apply `os.sched_setaffinity(0, cpus)`, and refuse to start if the resulting affinity contains 5 or 11.
   - For each array in preference order, loop:
     1. Find eligible units `(map, N, case)` in manifest order:
        - the trace case record `T/<map>/cases/<case_id>.json` exists with `status == "pass"` and the scope's `case_manifest_sha256`;
        - the unit is not done (`array_<N>.h5` + `.json` verify: the sidecar `h5_sha256` matches and the manifest hash matches);
        - the unit is not FAILED;
        - the map has no `C/<map>/FAILED` and no `T/<map>/FAILED`.
     2. Claim each unit with a non-blocking `fcntl.flock` on `C/claims/<map>/<N>/<case_id>.lock`. Skip it if the lock is busy.
     3. Build `RisBasis` for N **lazily**: only when the first claimable unit for N appears. Check `MemAvailable` ≥ 16 GiB first, and fail the worker cleanly if not. Free the basis before moving to the next array.
     4. Process the unit with the **same per-frame logic** as `write_array`. Factor a shared `channel_frame(...)` used by both pilot and production, so the physics stays identical:
        - check each trace npz against the case record's sha256/bytes;
        - `frame_inputs` checks;
        - `project_rays`;
        - the dense round-trip ≤ 1e-10;
        - the same datasets, attrs and metadata record.

        Write to `C/<map>/cases/<case_id>/array_<N>.h5.tmp`, rename it, then write the sidecar atomically and last.
     5. On any exception in a unit: write `array_<N>.FAILED.json` with the error, remove the tmp file, and continue. Then recompute the map's failed-case count (the trace FAILED files plus the channel FAILED files, counted per distinct case). If `stop_rule_exceeded`, write `C/<map>/FAILED`.
     6. After each unit, if the map is complete as the contract defines it, write `C/<map>/DONE` under a map lock (`C/<map>/map.lock`).
   - **When nothing is eligible:**
     - if any in-scope map's trace is neither `DONE` nor `FAILED`, sleep 60 s and retry;
     - otherwise, move to the next array;
     - after the last array, exit 0.
   - Worker markers: `C/workers/w<K>.RUNNING`, then `w<K>.DONE` or `w<K>.FAILED`.
2. **`--production --assemble`:** requires every map in the manifest to be `C/<map>/DONE`. It writes `channel_realizations.h5`, `metadata.json` and `channel_run.json`, as in the contract, from the per-case shards, excluding failed cases. It refuses to overwrite.
3. **Launcher:** `scripts/run_bench_production_full_channels.sh REPO MANIFEST TRACE_OUT CHANNEL_OUT PHYSICS`.
   - It starts 3 workers as background processes inside the one tmux job, with the contract's CPU sets and array orders: w0 `0,6` `128,256,64`; w1 `1,7` `256,128,64`; w2 `2,8` `64,128,256`.
   - Each worker runs under `taskset -c`, `ulimit -v 25165824`, and `OPENBLAS/MKL/OMP_NUM_THREADS=1`.
   - Use `PYTHON` or `/mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python`.
   - It waits for all workers, then runs `--assemble` if every map is DONE. It writes `CHANNEL_OUT/JOB_DONE` or `CHANNEL_OUT/JOB_FAILED` (with the per-worker exit codes).
   - It is safe to rerun (resume).
   - Model it on `scripts/run_bench_production_channel_job.sh`, including the conflicting-timing-process guard and the `sha256sum -c STAGED_SHA256SUMS` check when that file exists.
4. **Tests** (no NEC, no real data). Make the basis builder and the per-frame function injectable, and use fakes plus tiny fake trace records in a temp dir. Cover:
   - eligibility waits for the trace record;
   - done units are skipped and a corrupted sidecar hash is not;
   - two workers never process the same unit (flock);
   - the basis is built lazily, once per array;
   - a unit failure writes FAILED and continues;
   - the stop rule writes the map FAILED (3/120 yes, 2/120 no; 1/23 yes), and trace failures count;
   - map DONE only when complete;
   - assemble excludes failed cases and refuses when a map is not DONE;
   - CPUs 5 and 11 are refused;
   - the pilot path is unchanged (`--array` without `--production` still requires the pilot single `trace_manifest.json`).

   Run the full suite.
5. **Real smoke check on 3060-3** (bounded; CPUs `0,6`). It may need trace files: if T6b1's smoke output exists at `/mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/`, use it. Otherwise, skip the real smoke and say so. In a scratch dir `/var/tmp/atomwise-bench-production-full-t6b2-smoke/`, run one worker on array 64 only, using an unregistered-smoke escape hatch: a hidden `--smoke-unregistered` flag, allowed only when the output path contains `t6b2-smoke`. Report the per-frame channel seconds and peak RSS. Copy `bench/CoupledRIS-Bench/physics` from `/var/tmp/atomwise-bench-production-channel-20261109/` (the pilot workspace; read-only use, do not modify it).

## Do not
- launch production;
- edit the trace, package or gate scripts.

## Hand-back
`docs/flash-T6b2-handoff-20261109.md`, with:
- the changed files and test result;
- the smoke result or why it was skipped;
- anything in the contract you could not follow.
