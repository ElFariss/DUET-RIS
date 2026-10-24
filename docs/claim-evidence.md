# Claims supported by this repository

| Statement | Evidence | Limit |
|---|---|---|
| Cached single/pair updates implement the full evaluator | Numerical tests, per-result full recomputation, scenario audit | Mathematical correctness of an approximate physical model |
| Whole trajectories stay within one split | Scenario validation and saved trajectory IDs | Only 24 trajectories; no untouched final paper set |
| Completed two-bit improvements exist after single-bit convergence | `headroom.json`, training trajectories only | Does not imply learned edits beat analytical pair search |
| Neural inference overhead is included | Complete CPU timing, per-component durations, inference activity | One Ryzen CPU; excludes CSI acquisition/model load and RF switching |
| Exported paths reproduce the originating coherent channel | Nine export audits, 68 transmitter coordinates | Float32 phase/delay precision; default DeepMIMO summed taps are not the tested carrier-phase convention |
| Learned mutation improves the current nominal pilot | **Not established**; both v4 and canonical v5 favor pair/greedy | Use the exact-export v5 report for canonical current results |
| Attention, memory or meta-atom awareness is novel by itself | **Not established** | A contribution requires a demonstrated benefit and literature comparison |
| The controller is ready for hardware or a microcontroller | **Not established** | No target hardware, coupling calibration, switching latency or RF validation |

## Reading the ablations

`attention_no_physics_ga` removes explicit response and complex-contribution features, but retains exact analytical flip scores and thus still has indirect physics information. It is not a wholly physics-free controller.

`attention_no_conditioning_ga` removes the marker for the first selected bit. The bit is still excluded from the second draw, so every two-bit mutation selects distinct cells. Supervision uses completed pair gain from the original parent, including beneficial pairs whose first flip alone is harmful.

`attention_no_memory_ga` disables causal retrieval of previous configurations while using the same attention checkpoint. Memory resets at trajectory boundaries and retrieved configurations are rescored on the current channel. It is not a learned recurrent memory encoder. Population-frequency/recent-edit feature slots remain zero in this pilot.

The MLP and attention receive the same observations and completed-move supervision. Their parameter counts are 18,145 and 18,113. All GA variants use population 12, memory capacity 8, 25% crossover, 50/50 one/two-bit edits and 5% uniform exploration. These architecture/GA constants are implemented in the source, not adjustable through the job configuration.

## Decisions

Keep the simpler controller when learned gains fail to offset overhead. Validate the response model before attributing small improvements to hardware awareness. Any method revision informed by these pilot results uses development data; a future claim needs an untouched final set, targeting at least 30 independent trajectories and 10 paired seeds.
