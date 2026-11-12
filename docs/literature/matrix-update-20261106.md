# Literature matrix update draft, 2026-11-06

Status: DRAFT for the user's review. Nothing has been written to the Google Sheet. New rows are also in `matrix-update-20261106.csv` (10 columns, numbered 29 to 42).

## 0. Basis and caveats

- Source of truth: Google Sheet `1Sa4wgYj23wOWy7-iLMHDoRCzCFPBmKHrnyzRfWbavOg`, Sheet1, read through the Drive connector on 2026-11-06. `read_file_content` returned only rows 1 to 15 as a "sample"; a CSV export returned all 28 rows as base64, which I did not decode in full. The "before" text for rows 16 to 28 is therefore taken from `docs/literature/coupling-temporal/matrix-new-rows.csv`, which matches the Sheet for rows 12 to 15 and, by spot check against the export, rows 24 and 28. **Diff the before-text against the live Sheet before any write.** The local `RIS Research.xlsx` was not used.
- Direction used: the project no longer proposes learned mutation guidance as its contribution. The question is whether exact, deadline-accounted pair (two-flip) search on a coupled multiport binary RIS can be improved algorithmically for a fixed-precoder worst-user rate (screened restarts, restart distribution, elite recombination, cross-frame memory, sound pruning), against a faithful ME-GA reimplementation, with learned ranking kept as a comparator. Source: `docs/novelty-analysis.md` and project direction plan.
- No results exist yet for this direction. No cell below states an improvement or any project result. A paper never justifies "novel"; every distinction is phrased as something to test.
- Tools: values from arXiv HTML pages were obtained through a summarizing fetch tool, not verbatim text. Anything that goes into a cell as a specific parameter (notably the Zardi parameters) should be double-checked against the paper once before writing.
- "Partly read" is a third status I used where I read selected full-text sections but not the whole paper. The Sheet only uses "Read" and "Not read" (the contract allowed "Read" or "Abstract only"). The user can map "Partly read" to either.
- The arXiv API queries I tried returned no entries, so they count as no evidence. "Not found" below means not found in the three web searches and the Consensus queries listed in section 4.

## (a) Claim verification

| Claim from the user | Paper | Verdict | Evidence and scope |
|---|---|---|---|
| "Uses iterative single-element flips to produce binary RIS configurations" | Martín-Martín et al. 2024, Sensors 24(3):899, matrix #1 | **Supported only for training labels, not for the proposed method** | Full text read (Europe PMC copy, PMC10857622). The deployed method is a supervised CNN that predicts 225 binary cell states in one pass. The labels come from an offline brute-force routine: start from a random 0/1 pattern, invert cells "cell by cell", keep an inversion if the energy in the target direction rises, otherwise revert, and sweep again until fewer than 10 percent of cells change in a sweep. The paper notes this is costly and unsuitable for real-time use. So the single-flip sweep is real but it is the label generator, not what the paper proposes. |
| "Uses one-flip and two-flip local search" | Goudet, Goëffon, Hao 2024, COR 168:106684 | **Supported, with qualifiers** | Full-text PDF, Sections 2.1, 3.2, 4.5. The algorithm (TS1\|2*) searches the union of the one-flip neighbourhood and a two-flip neighbourhood. The two-flip neighbourhood is restricted to pairs of variables with a non-zero interaction coefficient Q(i,j), and when the neighbourhood is dense (ratio above a threshold) the search falls back to one-flip tabu search. It is for UBQP/max-cut, not RIS. In the paper's equal-time comparison the two-flip variant improved five sparse instances by roughly 0.04 to 0.18 percent. Consequence for us: our coupled objective is dense, so Goudet's own scheme would not use the pair neighbourhood there; whether full pair scans pay off is something to test. |
| "Incorporates adaptive neighborhood search into RIS optimization" | Tarek et al., IEEE IoT J. 12(8):10012-10031 (DOI 10.1109/JIOT.2024.3508818) | **Supported as worded (abstract), but misleading as prior art for RIS state configuration** | Abstract only (full text closed). The abstract says the modified Aquila optimizer includes an adaptive neighbourhood search to refine solutions near the current best, and that the goal is to determine the optimal number of RISs and their installed positions, with average or worst-user (max-min) rate objectives, for 20 and 50 users. So it is deployment optimization, not bit configuration. Whether the paper does any element-level state search could not be confirmed. Year: the DOI is from 2024 but the issue is dated April 2025. |
| "Exploits structural properties of binary RIS configurations to reduce search complexity" | Gkekas et al., arXiv 2608.04133 | **Supported, with scope limits** | Full text read in part (model, Lemma 1, algorithms, simulations, limitations). Structure: every global optimum has signs equal to the signs of projections onto one common direction (necessary condition). SISO: at most N+1 candidates, exact. MIMO: random direction sampling with 1,000 samples, no guarantee. Assumptions: objective is the norm of the noise-free received CSI vector (a received-power objective); a single RIS with NT transmitters and NR receive antennas, transmit signals known and orthogonal, no BS precoder, no multiuser or worst-user objective; independent scalar cells, cascaded free-space channel, mutual coupling explicitly excluded; static channel; no deadlines or runtime accounting. Baselines are random sampling and a continuous-phase RIS. **Baseline for our objective: not directly.** Our objective is a minimum over users with a fixed precoder on a coupled network, not a norm of a signed sum; I found no statement that Lemma 1 carries over, and the paper's argument (a sign that disagrees with its projection can be flipped to increase the norm) relies on the norm structure. That is my inference, not the paper's. It could serve as a sampling comparator in a single-user, uncoupled sanity case. |

Corrections to the user's shorthand: the paper listed as "optimal search for discrete beamforming" (arXiv 2507.07342) is titled "Discrete Beamforming Optimization for RISs with a Limited Phase Range and Amplitude Attenuation". Prod'homme and del Hougne 2023 is already row 28 (DOI 10.1109/lcomm.2023.3330527), so no new row.

## (b) New rows

Rows are numbered from 29. Dedupe: checked against rows 1 to 28 by DOI and by title; no duplicates among the rows below. Prod'homme and del Hougne is row 28, so it is not repeated.

14 new rows. Rows 29 to 37 are the nine requested candidates that were not already in the Sheet (Goudet, Tarek, 2608.04133, Panuganti, Hama, 2511.05132, 2507.07342, Lim, Zhao); the tenth, Prod'homme and del Hougne, is the duplicate. Rows 38 to 42 come from the targeted searches listed at the end of this file.

| No. | Paper | Record checked against | Status to write |
|---|---|---|---|
| 29 | A large population island framework for the unconstrained binary quadratic problem | pdftotext of https://leria-info.univ-angers.fr/~jinkao.hao/papers/GoudetGoeffonHaoCOR2024.pdf. Record (volume 168, article 106684, Aug 2024) confirmed by Crossref. | Partly read |
| 30 | Integrating Reconfigurable Intelligent Surface and Modified Aquila Optimization for Enhancing Wireless Communication Capacity | Crossref record (DOI registered 2024, issue 12(8), 15 Apr 2025) and Semantic Scholar abstract. Open-access PDF status CLOSED. Year given as 2025 (issue date); DOI prefix says 2024. | Abstract only |
| 31 | Geometry-Informed Optimization of Binary RIS Configurations for Communication and Sensing | WebFetch of arxiv.org/html/2608.04133v1 plus pdftotext keyword checks (precoder, coupling, user, flip) on arxiv.org/pdf/2608.04133. Authors from arXiv abs page. | Partly read |
| 32 | Impact of Metaheuristic Optimization Algorithms on Wireless Network Coverage Enhancement With Reconfigurable Intelligent Surfaces | Consensus abstract; Crossref record (published 16 Feb 2025, 38(5), e70026). | Abstract only |
| 33 | Scalable and Near-Optimal Discrete Phase Shift Optimization for Reconfigurable Intelligent Surfaces with Over 20,000 Elements | pdftotext of arxiv.org/pdf/2603.29144; keyword checks (flip, local search, coupling, user). | Abstract only |
| 34 | Near-Optimal Reconfigurable Intelligent Surface Configuration: Blind Beamforming with Sensing | pdftotext of arxiv.org/pdf/2511.05132 (v2). | Abstract only |
| 35 | Discrete Beamforming Optimization for RISs with a Limited Phase Range and Amplitude Attenuation | pdftotext of arxiv.org/pdf/2507.07342. The title differs from the shorthand 'optimal search for discrete beamforming'. | Abstract only |
| 36 | Quantum-Assisted Combinatorial Optimization for Reconfigurable Intelligent Surfaces in Smart Electromagnetic Environments | Consensus abstract; Crossref record (72(1), Jan 2024, 147-159). | Abstract only |
| 37 | Optimal Passive Beamforming for Reconfigurable Intelligent Surface-Assisted Communications With Discrete Phase Shifts | Consensus abstract; Crossref record (13(2), Feb 2024, 427-431). | Abstract only |
| 38 | Site-Specific Channel Modeling and Optimization of RIS-Assisted Multiuser MISO Systems | pdftotext of arxiv.org/pdf/2603.21433 (v1) and Crossref record (7(4), Aug 2026). Surfaced by web search for the max-min objective. | Abstract only |
| 39 | Hybrid Beamforming for RIS-Aided Communications: Fitness Landscape Analysis and Niching Genetic Algorithm | pdftotext of arxiv.org/pdf/2109.09054; journal record from Crossref (131, Dec 2022). | Abstract only |
| 40 | Optimal Discrete Beamforming of RIS-Aided Wireless Communications: An Inner Product Maximization Approach | pdftotext of arxiv.org/pdf/2211.04167 (abstract); Crossref record for the WCNC version. | Abstract only |
| 41 | Physics-Informed Metaheuristics for Fast RIS Codebook Compilation | Consensus abstract; Crossref record (62(11), Nov 2024, 152-158). | Abstract only |
| 42 | Electromagnetically Consistent Bounds on Information Transfer in Real-World RIS-Parametrized Wireless Channels | pdftotext of arxiv.org/pdf/2601.20017 (v1). | Abstract only |


How "Read" was judged: nothing below is marked plain "Read". I read full text only in part for Goudet and 2608.04133; everything else is abstract-level, with keyword checks on arXiv full text where noted.

### Row 29. A large population island framework for the unconstrained binary quadratic problem

- How read and verified: pdftotext of https://leria-info.univ-angers.fr/~jinkao.hao/papers/GoudetGoeffonHaoCOR2024.pdf. Record (volume 168, article 106684, Aug 2024) confirmed by Crossref.
- Reading status to write: Partly read (full text of author-hosted PDF: abstract, introduction, Section 3.2 neighbourhoods, Section 4.5 results; island/pairing experiments not read in detail)

- **Authors:** Olivier Goudet; Adrien Goëffon; Jin-Kao Hao
- **Publication year:** 2024
- **DOI link:** https://doi.org/10.1016/j.cor.2024.106684
- **Research gap:** Addressed: one-flip and sparse two-flip tabu search inside a large-population island evolutionary algorithm, on unconstrained binary quadratic problems (UBQP/max-cut), not RIS. Current comparison: direct prior art for pair-flip moves, local-search restarts from a population and recombination of local optima, so none of these can be called novel in a RIS paper. Its two-flip moves are limited to pairs with non-zero Q(i,j) and the search reverts to one-flip when the neighbourhood is dense. Whether exhaustive pair scans stay affordable on our dense coupled-impedance objective, and whether a worst-user rate (not a quadratic form) behaves like a UBQP, are things to test, not assumptions.
- **Source / journal:** Computers & Operations Research, 168, 106684
- **Dataset and methods:** Three UBQP benchmark families (Beasley-type p3000-p7000, 3D Ising n=2744, max-cut G-set). Very large population split into islands; each individual improved by a one-or-two-flip tabu search (TS1|2*, union of both neighbourhoods, incremental delta evaluation); new pairing and recombination method; migration topologies. In the paper's equal-time comparison on five sparse G-set instances the two-flip variant gains roughly 0.04-0.18 percent; new bounds reported for hard max-cut instances. Numbers taken from the author-hosted preprint PDF; check against the published version before citing.
- **Relevance to the proposed research:** Closest algorithmic prior art for the pair-search direction (pair flips + tabu + population recombination + elite restarts). Use it to fix what 'screened restarts' and 'elite recombination' already mean in the literature, and to compare design choices (density-based fallback to one-flip, tabu tenure tied to neighbourhood size). Not an RIS baseline; a faithful port to our objective could be a further comparator, to be decided.

### Row 30. Integrating Reconfigurable Intelligent Surface and Modified Aquila Optimization for Enhancing Wireless Communication Capacity

- How read and verified: Crossref record (DOI registered 2024, issue 12(8), 15 Apr 2025) and Semantic Scholar abstract. Open-access PDF status CLOSED. Year given as 2025 (issue date); DOI prefix says 2024.
- Reading status to write: Abstract only

- **Authors:** Zahraa Tarek; Mona G. Gafar; Shahenda Sarhan; Abdullah M. Shaheen; Ahmed S. Alwakeel
- **Publication year:** 2025
- **DOI link:** https://doi.org/10.1109/JIOT.2024.3508818
- **Research gap:** Addressed: a modified Aquila optimizer with an adaptive neighbourhood search, used to decide the number and installed positions of RISs so as to maximize the average or the worst (max-min) achievable user rate in multiuser systems with 20 and 50 users. Current comparison: the abstract describes RIS deployment (number and placement), not the binary state configuration of the elements, so it says nothing about pair flips on a fixed surface. The 'adaptive neighbourhood search' is an exploitation step inside an Aquila-type metaheuristic. Full text was not accessible (closed), so whether any element-level state search appears is unverified.
- **Source / journal:** IEEE Internet of Things Journal, 12(8), 10012-10031
- **Dataset and methods:** From the abstract only: multiuser wireless systems with 20 and 50 users; compared with AOA, GWO, JFSOA, AJFSOA, PSO and DE; abstract claims 16-38 percent higher max-min achievable rate for 20 users (not checked).
- **Relevance to the proposed research:** Peripheral. Shows that max-min rate objectives and neighbourhood-search metaheuristics appear in the RIS literature, but for deployment optimization. Not a baseline for element configuration; keep out of core related work unless the full text shows element-level search.

### Row 31. Geometry-Informed Optimization of Binary RIS Configurations for Communication and Sensing

- How read and verified: WebFetch of arxiv.org/html/2608.04133v1 plus pdftotext keyword checks (precoder, coupling, user, flip) on arxiv.org/pdf/2608.04133. Authors from arXiv abs page.
- Reading status to write: Partly read (full text via arXiv HTML and PDF: model, Lemma 1, algorithms, simulations, stated limitations; proofs not checked)

- **Authors:** Angelos Gkekas; Alexandros I. Papadopoulos; Petros Andreas Pantazopoulos; Antonios Lalas; Konstantinos Votis; Christos Liaskos
- **Publication year:** 2026
- **DOI link:** https://doi.org/10.48550/arXiv.2608.04133
- **Research gap:** Addressed: structure of 1-bit RIS configuration for received-power maximization, written as maximizing the norm of a signed sum of channel vectors; exact SISO enumeration of at most N+1 candidates, a sampling method for MIMO, and an ISAC extension. Current comparison: it assumes one aggregate norm objective, known orthogonal transmit signals with no precoder, no multiuser or worst-user objective, independent scalar cells with no mutual coupling, and static channels without deadlines. Our objective (fixed-precoder worst-user rate on a coupled multiport model) is not shown to share this structure, so its pruning is not assumed to transfer; whether an analogous sound pruning exists for our objective is a thing to test.
- **Source / journal:** arXiv:2608.04133 [cs.IT], v1, 4 Aug 2026 (peer-review status not verified)
- **Dataset and methods:** Free-space scalar channels; 8x8 and 16x16 RIS; NT in {1,5,9}, NR up to 10; sampling budget 1000; baselines are uniform random sampling at equal budget and an ideal continuous-phase RIS; ISAC with 100 random targets. Lemma 1: at a global optimum each sign equals the sign of the projection on the optimal sum vector (necessary, not sufficient). MIMO sampling has no local search and no optimality guarantee; no run statistics reported.
- **Relevance to the proposed research:** Closest recent structural-pruning idea, hence a novelty boundary for 'sound pruning'. As a baseline it fits only where the evaluator reduces to norm maximization, which ours does not by default (minimum over users, fixed precoder, coupled network). It could serve as a sampling comparator on a single-user, uncoupled sanity case. Applicability to a max-min objective is not established (our inference, not a statement of the paper).

### Row 32. Impact of Metaheuristic Optimization Algorithms on Wireless Network Coverage Enhancement With Reconfigurable Intelligent Surfaces

- How read and verified: Consensus abstract; Crossref record (published 16 Feb 2025, 38(5), e70026).
- Reading status to write: Abstract only

- **Authors:** Nitin Panuganti; Ranjan; Shukla (given names of co-authors unverified; Crossref family names Panuganti, Ranjan, Shukla)
- **Publication year:** 2025
- **DOI link:** https://doi.org/10.1002/dac.70026
- **Research gap:** Addressed: comparison of nine metaheuristics (GA, cuckoo search, harmony search, ant colony, differential evolution, dual annealing, gradient descent, tabu search, bee algorithm) for RIS configuration, judged by received signal strength and coverage. Current comparison: per the abstract, tabu search is one entry in a broad comparison. Whether it uses pair flips, 1-bit states, a coupled model or deadlines cannot be seen from the abstract (unverified).
- **Source / journal:** International Journal of Communication Systems, 38(5), e70026
- **Dataset and methods:** Abstract only: simulation comparison of the listed algorithms; dataset and channel model unverified.
- **Relevance to the proposed research:** Evidence that tabu search on RIS is already studied generically. Read the full text before deciding whether it counts as tabu prior art for binary RIS. Not a baseline until its objective and move set are known.

### Row 33. Scalable and Near-Optimal Discrete Phase Shift Optimization for Reconfigurable Intelligent Surfaces with Over 20,000 Elements

- How read and verified: pdftotext of arxiv.org/pdf/2603.29144; keyword checks (flip, local search, coupling, user).
- Reading status to write: Abstract only (abstract read; full text only keyword-searched)

- **Authors:** Yuto Hama; Daisuke Kitayama; Kensuke Inaba; Toshimori Honjo; Hiroki Takesue; Naoki Ishikawa; Hiroyuki Takahashi
- **Publication year:** 2026
- **DOI link:** https://doi.org/10.48550/arXiv.2603.29144
- **Research gap:** Addressed: binary and quaternary RIS phase optimization written as a quadratic Ising model and solved on a coherent Ising machine (CIM) for up to 22,201 elements, with a spin-size reduction that removes spins fixed by dominant channel components in line-of-sight. Current comparison: the text describes a single-user MISO link with maximum-ratio transmission and no mutual coupling or worst-user objective; it is an Ising/QUBO route to discrete RIS search, not a flip-neighbourhood heuristic. Whether its spin-fixing idea has a counterpart under coupling is a thing to test.
- **Source / journal:** arXiv:2603.29144 [cs.IT], v1, 31 Mar 2026 (peer-review status not verified)
- **Dataset and methods:** Quadratic Ising formulation; real-hardware CIM experiments; geometric LoS and NLoS evaluation (BS with 64 antennas, one single-antenna user, per the parameter table).
- **Relevance to the proposed research:** Context for Ising/QUBO solvers as an alternative to flip-based search, and a precedent for deterministic variable fixing as problem reduction. Not a comparator for a coupled multiport worst-user objective.

### Row 34. Near-Optimal Reconfigurable Intelligent Surface Configuration: Blind Beamforming with Sensing

- How read and verified: pdftotext of arxiv.org/pdf/2511.05132 (v2).
- Reading status to write: Abstract only (abstract read; full text only keyword-searched)

- **Authors:** Son Dinh-Van; Nam Phuong Tran; Matthew D. Higgins
- **Publication year:** 2025
- **DOI link:** https://doi.org/10.48550/arXiv.2511.05132
- **Research gap:** Addressed: blind (CSI-free) configuration of a binary RIS in a SISO link from received-signal-strength measurements: a quadratic model of the received SNR is estimated, then optimized; simulations and a field test. Current comparison: SISO only; the multiuser extension is an alternating heuristic. No mutual coupling and no fixed-precoder worst-user rate. Its measurement-driven setting differs from our known-evaluator, deadline-limited search.
- **Source / journal:** arXiv:2511.05132 [eess.SP], v2 20 Aug 2026 (first posted Nov 2025; peer-review status not verified)
- **Dataset and methods:** Sensing stage with random binary configurations and RSS; optimization stage enumerating arcs of flip points (SISO case, O(N)); baselines RFocus, CSM, GCSM, MV-CSM; field test in a manufacturing building plus simulations.
- **Relevance to the proposed research:** Shows exploitation of quadratic structure in binary RIS configuration. Relevant only if our work adds measurement-based variants; low priority for the main comparison.

### Row 35. Discrete Beamforming Optimization for RISs with a Limited Phase Range and Amplitude Attenuation

- How read and verified: pdftotext of arxiv.org/pdf/2507.07342. The title differs from the shorthand 'optimal search for discrete beamforming'.
- Reading status to write: Abstract only (abstract read; full text only keyword-searched)

- **Authors:** Dogan Kutay Pekcan; Hongyi Liao; Ender Ayanoglu
- **Publication year:** 2025
- **DOI link:** https://doi.org/10.48550/arXiv.2507.07342
- **Research gap:** Addressed: single-user received-power maximization with phase-dependent amplitude and discrete phases over a limited range; necessary and sufficient optimality conditions and an optimal search that finishes within at most N*K steps, plus quantization schemes. Current comparison: exact linear-time optimum for a single-user power objective; keyword search of the text found no multiuser, coupling or flip-search content. A 2^N count therefore does not by itself motivate heuristics for single-user control; our harder objective must be demonstrated.
- **Source / journal:** arXiv:2507.07342 [cs.ET], v1, 9 Jul 2025 (publication status not verified)
- **Dataset and methods:** Analytical derivation; optimal search algorithm; validation against exhaustive search at N=10 with 1,000 channel realizations; APQ/EAPQ quantization schemes.
- **Relevance to the proposed research:** Companion to row 11 as an exact single-user reference. Our search should recover the known optimum on a single-user, uncoupled sanity case.

### Row 36. Quantum-Assisted Combinatorial Optimization for Reconfigurable Intelligent Surfaces in Smart Electromagnetic Environments

- How read and verified: Consensus abstract; Crossref record (72(1), Jan 2024, 147-159).
- Reading status to write: Abstract only

- **Authors:** Q. Lim; Ross; Ghosh; Vook; Gradoni; Peng (Crossref family names; given names unverified)
- **Publication year:** 2024
- **DOI link:** https://doi.org/10.1109/tap.2023.3298134
- **Research gap:** Addressed: mapping EM scattered power to an Ising Hamiltonian so that RIS phase configuration becomes a ground-state problem for adiabatic quantum computing; demonstrated for weighted beamforming and diffuse scattering. Current comparison: Ising/QUBO formulation of binary configuration search; the abstract states no worst-user or fixed-precoder objective. Whether the pair interactions of our coupled objective admit a similar quadratic form is unverified.
- **Source / journal:** IEEE Transactions on Antennas and Propagation, 72(1), 147-159
- **Dataset and methods:** From the abstract: statistical-mechanics analogy of correlated spins, adiabatic quantum computing; demonstrations on weighted beamforming and diffusive scattering.
- **Relevance to the proposed research:** Alternative solver family for binary RIS configuration; cite as related work. No comparison planned.

### Row 37. Optimal Passive Beamforming for Reconfigurable Intelligent Surface-Assisted Communications With Discrete Phase Shifts

- How read and verified: Consensus abstract; Crossref record (13(2), Feb 2024, 427-431).
- Reading status to write: Abstract only

- **Authors:** Donglai Zhao; Wang; Wang; Wang (Crossref family names; given names of co-authors unverified)
- **Publication year:** 2024
- **DOI link:** https://doi.org/10.1109/lwc.2023.3331232
- **Research gap:** Addressed: optimal discrete-phase passive beamforming gain by turning the multi-ary problem into an equivalent binary one and running a linear search over the optimal phase of the superimposed channel; simulations show global optimality; reports that 3-bit phase shifters come close to continuous phase. Current comparison: exact single-link result in the same family as rows 11 and 35; the abstract does not cover multiuser, coupled or max-min settings.
- **Source / journal:** IEEE Wireless Communications Letters, 13(2), 427-431
- **Dataset and methods:** From the abstract: theoretical transformation to a binary phase problem; linear search with iterative operations for linear complexity; simulation comparison with existing algorithms.
- **Relevance to the proposed research:** Another exact single-user reference. Supports the point that search-space size alone does not justify heuristics for single-user control.

### Row 38. Site-Specific Channel Modeling and Optimization of RIS-Assisted Multiuser MISO Systems

- How read and verified: pdftotext of arxiv.org/pdf/2603.21433 (v1) and Crossref record (7(4), Aug 2026). Surfaced by web search for the max-min objective.
- Reading status to write: Abstract only (abstract read; full text only keyword-searched)

- **Authors:** Ziqi Liu; Wei Yu; Sean Victor Hum
- **Publication year:** 2026
- **DOI link:** https://doi.org/10.1109/ojap.2026.3696522
- **Research gap:** Addressed: site-specific RIS-assisted MU-MISO model combining ray tracing and full-wave analysis, with mutual coupling through a non-diagonal load-impedance matrix; alternating optimization of the BS beamformer and RIS loads for max-min achievable rate; a column-paired 1-bit RIS (10 pairs, 1,024 configurations) evaluated exhaustively in simulation and measurement. Current comparison: closest setting match (max-min rate, coupling, 1-bit loads), but it re-optimizes the beamformer jointly, uses continuous loads in its main mode, and enumerates only 1,024 states. No pair-flip search, restarts or deadline accounting were found in the passages checked. It offers a small-N exhaustive-enumeration regime for checking a search, not a large-N baseline.
- **Source / journal:** IEEE Open Journal of Antennas and Propagation, 7(4), 1356-1369; arXiv:2603.21433
- **Dataset and methods:** Hybrid ray tracing and full-wave EM; non-diagonal load-impedance model; Algorithm 1 alternating optimization; continuous and column-paired 1-bit modes; histogram of minimum rates over all 1,024 configurations; measurement validation (per abstract).
- **Relevance to the proposed research:** Reference for a coupled max-min model with 1-bit loads and for an exhaustive-enumeration protocol that could validate best-known references on small instances. Its objective differs from ours (joint beamformer, not fixed precoder).

### Row 39. Hybrid Beamforming for RIS-Aided Communications: Fitness Landscape Analysis and Niching Genetic Algorithm

- How read and verified: pdftotext of arxiv.org/pdf/2109.09054; journal record from Crossref (131, Dec 2022).
- Reading status to write: Abstract only (abstract and introduction)

- **Authors:** Bai Yan; Qi Zhao; Jin Zhang; J. Andrew Zhang; Xin Yao (arXiv v1 list; the published version has six authors, family names Yan, Zhao, Li, Zhang, Zhang, Yao)
- **Publication year:** 2022
- **DOI link:** https://doi.org/10.1016/j.asoc.2022.109725
- **Research gap:** Addressed: fitness-landscape analysis (fitness-distance correlation, autocorrelation) of joint BS-beamforming and discrete-phase sum-rate maximization, reporting a rugged multimodal landscape with many local peaks especially for large RISs, and a niching genetic algorithm. Current comparison: indirect evidence that restart distribution and diversity matter. Its objective is sum rate with joint beamforming, not fixed-precoder worst-user rate, and it uses no pair-flip local search. Whether our worst-user landscape is similarly rugged is to be measured, not assumed.
- **Source / journal:** Applied Soft Computing, 131, 109725; arXiv:2109.09054
- **Dataset and methods:** From the abstract and introduction: landscape analysis on sum-rate problems; niching GA with nearest-better clustering; discrete RIS phases.
- **Relevance to the proposed research:** Motivates measuring local-optima structure before tuning restarts. Cite as landscape evidence for the restart-distribution question; not a baseline.

### Row 40. Optimal Discrete Beamforming of RIS-Aided Wireless Communications: An Inner Product Maximization Approach

- How read and verified: pdftotext of arxiv.org/pdf/2211.04167 (abstract); Crossref record for the WCNC version.
- Reading status to write: Abstract only

- **Authors:** Rujing Xiong; Xuehui Dong; Tiebin Mi; Kai Wan; Robert Caiming Qiu
- **Publication year:** 2024
- **DOI link:** https://doi.org/10.1109/wcnc57260.2024.10571003
- **Research gap:** Addressed: exact divide-and-sort search for discrete-phase RIS in MISO systems, posed as inner-product maximization, with complexity linear in the number of phase levels and elements instead of exhaustive. Current comparison: global optimum for its single-link inner-product objective; the abstract does not cover coupling or worst-user objectives.
- **Source / journal:** 2024 IEEE Wireless Communications and Networking Conference (WCNC); arXiv:2211.04167
- **Dataset and methods:** From the abstract: discrete inner-product maximization; divide-and-sort search; numerical and real-device experiments.
- **Relevance to the proposed research:** Another exact discrete single-link reference; strengthens the point that hardness must be shown for our objective.

### Row 41. Physics-Informed Metaheuristics for Fast RIS Codebook Compilation

- How read and verified: Consensus abstract; Crossref record (62(11), Nov 2024, 152-158).
- Reading status to write: Abstract only

- **Authors:** Alexandros I. Papadopoulos et al. (co-author given names not captured; Crossref family names include Raptis, Lalas, Votis, Tyrovolas, Tegos, Pitilakis, Ioannidis, Karagiannidis)
- **Publication year:** 2024
- **DOI link:** https://doi.org/10.1109/mcom.001.2300582
- **Research gap:** Addressed: injecting RIS physics (micro-to-macro correlations, geometric optics, EM simulators) into well-known metaheuristics to cut offline RIS codebook compilation time. Current comparison: the abstract does not mention exact flip-gain updates, pair search, a coupled multiport model or worst-user rate. It shows that physics-aware metaheuristics exist, which bears on the comparison of learned and analytical ranking; details unverified.
- **Source / journal:** IEEE Communications Magazine, 62(11), 152-158
- **Dataset and methods:** Abstract only: metaheuristic optimizers with RIS physics attributes; evaluated on codebook compilation time.
- **Relevance to the proposed research:** Related work for physics-aware search heuristics; read the full text before using it as a comparator.

### Row 42. Electromagnetically Consistent Bounds on Information Transfer in Real-World RIS-Parametrized Wireless Channels

- How read and verified: pdftotext of arxiv.org/pdf/2601.20017 (v1).
- Reading status to write: Abstract only (abstract and the coordinate-descent and GA method passages read)

- **Authors:** Albert Salmi; Ville Viikari; Philipp del Hougne
- **Publication year:** 2026
- **DOI link:** https://doi.org/10.48550/arXiv.2601.20017
- **Research gap:** Addressed: semidefinite-relaxation upper bound on the SISO channel gain of a 1-bit-programmable RIS under a rigorous multiport (mutual-coupling-aware) model, applied to numerical and experimental examples and compared with four discrete optimizers (genetic algorithm, coordinate descent, exhaustive search where feasible, projected SDR solution). Current comparison: SISO only. Its coordinate descent starts from the best of 100 random binary configurations, flips each element in turn and evaluates each flip with the Woodbury identity, so single-flip search with Woodbury evaluation under coupling is already published. It reports reaching at least 64 percent (often 100 percent) of its bound. A bound for our two-user fixed-precoder max-min objective is not provided; adapting one is a thing to test.
- **Source / journal:** arXiv:2601.20017 [eess.SP], v1, 27 Jan 2026 (peer-review status not verified)
- **Dataset and methods:** Rigorous multiport network model of a SISO channel with 1-bit loads; QCQP lifted to an SDP; numerical and experimental RIS-parametrized environments; baselines GA, coordinate descent (random-start, single-flip, Woodbury), exhaustive search, projected SDR.
- **Relevance to the proposed research:** Closest prior art for Woodbury-accelerated single-flip search under coupling, and a source of an optimality-gap method for small SISO cases. Use as a reference point when stating what is new about pair search or cross-frame Woodbury memory (to be tested, not assumed). Also relevant for gap-to-reference reporting.


## (c) Cell-by-cell edits to existing rows 1 to 28

Principle: replace statements that present learned mutation guidance as "our proposal" with the pair-search question; keep every statement about the cited paper that is accurate. Cells not listed are unchanged.

### Row 1 (Martín-Martín et al. 2024)

Research gap (F), before:
> Addressed: efficient neural RIS-pattern prediction on edge hardware.
> Current comparison: direct target-direction prediction differs from physically conditioned mutation guidance inside an evolving population; use a matched task before comparing performance.

After:
> Addressed: efficient neural RIS-pattern prediction on edge hardware.
> Current comparison: direct target-direction prediction differs from exact pair search on a coupled multiport model with a fixed-precoder worst-user objective; use a matched task before comparing performance. Its training labels come from an offline cell-by-cell inversion sweep, which is single-flip local search used for label generation, not a deployed search.

Dataset and methods (H), before: "...Loss accounts for complementary valid patterns under its model. FP32/INT8 implementations evaluated on edge processors, TPU and FPGA platforms."
After: append at the end: " Training labels were generated offline by a cell-by-cell inversion sweep from a random 0/1 start, repeated until fewer than 10 percent of cells change in a sweep (checked in the open-access full text)."

Relevance (I), before:
> Direct-prediction control for the revised proposal. Tests whether one-pass prediction plus equal-budget local refinement is sufficient, without evolutionary mutation guidance. Check complement symmetry before reusing its training loss.

After:
> Direct-prediction comparator. Tests whether one-pass prediction plus equal-budget local refinement is sufficient compared with exact pair search. Its label-generation sweep is single-flip prior art for configuration search. Check complement symmetry before reusing its training loss.

Reading status (J): stays "Read" (I read the open-access full text).

### Row 2 (Xu, Gan, Huang 2022)

Research gap (F), before: "...Current comparison: our proposed fixed-precoder worst-user objective and learned mutation policy differ from its joint weighted-sum-rate optimizer; conclusions require compatible objectives and observations."
After: "...Current comparison: our fixed-precoder worst-user objective and pair-search algorithms differ from its joint weighted-sum-rate optimizer; conclusions require compatible objectives and observations."

### Row 3 (Padial-Allué et al. 2026)

Research gap (F), before: "...Current comparison: FPGA throughput does not establish the benefit or software cost of an iterative attention-guided mutation operator."
After: "...Current comparison: FPGA throughput does not establish the benefit or software cost of iterative pair search on a coupled model."

### Row 4 (Urbinati et al. 2026)

Research gap (F), before: "...Current comparison: our proposal concerns software evolutionary adaptation using physical-response descriptors; embedded inference alone is already established."
After: "...Current comparison: our proposal concerns software search for a fixed-precoder worst-user objective on a coupled multiport model under complete-runtime deadlines; embedded inference alone is already established."

### Row 5 (Zardi, Oliveri, Massa 2024): correction plus direction change

Verification (arXiv 2309.04353, HTML, 2026-11-06, via a summarizing fetch tool; re-check parameters against the paper before writing):
- The BS zero-forcing beamformer is not fixed. Eq. (10) defines A_ZF as the Moore-Penrose pseudo-inverse of the discretized cascaded Green's matrix of the current time instant, which depends on the RIS state, so it is recomputed at every time step.
- Specified: 3.5 GHz; BS of 30x30 half-wavelength antennas (900); wall 6x7 m, 0.2 m thick, relative permittivity 5.24, conductivity 0.123 S/m; RIS of 45x45 = 2,025 meta-atoms with 3 bits (8 states) per unit cell; transmit power 46 dBm, noise -96 dBm; 3 users in the aperiodic case; 100 time instants; population 100, at most 100 iterations, observation window 3; adaptive probabilities rho in [0.02, 0.06] and psi in [0.6, 0.95]; maximum replacement, storage and restore caps all 0.2; sigma_max = 1. Fitness is the inverse of the worst-user quantity. Initial states are random.
- Not specified in the text I read: crossover and mutation operators, parent selection, memory size, stagnation threshold delta. The roles of rho and psi as mutation and crossover probabilities were not confirmed in the text I read. The text gives the BS height inconsistently ("55 m" versus coordinates implying 5 m), probably an extraction error.
- Reports no numeric throughput and no latency or runtime; results appear only in figures. The only timing-related statement is qualitative (faster convergence).
- The memory step is as follows: an indicator over the observation window decides between storing the iteration's best individual with some probability and restoring the best memory entry over the worst individual with some probability. Eq. (9) is partly circular (the cascaded matrix is written in terms of excitations that the ZF step produces).

Research gap (F), before:
> Addressed: dynamic RIS optimization using evolutionary memory and electromagnetic meta-atom responses.
> Proposed distinction to test: physically conditioned, element-level mutation guidance inside an otherwise matched memory-enhanced GA; this is a candidate contribution, not a verified literature-wide gap.

After:
> Addressed: dynamic RIS optimization using evolutionary memory and electromagnetic meta-atom responses.
> Distinction to test: whether exact, deadline-accounted pair search with screened restarts, elite recombination and cross-frame memory can match or beat a faithful reimplementation of this memory-enhanced GA on a coupled multiport 1-bit model. The paper reports no numeric throughput or latency, so there are no published numbers to compare with. This is a candidate question, not a verified literature-wide gap.

Dataset and methods (H), before:
> Numerical dynamic multiuser communication scenarios; memory-enhanced genetic/evolutionary search maximizes worst-user throughput with fixed BS beamforming. EM-characterized meta-atom responses are included. The method does not require separately known BS–RIS and RIS–user partial Green's matrices.

After:
> Numerical dynamic multiuser communication scenarios; memory-enhanced genetic search maximizes worst-user throughput. The BS zero-forcing beamformer is recomputed at every time step as the pseudo-inverse of the discretized cascaded Green's matrix of the current RIS state (Eq. 10), so the precoder is not fixed. Stated parameters: 3.5 GHz; 30x30 BS array (900 antennas); 45x45 RIS (2,025 meta-atoms) with a 3-bit (8-state) unit cell; 3 users; 100 time instants; population 100, up to 100 iterations, observation window 3; adaptive probabilities in [0.02, 0.06] and [0.6, 0.95]; replacement, storage and restore caps 0.2. Not specified: crossover and mutation operators, parent selection, memory size, stagnation threshold. Results appear only in figures; no numeric throughput and no latency or runtime. EM-characterized meta-atom responses are included; the method does not require separately known BS–RIS and RIS–user partial Green's matrices.

Relevance (I), before:
> Primary evolutionary baseline. Reproduce where feasible or explicitly label our implementation an adaptation. Keep memory, population operators, evaluator and observations matched when isolating learned mutation locations.

After:
> Primary evolutionary baseline. Reimplement from the published specification and call it a reimplementation, not a reproduction: our declared adaptations include far fewer bits and elements and a different precoder. Document every open parameter and run a sensitivity check. Report a full-population form and a deadline-truncated form with runtimes accounted.

### Row 6 (Lange et al. 2023)

Research gap (F), before:
> Addressed: learning genetic operators instead of choosing only hand-designed rules.
> Proposed distinction: discrete RIS element edits conditioned on physical state responses and channel/search context. Attention-based GA operators themselves are established prior art.

After:
> Addressed: learning genetic operators instead of choosing only hand-designed rules.
> Current comparison: attention-based GA operators are established prior art and are no longer proposed as our contribution; learned atom ranking is kept as a comparator against analytical ranking inside the same search.

Relevance (I), before:
> Methodological foundation and novelty boundary for learned operators. Compare our residual attention policy with a simpler MLP and an analytical-score operator; do not claim novelty from adding attention to a GA.

After:
> Novelty boundary for learned operators. Keep our learned ranking (MLP and residual attention) as a comparator against analytical scoring under matched budgets; do not claim novelty from adding attention to a GA.

### Row 7 (Qian, Di Renzo 2020)

Research gap (F), before: "...Proposed distinction: learning a budgeted mutation operator for dynamic reuse of binary configurations. Generic unit-cell awareness is not new."
After: "...Current comparison: generic unit-cell and coupling awareness is not new; our question is whether search improvements for fixed-precoder worst-user rate hold on a coupled multiport model."

### Row 8 (RISnet, Peng et al.)

Research gap (F), before: "...Proposed distinction: learn mutation choices within a memory-based discrete search rather than use only a neural configuration optimizer. Full implementation comparison remains necessary."
After: "...Current comparison: a neural configuration optimizer differs from exact pair search with restarts and memory; a matched comparison under compatible observations and objectives remains necessary."

Relevance (I), before: "Strong related work for physical conditioning and architecture design. Tests whether the proposed attention search offers a benefit beyond existing domain-aware neural optimization; compare under compatible observations and objectives."
After: "Strong related work for physical conditioning and architecture design. Learned-ranking context: tests whether search improvements are needed beyond domain-aware neural optimization; compare under compatible observations and objectives."

### Row 9 (Liu et al. 2026, Advanced Electronic Materials)

Research gap (F), before: "...Proposed distinction: guide mutation locations in dynamic communication-rate optimization while holding the evaluator fixed. Physics + neural networks + evolution is already covered."
After: "...Current comparison: our study holds the evaluator fixed and varies the search algorithm for communication-rate optimization; physics + neural networks + evolution is already covered."

### Row 10 (Zheng et al. 2024)

Research gap (F), before: "...Proposed distinction: this supplies physical-model evidence, whereas our research tests a learned search operator. Simulation alone cannot inherit the paper's hardware validation."
After: "...Current comparison: this supplies physical-model evidence, whereas our research tests search algorithms on a coupled model. Simulation alone cannot inherit the paper's hardware validation."

### Row 11 (Zhang et al. 2022)

Relevance (I), before: "Mandatory specialized baseline and reason to retain single-user control as a sanity check. Our main proposed test is fixed-precoder multiuser worst-rate adaptation, with cached exact bit-flip and pair-search controls."
After: "Mandatory specialized baseline and reason to retain single-user control as a sanity check. Our main question is fixed-precoder multiuser worst-rate search on a coupled model, where exact bit-flip and pair search are the methods under study, not only controls."

### Row 12 (Nerini et al. 2024)

Research gap (F), before: "Provides network theory rather than a latency-matched spatial-versus-temporal learned controller benchmark."
After: "Provides network theory rather than a deadline-matched benchmark of discrete search algorithms."

### Row 21 (Kumar, Rathinam 2025), optional

Relevance (I), before: "Motivates separate spatial and temporal ablations rather than attributing all gains to attention."
After: "Temporal CSI prediction is not part of the current main question; kept as background for the cross-frame memory comparison, where history use should be compared against simple persistence."

### Row 28 (Prod'homme, del Hougne 2023)

Research gap (F), before: "Fast physical evaluation is a numerical method, not evidence that neural mutation is needed."
After: "Fast physical evaluation is a numerical method, not evidence that learned ranking is needed; low-rank updates are available to every method, including the baselines."

Reading status (J): the Sheet says "Not read"; `docs/novelty-analysis.md` records a partial full-text read of the arXiv version (update section). Suggest "Partly read" if the user agrees (not changed in this draft).

### Rows listed as unchanged

13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27 are accurate under the new direction and are left alone. Notes:
- Rows 19, 20 and 22 (temporal CSI and traffic prediction) are accurate but now peripheral because temporal prediction is no longer part of the main question; user may want to move them to a background section. Not edited.
- Row 24 (Hammami et al.) also fits the new direction as a coordinate-descent baseline; its cells already say so. I did not re-read the paper, so I cannot confirm the novelty-analysis statement that plain coordinate descent was the best trade-off.
- Row 27 still correctly says its closed-form results do not solve our binary-load, two-user max-min objective.
- Rows 2, 3, 4, 7, 8, 9, 10 and 12 keep their "Relevance" cells; only the cells shown above change.

## (d) Papers considered and rejected, or found but not added

| Paper | Reason |
|---|---|
| Prod'homme and del Hougne 2023 (DOI 10.1109/lcomm.2023.3330527) | Already row 28; no duplicate. |
| Pekcan and Ayanoglu 2024, "Achieving Optimum Received Power for Discrete-Phase RISs With Elementwise Updates in the Least Number of Steps", IEEE OJCOMS 5:2706-2722 (DOI 10.1109/ojcoms.2024.3386559) | Record verified in Crossref, but I saw only a one-line search summary, not the abstract. Content (what its element-wise updates are) is unverified. Worth reading: it may bear on single-flip update prior art. Not added. |
| Papadopoulos et al. 2026, "Physics-Aware RIS Codebook Compilation for Near-Field Beam Focusing under Mutual Coupling and Specular Reflections", ICC 2026 (DOI 10.1109/icc59461.2026.11586855) | Title only; content unverified. Possibly relevant to metaheuristics under coupling. |
| Pasquale et al. 2026, "Quantum Optimization for Electromagnetics: Physics-Informed QAOA for RIS", ACM ICS Workshops | Abstract read: QAOA with coupling-aware Ising terms on a 5x5 grid. Quantum route on a tiny array, redundant with row 36. |
| Zhou et al. 2023 (IEEE COMST survey; IEEE Wireless Commun. heuristic algorithms and learning) | Surveys of optimization approaches; no specific move set or deadline analysis seen in the abstracts. Could be cited as background. |
| Multi-RIS deployment and placement papers (Ma et al. 2024; Khatiwoda et al. 2025; Liu et al. 2023 GC Wkshps) | Placement or deployment optimization, not element configuration. Same reason Tarek (row 30) is peripheral. |
| Wu and Zhang 2019, IRS with discrete phase shifts (IEEE TCOM); An et al. 2022 (IEEE TCOM) | Classic discrete-phase references seen in Consensus; not in the requested list and not read beyond abstracts. Candidates if the user wants broader coverage. |
| Güttel et al., Sherman-Morrison-Woodbury for least squares with low-rank updates (arXiv 2406.15120) | Numerical linear algebra, not RIS. Note only that the plain Woodbury identity does not apply to the pseudo-inverse of a rectangular matrix, which is relevant if a pseudo-inverse precoder (as in the Zardi paper) is rebuilt per flip. |
| AutoOpt metaheuristic design framework (arXiv 2204.00998) | Generic algorithm-design framework; not specific to flip neighbourhoods. |

## Searches run for closer prior art

1. Web search: pair-flip/two-flip neighbourhood, tabu search, coordinate descent and worst-user rate on 1-bit RIS. No paper found that evaluates a pair-flip neighbourhood for 1-bit RIS with worst-user rate. Surfaced rows 38 (Liu, Yu, Hum) and 42 (Salmi et al.).
2. Web search: memetic, iterated local search or path relinking applied to discrete RIS phases. Nothing found for these terms in RIS. Surfaced row 39 (landscape analysis and niching GA) and row 40 (divide-and-sort).
3. Web search: Woodbury or low-rank updates for element flips in discrete RIS search. No dedicated paper found; the closest hit came from reading row 42, where coordinate descent evaluates each flip with the Woodbury identity under a multiport model. Row 28 (Prod'homme, del Hougne) was already in the Sheet.
4. Consensus: RIS metaheuristics with tabu (Panuganti), plus lookups of Zhao and Lim records. One Consensus batch was rate-limited and retried.

Absence of a hit is not evidence that no such paper exists. Two of the three web searches returned only snippets, so deeper searching on these terms (for example in IEEE Xplore, which I could not open) remains advisable before the final novelty check.

## Closest prior art found, for the novelty check

1. Goudet et al. 2024 (row 29): pair flips plus tabu plus population recombination, UBQP.
2. Salmi et al. 2026 (row 42): random-start single-flip coordinate descent with Woodbury flip evaluation under a multiport coupling model for 1-bit RIS, with an SDR upper bound (SISO).
3. Zardi et al. 2024 (row 5): memory-enhanced GA for worst-user throughput; no numeric results published.
4. Martín-Martín et al. 2024 (row 1): single-flip inversion sweeps for label generation.
5. Liu, Yu, Hum 2026 (row 38): max-min rate with coupling and 1-bit exhaustive enumeration.
6. Gkekas et al. 2026 (row 31): structural pruning of 1-bit configurations for a norm objective.

## Could not verify

- Full text of Tarek et al. (closed access), Panuganti, Lim, Zhao, and the published versions of the arXiv papers; their cells are abstract-level.
- Co-author given names for Panuganti, Lim, Zhao and Papadopoulos (only Crossref family names seen).
- Whether Lemma 1 of Gkekas et al. has any analogue for a fixed-precoder worst-user objective.
- Zardi parameters came through a summarizing fetch tool and the roles of rho and psi were not confirmed.
- Rows 16 to 28 "before" text was taken from the local CSV, not decoded from the live Sheet export.
