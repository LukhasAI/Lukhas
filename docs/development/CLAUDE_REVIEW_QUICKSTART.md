# Claude Code PR Review - Quick Start

Get AI-assisted code reviews from Claude in 3 steps.

## Setup

1. Get API key: https://console.anthropic.com/
2. Add to GitHub: Settings → Secrets → Actions → `ANTHROPIC_API_KEY`
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

@claude please review for lane compliance
```

## What Happens

1. Workflow detects `@claude` mention
2. Analyzes PR diff (30-60 seconds)
3. Posts review comment
4. Adds `claude-reviewed` label

## Review Includes

- ✅ Architecture & lane boundaries  
- ✅ Code quality & security
- ✅ LUKHAS standards
- ✅ MATRIZ integration impact

## Cost

~$0.01-0.05 per review (works best with PRs <10k lines)

## Full Documentation

See [CLAUDE_PR_REVIEW_SETUP.md](./CLAUDE_PR_REVIEW_SETUP.md)
