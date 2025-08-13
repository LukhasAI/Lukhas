#!/bin/bash

# 🎯 LUKHAS Correct Namespace Plan 
# Understanding: lukhas/ is acceptance system, lukhas_pwm/ is main package

echo "🎯 LUKHAS Namespace Transition - CORRECTED PLAN"
echo "═══════════════════════════════════════════════════════════════"
echo

echo "📊 CORRECT Understanding:"
echo "• lukhas/ = Acceptance system (accepted/archive/candidate/quarantine)"
echo "• lukhas_pwm/ = Main package (should become new lukhas/)"
echo "• Goal: lukhas_pwm/ → lukhas/ AND current lukhas/ → lukhas/acceptance/"
echo

echo "🔄 SAFE Namespace Migration Plan:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "STEP 1: Preserve the acceptance system 📦"
echo "  git mv lukhas/ lukhas_acceptance_system/"
echo "  # Temporarily move the acceptance system out of the way"
echo

echo "STEP 2: Move main package 🔄"  
echo "  git mv lukhas_pwm/ lukhas/"
echo "  # Now lukhas/ contains the main package (flags, api, etc.)"
echo

echo "STEP 3: Restore acceptance system as submodule 🏗️"
echo "  git mv lukhas_acceptance_system/ lukhas/acceptance/"
echo "  # Now it's lukhas/acceptance/{accepted,archive,candidate,quarantine}"
echo

echo "STEP 4: Update lukhas/__init__.py 📝"
echo "  # Expose main modules (flags, api, etc.)"
echo "  # Keep acceptance system separate in lukhas.acceptance"
echo

echo "STEP 5: Update imports gradually 🔄"
echo "  # from lukhas_pwm.flags → from lukhas.flags"
echo "  # Keep lukhas.acceptance.* separate"
echo

echo "🎮 Would you like to proceed with this plan?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1] YES - Execute the full plan"
echo "[2] STEP-BY-STEP - Do one step at a time"  
echo "[3] NO - Keep current structure for now"
echo

read -p "Enter choice [1/2/3]: " choice

case $choice in
    1)
        echo "🚀 Executing full namespace migration..."
        
        # Step 1: Preserve acceptance system
        echo "Step 1: Moving acceptance system..."
        git mv lukhas/ lukhas_acceptance_system/
        
        # Step 2: Move main package  
        echo "Step 2: Moving main package..."
        git mv lukhas_pwm/ lukhas/
        
        # Step 3: Restore acceptance as submodule
        echo "Step 3: Restoring acceptance system..."
        mkdir -p lukhas/acceptance
        git mv lukhas_acceptance_system/* lukhas/acceptance/
        rmdir lukhas_acceptance_system/
        
        # Step 4: Update lukhas/__init__.py
        echo "Step 4: Updating main init file..."
        cat > lukhas/__init__.py << 'EOF'
"""
LUKHAS AI - Main Package
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

__version__ = "3.0.0"
__trinity__ = "⚛️🧠🛡️"

# Main package exports (from old lukhas_pwm)
from . import flags
from . import api
from . import audit
from . import branding
from . import colony
from . import dna
from . import feedback
from . import metrics
from . import migration
from . import modulation
from . import openai
from . import tools

# Acceptance system (kept separate)
from . import acceptance

EOF
        
        echo "✅ Full migration complete!"
        echo "🧪 Test with: python -c 'import lukhas; print(lukhas.__version__)'"
        ;;
        
    2)
        echo "📋 STEP-BY-STEP mode selected"
        echo ""
        echo "Run these commands one by one:"
        echo "  git mv lukhas/ lukhas_acceptance_system/"
        echo "  git mv lukhas_pwm/ lukhas/"  
        echo "  mkdir -p lukhas/acceptance"
        echo "  git mv lukhas_acceptance_system/* lukhas/acceptance/"
        echo "  # Then update lukhas/__init__.py manually"
        ;;
        
    3)
        echo "✅ Keeping current structure"
        echo "💡 Alternative: Just update imports to use 'lukhas_pwm' consistently"
        echo "   This avoids any folder moves and is safest"
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo
echo "🎯 After any changes:"
echo "• Test imports: python -c 'import lukhas.flags; print(\"✅ Working\")'"
echo "• Test acceptance: python -c 'import lukhas.acceptance.accepted; print(\"✅ Working\")'"
echo "• Run tests: python -m pytest tests/ -x"
echo "• Commit: git add . && git commit -m 'chore: namespace lukhas_pwm → lukhas'"

echo "🎉 Namespace plan ready!"
