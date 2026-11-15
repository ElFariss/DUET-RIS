#!/usr/bin/env bash
# Declared fallback (crosscity-search-declaration-20261114.md s.6): when the first city is READY (a 64 unit is due), test
# whether labkc-comm2 answers on the lab LAN (tcp/22 at 10.34.0.212) for up to 30 min. If it never answers, publish
# FALLBACK_64_ON_COMM3.json (comm2's queue stops when it sees it) and run ALL 64 units on comm3 CPUs 4/5, yielding to
# pending 128 units. If comm2 answers, record that and exit (comm2 runs the 64 units).
set -uo pipefail
C=/mnt/home/faris/atomwise-crosscity-search-20261114; ROOT=/mnt/home/faris/atomwise-bench-ris-relevant-v3x-20261114
PY=/mnt/home/faris/projects/atom-wise-ris/.venv-em/bin/python; DEPS=/var/tmp/atomwise-bench-ris-relevant-20261112/deps
CUT=$(date -u -d 2026-11-15T02:00:00Z +%s); LOG=$C/runs/fallback_watch.log
say() { echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }
up() { timeout 3 bash -c '</dev/tcp/10.34.0.212/22' 2>/dev/null; }
say "watching for the first READY.json"
until ls $ROOT/*/READY.json >/dev/null 2>&1; do (( $(date -u +%s) > CUT )) && { say "cutoff"; exit 0; }; sleep 60; done
say "first READY: $(ls $ROOT/*/READY.json | tr '\n' ' ')"
for i in $(seq 1 30); do
  if up; then say "comm2 answers on tcp/22 (minute $i): comm2 runs the 64 units"; date -u +%FT%TZ > $C/runs/COMM2_UP_AT_DUE; exit 0; fi
  sleep 60
done
say "comm2 unreachable for 30 min after the first READY: FALLBACK, all 64 units on comm3 (yield to 128)"
mkdir -p $C/stage
printf '{"utc":"%s","reason":"comm2 unreachable on tcp/22 for 30 min after the first READY"}\n' "$(date -u +%FT%TZ)" | tee $C/stage/FALLBACK_64_ON_COMM3.json > $C/runs/FALLBACK_64_ON_COMM3.json
tmux -L cc new-session -d -s ccq64 "W=$C PY=$PY PYDEPS=$DEPS $PY $C/scripts/cc_queue_20261114.py --array 64 --slots 4:10,5:11 --root $ROOT --yield-to 128 --cutoff 2026-11-15T02:00:00Z --min-run-min 40 >> $C/runs/queue64.out 2>&1"
say "comm3 64 queue started"
