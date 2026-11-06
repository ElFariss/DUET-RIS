# Matched comparison report (coupled, validation, search config medium)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 48; trajectories: 3; runs: 28800. Target margin 0.015 bit/s/Hz. Protocol sha256 77f880fa16c48934.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 14.34966 | 49.202 | 0.477 / 0.673 | 0.106 | 23945.8 | 147.9 | 0/480 |
| pair | 15.51462 | 48.980 | 0.482 / 39.834 | 0.167 | 78308.1 | 11401.1 | 0/480 |
| random | 13.85489 | 49.220 | 0.475 / 0.677 | 0.104 | 284.4 | 1.0 | 0/480 |
| population_ga | 13.89523 | 49.337 | 0.478 / 0.658 | 0.104 | 315.8 | 1.0 | 0/480 |
| uniform_ga | 14.63893 | 10.546 | 0.476 / 0.886 | 0.110 | 3966.0 | 199.5 | 0/480 |
| memory_ga | 15.04044 | 12.034 | 0.479 / 6.012 | 0.125 | 4381.9 | 450.3 | 0/480 |
| analytical_ga | 15.01472 | 11.423 | 0.477 / 6.024 | 0.125 | 4387.8 | 450.3 | 0/480 |
| analytical_no_memory_ga | 14.62675 | 7.683 | 0.478 / 5.852 | 0.125 | 2794.6 | 450.3 | 0/480 |
| mlp_ga | 15.01729 | 12.859 | 0.477 / 6.381 | 0.125 | 4302.3 | 450.3 | 0/480 |
| attention_ga | 15.01126 | 13.675 | 0.477 / 6.627 | 0.125 | 4329.2 | 450.3 | 0/480 |
| attention_no_memory_ga | 14.65200 | 9.496 | 0.476 / 6.932 | 0.125 | 2759.9 | 450.3 | 0/480 |
| attention_no_physics_ga | 14.96292 | 13.955 | 0.477 / 6.645 | 0.125 | 4286.1 | 450.3 | 0/480 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | -0.02918 | [-0.12913, 0.04160] | 1.0000 | inconclusive |
| mlp_ga - memory_ga | -0.02315 | [-0.11367, 0.04422] | 1.0000 | inconclusive |
| analytical_ga - memory_ga | -0.02571 | [-0.08328, 0.00613] | 1.0000 | inconclusive |
| attention_ga - analytical_ga | -0.00346 | [-0.13527, 0.12487] | 1.0000 | inconclusive |
| memory_ga - pair | -0.47418 | [-0.74811, -0.04191] | 0.0022 | deteriorated |
| attention_ga - attention_no_memory_ga | 0.35926 | [0.31677, 0.40486] | 0.0022 | numerically_unresolved |
| analytical_ga - analytical_no_memory_ga | 0.38797 | [0.27288, 0.54174] | 0.0022 | numerically_unresolved |
| analytical_ga - uniform_ga | 0.37579 | [0.25966, 0.48960] | 0.0022 | numerically_unresolved |
| attention_ga - mlp_ga | -0.00603 | [-0.01546, 0.00000] | 0.4248 | inconclusive |
| attention_ga - attention_no_physics_ga | 0.04834 | [0.00000, 0.12862] | 0.4248 | inconclusive |
| population_ga - analytical_ga | -1.11949 | [-1.62627, -0.48385] | 0.0022 | deteriorated |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 13.85489 | 0.547 | 0.104 | 1.0 | 0/480 |
| pair | 1 | 13.85489 | 0.697 | 0.104 | 1.0 | 0/480 |
| random | 1 | 13.85489 | 0.564 | 0.104 | 1.0 | 1/480 |
| population_ga | 1 | 13.85489 | 0.636 | 0.104 | 1.0 | 2/480 |
| uniform_ga | 1 | 13.85489 | 0.636 | 0.104 | 64.6 | 1/480 |
| memory_ga | 1 | 13.85489 | 0.804 | 0.104 | 64.6 | 1/480 |
| analytical_ga | 1 | 13.85489 | 0.784 | 0.104 | 64.9 | 1/480 |
| analytical_no_memory_ga | 1 | 13.85489 | 0.701 | 0.104 | 65.0 | 0/480 |
| mlp_ga | 1 | 13.85489 | 0.878 | 0.104 | 65.0 | 9/480 |
| attention_ga | 1 | 13.85489 | 0.657 | 0.104 | 64.7 | 0/480 |
| attention_no_memory_ga | 1 | 13.85489 | 0.649 | 0.104 | 64.9 | 0/480 |
| attention_no_physics_ga | 1 | 13.85489 | 0.647 | 0.104 | 64.7 | 1/480 |
| greedy | 5 | 13.91386 | 4.190 | 0.104 | 1696.6 | 0/480 |
| pair | 5 | 14.97701 | 4.023 | 0.125 | 5010.3 | 1/480 |
| random | 5 | 13.85489 | 4.219 | 0.104 | 22.0 | 0/480 |
| population_ga | 5 | 13.85489 | 4.327 | 0.104 | 23.6 | 0/480 |
| uniform_ga | 5 | 14.44404 | 4.911 | 0.104 | 2538.2 | 2/480 |
| memory_ga | 5 | 14.90159 | 4.883 | 0.113 | 2571.0 | 1/480 |
| analytical_ga | 5 | 14.86641 | 4.904 | 0.113 | 2688.7 | 1/480 |
| analytical_no_memory_ga | 5 | 14.59581 | 4.834 | 0.115 | 2272.7 | 0/480 |
| mlp_ga | 5 | 14.94695 | 4.923 | 0.125 | 2087.0 | 3/480 |
| attention_ga | 5 | 14.89744 | 4.935 | 0.125 | 1840.7 | 4/480 |
| attention_no_memory_ga | 5 | 14.58341 | 4.877 | 0.125 | 1426.9 | 1/480 |
| attention_no_physics_ga | 5 | 14.87344 | 4.933 | 0.125 | 1838.4 | 1/480 |
| greedy | 10 | 13.98897 | 9.204 | 0.104 | 4206.4 | 0/480 |
| pair | 10 | 15.06838 | 8.988 | 0.129 | 13248.7 | 0/480 |
| random | 10 | 13.85489 | 9.216 | 0.104 | 51.5 | 0/480 |
| population_ga | 10 | 13.86002 | 9.333 | 0.104 | 56.6 | 0/480 |
| uniform_ga | 10 | 14.62069 | 9.453 | 0.110 | 3721.0 | 0/480 |
| memory_ga | 10 | 14.97542 | 9.731 | 0.125 | 4048.7 | 1/480 |
| analytical_ga | 10 | 14.94862 | 9.722 | 0.125 | 4043.6 | 0/480 |
| analytical_no_memory_ga | 10 | 14.62675 | 7.103 | 0.125 | 2787.7 | 0/480 |
| mlp_ga | 10 | 14.98062 | 9.850 | 0.125 | 3831.3 | 1/480 |
| attention_ga | 10 | 14.94373 | 9.895 | 0.125 | 3834.2 | 0/480 |
| attention_no_memory_ga | 10 | 14.65200 | 8.569 | 0.125 | 2740.6 | 0/480 |
| attention_no_physics_ga | 10 | 14.91645 | 9.876 | 0.125 | 3808.2 | 1/480 |
| greedy | 50 | 14.34966 | 49.202 | 0.106 | 23945.8 | 0/480 |
| pair | 50 | 15.51462 | 48.980 | 0.167 | 78308.1 | 0/480 |
| random | 50 | 13.85489 | 49.220 | 0.104 | 284.4 | 0/480 |
| population_ga | 50 | 13.89523 | 49.337 | 0.104 | 315.8 | 0/480 |
| uniform_ga | 50 | 14.63893 | 10.546 | 0.110 | 3966.0 | 0/480 |
| memory_ga | 50 | 15.04044 | 12.034 | 0.125 | 4381.9 | 0/480 |
| analytical_ga | 50 | 15.01472 | 11.423 | 0.125 | 4387.8 | 0/480 |
| analytical_no_memory_ga | 50 | 14.62675 | 7.683 | 0.125 | 2794.6 | 0/480 |
| mlp_ga | 50 | 15.01729 | 12.859 | 0.125 | 4302.3 | 0/480 |
| attention_ga | 50 | 15.01126 | 13.675 | 0.125 | 4329.2 | 0/480 |
| attention_no_memory_ga | 50 | 14.65200 | 9.496 | 0.125 | 2759.9 | 0/480 |
| attention_no_physics_ga | 50 | 14.96292 | 13.955 | 0.125 | 4286.1 | 0/480 |
| greedy | 100 | 14.56051 | 99.210 | 0.110 | 49128.9 | 0/480 |
| pair | 100 | 15.85092 | 98.974 | 0.215 | 162154.8 | 0/480 |
| random | 100 | 13.85489 | 99.216 | 0.104 | 585.5 | 0/480 |
| population_ga | 100 | 13.96150 | 99.327 | 0.104 | 650.4 | 0/480 |
| uniform_ga | 100 | 14.63893 | 10.198 | 0.110 | 3966.0 | 0/480 |
| memory_ga | 100 | 15.04044 | 11.346 | 0.125 | 4381.9 | 0/480 |
| analytical_ga | 100 | 15.01472 | 11.127 | 0.125 | 4387.8 | 0/480 |
| analytical_no_memory_ga | 100 | 14.62675 | 7.116 | 0.125 | 2794.6 | 0/480 |
| mlp_ga | 100 | 15.01729 | 12.384 | 0.125 | 4302.3 | 0/480 |
| attention_ga | 100 | 15.01126 | 13.167 | 0.125 | 4329.2 | 0/480 |
| attention_no_memory_ga | 100 | 14.65200 | 8.901 | 0.125 | 2759.9 | 0/480 |
| attention_no_physics_ga | 100 | 14.96292 | 13.250 | 0.125 | 4286.1 | 0/480 |
