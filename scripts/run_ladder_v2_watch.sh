#!/usr/bin/env bash
# Runs on rx6600 in tmux. Waits for the 161-segment dev generation, copies it to 3060-1 with hash
# verification, then starts the ladder there in its own tmux session. No test data is touched.
set -uo pipefail
GEN=/var/tmp/atomwise-ris-gen-20261106/data/processed/coupled_wire_dev_fine161
NODE=faris@100.68.29.126
W=/mnt/home/faris/projects/atom-wise-ris-ladder-20261107
LOG=$HOME/compute-jobs/ladder-v2-watch; mkdir -p "$LOG"
say(){ echo "$(date -Is) $*" | tee -a "$LOG/status"; }
export PATH="$HOME/.local/bin:$PATH"
say waiting
while :; do
  st=$(python3 -c "import json;d=json.load(open('$GEN/generation_status.json'));print(d.get('status'),d.get('ready_for_development_evaluation'))" 2>/dev/null)
  [ "$st" = "complete True" ] && break
  case "$st" in validation_failed*) say "FAILED generation status: $st"; touch "$LOG/FAILED"; exit 1;; esac
  if ! tmux has-session -t coupled-dev-fine161-20261106 2>/dev/null; then
    sleep 120
    st=$(python3 -c "import json;d=json.load(open('$GEN/generation_status.json'));print(d.get('status'),d.get('ready_for_development_evaluation'))" 2>/dev/null)
    [ "$st" = "complete True" ] && break
    say "FAILED generation session ended without completion: $st"; touch "$LOG/FAILED"; exit 1
  fi
  sleep 300
done
say "generation complete; copying"
for try in 1 2 3 4 5; do
  rsync -a --partial -e 'ssh -o BatchMode=yes -o ConnectTimeout=20' "$GEN/" "$NODE:$W/data/processed/coupled_wire_dev_fine161/" && ok=1 && break
  ok=0; sleep 300
done
[ "${ok:-0}" = 1 ] || { say "FAILED rsync"; touch "$LOG/FAILED"; exit 1; }
a=$(cd "$GEN" && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1)
b=$(ssh -o BatchMode=yes "$NODE" "cd $W/data/processed/coupled_wire_dev_fine161 && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1")
[ "$a" = "$b" ] || { say "FAILED hash mismatch $a $b"; touch "$LOG/FAILED"; exit 1; }
say "copy verified $a; starting ladder"
ssh -o BatchMode=yes "$NODE" "cd $W && tmux new-session -d -s ladder-v2 'bash scripts/run_ladder_v2_node.sh'" || { say "FAILED launch"; touch "$LOG/FAILED"; exit 1; }
sleep 30
ssh -o BatchMode=yes "$NODE" "tmux has-session -t ladder-v2 && cat $W/logs/ladder_v2/status" | tee -a "$LOG/status"
say launched
touch "$LOG/DONE"
