# CI Merge-Block Activation Schedule

**Status**: ⏳ Scheduled for 2025-10-13
**Workflow**: `.github/workflows/docs-lint.yml`

---

## Current Status

**Docs-Lint CI**: ✅ Running on all PRs (advisory only)
**Merge Blocking**: ⚠️ **NOT ENABLED** (1-week grace period)

---

## Grace Period Timeline

| Date | Event |
|------|-------|
| **2025-10-06** | Phase 7 rollout completed |
| **2025-10-06 - 2025-10-13** | **Grace period** - CI runs but doesn't block |
| **2025-10-13** | **Merge blocking activates** |

---

## What Happens During Grace Period?

### For Contributors

1. **CI runs on every PR** touching `docs/**`
2. **Red ❌ status is advisory** - merges still allowed
3. **Fix errors before 2025-10-13** to avoid future blocks
4. **Review errors**: Front-matter, broken links, orphans

### For Maintainers

1. Monitor CI failures in #docs-governance
2. Help contributors fix common errors
3. Triage broken links (use `scripts/links_triage.py`)
4. Assign owners (use `scripts/owners_queue.py`)

---

## Activation Steps (2025-10-13)

### GitHub Repository Settings

1. Navigate to: `Settings → Branches → main`
2. Click: `Add rule` or edit existing branch protection
3. Enable: `Require status checks to pass before merging`
4. Select: `docs-lint` from status checks list
5. Save changes

### Verification

```bash
# Test locally before push
make docs-lint

# Should pass without errors
echo $?  # Should be 0
```

### Communication

**Announcement Template**:
```markdown
🚨 **CI Merge Blocking NOW ACTIVE**

Starting today (2025-10-13), PRs with docs changes must pass `docs-lint` to merge.

**Common Errors**:
- Missing front-matter: Add YAML block to all .md files
- owner: unknown: Assign real owner (@username or team)
- Broken links: Fix or remove invalid links

**Help**:
- Docs: docs/adr/ADR-0002-docs-governance.md
- Slack: #docs-governance
- Scripts: scripts/README_DOCS_SCRIPTS.md
```

---

## Opt-Out Process

If blocking causes significant friction during grace period:

### Temporary Disable

**Option 1**: Disable for all PRs
```yaml
# .github/workflows/docs-lint.yml
jobs:
  lint:
    if: false  # Disable temporarily
```

**Option 2**: Make advisory-only
```yaml
# .github/workflows/docs-lint.yml
jobs:
  lint:
    continue-on-error: true  # Don't block merges
```

### Permanent Disable

Remove from branch protection:
1. Settings → Branches → main
2. Edit rule → Uncheck `docs-lint`
3. Notify team in #docs-governance

---

## Success Criteria for Activation

Before enabling merge blocking, verify:

- [ ] Grace period completed (1 week)
- [ ] <10% of recent PRs fail docs-lint
- [ ] Team comfortable with governance policies
- [ ] Owner assignment process established
- [ ] Broken links triaged (major issues resolved)

If any criterion fails, **extend grace period by 1 week**.

---

## Rollback Plan

If blocking causes unexpected issues after activation:

1. **Immediate**: Disable via GitHub settings (5 minutes)
2. **Communicate**: Post in #docs-governance with reason
3. **Investigate**: Review failed PRs, gather feedback
4. **Adjust**: Fix scripts or policies as needed
5. **Re-enable**: After fixes verified, re-activate blocking

---

## Monitoring During Grace Period

### Daily Checks

```bash
# Count failed CI runs
gh pr list --state all --json number,labels,statusCheckRollup \
  | jq '[.[] | select(.statusCheckRollup[]? .name == "docs-lint" and .statusCheckRollup[].conclusion == "failure")] | length'
```

### Weekly Report

Generate report:
```bash
python3 - <<'PY'
import json
import subprocess

result = subprocess.run(
    ['gh', 'pr', 'list', '--state', 'all', '--limit', '100', '--json', 'number,title,statusCheckRollup'],
    capture_output=True, text=True
)

prs = json.loads(result.stdout)
failed = [pr for pr in prs if any(
    check.get('name') == 'docs-lint' and check.get('conclusion') == 'failure'
    for check in pr.get('statusCheckRollup', [])
)]

print(f"Docs-Lint Failures: {len(failed)}/{len(prs)} PRs")
for pr in failed[:5]:
    print(f"  - #{pr['number']}: {pr['title']}")
PY
```

---

## FAQ

**Q: What if my PR fails docs-lint?**
A: Run `make docs-lint` locally to see errors. Fix front-matter or links, then push again.

**Q: Can I bypass the check for urgent hotfixes?**
A: During grace period: yes, checks are advisory. After activation: admin override required.

**Q: What if I have `owner: unknown` intentionally?**
A: Assign a real owner. `unknown` is a governance flag requiring assignment.

**Q: Why are broken links blocking my PR?**
A: They're not during grace period. After activation, fix broken links before merging.

**Q: Can I disable this for my PR only?**
A: No. All PRs touching docs must pass. Request admin override for exceptions.

---

## Contact

**Questions**: #docs-governance Slack channel
**Issues**: GitHub Issues with label `docs:governance`
**Escalation**: @docs-team or @agi_dev

---

**Created**: 2025-10-06
**Grace Period**: 2025-10-06 to 2025-10-13
**Activation**: 2025-10-13 (scheduled)
**Status**: ⏳ Pending activation
