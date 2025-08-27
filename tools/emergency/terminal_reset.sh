#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════════
# 🛠️ LUKHAS AI - Emergency Terminal Reset Script
# ═══════════════════════════════════════════════════════════════════════════════════
# Purpose: Reset frozen terminals and optimize VS Code performance
# Usage: ./tools/emergency/terminal_reset.sh
# ═══════════════════════════════════════════════════════════════════════════════════

echo "🚨 LUKHAS AI - Emergency Terminal Reset"
echo "═══════════════════════════════════════════════════════════════════════════════════"

# Kill any hanging Python processes from VS Code extensions
echo "🔄 Cleaning up Python LSP processes..."
pkill -f "lsp_server.py" || true
pkill -f "lsp_runner.py" || true
pkill -f "black-formatter" || true
pkill -f "flake8" || true

# Clear terminal history and reset
echo "🧹 Resetting terminal state..."
reset
clear

# Restart VS Code workspace if needed
echo "💡 To fully reset VS Code:"
echo "   1. Cmd+Shift+P → 'Developer: Reload Window'"
echo "   2. Or close and reopen VS Code"

# Check if we're in the correct directory
if [[ $(pwd) == *"Lukhas_PWM"* ]]; then
    echo "✅ Current directory: $(pwd)"

    # Activate virtual environment if available
    if [[ -f ".venv/bin/activate" ]]; then
        echo "🐍 Activating Python virtual environment..."
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    fi

    # Check Git status
    echo "📊 Git status:"
    git status --porcelain | head -10

else
    echo "⚠️  Not in Lukhas_PWM directory. Navigating..."
    cd /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM 2>/dev/null || {
        echo "❌ Could not find Lukhas_PWM directory"
        exit 1
    }
fi

echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "✅ Terminal reset complete! Ready for LUKHAS AI development."
echo "💫 'Where consciousness meets code, and quantum thoughts dance with logic.'"
echo "═══════════════════════════════════════════════════════════════════════════════════"
