# Pair-search profiling tool (v2 development)

[`scripts/profile_pair_v2.py`](../scripts/profile_pair_v2.py) runs the matched-v1 `pair` controller with a delegating observer and `cProfile`, using the frozen shared controller configuration from `configs/experiments/matched_v1.json`. It does not edit or replace the search/network implementation. The output separates network construction from the search call and records wall time, returned evaluation count, the observer's actual score and scan candidate counts, restart state builds, function call counts, and cumulative `cProfile` hotspots. Protocol hash is recorded with the per-frame provenance.

This is a descriptive diagnosis only. `cProfile` adds overhead and can alter a deadline-limited search path. The script therefore also runs an unprofiled companion with the same frame, seed, budget, and observer, and records their elapsed-time ratio as an overhead proxy. Neither the profiled nor companion rate/time is eligible for method selection or official benchmark reporting. The observer itself also adds a small amount of overhead to both runs. Method timers are inclusive: `moves` includes its nested scoring call, so component times are not additive. The reported inverse counts are explicitly inferred from the unchanged `CoupledNetwork` contract: one external-block inverse during construction, one inverse per `state` call, and small `solve` updates (no inverse) during `flip`.

The input gate accepts only the canonical `coupled_wire_dev_v1` 81-segment dataset or `coupled_wire_dev_fine161` with a readiness manifest hash-bound to the canonical DEV scenario and exact DEV index set. It verifies every sidecar/frame hash before use and rejects test paths/splits. `--indices` is mandatory, accepts at most ten distinct frame indices, and the budget is capped at 100 ms. The output records selected counts per trajectory alongside each frame's available trajectory count.

Example for the coarse development smoke set, with a CPU selected from the remote process's allowed affinity and a fresh output path:

```bash
PYTHONPATH=src python scripts/profile_pair_v2.py \
  --data data/processed/coupled_wire_dev_v1 \
  --physics-gate outputs/runs/coupled_wire_v1/physics_gate.json \
  --protocol configs/experiments/matched_v1.json \
  --indices 0,16,32,48,64,80,96,112,128,144 \
  --seed 7 --budget-ms 100 --cpu 0 \
  --output /tmp/pair-profile-dev81-seed7.jsonl
```

Use the new frame-level `coupled_wire_dev_fine161` directory only after its `generation_status.json` reports complete development readiness. Its scenario must bind to the canonical coarse scenario hash. Choose indices explicitly from its verified DEV set and write to a different fresh output. Do not use any `test` split, frozen v1 results, or profile rows as a benchmark comparison. Run the focused synthetic checks with:

```bash
PYTHONPATH=src python -m unittest tests.test_pair_profile -v
```
