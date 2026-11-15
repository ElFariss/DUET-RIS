# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 115200  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 72  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 72 | 5.371 | 9.14 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 72 | 5.136 | 8.72 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 72 | 5.236 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 72 | 5.407 | 8.75 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 72 | 5.403 | 9.51 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 72 | 5.390 | 49.14 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 72 | 5.282 | 48.81 | 0.000 | 0.00% | 4 | 0.03% | No |
| 64 | 50.0 | nsga2 | 72 | 5.355 | 49.50 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 72 | 5.419 | 48.71 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 72 | 5.420 | 49.49 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 72 | +0.032 | [+0.021, +0.045] | 68 / 4 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 72 | +0.035 | [+0.023, +0.050] | 69 / 3 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 72 | +0.029 | [+0.019, +0.042] | 68 / 3 / 1 | **supported** |
| 64 | 50.0 | pair - greedy | 72 | +0.029 | [+0.019, +0.041] | 69 / 2 / 1 | **supported** |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.023 | [+0.009, +0.044] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.025 | [+0.010, +0.050] | 34 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.019 | [+0.007, +0.036] | 32 / 3 / 1 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.019 | [+0.007, +0.036] | 33 / 2 / 1 | supported |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.026, +0.058] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.045 | [+0.029, +0.064] | 35 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.040 | [+0.025, +0.058] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.039 | [+0.024, +0.057] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 34 | +0.030 | [+0.016, +0.052] | 34 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 34 | +0.034 | [+0.017, +0.059] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 34 | +0.026 | [+0.013, +0.045] | 34 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 34 | +0.026 | [+0.013, +0.045] | 34 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 25 | +0.043 | [+0.023, +0.066] | 22 / 3 / 0 | supported |
| 64 | 10.0 | pair - greedy | 25 | +0.048 | [+0.025, +0.073] | 23 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 25 | +0.041 | [+0.021, +0.064] | 23 / 1 / 1 | supported |
| 64 | 50.0 | pair - greedy | 25 | +0.041 | [+0.021, +0.063] | 24 / 0 / 1 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 13 | +0.015 | [+0.002, +0.034] | 12 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 13 | +0.017 | [+0.002, +0.037] | 12 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 13 | +0.015 | [+0.002, +0.035] | 11 / 2 / 0 | supported |
| 64 | 50.0 | pair - greedy | 13 | +0.015 | [+0.002, +0.034] | 11 / 2 / 0 | supported |


