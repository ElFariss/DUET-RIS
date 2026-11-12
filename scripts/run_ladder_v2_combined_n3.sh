#!/usr/bin/env bash
# V2 combined b3+b5 development round, rerun on 3060-3 because 3060-1 throughput fell ~26% under other users' load.
# Development data only. See docs/ladder-v2-combined-design-20261107.md. Pinned to one logical CPU; its SMT sibling's
# load is logged too, since a busy sibling slows the pinned CPU even when nothing else runs on it.
set -uo pipefail
cd "$(dirname "$0")/.."
CPU=${CPU:?set CPU}
SIB=$(lscpu -p=CPU,CORE | grep -v '^#' | awk -F, -v c="$CPU" '{core[$1]=$2} END{for (i in core) if (i!=c && core[i]==core[c]) print i}')
L=logs/ladder_v2_combined_n3; mkdir -p "$L"
[ -e "$L/DONE" ] && { echo "already done"; exit 0; }
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=
PY=${PY:-$HOME/projects/atom-wise-ris/.venv/bin/python}
D=outputs/runs/pair_plus_ladder_v2_combined_n3
( while :; do printf '%s ' "$(date -Is)"; awk -v a="cpu$CPU" -v b="cpu$SIB" '$1==a||$1==b{printf "%s %d %d ", $1, $2+$3+$4, $5}' /proc/stat;
    ps -eLo psr,pcpu,user,comm | awk -v a="$CPU" -v b="$SIB" '($1==a||$1==b) && $2>5 {printf "%s:%s:%s:%s,", $1,$2,$3,$4}'; echo; sleep 20; done ) >"$L/cpu_load.log" 2>&1 &
MON=$!
trap 'kill $MON 2>/dev/null' EXIT
echo "start $(date -Is) host $(hostname) cpu $CPU sibling $SIB" >"$L/status"
"$PY" scripts/benchmark_pair_plus.py --data data/processed/coupled_wire_dev_fine161 --output "$D/combined_dev161.jsonl" \
  --methods pair,pair_plus_b0,pair_plus_b3,pair_plus_b5,pair_plus_b35 \
  --budgets 1,5,10,50,100 --seeds 7,19,43,3,11,23,31,59,67,83 --threads 1 --cpu "$CPU" --skip-me-ga-paper >"$L/benchmark.log" 2>&1
rc=$?
echo "end $(date -Is) rc=$rc" >>"$L/status"
if [ $rc -eq 0 ]; then sha256sum "$D"/* >"$L/output.sha256" && touch "$L/DONE"; else echo "rc=$rc" >"$L/FAILED"; fi
exit $rc
