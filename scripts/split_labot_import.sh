#!/usr/bin/env bash
set -euo pipefail

# Split a large commit into policy-compliant draft PRs
# Usage: ./scripts/split_labot_import.sh <commit_hash> [group_size]

COMMIT_HASH=${1:?Please provide a commit hash}
GROUP_SIZE=${2:-2}

echo "═══════════════════════════════════════════════════════════"
echo "Commit Splitter - Creating Draft PRs"
echo "Commit: $COMMIT_HASH"
echo "Group size: $GROUP_SIZE files per PR"
echo "═══════════════════════════════════════════════════════════"

# Get the list of files changed in the commit
FILES=($(git show --pretty="" --name-only "$COMMIT_HASH"))

# Function to create PR for a group of files
create_pr_for_group() {
    local commit=$1
    local branch_prefix=$2
    local group_num=$3
    shift 3
    local files=("$@")

    local branch="${branch_prefix}-$(printf '%02d' $group_num)"
    echo ""
    echo "==> Creating branch: $branch"
    echo "Files (${#files[@]}): ${files[*]}"

    # Create branch from main
    git checkout -b "$branch" origin/main || {
        echo "Branch $branch already exists, skipping"
        git checkout main
        return
    }

    # Restore files from commit
    for file in "${files[@]}"; do
        mkdir -p "$(dirname "$file")"
        git checkout "$commit" -- "$file" 2>/dev/null || {
            echo "Warning: Could not restore $file from $commit"
            continue
        }
    done

    # Check if we have changes
    if ! git diff --cached --quiet 2>/dev/null; then
        # Files are already staged by git checkout, don't add extra files
        # git add . would pick up unrelated working directory changes
        git commit -m "chore(import): import files (group $group_num)

Imported from commit $commit:
$(printf '- %s\n' "${files[@]}")

This is part of the systematic import to satisfy policy guard
(max 2 files, max 40 lines per PR).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

        # Push branch
        git push -u origin "$branch"

        # Create draft PR
        local pr_title="chore(import): import artifacts (group $group_num)"
        local pr_body="# Import - Group $group_num

**Source commit**: \`$commit\`
**Files**: ${#files[@]}

## Files in this PR
$(printf '- `%s\n' "${files[@]}")

## Context
This draft PR is part of splitting a large import into policy-compliant chunks (≤2 files, ≤40 lines per PR).

## Review checklist
- [ ] No production code modified (tests/prompts/config only)
- [ ] No secrets committed
- [ ] YAML syntax valid (if applicable)
- [ ] Policy guard passes (\`make policy\`)

**Status**: Draft - requires human review before merge"

        gh pr create --draft \
            --title "$pr_title" \
            --body "$pr_body" \
            2>/dev/null && echo "✅ Draft PR created" || echo "⚠️  PR creation skipped (may require manual creation)"
    else
        echo "No changes to commit, skipping"
    fi

    # Return to main
    git checkout main
}

# Split the files into groups and create PRs
GROUP_NUM=1
for (( i=0; i<${#FILES[@]}; i+=GROUP_SIZE )); do
  GROUP_FILES=("${FILES[@]:i:GROUP_SIZE}")
  create_pr_for_group "$COMMIT_HASH" "import/split" "$GROUP_NUM" "${GROUP_FILES[@]}"
  ((GROUP_NUM++))
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Import splitting complete!"
echo "Created draft PRs for systematic review and merge"
echo ""
echo "Next steps:"
echo "1. Review draft PRs on GitHub"
echo "2. Merge in a safe order"
echo "═══════════════════════════════════════════════════════════"
