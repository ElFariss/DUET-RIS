# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 115200  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 72  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 72 | 5.911 | 9.07 | 0.000 | 0.00% | 24 | 0.21% | No |
| 128 | 10.0 | me_ga | 72 | 5.489 | 2.46 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 72 | 5.657 | 9.23 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 72 | 5.912 | 8.79 | 0.000 | 0.00% | 133 | 1.16% | YES |
| 128 | 10.0 | pair_plus_b35 | 72 | 5.915 | 9.60 | 0.000 | 0.00% | 221 | 1.92% | YES |
| 128 | 50.0 | greedy | 72 | 5.958 | 48.86 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 72 | 5.670 | 43.60 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 72 | 5.790 | 49.03 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 72 | 5.990 | 46.48 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 72 | 5.990 | 49.63 | 0.000 | 0.00% | 413 | 3.58% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 72 | +0.004 | [+0.000, +0.008] | 37 / 35 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - greedy | 72 | +0.001 | [-0.008, +0.006] | 68 / 4 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 72 | +0.032 | [+0.018, +0.050] | 70 / 2 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 72 | +0.032 | [+0.018, +0.049] | 70 / 2 / 0 | **supported** |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.002 | [+0.001, +0.004] | 16 / 20 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 36 | +0.002 | [+0.001, +0.003] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.011 | [+0.005, +0.017] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.011 | [+0.005, +0.017] | 36 / 0 / 0 | supported |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.005 | [-0.002, +0.013] | 21 / 15 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 36 | -0.001 | [-0.018, +0.011] | 33 / 3 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.054 | [+0.027, +0.086] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.054 | [+0.027, +0.086] | 34 / 2 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 34 | +0.005 | [+0.003, +0.009] | 24 / 10 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 34 | +0.005 | [+0.003, +0.007] | 34 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 34 | +0.025 | [+0.013, +0.042] | 33 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 34 | +0.025 | [+0.013, +0.042] | 34 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 25 | +0.002 | [-0.007, +0.013] | 10 / 15 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 25 | -0.006 | [-0.031, +0.011] | 23 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 25 | +0.052 | [+0.018, +0.095] | 24 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 25 | +0.051 | [+0.018, +0.093] | 24 / 1 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 13 | +0.002 | [-0.000, +0.005] | 3 / 10 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 13 | +0.003 | [+0.000, +0.007] | 11 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 13 | +0.013 | [+0.000, +0.035] | 13 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 13 | +0.013 | [+0.000, +0.035] | 12 / 1 / 0 | supported |


