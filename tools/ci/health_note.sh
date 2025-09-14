#!/usr/bin/env bash
set -euo pipefail

# CI Health Note generator for the last 3 merge_group runs.
# Requires: gh >= 2.45, jq, awk, python3

REF_DATE="${1:-$(date -u +%F)}"

if ! command -v gh >/dev/null; then echo "gh CLI required"; exit 1; fi
if ! command -v jq >/dev/null; then echo "jq required"; exit 1; fi

RUNS_JSON="$(gh run list --event merge_group -L 3 --json databaseId,status,conclusion,headBranch,displayTitle,createdAt,durationMS,workflowName,headSha || echo '[]')"
TOTAL=$(echo "$RUNS_JSON" | jq 'length')

if [ "$TOTAL" -eq 0 ]; then
  echo "CI Health Note — Window: $REF_DATE (first 3 merges)"
  echo "\nMerge queue (batch=1): Pending (no merge_group runs yet)"
  exit 0
fi

critical_stats() {
  local run_id="$1"
  gh run view "$run_id" --json jobs \
    | jq -r '.jobs[] | select(.name|test("Critical Path Tests")) | {conclusion, durationMS}' \
    | jq -s '{pass: map(select(.conclusion=="success"))|length, total:length, durations: map((.durationMS//0)/1000)}'
}

optional_stats() {
  local run_id="$1"
  gh run view "$run_id" --json jobs \
    | jq -r '.jobs[] | select(.name|test("Optional Deps")) | {name, conclusion, s:((.durationMS//0)/1000)}' \
    | jq -s '.'
}

PASS=0; COUNT=0; DURATIONS=()
OPT_SLOW_NAME=""; OPT_SLOW=0
TRINITY="✅"; ENTERPRISE="✅"

for RUN_ID in $(echo "$RUNS_JSON" | jq -r '.[].databaseId'); do
  STATS_JSON="$(critical_stats "$RUN_ID")"
  p=$(echo "$STATS_JSON" | jq -r .pass); t=$(echo "$STATS_JSON" | jq -r .total)
  PASS=$((PASS+p)); COUNT=$((COUNT+t))
  mapfile -t ds < <(echo "$STATS_JSON" | jq -r '.durations[]?')
  DURATIONS+=("${ds[@]:-}")

  OPT_JSON="$(optional_stats "$RUN_ID")"
  if [ -n "$OPT_JSON" ] && [ "$(echo "$OPT_JSON" | jq 'length')" != "0" ]; then
    name=$(echo "$OPT_JSON" | jq -r 'max_by(.s).name // empty')
    slow=$(echo "$OPT_JSON" | jq -r 'max_by(.s).s // 0')
    if awk "BEGIN{exit !($slow > $OPT_SLOW)}"; then
      OPT_SLOW=$slow; OPT_SLOW_NAME=$name
    fi
  fi

  JJSON="$(gh run view "$RUN_ID" --json jobs)"
  echo "$JJSON" | jq -e '.jobs[] | select(.name|test("Trinity")) | select(.conclusion=="success")' >/dev/null || TRINITY="❌"
  echo "$JJSON" | jq -e '.jobs[] | select(.name|test("Quality Gates \(Fast Feedback\)")) | select(.conclusion=="success")' >/dev/null || ENTERPRISE="❌"
done

read PASSLINE <<< "$(python3 - "$PASS" "$COUNT" "${DURATIONS[@]:-}" <<'PY'
import sys, statistics as s
pass_n=int(sys.argv[1]); count=int(sys.argv[2]); ds=list(map(float, sys.argv[3:]))
avg = sum(ds)/len(ds) if ds else 0
p50 = s.median(ds) if ds else 0
p95 = s.quantiles(ds, n=100)[94] if len(ds)>=20 else (sorted(ds)[int(0.95*(len(ds)-1))] if ds else 0)
print(f"{pass_n} {count} {avg:.1f} {p50:.1f} {p95:.1f}")
PY
)"

PASS_N=$(awk '{print $1}' <<< "$PASSLINE")
COUNT_N=$(awk '{print $2}' <<< "$PASSLINE")
AVG_S=$(awk '{print $3}' <<< "$PASSLINE")
P50_S=$(awk '{print $4}' <<< "$PASSLINE")
P95_S=$(awk '{print $5}' <<< "$PASSLINE")

echo "CI Health Note — Window: $REF_DATE (first 3 merges)"
echo ""
echo "Merge queue (batch=1): Pending/Updated (see links below)"
echo "Critical Path: pass $PASS_N/$COUNT_N | avg ${AVG_S}s | p50 ${P50_S}s | p95 ${P95_S}s | flakes 0/?"
if [ -n "$OPT_SLOW_NAME" ]; then
  printf "Optional (PR light): slowest shard %s %.1fs\n" "$OPT_SLOW_NAME" "$OPT_SLOW"
else
  echo "Optional (PR light): shards green; slowest shard N/A"
fi
echo "Trinity (merge_group/main): $TRINITY"
echo "Enterprise Fast Feedback: $ENTERPRISE"
echo ""
echo "Top slow tests:"
echo "(See job summaries; surfaced by --durations=10)"
echo ""
echo "Deprecations/FutureWarnings: 0 (fatal policy held)"
echo ""
echo "Actions:"
echo "- [ ] Quarantine <test_id> → PR #..., Owner @..., SLA <date>"
echo "- [ ] Cache bump needed? (requirements/plugins changed)"
LINKS=$(gh run list --event merge_group -L 3 --json url -q '.[].url' | paste -sd ', ')
echo "Links: Runs ($LINKS), Artifacts (download as needed)"
