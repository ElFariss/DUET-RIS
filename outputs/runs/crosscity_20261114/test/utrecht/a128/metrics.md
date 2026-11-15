# Primary metrics M1/M2/M3 - utrecht test array 128

Rows: 57600 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 7.5117 | 9.03 | 9.51 | 4191 | 4993 | 0.42 | no |
| 128 | 10 | pair | 7.5112 | 8.68 | 9.79 | 8373 | 17793 | 1.70 | YES |
| 128 | 10 | me_ga | 6.9174 | 2.63 | 2.76 | 9 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 7.1651 | 9.21 | 9.33 | 34 | 35 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 7.5169 | 9.62 | 9.83 | 8336 | 18305 | 3.84 | YES |
| 128 | 50 | greedy | 7.5919 | 48.81 | 49.31 | 24704 | 27908 | 0.00 | no |
| 128 | 50 | pair | 7.6456 | 46.56 | 48.72 | 85678 | 135809 | 0.00 | no |
| 128 | 50 | me_ga | 7.1658 | 43.39 | 45.73 | 175 | 175 | 0.00 | no |
| 128 | 50 | nsga2 | 7.3433 | 49.00 | 49.17 | 186 | 196 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 7.6459 | 49.65 | 50.06 | 85837 | 135811 | 5.90 | YES |
