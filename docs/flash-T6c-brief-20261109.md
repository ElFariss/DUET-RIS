# Flash task T6c: generate the separate challenge-subset manifest

Read `docs/flash-common-rules-20261109.md` first. Then read `docs/flash-T6a-handoff-20261109.md` and `docs/bench-production-full-20261109.md`.

## Background
- The declaration promises a separately labelled challenge subset at the frozen v1.1 generator's share (16.0%).
- The natural manifest `outputs/runs/bench_production_full_20261109/cases.json` (sha256 `21d54cfbf1db69721aedf89144afb95a38a5c7f0bafc9c0ee24273d445203adf`) has 0% challenge, because `scripts/build_bench_production_cases.py::new_cases()` only calls `natural()`.
- The lead's decision: keep the natural manifest **exactly as it is**, and add a **separate** challenge manifest of **23 trajectories per development map** (69 in total; 23 / (120 + 23) = 16.1%). It is its own scope and is never mixed into the natural splits.
- The local `.venv` already has the GIS packages (rasterio, shapely, pyproj, trimesh, embreex, pyarrow). Do not install anything else.

## Your task

### 1. Environment reproducibility check (report only)
Regenerate only natural case `munich` i=0 with the unchanged natural code path, into a scratch directory **outside** the repository (`/tmp/work-1012/t6c-repro/`). Compare its `frames_sha256` with `outputs/runs/bench_production_full_20261109/cases/munich-v11-0000/case.json`.
- Report match or mismatch.
- Either way, continue. Never write into the natural output tree.

### 2. Extend the driver with a challenge mode
Edit `scripts/build_bench_production_cases.py`. Add a `--challenge` flag that runs a new function `challenge_cases(root, cache, count, n_frames)`.
- **The natural path must not change in behaviour.** Do not edit `natural`, `compact`, `new_cases` or `approved_pilot`, except for a shared helper you factor out without changing results.
- **Frozen files stay untouched,** including `scripts/generate_bench_users_preview.py` and `src/atomwise_ris/bench/users.py`. `verify_freeze()` must pass.
- **Map and generator setup:** the same as `new_cases()` (same site pool, ground fill and `osm_point_hotspots`). Keep the **full** site pool on the generator, because the challenge methods choose their own site.
- **Seed rule** (state it in the doc): `np.random.SeedSequence([users.SEED, 202611092, im, i])`, with `im` the map index in `DEVELOPMENT` and `i` in 0..count-1. The value 202611092 differs from the preview/bulk words {1, 2, 3, 4, 5} and the natural production word 20261109.
- **Category per trajectory** (declared now, before running): `CHALLENGE_ORDER = ("shadow_edge", "shadow_edge_sloped", "all_no_los", "dense_crowd", "elevated_crowd")`. Trajectory `i` first tries category `CHALLENGE_ORDER[i % 5]`.
- **Generate on the target map only.** `create_challenge()` falls back to other maps, so do not call it. Write a single-map helper `challenge_on_map(g, category, t, rng, counts)` that mirrors `create_challenge`'s branch logic exactly for one generator:
  - same methods, same arguments, same `extra` dict;
  - `dense_crowd` keeps the `c.size >= 60` rule with 250 tries.
  - It returns `None` when the category cannot be produced.

  Call it up to **20 attempts** on the same `rng`. If the category still fails, substitute: try the next category in `CHALLENGE_ORDER` (cyclically), with the same 20-attempt limit, using the same rng. Record the substitution in the case (`requested_scenario`, `scenario`). If all five categories fail, raise an error. Do not loosen any challenge definition, threshold or the `write_case` checks.
- **Writing cases:** `write_case(root, g, site, c, t, case_id, "challenge", scenario, counts, rng, extra)`.
  - Case id: `f"{name}-v11c-{i:04d}"`.
  - Frames: the same 16-frame rule as natural.
  - Compacted record: `{**compact(root/"cases", case, frames), "kind": "challenge", "scenario": scenario, "requested_scenario": requested}`.
  - Add `shadow_user_id` / `first_shadow_transition_frame` when present in `extra`.
- **Manifest top level:** `{"scope": "development", "subset": "challenge", "is_pilot": false, "freeze_sha256": ..., "seed_word": 202611092, "challenge_order": [...], "cases": [...]}`.
- **Size guard:** `--challenge` requires `--lead-approved-size`, and `--generate-count` must be ≤ 23.

### 3. Run it locally
```
PYTHONPATH=src:scripts .venv/bin/python scripts/build_bench_production_cases.py --challenge --generate-count 23 --frame-count 16 --lead-approved-size --output outputs/runs/bench_production_full_20261109/challenge_cases.json
```
- The case directories land in `outputs/runs/bench_production_full_20261109/cases/<map>-v11c-NNNN/`. Natural ids differ, so nothing is overwritten.
- Check that `sha256sum outputs/runs/bench_production_full_20261109/cases.json` is still `21d54cfb…`, before and after.

### 4. Register the challenge manifest
In `src/atomwise_ris/bench/production_pilot.py`, add `CHALLENGE_HASH` and `CHALLENGE_CASES` (the 69 ids → map), registered as run scope **`development_challenge`**.
- `registered_manifest()` must validate, for this scope:
  - hash;
  - `scope == "development"`, `subset == "challenge"`, `is_pilot is False`, freeze hash;
  - exact id → map set;
  - 16 frames per case;
  - every case `kind == "challenge"`.
- **Do not change** how `two_map_pilot`, `three_map_pilot2` or `development_full` validate. A natural manifest must never validate as challenge, and vice versa.
- Add a helper `registered_scopes()` or a constant naming the production scopes `("development_full", "development_challenge")`. Later tasks will use it.

### 5. Tests
Extend `tests/test_bench_production_manifest.py` (or add a new test file). Cover:
- challenge registration;
- tamper rejection (wrong `subset`, a case with `kind == "natural"`, a missing case);
- the two scopes never cross-validate;
- `challenge_on_map` never touches another map's generator (use a fake generator object; no real map load);
- the category order and substitution are deterministic (fake generator).

Run the full suite (green, apart from the known failure named in the common rules).

### 6. Amend the declaration
Append a section to `docs/bench-production-full-20261109.md`, titled `## Amendment 2026-11-09: separate challenge subset (lead decision)`. It states:
- the 23-per-map size, the seed word, the category order and substitution rule, and the 20-attempt limit;
- that the subset is its own scope and manifest (path and sha256), labelled with the same protocol, and **never mixed into the natural splits or the leave-environment-out folds**: it is a separately reported evaluation set;
- that challenge trajectories use the same per-case checks and a separate per-map 2% stop rule. With 23 cases, 2% means any failed case stops that map's challenge subset;
- the updated projection: 429 trajectories; serial ≈ 51.63 h × 429/360 ≈ 61.5 h, under the 72 h cap.

Do not change any other part of the declaration.

## Do not
- trace, run channels or touch 3060-3;
- edit the trace, channel, package or gate scripts.

## Hand-back
`docs/flash-T6c-handoff-20261109.md`, with:
- the reproducibility check result;
- the manifest path and sha256;
- per map: the count per scenario, the substitutions, the served users (min/mean/max), and how many shadow cases have a LOS change inside the 16 selected frames;
- the natural manifest sha256, before and after;
- the test result and changed files.
