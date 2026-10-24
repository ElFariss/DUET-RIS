# We are extending a simulation-only 1-bit RIS controller study. Find and assess l

**Question:** We are extending a simulation-only 1-bit RIS controller study. Find and assess literature needed to implement validated neighboring-meta-atom mutual coupling and compare spatial versus temporal intelligence fairly. Current setting: 64 elements (8x8), 4 BS antennas, 2 mobile users, nominal 5.53 GHz, public Sionna Munich propagation, independent scalar responses digitized from OpenSourceRIS uniform-panel plots, fixed reference RZF, max-min spectral efficiency, complete CPU runtime budgets (primary 10 ms). Independent-cell attention mutation did not beat cached analytical pair search. We now need: (1) physically consistent mutual-impedance, scattering-network, coupled-dipole and full-wave FDTD/MoM RIS models with accessible code/data, preferably experimental or full-wave validation; explicitly check PhysFad, multiport-network formulations, and OpenSourceRIS geometry/model applicability. Identify whether actual 5.53 GHz OpenSourceRIS mixed-state coupling can be calibrated from public data, and what is missing. (2) spatial attention/GNN versus causal temporal GRU/LSTM/transformer/channel prediction for moving users and stale CSI; matching observation information and total latency, persistence/linear prediction and analytical baselines. (3) strongest available open implementation feasible on a university lab CPU/RTX3060/64GB RAM, with mesh/time/passivity/reciprocity/no-coupling checks before training, and any benchmark suitable for comparing full wave with a reduced model. (4) paper matrix entries with exact title, all authors, year, DOI, venue, dataset/code links, supported limitations, and relevance. Prefer primary sources; mark preprints, unavailable evidence, dimensional approximations, user motion versus moving scatterers, and uncalibrated assumptions clearly. Do not assume attention must win or call arbitrary distance-weighted coupling a validated electromagnetic model. Do not modify any external spreadsheet; return cited research evidence and model selection guidance.

# **Validated RIS Coupling** and Fair **Spatial-Temporal** Comparison

The literature splits cleanly into **mutual-coupling modeling**, **fair spatial-versus-temporal learning**, and **practical open implementations/benchmarks**. The strongest evidence supports multiport-network RIS models with explicit passivity, reciprocity, mismatch, and mutual coupling, and it does **not** support calibrating true 5.53 GHz mixed-state neighboring-cell coupling for OpenSourceRIS from public per-state panel plots alone.

## Coupling Models

For **physically consistent** RIS modeling, the best-supported starting point is the multiport-network framework, because it unifies impedance, admittance, and scattering formulations and derives equivalent models that explicitly include mismatch and mutual coupling [[1.1]](https://consensus.app/papers/a-universal-framework-for-multiport-network-analysis-of-nerini-shen/3aad98c7fefd50cdb1bad5c79ee3dc44/) [[1.2]](https://consensus.app/papers/a-universal-framework-for-multiport-network-analysis-of-nerini-shen/3aad98c7fefd50cdb1bad5c79ee3dc44/) [[1.3]](https://consensus.app/papers/a-universal-framework-for-multiport-network-analysis-of-nerini-shen/3aad98c7fefd50cdb1bad5c79ee3dc44/) [[1.4]](https://consensus.app/papers/a-universal-framework-for-multiport-network-analysis-of-nerini-shen/3aad98c7fefd50cdb1bad5c79ee3dc44/). The same literature also warns that the usual independent phase-only cell model is physically inconsistent even before adding coupling, losses, or mismatch [[2.1]](https://consensus.app/papers/physically-consistent-modeling-of-wireless-links-with-nossek-semmler/8e1fe5f7f6e05945a9a8e11b6e362505/) [[2.2]](https://consensus.app/papers/physically-consistent-modeling-of-wireless-links-with-nossek-semmler/8e1fe5f7f6e05945a9a8e11b6e362505/) [[2.3]](https://consensus.app/papers/physically-consistent-modeling-of-wireless-links-with-nossek-semmler/8e1fe5f7f6e05945a9a8e11b6e362505/).

- **Universal multiport analysis** is the most defensible reduced model for your 8×8 study [[1.5]](https://consensus.app/papers/a-universal-framework-for-multiport-network-analysis-of-nerini-shen/3aad98c7fefd50cdb1bad5c79ee3dc44/) [[1.6]](https://consensus.app/papers/a-universal-framework-for-multiport-network-analysis-of-nerini-shen/3aad98c7fefd50cdb1bad5c79ee3dc44/).
- **S-parameter optimization with full-wave validation** is available and explicitly separates structural scattering from controllable reradiation [[3.1]](https://consensus.app/papers/design-of-reconfigurable-intelligent-surfaces-by-using-abrardo-toccafondi/8b9323ed893c5b309a7d8b21d2235854/) [[3.2]](https://consensus.app/papers/design-of-reconfigurable-intelligent-surfaces-by-using-abrardo-toccafondi/8b9323ed893c5b309a7d8b21d2235854/).
- **Experimental coupling validation** exists through a trained scattering-matrix model on a fabricated 1-bit RIS, improving prediction versus coupling-unaware models by up to **10.7%** against full-wave reference [[4.1]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) [[4.2]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) [[4.3]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/).

A key caveat is that these validated models are **not** the same as arbitrary distance-weighted neighbor penalties. The evidence-backed models infer or derive a network matrix subject to microwave constraints, sometimes from a single 3D full-wave radiation simulation and then experimental VNA confirmation [[4.4]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) [[4.5]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) [[4.6]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) [[4.7]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/).

**Fig 11.** The comparison of the RIS radiation pattern obtained through the mutual coupling-unaware model, the mutual coupling-aware model using simulated ˜ S (MIMO setup), the mutual coupling-aware model using trained ˆ S , and the full-wave simulation. [[4]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/)

*How to read: This plot compares several RIS radiation-pattern predictions against the full-wave reference. Read the curves by comparing coupling-unaware, simulated-coupling, and trained-coupling models across angle; closer overlap with the full-wave curve is better.*

## OpenSourceRIS Applicability

OpenSourceRIS is highly relevant because it is an **open 5 GHz WiFi RIS** with fabrication data and firmware, optimized across 5.15-5.875 GHz, and evaluated with measured reflection coefficients on a 256-element prototype [[5.1]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/) [[5.2]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/) [[5.3]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/) [[5.4]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/). But that evidence does **not** establish publicly available **mixed-state nearest-neighbor coupling matrices** at 5.53 GHz.

- Public OpenSourceRIS material supports **geometry and single-panel RF behavior**, not full mixed-state coupling calibration [[5.3]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/) [[5.4]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/).
- Public 5 GHz datasets exist, but they are mostly **system-channel or beam measurements**, not per-neighbor multiport scans over joint cell states [[6.1]](https://consensus.app/papers/a-comprehensive-dataset-of-risbased-channel-measurements-tewes-heinrichs/4879cd96839852cb8910f43c89d9f638/) [[6.2]](https://consensus.app/papers/a-comprehensive-dataset-of-risbased-channel-measurements-tewes-heinrichs/4879cd96839852cb8910f43c89d9f638/) [[6.3]](https://consensus.app/papers/a-comprehensive-dataset-of-risbased-channel-measurements-tewes-heinrichs/4879cd96839852cb8910f43c89d9f638/).
- BRISC adds **5.53 GHz binary-state CSI measurements** useful for reduced-model calibration and validation, but it groups elements into blocks and targets channel reconstruction rather than extracting local mixed-state EM coupling tensors [[7.1]](https://consensus.app/papers/brisc-a-dataset-of-channel-measurements-at-5-ghz-with-a-piana-alghisi/ad2d5d868ea4550c851704962cd56cee/) [[7.2]](https://consensus.app/papers/brisc-a-dataset-of-channel-measurements-at-5-ghz-with-a-piana-alghisi/ad2d5d868ea4550c851704962cd56cee/) [[7.3]](https://consensus.app/papers/brisc-a-dataset-of-channel-measurements-at-5-ghz-with-a-piana-alghisi/ad2d5d868ea4550c851704962cd56cee/) [[7.4]](https://consensus.app/papers/brisc-a-dataset-of-channel-measurements-at-5-ghz-with-a-piana-alghisi/ad2d5d868ea4550c851704962cd56cee/).

What is missing for **actual OpenSourceRIS mixed-state coupling calibration** is a state-resolved multiport or field dataset: per-cell geometry/material stack, reference impedances, VNA-accessible port definition or equivalent de-embedded network model, and measurements or full-wave sweeps over at least pairwise joint states across offsets. Existing open sub-6 GHz datasets are valuable benchmarks, but they do not expose that full calibration target [[8.1]](https://consensus.app/papers/open-experimental-measurements-of-sub6ghz-rossanese-mursia/f293e9ddd9d05656b9b7a7953753e425/) [[8.2]](https://consensus.app/papers/open-experimental-measurements-of-sub6ghz-rossanese-mursia/f293e9ddd9d05656b9b7a7953753e425/) [[8.3]](https://consensus.app/papers/open-experimental-measurements-of-sub6ghz-rossanese-mursia/f293e9ddd9d05656b9b7a7953753e425/) [[8.4]](https://consensus.app/papers/open-experimental-measurements-of-sub6ghz-rossanese-mursia/f293e9ddd9d05656b9b7a7953753e425/).

## Spatial vs Temporal Intelligence

A fair comparison between **spatial attention/GNN** and **causal temporal GRU/LSTM/transformer** needs matched observation information and matched total latency, because the strongest spatio-temporal CSI papers succeed by using both spatial correlation and temporal dependence rather than attention alone [[9.1]](https://consensus.app/papers/spatiotemporal-neural-network-for-channel-prediction-in-liu-hu/2ebbc358079051bb8fc08eb155ff9ea6/) [[9.2]](https://consensus.app/papers/spatiotemporal-neural-network-for-channel-prediction-in-liu-hu/2ebbc358079051bb8fc08eb155ff9ea6/) [[10.1]](https://consensus.app/papers/spectral-temporal-graph-transformer-for-massive-mimo-csi-dayer-akash/e5e87b8485825c54a739e84ed9430752/) [[10.2]](https://consensus.app/papers/spectral-temporal-graph-transformer-for-massive-mimo-csi-dayer-akash/e5e87b8485825c54a739e84ed9430752/). The user’s negative result for independent-cell attention is therefore unsurprising.

- **Temporal baselines are mandatory**: persistence and linear predictors should be included before claiming gains from GRU/LSTM/transformers or GNNs [[7.5]](https://consensus.app/papers/brisc-a-dataset-of-channel-measurements-at-5-ghz-with-a-piana-alghisi/ad2d5d868ea4550c851704962cd56cee/).
- **Dynamic graphs help only when dynamics exist**: ERAN improved high-mobility CSI prediction over a static GNN at 120 km/h, but that is a generic massive-MIMO result, not RIS-specific evidence [[11.1]](https://consensus.app/papers/an-eranbased-dynamic-graph-neural-network-for-csi-kumar-rathinam/25b557fc83d85a1b81855e45594c1722/) [[11.2]](https://consensus.app/papers/an-eranbased-dynamic-graph-neural-network-for-csi-kumar-rathinam/25b557fc83d85a1b81855e45594c1722/) [[11.3]](https://consensus.app/papers/an-eranbased-dynamic-graph-neural-network-for-csi-kumar-rathinam/25b557fc83d85a1b81855e45594c1722/).
- **Spatio-temporal models beat purely temporal ones** in the cited CSI literature, but those papers study mobility and fading dynamics, not moving scatterers inside a calibrated RIS environment [[9.3]](https://consensus.app/papers/spatiotemporal-neural-network-for-channel-prediction-in-liu-hu/2ebbc358079051bb8fc08eb155ff9ea6/) [[10.3]](https://consensus.app/papers/spectral-temporal-graph-transformer-for-massive-mimo-csi-dayer-akash/e5e87b8485825c54a739e84ed9430752/) [[12.1]](https://consensus.app/papers/spatialtemporal-cellular-traffic-prediction-for-5g-and-wang-hu/fe9c405396c954229e50d4ea2ffd7945/).

For your setup, the fairest comparison is likely: identical stale-CSI windows, identical side information, identical inference budget inside the **10 ms** controller deadline, and analytical search plus persistence/linear prediction as first baselines. The available evidence does not justify assuming attention will outperform analytical pair search under those constraints.

## Practical Stack

The strongest **open and feasible** stack is a reduced multiport model calibrated against either full-wave simulation or open measurements, then embedded in an open system simulator. QRIS is open and built on QuaDRiGa for spatially consistent multi-antenna channels, but it is a channel platform rather than a validated neighboring-meta-atom coupling extractor [[13.1]](https://consensus.app/papers/qris-a-quadrigabased-simulation-platform-for-burtakov-kureev/82fec3a8649f554791a1287ab63a279c/) [[13.2]](https://consensus.app/papers/qris-a-quadrigabased-simulation-platform-for-burtakov-kureev/82fec3a8649f554791a1287ab63a279c/) [[13.3]](https://consensus.app/papers/qris-a-quadrigabased-simulation-platform-for-burtakov-kureev/82fec3a8649f554791a1287ab63a279c/). Its value is benchmarking reduced RIS models against richer propagation, including published validation against CST and radar-cross-section references [[13.4]](https://consensus.app/papers/qris-a-quadrigabased-simulation-platform-for-burtakov-kureev/82fec3a8649f554791a1287ab63a279c/) [[13]](https://consensus.app/papers/qris-a-quadrigabased-simulation-platform-for-burtakov-kureev/82fec3a8649f554791a1287ab63a279c/).

| Model Family | Validation Level | Open/Accessible Assets | Main Limitation | Relevance |
|---|---|---|---|---|
| Multiport S/Z/Y reduced model | Full-wave theory; some experiments | Equations in primary papers | Needs calibration inputs | Best first implementation |
| Trained scattering-matrix model | Full-wave + experiment | Method described, prototype-specific | Full-wave precomputation required | Best validated coupling-aware reducer |
| OpenSourceRIS geometry | Measured sub-6 GHz prototype | Fabrication + firmware open | No public mixed-state coupling matrix | Best 5 GHz hardware anchor |
| BRISC / 5 GHz datasets | Real measurements | Public datasets | Channel-level, not local EM ports | Best calibration benchmark |
| QRIS / RT-system simulation | Open simulator validation | Open platform | Not a cell-coupling solver | Best propagation wrapper |

**Figure 1:** Comparison of candidate modeling layers for a practical 5.53 GHz RIS workflow.

Before training, the literature most clearly supports checking **passivity**, **reciprocity**, and the **no-coupling limit** as sanity tests, because those constraints are built directly into physics-consistent multiport formulations and recent statistical generators [[14.1]](https://consensus.app/papers/statistical-multiportnetwork-modeling-and-efficient-hammami-magoarou/9afad547d28451d38a0c7389e32378c2/) [[14.2]](https://consensus.app/papers/statistical-multiportnetwork-modeling-and-efficient-hammami-magoarou/9afad547d28451d38a0c7389e32378c2/) [[15.1]](https://consensus.app/papers/a-tutorial-on-beyonddiagonal-reconfigurable-intelligent-li-nerini/dd150dcc49645969936033912eeb7cea/). For a full-wave-versus-reduced benchmark, the best open anchors are OpenSourceRIS hardware/material files plus public 5 GHz/5.53 GHz measurement datasets, while the best validated reference workflow is the scattering-matrix training-and-validation approach against one full-wave radiation simulation and measurements [[5.4]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/) [[8.5]](https://consensus.app/papers/open-experimental-measurements-of-sub6ghz-rossanese-mursia/f293e9ddd9d05656b9b7a7953753e425/) [[8.6]](https://consensus.app/papers/open-experimental-measurements-of-sub6ghz-rossanese-mursia/f293e9ddd9d05656b9b7a7953753e425/) [[4.8]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) [[4.9]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/).

## Paper Matrix

Below is a compact matrix of the **most decision-relevant** papers for immediate implementation triage.

| Exact Title | Authors | Year | Venue | Code/Data Links in Evidence | Supported Limitations | Relevance |
|---|---|---:|---|---|---|---|
| Design of Reconfigurable Intelligent Surfaces by Using S-Parameter Multiport Network Theory—Optimization and Full-Wave Validation | A. Abrardo, A. Toccafondi, M. di Renzo | 2023 | IEEE Transactions on Wireless Communications | Not stated in supplied text | MoM full-wave validation, not stated open code | Best S-parameter optimization paper |
| Mutual Coupling in RIS-Aided Communication: Model Training and Experimental Validation | Pin-Jun Zheng, Ruiqi Wang, A. Shamim, T. Al-Naffouri | 2023 | IEEE Transactions on Wireless Communications | Not stated in supplied text | Needs full-wave simulation; not online calibration [[4.10]](https://consensus.app/papers/mutual-coupling-in-risaided-communication-model-training-zheng-wang/510fdc70258c51babf6695aed4ff590d/) | Best experimental coupling validation |
| A Universal Framework for Multiport Network Analysis of Reconfigurable Intelligent Surfaces | Matteo Nerini, Shan-Pu Shen, Hong-Yu Li, M. di Renzo, Bruno Clerckx | 2023 | IEEE Transactions on Wireless Communications | Not stated in supplied text | Framework paper, not hardware-calibrated alone | Best unifying physical model |
| Open Source Reconfigurable Intelligent Surface for the Frequency Range of 5 GHz WiFi | Markus Heinrichs, A. Sezgin, R. Kronberger | 2023 | IEEE ISAP | Fabrication and firmware open [[5.4]](https://consensus.app/papers/open-source-reconfigurable-intelligent-surface-for-the-heinrichs-sezgin/eecd5fcae1dc5713aa1799b520189722/) | Reflection-coefficient data, not mixed-state coupling tensor | Best hardware match |
| A comprehensive dataset of RIS-based channel measurements in the 5GHz band | Simon Tewes, Markus Heinrichs, K. Weinberger, R. Kronberger, A. Sezgin | 2023 | IEEE VTC2023-Spring | IEEE DataPort + GitHub [[6.2]](https://consensus.app/papers/a-comprehensive-dataset-of-risbased-channel-measurements-tewes-heinrichs/4879cd96839852cb8910f43c89d9f638/) | Stationary scenarios [[6.3]](https://consensus.app/papers/a-comprehensive-dataset-of-risbased-channel-measurements-tewes-heinrichs/4879cd96839852cb8910f43c89d9f638/) | Best 5 GHz public benchmark |

**Figure 10.** QRIS vs. CST full-wave validation. [[13]](https://consensus.app/papers/qris-a-quadrigabased-simulation-platform-for-burtakov-kureev/82fec3a8649f554791a1287ab63a279c/)

*How to read: Compare the reduced-model and CST results across the plotted cases. Smaller separation between the two traces indicates a better approximation of the full-wave reference.*

The best-supported path is to implement a **multiport reduced model** first, calibrate it only where public data genuinely supports calibration, and compare spatial and temporal learning only under **matched information and latency**. For your 5.53 GHz OpenSourceRIS target, public evidence supports hardware geometry and channel-level benchmarking, but not a validated mixed-state neighboring-cell coupling matrix without new full-wave or VNA-style calibration data.
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
`1.` Nerini M, Shen S, Li H, Di Renzo M, Clerckx B. A Universal Framework for Multiport Network Analysis of Reconfigurable Intelligent Surfaces. *IEEE Transactions on Wireless Communications.* 2023;23:14575-14590. doi:10.1109/twc.2024.3416825
 
> [1.1] In this study, we propose a universal framework for the multiport network analysis of RIS-aided systems. (Body)
 
> [1.2] With our framework, we model RISaided systems and RIS architectures through impedance, admittance, and scattering parameter analysis. (Body)
 
> [1.3] Based on these analyses, three equivalent models are derived accounting for the effects of impedance mismatching and mutual coupling. (Body)
 
> [1.4] Based on these analyses, three equivalent models are derived accounting for the effects of impedance mismatching and mutual coupling. (Abstract)
 
> [1.5] We discuss the benefits of each analysis in characterizing and optimizing the RIS and how to select the most suitable parameters according to the needs. (Body)
 
> [1.6] Such a framework would improve our understanding of different EM-consistent models for RIS-aided systems, and would provide additional tools to perform RIS optimization. (Body)
 
`2.` Nossek J, Semmler D, Joham M, Utschick W. Physically Consistent Modeling of Wireless Links With Reconfigurable Intelligent Surfaces Using Multiport Network Analysis. *IEEE Wireless Communications Letters.* 2023;13:2240-2244. doi:10.1109/lwc.2024.3410528
 
> [2.1] Nevertheless, the widely employed model is still inconsistent with basic physical laws. (Body)
 
> [2.2] We will show that even with a very simple abstract model based on isotropic radiators, ignoring any mismatch, mutual coupling, and losses, each RIS element cannot be modeled to simply reflect the incident signal by manipulating its phase only and letting the amplitude unchanged. (Body)
 
> [2.3] Nevertheless, the widely employed model is still inconsistent with basic physical laws. (Abstract)
 
`3.` Abrardo A, Toccafondi A, Di Renzo M. Design of Reconfigurable Intelligent Surfaces by Using S-Parameter Multiport Network Theory—Optimization and Full-Wave Validation. *IEEE Transactions on Wireless Communications.* 2023;23:17084-17102. doi:10.1109/twc.2024.3450722
 
> [3.1] In the context of multiport network modeling, there exist no prior works in which the structural scattering is mathematically and explicitly formulated, optimization algorithms are developed to mitigate it, and full-wave simulations are used to validate the accuracy of the models and the effectiveness of the optimization algorithms. (Introduction)
 
> [3.2] (iv) Finally, we validate the theoretical findings and algorithms with numerical simulations and a commercial full-wave electromagnetic simulator based on the method of moments. (Abstract)
 
`4.` Zheng P, Wang R, Shamim A, Al-Naffouri T. Mutual Coupling in RIS-Aided Communication: Model Training and Experimental Validation. *IEEE Transactions on Wireless Communications.* 2023;23:17174-17188. doi:10.1109/twc.2024.3451548
 
> [4.1] The trained model is validated through both full-wave simulations and experimental measurements on the fabricated RIS prototype. (Body)
 
> [4.2] Compared to the conventional communication model that does not account for mutual coupling in RIS, the mutual couplingaware model incorporating trained scattering parameters demonstrates improved prediction accuracy. (Body)
 
> [4.3] Benchmarked against the full-wave simulated RIS radiation pattern, the trained model can reduce prediction error by up to approximately 10.7%. (Body)
 
> [4.4] Utilizing a fabricated 1-bit quasi-passive RIS prototype operating in the mmWave band, we propose a practical model training approach based on a single 3D fullwave simulation of the RIS radiation pattern, which enables the estimation of the scattering matrix among RIS unit cells. (Body)
 
> [4.5] The formulated estimation problem is rigorously convex with a limited number of unknowns un-scaling with RIS size. (Body)
 
> [4.6] Meanwhile, the S-parameter between the Tx and Rx antennas is measured, validating that the trained model exhibits closer alignment with the experimental measurements. (Body)
 
> [4.7] These results affirm the accuracy of the adopted model and the effectiveness of the proposed model training method. (Body)
 
> [4.8] A practical training approach for these scattering parameters is proposed leveraging a single 3D full-wave simulation of the RIS radiation pattern. (Conclusion)
 
> [4.9] Both full-wave simulations and experimental measurements are carried out to verify the accuracy of the trained model. (Conclusion)
 
> [4.10] Nonetheless, the proposed model training method requires full-wave simulation, which is time-consuming and thus not suitable for online mutual coupling calibration. (Conclusion)
 
`5.` Heinrichs M, Sezgin A, Kronberger R. Open Source Reconfigurable Intelligent Surface for the Frequency Range of 5 GHz WiFi. *2023 IEEE International Symposium On Antennas And Propagation (ISAP).* 2023. doi:10.1109/isap57493.2023.10389095
 
> [5.1] To close this gap, a Reconfigurable Intelligent Surface for the frequency range of 5 GHz WiFi is presented in this work. (Abstract)
 
> [5.2] We describe the designed unit cell, which is optimized for the full frequency range of 5.15 to 5.875 GHz. (Abstract)
 
> [5.3] The measured reflection coefficient of a rectangular RIS prototype with 256 elements is used for RF performance evaluation. (Abstract)
 
> [5.4] Fabrication data and firmware source code are made open source, which makes RIS more available in real measurement setups. (Abstract)
 
`6.` Tewes S, Heinrichs M, Weinberger K, Kronberger R, Sezgin A. A comprehensive dataset of RIS-based channel measurements in the 5GHz band. *2023 IEEE 97th Vehicular Technology Conference (VTC2023-Spring).* 2023. doi:10.1109/vtc2023-spring57618.2023.10200973
 
> [6.1] By utilizing an RIS prototype system in the 5 GHz band, this paper provides a comprehensive dataset of channel measurements of various geometric arrangements of antennas and RIS. (Abstract)
 
> [6.2] The dataset and the in-detail documentation is provided on IEEE DataPort and GitHub, respectively. (Abstract)
 
> [6.3] Due to the consistent quality of the measurements that is ensured by the measurement chamber, the provided dataset is also well suited to be used as a basis for machine learning concepts.In order to provide a solid baseline for comparing and validating a wide range of applications in different scenarios, the measurements are taken in stationary scenarios. (Abstract)
 
`7.` Piana M, Alghisi GA, Guglielmi A, Perin G, Gringoli F, Tomasin S. BRISC: A Dataset of Channel Measurements at 5 GHz With a Reflective Intelligent Surface. 2026. doi:10.48550/arxiv.2602.21102
 
> [7.1] 53 GHz using a 256element binary-state RIS. (Body)
 
> [7.2] This article introduced BRISC, a comprehensive measurement-based dataset for RIS-assisted 80 MHz wireless channels in an indoor environment at 5 . (Conclusion)
 
> [7.3] The dataset was shown to be effective both for calibrating and validating state-of-the-art RIS channel models, highlighting the trade-offs between linear and data-driven approaches in terms of accuracy and training requirements. (Conclusion)
 
> [7.4] To manage complexity, the RIS elements are grouped into blocks of different sizes, where all elements within a block share the same state. (Abstract)
 
> [7.5] Specifically, a linear model with incorporated bias has been shown to perform similarly, if not even better than a neural network for the channel frequency response reconstruction task. (Conclusion)
 
`8.` Rossanese M, Mursia P, Garcia-Saavedra A, Sciancalepore V, Asadi A, Costa-Pérez X. Open Experimental Measurements of Sub-6GHz Reconfigurable Intelligent Surfaces. *IEEE Internet Computing.* 2024;28:19-28. doi:10.1109/mic.2024.3376772
 
> [8.1] Given the novel nature of this technology, publicly available datasets for RISbased systems are rare today. (Body)
 
> [8.2] The only publicly accessible dataset derived from real measurements is delineated in [4]. (Body)
 
> [8.3] Points of difference from our dataset include the absence of clearly delineated radiation patterns for the considered RIS, hindering its utility 1 The datasets and associated documentation are available at https://github.com/marcantonio14/RIS-Power-Measurements-Dataset. (Body)
 
> [8.4] in other investigations; the provision of power values with a wider measurement interval; restriction to a single size of RIS elements; and a lack of accompanying use case illustrations for contextualization. (Body)
 
> [8.5] Motivated by these considerations, we decided to implement our RIS prototype, which fulfills the aforementioned design points, together with high granularity beam steering, and to make publicly accessible the measurements collected during our tests in an anechoic chamber, in the hope it may be useful to foster the progress of the field. (Body)
 
> [8.6] In this article, we present two datasets that we make publicly available for research. (Abstract)
 
`9.` Liu G, Hu Z, Wang L, Xue J, Yin H, Gesbert D. Spatio-Temporal Neural Network for Channel Prediction in Massive MIMO-OFDM Systems. *IEEE Transactions on Communications.* 2022;70:8003-8016. doi:10.1109/tcomm.2022.3215198
 
> [9.1] In this paper, we propose a spatio-temporal neural network (STNN) to achieve better performance by carefully taking into account the spatio-temporal characteristics of CSI. (Abstract)
 
> [9.2] Specifically, STNN uses its encoder and decoder modules to capture the spatial correlation and temporal dependence of CSI. (Abstract)
 
> [9.3] Evaluated on a realistic channel model with enhanced mobility and spherical waves, experimental results show that STNN can effectively improve the accuracy of prediction and perform well with respect to different signal to noise ratios (SNRs). (Abstract)
 
`10.` Dayer A,  A, Soni S, Singh S. Spectral Temporal Graph Transformer for Massive MIMO CSI Prediction in 5G and Beyond. *2025 2nd International Conference on Intelligent Algorithms for Computational Intelligence Systems (IACIS).* 2025. doi:10.1109/iacis65746.2025.11211349
 
> [10.1] We propose a Spectral Temporal Graph Transformer (STGT) that unifies graph-based spatial learning with transformer-based temporal attention to predict compressed CSI. (Abstract)
 
> [10.2] The model dynamically constructs data-driven graphs, performs spectral filtering to capture multi-scale spatial dependencies, and leverages self-attention to learn long-range temporal evolution. (Abstract)
 
> [10.3] Evaluations on realistic 3GPP TR 38.901 channel models across diverse SNR and mobility regimes show that STGT outperforms RNN/LSTM, vanilla transformers, and STEM-GNN in NMSE and spectral efficiency, while maintaining robustness under high mobility and aggressive compression. (Abstract)
 
`11.` Kumar R, Rathinam M. An ERAN-Based Dynamic Graph Neural Network for CSI Prediction in Massive MIMO Systems. *IEEE Wireless Communications Letters.* 2025;14:3560-3564. doi:10.1109/lwc.2025.3598251
 
> [11.1] In this letter, we adapt the evolving relational attention network (ERAN)—a generic spatio-temporal graph neural network (GNN)—for CSI prediction. (Abstract)
 
> [11.2] ERAN dynamically learns evolving adjacency matrices using a gated recurrent unit (GRU)-driven evolving graph learning (EGL) module, enabling it to capture dependencies among multiple variables. (Abstract)
 
> [11.3] Experiments show that at high mobility ( $\mu = 120$ km/h), ERAN achieves a 34.93% reduction in root-mean-square error (RMSE) compared to STEM, while incurring only a 5.64% drop in spectral efficiency (SE), in contrast to STEM’s 15.1% degradation—demonstrating nearly three times higher temporal robustness under severe dynamic conditions. (Abstract)
 
`12.` Wang Z, Hu J, Min G, Zhao Z, Chang Z, Wang Z. Spatial-Temporal Cellular Traffic Prediction for 5G and Beyond: A Graph Neural Networks-Based Approach. *IEEE Transactions on Industrial Informatics.* 2023;19:5722-5731. doi:10.1109/tii.2022.3182768
 
> [12.1] The simulation results show that our proposed TSGAN outperforms three classic prediction models based on GNNs or GRU on a real-world cellular network dataset in short-term, mid-term, and long-term prediction scenarios. (Abstract)
 
`13.` Burtakov I, Kureev AA, Tyarin A, Khorov EM. QRIS: A QuaDRiGa-Based Simulation Platform for Reconfigurable Intelligent Surfaces. *IEEE Access.* 2023;11:90670-90682. doi:10.1109/access.2023.3306954
 
> [13.1] In this paper, we address this problem and present QRIS, an open-source RIS simulation platform that eliminates the drawbacks of existing platforms. (Body)
 
> [13.2] QRIS is based on the QUAsi Deterministic Radio channel Gener- ator (QuaDRiGa) [7], which already supports many wellapproved channel models for various wireless technologies and indoor/outdoor scenarios. (Body)
 
> [13.3] Its essential features consider such physical effects as shadowing and accurate modeling of spatial consistency, which is important for scenarios with MIMO. (Body)
 
> [13.4] This problem is addressed in this paper, where we design a new QRIS model. (Body)
 
`14.` Hammami C, Magoarou LL, Del Hougne P. Statistical Multiport-Network Modeling and Efficient Discrete Optimization of RIS. *IEEE Wireless Communications Letters.* 2025;15:1425-1429. doi:10.1109/lwc.2026.3652464
 
> [14.1] We account for reciprocity, passivity, and coherent backscattering; then, we add a simple hyper-parameter to control the MC strength. (Body)
 
> [14.2] We account for reciprocity, passivity, and coherent backscattering; then, we add a simple hyper-parameter to control the MC strength. (Abstract)
 
`15.` Li H, Nerini M, Shen S, Clerckx B. A Tutorial on Beyond-Diagonal Reconfigurable Intelligent Surfaces: Modeling, Architectures, System Design and Optimization, and Applications. *IEEE Communications Surveys & Tutorials.* 2025;28:4086-4126. doi:10.1109/comst.2025.3647003
 
> [15.1] In its passive form, <inline-formula> <tex-math notation="LaTeX">$\boldsymbol {\Theta }$ </tex-math></inline-formula> satisfies the unitary property <inline-formula> <tex-math notation="LaTeX">$\boldsymbol {\Theta }^{\textsf {H}}\boldsymbol {\Theta }=\mathbf {I}$ </tex-math></inline-formula> (for energy conservation in lossless ideal surfaces) and be either symmetric <inline-formula> <tex-math notation="LaTeX">$\boldsymbol {\Theta }=\boldsymbol {\Theta }^{\textsf {T}}$ </tex-math></inline-formula> or asymmetric <inline-formula> <tex-math notation="LaTeX">$\boldsymbol {\Theta }\neq \boldsymbol {\Theta }^{\textsf {T}}$ </tex-math></inline-formula> hence leading to reciprocal or non-reciprocal BD-RIS. (Abstract)

