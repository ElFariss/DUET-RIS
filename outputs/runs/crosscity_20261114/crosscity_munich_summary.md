# munich v3x test

## Primary metrics (M1 bit/s/Hz, M2 search_elapsed_ms mean/p95, M3 budget + evaluations)

| Array | Budget ms | Method | M1 | M2 mean | M2 p95 | M3 evals mean | Miss % | Excl. |
|---:|---:|---|---:|---:|---:|---:|---:|---|
| 64 | 10 | greedy | 9.0742 | 9.12 | 9.20 | 4351 | 0.00 |  |
| 64 | 10 | pair | 9.0926 | 8.89 | 9.11 | 13805 | 0.00 |  |
| 64 | 10 | me_ga | 8.9419 | 8.92 | 9.43 | 197 | 0.00 |  |
| 64 | 10 | nsga2 | 8.9882 | 9.55 | 9.65 | 157 | 0.00 |  |
| 64 | 10 | pair_plus_b35 | 9.0913 | 9.46 | 9.65 | 12357 | 0.00 |  |
| 64 | 50 | greedy | 9.0848 | 49.12 | 49.21 | 24268 | 0.00 |  |
| 64 | 50 | pair | 9.1026 | 48.86 | 49.02 | 87082 | 0.00 |  |
| 64 | 50 | me_ga | 9.0231 | 48.99 | 49.56 | 1112 | 0.02 |  |
| 64 | 50 | nsga2 | 9.0622 | 49.41 | 49.49 | 1098 | 0.00 |  |
| 64 | 50 | pair_plus_b35 | 9.1026 | 49.45 | 49.65 | 81775 | 0.00 |  |
| 128 | 10 | greedy | 8.9547 | 9.02 | 9.42 | 4610 | 0.00 |  |
| 128 | 10 | pair | 8.9628 | 8.17 | 9.57 | 13830 | 1.35 | YES |
| 128 | 10 | me_ga | 8.4015 | 2.31 | 2.27 | 10 | 0.00 |  |
| 128 | 10 | nsga2 | 8.7501 | 9.25 | 9.45 | 39 | 0.00 |  |
| 128 | 10 | pair_plus_b35 | 8.9650 | 9.58 | 9.74 | 14051 | 1.16 | YES |
| 128 | 50 | greedy | 8.9852 | 48.98 | 49.41 | 27046 | 0.00 |  |
| 128 | 50 | pair | 9.0287 | 47.09 | 48.71 | 112400 | 0.00 |  |
| 128 | 50 | me_ga | 8.7529 | 44.96 | 46.80 | 216 | 0.00 |  |
| 128 | 50 | nsga2 | 8.8624 | 49.06 | 49.19 | 239 | 0.00 |  |
| 128 | 50 | pair_plus_b35 | 9.0287 | 49.56 | 49.75 | 111764 | 2.31 | YES |

## Contrasts (99% Bonferroni intervals, family 5; 50 ms primary)

| Array | Budget | N traj | H1 b35−pair | H2 b35−ME-GA | H5 b35−NSGA-II | C6 pair−NSGA-II | C7 pair−ME-GA |
|---:|---:|---:|---|---|---|---|---|
| 64 | 10 | 36 | -0.0013 [-0.0030, -0.0004] **FAIL (below 0)** | +0.1494 [+0.0722, +0.2707] **PASS** | +0.1031 [+0.0423, +0.1985] **PASS** | +0.1043 [+0.0426, +0.2014] **PASS** | +0.1506 [+0.0726, +0.2736] **PASS** |
| 64 | 50 (primary) | 36 | +0.0000 [-0.0003, +0.0005] **FAIL** | +0.0796 [+0.0330, +0.1509] **PASS** | +0.0404 [+0.0163, +0.0737] **PASS** | +0.0403 [+0.0161, +0.0737] **PASS** | +0.0795 [+0.0330, +0.1510] **PASS** |
| 128 | 10 | 36 | +0.0022 [-0.0002, +0.0070] **FAIL (excluded by miss rule)** | +0.5635 [+0.3513, +0.8317] **FAIL (excluded by miss rule)** | +0.2149 [+0.0849, +0.4077] **FAIL (excluded by miss rule)** | +0.2127 [+0.0833, +0.4069] **FAIL (excluded by miss rule)** | +0.5613 [+0.3502, +0.8313] **FAIL (excluded by miss rule)** |
| 128 | 50 (primary) | 36 | -0.0000 [-0.0002, +0.0001] **FAIL (excluded by miss rule)** | +0.2758 [+0.1258, +0.5074] **FAIL (excluded by miss rule)** | +0.1663 [+0.0521, +0.3503] **FAIL (excluded by miss rule)** | +0.1663 [+0.0521, +0.3503] **PASS** | +0.2758 [+0.1259, +0.5073] **PASS** |

## Provenance

- 64: munich on labkc-comm3 CPU 5 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
- 128: munich on labkc-comm3 CPU 4 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
