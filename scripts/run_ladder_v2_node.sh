#!/usr/bin/env bash
# V2 development ladder on 3060-1, pinned core 3. Development data only; never touches a test split.
# Writes logs/ladder_v2/{DONE,FAILED}. Refuses to run twice because the benchmark preserves existing output.
set -uo pipefail
cd "$(dirname "$0")/.."
L=logs/ladder_v2; mkdir -p "$L"
[ -e "$L/DONE" ] && { echo "already done"; exit 0; }
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=
PY=${PY:-$HOME/projects/atom-wise-ris/.venv/bin/python}
OUT=outputs/runs/pair_plus_ladder_v2/ladder_dev161.jsonl
( while :; do printf '%s ' "$(date -Is)"; awk '/^cpu3 /{print $2+$3+$4, $5}' /proc/stat; ps -eo psr,pcpu,user,comm --sort=-pcpu | awk '$1==3 && $2>5' | head -3 | tr '\n' ';'; echo; sleep 60; done ) >"$L/core3_load.log" 2>&1 &
MON=$!
trap 'kill $MON 2>/dev/null' EXIT
echo "start $(date -Is) host $(hostname)" >"$L/status"
"$PY" scripts/benchmark_pair_plus.py --data data/processed/coupled_wire_dev_fine161 --output "$OUT" \
  --budgets 1,5,10,50,100 --seeds 7,19,43,3,11,23,31,59,67,83 --threads 1 --cpu 3 >"$L/benchmark.log" 2>&1
rc=$?
echo "end $(date -Is) rc=$rc" >>"$L/status"
if [ $rc -eq 0 ]; then sha256sum outputs/runs/pair_plus_ladder_v2/* >"$L/output.sha256" && touch "$L/DONE"; else echo "rc=$rc" >"$L/FAILED"; fi
exit $rc
