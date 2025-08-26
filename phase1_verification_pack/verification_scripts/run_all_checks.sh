#!/bin/bash
# Phase 1 Verification Script
# Run all checks to validate Phase 1 implementation

# Navigate to repository root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/../.."

echo "================================"
echo "Phase 1 Verification Suite"
echo "================================"
echo "Running from: $(pwd)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

echo "1. Running AST Acceptance Gate..."
echo "---------------------------------"
python3 tools/acceptance_gate.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Acceptance gate passed${NC}"
else
    echo -e "${RED}❌ Acceptance gate failed${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "2. Running E2E Dry-Run Tests..."
echo "--------------------------------"
python3 -m pytest tests/test_e2e_dryrun.py -v --tb=short
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ E2E tests passed${NC}"
else
    echo -e "${RED}❌ E2E tests failed${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "3. Checking Safety Defaults..."
echo "-------------------------------"
if grep -q "LUKHAS_DRY_RUN_MODE=true" .env.example; then
    echo -e "${GREEN}✅ Dry-run mode enabled by default${NC}"
else
    echo -e "${RED}❌ Dry-run mode not set correctly${NC}"
    OVERALL_STATUS=1
fi

if grep -q "FEATURE_.*=false" .env.example; then
    echo -e "${GREEN}✅ Feature flags disabled by default${NC}"
else
    echo -e "${RED}❌ Feature flags not disabled${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "4. Checking Registry Pattern..."
echo "--------------------------------"
REGISTRY_COUNT=$(grep -l "_REGISTRY\|register_" lukhas/core/core_wrapper.py lukhas/consciousness/consciousness_wrapper.py lukhas/vivox/vivox_wrapper.py 2>/dev/null | wc -l)
if [ $REGISTRY_COUNT -eq 3 ]; then
    echo -e "${GREEN}✅ Registry pattern implemented in all 3 files${NC}"
else
    echo -e "${RED}❌ Registry pattern missing in some files${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "5. Checking CI Configuration..."
echo "--------------------------------"
if grep -q "acceptance-gate:" .github/workflows/ci-enhanced.yml; then
    echo -e "${GREEN}✅ Acceptance gate added to CI${NC}"
else
    echo -e "${RED}❌ Acceptance gate not in CI${NC}"
    OVERALL_STATUS=1
fi
echo ""

echo "================================"
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL PHASE 1 CHECKS PASSED${NC}"
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
fi
echo "================================"

exit $OVERALL_STATUS
