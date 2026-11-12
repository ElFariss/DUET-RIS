# V2 combined b3+b5 development round: design declared before running (2026-11-07)

Why: in the no-L2 round, restart density (`b3`) beat `pair` at 10, 50 and 100 ms, and elite recombination (`b5`) beat it at 100 ms. The declared rule says a combined method needs its own development round. Screening is excluded after the fixed-L2 round. Development data only (`coupled_wire_dev_fine161`); no test data.

Methods:
- `pair`: control.
- `pair_plus_b0`, `pair_plus_b3`, `pair_plus_b5`: unchanged from the no-L2 round, rerun here because 3060-1 throughput fell about 22% between rounds.
- `pair_plus_b35`: `b0` with both components. Every third restart, once two elites exist, is a recombination; the others alternate density 18/64 and 0.5. This is the existing precedence in the code, not tuned.

Settings: 1/5/10/50/100 ms, the 10 registered seeds, 3060-1 core 3, single thread, `me_ga_paper` skipped.

Contrasts, per budget: b0-pair; each of b3/b5/b35 minus b0; each minus pair; b35-b3; b35-b5. 9 contrasts, Bonferroni within a budget, paired trajectory bootstrap with 10,000 resamples and seed 8251.

How this will be read, per budget:
- A method is an improvement candidate over `pair` only if its intervals against both `b0` and `pair` lie above zero.
- `b35` is preferred over a single component only if its interval against that component lies above zero. Otherwise the simpler qualifying method is preferred, `b3` before `b5`.
- If `b3` no longer beats `pair` here, the no-L2 finding did not replicate and is reported as such.
- This round chooses the method to carry towards a `matched_v2` freeze, but the freeze itself, the primary budget, the miss rule and the practical margin still need your decision. It cannot support a claim.
