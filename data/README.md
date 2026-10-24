# Data inventory and reconstruction

## Canonical inputs

`processed/munich_specular_v3/scenario.npz` is the frozen input for `outputs/runs/specular_v5`.

SHA256: `346feaca8edc6bd1ed511fed229255ad776ab50854cee6d295e99ee4e35abe24`.

It contains the Sionna coherent CIR sums from the **same trace** exported to DeepMIMO under `raw/acquisition/munich_specular_v3`. It is not reconstructed by blindly summing DeepMIMO's default taps. All nine exports (four BS and 64 RIS transmitters) have been checked through carrier-phase-aware reconstruction; maximum relative L2 error is 0.001327, below the declared 0.01 float32 tolerance.

`processed/responses/opensourceris_v1.csv` contains the digitized ON/OFF magnitude and phase curves. The accompanying JSON records calibration, uncertainty, source commit, image hashes and applicability. `raw/opensourceris-and-upstream/` preserves the original reference images and source records.

`raw/deepmimo_scenarios/` contains both the retained older conversions and repaired names ending in `_fullpaths`. Use the names recorded by the repaired `trace.json` files. Original default 25-path conversions are retained for audit only.

## Dataset lineage

| Folder/run | Role |
|---|---|
| `raw/acquisition/munich_pilot` | Rejected initial geometry; do not train/evaluate |
| Other early/diffraction/convergence acquisitions | Diagnostic trials, not main results |
| `processed/munich_specular_compute_v3` → run v4 | Independent five-million-ray Sionna run; retained preliminary pilot |
| `processed/munich_specular_v3` → run v5 | Exact originating trace of the verified DeepMIMO export; canonical input |

The two five-million-ray runs are **not identical**: relative channel differences were approximately 0.0021% (BS→RIS), 0.454% (RIS→user) and 3.82% (direct). Preserve and identify their hashes rather than claiming exact repeated tracing. Raw arrays are saved before response application, precoding, labels or learned fitting.

The acquisition JSON includes a historical direct-only precoder description. This is acquisition provenance, not the current evaluator contract. The v4/v5 runtime uses an all-OFF-reference effective-channel precoder; see source and run manifests.

## Storage

The local workspace and lab mirror retain raw paths, channel arrays, checkpoints and timing records. These large files are excluded from normal Git; compact metadata, response tables, reports and configuration remain trackable. `artifact-manifest.json` inventories local evidence by path, size and SHA256. There is no public artifact download URL yet. A fresh clone must obtain this frozen artifact bundle or generate an independently identified dataset.

The main remote copy is `~/projects/atom-wise-ris` on port 2002. Outside the university network, use `faris@labkc-comm1` as SSH jump host. Authentication is outside the repository.

## Independent regeneration

Install simulation dependencies, then from the repository root:

```bash
uv sync --frozen --extra training --extra simulation
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/trace_munich.py \
  --out data/raw/acquisition/my_trace --samples 5000000 --no-diffraction
.venv/bin/python scripts/verify_all_exports.py --data data/raw/acquisition/my_trace
```

DeepMIMO writes conversion output under `deepmimo_scenarios/` in the working directory. Existing repaired exports are stored under `data/raw/deepmimo_scenarios/`; create a root symlink to that folder to re-run their audit. Use a new output name for every independent trace. Copy the saved scenario/layout into a new processed dataset directory and freeze its hashes in a new dataset configuration before training.

Important conversion details:

1. The exporter writes an incorrect diffraction metadata alias; the acquisition code records and corrects it.
2. DeepMIMO 4.0.5 converts only the first 25 paths by default. The wrapper temporarily raises the converter path capacity to the actual saved path dimension, then restores it. A larger loader limit alone cannot recover discarded paths.
3. Conversion changes transmitter ordering. Verification uses physical coordinate matching.
4. Reconstruct exported interaction phase with the carrier delay once; CIR coefficients already include it.

Response redigitization is available through `scripts/digitize_response.py`; use only the pinned source images and review the resulting overlay. Frequency interpolation is allowed inside the digitized range; extrapolation is rejected.
