# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 36 | 4.310 | 9.11 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | me_ga | 36 | 4.060 | 2.30 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 36 | 4.148 | 9.25 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 36 | 4.312 | 8.90 | 0.000 | 0.00% | 35 | 0.61% | YES |
| 128 | 10.0 | pair_plus_b35 | 36 | 4.312 | 9.58 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | greedy | 36 | 4.324 | 48.91 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 36 | 4.175 | 43.80 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 36 | 4.237 | 49.05 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 36 | 4.334 | 46.39 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 36 | 4.334 | 49.61 | 0.000 | 0.00% | 73 | 1.27% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 14 / 22 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.252 | [+0.155, +0.357] | 36 / 0 / 0 | **supported** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.164 | [+0.093, +0.245] | 36 / 0 / 0 | **supported** |
| 128 | 10.0 | pair - nsga2 | 36 | +0.164 | [+0.093, +0.245] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 36 | +0.252 | [+0.155, +0.357] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 22 / 14 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.059, +0.140] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.059, +0.140] | 36 / 0 / 0 | **supported** |
| 128 | 50.0 | pair - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | **supported** |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 14 / 22 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.252 | [+0.155, +0.357] | 36 / 0 / 0 | supported |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.164 | [+0.093, +0.245] | 36 / 0 / 0 | supported |
| 128 | 10.0 | pair - nsga2 | 36 | +0.164 | [+0.093, +0.245] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 36 | +0.252 | [+0.155, +0.357] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 22 / 14 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.059, +0.140] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.059, +0.140] | 36 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 17 | +0.000 | [-0.001, +0.002] | 8 / 9 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 17 | +0.412 | [+0.276, +0.553] | 17 / 0 / 0 | supported |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 17 | +0.244 | [+0.123, +0.378] | 17 / 0 / 0 | supported |
| 128 | 10.0 | pair - nsga2 | 17 | +0.244 | [+0.123, +0.379] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 17 | +0.412 | [+0.276, +0.554] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 17 | +0.000 | [-0.000, +0.001] | 12 / 5 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 17 | +0.243 | [+0.136, +0.355] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 17 | +0.130 | [+0.069, +0.194] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 17 | +0.130 | [+0.069, +0.194] | 17 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 17 | +0.242 | [+0.136, +0.355] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 12 | +0.000 | [-0.000, +0.002] | 4 / 8 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 12 | +0.143 | [+0.054, +0.271] | 12 / 0 / 0 | supported |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 12 | +0.120 | [+0.047, +0.223] | 12 / 0 / 0 | supported |
| 128 | 10.0 | pair - nsga2 | 12 | +0.120 | [+0.047, +0.222] | 12 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 12 | +0.143 | [+0.054, +0.270] | 12 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 12 | +0.000 | [-0.000, +0.001] | 6 / 6 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 12 | +0.112 | [+0.043, +0.206] | 12 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 12 | +0.088 | [+0.036, +0.154] | 12 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 12 | +0.087 | [+0.036, +0.153] | 12 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 12 | +0.112 | [+0.043, +0.205] | 12 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 7 | -0.000 | [-0.000, +0.000] | 2 / 5 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 7 | +0.049 | [+0.015, +0.093] | 7 / 0 / 0 | supported |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 7 | +0.044 | [+0.013, +0.084] | 7 / 0 / 0 | supported |
| 128 | 10.0 | pair - nsga2 | 7 | +0.044 | [+0.013, +0.085] | 7 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 7 | +0.049 | [+0.015, +0.093] | 7 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 7 | +0.000 | [-0.000, +0.000] | 4 / 3 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 7 | +0.040 | [+0.011, +0.079] | 7 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 7 | +0.036 | [+0.009, +0.072] | 7 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 7 | +0.036 | [+0.009, +0.072] | 7 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 7 | +0.040 | [+0.011, +0.079] | 7 / 0 / 0 | supported |


