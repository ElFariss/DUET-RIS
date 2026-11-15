# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 3.466 | 9.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 3.332 | 8.78 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 3.379 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 3.492 | 8.75 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 3.490 | 9.54 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 3.479 | 49.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 3.418 | 48.91 | 0.000 | 0.00% | 4 | 0.07% | No |
| 64 | 50.0 | nsga2 | 36 | 3.467 | 49.49 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 3.498 | 48.71 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 3.498 | 49.51 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.023 | [+0.009, +0.044] | 34 / 2 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 36 | +0.025 | [+0.010, +0.050] | 34 / 2 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.019 | [+0.007, +0.036] | 32 / 3 / 1 | **supported** |
| 64 | 50.0 | pair - greedy | 36 | +0.019 | [+0.007, +0.036] | 33 / 2 / 1 | **supported** |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.023 | [+0.009, +0.044] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.025 | [+0.010, +0.050] | 34 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.019 | [+0.007, +0.036] | 32 / 3 / 1 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.019 | [+0.007, +0.036] | 33 / 2 / 1 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 17 | +0.040 | [+0.015, +0.080] | 17 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 17 | +0.044 | [+0.015, +0.090] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 17 | +0.032 | [+0.011, +0.066] | 17 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 17 | +0.032 | [+0.011, +0.066] | 17 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 12 | +0.012 | [+0.001, +0.025] | 10 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 12 | +0.013 | [+0.001, +0.027] | 10 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 12 | +0.011 | [+0.000, +0.022] | 10 / 1 / 1 | supported |
| 64 | 50.0 | pair - greedy | 12 | +0.011 | [+0.000, +0.022] | 11 / 0 / 1 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 7 | +0.000 | [+0.000, +0.001] | 7 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 7 | +0.000 | [+0.000, +0.001] | 7 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 7 | +0.000 | [-0.000, +0.001] | 5 / 2 / 0 | includes_0 |
| 64 | 50.0 | pair - greedy | 7 | +0.000 | [+0.000, +0.001] | 5 / 2 / 0 | supported |


