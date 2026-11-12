# V2 no-L2 development round: design declared before running (2026-11-07)

Why: in the cumulative ladder, L2 screening lowered rate, and L3 to L6 were only measured on top of it. Development data only (`coupled_wire_dev_fine161`); no test data.

Methods, each identical to `pair_plus_b0` except for the one named component:
- `pair`: control.
- `pair_plus_b0`: L1 with reduced overhead: no repeated single-flip scan, no full sort per pair scan, deadline reserves set from a smoke run, and no second verification inside the controller (the benchmark rescores every returned action inside the timed section, as for `pair`).
- `pair_plus_b3`: restart density alternating 18/64 and 0.5.
- `pair_plus_b4`: all-OFF escape as in L4 (tabu non-improving pair moves and second-user tie-break) at every basin. The escape counter resets only on a new basin best. In L4 it reset on any improvement of the current state, which a smoke run showed could hold one basin for the whole deadline (1 restart in 50 ms). This is a fix to the mechanism, found from behaviour on 3 frames, not from comparing rates.
- `pair_plus_b4o`: the same escape, in the first basin only. Added because L4 flattened from 50 to 100 ms, which may mean escape moves crowd out restarts.
- `pair_plus_b5`: elite recombination every third restart.
- `pair_plus_b6`: cross-frame elite memory.

Settings: 1/5/10/50/100 ms, the 10 registered seeds, 3060-1 core 3, single thread, `me_ga_paper` skipped. Parameters reuse the ladder values and are not tuned here.

Contrasts, per budget: b0-pair, each of b3/b4/b4o/b5/b6 minus b0, each of those minus pair. 11 contrasts, Bonferroni within a budget, paired trajectory bootstrap with 10,000 resamples and seed 8251.

How this will be read: a component is a candidate only if its interval against b0 lies above zero at a budget. It is an improvement candidate over `pair` only if its interval against `pair` also lies above zero. If none does, the no-gain stop rule applies. If more than one qualifies, a combined method needs its own later development round. This round cannot support a claim, and the practical margin is still unset.
