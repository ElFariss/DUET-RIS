#!/usr/bin/env bash
# Usage: run_flash_task.sh <task-id>   (reads docs/flash-<task-id>-brief-20261109.md)
set -u
t=$1; cd "$(dirname "$0")/../.."
log=logs/agy/flash-$t.log
echo "=== $t start $(date) ===" >> "$log"
"${AGY:-agy}" --model gemini-3.8-flash-high --dangerously-skip-permissions --print-timeout 0 \
  -p "You are a Flash worker. Read docs/flash-common-rules-20261109.md, then do exactly the task in docs/flash-$t-brief-20261109.md, and write its hand-back file. Do not do any other task." >> "$log" 2>&1
echo "exit=$? $(date)" >> "$log"
tmux wait-for -S flash-$t-done
