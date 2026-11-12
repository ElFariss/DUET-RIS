#!/usr/bin/env bash
# Durable, restart-safe fine-mesh development generation on the rx6600.
# This creates physical matrices only; it does not create labels or run controllers.
set -euo pipefail

ROOT=/var/tmp/atomwise-ris-gen-20261106
cd "$ROOT"
mkdir -p logs
LOG=logs/coupled_wire_dev_fine161.log
exec > >(tee -a "$LOG") 2>&1

DEV_SCENARIO_SHA256=e78ddb7f5c551133efb271e968f2c49c5742391f43ba8178cbb0334fc43426cf
TEST_V2_SCENARIO_SHA256=de08a1495d295946bcc7b39b952c3523efd006e90527a3802252375f5147bb58
test "$(sha256sum data/processed/coupled_wire_dev_v1/scenario.json | cut -d' ' -f1)" = "$DEV_SCENARIO_SHA256"
# Checksum-only guard: never parse or evaluate the v2 test scenario in this development job.
test "$(sha256sum data/processed/coupled_wire_test_v2/scenario.json | cut -d' ' -f1)" = "$TEST_V2_SCENARIO_SHA256"

export PYTHONPATH="$ROOT/src"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

echo "START $(date -Is)"
{
  echo "dev_source_scenario_sha256=$DEV_SCENARIO_SHA256"
  echo "test_v2_scenario_sha256_checksum_only=$TEST_V2_SCENARIO_SHA256"
  sha256sum scripts/generate_coupled_test.py scripts/generate_coupled_reference.py \
    src/atomwise_ris/physics/nec.py data/processed/coupled_wire_dev_v1/scenario.json
  .venv-em/bin/python -c 'import sys,numpy,PyNEC; print("python="+sys.version.split()[0]); print("numpy="+numpy.__version__); print("pynec="+PyNEC.__file__)'
} | tee logs/coupled_wire_dev_fine161.provenance.txt

exec .venv-em/bin/python -u scripts/generate_coupled_test.py \
  --out data/processed/coupled_wire_dev_fine161 \
  --fine-from data/processed/coupled_wire_dev_v1 \
  --fine-split dev \
  --segments 161 \
  --workers 4
