# Flash task watch: check the CoupledRIS-Bench production run every 30 minutes (read-only)

Read `docs/flash-common-rules-20261109.md` first. This task is **read-only**. The user asked for it: check the production run every 30 minutes yourself.
Repeat: run the check, judge it, append the report line, then `sleep 1800`, then check again.
Stop when `PRODUCTION_DONE` exists (after reporting DONE), or after 72 hours, whichever comes first.
On ALERT, keep checking every 30 minutes; do not stop and do not try to fix anything.

## Do not
- edit, move or delete any file on 3060-3, or any code in this checkout;
- kill, restart or launch anything (no tmux commands other than `tmux ls`);
- clear any FAILED or RUNNING marker, or "fix" anything. If something is wrong, report it; the lead fixes it;
- use CPUs 5 or 11, 3060-1, or 3060-2; copy data back; print credentials.

## The check (one ssh command, well under a minute)
```bash
ssh -o BatchMode=yes -p 2003 gpu-labkc.ub.ac.id 'V=/var/tmp/atomwise-bench-production-full-20261109; cd $V; date -u +%FT%TZ; tmux ls; cat LIVENESS.json; ls LIVENESS_ALERT PRODUCTION_DONE PRODUCTION_FAILED FIRST_CASES_OK FIRST_CASES_FAILED 2>/dev/null; tail -n 3 production_chain.log; for s in natural challenge; do echo $s $(find channels-$s -path "*/cleared_20261110" -prune -o -name "array_*.h5" -print | wc -l) shards, $(find channels-$s -path "*/cleared_20261110" -prune -o -name "*.FAILED.json" -print | wc -l) unit-failed, $(find channels-$s -name "*.transient.json" | wc -l) transient; done; ps -u faris -o rss=,cmd= | grep build_bench_production_channels.py | grep -v grep | awk "{s+=\$1} END {print \"worker RSS GiB\", s/1048576}"; free -g | sed -n 2p'
```
Totals for reference: natural needs 1,080 shards (360 cases x 3 arrays); challenge needs 207 (69 x 3).

## Judge it
**ALERT** if any of these holds; otherwise **OK**:
- `LIVENESS.json` has `"status": "alert"`, or `LIVENESS_ALERT`, `PRODUCTION_FAILED` or `FIRST_CASES_FAILED` exists;
- `checked_utc` in `LIVENESS.json` is more than 25 minutes older than the remote time (the watcher itself has stopped);
- tmux session `cris-channels` or `cris-watch` is missing while `PRODUCTION_DONE` does not exist;
- any unit-failed count is above 0;
- available memory (last column of the `free` line) is below 8 GiB;
- the ssh command itself fails (report the error text).

`PRODUCTION_DONE` present means **DONE** (report it as OK/DONE).

## Report
1. Append exactly one line to `outputs/runs/bench_production_full_20261109/agy_checks.md` (create it if missing):
   `- <remote UTC time> | OK or ALERT or DONE | natural <n>/1080, challenge <n>/207 shards | failed <n>, transient <n> | worker RSS <x> GiB, mem available <y> GiB | <reason or "-">`
2. Only on ALERT: also write `outputs/runs/bench_production_full_20261109/AGY_ALERT.md` with the time, every reason,
   and the raw output of the check command. Do not overwrite an existing `AGY_ALERT.md`; append to it.
3. When you stop, write `docs/flash-watch-handoff-20261109.md`: the number of checks, the last status, and any alerts.
