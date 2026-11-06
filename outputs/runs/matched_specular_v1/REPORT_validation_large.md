# Matched comparison report (specular, validation, search config large)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 24; trajectories: 6; runs: 14400. Target margin 0.015 bit/s/Hz. Protocol sha256 a033b2866c154ecf.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 4.97328 | 48.839 | 0.420 / 0.804 | 1.000 | 103967.0 | 422.3 | 0/240 |
| pair | 4.97331 | 48.501 | 0.418 / 0.799 | 1.000 | 163326.0 | 422.3 | 0/240 |
| random | 4.95872 | 48.861 | 0.220 / 25.606 | 0.525 | 13586.0 | 974.2 | 0/240 |
| population_ga | 4.97094 | 49.347 | 6.704 / 24.578 | 0.988 | 729.8 | 118.0 | 0/240 |
| uniform_ga | 4.97317 | 7.857 | 0.421 / 0.787 | 1.000 | 4911.5 | 422.3 | 0/240 |
| memory_ga | 4.97328 | 8.999 | 0.416 / 0.811 | 1.000 | 5230.3 | 422.3 | 0/240 |
| analytical_ga | 4.97328 | 8.998 | 0.423 / 0.790 | 1.000 | 5242.3 | 422.3 | 0/240 |
| analytical_no_memory_ga | 4.97328 | 9.011 | 0.422 / 0.790 | 1.000 | 5241.0 | 422.3 | 0/240 |
| mlp_ga | 4.97328 | 9.490 | 0.424 / 0.802 | 1.000 | 5242.3 | 422.3 | 0/240 |
| attention_ga | 4.97328 | 9.776 | 0.416 / 0.787 | 1.000 | 5242.3 | 422.3 | 0/240 |
| attention_no_memory_ga | 4.97328 | 9.743 | 0.417 / 0.785 | 1.000 | 5241.0 | 422.3 | 0/240 |
| attention_no_physics_ga | 4.97328 | 9.816 | 0.418 / 0.798 | 1.000 | 5242.3 | 422.3 | 0/240 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| mlp_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| attention_ga - analytical_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| memory_ga - pair | -0.00003 | [-0.00009, -0.00000] | 0.0040 | equivalent |
| attention_ga - attention_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - analytical_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - uniform_ga | 0.00011 | [-0.00000, 0.00041] | 1.0000 | equivalent |
| attention_ga - mlp_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| attention_ga - attention_no_physics_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| population_ga - analytical_ga | -0.00234 | [-0.00394, -0.00069] | 0.0022 | equivalent |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 4.96341 | 0.587 | 0.754 | 724.8 | 0/240 |
| pair | 1 | 4.96340 | 0.586 | 0.750 | 721.0 | 0/240 |
| random | 1 | 4.95231 | 0.607 | 0.346 | 96.5 | 0/240 |
| population_ga | 1 | 4.94327 | 0.303 | 0.333 | 1.6 | 0/240 |
| uniform_ga | 1 | 4.94501 | 0.328 | 0.375 | 65.8 | 0/240 |
| memory_ga | 1 | 4.94501 | 0.341 | 0.375 | 65.8 | 0/240 |
| analytical_ga | 1 | 4.94501 | 0.322 | 0.375 | 65.8 | 0/240 |
| analytical_no_memory_ga | 1 | 4.94501 | 0.291 | 0.375 | 65.0 | 0/240 |
| mlp_ga | 1 | 4.94501 | 0.621 | 0.375 | 65.8 | 0/240 |
| attention_ga | 1 | 4.94501 | 0.842 | 0.375 | 65.8 | 0/240 |
| attention_no_memory_ga | 1 | 4.94501 | 0.806 | 0.375 | 65.0 | 0/240 |
| attention_no_physics_ga | 1 | 4.94501 | 0.853 | 0.375 | 65.8 | 0/240 |
| greedy | 5 | 4.97315 | 4.358 | 1.000 | 8635.1 | 0/240 |
| pair | 5 | 4.97324 | 4.041 | 1.000 | 11813.8 | 0/240 |
| random | 5 | 4.95580 | 4.380 | 0.433 | 1120.2 | 0/240 |
| population_ga | 5 | 4.95428 | 4.348 | 0.429 | 65.2 | 0/240 |
| uniform_ga | 5 | 4.97313 | 4.196 | 1.000 | 3603.2 | 0/240 |
| memory_ga | 5 | 4.97328 | 4.112 | 1.000 | 3617.4 | 0/240 |
| analytical_ga | 5 | 4.97328 | 4.103 | 1.000 | 3620.3 | 0/240 |
| analytical_no_memory_ga | 5 | 4.97328 | 4.061 | 1.000 | 3633.0 | 0/240 |
| mlp_ga | 5 | 4.97328 | 4.217 | 1.000 | 3499.5 | 0/240 |
| attention_ga | 5 | 4.97327 | 4.169 | 1.000 | 3448.6 | 0/240 |
| attention_no_memory_ga | 5 | 4.97326 | 4.173 | 1.000 | 3432.0 | 0/240 |
| attention_no_physics_ga | 5 | 4.97327 | 4.171 | 1.000 | 3434.8 | 0/240 |
| greedy | 10 | 4.97320 | 9.152 | 1.000 | 17686.3 | 0/240 |
| pair | 10 | 4.97330 | 8.804 | 1.000 | 26157.4 | 0/240 |
| random | 10 | 4.95675 | 9.177 | 0.458 | 2308.5 | 0/240 |
| population_ga | 10 | 4.95921 | 9.361 | 0.583 | 131.3 | 1/240 |
| uniform_ga | 10 | 4.97314 | 6.518 | 1.000 | 4189.0 | 0/240 |
| memory_ga | 10 | 4.97328 | 6.469 | 1.000 | 4256.8 | 0/240 |
| analytical_ga | 10 | 4.97328 | 6.460 | 1.000 | 4260.2 | 0/240 |
| analytical_no_memory_ga | 10 | 4.97328 | 6.414 | 1.000 | 4298.6 | 0/240 |
| mlp_ga | 10 | 4.97328 | 6.591 | 1.000 | 4171.5 | 0/240 |
| attention_ga | 10 | 4.97328 | 6.596 | 1.000 | 4075.9 | 0/240 |
| attention_no_memory_ga | 10 | 4.97328 | 6.511 | 1.000 | 4094.8 | 0/240 |
| attention_no_physics_ga | 10 | 4.97328 | 6.657 | 1.000 | 4048.5 | 0/240 |
| greedy | 50 | 4.97328 | 48.839 | 1.000 | 103967.0 | 0/240 |
| pair | 50 | 4.97331 | 48.501 | 1.000 | 163326.0 | 0/240 |
| random | 50 | 4.95872 | 48.861 | 0.525 | 13586.0 | 0/240 |
| population_ga | 50 | 4.97094 | 49.347 | 0.988 | 729.8 | 0/240 |
| uniform_ga | 50 | 4.97317 | 7.857 | 1.000 | 4911.5 | 0/240 |
| memory_ga | 50 | 4.97328 | 8.999 | 1.000 | 5230.3 | 0/240 |
| analytical_ga | 50 | 4.97328 | 8.998 | 1.000 | 5242.3 | 0/240 |
| analytical_no_memory_ga | 50 | 4.97328 | 9.011 | 1.000 | 5241.0 | 0/240 |
| mlp_ga | 50 | 4.97328 | 9.490 | 1.000 | 5242.3 | 0/240 |
| attention_ga | 50 | 4.97328 | 9.776 | 1.000 | 5242.3 | 0/240 |
| attention_no_memory_ga | 50 | 4.97328 | 9.743 | 1.000 | 5241.0 | 0/240 |
| attention_no_physics_ga | 50 | 4.97328 | 9.816 | 1.000 | 5242.3 | 0/240 |
| greedy | 100 | 4.97329 | 98.839 | 1.000 | 213361.1 | 0/240 |
| pair | 100 | 4.97331 | 98.497 | 1.000 | 336734.4 | 0/240 |
| random | 100 | 4.95953 | 98.860 | 0.588 | 27720.5 | 0/240 |
| population_ga | 100 | 4.97263 | 99.348 | 1.000 | 1471.3 | 0/240 |
| uniform_ga | 100 | 4.97317 | 8.130 | 1.000 | 4911.5 | 0/240 |
| memory_ga | 100 | 4.97328 | 9.215 | 1.000 | 5230.3 | 0/240 |
| analytical_ga | 100 | 4.97328 | 9.044 | 1.000 | 5242.3 | 0/240 |
| analytical_no_memory_ga | 100 | 4.97328 | 9.135 | 1.000 | 5241.0 | 0/240 |
| mlp_ga | 100 | 4.97328 | 9.601 | 1.000 | 5242.3 | 0/240 |
| attention_ga | 100 | 4.97328 | 9.834 | 1.000 | 5242.3 | 0/240 |
| attention_no_memory_ga | 100 | 4.97328 | 9.825 | 1.000 | 5241.0 | 0/240 |
| attention_no_physics_ga | 100 | 4.97328 | 9.856 | 1.000 | 5242.3 | 0/240 |
