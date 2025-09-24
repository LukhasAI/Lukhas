#!/bin/bash
# Capture comprehensive environment information for test baseline
# Generated: 2025-01-22

set -e

OUTPUT_DIR="tests/benchmarks/baseline"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_HUMAN=$(date +"%Y-%m-%d %H:%M:%S %Z")
ENV_FILE="$OUTPUT_DIR/environment_${TIMESTAMP}.txt"

echo "📊 Capturing Environment Information for Test Baseline"
echo "======================================================"

# Create environment report
{
    echo "LUKHAS Memory Safety & Slow Tests - Baseline Environment Report"
    echo "================================================================"
    echo ""
    echo "Timestamp: $DATE_HUMAN"
    echo "Unix Timestamp: $(date +%s)"
    echo ""

    echo "System Information:"
    echo "-------------------"
    echo "Hostname: $(hostname)"
    echo "Operating System: $(uname -s)"
    echo "Kernel Version: $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo "Platform: $(uname -p)"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS Version: $(sw_vers -productVersion)"
        echo "Build Version: $(sw_vers -buildVersion)"
        echo "Hardware: $(sysctl -n hw.model)"
        echo "CPU: $(sysctl -n machdep.cpu.brand_string)"
        echo "CPU Cores: $(sysctl -n hw.ncpu)"
        echo "Physical Memory: $(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}')"
    else
        echo "CPU Info: $(lscpu | grep 'Model name' | sed 's/.*: *//')"
        echo "CPU Cores: $(nproc)"
        echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
    fi

    echo ""
    echo "Python Environment:"
    echo "-------------------"
    echo "Python Version: $(python3 --version 2>&1)"
    echo "Python Path: $(which python3)"
    echo "Pip Version: $(pip3 --version 2>&1 || echo 'pip3 not found')"

    echo ""
    echo "Python Packages (Key Dependencies):"
    echo "------------------------------------"
    pip3 list 2>/dev/null | grep -E "pytest|hypothesis|numpy|scipy|torch|tensorflow" || echo "Unable to list packages"

    echo ""
    echo "Environment Variables (LUKHAS-specific):"
    echo "-----------------------------------------"
    env | grep -E "LUKHAS|PYTHON|PATH" | sort || echo "No LUKHAS-specific variables set"

    echo ""
    echo "Git Information:"
    echo "----------------"
    echo "Current Branch: $(git branch --show-current)"
    echo "Last Commit: $(git log -1 --oneline)"
    echo "Git SHA: $(git rev-parse HEAD)"
    echo "Uncommitted Changes: $(git status --porcelain | wc -l | tr -d ' ') files"

    echo ""
    echo "Test Configuration:"
    echo "-------------------"
    echo "pytest.ini markers:"
    grep -E "memory_safety|memory_interleavings|slow" pytest.ini | head -5

    echo ""
    echo "Resource Limits:"
    echo "----------------"
    ulimit -a 2>/dev/null || echo "Unable to get resource limits"

    echo ""
    echo "Disk Space:"
    echo "-----------"
    df -h . | tail -1

    echo ""
    echo "Load Average:"
    echo "-------------"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        uptime
    else
        cat /proc/loadavg 2>/dev/null || uptime
    fi

    echo ""
    echo "Test Command:"
    echo "-------------"
    echo "pytest -m 'memory_safety or memory_interleavings or slow' -v --tb=short --timeout=600"

} > "$ENV_FILE"

echo "✅ Environment captured to: $ENV_FILE"
echo ""

# Return the filename for use in other scripts
echo "$ENV_FILE"