#!/usr/bin/env bash
# Existing SSH agent/key or interactive authentication; never save credentials here.
set -euo pipefail
cd "$(dirname "$0")/.."
port="${RIS_SSH_PORT:-2002}"
target="${RIS_SSH_TARGET:-faris@gpu-labkc.ub.ac.id}"
jump="${RIS_JUMP_HOST:-faris@labkc-comm1}"
remote_dir="${RIS_REMOTE_DIR:-projects/atom-wise-ris}"
transport="ssh -J $jump -p $port"
case "${1:-}" in
  push)
    rsync -az --exclude .git --exclude .venv --exclude __pycache__ --exclude outputs \
      --exclude archives --exclude data/raw/acquisition --exclude data/raw/deepmimo_scenarios \
      -e "$transport" ./ "$target:$remote_dir/"
    ;;
  pull)
    mkdir -p outputs/runs
    rsync -az -e "$transport" "$target:$remote_dir/outputs/runs/" outputs/runs/
    ;;
  *) echo 'Usage: scripts/remote.sh push|pull (existing SSH authentication)' >&2; exit 2 ;;
esac
