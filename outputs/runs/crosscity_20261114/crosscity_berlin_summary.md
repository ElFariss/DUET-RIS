# berlin v3x test

## Primary metrics (M1 bit/s/Hz, M2 search_elapsed_ms mean/p95, M3 budget + evaluations)

| Array | Budget ms | Method | M1 | M2 mean | M2 p95 | M3 evals mean | Miss % | Excl. |
|---:|---:|---|---:|---:|---:|---:|---:|---|
| 64 | 10 | greedy | 8.1963 | 9.12 | 9.20 | 4382 | 0.00 |  |
| 64 | 10 | pair | 8.2412 | 8.91 | 9.12 | 14015 | 0.00 |  |
| 64 | 10 | me_ga | 8.0562 | 8.94 | 9.42 | 198 | 0.00 |  |
| 64 | 10 | nsga2 | 8.1112 | 9.56 | 9.65 | 156 | 0.00 |  |
| 64 | 10 | pair_plus_b35 | 8.2395 | 9.46 | 9.65 | 12555 | 0.00 |  |
| 64 | 50 | greedy | 8.2164 | 49.12 | 49.19 | 24371 | 0.00 |  |
| 64 | 50 | pair | 8.2561 | 48.88 | 49.02 | 88682 | 0.00 |  |
| 64 | 50 | me_ga | 8.1542 | 48.97 | 49.57 | 1121 | 0.00 |  |
| 64 | 50 | nsga2 | 8.2106 | 49.41 | 49.49 | 1135 | 0.00 |  |
| 64 | 50 | pair_plus_b35 | 8.2570 | 49.46 | 49.65 | 82653 | 0.00 |  |
| 128 | 10 | greedy | 7.8974 | 9.05 | 9.54 | 4783 | 0.00 |  |
| 128 | 10 | pair | 7.9099 | 8.31 | 9.70 | 12031 | 2.24 | YES |
| 128 | 10 | me_ga | 7.4205 | 2.36 | 2.31 | 10 | 0.00 |  |
| 128 | 10 | nsga2 | 7.6516 | 9.25 | 9.48 | 40 | 0.00 |  |
| 128 | 10 | pair_plus_b35 | 7.9132 | 9.55 | 9.73 | 11983 | 1.84 | YES |
| 128 | 50 | greedy | 7.9465 | 48.97 | 49.41 | 27788 | 0.00 |  |
| 128 | 50 | pair | 7.9874 | 47.03 | 48.64 | 110268 | 0.00 |  |
| 128 | 50 | me_ga | 7.6933 | 44.95 | 46.78 | 216 | 0.00 |  |
| 128 | 50 | nsga2 | 7.8005 | 49.06 | 49.19 | 228 | 0.00 |  |
| 128 | 50 | pair_plus_b35 | 7.9872 | 49.56 | 49.74 | 109565 | 0.90 | YES |

## Contrasts (99% Bonferroni intervals, family 5; 50 ms primary)

| Array | Budget | N traj | H1 b35−pair | H2 b35−ME-GA | H5 b35−NSGA-II | C6 pair−NSGA-II | C7 pair−ME-GA |
|---:|---:|---:|---|---|---|---|---|
| 64 | 10 | 36 | -0.0017 [-0.0031, -0.0007] **FAIL (below 0)** | +0.1833 [+0.0959, +0.3147] **PASS** | +0.1283 [+0.0636, +0.2427] **PASS** | +0.1300 [+0.0651, +0.2446] **PASS** | +0.1850 [+0.0968, +0.3166] **PASS** |
| 64 | 50 (primary) | 36 | +0.0009 [-0.0000, +0.0031] **FAIL** | +0.1028 [+0.0477, +0.2002] **PASS** | +0.0464 [+0.0229, +0.0897] **PASS** | +0.0456 [+0.0227, +0.0869] **PASS** | +0.1019 [+0.0475, +0.1972] **PASS** |
| 128 | 10 | 36 | +0.0032 [+0.0004, +0.0089] **FAIL (excluded by miss rule)** | +0.4927 [+0.2406, +0.8427] **FAIL (excluded by miss rule)** | +0.2616 [+0.1301, +0.4518] **FAIL (excluded by miss rule)** | +0.2583 [+0.1288, +0.4454] **FAIL (excluded by miss rule)** | +0.4894 [+0.2395, +0.8357] **FAIL (excluded by miss rule)** |
| 128 | 50 (primary) | 36 | -0.0002 [-0.0006, +0.0001] **FAIL (excluded by miss rule)** | +0.2939 [+0.1468, +0.4855] **FAIL (excluded by miss rule)** | +0.1868 [+0.0864, +0.3299] **FAIL (excluded by miss rule)** | +0.1869 [+0.0863, +0.3300] **PASS** | +0.2941 [+0.1468, +0.4856] **PASS** |

## Provenance

- 64: berlin on labkc-comm3 CPU 5 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
- 128: berlin on labkc-comm3 CPU 4 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
