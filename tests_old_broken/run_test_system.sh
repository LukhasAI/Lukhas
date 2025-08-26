#!/bin/bash
# LUKHAS AI Comprehensive Test System Runner
# Created: 2025-08-17

set -e

echo "🚀 LUKHAS AI Test System"
echo "========================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking environment...${NC}"
python3 --version

# Install required packages if needed
echo -e "${YELLOW}Installing dependencies...${NC}"
pip3 install -q pytest pytest-asyncio pytest-cov fastapi uvicorn aiohttp 2>/dev/null || true

# Function to display menu
show_menu() {
    echo ""
    echo -e "${GREEN}Select an option:${NC}"
    echo "1) 🧹 Clean up obsolete tests"
    echo "2) 🔍 Analyze test coverage"
    echo "3) 🏗️ Generate missing tests"
    echo "4) ✅ Run all valid tests"
    echo "5) 🔧 Start self-healing system"
    echo "6) 📊 Open test dashboard"
    echo "7) 📈 Generate test report"
    echo "8) 🚀 Full test suite (all of above)"
    echo "9) ❌ Exit"
    echo ""
    read -p "Enter choice [1-9]: " choice
}

# Clean up obsolete tests
cleanup_tests() {
    echo -e "${YELLOW}Cleaning up obsolete tests...${NC}"
    if [ -f "scripts/cleanup_obsolete_tests.sh" ]; then
        bash scripts/cleanup_obsolete_tests.sh
    else
        python3 tests/cleanup_tests.py
    fi
}

# Analyze test coverage
analyze_coverage() {
    echo -e "${YELLOW}Analyzing test coverage...${NC}"
    python3 tests/test_cleanup_plan.py
    echo -e "${GREEN}✅ Analysis complete. Check tests/test_analysis_report.md${NC}"
}

# Generate missing tests
generate_tests() {
    echo -e "${YELLOW}Generating tests for untested functions...${NC}"
    python3 tests/generate_test_suite.py
}

# Run valid tests
run_tests() {
    echo -e "${YELLOW}Running valid tests...${NC}"
    python3 -m pytest tests/ \
        --ignore=tests/test_STUB* \
        -k "not STUB and not stub" \
        --tb=short \
        -v \
        --cov=. \
        --cov-report=html \
        --cov-report=term-missing \
        2>&1 | tee test_results.log
    
    echo -e "${GREEN}✅ Test results saved to test_results.log${NC}"
    echo -e "${GREEN}✅ Coverage report saved to htmlcov/index.html${NC}"
}

# Start self-healing system
start_healing() {
    echo -e "${YELLOW}Starting self-healing system...${NC}"
    echo -e "${BLUE}Dashboard will be available at: http://localhost:8001${NC}"
    python3 tests/self_healing_test_system.py &
    HEALING_PID=$!
    echo "Self-healing system started with PID: $HEALING_PID"
    echo "Press Ctrl+C to stop"
    wait $HEALING_PID
}

# Open dashboard
open_dashboard() {
    echo -e "${YELLOW}Opening test dashboard...${NC}"
    
    # Check if server is running
    if ! curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "Starting server..."
        python3 tests/self_healing_test_system.py &
        sleep 3
    fi
    
    # Open in browser
    if command -v open &> /dev/null; then
        open http://localhost:8001
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8001
    else
        echo -e "${BLUE}Open http://localhost:8001 in your browser${NC}"
    fi
}

# Generate report
generate_report() {
    echo -e "${YELLOW}Generating comprehensive test report...${NC}"
    
    # Run analysis
    python3 tests/test_cleanup_plan.py
    
    # Create summary report
    cat > tests/test_summary_report.md << EOF
# LUKHAS AI Test System Report
Generated: $(date)

## Test Statistics
- Total test files: $(find tests -name "test_*.py" | wc -l)
- Valid tests: $(find tests -name "test_*.py" | grep -v STUB | wc -l)
- Obsolete tests: $(find tests -name "*STUB*" -o -name "*obsolete*" | wc -l)

## Coverage Summary
$(python3 -m pytest tests --cov=. --cov-report=term | tail -5 2>/dev/null || echo "Coverage data not available")

## Recent Test Results
$(tail -20 test_results.log 2>/dev/null || echo "No recent test results")

## Self-Healing Status
- Pattern database: tests/.healing_patterns.pkl
- Healing history: $(ls tests/.backups 2>/dev/null | wc -l) backups created

## Recommendations
1. Remove obsolete tests to improve performance
2. Generate tests for uncovered functions
3. Enable self-healing for automatic fixes
4. Monitor test trends in dashboard

## Next Steps
- Run option 8 for full test suite execution
- Check dashboard at http://localhost:8001
- Review coverage report at htmlcov/index.html
EOF
    
    echo -e "${GREEN}✅ Report saved to tests/test_summary_report.md${NC}"
}

# Full test suite
full_suite() {
    echo -e "${GREEN}Running full test suite...${NC}"
    cleanup_tests
    analyze_coverage
    generate_tests
    run_tests
    generate_report
    echo -e "${GREEN}✅ Full test suite complete!${NC}"
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1) cleanup_tests ;;
        2) analyze_coverage ;;
        3) generate_tests ;;
        4) run_tests ;;
        5) start_healing ;;
        6) open_dashboard ;;
        7) generate_report ;;
        8) full_suite ;;
        9) 
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            ;;
    esac
done