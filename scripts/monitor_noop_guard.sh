#!/usr/bin/env bash
# No-Op Guard Monitoring Script (TG-009)
# Purpose: Analyze noop_guard.log and calculate metrics
# Usage: ./scripts/monitor_noop_guard.sh [--report] [--alert]

set -euo pipefail

REPO_ROOT="${LUKHAS_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LOG_FILE="${REPO_ROOT}/docs/audits/noop_guard.log"
REPORT_MODE=false
ALERT_MODE=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --report) REPORT_MODE=true ;;
    --alert) ALERT_MODE=true ;;
    --help)
      echo "Usage: $0 [--report] [--alert]"
      echo "  --report  Generate detailed metrics report"
      echo "  --alert   Check if false positive rate exceeds threshold"
      exit 0
      ;;
  esac
done

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
  echo "⚠️  No-op guard log not found: $LOG_FILE"
  echo "   This is expected if the guard has never been triggered."
  exit 0
fi

# Parse log entries (skip comments and blank lines)
TOTAL_ENTRIES=$(grep -v "^#\|^$" "$LOG_FILE" | wc -l | tr -d ' ')
NO_OP_COUNT=$(grep -v "^#\|^$" "$LOG_FILE" | grep -c "NO-OP" || echo "0")
FALSE_POS_COUNT=$(grep -v "^#\|^$" "$LOG_FILE" | grep -c "FALSE_POSITIVE" || echo "0")
BYPASS_COUNT=$(grep -v "^#\|^$" "$LOG_FILE" | grep -c "BYPASS" || echo "0")

# Calculate metrics
TRUE_POS_COUNT=$NO_OP_COUNT
TRUE_NEG_COUNT=0  # Not tracked in log (successful passes)

# False positive rate calculation
# FP rate = FP / (FP + TN)
# Note: We don't track true negatives, so we use total runs as proxy
if [ "$TOTAL_ENTRIES" -gt 0 ]; then
  # Use awk for floating point math (more portable than bc)
  FP_RATE=$(awk -v fp="$FALSE_POS_COUNT" -v total="$TOTAL_ENTRIES" 'BEGIN { printf "%.4f", (fp * 100 / total) }')
else
  FP_RATE="0.0000"
fi

TARGET_RATE="0.2"
ALERT_THRESHOLD=0
if [ "$TOTAL_ENTRIES" -gt 0 ]; then
  # Use awk to compare floating point values
  ALERT_THRESHOLD=$(awk -v rate="$FP_RATE" -v target="$TARGET_RATE" 'BEGIN { print (rate > target ? 1 : 0) }')
fi

# Display results
if [ "$REPORT_MODE" = true ]; then
  echo "════════════════════════════════════════════════════════"
  echo "  No-Op Guard Monitoring Report (TG-009)"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "📊 Metrics Summary"
  echo "  Total Log Entries:    $TOTAL_ENTRIES"
  echo "  True Positives:       $TRUE_POS_COUNT (correct blocks)"
  echo "  False Positives:      $FALSE_POS_COUNT (incorrect blocks)"
  echo "  Manual Bypasses:      $BYPASS_COUNT"
  echo ""
  echo "📈 False Positive Rate"
  echo "  Current Rate:         ${FP_RATE}%"
  echo "  Target Rate:          <${TARGET_RATE}%"
  
  if [ "$ALERT_THRESHOLD" -eq 1 ]; then
    echo "  Status:               🔴 EXCEEDS TARGET"
  else
    echo "  Status:               ✅ WITHIN TARGET"
  fi
  echo ""
  
  if [ "$TOTAL_ENTRIES" -gt 0 ]; then
    echo "📋 Recent Entries (last 10)"
    echo "────────────────────────────────────────────────────────"
    grep -v "^#\|^$" "$LOG_FILE" | tail -10 || echo "  (none)"
  else
    echo "📋 Recent Entries"
    echo "────────────────────────────────────────────────────────"
    echo "  No entries recorded (guard not triggered)"
  fi
  echo ""
  echo "════════════════════════════════════════════════════════"
else
  # Simple status output
  echo "No-Op Guard Status: $TOTAL_ENTRIES entries, ${FP_RATE}% FP rate"
fi

# Alert mode: exit with error if threshold exceeded
if [ "$ALERT_MODE" = true ] && [ "$ALERT_THRESHOLD" -eq 1 ]; then
  echo ""
  echo "🚨 ALERT: False positive rate (${FP_RATE}%) exceeds target (${TARGET_RATE}%)"
  echo "   Action required: Review recent guard activations and tune logic"
  echo "   See: docs/audits/noop_guard_observation_report.md"
  exit 1
fi

exit 0
