# Matched comparison report (coupled, validation, search config large)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 48; trajectories: 3; runs: 28800. Target margin 0.015 bit/s/Hz. Protocol sha256 a033b2866c154ecf.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 14.36271 | 49.192 | 0.480 / 0.704 | 0.108 | 24028.2 | 523.3 | 0/480 |
| pair | 15.50803 | 48.969 | 0.492 / 35.732 | 0.167 | 78668.5 | 11368.2 | 0/480 |
| random | 13.85489 | 49.219 | 0.475 / 0.506 | 0.104 | 286.2 | 1.0 | 0/480 |
| population_ga | 13.89523 | 49.336 | 0.479 / 0.694 | 0.104 | 317.5 | 1.0 | 0/480 |
| uniform_ga | 14.77658 | 9.709 | 0.479 / 3.040 | 0.119 | 4290.6 | 294.3 | 0/480 |
| memory_ga | 15.18499 | 12.373 | 0.482 / 6.114 | 0.125 | 4888.0 | 516.7 | 0/480 |
| analytical_ga | 15.16387 | 12.150 | 0.481 / 6.116 | 0.125 | 4828.5 | 516.7 | 0/480 |
| analytical_no_memory_ga | 14.82315 | 7.358 | 0.479 / 6.066 | 0.125 | 3308.2 | 516.7 | 0/480 |
| mlp_ga | 15.13896 | 12.529 | 0.480 / 6.247 | 0.125 | 4769.8 | 516.7 | 0/480 |
| attention_ga | 15.11327 | 13.776 | 0.480 / 6.458 | 0.125 | 4793.9 | 516.7 | 0/480 |
| attention_no_memory_ga | 14.82218 | 9.589 | 0.479 / 6.600 | 0.125 | 3300.2 | 516.7 | 0/480 |
| attention_no_physics_ga | 15.09919 | 13.716 | 0.479 / 6.595 | 0.125 | 4768.2 | 516.7 | 0/480 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | -0.07172 | [-0.13959, 0.00000] | 0.0022 | inconclusive |
| mlp_ga - memory_ga | -0.04603 | [-0.07602, 0.00000] | 0.0022 | inconclusive |
| analytical_ga - memory_ga | -0.02112 | [-0.07557, 0.01221] | 1.0000 | inconclusive |
| attention_ga - analytical_ga | -0.05060 | [-0.15180, 0.00000] | 1.0000 | inconclusive |
| memory_ga - pair | -0.32305 | [-0.62346, -0.02622] | 0.0022 | deteriorated |
| attention_ga - attention_no_memory_ga | 0.29109 | [0.19108, 0.34269] | 0.0022 | numerically_unresolved |
| analytical_ga - analytical_no_memory_ga | 0.34072 | [0.27780, 0.45387] | 0.0022 | numerically_unresolved |
| analytical_ga - uniform_ga | 0.38729 | [0.28023, 0.50073] | 0.0022 | numerically_unresolved |
| attention_ga - mlp_ga | -0.02569 | [-0.07752, 0.00045] | 1.0000 | inconclusive |
| attention_ga - attention_no_physics_ga | 0.01408 | [0.00000, 0.04180] | 0.2832 | inconclusive |
| population_ga - analytical_ga | -1.26864 | [-1.94816, -0.48385] | 0.0022 | deteriorated |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 13.85489 | 0.583 | 0.104 | 1.0 | 1/480 |
| pair | 1 | 13.85489 | 0.540 | 0.104 | 1.0 | 1/480 |
| random | 1 | 13.85489 | 0.543 | 0.104 | 1.0 | 0/480 |
| population_ga | 1 | 13.85489 | 0.590 | 0.104 | 1.0 | 1/480 |
| uniform_ga | 1 | 13.85489 | 0.637 | 0.104 | 64.7 | 2/480 |
| memory_ga | 1 | 13.85489 | 0.658 | 0.104 | 64.7 | 1/480 |
| analytical_ga | 1 | 13.85489 | 0.670 | 0.104 | 64.9 | 1/480 |
| analytical_no_memory_ga | 1 | 13.85489 | 0.646 | 0.104 | 65.0 | 0/480 |
| mlp_ga | 1 | 13.85489 | 0.803 | 0.104 | 64.9 | 7/480 |
| attention_ga | 1 | 13.85489 | 0.636 | 0.104 | 64.7 | 0/480 |
| attention_no_memory_ga | 1 | 13.85489 | 0.633 | 0.104 | 64.9 | 1/480 |
| attention_no_physics_ga | 1 | 13.85489 | 0.644 | 0.104 | 64.9 | 1/480 |
| greedy | 5 | 13.91515 | 4.187 | 0.104 | 1727.8 | 0/480 |
| pair | 5 | 14.98079 | 4.027 | 0.125 | 5079.0 | 0/480 |
| random | 5 | 13.85489 | 4.216 | 0.104 | 22.6 | 0/480 |
| population_ga | 5 | 13.85489 | 4.323 | 0.104 | 24.1 | 0/480 |
| uniform_ga | 5 | 14.63126 | 4.816 | 0.108 | 2481.8 | 1/480 |
| memory_ga | 5 | 15.06882 | 4.893 | 0.125 | 2920.1 | 1/480 |
| analytical_ga | 5 | 15.06558 | 4.873 | 0.125 | 2926.5 | 0/480 |
| analytical_no_memory_ga | 5 | 14.77831 | 4.506 | 0.125 | 2318.4 | 0/480 |
| mlp_ga | 5 | 15.01481 | 4.923 | 0.125 | 2529.0 | 0/480 |
| attention_ga | 5 | 15.01983 | 4.963 | 0.125 | 2225.8 | 9/480 |
| attention_no_memory_ga | 5 | 14.79002 | 4.879 | 0.125 | 1984.6 | 0/480 |
| attention_no_physics_ga | 5 | 15.00628 | 4.921 | 0.125 | 2187.2 | 8/480 |
| greedy | 10 | 13.99254 | 9.210 | 0.104 | 4056.4 | 0/480 |
| pair | 10 | 15.06213 | 8.977 | 0.129 | 12721.1 | 0/480 |
| random | 10 | 13.85489 | 9.242 | 0.104 | 49.8 | 0/480 |
| population_ga | 10 | 13.85879 | 9.342 | 0.104 | 54.5 | 0/480 |
| uniform_ga | 10 | 14.76052 | 9.548 | 0.119 | 4022.3 | 0/480 |
| memory_ga | 10 | 15.15037 | 9.729 | 0.125 | 4397.3 | 2/480 |
| analytical_ga | 10 | 15.10322 | 9.820 | 0.125 | 4373.6 | 0/480 |
| analytical_no_memory_ga | 10 | 14.82315 | 7.799 | 0.125 | 3298.3 | 0/480 |
| mlp_ga | 10 | 15.06944 | 9.870 | 0.125 | 4268.4 | 5/480 |
| attention_ga | 10 | 15.05741 | 9.905 | 0.125 | 4178.7 | 7/480 |
| attention_no_memory_ga | 10 | 14.82218 | 9.707 | 0.125 | 3260.0 | 2/480 |
| attention_no_physics_ga | 10 | 15.05404 | 9.911 | 0.125 | 4151.9 | 1/480 |
| greedy | 50 | 14.36271 | 49.192 | 0.108 | 24028.2 | 0/480 |
| pair | 50 | 15.50803 | 48.969 | 0.167 | 78668.5 | 0/480 |
| random | 50 | 13.85489 | 49.219 | 0.104 | 286.2 | 0/480 |
| population_ga | 50 | 13.89523 | 49.336 | 0.104 | 317.5 | 0/480 |
| uniform_ga | 50 | 14.77658 | 9.709 | 0.119 | 4290.6 | 0/480 |
| memory_ga | 50 | 15.18499 | 12.373 | 0.125 | 4888.0 | 0/480 |
| analytical_ga | 50 | 15.16387 | 12.150 | 0.125 | 4828.5 | 0/480 |
| analytical_no_memory_ga | 50 | 14.82315 | 7.358 | 0.125 | 3308.2 | 0/480 |
| mlp_ga | 50 | 15.13896 | 12.529 | 0.125 | 4769.8 | 0/480 |
| attention_ga | 50 | 15.11327 | 13.776 | 0.125 | 4793.9 | 0/480 |
| attention_no_memory_ga | 50 | 14.82218 | 9.589 | 0.125 | 3300.2 | 0/480 |
| attention_no_physics_ga | 50 | 15.09919 | 13.716 | 0.125 | 4768.2 | 0/480 |
| greedy | 100 | 14.55679 | 99.221 | 0.110 | 47861.3 | 0/480 |
| pair | 100 | 15.83386 | 98.966 | 0.215 | 158620.6 | 0/480 |
| random | 100 | 13.85489 | 99.222 | 0.104 | 571.8 | 0/480 |
| population_ga | 100 | 13.94337 | 99.333 | 0.104 | 632.8 | 0/480 |
| uniform_ga | 100 | 14.77658 | 10.748 | 0.119 | 4290.6 | 0/480 |
| memory_ga | 100 | 15.18499 | 12.615 | 0.125 | 4888.0 | 0/480 |
| analytical_ga | 100 | 15.16387 | 12.348 | 0.125 | 4828.5 | 0/480 |
| analytical_no_memory_ga | 100 | 14.82315 | 7.577 | 0.125 | 3308.2 | 0/480 |
| mlp_ga | 100 | 15.13896 | 13.146 | 0.125 | 4769.8 | 0/480 |
| attention_ga | 100 | 15.11327 | 14.176 | 0.125 | 4793.9 | 0/480 |
| attention_no_memory_ga | 100 | 14.82218 | 9.798 | 0.125 | 3300.2 | 0/480 |
| attention_no_physics_ga | 100 | 15.09919 | 14.468 | 0.125 | 4768.2 | 0/480 |
