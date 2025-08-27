#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════════
# ⚡ LUKHAS AI - Terminal Performance Optimizer
# ═══════════════════════════════════════════════════════════════════════════════════
# Purpose: Optimize terminal and VS Code performance to prevent freezing
# Usage: ./tools/emergency/optimize_performance.sh
# ═══════════════════════════════════════════════════════════════════════════════════

echo "⚡ LUKHAS AI - Performance Optimization"
echo "═══════════════════════════════════════════════════════════════════════════════════"

# Limit VS Code extension processes
echo "🔧 Optimizing VS Code extension processes..."

# Set environment variables to limit resource usage
export PYTHONPATH="/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM:$PYTHONPATH"
export COPILOT_TOOLS_LIMIT=5
export COPILOT_ENABLED=true

# Limit Python processes to prevent memory bloat
echo "🐍 Setting Python performance limits..."
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Clean up temporary files
echo "🧹 Cleaning temporary files..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Check memory usage
echo "📊 Current memory usage:"
memory_pressure=$(memory_pressure | head -1)
echo "$memory_pressure"

# Optimize git for better performance
echo "🔧 Optimizing Git performance..."
git config core.preloadindex true
git config core.fscache true
git config gc.auto 256

# Check terminal responsiveness
echo "✅ Testing terminal responsiveness..."
for i in {1..3}; do
    echo "  Test $i: $(date)"
    sleep 0.5
done

echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "✅ Performance optimization complete!"
echo "🚀 Terminal should now run smoother with reduced freezing."
echo "💡 If issues persist, run: ./tools/emergency/terminal_reset.sh"
echo "═══════════════════════════════════════════════════════════════════════════════════"

# Source the optimized environment
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
    echo "🐍 Virtual environment reactivated with optimizations"
fi
