#!/bin/bash
# LUKHAS PWM Code Formatting Script ⚛️🧠🛡️

echo "🎭 LUKHAS Trinity Framework - Code Formatting"
echo "============================================="

# Activate virtual environment
source .venv/bin/activate

# Format all Python files in lukhas_pwm directory
echo "📝 Formatting Python files with Black..."
python -m black lukhas_pwm/ --exclude="__pycache__|\.git|\.venv|\.pytest_cache"

# Sort imports with isort (if available)
if python -c "import isort" 2>/dev/null; then
    echo "📚 Organizing imports with isort..."
    python -m isort lukhas_pwm/
else
    echo "⚠️  isort not available, skipping import organization"
fi

# Check for syntax errors
echo "🔍 Checking for syntax errors..."
python -m py_compile lukhas_pwm/feedback/store.py
python -m py_compile lukhas_pwm/api/feedback.py
python -m py_compile lukhas_pwm/modulation/lut_adapter.py

echo "✅ Code formatting complete!"
echo ""
echo "🎯 VS Code Settings Applied:"
echo "   - Black formatter enabled"
echo "   - Format on save enabled"
echo "   - Import organization enabled"
echo "   - Python path configured for lukhas_pwm/"
