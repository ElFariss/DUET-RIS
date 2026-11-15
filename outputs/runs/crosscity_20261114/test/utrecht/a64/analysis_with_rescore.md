# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 7.276 | 9.32 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 6.939 | 8.86 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 7.093 | 9.75 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 7.322 | 8.93 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 7.317 | 9.66 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 7.301 | 49.32 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 7.145 | 48.90 | 0.000 | 0.00% | 17 | 0.29% | No |
| 64 | 50.0 | nsga2 | 36 | 7.243 | 49.71 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 7.340 | 48.89 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 7.341 | 49.65 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.004 | [-0.007, -0.002] | 1 / 32 / 3 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.378 | [+0.191, +0.620] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.224 | [+0.110, +0.379] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 36 | +0.228 | [+0.113, +0.385] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 36 | +0.382 | [+0.194, +0.625] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [+0.000, +0.002] | 25 / 11 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.195 | [+0.102, +0.306] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.046, +0.161] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.046, +0.160] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 36 | +0.195 | [+0.102, +0.305] | 36 / 0 / 0 | **supported** |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.004 | [-0.007, -0.002] | 1 / 32 / 3 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.378 | [+0.191, +0.620] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.224 | [+0.110, +0.379] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.228 | [+0.113, +0.385] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.382 | [+0.194, +0.625] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [+0.000, +0.002] | 25 / 11 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.195 | [+0.102, +0.306] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.046, +0.161] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.046, +0.160] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.195 | [+0.102, +0.305] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 17 | -0.002 | [-0.005, -0.000] | 1 / 15 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 17 | +0.295 | [+0.085, +0.630] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 17 | +0.094 | [+0.040, +0.157] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 17 | +0.096 | [+0.041, +0.161] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 17 | +0.297 | [+0.086, +0.632] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 17 | +0.000 | [-0.000, +0.001] | 12 / 5 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 17 | +0.135 | [+0.039, +0.275] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 17 | +0.020 | [+0.008, +0.035] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 17 | +0.020 | [+0.007, +0.035] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 17 | +0.134 | [+0.039, +0.274] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 13 | -0.007 | [-0.013, -0.002] | 0 / 12 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 13 | +0.546 | [+0.223, +1.022] | 13 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 13 | +0.404 | [+0.145, +0.751] | 13 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 13 | +0.411 | [+0.150, +0.759] | 13 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 13 | +0.553 | [+0.228, +1.031] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 13 | +0.002 | [-0.000, +0.004] | 9 / 4 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 13 | +0.299 | [+0.130, +0.511] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 13 | +0.187 | [+0.086, +0.296] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 13 | +0.185 | [+0.085, +0.294] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 13 | +0.297 | [+0.129, +0.508] | 13 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 6 | -0.004 | [-0.008, -0.000] | 0 / 5 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 6 | +0.249 | [+0.068, +0.633] | 6 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 6 | +0.204 | [+0.057, +0.508] | 6 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 6 | +0.207 | [+0.058, +0.514] | 6 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 6 | +0.253 | [+0.069, +0.639] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 6 | +0.000 | [-0.000, +0.001] | 4 / 2 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 6 | +0.144 | [+0.033, +0.372] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 6 | +0.124 | [+0.025, +0.321] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 6 | +0.123 | [+0.025, +0.320] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 6 | +0.143 | [+0.033, +0.370] | 6 / 0 / 0 | supported |


