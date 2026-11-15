# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

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
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.002 | [+0.001, +0.004] | 16 / 20 / 0 | **supported** |
| 128 | 10.0 | pair - greedy | 36 | +0.002 | [+0.001, +0.003] | 35 / 1 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.011 | [+0.005, +0.017] | 35 / 1 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 36 | +0.011 | [+0.005, +0.017] | 36 / 0 / 0 | **supported** |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.002 | [+0.001, +0.004] | 16 / 20 / 0 | supported |
| 128 | 10.0 | pair - greedy | 36 | +0.002 | [+0.001, +0.003] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.011 | [+0.005, +0.017] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.011 | [+0.005, +0.017] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 17 | +0.004 | [+0.001, +0.007] | 11 / 6 / 0 | supported |
| 128 | 10.0 | pair - greedy | 17 | +0.004 | [+0.002, +0.006] | 17 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 17 | +0.018 | [+0.008, +0.030] | 16 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 17 | +0.018 | [+0.008, +0.030] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 12 | +0.001 | [-0.000, +0.003] | 4 / 8 / 0 | includes_0 |
| 128 | 10.0 | pair - greedy | 12 | +0.001 | [+0.000, +0.002] | 12 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 12 | +0.005 | [+0.001, +0.011] | 12 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 12 | +0.005 | [+0.001, +0.010] | 12 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 7 | +0.000 | [-0.000, +0.000] | 1 / 6 / 0 | includes_0 |
| 128 | 10.0 | pair - greedy | 7 | +0.000 | [-0.000, +0.000] | 6 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 7 | +0.001 | [+0.000, +0.002] | 7 / 0 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 7 | +0.001 | [+0.000, +0.002] | 7 / 0 / 0 | supported |


