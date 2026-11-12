#!/usr/bin/env bash
# matched_v2 single test on 3060-3: (1) 161-segment physics generation of coupled_wire_test_v2, off the timing CPU;
# (2) the one test run pinned to CPU, sibling load logged. Requires configs/experiments/matched_v2.json frozen.
# Restart-safe: generation resumes from verified frames; the test refuses to overwrite an existing output.
set -uo pipefail
cd "$(dirname "$0")/.."
CPU=${CPU:-5}
SIB=$(lscpu -p=CPU,CORE | grep -v '^#' | awk -F, -v c="$CPU" '{core[$1]=$2} END{for (i in core) if (i!=c && core[i]==core[c]) print i}')
GENCPUS=$(lscpu -p=CPU | grep -v '^#' | awk -v a="$CPU" -v b="$SIB" '$1!=a && $1!=b' | paste -sd,)
L=logs/matched_v2_test; mkdir -p "$L"
[ -e "$L/DONE" ] && { echo "already done"; exit 0; }
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=
PYEM=$HOME/projects/atom-wise-ris/.venv-em/bin/python
PY=$HOME/projects/atom-wise-ris/.venv/bin/python
fail() { echo "$1" >"$L/FAILED"; echo "end $(date -Is) FAILED $1" >>"$L/status"; exit 1; }
grep -q '"status": "frozen"' configs/experiments/matched_v2.json || fail "protocol not frozen"
echo "start $(date -Is) host $(hostname) cpu $CPU sibling $SIB gencpus $GENCPUS" >>"$L/status"
sha256sum configs/experiments/matched_v2.json "$0" >"$L/provenance.sha256"
if [ ! -e "$L/GEN_DONE" ]; then
  echo "gen start $(date -Is)" >>"$L/status"
  taskset -c "$GENCPUS" "$PYEM" -u scripts/generate_coupled_test.py --out data/processed/coupled_wire_test_v2_fine161 \
    --fine-from data/processed/coupled_wire_test_v2 --fine-split test --segments 161 --workers 6 >>"$L/generation.log" 2>&1 \
    || fail "generation rc=$?"
  grep -q '"status": "complete"' data/processed/coupled_wire_test_v2_fine161/generation_status.json || fail "generation incomplete"
  touch "$L/GEN_DONE"; echo "gen end $(date -Is)" >>"$L/status"
fi
D=outputs/runs/matched_v2_test
( while :; do printf '%s ' "$(date -Is)"; awk -v a="cpu$CPU" -v b="cpu$SIB" '$1==a||$1==b{printf "%s %d %d ", $1, $2+$3+$4, $5}' /proc/stat;
    ps -eLo psr,pcpu,user,comm | awk -v a="$CPU" -v b="$SIB" '($1==a||$1==b) && $2>5 {printf "%s:%s:%s:%s,", $1,$2,$3,$4}'; echo; sleep 20; done ) >"$L/cpu_load.log" 2>&1 &
MON=$!
trap 'kill $MON 2>/dev/null' EXIT
echo "test start $(date -Is)" >>"$L/status"
"$PY" scripts/run_matched_v2_test.py --cpu "$CPU" --output "$D/test_v2.jsonl" >"$L/test.log" 2>&1 || fail "test rc=$?"
sha256sum "$D"/* data/processed/coupled_wire_test_v2_fine161/scenario.json data/processed/coupled_wire_test_v2_fine161/generation_status.json >"$L/output.sha256"
echo "end $(date -Is) rc=0" >>"$L/status"
touch "$L/DONE"
