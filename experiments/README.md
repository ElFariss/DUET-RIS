# Hypotheses and evidence

| Study | Question | Evidence |
|---|---|---|
| Baseline comparison | Do learned edits improve rate at equal complete CPU time? | `outputs/runs/specular_v5/summary.json` and paired raw timing records |
| Physics-feature ablation | Do explicit response and complex-contribution features help beyond exact analytical flip scores? | `attention_no_physics_ga` versus `attention_ga` |
| Pair-conditioning ablation | Does the first-selected-bit marker improve completed two-bit edits? | `attention_no_conditioning_ga` versus `attention_ga` |
| Memory ablation | Does causal retrieval of previous configurations help? | `attention_no_memory_ga` versus `attention_ga` |
| Response sensitivity | Does nominal ranking survive declared uncertainty? | `sensitivity_summary.json`; fixed actions, shared perturbations |
| Propagation convergence | Do channels stabilize as the ray budget increases? | Raw acquisition audits; diffraction instability remains unresolved |

The pilot is development data. It does not establish novelty. The main nominal
result favors analytical pair/greedy search. See `docs/claim-evidence.md` for the
limits on interpreting these experiments.
