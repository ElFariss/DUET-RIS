# Matched comparison report (specular, validation, search config medium)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 24; trajectories: 6; runs: 14400. Target margin 0.015 bit/s/Hz. Protocol sha256 a033b2866c154ecf.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 4.97328 | 48.838 | 0.435 / 0.807 | 1.000 | 103610.7 | 422.3 | 0/240 |
| pair | 4.97331 | 48.513 | 0.427 / 0.799 | 1.000 | 162870.9 | 422.3 | 0/240 |
| random | 4.95869 | 48.862 | 0.226 / 25.884 | 0.529 | 13510.8 | 1048.2 | 0/240 |
| population_ga | 4.97082 | 49.346 | 6.729 / 23.192 | 0.979 | 711.1 | 112.8 | 0/240 |
| uniform_ga | 4.97314 | 4.704 | 0.435 / 0.802 | 1.000 | 3636.2 | 422.3 | 0/240 |
| memory_ga | 4.97327 | 4.989 | 0.427 / 0.796 | 1.000 | 3807.0 | 422.3 | 0/240 |
| analytical_ga | 4.97327 | 4.977 | 0.431 / 0.806 | 1.000 | 3807.0 | 422.3 | 0/240 |
| analytical_no_memory_ga | 4.97327 | 4.931 | 0.428 / 0.800 | 1.000 | 3805.7 | 422.3 | 0/240 |
| mlp_ga | 4.97327 | 5.379 | 0.428 / 0.800 | 1.000 | 3807.0 | 422.3 | 0/240 |
| attention_ga | 4.97327 | 5.594 | 0.438 / 0.802 | 1.000 | 3807.0 | 422.3 | 0/240 |
| attention_no_memory_ga | 4.97327 | 5.704 | 0.423 / 0.798 | 1.000 | 3805.7 | 422.3 | 0/240 |
| attention_no_physics_ga | 4.97327 | 5.684 | 0.426 / 0.805 | 1.000 | 3807.0 | 422.3 | 0/240 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| mlp_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| attention_ga - analytical_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| memory_ga - pair | -0.00004 | [-0.00009, -0.00000] | 0.0040 | equivalent |
| attention_ga - attention_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - analytical_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - uniform_ga | 0.00013 | [-0.00000, 0.00052] | 1.0000 | equivalent |
| attention_ga - mlp_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| attention_ga - attention_no_physics_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| population_ga - analytical_ga | -0.00245 | [-0.00430, -0.00072] | 0.0022 | equivalent |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 4.96297 | 0.586 | 0.713 | 701.6 | 0/240 |
| pair | 1 | 4.96295 | 0.586 | 0.708 | 693.8 | 0/240 |
| random | 1 | 4.95230 | 0.614 | 0.346 | 95.9 | 0/240 |
| population_ga | 1 | 4.94263 | 0.303 | 0.333 | 1.3 | 0/240 |
| uniform_ga | 1 | 4.94501 | 0.335 | 0.375 | 65.8 | 0/240 |
| memory_ga | 1 | 4.94501 | 0.348 | 0.375 | 65.8 | 0/240 |
| analytical_ga | 1 | 4.94501 | 0.329 | 0.375 | 65.8 | 0/240 |
| analytical_no_memory_ga | 1 | 4.94501 | 0.295 | 0.375 | 65.0 | 0/240 |
| mlp_ga | 1 | 4.94501 | 0.632 | 0.375 | 65.8 | 0/240 |
| attention_ga | 1 | 4.94501 | 0.848 | 0.375 | 65.8 | 0/240 |
| attention_no_memory_ga | 1 | 4.94501 | 0.814 | 0.375 | 65.0 | 0/240 |
| attention_no_physics_ga | 1 | 4.94501 | 0.860 | 0.375 | 65.8 | 0/240 |
| greedy | 5 | 4.97315 | 4.359 | 1.000 | 8564.1 | 0/240 |
| pair | 5 | 4.97330 | 4.042 | 1.000 | 11877.9 | 0/240 |
| random | 5 | 4.95577 | 4.382 | 0.429 | 1124.7 | 0/240 |
| population_ga | 5 | 4.95420 | 4.344 | 0.421 | 64.6 | 0/240 |
| uniform_ga | 5 | 4.97311 | 3.604 | 1.000 | 3275.2 | 0/240 |
| memory_ga | 5 | 4.97326 | 3.601 | 1.000 | 3390.1 | 0/240 |
| analytical_ga | 5 | 4.97326 | 3.588 | 1.000 | 3364.5 | 0/240 |
| analytical_no_memory_ga | 5 | 4.97326 | 3.546 | 1.000 | 3377.8 | 0/240 |
| mlp_ga | 5 | 4.97327 | 3.714 | 1.000 | 3308.4 | 0/240 |
| attention_ga | 5 | 4.97326 | 3.824 | 1.000 | 3200.7 | 0/240 |
| attention_no_memory_ga | 5 | 4.97326 | 3.782 | 1.000 | 3220.8 | 0/240 |
| attention_no_physics_ga | 5 | 4.97326 | 3.845 | 1.000 | 3173.1 | 0/240 |
| greedy | 10 | 4.97321 | 9.149 | 1.000 | 18725.5 | 0/240 |
| pair | 10 | 4.97330 | 8.794 | 1.000 | 27796.8 | 1/240 |
| random | 10 | 4.95681 | 9.176 | 0.463 | 2456.3 | 0/240 |
| population_ga | 10 | 4.95937 | 9.346 | 0.592 | 135.4 | 0/240 |
| uniform_ga | 10 | 4.97314 | 4.523 | 1.000 | 3581.5 | 0/240 |
| memory_ga | 10 | 4.97327 | 4.377 | 1.000 | 3639.8 | 0/240 |
| analytical_ga | 10 | 4.97327 | 4.409 | 1.000 | 3639.8 | 0/240 |
| analytical_no_memory_ga | 10 | 4.97327 | 4.378 | 1.000 | 3638.7 | 0/240 |
| mlp_ga | 10 | 4.97327 | 4.686 | 1.000 | 3604.5 | 0/240 |
| attention_ga | 10 | 4.97327 | 4.729 | 1.000 | 3545.8 | 0/240 |
| attention_no_memory_ga | 10 | 4.97327 | 4.720 | 1.000 | 3552.5 | 0/240 |
| attention_no_physics_ga | 10 | 4.97327 | 4.793 | 1.000 | 3560.7 | 0/240 |
| greedy | 50 | 4.97328 | 48.838 | 1.000 | 103610.7 | 0/240 |
| pair | 50 | 4.97331 | 48.513 | 1.000 | 162870.9 | 0/240 |
| random | 50 | 4.95869 | 48.862 | 0.529 | 13510.8 | 0/240 |
| population_ga | 50 | 4.97082 | 49.346 | 0.979 | 711.1 | 0/240 |
| uniform_ga | 50 | 4.97314 | 4.704 | 1.000 | 3636.2 | 0/240 |
| memory_ga | 50 | 4.97327 | 4.989 | 1.000 | 3807.0 | 0/240 |
| analytical_ga | 50 | 4.97327 | 4.977 | 1.000 | 3807.0 | 0/240 |
| analytical_no_memory_ga | 50 | 4.97327 | 4.931 | 1.000 | 3805.7 | 0/240 |
| mlp_ga | 50 | 4.97327 | 5.379 | 1.000 | 3807.0 | 0/240 |
| attention_ga | 50 | 4.97327 | 5.594 | 1.000 | 3807.0 | 0/240 |
| attention_no_memory_ga | 50 | 4.97327 | 5.704 | 1.000 | 3805.7 | 0/240 |
| attention_no_physics_ga | 50 | 4.97327 | 5.684 | 1.000 | 3807.0 | 0/240 |
| greedy | 100 | 4.97329 | 98.838 | 1.000 | 205120.2 | 0/240 |
| pair | 100 | 4.97331 | 98.502 | 1.000 | 324883.4 | 0/240 |
| random | 100 | 4.95954 | 98.860 | 0.588 | 27031.9 | 0/240 |
| population_ga | 100 | 4.97254 | 99.354 | 1.000 | 1405.5 | 0/240 |
| uniform_ga | 100 | 4.97314 | 4.774 | 1.000 | 3636.2 | 0/240 |
| memory_ga | 100 | 4.97327 | 5.904 | 1.000 | 3807.0 | 0/240 |
| analytical_ga | 100 | 4.97327 | 5.320 | 1.000 | 3807.0 | 0/240 |
| analytical_no_memory_ga | 100 | 4.97327 | 5.226 | 1.000 | 3805.7 | 0/240 |
| mlp_ga | 100 | 4.97327 | 5.911 | 1.000 | 3807.0 | 0/240 |
| attention_ga | 100 | 4.97327 | 5.762 | 1.000 | 3807.0 | 0/240 |
| attention_no_memory_ga | 100 | 4.97327 | 6.055 | 1.000 | 3805.7 | 0/240 |
| attention_no_physics_ga | 100 | 4.97327 | 5.773 | 1.000 | 3807.0 | 0/240 |
