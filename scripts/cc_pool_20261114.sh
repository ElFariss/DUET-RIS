#!/usr/bin/env bash
# Pooled analysis for one array over every city whose TEST unit completed (PASS_DONE) before the cutoff (declaration s.5, s.9).
# Usage: cc_pool_20261114.sh ARRAY [CUTOFF_UTC]      Env: W, PY, PYDEPS
set -uo pipefail
A=$1; CUT=${2:-2026-11-15T02:00:00Z}
: "${W:?}"; : "${PY:?}"
OUT=$W/runs/pooled/a$A; mkdir -p "$OUT"
cut=$(date -u -d "$CUT" +%s); dirs=(); cities=(); excl=()
for c in munich maastricht utrecht berlin; do
  d=$W/runs/test/$c/a$A
  if [[ -f $d/PASS_DONE ]] && (( $(date -u -d "$(cat $d/PASS_DONE)" +%s) <= cut )); then dirs+=("$d"); cities+=("$c")
  else excl+=("$c"); fi
done
for d in "${dirs[@]}"; do "$PY" "$W/scripts/cc_sumcpu_20261114.py" "$d/cpu_samples.jsonl" > "$d/cpu_samples_summary.json"; done
"$PY" - "$OUT/pool_record.json" "$A" "$CUT" "${cities[*]:-}" "${excl[*]:-}" <<'EOF'
import json, sys, time
o, a, cut, inc, exc = sys.argv[1:6]
json.dump({"array": int(a), "cutoff_utc": cut, "cities": inc.split(), "not_completed": exc.split(),
           "pooled_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, open(o, "w"), indent=1)
EOF
(( ${#dirs[@]} > 0 )) || { echo "no completed city for a$A"; exit 3; }
bash "$W/scripts/cc_analyse_20261114.sh" "$OUT" "pooled ${cities[*]} array $A" "${dirs[@]}" && date -u +%FT%TZ > "$OUT/POOL_DONE"
