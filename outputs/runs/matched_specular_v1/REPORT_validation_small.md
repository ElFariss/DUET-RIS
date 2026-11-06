# Matched comparison report (specular, validation, search config small)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 24; trajectories: 6; runs: 14400. Target margin 0.015 bit/s/Hz. Protocol sha256 a033b2866c154ecf.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 4.97328 | 48.840 | 0.415 / 0.796 | 1.000 | 105177.0 | 422.3 | 0/240 |
| pair | 4.97331 | 48.498 | 0.422 / 0.795 | 1.000 | 164549.9 | 422.3 | 0/240 |
| random | 4.95872 | 48.861 | 0.225 / 26.757 | 0.529 | 13610.6 | 1061.2 | 0/240 |
| population_ga | 4.97094 | 49.345 | 6.644 / 23.981 | 0.988 | 729.3 | 118.0 | 0/240 |
| uniform_ga | 4.97313 | 3.286 | 0.421 / 0.791 | 1.000 | 3046.9 | 422.3 | 0/240 |
| memory_ga | 4.97327 | 3.563 | 0.418 / 0.813 | 1.000 | 3281.2 | 422.3 | 0/240 |
| analytical_ga | 4.97327 | 3.511 | 0.424 / 0.796 | 1.000 | 3281.2 | 422.3 | 0/240 |
| analytical_no_memory_ga | 4.97327 | 3.534 | 0.428 / 0.807 | 1.000 | 3280.0 | 422.3 | 0/240 |
| mlp_ga | 4.97327 | 3.905 | 0.420 / 0.795 | 1.000 | 3281.2 | 422.3 | 0/240 |
| attention_ga | 4.97327 | 4.736 | 0.420 / 0.798 | 1.000 | 3281.2 | 422.3 | 0/240 |
| attention_no_memory_ga | 4.97327 | 4.322 | 0.416 / 0.802 | 1.000 | 3280.0 | 422.3 | 0/240 |
| attention_no_physics_ga | 4.97327 | 4.453 | 0.422 / 0.800 | 1.000 | 3281.2 | 422.3 | 0/240 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| mlp_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| attention_ga - analytical_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| memory_ga - pair | -0.00004 | [-0.00010, -0.00000] | 0.0040 | equivalent |
| attention_ga - attention_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - analytical_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - uniform_ga | 0.00014 | [-0.00000, 0.00055] | 1.0000 | equivalent |
| attention_ga - mlp_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| attention_ga - attention_no_physics_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| population_ga - analytical_ga | -0.00233 | [-0.00396, -0.00072] | 0.0022 | equivalent |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 4.96301 | 0.586 | 0.758 | 712.2 | 0/240 |
| pair | 1 | 4.96313 | 0.586 | 0.729 | 708.7 | 0/240 |
| random | 1 | 4.95221 | 0.611 | 0.346 | 95.3 | 0/240 |
| population_ga | 1 | 4.94285 | 0.303 | 0.333 | 1.5 | 0/240 |
| uniform_ga | 1 | 4.94501 | 0.332 | 0.375 | 65.8 | 0/240 |
| memory_ga | 1 | 4.94501 | 0.348 | 0.375 | 65.8 | 0/240 |
| analytical_ga | 1 | 4.94501 | 0.327 | 0.375 | 65.8 | 0/240 |
| analytical_no_memory_ga | 1 | 4.94501 | 0.295 | 0.375 | 65.0 | 0/240 |
| mlp_ga | 1 | 4.94501 | 0.647 | 0.375 | 65.8 | 0/240 |
| attention_ga | 1 | 4.94501 | 0.866 | 0.375 | 65.8 | 0/240 |
| attention_no_memory_ga | 1 | 4.94501 | 0.830 | 0.375 | 65.0 | 0/240 |
| attention_no_physics_ga | 1 | 4.94501 | 0.877 | 0.375 | 65.8 | 1/240 |
| greedy | 5 | 4.97313 | 4.370 | 1.000 | 7655.2 | 0/240 |
| pair | 5 | 4.97330 | 4.138 | 1.000 | 10375.1 | 0/240 |
| random | 5 | 4.95565 | 4.393 | 0.429 | 997.2 | 0/240 |
| population_ga | 5 | 4.95379 | 4.374 | 0.412 | 59.2 | 0/240 |
| uniform_ga | 5 | 4.97311 | 3.152 | 1.000 | 2859.7 | 0/240 |
| memory_ga | 5 | 4.97326 | 3.716 | 1.000 | 3023.1 | 0/240 |
| analytical_ga | 5 | 4.97326 | 3.697 | 1.000 | 3023.1 | 0/240 |
| analytical_no_memory_ga | 5 | 4.97326 | 3.641 | 1.000 | 3015.8 | 0/240 |
| mlp_ga | 5 | 4.97326 | 4.119 | 1.000 | 3003.8 | 0/240 |
| attention_ga | 5 | 4.97325 | 4.459 | 1.000 | 2884.7 | 0/240 |
| attention_no_memory_ga | 5 | 4.97325 | 4.366 | 1.000 | 2860.8 | 0/240 |
| attention_no_physics_ga | 5 | 4.97325 | 4.455 | 1.000 | 2859.5 | 0/240 |
| greedy | 10 | 4.97321 | 9.160 | 1.000 | 17705.3 | 0/240 |
| pair | 10 | 4.97330 | 8.828 | 1.000 | 26230.2 | 0/240 |
| random | 10 | 4.95668 | 9.177 | 0.458 | 2291.4 | 0/240 |
| population_ga | 10 | 4.95920 | 9.351 | 0.579 | 130.8 | 0/240 |
| uniform_ga | 10 | 4.97312 | 3.517 | 1.000 | 3014.0 | 0/240 |
| memory_ga | 10 | 4.97327 | 3.794 | 1.000 | 3209.9 | 0/240 |
| analytical_ga | 10 | 4.97327 | 3.744 | 1.000 | 3201.5 | 0/240 |
| analytical_no_memory_ga | 10 | 4.97327 | 3.702 | 1.000 | 3208.6 | 0/240 |
| mlp_ga | 10 | 4.97326 | 3.989 | 1.000 | 3150.9 | 0/240 |
| attention_ga | 10 | 4.97326 | 4.210 | 1.000 | 3134.2 | 0/240 |
| attention_no_memory_ga | 10 | 4.97326 | 4.143 | 1.000 | 3128.9 | 0/240 |
| attention_no_physics_ga | 10 | 4.97326 | 4.221 | 1.000 | 3134.2 | 0/240 |
| greedy | 50 | 4.97328 | 48.840 | 1.000 | 105177.0 | 0/240 |
| pair | 50 | 4.97331 | 48.498 | 1.000 | 164549.9 | 0/240 |
| random | 50 | 4.95872 | 48.861 | 0.529 | 13610.6 | 0/240 |
| population_ga | 50 | 4.97094 | 49.345 | 0.988 | 729.3 | 0/240 |
| uniform_ga | 50 | 4.97313 | 3.286 | 1.000 | 3046.9 | 0/240 |
| memory_ga | 50 | 4.97327 | 3.563 | 1.000 | 3281.2 | 0/240 |
| analytical_ga | 50 | 4.97327 | 3.511 | 1.000 | 3281.2 | 0/240 |
| analytical_no_memory_ga | 50 | 4.97327 | 3.534 | 1.000 | 3280.0 | 0/240 |
| mlp_ga | 50 | 4.97327 | 3.905 | 1.000 | 3281.2 | 0/240 |
| attention_ga | 50 | 4.97327 | 4.736 | 1.000 | 3281.2 | 0/240 |
| attention_no_memory_ga | 50 | 4.97327 | 4.322 | 1.000 | 3280.0 | 0/240 |
| attention_no_physics_ga | 50 | 4.97327 | 4.453 | 1.000 | 3281.2 | 0/240 |
| greedy | 100 | 4.97329 | 98.840 | 1.000 | 215617.0 | 0/240 |
| pair | 100 | 4.97331 | 98.487 | 1.000 | 339538.1 | 0/240 |
| random | 100 | 4.95953 | 98.860 | 0.588 | 28018.0 | 0/240 |
| population_ga | 100 | 4.97263 | 99.349 | 1.000 | 1486.5 | 0/240 |
| uniform_ga | 100 | 4.97313 | 3.282 | 1.000 | 3046.9 | 0/240 |
| memory_ga | 100 | 4.97327 | 3.510 | 1.000 | 3281.2 | 0/240 |
| analytical_ga | 100 | 4.97327 | 3.471 | 1.000 | 3281.2 | 0/240 |
| analytical_no_memory_ga | 100 | 4.97327 | 3.410 | 1.000 | 3280.0 | 0/240 |
| mlp_ga | 100 | 4.97327 | 3.900 | 1.000 | 3281.2 | 0/240 |
| attention_ga | 100 | 4.97327 | 4.144 | 1.000 | 3281.2 | 0/240 |
| attention_no_memory_ga | 100 | 4.97327 | 4.105 | 1.000 | 3280.0 | 0/240 |
| attention_no_physics_ga | 100 | 4.97327 | 4.152 | 1.000 | 3281.2 | 0/240 |
