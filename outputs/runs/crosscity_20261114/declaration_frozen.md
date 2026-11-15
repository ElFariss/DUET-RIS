# Cross-city held-out search test for Paper A: pre-run declaration (2026-11-14 WIB)

**Status:** FROZEN once its SHA-256 is written to `docs/crosscity-search-declaration-20261114.freeze.sha256`.
At the freeze no cross-city dataset existed on labkc-comm3 or labkc-comm2: no workspace, READY file, channel, label or
result for Munich, Maastricht, Utrecht or Berlin had been created or read (checked 2026-11-14 07:26Z). Sections 1–11 are
never changed afterwards. Results are appended under "Results" only, each with its time.

**Parents (not edited):**
- `paper-b-neural-pair-search/docs/bench-ris-relevant-v3-search-declaration-20261113.md`: the Rotterdam v3 test,
  frozen sha256 `391775b1…e156`. Methods, code, clock, miss rule and statistics are taken from it unchanged unless §10
  says otherwise.
- `GeoRIS-Bench/docs/bench-ris-relevant-v3-crosscity-20261114.md`: the cross-city scope declaration (being written by the
  scope agent). It defines the four city datasets, their per-array check and `READY.json`.

**Sealed maps:** Berlin and Utrecht were sealed in every earlier declaration. They are opened here by the user's decision
of 2026-11-14 (relayed by the coordinating session), as held-out cities for this one test only. No method, parameter or
rule below was chosen with any cross-city data.

## 1. Purpose

Test, on four cities that played no part in development, whether the Rotterdam v3 ranking of the search methods under a
CPU deadline holds: b35 against pair, ME-GA and NSGA-II, and pair against the two evolutionary baselines. This is Paper A's
held-out generalisation result.

## 2. Data

**Cities:** Munich, Maastricht, Utrecht and Berlin, built with the v3 rules by the scope agent. Each has 48 trajectories,
16 frames and arrays 64 / 128 / 256.

| Part | Indices | Use here |
|---|---|---|
| check | 0000–0011 | the scope agent's per-array check; here only a development smoke (§8), never reported |
| **test (SEALED)** | **0012–0047** | the one test pass per city and array |

**Readiness:**
- Each city signals readiness with `<workspace>/<city>/READY.json`.
- A city × array is eligible only if that file states, for that array, that the check PASSED.
- The reading must be unambiguous. Otherwise the city × array waits until this session has recorded its reading under
  "Results", without changing any rule.

**Data integrity:**
- The package of each city is verified with `sha256sum -c` on the machine that runs it, before any timed call.
- The hashes are recorded in each `run_record.json`.

**Test trajectories:**
- These are the trajectory groups of that city and array in the channel file whose index is 12–47. Their ids must match
  `<city>-<tag>-NNNN`, with one tag per city.
- Missing indices (generation or trace failures) are reported, not replaced.
- `frame_row_index` = 16 × (position of the trajectory in the sorted test list) + frame position.

**Frame exclusion:**
- The v3 rule: a frame with a served user whose direct and all-OFF RIS rows are exactly zero is flagged. Flags are
  computed untimed and every method skips flagged frames.
- Any stricter rule in the cross-city scope declaration is applied as well and reported.

## 3. Methods: frozen, identical to the Rotterdam v3 test

| Name | Code name | Notes |
|---|---|---|
| single-flip | `greedy` | `coupled_search.search`, `matched_v1.json` `medium` |
| pair | `pair` | same |
| ME-GA | `me_ga` | `me_ga.search_coupled`, published-spec parameters, one memory per trajectory (C3), as in v3 |
| NSGA-II | `nsga2` | `nsga2.py` A2 module; P = 20, pc = 0.9, uniform crossover, 1/N mutation, all-OFF + 19 random; tuned on RIS-relevant v1 train only (`NSGA2_READY.json`, 2026-11-13T01:21:53Z) |
| b35 | `pair_plus_b35` | `pair_plus.search`, exact full pair scan, restart densities and elite recombination |

**Not run:** b3, b5, M0 and the learned head, which are not needed for this test.

**Source hashes** (full sha256; checked by the runner; identical to the v3 test trees on both machines, verified
2026-11-14 07:26Z):
- `coupled_search.py` `0b4d863c…4423`, `search.py` `7bc38bb1…d633`, `me_ga.py` `7858402e…ed48`
- `pair_plus.py` `a8de7966…d2d6`, `pair_select.py` `a957d943…db37`, `hybrid/operator.py` `d0e34850…7e13`
- `search_adapter.py` `af5f5121…0886`, `nsga2.py` `fec0a3d7…7260`, `search_adapter_nsga2.py` `3d6c16b1…62d8`
- `matched_v1.json` `77f880fa…2d88`

**Method order in every process:** greedy, pair, me_ga, nsga2, pair_plus_b35.

## 4. Protocol

- **Arrays:** **64 and 128 only.** 256 is not tested, because under the 0.5% miss rule every declared contrast is
  untestable there. On the Rotterdam v3 test (search clock):
  - b35 missed in 55.3% of calls at 50 ms and 2.0% at 10 ms;
  - pair missed in 3.8% at 50 ms and 1.4% at 10 ms;
  - ME-GA missed in 100% at 10 ms.

  So b35 and pair are excluded at both budgets, which excludes every contrast H1, H2, H5, C6 and C7.
- **Budgets:** 10 and 50 ms; **50 ms is primary.**
- **Seeds:** 7, 19, 43, 3, 11, 23, 31, 59, 67, 83. Search seed `seed × 1000003 + frame_row_index` (C2).
- **Clock:** `search_elapsed_ms` decides: evaluator build plus search, stopped before rescoring (C5). `elapsed_ms` is a side
  table.
- **Rescoring:** every action is rescored outside the clock; a difference above 1e-7 stops the run.
- **Miss:** `search_elapsed_ms > budget` or the solver's own flag. Misses stay in the means.
  - **0.5% rule:** a method whose miss fraction in a cell exceeds 0.5% is excluded from that cell's contrasts.
  - A cell is (unit, array, budget), where the unit is a city or the pool.
  - Misses never trigger a retune or a rerun.
- **Warm-up:** one discarded 20 ms warm-up call per method and process.
- **Arrays:** each array size is a separate experiment and is never pooled across sizes.

## 5. Statistics and contrasts

**Unit:** the trajectory. Unflagged frames and seeds are averaged within a trajectory; methods are paired on the same
trajectories, frames and seeds.

**Bootstrap:** paired, over trajectories, 10,000 resamples, seed 8251, percentile intervals. The code is the unchanged
`analyze_bench_search.py --clock search`.

**Family:** five contrasts, Bonferroni over the five, so each interval is at 1 − 0.05/5 = 99%:

| ID | Contrast |
|---|---|
| H1 | b35 − pair |
| H2 | b35 − ME-GA |
| H5 | b35 − NSGA-II |
| C6 | pair − NSGA-II |
| C7 | pair − ME-GA |

**Rules** (for every unit, array and budget):
- **PASS:** the 99% interval lies entirely above 0, and neither method is excluded by the miss rule.
- **Excluded evolutionary baseline:** for H2, H5, C6 and C7, if the evolutionary method (ME-GA or NSGA-II) is excluded,
  the verdict is "not testable at this budget".
- **Excluded b35 or pair:** if b35 or pair is excluded, the verdict is "FAIL (excluded by miss rule)".
- **Interval wholly below 0:** reported as "below 0".

**Units:**
- **Pooled (confirmatory):** at 50 ms, separately for 64 and 128, over all cities whose test for that array completed
  before the cutoff (§9). Rows of those cities are pooled and the bootstrap resamples trajectories over the pool (as the
  natural declaration pooled its three maps). The miss rule uses the pooled miss fraction.
- **Per city (secondary):** the same 99% intervals and labels per city. The number of cities in which each contrast
  passes is reported. Per-city results carry no family-wise claim across cities.
- **10 ms:** secondary, both pooled and per city.

**Descriptive** (unadjusted 95%, no claim): b35 − single-flip and pair − single-flip.

**Primary metrics** (identical to Paper B; `metrics_bench_search.py`), for every method, array, budget, city and the pool:
- **M1:** worst-user SE `min_k R_k` in bit/s/Hz, under the stored all-OFF RZF precoder, trajectory-averaged.
- **M2:** `search_elapsed_ms`, mean and p95.
- **M3:** the budget, plus the candidate evaluations per call (mean, median, p95).

Miss %, intervals and verdicts are secondary.

## 6. Timing layout (declared)

**One process per city × array, pinned to one physical core with its SMT sibling idle of our jobs.** All five methods of
that city × array run in that process, on that core.

| Array | Machine | Slots: timing CPU (idle sibling) | Sampler |
|---:|---|---|---|
| 128 | labkc-comm3 | 4 (10), 5 (11) | CPU 0, logs 4, 5, 10 and 11 |
| 64 | labkc-comm2 | 4 (10), 5 (11) | CPU 0, logs 4, 5, 10 and 11 |

**Hardware** (checked 2026-11-14 07:26Z): both machines are AMD Ryzen 5 5600 6-core with SMT pairs 4↔10 and 5↔11.

**Software:** Python 3.12.3, numpy 2.2.6, scipy 1.15.3, h5py 3.16.0 on both, with single-threaded BLAS.

**Placement:**
- Each array size runs on one machine, so pooled and per-city contrasts never mix machines.
- Within a machine the two slots share the L3 cache and memory bandwidth. This is identical for all methods of a city ×
  array, and contrasts are always within one process.

**Queue:**
- Per machine, city × array units start in the order in which their eligibility (§2) appears. Ties go alphabetically.
- A unit starts on the first free slot whose core and sibling show < 10% busy over 30 s.
- If our dataset build occupies a slot's core, the unit waits. The sampler records all four cores; load from other jobs
  is reported with its time range and not rerun.

**Fallback:**
- If labkc-comm2 is down when a 64 unit is due, or dies during it and is not back within 30 min, the 64 units run on
  the comm3 slots after the 128 units, and the reverse for comm3.
- A unit that moves machine is rerun completely; rows from two machines are never mixed, and partial rows are kept on
  disk but not analysed.

**Not used:** labkc-comm1.

## 7. Sealing and one-shot rule

The new adapter `search_adapter_crosscity` accepts only the four cities. It opens the test split for a city × array only
when three conditions hold:
1. the caller gives this declaration's freeze token;
2. that city's `READY.json` states that the array's check PASSED;
3. the per-unit guard `TEST_ONCE_<city>_a<array>.json` does not name a different output directory.

**One-shot:** each city × array test runs **exactly once**. An infrastructure failure (reboot, killed process) may be
resumed with identical code, data, arguments, machine and core, keeping completed rows; the interruption is reported. No
result triggers a retune or a second pass. Rotterdam is not part of this test.

## 8. Order

1. **Before any data:** freeze this declaration, stage the code on both machines and check the hashes.
2. **Development smoke** (not reported): on the first eligible city per machine, run one check trajectory, frames 0 and 8,
   seed 7, both budgets, all five methods, to confirm the paths and data layout. It reads only the check split.
3. **Test:** each eligible city × array is tested once, through the queue (§6), with the analysis of §5 per city.
4. **Pooled analysis** at the cutoff, or when all eight city × array units are done.
5. **Writing:** summaries go to `paper-a-ris-physics/outputs/runs/crosscity_20261114/`, in the schema of
   `rr3_test_summary.json`.

## 9. Cutoff

**2026-11-15 09:00 WIB (02:00 UTC).** A city × array test not complete by then is **"not completed"**: its partial rows are
not analysed and it is excluded from the pool. The pooled analysis uses only completed units and lists the others.

## 10. Changes from the Rotterdam v3 declaration, with reasons

1. **Data:** four held-out cities (36 test trajectories each) replace Rotterdam. Berlin and Utrecht are unsealed by user
   decision (preamble).
2. **Methods:** greedy, pair, ME-GA, NSGA-II and b35 only (no b3, b5, M0 or head), because this test is about the search
   methods.
3. **Arrays 64 and 128 only** (§4).
4. **Budgets 10 and 50 ms only.**
5. **Family:** H1, H2, H5, C6 and C7 (five contrasts) replace H1–H5, with H3 and H4 dropped and C6 and C7 added.
   The family size is the same.
6. **Units:** per city and pooled; the pool is confirmatory.
7. **Timing:** four timing cores, two per machine, one array size per machine (§6).
8. **Cutoff** (§9).

## 11. Known limitations

- **Placements:** a few RIS placements per city, as set by the cross-city scope declaration.
- **Shared package:** the two timing slots of one machine share a CPU package.
- **NSGA-II:** tuned on Rotterdam v1 train; it is not re-tuned per city, by design.
- **Mesh sensitivity:** not tested.

---

## Results

(Appended after the freeze only.)
