# Coupled-wire development and v2 data generation

This note tracks trajectory-only NEC-2 data for the planned matched-v2 search work. The frozen `coupled_wire_test_v1` and all v1 results remain unchanged. The registered v2 test set is data-only: this work does not generate test labels, run controllers on test frames, or compute test results.

## Set registry and observed artifacts

Each trajectory set has 30 independently sampled trajectories with 16 frames each. The registered seed/split mapping lives in `scripts/generate_coupled_test.py` and is enforced as a name/seed/split tuple.

| Set | Seed | Split | Mesh | Frames | Scenario SHA-256 | Status at this handoff |
|---|---:|---|---:|---:|---|---|
| `coupled_wire_dev_v1` | 20261107 | dev | 81 | 480 | `e78ddb7f5c551133efb271e968f2c49c5742391f43ba8178cbb0334fc43426cf` | Complete; all frame NPZ sidecar hashes verified |
| `coupled_wire_validation_fine161` | inherited | validation | 161 | 48 | `410429f3a943721b92044acd99782ed3c4d8a2db47c21e33f36719d307ab554d` | Complete; source scenario SHA-256 `5880584639bdeea45dca0e0c37fe82fb9ac69d4f891050d136c5a654c8e0ea21` |
| `coupled_wire_test_v2` | 20261108 | test | 81 | 480 | `de08a1495d295946bcc7b39b952c3523efd006e90527a3802252375f5147bb58` | Geometry/matrix generation complete; no controller or label evaluation |
| `coupled_wire_dev_fine161` | inherited | dev | 161 | 480 | `101b49a99966ab49b553163ba97dd32b9b157b96fef2c9fd94a3df20f49559dc` | In progress on rx6600; 44 frame sidecars verified at 2026-11-07 00:22 WIB |
| `coupled_wire_validation_refinement201` | inherited | validation subset | 201 | 4 selected / 48 expected | `d93023a89c0e13e4afec058b917b7bcfff0c3e9a6e1e14140c513a58b11ea11b` | Four selected indices complete and validated; 44 of 48 rows intentionally missing, manifest remains partial |

Fine-mesh scenario files preserve the source row positions and indices and pin the source scenario SHA-256. A frame is reusable only when its NPZ checksum, expected row metadata, mesh size, generator identity, matrix dimensions/finiteness, and passivity diagnostics match. `generation_status.json` records the exact protocol/source hashes, expected and verified frame indices, per-frame NPZ checksums, and validation outcome. Partial `--only-indices` jobs remain marked partial until every expected row verifies. A changed protocol or source-code hash blocks resume without deleting the existing artifacts.

## Fine development generation

The full source scenario is `data/processed/coupled_wire_dev_v1/scenario.json` (SHA-256 above). It contains 480 dev-only frames from seed 20261107. Fine-mesh extraction uses the exact same positions and frame indices with 161 segments per wire; it performs no test split extraction.

Command, from the staged project root on rx6600:

```bash
bash scripts/run_coupled_dev_fine161.sh
```

The driver fixes BLAS/OpenMP thread counts to one and uses four NEC workers. Its remote output is `/var/tmp/atomwise-ris-gen-20261106/data/processed/coupled_wire_dev_fine161`; log and durable runner session are recorded below. The 48-frame validation fine mesh measured a mean of about 245 seconds per frame and 3.6 MB total output. This is a physical-data generation job, not a rate benchmark, so it does not use 3060-1. The observed rx6600 environment is Python 3.12.3, NumPy 2.2.6, and PyNEC 2.3.4. A separate bounded 201-segment validation refinement uses node3 with an isolated venv; no global packages or sudo were used. 3060-2 is not used.

At launch, the local source hashes were:

| File | SHA-256 |
|---|---|
| `scripts/generate_coupled_test.py` | `3687b11c8897a3a0d87e49c3685af2347c8b8b27c453f82cccbdf480d2ca71ef` |
| `scripts/generate_coupled_reference.py` | `d2a9ed1ef11b12b6de04a9926759b6983df0e157ff9f932fbaedce0baf6b4074` |
| `src/atomwise_ris/physics/nec.py` | `d982356599afa2e561db0303d7ac28fe004698f16aea68a85c5442c85fe29876` |
| `scripts/run_coupled_dev_fine161.sh` | `eff0a896a0fab9b65545de1ea5751a74de7bb807f766986abe8ddb949eeb23c1` |

The test-v2 scenario checksum is checked before and after generation; generation output is written to a separate dev-only directory. Do not run `benchmark*.py`, label generation, controller evaluation, or test analysis on `coupled_wire_test_v2` as part of this task.

## Launch record

| Field | Value |
|---|---|
| Target | rx6600 (`labkc1-amd`) |
| Start time (Asia/Jakarta) | 2026-11-06 23:35:48 |
| Durable session/job | tmux `coupled-dev-fine161-20261106` (`~/compute-jobs/coupled-dev-fine161-20261106`) |
| PID | 271624 (parent); workers 271647–271650 at first process readback |
| Command | `bash scripts/run_coupled_dev_fine161.sh` |
| Log | `/var/tmp/atomwise-ris-gen-20261106/logs/coupled_wire_dev_fine161.log` |
| Status | Running; 480 expected frames; generation identity SHA-256 `e324cdddd4f1cccccf48dbb3a58e49978f8da5977ab9e7d8dd2b247ea46e7bc8`; first live readback at 2026-11-06 23:40:49 showed four sidecar-verified frames (indices 0–3) |

The first four frame solve times were 246.85, 245.45, 244.48, and 246.14 seconds. At 00:22 WIB, a direct read-only check found 44 completed NPZ/sidecar pairs with matching SHA-256, generation identity, mesh size, and `dev` split; no invalid sidecars. With about 7.7 hours remaining at the observed pace, estimated completion is around 08:00 WIB, subject to runtime variation. The four active workers each held about 4 GiB RSS in the earlier sample, with substantial host memory available. The active run was not interrupted. The lab VPN was unavailable through the wrapper, but direct SSH status checks succeeded.

## Bounded 201-segment validation refinement

The node3 experiment extracts only validation frames 32, 96, 160, and 174 from `coupled_wire_v1` at 201 segments per wire. It is a four-frame physics diagnostic, not the full 48-frame validation split. The output's `generation_status.json` therefore remains `partial` with 44 expected rows missing and `ready_for_development_evaluation=false`; it must not be represented as a complete validation set. This run does not access any test rows or labels.

The isolated node3 workspace is `/mnt/home/faris/projects/atom-wise-ris-v2-20261106`; output is `outputs/coupled_wire_validation_refinement201`, and the driver is `scripts/run_coupled_validation_refinement201.sh`. It uses Python 3.12.3, NumPy 2.2.6, SciPy 1.15.3, and PyNEC 2.3.4 in a project-local venv. Source and input scenario hashes are listed in the launch record. The destination scenario SHA-256 is `d93023a89c0e13e4afec058b917b7bcfff0c3e9a6e1e14140c513a58b11ea11b`; generation identity SHA-256 is `fd9bb9e6fcedde440202608485ce9fe0fa9940f9f5d56bdeef7ce10eff74d0`. A byte-preserving copy of the four frame NPZ/JSON pairs, this scenario, and the final manifest is at `outputs/audits/v2-20261106/mesh201_selected_frames/`; local copy hashes match node3.

| Field | Value |
|---|---|
| Target | node3 (`labkc-comm3`, port 2003) |
| Initial / resumed start time (Asia/Jakarta) | 2026-11-06 23:51:45 / 2026-11-06 23:57:55 (same session and output) |
| Durable session | tmux `coupled-validation-refinement201-20261106` |
| Current parent PID | 1712058; workers 1712060–1712062 |
| Command | `bash scripts/run_coupled_validation_refinement201.sh` |
| Log | `/mnt/home/faris/projects/atom-wise-ris-v2-20261106/logs/coupled_wire_validation_refinement201.log` |
| Driver SHA-256 | `0e63f7aa19c925efada1fe4a44614ed7b0c6e7ab4b06c26963ff5ee89071012f` |
| Final manifest SHA-256 | `b5ec15693a35bc2e50888ab8f4330dcbfd6cbc2788e8652199521a58b2edab4b` |
| Final status | Partial by design; 4/48 expected indices validated, 44 missing, 0 invalid; ready-for-development-evaluation is false |

The first four-worker attempt reached 25.7 GB of session memory (about 6.3 GB per worker), exceeding the requested approximate 24 GB budget. It was stopped before any frame NPZ completed. The exact same output, selected frames, protocol identity, and source hashes were resumed with three workers; this does not alter the generated physics. Frames 32, 96, 160, and 174 took 585.04, 575.28, 566.26, and 541.89 seconds, respectively, and all passed `validate_frame` for checksum, identity, exact validation-row metadata, 201-segment matrices, finiteness, and passivity. The run ended at 2026-11-07 00:18:11 WIB with status `partial`: 44 of the 48 expected validation indices are missing by design, with zero invalid frames and `ready_for_development_evaluation=false`. No full-split evaluation or test evaluation was run. This output has no dependency on the separate rx6600 161-segment development generation.

Local archive verification reran the same `validate_frame` function against all four copied NPZs, checked each local digest against the final manifest, and confirmed scenario, manifest, sidecar, and NPZ hashes match the remote output. The archive is a validation-only subset and must not be relabeled as a full split.

| Validation frame | NPZ SHA-256 | Min resistance eigenvalue (Ω) | Max scattering singular value | Reciprocity relative |
|---:|---|---:|---:|---:|
| 32 | `d69753be04413727edd2e29d5f1d28175e3ef7132bc91a8ce3d177ad68ae732a` | 0.53935586 | 0.98666663 | 4.7969e-9 |
| 96 | `ad1d4151fb80a3ea507f804b3c827a31f785461cbefc6d06a08f1ee1421335f3` | 0.53936229 | 0.98666646 | 4.7980e-9 |
| 160 | `382e5b6a46b18b380a0c08531e1a33297ce6a1de3b51b05f8683d8457993f211` | 0.53936591 | 0.98666640 | 4.7595e-9 |
| 174 | `25ecbb97ceefc8575a4540a2b6a68aa698df58c1833f85bc9f040787ba817921` | 0.53933626 | 0.98666709 | 4.7546e-9 |

The selected 201-segment validation diagnostic is complete, with no further frames in this artifact. The job is not a complete validation split. Preserve the output and manifest as recorded; do not relabel it or overwrite it with a broader run.
