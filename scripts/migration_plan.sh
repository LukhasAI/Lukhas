#!/bin/bash

# 🎯 LUKHAS Safe Internal Migration - Incremental Plan
# Step-by-step namespace transition (lukhas_pwm → lukhas)

echo "🎯 LUKHAS Internal Namespace Migration Plan"
echo "═══════════════════════════════════════════════════════════════"
echo

echo "📊 Current State Analysis:"
echo "✅ lukhas_pwm/ exists with main modules"
echo "✅ lukhas/ exists with different structure"  
echo "✅ Import aliasing system already in place"
echo "✅ Both namespaces currently working"
echo

echo "🔄 Safe Migration Steps (Choose your pace):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

echo "STEP 1: Test Current State 🧪"
echo "  python -c 'import lukhas_pwm; import lukhas; print(\"✅ Both work\")'"
echo

echo "STEP 2: Gradual Import Updates (Low Risk) 📝"
echo "  # Update new code to use 'import lukhas'"
echo "  # Leave existing 'import lukhas_pwm' for now"
echo "  # Test each change individually"
echo

echo "STEP 3: Move Modules to lukhas/ (Medium Risk) 📦"
echo "  # Move lukhas_pwm/* to lukhas/ gradually"
echo "  # Update lukhas/__init__.py to expose them"
echo "  # Keep lukhas_pwm/ as alias directory"
echo

echo "STEP 4: Update All Imports (Medium Risk) 🔄"
echo "  # Run: ./scripts/migrate_namespace_internal.sh"
echo "  # Updates all 'from lukhas_pwm' → 'from lukhas'"
echo "  # Creates backup before changes"
echo

echo "STEP 5: Remove lukhas_pwm/ (High Risk - Later) 🗑️"
echo "  # Only after everything tested"
echo "  # git mv lukhas_pwm/ → rename to avoid this step"
echo

echo "🎮 Choose Your Approach:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1] CONSERVATIVE: Just update new code to use 'lukhas'"
echo "[2] MODERATE: Run import migration script (with backup)"
echo "[3] AGGRESSIVE: Full migration including module moves"
echo

read -p "Enter choice [1/2/3]: " choice

case $choice in
    1)
        echo "✅ CONSERVATIVE approach selected"
        echo "• Continue using existing lukhas_pwm imports"
        echo "• Use 'import lukhas' for new code only" 
        echo "• Transition gradually over time"
        ;;
    2)
        echo "⚡ MODERATE approach selected"
        echo "• Will update import statements"
        echo "• Creates backup automatically"
        echo "• Test thoroughly after changes"
        read -p "Ready to run migration script? [y/N]: " confirm
        if [[ $confirm =~ ^[Yy] ]]; then
            ./scripts/migrate_namespace_internal.sh
        else
            echo "⏸️  Migration cancelled - run manually when ready"
        fi
        ;;
    3)
        echo "🚨 AGGRESSIVE approach selected"
        echo "• This includes module structure changes"
        echo "• High risk - recommend Step 2 first"
        echo "• Requires careful testing"
        read -p "Are you sure? This is advanced! [y/N]: " confirm
        if [[ $confirm =~ ^[Yy] ]]; then
            echo "🔄 Advanced migration not implemented yet"
            echo "💡 Recommend: Start with option 2 first"
        else
            echo "✅ Smart choice - try option 2 first"
        fi
        ;;
    *)
        echo "❌ Invalid choice. Run script again with 1, 2, or 3"
        exit 1
        ;;
esac

echo
echo "🎯 Next Steps After Any Changes:"
echo "1. Test imports: python -c 'import lukhas; print(\"✅ OK\")'"
echo "2. Run smoke tests: python -m pytest tests/ -k smoke" 
echo "3. Check specific modules you use most"
echo "4. Commit changes: git add . && git commit -m 'chore: namespace migration'"
echo
echo "🔄 Always have rollback ready:"
echo "   • Backup files are in .namespace_migration_backup_*/"
echo "   • git reset --hard HEAD~1 (if committed)"
echo

echo "🎉 Ready for safe, incremental migration!"
