# Claude Code PR Review Setup

Automated Claude Code reviews for LUKHAS pull requests.

## Setup (One-Time)

### Add Anthropic API Key to GitHub

1. Get API key from https://console.anthropic.com/
2. Go to Repository Settings → Secrets and variables → Actions
3. Add secret: `ANTHROPIC_API_KEY` = your API key

## Usage

### Request Claude Review

**Option 1: Using Make**
```bash
make claude-review
```

**Option 2: Using Script**
```bash
./scripts/request_claude_review.sh [PR_NUMBER]
```

**Option 3: Manual Comment**
```bash
gh pr comment 123 --body "@claude review this PR"
```

### PR Template

When creating a PR via GitHub UI, uncomment:
```markdown
<!-- @claude review this PR for architecture compliance and code quality -->
```

## What Gets Reviewed

- Architecture & lane boundaries
- Code quality & bugs
- Security issues
- LUKHAS standards compliance
- MATRIZ integration impact

## Cost & Limits

- **Cost**: ~$0.01-0.05 per review
- **Best for**: PRs <10k lines
- **Time**: 30-60 seconds

## Troubleshooting

- Verify `@claude` is mentioned in PR
- Check `ANTHROPIC_API_KEY` secret is set
- View workflow logs in Actions tab

See: docs/development/CLAUDE_REVIEW_QUICKSTART.md
