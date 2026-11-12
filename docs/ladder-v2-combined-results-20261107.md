# V2 combined b3+b5 development round: results (2026-11-07)

Design: `docs/ladder-v2-combined-design-20261107.md`. Development data only (`coupled_wire_dev_fine161`, 30 trajectories, 161-segment mesh). No test data was read. Intervals are exploratory: paired trajectory bootstrap, 10,000 resamples, seed 8251, Bonferroni over the 9 contrasts within each budget.

## Runs

| | Primary | Secondary |
|---|---|---|
| Node | 3060-3 (`labkc-comm3`), CPU 5, SMT sibling 11 | 3060-1 (`labkc-comm1`), core 3 |
| Time | 10:23:37–11:29:06 UTC (17:23–18:29 WIB), rc=0 | 16:21:08–17:26:48 WIB, rc=0 |
| Rows | 120,000 | 120,000 |
| Output sha256 | `f334639c…cd65` (local = remote) | `97663d25…bd67` (local = remote) |
| Load on the timed CPU | CPU 5 100% ours. CPU 11 busy 1.6% of the run. 2 of 196 samples had another user's thread on CPU 5 or 11 (`agung` python on CPU 11 at 10:27:17 UTC, and one more at 11:20:02 UTC) | CPU 3 100% ours. 1 of 66 samples had another user's thread on CPU 3 itself (`probati+` at start). Sibling CPU 9 was not logged |
| `pair` evaluations at 10 / 100 ms | 13,186 / 167,354 | 9,162 / 120,768 |
| Deadline misses, all 25 cells | **0** | 2–125 per cell (b-methods 42–104 per cell of 4,800 at ≥5 ms) |

Analysis outputs: `outputs/runs/pair_plus_ladder_v2_combined_n3/analysis_combined_dev161.json` (primary) and `outputs/runs/pair_plus_ladder_v2_combined/analysis_combined_dev161.json` (secondary).

Throughput across rounds, `pair` evaluations at 100 ms: no-L2 (3060-1) 161,339; fixed-L2 (3060-1) 125,580; combined on 3060-1 120,768; combined on 3060-3 167,354. On 3060-1 other users' threads were almost never on CPU 3 itself, so the slowdown there is not explained by direct sharing of the timed CPU. The SMT sibling or shared cache and memory bandwidth are plausible causes, but neither was measured. 3060-3 matched the no-L2 throughput and had no misses.

## Primary run (3060-3): per method and budget

Rate is mean worst-user SE (bit/s/Hz). Gap is to this round's best-known value per frame (mean 18.525), which includes `b35`'s own results. Restarts and pair scans are per frame.

| Method | Budget ms | Rate | Gap | p95 ms | Misses | Evaluations | Restarts | Pair scans | All-OFF share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pair | 1 | 15.339 | 3.186 | 0.52 | 0 | 1 | – | – | 1.000 |
| pair | 5 | 15.845 | 2.680 | 4.11 | 0 | 4,219 | – | – | 0.754 |
| pair | 10 | 15.961 | 2.564 | 9.08 | 0 | 13,186 | – | – | 0.686 |
| pair | 50 | 16.408 | 2.117 | 49.08 | 0 | 81,552 | – | – | 0.521 |
| pair | 100 | 16.665 | 1.860 | 99.07 | 0 | 167,354 | – | – | 0.444 |
| b0 | 1 | 15.372 | 3.153 | 0.58 | 0 | 65 | 0.0 | 0.0 | 0.965 |
| b0 | 5 | 15.830 | 2.695 | 4.71 | 0 | 4,216 | 1.4 | 1.3 | 0.757 |
| b0 | 10 | 15.937 | 2.588 | 9.71 | 0 | 12,149 | 2.4 | 4.5 | 0.697 |
| b0 | 50 | 16.380 | 2.145 | 49.71 | 0 | 76,270 | 10.0 | 30.3 | 0.528 |
| b0 | 100 | 16.638 | 1.887 | 99.71 | 0 | 156,739 | 19.5 | 62.8 | 0.454 |
| b3 | 1 | 15.372 | 3.153 | 0.57 | 0 | 65 | 0.0 | 0.0 | 0.965 |
| b3 | 5 | 15.844 | 2.681 | 4.71 | 0 | 4,323 | 1.9 | 1.4 | 0.750 |
| b3 | 10 | 15.994 | 2.531 | 9.71 | 0 | 12,716 | 2.8 | 4.8 | 0.675 |
| b3 | 50 | 16.454 | 2.071 | 49.71 | 0 | 81,538 | 11.5 | 33.4 | 0.511 |
| b3 | 100 | 16.716 | 1.809 | 99.71 | 0 | 167,190 | 22.5 | 68.8 | 0.429 |
| b5 | 1 | 15.372 | 3.153 | 0.57 | 0 | 65 | 0.0 | 0.0 | 0.965 |
| b5 | 5 | 15.836 | 2.689 | 4.72 | 0 | 4,214 | 1.4 | 1.3 | 0.757 |
| b5 | 10 | 15.937 | 2.588 | 9.73 | 0 | 12,078 | 2.6 | 4.5 | 0.697 |
| b5 | 50 | 16.437 | 2.088 | 49.74 | 0 | 80,297 | 11.9 | 33.0 | 0.514 |
| b5 | 100 | 16.711 | 1.814 | 99.74 | 0 | 165,279 | 23.3 | 68.4 | 0.428 |
| b35 | 1 | 15.372 | 3.153 | 0.57 | 0 | 65 | 0.0 | 0.0 | 0.965 |
| b35 | 5 | 15.842 | 2.683 | 4.72 | 0 | 4,315 | 1.9 | 1.4 | 0.750 |
| b35 | 10 | 15.995 | 2.530 | 9.73 | 0 | 12,638 | 3.2 | 4.8 | 0.673 |
| b35 | 50 | 16.504 | 2.021 | 49.73 | 0 | 84,785 | 13.4 | 35.6 | 0.491 |
| b35 | 100 | 16.791 | 1.734 | 99.74 | 0 | 174,415 | 26.3 | 73.7 | 0.409 |

The benchmark log does not record recombination counts separately. By construction, `b5` and `b35` recombine on every third restart once two elites exist, so at 100 ms that is about 7–8 of their 23–26 restarts per frame. This is inferred from the code, not measured.

## Primary run: contrasts (difference, [Bonferroni interval], trajectories won of 30)

| Contrast | 5 ms | 10 ms | 50 ms | 100 ms |
|---|---|---|---|---|
| b0 − pair | −0.015 [−0.043, +0.000] | −0.024 [−0.045, −0.011] | −0.028 [−0.039, −0.017] | −0.027 [−0.038, −0.018] |
| b3 − b0 | +0.014 [+0.001, +0.039] | +0.057 [+0.025, +0.093] | +0.074 [+0.036, +0.120] | +0.078 [+0.040, +0.118] |
| b5 − b0 | +0.006 [+0.000, +0.023] | +0.001 [−0.003, +0.005] | +0.057 [+0.024, +0.094] | +0.073 [+0.039, +0.106] |
| b35 − b0 | +0.012 [+0.001, +0.031] | +0.058 [+0.027, +0.093] | +0.124 [+0.075, +0.176] | +0.153 [+0.107, +0.196] |
| b3 − pair | −0.001 [−0.011, +0.008] | +0.033 [+0.006, +0.060] 23 | +0.046 [+0.010, +0.089] 21 | +0.051 [+0.016, +0.089] 21 |
| b5 − pair | −0.008 [−0.025, +0.000] | −0.024 [−0.041, −0.011] | +0.029 [−0.001, +0.065] | +0.046 [+0.015, +0.078] 22 |
| b35 − pair | −0.003 [−0.016, +0.008] | +0.034 [+0.008, +0.061] 24 | +0.097 [+0.051, +0.143] 27 | +0.126 [+0.083, +0.167] 28 |
| b35 − b3 | −0.002 [−0.010, +0.000] | +0.001 [−0.002, +0.005] | +0.051 [+0.016, +0.087] 22 | +0.075 [+0.036, +0.111] 25 |
| b35 − b5 | +0.006 [−0.001, +0.015] | +0.057 [+0.027, +0.092] | +0.068 [+0.028, +0.108] | +0.080 [+0.036, +0.121] |

At 1 ms, every fast method is +0.033 [+0.010, +0.063] over `pair` and identical to `b0`. `pair` makes 1 evaluation (all-OFF) at 1 ms, while `b0` completes a partial single-flip climb. This is the `b0` overhead change, not a component effect.

## Reading by the declared rule (primary run)

- **1 ms:** no component beats `b0`, so no candidate.
- **5 ms:** `b3` and `b35` beat `b0`, but nothing beats `pair`. No improvement candidate.
- **10 ms:** `b3` and `b35` qualify over `pair`. `b35 − b3` includes zero, so the simpler **`b3`** is preferred.
- **50 ms:** `b3` and `b35` qualify, and `b5 − pair` includes zero. `b35` beats both components, so **`b35`** is preferred.
- **100 ms:** `b3`, `b5` and `b35` qualify. `b35` beats both components, so **`b35`** is preferred.

The two components add up: at 100 ms, `b3 − b0` + `b5 − b0` = +0.151 and `b35 − b0` = +0.153. Some of the gain comes from throughput, not only from better starting points. `b35` completed 26.3 restarts per frame against 19.5 for `b0`, and 174k evaluations against 157k. Sparse and recombined starts climb in fewer steps. `b35` also returned all-OFF less often (0.409 against 0.444 for `pair`).

Against `pair`, `b35` closes 0.126 of `pair`'s 1.860 gap to the best-known value at 100 ms, about 7%.

## Replication

**b3 vs pair replicated.** No-L2 round, 3060-1: +0.032, +0.047, +0.052 at 10/50/100 ms. This round, 3060-3: +0.033, +0.046, +0.051. Both rounds used the same frames and seeds, so this replicates the result across runs and timing noise, not across new data.

**The two nodes agree.** Every contrast at 10, 50 and 100 ms has the same sign on both nodes and differs by at most 0.015. The verdict of whether the interval excludes zero is the same, with these exceptions:
- `b5 − pair` at 50 ms: lower bound +0.002 on 3060-1, −0.001 on 3060-3.
- At 5 ms, `b3 − b0` and `b35 − b0` exclude zero only on 3060-3, and `b5 − pair` and `b35 − pair` only on 3060-1 (negative).
- At 1 ms, the `b0 − pair` effect is about half as large on 3060-1 (+0.015).

The 50 and 100 ms readings, `b35` over both components and over `pair`, hold on both nodes. On 3060-1 the size is +0.101/+0.120 against `pair`, despite its 28% lower throughput and 1–2% misses.

## Limitations

- **Development only, with selection.** `b35` was proposed after the no-L2 round on the same 30 trajectories and seeds. The intervals do not correct for that choice. Only the frozen `coupled_wire_test_v2` run can support a claim.
- **The practical margin is unset.** The largest gain, +0.126 at 100 ms, is far below the single-frame mesh shift seen earlier (frame 190, −1.14 from coarse to fine). All scoring here is on the 161-segment mesh, which is not shown to be converged.
- **Miss rule.** The current rule is zero misses across all methods. It is met at every budget on 3060-3 and at none on 3060-1, so the rule depends on the node. The primary budget is still undecided.
- **Recombination counts** are inferred, not logged.
- **Best-known reference.** It is the maximum within this round, so it differs by round (18.525 here, 18.403 in the no-L2 round) and should not be compared across rounds.

## Carried forward

The candidate to carry towards a `matched_v2` freeze is **`pair_plus_b35`** at 50 or 100 ms, with `b3` as the simpler alternative if 10 ms becomes the primary budget. Nothing is frozen. These decisions still need the user: the primary budget, the miss rule, the practical margin and the mesh-convergence criterion. `coupled_wire_test_v2` was not touched.
