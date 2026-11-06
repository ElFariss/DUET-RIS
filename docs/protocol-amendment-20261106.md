# Matched protocol amendment — 2026-11-06

The original registration is preserved byte-for-byte at
`configs/experiments/archive/matched_v1-registered-20261106.json` (SHA-256
`2e2fc77e8fcb8472fc25c5b2b76d612dd29b1adebe53354527485110e5dc7514`). This amendment was
made before inspecting matched-test outcomes. Whether test frames had started generating was
unknown at amendment time, so the amended protocol makes no claim that generation had not begun.
The amendment does not authorize consulting test results for method selection.

The method IDs ending in `_ga` are kept for checkpoint and runner compatibility. They identify
ranked iterated-local-search hybrids that share a search skeleton; they are not population genetic
algorithms. A separate `population_ga` baseline is included in both experiments with population 12,
tournament size 2, crossover probability 0.25 and a mutation that chooses one or two distinct bit
indices with equal probability. Although its controller can accept remembered patterns, the
registered benchmark supplies none: initialization is the all-OFF pattern plus seeded random fill.
It does not rank, refine or update memory. The other baselines (`greedy`, `pair`, `random`) also
receive no remembered patterns in either experiment. The population baseline is not part of the
shared-step ILS contrasts. It is compared with
`analytical_ga` as a separate primary-budget contrast.

The shared ILS variants keep the same step sequence and configuration within each scene. The
registered primary remains `medium`; small and large are validation sensitivity settings. The
`attention_no_physics_ga` ablation removes explicit policy physics features while retaining
analytical flip gains, so it supports only a claim about *additional physics features*. It does not
isolate analytical physics from the full controller. Two contrasts were added: attention versus MLP,
and attention versus the no-extra-physics-features ablation. Results for these contrasts are part of
the same inferential family.

## Statistics implemented by the analysis script

The unit is the trajectory: average seeds and frames within each trajectory before comparing
methods. The script draws paired trajectory-bootstrap resamples with one shared index matrix for all
contrasts, using 10,000 resamples and seed 8251. It reports Bonferroni simultaneous percentile
intervals with family-wise level 95% across all registered contrasts. Practical decisions use those
intervals directly: improved if the whole interval is above `+0.015`, deteriorated if it is below
`-0.015`, equivalent if wholly inside `[-0.015, +0.015]`, otherwise inconclusive. A separate
two-sided centered-bootstrap p-value tests zero difference and receives Holm adjustment across
contrasts. No Holm-adjusted p-value is converted into a confidence interval.

These are trajectory-level bootstrap approximations, not exact finite-sample guarantees. Their
interpretation assumes held-out trajectories are exchangeable independent sampling units. With 30
trajectories per scene, tail resolution and coverage can still be limited; seed-level trials and
frames do not increase the independent sample size. A result should not be upgraded based on the
zero-null p-value when its simultaneous interval does not clear the practical margin.

The `0.015 bit/s/Hz` value is a practical engineering threshold. It came from a mesh-doubling
observation and is **not** a general mesh-accuracy bound, nor evidence that all returned actions are
resolved to that tolerance. In the coupled experiment, a statistical improvement is numerically
unresolved without a fine-mesh audit selected before test actions are scored at fine resolution.
That audit must recompute every primary-budget returned action (all methods, seeds, frames and
trajectories) using 81- and 161-segment models, and report the maximum absolute rate difference
against a resolution criterion declared before the audit. Missing or failed audit evidence withholds
the coupled improvement claim; it does not change the statistical estimate or tune the methods.
For the specular experiment, the same margin is borrowed from coupled-wire evidence and is a
sensitivity threshold, not a validated specular numerical-error bound.

## Analysis API contract

`scripts/analyze_matched.py` exposes `analyse(rows, protocol, budget_ms, search_config='medium',
experiment='specular', protocol_hash=None, mesh_audit=None)`. `rows` is a sequence of benchmark
record dictionaries. Each record needs `method`, `budget_ms`, `index`, `trajectory`, `seed`, `split`,
`rate`, `elapsed_ms`, `deadline_missed`, `evaluations`, `trace`, and optional `breakdown_ms`.
`protocol` is the parsed amended JSON object; `protocol_hash` is its SHA-256 hex digest. The return
value contains experiment scope, primary budget, per-method/per-budget cells, all protocol contrasts,
the selected margin and whether the coupled mesh audit passed.

For a coupled audit, `mesh_audit` must be a JSON object with the amended protocol hash,
`preselected_before_test_evaluation: true`, `split: "test"`, `segment_count_coarse: 81`,
`segment_count_fine: 161`, `audited_action_count` equal to the number of primary-budget rows,
finite `rate_difference_abs_max_bit_s_hz`, positive `resolution_criterion_bit_s_hz`, and boolean
`criterion_passed`. The analyzer checks provenance, action coverage, mesh sizes and consistency of
the declared maximum with the criterion. A missing audit leaves coupled statistical improvements
as `numerically_unresolved`; a passing audit is required to retain `improved`.

The report uses the held-out rows to define the per-frame best-found reference for the
time-to-target metric. This metric is descriptive and must not feed method, hyperparameter, budget,
or claim selection. Test outcomes remain untouched by development decisions. The registered final
timing node remains `3060-1`; development runs performed on `3060-2` do not redefine that protocol
setting.

## Addendum: fine-mesh resolution criterion (2026-11-06)

Declared before validation, freeze, and any test benchmark of the matched controllers. The
`mesh_audit_contract` resolution criterion is `0.015 bit/s/Hz`, equal to the practical margin. Because
rate changes up to 0.72 bit/s/Hz have been observed under mesh doubling on moving frames, this
criterion may fail. A failure withholds the coupled improvement claim and leaves the statistical
estimate unchanged. The audit recomputes every primary-budget returned action, which is estimated at
about 12 hours on four workers, so it runs only if at least one coupled contrast is otherwise decided
improved.

Test-set properties recorded for reporting: the Munich test blocks lie mostly at larger y than the v3
blocks and all have non-blocked direct links (0.74 non-zero fraction in v3), so the specular test is
subject to covariate shift. Repeated traces differ by about 1 percent in channel coefficients (Monte
Carlo noise). The new-to-new block guard is 2 m because 30 blocks do not fit at 4 m.
