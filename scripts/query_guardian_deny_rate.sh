#!/usr/bin/env bash
# Query Guardian denial rate over the last 15 minutes from Prometheus

set -euo pipefail

PROM_URL="${PROMETHEUS_URL:-http://localhost:9090}"
LOOKBACK="${LOOKBACK:-15m}"

QUERY='100 * (rate(guardian_denied_total['$LOOKBACK']) / (rate(guardian_decision_total{effect="allow"}['$LOOKBACK']) + rate(guardian_decision_total{effect="deny"}['$LOOKBACK'])))'

# Use curl to query Prometheus instant query API
RESPONSE=$(curl -sG --data-urlencode "query=${QUERY}" "${PROM_URL}/api/v1/query")

# Parse JSON response with jq
if command -v jq &> /dev/null; then
    STATUS=$(echo "$RESPONSE" | jq -r '.status')

    if [ "$STATUS" = "success" ]; then
        RESULT=$(echo "$RESPONSE" | jq -r '.data.result[0].value[1] // "0"')

        # Format output
        printf "📊 Guardian Denial Rate (last %s): %.2f%%\n" "$LOOKBACK" "$RESULT"

        # Color-coded thresholds
        if (( $(echo "$RESULT > 5" | bc -l) )); then
            printf "🔴 CRITICAL: Denial rate >5%% (threshold breach)\n"
            exit 2
        elif (( $(echo "$RESULT > 1" | bc -l) )); then
            printf "🟡 WARNING: Denial rate >1%% (monitor closely)\n"
            exit 1
        else
            printf "✅ OK: Denial rate within acceptable range (<1%%)\n"
            exit 0
        fi
    else
        ERROR=$(echo "$RESPONSE" | jq -r '.error')
        printf "❌ Prometheus query failed: %s\n" "$ERROR"
        exit 3
    fi
else
    # Fallback if jq not available - just print raw response
    echo "$RESPONSE"
fi
