# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 3.466 | 9.31 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 3.332 | 8.96 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 3.379 | 9.74 | 0.000 | 0.00% | 1 | 0.02% | No |
| 64 | 10.0 | pair | 36 | 3.492 | 8.93 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 3.490 | 9.72 | 0.000 | 0.00% | 3 | 0.05% | No |
| 64 | 50.0 | greedy | 36 | 3.479 | 49.31 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 3.418 | 49.09 | 0.000 | 0.00% | 74 | 1.29% | YES |
| 64 | 50.0 | nsga2 | 36 | 3.467 | 49.68 | 0.000 | 0.00% | 5 | 0.09% | No |
| 64 | 50.0 | pair | 36 | 3.498 | 48.89 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 3.498 | 49.69 | 0.000 | 0.00% | 7 | 0.12% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.007, -0.000] | 1 / 33 / 2 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.157 | [+0.086, +0.252] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.110 | [+0.061, +0.173] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 36 | +0.113 | [+0.061, +0.180] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 36 | +0.160 | [+0.087, +0.258] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 17 / 17 / 2 | **includes_0** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | **excluded_by_miss_rule** |


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


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 17 | -0.004 | [-0.014, -0.001] | 0 / 16 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 17 | +0.232 | [+0.120, +0.387] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 17 | +0.157 | [+0.081, +0.267] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 17 | +0.161 | [+0.082, +0.280] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 17 | +0.236 | [+0.120, +0.400] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 17 | +0.000 | [-0.000, +0.000] | 10 / 6 / 1 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 17 | +0.120 | [+0.059, +0.224] | 17 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 17 | +0.033 | [+0.017, +0.058] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 17 | +0.033 | [+0.017, +0.058] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 17 | +0.120 | [+0.059, +0.223] | 17 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 12 | -0.001 | [-0.002, -0.000] | 1 / 10 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 12 | +0.127 | [+0.032, +0.250] | 12 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 12 | +0.092 | [+0.026, +0.175] | 12 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 12 | +0.093 | [+0.026, +0.176] | 12 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 12 | +0.128 | [+0.032, +0.252] | 12 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 12 | +0.000 | [-0.000, +0.001] | 6 / 5 / 1 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 12 | +0.063 | [+0.015, +0.125] | 12 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 12 | +0.040 | [+0.010, +0.077] | 12 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 12 | +0.039 | [+0.010, +0.076] | 12 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 12 | +0.063 | [+0.015, +0.124] | 12 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 7 | -0.000 | [-0.000, -0.000] | 0 / 7 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 7 | +0.029 | [+0.006, +0.059] | 7 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 7 | +0.027 | [+0.005, +0.059] | 7 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 7 | +0.027 | [+0.005, +0.059] | 7 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 7 | +0.029 | [+0.006, +0.059] | 7 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 7 | -0.000 | [-0.000, -0.000] | 1 / 6 / 0 | below_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 7 | +0.013 | [+0.002, +0.027] | 7 / 0 / 0 | excluded_by_miss_rule |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 7 | +0.013 | [+0.002, +0.030] | 7 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 7 | +0.013 | [+0.002, +0.030] | 7 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 7 | +0.013 | [+0.002, +0.027] | 7 / 0 / 0 | excluded_by_miss_rule |


