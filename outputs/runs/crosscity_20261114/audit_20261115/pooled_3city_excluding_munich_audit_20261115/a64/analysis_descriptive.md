# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 172800  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 108  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 108 | 6.313 | 9.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 108 | 6.109 | 8.80 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 108 | 6.195 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 108 | 6.351 | 8.80 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 108 | 6.349 | 9.49 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 108 | 6.332 | 49.13 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 108 | 6.239 | 48.86 | 0.000 | 0.00% | 4 | 0.02% | No |
| 64 | 50.0 | nsga2 | 108 | 6.307 | 49.47 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 108 | 6.365 | 48.77 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 108 | 6.365 | 49.48 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 108 | +0.036 | [+0.022, +0.055] | 104 / 4 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 108 | +0.038 | [+0.024, +0.058] | 105 / 3 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 108 | +0.033 | [+0.021, +0.049] | 104 / 3 / 1 | **supported** |
| 64 | 50.0 | pair - greedy | 108 | +0.033 | [+0.021, +0.048] | 105 / 2 / 1 | **supported** |


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
| 64 | 10.0 | pair_plus_b35 - greedy | 57 | +0.043 | [+0.021, +0.079] | 57 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 57 | +0.046 | [+0.022, +0.082] | 57 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 57 | +0.038 | [+0.018, +0.067] | 57 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 57 | +0.037 | [+0.018, +0.065] | 57 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 34 | +0.035 | [+0.019, +0.053] | 31 / 3 / 0 | supported |
| 64 | 10.0 | pair - greedy | 34 | +0.039 | [+0.022, +0.058] | 32 / 2 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 34 | +0.036 | [+0.020, +0.053] | 32 / 1 / 1 | supported |
| 64 | 50.0 | pair - greedy | 34 | +0.035 | [+0.020, +0.052] | 33 / 0 / 1 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 17 | +0.013 | [+0.002, +0.027] | 16 / 1 / 0 | supported |
| 64 | 10.0 | pair - greedy | 17 | +0.014 | [+0.002, +0.030] | 16 / 1 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 17 | +0.013 | [+0.002, +0.028] | 15 / 2 / 0 | supported |
| 64 | 50.0 | pair - greedy | 17 | +0.013 | [+0.002, +0.027] | 15 / 2 / 0 | supported |


