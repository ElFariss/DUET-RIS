# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 7.276 | 9.14 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 6.939 | 8.67 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 7.093 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 7.322 | 8.75 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 7.317 | 9.47 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 7.301 | 49.14 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 7.145 | 48.70 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | nsga2 | 36 | 7.243 | 49.51 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 7.340 | 48.71 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 7.341 | 49.47 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.026, +0.058] | 34 / 2 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 36 | +0.045 | [+0.029, +0.064] | 35 / 1 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.040 | [+0.025, +0.058] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - greedy | 36 | +0.039 | [+0.024, +0.057] | 36 / 0 / 0 | **supported** |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.026, +0.058] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.045 | [+0.029, +0.064] | 35 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.040 | [+0.025, +0.058] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.039 | [+0.024, +0.057] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 17 | +0.021 | [+0.011, +0.031] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 17 | +0.023 | [+0.012, +0.035] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 17 | +0.020 | [+0.009, +0.033] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 17 | +0.020 | [+0.009, +0.033] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 13 | +0.072 | [+0.040, +0.106] | 12 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 13 | +0.079 | [+0.043, +0.116] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 13 | +0.070 | [+0.037, +0.104] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 13 | +0.068 | [+0.036, +0.102] | 13 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 6 | +0.032 | [+0.006, +0.066] | 5 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 6 | +0.036 | [+0.006, +0.072] | 5 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 6 | +0.033 | [+0.007, +0.067] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 6 | +0.033 | [+0.006, +0.066] | 6 / 0 / 0 | supported |


