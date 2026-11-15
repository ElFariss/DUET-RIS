# utrecht v3x test

## Primary metrics (M1 bit/s/Hz, M2 search_elapsed_ms mean/p95, M3 budget + evaluations)

| Array | Budget ms | Method | M1 | M2 mean | M2 p95 | M3 evals mean | Miss % | Excl. |
|---:|---:|---|---:|---:|---:|---:|---:|---|
| 64 | 10 | greedy | 7.2763 | 9.14 | 9.25 | 3782 | 0.00 |  |
| 64 | 10 | pair | 7.3215 | 8.75 | 9.02 | 13712 | 0.00 |  |
| 64 | 10 | me_ga | 6.9393 | 8.67 | 9.22 | 164 | 0.00 |  |
| 64 | 10 | nsga2 | 7.0932 | 9.56 | 9.65 | 131 | 0.00 |  |
| 64 | 10 | pair_plus_b35 | 7.3174 | 9.47 | 9.68 | 12250 | 0.00 |  |
| 64 | 50 | greedy | 7.3007 | 49.14 | 49.23 | 21342 | 0.00 |  |
| 64 | 50 | pair | 7.3401 | 48.71 | 48.91 | 86362 | 0.00 |  |
| 64 | 50 | me_ga | 7.1454 | 48.70 | 49.39 | 945 | 0.00 |  |
| 64 | 50 | nsga2 | 7.2432 | 49.51 | 49.62 | 947 | 0.00 |  |
| 64 | 50 | pair_plus_b35 | 7.3408 | 49.47 | 49.68 | 81052 | 0.00 |  |
| 128 | 10 | greedy | 7.5117 | 9.03 | 9.51 | 4191 | 0.42 |  |
| 128 | 10 | pair | 7.5112 | 8.68 | 9.79 | 8373 | 1.70 | YES |
| 128 | 10 | me_ga | 6.9174 | 2.63 | 2.76 | 9 | 0.00 |  |
| 128 | 10 | nsga2 | 7.1651 | 9.21 | 9.33 | 34 | 0.00 |  |
| 128 | 10 | pair_plus_b35 | 7.5169 | 9.62 | 9.83 | 8336 | 3.84 | YES |
| 128 | 50 | greedy | 7.5919 | 48.81 | 49.31 | 24704 | 0.00 |  |
| 128 | 50 | pair | 7.6456 | 46.56 | 48.72 | 85678 | 0.00 |  |
| 128 | 50 | me_ga | 7.1658 | 43.39 | 45.73 | 175 | 0.00 |  |
| 128 | 50 | nsga2 | 7.3433 | 49.00 | 49.17 | 186 | 0.00 |  |
| 128 | 50 | pair_plus_b35 | 7.6459 | 49.65 | 50.06 | 85837 | 5.90 | YES |

## Contrasts (99% Bonferroni intervals, family 5; 50 ms primary)

| Array | Budget | N traj | H1 b35−pair | H2 b35−ME-GA | H5 b35−NSGA-II | C6 pair−NSGA-II | C7 pair−ME-GA |
|---:|---:|---:|---|---|---|---|---|
| 64 | 10 | 36 | -0.0041 [-0.0071, -0.0018] **FAIL (below 0)** | +0.3781 [+0.1914, +0.6203] **PASS** | +0.2242 [+0.1103, +0.3793] **PASS** | +0.2284 [+0.1129, +0.3846] **PASS** | +0.3822 [+0.1941, +0.6251] **PASS** |
| 64 | 50 (primary) | 36 | +0.0007 [+0.0001, +0.0015] **PASS** | +0.1954 [+0.1024, +0.3060] **PASS** | +0.0977 [+0.0465, +0.1610] **PASS** | +0.0970 [+0.0459, +0.1598] **PASS** | +0.1947 [+0.1020, +0.3049] **PASS** |
| 128 | 10 | 36 | +0.0057 [-0.0023, +0.0235] **FAIL (excluded by miss rule)** | +0.5995 [+0.2823, +1.0464] **FAIL (excluded by miss rule)** | +0.3518 [+0.1667, +0.6147] **FAIL (excluded by miss rule)** | +0.3461 [+0.1611, +0.6063] **FAIL (excluded by miss rule)** | +0.5938 [+0.2749, +1.0352] **FAIL (excluded by miss rule)** |
| 128 | 50 (primary) | 36 | +0.0003 [-0.0001, +0.0013] **FAIL (excluded by miss rule)** | +0.4801 [+0.2062, +0.8402] **FAIL (excluded by miss rule)** | +0.3026 [+0.1211, +0.5599] **FAIL (excluded by miss rule)** | +0.3023 [+0.1211, +0.5596] **PASS** | +0.4798 [+0.2062, +0.8395] **PASS** |

## Provenance

- 64: utrecht on labkc-comm3 CPU 4 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
- 128: utrecht on labkc-comm3 CPU 5 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
