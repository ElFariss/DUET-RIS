# Flash Task T6c Handoff: Separate Challenge-Subset Manifest (2026-11-09)

## 1. Environment reproducibility check
- **Command / method:** Regenerated natural case `munich-v11-0000` (`im=0`, `i=0`) into `/tmp/work-1012/t6c-repro/` using the unchanged natural code path.
- **Original frames SHA-256:** `030cb6e729bf046cc4457cac297ae44eb6160fae9e35aba87575b28186d4b9a2`
- **Reproduction frames SHA-256:** `db2a123094f4638adbf4cb86d32966e41bdf5fd4b6ef6b882f919081cfdefd41`
- **Result:** **Mismatch**.
  - All case metadata in `case.json` (crowd size 21, served users `[5, 6, 8, 16]`, initial link counts `{'no_los': 16, 'los': 5}`, geometry distances, coordinates) matches identically.
  - The diff in `frames.parquet` is isolated to sub-epsilon floating-point trigonometric differences (`slope_deg`, `bs_az_deg`, `bs_el_deg`, `ris_az_deg`, `ris_el_deg` with maximum absolute difference $\approx 2.84 \times 10^{-14}$) and pyarrow metadata format (`parquet-cpp-arrow` 24.0.0 on AMD-kc vs. 26.0.1 on the original host).
  - Per instructions, the natural output tree was left completely untouched.

---

## 2. Challenge manifest identity
- **Manifest path:** `outputs/runs/bench_production_full_20261109/challenge_cases.json`
- **SHA-256:** `999d221ef4b3ac46ad7a66871cd176470d38cd08faac051159826b4575205f91`
- **Registered scope:** `development_challenge` in `src/atomwise_ris/bench/production_pilot.py`
- **Total cases:** 69 (23 per development map)
- **Frames per case:** 16 (1,104 frames total; 3,312 array-frames)

---

## 3. Per-map metrics & counts

| Metric | Munich | Rotterdam | Maastricht | Total / Summary |
|---|---:|---:|---:|---:|
| **Total cases** | 23 | 23 | 23 | 69 |
| **`shadow_edge`** | 5 | 5 | 5 | 15 |
| **`shadow_edge_sloped`** | 5 | 5 | 5 | 15 |
| **`all_no_los`** | 5 | 5 | 5 | 15 |
| **`dense_crowd`** | 4 | 4 | 4 | 12 |
| **`elevated_crowd`** | 4 | 4 | 4 | 12 |
| **Substitutions** | 0 | 0 | 0 | 0 (0.0%) |
| **Served users (min / mean / max)** | 2 / 2.70 / 4 | 2 / 3.13 / 4 | 2 / 2.96 / 4 | 2 / 2.93 / 4 |
| **Shadow cases total** | 10 | 10 | 10 | 30 |
| **Shadow cases with LOS change in 16 frames** | 10 (100%) | 10 (100%) | 10 (100%) | 30 (100%) |

All 69 challenge trajectories succeeded on their primary requested scenario on the single target map without substitutions. Every shadow trajectory preserves its leader LOS transition within the 16 selected frames.

---

## 4. Natural manifest SHA-256
- **Before task execution:** `21d54cfbf1db69721aedf89144afb95a38a5c7f0bafc9c0ee24273d445203adf`
- **After task execution:** `21d54cfbf1db69721aedf89144afb95a38a5c7f0bafc9c0ee24273d445203adf`
- **Status:** **Unchanged (identical)**.

---

## 5. Changed files
1. `scripts/build_bench_production_cases.py`:
   - Added `CHALLENGE_ORDER = ("shadow_edge", "shadow_edge_sloped", "all_no_los", "dense_crowd", "elevated_crowd")`.
   - Added `challenge_on_map(g, category, t, rng, counts)` mirroring single-generator branch logic.
   - Added `choose_challenge(generator, i, t, rng, counts)` implementing deterministic category order and cyclic substitution up to 20 attempts per category.
   - Added `challenge_cases(root, cache, count, n_frames)` keeping full site pool and writing `-v11c-` cases with challenge metadata.
   - Added `--challenge` CLI flag with size guard (`--lead-approved-size` required, count $\le 23$).
2. `src/atomwise_ris/bench/production_pilot.py`:
   - Added `CHALLENGE_HASH` and `CHALLENGE_CASES` (69 cases across Munich, Rotterdam, Maastricht).
   - Registered scope `development_challenge` with validation of subset, kind, 16 frames, and freeze lock.
   - Added `PRODUCTION_SCOPES = ("development_full", "development_challenge")` and `registered_scopes()` helper.
3. `tests/test_bench_production_manifest.py`:
   - Extended unit tests to 12 tests covering challenge registration, tamper rejection (wrong subset, non-challenge kind, missing case, altered pilot/frame counts), scope cross-validation rejection, `challenge_on_map` isolation (fake generator), and deterministic substitution.
4. `docs/bench-production-full-20261109.md`:
   - Appended `## Amendment 2026-11-09: separate challenge subset (lead decision)` recording subset specifications, isolation policy, separate 2% stop rule, and updated runtime projection (429 trajectories, 61.5 h $\le$ 72.0 h).
5. `outputs/runs/bench_production_full_20261109/challenge_cases.json`:
   - Generated separate 69-case challenge manifest.
6. `outputs/runs/bench_production_full_20261109/cases/*-v11c-*`:
   - 69 case directories containing `case.json` and `frames.parquet`.
7. `docs/flash-T6c-handoff-20261109.md`:
   - This hand-back documentation.

---

## 6. Test results
- `PYTHONPATH=src:scripts .venv/bin/python -m unittest tests/test_bench_production_manifest.py`:
  - **Ran 12 tests in 1.030s — OK**
- `PYTHONPATH=src:scripts .venv/bin/python -m unittest discover -s tests`:
  - **Ran 302 tests in 10.224s — FAILED (failures=1, skipped=10)**
  - Failure: `test_memory_ga_ranking_uses_pattern_spread` in `tests/test_matched.py` (known, pre-existing Paper 1 CPU-math discrepancy documented in common rules). All 301 other tests passed.
- Generator freeze check: `verify_freeze()` passed (`e152e78cb7b66204ea4080339c29a80a53c94685f8c3743b4eddd0cbab6e0ecd`).

---

## 7. Remote jobs
- None. Task T6c is strictly local driver extension, challenge case generation, manifest registration, tests, and documentation. No remote jobs or GPU ray tracing were launched.

---

## 8. Open problems
- None. The challenge subset is fully generated, verified, registered, and isolated from natural splits.
