#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# pip Version Monitoring Script
# 
# Purpose: Monitor PyPI for pip 25.3 release (CVE-2025-8869 fix)
# Usage: ./check_pip_version.sh [--notify]
# Cron: 0 9 * * * /path/to/check_pip_version.sh --notify
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/pip-version-monitor.log"
ALERT_FILE="${PROJECT_ROOT}/.pip-upgrade-alert"

# Configuration
CURRENT_VERSION="24.0"
TARGET_VERSION="25.3"
PYPI_API_URL="https://pypi.org/pypi/pip/json"
GITHUB_RELEASES_URL="https://api.github.com/repos/pypa/pip/releases/latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Print colored message
print_color() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

# Check if notification is enabled
NOTIFY=false
if [[ "${1:-}" == "--notify" ]]; then
    NOTIFY=true
fi

# Function to compare versions
version_gt() {
    # Returns 0 if $1 > $2
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

# Fetch latest pip version from PyPI
fetch_pypi_version() {
    log "INFO" "Fetching latest pip version from PyPI..."
    
    if ! command -v curl &> /dev/null; then
        log "ERROR" "curl not found. Please install curl."
        return 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log "ERROR" "jq not found. Please install jq."
        return 1
    fi
    
    local response
    response=$(curl -s "$PYPI_API_URL")
    
    if [[ -z "$response" ]]; then
        log "ERROR" "Failed to fetch data from PyPI"
        return 1
    fi
    
    local latest_version
    latest_version=$(echo "$response" | jq -r '.info.version')
    
    if [[ -z "$latest_version" ]] || [[ "$latest_version" == "null" ]]; then
        log "ERROR" "Could not parse version from PyPI response"
        return 1
    fi
    
    echo "$latest_version"
}

# Fetch latest pip version from GitHub Releases
fetch_github_version() {
    log "INFO" "Fetching latest pip release from GitHub..."
    
    local response
    response=$(curl -s "$GITHUB_RELEASES_URL")
    
    if [[ -z "$response" ]]; then
        log "WARN" "Failed to fetch data from GitHub"
        return 1
    fi
    
    local latest_version
    latest_version=$(echo "$response" | jq -r '.tag_name' | sed 's/^v//')
    
    if [[ -z "$latest_version" ]] || [[ "$latest_version" == "null" ]]; then
        log "WARN" "Could not parse version from GitHub response"
        return 1
    fi
    
    echo "$latest_version"
}

# Send notification (placeholder - implement based on notification system)
send_notification() {
    local subject="$1"
    local message="$2"
    
    log "INFO" "NOTIFICATION: $subject"
    log "INFO" "$message"
    
    # Email notification (if mail command is available)
    if command -v mail &> /dev/null && [[ -n "${SECURITY_EMAIL:-}" ]]; then
        echo "$message" | mail -s "$subject" "$SECURITY_EMAIL"
        log "INFO" "Email notification sent to $SECURITY_EMAIL"
    fi
    
    # Slack notification (if webhook URL is configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        local payload
        payload=$(cat <<EOF
{
    "text": "*$subject*",
    "attachments": [{
        "color": "good",
        "text": "$message"
    }]
}
EOF
)
        curl -s -X POST -H 'Content-type: application/json' \
            --data "$payload" "$SLACK_WEBHOOK_URL" > /dev/null
        log "INFO" "Slack notification sent"
    fi
    
    # GitHub Issue notification (if GitHub token is available)
    if [[ -n "${GITHUB_TOKEN:-}" ]] && [[ -n "${GITHUB_REPO:-}" ]]; then
        local issue_body="$message

Automated notification from pip version monitoring.
See: docs/security/PIP_VERSION_MONITORING.md"
        
        gh issue create \
            --repo "$GITHUB_REPO" \
            --title "$subject" \
            --body "$issue_body" \
            --label "security,P0,enhancement" \
            2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Create alert file for dashboard
    cat > "$ALERT_FILE" <<EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "alert_type": "pip_upgrade_available",
    "severity": "high",
    "message": "$subject",
    "details": "$message",
    "action_required": true
}
EOF
    
    log "INFO" "Alert file created: $ALERT_FILE"
}

# Main monitoring logic
main() {
    print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$BLUE" "🔍 pip Version Monitoring"
    print_color "$BLUE" "   CVE-2025-8869 Upgrade Tracker"
    print_color "$BLUE" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    log "INFO" "Starting pip version check..."
    log "INFO" "Current version: $CURRENT_VERSION"
    log "INFO" "Target version: $TARGET_VERSION"
    
    # Fetch latest version
    local latest_version
    latest_version=$(fetch_pypi_version)
    
    if [[ -z "$latest_version" ]]; then
        log "ERROR" "Failed to fetch pip version from PyPI"
        # Try GitHub as fallback
        latest_version=$(fetch_github_version)
        if [[ -z "$latest_version" ]]; then
            log "ERROR" "Failed to fetch pip version from both PyPI and GitHub"
            exit 1
        fi
    fi
    
    log "INFO" "Latest pip version: $latest_version"
    
    # Display current status
    print_color "$YELLOW" "\n📊 Status:"
    echo "   Current LUKHAS version: $CURRENT_VERSION"
    echo "   Latest PyPI version:    $latest_version"
    echo "   Target version:         $TARGET_VERSION"
    echo
    
    # Check if target version is released
    if [[ "$latest_version" == "$TARGET_VERSION" ]] || version_gt "$latest_version" "$TARGET_VERSION"; then
        print_color "$GREEN" "✅ SUCCESS: pip $TARGET_VERSION or later is available!"
        echo
        print_color "$GREEN" "🎉 CVE-2025-8869 fix is now available in pip $latest_version"
        echo
        
        log "INFO" "Target version $TARGET_VERSION released! Current latest: $latest_version"
        
        # Send notification if enabled
        if [[ "$NOTIFY" == true ]]; then
            local subject="🚨 pip $TARGET_VERSION Released - CVE-2025-8869 Fix Available"
            local message="pip version $latest_version has been released!

CVE-2025-8869 (Arbitrary File Overwrite) fix is now available.

Action Required:
1. Review upgrade plan: docs/security/PIP_VERSION_MONITORING.md
2. Test in development environment
3. Schedule production upgrade

Current LUKHAS version: $CURRENT_VERSION
Latest available: $latest_version

References:
- Advisory: docs/security/CVE-2025-8869-PIP-ADVISORY.md
- Upgrade Guide: docs/security/PIP_VERSION_MONITORING.md
- GitHub PR: https://github.com/pypa/pip/pull/13550"
            
            send_notification "$subject" "$message"
        fi
        
        print_color "$YELLOW" "📋 Next Steps:"
        echo "   1. Review: docs/security/PIP_VERSION_MONITORING.md"
        echo "   2. Test in development environment"
        echo "   3. Update CI/CD pipelines"
        echo "   4. Schedule production upgrade"
        echo
        
        exit 0
    else
        print_color "$YELLOW" "⏳ Waiting for pip $TARGET_VERSION release..."
        echo
        echo "   Latest version ($latest_version) does not yet contain the fix."
        echo "   Continuing to monitor for pip $TARGET_VERSION release."
        echo
        
        log "INFO" "Still waiting for target version. Latest: $latest_version, Target: $TARGET_VERSION"
        
        # Check if alert file exists and should be cleaned up
        if [[ -f "$ALERT_FILE" ]]; then
            rm -f "$ALERT_FILE"
            log "INFO" "Removed stale alert file"
        fi
        
        exit 1
    fi
}

# Run main function
main "$@"
