#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/home/faris/projects/atom-wise-ris-v2-20261106
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

PY="$ROOT/.venv/bin/python"
OUT="$ROOT/outputs/coupled_wire_validation_refinement201"
LOG="$ROOT/logs/coupled_wire_validation_refinement201.log"
mkdir -p "$OUT" "$ROOT/logs"

{
  date -Is
  printf 'root=%s\noutput=%s\n' "$ROOT" "$OUT"
  printf 'selected_indices=32,96,160,174\nsegments=201\nworkers=3\nsplit=validation\n'
  sha256sum \
    scripts/generate_coupled_test.py \
    scripts/generate_coupled_reference.py \
    src/atomwise_ris/physics/nec.py \
    data/processed/coupled_wire_v1/scenario.json
  "$PY" - <<'PY'
import importlib.metadata as md
import platform
import numpy, scipy
print('python', platform.python_version())
print('numpy', numpy.__version__)
print('scipy', scipy.__version__)
print('PyNEC', md.version('PyNEC'))
PY
} | tee -a "$LOG"

"$PY" scripts/generate_coupled_test.py \
  --out "$OUT" \
  --segments 201 \
  --workers 3 \
  --fine-from "$ROOT/data/processed/coupled_wire_v1" \
  --fine-split validation \
  --only-indices 32,96,160,174 2>&1 | tee -a "$LOG"

