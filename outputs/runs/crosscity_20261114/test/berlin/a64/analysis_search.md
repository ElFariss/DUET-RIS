# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 8.196 | 9.12 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 8.056 | 8.94 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 8.111 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 8.241 | 8.91 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 8.239 | 9.46 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 8.216 | 49.12 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 8.154 | 48.97 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | nsga2 | 36 | 8.211 | 49.41 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 8.256 | 48.88 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 8.257 | 49.46 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.003, -0.001] | 3 / 31 / 2 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.183 | [+0.096, +0.315] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.128 | [+0.064, +0.243] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 36 | +0.130 | [+0.065, +0.245] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 36 | +0.185 | [+0.097, +0.317] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [-0.000, +0.003] | 22 / 14 / 0 | **includes_0** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.103 | [+0.048, +0.200] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.046 | [+0.023, +0.090] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 36 | +0.046 | [+0.023, +0.087] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 36 | +0.102 | [+0.048, +0.197] | 36 / 0 / 0 | **supported** |


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


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 23 | -0.002 | [-0.004, -0.000] | 1 / 20 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 23 | +0.197 | [+0.085, +0.398] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 23 | +0.136 | [+0.054, +0.314] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 23 | +0.138 | [+0.055, +0.315] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 23 | +0.199 | [+0.086, +0.400] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 23 | +0.001 | [-0.000, +0.005] | 16 / 7 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 23 | +0.115 | [+0.042, +0.266] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 23 | +0.045 | [+0.016, +0.113] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 23 | +0.044 | [+0.015, +0.108] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 23 | +0.114 | [+0.042, +0.262] | 23 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 9 | -0.002 | [-0.005, -0.001] | 2 / 7 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 9 | +0.208 | [+0.093, +0.414] | 9 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 9 | +0.146 | [+0.066, +0.262] | 9 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 9 | +0.148 | [+0.067, +0.266] | 9 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 9 | +0.210 | [+0.094, +0.419] | 9 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 9 | +0.000 | [-0.000, +0.001] | 4 / 5 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 9 | +0.106 | [+0.046, +0.211] | 9 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 9 | +0.059 | [+0.029, +0.093] | 9 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 9 | +0.059 | [+0.029, +0.093] | 9 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 9 | +0.106 | [+0.046, +0.211] | 9 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 4 | -0.000 | [-0.001, -0.000] | 0 / 4 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 4 | +0.048 | [+0.027, +0.074] | 4 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 4 | +0.043 | [+0.026, +0.067] | 4 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 4 | +0.043 | [+0.026, +0.067] | 4 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 4 | +0.048 | [+0.028, +0.075] | 4 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 4 | +0.000 | [-0.000, +0.000] | 2 / 2 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 4 | +0.024 | [+0.016, +0.038] | 4 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 4 | +0.023 | [+0.015, +0.035] | 4 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 4 | +0.023 | [+0.015, +0.035] | 4 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 4 | +0.024 | [+0.016, +0.038] | 4 / 0 / 0 | supported |


