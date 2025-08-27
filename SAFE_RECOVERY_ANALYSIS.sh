#!/bin/bash
# SAFE RECOVERY ANALYSIS - READ ONLY
# No modifications, only analysis and reporting

echo "🔍 LUKHAS SAFE RECOVERY ANALYSIS"
echo "================================="
echo "Timestamp: $(date)"
echo ""

# Create analysis directory
mkdir -p /tmp/lukhas_recovery_analysis
ANALYSIS_DIR="/tmp/lukhas_recovery_analysis"

echo "📊 STEP 1: Categorize Empty Files"
echo "----------------------------------"

# Separate likely legitimate empty files from suspicious ones
echo "🔍 Analyzing empty files by category..."

# Legitimate empty files (usually OK to be empty)
find . -name "__init__.py" -size 0 > "$ANALYSIS_DIR/empty_init_files.txt"
find . -name "*.pyc" -size 0 > "$ANALYSIS_DIR/empty_cache_files.txt"
find . -name ".DS_Store" -size 0 > "$ANALYSIS_DIR/empty_system_files.txt"

# Suspicious empty files (likely should have content)
find . -name "*.md" -size 0 -not -path "*/node_modules/*" > "$ANALYSIS_DIR/suspicious_md_files.txt"
find . -name "*.py" -size 0 -not -name "__init__.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" > "$ANALYSIS_DIR/suspicious_py_files.txt"
find . -name "*.sh" -size 0 > "$ANALYSIS_DIR/suspicious_script_files.txt"
find . -name "*.json" -size 0 -not -path "*/node_modules/*" -not -path "*/.venv/*" > "$ANALYSIS_DIR/suspicious_json_files.txt"

echo "📊 STATISTICS:"
echo "- Legitimate empty __init__.py files: $(wc -l < "$ANALYSIS_DIR/empty_init_files.txt")"
echo "- Suspicious empty .md files: $(wc -l < "$ANALYSIS_DIR/suspicious_md_files.txt")"
echo "- Suspicious empty .py files: $(wc -l < "$ANALYSIS_DIR/suspicious_py_files.txt")"
echo "- Suspicious empty .sh files: $(wc -l < "$ANALYSIS_DIR/suspicious_script_files.txt")"
echo "- Suspicious empty .json files: $(wc -l < "$ANALYSIS_DIR/suspicious_json_files.txt")"
echo ""

echo "🔍 STEP 2: Check Git History for Recovery Sources"
echo "------------------------------------------------"

# Check if files exist in recent commits
echo "Checking git history for file content..."

# Check last 20 commits for key files
key_files=(
    "branding/trinity/TRINITY_BRANDING_GUIDELINES.md"
    "tests/README.md"
    "tools/ci/README.md"
    "EMERGENCY_DATA_RECOVERY_PLAN.md"
    "migrate_paths.py"
    "quantum_to_qi_migrator.py"
)

for file in "${key_files[@]}"; do
    echo "🔍 Checking history for: $file"
    
    # Check last 10 commits
    for i in {1..10}; do
        if git show HEAD~$i:"$file" >/dev/null 2>&1; then
            size=$(git show HEAD~$i:"$file" | wc -c)
            if [ $size -gt 0 ]; then
                echo "  ✅ Found content in HEAD~$i ($size bytes)"
                echo "$file:HEAD~$i:$size" >> "$ANALYSIS_DIR/recoverable_files.txt"
                break
            fi
        fi
    done
done

echo ""
echo "🔍 STEP 3: Analyze Git Stashes"
echo "------------------------------"

# Check stashes for content
stash_count=$(git stash list | wc -l)
echo "Found $stash_count stashes to analyze..."

for i in $(seq 0 $((stash_count-1))); do
    echo "🔍 Analyzing stash@{$i}:"
    git stash show "stash@{$i}" --name-only | head -5 | sed 's/^/  - /'
    
    # Save stash contents list
    git stash show "stash@{$i}" --name-only > "$ANALYSIS_DIR/stash_${i}_files.txt"
done

echo ""
echo "🔍 STEP 4: Time Analysis"
echo "------------------------"

echo "Recent empty file creation times:"
find . -type f -size 0 -newermt "2025-08-26 16:00" -not -path "*/node_modules/*" -not -path "*/.venv/*" | head -10 | while read file; do
    echo "  $(ls -la "$file")"
done

echo ""
echo "📋 STEP 5: Recovery Recommendations"
echo "-----------------------------------"

echo "📁 Analysis files saved to: $ANALYSIS_DIR"
echo ""
echo "🎯 SAFE RECOVERY OPTIONS (in order of safety):"
echo "1. 📚 Review analysis files first"
echo "2. 🔍 Examine specific git commits for content"
echo "3. 📦 Selectively restore files from git history"
echo "4. 🗄️  Check stashes for missing content"
echo "5. 🆘 Last resort: Recreate critical files from templates"
echo ""
echo "⚠️  NEXT STEPS:"
echo "- Review files in $ANALYSIS_DIR"
echo "- Identify which files definitely need recovery"
echo "- Test recovery on a single file first"
echo "- Never bulk restore without verification"
echo ""
echo "🚫 DO NOT COMMIT until recovery is complete!"

ls -la "$ANALYSIS_DIR"
