# Source audit

Checked 21 October 2026. Sources below support prior-work descriptions, not the proposed controller's untested performance. No citation counts were retrieved or invented. Consensus search did not succeed: student returned an internal error and then an OAuth reauthentication error; helma and Primary returned reauthentication errors. The user authorized proceeding without it.

## Sources used

1. Zardi, Oliveri, Massa (2024), Memory-Enhanced Dynamic Evolutionary Control of Reconfigurable Intelligent Surfaces. DOI 10.1109/TAP.2024.3407964. Institutional publication record and abstract: https://iris.unitn.it/handle/11572/423050 ; author preprint: https://arxiv.org/abs/2309.04353 . Verified memory reuse, dynamic control, physical-response modeling, fixed BS strategy, worst-user throughput. A matched implementation in this proposal is explicitly an adaptation, not a completed reproduction. The proposed full-information benchmark must not be compared as an information-equivalent reproduction of the paper's cascaded-information setting.

2. Lange et al. (2023), Discovering Attention-Based Genetic Algorithms via Meta-Black-Box Optimization. DOI 10.1145/3583131.3590496. https://arxiv.org/abs/2304.03995 ; author paper https://human-competitive.org/sites/default/files/2023_gecco_lga.pdf . Abstract and author-paper search extract verify attention-based selection and mutation-rate adaptation. Does not establish absence of every atom-level operator in later literature.

3. Qian and Di Renzo, Mutual Coupling and Unit Cell Aware Optimization for Reconfigurable Intelligent Surfaces. https://arxiv.org/abs/2011.14373 . Primary abstract read. Cited as the verified 2020 preprint rather than relying on unchecked journal metadata. Establishes unit-cell/coupling-aware optimization is prior art.

4. Peng et al. (2024), RISnet. https://arxiv.org/abs/2403.04028 . Primary abstract verifies domain-informed neural architecture, mutual coupling, partial CSI, and joint precoding/RIS optimization. Proposal cites identified preprint, not an assumed final publication.

5. Liu et al. (2026), Physics Informed Generative Surrogate Learning for Full Wave Validated Real Time Beamforming in Programmable Metasurfaces. https://advanced.onlinelibrary.wiley.com/doi/10.1002/aelm.70480 . Publisher full-text search extract, including Section 3 and publication history (4 September 2026). Verified surrogate, binary aperture optimization, NSGA-II, and full-wave validation. No numerical performance claims are borrowed into the proposal. Distinguish structural/radiation-pattern design from the planned communication-rate mutation operator.

6. Urbinati et al. (2026), On-Device Deep Learning for RIS Beamforming: Design and Latency-Rate Trade-Offs. https://doi.org/10.1109/OJCOMS.2026.3687306 . IEEE indexed full text verified final title, publication 27 April 2026, volume 7, pages 4605–4622, codebook selection and MCU measurements. Direct IEEE document URL triggered bot verification, but the publisher DOI search result supplied full text. https://github.com/LucaUrbinati44/DL-on-RISC/ corroborates implementation; its README retains an older title/venue and is not used for final bibliographic details.

7. Martín-Martín et al. (2024), Hardware Implementations of a Deep Learning Approach to Optimal Configuration of Reconfigurable Intelligence Surfaces. https://www.mdpi.com/1424-8220/24/3/899/notes ; publisher PDF https://www.mdpi.com/1424-8220/24/3/899/pdf?version=1706614584 . Publisher notes and PDF search extract used; direct HTML returned rate limiting. Proposal describes learned binary configuration/hardware implementation at a broad level, without claiming CSI input or universal complement symmetry.

8. Zheng et al., Mutual Coupling in RIS-Aided Communication: Model Training and Experimental Validation. https://arxiv.org/abs/2311.10544 . Primary abstract read; submitted 2023, revised 2024. Scattering model, full-wave validation, fabricated 1-bit prototype. Cited as preprint; hardware evidence belongs to that paper, not this proposed study.

9. Zhang et al., Configuring Intelligent Reflecting Surface with Performance Guarantees: Optimal Beamforming. https://arxiv.org/abs/2112.02260 . Primary abstract and linked journal DOI 10.1109/JSTSP.2022.3176479 verified. Supports efficient optimal ideal binary single-user control. The nonideal two-state signed-sum reduction in Section 4 is independently derived algebra, with its assumptions explicitly stated.

10. DeepMIMO official repository/manual: https://github.com/DeepMIMO/DeepMIMO ; https://www.deepmimo.net/docs/tutorials/manual.html . Channel generation, geometry and ray information. Actual scenario selection and the availability of compatible RIS links are unresolved implementation milestones, not asserted dataset properties.

11. openEMS official source: https://github.com/thliebig/openEMS . Supports choice of open-source EC-FDTD tool; no claim of a completed solver setup.

12. openEMS boundary documentation: https://wiki.openems.de/index.php/FDTD_Boundary_Conditions.html . Lists PEC, PMC, MUR and PML. The proposal requires verification of needed periodic/oblique illumination support rather than claiming that symmetry boundaries universally replace it.

## Search coverage and unresolved leads

Searches included memory-enhanced evolutionary RIS control, RIS learned mutation attention, metasurface attention genetic mutation, unit-cell-aware optimization, RISnet, and physics-informed surrogate metasurfaces. This was targeted coverage, not a systematic review.

- `2D Mutation-Based Elitist Genetic Algorithm for Optimal Design of Transmissive Linear-to-Circular Polarization Conversion Metasurfaces`, Applied Sciences 15(20), 11265: https://www.mdpi.com/2076-3417/15/20/11265 . Publisher search extract indicates spatially aware mutation in geometry design. Full method comparison is still needed before any broad claim of first spatial mutation.
- `Synergistic integration of deep learning and genetic algorithms for autonomous metasurface design`, Diamond and Related Materials 168, 114031 (2026), DOI 10.1016/j.diamond.2026.114031. Publisher abstract indicates a CNN/GA structural-design framework. Full operator inspection remains outstanding; generic AI-plus-GA novelty is not claimed.
- Recent EM-aware end-to-end discrete-phase RIS learning should be included in a systematic follow-up review; the present proposal does not claim exhaustive novelty of physical conditioning.

## Input provenance

User draft: `/home/parasite/.codex/attachments/4ea681b2-a79c-4048-9af5-e78a1bdcadd6/Pasted text.txt`.

Referenced conversation: `6ad48b47-83b0-83ec-8a4e-24a040f65544`, title `Explain DeepMIMO Reranking`. Accessible user messages corroborated simulation-only scope and interest in physical meta-atom information; assistant messages were content-reference placeholders. This revision relies on the supplied full draft for detailed proposal context.

## Claim classification

- Established prior art: memory-based RIS evolution, unit-cell-aware optimization, attention genetic operators, neural RIS controllers, physics-informed metasurface surrogates.
- Proposed methodological contribution: physics-residual conditional edits in a matched memory-based RIS controller.
- Engineering contribution: validated propagation/response interface and reproducible benchmark.
- Unverified hypothesis: improvement in rate at a fixed deadline, hardware-response transfer, usefulness of attention.
- Outside evidence boundary: physical deployment, MCU efficiency, guaranteed optimality, full-array coupling without validation.
