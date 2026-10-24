#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for mode in spatial temporal; do
 .venv/bin/python scripts/benchmark_coupled.py --split validation --mode "$mode"
done
.venv/bin/python scripts/select_coupled_budget.py
for mode in spatial temporal; do
 .venv/bin/python scripts/benchmark_coupled.py --split pilot --mode "$mode"
done
