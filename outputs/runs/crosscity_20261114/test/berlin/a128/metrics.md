# Primary metrics M1/M2/M3 - berlin test array 128

Rows: 57600 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 7.8974 | 9.05 | 9.54 | 4783 | 5634 | 0.00 | no |
| 128 | 10 | pair | 7.9099 | 8.31 | 9.70 | 12031 | 19201 | 2.24 | YES |
| 128 | 10 | me_ga | 7.4205 | 2.36 | 2.31 | 10 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 7.6516 | 9.25 | 9.48 | 40 | 40 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 7.9132 | 9.55 | 9.73 | 11983 | 19329 | 1.84 | YES |
| 128 | 50 | greedy | 7.9465 | 48.97 | 49.41 | 27788 | 31110 | 0.00 | no |
| 128 | 50 | pair | 7.9874 | 47.03 | 48.64 | 110268 | 147905 | 0.00 | no |
| 128 | 50 | me_ga | 7.6933 | 44.95 | 46.78 | 216 | 226 | 0.00 | no |
| 128 | 50 | nsga2 | 7.8005 | 49.06 | 49.19 | 228 | 276 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 7.9872 | 49.56 | 49.74 | 109565 | 147138 | 0.90 | YES |
