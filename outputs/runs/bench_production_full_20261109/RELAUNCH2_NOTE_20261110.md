# Second relaunch, 2026-11-10 14:15 UTC (lead)

- At 14:01Z and 14:04Z workers w2 and w0 exited with PyNEC 'Unknown exception' while building their NEXT basis (256)
  after finishing 64/128. Cause: PyNEC does not return the memory of an earlier basis, so a second basis in one
  process hits the 24 GiB ulimit -v. Worker-level infrastructure failure; no unit or map FAILED record was written.
- No unit FAILED records existed or were cleared. The stop rule is unchanged.
- Fix: the worker re-execs itself before building a second basis (scripts/build_bench_production_channels.py).
- Stopped session cris-channels by name (w1 lost at most one in-progress unit; shards are written atomically).
- Moved to cleared_20261110/markers_relaunch2/: workers/w0.FAILED, workers/w2.FAILED, workers/w1.RUNNING or
  w1.FAILED, and LIVENESS_ALERT.
- State at relaunch: munich DONE (360/360 shards); rotterdam 64/128 complete, 256 107/120; maastricht 64/128
  118/118 traced cases, 256 0/118. Two Maastricht cases failed in TRACE on 2026-11-09 (0073 GPU-memory guard,
  0078 probes outside scene extent); they are untouched and count toward the map stop rule (2 of 120, limit is >2%).
