# Flash task T1: state audit and cleanup of interrupted edits

Read `docs/flash-common-rules-20261109.md` first.

## Background
Two earlier workers were interrupted mid-work:
- **Codex** hit a usage limit at about 09:45 WIB while editing.
- **agy (Argon)** was interrupted at about 11:30 WIB by a host restart, after writing `docs/bench-production-mesh-policy-20261109.md` and changing `scripts/run_bench_production_trace.py` and `bench/CoupledRIS-Bench/README.md`.

These files changed after 09:41 and may be half-finished:
- `scripts/verify_bench_production_gate.py`
- `scripts/build_bench_production_channels.py`
- `scripts/package_bench_production.py`
- `scripts/run_bench_production_channel_job.sh`
- `scripts/run_bench_production_channel_after_trace.sh`
- `scripts/build_bench_production_cases.py`
- `scripts/run_bench_production_trace.py`
- `docs/bench-production-pilot-20261109.md`
- `src/atomwise_ris/bench/production_pilot.py` (new)

## Your task
1. Run the test suite and record the result.
2. For each file above, read it and decide whether it is complete and consistent: syntax, imports, unfinished functions, TODOs, call sites that don't match. Codex's last visible edits added checks that the pilot case manifest hash and pilot identity are approved; check those are complete.
   - Fix only clear breakage: a syntax error, an obviously unfinished function body, a broken import.
   - If a fix needs a design decision, do not guess. List it in the hand-back.
3. Re-run the suite until green, or report exactly what still fails.
4. **Read-only remote check on 3060-3:** list tmux sessions, then for each of these workspaces list any `WAITING`, `RUNNING`, `DONE`, `FAILED` or `DEPENDENCY_FAILED` marker files and their contents:
   - `/mnt/home/faris/projects/bench-production-pilot-20261109/` (recursively, depth 2);
   - `/var/tmp/atomwise-bench-production-channel-20261109`.

   Also report free disk (`df -h /mnt/home /var/tmp`), free RAM and GPU state (`nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv`).
   **Start nothing.**

## Do not
- run any pilot or production stage;
- edit tests to force a pass;
- edit the frozen generator files.

## Hand-back
`docs/flash-T1-handoff-20261109.md`
