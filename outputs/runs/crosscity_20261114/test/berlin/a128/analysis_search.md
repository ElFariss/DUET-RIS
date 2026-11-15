# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 36 | 7.897 | 9.05 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | me_ga | 36 | 7.420 | 2.36 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 36 | 7.652 | 9.25 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 36 | 7.910 | 8.31 | 0.000 | 0.00% | 129 | 2.24% | YES |
| 128 | 10.0 | pair_plus_b35 | 36 | 7.913 | 9.55 | 0.000 | 0.00% | 106 | 1.84% | YES |
| 128 | 50.0 | greedy | 36 | 7.947 | 48.97 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 36 | 7.693 | 44.95 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 36 | 7.801 | 49.06 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 36 | 7.987 | 47.03 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 36 | 7.987 | 49.56 | 0.000 | 0.00% | 52 | 0.90% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.003 | [+0.000, +0.009] | 25 / 9 / 2 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.493 | [+0.241, +0.843] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.262 | [+0.130, +0.452] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - nsga2 | 36 | +0.258 | [+0.129, +0.445] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 36 | +0.489 | [+0.239, +0.836] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | -0.000 | [-0.001, +0.000] | 14 / 21 / 1 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.294 | [+0.147, +0.485] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.187 | [+0.086, +0.330] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 36 | +0.187 | [+0.086, +0.330] | 36 / 0 / 0 | **supported** |
| 128 | 50.0 | pair - me_ga | 36 | +0.294 | [+0.147, +0.486] | 36 / 0 / 0 | **supported** |


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


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 23 | +0.004 | [+0.000, +0.013] | 16 / 6 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 23 | +0.560 | [+0.217, +1.111] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 23 | +0.253 | [+0.105, +0.518] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 23 | +0.248 | [+0.104, +0.505] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 23 | +0.556 | [+0.217, +1.102] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 23 | -0.000 | [-0.001, +0.000] | 8 / 14 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 23 | +0.294 | [+0.122, +0.551] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 23 | +0.172 | [+0.065, +0.367] | 23 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 23 | +0.172 | [+0.065, +0.367] | 23 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 23 | +0.294 | [+0.123, +0.552] | 23 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 9 | +0.001 | [-0.001, +0.003] | 7 / 1 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 9 | +0.485 | [+0.200, +0.914] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 9 | +0.363 | [+0.111, +0.763] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 9 | +0.362 | [+0.110, +0.763] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 9 | +0.484 | [+0.199, +0.913] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 9 | +0.000 | [-0.001, +0.001] | 4 / 5 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 9 | +0.389 | [+0.119, +0.822] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 9 | +0.278 | [+0.072, +0.587] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 9 | +0.278 | [+0.072, +0.587] | 9 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 9 | +0.389 | [+0.119, +0.823] | 9 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 4 | +0.002 | [-0.000, +0.005] | 2 / 2 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 4 | +0.120 | [+0.076, +0.157] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 4 | +0.082 | [+0.058, +0.114] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 4 | +0.081 | [+0.056, +0.114] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 4 | +0.118 | [+0.076, +0.153] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 4 | -0.000 | [-0.000, +0.000] | 2 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 4 | +0.080 | [+0.056, +0.115] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 4 | +0.068 | [+0.048, +0.099] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 4 | +0.068 | [+0.048, +0.099] | 4 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 4 | +0.080 | [+0.056, +0.115] | 4 / 0 / 0 | supported |


