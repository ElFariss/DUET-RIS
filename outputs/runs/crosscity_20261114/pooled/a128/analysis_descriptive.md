# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 230400  
**Arrays:** [np.int64(128)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 144  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 128 | 10.0 | greedy | 144 | 7.168 | 9.05 | 0.000 | 0.00% | 24 | 0.10% | No |
| 128 | 10.0 | me_ga | 144 | 6.700 | 2.40 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | nsga2 | 144 | 6.929 | 9.24 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 10.0 | pair | 144 | 7.174 | 8.52 | 0.000 | 0.00% | 340 | 1.48% | YES |
| 128 | 10.0 | pair_plus_b35 | 144 | 7.177 | 9.58 | 0.000 | 0.00% | 394 | 1.71% | YES |
| 128 | 50.0 | greedy | 144 | 7.212 | 48.92 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | me_ga | 144 | 6.947 | 44.28 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | nsga2 | 144 | 7.061 | 49.04 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair | 144 | 7.249 | 46.77 | 0.000 | 0.00% | 0 | 0.00% | No |
| 128 | 50.0 | pair_plus_b35 | 144 | 7.249 | 49.59 | 0.000 | 0.00% | 598 | 2.60% | YES |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 144 | +0.008 | [+0.004, +0.014] | 101 / 42 / 1 | **excluded_by_miss_rule** |
| 128 | 10.0 | pair - greedy | 144 | +0.005 | [-0.000, +0.011] | 131 / 12 / 1 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair_plus_b35 - greedy | 144 | +0.037 | [+0.025, +0.051] | 140 / 4 / 0 | **excluded_by_miss_rule** |
| 128 | 50.0 | pair - greedy | 144 | +0.037 | [+0.025, +0.051] | 141 / 3 / 0 | **supported** |


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


### Map: munich

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 36 | +0.010 | [+0.004, +0.019] | 33 / 3 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 36 | +0.008 | [+0.003, +0.014] | 31 / 5 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 36 | +0.043 | [+0.016, +0.080] | 35 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 36 | +0.043 | [+0.016, +0.080] | 36 / 0 / 0 | supported |


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
| 128 | 10.0 | pair_plus_b35 - greedy | 79 | +0.012 | [+0.005, +0.022] | 63 / 15 / 1 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 79 | +0.010 | [+0.004, +0.018] | 75 / 3 / 1 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 79 | +0.036 | [+0.022, +0.052] | 77 / 2 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 79 | +0.036 | [+0.022, +0.052] | 78 / 1 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 42 | +0.005 | [-0.001, +0.012] | 25 / 17 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 42 | +0.000 | [-0.016, +0.010] | 38 / 4 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 42 | +0.054 | [+0.027, +0.088] | 41 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 42 | +0.053 | [+0.027, +0.087] | 41 / 1 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 128 | 10.0 | pair_plus_b35 - greedy | 23 | +0.001 | [+0.000, +0.003] | 13 / 10 / 0 | excluded_by_miss_rule |
| 128 | 10.0 | pair - greedy | 23 | +0.001 | [-0.000, +0.004] | 18 / 5 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair_plus_b35 - greedy | 23 | +0.012 | [+0.003, +0.026] | 22 / 1 / 0 | excluded_by_miss_rule |
| 128 | 50.0 | pair - greedy | 23 | +0.012 | [+0.003, +0.026] | 22 / 1 / 0 | supported |


