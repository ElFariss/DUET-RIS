# ME-GA / GA-RISC: a reimplementation from the published specification

Source: F. Zardi, P. Oliveri, A. Massa, "Memory-Enhanced Dynamic Evolutionary Control of Reconfigurable
Intelligent Surfaces", IEEE TAP 2024, arXiv 2309.04353 (Sect. III, Fig. 2, Sect. IV parameters).
Code: `src/atomwise_ris/optimization/me_ga.py`. Tests: `tests/test_me_ga.py`.

This is a **reimplementation from the published specification**, not a reproduction. The paper publishes no code,
no stagnation threshold, no selection/crossover/mutation operator definitions, no memory size or eviction rule, and
**no numbers comparable to ours** (its results are throughput curves for a 2025-atom, 3-bit RIS with a per-step ZF
precoder on a different channel). It therefore cannot be validated numerically against the paper; only its stated
mechanism can be checked, and the unit tests do that.

## 1. What was read

* arXiv HTML text of the whole paper, and the arXiv TeX source (read as data, never executed or compiled; the
  figure files were not rendered because rendering EPS is executing PostScript).
* Fig. 2 (flowchart): the EPS is a poppler `pdftops` export, so its node labels and the geometry of its arrows were
  read from the PostScript text, not rendered. Nodes: `INIT`, `Mutation and Crossover operators`, `Population Replacement`,
  `Effectiveness Self-Evaluation`, a diamond `Scenario changed?` with `Yes` to `Memory Remembering` and `No` to `Memory Learning`,
  a `MEMORY` cylinder attached to both memory boxes, and both memory boxes looping back to Mutation and Crossover.
  There is no fitness-evaluation box and no stop box in the drawing; those are only in the text. The arrow topology is
  inferred from coordinates (moderate confidence); the box order matches the text exactly.
  The diamond label ("scenario changed?") is not the text's criterion (sign of Theta); I follow the text: Theta >= 0 Learning,
  Theta < 0 Remembering, and Yes = Remembering = Theta < 0.
* Reference [32] is A. Massa, M. Donelli, F. G. B. De Natale, S. Caorsi, A. Lommi, "Planar antenna array control with
  genetic algorithms and adaptive array theory", IEEE TAP 52(11), 2004 (with [31] Caorsi et al., MOTL 36(4), 2003,
  "learned genetic algorithm"). I identified them from the bibliography but could not read either; the GA operators
  below are therefore **assumptions**, not transcriptions of [32].
* The TeX equations are unlabelled; the equation numbers below are counted in source order and agree with the
  numbering in the task spec: (7) cost Phi = 1/T_worst, (10) ZF, (11) dynamic problem, (12) random initial population,
  (13) adaptive rho/psi, (14) variance, (15) Theta, (16) beta, (17) kappa, (18) Delta s.

## 2. Corrections to the spec I was given

1. **Theta series.** The TeX *formula* for s_best(v)/Phi_best(v) is `argmin over gamma AND v~=1..v` (a running minimum), although the
   prose calls it "the v-th iteration best". With the running minimum Phi_best is non-increasing, so every term of Eq. (15) is <= 0, Theta <= 0
   always, Memory Learning (Theta >= 0) is reachable only at exactly 0, and the two-branch design is dead. So the TeX shows the running minimum
   in the formula but contradicts itself in the prose and in its own Fig. 4a (which I could not read; the claim that Fig. 4a shows both signs comes from the
   task spec). I used the per-iteration best for Theta and for the stored individual, as instructed, and kept the running best only for the output and the stagnation
   test. This is a judgement call and the first sensitivity item (`theta_series='running'` reproduces the literal formula; it never stores).
2. **"Worst individual".** The TeX defines s_worst as argmax over gamma and v~=1..v (all-time worst), which is not in the population and cannot be substituted. I use the worst individual of the current population.
3. **Theta_max** in both Eq. (16) and Eq. (17) is the maximum over the iterations so far (TeX: `max_{v~=1..v} Theta_v~`), as in the spec; this is what makes Eq. (17) ill-defined (see table).
4. Population replacement is listed in the text as one of the "non-conventional Genetic operators" applied "to leverage on the memory", so "GA-RISC = standard GA without memory-based operators" is ambiguous about replacement (table row 19).

## 3. Decision table

Sensitivity column: **Y** = a sensitivity test is warranted before any claim rests on the choice; **N** = not needed. Nothing below was tuned
on rate results; every default was fixed before any run.

| # | Gap | Decision (default) | Reason | Paper location | Sens. |
|---|-----|--------------------|--------|----------------|-------|
| 1 | Theta series (running-min vs per-iteration) | Per-iteration best of S_v for Theta (and for the stored individual); running best for output and stagnation | Running-min makes Theta <= 0 and Learning unreachable; contradicts "v-th iteration best" and Fig. 4a | Eq. (15), definition of s_best(v), Fig. 4a | **Y** (`theta_series`) |
| 2 | Phi | Phi = 1/max(T_worst, 1e-12); T_worst = our exact min-user rate | Eq. (7); guard only for a zero rate | Eq. (7), (11) | N |
| 3 | Theta for v <= W | Index 0 = best of S_0; terms with v - v~ < 0 dropped (window truncated, weights 2^-v~ unchanged) | Phi_best(v - v~) undefined below 0; minimal fix | Eq. (15) | N |
| 4 | beta at Theta_max <= 0 | beta = beta_max * Theta/Theta_max in [0, beta_max] for Theta >= 0; **0 when Theta_max = 0** (0/0) | Literal Eq. (16) is a valid probability when Theta_max > 0 | Eq. (16) | N |
| 5 | kappa (Theta < 0) | **Deviation.** kappa = kappa_max * abs(Theta) / max abs(Theta seen), clipped to [0, kappa_max]. Literal Eq. (17) is negative if any earlier Theta > 0, > kappa_max if all earlier Theta < 0, 0/0 at Theta_max = 0 | A probability must lie in [0, kappa_max]; magnitude normalisation is the symmetric reading of Eq. (16)/(17) | Eq. (17) | **Y** (`kappa_rule` = `negative_extreme`, `literal_clipped`) |
| 6 | sigma for integer labels | Normalised binary variance: mean per-gene p(1-p) / 0.25, so it lies in [0, 1] and sigma_max = 1 (B = 1) | Eq. (14) on raw labels is unbounded; the paper's sigma_max = 1 only makes sense for a normalised variance | Eq. (14), Sect. IV | N |
| 7 | Which population sigma drives what | rho, psi use sigma of the population the operators act on (S_{v-1} after replacement; S_0 at v = 1); nu uses sigma of S_v | Eq. (13) needs sigma_v before S_v exists | Eq. (13), nu_v | N |
| 8 | Order of operations | Evaluate S_0 -> [selection+crossover+mutation -> evaluate S_v -> replacement (nu) -> Theta -> Learning or Remembering -> stop test] | Fig. 2 box order and the text; fitness is needed before selection so S_0 is evaluated first | Fig. 2, Sect. III | N |
| 9 | Selection | Binary tournament on Phi | The paper names no selection step, but a GA has none otherwise; scale-free, no transform of a cost | Sect. III ("Genetic operators", [32]) | **Y** |
| 10 | Crossover | One-point, probability psi_v per parent pair, two children | Textbook default; [32] not readable | Sect. III, Eq. (13) | **Y** |
| 11 | Mutation | Gene-wise bit flip with probability rho_v per gene (B = 1) | Standard meaning of a mutation probability; individual-wise is the alternative | Eq. (13) | **Y** |
| 12 | Elitism | None (`elitism=0`; option exists) | None stated; with elitism the iteration best is monotone and Theta <= 0 again | Sect. III | **Y** (`elitism`) |
| 13 | Fitness of replaced and restored individuals | They are evaluated when inserted (counted, inside the deadline) so every member entering the next selection has a known Phi | Without it the inserted individuals cannot be ranked; the alternative (treat as worst) defeats their purpose | Fig. 2 | N |
| 14 | Psi size and eviction | 12 entries, newest first, duplicates collapsed, oldest evicted (the repo's `Memory`) | Not stated; size-matched to the existing methods | "memory pool" | **Y** (`capacity`) |
| 15 | What is stored | The iteration-best individual of S_v (prose), not the running best | Prose of Learning step | Sect. III | N |
| 16 | "Best individual of Psi" at a new time step | **Inference.** Entries are rescored on the current channel (batched, counted, timed as memory); the best current-channel score is restored. Scores are cached for the rest of the step; entries stored in this step reuse their known score | Stored values belong to an old channel, so "best" is only meaningful after rescoring; the paper does not say how it is judged | Eq. (17), Sect. III | N |
| 17 | Restoring | Replaces the worst individual of the current population unconditionally, with probability kappa; no-op when Psi is empty | Literal text | Eq. (17) | N |
| 18 | Memory use at initialisation | None: S_0 is random (Eq. 12); memory enters only through Remembering | Literal | Eq. (12) | N |
| 19 | GA-RISC | Same loop with Learning/Remembering off and Psi never read or written; adaptive rho/psi, Theta and population replacement stay | The paper's claim is about memory; isolating Psi changes the least | Sect. IV, Figs. 4-5 | **Y** (`ga_risc_replacement`) |
| 20 | Stagnation threshold delta | Default `None` (uses published V = 100 cap only, since the paper gives no delta value). Optional `stagnation_delta`: test on running best: abs(Phi_best(v) - mean over v~=1..W of Phi_best(v - v~)) < delta, checked from v = W. | Paper gives no value; arbitrary delta stops early before memory events occur; None uses the published V cap | Sect. III stop rule | **Y** (`stagnation_delta`, `stagnation_stop`) -- strongly affects run length |
| 21 | Stagnation applies to | Optional for all three methods; disabled by default because the paper does not give δ. When supplied, the paper's absolute cost-difference test is used | Avoids inventing a convergence tolerance that controls runtime and may prevent memory events | Sect. III | N |
| 22 | Output | Best individual ever evaluated in the step (running best), not the last iteration's best | The TeX output is s_best(v) with running-min definition; also what "keeps best so far" requires under a deadline | Sect. III | N |
| 23 | Odd Gamma, B > 1 | Odd Gamma handled; only B = 1 (binary) implemented | Declared adaptation | Sect. IV | N |
| 24 | Deadline | Evaluation in chunks (first an 8-individual calibration chunk after one mandatory single evaluation); a chunk is started only if its predicted end is before the deadline; a chunk ending after it is discarded and not counted; best-so-far is returned. `me_ga_paper` has no deadline | `_search_population` style, `_score_completed_by_deadline` | n/a | N |

## 4. Declared adaptations

B = 1 not 3; 64 elements not 2025; a fixed all-OFF RZF precoder rather than a per-step ZF pseudo-inverse (Eq. 10); our exact multiport evaluator;
population and iteration counts as in the paper (Gamma = 100, V = 100, W = 3, rho in [0.02, 0.06], psi in [0.6, 0.95], nu_max = kappa_max = beta_max = 0.2, sigma_max = 1).
A consequence worth stating: with ~100 us per individual on the coupled evaluator, Gamma = 100 costs about 10 ms per generation, so at the 10 ms budget `me_ga` cannot finish even the initial population.

## 5. Method IDs and benchmark wiring

| ID | Behaviour |
|----|-----------|
| `me_ga` | deadline-truncated, best-so-far kept, memory on |
| `ga_risc` | same, Learning/Remembering off, memory never touched |
| `me_ga_paper` | full Gamma x V by default; an explicitly configured absolute stagnation delta may stop it earlier; no deadline cut; true runtime in `elapsed_ms`; rows carry `deadline_missed = null` and `deadline_applicable = false` (a reference, reported separately) |

* `search.search(...)` and `coupled_search.search(...)` dispatch these three names to `me_ga.py` and ignore `config`, `legacy`, `policy`, `scaling`, `initial` (not part of the matched step limits). They are in `ME_GA_METHODS`, **not** in `GA_METHODS`, so `variant_spec` rejects them and `matched_v1.json` and `protocol_methods` are untouched. Existing methods are unchanged (golden regression test).
* Both benchmark scripts gain `--extra-methods me_ga,ga_risc,me_ga_paper` (default empty). It requires an explicit `--output`, is refused for `--split test`, and coupled mode is spatial only. Protocol validation is untouched.
* Memory Psi is a `Memory` object per (method, seed), created fresh whenever the trajectory changes (`Memory.enter` in `benchmark.py`; the dict reset in `benchmark_coupled.py`), mutated in place by the controller so it persists across frames. `should_store_memory` is False for the ME family so the script's post-hoc "store the final bits" never overwrites Psi. All Psi work (store, rescoring, restore) happens inside the controller call and is inside its elapsed time and `breakdown['memory']` / `breakdown_ms['memory_ms']`.
* Seeds: `numpy.random.default_rng(seed)`; the draw for the memory event is made even for GA-RISC so `me_ga` and `ga_risc` share a random stream until the first memory event.

## 6. Evaluation cost (no strawman)

Coupled population scoring (`CoupledPopulation`): the stack of 64x64 systems is solved with `np.linalg.solve` and 2 right-hand sides (not inverted); children within 24 flips of
the previous iteration's best use a vectorised exact rank-m Woodbury update (padded with identity rows, exact no-op), the rest use the batched solve; `'auto'` pays for the base inverse only when at least 12 children qualify.
`np.linalg.inv` on the stack is kept as the reference. All paths are tested against `CoupledNetwork.state(bits).field` to rtol 1e-9. The specular evaluator is one batched contraction.

## 7. Historical smoke output (superseded, NON-RESULT)

Not a performance comparison. These measurements used the earlier assumed relative `delta_rel=1e-3` stopping threshold. The live implementation now defaults to no early-stop delta and follows the stated V cap; these timings and generation counts do not describe the current default. Raw historical file: external scratchpad `smoke_nonresult.json` (historical non-result).
3 validation frames per physics, 5 repetitions, one pinned core, `OPENBLAS_NUM_THREADS=1`, on a laptop with load average ~5 (timings are indicative, not benchmark grade).

Measured microseconds per individual:

| evaluator | engine | batch 25 | batch 100 |
|-----------|--------|---------:|----------:|
| coupled | batched solve (default) | 107 | 101 |
| coupled | stacked inverse (reference) | 357 | 322 |
| coupled | Woodbury, children ~10% flips from base | 15 | 12 |
| coupled | auto | 15 | 12 |
| specular | batched contraction | 4.7 | 3.9 |

Complete generations that fit in a budget (median, min-max over 15 runs; `me_ga`, fresh Psi):

| budget | coupled generations | coupled evaluations (median) | deadline misses | specular generations |
|-------:|--------------------:|-----------------------------:|----------------|---------------------:|
| 10 ms | 0 (initial population not even finished) | 34 | 0/15 | 3 (stagnation stop) |
| 50 ms | 3 (1-3) | 403 | 0/15 | 3 (stagnation stop) |
| 100 ms | 7 (3-10) | 816 | 0/15 | 3 (stagnation stop) |

Under that earlier setting, untimed `me_ga_paper` stopped after 6-12 coupled generations and 3-4 specular generations; none reached V = 100 or stored/restored. Those outcomes exposed the ungrounded stopping assumption and are retained only as historical implementation evidence. With the current default, `me_ga` ends at its complete-action deadline and `me_ga_paper` reaches the published V cap unless a caller supplies an absolute `stagnation_delta`.

## 8. Risks

* **Frozen-code hash.** `scripts/select_matched_budget.py::CODE_GLOBS` hashes `src/atomwise_ris/**/*.py`, `scripts/benchmark.py` and `scripts/benchmark_coupled.py`. This change edits or adds files in that set, so `frozen_code_sha256` of this working tree no longer equals the hash recorded for the frozen v1 run. The frozen test on 3060-1 is unaffected as long as nothing here is synced; do not sync or compare this tree against v1 provenance.
* Judgement calls with real influence: rows 1, 5, 9-12, 14, 19, 20.
* Timings here come from a loaded host; deadline misses of a few tenths of a millisecond occur occasionally and are reported, not hidden.
* Test environment: the project's `.venv` is absent. The suite was run with the system `python3` (3.14, numpy 2.4.3, torch 2.14 cpu; outside `requires-python`) and `.venv-em` (numpy 2.2.6) for the torch-free tests; `uv.lock` was not touched.
