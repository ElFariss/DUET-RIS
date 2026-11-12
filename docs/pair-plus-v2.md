# Pair-plus search ladder (V2 development implementation)

This document describes the development-only pair-search ladder implemented
in `src/atomwise_ris/optimization/pair_plus.py` and driven by
`scripts/benchmark_pair_plus.py`. It is an algorithm specification, not a
result or novelty claim. The methods are deliberately kept outside the
matched-v1 dispatchers so existing baselines are not changed.

## Common controller and timing contract

Each method starts with the all-OFF state as a feasible fallback, then
continues until its absolute `perf_counter_ns` deadline. Every restart,
single-flip scan, pair scan, memory rescore, exact candidate verification and
final returned-action rescore is inside the timed call. The development runner
starts its clock before constructing `CoupledNetwork`, and records network
preparation, search, and final full-channel rescore in `elapsed_ms`.

Candidate neighborhoods use `CoupledNetwork.moves`, `moves_subspace`,
`flip`, and the full `score` evaluator. A batch scan is eligible only if its
complete call finishes by the deadline; a late scan is discarded. The chosen
candidate is then reconstructed with `flip` and its score recomputed through
`score`. The returned best action receives a final direct full-network rescore.
The runner records misses when total row time exceeds the budget or a scan
finishes late. The mandatory all-OFF score is retained as a valid fallback
even when setup leaves too little time for a neighborhood scan.

L4-L6 optimize the max-min user rate first. When two candidates have rates
equal within `1e-12`, L4 and later prefer the larger second-user rate among
the first eight tied moves (ordered by index), then the lower index for
deterministic resolution. This bounds the extra field updates needed for ties.
The tie-break is computed from the two-user, two-stream `CoupledNetwork` field.
An evaluator without that shape has no second-user tie-break and remains
ordered by max-min score and index.

## Ablation ladder

| Method | Added component | Exact rule |
|---|---|---|
| `pair_plus_l1` | Anytime ILS | Descend by the best improving single flip, then the best improving pair flip; after reaching a 2-opt basin, draw a uniform binary restart and repeat until the deadline. Retain the best state across restarts. |
| `pair_plus_l2` | Screened restarts | After single-flip descent, basins more than 0.50 bit/s/Hz below the current best receive an exact pair probe over the eight best single-flip anchors. Only a probe within 0.50 of the incumbent earns the full pair scan. |
| `pair_plus_l3` | Predeclared restart densities | Alternate Bernoulli restart densities `18/64` and `0.5`. The density schedule is fixed before a run and does not learn from validation outcomes. |
| `pair_plus_l4` | Tabu escape | At a pair-local optimum, accept the best non-tabu pair move even if its max-min score decreases, then resume single/pair descent. A pair is tabu for five escape moves; allow at most eight escape moves per basin. Exact max-min ties use the second-user rule above. |
| `pair_plus_l5` | Elite recombination | Keep at most eight distinct local optima. Every third restart, when two elites exist, create a child by independent per-bit inheritance from two distinct elites, then optimize it with the preceding L4 rules. |
| `pair_plus_l6` | Cross-frame memory | Keep four distinct patterns per trajectory. On each frame, rescore at most four prior patterns on the current network using `flip` from the all-OFF reference, and skip patterns requiring more than 20 flips. Values never carry across frames. The current-frame elite can then update the store. |

L2’s 0.50 screen and eight-anchor probe, L3’s densities, L4’s tenure/escape
limits, L5’s elite capacity, and L6’s bounded rank-k update are explicit
engineering choices to be assessed on development trajectories. They are not
claimed optimal. L6 uses the current all-OFF state as its Woodbury reference;
the 20-flip cap bounds the update cost and causes explicit skip counts.

## Development runner and provenance

After the C1 mesh-resolution stop rule (81→161 changed selected actions), every
optimization result must use the registered, source-bound 161-segment
development set. The default input is `data/processed/coupled_wire_dev_fine161`;
a normal run requires its complete `generation_status.json` readiness and
physics manifest, all 480 verified frames, and per-file hashes. The fine-mesh
readiness checks are separate from the baseline two-load physics gate. There
is no test-split argument.
The runner writes a new JSONL and JSON metadata sidecar; existing outputs are
preserved. The metadata records source, physics-gate, protocol, MLP checkpoint,
scaling, readiness and frame-manifest hashes, budgets, seeds, selected indices,
timing scope and algorithm parameters. Each row records its exact bit vector,
score, trace, evaluation count, elapsed time, miss flag and component counters.
`--fine-smoke --indices i[,j,k]` is capped at three individually verified fine
development frames while generation is incomplete. `--coarse-smoke
--indices i[,j,k]` is capped at three coarse-81 frames and is diagnostic only.
Both are tagged as smoke non-results and cannot support selection, tuning
claims, or paper conclusions. Full coarse comparisons and unbounded partial
fine runs are rejected. Coarse 81-segment data cannot serve as the V2
optimization reference after the C1 drift finding.

The timed comparison contains `greedy`, the unchanged `pair` baseline,
deadline-limited `me_ga` and `ga_risc`, the frozen matched MLP comparator, and
all six pair-plus levels. The full `me_ga_paper` run is written separately
without a deadline and has `deadline_applicable: false` and
`deadline_missed: null`; it is never mixed into budget-matched summaries.
`--skip-me-ga-paper` omits that potentially long reference and must be
disclosed if used.

This runner does not select a V2 budget or freeze a test protocol. Dev
trajectories are development data. No `coupled_wire_test_v2` path is accepted,
and no held-out result is produced by this implementation.
