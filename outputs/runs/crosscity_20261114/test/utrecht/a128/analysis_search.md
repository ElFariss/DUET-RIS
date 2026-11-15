# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 36 | 7.512 | 9.03 | 0.000 | 0.00% | 24 | 0.42% | No |
| 128 | 10.0 | me_ga | 36 | 6.917 | 2.63 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 36 | 7.165 | 9.21 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 36 | 7.511 | 8.68 | 0.000 | 0.00% | 98 | 1.70% | YES |
| 128 | 10.0 | pair_plus_b35 | 36 | 7.517 | 9.62 | 0.000 | 0.00% | 221 | 3.84% | YES |
| 128 | 50.0 | greedy | 36 | 7.592 | 48.81 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 36 | 7.166 | 43.39 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 36 | 7.343 | 49.00 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 36 | 7.646 | 46.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 36 | 7.646 | 49.65 | 0.000 | 0.00% | 340 | 5.90% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.006 | [-0.002, +0.024] | 18 / 18 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.600 | [+0.282, +1.046] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.352 | [+0.167, +0.615] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - nsga2 | 36 | +0.346 | [+0.161, +0.606] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 36 | +0.594 | [+0.275, +1.035] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 20 / 16 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.480 | [+0.206, +0.840] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.303 | [+0.121, +0.560] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 36 | +0.302 | [+0.121, +0.560] | 36 / 0 / 0 | **supported** |
| 128 | 50.0 | pair - me_ga | 36 | +0.480 | [+0.206, +0.840] | 36 / 0 / 0 | **supported** |


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
| 128 | 10.0 | pair_plus_b35 - pair | 17 | +0.002 | [-0.001, +0.004] | 12 / 5 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 17 | +0.574 | [+0.246, +1.248] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 17 | +0.213 | [+0.147, +0.297] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 17 | +0.212 | [+0.146, +0.293] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 17 | +0.573 | [+0.245, +1.247] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 17 | -0.000 | [-0.000, +0.000] | 6 / 11 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 17 | +0.352 | [+0.140, +0.793] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 17 | +0.129 | [+0.074, +0.198] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 17 | +0.129 | [+0.074, +0.198] | 17 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 17 | +0.352 | [+0.141, +0.793] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 13 | +0.014 | [-0.007, +0.062] | 5 / 8 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 13 | +0.750 | [+0.210, +1.537] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 13 | +0.595 | [+0.155, +1.227] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 13 | +0.580 | [+0.141, +1.202] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 13 | +0.736 | [+0.206, +1.525] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 13 | +0.001 | [-0.000, +0.004] | 10 / 3 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 13 | +0.752 | [+0.189, +1.521] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 13 | +0.592 | [+0.150, +1.217] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 13 | +0.591 | [+0.150, +1.215] | 13 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 13 | +0.751 | [+0.188, +1.520] | 13 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 6 | -0.001 | [-0.006, +0.001] | 1 / 5 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 6 | +0.344 | [+0.018, +1.219] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 6 | +0.218 | [+0.013, +0.760] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 6 | +0.219 | [+0.013, +0.766] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 6 | +0.345 | [+0.018, +1.225] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 6 | +0.000 | [-0.000, +0.001] | 4 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 6 | +0.253 | [+0.011, +0.915] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 6 | +0.170 | [+0.009, +0.605] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 6 | +0.170 | [+0.009, +0.604] | 6 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 6 | +0.252 | [+0.011, +0.915] | 6 / 0 / 0 | supported |


