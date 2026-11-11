# Codex brief: generator freeze, P4 closure, production pipeline and pilot (2026-11-09)

Acceptance decisions are reviewed centrally. agy works in parallel (see `docs/agy-brief-bench-20261109.md`).

All earlier rules apply:
- `faris` only. 3060-3 via `ssh -J faris@100.68.29.126 -p 2003 faris@gpu-labkc.ub.ac.id`; rx6600 via `faris@100.89.211.119`.
- Never use 3060-2 or 3060-1 for compute. GPU work runs on 3060-3, kept off CPUs 5 and 11.
- Frozen Paper 1 material stays untouched.
- Criteria are declared in a dated doc before each run and never loosened.
- Durable tmux jobs with DONE/FAILED markers and resume manifests; no sleep polling.
- No commits, Sheet or manuscript edits.
- The suite stays green: `PYTHONPATH=src:scripts python3 -m unittest discover -s tests`.
- **Never open Berlin or Utrecht data, or `coupled_wire_test_v1`, `coupled_wire_test_v2`, `coupled_wire_test_v2_fine161`.**

## File ownership
- **agy owns this round:**
  - `scripts/run_bench_rt_preview_smoke.py` (the Maastricht mesh fix);
  - `scripts/train_pair_selector_gpu.py`, `src/atomwise_ris/optimization/pair_select.py`;
  - packaging `bench/CoupledRIS-Bench/physics/array_256/`.
- **You:** do not edit those files. For production ray tracing, write a new production module or script that **imports** the scene builders from agy's script, or copies them only after agy hands back the Maastricht fix.

## User decisions (2026-11-09)
1. **Generator v1.1 is approved** after the user reviewed all 50 cases in ParaView.
2. **P4 is closed** as passed on the ray→wire conversion checks:
   - line of sight: <0.05% error;
   - controlled PEC-plane reflection: <0.05% error.

   The urban-reflection reference requirement is dropped, with this declared reason: city propagation is Sionna's validated job, and NEC-2 is used only for RIS coupling. Material uncertainty stays out of scope.
3. **256 elements use the 81-segment mesh only.** The 161 run needs about 54 GB, over the 53.5 GB cap. The mesh argument comes from the 64 and 128 trend (0.63% and 0.88%).
4. **The `bs_link` preview label stays as it is.** Production link classes come from ray tracing.

## Task 1: generator freeze (small; do first)
Write `docs/bench-users-v1.1-freeze-20261109.md`. It must record:
- the v1.1 source files and their SHA-256;
- the parameters doc, seed scheme and source manifest hash (`recovered-source-manifest.json`);
- the validation hash `722bf2b4…`;
- the geometry and ground-fill audit hashes.

Production must refuse to run if any frozen file hash differs.

## Task 2: P4 closure record (small)
Write `docs/p4-closure-20261109.md`. It must cover:
- the user decision;
- the evidence files: `outputs/runs/p4_calibrated_20261108/full_gate.json` and the reflection docs;
- the tolerances, unchanged;
- exactly what is and is not validated.

Update the README's methods text to match. Do not alter the old gate artifacts.

## Task 3: production pipeline (development maps only: Munich, Rotterdam, Maastricht)
Build the pipeline that fills the `bench/CoupledRIS-Bench` layout given in the plan (project plan, Phase 4 and the Amendment). The steps:
1. **Cases.** Generate them at scale with the frozen v1.1 generator, giving many sites and trajectories per map.
2. **Ray tracing.** Run Sionna RT on 3060-3 with per-element probes at the NEC lattice for 64/128/256, both polarizations, reflections and diffraction on, transmission off. Declare the max depth and samples. Store per-path angles, delays and coefficients at the RIS elements and users. Record exact link classes (LOS, reflection-only, diffraction-only, blocked) for BS→user, RIS→user and BS→RIS.
3. **Channels.** Use the validated P4 conversion with the open-gap term in `H_direct`: `H_direct`, `C_in`, `C_out` and the noise and precoder conventions go into `channels/channel_realizations.h5`, with `Z_RIS` from `physics/array_*`.
4. **Labels.** Write `optimization/{single_flip_gains,pair_flip_gains,synergy}.h5` at sampled parent states, generalizing `scripts/harvest_pair_parents.py` and `scripts/build_pair_labels.py` to `HybridCoupledNetwork`. Use all pairs at 64 and 128; at 256, sampled pairs plus a full-label audit subset.
5. **Packaging.** Write `trajectories.parquet`, `splits/` (leave-environment-out among the development maps plus within-map trajectory splits; held-out maps are not generated), `provenance.json` and `examples/load_dataset.py`. The loader must reproduce a stored rate to 1e-10.

**Maastricht:** its scenes currently give exactly one path per probe, which is under investigation by agy. Build and pilot on **Munich and Rotterdam first**, and add Maastricht only after agy's fix is accepted by the lead.

### Pilot gate (stop here and hand back)
Declare the following in `docs/bench-production-pilot-20261109.md` **before running**:
- the target production size: cases per map, frames, arrays, label sampling;
- pass criteria: loader round-trip, link-class sanity versus the geometry labels, the HDF5 schema check, no NaNs, and storage and runtime per case.

Then run a pilot on a small declared subset of Munich and Rotterdam and report:
- the measured runtime, GPU memory and storage per case;
- a projection for full production.

**Do not launch full production.** The lead approves its size first.

## Hand-back
Write `docs/codex-handoff-bench-production-20261109.md` with:
- results per task and the changed files;
- running jobs, with check commands;
- the projection and risks.

End with a short summary.
