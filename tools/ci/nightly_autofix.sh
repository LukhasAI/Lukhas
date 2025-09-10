#!/usr/bin/env bash
# T4 Nightly Autofix - Comprehensive automated code maintenance
# Runs repo-wide fixes, TODO annotation, and security scanning

set -euo pipefail

# Configuration
T4_CONFIG=".t4autofix.toml"
LOG_FILE="data/nightly_autofix_$(date +%Y%m%d_%H%M%S).log"
REPORT_FILE="reports/todos/summary.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Skip if disabled
if [[ "${SKIP_NIGHTLY_AUTOFIX:-}" == "1" ]]; then
    log "Nightly autofix disabled by SKIP_NIGHTLY_AUTOFIX=1"
    exit 0
fi

# Ensure we're in the repository root
if [[ ! -f "$T4_CONFIG" ]]; then
    error "T4 config not found. Run from repository root."
    exit 1
fi

# Create necessary directories
mkdir -p data reports/todos

log "🌙 Starting nightly T4 autofix process"

# 1. Security scanning (blocking)
log "🔒 Running security scan..."
if command -v bandit >/dev/null 2>&1; then
    if ! bandit -r . -f json -o data/security_scan.json 2>/dev/null; then
        if [[ -f data/security_scan.json ]] && [[ $(jq '.results | length' data/security_scan.json 2>/dev/null || echo 0) -gt 0 ]]; then
            error "Security vulnerabilities found. Blocking autofix."
            jq -r '.results[] | "  - \(.filename):\(.line_number): \(.issue_text)"' data/security_scan.json | head -10
            exit 1
        fi
    fi
    log "✅ Security scan passed"
else
    warn "bandit not available, skipping security scan"
fi

# 2. Run comprehensive autofix
log "🔧 Running comprehensive autofix..."
initial_changes=$(git diff --name-only | wc -l)

# Run diagnostic-driven orchestrator first
log "🎼 Running diagnostic-driven fix orchestrator..."
if [[ -f tools/automation/diagnostic_orchestrator.py ]]; then
    python3 tools/automation/diagnostic_orchestrator.py --verbose 2>&1 | tee -a "$LOG_FILE" || {
        warn "Diagnostic orchestrator had issues, continuing with standard autofix..."
    }
fi

# Apply enhanced safe transformations
if [[ -f tools/ci/enhanced_auto_fix_safe.py ]]; then
    python3 tools/ci/enhanced_auto_fix_safe.py --batch || {
        warn "Enhanced autofix had issues, falling back to standard autofix..."
        python3 tools/ci/auto_fix_safe.py . --batch || {
            warn "Some autofix operations failed, continuing..."
        }
    }
else
    # Fallback to original autofix
    python3 tools/ci/auto_fix_safe.py . --batch || {
        warn "Some autofix operations failed, continuing..."
    }
fi

# 3. Mark remaining TODOs
log "📝 Annotating remaining TODOs..."
if [[ -f tools/ci/mark_todos.py ]]; then
    python3 tools/ci/mark_todos.py || {
        warn "TODO annotation failed, continuing..."
    }
fi

# 3.5. Collect coverage data for golden nudge
log "📈 Collecting coverage data..."
mkdir -p reports/autofix
if command -v coverage >/dev/null 2>&1 || pip install coverage pytest-cov 2>/dev/null; then
    coverage run -m pytest -q tests/test_imports.py tests/test_integration.py tests/golden/ 2>/dev/null || true
    coverage json -o reports/autofix/coverage.json 2>/dev/null || true
    log "✅ Coverage data collected"
else
    warn "Coverage tools not available, skipping coverage collection"
fi

# 4. Generate TODO summary report
log "📊 Generating TODO summary..."
{
    echo "# TODO Summary Report"
    echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    echo "## Statistics"

    # Count different TODO types
    todo_autofix=$(grep -r "TODO\[T4-AUTOFIX\]" . --include="*.py" 2>/dev/null | wc -l || echo 0)
    todo_manual=$(grep -r "TODO\[T4-MANUAL\]" . --include="*.py" 2>/dev/null | wc -l || echo 0)
    todo_research=$(grep -r "TODO\[T4-RESEARCH\]" . --include="*.py" 2>/dev/null | wc -l || echo 0)
    todo_security=$(grep -r "TODO\[T4-SECURITY\]" . --include="*.py" 2>/dev/null | wc -l || echo 0)

    echo "- T4-AUTOFIX: $todo_autofix"
    echo "- T4-MANUAL: $todo_manual"
    echo "- T4-RESEARCH: $todo_research"
    echo "- T4-SECURITY: $todo_security"
    echo ""

    if [[ $todo_autofix -gt 0 ]]; then
        echo "## Pending Autofix TODOs"
        grep -rn "TODO\[T4-AUTOFIX\]" . --include="*.py" 2>/dev/null | head -20 | while IFS= read -r line; do
            echo "- $line"
        done
        echo ""
    fi

    echo "## System Health"
    echo "- Last nightly run: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- Git status: $(git status --porcelain | wc -l) uncommitted changes"
    echo "- Repository size: $(du -sh . 2>/dev/null | cut -f1 || echo 'unknown')"
    
    # Include orchestrator results if available
    if [[ -f "reports/autofix/orchestrator.json" ]]; then
        echo ""
        echo "## Diagnostic Orchestrator Results"
        python3 -c "
import json
try:
    with open('reports/autofix/orchestrator.json') as f:
        data = json.load(f)
    summary = data.get('summary', {})
    print(f\"- Errors found: {summary.get('total_errors_found', 0)}\")
    print(f\"- Fix strategies applied: {summary.get('fix_strategies_applied', 0)}\")
    print(f\"- Successful fixes: {summary.get('successful_fixes', 0)}\")
    fixes = data.get('fixes_applied', {})
    for strategy, result in fixes.items():
        status = result.get('status', 'unknown')
        print(f\"- {strategy}: {status}\")
except Exception as e:
    print(f\"- Orchestrator report unavailable: {e}\")
" 2>/dev/null || echo "- Orchestrator report unavailable"
    fi

} > "$REPORT_FILE"

# 4.5. Add ownership routing if CODEOWNERS exists and we have TODOs
if [[ -f "CODEOWNERS" ]] && [[ -f "reports/todos/index.json" ]]; then
    python3 - << 'PY'
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path.cwd()))
try:
    from tools.ci.owners_from_codeowners import map_files_to_owners
    todos = Path("reports/todos/index.json")
    body = Path("reports/todos/summary.md")
    if todos.exists() and body.exists():
        data = json.loads(todos.read_text() or "{}")
        files = sorted(list(data.get("files", {}).keys()))
        if files:
            mapping = map_files_to_owners(files)
            lines = ["\n## Ownership Routing", "", "| File | Owners |", "|---|---|"]
            for f in files:
                owners = " ".join(mapping.get(f, [])) or "_unowned_"
                lines.append(f"| `{f}` | {owners} |")
            body.write_text(body.read_text() + "\n" + "\n".join(lines) + "\n")
            print("✅ Added ownership routing to summary")
except Exception as e:
    print(f"⚠️ Could not add ownership routing: {e}")
PY
fi

# 5. Check if we have meaningful changes
final_changes=$(git diff --name-only | wc -l)
total_changes=$((final_changes - initial_changes))

if [[ $total_changes -gt 0 ]]; then
    log "📋 Found $total_changes changes, preparing commit..."

    # Create commit with detailed message
    {
        echo "chore(autofix): nightly T4 maintenance $(date +%Y-%m-%d)"
        echo ""
        echo "Automated fixes applied:"
        git diff --name-only | head -10 | sed 's/^/- /'
        if [[ $(git diff --name-only | wc -l) -gt 10 ]]; then
            echo "- ... and $(($(git diff --name-only | wc -l) - 10)) more files"
        fi
        echo ""
        echo "TODO Summary:"
        echo "- T4-AUTOFIX: $(grep -r "TODO\[T4-AUTOFIX\]" . --include="*.py" 2>/dev/null | wc -l || echo 0)"
        echo "- T4-MANUAL: $(grep -r "TODO\[T4-MANUAL\]" . --include="*.py" 2>/dev/null | wc -l || echo 0)"
        echo ""
        echo "Generated by: tools/ci/nightly_autofix.sh"
        echo "Config: $T4_CONFIG"
        echo "Log: $LOG_FILE"
    } > data/nightly_commit_message.txt

    # Stage all changes
    git add .

    # Commit changes
    if git commit -F data/nightly_commit_message.txt; then
        log "✅ Committed nightly autofix changes"

        # For significant changes, consider creating a PR
        if [[ $total_changes -gt 20 ]] && [[ "${CREATE_NIGHTLY_PR:-}" == "1" ]]; then
            log "🔄 Creating PR for significant changes..."
            # This would require gh CLI or similar
            if command -v gh >/dev/null 2>&1; then
                gh pr create \
                    --title "chore: nightly T4 autofix $(date +%Y-%m-%d)" \
                    --body-file data/nightly_commit_message.txt \
                    --label "automated" \
                    --label "autofix" || {
                    warn "Failed to create PR, changes committed to branch"
                }
            fi
        fi
    else
        warn "Failed to commit changes"
    fi
else
    log "✅ No changes needed, repository clean"
fi

# 6. Run diagnostic monitoring
log "🔍 Running diagnostic monitoring..."
if [[ -f tools/monitoring/diagnostic_monitor.py ]]; then
    python3 tools/monitoring/diagnostic_monitor.py --verbose 2>&1 | tee -a "$LOG_FILE" || {
        warn "Diagnostic monitoring had issues, continuing..."
    }
fi

# 7. Cleanup old logs (keep last 30 days) 
find data/ -name "nightly_autofix_*.log" -mtime +30 -delete 2>/dev/null || true

log "🌙 Nightly T4 autofix completed"
log "📊 Report: $REPORT_FILE"
log "📋 Log: $LOG_FILE"

# Final status
if [[ -f "$REPORT_FILE" ]]; then
    echo ""
    echo "=== TODAY'S TODO SUMMARY ==="
    cat "$REPORT_FILE" | head -20
fi
