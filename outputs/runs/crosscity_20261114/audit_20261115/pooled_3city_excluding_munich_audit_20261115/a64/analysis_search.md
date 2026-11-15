# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 172800  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 108  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 108 | 6.313 | 9.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 108 | 6.109 | 8.80 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 108 | 6.195 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 108 | 6.351 | 8.80 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 108 | 6.349 | 9.49 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 108 | 6.332 | 49.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 108 | 6.239 | 48.86 | 0.000 | 0.00% | 4 | 0.02% | No |
| 64 | 50.0 | nsga2 | 108 | 6.307 | 49.47 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 108 | 6.365 | 48.77 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 108 | 6.365 | 49.48 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 108 | -0.003 | [-0.005, -0.002] | 5 / 96 / 7 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 108 | +0.239 | [+0.161, +0.336] | 108 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 108 | +0.154 | [+0.104, +0.219] | 108 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 108 | +0.157 | [+0.106, +0.223] | 108 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 108 | +0.242 | [+0.163, +0.340] | 108 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 108 | +0.001 | [+0.000, +0.001] | 64 / 42 / 2 | **supported** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 108 | +0.126 | [+0.084, +0.179] | 108 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 108 | +0.059 | [+0.037, +0.085] | 108 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 108 | +0.058 | [+0.037, +0.084] | 108 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 108 | +0.126 | [+0.083, +0.177] | 108 / 0 / 0 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.003, -0.001] | 3 / 31 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.183 | [+0.096, +0.315] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.128 | [+0.064, +0.243] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.130 | [+0.065, +0.245] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.185 | [+0.097, +0.317] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [-0.000, +0.003] | 22 / 14 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.103 | [+0.048, +0.200] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.046 | [+0.023, +0.090] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.046 | [+0.023, +0.087] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.102 | [+0.048, +0.197] | 36 / 0 / 0 | supported |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.007, -0.000] | 1 / 33 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.157 | [+0.086, +0.252] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.110 | [+0.061, +0.173] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.113 | [+0.061, +0.180] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.160 | [+0.087, +0.258] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 17 / 17 / 2 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | supported |


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
| 64 | 10.0 | pair_plus_b35 - pair | 57 | -0.003 | [-0.006, -0.001] | 2 / 51 / 4 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 57 | +0.237 | [+0.136, +0.368] | 57 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 57 | +0.130 | [+0.079, +0.210] | 57 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 57 | +0.133 | [+0.080, +0.213] | 57 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 57 | +0.239 | [+0.139, +0.372] | 57 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 57 | +0.001 | [+0.000, +0.002] | 38 / 18 / 1 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 57 | +0.122 | [+0.069, +0.199] | 57 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 57 | +0.034 | [+0.019, +0.063] | 57 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 57 | +0.034 | [+0.018, +0.061] | 57 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 57 | +0.122 | [+0.068, +0.197] | 57 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 34 | -0.004 | [-0.006, -0.001] | 3 / 29 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 34 | +0.309 | [+0.155, +0.532] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 34 | +0.226 | [+0.111, +0.390] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 34 | +0.229 | [+0.113, +0.393] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 34 | +0.312 | [+0.157, +0.536] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 34 | +0.001 | [+0.000, +0.002] | 19 / 14 / 1 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 34 | +0.165 | [+0.083, +0.270] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 34 | +0.101 | [+0.053, +0.159] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 34 | +0.101 | [+0.053, +0.158] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 34 | +0.164 | [+0.083, +0.268] | 34 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 17 | -0.001 | [-0.003, -0.000] | 0 / 16 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 17 | +0.111 | [+0.035, +0.263] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 17 | +0.093 | [+0.031, +0.214] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 17 | +0.094 | [+0.031, +0.216] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 17 | +0.112 | [+0.035, +0.265] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 17 | +0.000 | [-0.000, +0.001] | 7 / 10 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 17 | +0.062 | [+0.017, +0.151] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 17 | +0.054 | [+0.015, +0.132] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 17 | +0.054 | [+0.015, +0.132] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 17 | +0.061 | [+0.017, +0.151] | 17 / 0 / 0 | supported |


