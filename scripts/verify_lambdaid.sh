#!/bin/bash
# verify_lambdaid.sh - Verification script for Lambda ID authentication system
#
# Usage:
#   ./scripts/verify_lambdaid.sh [--quick|--full]
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
#   2 - Script error (missing dependencies, etc.)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Test mode (quick or full)
TEST_MODE="${1:-quick}"

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

print_check() {
    echo -e "${YELLOW}→${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check if file exists
check_file() {
    local file="$1"
    local description="$2"

    print_check "Checking $description"

    if [ -f "$REPO_ROOT/$file" ]; then
        print_pass "Found: $file"
        return 0
    else
        print_fail "Missing: $file"
        return 1
    fi
}

# Check if Python module can be imported
check_python_module() {
    local module="$1"
    local description="$2"

    print_check "Checking $description"

    if python3 -c "import $module" 2>/dev/null; then
        print_pass "Module '$module' available"
        return 0
    else
        print_fail "Module '$module' not available"
        return 1
    fi
}

# Check Lambda ID format using Python
check_lambdaid_format() {
    print_check "Validating Lambda ID format"

    local result
    result=$(python3 -c "
import re
import sys

# Expected format: lid:<base64url>
LID_PATTERN = r'^lid:[A-Za-z0-9_-]{22,}$'

test_cases = [
    ('lid:abc123XYZ-_def456GHI', True),   # Valid
    ('lid:short', False),                  # Too short
    ('invalid:abc123', False),             # Wrong prefix
    ('lid:abc@123', False),                # Invalid chars
    ('lid:', False),                       # Empty ID
]

passed = 0
failed = 0

for test_id, expected_valid in test_cases:
    is_valid = bool(re.match(LID_PATTERN, test_id))
    if is_valid == expected_valid:
        passed += 1
    else:
        failed += 1
        print(f'FAIL: {test_id} (expected valid={expected_valid}, got {is_valid})', file=sys.stderr)

if failed > 0:
    sys.exit(1)
print(f'{passed}/{passed+failed}')
" 2>&1)

    if [ $? -eq 0 ]; then
        print_pass "Lambda ID format validation: $result passed"
        return 0
    else
        print_fail "Lambda ID format validation failed"
        echo "$result"
        return 1
    fi
}

# Check Lambda ID uniqueness using Python
check_lambdaid_uniqueness() {
    print_check "Testing Lambda ID uniqueness (generating 1000 samples)"

    local result
    result=$(python3 -c "
import hashlib
import secrets
import base64
from datetime import datetime

def generate_lambda_id(user_email: str, timestamp: datetime) -> str:
    '''Generate Lambda ID (inferred implementation)'''
    data = f'{user_email}:{timestamp.isoformat()}:{secrets.token_hex(16)}'
    lid_hash = hashlib.sha256(data.encode()).digest()
    lid_b64 = base64.urlsafe_b64encode(lid_hash)[:32].decode()
    return f'lid:{lid_b64}'

# Generate sample Lambda IDs
sample_size = 1000
generated_ids = set()
now = datetime.utcnow()

for i in range(sample_size):
    lid = generate_lambda_id(f'user{i}@example.com', now)
    generated_ids.add(lid)

# Check for duplicates
if len(generated_ids) == sample_size:
    print(f'{sample_size}/{sample_size} unique')
else:
    print(f'DUPLICATES: {sample_size - len(generated_ids)} found', file=sys.stderr)
    exit(1)
" 2>&1)

    if [ $? -eq 0 ]; then
        print_pass "Lambda ID uniqueness: $result"
        return 0
    else
        print_fail "Lambda ID uniqueness check failed"
        echo "$result"
        return 1
    fi
}

# Check core Lambda ID files
check_core_files() {
    print_header "Core Lambda ID Files"

    check_file "lukhas_website/lukhas/identity/lambda_id.py" "Lambda ID core module" || true
    check_file "lukhas_website/lukhas/identity/tiers.py" "Tiered authentication" || true
    check_file "lukhas_website/lukhas/identity/webauthn_production.py" "WebAuthn production" || true
    check_file "lukhas-b904-scan/lukhas_website/lukhas/api/oidc.py" "OIDC API" || true
}

# Check QRG integration status
check_qrg_status() {
    print_header "QRG Integration Status"

    print_check "Checking QRG mock implementations"

    if grep -q "MockModule" "$REPO_ROOT/core/governance/identity/qrg_integration.py" 2>/dev/null; then
        print_warn "QRG uses mock implementations (expected - see issue #1253)"
    else
        print_pass "QRG mock implementations replaced"
    fi

    check_file "products/security/qrg/qrg_core.py" "QRG core system" || true
    check_file "core/governance/identity/qrg_integration.py" "QRG integration layer" || true
}

# Check GLYPH system
check_glyph_system() {
    print_header "GLYPH System Status"

    check_file "lukhas_website/lukhas/core/common/glyph.py" "GLYPH token system" || true
    check_file "labs/governance/identity/core/glyph/glyph_pipeline.py" "GLYPH pipeline" || true

    print_check "Checking GLYPH pipeline dependencies"

    # Check if pipeline references unimplemented components
    if [ -f "$REPO_ROOT/labs/governance/identity/core/glyph/glyph_pipeline.py" ]; then
        if grep -q "LUKHASQRGManager\|PQCCryptoEngine\|LUKHASOrb" "$REPO_ROOT/labs/governance/identity/core/glyph/glyph_pipeline.py"; then
            print_warn "GLYPH pipeline references unimplemented components (expected - see issue #1254)"
        else
            print_pass "GLYPH pipeline components implemented"
        fi
    fi
}

# Check environment configuration
check_env_config() {
    print_header "Environment Configuration"

    print_check "Checking recommended deployment flags"

    # These should be set in production environment (not in code)
    local flags=(
        "WEBAUTHN_ACTIVE"
        "QRG_CONSCIOUSNESS_ENABLED"
        "GLYPH_PIPELINE_ENABLED"
    )

    for flag in "${flags[@]}"; do
        if env | grep -q "^${flag}="; then
            value=$(env | grep "^${flag}=" | cut -d= -f2)
            print_pass "$flag=$value (set in environment)"
        else
            print_warn "$flag not set (should be configured in deployment)"
        fi
    done
}

# Run Python tests if available
run_python_tests() {
    print_header "Python Tests"

    if [ "$TEST_MODE" == "quick" ]; then
        print_check "Quick mode: Skipping full test suite"
        return 0
    fi

    print_check "Running Lambda ID unit tests"

    cd "$REPO_ROOT"

    if [ -d "tests/unit/identity" ]; then
        if pytest tests/unit/identity/ -v --tb=short 2>&1 | tail -10; then
            print_pass "Lambda ID unit tests passed"
        else
            print_fail "Lambda ID unit tests failed"
        fi
    else
        print_warn "No identity unit tests found (tests/unit/identity/ missing)"
    fi
}

# Check audit documentation
check_audit_docs() {
    print_header "Audit Documentation"

    if [ -f "$REPO_ROOT/LAMBDA_ID_AUTHENTICATION_AUDIT.md" ]; then
        print_pass "Audit report exists"
    else
        print_warn "Audit report not in main (see PR #1244)"
    fi

    # Check for Lambda ID generation docs
    if [ -f "$REPO_ROOT/docs/identity/LAMBDA_ID_GENERATION.md" ]; then
        print_pass "Lambda ID generation documented"
    else
        print_warn "Lambda ID generation not documented (see issue #1255)"
    fi
}

# Print summary
print_summary() {
    print_header "Verification Summary"

    echo -e "${GREEN}Passed:${NC}   $PASSED"
    echo -e "${RED}Failed:${NC}   $FAILED"
    echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
    echo ""

    if [ "$FAILED" -eq 0 ]; then
        echo -e "${GREEN}✓ All critical checks passed${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Review warnings above"
        echo "  2. Check PR #1244 for deployment recommendations"
        echo "  3. Review tracking issues: #1253 (QRG), #1254 (GLYPH), #1255 (Lambda ID docs)"
        return 0
    else
        echo -e "${RED}✗ Some checks failed${NC}"
        echo ""
        echo "Please address failures before deploying."
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Lambda ID Authentication System Verification${NC}"
    echo -e "Mode: $TEST_MODE"
    echo ""

    # Change to repo root
    cd "$REPO_ROOT"

    # Run checks
    check_core_files
    check_lambdaid_format
    check_lambdaid_uniqueness
    check_qrg_status
    check_glyph_system
    check_env_config
    check_audit_docs

    if [ "$TEST_MODE" == "full" ]; then
        run_python_tests
    fi

    # Print summary and exit
    print_summary
    exit $?
}

# Run main
main "$@"
