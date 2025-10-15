#!/bin/bash
# RC Soak Period Health Check Script
#
# Purpose: Automated daily health check for v0.9.0-rc soak period
# Owner: Claude (Observability/CI)
# Usage: ./scripts/rc_soak_health_check.sh [--prom-url URL] [--verbose]
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed (health score <0.8, latency >10ms, etc.)
#   2 - Prometheus unreachable or query error

set -euo pipefail

# Configuration
PROM_URL="${PROMETHEUS_URL:-http://localhost:9090}"
REPORT_DIR="docs/audits/rc-soak"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S%z)
VERBOSE=false

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prom-url)
            PROM_URL="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prom-url URL   Prometheus server URL (default: http://localhost:9090)"
            echo "  --verbose        Show detailed query results"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 2
            ;;
    esac
done

# Ensure report directory exists
mkdir -p "$REPORT_DIR"

# Function to query Prometheus and extract value
query_prom() {
    local query="$1"
    local result

    result=$(curl -s -G --data-urlencode "query=$query" "${PROM_URL}/api/v1/query" | \
        jq -r '.data.result[0].value[1] // "null"' 2>/dev/null)

    if [[ "$result" == "null" || -z "$result" ]]; then
        echo "0"
    else
        echo "$result"
    fi
}

# Function to log with color
log() {
    local level="$1"
    local message="$2"

    case "$level" in
        INFO)
            echo -e "${BLUE}ℹ${NC}  $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}✓${NC}  $message"
            ;;
        WARNING)
            echo -e "${YELLOW}⚠${NC}  WARNING: $message"
            ;;
        ERROR)
            echo -e "${RED}✗${NC}  ERROR: $message"
            ;;
    esac
}

# Banner
echo "======================================================================"
echo "  RC Soak Health Check — v0.9.0-rc"
echo "  Date: $DATE"
echo "  Timestamp: $TIMESTAMP"
echo "======================================================================"
echo ""

# Check Prometheus connectivity
log INFO "Checking Prometheus connectivity at $PROM_URL..."
if ! curl -sf "${PROM_URL}/-/healthy" > /dev/null; then
    log ERROR "Prometheus is not reachable at $PROM_URL"
    exit 2
fi
log SUCCESS "Prometheus is healthy"
echo ""

# Initialize status tracking
WARNINGS=0
FAILURES=0

# ============================================================================
# 1. Guardian PDP Latency
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Guardian PDP Performance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

P50=$(query_prom "guardian:pdp_latency:p50")
P95=$(query_prom "guardian:pdp_latency:p95")
P99=$(query_prom "guardian:pdp_latency:p99")

P50_MS=$(echo "$P50 * 1000" | bc -l | xargs printf "%.2f")
P95_MS=$(echo "$P95 * 1000" | bc -l | xargs printf "%.2f")
P99_MS=$(echo "$P99 * 1000" | bc -l | xargs printf "%.2f")

echo "  P50 latency: ${P50_MS}ms"
echo "  P95 latency: ${P95_MS}ms (SLO: <10ms)"
echo "  P99 latency: ${P99_MS}ms"

# Check P95 latency SLO
if (( $(echo "$P95 > 0.010" | bc -l) )); then
    log ERROR "PDP P95 latency ${P95_MS}ms exceeds 10ms SLO"
    ((FAILURES++))
elif (( $(echo "$P95 > 0.008" | bc -l) )); then
    log WARNING "PDP P95 latency ${P95_MS}ms approaching 10ms SLO"
    ((WARNINGS++))
else
    log SUCCESS "PDP P95 latency within SLO"
fi

# Check P99 latency
if (( $(echo "$P99 > 0.050" | bc -l) )); then
    log ERROR "PDP P99 latency ${P99_MS}ms critically high (>50ms)"
    ((FAILURES++))
elif (( $(echo "$P99 > 0.020" | bc -l) )); then
    log WARNING "PDP P99 latency ${P99_MS}ms elevated (>20ms)"
    ((WARNINGS++))
fi

echo ""

# ============================================================================
# 2. Guardian Denial Rate
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Guardian Denial Rate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DENIAL_RATE=$(query_prom "guardian:denial_rate:ratio")
DENIAL_PCT=$(echo "$DENIAL_RATE * 100" | bc -l | xargs printf "%.2f")

echo "  Denial rate: ${DENIAL_PCT}%"

if (( $(echo "$DENIAL_RATE > 0.15" | bc -l) )); then
    log ERROR "Denial rate ${DENIAL_PCT}% exceeds 15% threshold"
    ((FAILURES++))
elif (( $(echo "$DENIAL_RATE > 0.12" | bc -l) )); then
    log WARNING "Denial rate ${DENIAL_PCT}% approaching 15% threshold"
    ((WARNINGS++))
else
    log SUCCESS "Denial rate within expected range"
fi

echo ""

# ============================================================================
# 3. Rate Limiting
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Rate Limiting"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HIT_RATE=$(query_prom "rl:hit_rate:ratio")
HIT_PCT=$(echo "$HIT_RATE * 100" | bc -l | xargs printf "%.2f")

NEAR_EXHAUSTION=$(query_prom "rl:near_exhaustion:ratio")
EXHAUST_PCT=$(echo "$NEAR_EXHAUSTION * 100" | bc -l | xargs printf "%.2f")

AVG_UTIL=$(query_prom "rl:utilization:avg")
AVG_UTIL_PCT=$(echo "$AVG_UTIL * 100" | bc -l | xargs printf "%.2f")

MAX_UTIL=$(query_prom "rl:utilization:max")
MAX_UTIL_PCT=$(echo "$MAX_UTIL * 100" | bc -l | xargs printf "%.2f")

echo "  Hit rate (429s): ${HIT_PCT}%"
echo "  Near-exhaustion: ${EXHAUST_PCT}% of principals"
echo "  Avg utilization: ${AVG_UTIL_PCT}%"
echo "  Max utilization: ${MAX_UTIL_PCT}%"

# Check hit rate
if (( $(echo "$HIT_RATE > 0.10" | bc -l) )); then
    log ERROR "RL hit rate ${HIT_PCT}% exceeds 10% target"
    ((FAILURES++))
elif (( $(echo "$HIT_RATE > 0.05" | bc -l) )); then
    log WARNING "RL hit rate ${HIT_PCT}% elevated (>5%)"
    ((WARNINGS++))
else
    log SUCCESS "RL hit rate within healthy range"
fi

# Check near-exhaustion
if (( $(echo "$NEAR_EXHAUSTION > 0.30" | bc -l) )); then
    log ERROR "Near-exhaustion ${EXHAUST_PCT}% exceeds 30% threshold"
    ((FAILURES++))
elif (( $(echo "$NEAR_EXHAUSTION > 0.25" | bc -l) )); then
    log WARNING "Near-exhaustion ${EXHAUST_PCT}% approaching threshold"
    ((WARNINGS++))
fi

# Check max utilization
if (( $(echo "$MAX_UTIL > 0.90" | bc -l) )); then
    log WARNING "Max utilization ${MAX_UTIL_PCT}% very high (>90%)"
    ((WARNINGS++))
fi

echo ""

# ============================================================================
# 4. Combined Health Score
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Combined Health Score"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HEALTH=$(query_prom "lukhas:guardian_rl:health_score")
HEALTH_DISPLAY=$(echo "$HEALTH * 100" | bc -l | xargs printf "%.1f")

echo "  Health score: ${HEALTH_DISPLAY}% (target >85%)"

if (( $(echo "$HEALTH < 0.70" | bc -l) )); then
    log ERROR "Health score ${HEALTH_DISPLAY}% critically low (<70%)"
    ((FAILURES++))
elif (( $(echo "$HEALTH < 0.80" | bc -l) )); then
    log ERROR "Health score ${HEALTH_DISPLAY}% below 80% threshold"
    ((FAILURES++))
elif (( $(echo "$HEALTH < 0.85" | bc -l) )); then
    log WARNING "Health score ${HEALTH_DISPLAY}% below 85% target"
    ((WARNINGS++))
else
    log SUCCESS "Health score within target range"
fi

echo ""

# ============================================================================
# 5. Traffic Volume
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Traffic Volume"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TRAFFIC=$(query_prom "lukhas:traffic:requests_per_sec")
TRAFFIC_DISPLAY=$(echo "$TRAFFIC" | xargs printf "%.2f")

echo "  Current traffic: ${TRAFFIC_DISPLAY} req/sec"

if (( $(echo "$TRAFFIC < 0.1" | bc -l) )); then
    log WARNING "Very low traffic (${TRAFFIC_DISPLAY} req/sec) - may indicate issue"
    ((WARNINGS++))
else
    log INFO "Traffic volume: ${TRAFFIC_DISPLAY} req/sec"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "======================================================================"
echo "  Summary"
echo "======================================================================"
echo "  Warnings: $WARNINGS"
echo "  Failures: $FAILURES"
echo ""

if [[ $FAILURES -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        log SUCCESS "All checks passed — system healthy ✓"
        STATUS="PASS"
        EXIT_CODE=0
    else
        log WARNING "$WARNINGS warning(s) detected — review recommended"
        STATUS="PASS_WITH_WARNINGS"
        EXIT_CODE=0
    fi
else
    log ERROR "$FAILURES check(s) failed — action required"
    STATUS="FAIL"
    EXIT_CODE=1
fi

echo ""

# ============================================================================
# Generate Report
# ============================================================================
REPORT_FILE="$REPORT_DIR/$DATE.md"

log INFO "Generating report: $REPORT_FILE"

cat > "$REPORT_FILE" <<EOF
# RC Soak Health Check — $DATE

**Timestamp**: $TIMESTAMP
**Status**: $STATUS
**Warnings**: $WARNINGS
**Failures**: $FAILURES

---

## Metrics

### Guardian PDP Performance
- **P50 latency**: ${P50_MS}ms
- **P95 latency**: ${P95_MS}ms (SLO: <10ms)
- **P99 latency**: ${P99_MS}ms

### Guardian Denial Rate
- **Denial rate**: ${DENIAL_PCT}%

### Rate Limiting
- **Hit rate**: ${HIT_PCT}%
- **Near-exhaustion**: ${EXHAUST_PCT}% of principals
- **Avg utilization**: ${AVG_UTIL_PCT}%
- **Max utilization**: ${MAX_UTIL_PCT}%

### Combined Health
- **Health score**: ${HEALTH_DISPLAY}% (target >85%)

### Traffic
- **Current traffic**: ${TRAFFIC_DISPLAY} req/sec

---

## Status

EOF

if [[ $FAILURES -eq 0 && $WARNINGS -eq 0 ]]; then
    echo "✅ **PASS** — All checks passed, system healthy" >> "$REPORT_FILE"
elif [[ $FAILURES -eq 0 ]]; then
    echo "⚠️ **PASS WITH WARNINGS** — $WARNINGS warning(s), review recommended" >> "$REPORT_FILE"
else
    echo "❌ **FAIL** — $FAILURES check(s) failed, action required" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" <<EOF

---

## Next Steps

EOF

if [[ $FAILURES -gt 0 ]]; then
    cat >> "$REPORT_FILE" <<EOF
1. Review Grafana Guardian/RL dashboard
2. Check Prometheus alerts (/alerts)
3. Investigate failing metrics
4. Consider rollback if critical
EOF
else
    cat >> "$REPORT_FILE" <<EOF
1. Continue monitoring per RC_SOAK_MONITORING_PLAN.md
2. Review Grafana dashboard daily
3. Compare against baseline metrics
4. Document any anomalies
EOF
fi

cat >> "$REPORT_FILE" <<EOF

---

_Generated by: scripts/rc_soak_health_check.sh_
_RC Version: v0.9.0-rc_
EOF

log SUCCESS "Report saved: $REPORT_FILE"
echo ""

# ============================================================================
# Verbose Output (if requested)
# ============================================================================
if [[ "$VERBOSE" == "true" ]]; then
    echo "======================================================================"
    echo "  Verbose Metrics (Raw Prometheus Values)"
    echo "======================================================================"
    echo "  P50 latency: $P50"
    echo "  P95 latency: $P95"
    echo "  P99 latency: $P99"
    echo "  Denial rate: $DENIAL_RATE"
    echo "  RL hit rate: $HIT_RATE"
    echo "  Near-exhaustion: $NEAR_EXHAUSTION"
    echo "  Avg utilization: $AVG_UTIL"
    echo "  Max utilization: $MAX_UTIL"
    echo "  Health score: $HEALTH"
    echo "  Traffic: $TRAFFIC"
    echo ""
fi

# ============================================================================
# Exit
# ============================================================================
exit $EXIT_CODE
