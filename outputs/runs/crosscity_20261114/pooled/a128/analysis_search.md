# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 230400  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 144  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 144 | 7.168 | 9.05 | 0.000 | 0.00% | 24 | 0.10% | No |
| 128 | 10.0 | me_ga | 144 | 6.700 | 2.40 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 144 | 6.929 | 9.24 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 144 | 7.174 | 8.52 | 0.000 | 0.00% | 340 | 1.48% | YES |
| 128 | 10.0 | pair_plus_b35 | 144 | 7.177 | 9.58 | 0.000 | 0.00% | 394 | 1.71% | YES |
| 128 | 50.0 | greedy | 144 | 7.212 | 48.92 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 144 | 6.947 | 44.28 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 144 | 7.061 | 49.04 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 144 | 7.249 | 46.77 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 144 | 7.249 | 49.59 | 0.000 | 0.00% | 598 | 2.60% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 144 | +0.003 | [+0.000, +0.008] | 85 / 57 / 2 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 144 | +0.477 | [+0.345, +0.634] | 144 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 144 | +0.248 | [+0.172, +0.348] | 144 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - nsga2 | 144 | +0.245 | [+0.170, +0.345] | 144 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 144 | +0.474 | [+0.343, +0.629] | 144 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 144 | +0.000 | [-0.000, +0.000] | 74 / 68 / 2 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 144 | +0.302 | [+0.205, +0.424] | 144 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 144 | +0.188 | [+0.121, +0.278] | 144 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 144 | +0.188 | [+0.121, +0.278] | 144 / 0 / 0 | **supported** |
| 128 | 50.0 | pair - me_ga | 144 | +0.302 | [+0.205, +0.424] | 144 / 0 / 0 | **supported** |


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


### Map: munich

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.002 | [-0.000, +0.007] | 28 / 8 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.564 | [+0.351, +0.832] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.215 | [+0.085, +0.408] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 36 | +0.213 | [+0.083, +0.407] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 36 | +0.561 | [+0.350, +0.831] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | -0.000 | [-0.000, +0.000] | 18 / 17 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.276 | [+0.126, +0.507] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.166 | [+0.052, +0.350] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 36 | +0.166 | [+0.052, +0.350] | 36 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 36 | +0.276 | [+0.126, +0.507] | 36 / 0 / 0 | supported |


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
| 128 | 10.0 | pair_plus_b35 - pair | 79 | +0.002 | [+0.000, +0.006] | 54 / 24 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 79 | +0.541 | [+0.375, +0.765] | 79 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 79 | +0.205 | [+0.142, +0.289] | 79 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 79 | +0.203 | [+0.141, +0.284] | 79 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 79 | +0.539 | [+0.374, +0.761] | 79 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 79 | -0.000 | [-0.000, +0.000] | 34 / 43 / 2 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 79 | +0.267 | [+0.176, +0.391] | 79 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 79 | +0.126 | [+0.082, +0.188] | 79 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 79 | +0.126 | [+0.082, +0.188] | 79 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 79 | +0.267 | [+0.176, +0.391] | 79 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 42 | +0.005 | [-0.002, +0.021] | 21 / 20 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 42 | +0.530 | [+0.294, +0.846] | 42 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 42 | +0.404 | [+0.208, +0.665] | 42 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 42 | +0.399 | [+0.203, +0.660] | 42 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 42 | +0.525 | [+0.289, +0.840] | 42 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 42 | +0.000 | [-0.000, +0.001] | 27 / 15 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 42 | +0.471 | [+0.229, +0.793] | 42 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 42 | +0.360 | [+0.171, +0.613] | 42 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 42 | +0.359 | [+0.171, +0.612] | 42 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 42 | +0.470 | [+0.229, +0.793] | 42 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 23 | +0.000 | [-0.001, +0.001] | 10 / 13 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 23 | +0.160 | [+0.050, +0.397] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 23 | +0.110 | [+0.038, +0.258] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 23 | +0.110 | [+0.038, +0.259] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 23 | +0.160 | [+0.049, +0.398] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 23 | +0.000 | [-0.000, +0.000] | 13 / 10 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 23 | +0.117 | [+0.035, +0.297] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 23 | +0.088 | [+0.030, +0.207] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 23 | +0.088 | [+0.030, +0.207] | 23 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 23 | +0.117 | [+0.035, +0.297] | 23 / 0 / 0 | supported |


