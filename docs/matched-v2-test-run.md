# matched_v2 single test run: manifest (Paper 1)

Protocol: `configs/experiments/matched_v2.json`, frozen 2026-11-07 12:49:41 UTC, sha256 `d9ed1a21e4d1568b63ab083918a9a5c9fc6d7b6f386f221dfd353cde7505e468`. The frozen sources run on 3060-3; byte copies are in `outputs/frozen/matched_v2_src/` and the protocol copy in `outputs/frozen/matched_v2.json`. The local working tree diverges in `pair_plus.py` and `network.py` because of Track 3 work. Do not run the test from the local tree.

Approved values (plan of 2026-11-07):
- primary budget 50 ms; 5, 10 and 100 ms secondary
- methods: greedy, pair, me_ga, b3, b5, b35
- 10 registered seeds
- contrast family: b35−pair, b35−b3, b35−b5, b35−me_ga, pair−greedy, with Bonferroni correction within each budget
- a contrast is supported only if its interval excludes zero on both the 161- and 81-segment meshes, and neither method misses more than 0.5% of its runs

Before freezing, a smoke run on 2 development frames on 3060-3 checked the runner. It read no test data.

| Field | Value |
|---|---|
| Node | 3060-3 (`labkc-comm3`), reached from 3060-1 with `ssh -p 2003 faris@gpu-labkc.ub.ac.id`; clock is UTC |
| Workspace | `/mnt/home/faris/projects/atom-wise-ris-ladder-20261107` |
| Session | tmux `matched-v2-test`, started 2026-11-07 12:50:13 UTC (19:50 WIB) |
| Entry point | `CPU=5 bash scripts/run_matched_v2_test_n3.sh` (restart-safe) |
| Stage 1 | `generate_coupled_test.py --fine-from coupled_wire_test_v2 --fine-split test --segments 161 --workers 6`, pinned to CPUs 0–4 and 6–10. Output `data/processed/coupled_wire_test_v2_fine161`, 480 frames; physics matrices only. Marker `GEN_DONE` |
| Stage 2 | `run_matched_v2_test.py --cpu 5`. Output `outputs/runs/matched_v2_test/test_v2.jsonl`, 115,200 rows (480 frames × 4 budgets × 10 seeds × 6 methods). CPU 5 and sibling 11 logged every 20 s |
| Markers | `logs/matched_v2_test/{status,provenance.sha256,generation.log,test.log,cpu_load.log,GEN_DONE,DONE,FAILED,output.sha256}` |
| Expected | Stage 1 measured at about 335–360 s per frame per worker (78 of 480 frames at 21:18 WIB), so generation ends around 04:50 WIB; stage 2 about 1.5 h. Finish around 06:20 WIB on 2026-11-08. Check scheduled at 06:43 WIB |
| On DONE | Sync `outputs/runs/matched_v2_test`, `logs/matched_v2_test` and the fine scenario and status files with a hash check. Check the CPU log. Run `python3 scripts/analyze_matched_v2_test.py --input outputs/runs/matched_v2_test/test_v2.jsonl` using the frozen analysis script. Report every cell and contrast, primary budget first |
| On FAILED | Read the tail of the named log only. A generation failure can resume, because frames are verified per index. A test crash may resume only into a fresh output with identical code and data, and is reported (`one_shot` in the protocol) |

The test is run once. No result can trigger retuning, a change of budget or a rerun.
