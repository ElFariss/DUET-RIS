#!/usr/bin/env bash
# Retrace Maastricht natural case 0073 (infrastructure failure: GPU free-memory guard), then rebuild the
# natural channels assemble, package and gate. Lead, 2026-11-11. 0078 (genuine failure) is NOT retried.
set -Eeuo pipefail
V=/var/tmp/atomwise-bench-production-full-20261109
B=/mnt/home/faris/projects/bench-production-full-20261109
M=outputs/runs/bench_production_full_20261109/cases.json
C=maastricht-v11-0073
PY=/mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python
T=$B/trace-natural; N=$V/channels-natural
fail() { echo "[$(date -u +%FT%TZ)] FAILED: $1"; echo "stage=$1 time=$(date -u +%FT%TZ)" > $V/RETRACE_FAILED; exit 1; }
trap 'fail "line $LINENO"' ERR
rm -f $V/RETRACE_FAILED
echo "[$(date -u +%FT%TZ)] retrace start"

# 1. trace: archive only 0073's failure record and the map/job DONE markers; rerun the map (resume verifies the rest)
if [[ ! -f $T/maastricht/cases/$C.json ]]; then
  mkdir -p $T/cleared_20261111
  mv $T/maastricht/cases/$C.FAILED.json $T/cleared_20261111/
  mv $T/maastricht/DONE $T/cleared_20261111/maastricht.DONE
  cp -p $T/maastricht/trace_manifest.json $T/cleared_20261111/maastricht.trace_manifest.json
  mv $T/JOB_DONE $T/cleared_20261111/JOB_DONE
  /bin/bash $B/src-stage/scripts/run_bench_production_full_trace.sh $B/src-stage $B/trace-work $B/src-stage/$M $T 0 maastricht
fi
[[ -f $T/maastricht/cases/$C.json && ! -e $T/maastricht/cases/$C.FAILED.json && -f $T/maastricht/DONE ]] || fail trace
[[ -f $T/maastricht/cases/maastricht-v11-0078.FAILED.json ]] || fail "0078 record missing"
grep -q '^cases_passed=119$' $T/maastricht/DONE && grep -q '^cases_failed=1$' $T/maastricht/DONE || fail "trace DONE counts"
echo "[$(date -u +%FT%TZ)] trace ok: $(tr '\n' ' ' < $T/maastricht/DONE)"

# 2. channels: set the superseded natural outputs aside, run the normal launcher (only 0073's 3 units are open)
S=$N/superseded_20261111
if [[ ! -d $S ]]; then
  mkdir -p $S
  mv $N/JOB_DONE $N/channel_realizations.h5 $N/metadata.json $N/channel_run.json $N/package $N/production_gate.json $N/output_sha256sums $S/
  mv $N/maastricht/DONE $S/maastricht.DONE
fi
cd $V
/bin/bash $V/scripts/run_bench_production_full_channels.sh $V $V/$M $T $N $V/bench/CoupledRIS-Bench/physics
for n in 64 128 256; do [[ -f $N/maastricht/cases/$C/array_$n.h5 && -f $N/maastricht/cases/$C/array_$n.json ]] || fail "channel unit $n"; done
[[ -f $N/JOB_DONE ]] || fail channels
echo "[$(date -u +%FT%TZ)] channels ok"

# 3. package, gate, checksums (same commands as run_production_chain.sh)
export PYTHONPATH="$V/deps:$V/src:$V/scripts" PYTHONDONTWRITEBYTECODE=1
taskset -c 4,10 $PY $V/scripts/package_bench_production.py --production --manifest $V/$M \
  --channels $N/channel_realizations.h5 --metadata $N/metadata.json --channel-run $N/channel_run.json --output $N/package > $V/retrace_package.log 2>&1 || fail package
taskset -c 4,10 $PY $V/scripts/verify_bench_production_gate.py --production --manifest $V/$M --trace-out $T \
  --channel-run $N/channel_run.json --metadata $N/metadata.json --package $N/package --output $N/production_gate.json > $V/retrace_gate.log 2>&1 || fail gate
( cd $N && sha256sum channel_realizations.h5 metadata.json channel_run.json production_gate.json $(find package -type f | LC_ALL=C sort) > output_sha256sums )
echo "[$(date -u +%FT%TZ)] retrace chain finished"
date -u +%FT%TZ > $V/RETRACE_DONE
