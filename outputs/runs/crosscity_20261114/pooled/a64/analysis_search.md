# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 230400  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 144  
**Bonferroni family size:** 5 (alpha = 0.01000)

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
| 64 | 10.0 | pair_plus_b35 - pair | 144 | -0.002 | [-0.004, -0.001] | 10 / 127 / 7 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 144 | +0.217 | [+0.152, +0.297] | 144 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 144 | +0.141 | [+0.098, +0.200] | 144 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 144 | +0.144 | [+0.100, +0.203] | 144 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 144 | +0.219 | [+0.154, +0.301] | 144 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 144 | +0.000 | [+0.000, +0.001] | 87 / 55 / 2 | **supported** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 144 | +0.115 | [+0.079, +0.160] | 144 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 144 | +0.054 | [+0.036, +0.077] | 144 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 144 | +0.053 | [+0.036, +0.076] | 144 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 144 | +0.114 | [+0.078, +0.159] | 144 / 0 / 0 | **supported** |


### Map: berlin

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.003, -0.001] | 3 / 31 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.183 | [+0.096, +0.315] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.128 | [+0.064, +0.243] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.130 | [+0.065, +0.245] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.185 | [+0.097, +0.317] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [-0.000, +0.003] | 22 / 14 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.103 | [+0.048, +0.200] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.046 | [+0.023, +0.090] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.046 | [+0.023, +0.087] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.102 | [+0.048, +0.197] | 36 / 0 / 0 | supported |


### Map: maastricht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.002 | [-0.007, -0.000] | 1 / 33 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.157 | [+0.086, +0.252] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.110 | [+0.061, +0.173] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.113 | [+0.061, +0.180] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.160 | [+0.087, +0.258] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.000] | 17 / 17 / 2 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.031 | [+0.018, +0.049] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.080 | [+0.042, +0.138] | 36 / 0 / 0 | supported |


### Map: munich

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.001 | [-0.003, -0.000] | 5 / 31 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.149 | [+0.072, +0.271] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.103 | [+0.042, +0.199] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.104 | [+0.043, +0.201] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.151 | [+0.073, +0.274] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 23 / 13 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.080 | [+0.033, +0.151] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.040 | [+0.016, +0.074] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.040 | [+0.016, +0.074] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.080 | [+0.033, +0.151] | 36 / 0 / 0 | supported |


### Map: utrecht

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.004 | [-0.007, -0.002] | 1 / 32 / 3 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.378 | [+0.191, +0.620] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.224 | [+0.110, +0.379] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 36 | +0.228 | [+0.113, +0.385] | 36 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 36 | +0.382 | [+0.194, +0.625] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.001 | [+0.000, +0.002] | 25 / 11 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.195 | [+0.102, +0.306] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.098 | [+0.046, +0.161] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 36 | +0.097 | [+0.046, +0.160] | 36 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 36 | +0.195 | [+0.102, +0.305] | 36 / 0 / 0 | supported |


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 79 | -0.002 | [-0.004, -0.001] | 6 / 69 / 4 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 79 | +0.197 | [+0.124, +0.296] | 79 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 79 | +0.107 | [+0.067, +0.166] | 79 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 79 | +0.109 | [+0.069, +0.168] | 79 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 79 | +0.199 | [+0.125, +0.300] | 79 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 79 | +0.001 | [+0.000, +0.002] | 53 / 25 / 1 | supported |
| 64 | 50.0 | pair_plus_b35 - me_ga | 79 | +0.102 | [+0.060, +0.158] | 79 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 79 | +0.028 | [+0.016, +0.049] | 79 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 79 | +0.028 | [+0.016, +0.048] | 79 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 79 | +0.101 | [+0.060, +0.157] | 79 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 42 | -0.004 | [-0.006, -0.002] | 4 / 36 / 2 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 42 | +0.319 | [+0.177, +0.516] | 42 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 42 | +0.237 | [+0.129, +0.381] | 42 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 42 | +0.241 | [+0.131, +0.386] | 42 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 42 | +0.322 | [+0.178, +0.520] | 42 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 42 | +0.001 | [-0.000, +0.001] | 23 / 18 / 1 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 42 | +0.172 | [+0.096, +0.271] | 42 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 42 | +0.105 | [+0.063, +0.157] | 42 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 42 | +0.105 | [+0.062, +0.156] | 42 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 42 | +0.171 | [+0.096, +0.270] | 42 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 23 | -0.001 | [-0.003, -0.000] | 0 / 22 / 1 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 23 | +0.099 | [+0.037, +0.216] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 23 | +0.084 | [+0.033, +0.177] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 23 | +0.085 | [+0.034, +0.180] | 23 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 23 | +0.101 | [+0.038, +0.219] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 23 | +0.000 | [-0.000, +0.000] | 11 / 12 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 23 | +0.054 | [+0.018, +0.123] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 23 | +0.049 | [+0.017, +0.110] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 23 | +0.049 | [+0.017, +0.110] | 23 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 23 | +0.053 | [+0.018, +0.123] | 23 / 0 / 0 | supported |


