---
status: stable
type: runbook
owner: @lukhas-core
module: governance
redirect: false
moved_to: null
---

![Status: Stable](https://img.shields.io/badge/status-stable-green)
![Owner: @lukhas-core](https://img.shields.io/badge/owner-lukhas--core-lightblue)

# Documentation Governance Merge-Block Activation Runbook

**Version**: 1.0
**Activation Date**: 2025-10-13
**Owner**: @lukhas-core
**Severity**: P1 (Blocks all PR merges touching docs/)

## Overview

This runbook guides the activation of CI merge-blocking for documentation governance violations. After a 1-week grace period (2025-10-07 to 2025-10-13), the CI will **fail** on:

- Non-UTF-8 encoding
- Missing or invalid front-matter
- `owner: unknown` (after grace period ends)
- Stale generated files

## Pre-Activation Checklist

**Deadline**: 2025-10-13 00:00 UTC

- [ ] Verify owner assignment backlog ≤ 100 docs
- [ ] Verify encoding compliance = 100%
- [ ] Verify badge coverage ≥ 90%
- [ ] Send notification to all contributors (Slack/email)
- [ ] Update CLAUDE.md with new governance standards
- [ ] Create GitHub issue template for governance exceptions

## Activation Steps

### Step 1: Update docs_lint.py (Remove Grace Period)

**File**: `scripts/docs_lint.py`

**Change**: Convert owner warnings to errors

```python
# BEFORE (grace period):
if doc.get('owner') in ['unknown', '', None]:
    warnings.append({
        "file": doc_path,
        "warning": "owner_unknown",
        "message": "Owner is 'unknown' - assignment recommended (see OWNERS_BACKLOG.md)",
    })

# AFTER (enforcement):
if doc.get('owner') in ['unknown', '', None]:
    errors.append({
        "file": doc_path,
        "error": "owner_unknown",
        "message": "Owner is 'unknown' - REQUIRED for merge (see OWNERS_BACKLOG.md)",
    })
```

**Test**:
```bash
python3 scripts/docs_lint.py
# Should FAIL if any docs have owner: unknown
```

### Step 2: Update GitHub Branch Protection

**Repository**: `github.com/LukhasAI/Lukhas` (or your org/repo)

**Settings** → **Branches** → **Branch protection rules** → `main`

Add required status check:
- ✅ `docs-governance-gate` (exact job name from .github/workflows/docs-lint.yml)

**Required checks**:
1. Navigate to: `https://github.com/ORG/REPO/settings/branch_protection_rules/RULE_ID`
2. Check: "Require status checks to pass before merging"
3. Add: `Documentation Governance Gate (T4/0.01%)`
4. Ensure: "Require branches to be up to date before merging"
5. Save changes

**Validation**:
- Create test PR touching `docs/` with `owner: unknown`
- Verify CI fails
- Verify PR cannot be merged (red X, not green checkmark)

### Step 3: Communication

**1. Slack Announcement** (2025-10-12 - 24h before activation)

```markdown
🚨 **Documentation Governance Enforcement - 24h Warning**

Starting **2025-10-13 00:00 UTC**, all PRs touching `docs/` will be blocked if:

❌ Any doc has `owner: unknown`
❌ Non-UTF-8 encoding detected
❌ Invalid front-matter
❌ Generated files are stale

**Action Required**:
- Check your assigned docs: `docs/_generated/OWNERS_BACKLOG.md`
- Update front-matter: `owner: @your-github-username`
- Run linter: `python3 scripts/docs_lint.py`

**Help**: See `docs/reports/MERGE_BLOCK_ACTIVATION.md` or ping @lukhas-core
```

**2. Email to All Contributors**

Subject: `[ACTION REQUIRED] Docs Governance Enforcement - Oct 13`

Body: (Same as Slack message + link to runbook)

**3. GitHub Issue Template**

Create `.github/ISSUE_TEMPLATE/governance-exception.md`:

```yaml
---
name: Documentation Governance Exception Request
about: Request temporary exception from docs governance rules
title: '[GOVERNANCE] Exception Request: '
labels: governance, docs
assignees: lukhas-core
---

## Exception Details

**Affected Files**:
- docs/path/to/file.md

**Governance Rule Violated**:
- [ ] owner: unknown
- [ ] Encoding (non-UTF-8)
- [ ] Invalid front-matter
- [ ] Other: ___

**Justification**:
<!-- Why is an exception needed? -->

**Remediation Plan**:
<!-- How and when will this be fixed? -->

**Duration Requested**:
- [ ] 1 week
- [ ] 2 weeks
- [ ] 1 month
- [ ] Other: ___

/cc @lukhas-core
```

### Step 4: Monitor First 48 Hours

**Key Metrics** (check hourly for first 48h):

```bash
# Check failed PRs
gh pr list --state open --label docs

# Check governance errors
python3 scripts/docs_lint.py

# Check backlog
wc -l docs/_generated/OWNERS_BACKLOG.md
```

**Escalation Triggers**:
- \>10 blocked PRs within 4 hours → Review exceptions
- \>50 owner: unknown after 24h → Extend grace period
- CI performance degradation (>2min) → Optimize linter

### Step 5: Weekly Review (Post-Activation)

**Schedule**: Every Monday 10:00 UTC

**Agenda**:
1. Review governance metrics dashboard
2. Process exception requests
3. Update owner assignments from backlog
4. Adjust rules based on feedback

**Command**:
```bash
python3 scripts/governance_metrics.py
# Generates docs/_generated/DOCS_METRICS.json
```

## Rollback Procedure

**Trigger**: >25% of PRs blocked inappropriately

**Steps**:
1. Remove `docs-governance-gate` from required checks (GitHub Settings)
2. Revert `scripts/docs_lint.py` to grace period mode
3. Post mortem: Identify root cause
4. Set new activation date with fixes

**Rollback Command**:
```bash
git revert <merge-block-activation-commit-sha>
git push origin main
```

## Success Criteria

**Week 1** (2025-10-13 to 2025-10-20):
- [ ] <5% PRs require governance exceptions
- [ ] Owner assignment backlog ≤ 50 docs
- [ ] CI performance <60s per PR
- [ ] Zero false positives reported

**Week 4** (2025-10-13 to 2025-11-10):
- [ ] Owner coverage ≥ 95%
- [ ] Badge coverage ≥ 95%
- [ ] Broken links ≤ 100
- [ ] Encoding compliance = 100%

## Troubleshooting

### Issue: "My PR is blocked but docs look correct"

**Solution**:
1. Run linter locally: `python3 scripts/docs_lint.py`
2. Check specific error in CI logs
3. Verify front-matter YAML syntax (no tabs, proper boolean/null types)
4. Regenerate manifest: `python3 scripts/docs_inventory.py`

### Issue: "I don't know who should own this doc"

**Solution**:
1. Check git blame: `git blame -L 1,50 docs/path/to/file.md`
2. Check module mapping: `scripts/owners_map.yaml`
3. Default to team: `owner: @lukhas-core` (will reassign later)
4. Create triage issue if unclear

### Issue: "CI is too slow"

**Solution**:
1. Check if manifest is up to date
2. Verify no large binary files in docs/
3. Optimize linter (reduce link check sample size)
4. Consider caching Python dependencies in CI

## Contacts

**Primary**: @lukhas-core
**Escalation**: @agi-dev
**Slack**: #docs-governance
**GitHub**: Issues labeled `governance`

## References

- [ADR-0002: Documentation Governance](../ADR/ADR-0002-docs-governance.md)
- [OWNERS_BACKLOG.md](../_generated/OWNERS_BACKLOG.md)
- [CI Configuration](.github/workflows/docs-lint.yml)
- [Encoding Guard](../../scripts/encoding_guard.py)
- [Badge Renderer](../../scripts/render_badges.py)

---

*Last Updated*: 2025-10-07
*Next Review*: 2025-10-13 (Activation Day)
*Version*: 1.0
