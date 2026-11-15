# Primary metrics M1/M2/M3 - pooled maastricht utrecht array 128 (user decision 15 Nov: Munich and Berlin dropped)

Rows: 115200 (unparseable lines skipped: 0); splits: test. M1 trajectory-averaged; M2 = search_elapsed_ms; M3 = deadline + candidate evaluations.

| Array | M3 budget (ms) | Method | M1 rate (bit/s/Hz) | M2 mean (ms) | M2 p95 (ms) | M3 evals mean | M3 evals p95 | Miss % | Excluded |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 128 | 10 | greedy | 5.9109 | 9.07 | 9.38 | 4530 | 5505 | 0.21 | no |
| 128 | 10 | pair | 5.9116 | 8.79 | 9.65 | 8019 | 18178 | 1.15 | YES |
| 128 | 10 | me_ga | 5.4889 | 2.46 | 2.73 | 9 | 9 | 0.00 | no |
| 128 | 10 | nsga2 | 5.6567 | 9.23 | 9.48 | 36 | 39 | 0.00 | no |
| 128 | 10 | pair_plus_b35 | 5.9146 | 9.60 | 9.76 | 7860 | 18690 | 1.92 | YES |
| 128 | 50 | greedy | 5.9578 | 48.86 | 49.26 | 26316 | 30724 | 0.00 | no |
| 128 | 50 | pair | 5.9898 | 46.48 | 48.56 | 79094 | 131395 | 0.00 | no |
| 128 | 50 | me_ga | 5.6702 | 43.60 | 45.46 | 188 | 201 | 0.00 | no |
| 128 | 50 | nsga2 | 5.7900 | 49.03 | 49.20 | 200 | 221 | 0.00 | no |
| 128 | 50 | pair_plus_b35 | 5.9901 | 49.63 | 49.82 | 79227 | 129219 | 3.59 | YES |
