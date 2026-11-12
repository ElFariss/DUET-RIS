# V2 ladder run manifest (development data only)

Started 2026-11-07. This is a durable, unattended run; no test data is involved.

| Item | Value |
|---|---|
| Watcher | rx6600, tmux `ladder-v2-watch`, `~/compute-jobs/ladder-v2-watch/{status,out.log,DONE,FAILED}` |
| Waits for | `coupled-dev-fine161-20261106` on rx6600, `generation_status.json` status `complete` |
| Then | copies data to 3060-1 with a hash check, starts tmux `ladder-v2` there |
| Workspace | 3060-1 `/mnt/home/faris/projects/atom-wise-ris-ladder-20261107` |
| Entry point | `scripts/run_ladder_v2_node.sh` -> `scripts/benchmark_pair_plus.py`, core 3, 1/5/10/50/100 ms, 10 seeds |
| Output | `outputs/runs/pair_plus_ladder_v2/ladder_dev161.jsonl`, `.json`, `.me-ga-paper.jsonl` |
| Finish markers | `logs/ladder_v2/DONE` or `FAILED`, `status`, `benchmark.log`, `core3_load.log` |
| Expected | data about 08:00 WIB, ladder about 3 h after that (from a 3-frame smoke run) |

Check status:

    compute lab exec rx6600 'cat ~/compute-jobs/ladder-v2-watch/status'
    ssh faris@100.68.29.126 'cd /mnt/home/faris/projects/atom-wise-ris-ladder-20261107/logs/ladder_v2 && ls && cat status && wc -l ../../outputs/runs/pair_plus_ladder_v2/*.jsonl'

On success: sync outputs back with hash check, then decide which L-steps to keep. The benchmark runs the methods as defined, so if a step is dropped, later cumulative steps may need a rerun without it. Review `core3_load.log` first: another user's job has been running on this node without a core restriction.
On failure: read the tail of `benchmark.log`. The benchmark refuses to overwrite output, so move a partial output aside before rerunning.

Smoke result (non-result, 3 frames, 2 seeds): 330 rows and 6 full ME-GA rows, 13 s. It found and fixed a crash on the `deadline_missed` lookup for non-pair-plus methods, and a missing warm-up pass in `benchmark_pair_plus.py`.
Do not start this ladder a second time from another agent.

## No-L2 round (started 2026-11-07)

Design: `docs/ladder-v2-nol2-design-20261107.md`. 3060-1 tmux `ladder-v2-nol2`, same workspace, entry point `scripts/run_ladder_v2_nol2_node.sh`. Output `outputs/runs/pair_plus_ladder_v2_nol2/nol2_dev161.jsonl`; markers `logs/ladder_v2_nol2/{DONE,FAILED,status,benchmark.log,core3_load.log}`. Expect 168,000 rows, about 1.6 h. Do not start it twice.

No-L2 round finished 2026-11-07 13:56 WIB, rc=0, 168,000 rows; synced with hash check. Results: `docs/ladder-v2-nol2-results-20261107.md`.

## Fixed-L2 round (started 2026-11-07)

Design: `docs/ladder-v2-fixed-l2-design-20261107.md`. 3060-1 tmux `ladder-v2-fixedl2`, same workspace, entry point `scripts/run_ladder_v2_fixedl2_node.sh`. Output `outputs/runs/pair_plus_ladder_v2_fixedl2/fixedl2_dev161.jsonl`; markers `logs/ladder_v2_fixedl2/{DONE,FAILED,status,benchmark.log,core3_load.log}`. Expect 96,000 rows, about 55 min. Do not start it twice.

Fixed-L2 round finished 2026-11-07 15:32 WIB, rc=0, 96,000 rows; synced with hash check. Results: `docs/ladder-v2-fixed-l2-results-20261107.md`. Machine throughput was about 22% lower than in the no-L2 round, so rates are not comparable across rounds.

## Combined b3+b5 round (started 2026-11-07)

Design: `docs/ladder-v2-combined-design-20261107.md`. 3060-1 tmux `ladder-v2-combined`, same workspace, entry point `scripts/run_ladder_v2_combined_node.sh`. Output `outputs/runs/pair_plus_ladder_v2_combined/combined_dev161.jsonl`; markers `logs/ladder_v2_combined/{DONE,FAILED,status,benchmark.log,core3_load.log}`. Expect 120,000 rows, about 70 min. Do not start it twice.

Combined round rerun on 3060-3 (started 2026-11-07 17:23 WIB): 3060-1 throughput was about 26% below the no-L2 round, with deadline misses of 1–2% per budget. The log later showed other users' threads on CPU 3 itself in only 1 of 66 samples, so the cause is not direct sharing of the timed CPU (sibling CPU 9 was not logged). The 3060-1 run is allowed to finish and is kept as a secondary record. 3060-3 (`labkc-comm3`, reached from 3060-1 with `ssh -p 2003 faris@gpu-labkc.ub.ac.id`) has the same CPU model and Python 3.12.3, the workspace and venv copied from 3060-1 with matching source hashes, and 962 dev files. tmux `ladder-v2-combined-n3`, CPU 5 (SMT sibling 11), entry point `CPU=5 scripts/run_ladder_v2_combined_n3.sh`. Output `outputs/runs/pair_plus_ladder_v2_combined_n3/combined_dev161.jsonl`; markers `logs/ladder_v2_combined_n3/{DONE,FAILED,status,benchmark.log,cpu_load.log}` (CPU 5 and sibling load every 20 s). Expect 120,000 rows, about 65 min. The 3060-3 clock is UTC. This run is the primary result for the combined round; analysis `python3 scripts/analyze_ladder_v2_nol2.py --round combined_n3`.


Both combined runs finished (3060-3 11:29 UTC, 3060-1 17:26 WIB), 120,000 rows each, rc=0, hashes checked after sync. 3060-3 had 0 misses in every cell. Results: `docs/ladder-v2-combined-results-20261107.md`.
