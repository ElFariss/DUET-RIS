# Flash task T7: stage and launch full production on 3060-3

Read `docs/flash-common-rules-20261109.md` first. Then read:
- the contract `docs/bench-production-full-layout-20261109.md`;
- the hand-backs `docs/flash-T6b1-handoff-20261109.md`, `docs/flash-T6b2-handoff-20261109.md` and `docs/flash-T6b3-handoff-20261109.md`.

The lead has reviewed T6b, and the code in this checkout is the approved code. **Do not edit any code in this task.** If something does not work, stop and report it.

## Scopes and manifests (both registered)
- **Natural:** `outputs/runs/bench_production_full_20261109/cases.json`, sha256 `21d54cfbf1db69721aedf89144afb95a38a5c7f0bafc9c0ee24273d445203adf`, scope `development_full`.
- **Challenge:** `outputs/runs/bench_production_full_20261109/challenge_cases.json`, sha256 `999d221ef4b3ac46ad7a66871cd176470d38cd08faac051159826b4575205f91`, scope `development_challenge`.

## Remote layout (3060-3, user faris; `ssh -o BatchMode=yes -p 2003 gpu-labkc.ub.ac.id`)
Let `B=/mnt/home/faris/projects/bench-production-full-20261109` and `V=/var/tmp/atomwise-bench-production-full-20261109`.

**Trace side, under `$B`:**
- `$B/src-stage/`: rsync from this checkout of `src scripts configs bench docs`, `outputs/previews/bench-users-v1.1` (needed: `verify_freeze()` checks those frozen files and the trace builder reads the v1.1 references), and the two manifests (keep repo-relative paths). Write `$B/src-stage/STAGED_SHA256SUMS` over every staged file and check it. Do NOT stage `outputs/runs/*/cases/` directories (not needed; manifests are compact).
- `$B/trace-work/`: TRACE_ROOT. Copy (not move) `raw/` from `/mnt/home/faris/projects/bench-production-pilot-20261109/trace-work/raw`. Do not modify anything in the pilot directories.
- `$B/trace-natural/` and `$B/trace-challenge/`: TRACE_OUT per scope.

**Channel side, under `$V`:**
- The same staged code (rsync from `$B/src-stage`, including `STAGED_SHA256SUMS`).
- `deps/` copied from `/var/tmp/atomwise-bench-production-channel-20261109/deps`. Required: `.venv-em` has no h5py/pyarrow/pandas; the channel launcher puts `$V/deps` first on PYTHONPATH when it exists. Do not include `deps/` in STAGED_SHA256SUMS mismatch-prone ways: generate STAGED_SHA256SUMS on `$V` after copying, covering the staged code and manifests (not deps).
- `bench/CoupledRIS-Bench/physics` copied from the same pilot workspace.
- `$V/channels-natural/` and `$V/channels-challenge/`: CHANNEL_OUT per scope.

Before launch, check that the staged manifests' sha256 equal the values above, and that `verify_freeze()` passes on the remote with both venvs:
- `/mnt/home/faris/projects/atom-wise-ris/.venv/bin/python` (trace);
- `/mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python` (channels, PyNEC).

## Launch: durable tmux sessions on 3060-3, named exactly
1. **`cris-trace-natural`:** `scripts/run_bench_production_full_trace.sh` for the natural manifest, GPU 0, all maps.
2. **`cris-trace-challenge`:** the same wrapper for the challenge manifest, GPU 1, all maps, with `TRACE_CPUS=4,10` in its environment (the wrapper defaults to `3,9` for natural).
3. **`cris-channels`:** one chain that runs in order:
   1. `scripts/run_bench_production_full_channels.sh` for natural, with `$V/channels-natural` (3 workers; the trace is still running, and the workers wait on trace records by design);
   2. the same launcher for challenge, with `$V/channels-challenge`;
   3. for each scope, on `taskset -c 4,10`: package `--production`, then gate `--production`, writing `production_gate.json`, then `sha256sum` over the outputs into `output_sha256sums`.
   4. `$V/PRODUCTION_DONE` or `$V/PRODUCTION_FAILED`, written atomically, with the stage and exit codes.

   Put this chain in a script `$V/run_production_chain.sh`, written on the remote (not in the repo), and show its full text in your hand-back. It must stop at the first failing stage and record which one.

Use `tmux new -d -s <name> '<cmd>'`. Never kill tmux sessions or processes by PID. Never touch any session you did not create.

## First-case verification (bounded; no LLM polling loops)
After launch, the first cases take a few minutes per map. Natural maps are traced in manifest order, so Munich comes first.
- Run `check_bench_production_progress.py` on the remote (with the `.venv-em` python and `PYTHONPATH=$V/deps:$V/src:$V/scripts`) at most **every 10 minutes**, with a hard limit of **90 minutes** in total, until **each of the three natural maps** has at least one case with all 3 channel shards. Then run it once with `--verify-finished --max-cases 3`.
- If after 90 minutes a map has no finished case, report that and how far it got; do not wait longer.
- Do the same for one challenge case if one is finished by then; otherwise, note that it is pending.
- **Check during this time:**
  - `nvidia-smi`: the GPUs are used by your trace processes only;
  - `taskset -cp` for every production process: none uses CPU 5 or 11;
  - free memory;
  - channel per-frame seconds against the pilot (64: ~3 s; 128/256: ~11–15 s per frame).
- **Projection:** from the observed trace and channel rates, give the projected finish time for natural, challenge and the whole chain. If the projected total wall time from now exceeds **72 h**, say so prominently.

## Resume manifest
Write `outputs/runs/bench_production_full_20261109/resume_manifest.json` locally, with:
- hosts, paths, tmux session names;
- manifest hashes;
- staged code `STAGED_SHA256SUMS` hash;
- the exact launch commands;
- the progress-check command;
- how to resume each stage after a crash. All stages resume per case: rerun the same command, and a stale `RUNNING` marker may need removal; say exactly which marker files block a rerun;
- the stop rule;
- the marker paths for DONE/FAILED per map and per stage.

Also copy the first progress JSON outputs (small) to `outputs/runs/bench_production_full_20261109/progress/`.

## Do not
- edit code;
- loosen anything;
- use CPUs 5 or 11, 3060-1 compute, or 3060-2;
- copy raw npz or HDF5 back to this host (`/home` has ~8 GB free).

## Hand-back
`docs/flash-T7-handoff-20261109.md`, with:
- what was staged;
- the sessions running;
- the first-case results per map, with the numbers;
- the observed rates and projection;
- the exact check and resume commands for the user;
- any problem.

## Lead notes (verified before this task)
- A real smoke (trace → array-64 channel → progress) passed on 3060-3 on 2026-11-09: NEC basis 64 built in 209 s, 3.9 s per Munich frame, peak RSS 3.5 GB. Expect the basis builds for 128 and 256 to take ~28–32 min each before the first 128/256 shards appear. So a case with all 3 shards will appear about 35–45 min after the first trace record. Plan your 10-minute checks accordingly.
- `--verify-finished` only verifies cases that have all 3 shards.
- Leave the smoke dirs (`$B/t6b1-smoke`, `/var/tmp/atomwise-bench-production-full-t6b2-smoke`) alone.
