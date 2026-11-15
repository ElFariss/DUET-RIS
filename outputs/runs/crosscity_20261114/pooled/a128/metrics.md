# Primary metrics M1/M2/M3 - pooled munich maastricht utrecht berlin array 128

Rows: 230400 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 7.1685 | 9.05 | 9.44 | 4613 | 5505 | 0.10 | no |
| 128 | 10 | pair | 7.1740 | 8.52 | 9.66 | 10475 | 24897 | 1.48 | YES |
| 128 | 10 | me_ga | 6.7000 | 2.40 | 2.72 | 9 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 6.9288 | 9.24 | 9.47 | 38 | 40 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 7.1768 | 9.58 | 9.75 | 10438 | 25666 | 1.71 | YES |
| 128 | 50 | greedy | 7.2118 | 48.92 | 49.35 | 26867 | 30852 | 0.00 | no |
| 128 | 50 | pair | 7.2489 | 46.77 | 48.63 | 95214 | 152962 | 0.00 | no |
| 128 | 50 | me_ga | 6.9466 | 44.28 | 46.65 | 202 | 226 | 0.00 | no |
| 128 | 50 | nsga2 | 7.0607 | 49.04 | 49.19 | 217 | 274 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 7.2490 | 49.59 | 49.79 | 94946 | 152836 | 2.60 | YES |
