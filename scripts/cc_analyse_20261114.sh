#!/usr/bin/env bash
# Frozen-rule analysis for one unit or a pool (declaration s.5): unchanged analyze_bench_search.py (search clock,
# Bonferroni family 5 over H1 H2 H5 C6 C7), the rescoring-clock side table, descriptive contrasts (family 1),
# verdicts_crosscity.py and metrics_bench_search.py (M1/M2/M3).
# Usage: cc_analyse_20261114.sh OUT_DIR LABEL INPUT_DIR [INPUT_DIR ...]     Env: W, PY, PYDEPS
set -uo pipefail
OUT=$1; LABEL=$2; shift 2
: "${W:?}"; : "${PY:?}"; PYDEPS=${PYDEPS:-}
export PYTHONPATH=${PYDEPS:+$PYDEPS:}$W/src:$W/scripts PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT"
F="pair_plus_b35-pair,pair_plus_b35-me_ga,pair_plus_b35-nsga2,pair-nsga2,pair-me_ga"
an() { taskset -c 0 "$PY" "$W/scripts/analyze_bench_search.py" --input "$@" >> "$OUT/analysis.log" 2>&1; }
an "$@" --clock search --family-size 5 --contrasts "$F" --output-json "$OUT/analysis_search.json" --output-md "$OUT/analysis_search.md" \
 && an "$@" --clock with_rescore --family-size 5 --contrasts "$F" --output-json "$OUT/analysis_with_rescore.json" --output-md "$OUT/analysis_with_rescore.md" \
 && an "$@" --clock search --family-size 1 --contrasts "pair_plus_b35-greedy,pair-greedy" \
      --output-json "$OUT/analysis_descriptive.json" --output-md "$OUT/analysis_descriptive.md" \
 && taskset -c 0 "$PY" "$W/scripts/verdicts_crosscity.py" "$OUT/analysis_search.json" "$OUT/analysis_descriptive.json" "$OUT/verdicts" >> "$OUT/analysis.log" 2>&1 \
 && taskset -c 0 "$PY" "$W/scripts/metrics_bench_search.py" --input "$@" --output-json "$OUT/metrics.json" --output-md "$OUT/metrics.md" \
      --label "$LABEL" >> "$OUT/analysis.log" 2>&1
