# Primary metrics M1/M2/M3 - maastricht test array 128

Rows: 57600 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 4.3100 | 9.11 | 9.27 | 4868 | 5505 | 0.00 | no |
| 128 | 10 | pair | 4.3120 | 8.90 | 9.46 | 7664 | 18689 | 0.61 | YES |
| 128 | 10 | me_ga | 4.0604 | 2.30 | 2.43 | 9 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 4.1484 | 9.25 | 9.54 | 38 | 39 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 4.3123 | 9.58 | 9.73 | 7384 | 18945 | 0.00 | no |
| 128 | 50 | greedy | 4.3236 | 48.91 | 49.17 | 27929 | 30852 | 0.00 | no |
| 128 | 50 | pair | 4.3341 | 46.39 | 48.42 | 72509 | 125059 | 0.00 | no |
| 128 | 50 | me_ga | 4.1745 | 43.80 | 45.26 | 200 | 201 | 0.00 | no |
| 128 | 50 | nsga2 | 4.2367 | 49.05 | 49.21 | 214 | 234 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 4.3342 | 49.61 | 49.76 | 72618 | 124931 | 1.27 | YES |
