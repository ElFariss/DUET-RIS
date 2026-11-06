# Improvement campaign: verified development results (2026-11-06)

This report separates the registered matched comparison on node1 from the smaller follow-up development campaign on node2. The results below are validation-only. No held-out test controller scores were read or used for method selection; the test remains frozen and unrun.

## Node1 registered matched validation

The registered comparison used 60 trained models across its prescribed method/seed set and completed on node1 (`3060-1`). Its frozen protocol is [the archived matched_v1 snapshot](../configs/experiments/archive/matched_v1-pre-gatefix-lock-20261106.json), SHA-256 `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe`. The primary budget selected from validation was 50 ms because there were deadline misses at 10 ms (Munich/specular 1; coupled 6). At 50 ms there were no misses. At the initial freeze the campaign gate still checked a hardcoded 10 ms value; the gate was corrected without changing the selection rule and a fresh source validation is summarized below. No test benchmark has run. This protocol selection is distinct from the subsequent node2 development grid, which was run at 5, 10, and 50 ms.

The node1 primary-budget summaries are in [specular report](../outputs/runs/matched_specular_v1/REPORT_validation.md) and [coupled report](../outputs/runs/matched_coupled_v1/REPORT_validation.md), with machine-readable detail in their adjacent `summary_validation.json` files. At 50 ms, the coupled mean worst-user rates were 15.515 bit/s/Hz for `pair`, 15.040 for `memory_ga`, 15.017 for `mlp_ga`, 15.015 for `analytical_ga`, and 15.011 for `attention_ga`; `pair` had p95 runtime 48.98 ms while the ranked variants took 11.56–13.66 ms p95. In specular validation, all ranked methods were approximately 4.97327 bit/s/Hz; `pair` was 4.97331. These outcomes show a rate/runtime tradeoff in coupled validation and near parity in specular validation, not a neural-model win.

`memory_ga` is the project's memory-enhanced ILS adaptation and serves as an incumbent search-policy reference. It is not a faithful reproduction of Zardi et al. (2024). The `population_ga` result is a separate population-based baseline; it is not part of the same-step ranked-ILS contrast. The ranked-ILS variants share the registered search settings and deadline, with explicit memory/no-memory controls. The original pilot/handoff benchmark used a different engine and method-specific settings, so comparisons to it cannot isolate model learning from search-engine changes.

## Node2 development checkpoint validation at 10 ms

The follow-up was run on node2 (`3060-2`, core 0), with seeds 7, 19, and 43. The campaign sidecars freeze the development protocol snapshot at SHA-256 `ffc1a771622acaa2114c11e2941c62bbb22a844cbeaee84580ede1fc214974fe`; this is distinct from both the archived original registration (`2e2fc77e8fcb8472fc25c5b2b76d612dd29b1adebe53354527485110e5dc7514`) and node1's amended formal protocol (`a033…`). Each row is a frame-by-seed observation, but inference/uncertainty must cluster at the physical trajectory: six specular validation trajectories (IDs 12–17, 24 frames total) and three coupled trajectories (48 frames total). Thus the CSV's 72 and 144 rows per method are not independent sample counts. The ten artifact-root/policy cases below are reported separately; conditional-pair runs are never pooled with default runs. The incumbent roots evaluated here use the October 24 canonical local weights identified in their manifests, not the separate Gemini-recovered weights.

| Case | Pair | Analytical ILS | MLP ILS | Attention ILS |
|---|---:|---:|---:|---:|
| Specular incumbent, default | 4.973304 | 4.973268 | 4.973268 | 4.973268 |
| Specular new A, default | 4.973303 | 4.973268 | 4.973268 | 4.973268 |
| Specular new B, default | 4.973304 | 4.973268 | 4.973268 | 4.973268 |
| Specular incumbent, conditional | 4.973304 | 4.973268 | 4.973268 | 4.973262 |
| Specular new A, conditional | 4.973304 | 4.973268 | 4.973268 | 4.973262 |
| Specular new B, conditional | 4.973303 | 4.973268 | 4.973268 | 4.973262 |
| Coupled incumbent, default | 15.063451 | 14.954461 | 14.956986 | 14.903799 |
| Coupled new, default | 15.063451 | 14.954461 | 14.998194 | 14.929707 |
| Coupled incumbent, conditional | 15.063451 | 14.954461 | 14.956986 | 14.903799 |
| Coupled new, conditional | 15.051568 | 14.954461 | 14.998194 | 14.929707 |

Rates are mean worst-user throughput in bit/s/Hz. The relevant paired row averages (same scene/frame/seed) show that the fresh coupled MLP checkpoint exceeded the October 24 canonical incumbent MLP by `+0.041208` bit/s/Hz (mean paired elapsed-time change `+0.0884 ms`); fresh attention exceeded incumbent attention by `+0.025908` bit/s/Hz (mean paired elapsed-time change `−0.0146 ms`). These are descriptive paired differences over only three trajectories. They are not formal significance claims and do not establish generalization. The `pair` baseline remained highest in the default coupled cases (15.063451), and therefore no new learned model beat the best search baseline. The conditional-pair rows do not show a consistent physical effect: learned rates were unchanged and the small `pair` differences between independent runs are wall-clock/pass variation, not an effect of that option on the `pair` method.

In specular, the rates barely changed with the fresh checkpoints. The conditional attention policy shifted the mean by only `−0.0000054` bit/s/Hz and added approximately 0.81 ms average latency. In coupled runs the conditional policy preserved learned rates and added roughly 0.43 ms for MLP and 0.57 ms for attention in the incumbent case. All 10 ms campaigns had zero reported deadline misses. This development comparison does not change the node1 primary-budget selection.

The completed node2 follow-up also covers 5 and 50 ms in the same ten separately identified cases. At 50 ms, the coupled default new MLP mean was 15.054877 versus 14.985687 for the canonical incumbent (`+0.069190` paired) and 15.030347 for the shared `memory_ga`; the new MLP therefore exceeded this search-policy control by about 0.024530 in this development sample. Attention was 14.951957 versus 14.959086 (`−0.007129`), showing no attention improvement at that budget. `pair` remained highest in the new coupled default case at 15.524868. In specular, every ranked method remained near 4.973268 at 50 ms. At 5 ms, the default new coupled MLP/attention means were 14.961816/14.893499 versus 14.934298/14.868496 for the incumbent. There were three deadline misses in the full 5 ms grid, all in new-coupled-conditional: attention had two and attention-no-physics had one (each out of 144). The 10 and 50 ms grids had no misses. Full per-case/per-method/per-budget values and paired row deltas are in the machine-readable summary and contrast files below; these remain descriptive, with cluster counts of six and three trajectories.

The new coupled campaign includes `attention_no_physics_ga` as a copied incumbent control, not as a newly trained checkpoint. It is not a fresh no-extra-physics ablation. The `0.015 bit/s/Hz` value in the protocol is an engineering decision margin only; it is not a numerical mesh-accuracy bound. Any coupled improvement claim requires the preselected fine-mesh audit of the actual returned actions.

### Training and provenance

The separate development training produced 18 fresh checkpoints: 12 specular (recipes A/B × attention/MLP × seeds 7/19/43) and six coupled (attention/MLP × seeds 7/19/43). The older copied no-physics weights do not count as fresh training. These are distinct from the 60 models in the node1 registered comparison.

| Provenance item | SHA-256 |
|---|---|
| Node1 formal matched protocol used for completed validation | `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe` |
| Current gate-fix budget lock protocol | `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88` |
| Node2 frozen development protocol snapshot | `ffc1a771622acaa2114c11e2941c62bbb22a844cbeaee84580ede1fc214974fe` |
| Archived pre-amendment registration | `2e2fc77e8fcb8472fc25c5b2b76d612dd29b1adebe53354527485110e5dc7514` |
| Specular fresh-training summary | `e422908a1a2ba4b51bbe8d2939a731f704fb15eb40795d7f94f60a9dd4a9e12c` |
| Coupled fresh-training summary | `c0289f18904bb2bc120c95baeca0147961273c608ce765ac00024cfc71f5d6b6` |
| Node2 10 ms campaign provenance | `1776ecbaec2302227529c5965e95e3cc5c4bbb08b5db4c5de8786f6bdb106d45` |
| Node2 10 ms method summary | `96c56488fba1fce3a518e204312959b45bd330939ef1c1ed00050726ee17afe6` |
| Node2 10 ms paired contrasts | `c01fd9e9b2a23a87530aa55a5ed6dba8792cf5045d918bb994d241828f33d0e3` |
| Node2 final 5/10/50 ms method summary | `d57ec513fef9bc78b13480d6812c2817f3f8b63cc8ab24c6822e97641c8fb337` |
| Node2 final 5/10/50 ms paired contrasts | `3fc47609d562d6911c9b692bbb80cc8aa01227612e11befc30037b228890a3d0` |
| Node2 final source hashes | `e59ca37a4f950c4a7a1a4bdfb76b602252a3ce6986a29b8458301845e3a7909d` |

The summary JSONs include the exact checkpoint SHA-256 for each of the 18 fresh weights, input hashes, training seeds, and recipe metadata. The node2 frozen protocol JSON is retained at `outputs/recovered/20261106/3060-2/improvement-campaign-final2/source_config/matched_v1.json`; `source_config/archive_manifest.json` and `source_hashes_final2.json` identify the frozen protocol/source/data/response/gate/checkpoint hashes for the full campaign. Each campaign manifest and sidecar also includes per-run checkpoint and JSONL hashes. The updated active budget-lock protocol archives the previous node1 protocol byte-for-byte at `configs/experiments/archive/matched_v1-pre-gatefix-lock-20261106.json` and cites unchanged selection/input hashes with the miss counts that selected 50 ms before any test outcome. Raw checkpoints, arrays, and run JSONL files are retained locally under `outputs/runs/` and `outputs/recovered/` and are intentionally excluded from Git; compact summaries and this report remain reviewable. The specular training labels hash to `c831b0de3cd59084ddb3f48ad9b1bf61c3e6525e9090f1d41ad1c61d65260285` (train) and `859a163a064030460908d3d0f1183bea40fb22816e3f4cc1579a555d31130d8e` (validation). Coupled label hashes are `13d1a8e489bde63a29ff2e97e8edd1fbd6b2cacd72ec318b0ef5a60c0f020de8` (train) and `9a51e016ea0e669defc344c541759822e2100dc7ef29326d88e005e802d0d8b9` (validation); physical dataset, scaling, and physics-gate hashes are recorded in the coupled training summary.

### Interpretation and limits

The node2 deltas compare checkpoint roots under the same newer engine and are useful for checking candidate model behavior. They do not estimate the benefit of the search-engine upgrades over the historical handoff engine. The broader 10 ms grid is descriptive, uses only three seeds and three or six validation trajectories, and has not been frozen as a formal matched primary-budget analysis. No uncertainty interval or p-value from the frame rows should be treated as if those rows were independent trajectories. The node1 reports provide the registered matched statistics and must remain the formal validation reference. No result here establishes a general physical-performance claim, calibrated hardware feasibility, or a held-out test result.

## Artifacts

- 5/10/50 ms campaign root: `outputs/recovered/20261106/3060-2/improvement-campaign-final2/`
- Final node2 summary and paired contrasts: `outputs/recovered/20261106/3060-2/improvement-campaign-final2/method_summary_final2.csv` and `paired_contrasts_final2.csv`
- Node2 training summaries: [specular summary](../outputs/runs/specular_improvement_remote_20261106/summary.json) and [coupled summary](../outputs/runs/coupled_improvement_remote_20261106/summary.json)
- Node1 matched reports: `outputs/runs/matched_specular_v1/REPORT_validation.md` and `outputs/runs/matched_coupled_v1/REPORT_validation.md`
- Reproducible development plotter: [plot_improvement_results.py](../scripts/plot_improvement_results.py)

Figures are generated as separate case files so checkpoint roots and policy variants are never pooled: [specular new A, default, 10 ms](../outputs/figures/improvement-20261106/specular-newA-default-10ms.png), [specular new A, conditional, 10 ms](../outputs/figures/improvement-20261106/specular-newA-conditional-10ms.png), [coupled new, default, 10 ms](../outputs/figures/improvement-20261106/coupled-new-default-10ms.png), [coupled new, conditional, 10 ms](../outputs/figures/improvement-20261106/coupled-new-conditional-10ms.png), [coupled new, default, 50 ms](../outputs/figures/improvement-20261106/coupled-new-default-50ms.png), and [specular new A, default, 50 ms](../outputs/figures/improvement-20261106/specular-newA-default-50ms.png). Their horizontal intervals resample physical trajectories; with only three coupled trajectories, these intervals are descriptive and coarse.

## Completion update: fresh node1 gate validation and temporal development

The gate-fixed source (active protocol SHA-256 `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88`) was revalidated on node1 in a fresh isolated workspace using the same 60 matched checkpoints; no retraining occurred. Both fresh selectors retained the locked 50 ms primary. The full 10-seed, five-budget, medium-config runs had zero 50 ms misses; at 10 ms, specular had zero misses and coupled had three. Read-only validation-gate checks passed in both the remote workspace and local mirror. No test split was run. Full recovery details, timings, source/input hashes, and artifact paths are in [RECOVERY-NOTE.md](../outputs/recovered/20261106/3060-1/fresh-gatefix-validation/RECOVERY-NOTE.md), with per-experiment reports and selections in its `specular/` and `coupled/` directories.

Temporal v2 development validation evaluated 1,296 actions from three fresh GRU seeds over three validation trajectories, three budgets, and four forecast methods. It had zero deadline misses. GRU v2 reduced forecast MSE to 0.0031504 versus linear extrapolation's 0.0050039, but its paired truth-rate deltas versus linear were −0.0132, +0.0274, and +0.0515 bit/s/Hz at 5, 10, and 50 ms. With only three trajectories and mixed budget-dependent outcomes, this is not an established controller improvement. The current-CSI comparator is a noncausal reference, not a guaranteed optimum. See [the temporal v2 report](temporal-v2-20261106.md) for per-budget rates and detailed accounting.

These temporal weights add three fresh exploratory GRUs to the 18 fresh spatial checkpoints documented above. They are separate from the 60 matched checkpoints. Training provenance has a limitation: per-seed temporal metadata does not contain the trainer-source hash, and the migration manifest records a training-workspace drift; the resulting weights, scaling arrays, and metadata were copied into the final isolated workspace and verified by checkpoint hash. Do not claim byte-exact training reproducibility from the current metadata.
