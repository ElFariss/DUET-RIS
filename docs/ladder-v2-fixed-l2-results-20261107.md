# V2 fixed-L2 development results (2026-11-07)

Exploratory development results on `coupled_wire_dev_fine161`. They support no claim. No test data was used, and `matched_v2` is not frozen. Design and recorded forecast: `docs/ladder-v2-fixed-l2-design-20261107.md`. Analysis: `scripts/analyze_ladder_v2_nol2.py --round fixedl2`, output `outputs/runs/pair_plus_ladder_v2_fixedl2/analysis_fixedl2_dev161.json`.

## Run

- 3060-1 core 3, 14:40 to 15:32 WIB, rc=0. 96,000 rows, 4,800 per method and budget.
- `fixedl2_dev161.jsonl` and its metadata match their hashes after sync. `pair_plus.py` (sha256 `81807fd4...76da`) matches the hash recorded by the run.
- Core 3 was fully busy for the whole run, and all 53 process samples showed only our process above 5% CPU.
- **The machine was slower than in earlier rounds.** `pair` did 125,580 evaluations per frame at 100 ms, against 161,339 in the no-L2 round, and its rate fell from 16.646 to 16.547. Another user's two Python jobs and the Blender job were running on other cores, so shared cache or memory bandwidth is the likely cause; it is not measured. Misses also rose to about 1% per cell for the b-methods. Contrasts within this round stay valid because methods are interleaved frame by frame, but **rates from this round must not be compared with other rounds.**

## Rate, timing, misses, restarts and screening

Misses are out of 4,800. Pair-searched restarts are restarts minus screened out.

| Method | Measure | 1 ms | 5 ms | 10 ms | 50 ms | 100 ms |
|---|---|---:|---:|---:|---:|---:|
| `pair` | rate | 15.339 | 15.824 | 15.915 | 16.309 | 16.547 |
| | p95 ms | 0.89 | 4.02 | 9.01 | 48.97 | 98.91 |
| | misses | 95 | 1 | 2 | 1 | 2 |
| `b0` | rate | 15.360 | 15.808 | 15.893 | 16.284 | 16.519 |
| | p95 ms | 0.86 | 4.86 | 9.87 | 49.88 | 99.88 |
| | misses | 65 | 46 | 49 | 54 | 57 |
| | restarts / screened | 0 / 0 | 1.1 / 0 | 2.0 / 0 | 7.7 / 0 | 14.8 / 0 |
| | pair scans | 0.0 | 1.3 | 3.2 | 22.8 | 47.1 |
| `b2` | rate | 15.359 | 15.805 | 15.895 | 16.203 | 16.413 |
| | p95 ms | 0.86 | 4.87 | 9.87 | 49.87 | 99.87 |
| | misses | 57 | 46 | 50 | 56 | 45 |
| | restarts / screened | 0 / 0 | 1.1 / 0.1 | 2.0 / 0.9 | 9.8 / 5.2 | 19.6 / 10.2 |
| | pair scans | 0.0 | 1.3 | 3.2 | 14.4 | 28.2 |
| `b2t` | rate | 15.359 | 15.803 | 15.894 | 16.145 | 16.305 |
| | p95 ms | 0.85 | 4.87 | 9.87 | 49.87 | 99.87 |
| | misses | 55 | 59 | 57 | 50 | 52 |
| | restarts / screened | 0 / 0 | 1.1 / 0.1 | 2.0 / 0.9 | 10.5 / 6.9 | 21.8 / 15.3 |
| | pair scans | 0.0 | 1.3 | 3.2 | 11.5 | 19.1 |

## Declared contrasts and reading rule

Bonferroni over 5 contrasts within a budget.

| Budget | `b2` - `b0` | `b2t` - `b0` | `b2` - `pair` | `b2t` - `pair` |
|---:|---|---|---|---|
| 1 ms | -0.000 [-0.001, +0.000] | -0.001 [-0.004, +0.001] | +0.020 [+0.004, +0.043] | +0.020 [+0.004, +0.042] |
| 5 ms | -0.003 [-0.011, +0.002] | -0.005 [-0.016, +0.002] | -0.019 [-0.043, -0.003] | -0.020 [-0.049, -0.003] |
| 10 ms | +0.001 [-0.003, +0.006] | +0.001 [-0.003, +0.005] | -0.020 [-0.032, -0.010] | -0.021 [-0.031, -0.012] |
| 50 ms | -0.081 [-0.107, -0.055] | -0.138 [-0.188, -0.093] | -0.107 [-0.143, -0.074] | -0.164 [-0.223, -0.111] |
| 100 ms | -0.106 [-0.144, -0.071] | -0.214 [-0.281, -0.151] | -0.134 [-0.176, -0.093] | -0.242 [-0.314, -0.173] |

`b0` - `pair`: +0.021 at 1 ms, then -0.015, -0.022, -0.025 and -0.028 at 5 to 100 ms, all with intervals clear of zero, as in the no-L2 round.

**Reading: neither screen qualifies at any budget, so screening is dropped from the method.** At 50 and 100 ms both screens are worse than `b0`, and the stricter screen is worse by about twice as much.

## Against the forecast

The forecast expected no gain at the 50th percentile and possibly a loss at the 75th. The direction held, but the 50th-percentile screen lost more than forecast. At 100 ms, `b2` pair-searched about 9.4 restarts per frame against `b0`'s 14.8, which is 0.64 times as many. The probe's no-deadline estimate was 0.79 times. Why the deadline run lost more was not measured; one possibility is that screened restarts, which still pay for single-flip descent, cost more under the deadline than in the probe.

## What this settles

- Screening after single-flip descent cannot help here, because the single-flip value barely ranks basins (within-frame Spearman 0.077 in the probe). This is a fair test of L2's idea, and it confirms that L2's loss in the cumulative ladder was not only a calibration error.
- The next round (`b3` + `b5`) should not include a screen.
- The slowdown on 3060-1 means the next round should rerun `pair`, `b0`, `b3` and `b5` alongside the combined method, rather than reuse the no-L2 rates.
