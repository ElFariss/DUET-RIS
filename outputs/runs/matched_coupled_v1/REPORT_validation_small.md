# Matched comparison report (coupled, validation, search config small)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 48; trajectories: 3; runs: 28800. Target margin 0.015 bit/s/Hz. Protocol sha256 a033b2866c154ecf.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 14.36323 | 49.201 | 0.477 / 0.665 | 0.108 | 23766.6 | 523.3 | 0/480 |
| pair | 15.52037 | 48.972 | 0.493 / 39.650 | 0.169 | 77811.5 | 12152.9 | 0/480 |
| random | 13.85489 | 49.225 | 0.478 / 0.682 | 0.104 | 282.4 | 1.0 | 0/480 |
| population_ga | 13.89523 | 49.341 | 0.479 / 0.663 | 0.104 | 313.8 | 1.0 | 0/480 |
| uniform_ga | 14.61071 | 10.321 | 0.478 / 0.679 | 0.108 | 3682.8 | 168.2 | 0/480 |
| memory_ga | 14.90325 | 12.083 | 0.477 / 6.204 | 0.125 | 4039.1 | 429.7 | 0/480 |
| analytical_ga | 14.91480 | 11.759 | 0.480 / 6.184 | 0.125 | 4022.3 | 429.7 | 0/480 |
| analytical_no_memory_ga | 14.57480 | 7.656 | 0.479 / 6.213 | 0.125 | 2644.2 | 429.7 | 0/480 |
| mlp_ga | 14.93219 | 12.873 | 0.481 / 7.112 | 0.125 | 4047.7 | 429.7 | 0/480 |
| attention_ga | 14.87705 | 13.100 | 0.482 / 6.783 | 0.125 | 3893.1 | 429.7 | 0/480 |
| attention_no_memory_ga | 14.58112 | 9.285 | 0.480 / 6.776 | 0.125 | 2610.6 | 429.7 | 0/480 |
| attention_no_physics_ga | 14.89151 | 13.647 | 0.477 / 6.783 | 0.125 | 3980.4 | 429.7 | 0/480 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | -0.02620 | [-0.21326, 0.14665] | 1.0000 | inconclusive |
| mlp_ga - memory_ga | 0.02893 | [-0.09491, 0.24928] | 1.0000 | inconclusive |
| analytical_ga - memory_ga | 0.01154 | [0.00000, 0.03265] | 0.4248 | inconclusive |
| attention_ga - analytical_ga | -0.03775 | [-0.21524, 0.14665] | 1.0000 | inconclusive |
| memory_ga - pair | -0.61712 | [-0.79561, -0.30232] | 0.0022 | deteriorated |
| attention_ga - attention_no_memory_ga | 0.29593 | [0.24727, 0.33797] | 0.0022 | numerically_unresolved |
| analytical_ga - analytical_no_memory_ga | 0.34000 | [0.09029, 0.57762] | 0.0022 | numerically_unresolved |
| analytical_ga - uniform_ga | 0.30408 | [0.14063, 0.54673] | 0.0022 | numerically_unresolved |
| attention_ga - mlp_ga | -0.05514 | [-0.11835, 0.05557] | 1.0000 | inconclusive |
| attention_ga - attention_no_physics_ga | -0.01446 | [-0.14537, 0.14665] | 1.0000 | inconclusive |
| population_ga - analytical_ga | -1.01956 | [-1.59406, -0.23457] | 0.0022 | deteriorated |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 13.85489 | 0.522 | 0.104 | 1.0 | 0/480 |
| pair | 1 | 13.85489 | 0.523 | 0.104 | 1.0 | 0/480 |
| random | 1 | 13.85489 | 0.524 | 0.104 | 1.0 | 1/480 |
| population_ga | 1 | 13.85489 | 0.595 | 0.104 | 1.0 | 2/480 |
| uniform_ga | 1 | 13.85489 | 0.609 | 0.104 | 64.9 | 1/480 |
| memory_ga | 1 | 13.85489 | 0.643 | 0.104 | 65.0 | 0/480 |
| analytical_ga | 1 | 13.85489 | 0.637 | 0.104 | 64.9 | 1/480 |
| analytical_no_memory_ga | 1 | 13.85489 | 0.624 | 0.104 | 65.0 | 0/480 |
| mlp_ga | 1 | 13.85489 | 0.630 | 0.104 | 65.0 | 0/480 |
| attention_ga | 1 | 13.85489 | 0.610 | 0.104 | 65.0 | 0/480 |
| attention_no_memory_ga | 1 | 13.85489 | 0.600 | 0.104 | 65.0 | 0/480 |
| attention_no_physics_ga | 1 | 13.85489 | 0.609 | 0.104 | 65.0 | 0/480 |
| greedy | 5 | 13.91485 | 4.175 | 0.104 | 1725.4 | 0/480 |
| pair | 5 | 14.96903 | 4.026 | 0.125 | 5046.9 | 0/480 |
| random | 5 | 13.85489 | 4.217 | 0.104 | 22.4 | 0/480 |
| population_ga | 5 | 13.85489 | 4.323 | 0.104 | 24.1 | 0/480 |
| uniform_ga | 5 | 14.44816 | 4.899 | 0.104 | 2476.5 | 0/480 |
| memory_ga | 5 | 14.75912 | 4.883 | 0.108 | 2407.5 | 1/480 |
| analytical_ga | 5 | 14.76538 | 4.895 | 0.110 | 2528.5 | 0/480 |
| analytical_no_memory_ga | 5 | 14.54217 | 4.826 | 0.113 | 2166.3 | 0/480 |
| mlp_ga | 5 | 14.84434 | 4.924 | 0.125 | 1907.7 | 0/480 |
| attention_ga | 5 | 14.78060 | 4.937 | 0.125 | 1643.0 | 1/480 |
| attention_no_memory_ga | 5 | 14.52041 | 4.867 | 0.125 | 1261.5 | 1/480 |
| attention_no_physics_ga | 5 | 14.78449 | 4.939 | 0.125 | 1643.1 | 3/480 |
| greedy | 10 | 13.99455 | 9.211 | 0.104 | 4152.9 | 0/480 |
| pair | 10 | 15.07210 | 8.979 | 0.129 | 13047.9 | 0/480 |
| random | 10 | 13.85489 | 9.216 | 0.104 | 50.8 | 0/480 |
| population_ga | 10 | 13.86002 | 9.330 | 0.104 | 55.9 | 0/480 |
| uniform_ga | 10 | 14.61106 | 9.526 | 0.108 | 3506.1 | 0/480 |
| memory_ga | 10 | 14.85941 | 9.703 | 0.125 | 3682.2 | 0/480 |
| analytical_ga | 10 | 14.87029 | 9.688 | 0.125 | 3651.5 | 4/480 |
| analytical_no_memory_ga | 10 | 14.57480 | 7.278 | 0.125 | 2636.8 | 0/480 |
| mlp_ga | 10 | 14.88503 | 9.817 | 0.125 | 3642.8 | 1/480 |
| attention_ga | 10 | 14.81211 | 9.863 | 0.125 | 3496.9 | 2/480 |
| attention_no_memory_ga | 10 | 14.57885 | 9.008 | 0.125 | 2586.9 | 0/480 |
| attention_no_physics_ga | 10 | 14.83572 | 9.879 | 0.125 | 3527.0 | 4/480 |
| greedy | 50 | 14.36323 | 49.201 | 0.108 | 23766.6 | 0/480 |
| pair | 50 | 15.52037 | 48.972 | 0.169 | 77811.5 | 0/480 |
| random | 50 | 13.85489 | 49.225 | 0.104 | 282.4 | 0/480 |
| population_ga | 50 | 13.89523 | 49.341 | 0.104 | 313.8 | 0/480 |
| uniform_ga | 50 | 14.61071 | 10.321 | 0.108 | 3682.8 | 0/480 |
| memory_ga | 50 | 14.90325 | 12.083 | 0.125 | 4039.1 | 0/480 |
| analytical_ga | 50 | 14.91480 | 11.759 | 0.125 | 4022.3 | 0/480 |
| analytical_no_memory_ga | 50 | 14.57480 | 7.656 | 0.125 | 2644.2 | 0/480 |
| mlp_ga | 50 | 14.93219 | 12.873 | 0.125 | 4047.7 | 0/480 |
| attention_ga | 50 | 14.87705 | 13.100 | 0.125 | 3893.1 | 0/480 |
| attention_no_memory_ga | 50 | 14.58112 | 9.285 | 0.125 | 2610.6 | 0/480 |
| attention_no_physics_ga | 50 | 14.89151 | 13.647 | 0.125 | 3980.4 | 0/480 |
| greedy | 100 | 14.57007 | 99.204 | 0.113 | 48837.8 | 0/480 |
| pair | 100 | 15.83298 | 98.973 | 0.212 | 160718.4 | 0/480 |
| random | 100 | 13.85489 | 99.223 | 0.104 | 579.6 | 0/480 |
| population_ga | 100 | 13.96202 | 99.339 | 0.104 | 645.2 | 0/480 |
| uniform_ga | 100 | 14.61071 | 10.118 | 0.108 | 3682.8 | 0/480 |
| memory_ga | 100 | 14.90325 | 11.913 | 0.125 | 4039.1 | 0/480 |
| analytical_ga | 100 | 14.91480 | 12.172 | 0.125 | 4022.3 | 0/480 |
| analytical_no_memory_ga | 100 | 14.57480 | 7.763 | 0.125 | 2644.2 | 0/480 |
| mlp_ga | 100 | 14.93219 | 12.827 | 0.125 | 4047.7 | 0/480 |
| attention_ga | 100 | 14.87705 | 13.460 | 0.125 | 3893.1 | 0/480 |
| attention_no_memory_ga | 100 | 14.58112 | 8.845 | 0.125 | 2610.6 | 0/480 |
| attention_no_physics_ga | 100 | 14.89151 | 14.145 | 0.125 | 3980.4 | 0/480 |
