#!/bin/bash
# Security automation cron script for LUKHAS
# Add to crontab: 0 2 * * * /path/to/lukhas/scripts/security-cron.sh

set -e

# Configuration
LUKHAS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$LUKHAS_DIR/logs/security"
DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/security-scan-$DATE.log"
REPORT_FILE="$LOG_DIR/security-report-$DATE.md"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"  # Set in environment
EMAIL="${SECURITY_EMAIL:-}"  # Set in environment

# Create log directory
mkdir -p "$LOG_DIR"

# Function to send notifications
send_notification() {
    local severity="$1"
    local message="$2"
    
    # Slack notification
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🔒 LUKHAS Security Alert [$severity]: $message\"}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi
    
    # Email notification
    if [ -n "$EMAIL" ]; then
        echo "$message" | mail -s "LUKHAS Security Alert [$severity]" "$EMAIL" 2>/dev/null || true
    fi
    
    # Log to file
    echo "[$(date)] [$severity] $message" >> "$LOG_FILE"
}

# Change to LUKHAS directory
cd "$LUKHAS_DIR"

echo "🔒 LUKHAS Security Scan - $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Install/update security tools
python3 -m pip install -q --upgrade pip safety pip-audit bandit 2>&1 | tee -a "$LOG_FILE"

# Run security scans
echo -e "\n📊 Running security scans..." | tee -a "$LOG_FILE"

# Safety check
echo -e "\n1. Safety Check:" | tee -a "$LOG_FILE"
SAFETY_OUTPUT=$(python3 -m safety check --json 2>&1)
SAFETY_EXIT=$?

if [ $SAFETY_EXIT -ne 0 ]; then
    VULN_COUNT=$(echo "$SAFETY_OUTPUT" | jq '.vulnerabilities | length' 2>/dev/null || echo "unknown")
    echo "   ⚠️ Found $VULN_COUNT vulnerabilities" | tee -a "$LOG_FILE"
    HIGH_VULNS=$(echo "$SAFETY_OUTPUT" | jq '[.vulnerabilities[] | select(.severity == "high")] | length' 2>/dev/null || echo "0")
    
    if [ "$HIGH_VULNS" -gt "0" ]; then
        send_notification "HIGH" "Found $HIGH_VULNS high-severity vulnerabilities"
    fi
else
    echo "   ✅ No vulnerabilities found" | tee -a "$LOG_FILE"
fi

# Pip-audit check
echo -e "\n2. Pip-audit Check:" | tee -a "$LOG_FILE"
PIP_AUDIT_OUTPUT=$(python3 -m pip_audit --format json 2>&1)
PIP_AUDIT_EXIT=$?

if [ $PIP_AUDIT_EXIT -ne 0 ]; then
    AUDIT_COUNT=$(echo "$PIP_AUDIT_OUTPUT" | jq '.vulnerabilities | length' 2>/dev/null || echo "unknown")
    echo "   ⚠️ Found $AUDIT_COUNT vulnerabilities" | tee -a "$LOG_FILE"
else
    echo "   ✅ No vulnerabilities found" | tee -a "$LOG_FILE"
fi

# Bandit security scan
echo -e "\n3. Bandit Security Scan:" | tee -a "$LOG_FILE"
BANDIT_OUTPUT=$(bandit -r . -f json 2>&1)
BANDIT_HIGH=$(echo "$BANDIT_OUTPUT" | jq '.metrics."SEVERITY.HIGH"' 2>/dev/null || echo "0")
BANDIT_MEDIUM=$(echo "$BANDIT_OUTPUT" | jq '.metrics."SEVERITY.MEDIUM"' 2>/dev/null || echo "0")

if [ "$BANDIT_HIGH" -gt "0" ]; then
    echo "   ⚠️ Found $BANDIT_HIGH high-severity code issues" | tee -a "$LOG_FILE"
    send_notification "HIGH" "Bandit found $BANDIT_HIGH high-severity code issues"
else
    echo "   ✅ No high-severity code issues" | tee -a "$LOG_FILE"
fi

# Check for outdated packages
echo -e "\n4. Outdated Packages Check:" | tee -a "$LOG_FILE"
OUTDATED=$(python3 -m pip list --outdated --format=json 2>/dev/null)
OUTDATED_COUNT=$(echo "$OUTDATED" | jq '. | length' 2>/dev/null || echo "0")

if [ "$OUTDATED_COUNT" -gt "10" ]; then
    echo "   ⚠️ $OUTDATED_COUNT packages are outdated" | tee -a "$LOG_FILE"
    send_notification "MEDIUM" "$OUTDATED_COUNT packages need updates"
else
    echo "   ✅ Packages are reasonably up-to-date" | tee -a "$LOG_FILE"
fi

# Generate summary report
echo -e "\n📊 Generating Summary Report..." | tee -a "$LOG_FILE"

cat > "$REPORT_FILE" << EOF
# LUKHAS Security Scan Report
Date: $(date)

## Summary
- Safety vulnerabilities: ${VULN_COUNT:-0}
- Pip-audit vulnerabilities: ${AUDIT_COUNT:-0}
- Bandit high-severity issues: ${BANDIT_HIGH:-0}
- Outdated packages: ${OUTDATED_COUNT:-0}

## Recommendations
EOF

# Add recommendations based on findings
if [ "${HIGH_VULNS:-0}" -gt "0" ] || [ "${BANDIT_HIGH:-0}" -gt "0" ]; then
    echo "1. **URGENT**: Address high-severity vulnerabilities immediately" >> "$REPORT_FILE"
    echo "2. Run 'make security-update' to auto-update vulnerable packages" >> "$REPORT_FILE"
fi

if [ "${OUTDATED_COUNT:-0}" -gt "10" ]; then
    echo "3. Consider updating outdated packages: 'make security-update'" >> "$REPORT_FILE"
fi

echo -e "\n## Next Steps" >> "$REPORT_FILE"
echo "1. Review the full logs at: $LOG_FILE" >> "$REPORT_FILE"
echo "2. Run 'make security-audit' for detailed reports" >> "$REPORT_FILE"
echo "3. Use 'make security-fix' to automatically fix issues" >> "$REPORT_FILE"

# Auto-fix if LUKHAS_AUTO_FIX is set
if [ "${LUKHAS_AUTO_FIX:-false}" = "true" ]; then
    echo -e "\n🔧 Auto-fix enabled, attempting to fix issues..." | tee -a "$LOG_FILE"
    
    # Only auto-fix if there are vulnerabilities
    if [ "${VULN_COUNT:-0}" -gt "0" ] || [ "${AUDIT_COUNT:-0}" -gt "0" ]; then
        python scripts/security-update.py --auto --no-test >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            send_notification "INFO" "Auto-fix completed successfully"
            echo "   ✅ Auto-fix completed" | tee -a "$LOG_FILE"
        else
            send_notification "WARNING" "Auto-fix failed, manual intervention required"
            echo "   ❌ Auto-fix failed" | tee -a "$LOG_FILE"
        fi
    fi
fi

# Final summary
echo -e "\n========================================" | tee -a "$LOG_FILE"
echo "Security scan completed at $(date)" | tee -a "$LOG_FILE"
echo "Report saved to: $REPORT_FILE" | tee -a "$LOG_FILE"
echo "Logs saved to: $LOG_FILE" | tee -a "$LOG_FILE"

# Exit with appropriate code
if [ "${HIGH_VULNS:-0}" -gt "0" ] || [ "${BANDIT_HIGH:-0}" -gt "0" ]; then
    exit 1  # High severity issues found
elif [ "${VULN_COUNT:-0}" -gt "0" ] || [ "${AUDIT_COUNT:-0}" -gt "0" ]; then
    exit 2  # Medium severity issues found
else
    exit 0  # All clear
fi