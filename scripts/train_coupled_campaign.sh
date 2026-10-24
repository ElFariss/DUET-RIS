#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for seed in 7 19 43; do
  for kind in mlp attention attention_no_physics gru; do
    file="outputs/runs/coupled_wire_v1/models/${kind}_seed${seed}/metadata.json"
    if [[ ! -f "$file" ]]; then
      .venv/bin/python scripts/train_coupled.py --kind "$kind" --seed "$seed" \
        > "outputs/runs/coupled_wire_v1/logs/${kind}_seed${seed}.log" 2>&1
    fi
  done
done
