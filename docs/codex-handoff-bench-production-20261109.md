# CoupledRIS-Bench production handoff — 2026-11-09 WIB

Scope: Tasks 1–3 only, with a hard stop at the development pilot gate.
No full production, Maastricht trace, held-out map access, old test-data
access, Git commits, manuscript or Sheet edits. agy's RT smoke, selector
and 256 packaging sources were not edited. All 13 frozen Paper 1 source
hashes and the frozen config hash still match.

## 1. Approved generator freeze

[Freeze record](bench-users-v1.1-freeze-20261109.md) and
`configs/bench/users-v1.1-freeze-20261109.json` pin all v1.1 source files,
the seed and parameter documents, the recovered-source manifest, the
validation (SHA-256 `722bf2b4…`), and geometry/overlay audits and arrays.
The anchored lock SHA-256 is
`e152e78cb7b66204ea4080339c29a80a53c94685f8c3743b4eddd0cbab6e0ecd`.
`src/atomwise_ris/bench/production_freeze.py` rehashes each file and is
called before the new generation, trace, channel and packaging entry
points. Checked locally and in the isolated channel workspace on 3060-3.
The approved generator files and preview were left untouched.

## 2. P4 closure

[P4 decision record](p4-closure-20261109.md) and the dataset README now state
the accepted scope. The registered Munich LOS and controlled PEC-plane
checks validate the no-fit ray-to-wire conversion; the original urban
reflection requirement was dropped by the user. The historical gate
artifacts remain unchanged. Native material accuracy and a full-wave urban
validation are outside this acceptance. The 256 archive is 81-segment only.

## 3. Pilot implementation

The [preregistration](bench-production-pilot-20261109.md) fixes the two
approved cases, frame 0, all three array sizes, RT settings and exact
gate checks. The prepared `outputs/runs/bench_production_pilot_20261109/pilot_cases.json`
has SHA-256 `998083842c02870e45724313151c15c77910754372baba6669776433206eb865`.
It reuses the original served-user sets; no new placement was substituted.

The case driver `scripts/build_bench_production_cases.py` can reuse the
frozen v1.1 generator, terrain overlays and approved site pool with a
disjoint seed stream. The default mode only extracts the approved pilot
frames. The trace pilot is separately constrained to the two cases.

- [Trace implementation](bench-production-trace-20261109.md):
  `scripts/run_bench_production_trace.py`, `run_bench_production_trace_job.sh`
  and `run_bench_production_munich_diag.sh`. Native
  pinned inputs, explicit polarized array probes, per-path interaction
  classification, timing and sampled GPU memory. Raw path arrays and
  native meshes stay on node3.
- Channel conversion: `src/atomwise_ris/bench/production_channel.py`,
  `scripts/build_bench_production_channels.py` and its durable wrappers.
  Applies the absolute P4 projection path by path, carries a RIS-only
  impressed-current open-gap term into the Schur operator, preserves
  archived 161/161/81 mesh choice and writes frame HDF5 and provenance.
  The same NEC factorization is reused across the pilot frames of each
  array. Reused-factor and independent open-gap solves matched in a real
  PyNEC test; the vertical projection matches the registered P4 Cartesian
  operator. Full pilot timing and scaling remain to be measured.
- [Packaging](bench-production-package-20261109.md):
  `scripts/package_bench_production.py` and the example loader. The focused
  synthetic test passed for HDF5, exact flip and synergy algebra, splits,
  Parquet, copied-file hash and loader round-trip. The integrated synthetic
  contract covered all six array-frames and 18 rows (one per served user
  and array), with 0 loader error and `3.553e-15` bit/s/Hz maximum dense
  round-trip error. These are synthetic contract results, not pilot rates.
- `scripts/verify_bench_production_gate.py` checks actual pilot coverage,
  packaged loader and dense rate readback, link sanity and resource/storage
  projection. It cannot authorize full production.

Local verification: the standard suite passed (277 tests, 13 optional
skips); two focused HDF5/Parquet packaging tests and three physical
projection/factorization tests passed in their respective environments.

### Resume / outputs

The frozen channel workspace on 3060-3 is
`/var/tmp/atomwise-bench-production-channel-20261109`.
The trace workspace is
`/mnt/home/faris/projects/bench-production-pilot-20261109/trace`.
Check markers before starting or resuming either:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -J faris@100.68.29.126 \
  -p 2003 faris@gpu-labkc.ub.ac.id \
  'tmux ls; for d in /mnt/home/faris/projects/bench-production-pilot-20261109/trace /var/tmp/atomwise-bench-production-channel-20261109; do ls -ld "$d"; for m in WAITING RUNNING DONE FAILED DEPENDENCY_FAILED; do if test -f "$d/$m"; then printf "%s: " "$d/$m"; cat "$d/$m"; fi; done; done'
```

The tmux jobs are `bench-prod-trace-20261109` and
`bench-prod-channels-20261109`. The channel job waits for a single trace
completion event through `scripts/run_bench_production_channel_after_trace.sh`,
then validates the trace, processes the arrays sequentially, assembles
`channels/`, writes `package/`, and runs the verifier to emit `pilot_gate.json`.
It starts no NEC work on a failed trace. After channel `DONE`, run
`sha256sum -c output_sha256sums` inside the channel workspace, then read
`pilot_gate.json`; `DONE` means the verifier finished, and a measured gate
may still say `fail`. The standalone package is checksummed via its
`provenance.json`. Transfer the compact gate and trace manifests, not native
meshes or raw paths. If a marker says `FAILED` or `DEPENDENCY_FAILED`, use
`logs/run.log` or `logs/wait_trace.log` in the channel workspace, or
`trace-job.log` in the trace workspace, before any deliberate resume. No
automatic model wake or full production is configured.

If the dependency needs a deliberate rearm after a documented trace fix,
first verify there is no live channel session or `WAITING`/`RUNNING` marker,
verify the trace is running or complete without `FAILED`, and archive any
previous dependency-failure marker and log. Then, on 3060-3 as Faris:

```sh
cd /var/tmp/atomwise-bench-production-channel-20261109
sha256sum -c --quiet STAGED_SHA256SUMS &&
  tmux new-session -d -s bench-prod-channels-20261109 -c "$PWD" \
    'taskset -c 2,8 bash scripts/run_bench_production_channel_after_trace.sh /var/tmp/atomwise-bench-production-channel-20261109 /mnt/home/faris/projects/bench-production-pilot-20261109/trace'
```

Channel staging file list SHA-256:
`7e428650e0818134a7f5be454343eb5b9d06d0a616344df15e98342a6ee5fe21`.
The first trace preflight hit a missing pinned Munich input and the channel
dependency stopped without touching NEC. The next preflight recovered the
Munich input and found a zero-area Rotterdam ring. Prior failure markers
and logs are retained. The zero-area-only retry then stopped on an invalid
projected Rotterdam `GroundSurface` outside the scene. The next retry added
the declared, counted scene-bounds crop and corrected the double origin
shift. It failed closed on `NL.IMBAG.Pand.0599100000640552-0/RoofSurface`
(`invalid projected face polygon`, `trace/FAILED` at 08:55 WIB).
This is LoD2.2 geometry 2, shell 0, face 56 in the pinned
`9-312-520.city.json.gz` tile: the ring self-intersects inside the declared
scene and covers 17.982 m² in its dominant projection. A local topology
diagnostic found an area-preserving polygon repair, but no repair was applied
to the mesh; accepting a repair requires a separately registered decision.
None of the two-map attempts reached GPU tracing. No channel conversion,
label generation or full pilot gate ran. The channel stage is staged but
idle; its first `DEPENDENCY_FAILED` records the first preflight failure.

### Measured Munich-only diagnostic

The first isolated Munich attempt stopped before solving because a metadata
field reached `PathSolver`. Its `FAILED` and log remain in `munich-diagnostic/`.
The corrected detached run traced the registered three sizes with the same
approved geometry/settings in a separate output
directory, `munich-diagnostic-retry1/`, beneath the trace workspace's parent.
It wrote `DONE` and never signaled the two-map channel dependency.

| Elements | Paths | Solver s | Export s | NPZ bytes | Sampled GPU0 peak MiB |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 5,693 | 1.433 | 0.307 | 264,737 | 775 |
| 128 | 9,210 | 1.012 | 0.430 | 422,376 | 807 |
| 256 | 17,217 | 1.481 | 0.758 | 759,114 | 841 |

This is 5.420 s and 1,446,227 raw bytes for one Munich frame across all
sizes. Timings exclude scene preparation/loading. Peak GPU use is the
device total sampled every 100 ms, not an allocation counter. A separate
readback verified each remote NPZ hash and byte count, port order and
coordinates against the archived array, and 12/12 Munich geometry LOS
checks. All three BS–RIS arrays had LOS. The local compact receipts in
`outputs/runs/bench_production_pilot_20261109/` are:

- `munich_trace_manifest.json`, SHA-256 `69b2449e4d5cba945cdda9a8115298fa8935ad9efd8681d3baf2636546f8c7b1`;
- `munich_trace_readback.json`, SHA-256 `70aad1f3a78adb422771caeec0178448a8e5296eb2d9d19cb48176cb7788a5f3`.

To check the remote diagnostic without opening any raw data, use the same
SSH command above with `cat /mnt/home/faris/projects/bench-production-pilot-20261109/munich-diagnostic-retry1/DONE`.
The geometry result from a single placement repeated across sizes is not
an independent trajectory sample or a channel/label gate result.

### Projection and risks

Proposed initial size: 240 trajectories, 3,840 selected frames and 11,520
array-frames across Munich/Rotterdam. Adding the conditional third
development map would yield 360 trajectories and 17,280 array-frames.
As a Munich-only RT planning estimate, scaling the diagnostic to 120 × 16
frames gives about 2.89 solver-plus-export hours on one GPU and 2.59 GiB
of raw paths. It assumes the same link and path density, excludes scene
loading and all NEC/label work, and is not an estimate for Rotterdam or
the full production build. A measured two-map projection requires the
remaining pilot artifacts. The CPU cost of the exact 128/256 wire factorizations,
long-run RHS history, float32 ray delay precision for multipath, and possible
native-geometry LOS disagreements are material pilot risks. The v1.1
placement labels are never promoted to physical path classes.
For budgeting only, previous *impedance-only* extractions took about 25 min
for 128×161 and 32 min for 256×81. Those are not measured production channel
times. The gate records solver/export, NEC setup, per-frame conversion,
label timing, sampled GPU memory and raw/derived bytes separately.
It checks the two storage volumes separately if the raw trace workspace and
the package workspace are mounted on different devices.
The trace/channel/package entry points are intentionally bounded to the two
pilot cases; the fresh-case generator and larger-size settings are prepared
for lead review, not proof that a full build is ready or authorized.
Before a new Rotterdam attempt, inventory the in-scene mesh failures and
register any proposed topology handling with the lead; retain this failure
receipt. Only then rearm the two-map trace and its channel dependency.
