# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 9.074 | 9.12 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 8.942 | 8.92 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 8.988 | 9.55 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 9.093 | 8.89 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 9.091 | 9.46 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 9.085 | 49.12 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 9.023 | 48.99 | 0.000 | 0.00% | 1 | 0.02% | No |
| 64 | 50.0 | nsga2 | 36 | 9.062 | 49.41 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 9.103 | 48.86 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 9.103 | 49.45 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.017 | [+0.009, +0.027] | 34 / 2 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 36 | +0.018 | [+0.010, +0.029] | 34 / 2 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.018 | [+0.008, +0.030] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - greedy | 36 | +0.018 | [+0.008, +0.030] | 36 / 0 / 0 | **supported** |


### Map: munich

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.017 | [+0.009, +0.027] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.018 | [+0.010, +0.029] | 34 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.018 | [+0.008, +0.030] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.018 | [+0.008, +0.030] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 22 | +0.013 | [+0.006, +0.021] | 21 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 22 | +0.014 | [+0.006, +0.023] | 21 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 22 | +0.015 | [+0.005, +0.031] | 22 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 22 | +0.015 | [+0.005, +0.031] | 22 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 8 | +0.035 | [+0.011, +0.066] | 8 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 8 | +0.039 | [+0.012, +0.074] | 8 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 8 | +0.033 | [+0.012, +0.064] | 8 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 8 | +0.033 | [+0.012, +0.064] | 8 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 6 | +0.007 | [+0.001, +0.016] | 5 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 6 | +0.007 | [+0.001, +0.017] | 5 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 6 | +0.007 | [+0.001, +0.015] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 6 | +0.007 | [+0.001, +0.015] | 6 / 0 / 0 | supported |


