# Coupled RIS: spatial and temporal feasibility report

This is a completed **development pilot**, not hardware validation or a final paper test. The original independent-cell Munich `specular_v5` run is preserved. This new experiment uses a different, fully specified wire surface and free-space geometry; its absolute rates must not be interpreted as the effect of adding coupling to Munich.

## Result in plain language

- **Spatial:** exact pair search achieved 17.1022 bit/s/Hz, compared with 16.7650 for attention at 10 ms. The current attention policy did not beat analytical search after its overhead.
- **Temporal:** linear prediction plus pair search achieved 5.1270; persistence plus pair search 4.7815; GRU plus pair search 4.6664. GRU prediction therefore did not provide a consistent advantage just by being learned.
- **Combined:** GRU plus attention achieved 5.0682. It must be compared with both the same attention controller under persistence and the simpler linear predictor plus pair search; combining two learned components is not automatically the best option.

These findings select a simpler controller for this pilot. They do not establish that attention can never help. The dataset is small, the attention model has no explicit pairwise edge bias, and training parents are random configurations and their single-flip local optima rather than a full distribution of online memory states. A redesigned model would need a new untouched evaluation set.

## What was simulated

A 5.53 GHz 3D PEC wire model includes all 64 RIS elements, four BS antennas and two UE antennas in a 70-port NEC-2 method-of-moments solve. Wires are 24 mm long and 50 μm in radius; the panel pitches are 28 and 30 mm. Each center port selects one of two loads: 1 − j10.799 Ω or 1 + j129.201 Ω. The production mesh has 81 segments per wire (5,670 unknowns). The reference uses 161 (11,270 unknowns). There is no substrate, ground plane, real switch model, material loss, city geometry or moving human blockage.

The channel is a power-wave transfer matrix with 50 Ω external references. The fixed all-OFF-reference RZF precoder has 0.1 W total **incident** BS power; mismatch means this is not identical to radiated power. The objective is minimum user spectral efficiency with multiuser interference, 1 MHz bandwidth, 290 K and 7 dB noise figure. Exact Schur reduction and rank-one/rank-two updates are shared by learned and analytical controllers.

![Actual geometry and coupling strength](figures/geometry_3d.png)

The 3D height map shows summed off-diagonal impedance magnitude, not received signal strength or a measured field map.

## Physics evidence

Across 103 reference-geometry patterns, doubling the mesh changed the complex channel by at most **0.740%** and the rate by at most **0.01503 bit/s/Hz**. Direct loaded NEC currents and network predictions differed by **7.41e-14** relative norm. Passivity and reciprocity checks passed at the reference geometry; passivity was also checked for all 192 frames. Additional moving-frame and optimizer-action mesh audits are recorded separately below.

On 250 random configurations of a training frame, removing inter-element coupling changed rate predictions by **0.2340 bit/s/Hz** mean absolute error. This is evidence that the approximation matters in this geometry, not evidence that attention is needed.

![Coupling and model mismatch](figures/coupling_effect.png)

## Experimental separation

- **Spatial:** current complete network observations; compare greedy, pair, random, memory GA, analytical-guided GA, shared MLP and two-layer atom attention. The no-physics ablation removes additional complex/coupling features but retains exact analytical flip gains. Coupling-blind pair search removes inter-RIS off-diagonal impedance only in its internal prediction; every action is scored on the same fully coupled truth. Its reference precoder is shared with the other methods.
- **Temporal:** four perfect past network observations at 20 ms intervals; predict one frame ahead. Compare persistence, linear extrapolation and a shared GRU. Forecast matrices are projected to passive reciprocal matrices. All use the same precoder derived from the last observation. Current-CSI pair search is an information oracle, not a global optimization upper bound.
- **Joint:** compare MLP and attention mutation with persistence versus GRU predictions. The comparison changes the forecast while holding the downstream controller fixed.
- **Information limit:** complete multiport impedance observations are an idealized input. We have not demonstrated affordable channel acquisition, an IoT implementation or human-blockage prediction. Attention uses per-atom coupled-network features; this version has no explicit edge-biased graph attention.

Twelve whole receiver trajectories have 16 snapshots each. Six trajectories train, three select checkpoints/budgets, and three form a development pilot. There is no frame mixing across splits, but all trajectories share one surface and free-space scene. Three seeds (7, 19, 43) repeat each controller. The MLP has 14,113 parameters, attention 17,665 and the shared temporal GRU 1,090. Training uses 25 epochs with validation checkpoint selection.

Training used 2,304 labeled examples and validation 1,152, derived from completed single/pair gains. Among 1,152 parents, **524** single-flip local optima admitted improving pairs. The second-action target includes pairs with harmful individual flips; all 2,016 pairs are evaluated offline for supervision.

## Pilot results at the validation-selected 10 ms budget

CPU timing includes forecasts, feature preparation, network preparation, precoding, memory, inference and candidate evaluation. It excludes one-time model loading, EM generation, channel acquisition and the environmental evaluation of the already returned action. All methods run sequentially on the same CPU core. Any deadline misses remain reported; no late candidate improvement is accepted.

| Mode | Controller | Mean rate (bit/s/Hz) | p95 runtime (ms) | Deadline misses |
|---|---|---:|---:|---:|
| spatial | pair | 17.102184 | 8.988 | 0/144 |
| spatial | analytical_ga | 16.907999 | 9.320 | 0/144 |
| spatial | greedy | 16.775225 | 9.112 | 0/144 |
| spatial | attention_no_physics_ga | 16.768689 | 8.988 | 0/144 |
| spatial | attention_ga | 16.765033 | 8.923 | 0/144 |
| spatial | attention_no_memory_ga | 16.765033 | 8.964 | 0/144 |
| spatial | memory_ga | 16.765033 | 9.268 | 0/144 |
| spatial | mlp_ga | 16.765033 | 8.555 | 0/144 |
| spatial | random | 16.765033 | 9.152 | 0/144 |
| spatial | blind_pair | 6.025364 | 9.000 | 0/144 |
| temporal | oracle_pair | 15.639527 | 9.036 | 0/108 |
| temporal | linear_pair | 5.126982 | 8.997 | 0/108 |
| temporal | gru_attention_ga | 5.068233 | 8.911 | 0/108 |
| temporal | gru_mlp_ga | 5.022948 | 8.596 | 0/108 |
| temporal | persistence_pair | 4.781546 | 8.981 | 0/108 |
| temporal | persistence_attention_ga | 4.764123 | 8.945 | 0/108 |
| temporal | persistence_mlp_ga | 4.764123 | 8.583 | 0/108 |
| temporal | gru_pair | 4.666397 | 9.050 | 0/108 |

![Runtime curves](figures/rate_runtime.png)

All budget curves include observed overruns; consult `summary.csv` and the raw records before making a deadline claim.

## Paired differences

Differences average optimizer seeds and frames within each trajectory first. With only three independent pilot trajectories, bootstrap intervals below are descriptive and cannot establish general superiority.

| Comparison | Mean difference (bit/s/Hz) | Descriptive 95% interval |
|---|---:|---|
| attention_ga − pair | -0.337150 | [-0.789794, -0.029135] |
| mlp_ga − pair | -0.337150 | [-0.789794, -0.029135] |
| pair − blind_pair | +11.076820 | [+10.371318, +11.619131] |
| attention_ga − mlp_ga | +0.000000 | [+0.000000, +0.000000] |
| attention_ga − attention_no_physics_ga | -0.003656 | [-0.010967, +0.000000] |
| attention_ga − attention_no_memory_ga | +0.000000 | [+0.000000, +0.000000] |
| gru_pair − persistence_pair | -0.115149 | [-1.398955, +0.617203] |
| linear_pair − persistence_pair | +0.345436 | [+0.013366, +0.692809] |
| gru_pair − linear_pair | -0.460585 | [-1.729089, +0.422940] |
| oracle_pair − persistence_pair | +10.857982 | [+8.590098, +13.094231] |
| gru_attention_ga − persistence_attention_ga | +0.304110 | [-0.387579, +0.880365] |
| gru_attention_ga − gru_pair | +0.401836 | [-0.253634, +1.011376] |

![Example moving trajectory](figures/trajectory_rates.png)

## Additional mesh and selected-action audit

| Frame | Split/use | Maximum channel change | Maximum rate change (bit/s/Hz) |
|---|---|---:|---:|
| 0 | Training | 0.643% | 0.02930 |
| 32 | Validation | 0.604% | 0.37764 |
| 48 | Pilot spatial | 0.716% | 0.07459 |
| 52 | Pilot temporal | 0.676% | 0.72021 |

All four random-pattern channel-norm checks passed the 1% threshold. The rate changes reveal why that threshold alone cannot certify optimizer rankings. For **54 actual returned actions** at one pilot frame per mode, the maximum channel change was **0.523%** and maximum rate change **0.64381 bit/s/Hz** with the original precoder frozen.

| Mode | Controller | Coarse rate | Fine rate |
|---|---|---:|---:|
| spatial | analytical_ga | 18.13488 | 18.20947 |
| spatial | attention_ga | 18.13488 | 18.20947 |
| spatial | attention_no_memory_ga | 18.13488 | 18.20947 |
| spatial | attention_no_physics_ga | 18.13488 | 18.20947 |
| spatial | blind_pair | 6.11728 | 6.14795 |
| spatial | greedy | 18.13488 | 18.20947 |
| spatial | memory_ga | 18.13488 | 18.20947 |
| spatial | mlp_ga | 18.13488 | 18.20947 |
| spatial | pair | 18.13488 | 18.20947 |
| spatial | random | 18.13488 | 18.20947 |
| temporal | gru_attention_ga | 7.15338 | 7.14297 |
| temporal | gru_mlp_ga | 7.15338 | 7.14297 |
| temporal | gru_pair | 5.15716 | 5.14138 |
| temporal | linear_pair | 5.64792 | 5.62543 |
| temporal | oracle_pair | 15.33558 | 15.53247 |
| temporal | persistence_attention_ga | 7.15338 | 7.14297 |
| temporal | persistence_mlp_ga | 7.15338 | 7.14297 |
| temporal | persistence_pair | 7.15338 | 7.14297 |

These are frame-level checks, not replacements for the trajectory-average tables. No selected configuration was optimized on the finer mesh. Near-tied methods remain unresolved until a larger, finer-mesh and lower-SNR study.

## Interpretation boundaries

Coupling-aware modeling, attention, multiport reduction and channel prediction all have existing literature. This pilot tests whether their computational tradeoffs are useful in one specified scenario. It cannot establish novelty simply by combining them. Small optimizer differences need to survive the mesh/action audit, a broader geometry/mobility study, uncertain/noisy/stale channel acquisition, and an untouched final evaluation.

The short free-space links and high incident power produce high-SNR cases that are particularly sensitive to interference cancellation. A small complex-channel error can cause a much larger rate error; channel-norm convergence alone must not be treated as rate convergence.

The earlier Munich result and this wire-model result answer different physical questions. A more faithful OpenSourceRIS extension still needs its PCB/substrate/switch EM model or measured mixed-pattern multiport calibration. Uniform ON/OFF panel curves cannot identify that matrix.

## References and artifacts

The live literature matrix contains 28 papers, including all papers in the saved Consensus research document and the numerical-model references used here. The existing Zheng et al. coupling-validation entry now cites its 2024 journal version. Reading statuses were preserved.

- [Live matrix](https://docs.google.com/spreadsheets/d/1Sa4wgYj23wOWy7-iLMHDoRCzCFPBmKHrnyzRfWbavOg/edit)

- [Consensus research](https://consensus.app/search/we-are-extending-a-simulation-only-1-bit-ris-contr/0fUy254zRdOo9479vnAKiQ/)

- [Multiport framework, Nerini et al.](https://doi.org/10.1109/TWC.2024.3416825)

- [Full-wave validation, Abrardo et al.](https://doi.org/10.1109/TWC.2024.3450722)

- [Measured coupling validation, Zheng et al.](https://doi.org/10.1109/TWC.2024.3451548)

- [Efficient physical channel computation, Prod’homme and del Hougne](https://doi.org/10.1109/LCOMM.2023.3330527)

- [Discrete multiport optimization, Hammami et al.](https://doi.org/10.1109/LWC.2026.3652464)

- [Spatio-temporal channel prediction, Liu et al.](https://doi.org/10.1109/TCOMM.2022.3215198)

`provenance.json`, `source_snapshot.tar.gz`, the dataset manifest, per-frame metadata, model histories/checkpoints and all JSONL controller records are retained. Large binary arrays/checkpoints remain in the local and lab workspace; source, reports, figures and metadata are published in Git.
