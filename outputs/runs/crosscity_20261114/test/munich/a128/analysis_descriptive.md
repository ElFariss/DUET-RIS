# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

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
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.010 | [+0.004, +0.019] | 33 / 3 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - greedy | 36 | +0.008 | [+0.003, +0.014] | 31 / 5 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.043 | [+0.016, +0.080] | 35 / 1 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 36 | +0.043 | [+0.016, +0.080] | 36 / 0 / 0 | **supported** |


### Map: munich

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.010 | [+0.004, +0.019] | 33 / 3 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 36 | +0.008 | [+0.003, +0.014] | 31 / 5 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.043 | [+0.016, +0.080] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.043 | [+0.016, +0.080] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 22 | +0.010 | [+0.002, +0.023] | 19 / 3 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 22 | +0.007 | [+0.002, +0.015] | 19 / 3 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 22 | +0.032 | [+0.008, +0.072] | 22 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 22 | +0.032 | [+0.008, +0.072] | 22 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 8 | +0.018 | [+0.005, +0.034] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 8 | +0.016 | [+0.004, +0.031] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 8 | +0.097 | [+0.023, +0.209] | 8 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 8 | +0.097 | [+0.023, +0.209] | 8 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 6 | +0.001 | [+0.000, +0.001] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 6 | +0.000 | [-0.001, +0.001] | 4 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 6 | +0.014 | [+0.004, +0.027] | 5 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 6 | +0.014 | [+0.004, +0.027] | 6 / 0 / 0 | supported |


