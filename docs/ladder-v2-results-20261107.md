# V2 ladder results on 161-segment development data (2026-11-07)

Development data only: 30 trajectories, 480 frames, 10 seeds, 5 budgets, 264,000 timed rows and 4,800 `me_ga_paper` rows. Run on 3060-1 core 3, 07:47 to 10:24 WIB, rc 0; hashes verified after sync. `coupled_wire_test_v2` was not touched and `matched_v2` is not frozen. Analysis: `scripts/analyze_ladder_v2.py`, output `outputs/runs/pair_plus_ladder_v2/analysis_dev161.json`. Intervals are paired trajectory bootstrap (10,000 resamples, seed 8251), Bonferroni across 33 contrasts within a budget. They are exploratory, and no practical margin is set.

| Method | 10 ms | 50 ms | 100 ms | Misses at 50 ms (of 4,800) | All-OFF at 50 ms |
|---|---:|---:|---:|---:|---:|
| pair | 15.950 | 16.390 | 16.647 | 5 | 0.53 |
| L1 anytime ILS | 15.908 | 16.335 | 16.591 | 4 | 0.54 |
| L2 screened restarts | 15.854 | 15.968 | 16.057 | 5 | 0.70 |
| L3 restart distribution | 15.870 | 16.026 | 16.135 | 5 | 0.67 |
| L4 all-OFF escape | 15.969 | 16.247 | 16.277 | 7 | 0.60 |
| L5 elite recombination | 15.968 | 16.249 | 16.277 | 4 | 0.60 |
| L6 cross-frame memory | 15.949 | 16.248 | 16.279 | 6 | 0.60 |
| mlp_ga | 15.808 | 15.872 | 15.872 | 0 | 0.71 |
| greedy | 15.481 | 15.651 | 15.773 | 0 | 0.81 |
| me_ga | 3.015 | 5.391 | 7.664 | 19 | 0.00 |
| ga_risc | 3.015 | 5.324 | 7.480 | 21 | 0.00 |

`me_ga_paper` (no deadline): 9.67 bit/s/Hz, median 301 ms, about 10,700 evaluations. Mean best-known rate per frame across all runs: 17.846 (a max across seeds and budgets, so optimistic).

Step contrasts at 50 ms: L1-pair -0.055 [-0.077, -0.035]; L2-L1 -0.367 [-0.539, -0.223]; L3-L2 +0.058 [0.024, 0.110]; L4-L3 +0.221 [0.108, 0.364]; L5-L4 +0.001 [-0.001, 0.004]; L6-L5 0.000 [-0.057, 0.063]. L4-pair at 10 ms is +0.019 [-0.040, 0.083]. me_ga-ga_risc at 50 ms is +0.066 [0.037, 0.096].

Limits:
- The steps are cumulative. L3 to L6 were tested on top of L2, which lowered rate, so their value without L2 has not been measured.
- ME-GA starts from random states, as the paper says, under an RZF precoder fixed to all-OFF. All-OFF already scores about 15.34 here. The large gap is largely this adaptation and short deadlines, and it does not evaluate ME-GA under its own per-step ZF setting.
- Every budget has at least one miss across methods, so the zero-miss budget rule selects no budget. Overruns at 50 ms reach about 4.5 ms. Core 3 load samples showed only our process above 5%, in 157 of 158 samples. Sibling-thread or shared-cache interference was not measured.
- 161 segments are not shown to be converged.
