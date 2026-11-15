# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 1 (alpha = 0.05000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 8.196 | 9.12 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 8.056 | 8.94 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 8.111 | 9.56 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 8.241 | 8.91 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 8.239 | 9.46 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 8.216 | 49.12 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 8.154 | 48.97 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | nsga2 | 36 | 8.211 | 49.41 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 8.256 | 48.88 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 8.257 | 49.46 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.043 | [+0.015, +0.093] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - greedy | 36 | +0.045 | [+0.016, +0.095] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.015, +0.082] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - greedy | 36 | +0.040 | [+0.015, +0.080] | 36 / 0 / 0 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 36 | +0.043 | [+0.015, +0.093] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 36 | +0.045 | [+0.016, +0.095] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 36 | +0.041 | [+0.015, +0.082] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 36 | +0.040 | [+0.015, +0.080] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 23 | +0.062 | [+0.019, +0.138] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 23 | +0.064 | [+0.020, +0.140] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 23 | +0.055 | [+0.017, +0.120] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 23 | +0.054 | [+0.017, +0.116] | 23 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 9 | +0.012 | [+0.004, +0.022] | 9 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 9 | +0.014 | [+0.006, +0.024] | 9 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 9 | +0.020 | [+0.007, +0.034] | 9 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 9 | +0.020 | [+0.008, +0.034] | 9 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - greedy | 4 | +0.004 | [+0.001, +0.007] | 4 / 0 / 0 | supported |
| 64 | 10.0 | pair - greedy | 4 | +0.005 | [+0.002, +0.007] | 4 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - greedy | 4 | +0.004 | [+0.001, +0.006] | 4 / 0 / 0 | supported |
| 64 | 50.0 | pair - greedy | 4 | +0.004 | [+0.001, +0.006] | 4 / 0 / 0 | supported |


