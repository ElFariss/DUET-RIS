# AI directions for NeurRIS-1bit

Date: 18 October 2026 (Asia/Jakarta).
Scope: preliminary literature and implementation audit, not an exhaustive SOTA survey.
User preference: no target device yet; identify a practical research direction.
Status: research only. No model trained, no new benchmark run, and no manuscript results replaced.

## Main assessment

Fast AI-based RIS control is an active research area with existing embedded MLP/INT8, graph-transformer, temporal attention, hybrid MoE, and classical deadline-aware work. Architecture names do not establish novelty. The useful question is whether a specific controller improves the quality/latency tradeoff under a declared observation model and device budget.

Recommendation: establish strong classical baselines, correct the learning objective, and try a tiny INT8 controller before introducing conditional refinement. Treat the eventual claim as a hypothesis until a common-protocol comparison succeeds.

## What the current code actually contains

Sources: [fair_ris.py](/home/parasite/Work/conference/smap2027-paper/code/fair_ris.py), [main.tex](/home/parasite/Work/conference/smap2027-paper/paper/main.tex), [saved results](/home/parasite/Work/conference/smap2027-paper/experiments/20261002/ris/results.json).

- One transmitter/receiver scalar effective channel, 64 independent reflected coefficients and one direct coefficient.
- Two illustrative surface responses: ideal opposite phases, and an attenuated/phase-imperfect alternative. These are not measured unit-cell responses.
- Independent simulated channel snapshots, rather than trajectories, a spatially correlated panel, frequency-dependent subcarriers, or a physical 6 GHz deployment.
- A dense network: 132 inputs, hidden widths 256 and 128, 64 outputs. Parameter count by architecture arithmetic: 75,200.
- Inputs are estimated channel values. Targets come from coordinate search using clean training channels. Binary cross-entropy learns switch labels; validation selects by that label loss.
- The tested network loses to estimated-channel coordinate search across all 18 seed/noise/response combinations.
- Saved latency is batch-amortized inference over 1,000 channels. The network runs on CUDA and the analytic control in NumPy on CPU. These numbers do not establish fair single-update speedup.
- Code SHA-256: 99d0f84d377c375f62ef384a36fa0e8898ed3e0afea24bed799a9f5c0333b30c.
- Manuscript SHA-256: e380d481ae746b9a8caa2793a7d67af38c332c66fec8caf500996fd6c30c78c3.
- Results SHA-256: 657460810b6a5c52dbad818ed8fea2fa79542c0028c80a3773c463082bcdd138.

## Relevant evidence and its boundaries

### [1] Embedded MLP and quantization

Urbinati et al. implement RIS codebook prediction on actual microcontrollers. Compact configurations report roughly 0.2–0.8 ms on a Cortex-M7; the fastest configurations have materially lower achievable rates. The work evaluates INT8 conversion and a latency/rate frontier. Communication rates derive from the study's channel/data model; MCU execution is hardware measured. Its sampled-CSI/codebook task differs from our full-vector binary-output task. Do not divide its latency by another paper's latency to rank architectures. Primary paper: [On-Device Deep Learning for RIS Beamforming: Design and Latency-Rate Trade-Offs](https://doi.org/10.1109/OJCOMS.2026.3687306). [Author repository](https://github.com/LucaUrbinati44/DL-on-RISC/).

### [2] Graph transformer on an SBC

Samaranayake et al. report native Raspberry Pi 4B execution of a graph transformer and competing controllers. Their abstract reports 39.7 ms inference and 5.37 MB memory, with mean SNR 29.49 dB, 0.50 dB below their simulated-annealing reference. This is evidence of embedded inference, not proof that their reference is a global optimum or that a physical RF panel was validated. Full implementation and timing protocol were not audited here. [Primary record](https://ieeexplore.ieee.org/abstract/document/11691528/).

### [3] Temporal attention/LSTM

APRIS forecasts orientation-related angles using an Attention-LSTM and computes quantized phases analytically. It reports 2.36 ms per-slot inference for a simulated 28 GHz, 64-element, 3-bit setting. The accessible material does not establish a comparable MCU timing result. Its temporal inputs and physical setup differ from our independent snapshots. [Primary paper](https://doi.org/10.1016/j.phycom.2026.103171).

### [4] MoE and CNN gating

Yildiz studies hybrid MoE and CNN-based gating in a simulation framework. This overlaps generic claims about using these ingredients for RIS. The described CNN gates allocate spatial surface responses; that is different from demonstrating that early exit or sparse expert execution reduces processor time. A runtime-routing proposal still needs a more specific overlap check. [Primary paper](https://doi.org/10.3390/electronics14224421).

### [5] Stronger classical baseline

Zhang et al. give a linear-time globally optimal solution for ideal binary-phase scalar-channel beamforming, including a direct/background path. That objective closely matches our ideal-response snapshot objective. With estimated CSI, the solver optimizes the estimated objective; it does not receive true test CSI or guarantee the best true-channel result under estimation error. Do not automatically extend the theorem to our nonideal scenario without checking its assumptions. [Author manuscript, especially Theorem 1](https://kaimingshen.github.io/doc/OptimalBeamforming.pdf).

### [6] Budgeted classical refinement

Turbo-FQCA uses warm starts, early stopping, update/time budgets, and delta signaling. This overlaps a generic proposal to refine only as needed under a deadline. Its published setup and information-access assumptions must be checked before reproduction; its reported rates are not comparable to our scalar-channel rates. [Author-institution publication record](https://pure.kfupm.edu.sa/en/publications/turbo-fqca-budget-constrained-ris-phase-optimization-with-robust-/).

### [7] and [8]: additional adjacent coverage

Deep unfolding of RIS beamforming iterations [7] and predictive closed-loop control to compensate delays [8] are already reported. Consensus abstracts were fetched; full implementations were not audited. These are overlap leads, not reproduced baselines or speed evidence. No general novelty is assigned to unrolling optimization or predicting around control delays.

## Architecture choices: hypotheses, not measured rankings

| Choice | When it makes sense | Issue in our current setup | Proposed priority |
|---|---|---|---|
| Tiny dense MLP | Small, fixed vector input | Must fix loss and compare against strong analytic controls | First neural baseline |
| Shared per-element network with global pooling | Element sets and variable panel size | Define equivariance and global interaction explicitly | Useful structural baseline |
| CNN | Known panel geometry and correlated neighboring elements | Current independent coefficients have no meaningful image-like neighborhood | Add after realistic spatial data |
| GRU/LSTM or temporal CNN | Correlated channel history, motion, stale observations | Current samples contain no temporal sequence | Add with a temporal task |
| Small attention/graph model | Important inter-element/user interactions or variable topology | More operators do not automatically buy useful quality | Later accuracy/structure comparator |
| Deep unfolding | A good iterative solver needs fewer learned steps | Baseline solver and observation model must be established first | Strong alternative to black-box prediction |
| Sparse MoE / early exit | Different regimes need different computation | Routing, model storage and branch execution cost must be counted | Only after fixed-cost baselines |
| INT8 | Supported integer kernels and an acceptable quality loss | Weight-file size alone is insufficient | First deployment compression experiment |

Surface phase resolution and neural precision are separate: a 1-bit reflecting element can be controlled by an INT8 neural network.

For the present independent-element simulator, CNN adjacency and LSTM memory have no supplied physical structure to exploit. These are implementation-based assessments, not universal architecture rankings.

## First fix the learning problem

A high switch-label match rate need not imply a strong combined signal. Multiple configurations can have similar utility; copying one optimizer's labels gives equal classification weight to important and unimportant switches. This is a plausible failure mode, not a causal diagnosis already proven.

Compare label imitation with a signal/rate-based training objective, or a combination of imitation and utility fine-tuning. Binary decisions require a stated discrete training estimator or relaxation, followed by evaluation of the actual hard bits. Under noisy observations, optimize a declared expected/worst-case utility over training uncertainties; do not quietly give inference true channels.

Add normalization/representation ablations such as referencing phases to the direct path, while handling near-zero direct paths explicitly. Select checkpoints on a validation communication objective consistent with the eventual task.

## Candidate research direction

Question: can a quantized controller allocate additional computation according to estimated utility, observation age and remaining deadline, improving delivered communication quality over fixed-cost neural and analytic controls?

This is a tentative engineering/evaluation opportunity. Embedded INT8, predictive control, MoE and budgeted refinement all have prior coverage. The interaction must be investigated rather than called first-of-kind.

Candidate flow:

1. Acquire the observations permitted by the task.
2. Produce a feasible cheap analytic or tiny-neural configuration.
3. Estimate the benefit of further refinement using only currently available observations.
4. If benefit is likely to justify the measured cost and deadline permits, run a bounded refinement.
5. Apply the selected hard configuration.

Possible expensive branches include a few optimization steps, a learned residual block, or a stronger neural expert. There is no reason to assume that the expensive branch must be a transformer.

A gate should estimate communication benefit, not simply use bitwise confidence. A highly confident classifier may still choose a poor phase pattern.

If channel acquisition dominates, consider a separate task of deciding when extra pilots/reconfiguration are worth their cost. Such a gate needs observable pilot/feedback inputs; it cannot assume full fresh CSI is available for free. This is a different task from reducing inference time and needs separate coverage and experiments.

## Staged experiment proposal

### Stage A: independent-snapshot diagnostic

Keep the old results intact. Create a new development protocol and an untouched evaluation sample before further tuning.

Compare estimated phase slicing, coordinate search, an exact binary solver for the applicable ideal setting, the existing MLP, a smaller MLP, and utility-trained variants. Use the same observations and response constraints for all deployable methods. Tiny-N enumeration checks implementations; true-channel solvers remain explicitly labeled references.

An AI need not beat the exact estimated-objective solver on its own objective. Under uncertainty, an AI might instead improve expected true utility through distributional learning, or provide a useful measured cost tradeoff. Both must be tested.

### Stage B: realistic deployment task

Choose a target scenario before claiming 6 GHz relevance. Define carrier frequency, bandwidth/subcarriers if relevant, geometry/path loss, temporal evolution, CSI acquisition, and frequency-dependent panel response. Use measured or justified ray-traced channels where available, with clear provenance. Setting a frequency label on the existing random coefficients is insufficient.

Hold out environments/trajectories, not random overlapping windows from the same trajectory. Add delay, calibration drift and unseen-noise probes.

### Stage C: deployment and conditional computation

Start with an available CPU/SBC implementation; choose an MCU only if the baseline quality/latency tradeoff warrants it. No device purchase is implied.

Measure FP32 and genuinely executed INT8 models at batch size one. Include feature preparation, quantize/dequantize operations, output packing, and dispatch. Compare all methods on the same target, thread count and workload. Report warm-up and cold-start separately.

For gating, compare always-cheap, always-refine, a heuristic gate, a random gate at matched average budget, and the learned gate. Include fixed compute/depth alternatives with comparable average cost. Report tail latency and deadline misses, not just average active layers.

Measure or explicitly model:
T_update = T_acquisition + T_preprocess + T_decision + T_transfer + T_settle.

Use delivered rate/goodput, outage or a declared reliability metric after accounting for observation aging and update overhead. Do not equate FLOPs, parameter count, CUDA batch throughput or model-file compression with end-to-end latency.

## Decision criteria

Proceed if the candidate produces a reproducible improvement in the quality/cost frontier, survives new environments/noise and has lower measured update cost on the intended device. Claim an end-to-end advantage only when acquisition, transfer and settling costs are included or explicitly separated as unmeasured.

If a simple analytic solver is faster and equally useful, retain that negative result and reconsider the task. Do not add architecture complexity to conceal a baseline advantage.

## Literature register

Citation counts below are Consensus snapshots retrieved 18 October 2026, not quality rankings. Search followed by fetch was completed for all eight entries. Publisher/author records take precedence for publication year and version.

[1] Luca Urbinati, Nicoló Decarli, Francesco Guidi, Anna Guerra, Barbara Mavì Masini, Alberto Zanella. 2026. IEEE Open Journal of the Communications Society 7, 4605–4622. 0 citations. DOI: 10.1109/OJCOMS.2026.3687306. [On-Device Deep Learning for RIS Beamforming: Design and Latency-Rate Trade-Offs](https://consensus.app/papers/ondevice-deep-learning-for-ris-beamforming-design-and-urbinati-decarli/f065a758c3fb5320ae9fa07cb330248f/?utm_source=chatgpt).

[2] S. R. M. I. U. Samaranayake, D. Walpita, R. A. R. Ranawaka, M. Maduranga, U. Wijewardhana, H. Aluvihare. 2026. MERCon, 548–553. 0 citations. DOI: 10.1109/MERCon71835.2026.11691528. [Edge-Native Graph Transformer Networks for Real-Time RIS Beamforming on Low-Cost Hardware](https://consensus.app/papers/edgenative-graph-transformer-networks-for-realtime-ris-samaranayake-walpita/c8b5203b7ae5506fa5a3c50a2f0a59ad/?utm_source=chatgpt).

[3] Saif A. Abdulhussien, Sarmad K. Ibrahim. 2026. Physical Communication 77, 103171. 0 citations. DOI: 10.1016/j.phycom.2026.103171. [Proactive orientation-aware reconfigurable intelligent surface reconfiguration via Attention-LSTM and direct phase computation](https://consensus.app/papers/proactive-orientationaware-reconfigurable-intelligent-abdulhussien-ibrahim/677eb6d460a054c7b9cc861ce09b074f/?utm_source=chatgpt). Consensus supplied metadata without an abstract; the publisher preview supplied the technical description.

[4] O. Yildiz. 2025. Electronics 14(22), 4421. 1 citation. DOI: 10.3390/electronics14224421. [Toward Intelligent and Sustainable Wireless Environments with Hybrid and AI-Enhanced RIS Strategies](https://consensus.app/papers/toward-intelligent-and-sustainable-wireless-yildiz/aa5e1aeb04d55b138d266dd90be06608/?utm_source=chatgpt).

[5] Yaowen Zhang, Kaiming Shen, Shuyi Ren, Xin Li, Xin Chen, Zhi-Quan Luo. IEEE Journal of Selected Topics in Signal Processing 16(5), 967–979, 2022; preprint 2021. 54 citations. DOI: 10.1109/JSTSP.2022.3176479. [Configuring Intelligent Reflecting Surface With Performance Guarantees: Optimal Beamforming](https://consensus.app/papers/configuring-intelligent-reflecting-surface-with-zhang-shen/919b848190695c53b1041b8298af6fad/?utm_source=chatgpt). Consensus lists 2021; the journal version is 2022.

[6] Kinza Shafique, Mohammad Alhassoun, Haitham H. Saleh. 2026. IEEE Access 14, 26683–26701. 0 citations. DOI: 10.1109/ACCESS.2026.3661864. [Turbo-FQCA: Budget Constrained RIS Phase Optimization With Robust Throughput and Minimal Overhead](https://consensus.app/papers/turbofqca-budget-constrained-ris-phase-optimization-with-shafique-alhassoun/07726976966c513aa4e540e1acfab0b1/?utm_source=chatgpt).

[7] Wenchao Xia, Yajing Jiang, Ben Zhao, Haitao Zhao, Hongbo Zhu. 2024 journal issue. IEEE Wireless Communications Letters 13, 515–519. 11 citations. DOI: 10.1109/LWC.2023.3334031. [Deep Unfolded Fractional Programming-Based Beamforming in RIS-Aided MISO Systems](https://consensus.app/papers/deep-unfolded-fractional-programmingbased-beamforming-xia-jiang/45d5fa0e802051b5b4ff44a86db51130/?utm_source=chatgpt). Abstract-level lead; full paper not audited.

[8] L. Mathias, Rafael Marasca Martins, Taufik Abrão. 2026. IEEE Wireless Communications Letters 15, 3581–3585. 0 citations. [A Closed-Loop Model Predictive Control for Beamforming in RIS-Aided Communications](https://consensus.app/papers/a-closedloop-model-predictive-control-for-beamforming-in-mathias-martins/7aaa5c375134568291409d3c1b75f699/?utm_source=chatgpt). Abstract-level lead; DOI not independently resolved here.

## Search limitations

Broad architecture/hardware/routing searches and targeted title/novelty reverse searches were performed through Consensus and primary web records. Two initial concurrent Consensus searches were rate-limited; later targeted searches succeeded. Some publisher opens were blocked, while indexed primary text or author/institution records were available. No paper results were reproduced. Absence from these searches is not proof of an uncovered research gap.
