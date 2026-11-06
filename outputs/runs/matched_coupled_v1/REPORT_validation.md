# Matched comparison report (coupled, validation, search config medium)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 48; trajectories: 3; runs: 28800. Target margin 0.015 bit/s/Hz. Protocol sha256 a033b2866c154ecf.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 14.36230 | 49.199 | 0.482 / 0.728 | 0.108 | 23938.3 | 523.3 | 0/480 |
| pair | 15.51489 | 48.977 | 0.493 / 36.265 | 0.167 | 78873.7 | 11543.5 | 0/480 |
| random | 13.85489 | 49.216 | 0.483 / 0.680 | 0.104 | 288.1 | 1.0 | 0/480 |
| population_ga | 13.89192 | 49.335 | 0.483 / 0.669 | 0.104 | 317.3 | 1.0 | 0/480 |
| uniform_ga | 14.63893 | 10.449 | 0.480 / 0.943 | 0.110 | 3966.0 | 199.5 | 0/480 |
| memory_ga | 15.04044 | 11.690 | 0.483 / 5.880 | 0.125 | 4381.9 | 450.3 | 0/480 |
| analytical_ga | 15.01472 | 11.562 | 0.482 / 5.859 | 0.125 | 4387.8 | 450.3 | 0/480 |
| analytical_no_memory_ga | 14.62675 | 7.222 | 0.483 / 5.874 | 0.125 | 2794.6 | 450.3 | 0/480 |
| mlp_ga | 15.01729 | 13.059 | 0.481 / 6.234 | 0.125 | 4302.3 | 450.3 | 0/480 |
| attention_ga | 15.01126 | 13.659 | 0.483 / 6.429 | 0.125 | 4329.2 | 450.3 | 0/480 |
| attention_no_memory_ga | 14.65200 | 8.778 | 0.481 / 6.419 | 0.125 | 2759.9 | 450.3 | 0/480 |
| attention_no_physics_ga | 14.96292 | 13.635 | 0.484 / 6.420 | 0.125 | 4286.1 | 450.3 | 0/480 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | -0.02918 | [-0.12913, 0.04160] | 1.0000 | inconclusive |
| mlp_ga - memory_ga | -0.02315 | [-0.11367, 0.04422] | 1.0000 | inconclusive |
| analytical_ga - memory_ga | -0.02571 | [-0.08328, 0.00613] | 1.0000 | inconclusive |
| attention_ga - analytical_ga | -0.00346 | [-0.13527, 0.12487] | 1.0000 | inconclusive |
| memory_ga - pair | -0.47445 | [-0.74576, -0.03572] | 0.0022 | deteriorated |
| attention_ga - attention_no_memory_ga | 0.35926 | [0.31677, 0.40486] | 0.0022 | numerically_unresolved |
| analytical_ga - analytical_no_memory_ga | 0.38797 | [0.27288, 0.54174] | 0.0022 | numerically_unresolved |
| analytical_ga - uniform_ga | 0.37579 | [0.25966, 0.48960] | 0.0022 | numerically_unresolved |
| attention_ga - mlp_ga | -0.00603 | [-0.01546, 0.00000] | 0.4248 | inconclusive |
| attention_ga - attention_no_physics_ga | 0.04834 | [0.00000, 0.12862] | 0.4248 | inconclusive |
| population_ga - analytical_ga | -1.12280 | [-1.62627, -0.48385] | 0.0022 | deteriorated |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 13.85489 | 0.733 | 0.104 | 1.0 | 1/480 |
| pair | 1 | 13.85489 | 0.734 | 0.104 | 1.0 | 0/480 |
| random | 1 | 13.85489 | 0.732 | 0.104 | 1.0 | 0/480 |
| population_ga | 1 | 13.85489 | 0.844 | 0.104 | 1.0 | 0/480 |
| uniform_ga | 1 | 13.85489 | 0.847 | 0.104 | 64.7 | 1/480 |
| memory_ga | 1 | 13.85489 | 0.842 | 0.104 | 64.9 | 0/480 |
| analytical_ga | 1 | 13.85489 | 0.849 | 0.104 | 64.9 | 1/480 |
| analytical_no_memory_ga | 1 | 13.85489 | 0.834 | 0.104 | 65.0 | 0/480 |
| mlp_ga | 1 | 13.85489 | 0.849 | 0.104 | 64.9 | 1/480 |
| attention_ga | 1 | 13.85489 | 0.851 | 0.104 | 65.0 | 0/480 |
| attention_no_memory_ga | 1 | 13.85489 | 0.842 | 0.104 | 64.9 | 0/480 |
| attention_no_physics_ga | 1 | 13.85489 | 0.853 | 0.104 | 65.0 | 0/480 |
| greedy | 5 | 13.91515 | 4.181 | 0.104 | 1716.7 | 0/480 |
| pair | 5 | 14.97428 | 4.032 | 0.125 | 5064.9 | 0/480 |
| random | 5 | 13.85489 | 4.217 | 0.104 | 22.2 | 0/480 |
| population_ga | 5 | 13.85489 | 4.332 | 0.104 | 23.9 | 0/480 |
| uniform_ga | 5 | 14.41743 | 4.888 | 0.104 | 2560.9 | 0/480 |
| memory_ga | 5 | 14.91310 | 4.876 | 0.115 | 2564.1 | 1/480 |
| analytical_ga | 5 | 14.87269 | 4.911 | 0.110 | 2682.0 | 1/480 |
| analytical_no_memory_ga | 5 | 14.56579 | 4.828 | 0.110 | 2238.2 | 1/480 |
| mlp_ga | 5 | 14.94621 | 4.919 | 0.125 | 2118.9 | 1/480 |
| attention_ga | 5 | 14.90451 | 4.932 | 0.125 | 1868.5 | 4/480 |
| attention_no_memory_ga | 5 | 14.58644 | 4.844 | 0.125 | 1433.3 | 2/480 |
| attention_no_physics_ga | 5 | 14.87901 | 4.936 | 0.125 | 1864.1 | 3/480 |
| greedy | 10 | 13.99455 | 9.181 | 0.104 | 4216.0 | 0/480 |
| pair | 10 | 15.07104 | 8.978 | 0.129 | 13250.5 | 0/480 |
| random | 10 | 13.85489 | 9.216 | 0.104 | 52.1 | 0/480 |
| population_ga | 10 | 13.86002 | 9.339 | 0.104 | 56.7 | 0/480 |
| uniform_ga | 10 | 14.62196 | 9.390 | 0.110 | 3728.2 | 1/480 |
| memory_ga | 10 | 14.98335 | 9.618 | 0.125 | 4072.4 | 0/480 |
| analytical_ga | 10 | 14.95330 | 9.613 | 0.125 | 4056.8 | 0/480 |
| analytical_no_memory_ga | 10 | 14.62675 | 7.007 | 0.125 | 2787.3 | 0/480 |
| mlp_ga | 10 | 14.98855 | 9.799 | 0.125 | 3856.2 | 2/480 |
| attention_ga | 10 | 14.94460 | 9.873 | 0.125 | 3850.7 | 2/480 |
| attention_no_memory_ga | 10 | 14.65200 | 8.530 | 0.125 | 2746.6 | 0/480 |
| attention_no_physics_ga | 10 | 14.91645 | 9.855 | 0.125 | 3832.5 | 1/480 |
| greedy | 50 | 14.36230 | 49.199 | 0.108 | 23938.3 | 0/480 |
| pair | 50 | 15.51489 | 48.977 | 0.167 | 78873.7 | 0/480 |
| random | 50 | 13.85489 | 49.216 | 0.104 | 288.1 | 0/480 |
| population_ga | 50 | 13.89192 | 49.335 | 0.104 | 317.3 | 0/480 |
| uniform_ga | 50 | 14.63893 | 10.449 | 0.110 | 3966.0 | 0/480 |
| memory_ga | 50 | 15.04044 | 11.690 | 0.125 | 4381.9 | 0/480 |
| analytical_ga | 50 | 15.01472 | 11.562 | 0.125 | 4387.8 | 0/480 |
| analytical_no_memory_ga | 50 | 14.62675 | 7.222 | 0.125 | 2794.6 | 0/480 |
| mlp_ga | 50 | 15.01729 | 13.059 | 0.125 | 4302.3 | 0/480 |
| attention_ga | 50 | 15.01126 | 13.659 | 0.125 | 4329.2 | 0/480 |
| attention_no_memory_ga | 50 | 14.65200 | 8.778 | 0.125 | 2759.9 | 0/480 |
| attention_no_physics_ga | 50 | 14.96292 | 13.635 | 0.125 | 4286.1 | 0/480 |
| greedy | 100 | 14.57429 | 99.198 | 0.113 | 48816.3 | 0/480 |
| pair | 100 | 15.84394 | 98.966 | 0.215 | 160842.7 | 0/480 |
| random | 100 | 13.85489 | 99.217 | 0.104 | 585.5 | 0/480 |
| population_ga | 100 | 13.96238 | 99.326 | 0.104 | 645.7 | 0/480 |
| uniform_ga | 100 | 14.63893 | 10.402 | 0.110 | 3966.0 | 0/480 |
| memory_ga | 100 | 15.04044 | 11.182 | 0.125 | 4381.9 | 0/480 |
| analytical_ga | 100 | 15.01472 | 11.130 | 0.125 | 4387.8 | 0/480 |
| analytical_no_memory_ga | 100 | 14.62675 | 7.144 | 0.125 | 2794.6 | 0/480 |
| mlp_ga | 100 | 15.01729 | 12.504 | 0.125 | 4302.3 | 0/480 |
| attention_ga | 100 | 15.01126 | 13.195 | 0.125 | 4329.2 | 0/480 |
| attention_no_memory_ga | 100 | 14.65200 | 8.752 | 0.125 | 2759.9 | 0/480 |
| attention_no_physics_ga | 100 | 14.96292 | 13.137 | 0.125 | 4286.1 | 0/480 |
