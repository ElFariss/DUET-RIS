# Upstream sources and usage boundaries

| Source | Used for | Provenance |
|---|---|---|
| [OpenSourceRIS](https://github.com/mheinri/OpenSourceRIS) | Digitized magnitude/phase plots and cell dimensions | MIT repository, pinned commit `7982a576a5edd389edfd81ece9a1f6675c7c545e`; retain attribution to Heinrichs et al. |
| [DeepMIMO](https://github.com/DeepMIMO/DeepMIMO) | Export/conversion format and application example | Installed version 4.0.5; example pinned to `45238f9a4c4311b8747dad2eefdebc8c74b1a104` |
| [Sionna RT](https://github.com/NVlabs/sionna-rt) | Munich geometry and ray tracing | Version 2.0.1; original scene file hashes retained in scenario metadata |
| [Fara lookup table](https://zenodo.org/records/7674708) | Backup source, not used in main experiments | Requires operating-condition verification before use |
| [BRISC](https://zenodo.org/records/18714621) | Potential later whole-channel validation, not used here | Complete channels must not be used as individual cell coefficients |

The response table is derived from published uniform-panel plots; it is not a
new measurement or a full-wave per-cell EM simulation. Exact download URLs,
retrieval timestamps and hashes are in `data/raw/opensourceris-and-upstream/manifest.json`.
Consult each upstream license before redistributing raw assets. Repository access
does not itself establish publication permission for every third-party figure.

## Coupled-model references

- [PyNEC / NEC++](https://github.com/tmolteno/python-necpp): NEC-2 thin-wire solver, installed from PyPI as PyNEC 2.3.4. Original solver licensing applies; no solver code is relicensed here.
- [PhysFad](https://github.com/philipp-delhougne/PhysFad) and [Nerini mutual-coupling code](https://github.com/matteonerini/ris-mutual-coupling): inspected reference implementations, not the electromagnetic engine used by this repository. Pinned URLs and hashes are in `data/raw/em_reference/manifest.json`; downloaded copies are excluded from Git.
- The Consensus research document is retained with its citation markers and attribution. Paper metadata is independently checked where possible; journal publication years can differ from preprint years.
