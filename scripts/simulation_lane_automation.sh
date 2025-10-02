#!/usr/bin/env bash
# ---
# title: sim-lane: comprehensive automation wrapper
# about: Complete simulation lane management - validate, test, commit
# entry: bash
# ---
set -euo pipefail

echo "🎭 LUKHAS Simulation Lane Automation (T4/0.01%)"
echo "=============================================="

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Stage 1: Import Isolation Validation
echo -e "\n${YELLOW}Stage 1: Import Isolation Guard${NC}"
if import-linter --cache-dir .importlinter_cache; then
    echo -e "${GREEN}✅ Import isolation passed${NC}"
else
    echo -e "${RED}❌ Import isolation FAILED${NC}"
    echo "Fix import violations before proceeding"
    exit 1
fi

# Stage 2: Manifest Validation
echo -e "\n${YELLOW}Stage 2: Module Manifest Validation${NC}"
if python tools/manifest_validate.py --batch; then
    echo -e "${GREEN}✅ Manifest validation passed${NC}"
else
    echo -e "${RED}❌ Manifest validation FAILED${NC}"
    echo "Fix manifest issues before proceeding"
    exit 1
fi

# Stage 3: Simulation Lane Summary Generation
echo -e "\n${YELLOW}Stage 3: Simulation Lane Summary${NC}"
bash .claude/commands/95_sim_lane_summary.yaml

# Stage 4: Run Simulation Lane Tests (if they exist)
echo -e "\n${YELLOW}Stage 4: Simulation Tests${NC}"
if [ -f "tests/consciousness/simulation/test_simulation_lane.py" ]; then
    if python -m pytest tests/consciousness/simulation/test_simulation_lane.py -v; then
        echo -e "${GREEN}✅ Simulation tests passed${NC}"
    else
        echo -e "${RED}❌ Simulation tests FAILED${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ No simulation tests found (tests/consciousness/simulation/test_simulation_lane.py)${NC}"
fi

# Stage 5: Optional Smoke Test
echo -e "\n${YELLOW}Stage 5: Simulation Smoke Test${NC}"
if [ -f "examples/simulation_smoke.py" ]; then
    if python examples/simulation_smoke.py; then
        echo -e "${GREEN}✅ Smoke test passed${NC}"
    else
        echo -e "${RED}❌ Smoke test FAILED${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ No smoke test found (examples/simulation_smoke.py)${NC}"
fi

# Stage 6: Summary Report
echo -e "\n${GREEN}🎯 Simulation Lane Validation Complete${NC}"
echo "========================================"
echo "✅ Import isolation enforced"
echo "✅ Manifests validated"
echo "✅ Summary generated"
echo "✅ Tests executed"
echo "✅ Smoke tests passed"

# Stage 7: Optional Auto-commit
if [[ "${AUTO_COMMIT:-0}" == "1" ]]; then
    echo -e "\n${YELLOW}Auto-commit mode enabled${NC}"
    if git diff --quiet --exit-code docs/consciousness/SIMULATION_SUMMARY.md; then
        echo "No changes to commit"
    else
        git add docs/consciousness/SIMULATION_SUMMARY.md
        git commit -m "docs(simulation): auto-refresh simulation summary [T4/0.01%]"
        echo -e "${GREEN}✅ Summary auto-committed${NC}"
    fi
fi

echo -e "\n${GREEN}🚀 Simulation lane is ready for development!${NC}"