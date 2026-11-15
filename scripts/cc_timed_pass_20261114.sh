#!/usr/bin/env bash
# One cross-city unit = one city x one array (declaration paper-a-ris-physics/docs/crosscity-search-declaration-20261114.md).
# Usage: cc_timed_pass_20261114.sh CITY SPLIT ARRAY CPU CHANNEL_FILE SUMS_FILE READY_FILE OUT SEEDS [extra runner args]
# Env: W (workspace root with src/ scripts/ docs/ configs/), PY, PYDEPS (may be empty), METHODS, BUDGETS, WATCH.
set -uo pipefail
CITY=$1; SPLIT=$2; A=$3; CPU=$4; CH=$5; SUMS=$6; READY=$7; OUT=$8; SEEDS=$9; shift 9
: "${W:?}"; : "${PY:?}"; PYDEPS=${PYDEPS:-}
METHODS=${METHODS:-greedy,pair,me_ga,nsga2,pair_plus_b35}
BUDGETS=${BUDGETS:-10,50}
WATCH=${WATCH:-4,5,10,11}
export PYTHONPATH=${PYDEPS:+$PYDEPS:}$W/src:$W/scripts PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT"; cd "$W"
exec 9>"$OUT/pass.lock"; flock -n 9 || { echo "pass already running" >&2; exit 4; }
rm -f "$OUT/PASS_FAILED" "$OUT/STOP_SAMPLER"
say() { echo "[$(date -u +%FT%TZ)] $*" >> "$OUT/pass.log"; }
say "start city=$CITY split=$SPLIT array=$A cpu=$CPU seeds=$SEEDS budgets=$BUDGETS methods=$METHODS extra=$*"
taskset -c 0 "$PY" "$W/scripts/sample_cpu_load.py" --cpus "$WATCH" --interval 20 --pin 0 \
  --output "$OUT/cpu_samples.jsonl" --stop-file "$OUT/STOP_SAMPLER" >> "$OUT/sampler.log" 2>&1 &
sp=$!
rc=0
if [[ ! -e "$OUT/DONE" ]]; then
  "$PY" "$W/scripts/run_bench_search_crosscity.py" --city "$CITY" --channel-file "$CH" --sums-file "$SUMS" \
    --ready-file "$READY" --split "$SPLIT" --arrays "$A" --methods "$METHODS" --budgets-ms "$BUDGETS" --seeds "$SEEDS" \
    --cpu "$CPU" --output "$OUT" --nsga2-ready "$W/runs/NSGA2_READY.json" "$@" >> "$OUT/runner.log" 2>&1
  rc=$?
fi
touch "$OUT/STOP_SAMPLER"; wait "$sp" 2>/dev/null
if (( rc != 0 )); then say "runner rc=$rc"; echo "runner rc=$rc" > "$OUT/PASS_FAILED"; exit 1; fi
say "runner done"
bash "$W/scripts/cc_analyse_20261114.sh" "$OUT" "$CITY $SPLIT array $A" "$OUT" || { say "analysis failed"; echo analysis > "$OUT/PASS_FAILED"; exit 2; }
date -u +%FT%TZ > "$OUT/PASS_DONE"; say "PASS_DONE"
