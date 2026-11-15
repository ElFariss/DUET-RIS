# Primary metrics M1/M2/M3 - pooled maastricht utrecht array 64 (user decision 15 Nov: Munich and Berlin dropped)

Rows: 115200 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 64 | 10 | greedy | 5.3714 | 9.14 | 9.24 | 3951 | 4550 | 0.00 | no |
| 64 | 10 | pair | 5.4067 | 8.75 | 9.04 | 11828 | 19491 | 0.00 | no |
| 64 | 10 | me_ga | 5.1358 | 8.72 | 9.25 | 170 | 201 | 0.00 | no |
| 64 | 10 | nsga2 | 5.2363 | 9.56 | 9.65 | 135 | 159 | 0.00 | no |
| 64 | 10 | pair_plus_b35 | 5.4034 | 9.51 | 9.67 | 10611 | 17603 | 0.00 | no |
| 64 | 50 | greedy | 5.3900 | 49.14 | 49.22 | 22203 | 25565 | 0.00 | no |
| 64 | 50 | pair | 5.4191 | 48.71 | 48.97 | 74921 | 113160 | 0.00 | no |
| 64 | 50 | me_ga | 5.2816 | 48.81 | 49.54 | 990 | 1155 | 0.03 | no |
| 64 | 50 | nsga2 | 5.3550 | 49.50 | 49.62 | 985 | 1289 | 0.00 | no |
| 64 | 50 | pair_plus_b35 | 5.4195 | 49.49 | 49.68 | 70449 | 105770 | 0.00 | no |
