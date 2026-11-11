# Flash Task T6a Handoff: Full Production Declaration & Case Manifest (2026-11-09)

## 1. What was done
1. **Full production preregistration declaration**: Wrote `docs/bench-production-full-20261109.md` prior to generating any cases, specifying size (120 trajectories × 16 frames × 3 arrays over Munich, Rotterdam, Maastricht = 5,760 frames, 17,280 array-frames), frozen v1.1 challenge share (16.0%), disjoint seed stream rule (`[users.SEED, 20261109, im, i]`), exact pilot labeling protocol (all pairs at 64/128, sampled + 10th trajectory audit at 256), leave-environment-out and within-map 70/15/15 trajectory splits, budget caps (projected wall time 51.63 h $\le$ 72 h; storage 1.82% trace volume, 17.89% package volume $\le$ 60%), and fail-closed per-case/per-map gate checks with a 2% stop rule.
2. **Production case manifest generation**: Executed `scripts/build_bench_production_cases.py` in non-pilot mode with `--output outputs/runs/bench_production_full_20261109/cases.json --generate-count 120 --frame-count 16 --lead-approved-size`.
3. **Approved manifest registration**: Registered `FULL_HASH` and `FULL_CASES` for scope `development_full` in `src/atomwise_ris/bench/production_pilot.py`. The validation preserves existing pilot scope rules (`two_map_pilot`, `three_map_pilot2`) untouched while strictly validating `development_full` (hash match, `is_pilot == False`, scope `"development"`, freeze hash, 360 cases across the 3 development maps, and 16 frames per case).
4. **Unit test implementation**: Added `tests/test_bench_production_manifest.py` verifying registration and validation across all three scopes and negative tampering checks.
5. **Full test suite verification**: Ran full unit test suite `PYTHONPATH=src:scripts python3 -m unittest discover -s tests` and verified the immutable v1.1 generator freeze lock.

---

## 2. Manifest hash & SHA-256
- **Manifest path:** `outputs/runs/bench_production_full_20261109/cases.json`
- **SHA-256:** `21d54cfbf1db69721aedf89144afb95a38a5c7f0bafc9c0ee24273d445203adf`
- **Scope registered:** `development_full` in `src/atomwise_ris/bench/production_pilot.py`

---

## 3. Counts per map

| Metric | Munich | Rotterdam | Maastricht | Total |
|---|---:|---:|---:|---:|
| **Trajectories (cases)** | 120 | 120 | 120 | 360 |
| **Frames per case** | 16 | 16 | 16 | 16 |
| **Total frames** | 1,920 | 1,920 | 1,920 | 5,760 |
| **Array-frames (64/128/256)** | 5,760 | 5,760 | 5,760 | 17,280 |
| **Kinds** | 120 natural | 120 natural | 120 natural | 360 natural |
| **Challenge share** | 0.0% | 0.0% | 0.0% | 0.0% |
| **Total served user instances** | 354 | 343 | 355 | 1,052 |
| **Served users / case (min / mean / max)** | 2 / 2.95 / 4 | 2 / 2.86 / 4 | 2 / 2.96 / 4 | 2 / 2.92 / 4 |

---

## 4. Case driver audit & blockers

1. **Challenge subset limitation**:
   - The frozen preview generator (`scripts/generate_bench_users_preview.py`) declared a 16.0% challenge share (8 challenge cases out of 50 total).
   - In `scripts/build_bench_production_cases.py`, the driver's `new_cases()` function only invokes `c = natural(generator, t, rng, counts)` for each trajectory index `i in range(count)`. It does not call `create_challenge()` or generate any `kind == "challenge"` records.
   - Consequently, the generated manifest has 0.0% challenge share (all 360 cases are `natural`). If challenge cases are desired in production, the driver requires an extension to allocate challenge scenarios per map.
2. **Lead approved size guard**:
   - The driver enforces `if a.generate_count > 2 and not a.lead_approved_size: raise ValueError(...)`. Passing `--lead-approved-size` correctly authorized the full size.
3. **Local GIS dependencies**:
   - Following system reboot, `/tmp/atomwise-phase0b-audit-env` was absent and system Python lacked `pyarrow`, `rasterio`, `shapely`, `pyproj`, `embreex`, and `trimesh`. Installing these into local user site-packages enabled local execution without altering any project files.

---

## 5. Changed files
- `docs/bench-production-full-20261109.md` (new): Full production preregistration declaration.
- `outputs/runs/bench_production_full_20261109/cases.json` (new): 360-case production manifest.
- `src/atomwise_ris/bench/production_pilot.py` (modified): Registered `FULL_HASH`, `FULL_CASES`, and scope `development_full` in `registered_manifest()`.
- `tests/test_bench_production_manifest.py` (new): 7 unit tests covering manifest registrations and validation.
- `docs/flash-T6a-handoff-20261109.md` (new): This hand-back record.

---

## 6. Test results
- `PYTHONPATH=src:scripts python3 -m unittest discover -s tests`
- Result: **Ran 290 tests in 16.253s — OK (skipped=10)**.
- Generator freeze check: `verify_freeze()` passed (`e152e78cb7b66204ea4080339c29a80a53c94685f8c3743b4eddd0cbab6e0ecd`).

---

## 7. Remote jobs
- None. Task T6a is strictly local declaration, case generation, and manifest registration. No ray tracing or channel jobs were launched.

---

## 8. Open problems
- The case driver generates natural trajectories exclusively (0% challenge share vs. 16.0% declared preview share). If the lead wants challenge trajectories included in the full build, a driver change will be needed before ray tracing starts.
