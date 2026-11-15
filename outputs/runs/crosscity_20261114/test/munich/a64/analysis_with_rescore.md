# CoupledRIS-Bench Search Benchmark Analysis Report

**Total rows analyzed:** 57600  
**Arrays:** [np.int64(64)]  
**Budgets (ms):** [np.float64(10.0), np.float64(50.0)]  
**Trajectories:** 36  
**Bonferroni family size:** 5 (alpha = 0.01000)

## Cell Performance Summary

| Array | Budget (ms) | Method | Trajectories | Mean Rate (bps/Hz) | Elapsed (ms) | Selector (ms) | Selector Share (%) | Misses | Miss % | Excluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 64 | 10.0 | greedy | 36 | 9.074 | 9.28 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | me_ga | 36 | 8.942 | 9.09 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | nsga2 | 36 | 8.988 | 9.72 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair | 36 | 9.093 | 9.05 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 10.0 | pair_plus_b35 | 36 | 9.091 | 9.62 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | greedy | 36 | 9.085 | 49.28 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | me_ga | 36 | 9.023 | 49.15 | 0.000 | 0.00% | 25 | 0.43% | No |
| 64 | 50.0 | nsga2 | 36 | 9.062 | 49.58 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair | 36 | 9.103 | 49.02 | 0.000 | 0.00% | 0 | 0.00% | No |
| 64 | 50.0 | pair_plus_b35 | 36 | 9.103 | 49.61 | 0.000 | 0.00% | 0 | 0.00% | No |


## Contrast Family (Paired Trajectory Bootstrap)

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | Bonferroni CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 36 | -0.001 | [-0.003, -0.000] | 5 / 31 / 0 | **below_0** |
| 64 | 10.0 | pair_plus_b35 - me_ga | 36 | +0.149 | [+0.072, +0.271] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 36 | +0.103 | [+0.042, +0.199] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - nsga2 | 36 | +0.104 | [+0.043, +0.201] | 36 / 0 / 0 | **supported** |
| 64 | 10.0 | pair - me_ga | 36 | +0.151 | [+0.073, +0.274] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - pair | 36 | +0.000 | [-0.000, +0.001] | 23 / 13 / 0 | **includes_0** |
| 64 | 50.0 | pair_plus_b35 - me_ga | 36 | +0.080 | [+0.033, +0.151] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 36 | +0.040 | [+0.016, +0.074] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - nsga2 | 36 | +0.040 | [+0.016, +0.074] | 36 / 0 / 0 | **supported** |
| 64 | 50.0 | pair - me_ga | 36 | +0.080 | [+0.033, +0.151] | 36 / 0 / 0 | **supported** |


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


### Users: K = 2

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 22 | -0.001 | [-0.002, -0.000] | 4 / 18 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 22 | +0.095 | [+0.052, +0.151] | 22 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 22 | +0.049 | [+0.020, +0.088] | 22 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 22 | +0.049 | [+0.020, +0.090] | 22 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 22 | +0.096 | [+0.052, +0.152] | 22 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 22 | -0.000 | [-0.000, +0.000] | 15 / 7 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 22 | +0.048 | [+0.018, +0.090] | 22 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 22 | +0.012 | [+0.005, +0.025] | 22 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 22 | +0.012 | [+0.005, +0.025] | 22 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 22 | +0.048 | [+0.018, +0.091] | 22 / 0 / 0 | supported |


### Users: K = 3

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 8 | -0.003 | [-0.010, -0.000] | 1 / 7 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 8 | +0.362 | [+0.079, +0.793] | 8 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 8 | +0.287 | [+0.065, +0.613] | 8 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 8 | +0.290 | [+0.065, +0.623] | 8 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 8 | +0.365 | [+0.080, +0.802] | 8 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 8 | +0.000 | [-0.001, +0.002] | 4 / 4 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 8 | +0.203 | [+0.043, +0.454] | 8 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 8 | +0.122 | [+0.040, +0.222] | 8 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 8 | +0.122 | [+0.040, +0.222] | 8 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 8 | +0.203 | [+0.044, +0.454] | 8 / 0 / 0 | supported |


### Users: K = 4

| Array | Budget (ms) | Contrast (A - B) | N Traj | Mean Diff | CI | W / L / T | Status |
|---|---|---|---|---|---|---|---|
| 64 | 10.0 | pair_plus_b35 - pair | 6 | -0.001 | [-0.002, -0.000] | 0 / 6 / 0 | below_0 |
| 64 | 10.0 | pair_plus_b35 - me_ga | 6 | +0.066 | [+0.016, +0.154] | 6 / 0 / 0 | supported |
| 64 | 10.0 | pair_plus_b35 - nsga2 | 6 | +0.058 | [+0.015, +0.131] | 6 / 0 / 0 | supported |
| 64 | 10.0 | pair - nsga2 | 6 | +0.058 | [+0.015, +0.133] | 6 / 0 / 0 | supported |
| 64 | 10.0 | pair - me_ga | 6 | +0.067 | [+0.016, +0.156] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - pair | 6 | +0.000 | [-0.000, +0.000] | 4 / 2 / 0 | includes_0 |
| 64 | 50.0 | pair_plus_b35 - me_ga | 6 | +0.031 | [+0.007, +0.078] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair_plus_b35 - nsga2 | 6 | +0.035 | [+0.008, +0.086] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair - nsga2 | 6 | +0.035 | [+0.008, +0.086] | 6 / 0 / 0 | supported |
| 64 | 50.0 | pair - me_ga | 6 | +0.031 | [+0.007, +0.078] | 6 / 0 / 0 | supported |


