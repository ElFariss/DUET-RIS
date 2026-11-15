# RIS-relevant v3 VALIDATION (rr3 0084-0101, 18 trajectories, 3 seeds, no heads) - descriptive

## Primary metrics (M1 rate bit/s/Hz, M2 search_elapsed_ms mean/p95, M3 budget + evaluations)

| Array | Budget ms | Method | M1 | M2 mean | M2 p95 | M3 evals mean | Miss % | Excl. |
|---:|---:|---|---:|---:|---:|---:|---:|---|
| 64 | 5 | greedy | 4.8963 | 4.12 | 4.22 | 1944 | 0.00 |  |
| 64 | 5 | pair | 4.9211 | 4.10 | 4.23 | 3082 | 0.00 |  |
| 64 | 5 | me_ga | 4.6903 | 4.10 | 4.47 | 91 | 0.00 |  |
| 64 | 5 | nsga2 | 4.7305 | 4.57 | 4.65 | 71 | 0.00 |  |
| 64 | 5 | pair_plus_b3 | 4.9070 | 4.50 | 4.62 | 2621 | 0.00 |  |
| 64 | 5 | pair_plus_b5 | 4.9091 | 4.51 | 4.64 | 2681 | 0.00 |  |
| 64 | 5 | pair_plus_b35 | 4.9089 | 4.51 | 4.64 | 2682 | 0.00 |  |
| 64 | 5 | pair_plus_b35_m0_k128 | 4.9043 | 4.50 | 4.64 | 2136 | 0.00 |  |
| 64 | 10 | greedy | 4.9124 | 9.12 | 9.18 | 4503 | 0.00 |  |
| 64 | 10 | pair | 4.9558 | 8.86 | 9.11 | 10484 | 0.12 |  |
| 64 | 10 | me_ga | 4.7285 | 9.02 | 9.35 | 200 | 0.00 |  |
| 64 | 10 | nsga2 | 4.8078 | 9.56 | 9.64 | 158 | 0.00 |  |
| 64 | 10 | pair_plus_b3 | 4.9537 | 9.50 | 9.63 | 9710 | 0.00 |  |
| 64 | 10 | pair_plus_b5 | 4.9536 | 9.52 | 9.65 | 9733 | 0.00 |  |
| 64 | 10 | pair_plus_b35 | 4.9538 | 9.51 | 9.65 | 9749 | 0.00 |  |
| 64 | 10 | pair_plus_b35_m0_k128 | 4.9431 | 9.54 | 9.65 | 7078 | 0.00 |  |
| 64 | 50 | greedy | 4.9337 | 49.12 | 49.18 | 25014 | 0.00 |  |
| 64 | 50 | pair | 4.9683 | 48.83 | 49.02 | 66222 | 0.00 |  |
| 64 | 50 | me_ga | 4.8538 | 49.04 | 49.65 | 1158 | 0.00 |  |
| 64 | 50 | nsga2 | 4.9291 | 49.41 | 49.49 | 1147 | 0.00 |  |
| 64 | 50 | pair_plus_b3 | 4.9683 | 49.50 | 49.63 | 61759 | 0.00 |  |
| 64 | 50 | pair_plus_b5 | 4.9699 | 49.50 | 49.65 | 63165 | 0.00 |  |
| 64 | 50 | pair_plus_b35 | 4.9695 | 49.50 | 49.65 | 63115 | 0.00 |  |
| 64 | 50 | pair_plus_b35_m0_k128 | 4.9664 | 49.50 | 49.65 | 47299 | 0.00 |  |
| 64 | 100 | greedy | 4.9411 | 99.12 | 99.18 | 50708 | 0.00 |  |
| 64 | 100 | pair | 4.9715 | 98.83 | 99.02 | 135939 | 0.00 |  |
| 64 | 100 | me_ga | 4.9007 | 99.23 | 99.80 | 2799 | 0.58 | YES |
| 64 | 100 | nsga2 | 4.9450 | 98.95 | 99.04 | 2410 | 0.00 |  |
| 64 | 100 | pair_plus_b3 | 4.9717 | 99.51 | 99.63 | 127322 | 0.00 |  |
| 64 | 100 | pair_plus_b5 | 4.9733 | 99.50 | 99.65 | 130519 | 0.00 |  |
| 64 | 100 | pair_plus_b35 | 4.9729 | 99.50 | 99.65 | 130412 | 0.00 |  |
| 64 | 100 | pair_plus_b35_m0_k128 | 4.9708 | 99.49 | 99.65 | 98066 | 0.00 |  |
| 128 | 5 | greedy | 4.7094 | 4.18 | 4.51 | 1891 | 0.00 |  |
| 128 | 5 | pair | 4.7116 | 4.19 | 4.60 | 2400 | 0.00 |  |
| 128 | 5 | me_ga | 4.4356 | 2.25 | 2.52 | 9 | 0.00 |  |
| 128 | 5 | nsga2 | 4.5131 | 4.26 | 4.37 | 18 | 0.00 |  |
| 128 | 5 | pair_plus_b3 | 4.7192 | 4.58 | 4.73 | 2454 | 0.00 |  |
| 128 | 5 | pair_plus_b5 | 4.7202 | 4.58 | 4.72 | 2468 | 0.00 |  |
| 128 | 5 | pair_plus_b35 | 4.7205 | 4.58 | 4.72 | 2472 | 0.00 |  |
| 128 | 5 | pair_plus_b35_m0_k128 | 4.7202 | 4.62 | 4.76 | 2103 | 1.50 | YES |
| 128 | 10 | greedy | 4.7981 | 9.09 | 9.28 | 4764 | 0.00 |  |
| 128 | 10 | pair | 4.8104 | 8.87 | 9.72 | 8558 | 3.01 | YES |
| 128 | 10 | me_ga | 4.4368 | 2.44 | 2.67 | 10 | 0.00 |  |
| 128 | 10 | nsga2 | 4.5533 | 9.25 | 9.52 | 38 | 0.00 |  |
| 128 | 10 | pair_plus_b3 | 4.8125 | 9.61 | 9.74 | 8202 | 0.81 | YES |
| 128 | 10 | pair_plus_b5 | 4.8124 | 9.62 | 9.75 | 8328 | 1.16 | YES |
| 128 | 10 | pair_plus_b35 | 4.8122 | 9.62 | 9.75 | 8264 | 1.27 | YES |
| 128 | 10 | pair_plus_b35_m0_k128 | 4.8043 | 9.55 | 9.74 | 5749 | 0.69 | YES |
| 128 | 50 | greedy | 4.8365 | 48.91 | 49.23 | 27196 | 0.00 |  |
| 128 | 50 | pair | 4.9033 | 46.59 | 48.52 | 83514 | 0.12 |  |
| 128 | 50 | me_ga | 4.6133 | 44.44 | 46.96 | 206 | 0.00 |  |
| 128 | 50 | nsga2 | 4.7075 | 49.05 | 49.20 | 213 | 0.00 |  |
| 128 | 50 | pair_plus_b3 | 4.9032 | 49.59 | 49.74 | 83693 | 1.04 | YES |
| 128 | 50 | pair_plus_b5 | 4.9033 | 49.60 | 49.77 | 83183 | 1.74 | YES |
| 128 | 50 | pair_plus_b35 | 4.9032 | 49.60 | 49.77 | 83413 | 1.16 | YES |
| 128 | 50 | pair_plus_b35_m0_k128 | 4.8957 | 49.57 | 49.75 | 61536 | 0.69 | YES |
| 128 | 100 | greedy | 4.8468 | 98.87 | 99.12 | 55499 | 0.00 |  |
| 128 | 100 | pair | 4.9116 | 96.45 | 98.27 | 179532 | 0.00 |  |
| 128 | 100 | me_ga | 4.6546 | 94.57 | 97.01 | 439 | 0.00 |  |
| 128 | 100 | nsga2 | 4.7942 | 98.57 | 98.73 | 551 | 0.00 |  |
| 128 | 100 | pair_plus_b3 | 4.9107 | 99.58 | 99.74 | 177004 | 1.39 | YES |
| 128 | 100 | pair_plus_b5 | 4.9116 | 99.60 | 99.78 | 178146 | 2.55 | YES |
| 128 | 100 | pair_plus_b35 | 4.9107 | 99.60 | 99.79 | 178214 | 1.50 | YES |
| 128 | 100 | pair_plus_b35_m0_k128 | 4.9075 | 99.55 | 99.77 | 131236 | 0.46 |  |
| 256 | 5 | greedy | 5.2538 | 5.05 | 5.52 | 1 | 38.66 | YES |
| 256 | 5 | pair | 5.2538 | 5.04 | 5.52 | 1 | 33.22 | YES |
| 256 | 5 | me_ga | 4.7908 | 11.68 | 13.43 | 1 | 91.09 | YES |
| 256 | 5 | nsga2 | 5.2538 | 1.71 | 1.99 | 1 | 0.00 |  |
| 256 | 5 | pair_plus_b3 | 5.2538 | 5.05 | 5.50 | 1 | 35.19 | YES |
| 256 | 5 | pair_plus_b5 | 5.2538 | 5.05 | 5.55 | 1 | 35.30 | YES |
| 256 | 5 | pair_plus_b35 | 5.2538 | 5.04 | 5.52 | 1 | 34.61 | YES |
| 256 | 5 | pair_plus_b35_m0_k128 | 5.2538 | 5.07 | 5.55 | 1 | 40.28 | YES |
| 256 | 10 | greedy | 5.6562 | 9.30 | 9.52 | 2236 | 0.00 |  |
| 256 | 10 | pair | 5.6565 | 9.31 | 9.51 | 2241 | 0.12 |  |
| 256 | 10 | me_ga | 4.7908 | 12.74 | 13.79 | 1 | 100.00 | YES |
| 256 | 10 | nsga2 | 5.3267 | 6.97 | 7.41 | 5 | 0.00 |  |
| 256 | 10 | pair_plus_b3 | 5.6722 | 9.76 | 9.99 | 2398 | 4.28 | YES |
| 256 | 10 | pair_plus_b5 | 5.6741 | 9.77 | 10.00 | 2418 | 5.44 | YES |
| 256 | 10 | pair_plus_b35 | 5.6742 | 9.76 | 10.01 | 2421 | 6.13 | YES |
| 256 | 10 | pair_plus_b35_m0_k128 | 5.6730 | 9.77 | 10.00 | 2408 | 4.98 | YES |
| 256 | 50 | greedy | 6.1334 | 46.19 | 49.54 | 19544 | 3.36 | YES |
| 256 | 50 | pair | 6.1604 | 45.49 | 52.52 | 51755 | 8.91 | YES |
| 256 | 50 | me_ga | 5.2619 | 12.89 | 14.01 | 9 | 0.00 |  |
| 256 | 50 | nsga2 | 5.4640 | 46.71 | 47.39 | 33 | 0.00 |  |
| 256 | 50 | pair_plus_b3 | 6.1727 | 51.03 | 55.02 | 52316 | 42.82 | YES |
| 256 | 50 | pair_plus_b5 | 6.1729 | 51.04 | 54.99 | 52213 | 42.01 | YES |
| 256 | 50 | pair_plus_b35 | 6.1724 | 51.03 | 54.94 | 52062 | 42.94 | YES |
| 256 | 50 | pair_plus_b35_m0_k128 | 6.1562 | 51.04 | 54.69 | 35335 | 44.68 | YES |
| 256 | 100 | greedy | 6.1632 | 94.16 | 96.79 | 41107 | 0.00 |  |
| 256 | 100 | pair | 6.2497 | 90.72 | 97.06 | 162059 | 0.81 | YES |
| 256 | 100 | me_ga | 5.4575 | 68.92 | 81.65 | 50 | 0.00 |  |
| 256 | 100 | nsga2 | 5.5629 | 96.22 | 96.88 | 69 | 0.00 |  |
| 256 | 100 | pair_plus_b3 | 6.2562 | 101.70 | 106.52 | 168171 | 56.83 | YES |
| 256 | 100 | pair_plus_b5 | 6.2564 | 101.74 | 106.89 | 168189 | 57.18 | YES |
| 256 | 100 | pair_plus_b35 | 6.2565 | 101.73 | 106.96 | 168563 | 56.60 | YES |
| 256 | 100 | pair_plus_b35_m0_k128 | 6.2277 | 101.63 | 105.95 | 118890 | 59.49 | YES |

## Hypotheses (99% Bonferroni intervals, family 5; primary budget 50 ms)

| Array | Budget | H1 b35−pair | H2 b35−ME-GA | H3a share head/M0 | H3b head−M0 | H3 | H4 head−b35 | H5 b35−NSGA-II |
|---:|---:|---|---|---|---|---|---|---|
| 64 | 5 | -0.0122 [-0.0280, -0.0024] **FAIL** | +0.2187 [+0.1214, +0.3319] **PASS** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.1785 [+0.0985, +0.2758] **PASS** |
| 64 | 10 | -0.0020 [-0.0046, -0.0002] **FAIL** | +0.2252 [+0.1174, +0.3634] **PASS** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.1460 [+0.0796, +0.2370] **PASS** |
| 64 | 50 (primary) | +0.0011 [-0.0007, +0.0046] **FAIL** | +0.1156 [+0.0528, +0.2107] **PASS** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.0403 [+0.0221, +0.0646] **PASS** |
| 64 | 100 | +0.0015 [+0.0000, +0.0037] **FAIL** | +0.0722 [+0.0284, +0.1433] **not testable at this budget** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.0279 [+0.0143, +0.0445] **PASS** |
| 128 | 5 | +0.0090 [+0.0034, +0.0165] **PASS** | +0.2849 [+0.1433, +0.4653] **PASS** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.2075 [+0.1015, +0.3367] **PASS** |
| 128 | 10 | +0.0018 [+0.0001, +0.0043] **FAIL (excluded by miss rule)** | +0.3754 [+0.2037, +0.5759] **FAIL (excluded by miss rule)** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.2589 [+0.1441, +0.3900] **FAIL (excluded by miss rule)** |
| 128 | 50 (primary) | -0.0001 [-0.0006, +0.0003] **FAIL (excluded by miss rule)** | +0.2899 [+0.1643, +0.4352] **FAIL (excluded by miss rule)** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.1957 [+0.1142, +0.2871] **FAIL (excluded by miss rule)** |
| 128 | 100 | -0.0009 [-0.0024, +0.0001] **FAIL (excluded by miss rule)** | +0.2561 [+0.1408, +0.3926] **FAIL (excluded by miss rule)** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.1165 [+0.0613, +0.1830] **FAIL (excluded by miss rule)** |
| 256 | 5 | +0.0000 [+0.0000, +0.0000] **FAIL (excluded by miss rule)** | +0.4630 [+0.1084, +0.9586] **not testable at this budget** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.0000 [+0.0000, +0.0000] **FAIL (excluded by miss rule)** |
| 256 | 10 | +0.0177 [+0.0063, +0.0342] **FAIL (excluded by miss rule)** | +0.8834 [+0.4206, +1.4496] **not testable at this budget** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.3475 [+0.1732, +0.5531] **FAIL (excluded by miss rule)** |
| 256 | 50 (primary) | +0.0120 [+0.0034, +0.0223] **FAIL (excluded by miss rule)** | +0.9104 [+0.5154, +1.3694] **FAIL (excluded by miss rule)** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.7083 [+0.3601, +1.1166] **FAIL (excluded by miss rule)** |
| 256 | 100 | +0.0069 [+0.0024, +0.0125] **FAIL (excluded by miss rule)** | +0.7990 [+0.4373, +1.2292] **FAIL (excluded by miss rule)** | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | not tested (no locked head for this array size) | +0.6936 [+0.3566, +1.0912] **FAIL (excluded by miss rule)** |

## Run provenance

- 64: host labkc-comm2, CPU 5 (AMD Ryzen 5 5600 6-Core Processor), numpy 2.2.6, seeds 3, rows 27648, flagged frames 0/288, heads none, resumes 0, sampler samples 0
- 128: host labkc-comm3, CPU 4 (AMD Ryzen 5 5600 6-Core Processor), numpy 2.2.6, seeds 3, rows 27648, flagged frames 0/288, heads none, resumes 0, sampler samples 0
- 256: host labkc-comm3, CPU 5 (AMD Ryzen 5 5600 6-Core Processor), numpy 2.2.6, seeds 3, rows 27648, flagged frames 0/288, heads none, resumes 0, sampler samples 0
