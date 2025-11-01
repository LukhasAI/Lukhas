#!/bin/bash
# Helper script to add Perplexity API key to GitHub repository secrets

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔐 Perplexity API Key Setup${NC}"
echo ""

# Check if gh CLI is authenticated
if ! gh auth status &>/dev/null; then
    echo -e "${RED}❌ GitHub CLI not authenticated${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Check current repo
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo -e "Repository: ${GREEN}${REPO}${NC}"
echo ""

# Prompt for API key
echo -e "${YELLOW}Please enter your Perplexity API key:${NC}"
echo "(Get it from: https://www.perplexity.ai/settings/api)"
echo ""
read -s -p "API Key: " API_KEY
echo ""

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ No API key provided${NC}"
    exit 1
fi

# Validate key format (basic check)
if [[ ! "$API_KEY" =~ ^pplx- ]]; then
    echo -e "${YELLOW}⚠️  Warning: API key doesn't start with 'pplx-'${NC}"
    echo "Perplexity keys usually start with 'pplx-'"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Add secret to repository
echo ""
echo "Adding secret to GitHub repository..."

if gh secret set PERPLEXITY_API_KEY --body "$API_KEY" 2>&1; then
    echo ""
    echo -e "${GREEN}✅ Success!${NC} PERPLEXITY_API_KEY has been added to repository secrets"
    echo ""
    echo "Next steps:"
    echo "1. The Claude PR review workflow is now ready to use"
    echo "2. Test it by mentioning @claude in any PR"
    echo "3. Example: 'gh pr comment 123 --body \"@claude review this PR\"'"
    echo ""
    echo "Documentation:"
    echo "  - Quick Start: docs/development/CLAUDE_REVIEW_QUICKSTART.md"
    echo "  - Full Setup: docs/development/CLAUDE_PR_REVIEW_SETUP.md"
else
    echo -e "${RED}❌ Failed to add secret${NC}"
    echo "You may need to add it manually via GitHub web interface:"
    echo "  Settings → Secrets and variables → Actions → New repository secret"
    exit 1
fi
