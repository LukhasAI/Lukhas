# Claude Code PR Review - Quick Start

Get AI-assisted code reviews from Claude (via Perplexity) in 3 steps.

## Setup

1. Get API key: https://www.perplexity.ai/settings/api
2. Add to GitHub: Settings → Secrets → Actions → `PERPLEXITY_API_KEY`
3. Done! Workflow is already configured.

## Usage

### Quick Commands

```bash
# Request review for current PR
make claude-review

# Or specify PR number
./scripts/request_claude_review.sh 123

# Or manually
gh pr comment 123 --body "@claude review this PR"
```

### In PR Description

Mention `@claude` anywhere:
```markdown
## Summary
This PR adds new features.

@claude review with 4.5
```

### Choose Model Version

```bash
@claude review          # Uses Claude 4.0 (default)
@claude review with 3.7 # Fastest - Claude Sonnet 3.7
@claude review with 4.5 # Most thorough - Claude Sonnet 4.5
```

## What Happens

1. Workflow detects `@claude` mention
2. Selects model (3.7/4.0/4.5)
3. Analyzes PR diff (30-60 seconds)
4. Posts review comment
5. Adds `claude-reviewed` label

## Review Includes

- ✅ Architecture & lane boundaries
- ✅ Code quality & security
- ✅ LUKHAS standards
- ✅ MATRIZ integration impact

## Cost

~$0.005-0.03 per review via Perplexity (50% cheaper than direct Anthropic)

## Full Documentation

See [CLAUDE_PR_REVIEW_SETUP.md](./CLAUDE_PR_REVIEW_SETUP.md)
