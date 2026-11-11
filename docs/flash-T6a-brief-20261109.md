# Flash task T6a: declare full production and generate its case manifest

Read `docs/flash-common-rules-20261109.md` first.

## Background
- **The pilot passed.** The three-map pilot (Munich, Rotterdam, Maastricht; frame 0; arrays 64/128/256) is complete. See `outputs/runs/bench_production_pilot2_20261109/pilot_gate.json` (`status: pass`).
- **Its projection** (`production_projection`):
  - full size: 360 trajectories, 5,760 frames, 17,280 array-frames;
  - storage: about 13 GB;
  - time: about 52 h serial, mostly the channel step (`channel_s` ≈ 164,000 s), plus about 1 h of one-time NEC setup.
- **The user approved full production.**
- **The pilot plan:** the production label plan is already written in `docs/bench-production-pilot-20261109.md` (lines 10–20: selected frames, two parents, pair coverage). The case driver is `scripts/build_bench_production_cases.py`. The approved-manifest registry is `src/atomwise_ris/bench/production_pilot.py`.

## Your task
1. **Write the declaration** `docs/bench-production-full-20261109.md` **before generating anything.** It must state:
   - **Size:** 120 trajectories per development map (munich, rotterdam, maastricht) × 16 selected frames, at arrays 64/128/256. Include the separately labelled challenge subset at the frozen v1.1 generator's own declared share; state that share.
   - **Seeds:** a seed stream disjoint from the preview and the pilots. State the exact seed rule and show it cannot collide with them.
   - **Labels:** exactly as in the pilot doc lines 10–20.
   - **Splits:**
     - leave-environment-out rotation over the three maps;
     - within-map trajectory split for training (state the fractions, for example 70/15/15 by trajectory, grouped so no trajectory is split).
     - No Berlin or Utrecht.
   - **Budget caps:**
     - projected wall time ≤ 72 h;
     - storage ≤ 60% of free space on each target volume. Use the free bytes recorded in the gate.
   - **Pass criteria per case and per map:** the same checks as the pilot gate (schema, finite, loader 1e-10, mesh preflight). Also a stop rule: if more than 2% of a map's cases fail, stop that map.
2. **Generate the production case manifest** with `scripts/build_bench_production_cases.py` in its non-pilot mode, running it locally. If it needs a small change to support the full size, make it, with a unit test.
   - Write the manifest to `outputs/runs/bench_production_full_20261109/cases.json`.
   - Record its SHA-256.
   - Report the counts per map: trajectories, frames, the challenge share, and served users.
3. **Register the manifest as approved** for scope `development_full` in `src/atomwise_ris/bench/production_pilot.py`, the same way `PILOT2_HASH` is registered, with a test. **Do not change** how the existing pilot scopes validate.
4. Run the suite (must be green).

## Do not
- trace or run channels; that is a later task;
- change the trace, channel or package scripts' logic, beyond what step 3 needs.

## Hand-back
`docs/flash-T6a-handoff-20261109.md`, with:
- the manifest hash;
- the counts per map;
- anything in the case driver that blocked the full size.
