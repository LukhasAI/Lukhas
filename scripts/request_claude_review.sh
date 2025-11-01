#!/bin/bash
# Request Claude Code review for a pull request
# Usage: ./scripts/request_claude_review.sh [PR_NUMBER]

set -e

PR_NUMBER="${1}"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🤖 Claude Code PR Review Request${NC}"
echo ""

if [ -z "$PR_NUMBER" ]; then
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "${YELLOW}Detecting PR for branch: ${CURRENT_BRANCH}${NC}"
    PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number')
    if [ -z "$PR_NUMBER" ] || [ "$PR_NUMBER" = "null" ]; then
        echo "❌ Error: No open PR found for current branch."
        echo "Usage: $0 [PR_NUMBER]"
        exit 1
    fi
    echo -e "${GREEN}✓ Found PR #${PR_NUMBER}${NC}"
fi

if ! gh pr view "$PR_NUMBER" &>/dev/null; then
    echo "❌ Error: PR #${PR_NUMBER} not found"
    exit 1
fi

PR_TITLE=$(gh pr view "$PR_NUMBER" --json title --jq '.title')
echo "PR #${PR_NUMBER}: ${PR_TITLE}"
echo ""

gh pr comment "$PR_NUMBER" --body "@claude review this PR for:
- Architecture alignment with LUKHAS lane-based structure
- Code quality and best practices
- Security considerations
- Lane boundary compliance
- MATRIZ integration impact"

echo -e "${GREEN}✓ Claude review requested for PR #${PR_NUMBER}${NC}"
echo ""
echo "View workflow progress: gh pr checks $PR_NUMBER"
echo "View PR: gh pr view $PR_NUMBER --web"
