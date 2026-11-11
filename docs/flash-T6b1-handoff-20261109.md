# Flash Task T6b1 Handoff: Production Mode for Trace Stage

**Date:** 2026-11-09  
**Worker:** Flash worker (T6b1)  
**Lead:** Coordinator  
**Target:** Production trace stage (`scripts/run_bench_production_trace.py`, wrapper `scripts/run_bench_production_full_trace.sh`, tests `tests/test_bench_production_trace_full.py`)

---

## 1. Files Changed & Added

1. **`scripts/run_bench_production_trace.py`**
   - Added `--production`, `--maps`, `--retry-failed`, and `--smoke-unregistered` flags.
   - Preserved byte-for-byte pilot behavior when `--production` is absent (retains frame-0 check, `scenes/<map>/` path, GPU 0 lock).
   - Generalized `verify_case_manifest`:
     - Rejects production scopes without `--production`.
     - Rejects pilot scopes with `--production`.
     - Enforces 16 frames per case in production (unless `--smoke-unregistered`), checking finite xyz coordinates for all frames' users, BS, RIS, and unit normal.
   - Generalized `_munich_scene`, `_three_dbag_scene`, `_rotterdam_scene`, `_maastricht_scene`, and `build_scene`:
     - In production mode, uses per-case scene directory (`TRACE_ROOT/scenes/<map>/<case_id>/`) and passes all frames' users to crop anchors, `validate_case_geometry`, and endpoint preflight.
     - Writes `scene_info.json` beside `scene.xml`.
     - In pilot mode, keeps frame-0 users and map-level scene directory (`TRACE_ROOT/scenes/<map>/`).
   - Generalized `trace_one` and `extract_npz`:
     - Accepts arbitrary frame dict and `gpu_id` (0 or 1).
     - GPU preflight check and `GpuSampler` sample the designated GPU.
     - Exports to `TRACE_OUT/<map>/n<N>/<case_id>/frame-<FFFF>.npz` where `FFFF` is the 4-digit zero-padded original frame index.
     - `extract_npz` writes metadata with correct `frame` index and frame-specific UE order in `tx_order` and `rx_order`.
   - Factored production loop into `run_production_trace`:
     - Injectable `scene_builder_fn` and `trace_one_fn` for GPU-free testing.
     - Non-blocking flock on `TRACE_ROOT/gpu<K>.lock` and `TRACE_OUT/<map>/trace.lock`.
     - Drops CPU cores 5 and 11 from affinity.
     - Per-case resume: skips cases where record exists and all 48 NPZs verify (bytes and sha256); skips FAILED cases unless `--retry-failed` (which renames `.FAILED.json` to `.FAILED.prev.json`).
     - Exception isolation: writes `<case_id>.FAILED.json`, purges partial NPZs for that case, and continues.
     - Preregistered fail-closed stop rule `stop_rule_exceeded(failed, total)` stops map and writes `TRACE_OUT/<map>/FAILED` if exceeded.
     - Atomic case record write (`<case_id>.json`) last.
     - Writes `TRACE_OUT/<map>/trace_manifest.json` and `TRACE_OUT/<map>/DONE` upon map completion.

2. **`scripts/run_bench_production_full_trace.sh`**
   - Tmux job wrapper script accepting `REPO TRACE_ROOT MANIFEST TRACE_OUT GPU_ID MAPS [EXTRA_ARGS...]`.
   - Uses `taskset -c 3,9` and pinned Python `/mnt/home/faris/projects/atom-wise-ris/.venv/bin/python` (or `$PYTHON`).
   - Writes `TRACE_OUT/RUNNING`, `TRACE_OUT/JOB_DONE` (on success), `TRACE_OUT/JOB_FAILED` (on failure), and logs to `TRACE_OUT/trace-job.log`.
   - Safe to rerun: skips finished maps and resumes per case.

3. **`tests/test_bench_production_trace_full.py`**
   - 9 test cases covering:
     - `test_production_vs_pilot_manifest_acceptance`: rejects invalid cross-scope invocations, validates 16 frames and user xyz.
     - `test_production_anchors_include_every_frames_users`: validates anchors include all 64 users across 16 frames in production vs 4 users in pilot.
     - `test_npz_naming_and_frame_metadata`: validates 4-digit zero-padded naming (`frame-0007.npz`) and metadata `frame` index and `tx_order`/`rx_order`.
     - `test_resume_skips_verified_case_and_retraces_on_hash_mismatch`: verifies skip on valid hash, re-trace on NPZ corruption.
     - `test_failed_skip_and_retry_failed`: verifies `.FAILED.json` skip and `--retry-failed` rename to `.FAILED.prev.json`.
     - `test_stop_rule_thresholds_120_cases`: 2/120 failures still passes to `DONE` with `failed_cases`; 3/120 failures exceeds stop rule and writes `FAILED`.
     - `test_stop_rule_thresholds_23_cases`: 1/23 failure exceeds stop rule and writes `FAILED`.
     - `test_per_map_trace_manifest_fields`: verifies `status`, `run_scope`, `case_manifest_sha256`, `map_id`, `cases`, `failed_cases`.
     - `test_pilot_path_is_unchanged`: verifies pilot directories and frame-0 checks remain intact.

---

## 2. Test Results

- **New production trace unit tests:**
  `PYTHONPATH=src:scripts .venv/bin/python -m unittest tests/test_bench_production_trace_full.py`
  - **Result:** 9 tests passed (OK in 1.200s).

- **Existing pilot trace unit tests:**
  `PYTHONPATH=src:scripts .venv/bin/python -m unittest tests/test_bench_production_trace.py`
  - **Result:** 14 tests passed (OK in 0.023s).

- **Full repository test suite:**
  `PYTHONPATH=src:scripts .venv/bin/python -m unittest discover -s tests`
  - **Result:** 337 tests ran, 336 passed, 1 failure (known pre-existing `tests/test_matched.py::RankingIsTheOnlyDifference::test_memory_ga_ranking_uses_pattern_spread`), 9 skipped.

---

## 3. Remote Smoke Check on 3060-3

Executed on host `labkc-comm3` (3060-3) on GPU 0 using `taskset -c 3,9` in scratch directory `/mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/`:

### Setup
- Staged code: rsync of `src scripts configs bench docs` to the scratch dir.
- City source: symlinked `raw/` to `/mnt/home/faris/projects/bench-production-pilot-20261109/trace-work/raw` (existing `690_5334.gml` CityGML mesh).
- Geometry reference: copied `outputs/previews/bench-users-v1.1` from `bench-production-pilot-20261109/trace-src/outputs/previews/bench-users-v1.1`.
- Built 1-case sub-manifest: `munich-v11-0000` with 2 frames (original indices 0 and 28).

### Command
```bash
taskset -c 3,9 env PYTHONPATH=src:scripts \
  /mnt/home/faris/projects/atom-wise-ris/.venv/bin/python scripts/run_bench_production_trace.py \
  --production \
  --root /mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke \
  --manifest /mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/smoke_cases.json \
  --out /mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/out \
  --gpu-id 0 \
  --maps munich \
  --smoke-unregistered
```

### Timings & Outputs
- **Total run time:** ~19.0 seconds.
- **Scene build & geometry preflight:** ~3.5 seconds.
- **Per-array & frame trace timings:**
  - `frame-0000.npz`:
    - N=64: elapsed 0.727s (solver: 0.362s, export: 0.365s), 333,338 bytes
    - N=128: elapsed 1.071s (solver: 0.521s, export: 0.550s), 515,307 bytes
    - N=256: elapsed 2.723s (solver: 1.746s, export: 0.959s), 915,227 bytes
  - `frame-0028.npz`:
    - N=64: elapsed 0.443s (solver: 0.085s, export: 0.357s), 325,740 bytes
    - N=128: elapsed 0.662s (solver: 0.089s, export: 0.553s), 502,484 bytes
    - N=256: elapsed 1.039s (solver: 0.105s, export: 0.934s), 893,036 bytes
  - **Total solve+export for all 6 NPZs:** ~6.67 seconds.

### Per-Case Scene Size
Located at `/mnt/home/faris/projects/bench-production-full-20261109/t6b1-smoke/scenes/munich/munich-v11-0000/`:
- `GroundSurface.ply`: 277,902 bytes (2,535 triangles)
- `RoofSurface.ply`: 411,659 bytes (3,732 triangles)
- `WallSurface.ply`: 771,593 bytes (6,917 triangles)
- Total mesh size: 1,461,154 bytes (1.39 MB), 13,184 semantic triangles.
- `scene.xml`: 705 bytes
- `scene_info.json`: 8,826 bytes

### Verification
- Verified all 6 NPZ files loaded and inspected:
  - `metadata_json["frame"]` matches original frame indices (0 and 28).
  - Transmitters: 4 BS ports + 4 UEs = 8.
  - Receivers: N RIS elements + 4 BS ports + 4 UEs = N + 8 (72, 136, 264).
  - Case record at `out/munich/cases/munich-v11-0000.json` has `status: "pass"` and `smoke: true`.
  - Trace manifest at `out/munich/trace_manifest.json` has `status: "complete"` and `failed_cases: []`.
  - `out/munich/DONE` created.
  - Job wrapper `scripts/run_bench_production_full_trace.sh` tested on remote; exited 0 and wrote `out/JOB_DONE`.

---

## 4. Contract Deviations

None. Every requirement from `docs/bench-production-full-layout-20261109.md` and `docs/flash-T6b1-brief-20261109.md` was strictly implemented and verified.
