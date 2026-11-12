#!/usr/bin/env bash
# Matched protocol v1: train (registered scripts) and validation benchmarks, STOPPING at the freeze.
# Never runs --split test. Resumable: each stage is skipped if its done-marker exists.
# Usage: scripts/run_matched_v1.sh [train|validate|all]     (env: GPU=0 CORE=<cpu> to override the auto-picked core)
set -uo pipefail
me=$(id -un)
cd "$(dirname "$0")/.."
stage="${1:-all}"
PY=.venv/bin/python
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES="${GPU:-0}"
PROTOCOL=configs/experiments/matched_v1.json
SPEC=outputs/runs/matched_specular_v1
COUP=outputs/runs/matched_coupled_v1
mkdir -p logs "$SPEC/logs" "$COUP/logs" logs/matched_v1_markers
M=logs/matched_v1_markers
SEEDS=$($PY -c "import json;print(' '.join(map(str,json.load(open('$PROTOCOL'))['seeds'])))")
log() { echo "[$(date -u +%FT%TZ)] $*" | tee -a logs/matched_v1_driver.log; }
log "protocol sha256 $(sha256sum $PROTOCOL | cut -d' ' -f1) seeds: $SEEDS"

gpu_wait() {  # wait for >=2000 MiB free on the chosen GPU; never touches other users' jobs
  while :; do
    free=$(nvidia-smi --id="${GPU:-0}" --query-gpu=memory.free --format=csv,noheader,nounits | tr -d ' ')
    [[ "$free" -ge 2000 ]] && break
    log "GPU ${GPU:-0} has only ${free} MiB free; waiting"; sleep 60
  done
  log "GPU ${GPU:-0} free memory ${free} MiB"
}

train_specular() {
  for seed in $SEEDS; do
    for variant in mlp attention attention_no_physics; do
      tag="${variant}_seed${seed}"
      [[ -f "$SPEC/models/$tag/metadata.json" ]] && continue
      extra=(); kind=$variant
      [[ $variant == attention_no_physics ]] && { kind=attention; extra=(--no-physics); }
      $PY -u scripts/train.py --run "$SPEC" --kind "$kind" --seed "$seed" --epochs 30 "${extra[@]}" > "$SPEC/logs/train_${tag}.log" 2>&1 \
        || { log "specular training FAILED $tag"; return 1; }
    done
  done
  log "specular training complete"; touch $M/train_specular.done
}
train_coupled() {
  for seed in $SEEDS; do
    for kind in mlp attention attention_no_physics; do
      tag="${kind}_seed${seed}"
      [[ -f "$COUP/models/$tag/metadata.json" ]] && continue
      $PY -u scripts/train_coupled.py --run "$COUP" --kind "$kind" --seed "$seed" --epochs 25 > "$COUP/logs/train_${tag}.log" 2>&1 \
        || { log "coupled training FAILED $tag"; return 1; }
    done
  done
  log "coupled training complete"; touch $M/train_coupled.done
}

if [[ $stage == train || $stage == all ]]; then
  gpu_wait
  rc=0
  [[ -f $M/train_specular.done ]] || { train_specular > logs/matched_v1_train_specular.log 2>&1 & p1=$!; }
  [[ -f $M/train_coupled.done ]]  || { train_coupled  > logs/matched_v1_train_coupled.log 2>&1 & p2=$!; }
  [[ -n "${p1:-}" ]] && { wait $p1 || rc=1; }
  [[ -n "${p2:-}" ]] && { wait $p2 || rc=1; }
  [[ $rc -eq 0 ]] || { log "training stage failed"; exit 1; }
  log "training stage complete"
fi

if [[ $stage == validate || $stage == all ]]; then
  [[ -f $M/train_specular.done && -f $M/train_coupled.done ]] || { log "training not finished; refusing to time"; exit 1; }
  # Core: lowest combined utilisation of the core and its SMT sibling over 10 s; recorded.
  if [[ -z "${CORE:-}" ]]; then
    CORE=$($PY - <<'E'
import time
def snap():
    d={}
    for l in open('/proc/stat'):
        if l.startswith('cpu') and l[3].isdigit():
            f=l.split();v=list(map(int,f[1:]));d[int(f[0][3:])]=(sum(v),v[3]+v[4])
    return d
a=snap();time.sleep(10);b=snap()
def util(c):return 1-(b[c][1]-a[c][1])/max(1,b[c][0]-a[c][0])
def sib(c):return (c+6)%12
best=min((c for c in a if c not in (0,6)),key=lambda c:util(c)+util(sib(c)))
print(best)
E
)
  fi
  log "pinned timing core: $CORE (sibling $(( (CORE+6)%12 )))"
  cat /sys/devices/system/cpu/cpu$CORE/topology/thread_siblings_list > "logs/matched_v1_core.txt"
  { echo "core=$CORE"; mpstat -P ALL 5 1 2>/dev/null | tail -14; uptime; } >> logs/matched_v1_core.txt
  # Load recorder (our own processes excluded from the "others" list by user name).
  ( while :; do echo "$(date -u +%FT%TZ) load=$(cut -d' ' -f1-3 /proc/loadavg) core${CORE}_busy_other=$(ps -eo psr,pcpu,user,comm --no-headers | awk -v c=$CORE -v me=$me '$1==c && $3!=me{s+=$2}END{print s+0}')"
      ps -eo user,pcpu,comm --no-headers --sort=-pcpu | awk -v me=$me '$1!=me && $2>50{print "   other: "$0}' | head -5
      sleep 30; done >> logs/matched_v1_load.log ) &
  LOADPID=$!; trap 'kill $LOADPID 2>/dev/null' EXIT
  T="taskset -c $CORE"

  bench() {  # experiment config
    local exp=$1 cfg=$2 run jsonl cmd
    if [[ $exp == specular ]]; then run=$SPEC; jsonl=benchmark_validation; else run=$COUP; jsonl=benchmark_spatial_validation; fi
    [[ $cfg != medium ]] && jsonl=${jsonl}_$cfg
    [[ -f $M/bench_${exp}_${cfg}.done ]] && return 0
    if [[ -f $run/$jsonl.jsonl ]]; then   # partial output of an interrupted run: preserve, never overwrite
      mv "$run/$jsonl.jsonl" "$run/$jsonl.partial.$(date +%s).jsonl"; [[ -f $run/$jsonl.json ]] && mv "$run/$jsonl.json" "$run/$jsonl.partial.$(date +%s).json"
    fi
    log "benchmark $exp $cfg start (load $(cut -d' ' -f1-3 /proc/loadavg))"
    if [[ $exp == specular ]]; then
      $T $PY -u scripts/benchmark.py --matched --split validation --search-config $cfg > logs/matched_v1_bench_${exp}_${cfg}.log 2>&1
    else
      $T $PY -u scripts/benchmark_coupled.py --matched --mode spatial --split validation --search-config $cfg > logs/matched_v1_bench_${exp}_${cfg}.log 2>&1
    fi || { log "benchmark $exp $cfg FAILED"; return 1; }
    log "benchmark $exp $cfg done"; touch $M/bench_${exp}_${cfg}.done
  }
  for exp in specular coupled; do
    for cfg in medium small large; do bench $exp $cfg || exit 1; done
    run=$([[ $exp == specular ]] && echo $SPEC || echo $COUP)
    if [[ ! -f $run/budget_selection.json ]]; then
      $PY scripts/select_matched_budget.py --experiment $exp > logs/matched_v1_select_${exp}.log 2>&1 || { log "select $exp FAILED"; exit 1; }
      log "budget selection $exp: $(cat logs/matched_v1_select_${exp}.log)"
    fi
  done
  # Analysis of validation only (no test input exists or is read).
  for exp in specular coupled; do
    run=$([[ $exp == specular ]] && echo $SPEC || echo $COUP)
    inp=$([[ $exp == specular ]] && echo benchmark_validation || echo benchmark_spatial_validation)
    [[ -f $run/summary_validation.json ]] || $PY scripts/analyze_matched.py --experiment $exp --tag validation > logs/matched_v1_analyze_${exp}.log 2>&1 || { log "analyze $exp FAILED"; exit 1; }
    for cfg in small large; do   # sensitivity summaries, validation only
      [[ -f $run/summary_validation_$cfg.json ]] || $PY scripts/analyze_matched.py --experiment $exp --input ${inp}_$cfg.jsonl --tag validation_$cfg > logs/matched_v1_analyze_${exp}_$cfg.log 2>&1 || log "analyze $exp $cfg failed (non-fatal)"
    done
  done
  log "VALIDATION COMPLETE; STOP AT FREEZE (no test run)"
  touch $M/validation.done
fi
