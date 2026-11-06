# Matched comparison report (specular, validation, search config medium)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 24; trajectories: 6; runs: 14400. Target margin 0.015 bit/s/Hz. Protocol sha256 77f880fa16c48934.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 4.97328 | 48.836 | 0.426 / 0.776 | 1.000 | 106457.3 | 422.3 | 0/240 |
| pair | 4.97331 | 48.495 | 0.418 / 0.775 | 1.000 | 166455.0 | 422.3 | 0/240 |
| random | 4.95873 | 48.860 | 0.220 / 25.464 | 0.529 | 13785.8 | 1061.2 | 0/240 |
| population_ga | 4.97094 | 49.348 | 6.660 / 23.601 | 0.988 | 722.8 | 118.0 | 0/240 |
| uniform_ga | 4.97314 | 4.624 | 0.419 / 0.769 | 1.000 | 3636.2 | 422.3 | 0/240 |
| memory_ga | 4.97327 | 4.860 | 0.423 / 0.806 | 1.000 | 3807.0 | 422.3 | 0/240 |
| analytical_ga | 4.97327 | 4.840 | 0.425 / 0.771 | 1.000 | 3807.0 | 422.3 | 0/240 |
| analytical_no_memory_ga | 4.97327 | 4.984 | 0.419 / 0.785 | 1.000 | 3805.7 | 422.3 | 0/240 |
| mlp_ga | 4.97327 | 5.263 | 0.417 / 0.766 | 1.000 | 3807.0 | 422.3 | 0/240 |
| attention_ga | 4.97327 | 5.646 | 0.418 / 0.770 | 1.000 | 3807.0 | 422.3 | 0/240 |
| attention_no_memory_ga | 4.97327 | 5.523 | 0.415 / 0.770 | 1.000 | 3805.7 | 422.3 | 0/240 |
| attention_no_physics_ga | 4.97327 | 5.632 | 0.419 / 0.789 | 1.000 | 3807.0 | 422.3 | 0/240 |

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
| population_ga - analytical_ga | -0.00234 | [-0.00400, -0.00071] | 0.0022 | equivalent |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 4.96304 | 0.587 | 0.779 | 718.7 | 1/240 |
| pair | 1 | 4.96312 | 0.588 | 0.767 | 713.0 | 1/240 |
| random | 1 | 4.95227 | 0.603 | 0.346 | 94.8 | 0/240 |
| population_ga | 1 | 4.94353 | 0.349 | 0.333 | 1.7 | 0/240 |
| uniform_ga | 1 | 4.94500 | 0.359 | 0.375 | 65.5 | 1/240 |
| memory_ga | 1 | 4.94501 | 0.368 | 0.375 | 65.8 | 0/240 |
| analytical_ga | 1 | 4.94501 | 0.347 | 0.375 | 65.8 | 0/240 |
| analytical_no_memory_ga | 1 | 4.94499 | 0.334 | 0.375 | 64.7 | 1/240 |
| mlp_ga | 1 | 4.94501 | 0.719 | 0.375 | 65.8 | 0/240 |
| attention_ga | 1 | 4.94499 | 0.876 | 0.375 | 65.5 | 5/240 |
| attention_no_memory_ga | 1 | 4.94501 | 0.975 | 0.375 | 65.0 | 11/240 |
| attention_no_physics_ga | 1 | 4.94501 | 0.870 | 0.375 | 65.8 | 1/240 |
| greedy | 5 | 4.97316 | 4.358 | 1.000 | 8904.8 | 0/240 |
| pair | 5 | 4.97330 | 4.018 | 1.000 | 12216.5 | 0/240 |
| random | 5 | 4.95582 | 4.380 | 0.433 | 1144.7 | 0/240 |
| population_ga | 5 | 4.95436 | 4.343 | 0.425 | 66.2 | 0/240 |
| uniform_ga | 5 | 4.97313 | 3.639 | 1.000 | 3318.2 | 0/240 |
| memory_ga | 5 | 4.97326 | 3.540 | 1.000 | 3423.3 | 0/240 |
| analytical_ga | 5 | 4.97326 | 3.515 | 1.000 | 3419.4 | 0/240 |
| analytical_no_memory_ga | 5 | 4.97327 | 3.620 | 1.000 | 3391.5 | 0/240 |
| mlp_ga | 5 | 4.97327 | 3.795 | 1.000 | 3403.5 | 0/240 |
| attention_ga | 5 | 4.97327 | 3.735 | 1.000 | 3266.4 | 0/240 |
| attention_no_memory_ga | 5 | 4.97327 | 3.711 | 1.000 | 3277.7 | 0/240 |
| attention_no_physics_ga | 5 | 4.97326 | 3.754 | 1.000 | 3214.7 | 0/240 |
| greedy | 10 | 4.97321 | 9.150 | 1.000 | 19393.3 | 0/240 |
| pair | 10 | 4.97330 | 8.803 | 1.000 | 28808.0 | 0/240 |
| random | 10 | 4.95685 | 9.173 | 0.463 | 2523.6 | 0/240 |
| population_ga | 10 | 4.95960 | 9.346 | 0.604 | 140.0 | 0/240 |
| uniform_ga | 10 | 4.97314 | 4.449 | 1.000 | 3558.8 | 0/240 |
| memory_ga | 10 | 4.97327 | 4.390 | 1.000 | 3654.9 | 0/240 |
| analytical_ga | 10 | 4.97327 | 4.433 | 1.000 | 3639.2 | 0/240 |
| analytical_no_memory_ga | 10 | 4.97327 | 4.347 | 1.000 | 3658.2 | 0/240 |
| mlp_ga | 10 | 4.97327 | 4.577 | 1.000 | 3590.3 | 0/240 |
| attention_ga | 10 | 4.97327 | 4.739 | 1.000 | 3567.4 | 0/240 |
| attention_no_memory_ga | 10 | 4.97327 | 4.749 | 1.000 | 3579.8 | 0/240 |
| attention_no_physics_ga | 10 | 4.97327 | 4.788 | 1.000 | 3534.1 | 0/240 |
| greedy | 50 | 4.97328 | 48.836 | 1.000 | 106457.3 | 0/240 |
| pair | 50 | 4.97331 | 48.495 | 1.000 | 166455.0 | 0/240 |
| random | 50 | 4.95873 | 48.860 | 0.529 | 13785.8 | 0/240 |
| population_ga | 50 | 4.97094 | 49.348 | 0.988 | 722.8 | 0/240 |
| uniform_ga | 50 | 4.97314 | 4.624 | 1.000 | 3636.2 | 0/240 |
| memory_ga | 50 | 4.97327 | 4.860 | 1.000 | 3807.0 | 0/240 |
| analytical_ga | 50 | 4.97327 | 4.840 | 1.000 | 3807.0 | 0/240 |
| analytical_no_memory_ga | 50 | 4.97327 | 4.984 | 1.000 | 3805.7 | 0/240 |
| mlp_ga | 50 | 4.97327 | 5.263 | 1.000 | 3807.0 | 0/240 |
| attention_ga | 50 | 4.97327 | 5.646 | 1.000 | 3807.0 | 0/240 |
| attention_no_memory_ga | 50 | 4.97327 | 5.523 | 1.000 | 3805.7 | 0/240 |
| attention_no_physics_ga | 50 | 4.97327 | 5.632 | 1.000 | 3807.0 | 0/240 |
| greedy | 100 | 4.97329 | 98.842 | 1.000 | 207238.2 | 0/240 |
| pair | 100 | 4.97331 | 98.507 | 1.000 | 326828.2 | 0/240 |
| random | 100 | 4.95948 | 98.860 | 0.588 | 26719.5 | 0/240 |
| population_ga | 100 | 4.97256 | 99.350 | 1.000 | 1415.0 | 0/240 |
| uniform_ga | 100 | 4.97314 | 4.638 | 1.000 | 3636.2 | 0/240 |
| memory_ga | 100 | 4.97327 | 5.231 | 1.000 | 3807.0 | 0/240 |
| analytical_ga | 100 | 4.97327 | 5.350 | 1.000 | 3807.0 | 0/240 |
| analytical_no_memory_ga | 100 | 4.97327 | 4.950 | 1.000 | 3805.7 | 0/240 |
| mlp_ga | 100 | 4.97327 | 5.593 | 1.000 | 3807.0 | 0/240 |
| attention_ga | 100 | 4.97327 | 6.027 | 1.000 | 3807.0 | 0/240 |
| attention_no_memory_ga | 100 | 4.97327 | 5.951 | 1.000 | 3805.7 | 0/240 |
| attention_no_physics_ga | 100 | 4.97327 | 5.885 | 1.000 | 3807.0 | 0/240 |
