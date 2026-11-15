# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

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
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.016 | [+0.004, +0.036] | 31 / 4 / 1 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - greedy | 36 | +0.013 | [+0.003, +0.029] | 32 / 3 / 1 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.021, +0.067] | 35 / 1 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 36 | +0.041 | [+0.021, +0.067] | 35 / 1 / 0 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.016 | [+0.004, +0.036] | 31 / 4 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 36 | +0.013 | [+0.003, +0.029] | 32 / 3 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.021, +0.067] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.041 | [+0.021, +0.067] | 35 / 1 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 23 | +0.024 | [+0.006, +0.055] | 20 / 2 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 23 | +0.019 | [+0.005, +0.044] | 22 / 0 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 23 | +0.054 | [+0.024, +0.094] | 22 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 23 | +0.054 | [+0.024, +0.094] | 22 / 1 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 9 | +0.003 | [+0.000, +0.005] | 7 / 2 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 9 | +0.002 | [-0.001, +0.004] | 7 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 9 | +0.020 | [+0.009, +0.033] | 9 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 9 | +0.020 | [+0.009, +0.033] | 9 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 4 | +0.001 | [+0.000, +0.001] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 4 | -0.001 | [-0.003, +0.001] | 3 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 4 | +0.009 | [+0.003, +0.015] | 4 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 4 | +0.009 | [+0.003, +0.015] | 4 / 0 / 0 | supported |


