#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE=/mnt/home/faris/projects/atom-wise-ris-gatefix-20261106
PYTHON=/mnt/home/faris/projects/atom-wise-ris/.venv/bin/python
SPECULAR_RUN=outputs/runs/matched_specular_gatefix_20261106
COUPLED_RUN=outputs/runs/matched_coupled_gatefix_20261106

cd "$WORKSPACE"
mkdir -p logs
trap 'rc=$?; trap - EXIT; printf "EXIT status=%s %s\\n" "$rc" "$(date -Is)" >> logs/gatefix-validation-master.log; exit "$rc"' EXIT
test ! -e "$SPECULAR_RUN/benchmark_validation.jsonl"
test ! -e "$SPECULAR_RUN/budget_selection.json"
test ! -e "$COUPLED_RUN/benchmark_spatial_validation.jsonl"
test ! -e "$COUPLED_RUN/budget_selection.json"

export PYTHONPATH="$WORKSPACE/src"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1

printf 'START %s\n' "$(date -Is)" >> logs/gatefix-validation-master.log
printf 'SPECULAR_START %s\n' "$(date -Is)" >> logs/gatefix-validation-master.log
taskset -c 3 "$PYTHON" scripts/benchmark.py \
  --matched --split validation --search-config medium \
  --protocol configs/experiments/matched_v1.json \
  --scenario data/processed/munich_specular_v3/scenario.npz \
  --response data/processed/responses/opensourceris_v1.csv \
  --run "$SPECULAR_RUN" \
  > logs/gatefix-specular-medium-validation.log 2>&1
printf 'SPECULAR_DONE %s\n' "$(date -Is)" >> logs/gatefix-validation-master.log

printf 'COUPLED_START %s\n' "$(date -Is)" >> logs/gatefix-validation-master.log
taskset -c 3 "$PYTHON" scripts/benchmark_coupled.py \
  --matched --split validation --mode spatial \
  --search-config medium --protocol configs/experiments/matched_v1.json \
  --data data/processed/coupled_wire_v1/dataset.npz \
  --physics-gate "$COUPLED_RUN/physics_gate.json" \
  --run "$COUPLED_RUN" \
  > logs/gatefix-coupled-medium-validation.log 2>&1
printf 'COUPLED_DONE %s\n' "$(date -Is)" >> logs/gatefix-validation-master.log

taskset -c 3 "$PYTHON" scripts/select_matched_budget.py --experiment specular \
  --protocol configs/experiments/matched_v1.json --run "$SPECULAR_RUN" \
  --data data/processed/munich_specular_v3/scenario.npz \
  > logs/gatefix-specular-selection.log 2>&1
taskset -c 3 "$PYTHON" scripts/select_matched_budget.py --experiment coupled \
  --protocol configs/experiments/matched_v1.json --run "$COUPLED_RUN" \
  --data data/processed/coupled_wire_v1/dataset.npz \
  > logs/gatefix-coupled-selection.log 2>&1

taskset -c 3 "$PYTHON" scripts/analyze_matched.py --experiment specular \
  --protocol configs/experiments/matched_v1.json --run "$SPECULAR_RUN" \
  --tag validation \
  > logs/gatefix-specular-analysis.log 2>&1
taskset -c 3 "$PYTHON" scripts/analyze_matched.py --experiment coupled \
  --protocol configs/experiments/matched_v1.json --run "$COUPLED_RUN" \
  --tag validation \
  > logs/gatefix-coupled-analysis.log 2>&1
printf 'COMPLETE %s\n' "$(date -Is)" >> logs/gatefix-validation-master.log
