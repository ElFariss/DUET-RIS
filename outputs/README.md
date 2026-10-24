# Run artifacts

`runs/specular_v5` is the canonical exact-export campaign. `runs/specular_v4` retains the independent pre-reorganization pilot; `pilot_v1` and `specular_v3` contain earlier diagnostic labels/headroom and are not comparable final runs.

A complete v5 run contains:

- `manifest.json`, `resolved_config.json`, `source_snapshot.tar.gz`: frozen inputs, source hashes, dependency versions and actual source snapshot; no fabricated Git commit if the repository is still uncommitted.
- `headroom.json`, `*_labels.json/.npz`: training gate and completed-move labels with trajectory identity.
- `models/<variant>_seed<seed>/`: best checkpoint, epoch history, training metadata.
- `benchmark_validation.*`, `budget_selection.json`: complete CPU timing and validation-selected budget.
- `benchmark_pilot.*`: paired development evaluation, raw actions and component timing.
- `summary.json`, `REPORT.md`, `rate_runtime.png/.pdf`: aggregate result and trajectory bootstrap intervals.
- `sensitivity.json`, `sensitivity_summary.json`: shared response stress tests at fixed actions and precoder.
- `logs/`: command output; exclusive creation protects existing logs.

Timing records are machine-specific. Seeds improve repeatability but do not make wall-clock-budget searches or GPU ray tracing bitwise deterministic. One-time model load/warmup and disk I/O are outside online timing; per-observation preparation, features, retrieval, inference, search and evaluation are included. At 1 ms neural entries may use initialization with no learned inference; consult the recorded inference fraction.
