# NeurRIS-1bit — evidence and gap revision (2 October 2026)

This is a preliminary, abstract-level gap analysis using research-gap-finder and Consensus. One manuscript/prototype is provided for this topic; the search is not a systematic literature review. Generic novelty is not inferred from missing search results.

## Problem framing
Does the small clean-target neural classifier improve true-channel SE over slice/coordinate policies using the same estimated CSI?

Scope: Analytic single-user independent Rician simulation with estimated cascade/direct CSI and two illustrative response settings. No measured unit cell, geometry, mutual coupling or pilot-contamination claim.

## Existing coverage and common routes
Discrete imperfect-CSI neural control, noisy-CSI FCNs and physics-consistent one-bit optimization are covered [12], [13], [14]. Generic 1-bit/noisy neural novelty is downgraded.

## Bottlenecks and controversy
The central bottleneck is a valid data/split/evaluation contract, followed by whether a more complex model earns its added cost. Model size, call counts, dataset-level accuracy and downstream utility are distinct measurements.

## Candidate gap and reverse-search outcome
Information-matched control and hardware-response transfer are tentative evaluation directions. Reverse search found robust discrete neural beamforming and practical-response methods, so the old broad novelty claim is rejected.

## Small falsifiable experiment
Estimated slice, estimated coordinate descent, random codes, clean coordinate reference, triangle upper bound; exact N=8 enumeration. Same test channels and noise across policies; paired bootstrap intervals.

## Risks and remaining evidence
The neural recipe loses to estimated-coordinate control. Clean coordinate search is not an exact oracle. CPU and CUDA batch timings are different regimes; their ratio is not a fair deployment speedup.

The current measured pilot is not proof of publication readiness. Venue deadlines, fees and submission rules were not revalidated in this research revision.

## Fetched literature
Reference numbers below match the workspace literature register.

[12] [A Robust Deep Learning-Based Beamforming Design for RIS-Assisted Multiuser MISO Communications With Practical Constraints](https://consensus.app/papers/a-robust-deep-learningbased-beamforming-design-for-xu-gan/8cfb28b1e0d75f998cf0497e7736fa3d/?utm_source=chatgpt). Wangyang Xu, Lu Gan, Chongwen Huang. 2021. IEEE Transactions on Cognitive Communications and Networking. Citations: 76 (retrieved 2 October 2026).

[13] [Neural Networks for Phase Shift Optimization of Reconfigurable Intelligent Surfaces Under Imperfect Channel State Information](https://consensus.app/papers/neural-networks-for-phase-shift-optimization-of-fondo-ferreiro-saghezchi/6d52afd7342757c092e5822643722c9a/?utm_source=chatgpt). Pablo Fondo-Ferreiro, Firooz B. Saghezchi, Felipe J. Gil-Castiñeira, Jonathan Rodriguez. 2025. IEEE Access. Citations: 5 (retrieved 2 October 2026).

[14] [Statistical Multiport-Network Modeling and Efficient Discrete Optimization of RIS](https://consensus.app/papers/statistical-multiportnetwork-modeling-and-efficient-hammami-magoarou/9afad547d28451d38a0c7389e32378c2/?utm_source=chatgpt). Cheima Hammami, Luc Le Magoarou, P. del Hougne. 2025. IEEE Wireless Communications Letters. Citations: 8 (retrieved 2 October 2026).

## Completed pilot outcome

All 18 tested seed/noise/response cases put neural SE below estimated-channel coordinate descent. Clean coordinate search is correctly labeled a reference; enumeration and a direct-path-aware triangle bound are verified.
