# V2 development handoff readback — 2026-11-06

This file records documentation/configuration checks only. It does not certify the physics gate, search ladder, test freeze, or a V2 result.

| Artifact | SHA-256 / evidence |
|---|---|
| `configs/experiments/matched_v2.development.json` | `920506fabcd46a3d5b35c3e01f462247351c02f829b2e65ce0e5fd7f4e84d2fe`; parsed successfully with Python `json.loads` |
| `docs/v2-plan-20261106.md` | `8ae1ff1321b263827104da1856efc80a13816c0e7b5f181699b41466dcf26274`; exact `cmp` match to `/home/parasite/.codex/attachments/44332882-9bc5-4dee-bcdd-5361baedd3f3/Pasted text.txt` |
| `docs/v2-execution.md` | `2c80cefe4bf2a21ed796712d2bc6d52dfeb84869967d95d6fa3645c26ba4e8df` |
| `report.md` after factual correction and C1 qualifier | `c4f327fd458adf2a18f26f1818abb3461eaa8fd8a7453b16cdac9c3fb1df43c1`; before correction `dd939f31788435074b46c9f17187db37fd00d3e4594bdcc0368c03359dcbd0b7` |
| C1 validation audit | `outputs/audits/v2-20261106/c1_spatial_validation_mesh161.attempt2.json`: `a2dbf145a3f933312f8b3529ed473fb72d9510249ece683d3e074dfcbbc14e20` |
| C3 descriptive profile | `outputs/profiles/v2-20261106/pair_c3_dev81_descriptive_20261106.jsonl`: `6ffebe8d373e741cbe9a91a9ddead079f9f8170397b4408679d48bdc1ef68abc` |
| Canonical V1 specular summary | `outputs/runs/matched_specular_v1/summary_test.json`: `cb3396f4043b7527fe9dc6149a9ac84b6a83ca02b8b431e438a3085dfd3b6953` |
| Canonical V1 coupled summary | `outputs/runs/matched_coupled_v1/summary_test.json`: `562ff12b2c206dc970b01f1c36c1280f127a45a68f59a1f35441f045f6870b1d` |
| Active V1 protocol | `configs/experiments/matched_v1.json`: `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88` |
| Archived pre-gatefix V1 protocol | `configs/experiments/archive/matched_v1-pre-gatefix-lock-20261106.json`: `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe` |
| Plot script | `scripts/plot_v2_progress.py`: `2345b4797d9ccbda75b0c0f67b5cee2f39bb68ef0f1e0b4ef590cee8551a492d` |
| Manuscript source | `paper/manuscript/main.tex`: `fd7730e0c056b1ed9fadab6923920e8e2621166a982d4de494082b459266d849` |
| Munich scene figure/provenance | PDF `a1acd2f4fd1380f2457e8653af9310825705b385e60869b2bfd40a2f15efec9d`; PNG `4dfc74f91ee946e815295e7ab0be40e0ab6960f61e61c20a49e1fa7876fcd6c5`; JSON `ec37549db207699000b2f321dc18beeea14c5ae2c8f4bd0e70d201ac11eaab29` |
| NEC geometry figure/provenance | PDF `90fe711daeb77f90b8cf27fa219047228d026342c6b203c0c5041819660ee82a`; PNG `cc9b0048fe5a1e8a5344cdffe1ad11af9676c41674dad17757d73fb67d97ec09`; sidecar `75066ed81fbda190469b3f5fd90678db40d5082d9f4c05acabc660f679e131d3` |
| Munich plot source | `scripts/plot_munich_scene.py`: `105ad926214627d1935486e244fc886b59a17aa916138a22fe6693198c3c72cd` |

The V1 50 ms table in `report.md` was parsed row-by-row and compared, at its displayed rounding, against the `budget_ms == 50` cells in both canonical summaries: all 12 method rows matched. Programmatic counts were 14,400 specular and 57,600 coupled observations at 50 ms, with zero misses in each; at 10 ms the corresponding miss counts were zero and 72. This verifies the table and denominators against those files, not any broader claim about physical validity.

The development geometry plot uses `coupled_wire_dev_v1/frame_0109.npz`, its same-index JSON row, and development scenario metadata. The frame is trajectory 6, step 13. The PNG readback verified as a 1926 × 1287 RGBA image. It depicts coordinates only; the 81/161 segment labels provide mesh context and do not assert convergence.

The C1 figure is generated from the validation-only audit above. It shows per-method fixed-precoder rate-shift means by trajectory and within-trajectory ON-count rank associations, with no action-level confidence interval. The PNG hash is `7084f4e6a57bb19845a0724d09f2cbc3efb1c90b932af75346593ec295025249`; its PDF hash is `d04ee31f4b3ed2b45929e7184c4ba2e1db52848582b2f5df31a50bc326aeaa36`. It states the independent sample size is three trajectories, not 5,760 actions. C1 rejects the 81-segment objective for V2 optimizer claims; 161 segments are the development reference but are not established as converged.

No test split was loaded by the plotting script or included in either figure.

The local `paper/manuscript/main.tex` compiled successfully with both vector PDF figures using the Codex desktop editor's built-in LaTeX compiler. The compiler did not export a PDF; `paper/manuscript/main.pdf` remains the earlier file dated 2026-11-06 22:25 WIB. The README was updated to identify the new assets and this compile boundary.

No broad test suite was run for this documentation/configuration task. No V2 test action, score, label, rate, SNR or trace outcome was inspected. C1, L1–L6, the numerical margin, and the V2 protocol freeze remain pending.
