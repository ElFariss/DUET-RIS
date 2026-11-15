# DUET: Efficient Pairwise Search for Electromagnetically Coupled Meta-Atoms in Reconfigurable Intelligent Surfaces

Experiment scripts, pre-declared analysis plans, run records and manuscript source for the ACIIDS 2027 submission by M. F. El Hakim, A. D. H. Fadhlurrohman and W. Yahya (Universitas Brawijaya).

**DUET** (Deadline-bounded Updates for Exact Two-flip search) configures a mutually coupled 1-bit RIS to maximise the worst user's rate under a hard CPU deadline. It scores every single flip and every pair flip exactly with rank-one and rank-two updates of the coupled multiport network, so it evaluates 62–445 times more candidates per deadline than ME-GA or NSGA-II.

| Paper name | Code name | Description |
|---|---|---|
| DUET | `pair` | exact single + pair moves, uniform restarts |
| DUET-D | `b3` | DUET with two ON-density restarts |
| DUET-E | `b5` | DUET with elite recombination |
| DUET-M | `pair_plus_b35` | both rules (memetic) |
| DUET-M-SL | `pair_plus_b35_m0_k128` | DUET-M with an analytic top-128 pair shortlist |
| greedy, ME-GA, NSGA-II | `greedy`, `me_ga`, `nsga2` | baselines |

The search methods and baselines are implemented in [GeoRIS-Bench](https://github.com/ElFariss/GeoRIS-Bench) (`src/atomwise_ris/optimization/`: `coupled_search.py`, `pair_plus.py`, `me_ga.py`, `nsga2.py`). The dataset is GeoRIS-Bench 1.0 on Mendeley Data, https://doi.org/10.17632/td3w4cwbg5.1.

## Where things are

| What | Path |
|---|---|
| Manuscript (LNCS, Overleaf-ready) | `paper/aciids2027-overleaf-final/` (zip: `paper/paper-a-aciids2027-overleaf-final.zip`) |
| Rotterdam sealed-test results (Tables 3–5) | `outputs/runs/bench_ris_relevant_v3_search_20261113/rr3_test_summary.{json,md}` |
| Cross-city results reported in the paper (Maastricht + Utrecht, N = 72; Table 7) | `outputs/runs/crosscity_20261114/audit_20261115/pooled_2city_maastricht_utrecht_20261115/` and `crosscity_{maastricht,utrecht}_summary.*` |
| Cross-city analysis plan (frozen before the test) | `docs/crosscity-search-declaration-20261114.md` (+ `.freeze.sha256`) |
| Rotterdam analysis plan (frozen) | [GeoRIS-NeuralPair](https://github.com/ElFariss/GeoRIS-NeuralPair) `docs/bench-ris-relevant-v3-search-declaration-20261113.md` |
| Cross-city runner and analysis scripts | `scripts/run_bench_search_crosscity.py`, `scripts/cc_*_20261114.*`, `scripts/verdicts_crosscity.py`, `scripts/collect_crosscity_20261114.py` |
| Per-city data checks | `outputs/runs/dataset_5city_audit_20261115/` |

Internal identifiers in these records (`ris_relevant_v3`, `rotterdam-rr3-NNNN`, `<city>-rx3-NNNN`) map to the public GeoRIS-Bench 1.0 names (`georis_bench_1.0`, `<city>-NNNN`); see GeoRIS-Bench `docs/dataset-release-20261115.md`.

## Note on the cross-city records

The frozen cross-city plan covered four held-out cities. The records of all four are kept here for transparency. Munich failed its pre-declared RIS-leverage check at every array size, and Berlin failed it at 256 elements; the later relabelling files `leverage_gate_v2_*.json` were written after the check and are not used. The paper reports the two cities that pass every check at every array size (Maastricht and Utrecht). The verdicts are the same in the declared three-city pool (`pooled_3city_excluding_munich_audit_20261115/`) and in the original four-city pool (`pooled/`).

## Earlier work in this repository

The repository started as the free-space thin-wire study ("Paper 1", `docs/matched-v2-test-results-20261108.md`). Its files are frozen and must not be edited: `outputs/frozen/`, `configs/experiments/matched_v1.json`, `configs/experiments/matched_v2.json`. Older pilots are kept in `outputs/runs/` and `docs/`.
