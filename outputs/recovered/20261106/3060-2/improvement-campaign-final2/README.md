# Final2 validation campaign recovery

All results here are development-only validation data. No pilot or held-out test rows were read. Runs used node2 (`labkc-comm2`), CPU 0 pinned, single-thread BLAS/OMP, with CUDA hidden. The final2 source snapshot passed the complete local test suite (68/68); the independent gate review also passed. The older initial campaigns are preserved under `campaigns/` and listed in `superseded_campaigns.json`; final claims should use only the final2 directories below.

The validation grid covers 10 cases: five separate artifact roots (specular incumbent, new A, new B; coupled incumbent, new) under default and conditional-pair policy. Each case has 12 registered methods, seeds 7/19/43, and full validation frames at 5, 10 and 50 ms. There are 24 specular frames per seed across six trajectories (4 frames each) and 48 coupled frames per seed across three trajectories (16 frames each). Each campaign manifest verifies JSONL and sidecar hashes, complete method/seed/frame/budget coverage, source identity, and checkpoint hashes. There are 20 complete campaign directories, 90 JSONL files, and 36,288 result rows across all three budgets and cases.

## Observed results

These are descriptive row means and p95 runtimes, without inferential confidence intervals. The small number of trajectories (six specular, three coupled) limits generalization.

- Specular is at a rate ceiling: mean rates for analytical, MLP, attention, and pair methods are approximately 4.9733 bit/s/Hz across incumbent and both new checkpoint recipes at all three budgets. No learned-checkpoint improvement is visible in this validation slice.
- Coupled new checkpoints raise the descriptive 10 ms mean for MLP from 14.9570 to 14.9982 and attention from 14.9038 to 14.9297 bit/s/Hz. At 5 ms, MLP moves 14.9343→14.9618 and attention 14.8685→14.8935. At 50 ms, MLP moves 14.9857→15.0549 while attention moves 14.9591→14.9520.
- Pair remains higher-rate: at 10 ms it averages 15.0635 for both coupled incumbent and new controls; at 50 ms it averages 15.5077 incumbent and 15.5249 new. The 5 ms pair mean is 14.9817, also above the learned means shown above.
- Across all 12,096 observations per budget, deadline misses are 3/12,096 at 5 ms and 0/12,096 at 10 and 50 ms. All three 5 ms misses are in the new coupled conditional case: attention has 2 misses and attention-no-physics has 1. The new coupled conditional attention mean is 14.7506 at 5 ms versus 14.8935 default; conditional policy therefore needs more work before use at the tight budget.
- At 10 ms, conditional-vs-default paired rate changes are effectively zero for specular learned methods (roughly −0.00001 bit/s/Hz) and coupled learned methods (0 for MLP/attention), while the coupled conditional attention 5 ms case regresses as described above. Conditional inference costs additional elapsed time, around 0.6–0.8 ms for neural methods in these runs; refer to the paired contrast CSV for all exact deltas.

The new specular/coupled roots used freshly trained MLP and attention models. Existing incumbent attention-no-physics (and specular no-conditioning) checkpoints were retained as copied controls rather than retrained ablations. Old incumbent checkpoint roots were byte-preserved from the local canonical Oct24 `specular_v5` and `coupled_wire_v1` runs; their hashes and all new checkpoint hashes appear in `source_hashes_final2.json` and the per-campaign manifests. Thus this is not a complete retraining of every ablation.

## Files

- `method_summary_final2.csv`: mean rate, p95 elapsed time, candidate evaluations, miss counts, row counts, frame counts, and unique trajectories by case/method/budget.
- `paired_contrasts_final2.csv`: matched conditional-minus-default and new-minus-incumbent deltas by method and budget.
- `campaign_manifest_final2.json`: all 20 campaign identities plus hashes for all 90 JSONL files and metadata sidecars.
- `source_hashes_final2.json`: protocol/source/data/response/physics-gate and checkpoint hash maps.
- `superseded_campaigns.json`: identifies earlier runs retained for audit but excluded from final comparison.
- `campaigns/`: raw JSONL, JSON sidecars, campaign manifests, and command logs.

The validation summary is not a significance claim. Use the registered trajectory-level analysis, treating trajectories as the independent units (n=6 specular and n=3 coupled), and preserve the mesh-resolution limitation for coupled rates.

## Phase protocol archive

The exact node2 phase `matched_v1.json` and `coupled_wire_v1.json` are archived under `source_config/`. Their SHA-256 values match the protocol and source-config hashes recorded in the final2 campaign metadata. The node2 source tree was also reread: all 26 frozen code-file hashes, the campaign runner hash, and the selector-helper hash match the recorded phase values. The current local `matched_v1.json` was later amended (SHA-256 `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe`); it was not substituted into these historical campaign records.

## Later isolated temporal-v2 staging event (2026-11-06)

An independent temporal forecast task was first launched in the pre-existing `/home/faris/projects/atom-wise-ris-improvement-20261106` development workspace before its distinction from the final2 phase archive was clear. The three-seed GRU training completed there. No original node2 checkout, source-phase archive, train/validation dataset, or old checkpoint was edited. The only run outputs added there were `outputs/runs/temporal_v2_improvement_20261106/` and `logs/temporal_v2_train.log`.

Before training, these current files replaced the staged copies in that workspace: `scripts/train_coupled.py` (`dcc3eb3f...` to `84bfef23...`), `src/atomwise_ris/models/coupled_policy.py` (`8feaaa15...` to `666cfe29...`), and `configs/experiments/matched_v1.json` (`ffc1a771...` to `77f880fa...`). The forecast module remained at the final2 hash `f31c0466...`; the coupled search, general search, network, and core files used for the run match their final2 hashes. The temporal benchmark script was new (`710dc480...` at migration). These actual file hashes are recorded in the new temporal run manifest. The exact initial staged bytes for the replaced files were not available in a retained source tar; only the earlier `STAGING_SHA256SUMS` hashes remain, so no guessed restoration was attempted.

After training, only the fresh v2 GRU checkpoints, their train-only scaling and metadata, and the physics gate were copied into the separate current-source workspace `/home/faris/projects/atom-wise-ris-temporal-20261106`. The previous improvement workspace and its outputs were left untouched after that copy. The benchmark is run from the new workspace and records migration/input/source hashes; this temporal development run is not part of the final2 campaign or the matched spatial protocol.

The temporal task completed on 2026-11-06 with a hardened final2 benchmark. Its 1,296 validation actions cover 36 frames in the three coupled validation trajectories, three seeds, three budgets, and persistence/linear/GRU/current-CSI-reference methods. The fresh v2 GRU reduced forecast MSE relative to linear extrapolation, but paired truth-rate deltas were small and mixed across trajectories (macro means −0.0132, +0.0274, and +0.0515 bit/s/Hz at 5/10/50 ms); this is not an established online improvement. The current-CSI reference is not a guaranteed optimizer upper bound. Full metrics and artifact hashes are in `docs/temporal-v2-20261106.md` and `outputs/runs/temporal_v2_improvement_20261106/migration_manifest.json`. The initial temporal validation JSONL remains preserved and is explicitly superseded by the hardened final2 output.
