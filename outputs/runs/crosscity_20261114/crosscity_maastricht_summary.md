# maastricht v3x test

## Primary metrics (M1 bit/s/Hz, M2 search_elapsed_ms mean/p95, M3 budget + evaluations)

| Array | Budget ms | Method | M1 | M2 mean | M2 p95 | M3 evals mean | Miss % | Excl. |
|---:|---:|---|---:|---:|---:|---:|---:|---|
| 64 | 10 | greedy | 3.4664 | 9.13 | 9.22 | 4121 | 0.00 |  |
| 64 | 10 | pair | 3.4918 | 8.75 | 9.07 | 9944 | 0.00 |  |
| 64 | 10 | me_ga | 3.3323 | 8.78 | 9.31 | 177 | 0.00 |  |
| 64 | 10 | nsga2 | 3.3793 | 9.56 | 9.65 | 140 | 0.00 |  |
| 64 | 10 | pair_plus_b35 | 3.4895 | 9.54 | 9.67 | 8972 | 0.00 |  |
| 64 | 50 | greedy | 3.4794 | 49.13 | 49.21 | 23064 | 0.00 |  |
| 64 | 50 | pair | 3.4980 | 48.71 | 48.99 | 63480 | 0.00 |  |
| 64 | 50 | me_ga | 3.4178 | 48.91 | 49.63 | 1035 | 0.07 |  |
| 64 | 50 | nsga2 | 3.4668 | 49.49 | 49.61 | 1024 | 0.00 |  |
| 64 | 50 | pair_plus_b35 | 3.4982 | 49.51 | 49.68 | 59846 | 0.00 |  |
| 128 | 10 | greedy | 4.3100 | 9.11 | 9.27 | 4868 | 0.00 |  |
| 128 | 10 | pair | 4.3120 | 8.90 | 9.46 | 7664 | 0.61 | YES |
| 128 | 10 | me_ga | 4.0604 | 2.30 | 2.43 | 9 | 0.00 |  |
| 128 | 10 | nsga2 | 4.1484 | 9.25 | 9.54 | 38 | 0.00 |  |
| 128 | 10 | pair_plus_b35 | 4.3123 | 9.58 | 9.73 | 7384 | 0.00 |  |
| 128 | 50 | greedy | 4.3236 | 48.91 | 49.17 | 27929 | 0.00 |  |
| 128 | 50 | pair | 4.3341 | 46.39 | 48.42 | 72509 | 0.00 |  |
| 128 | 50 | me_ga | 4.1745 | 43.80 | 45.26 | 200 | 0.00 |  |
| 128 | 50 | nsga2 | 4.2367 | 49.05 | 49.21 | 214 | 0.00 |  |
| 128 | 50 | pair_plus_b35 | 4.3342 | 49.61 | 49.76 | 72618 | 1.27 | YES |

## Contrasts (99% Bonferroni intervals, family 5; 50 ms primary)

| Array | Budget | N traj | H1 b35−pair | H2 b35−ME-GA | H5 b35−NSGA-II | C6 pair−NSGA-II | C7 pair−ME-GA |
|---:|---:|---:|---|---|---|---|---|
| 64 | 10 | 36 | -0.0023 [-0.0071, -0.0004] **FAIL (below 0)** | +0.1572 [+0.0862, +0.2518] **PASS** | +0.1101 [+0.0610, +0.1735] **PASS** | +0.1125 [+0.0615, +0.1798] **PASS** | +0.1595 [+0.0867, +0.2579] **PASS** |
| 64 | 50 (primary) | 36 | +0.0001 [-0.0000, +0.0003] **FAIL** | +0.0804 [+0.0419, +0.1379] **PASS** | +0.0313 [+0.0176, +0.0490] **PASS** | +0.0312 [+0.0175, +0.0487] **PASS** | +0.0803 [+0.0418, +0.1376] **PASS** |
| 128 | 10 | 36 | +0.0002 [-0.0004, +0.0011] **FAIL (excluded by miss rule)** | +0.2518 [+0.1554, +0.3573] **PASS** | +0.1639 [+0.0932, +0.2454] **PASS** | +0.1636 [+0.0930, +0.2454] **FAIL (excluded by miss rule)** | +0.2516 [+0.1552, +0.3572] **FAIL (excluded by miss rule)** |
| 128 | 50 (primary) | 36 | +0.0001 [-0.0001, +0.0003] **FAIL (excluded by miss rule)** | +0.1597 [+0.0953, +0.2342] **FAIL (excluded by miss rule)** | +0.0975 [+0.0587, +0.1396] **FAIL (excluded by miss rule)** | +0.0974 [+0.0586, +0.1395] **PASS** | +0.1596 [+0.0954, +0.2340] **PASS** |

## Provenance

- 64: maastricht on labkc-comm3 CPU 4 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
- 128: maastricht on labkc-comm3 CPU 4 (AMD Ryzen 5 5600 6-Core Processor), seeds 10, trajectories 36 (missing []), flagged 0/576, resumes 0, rows 57600
