# Repository design and migration

The requested reproducible-research layout is adopted with three practical choices:

1. **Keep complete runs together.** Checkpoints, timing records, logs, configuration and generated figures live under one run ID. This avoids accidentally pairing metrics with a different model or scenario.
2. **Name the actual physical capability.** `responses/` holds digitized binary responses. Calling it a full `electromagnetic/` solver would overstate what is implemented.
3. **Separate active research from its history.** The old SISO/A100-required experiment and pre-reorganization source are preserved in `archives/`; the existing IEEE proposal is under `paper/proposal/`. Other conference projects are outside this consolidation.

Configuration has three levels: dataset identity/assumptions, training jobs, and experiment protocol. `scripts/reproduce.py` resolves these into an immutable run manifest. Model/GA constants remain explicit in scientific source and documentation; adding an ignored JSON parameter cannot silently change the architecture.

`docs/migration-source-audit.json` verifies byte-identical preservation of source, notes and paper material. `artifact-manifest.json` inventories the larger local data and experiment evidence. Existing source directories remain as backups; all new work uses this repository and `~/projects/atom-wise-ris` on the lab host.

Code and compact evidence are prepared for version control. Large data, models and historical copies stay in the workspace pending a deliberate release policy. No Git push, permissive licensing decision or publication is implied by consolidation.

The raw source tables and historical metadata are preserved, including superseded settings. Current claims come from the runtime source, resolved run configuration and report; archived acquisition metadata is not silently rewritten to match later methods.
