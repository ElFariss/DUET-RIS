# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 115200  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 72  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 72 | 5.371 | 9.31 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 72 | 5.136 | 8.91 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 72 | 5.236 | 9.75 | 0.000 | 0.00% | 1 | 0.01% | No |
| 64 | 10.0 | pair | 72 | 5.407 | 8.93 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 72 | 5.403 | 9.69 | 0.000 | 0.00% | 3 | 0.03% | No |
| 64 | 50.0 | greedy | 72 | 5.390 | 49.31 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 72 | 5.282 | 48.99 | 0.000 | 0.00% | 91 | 0.79% | YES |
| 64 | 50.0 | nsga2 | 72 | 5.355 | 49.70 | 0.000 | 0.00% | 5 | 0.04% | No |
| 64 | 50.0 | pair | 72 | 5.419 | 48.89 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 72 | 5.420 | 49.67 | 0.000 | 0.00% | 7 | 0.06% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 72 | -0.003 | [-0.006, -0.001] | 2 / 65 / 5 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 72 | +0.268 | [+0.164, +0.405] | 72 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 72 | +0.167 | [+0.102, +0.251] | 72 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 72 | +0.170 | [+0.104, +0.256] | 72 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 72 | +0.271 | [+0.166, +0.409] | 72 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 72 | +0.000 | [+0.000, +0.001] | 42 / 28 / 2 | **supported** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 72 | +0.138 | [+0.084, +0.204] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 72 | +0.065 | [+0.037, +0.100] | 72 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 72 | +0.064 | [+0.037, +0.099] | 72 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 72 | +0.138 | [+0.084, +0.203] | 72 / 0 / 0 | **excluded_by_miss_rule** |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.007, -0.000] | 1 / 33 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.157 | [+0.086, +0.252] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.110 | [+0.061, +0.173] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.113 | [+0.061, +0.180] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.160 | [+0.087, +0.258] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 17 / 17 / 2 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | excluded_by_miss_rule |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.004 | [-0.007, -0.002] | 1 / 32 / 3 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.378 | [+0.191, +0.620] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.224 | [+0.110, +0.379] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.228 | [+0.113, +0.385] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.382 | [+0.194, +0.625] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [+0.000, +0.002] | 25 / 11 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.195 | [+0.102, +0.306] | 36 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.046, +0.161] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.046, +0.160] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.195 | [+0.102, +0.305] | 36 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 34 | -0.003 | [-0.009, -0.001] | 1 / 31 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 34 | +0.263 | [+0.138, +0.457] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 34 | +0.126 | [+0.076, +0.190] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 34 | +0.129 | [+0.077, +0.197] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 34 | +0.267 | [+0.140, +0.460] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 34 | +0.000 | [-0.000, +0.001] | 22 / 11 / 1 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 34 | +0.128 | [+0.066, +0.213] | 34 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 34 | +0.027 | [+0.016, +0.041] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 34 | +0.027 | [+0.016, +0.041] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 34 | +0.127 | [+0.066, +0.212] | 34 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 25 | -0.004 | [-0.008, -0.001] | 1 / 22 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 25 | +0.345 | [+0.149, +0.622] | 25 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 25 | +0.254 | [+0.104, +0.461] | 25 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 25 | +0.258 | [+0.106, +0.468] | 25 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 25 | +0.349 | [+0.151, +0.628] | 25 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 25 | +0.001 | [+0.000, +0.002] | 15 / 9 / 1 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 25 | +0.186 | [+0.081, +0.322] | 25 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 25 | +0.116 | [+0.054, +0.191] | 25 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 25 | +0.115 | [+0.054, +0.190] | 25 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 25 | +0.185 | [+0.081, +0.320] | 25 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 13 | -0.002 | [-0.004, -0.000] | 0 / 12 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 13 | +0.131 | [+0.031, +0.334] | 13 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 13 | +0.108 | [+0.026, +0.270] | 13 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 13 | +0.110 | [+0.027, +0.274] | 13 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 13 | +0.132 | [+0.031, +0.338] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 13 | +0.000 | [-0.000, +0.001] | 5 / 8 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 13 | +0.073 | [+0.014, +0.194] | 13 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 13 | +0.064 | [+0.012, +0.169] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 13 | +0.064 | [+0.012, +0.169] | 13 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 13 | +0.073 | [+0.014, +0.193] | 13 / 0 / 0 | excluded_by_miss_rule |


