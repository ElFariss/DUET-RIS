# Flash task T6b1: production mode for the trace stage

Read `docs/flash-common-rules-20261109.md` first, then the contract `docs/bench-production-full-layout-20261109.md` (section "Trace"). Follow the contract exactly; other tasks depend on it. Two other Flash workers are editing other files at the same time:
- the channel script (T6b2);
- the package, gate and progress scripts (T6b3).

Touch only the files listed below.

## Files you may change
- `scripts/run_bench_production_trace.py`
- a new `scripts/run_bench_production_full_trace.sh` (tmux job wrapper)
- a new `tests/test_bench_production_trace_full.py`

Do not change `src/atomwise_ris/bench/production_run.py` or `production_pilot.py`; import from them.

## Task
Add a `--production` mode to `scripts/run_bench_production_trace.py` for the registered scopes `development_full` and `development_challenge` (`PRODUCTION_SCOPES`). **Without `--production`, pilot behaviour must stay byte-for-byte the same:** same code path, same outputs.

1. **Manifest check:** `verify_case_manifest` accepts production scopes only when `--production` is given.
   - It requires 16 frames per case, each with users that have finite xyz, plus the same BS, RIS and normal checks as the pilot.
   - Production scopes without `--production`, and pilot scopes with it, must raise an error.
2. **Per-case scenes:** `TRACE_ROOT/scenes/<map>/<case_id>/` with `scene.xml`, the meshes and `scene_info.json`.
   - The crop anchors in `_munich_scene` / `_three_dbag_scene`, the `validate_case_geometry` users, and the endpoint preflight in `build_scene` must use **all frames'** users in production.
   - Do it by passing an explicit anchor-user list, or a `scene_dir`, as a parameter. The pilot call keeps frame-0 users and the old `scenes/<map>/` dir.
   - The mesh repair policy, the preflight thresholds and the fail-closed raise stay exactly as they are.
3. **Trace all frames:** generalize `trace_one` to take a frame dict and the GPU id.
   - The output is `TRACE_OUT/<map>/n<N>/<case_id>/frame-<FFFF>.npz`, and the record has `"frame": <index>`.
   - The GPU-free check and the sampler use the chosen GPU, not a hard-coded 0.
   - Solver settings are unchanged.
   - Check what `extract_npz` reads from the case (for example `frames[0]` users). In production it must use the traced frame's users, and the stored metadata must carry the right frame index. The channel stage checks `metadata_json["frame"]` and the UE coordinates/order against the manifest frame.
4. **Production loop,** per case in manifest order, filtered by `--maps`:
   - **Skip** a case if its record exists and every listed npz verifies (sha256 + bytes). Skip it if it has a FAILED file, unless `--retry-failed`.
   - **Otherwise:** build the scene (geometry preflight), then trace 16 frames × arrays 64/128/256, then write the case record atomically and last (`atomic_write_json`).
   - **Any exception** inside a case: write `<case_id>.FAILED.json` with the stage and error, delete that case's partial npz files, and continue with the next case. An exception outside a case (CUDA init, wrong Sionna version) aborts the run.
   - **After each case**, apply `stop_rule_exceeded(failed, cases_in_map)`. If exceeded, write `TRACE_OUT/<map>/FAILED` and stop that map.
   - **When every case of a map** has a record or a FAILED file and the stop rule holds, write `<map>/trace_manifest.json`, then `<map>/DONE`, as in the contract.
   - **Locking:** `--gpu-id` may be 0 or 1 in production (pilot stays locked to 0). Use a lock file per GPU (`TRACE_ROOT/gpu<K>.lock`) and per map (`TRACE_OUT/<map>/trace.lock`), both with non-blocking flock, so two processes can never trace the same map. Keep the CPU-affinity code that drops 5 and 11.
   - Factor the loop so the scene-build and trace-one functions are injectable. Unit tests then run the loop with fakes, without a GPU or Sionna.
5. **Job wrapper:** `scripts/run_bench_production_full_trace.sh REPO TRACE_ROOT MANIFEST TRACE_OUT GPU_ID MAPS`.
   - It uses `PYTHON` or `/mnt/home/faris/projects/atom-wise-ris/.venv/bin/python`, and `taskset -c 3,9`.
   - It writes a log, `TRACE_OUT/RUNNING` and, on exit, `TRACE_OUT/JOB_DONE` or `TRACE_OUT/JOB_FAILED` (exit status, time).
   - It is safe to rerun: resume is per case, and per-map markers make finished maps no-ops.
   - Model it on `scripts/run_bench_production_trace_job.sh`.
6. **Tests** (no GPU), in `tests/test_bench_production_trace_full.py`:
   - production vs pilot manifest acceptance;
   - production anchors include every frame's users;
   - the npz naming;
   - resume skips a verified case and re-traces a case whose npz hash is wrong;
   - FAILED skip and `--retry-failed`;
   - 3 failures out of 120 write the map's FAILED, and 2 failures out of 120 still give DONE with `failed_cases`;
   - 1 failure out of 23 stops the map;
   - the per-map trace manifest fields;
   - the pilot path is unchanged (for example, the old scene dir and frame-0 check).

   Run the full suite.
7. **Real smoke check on 3060-3** (allowed, bounded; GPU 0; `taskset -c 3,9`). In a scratch dir `/mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/`:
   - stage the current repo code (rsync `src scripts configs bench docs` to the scratch dir; no secrets; do not touch other remote dirs);
   - build a 1-case natural sub-manifest by hand **only for this smoke**. It cannot be registered, so add a hidden `--smoke-unregistered` flag that allows an unregistered manifest only with an output path containing `t6b1-smoke`, and that marks every record `"smoke": true`;
   - trace 2 frames × 3 arrays of `munich-v11-0000`.

   Report the timings and that the npz metadata frame index is right. Run it in the foreground; it should take minutes. If it needs data that is missing on the host (raw city sources), report what is missing and where the pilot got it (`/mnt/home/faris/projects/bench-production-pilot-20261109/trace-work`); do not download big datasets.

## Do not
- launch production;
- edit the channel, package or gate scripts.

## Hand-back
`docs/flash-T6b1-handoff-20261109.md`, with:
- the changed files and test result;
- the smoke result with timings and per-case scene size;
- anything in the contract you could not follow, and why.
