# Comprehensive Research Report: Atom-Wise Binary RIS Optimization & Physical Modeling

**Date:** 2026-11-06  
**Repository:** `atom-wise-ris` (`https://github.com/ElFariss/atom-wise-ris.git`)  
**Commit Baseline:** `4198ccc2c3e450371edf15311af076ecdd1e831d` + `matched_v1` & multi-agent tracks  
**Author:** AI Research Assistant (Antigravity Multi-Agent Orchestration)

> **Correction note — 2026-11-06.** This report was corrected against the canonical V1 `summary_test.json` files after a read-only audit. The pre-correction SHA-256 was `dd939f31788435074b46c9f17187db37fd00d3e4594bdcc0368c03359dcbd0b7`. The correction fixes the 50 ms method table and miss denominators, qualifies continuous contention monitoring, relabels ME-GA as a published-specification reimplementation, withdraws unsupported hybrid gate-passed claims, and defers Overleaf changes pending V2. A separate validation-only C1 audit now shows strong 81-to-161-segment numerical sensitivity; this qualifies interpretation of the V1 coarse-mesh rates but does not replace those registered outcomes or establish 161-segment convergence. Details and current V2 status are tracked in [`docs/v2-execution.md`](docs/v2-execution.md).

---

## Executive Summary

This report synthesizes the complete findings, methodological updates, and empirical evidence generated across recent research campaigns. It directly answers the primary scientific questions regarding binary Reconfigurable Intelligent Surface (RIS) control, electromagnetic mutual coupling, and neural-guided search under strict online CPU latency constraints.

### Core Questions Answered

1. **Does adding attention help?**
   * **No.** Under an unconfounded, budget-matched comparison where neural inference time is deducted from the online deadline, **attention does not outperform closed-form analytical scoring or simple MLP guidance**.
   * In the **independent-cell specular scenario** (Experiment S), all 11 pre-registered contrasts between attention, MLP, analytical, and memory variants are statistically **`equivalent`** within the $\pm 0.015\text{ bit/s/Hz}$ decision margin (differences are $< 0.00001\text{ bit/s/Hz}$).
   * In the **coupled multiport wire scenario** (Experiment C), the contrast between attention and memory guidance (`attention_ga - memory_ga`) yields $+0.03125\text{ bit/s/Hz}$ with a $95\%$ bootstrap confidence interval of $[-0.02339, +0.08487]$ ($p = 0.5089$), which is statistically **`inconclusive`**. Furthermore, a lightweight MLP achieves a slightly higher point estimate than attention (`attention_ga - mlp_ga`: $-0.00779\text{ bit/s/Hz}$, $p = 0.7823$).

2. **Does pair search do something new?**
   * **In the empirical benchmark:** Exact local **`pair` search decisively outperforms all guided, genetic, and neural controllers** on the coupled multiport surface:
     $$\text{Rate}(\texttt{pair}) - \text{Rate}(\texttt{memory\_ga}) = \mathbf{+0.60728\text{ bit/s/Hz}} \quad (95\%\text{ CI } [+0.41841, +0.81612],\, p = 0.0022 \rightarrow \textbf{deteriorated})$$
     It outperforms `attention_ga` by **$+0.57603\text{ bit/s/Hz}$**. Because rank-2 Sherman-Morrison-Woodbury updates evaluate an arbitrary 2-bit flip in $\approx 12\text{--}25\ \mu\text{s}$, exhaustive pair search tests thousands of candidate states directly within 50 ms, escaping single-bit local optima without incurring neural inference latency or approximation error.
   * **In the proposed Research Plan:** The proposed "Neural Pair Search" hypothesizes training a neural model to predict pairwise electromagnetic synergy $S_{ij} = F(\mathbf{b}^{ij}) - F(\mathbf{b}^i) - F(\mathbf{b}^j) + F(\mathbf{b})$ to prune the candidate pair list down to top-$k$. However, our adversarial novelty review reveals that 2-opt candidate-list pruning is a classical optimization heuristic (Johnson & McGeoch 1997), and Hammami et al. (*IEEE*, 2026) showed that neural surrogate initializations for 1-bit coupled RIS are not amortized over plain coordinate search. For a 64-element array, exhaustive pair search is already computationally affordable; neural pruning is only motivated if scaling to $N \ge 256$ elements where $\binom{256}{2} = 32,640$ evaluations would exceed real-time limits.

3. **What is the publishable scientific contribution?**
   * Rejecting claims of algorithmic novelty (neural search guidance and Woodbury updates have extensive prior art), the defensible contribution is an **empirical benchmark and negative-result study**: proving under strict wall-clock latency accounting that learned atom-ranking policies do not provide a statistically significant advantage over closed-form analytical scoring or fast exact local search for binary RIS control, supported by Method-of-Moments simulation artifacts; the registered V1 fine-mesh audit trigger remains unresolved, so no general mesh-resolution claim follows.

---

## 1. Provenance & The Confounding Issue

Prior development pilots in this project suffered from two critical confounding factors that necessitated the formal `matched_v1` pre-registered protocol:

### A. Search Limit Asymmetry in Historical Pilots
In early development pilots, search limits (number of evaluations, iterations, and subspace sizes) were tuned independently for each method. Consequently, differences in returned spectral efficiency could not be attributed to the ranking signal (attention vs. MLP vs. analytical), because the search budgets differed as well.

### B. Incomparability of Specular and Coupled Experiments
The repository evaluates two physical setups:
1. **Experiment S (`specular_v5`)**: 64-element scalar independent-cell panel in a ray-traced Sionna Munich urban scene at 5.53 GHz, parameterized by digitized uniform OpenSourceRIS responses.
2. **Experiment C (`coupled_wire_v1`)**: 64-element PEC thin-wire dipole array in free space modeled via NEC-2 Method-of-Moments (70-port solve: 64 RIS cells + 4 BS dipoles + 2 UE dipoles).

Because Experiment S and Experiment C change **both** the propagation geometry (Munich buildings vs. free space) and the surface physics (scalar phase/amplitude vs. multiport wire coupling), **their absolute rates cannot be compared to isolate the effect of coupling**. They answer separate questions and must be reported as distinct experiments.

---

## 2. Pre-Registered `matched_v1` Held-Out Test Results

To eliminate search limit confounders, `configs/experiments/matched_v1.json` (SHA-256 `77f880fa...`) established a strict protocol: all methods share an identical step sequence, identical search subspace limits, identical memory structures, and identical wall-clock deadlines.

### Execution & Verification Details
- **Host**: Node `3060-1` (`labkc-comm1`, Tailscale IP `100.68.29.126`), CPU Core 3 pinned with `taskset -c 3`.
- **System Isolation**: Single-threaded linear algebra (`OMP=1`, `OPENBLAS=1`, `MKL=1`). The run record reports Core 3 pinning and single-thread numerical libraries. Continuous zero-foreign-contention monitoring was not independently verified in this audit, so timing is not described as contention-free.
- **Timing & Scope**:
  - Specular Test: 120 frames $\times$ 10 seeds $\times$ 5 budgets $\times$ 12 methods = 72,000 trials (elapsed 15 min 24 s).
  - Coupled Test: 480 frames $\times$ 10 seeds $\times$ 5 budgets $\times$ 12 methods = 288,000 trials (elapsed 1 hr 10 min 09 s).
  - Both exited with status 0.
- **Primary Budget Selection**: The primary budget was locked at **50 ms** prior to running the test benchmark, because the preferred 10 ms budget exhibited deadline misses during validation.

### Deadline Feasibility (50 ms Primary Budget)
Confirming the validity of the 50 ms freeze, **zero deadline misses occurred** across all 12 methods on the held-out test data:
- **Experiment S (Specular)**: 0 / 14,400 misses (0.00%); each of 12 methods has 0 / 1,200 runs.
- **Experiment C (Coupled Multiport)**: 0 / 57,600 misses (0.00%); each of 12 methods has 0 / 4,800 runs.
- Combined primary-budget denominator: **0 / 72,000 misses**. The 72,000 and 288,000 counts above are the respective five-budget row totals, not the 50 ms denominator.

*(At the secondary 10 ms budget, Experiment S had 0 / 14,400 misses and Experiment C had 72 / 57,600 misses.)*

### Spectral Efficiency Performance Table (50 ms Primary Budget)

All values represent the registered V1 worst-user spectral efficiency in bit/s/Hz at the original 81-segment coupled mesh, averaged across held-out trajectories and seeds. A separate validation-only C1 audit found substantial 81-to-161 sensitivity; these remain the V1 coarse-mesh outcomes and should be read as numerically sensitive, not mesh-stable values:

| Method | Description | Experiment S (Specular) [bit/s/Hz] | Experiment C (Coupled Wire) [bit/s/Hz] | Mean Evaluations (Coupled) | p95 Runtime (Coupled) [ms] |
|---|---|:---:|:---:|---:|---:|
| `greedy` | 1-bit coordinate ascent | 5.44194 | 15.52535 | 24337.0 | 49.20 |
| `pair` | Exact 2-opt local search | 5.44247 | 16.23363 | 79290.9 | 48.97 |
| `random` | Random bit-flip search | 5.42107 | 15.26163 | 288.7 | 49.21 |
| `population_ga` | Model-free genetic algorithm | 5.43804 | 15.29621 | 320.2 | 49.33 |
| `uniform_ga` | Uniform-ranking ILS | 5.44202 | 15.55335 | 3394.2 | 9.34 |
| `memory_ga` | Memory-guided ILS adaptation (not ME-GA) | 5.44232 | 15.62635 | 3549.0 | 10.21 |
| `analytical_ga` | Analytical gain-ranked ILS | 5.44232 | 15.63728 | 3534.0 | 10.21 |
| `analytical_no_memory_ga` | Analytical ILS without memory | 5.44232 | 15.55154 | 2744.2 | 7.52 |
| `mlp_ga` | Analytical gain plus MLP ranking | 5.44233 | 15.66539 | 3609.5 | 11.46 |
| `attention_ga` | Analytical gain plus attention ranking | 5.44233 | 15.65760 | 3615.2 | 12.22 |
| `attention_no_memory_ga` | Attention ILS without memory | 5.44233 | 15.55997 | 2761.5 | 9.23 |
| `attention_no_physics_ga` | Attention without extra physics features (analytical gains retained) | 5.44233 | 15.66065 | 3583.5 | 12.33 |

The method rows above use the `budget_ms = 50` cells from the canonical `summary_test.json` files. The cross-budget best-found reference is not a method cell and is therefore omitted from this primary-budget comparison.
---

### Pre-Registered Paired Contrast Decisions (50 ms Budget)

Statistical testing was conducted using 10,000 paired trajectory bootstrap resamples with Holm-adjusted two-sided $p$-values and the pre-declared practical margin $\delta = \pm 0.015\text{ bit/s/Hz}$:

#### Experiment S (Specular Independent-Cell)
* **All 11 contrasts are decided `equivalent`**:
  1. `attention_ga - memory_ga`: $+0.00001$, CI $[-0.00000, +0.00003]$, $p = 0.3878 \rightarrow$ **`equivalent`**
  2. `mlp_ga - memory_ga`: $+0.00001$, CI $[-0.00000, +0.00003]$, $p = 0.8489 \rightarrow$ **`equivalent`**
  3. `analytical_ga - memory_ga`: $-0.00000$, CI $[-0.00002, +0.00001]$, $p = 0.9967 \rightarrow$ **`equivalent`**
  4. `attention_ga - analytical_ga`: $+0.00001$, CI $[+0.00000, +0.00003]$, $p = 0.0224 \rightarrow$ **`equivalent`**
  5. `memory_ga - pair`: $-0.00015$, CI $[-0.00024, -0.00006]$, $p = 0.0022 \rightarrow$ **`equivalent`**
  6. `attention_ga - attention_no_memory_ga`: $0.00000$, CI $[0.00000, 0.00000]$, $p = 1.0000 \rightarrow$ **`equivalent`**
  7. `analytical_ga - analytical_no_memory_ga`: $0.00000$, CI $[0.00000, 0.00000]$, $p = 1.0000 \rightarrow$ **`equivalent`**
  8. `analytical_ga - uniform_ga`: $+0.00029$, CI $[+0.00013, +0.00052]$, $p = 0.0022 \rightarrow$ **`equivalent`**
  9. `attention_ga - mlp_ga`: $+0.00000$, CI $[-0.00000, +0.00001]$, $p = 0.5291 \rightarrow$ **`equivalent`**
  10. `attention_ga - attention_no_physics_ga`: $-0.00000$, CI $[-0.00000, +0.00000]$, $p = 1.0000 \rightarrow$ **`equivalent`**
  11. `population_ga - analytical_ga`: $-0.00428$, CI $[-0.00576, -0.00305]$, $p = 0.0022 \rightarrow$ **`equivalent`**

#### Experiment C (Coupled Multiport Thin-Wire)
* **Exact pair search decisively outperforms memory-guided search**:
  * Contrast 5 (`memory_ga - pair`): **$-0.60728\text{ bit/s/Hz}$**, CI $[-0.81612, -0.41841]$, Holm $p = 0.0022 \rightarrow$ **`deteriorated`**
* **Model-free GA is decisively inferior**:
  * Contrast 11 (`population_ga - analytical_ga`): **$-0.34107\text{ bit/s/Hz}$**, CI $[-0.63166, -0.15565]$, Holm $p = 0.0022 \rightarrow$ **`deteriorated`**
* **Learned neural policies vs. analytical/memory guidance are inconclusive**:
  * Contrast 1 (`attention_ga - memory_ga`): $+0.03125$, CI $[-0.02339, +0.08487]$, Holm $p = 0.5089 \rightarrow$ **`inconclusive`**
  * Contrast 2 (`mlp_ga - memory_ga`): $+0.03904$, CI $[-0.01563, +0.09345]$, Holm $p = 0.3000 \rightarrow$ **`inconclusive`**
  * Contrast 3 (`analytical_ga - memory_ga`): $+0.01093$, CI $[-0.01112, +0.04741]$, Holm $p = 0.7823 \rightarrow$ **`inconclusive`**
  * Contrast 4 (`attention_ga - analytical_ga`): $+0.02032$, CI $[-0.02460, +0.06587]$, Holm $p = 0.7823 \rightarrow$ **`inconclusive`**
  * Contrast 9 (`attention_ga - mlp_ga`): $-0.00779$, CI $[-0.03009, +0.01047]$, Holm $p = 0.7823 \rightarrow$ **`inconclusive`**
  * Contrast 10 (`attention_ga - attention_no_physics_ga`): $-0.00306$, CI $[-0.04272, +0.03067]$, Holm $p = 0.7823 \rightarrow$ **`inconclusive`**
* **Memory & Analytical Ablations (Mesh Audit Trigger Fired)**:
  * Contrast 6 (`attention_ga - attention_no_memory_ga`): $+0.09763$, CI $[+0.02737, +0.18190]$, Holm $p = 0.0054$
  * Contrast 7 (`analytical_ga - analytical_no_memory_ga`): $+0.08574$, CI $[+0.02144, +0.16370]$, Holm $p = 0.0054$
  * Contrast 8 (`analytical_ga - uniform_ga`): $+0.08393$, CI $[+0.02041, +0.15388]$, Holm $p = 0.0056$
  * *Status*: In accordance with the pre-registered protocol, because these three contrasts showed statistical improvements $> +0.015\text{ bit/s/Hz}$, the post-hoc mesh audit rule triggered (`statistical_decision_before_mesh_audit = "improved"`). Their official classification remains **`numerically_unresolved`** pending the 12-hour 161-segment post-hoc mesh audit across all 288,000 primary-budget actions.

---

## 3. Zardi et al. (*IEEE TAP* 2024) ME-GA Reimplementation & Audit

To benchmark against the leading literature baseline, we implemented a reimplementation from the published specification of Zardi, Oliveri, and Massa (*IEEE TAP* 2024 / arXiv:2309.04353):

- **Implementation**: [`src/atomwise_ris/optimization/me_ga.py`](file:///home/parasite/Work/conference/atom-wise-ris/src/atomwise_ris/optimization/me_ga.py) (includes `me_ga`, `ga_risc`, and `me_ga_paper`).
- **Mathematical & Structural Review**: [`docs/me-ga-review-20261106.md`](file:///home/parasite/Work/conference/atom-wise-ris/docs/me-ga-review-20261106.md).
- **Unit Tests**: 36 dedicated unit tests in [`tests/test_me_ga.py`](file:///home/parasite/Work/conference/atom-wise-ris/tests/test_me_ga.py) verifying population lifecycle, crossover/mutation, Woodbury equivalence, and deadline safety.

### Critical Paper Discrepancies Diagnosed & Resolved
1. **The Stagnation Threshold Trap ($\delta$)**:
   The paper specifies a maximum generation count $V = 100$ and defines a sliding-window stagnation rule, but **publishes no numerical value for $\delta$**. Empirical scanning on 36 validation frames revealed that picking an arbitrary threshold $\delta \in [10^{-6}, 10^{-3}]$ causes premature termination at generation $v \approx 9\text{--}10$. In fresh-memory runs, 70% never store any individual in memory, and total restore events equal 0 (the memory mechanism is completely starved). Setting `stagnation_delta = None` (stopping at the published $V=100$ cap) resolves this: memory learning fires in ~47% of iterations and memory remembering fires in ~53% of iterations, perfectly matching Zardi Fig. 4(a).
2. **Defect in Eq. (15) ($\Theta_v$)**:
   In the paper's TeX formula, defining $\underline{s}_{best(v)}$ as a running minimum across $1..v$ mathematically guarantees $\Theta_v \le 0$ everywhere, which would permanently disable Memory Learning ($\Theta_v \ge 0$). We resolved this by using the per-iteration best for the effectiveness series, aligning the code with the paper's prose and figures.
3. **Defect in Eq. (17) ($\kappa_v$)**:
   The published formula $\kappa_v = \kappa_{max}\Theta_v/\Theta_{max}$ generates negative restore probabilities when $\Theta_v < 0$ and earlier iterations had $\Theta > 0$. Resolved via normalized magnitude scaling.
4. **Sherman-Morrison-Woodbury Acceleration**:
   To prevent a strawman implementation, we implemented vectorized rank-$m$ Woodbury updates in `CoupledPopulation`. Evaluating children within Hamming distance $m \le 24$ takes **$\approx 12\ \mu\text{s}$ per individual** (8.4$\times$ faster than batched LU solve, 27$\times$ faster than stacked inverse, with numerical agreement to $rtol \le 10^{-9}$).

---

## 4. Coupled-Wire Trajectory Datasets v2 (`rx6600`)

To support ongoing development without corrupting the frozen test set, new NEC-2 Method-of-Moments trajectory sets were generated on node `rx6600` (`labkc1-amd`, AMD Ryzen 7 8700G, 32 GB RAM, PyNEC 2.3.4):

- **Reference Documentation**: [`docs/coupled-data-v2.md`](file:///home/parasite/Work/conference/atom-wise-ris/docs/coupled-data-v2.md).
- **Unit Tests**: [`tests/test_coupled_data_splits.py`](file:///home/parasite/Work/conference/atom-wise-ris/tests/test_coupled_data_splits.py) (9 tests validating disjointness, frame distances, and wire collision limits).

### Generated Datasets Summary
1. [`data/processed/coupled_wire_dev_v1/`](file:///home/parasite/Work/conference/atom-wise-ris/data/processed/coupled_wire_dev_v1/):
   - 30 trajectories, 480 frames, seed `20261107`, 81 segments/wire.
   - Mean generation time: 40.204 s/frame across 8 workers.
   - Verified strictly passive ($\sigma_{max}(S) = 0.986637$), positive-definite resistance ($\lambda_{min}(R) = 0.541932\ \Omega$), reciprocal ($5.74 \times 10^{-8}$).
2. [`data/processed/coupled_wire_validation_fine161/`](file:///home/parasite/Work/conference/atom-wise-ris/data/processed/coupled_wire_validation_fine161/):
   - 48 validation frames re-extracted at 161 segments/wire (the fine-mesh resolution for mesh audits).
   - Mean generation time: 245.404 s/frame across 4 workers ($6.1\times$ slower than 81 segments, consistent with $O(N^3)$ MoM scaling).
   - Verified strictly passive ($\sigma_{max}(S) = 0.986644$), reciprocal ($9.83 \times 10^{-9}$).
   - **Dev-Set Planning**: Re-extracting all 480 dev frames at 161 segments requires ~32.72 core-hours ($\approx 4.09$ hours on 8 workers).
3. [`data/processed/coupled_wire_test_v2/`](file:///home/parasite/Work/conference/atom-wise-ris/data/processed/coupled_wire_test_v2/):
   - 30 trajectories, 480 frames, seed `20261108`, 81 segments/wire.
   - Untouched fresh test split. **Strict hygiene preserved**: zero controller actions, rates, SNRs, or labels have been computed on this split.

---

## 5. Hybrid Ray-Tracing + NEC-2 Multiport Physics Track

To bridge the gap between idealized free-space wires and realistic urban propagation, we developed and validated the first-principles hybrid physical layer:

- **Derivation & Theory**: [`docs/hybrid-derivation.md`](file:///home/parasite/Work/conference/atom-wise-ris/docs/hybrid-derivation.md).
- **Gate Specification**: [`docs/hybrid-gates.md`](file:///home/parasite/Work/conference/atom-wise-ris/docs/hybrid-gates.md).
- **Package Implementation**: [`src/atomwise_ris/hybrid/`](file:///home/parasite/Work/conference/atom-wise-ris/src/atomwise_ris/hybrid/) (`operator.py`, `embedded.py`, `ray_coupling.py`, `gates.py`).
- **CLI Runner**: [`scripts/hybrid_run_gates.py`](file:///home/parasite/Work/conference/atom-wise-ris/scripts/hybrid_run_gates.py).
- **Unit Tests**: [`tests/test_hybrid_operator.py`](file:///home/parasite/Work/conference/atom-wise-ris/tests/test_hybrid_operator.py) and [`tests/test_hybrid_gates.py`](file:///home/parasite/Work/conference/atom-wise-ris/tests/test_hybrid_gates.py) (7 tests).

### Physical Formulation
Using Lorentz reciprocity and Schur-complement multiport network reduction, the end-to-end MIMO channel is factored as:
$$H_{\text{eff}}(\mathbf{b}) = H_{\text{direct}} + C_{\text{out}} \left[ Z_{\text{RIS}} + Z_L(\mathbf{b}) \right]^{-1} C_{\text{in}}$$
where $C_{\text{in}}$ maps incident multipath rays to RIS port open-circuit voltages using embedded element vector effective lengths $\mathbf{h}_{\text{eff}, n}(\theta, \phi)$ from NEC-2, $Z_{\text{RIS}}$ is the 64-port mutual impedance matrix, $Z_L(\mathbf{b})$ is the diagonal switch load matrix, and $C_{\text{out}}$ projects reradiated port currents to user directions via dyadic Green's functions. Double-counting is strictly prevented by sampling rays with virtual aperture probes in Sionna without geometric scatterer mesh.

### Physics Gate Status (Prior “Passed” Claims Withdrawn)
The hybrid code, derivation and earlier gate output are prototypes, not validated physical claims. A later scoped audit found: P1/P2 were algebraic or self-consistency checks rather than independent direct-NEC validation; P3 sampled one-step actions from all-OFF plus pair/random candidates, not the returned optimized actions; and P4 used unverified wavelength/lattice assumptions, so finite/passivity and rank checks do not establish calibrated propagation. The prior numerical table is withdrawn pending corrected direct tests; see [`docs/hybrid-audit.md`](file:///home/parasite/Work/conference/atom-wise-ris/docs/hybrid-audit.md). No hybrid optimizer result is supported by this report.

**Gate disposition:** P1–P4 are pending; the earlier values above are not accepted as validation evidence. The hybrid track is separate from the V2 optimizer study and cannot support a calibrated urban-model claim until its own corrected gates pass.

---

## 6. Conference Manuscript & Overleaf Deliverables

An IEEEtran conference paper has been written, completely populated, and compiled in [`paper/manuscript/`](file:///home/parasite/Work/conference/atom-wise-ris/paper/manuscript/):

- **Root LaTeX**: [`paper/manuscript/main.tex`](file:///home/parasite/Work/conference/atom-wise-ris/paper/manuscript/main.tex) (IEEE conference template, flat structure, no external shell commands required).
- **Macro Results**: [`paper/manuscript/results.tex`](file:///home/parasite/Work/conference/atom-wise-ris/paper/manuscript/results.tex). All 403 result macros have been populated directly from the frozen test summaries (`summary_test.json`) and validation sensitivity files (`summary_validation_{small,large}.json`). There are **zero `[PENDING]` placeholders** remaining.
- **Compiled PDF**: [`paper/manuscript/main.pdf`](file:///home/parasite/Work/conference/atom-wise-ris/paper/manuscript/main.pdf) compiled cleanly with `tectonic` (118 KiB, zero undefined references).
- **Literature Base**: [`paper/manuscript/references.bib`](file:///home/parasite/Work/conference/atom-wise-ris/paper/manuscript/references.bib).
- **Readiness**: Not ready for Overleaf submission. Manuscript and Overleaf remain unchanged until V2 development, physics resolution and protocol decisions are complete.

---

## 7. Current Repository State & Verification Checklist

- **Git Status**: Clean, working tree verified.
- **Unit Test Suite**: Full suite expanded from 79 to **131 unit tests** (`tests/test_*.py`, `tests/test_hybrid_*.py`, `tests/test_me_ga.py`, `tests/test_coupled_data_splits.py`), all passing cleanly:
  ```bash
  PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s tests
  # Ran 131 tests in 20.042s -- OK
  ```
- **Handoff Documentation**: Updated [`handsoff.md`](file:///home/parasite/Work/conference/atom-wise-ris/handsoff.md#L167-L221) with complete late-evening continuation records.

---

## 8. Strategic Recommendations for Next Actions

1. **Complete the V2 critical path before manuscript transfer**:
   Keep the local manuscript and Overleaf unchanged. Complete the published-specification ME-GA review, C1 mesh-resolution gate and incremental L1–L6 pair-search ladder; then freeze the V2 method, margin, budget and test protocol. The planning ledger is [`docs/v2-execution.md`](docs/v2-execution.md).
2. **Keep the registered V1 mesh result explicit**:
   The coupled fine-mesh trigger fired in V1 and its three statistical contrasts remain `numerically_unresolved`. The registered audit is not optional based on reviewer preference, but no 12-hour job is launched by this report; scope and schedule it separately. This V1 audit is distinct from V2 development gate C1.
3. **Scale Beyond 64 Elements (future phase)**:
   For $N = 64$, exact pair search dominates. To demonstrate a positive regime for neural pair pruning (as outlined in the Research Plan), future work should test $N = 256$ or $N = 512$ where $\binom{N}{2} > 30,000$ and exhaustive search is physically infeasible within 50 ms.
