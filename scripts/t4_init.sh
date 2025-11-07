#!/usr/bin/env bash
#
# T4 Unified Platform - Quick Start Initialization
#
# Validates setup, creates Intent Registry DB, generates initial dashboard
#
# Usage:
#   ./scripts/t4_init.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="$REPO_ROOT/reports/todos/intent_registry.db"
DASHBOARD_PATH="$REPO_ROOT/reports/t4_dashboard.html"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }

log_info "T4 Unified Platform - Quick Start"
log_info "=================================="
log_info ""

# Check Python version
log_info "Checking Python version..."
python_version=$(python3 --version | cut -d' ' -f2)
log_success "Python $python_version detected"

# Check dependencies
log_info "Checking dependencies..."

if ! python3 -c "import libcst" 2>/dev/null; then
    log_warning "libcst not found - installing..."
    pip install libcst
fi

if ! python3 -c "import fastapi" 2>/dev/null; then
    log_warning "fastapi not found - installing..."
    pip install fastapi uvicorn
fi

if ! python3 -c "import yaml" 2>/dev/null; then
    log_warning "pyyaml not found - installing..."
    pip install pyyaml
fi

log_success "All dependencies installed"

# Create Intent Registry DB
log_info "Creating Intent Registry database..."
mkdir -p "$(dirname "$DB_PATH")"

sqlite3 "$DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS intents (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    type TEXT NOT NULL,
    file TEXT NOT NULL,
    line INTEGER NOT NULL,
    reason TEXT NOT NULL,
    reason_category TEXT,
    status TEXT NOT NULL,
    owner TEXT,
    ticket TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_status ON intents(status);
CREATE INDEX IF NOT EXISTS idx_code ON intents(code);
CREATE INDEX IF NOT EXISTS idx_owner ON intents(owner);
CREATE INDEX IF NOT EXISTS idx_file ON intents(file);
EOF

log_success "Intent Registry database created: $DB_PATH"

# Generate initial dashboard
log_info "Generating initial dashboard..."
python3 "$REPO_ROOT/tools/ci/t4_dashboard.py" --output "$DASHBOARD_PATH" || {
    log_warning "Dashboard generation failed (expected on first run)"
}

if [[ -f "$DASHBOARD_PATH" ]]; then
    log_success "Dashboard generated: $DASHBOARD_PATH"
else
    log_warning "Dashboard not generated (will be created after first validator run)"
fi

# Create reports directories
log_info "Creating reports directories..."
mkdir -p "$REPO_ROOT/reports/todos"
mkdir -p "$REPO_ROOT/reports/metrics"
log_success "Reports directories created"

# Make scripts executable
log_info "Setting execute permissions..."
chmod +x "$REPO_ROOT/scripts/t4_parallel_batches.sh"
chmod +x "$REPO_ROOT/tools/ci/migrate_annotations.py"
chmod +x "$REPO_ROOT/tools/ci/check_t4_issues.py"
chmod +x "$REPO_ROOT/tools/ci/t4_dashboard.py"
chmod +x "$REPO_ROOT/tools/ci/intent_api.py"
chmod +x "$REPO_ROOT/tools/ci/codemods/run_codemod.py"
log_success "Execute permissions set"

# Test validator
log_info "Testing unified validator..."
python3 "$REPO_ROOT/tools/ci/check_t4_issues.py" --paths lukhas --json-only > /tmp/t4_test.json || true
violations=$(python3 -c "import json; print(json.load(open('/tmp/t4_test.json'))['summary']['total_findings'])" 2>/dev/null || echo "unknown")
log_success "Validator test complete - found $violations violations"

# Summary
log_info ""
log_info "=================================="
log_success "T4 Unified Platform Ready! 🎉"
log_info "=================================="
log_info ""
log_info "Next steps:"
log_info "  1. Run migration:    python3 tools/ci/migrate_annotations.py --dry-run"
log_info "  2. View dashboard:   open reports/t4_dashboard.html"
log_info "  3. Start API:        uvicorn tools.ci.intent_api:app --port 8001"
log_info "  4. Parallel fixes:   ./scripts/t4_parallel_batches.sh --dry-run"
log_info ""
log_info "Documentation:"
log_info "  - Complete guide:    T4_MEGA_PR_SUMMARY.md"
log_info "  - Design document:   T4_CHANGES.md"
log_info ""
log_info "Quick commands:"
log_info "  make t4-validate     # Run validator"
log_info "  make t4-dashboard    # Generate dashboard"
log_info "  make t4-api          # Start API server"
log_info "  make t4-parallel     # Run parallel batching"
log_info ""
log_success "Initialization complete!"
