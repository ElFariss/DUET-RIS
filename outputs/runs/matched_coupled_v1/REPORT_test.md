# Matched comparison report (coupled, test, search config medium)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 480; trajectories: 30; runs: 288000. Target margin 0.015 bit/s/Hz. Protocol sha256 77f880fa16c48934.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 15.52535 | 49.199 | 0.475 / 0.674 | 0.166 | 24337.0 | 189.5 | 0/4800 |
| pair | 16.23363 | 48.972 | 0.478 / 36.487 | 0.201 | 79290.9 | 7919.5 | 0/4800 |
| random | 15.26163 | 49.215 | 0.475 / 0.649 | 0.163 | 288.7 | 1.0 | 0/4800 |
| population_ga | 15.29621 | 49.332 | 0.477 / 0.655 | 0.163 | 320.2 | 1.0 | 0/4800 |
| uniform_ga | 15.55335 | 9.338 | 0.476 / 0.664 | 0.164 | 3394.2 | 25.2 | 0/4800 |
| memory_ga | 15.62635 | 10.210 | 0.475 / 0.660 | 0.164 | 3549.0 | 16.1 | 0/4800 |
| analytical_ga | 15.63728 | 10.214 | 0.476 / 0.671 | 0.165 | 3534.0 | 48.7 | 0/4800 |
| analytical_no_memory_ga | 15.55154 | 7.523 | 0.476 / 0.659 | 0.163 | 2744.2 | 4.3 | 0/4800 |
| mlp_ga | 15.66539 | 11.461 | 0.476 / 0.675 | 0.166 | 3609.5 | 68.2 | 0/4800 |
| attention_ga | 15.65760 | 12.221 | 0.475 / 0.668 | 0.166 | 3615.2 | 63.5 | 0/4800 |
| attention_no_memory_ga | 15.55997 | 9.231 | 0.476 / 0.659 | 0.164 | 2761.5 | 12.4 | 0/4800 |
| attention_no_physics_ga | 15.66065 | 12.335 | 0.476 / 0.675 | 0.166 | 3583.5 | 53.3 | 0/4800 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | 0.03125 | [-0.02339, 0.08487] | 0.5089 | inconclusive |
| mlp_ga - memory_ga | 0.03904 | [-0.01563, 0.09345] | 0.3000 | inconclusive |
| analytical_ga - memory_ga | 0.01093 | [-0.01112, 0.04741] | 0.7823 | inconclusive |
| attention_ga - analytical_ga | 0.02032 | [-0.02460, 0.06587] | 0.7823 | inconclusive |
| memory_ga - pair | -0.60728 | [-0.81612, -0.41841] | 0.0022 | deteriorated |
| attention_ga - attention_no_memory_ga | 0.09763 | [0.02737, 0.18190] | 0.0054 | numerically_unresolved |
| analytical_ga - analytical_no_memory_ga | 0.08574 | [0.02144, 0.16370] | 0.0054 | numerically_unresolved |
| analytical_ga - uniform_ga | 0.08393 | [0.02041, 0.15388] | 0.0056 | numerically_unresolved |
| attention_ga - mlp_ga | -0.00779 | [-0.03009, 0.01047] | 0.7823 | inconclusive |
| attention_ga - attention_no_physics_ga | -0.00306 | [-0.04272, 0.03067] | 0.7823 | inconclusive |
| population_ga - analytical_ga | -0.34107 | [-0.63166, -0.15565] | 0.0022 | deteriorated |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 15.26163 | 0.505 | 0.163 | 1.0 | 0/4800 |
| pair | 1 | 15.26163 | 0.507 | 0.163 | 1.0 | 0/4800 |
| random | 1 | 15.26163 | 0.506 | 0.163 | 1.0 | 3/4800 |
| population_ga | 1 | 15.26163 | 0.570 | 0.163 | 1.0 | 3/4800 |
| uniform_ga | 1 | 15.26877 | 0.666 | 0.163 | 65.1 | 2/4800 |
| memory_ga | 1 | 15.26877 | 0.714 | 0.163 | 65.1 | 2/4800 |
| analytical_ga | 1 | 15.26877 | 0.690 | 0.163 | 65.0 | 3/4800 |
| analytical_no_memory_ga | 1 | 15.26877 | 0.640 | 0.163 | 65.9 | 1/4800 |
| mlp_ga | 1 | 15.26877 | 0.726 | 0.163 | 65.1 | 66/4800 |
| attention_ga | 1 | 15.26877 | 0.666 | 0.163 | 65.0 | 5/4800 |
| attention_no_memory_ga | 1 | 15.26877 | 0.618 | 0.163 | 65.0 | 1/4800 |
| attention_no_physics_ga | 1 | 15.26877 | 0.667 | 0.163 | 65.0 | 4/4800 |
| greedy | 5 | 15.30829 | 4.209 | 0.163 | 1723.4 | 2/4800 |
| pair | 5 | 15.59947 | 4.000 | 0.163 | 3951.5 | 0/4800 |
| random | 5 | 15.26163 | 4.218 | 0.163 | 22.1 | 0/4800 |
| population_ga | 5 | 15.26183 | 4.331 | 0.163 | 23.6 | 4/4800 |
| uniform_ga | 5 | 15.46605 | 4.897 | 0.163 | 2379.0 | 8/4800 |
| memory_ga | 5 | 15.57251 | 4.870 | 0.163 | 2324.8 | 8/4800 |
| analytical_ga | 5 | 15.55010 | 4.894 | 0.163 | 2361.9 | 6/4800 |
| analytical_no_memory_ga | 5 | 15.51189 | 4.844 | 0.163 | 2190.2 | 2/4800 |
| mlp_ga | 5 | 15.58149 | 4.902 | 0.163 | 1758.1 | 21/4800 |
| attention_ga | 5 | 15.57085 | 4.923 | 0.163 | 1628.2 | 23/4800 |
| attention_no_memory_ga | 5 | 15.52540 | 4.815 | 0.163 | 1370.9 | 7/4800 |
| attention_no_physics_ga | 5 | 15.58080 | 4.926 | 0.163 | 1605.2 | 26/4800 |
| greedy | 10 | 15.35758 | 9.205 | 0.163 | 4218.7 | 1/4800 |
| pair | 10 | 15.74698 | 8.976 | 0.168 | 12652.6 | 1/4800 |
| random | 10 | 15.26163 | 9.217 | 0.163 | 51.4 | 0/4800 |
| population_ga | 10 | 15.26566 | 9.335 | 0.163 | 56.3 | 1/4800 |
| uniform_ga | 10 | 15.54412 | 8.719 | 0.164 | 3290.0 | 2/4800 |
| memory_ga | 10 | 15.61497 | 9.383 | 0.163 | 3403.3 | 3/4800 |
| analytical_ga | 10 | 15.63175 | 9.296 | 0.165 | 3401.7 | 5/4800 |
| analytical_no_memory_ga | 10 | 15.54885 | 7.503 | 0.163 | 2735.2 | 1/4800 |
| mlp_ga | 10 | 15.64995 | 9.748 | 0.166 | 3417.4 | 14/4800 |
| attention_ga | 10 | 15.63630 | 9.834 | 0.166 | 3379.3 | 19/4800 |
| attention_no_memory_ga | 10 | 15.55487 | 9.160 | 0.164 | 2740.3 | 7/4800 |
| attention_no_physics_ga | 10 | 15.64993 | 9.832 | 0.165 | 3357.8 | 18/4800 |
| greedy | 50 | 15.52535 | 49.199 | 0.166 | 24337.0 | 0/4800 |
| pair | 50 | 16.23363 | 48.972 | 0.201 | 79290.9 | 0/4800 |
| random | 50 | 15.26163 | 49.215 | 0.163 | 288.7 | 0/4800 |
| population_ga | 50 | 15.29621 | 49.332 | 0.163 | 320.2 | 0/4800 |
| uniform_ga | 50 | 15.55335 | 9.338 | 0.164 | 3394.2 | 0/4800 |
| memory_ga | 50 | 15.62635 | 10.210 | 0.164 | 3549.0 | 0/4800 |
| analytical_ga | 50 | 15.63728 | 10.214 | 0.165 | 3534.0 | 0/4800 |
| analytical_no_memory_ga | 50 | 15.55154 | 7.523 | 0.163 | 2744.2 | 0/4800 |
| mlp_ga | 50 | 15.66539 | 11.461 | 0.166 | 3609.5 | 0/4800 |
| attention_ga | 50 | 15.65760 | 12.221 | 0.166 | 3615.2 | 0/4800 |
| attention_no_memory_ga | 50 | 15.55997 | 9.231 | 0.164 | 2761.5 | 0/4800 |
| attention_no_physics_ga | 50 | 15.66065 | 12.335 | 0.166 | 3583.5 | 0/4800 |
| greedy | 100 | 15.63880 | 99.199 | 0.168 | 49281.1 | 0/4800 |
| pair | 100 | 16.50810 | 98.970 | 0.246 | 161618.3 | 0/4800 |
| random | 100 | 15.26163 | 99.217 | 0.163 | 581.8 | 1/4800 |
| population_ga | 100 | 15.31937 | 99.333 | 0.163 | 649.0 | 0/4800 |
| uniform_ga | 100 | 15.55335 | 9.345 | 0.164 | 3394.2 | 0/4800 |
| memory_ga | 100 | 15.62635 | 10.345 | 0.164 | 3549.0 | 0/4800 |
| analytical_ga | 100 | 15.63728 | 10.250 | 0.165 | 3534.0 | 0/4800 |
| analytical_no_memory_ga | 100 | 15.55154 | 7.608 | 0.163 | 2744.2 | 0/4800 |
| mlp_ga | 100 | 15.66539 | 11.539 | 0.166 | 3609.5 | 0/4800 |
| attention_ga | 100 | 15.65760 | 12.326 | 0.166 | 3615.2 | 0/4800 |
| attention_no_memory_ga | 100 | 15.55997 | 9.370 | 0.164 | 2761.5 | 0/4800 |
| attention_no_physics_ga | 100 | 15.66065 | 12.387 | 0.166 | 3583.5 | 0/4800 |
