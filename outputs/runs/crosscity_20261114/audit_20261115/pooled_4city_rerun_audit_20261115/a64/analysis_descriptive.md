# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 230400  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 144  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 144 | 7.003 | 9.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 144 | 6.817 | 8.83 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 144 | 6.893 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 144 | 7.037 | 8.82 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 144 | 7.034 | 9.48 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 144 | 7.020 | 49.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 144 | 6.935 | 48.89 | 0.000 | 0.00% | 5 | 0.02% | No |
| 64 | 50.0 | nsga2 | 144 | 6.996 | 49.45 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 144 | 7.049 | 48.79 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 144 | 7.050 | 49.47 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 144 | +0.031 | [+0.020, +0.046] | 138 / 6 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 144 | +0.034 | [+0.022, +0.049] | 139 / 5 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 144 | +0.029 | [+0.020, +0.042] | 140 / 3 / 1 | **supported** |
| 64 | 50.0 | pair - greedy | 144 | +0.029 | [+0.019, +0.041] | 141 / 2 / 1 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.043 | [+0.015, +0.093] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.045 | [+0.016, +0.095] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.015, +0.082] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.040 | [+0.015, +0.080] | 36 / 0 / 0 | supported |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.023 | [+0.009, +0.044] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.025 | [+0.010, +0.050] | 34 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.019 | [+0.007, +0.036] | 32 / 3 / 1 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.019 | [+0.007, +0.036] | 33 / 2 / 1 | supported |


### Map: munich

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.017 | [+0.009, +0.027] | 34 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.018 | [+0.010, +0.029] | 34 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.018 | [+0.008, +0.030] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.018 | [+0.008, +0.030] | 36 / 0 / 0 | supported |


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
| 64 | 10.0 | pair_plus_b35 - greedy | 79 | +0.035 | [+0.018, +0.060] | 78 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 79 | +0.037 | [+0.020, +0.062] | 78 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 79 | +0.032 | [+0.017, +0.052] | 79 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 79 | +0.031 | [+0.017, +0.051] | 79 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 42 | +0.035 | [+0.021, +0.051] | 39 / 3 / 0 | supported |
| 64 | 10.0 | pair - greedy | 42 | +0.039 | [+0.024, +0.056] | 40 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 42 | +0.035 | [+0.022, +0.051] | 40 / 1 / 1 | supported |
| 64 | 50.0 | pair - greedy | 42 | +0.035 | [+0.021, +0.050] | 41 / 0 / 1 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 23 | +0.011 | [+0.003, +0.022] | 21 / 2 / 0 | supported |
| 64 | 10.0 | pair - greedy | 23 | +0.012 | [+0.004, +0.024] | 21 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 23 | +0.011 | [+0.003, +0.022] | 21 / 2 / 0 | supported |
| 64 | 50.0 | pair - greedy | 23 | +0.011 | [+0.003, +0.022] | 21 / 2 / 0 | supported |


