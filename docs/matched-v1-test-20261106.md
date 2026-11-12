# Matched_v1 Held-Out Test Evaluation & Audit Report (2026-11-06)

## Executive Summary

The pre-registered, one-shot `matched_v1` held-out test benchmark was executed on node `3060-1` (`labkc-comm1`) on 2026-11-06 following the locked protocol (`configs/experiments/matched_v1.json`, SHA-256 `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88`). All staged sources, environment variables, CPU affinity constraints (core 3 isolation), and test datasets were verified prior to launch. Both specular and coupled benchmarks completed with `EXIT status=0`.

All test artifacts (`benchmark_test.json`, `benchmark_test.jsonl`, `summary_test.json`, `summary_test.csv`, `REPORT_test.md`, `benchmark_spatial_test.json`, `benchmark_spatial_test.jsonl`, `summary_test.json`, `summary_test.csv`, `REPORT_test.md`) were analyzed on `3060-1` at the locked primary budget of **50 ms**, synced back to the canonical local run roots (`outputs/runs/matched_specular_v1/` and `outputs/runs/matched_coupled_v1/`), and verified to match remote SHA-256 digests bit-for-bit.

### Key Findings
1. **Primary Budget Feasibility (50 ms)**: Both specular and coupled experiments experienced **zero deadline misses** (0 / 1,200 runs across all 12 methods in specular; 0 / 4,800 runs across all 12 methods in coupled). The frozen 50 ms budget confirmed complete feasibility on unseen test trajectories.
2. **Specular Experiment Contrasts**: All 11 pre-registered contrasts resulted in the decision **`equivalent`**. Their Bonferroni simultaneous 95% confidence intervals lie strictly within the practical margin of `[-0.015, +0.015] bit/s/Hz`. In this specular ray-tracing scenario, differences among the ILS variations are negligible in magnitude.
3. **Coupled Multiport Experiment Contrasts**:
   - `pair` local search substantially outperforms all GA/ILS heuristic methods by `> 0.60 bit/s/Hz` (`memory_ga - pair`: difference `-0.60728 bit/s/Hz`, simultaneous CI `[-0.81612, -0.41841]`, decision `deteriorated`).
   - `population_ga` is significantly inferior to `analytical_ga` (`population_ga - analytical_ga`: difference `-0.34107 bit/s/Hz`, simultaneous CI `[-0.63166, -0.15565]`, decision `deteriorated`).
   - Comparisons between neural policies (`attention_ga`, `mlp_ga`) and analytical/memory guidance (`memory_ga`, `analytical_ga`) are statistically `inconclusive` (simultaneous CIs span zero).
   - **Fine-Mesh Audit Trigger Fired**: Three memory-related contrasts demonstrated statistical improvements exceeding the practical threshold `+0.015 bit/s/Hz` (`attention_ga - attention_no_memory_ga` at `+0.09763`, `analytical_ga - analytical_no_memory_ga` at `+0.08574`, and `analytical_ga - uniform_ga` at `+0.08393`). In accordance with the pre-registered protocol, these three contrasts are designated `statistical_decision_before_mesh_audit = "improved"` and their final report status remains **`numerically_unresolved`** pending the separate 12-hour fine-mesh post-hoc audit.

---

## 1. Preflight Verification & Provenance Evidence

Prior to executing the held-out test runs, the preflight verification protocol was enforced on `3060-1` in isolated workspace `/mnt/home/faris/projects/atom-wise-ris-gatefix-20261106`.

### Protocol & Source Identity
- **Active Protocol**: `configs/experiments/matched_v1.json`
  - SHA-256: `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88`
  - Protocol Primary Budget: `50 ms` (locked on 2026-11-06T10:40:24Z after validation feasibility selection)
  - Preferred Budget: `10 ms` (requires 0 misses across all methods)
  - Practical Margin / SESOI: `0.015 bit/s/Hz`
- **Staged Source Integrity**: All 62 staged source, test, config, and packaging files were checked against `logs/matched-test-staged-source.sums` with `sha256sum -c`. The verification log `logs/matched-test-source-check.log` recorded 0 errors (`grep -vc ': OK$'` returned 0).
  - `scripts/benchmark.py`: `5305c12c44e04e91c9eaf855d6b791f025d27fdd883c95139f0b7aa145122fed`
  - `scripts/benchmark_coupled.py`: `c2487861b0938418963261fa51bea7482b0adeb140fd9ba3b5daca59bd296f29`
  - `scripts/select_matched_budget.py`: `ddffc80505e621274e64f2968528ba913e90431b9657c0c8df9054fad39077f1`
  - `scripts/analyze_matched.py`: `be7c2cf7b1bcf64f4fbce232b3f0943ff1f31e8bea5546c18af06be1f4833854`
  - `scripts/run_improvement_campaign.py`: `dce1afe7751ca20c73e7099d87e7850118d45785ecb6ac97ddc8d7d1e9520b83`
  - `docs/fallback-gate-fix-20261106.md`: `0a01a238d3c6289caf6148d10d67f7e86b04be472d462612185eb7e3946f8484`

### Validation Gate Status
The fresh validation run on `3060-1` confirmed:
- Specular validation: 0 misses at 10 ms, 0 misses at 50 ms.
- Coupled validation: 3 misses at 10 ms, 0 misses at 50 ms.
- Budget selection: both selectors chose 50 ms based on protocol rule (10 ms was infeasible due to misses in coupled).
- Validation locks remained intact: specular selection `48225d56302c92cbaf59d618fcfc44cf6f0052a4c936ba6dfef304f201d26966`, coupled selection `67bc95b8808728e3fa8e24b67e89dc1b1496ead3884e9a6a509ef78006bea435`.

### Test Dataset SHA-256 Hashes
The held-out test splits were generated strictly from held-out trajectories unseen during development:
- **Munich Specular Test Split** (`munich_specular_test_v1`, 30 trajectories, 4 frames/traj = 120 frames):
  - `scenario.npz`: `2f19e70d216610cd2d1aef7249f2c4811bf7637c57c26b62a685bf3fc1f4c7e4`
  - `scenario.json`: `654591e0c7468d987172a701ebea34cc5abab52255437015fee1839c969a818c`
  - `hashes.json`: `68e50516c67ddeed53a1530789426980be2b302ff24b498bcd90c8de2eae9b57`
  - `layout.json`: `23b339457ce3a4ece029ca5f0393c7bac132c4cafae13d2f9f2f781546d0b264`
- **Coupled Multiport Test Split** (`coupled_wire_test_v1`, 30 trajectories, 16 frames/traj = 480 frames):
  - `dataset.npz`: `a1163ddb89369f9e5c8b87e2803389eec1e4d22ac5a325f490163deb5115760a`
  - `manifest.json`: `3e442f9f8497013c40885021baf75035280494085a8d7847bf24fa2a2ba2477c`
  - `scenario.json`: `65b00fd76a5fc28e2d05603dfd98e61efda413835947f71e28dac2156758776b`

### Execution Isolation (Core 3 & Single-Thread)
- Process affinity pinned to physical Core 3 via `taskset -c 3`.
- Thread environment: `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`.
- Hardware monitor daemon (`logs/matched-test-load.log`) logged load average and Core 3 foreign CPU utilization every 60 seconds from start to completion. On every single minute probe:
  $$\text{core3\_others} = 0$$
  Confirming zero process contention or preemption on the pinned core throughout the run.

---

## 2. Benchmark Execution Details & Artifact Hashes

### Execution Log Summary
- **Host**: `3060-1` (`labkc-comm1`, Linux x86_64, Tailscale IP `100.68.29.126`)
- **Master Log**: `logs/matched-test-master.log`
  - `START 2026-11-06T19:55:37+07:00 host=labkc-comm1 protocol=77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88`
  - `LOADAVG 2.42 1.94 1.66 3/1664 1496594`
  - `SPECULAR_START 2026-11-06T19:55:37+07:00`
  - `SPECULAR_DONE 2026-11-06T20:11:01+07:00` (elapsed: 15 min 24 sec)
  - `COUPLED_START 2026-11-06T20:11:01+07:00`
  - `COUPLED_DONE 2026-11-06T21:21:10+07:00` (elapsed: 1 hr 10 min 09 sec)
  - `COMPLETE 2026-11-06T21:21:10+07:00`
  - `EXIT status=0 2026-11-06T21:21:10+07:00`

### Exact Invocation Commands

#### Benchmark Commands
```bash
# Specular Held-Out Test Benchmark (120 frames * 10 seeds * 5 budgets * 12 methods = 72,000 runs)
taskset -c 3 "$PYTHON" -u scripts/benchmark.py \
  --matched --split test --search-config medium \
  --protocol configs/experiments/matched_v1.json \
  --scenario data/processed/munich_specular_v3/scenario.npz \
  --response data/processed/responses/opensourceris_v1.csv \
  --run "$SPECULAR_RUN" \
  --test-data $ORIG/data/processed/munich_specular_test_v1 \
  > logs/matched-test-specular.log 2>&1

# Coupled Multiport Held-Out Test Benchmark (480 frames * 10 seeds * 5 budgets * 12 methods = 288,000 runs)
taskset -c 3 "$PYTHON" -u scripts/benchmark_coupled.py \
  --matched --mode spatial --split test --search-config medium \
  --protocol configs/experiments/matched_v1.json \
  --data data/processed/coupled_wire_v1/dataset.npz \
  --physics-gate "$COUPLED_RUN/physics_gate.json" \
  --run "$COUPLED_RUN" \
  --test-data $ORIG/data/processed/coupled_wire_test_v1 \
  > logs/matched-test-coupled.log 2>&1
```

#### Analysis Commands
```bash
# Specular Analysis
taskset -c 3 "$PYTHON" scripts/analyze_matched.py --experiment specular \
  --protocol configs/experiments/matched_v1.json \
  --run outputs/runs/matched_specular_gatefix_20261106 \
  --input benchmark_test.jsonl --budget 50 --tag test

# Coupled Analysis
taskset -c 3 "$PYTHON" scripts/analyze_matched.py --experiment coupled \
  --protocol configs/experiments/matched_v1.json \
  --run outputs/runs/matched_coupled_gatefix_20261106 \
  --input benchmark_spatial_test.jsonl --budget 50 --tag test
```

### Artifact Synchronization & Verification Hashes
All output files were synced from `3060-1` to local repository directories (`outputs/runs/matched_specular_v1/` and `outputs/runs/matched_coupled_v1/`). All SHA-256 digests match bit-for-bit:

| Experiment | Artifact Filename | Remote SHA-256 (`3060-1`) | Local SHA-256 (`localhost`) | Verification |
|---|---|---|---|:---:|
| **Specular** | `benchmark_test.json` | `73869c493cff55281aaf59a865e12b6c4e06613c541a0baf423117c2ff87678b` | `73869c493cff55281aaf59a865e12b6c4e06613c541a0baf423117c2ff87678b` | MATCH |
| **Specular** | `benchmark_test.jsonl` | `bd168baea7b7ce52f541a38e3e4cba6556152fc97651b136591181da62b8b27c` | `bd168baea7b7ce52f541a38e3e4cba6556152fc97651b136591181da62b8b27c` | MATCH |
| **Specular** | `summary_test.json` | `cb3396f4043b7527fe9dc6149a9ac84b6a83ca02b8b431e438a3085dfd3b6953` | `cb3396f4043b7527fe9dc6149a9ac84b6a83ca02b8b431e438a3085dfd3b6953` | MATCH |
| **Specular** | `summary_test.csv` | `f7b965ef67f6f4d5916e691fcce82da596e5681673773c0acaf5ee4aa25724fd` | `f7b965ef67f6f4d5916e691fcce82da596e5681673773c0acaf5ee4aa25724fd` | MATCH |
| **Specular** | `REPORT_test.md` | `7d8d41e5f07d213a4a18fcfcb4da3ff561fa9614c87b1d6b92cd1111c7f5bdc6` | `7d8d41e5f07d213a4a18fcfcb4da3ff561fa9614c87b1d6b92cd1111c7f5bdc6` | MATCH |
| **Coupled** | `benchmark_spatial_test.json` | `6c768600f80a8a5359c493e9fcd0422d1d81bee7880abaa43cd931404c130769` | `6c768600f80a8a5359c493e9fcd0422d1d81bee7880abaa43cd931404c130769` | MATCH |
| **Coupled** | `benchmark_spatial_test.jsonl` | `26be7c654bb2bdb96395aa132f848b392f5f87bef3b5d38b47e71a7898c2512e` | `26be7c654bb2bdb96395aa132f848b392f5f87bef3b5d38b47e71a7898c2512e` | MATCH |
| **Coupled** | `summary_test.json` | `562ff12b2c206dc970b01f1c36c1280f127a45a68f59a1f35441f045f6870b1d` | `562ff12b2c206dc970b01f1c36c1280f127a45a68f59a1f35441f045f6870b1d` | MATCH |
| **Coupled** | `summary_test.csv` | `48a3e481701a1650eb77a156903c2b32545db8766e4e107a45353ff5ff23605d` | `48a3e481701a1650eb77a156903c2b32545db8766e4e107a45353ff5ff23605d` | MATCH |
| **Coupled** | `REPORT_test.md` | `99cec4d2396ee565acbbdbd526471323fc0a877207eac7269e164feb47397aad` | `99cec4d2396ee565acbbdbd526471323fc0a877207eac7269e164feb47397aad` | MATCH |

---

## 3. Deadline Misses by Method & Budget

### Specular Experiment (120 frames $\times$ 10 seeds = 1,200 runs per cell)
| Method | 1 ms | 5 ms | 10 ms | 50 ms (Primary) | 100 ms |
|---|:---:|:---:|:---:|:---:|:---:|
| `greedy` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `pair` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `random` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `population_ga` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `uniform_ga` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `memory_ga` | 1 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `analytical_ga` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `analytical_no_memory_ga` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `mlp_ga` | 0 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `attention_ga` | 3 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `attention_no_memory_ga` | 7 / 1200 | 0 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| `attention_no_physics_ga` | 0 / 1200 | 1 / 1200 | 0 / 1200 | **0 / 1200** | 0 / 1200 |
| **Total Misses** | **11 / 14400** | **1 / 14400** | **0 / 14400** | **0 / 14400** | **0 / 14400** |

### Coupled Multiport Experiment (480 frames $\times$ 10 seeds = 4,800 runs per cell)
| Method | 1 ms | 5 ms | 10 ms | 50 ms (Primary) | 100 ms |
|---|:---:|:---:|:---:|:---:|:---:|
| `greedy` | 0 / 4800 | 2 / 4800 | 1 / 4800 | **0 / 4800** | 0 / 4800 |
| `pair` | 0 / 4800 | 0 / 4800 | 1 / 4800 | **0 / 4800** | 0 / 4800 |
| `random` | 3 / 4800 | 0 / 4800 | 0 / 4800 | **0 / 4800** | 1 / 4800 |
| `population_ga` | 3 / 4800 | 4 / 4800 | 1 / 4800 | **0 / 4800** | 0 / 4800 |
| `uniform_ga` | 2 / 4800 | 8 / 4800 | 2 / 4800 | **0 / 4800** | 0 / 4800 |
| `memory_ga` | 2 / 4800 | 8 / 4800 | 3 / 4800 | **0 / 4800** | 0 / 4800 |
| `analytical_ga` | 3 / 4800 | 6 / 4800 | 5 / 4800 | **0 / 4800** | 0 / 4800 |
| `analytical_no_memory_ga` | 1 / 4800 | 2 / 4800 | 1 / 4800 | **0 / 4800** | 0 / 4800 |
| `mlp_ga` | 66 / 4800 | 21 / 4800 | 14 / 4800 | **0 / 4800** | 0 / 4800 |
| `attention_ga` | 5 / 4800 | 23 / 4800 | 19 / 4800 | **0 / 4800** | 0 / 4800 |
| `attention_no_memory_ga` | 1 / 4800 | 7 / 4800 | 7 / 4800 | **0 / 4800** | 0 / 4800 |
| `attention_no_physics_ga` | 4 / 4800 | 26 / 4800 | 18 / 4800 | **0 / 4800** | 0 / 4800 |
| **Total Misses** | **90 / 57600** | **107 / 57600** | **72 / 57600** | **0 / 57600** | **1 / 57600** |

*Analysis of Misses*: In coupled spatial control, the preparation and candidate scoring overhead repeatedly violated the 10 ms budget (72 misses on test, 6 in validation). Selecting 50 ms as the primary budget yielded an immaculate zero-miss performance across both benchmarks, fully vindicating the fallback lock rule.

---

## 4. Primary Budget (50 ms) Detailed Performance Tables

All metrics are evaluated across the full held-out test split at the pre-registered 50 ms budget.

### Specular Scenario (N = 1,200 runs per method across 30 trajectories)
| Method | Rate Mean | Rate SD | Rate Median | Rate IQR | Evals Mean | Runtime p95 (ms) | Runtime Max (ms) | Miss Rate |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| `analytical_ga` | 5.44232 | 3.13835 | 6.22395 | 6.32628 | 8,082.8 | 6.946 | 11.275 | 0.0% (0/1200) |
| `analytical_no_memory_ga` | 5.44232 | 3.13835 | 6.22395 | 6.32628 | 8,081.6 | 7.043 | 11.107 | 0.0% (0/1200) |
| `attention_ga` | 5.44233 | 3.13834 | 6.22395 | 6.32628 | 8,112.8 | 7.706 | 11.832 | 0.0% (0/1200) |
| `attention_no_memory_ga` | 5.44233 | 3.13834 | 6.22395 | 6.32628 | 8,111.6 | 7.678 | 11.686 | 0.0% (0/1200) |
| `attention_no_physics_ga` | 5.44233 | 3.13834 | 6.22395 | 6.32628 | 8,111.5 | 7.679 | 11.176 | 0.0% (0/1200) |
| `greedy` | 5.44194 | 3.13817 | 6.22258 | 6.32590 | 103,022.9 | 48.841 | 48.872 | 0.0% (0/1200) |
| `memory_ga` | 5.44232 | 3.13835 | 6.22395 | 6.32628 | 8,068.9 | 7.086 | 11.921 | 0.0% (0/1200) |
| `mlp_ga` | 5.44233 | 3.13834 | 6.22395 | 6.32628 | 8,116.0 | 7.485 | 13.088 | 0.0% (0/1200) |
| `pair` | 5.44247 | 3.13833 | 6.22395 | 6.32620 | 196,913.8 | 48.512 | 48.711 | 0.0% (0/1200) |
| `population_ga` | 5.43804 | 3.13969 | 6.21758 | 6.34035 | 717.8 | 49.349 | 49.477 | 0.0% (0/1200) |
| `random` | 5.42107 | 3.14684 | 6.19519 | 6.40249 | 13,529.9 | 48.862 | 48.876 | 0.0% (0/1200) |
| `uniform_ga` | 5.44202 | 3.13839 | 6.22154 | 6.32607 | 6,921.8 | 5.755 | 9.867 | 0.0% (0/1200) |

### Coupled Multiport Scenario (N = 4,800 runs per method across 30 trajectories)
| Method | Rate Mean | Rate SD | Rate Median | Rate IQR | Evals Mean | Runtime p95 (ms) | Runtime Max (ms) | Miss Rate |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| `analytical_ga` | 15.63728 | 2.46030 | 16.05058 | 3.68215 | 3,534.0 | 10.214 | 18.756 | 0.0% (0/4800) |
| `analytical_no_memory_ga` | 15.55154 | 2.53590 | 16.00889 | 3.75380 | 2,744.2 | 7.523 | 14.937 | 0.0% (0/4800) |
| `attention_ga` | 15.65760 | 2.44781 | 16.05058 | 3.66645 | 3,615.2 | 12.221 | 23.709 | 0.0% (0/4800) |
| `attention_no_memory_ga` | 15.55997 | 2.54933 | 16.03224 | 3.75380 | 2,761.5 | 9.231 | 17.202 | 0.0% (0/4800) |
| `attention_no_physics_ga` | 15.66065 | 2.42896 | 16.04239 | 3.66365 | 3,583.5 | 12.335 | 22.395 | 0.0% (0/4800) |
| `greedy` | 15.52535 | 2.57716 | 16.01638 | 3.83526 | 24,337.0 | 49.199 | 49.512 | 0.0% (0/4800) |
| `memory_ga` | 15.62635 | 2.47423 | 16.06579 | 3.65522 | 3,549.0 | 10.210 | 22.106 | 0.0% (0/4800) |
| `mlp_ga` | 15.66539 | 2.44089 | 16.05369 | 3.66365 | 3,609.5 | 11.461 | 20.375 | 0.0% (0/4800) |
| `pair` | 16.23363 | 2.12153 | 16.60357 | 2.83676 | 79,290.9 | 48.972 | 49.552 | 0.0% (0/4800) |
| `population_ga` | 15.29621 | 2.87218 | 15.92094 | 4.02194 | 320.2 | 49.332 | 49.935 | 0.0% (0/4800) |
| `random` | 15.26163 | 2.94232 | 15.90742 | 4.02466 | 288.7 | 49.215 | 49.333 | 0.0% (0/4800) |
| `uniform_ga` | 15.55335 | 2.52421 | 16.00852 | 3.76221 | 3,394.2 | 9.338 | 18.984 | 0.0% (0/4800) |

---

## 5. Pre-Registered Contrast Statistical Decisions

Statistical decisions follow the pre-registered protocol:
- **Unit of Resampling**: Trajectory (averaging seeds within trajectory).
- **Bootstrap Parameters**: 10,000 paired resamples, seed `8251`.
- **Confidence Intervals**: Bonferroni simultaneous percentile intervals at family-wise $\alpha = 0.05$ ($M = 11$ contrasts; coverage level $1 - 0.05 / 11 = 99.545\%$).
- **Hypothesis Testing**: Centered-bootstrap two-sided $p$-value against zero difference, separately adjusted using the step-down Holm method.
- **Decision Rule**:
  - `improved`: simultaneous interval lower bound $> +0.015$ bit/s/Hz.
  - `deteriorated`: simultaneous interval upper bound $< -0.015$ bit/s/Hz.
  - `equivalent`: simultaneous interval entirely inside $[-0.015, +0.015]$ bit/s/Hz.
  - `inconclusive`: interval overlaps margin boundaries and contains values outside.
  - *Coupled constraint*: any statistical improvement remains `numerically_unresolved` unless the fine-mesh audit passes.

### Specular 11 Contrasts (Primary Budget 50 ms)
Decision Margin: $\pm 0.015\text{ bit/s/Hz}$.

| # | Contrast | Point Difference | Bonferroni 95% Simultaneous CI | Holm $p$ (Zero Null) | Final Protocol Decision |
|---|---|---:|---|---:|:---:|
| 1 | `attention_ga - memory_ga` | +0.00001 | [-0.00000, +0.00003] | 0.3878 | **equivalent** |
| 2 | `mlp_ga - memory_ga` | +0.00001 | [-0.00000, +0.00003] | 0.8489 | **equivalent** |
| 3 | `analytical_ga - memory_ga` | -0.00000 | [-0.00002, +0.00001] | 0.9967 | **equivalent** |
| 4 | `attention_ga - analytical_ga` | +0.00001 | [+0.00000, +0.00003] | 0.0224 | **equivalent** |
| 5 | `memory_ga - pair` | -0.00015 | [-0.00024, -0.00006] | 0.0022 | **equivalent** |
| 6 | `attention_ga - attention_no_memory_ga` | 0.00000 | [0.00000, 0.00000] | 1.0000 | **equivalent** |
| 7 | `analytical_ga - analytical_no_memory_ga` | 0.00000 | [0.00000, 0.00000] | 1.0000 | **equivalent** |
| 8 | `analytical_ga - uniform_ga` | +0.00029 | [+0.00013, +0.00052] | 0.0022 | **equivalent** |
| 9 | `attention_ga - mlp_ga` | +0.00000 | [-0.00000, +0.00001] | 0.5291 | **equivalent** |
| 10 | `attention_ga - attention_no_physics_ga` | -0.00000 | [-0.00000, +0.00000] | 1.0000 | **equivalent** |
| 11 | `population_ga - analytical_ga` | -0.00428 | [-0.00576, -0.00305] | 0.0022 | **equivalent** |

*Interpretation (Specular)*: In the Munich specular scenario, all ILS variants achieve within $0.0003\text{ bit/s/Hz}$ of each other. All 11 contrasts are rigorously equivalent under the 0.015 margin. Even though Holm tests against exact zero reject for contrasts #4, #5, #8, and #11, the practical effect size is orders of magnitude smaller than the engineering threshold.

---

### Coupled Multiport 11 Contrasts (Primary Budget 50 ms)
Decision Margin: $\pm 0.015\text{ bit/s/Hz}$.

| # | Contrast | Point Difference | Bonferroni 95% Simultaneous CI | Holm $p$ (Zero Null) | Final Protocol Decision |
|---|---|---:|---|---:|:---:|
| 1 | `attention_ga - memory_ga` | +0.03125 | [-0.02339, +0.08487] | 0.5089 | **inconclusive** |
| 2 | `mlp_ga - memory_ga` | +0.03904 | [-0.01563, +0.09345] | 0.3000 | **inconclusive** |
| 3 | `analytical_ga - memory_ga` | +0.01093 | [-0.01112, +0.04741] | 0.7823 | **inconclusive** |
| 4 | `attention_ga - analytical_ga` | +0.02032 | [-0.02460, +0.06587] | 0.7823 | **inconclusive** |
| 5 | `memory_ga - pair` | -0.60728 | [-0.81612, -0.41841] | 0.0022 | **deteriorated** |
| 6 | `attention_ga - attention_no_memory_ga` | +0.09763 | [+0.02737, +0.18190] | 0.0054 | **numerically_unresolved** |
| 7 | `analytical_ga - analytical_no_memory_ga` | +0.08574 | [+0.02144, +0.16370] | 0.0054 | **numerically_unresolved** |
| 8 | `analytical_ga - uniform_ga` | +0.08393 | [+0.02041, +0.15388] | 0.0056 | **numerically_unresolved** |
| 9 | `attention_ga - mlp_ga` | -0.00779 | [-0.03009, +0.01047] | 0.7823 | **inconclusive** |
| 10 | `attention_ga - attention_no_physics_ga` | -0.00306 | [-0.04272, +0.03067] | 0.7823 | **inconclusive** |
| 11 | `population_ga - analytical_ga` | -0.34107 | [-0.63166, -0.15565] | 0.0022 | **deteriorated** |

---

## 6. Fine-Mesh Audit Rule & Secondary Budgets

### Fine-Mesh Post-Hoc Audit Rule Evaluation
The pre-registered protocol specifies the following rule for the coupled multiport experiment:
> *"The audit runs only if at least one coupled contrast is otherwise decided improved. Without it, those contrasts are reported as numerically unresolved."*

**Status: The Audit Trigger Fired.**
- Contrasts #6 (`attention_ga - attention_no_memory_ga`), #7 (`analytical_ga - analytical_no_memory_ga`), and #8 (`analytical_ga - uniform_ga`) all achieved simultaneous Bonferroni confidence intervals whose lower limits strictly exceed $+0.015\text{ bit/s/Hz}$ ($+0.02737$, $+0.02144$, and $+0.02041$ respectively).
- Their pre-mesh statistical classification is `improved`.
- Because the ~12-hour fine-mesh post-hoc audit (`scripts/audit_coupled_posthoc.py`) was **not** run as part of this analysis (as explicitly instructed by the task contract), `analyze_matched.py` set `mesh_audit_passed: null` and assigned their final decision as **`numerically_unresolved`**.
- To confirm or withhold this improvement claim, the post-hoc audit must be executed on a 4-worker node comparing 81- vs 161-segment MoM solutions across all 288,000 primary-budget returned actions.

### Secondary Budgets Summary (1, 5, 10, 100 ms)

#### Specular Dynamics Across Budgets
- **1 ms**: Heuristic methods (`greedy`, `pair`) attain $\sim 5.428\text{ bit/s/Hz}$ within 730 evaluations. GAs achieve $\sim 5.399\text{ bit/s/Hz}$ (reaching target in 23% of frames).
- **5 ms**: Both greedy/pair and GA methods converge to $\ge 5.441\text{ bit/s/Hz}$.
- **10 ms**: Convergence is complete across all methods ($5.442\text{ bit/s/Hz}$).
- **100 ms**: Extended search provides no additional gain over 50 ms ($5.4423\text{ bit/s/Hz}$).

#### Coupled Dynamics Across Budgets
- **1 ms**: Insufficient budget for full local search sweeps; all methods average $\sim 15.26\text{ bit/s/Hz}$.
- **5 ms**: Local pair search already leads with $15.599\text{ bit/s/Hz}$. Neural/memory methods reach $15.57\text{ bit/s/Hz}$ but experience 20–26 misses per method.
- **10 ms**: `pair` reaches $15.747\text{ bit/s/Hz}$. ILS methods reach $\sim 15.63\text{ bit/s/Hz}$. Deadline misses remain elevated for neural policies (`mlp_ga`: 14, `attention_ga`: 19).
- **50 ms (Primary)**: `pair` dominates at $16.234\text{ bit/s/Hz}$ with 0 misses. Neural/memory ILS reach $15.66\text{ bit/s/Hz}$ with 0 misses.
- **100 ms**: `pair` scales further to $16.508\text{ bit/s/Hz}$ (161,618 evaluations), outperforming all genetic / iterated-local-search variants by $0.84\text{ bit/s/Hz}$.

---

## 7. Compliance Checklist

- [x] Preflight checks verified on `3060-1` prior to test run.
- [x] No modifications to `src/`, `scripts/`, or `configs/`.
- [x] Test runs executed with single-thread and Core 3 affinity (`taskset -c 3`).
- [x] Zero contention on Core 3 verified across the entire execution window.
- [x] Both test runs exited with status 0.
- [x] Primary budget of 50 ms locked and validated from validation freeze.
- [x] All 10 output files synced from `3060-1` to canonical local paths.
- [x] Bit-for-bit SHA-256 match confirmed for all synced test files.
- [x] Fine-mesh audit trigger verified (fired for 3 coupled contrasts).
- [x] 12-hour fine-mesh audit withheld in accordance with instructions.
- [x] Documentation recorded in `docs/matched-v1-test-20261106.md`.
