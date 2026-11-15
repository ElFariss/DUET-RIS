# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 115200  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 72  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 72 | 5.911 | 9.85 | 0.000 | 0.00% | 2433 | 21.12% | YES |
| 128 | 10.0 | me_ga | 72 | 5.489 | 3.25 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 72 | 5.657 | 10.02 | 0.000 | 0.00% | 5772 | 50.10% | YES |
| 128 | 10.0 | pair | 72 | 5.912 | 9.58 | 0.000 | 0.00% | 3006 | 26.09% | YES |
| 128 | 10.0 | pair_plus_b35 | 72 | 5.915 | 10.39 | 0.000 | 0.00% | 11018 | 95.64% | YES |
| 128 | 50.0 | greedy | 72 | 5.958 | 49.64 | 0.000 | 0.00% | 636 | 5.52% | YES |
| 128 | 50.0 | me_ga | 72 | 5.670 | 44.41 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 72 | 5.790 | 49.82 | 0.000 | 0.00% | 459 | 3.98% | YES |
| 128 | 50.0 | pair | 72 | 5.990 | 47.27 | 0.000 | 0.00% | 94 | 0.82% | YES |
| 128 | 50.0 | pair_plus_b35 | 72 | 5.990 | 50.42 | 0.000 | 0.00% | 10817 | 93.90% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 72 | +0.003 | [-0.001, +0.012] | 32 / 40 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 72 | +0.426 | [+0.255, +0.667] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 72 | +0.258 | [+0.154, +0.401] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - nsga2 | 72 | +0.255 | [+0.152, +0.398] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 72 | +0.423 | [+0.253, +0.663] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 72 | +0.000 | [-0.000, +0.001] | 42 / 30 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 72 | +0.320 | [+0.176, +0.516] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 72 | +0.200 | [+0.105, +0.340] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 72 | +0.200 | [+0.105, +0.340] | 72 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - me_ga | 72 | +0.320 | [+0.176, +0.516] | 72 / 0 / 0 | **excluded_by_miss_rule** |


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
| 128 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.059, +0.140] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - me_ga | 36 | +0.160 | [+0.095, +0.234] | 36 / 0 / 0 | excluded_by_miss_rule |


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
| 128 | 50.0 | pair - nsga2 | 36 | +0.302 | [+0.121, +0.560] | 36 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - me_ga | 36 | +0.480 | [+0.206, +0.840] | 36 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 34 | +0.001 | [-0.000, +0.003] | 20 / 14 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 34 | +0.493 | [+0.302, +0.862] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 34 | +0.229 | [+0.158, +0.306] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 34 | +0.228 | [+0.158, +0.306] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 34 | +0.492 | [+0.302, +0.861] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 34 | +0.000 | [-0.000, +0.000] | 18 / 16 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 34 | +0.297 | [+0.167, +0.542] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 34 | +0.129 | [+0.087, +0.176] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 34 | +0.129 | [+0.087, +0.176] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - me_ga | 34 | +0.297 | [+0.167, +0.542] | 34 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 25 | +0.008 | [-0.003, +0.033] | 9 / 16 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 25 | +0.459 | [+0.162, +0.926] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 25 | +0.367 | [+0.125, +0.733] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 25 | +0.359 | [+0.119, +0.729] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 25 | +0.451 | [+0.157, +0.915] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 25 | +0.001 | [-0.000, +0.002] | 16 / 9 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 25 | +0.445 | [+0.136, +0.898] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 25 | +0.350 | [+0.108, +0.702] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 25 | +0.349 | [+0.108, +0.702] | 25 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - me_ga | 25 | +0.444 | [+0.136, +0.897] | 25 / 0 / 0 | excluded_by_miss_rule |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 13 | -0.001 | [-0.003, +0.000] | 3 / 10 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 13 | +0.185 | [+0.026, +0.600] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 13 | +0.124 | [+0.021, +0.382] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 13 | +0.125 | [+0.021, +0.384] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 13 | +0.186 | [+0.026, +0.603] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 13 | +0.000 | [-0.000, +0.000] | 8 / 5 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 13 | +0.138 | [+0.018, +0.449] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 13 | +0.098 | [+0.015, +0.302] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 13 | +0.098 | [+0.015, +0.302] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - me_ga | 13 | +0.138 | [+0.018, +0.449] | 13 / 0 / 0 | excluded_by_miss_rule |


