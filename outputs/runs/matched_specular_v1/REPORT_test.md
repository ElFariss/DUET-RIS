# Matched comparison report (specular, test, search config medium)

## Scope and limits

- Simulation only: no measured RIS, calibrated hardware or deployed controller is involved.
- memory_ga is an adaptation inspired by Zardi et al. (2024), not a reproduction of their method or results.
- Held-out trajectories are new trajectories in the same scene and on the same surface; this is not a held-out environment.
- Spatial control only; temporal forecasting is out of scope for this comparison.

Primary budget: 50 ms. Frames: 120; trajectories: 30; runs: 72000. Target margin 0.015 bit/s/Hz. Protocol sha256 77f880fa16c48934.

## Primary budget

| Method | Rate (bit/s/Hz) | p95 runtime (ms) | Time to target median / p95 (ms) | Reached | Evaluations | Evals to target | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | 5.44194 | 48.841 | 0.517 / 1.020 | 1.000 | 103022.9 | 694.3 | 0/1200 |
| pair | 5.44247 | 48.512 | 0.516 / 1.003 | 1.000 | 196913.8 | 664.2 | 0/1200 |
| random | 5.42107 | 48.862 | 0.297 / 25.180 | 0.496 | 13529.9 | 1018.2 | 0/1200 |
| population_ga | 5.43804 | 49.349 | 9.981 / 38.561 | 0.971 | 717.8 | 190.2 | 0/1200 |
| uniform_ga | 5.44202 | 5.755 | 0.522 / 0.994 | 0.999 | 6921.8 | 601.2 | 0/1200 |
| memory_ga | 5.44232 | 7.086 | 0.526 / 1.004 | 1.000 | 8068.9 | 597.7 | 0/1200 |
| analytical_ga | 5.44232 | 6.946 | 0.516 / 0.998 | 1.000 | 8082.8 | 597.7 | 0/1200 |
| analytical_no_memory_ga | 5.44232 | 7.043 | 0.510 / 0.987 | 1.000 | 8081.6 | 597.7 | 0/1200 |
| mlp_ga | 5.44233 | 7.485 | 0.513 / 1.005 | 1.000 | 8116.0 | 597.7 | 0/1200 |
| attention_ga | 5.44233 | 7.706 | 0.518 / 1.014 | 1.000 | 8112.8 | 597.7 | 0/1200 |
| attention_no_memory_ga | 5.44233 | 7.678 | 0.513 / 1.007 | 1.000 | 8111.6 | 597.7 | 0/1200 |
| attention_no_physics_ga | 5.44233 | 7.679 | 0.523 / 1.003 | 1.000 | 8111.5 | 597.7 | 0/1200 |

## Contrasts (primary budget, rate)

Paired trajectory bootstrap, 10000 resamples, seed 8251; Holm across the listed contrasts; decision margin 0.015 bit/s/Hz.

| Contrast | Difference | Bonferroni simultaneous interval | p (Holm, zero null) | Decision |
|---|---:|---|---:|---|
| attention_ga - memory_ga | 0.00001 | [-0.00000, 0.00003] | 0.3878 | equivalent |
| mlp_ga - memory_ga | 0.00001 | [-0.00000, 0.00003] | 0.8489 | equivalent |
| analytical_ga - memory_ga | -0.00000 | [-0.00000, 0.00000] | 0.9967 | equivalent |
| attention_ga - analytical_ga | 0.00001 | [0.00000, 0.00003] | 0.0224 | equivalent |
| memory_ga - pair | -0.00015 | [-0.00024, -0.00006] | 0.0022 | equivalent |
| attention_ga - attention_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - analytical_no_memory_ga | 0.00000 | [0.00000, 0.00000] | 1.0000 | equivalent |
| analytical_ga - uniform_ga | 0.00029 | [0.00013, 0.00052] | 0.0022 | equivalent |
| attention_ga - mlp_ga | 0.00000 | [0.00000, 0.00001] | 0.5291 | equivalent |
| attention_ga - attention_no_physics_ga | -0.00000 | [-0.00000, 0.00000] | 1.0000 | equivalent |
| population_ga - analytical_ga | -0.00428 | [-0.00576, -0.00305] | 0.0022 | equivalent |

Intervals are paired trajectory-bootstrap percentile intervals with Bonferroni family-wise coverage across all listed contrasts; decisions compare these intervals with the practical margin. Holm-adjusted centered-bootstrap p-values test the separate zero-difference null and are not used to construct intervals. Equivalence requires the simultaneous interval to lie wholly within both margin boundaries. Small trajectory counts and the bootstrap exchangeability assumption limit precision. A coupled improvement remains numerically unresolved unless the preselected returned-action fine-mesh audit passes.

## All budgets

| Method | Budget (ms) | Rate | p95 runtime (ms) | Reached | Evaluations | Misses |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1 | 5.42781 | 0.587 | 0.655 | 733.2 | 0/1200 |
| pair | 1 | 5.42774 | 0.586 | 0.646 | 729.5 | 0/1200 |
| random | 1 | 5.41094 | 0.605 | 0.344 | 96.2 | 0/1200 |
| population_ga | 1 | 5.39723 | 0.302 | 0.198 | 1.8 | 0/1200 |
| uniform_ga | 1 | 5.39947 | 0.326 | 0.233 | 65.8 | 0/1200 |
| memory_ga | 1 | 5.39947 | 0.343 | 0.233 | 65.7 | 1/1200 |
| analytical_ga | 1 | 5.39947 | 0.320 | 0.233 | 65.8 | 0/1200 |
| analytical_no_memory_ga | 1 | 5.39947 | 0.289 | 0.233 | 65.0 | 0/1200 |
| mlp_ga | 1 | 5.39947 | 0.625 | 0.233 | 65.8 | 0/1200 |
| attention_ga | 1 | 5.39947 | 0.839 | 0.233 | 65.8 | 3/1200 |
| attention_no_memory_ga | 1 | 5.39947 | 0.800 | 0.233 | 65.0 | 7/1200 |
| attention_no_physics_ga | 1 | 5.39947 | 0.847 | 0.233 | 65.8 | 0/1200 |
| greedy | 5 | 5.44110 | 4.361 | 0.997 | 8653.4 | 0/1200 |
| pair | 5 | 5.44219 | 4.032 | 1.000 | 14421.2 | 0/1200 |
| random | 5 | 5.41663 | 4.381 | 0.408 | 1149.6 | 0/1200 |
| population_ga | 5 | 5.41328 | 4.345 | 0.352 | 65.7 | 0/1200 |
| uniform_ga | 5 | 5.44194 | 3.793 | 0.999 | 5713.3 | 0/1200 |
| memory_ga | 5 | 5.44221 | 3.838 | 1.000 | 5920.2 | 0/1200 |
| analytical_ga | 5 | 5.44221 | 3.829 | 1.000 | 5927.3 | 0/1200 |
| analytical_no_memory_ga | 5 | 5.44220 | 3.802 | 1.000 | 5931.2 | 0/1200 |
| mlp_ga | 5 | 5.44218 | 3.917 | 1.000 | 5455.8 | 0/1200 |
| attention_ga | 5 | 5.44216 | 4.163 | 1.000 | 5174.6 | 0/1200 |
| attention_no_memory_ga | 5 | 5.44216 | 4.111 | 1.000 | 5192.2 | 0/1200 |
| attention_no_physics_ga | 5 | 5.44216 | 4.177 | 1.000 | 5174.9 | 1/1200 |
| greedy | 10 | 5.44146 | 9.157 | 0.999 | 18636.7 | 0/1200 |
| pair | 10 | 5.44236 | 8.818 | 1.000 | 33793.8 | 0/1200 |
| random | 10 | 5.41802 | 9.175 | 0.431 | 2438.7 | 0/1200 |
| population_ga | 10 | 5.42099 | 9.348 | 0.463 | 136.5 | 0/1200 |
| uniform_ga | 10 | 5.44201 | 4.942 | 0.999 | 6601.7 | 0/1200 |
| memory_ga | 10 | 5.44229 | 5.066 | 1.000 | 7196.5 | 0/1200 |
| analytical_ga | 10 | 5.44230 | 5.081 | 1.000 | 7242.5 | 0/1200 |
| analytical_no_memory_ga | 10 | 5.44230 | 5.057 | 1.000 | 7257.0 | 0/1200 |
| mlp_ga | 10 | 5.44229 | 5.074 | 1.000 | 6926.8 | 0/1200 |
| attention_ga | 10 | 5.44227 | 5.116 | 1.000 | 6692.6 | 0/1200 |
| attention_no_memory_ga | 10 | 5.44227 | 5.113 | 1.000 | 6732.3 | 0/1200 |
| attention_no_physics_ga | 10 | 5.44227 | 5.119 | 1.000 | 6668.7 | 0/1200 |
| greedy | 50 | 5.44194 | 48.841 | 1.000 | 103022.9 | 0/1200 |
| pair | 50 | 5.44247 | 48.512 | 1.000 | 196913.8 | 0/1200 |
| random | 50 | 5.42107 | 48.862 | 0.496 | 13529.9 | 0/1200 |
| population_ga | 50 | 5.43804 | 49.349 | 0.971 | 717.8 | 0/1200 |
| uniform_ga | 50 | 5.44202 | 5.755 | 0.999 | 6921.8 | 0/1200 |
| memory_ga | 50 | 5.44232 | 7.086 | 1.000 | 8068.9 | 0/1200 |
| analytical_ga | 50 | 5.44232 | 6.946 | 1.000 | 8082.8 | 0/1200 |
| analytical_no_memory_ga | 50 | 5.44232 | 7.043 | 1.000 | 8081.6 | 0/1200 |
| mlp_ga | 50 | 5.44233 | 7.485 | 1.000 | 8116.0 | 0/1200 |
| attention_ga | 50 | 5.44233 | 7.706 | 1.000 | 8112.8 | 0/1200 |
| attention_no_memory_ga | 50 | 5.44233 | 7.678 | 1.000 | 8111.6 | 0/1200 |
| attention_no_physics_ga | 50 | 5.44233 | 7.679 | 1.000 | 8111.5 | 0/1200 |
| greedy | 100 | 5.44206 | 98.842 | 1.000 | 206248.7 | 0/1200 |
| pair | 100 | 5.44248 | 98.508 | 1.000 | 400123.3 | 0/1200 |
| random | 100 | 5.42226 | 98.862 | 0.511 | 27014.0 | 0/1200 |
| population_ga | 100 | 5.44073 | 99.349 | 1.000 | 1427.4 | 0/1200 |
| uniform_ga | 100 | 5.44202 | 5.769 | 0.999 | 6921.8 | 0/1200 |
| memory_ga | 100 | 5.44232 | 6.924 | 1.000 | 8068.9 | 0/1200 |
| analytical_ga | 100 | 5.44232 | 6.872 | 1.000 | 8082.8 | 0/1200 |
| analytical_no_memory_ga | 100 | 5.44232 | 6.863 | 1.000 | 8081.6 | 0/1200 |
| mlp_ga | 100 | 5.44233 | 7.389 | 1.000 | 8116.0 | 0/1200 |
| attention_ga | 100 | 5.44233 | 7.614 | 1.000 | 8112.8 | 0/1200 |
| attention_no_memory_ga | 100 | 5.44233 | 7.615 | 1.000 | 8111.6 | 0/1200 |
| attention_no_physics_ga | 100 | 5.44233 | 7.792 | 1.000 | 8111.5 | 0/1200 |
