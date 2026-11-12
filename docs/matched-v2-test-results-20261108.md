# matched_v2 held-out test: results (Paper 1), 2026-11-08

This is the single run of the frozen protocol `configs/experiments/matched_v2.json` (sha256 `d9ed1a21…e468`, frozen 2026-11-07 12:49:41 UTC) on `coupled_wire_test_v2`: 30 trajectories, 480 frames, never used for design. The analysis is the frozen `scripts/analyze_matched_v2_test.py` (sha256 `a2ea8394…18ab`, equal to the frozen value), run unchanged. Nothing was retuned or rerun.

## Run
- **Node and timing:**
  - 3060-3 (`labkc-comm3`), CPU 5 pinned, single thread.
  - Generation of the 161-segment test matrices ran 12:50–21:36 UTC on the other CPUs; the test ran 21:36–22:54 UTC.
  - rc=0, 115,200 rows (6 methods × 4 budgets × 10 seeds × 480 frames).
- **Load on the timed CPU:** 234 samples, every 20 s. No thread of another user was ever on CPU 5 or its sibling 11. CPU 11 was 0.1% busy over the run.
- **Integrity:** the outputs, the 161-segment scenario and the generation manifest were synced locally and match `logs/matched_v2_test/output.sha256`:
  - `test_v2.jsonl` `f4cf11a3…de2b`
  - `analysis_test_v2.json` `18e81d61…dea`
- **Mesh:** every returned action was found on the 161-segment network and rescored on the 81-segment network of the same frame, outside the timed section.

## Decision rule (frozen)
A contrast is **supported** only if both hold:
- its Bonferroni interval (5 contrasts per budget; paired trajectory bootstrap, 10,000 resamples, seed 8251) lies above zero on both the 161- and the 81-segment rates;
- neither method misses more than 0.5% of its runs at that budget.

50 ms is confirmatory; 5, 10 and 100 ms are secondary.

## Primary budget, 50 ms (confirmatory)

| Contrast | 161 segments | 81 segments | Trajectories won | Verdict |
|---|---|---|---:|---|
| b35 − pair | +0.085 [+0.047, +0.128] | +0.084 [+0.041, +0.125] | 27/30 | **supported** |
| b35 − b3 | +0.053 [+0.013, +0.093] | +0.046 [+0.008, +0.086] | 22/30 | **supported** |
| b35 − b5 | +0.047 [+0.014, +0.082] | +0.044 [+0.008, +0.080] | 21/30 | **supported** |
| b35 − me_ga | +10.561 [+9.924, +11.167] | +10.521 [+9.866, +11.140] | 30/30 | **supported** |
| pair − greedy | +0.861 [+0.648, +1.098] | +0.832 [+0.629, +1.053] | 30/30 | **supported** |

Every method at 50 ms met the miss rule: `me_ga` missed 14 of 4,800 runs (0.29%), and all other methods missed none.

## All cells
Rate is mean worst-user SE (bit/s/Hz) on the 161-segment mesh. The shift is the 81-segment rescored rate minus the 161-segment rate.

| Method | Budget ms | Rate | Rate at 81 | Shift | p95 ms | Misses (of 4,800) |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 5 | 15.224 | 15.218 | −0.006 | 4.24 | 0 |
| greedy | 10 | 15.277 | 15.270 | −0.007 | 9.25 | 0 |
| greedy | 50 | 15.502 | 15.489 | −0.013 | 49.25 | 0 |
| greedy | 100 | 15.638 | 15.617 | −0.021 | 99.25 | 0 |
| pair | 5 | 15.626 | 15.622 | −0.004 | 4.12 | 0 |
| pair | 10 | 15.786 | 15.777 | −0.010 | 9.11 | 0 |
| pair | 50 | 16.362 | 16.321 | −0.041 | 49.10 | 0 |
| pair | 100 | 16.690 | 16.621 | −0.069 | 99.10 | 0 |
| me_ga | 5 | 2.912 | 2.911 | −0.001 | 4.61 | 0 |
| me_ga | 10 | 3.268 | 3.266 | −0.001 | 9.02 | 0 |
| me_ga | 50 | 5.887 | 5.884 | −0.003 | 49.80 | 14 |
| me_ga | 100 | 8.236 | 8.232 | −0.004 | 99.92 | 97 (2.0%, **excluded**) |
| b3 | 5 | 15.629 | 15.625 | −0.004 | 4.71 | 0 |
| b3 | 10 | 15.793 | 15.784 | −0.009 | 9.70 | 0 |
| b3 | 50 | 16.395 | 16.359 | −0.036 | 49.70 | 0 |
| b3 | 100 | 16.741 | 16.687 | −0.053 | 99.70 | 0 |
| b5 | 5 | 15.619 | 15.614 | −0.004 | 4.72 | 0 |
| b5 | 10 | 15.760 | 15.749 | −0.011 | 9.72 | 0 |
| b5 | 50 | 16.400 | 16.361 | −0.039 | 49.73 | 0 |
| b5 | 100 | 16.742 | 16.678 | −0.064 | 99.73 | 0 |
| b35 | 5 | 15.629 | 15.625 | −0.004 | 4.71 | 0 |
| b35 | 10 | 15.797 | 15.787 | −0.010 | 9.72 | 0 |
| b35 | 50 | 16.448 | 16.405 | −0.043 | 49.73 | 0 |
| b35 | 100 | 16.815 | 16.753 | −0.062 | 99.73 | 0 |

## Secondary budgets

| Contrast | 5 ms (161 / 81) | 10 ms (161 / 81) | 100 ms (161 / 81) |
|---|---|---|---|
| b35 − pair | +0.003 [−0.005, +0.012] / +0.003 [−0.005, +0.011]: not supported | +0.011 [−0.014, +0.035] / +0.011 [−0.013, +0.035]: not supported | +0.125 [+0.072, +0.180] / +0.132 [+0.085, +0.181]: **supported** (27/30) |
| b35 − b3 | +0.000 [+0.000, +0.000] / same: not supported (identical in 28 of 30 trajectories) | +0.004 [+0.001, +0.007] / +0.003 [+0.000, +0.006]: supported, with an 81-segment lower bound just above zero | +0.074 [+0.026, +0.118] / +0.065 [+0.021, +0.106]: **supported** |
| b35 − b5 | +0.011 [+0.004, +0.020] / +0.011 [+0.005, +0.020]: supported | +0.037 [+0.010, +0.068] / +0.038 [+0.013, +0.068]: supported | +0.072 [+0.025, +0.117] / +0.074 [+0.033, +0.115]: **supported** |
| b35 − me_ga | +12.717 [+12.144, +13.290] / +12.714: supported | +12.529 [+11.968, +13.101] / +12.521: supported | +8.579 [+8.026, +9.132] / +8.521: **not supported**, because me_ga is excluded by the miss rule |
| pair − greedy | +0.402 [+0.214, +0.625] / +0.404: supported | +0.509 [+0.310, +0.744] / +0.507: supported | +1.052 [+0.836, +1.270] / +1.004 [+0.800, +1.204]: **supported** |

## Reading
1. **Main result.** At the primary 50 ms budget, `b35` (restart density + elite recombination) beats exact pair search by +0.085 bit/s/Hz, winning 27 of 30 held-out trajectories. The result holds on both meshes.
2. **Both components contribute.** `b35` also beats each of its components, `b3` and `b5`.
3. **The development result replicated.**

   | Budget | Development (`b35` − `pair`) | Test (`b35` − `pair`) |
   |---|---:|---:|
   | 50 ms | +0.097 | +0.085 |
   | 100 ms | +0.126 | +0.125 |

4. **No gain at short budgets.** At 5 and 10 ms, `b35` does not beat `pair`, as on development data: there is no time for the restarts and recombination to act.
5. **Pair moves matter.** Exact pair search beats single-flip `greedy` at every budget, by 0.86 bit/s/Hz at 50 ms.
6. **`me_ga` (published-specification reimplementation) is far below every other method:**
   - 5.9 bit/s/Hz at 50 ms, below the all-OFF state.
   - At 100 ms it misses 2.0% of deadlines and is excluded by the frozen rule.
   - As declared before the run, this contrast compares against a published specification and is not a contest between strong methods.
7. **Mesh sensitivity is small next to the gains.**
   - Mean shifts are −0.04 to −0.07 bit/s/Hz for the pair-based methods at 50–100 ms.
   - These shifts are similar across methods, so the contrasts barely move between meshes.
   - Per-frame sensitivity is larger: in the P3 development audit, `b35` and `pair` changed order on 115 of 480 frames between meshes. The claim is therefore about averages over trajectories, not individual frames.

## Limits
- Free-space thin-wire NEC-2 model; one RIS geometry (64 elements); 2 users; 4 BS antennas; fixed all-OFF RZF precoder; simulation only.
- 161 segments is not shown to be converged. The 81/161 agreement is a consistency check, not convergence, and 241 segments falls outside the kernel's stated validity range.
- `b35` was selected on development data from the same distribution. This test is its first unbiased evaluation, but it is still within one distribution, not a different site or geometry.
- No numeric practical-significance threshold was frozen; effect sizes are reported as they are.
- Before any novelty claim, the combination must be checked against current literature (`docs/novelty-analysis.md`).
