#!/bin/bash
# Comprehensive QI Component Test Suite
# Designed by: Gonzalo Dominguez - Lukhas AI

set -e

echo "🧪 LUKHAS QI Component Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0
RESULTS=""

test_component() {
    local name="$1"
    local cmd="$2"
    
    echo -e "${YELLOW}Testing: $name${NC}"
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name passed${NC}\n"
        RESULTS="$RESULTS\n✅ $name: PASSED"
        ((PASSED++))
    else
        echo -e "${RED}❌ $name failed${NC}\n"
        RESULTS="$RESULTS\n❌ $name: FAILED"
        ((FAILED++))
    fi
}

# 1. Test Calibration Engine
test_component "Calibration Engine" \
    "python3 -m qi.metrics.calibration --test"

# 2. Test PII Detection
test_component "PII Detection" \
    "python3 -m qi.safety.pii --test"

# 3. Test Budget Governor
test_component "Budget Governor" \
    "python3 -m qi.ops.budgeter --test"

# 4. Test TEQ Gate
test_component "TEQ Gate" \
    "python3 -m qi.safety.teq_gate \
        --policy-root qi/safety/policy_packs \
        --jurisdiction global \
        --run-tests"

# 5. Test Provenance (without PyNaCl)
test_component "Provenance Chain" \
    "python3 -m qi.ops.provenance --test"

# 6. Test Risk Orchestrator
test_component "Risk Orchestrator" \
    "echo '{\"calibrated_confidence\":0.3,\"pii\":{\"_auto_hits\":[{}]},\"content_flags\":[\"medical\"]}' > /tmp/test_risk.json && \
     python3 -m qi.safety.risk_orchestrator --context /tmp/test_risk.json --task medical_advice"

# 7. Test Confidence Router
test_component "Confidence Router" \
    "python3 -m qi.router.confidence_router --test"

# 8. Test ConsentGuard
test_component "ConsentGuard" \
    "python3 -m qi.memory.consent_guard test"

# 9. Test Policy Report
test_component "Policy Report" \
    "python3 -m qi.safety.policy_report \
        --policy-root qi/safety/policy_packs \
        --jurisdiction global"

# 10. Test Policy Linter
test_component "Policy Linter" \
    "python3 -m qi.safety.policy_linter \
        --policy-root qi/safety/policy_packs \
        --jurisdiction global"

# 11. Test Policy Mutate
test_component "Policy Mutate" \
    "python3 -m qi.safety.policy_mutate \
        --policy-root qi/safety/policy_packs \
        --jurisdiction global \
        --n 5"

# 12. Test CEVAL
test_component "CEVAL" \
    "python3 -m qi.analysis.ceval --test"

# 13. Test Policy Fuzzer
test_component "Policy Fuzzer" \
    "python3 -m qi.analysis.policy_fuzzer --test"

# 14. Test Consent Ledger
test_component "Consent Ledger" \
    "python3 -m qi.memory.consent_ledger --test"

# 15. Test Provenance Uploader
test_component "Provenance Uploader" \
    "python3 -m qi.safety.provenance_uploader record ./README.md \
        --model-id 'test-model' \
        --prompt 'test prompt' \
        --metadata '{\"test\":true}'"

# 16. Test CI Runner
test_component "CI Runner" \
    "python3 -m qi.safety.ci_runner \
        --policy-root qi/safety/policy_packs \
        --jurisdiction global \
        --mutations 5 \
        --max-mutation-passes 5 \
        --out-json /tmp/test_ci.json"

# 17. Test CI Report
test_component "CI Report" \
    "SAFETY_CI_JSON=/tmp/test_ci.json python3 -m qi.safety.ci_report"

echo "=================================="
echo -e "Test Results Summary:"
echo -e "$RESULTS"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 All QI components tested successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  $FAILED components failed testing${NC}"
    exit 1
fi