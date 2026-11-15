# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 172800  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 108  
**Bonferroni family size:** 1 (alpha = 0.05000)

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
| 128 | 10.0 | pair_plus_b35 - greedy | 108 | +0.008 | [+0.003, +0.015] | 68 / 39 / 1 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - greedy | 108 | +0.005 | [-0.003, +0.012] | 100 / 7 / 1 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 108 | +0.035 | [+0.023, +0.049] | 105 / 3 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 108 | +0.035 | [+0.023, +0.049] | 105 / 3 / 0 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.016 | [+0.004, +0.036] | 31 / 4 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 36 | +0.013 | [+0.003, +0.029] | 32 / 3 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.021, +0.067] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.041 | [+0.021, +0.067] | 35 / 1 / 0 | supported |


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
| 128 | 10.0 | pair_plus_b35 - greedy | 57 | +0.013 | [+0.005, +0.026] | 44 / 12 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 57 | +0.011 | [+0.004, +0.021] | 56 / 0 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 57 | +0.037 | [+0.022, +0.056] | 55 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 57 | +0.037 | [+0.022, +0.056] | 56 / 1 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 34 | +0.002 | [-0.005, +0.010] | 17 / 17 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 34 | -0.004 | [-0.022, +0.008] | 30 / 4 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 34 | +0.043 | [+0.019, +0.075] | 33 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 34 | +0.043 | [+0.018, +0.074] | 33 / 1 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 17 | +0.002 | [+0.000, +0.004] | 7 / 10 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 17 | +0.002 | [-0.001, +0.005] | 14 / 3 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 17 | +0.012 | [+0.002, +0.029] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 17 | +0.012 | [+0.002, +0.029] | 16 / 1 / 0 | supported |


