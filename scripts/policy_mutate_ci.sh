#!/bin/bash
# Safety CI Pipeline Script
# Designed by: Gonzalo Dominguez - Lukhas AI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🛡️  LUKHAS QI Safety CI Pipeline"
echo "================================"

# Configuration
POLICY_ROOT="${POLICY_ROOT:-qi/safety/policy_packs}"
JURISDICTION="${JURISDICTION:-global}"
MUTATIONS="${MUTATIONS:-25}"
MAX_PASSES="${MAX_PASSES:-2}"
OUT_DIR="${OUT_DIR:-ci_results}"

# Create output directory
mkdir -p "$OUT_DIR"

# Function to run step and check result
run_step() {
    local name="$1"
    local cmd="$2"
    echo -e "\n${YELLOW}→ Running: $name${NC}"
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $name passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $name failed${NC}"
        return 1
    fi
}

# Track failures
FAILED=0

# 1. Policy Coverage Report
run_step "Policy Coverage Report" \
    "python -m qi.safety.policy_report \
        --policy-root '$POLICY_ROOT' \
        --jurisdiction '$JURISDICTION' \
        --out-md '$OUT_DIR/coverage_report.md'" || ((FAILED++))

# 2. Policy Linter
run_step "Policy Linter" \
    "python -m qi.safety.policy_linter \
        --policy-root '$POLICY_ROOT' \
        --jurisdiction '$JURISDICTION'" || ((FAILED++))

# 3. TEQ Gate Tests
run_step "TEQ Gate Tests" \
    "python -m qi.safety.teq_gate \
        --policy-root '$POLICY_ROOT' \
        --jurisdiction '$JURISDICTION' \
        --run-tests > '$OUT_DIR/teq_tests.json'" || ((FAILED++))

# 4. Mutation Fuzzing
echo -e "\n${YELLOW}→ Running: Mutation Fuzzing (${MUTATIONS} mutations)${NC}"
MUTATION_OUT=$(python -m qi.safety.policy_mutate \
    --policy-root "$POLICY_ROOT" \
    --jurisdiction "$JURISDICTION" \
    --n "$MUTATIONS" 2>/dev/null)

# Check mutation results
if [ -n "$MUTATION_OUT" ]; then
    echo "$MUTATION_OUT" > "$OUT_DIR/mutations.json"
    
    # Count how many mutations incorrectly passed
    PASSED_COUNT=$(echo "$MUTATION_OUT" | python -c "
import json, sys
data = json.load(sys.stdin)
print(sum(1 for r in data if r.get('allowed', True)))
" 2>/dev/null || echo "$((MAX_PASSES + 1))")
    
    if [ "$PASSED_COUNT" -gt "$MAX_PASSES" ]; then
        echo -e "${RED}❌ Mutation test failed: $PASSED_COUNT mutations passed (max allowed: $MAX_PASSES)${NC}"
        ((FAILED++))
    else
        echo -e "${GREEN}✅ Mutation test passed: $PASSED_COUNT mutations allowed (max: $MAX_PASSES)${NC}"
    fi
else
    echo -e "${RED}❌ Mutation test failed: no output${NC}"
    ((FAILED++))
fi

# 5. ConsentGuard Tests
if python -c "import qi.memory.consent_guard" 2>/dev/null; then
    run_step "ConsentGuard Tests" \
        "python -m qi.memory.consent_guard test" || ((FAILED++))
else
    echo -e "${YELLOW}⚠️  ConsentGuard not available, skipping${NC}"
fi

# 6. Run comprehensive CI runner
run_step "Comprehensive CI Runner" \
    "python -m qi.safety.ci_runner \
        --policy-root '$POLICY_ROOT' \
        --jurisdiction '$JURISDICTION' \
        --mutations '$MUTATIONS' \
        --max-mutation-passes '$MAX_PASSES' \
        --out-json '$OUT_DIR/ci_summary.json'" || ((FAILED++))

# Final summary
echo -e "\n================================"
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ All Safety CI checks passed!${NC}"
    echo "Results saved to: $OUT_DIR/"
    exit 0
else
    echo -e "${RED}❌ $FAILED Safety CI checks failed${NC}"
    echo "Check results in: $OUT_DIR/"
    exit 1
fi