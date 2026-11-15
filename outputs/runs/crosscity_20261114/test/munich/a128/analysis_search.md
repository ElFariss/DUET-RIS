# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 36 | 8.955 | 9.02 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | me_ga | 36 | 8.402 | 2.31 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 36 | 8.750 | 9.25 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 36 | 8.963 | 8.17 | 0.000 | 0.00% | 78 | 1.35% | YES |
| 128 | 10.0 | pair_plus_b35 | 36 | 8.965 | 9.58 | 0.000 | 0.00% | 67 | 1.16% | YES |
| 128 | 50.0 | greedy | 36 | 8.985 | 48.98 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 36 | 8.753 | 44.96 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 36 | 8.862 | 49.06 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 36 | 9.029 | 47.09 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 36 | 9.029 | 49.56 | 0.000 | 0.00% | 133 | 2.31% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 36 | +0.002 | [-0.000, +0.007] | 28 / 8 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.564 | [+0.351, +0.832] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.215 | [+0.085, +0.408] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - nsga2 | 36 | +0.213 | [+0.083, +0.407] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - me_ga | 36 | +0.561 | [+0.350, +0.831] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - pair | 36 | -0.000 | [-0.000, +0.000] | 18 / 17 / 1 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.276 | [+0.126, +0.507] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.166 | [+0.052, +0.350] | 36 / 0 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - nsga2 | 36 | +0.166 | [+0.052, +0.350] | 36 / 0 / 0 | **supported** |
| 128 | 50.0 | pair - me_ga | 36 | +0.276 | [+0.126, +0.507] | 36 / 0 / 0 | **supported** |


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


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 22 | +0.003 | [-0.000, +0.010] | 18 / 4 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 22 | +0.595 | [+0.360, +0.919] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 22 | +0.119 | [+0.045, +0.212] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 22 | +0.117 | [+0.044, +0.207] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 22 | +0.592 | [+0.359, +0.916] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 22 | -0.000 | [-0.000, +0.000] | 8 / 13 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 22 | +0.191 | [+0.099, +0.309] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 22 | +0.074 | [+0.025, +0.151] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 22 | +0.074 | [+0.025, +0.151] | 22 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 22 | +0.191 | [+0.099, +0.309] | 22 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 8 | +0.002 | [-0.002, +0.007] | 5 / 3 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 8 | +0.802 | [+0.279, +1.514] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 8 | +0.565 | [+0.110, +1.226] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 8 | +0.563 | [+0.108, +1.228] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 8 | +0.800 | [+0.277, +1.517] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 8 | +0.000 | [-0.000, +0.000] | 7 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 8 | +0.644 | [+0.117, +1.465] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 8 | +0.483 | [+0.070, +1.122] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 8 | +0.483 | [+0.070, +1.121] | 8 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 8 | +0.644 | [+0.117, +1.465] | 8 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - pair | 6 | +0.001 | [-0.000, +0.002] | 5 / 1 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - me_ga | 6 | +0.131 | [+0.031, +0.327] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair_plus_b35 - nsga2 | 6 | +0.098 | [+0.025, +0.252] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - nsga2 | 6 | +0.098 | [+0.025, +0.251] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - me_ga | 6 | +0.130 | [+0.031, +0.326] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - pair | 6 | +0.000 | [-0.000, +0.000] | 3 / 3 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - me_ga | 6 | +0.097 | [+0.024, +0.256] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - nsga2 | 6 | +0.082 | [+0.022, +0.210] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - nsga2 | 6 | +0.082 | [+0.022, +0.210] | 6 / 0 / 0 | supported |
| 128 | 50.0 | pair - me_ga | 6 | +0.097 | [+0.024, +0.256] | 6 / 0 / 0 | supported |


