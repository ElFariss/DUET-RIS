# Primary metrics M1/M2/M3 - munich test array 128

Rows: 57600 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 8.9547 | 9.02 | 9.42 | 4610 | 5250 | 0.00 | no |
| 128 | 10 | pair | 8.9628 | 8.17 | 9.57 | 13830 | 25538 | 1.35 | YES |
| 128 | 10 | me_ga | 8.4015 | 2.31 | 2.27 | 10 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 8.7501 | 9.25 | 9.45 | 39 | 40 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 8.9650 | 9.58 | 9.74 | 14051 | 25794 | 1.16 | YES |
| 128 | 50 | greedy | 8.9852 | 48.98 | 49.41 | 27046 | 30864 | 0.00 | no |
| 128 | 50 | pair | 9.0287 | 47.09 | 48.71 | 112400 | 167681 | 0.00 | no |
| 128 | 50 | me_ga | 8.7529 | 44.96 | 46.80 | 216 | 226 | 0.00 | no |
| 128 | 50 | nsga2 | 8.8624 | 49.06 | 49.19 | 239 | 390 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 9.0287 | 49.56 | 49.75 | 111764 | 167682 | 2.31 | YES |
