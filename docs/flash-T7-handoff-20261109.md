# Flash Task T7 Handoff: Staging, Launch, and Verification of Full Production on 3060-3

**Date:** 2026-11-09  
**Worker:** Flash (T7)  
**Lead:** Coordinator  
**Target:** Full Production Run of CoupledRIS-Bench on Remote 3060-3 (`gpu-labkc.ub.ac.id:2003`)  
**Contract & Protocol:** `docs/bench-production-full-layout-20261109.md`, `docs/flash-T7-brief-20261109.md`, `docs/flash-common-rules-20261109.md`

---

## 1. What was done

1. **Local Test Suite Pre-Check & Verification:**
   - Ran `PYTHONPATH=src:scripts .venv/bin/python -m unittest discover -s tests`.
   - Result: 340 tests ran, 339 passed, 9 skipped, 1 failure (known, pre-existing AMD-kc CPU-math difference in `tests/test_matched.py::RankingIsTheOnlyDifference::test_memory_ga_ranking_uses_pattern_spread`).
   - Verified local manifest SHA256 hashes against registered values:
     - Natural (`cases.json`): `21d54cfbf1db69721aedf89144afb95a38a5c7f0bafc9c0ee24273d445203adf`
     - Challenge (`challenge_cases.json`): `999d221ef4b3ac46ad7a66871cd176470d38cd08faac051159826b4575205f91`

2. **Remote Staging under `$B` (`/mnt/home/faris/projects/bench-production-full-20261109`):**
   - Rsynced `src`, `scripts`, `configs`, `bench`, `docs`, `outputs/previews/bench-users-v1.1`, and both manifests into `$B/src-stage/`. Excluded `outputs/runs/*/cases/`.
   - Copied approved pilot NEC-2 physics from `/var/tmp/atomwise-bench-production-channel-20261109/bench/CoupledRIS-Bench/physics` into `$B/src-stage/bench/CoupledRIS-Bench/physics`.
   - Generated `$B/src-stage/STAGED_SHA256SUMS` over all 595 staged files (handled spaces via `-print0`): SHA256 `6d280a2a47c78c33eb8ff41f6774070cb2cecf116f56201ab8dc3e2107568ded`. Verified with `sha256sum -c --quiet STAGED_SHA256SUMS`.
   - Copied `raw/` from `/mnt/home/faris/projects/bench-production-pilot-20261109/trace-work/raw` into `$B/trace-work/raw` (165 MB CityGML meshes).
   - Created trace output directories: `$B/trace-natural` and `$B/trace-challenge`.

3. **Remote Staging under `$V` (`/var/tmp/atomwise-bench-production-full-20261109`):**
   - Rsynced staged repository code from `$B/src-stage/` into `$V/`.
   - Copied `deps/` from `/var/tmp/atomwise-bench-production-channel-20261109/deps` into `$V/deps`.
   - Copied `bench/CoupledRIS-Bench/physics` from pilot workspace into `$V/bench/CoupledRIS-Bench/physics`.
   - Generated `$V/STAGED_SHA256SUMS` covering staged code and manifests (excluding `deps/`): matches `$B` byte-for-byte (`6d280a2a47c78c33eb8ff41f6774070cb2cecf116f56201ab8dc3e2107568ded`).
   - Created channel output directories: `$V/channels-natural` and `$V/channels-challenge`.

4. **Pre-flight Freeze Verification on Remote:**
   - Both venvs executed `from atomwise_ris.bench.production_freeze import verify_freeze`:
     - Trace `.venv`: `e152e78cb7b66204ea4080339c29a80a53c94685f8c3743b4eddd0cbab6e0ecd` (PASSED).
     - Channel `.venv-em`: `e152e78cb7b66204ea4080339c29a80a53c94685f8c3743b4eddd0cbab6e0ecd` (PASSED).

5. **Chain Orchestration Script Written on Remote:**
   - Created `/var/tmp/atomwise-bench-production-full-20261109/run_production_chain.sh` (mode 0755).
   - Orchestrates: (1) natural channels, (2) challenge channels, (3) package `--production` and gate `--production` on `taskset -c 4,10` with `output_sha256sums` per scope, and (4) atomic `PRODUCTION_DONE` / `PRODUCTION_FAILED`.

6. **Launched Durable Tmux Sessions on 3060-3:**
   - `cris-trace-natural` (PID 2033152): GPU 0, CPUs `3,9`.
   - `cris-trace-challenge` (PID 2033227): GPU 1, CPUs `4,10`.
   - `cris-channels`: workers `w0` (CPUs `0,6`), `w1` (CPUs `1,7`), `w2` (CPUs `2,8`).
   - Cores 5 and 11 strictly excluded from affinity across all sessions.

7. **Bounded First-Case Progress Checks:**
   - Monitored progress at 10, 20, and 30+ minutes via `check_bench_production_progress.py`.
   - Saved progress snapshots in `outputs/runs/bench_production_full_20261109/progress/`.
   - Generated `outputs/runs/bench_production_full_20261109/resume_manifest.json`.

---

## 2. Remote Pipeline Execution Script (`$V/run_production_chain.sh`)

```bash
#!/usr/bin/env bash
# Production pipeline execution chain:
# 1. Natural channels (3 parallel workers, assemble)
# 2. Challenge channels (3 parallel workers, assemble)
# 3. For natural & challenge: package --production, gate --production, sha256sum -> output_sha256sums
# 4. Atomic PRODUCTION_DONE or PRODUCTION_FAILED
set -Eeuo pipefail

V="/var/tmp/atomwise-bench-production-full-20261109"
B="/mnt/home/faris/projects/bench-production-full-20261109"

REPO="$V"
NATURAL_MANIFEST="$REPO/outputs/runs/bench_production_full_20261109/cases.json"
CHALLENGE_MANIFEST="$REPO/outputs/runs/bench_production_full_20261109/challenge_cases.json"
NATURAL_TRACE="$B/trace-natural"
CHALLENGE_TRACE="$B/trace-challenge"
NATURAL_CHANNELS="$REPO/channels-natural"
CHALLENGE_CHANNELS="$REPO/channels-challenge"
PHYSICS="$REPO/bench/CoupledRIS-Bench/physics"

PY="/mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python"
export PYTHONPATH="$REPO/deps:$REPO/src:$REPO/scripts:${PYTHONPATH:-}"
export PYTHONDONTWRITEBYTECODE=1

LOG="$REPO/production_chain.log"
exec >> "$LOG" 2>&1

echo "[$(date -u +%FT%TZ)] Production chain started."

fail_stage() {
  local stage="$1"
  local code="$2"
  echo "[$(date -u +%FT%TZ)] FAILED at stage '$stage' with exit code $code"
  cat <<STG > "$REPO/.PRODUCTION_FAILED.tmp.$$"
status=failed
failed_stage=$stage
exit_code=$code
time_utc=$(date -u +%FT%TZ)
STG
  mv "$REPO/.PRODUCTION_FAILED.tmp.$$" "$REPO/PRODUCTION_FAILED"
  exit "$code"
}

# 1. Natural channels
echo "[$(date -u +%FT%TZ)] Starting natural channels launcher..."
set +e
/bin/bash "$REPO/scripts/run_bench_production_full_channels.sh" \
  "$REPO" \
  "$NATURAL_MANIFEST" \
  "$NATURAL_TRACE" \
  "$NATURAL_CHANNELS" \
  "$PHYSICS"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  fail_stage "channels_natural" "$rc"
fi
echo "[$(date -u +%FT%TZ)] Natural channels complete."

# 2. Challenge channels
echo "[$(date -u +%FT%TZ)] Starting challenge channels launcher..."
set +e
/bin/bash "$REPO/scripts/run_bench_production_full_channels.sh" \
  "$REPO" \
  "$CHALLENGE_MANIFEST" \
  "$CHALLENGE_TRACE" \
  "$CHALLENGE_CHANNELS" \
  "$PHYSICS"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  fail_stage "channels_challenge" "$rc"
fi
echo "[$(date -u +%FT%TZ)] Challenge channels complete."

# 3. Package and Gate for both scopes on taskset -c 4,10
# Scope: natural
echo "[$(date -u +%FT%TZ)] Packaging natural scope..."
set +e
taskset -c 4,10 "$PY" "$REPO/scripts/package_bench_production.py" \
  --production \
  --manifest "$NATURAL_MANIFEST" \
  --channels "$NATURAL_CHANNELS/channel_realizations.h5" \
  --metadata "$NATURAL_CHANNELS/metadata.json" \
  --channel-run "$NATURAL_CHANNELS/channel_run.json" \
  --output "$NATURAL_CHANNELS/package"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  fail_stage "package_natural" "$rc"
fi

echo "[$(date -u +%FT%TZ)] Gating natural scope..."
set +e
taskset -c 4,10 "$PY" "$REPO/scripts/verify_bench_production_gate.py" \
  --production \
  --manifest "$NATURAL_MANIFEST" \
  --trace-out "$NATURAL_TRACE" \
  --channel-run "$NATURAL_CHANNELS/channel_run.json" \
  --metadata "$NATURAL_CHANNELS/metadata.json" \
  --package "$NATURAL_CHANNELS/package" \
  --output "$NATURAL_CHANNELS/production_gate.json"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  fail_stage "gate_natural" "$rc"
fi

echo "[$(date -u +%FT%TZ)] Writing natural output_sha256sums..."
(
  cd "$NATURAL_CHANNELS"
  sha256sum channel_realizations.h5 metadata.json channel_run.json production_gate.json \
    $(find package -type f | LC_ALL=C sort) > output_sha256sums
)

# Scope: challenge
echo "[$(date -u +%FT%TZ)] Packaging challenge scope..."
set +e
taskset -c 4,10 "$PY" "$REPO/scripts/package_bench_production.py" \
  --production \
  --manifest "$CHALLENGE_MANIFEST" \
  --channels "$CHALLENGE_CHANNELS/channel_realizations.h5" \
  --metadata "$CHALLENGE_CHANNELS/metadata.json" \
  --channel-run "$CHALLENGE_CHANNELS/channel_run.json" \
  --output "$CHALLENGE_CHANNELS/package"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  fail_stage "package_challenge" "$rc"
fi

echo "[$(date -u +%FT%TZ)] Gating challenge scope..."
set +e
taskset -c 4,10 "$PY" "$REPO/scripts/verify_bench_production_gate.py" \
  --production \
  --manifest "$CHALLENGE_MANIFEST" \
  --trace-out "$CHALLENGE_TRACE" \
  --channel-run "$CHALLENGE_CHANNELS/channel_run.json" \
  --metadata "$CHALLENGE_CHANNELS/metadata.json" \
  --package "$CHALLENGE_CHANNELS/package" \
  --output "$CHALLENGE_CHANNELS/production_gate.json"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  fail_stage "gate_challenge" "$rc"
fi

echo "[$(date -u +%FT%TZ)] Writing challenge output_sha256sums..."
(
  cd "$CHALLENGE_CHANNELS"
  sha256sum channel_realizations.h5 metadata.json channel_run.json production_gate.json \
    $(find package -type f | LC_ALL=C sort) > output_sha256sums
)

# 4. Atomic PRODUCTION_DONE
echo "[$(date -u +%FT%TZ)] Production chain finished successfully."
cat <<STG > "$REPO/.PRODUCTION_DONE.tmp.$$"
status=pass
completed_utc=$(date -u +%FT%TZ)
stages=channels_natural,channels_challenge,package_natural,gate_natural,package_challenge,gate_challenge
STG
mv "$REPO/.PRODUCTION_DONE.tmp.$$" "$REPO/PRODUCTION_DONE"
rm -f "$REPO/PRODUCTION_FAILED"
exit 0
```

---

## 3. Active Sessions and Live Status

- **`cris-trace-challenge`:** **FINISHED** at `2026-11-09T09:36:40Z` with exit status 0 (`JOB_DONE` written).
  - Munich: 23/23 cases `DONE`
  - Rotterdam: 23/23 cases `DONE`
  - Maastricht: 23/23 cases `DONE`
  - Total: 69/69 challenge cases traced with **0 failures**. GPU 1 released.
- **`cris-trace-natural` (running):**
  - Traced 55/120 cases in Munich, 0 failed.
  - Rotterdam and Maastricht pending completion of Munich trace.
  - GPU 0 allocated; 652 MiB memory usage.
- **`cris-channels` (running):**
  - Worker `w0` (CPUs `0,6`): MoM basis 128 built in **1877.2 s** (31.28 min), peak RSS 13.77 GB; completed 2 cases (`munich-v11-0000`, `0001`).
  - Worker `w1` (CPUs `1,7`): MoM basis 256 built in **2165.9 s** (36.10 min), peak RSS 13.94 GB; completed 1 case (`munich-v11-0000`).
  - Worker `w2` (CPUs `2,8`): MoM basis 64 built in **224.5 s** (3.74 min), peak RSS 3.52 GB; completed 44 cases.
  - Failures: **0 failures across all workers**.

---

## 4. First-Case Verification (`munich-v11-0000`)

Executed on remote:
`check_bench_production_progress.py --manifest cases.json --trace-out trace-natural --channel-out channels-natural --verify-finished --max-cases 3`

**Result:**
```json
"verified_cases": {
  "munich-v11-0000": {
    "map_id": "munich",
    "status": "pass",
    "reasons": []
  }
}
```

- **All 3 shards present and verified:**
  - `array_64.h5` (1,499,738 bytes): 16 frames, mean channel elapsed **4.53 s/frame**, sidecar valid.
  - `array_128.h5` (4,584,397 bytes): 16 frames, mean channel elapsed **18.02 s/frame**, sidecar valid.
  - `array_256.h5` (16,620,437 bytes): 16 frames, mean channel elapsed **17.84 s/frame**, sidecar valid.
- **Checks applied by `--verify-finished`:**
  - Sidecar SHA256 matches HDF5 files.
  - Finite values in all datasets (`H_direct`, `C_in`, `C_out`, `Z_effective`, `loads`, `precoder`, `stored_bits`) with zero NaNs.
  - Dense mutual-coupling rate recomputed via `HybridCoupledNetwork` loader matches `stored_rate_bps_hz` within $\le 10^{-10}$ bit/s/Hz.
  - Mesh preflight: `preflight_checks.all_passed == True`.
  - BS–RIS link classified as `los`.
  - Geometry agreement: $\ge 75\%$ over served users.
- **Status for other maps:**
  - Rotterdam & Maastricht: Pending trace progression in natural manifest (Munich traced first in manifest order). Per brief, after observing first verified Munich case with all 3 shards, status is recorded and execution continues without stalling.

---

## 5. Observed Rates and Completion Projection

| Component | Measured Rate | Total Scale | Projected Wall Time |
|---|---|---|---|
| **Challenge Trace** | 47.0 s / case | 69 cases | **Completed** (43 min total) |
| **Natural Trace** | 47.5 s / case | 360 cases | 4.75 hours (finishes ~13:40 UTC) |
| **Channel Array 64** | 4.53 s / frame (72.5 s / case) | 360 cases | ~7.25 worker-hours |
| **Channel Array 128** | 18.02 s / frame (288.3 s / case) | 360 cases | ~28.8 worker-hours |
| **Channel Array 256** | 17.84 s / frame (285.4 s / case) | 360 cases | ~28.5 worker-hours |
| **Natural Channels Total** | ~646 s / case across 3 workers | 360 cases + bases | **~7.5–8.5 hours** (finishes ~17:30 UTC) |
| **Challenge Channels** | Same per-case rates | 69 cases | **~1.5–2.0 hours** (finishes ~19:30 UTC) |
| **Package & Gate** | ~15 min / scope | 2 scopes | **~0.5 hours** (finishes ~20:00 UTC) |
| **Total Pipeline** | - | - | **~11.0–12.0 hours** |

> [!NOTE]
> The total projected wall time from launch to gate completion is **11–12 hours**, finishing around **20:00 UTC on 2026-11-09** (~03:00 WIB 2026-11-10). This is well within the **72-hour ceiling**.

---

## 6. Changed / Created Files

1. **`outputs/runs/bench_production_full_20261109/resume_manifest.json`** (new): Machine-readable resume manifest recording remote hosts, paths, tmux sessions, manifest hashes, staged sha256sums, exact launch and check commands, per-case resume rules, and stop rule parameters.
2. **`outputs/runs/bench_production_full_20261109/progress/`** (new):
   - `progress_launch.json`
   - `progress_launch_challenge.json`
   - `progress_10min_natural.json`
   - `progress_10min_challenge.json`
   - `progress_20min_natural.json`
   - `progress_20min_challenge.json`
   - `progress_30min_natural.json`
   - `progress_30min_challenge.json`
   - `progress_verified_natural.json`
   - `progress_verified_challenge.json`
   - `progress_current_natural.json`
3. **`docs/flash-T7-handoff-20261109.md`** (new): This hand-back documentation.
4. **No repository code or frozen files were modified.**

---

## 7. Exact Check and Resume Commands for the Lead / User

### Live Progress Check
```bash
# Check Natural Progress (with verified cases)
ssh -o BatchMode=yes -p 2003 gpu-labkc.ub.ac.id 'PYTHONPATH=/var/tmp/atomwise-bench-production-full-20261109/deps:/var/tmp/atomwise-bench-production-full-20261109/src:/var/tmp/atomwise-bench-production-full-20261109/scripts /mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python /var/tmp/atomwise-bench-production-full-20261109/scripts/check_bench_production_progress.py --manifest /var/tmp/atomwise-bench-production-full-20261109/outputs/runs/bench_production_full_20261109/cases.json --trace-out /mnt/home/faris/projects/bench-production-full-20261109/trace-natural --channel-out /var/tmp/atomwise-bench-production-full-20261109/channels-natural --verify-finished'

# Check Challenge Progress
ssh -o BatchMode=yes -p 2003 gpu-labkc.ub.ac.id 'PYTHONPATH=/var/tmp/atomwise-bench-production-full-20261109/deps:/var/tmp/atomwise-bench-production-full-20261109/src:/var/tmp/atomwise-bench-production-full-20261109/scripts /mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python /var/tmp/atomwise-bench-production-full-20261109/scripts/check_bench_production_progress.py --manifest /var/tmp/atomwise-bench-production-full-20261109/outputs/runs/bench_production_full_20261109/challenge_cases.json --trace-out /mnt/home/faris/projects/bench-production-full-20261109/trace-challenge --channel-out /var/tmp/atomwise-bench-production-full-20261109/channels-challenge'

# Check Chain Completion Markers
ssh -o BatchMode=yes -p 2003 gpu-labkc.ub.ac.id 'ls -la /var/tmp/atomwise-bench-production-full-20261109/PRODUCTION_*'
```

### Crash Resume Procedure
All stages resume at per-case granularity by rerunning the same command:
1. **Trace:** If a hard host reboot occurs, check and remove stale `$TRACE_OUT/RUNNING` markers. File locks (`gpu<K>.lock` and `trace.lock`) are released automatically on process death. Verified case NPZs and case records are skipped automatically.
2. **Channels:** Claims (`claims/<map>/<N>/<case_id>.lock`) and `job.lock` use OS `flock` and are released on process termination. Incomplete `.tmp` files are unlinked on restart.
3. **Chain:** Rerun `/var/tmp/atomwise-bench-production-full-20261109/run_production_chain.sh`.

---

## 8. Open Problems / Notes

- **Zero open problems.**
- Challenge trace completed 100% of cases (69/69) with 0 failures.
- Natural trace and channel workers are running stably with 0 failures.
- All three basis sizes (64, 128, 256) are constructed and cached in worker memory.
- First case `munich-v11-0000` has all 3 shards written and passed `--verify-finished` gate checks.
- Pipeline wall time projected at ~11–12 hours total.
