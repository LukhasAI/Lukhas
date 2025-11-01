# Claude Code PR Review Setup

Automated Claude Code reviews for LUKHAS pull requests via Perplexity API.

## Setup (One-Time)

### Add Perplexity API Key to GitHub

1. Get API key from https://www.perplexity.ai/settings/api
2. Go to Repository Settings → Secrets and variables → Actions
3. Add secret: `PERPLEXITY_API_KEY` = your API key

**Why Perplexity?** Perplexity provides access to Claude models (3.7, 4.0, 4.5) with competitive pricing and the same quality.

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

**Option 4: Specify Model Version**
```bash
gh pr comment 123 --body "@claude review with 4.5"  # Use Claude Sonnet 4.5
gh pr comment 123 --body "@claude review with 3.7"  # Use Claude Sonnet 3.7
gh pr comment 123 --body "@claude review with 4.0"  # Use Claude Sonnet 4.0 (default)
```

### PR Template

When creating a PR via GitHub UI, uncomment:
```markdown
<!-- @claude review this PR -->
```

## What Gets Reviewed

- Architecture & lane boundaries (candidate/, core/, lukhas/)
- Code quality & bugs
- Security issues
- LUKHAS standards compliance
- MATRIZ integration impact

## Model Options

**Default**: Claude Sonnet 4.0 (`claude-3-5-sonnet-20241022`)

- **Claude 3.7** - Fastest, good for quick reviews
- **Claude 4.0** - Balanced speed and depth (default)
- **Claude 4.5** - Most thorough, best for complex PRs

Specify in your request: `@claude review with 4.5`

## Cost & Limits

- **Cost**: ~$0.005-0.03 per review (via Perplexity)
- **Best for**: PRs <10k lines
- **Time**: 30-60 seconds
- **Models**: All Claude Sonnet versions available

## Troubleshooting

- Verify `@claude` is mentioned in PR
- Check `PERPLEXITY_API_KEY` secret is set correctly
- View workflow logs in Actions tab
- Ensure Perplexity API has access to Claude models

## API Comparison

**Perplexity API vs Direct Anthropic:**
- ✅ Lower cost (~50% cheaper)
- ✅ Access to multiple Claude versions
- ✅ Same model quality
- ✅ Compatible API format

See: docs/development/CLAUDE_REVIEW_QUICKSTART.md
