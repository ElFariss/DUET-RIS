# V2 no-L2 development results (2026-11-07)

Exploratory development results on `coupled_wire_dev_fine161`. They support no claim. No test data was used, and `matched_v2` is not frozen. Design: `docs/ladder-v2-nol2-design-20261107.md`. Analysis: `scripts/analyze_ladder_v2_nol2.py`, output `outputs/runs/pair_plus_ladder_v2_nol2/analysis_nol2_dev161.json`.

## Run

- 3060-1 core 3, 12:25 to 13:56 WIB, rc=0. 168,000 rows, 4,800 per method and budget (480 frames, 10 seeds, 30 trajectories).
- `nol2_dev161.jsonl` sha256 `e7e0fae7...a99a` matches on 3060-1 and locally. `pair_plus.py` and `benchmark_pair_plus.py` match the hashes recorded by the run.
- Core 3 was almost fully busy, and all 91 process samples showed only our process above 5% CPU. The samples are one minute apart, and sibling-core and cache interference from the other user's Blender job is unmeasured.
- `pair` reproduces the earlier ladder: 15.952/16.395/16.646 against 15.950/16.390/16.647 at 10/50/100 ms.

## Rate, timing, misses and restarts

Misses are out of 4,800. `pair` does not report restarts.

| Method | Measure | 1 ms | 5 ms | 10 ms | 50 ms | 100 ms |
|---|---|---:|---:|---:|---:|---:|
| `pair` | rate | 15.339 | 15.844 | 15.952 | 16.395 | 16.646 |
| | p95 ms | 0.69 | 4.10 | 9.06 | 49.06 | 99.05 |
| | misses | 2 | 2 | 2 | 0 | 2 |
| `b0` | rate | 15.368 | 15.830 | 15.930 | 16.366 | 16.619 |
| | p95 ms | 0.69 | 4.72 | 9.72 | 49.72 | 99.72 |
| | misses | 3 | 4 | 0 | 5 | 9 |
| | restarts | 0.0 | 1.3 | 2.3 | 9.6 | 18.7 |
| `b3` | rate | 15.367 | 15.836 | 15.984 | 16.442 | 16.699 |
| | p95 ms | 0.69 | 4.72 | 9.72 | 49.72 | 99.72 |
| | misses | 2 | 7 | 8 | 4 | 10 |
| | restarts | 0.0 | 1.8 | 2.7 | 11.1 | 21.6 |
| `b4` | rate | 15.367 | 15.860 | 15.988 | 16.404 | 16.652 |
| | p95 ms | 0.71 | 4.75 | 9.76 | 49.76 | 99.76 |
| | misses | 0 | 3 | 11 | 6 | 5 |
| | restarts | 0.0 | 1.0 | 1.0 | 2.3 | 3.8 |
| `b4o` | rate | 15.368 | 15.860 | 15.987 | 16.381 | 16.616 |
| | p95 ms | 0.71 | 4.75 | 9.76 | 49.76 | 99.75 |
| | misses | 3 | 4 | 8 | 15 | 4 |
| | restarts | 0.0 | 1.0 | 1.0 | 5.6 | 14.1 |
| `b5` | rate | 15.368 | 15.829 | 15.931 | 16.420 | 16.693 |
| | p95 ms | 0.69 | 4.74 | 9.74 | 49.75 | 99.75 |
| | misses | 5 | 7 | 8 | 12 | 7 |
| | restarts | 0.0 | 1.3 | 2.4 | 11.4 | 22.4 |
| `b6` | rate | 15.361 | 15.805 | 15.910 | 16.363 | 16.618 |
| | p95 ms | 0.83 | 4.88 | 9.97 | 50.15 | 100.16 |
| | misses | 58 | 31 | 145 | 1306 | 1309 |
| | restarts | 0.0 | 1.2 | 2.2 | 9.4 | 18.4 |

## Declared reading rule

Bonferroni over 11 contrasts within a budget. Budget is in ms.

| Method | Budget | vs `b0` | vs `pair` | Reading |
|---:|---:|---|---|---|
| `b3` | 5 | +0.006 [+0.0005, +0.014] | -0.008 [-0.038, +0.007] | candidate |
| `b3` | 10 | +0.054 [+0.025, +0.087] | +0.032 [+0.005, +0.058] | improvement candidate |
| `b3` | 50 | +0.076 [+0.038, +0.123] | +0.047 [+0.013, +0.090] | improvement candidate |
| `b3` | 100 | +0.079 [+0.039, +0.122] | +0.052 [+0.014, +0.092] | improvement candidate |
| `b5` | 50 | +0.054 [+0.021, +0.094] | +0.025 [-0.007, +0.063] | candidate |
| `b5` | 100 | +0.074 [+0.041, +0.109] | +0.047 [+0.016, +0.081] | improvement candidate |
| `b4` | 5 | +0.030 [+0.005, +0.062] | +0.016 [-0.025, +0.056] | candidate |
| `b4` | 10 | +0.058 [+0.007, +0.116] | +0.036 [-0.013, +0.092] | candidate |
| `b4o` | 5 | +0.030 [+0.005, +0.062] | +0.016 [-0.025, +0.056] | candidate |
| `b4o` | 10 | +0.058 [+0.007, +0.116] | +0.035 [-0.013, +0.092] | candidate |

No method qualifies at 1 ms. `b6` qualifies at no budget. The no-gain stop rule does not apply. `b3` and `b5` both qualify over `pair` at 100 ms, so by the declared rule a combined method needs its own later development round.

Not part of the declared analysis: with Bonferroni over all 55 contrasts across budgets, `b3` vs `pair` stays above zero at 10, 50 and 100 ms, and `b5` vs `pair` at 100 ms.

## Limits

- **Effect size:** the gains over `pair` are 0.03 to 0.05 bit/s/Hz, about 0.3% of rate. The practical margin is unset, so they cannot yet be called meaningful. The gap to the best known rate is still about 1.7 at 100 ms.
- **All-OFF:** `b3` at 100 ms still returns all-OFF in 43.5% of runs, against 45.0% for `pair`.
- **Mesh:** rates are scored on the 161-segment mesh, which is not shown converged. Nobody has checked whether these small differences survive a mesh change.
- **Base:** `b0` is still below `pair` at 10, 50 and 100 ms (-0.022 to -0.029, intervals below zero), so its overhead reduction did not close the gap.
- **Deadline use:** the b-methods use about 0.66 ms more of each deadline at p95 than `pair`. At 10 ms that is about 7%, which may flatter `b3` there.
- **Budget rule:** only `pair` at 50 ms has zero misses, so no budget has zero misses across all methods. `b6` is the clear outlier at up to 27%. Other methods stay at or below 0.31%, with a worst overshoot of 3.7 ms (`b3` at 1 ms). The rule still has to be decided.
- **Selection:** the b-methods were designed after seeing ladder results on this same data, and the density 18/64 came from earlier data analysis. Only an untouched test run can confirm them.

## Mechanism

- Removing L2 mattered most. Rate at 100 ms went from 16.135 (L3) to 16.699 (`b3`), and from 16.277 (L5) to 16.693 (`b5`). These compare separate runs, so they are descriptive.
- The L4 counter fix also mattered: 16.277 (L4) to 16.652 (`b4`) at 100 ms. The fix changes the mechanism, and L2 is gone as well, so the two effects are not separated.
- Full escape (`b4`) has more evaluations than `b0` at every budget from 5 ms, but only 3.8 restarts at 100 ms against 18.7, and no significant gain from 50 ms. Escape helps only at short deadlines.
- Cross-frame memory (`b6`) gave no gain at any budget and caused the deadline misses above.
