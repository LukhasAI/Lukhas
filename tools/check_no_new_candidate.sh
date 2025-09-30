#!/bin/bash
# Check for new files under candidate/ directory
# Prevents regression during promotion phase

set -e

echo "🔍 Checking for new files under candidate/..."

# Get files added in this commit that are under candidate/
new_candidate_files=$(git diff --cached --name-only --diff-filter=A | grep '^candidate/' || true)

if [ -n "$new_candidate_files" ]; then
    echo "❌ New files detected under candidate/:"
    echo "$new_candidate_files"
    echo ""
    echo "📋 During the promotion phase, new files should go to flat-root:"
    echo "   Instead of: candidate/core/my_file.py"
    echo "   Use:        core/my_file.py"
    echo ""
    echo "⚠️  Add 'allow:candidate-additions' label to bypass this check if necessary."

    # Check for bypass label in commit message
    if git log -1 --pretty=%B | grep -q "allow:candidate-additions"; then
        echo "✅ Bypass label found in commit message. Allowing candidate additions."
        exit 0
    fi

    exit 1
fi

echo "✅ No new candidate/ files detected"
exit 0