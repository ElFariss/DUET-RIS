# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

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
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.005 | [-0.002, +0.013] | 21 / 15 / 0 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - greedy | 36 | -0.001 | [-0.018, +0.011] | 33 / 3 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.054 | [+0.027, +0.086] | 35 / 1 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 36 | +0.054 | [+0.027, +0.086] | 34 / 2 / 0 | **supported** |


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
| 128 | 10.0 | pair_plus_b35 - greedy | 17 | +0.007 | [+0.003, +0.013] | 13 / 4 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 17 | +0.006 | [+0.002, +0.009] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 17 | +0.033 | [+0.012, +0.065] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 17 | +0.033 | [+0.012, +0.065] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 13 | +0.003 | [-0.015, +0.023] | 6 / 7 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 13 | -0.011 | [-0.059, +0.019] | 11 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 13 | +0.095 | [+0.035, +0.165] | 12 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 13 | +0.094 | [+0.035, +0.163] | 12 / 1 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 6 | +0.004 | [-0.000, +0.011] | 2 / 4 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 6 | +0.005 | [+0.000, +0.015] | 5 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 6 | +0.026 | [+0.000, +0.074] | 6 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 6 | +0.026 | [+0.000, +0.073] | 5 / 1 / 0 | supported |


