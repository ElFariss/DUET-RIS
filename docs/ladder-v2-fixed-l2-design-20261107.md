# V2 fixed-L2 development round: design declared before running (2026-11-07)

Why: L2 ran to completion, but at 100 ms it rejected about 30.2 of 30.6 restarts and did only about 2 pair scans per frame. It compared a restart's single-flip value with a best result that had already had pair search, so this round tests a like-for-like screen. Development data only (`coupled_wire_dev_fine161`); no test data.

Methods, each identical to `pair_plus_b0` except for the screen:
- `pair`: control.
- `pair_plus_b0`: base with no screen.
- `pair_plus_b2`: after single-flip descent, a random restart gets pair search only if its value reaches the 50th percentile of earlier restarts' single-flip values in this frame. The first restart always passes. The all-OFF start is not in the history.
- `pair_plus_b2t`: the same with the 75th percentile.

Both percentiles are set here and not tuned. L2's subspace probe is dropped. `b3` and `b5` are not in this round.

Settings: 1/5/10/50/100 ms, the 10 registered seeds, 3060-1 core 3, single thread, `me_ga_paper` skipped.

Contrasts, per budget: b0-pair, each of b2/b2t minus b0, each minus pair. 5 contrasts, Bonferroni within a budget, paired trajectory bootstrap with 10,000 resamples and seed 8251.

How this will be read: the same rule as the no-L2 round. A screen is a candidate only if its interval against b0 lies above zero at a budget, and an improvement candidate over `pair` only if its interval against `pair` also lies above zero. If neither qualifies at any budget, screening is dropped from the method. This round cannot support a claim, and the practical margin is still unset.

## Forecast from a mechanism check, recorded before the round

`scripts/probe_l2_screen.py`, 60 evenly spaced dev frames, 64 uniform restarts each, no deadline, output `outputs/profiles/l2_screen_probe.json`:

| Measure | 50th percentile | 75th percentile |
|---|---:|---:|
| Share of restarts admitted | 0.500 | 0.283 |
| Frames where the best restart was admitted | 0.617 | 0.400 |
| Time used, relative to no screen | 0.630 | 0.500 |
| Mean final value, admitted / rejected | 13.375 / 13.219 | 13.449 / 13.241 |

The within-frame Spearman correlation between single-flip value and final value is only 0.077. Single-flip descent takes about 3.1 ms per restart and the pair stage about 5.2 ms, so a screen placed after descent can save only part of each restart.

Rough expectation, ignoring ties and restart-count effects: the chance of admitting the best restart, per unit time, is about 0.98 of no screen at the 50th percentile and about 0.80 at the 75th. **So this round is expected to show no gain at the 50th percentile and possibly a loss at the 75th.** The round still decides, because this estimate ignores how the deadline and history size behave at short budgets.
