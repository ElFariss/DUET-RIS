# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 172800  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 108  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 108 | 6.573 | 9.06 | 0.000 | 0.00% | 24 | 0.14% | No |
| 128 | 10.0 | me_ga | 108 | 6.133 | 2.43 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 108 | 6.322 | 9.23 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 108 | 6.578 | 8.63 | 0.000 | 0.00% | 262 | 1.52% | YES |
| 128 | 10.0 | pair_plus_b35 | 108 | 6.581 | 9.59 | 0.000 | 0.00% | 327 | 1.89% | YES |
| 128 | 50.0 | greedy | 108 | 6.621 | 48.90 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 108 | 6.345 | 44.05 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 108 | 6.460 | 49.04 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 108 | 6.656 | 46.66 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 108 | 6.656 | 49.61 | 0.000 | 0.00% | 465 | 2.69% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 108 | +0.003 | [-0.000, +0.009] | 57 / 49 / 2 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 108 | +0.448 | [+0.297, +0.641] | 108 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 108 | +0.259 | [+0.173, +0.371] | 108 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - nsga2 | 108 | +0.256 | [+0.171, +0.366] | 108 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 108 | +0.445 | [+0.296, +0.637] | 108 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 108 | +0.000 | [-0.000, +0.001] | 56 / 51 / 1 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 108 | +0.311 | [+0.194, +0.453] | 108 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 108 | +0.196 | [+0.120, +0.295] | 108 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 108 | +0.196 | [+0.120, +0.294] | 108 / 0 / 0 | **supported** |
| 128 | 50.0 | pair - me_ga | 108 | +0.311 | [+0.194, +0.453] | 108 / 0 / 0 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.003 | [+0.000, +0.009] | 25 / 9 / 2 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.493 | [+0.241, +0.843] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.262 | [+0.130, +0.452] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 36 | +0.258 | [+0.129, +0.445] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 36 | +0.489 | [+0.239, +0.836] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | -0.000 | [-0.001, +0.000] | 14 / 21 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.294 | [+0.147, +0.485] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.187 | [+0.086, +0.330] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 36 | +0.187 | [+0.086, +0.330] | 36 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 36 | +0.294 | [+0.147, +0.486] | 36 / 0 / 0 | supported |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 14 / 22 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.252 | [+0.155, +0.357] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.164 | [+0.093, +0.245] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 36 | +0.164 | [+0.093, +0.245] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 36 | +0.252 | [+0.155, +0.357] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 22 / 14 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.059, +0.140] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.059, +0.140] | 36 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | supported |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.006 | [-0.002, +0.024] | 18 / 18 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.600 | [+0.282, +1.046] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.352 | [+0.167, +0.615] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 36 | +0.346 | [+0.161, +0.606] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 36 | +0.594 | [+0.275, +1.035] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 20 / 16 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.480 | [+0.206, +0.840] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.303 | [+0.121, +0.560] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 36 | +0.302 | [+0.121, +0.560] | 36 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 36 | +0.480 | [+0.206, +0.840] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 57 | +0.002 | [+0.000, +0.006] | 36 / 20 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 57 | +0.520 | [+0.314, +0.824] | 57 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 57 | +0.238 | [+0.161, +0.350] | 57 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 57 | +0.236 | [+0.160, +0.345] | 57 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 57 | +0.518 | [+0.312, +0.821] | 57 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 57 | -0.000 | [-0.000, +0.000] | 26 / 30 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 57 | +0.296 | [+0.179, +0.462] | 57 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 57 | +0.146 | [+0.093, +0.227] | 57 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 57 | +0.146 | [+0.093, +0.227] | 57 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 57 | +0.296 | [+0.179, +0.462] | 57 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 34 | +0.006 | [-0.003, +0.025] | 16 / 17 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 34 | +0.466 | [+0.214, +0.824] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 34 | +0.366 | [+0.161, +0.654] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 34 | +0.360 | [+0.156, +0.649] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 34 | +0.460 | [+0.211, +0.819] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 34 | +0.000 | [-0.000, +0.002] | 20 / 14 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 34 | +0.430 | [+0.175, +0.778] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 34 | +0.331 | [+0.134, +0.609] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 34 | +0.330 | [+0.133, +0.609] | 34 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 34 | +0.430 | [+0.175, +0.778] | 34 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 17 | -0.000 | [-0.002, +0.001] | 5 / 12 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 17 | +0.170 | [+0.041, +0.484] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 17 | +0.114 | [+0.032, +0.309] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 17 | +0.114 | [+0.032, +0.311] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 17 | +0.170 | [+0.041, +0.486] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 17 | +0.000 | [-0.000, +0.000] | 10 / 7 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 17 | +0.124 | [+0.029, +0.361] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 17 | +0.091 | [+0.025, +0.246] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 17 | +0.091 | [+0.025, +0.246] | 17 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 17 | +0.124 | [+0.029, +0.361] | 17 / 0 / 0 | supported |


