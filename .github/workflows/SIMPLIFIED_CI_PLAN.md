# Simplified CI Plan for 3000 Minutes/Month

## Current Problem
- **136 total workflows**
- **91 workflows run on EVERY PR**
- Estimated cost: 10-30 min per PR × 91 workflows = **900-2700 min per PR!**
- With 5 PRs/month, you'd exceed the limit easily

## Recommended Simplification Strategy

### Tier 1: ESSENTIAL (Always Run on PR)
**Budget: ~300 min/month**

Keep these 5-7 critical workflows:
1. ✅ **ci.yml** - Core Python tests
2. ✅ **coverage-gates.yml** - Test coverage validation
3. ✅ **architectural-guardian.yml** - Lane boundary checks
4. ✅ **auto-copilot-review.yml** - AI code review (lightweight)
5. ✅ **auto-codex-review.yml** - LUKHAS-specific validation
6. ✅ **codeql-analysis.yml** - Security scanning
7. ✅ **dependency-review.yml** - Dependency security

### Tier 2: SELECTIVE (Path Filters)
**Budget: ~200 min/month**

Run ONLY when relevant files change:
- **docs-lint.yml** - Only run when `docs/**` or `*.md` changes
- **branding-docs-check.yml** - Only run when `branding/**` changes
- **dream-expand-*.yml** - Only run when `candidate/consciousness/dream/**` changes
- **bridge-quality.yml** - Only run when `candidate/bridge/**` changes
- **content-lint.yml** - Only run when branding content changes

### Tier 3: SCHEDULED (Nightly/Weekly)
**Budget: ~200 min/month**

Move expensive tests to scheduled runs:
- **benchmarks-nightly.yml** - Already scheduled ✅
- **advanced-testing.yml** - Run nightly instead of per-PR
- **coverage.yml** - Run nightly (coverage-gates.yml covers PRs)
- **security-scans.yml** - Full scans weekly
- **audit-*.yml** - Weekly audits

### Tier 4: MANUAL (workflow_dispatch only)
**Budget: ~100 min/month**

Disable auto-run, keep for manual use:
- **promotion-*.yml** - Manual promotion workflows
- **deploy-*.yml** - Manual deployments
- **migration-*.yml** - Manual migration checks
- **experimental/*.yml** - Development workflows

### Tier 5: DISABLE (Move to workflows-disabled/)
**Budget: Saved ~2000 min/month**

84 workflows to disable:
- Duplicate CI workflows
- Experimental features
- Non-critical quality checks
- Research/prototype workflows

## Implementation Plan

### Phase 1: Quick Wins (Save 80% immediately)
```bash
# Move 84 non-essential workflows to disabled folder
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/.github
mkdir -p workflows-streamlined
mv workflows/*.yml workflows-streamlined/  # Backup all
# Move back only Tier 1 workflows
```

### Phase 2: Add Path Filters (Save another 10%)
Add to Tier 2 workflows:
```yaml
on:
  pull_request:
    paths:
      - 'docs/**'
      - '**/*.md'
```

### Phase 3: Setup Monitoring (Stay within budget)
```yaml
# New workflow: usage-monitor.yml
# Runs weekly, alerts if >2400 min used
```

## Expected Results

### Before Simplification
- **Per PR**: ~900-2700 minutes
- **Monthly**: Exceeds 3000 min with just 2-3 PRs
- **Cost**: $$$ overage charges

### After Simplification
- **Per PR**: ~50-100 minutes (Tier 1 only)
- **Monthly**: ~500-800 minutes total
- **Cost**: FREE (within 3000 min limit)
- **Buffer**: 2200 min for scheduled/manual workflows

## Next Steps

1. **Approve this plan** - Confirm which workflows are truly essential
2. **Backup workflows** - Save current state
3. **Implement Tier 1** - Keep only 7 essential workflows
4. **Add path filters** - Smart triggers for Tier 2
5. **Setup monitoring** - Track usage weekly
6. **Test with 1 PR** - Validate minute consumption

## Questions for You

1. Which workflows are absolutely critical for you?
2. Can security scans run weekly instead of per-PR?
3. Should I create a single "mega-workflow" that combines related checks?
4. Do you want usage alerts at 50%, 75%, 90% of 3000 min?
