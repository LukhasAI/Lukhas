#!/bin/bash
# EMERGENCY EMPTY FILES RECOVERY ANALYSIS
# Created: $(date)

echo "🚨 LUKHAS EMPTY FILES CRISIS ANALYSIS"
echo "====================================="
echo ""

echo "📊 STATISTICS:"
echo "Total empty files: $(find . -type f -size 0 | wc -l)"
echo "Empty Python files: $(find . -name "*.py" -size 0 | wc -l)"
echo "Empty Markdown files: $(find . -name "*.md" -size 0 | wc -l)"
echo "Empty JSON files: $(find . -name "*.json" -size 0 | wc -l)"
echo ""

echo "📋 CRITICAL EMPTY FILES REQUIRING IMMEDIATE ATTENTION:"
echo "-----------------------------------------------------"

# Check critical documentation files
critical_files=(
    "README.md"
    "LUKHAS_SYSTEM_STATUS.md"
    "branding/trinity/TRINITY_BRANDING_GUIDELINES.md"
    "tests/README.md"
    "tools/ci/README.md"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ] && [ ! -s "$file" ]; then
        echo "❌ CRITICAL: $file is empty!"
    elif [ -f "$file" ] && [ -s "$file" ]; then
        echo "✅ OK: $file has content ($(wc -c < "$file") bytes)"
    else
        echo "❓ MISSING: $file does not exist"
    fi
done

echo ""
echo "🔍 RECOVERY OPTIONS:"
echo "1. Check git stash: git stash list"
echo "2. Check reflog: git reflog --all"
echo "3. Check VS Code local history"
echo "4. Check Time Machine backups"
echo "5. Regenerate critical files from templates"

echo ""
echo "⚠️  DO NOT COMMIT UNTIL RECOVERY COMPLETE!"
