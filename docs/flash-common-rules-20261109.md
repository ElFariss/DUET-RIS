# Common rules for every Flash worker task (2026-11-09)

You are one worker in a chain of small tasks. The coordinator reads your hand-back and decides what runs next.
- **Do only your task.** Do not start the next stage, even if it looks easy.
- **If something outside your task is broken,** report it in the hand-back; do not fix it.

## Project
- **Repository:** `/home/faris/atom-wise-ris` on AMD-kc (`labkc1-amd`; moved from the laptop on 2026-11-09). Use `.venv/bin/python`, never system `python3`. `/home` has only ~8 GB free: keep large or raw outputs on 3060-3. Python package `src/atomwise_ris`, scripts in `scripts/`, tests in `tests/`.
- **Test suite** (must stay green; run it before you hand back):
  `PYTHONPATH=src:scripts .venv/bin/python -m unittest discover -s tests`
  - Known, pre-existing failure on this host only: `tests/test_matched.py::RankingIsTheOnlyDifference::test_memory_ga_ranking_uses_pattern_spread` (frozen Paper 1; CPU-math difference). Do not touch it; report everything else.
- **What is being built:** CoupledRIS-Bench, an RIS dataset. Its production pipeline runs:
  1. frozen user generator v1.1;
  2. Sionna RT ray tracing on LoD2 city meshes;
  3. NEC-2 channel conversion;
  4. flip-gain labels;
  5. HDF5/Parquet packaging;
  6. a gate check.
- **Key docs:**
  - `docs/codex-handoff-bench-production-20261109.md`: pipeline layout, remote workspaces, the earlier failures.
  - `docs/bench-production-pilot-20261109.md`: the pilot preregistration.
  - `docs/bench-production-mesh-policy-20261109.md`: the approved mesh-repair policy.

## Remote machine: 3060-3
- **Access:**
  - From AMD-kc (the default host now): `ssh -o BatchMode=yes -p 2003 gpu-labkc.ub.ac.id '<command>'`
  - From the laptop: `ssh -o BatchMode=yes -J faris@100.68.29.126 -p 2003 faris@gpu-labkc.ub.ac.id '<command>'`
- **Account:** `faris` only.
- **Never use** 3060-2. Do not run compute on 3060-1 (the jump host).
- **CPUs:** keep processes off CPUs 5 and 11. Use `taskset -c` with other cores.
- **Long jobs:** run in `tmux` on the remote, with a log and DONE/FAILED marker files. Never `sleep`-loop to wait in your own session. Launch, confirm it started, record the check command and hand back.
- **Data placement:** raw ray paths and meshes stay on 3060-3. Copy back only small JSON summaries.

## Hard rules
- **Never open** Berlin or Utrecht data, or anything named `coupled_wire_test_v1`, `coupled_wire_test_v2` or `coupled_wire_test_v2_fine161`.
- **Never edit frozen files.** `production_freeze.py` checks them; if it fails, stop and report.
- **No changes to** git commits, `paper/`, or any spreadsheet.
- **Credentials:** never print or copy anything from `~/.config/compute/secrets.env`.
- **Criteria:** pass/fail criteria are written in a dated doc **before** a run, and never loosened after.
- **Honesty:** if a check fails, say so plainly with the numbers. Never edit a test to make it pass unless the test itself is wrong; explain why if you do.

## Hand-back
Write the hand-back file named in your task (in `docs/`) with:
- what you did;
- the changed files;
- the test result;
- any remote jobs, with check commands;
- open problems.

Keep it short and factual.
