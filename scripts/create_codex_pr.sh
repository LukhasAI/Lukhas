#!/bin/bash
# Create a PR draft and let Codex complete the implementation
# Usage: ./scripts/create_codex_pr.sh "task description" "branch-name"

set -e

TASK_DESC="$1"
BRANCH_NAME="${2:-codex-task-$(date +%m%d-%H%M)}"

if [ -z "$TASK_DESC" ]; then
    echo "Usage: $0 'task description' [branch-name]"
    exit 1
fi

echo "🚀 Creating Codex-assisted PR workflow..."
echo "Task: $TASK_DESC"
echo "Branch: $BRANCH_NAME"

# 1. Create and checkout new branch
git checkout -b "$BRANCH_NAME"

# 2. Create a placeholder commit (required for PR)
cat > .codex-task.md <<EOF
# Codex Task

**Task**: $TASK_DESC

**Status**: Awaiting Codex implementation

## Instructions for @codex

Please implement the following:

$TASK_DESC

When complete:
1. Run tests: \`pytest -q\`
2. Run linting: \`ruff check .\`
3. Update this file with completion status
EOF

git add .codex-task.md
git commit -m "chore: create codex task for $TASK_DESC"

# 3. Push branch
git push -u origin "$BRANCH_NAME"

# 4. Create draft PR with @codex mention
gh pr create \
    --draft \
    --title "Codex Task: $TASK_DESC" \
    --body "@codex please implement the following:

$TASK_DESC

## Requirements
- Run tests: \`pytest -q\`
- Run linting: \`ruff check .\`
- Follow LUKHAS coding standards
- Respect lane boundaries

## Context
Read \`lukhas_context.md\` in relevant directories for architecture context.

When done, mark this PR as ready for review." \
    --label "codex-task,automated"

echo "✅ PR created! Codex will begin work when it processes the mention."
echo "Check: gh pr list --label codex-task"
