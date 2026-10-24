#!/usr/bin/env bash
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES="${1:-0}"
kind="${2:-attention}"
run="${3:-outputs/runs/specular_v5}"
mkdir -p "$run/logs"
for seed in 7 19 43; do
  .venv/bin/python -u scripts/train.py --run "$run" --kind "$kind" --seed "$seed" > "$run/logs/${kind}_${seed}.log" 2>&1
done
if [[ "$kind" == attention ]]; then
  for seed in 7 19 43; do
    .venv/bin/python -u scripts/train.py --run "$run" --kind attention --seed "$seed" --no-physics > "$run/logs/attention_no_physics_${seed}.log" 2>&1
    .venv/bin/python -u scripts/train.py --run "$run" --kind attention --seed "$seed" --no-conditioning > "$run/logs/attention_no_conditioning_${seed}.log" 2>&1
  done
fi
