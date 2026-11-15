# Primary metrics M1/M2/M3 - pooled maastricht utrecht berlin array 128 (audit: Munich excluded, failed declared check)

Rows: 172800 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 6.5730 | 9.06 | 9.45 | 4614 | 5505 | 0.14 | no |
| 128 | 10 | pair | 6.5777 | 8.63 | 9.67 | 9356 | 18689 | 1.52 | YES |
| 128 | 10 | me_ga | 6.1328 | 2.43 | 2.73 | 9 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 6.3217 | 9.23 | 9.48 | 37 | 40 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 6.5808 | 9.59 | 9.75 | 9234 | 19073 | 1.89 | YES |
| 128 | 50 | greedy | 6.6207 | 48.90 | 49.32 | 26807 | 30852 | 0.00 | no |
| 128 | 50 | pair | 6.6557 | 46.66 | 48.60 | 89485 | 140034 | 0.00 | no |
| 128 | 50 | me_ga | 6.3445 | 44.05 | 46.56 | 197 | 226 | 0.00 | no |
| 128 | 50 | nsga2 | 6.4601 | 49.04 | 49.19 | 209 | 239 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 6.6558 | 49.61 | 49.79 | 89340 | 138630 | 2.69 | YES |
