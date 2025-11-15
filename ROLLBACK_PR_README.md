# MATRIZ Shim Rollback PR - Emergency Safety Measure

**Status**: 🟡 DRAFT - DO NOT MERGE (Keep ready for emergency use)
**Priority**: P0 - Critical Safety Infrastructure
**Purpose**: Emergency rollback mechanism for MATRIZ migration failures

---

## Purpose of This PR

This PR exists as a **pre-approved rollback plan** for the MATRIZ compatibility shim removal. It provides a quick-access mechanism to restore MATRIZ/__init__.py if the shim removal causes widespread import failures.

**THIS PR SHOULD REMAIN AS A DRAFT** until an actual rollback is needed.

---

## When to Merge This PR

Merge this PR **ONLY** if:
- ✅ MATRIZ shim removal causes P0/P1 production incident
- ✅ Widespread import failures (>15% of modules)
- ✅ CI/CD pipeline completely broken
- ✅ Incident Commander approves rollback
- ✅ Faster than creating individual fixes

**DO NOT merge if**:
- ❌ Only isolated test failures (fix individually instead)
- ❌ Issue can be resolved with forward patch
- ❌ Failures unrelated to MATRIZ shim

---

## What This PR Contains

### 1. Rollback Runbook
**File**: `docs/runbooks/MATRIZ_SHIM_ROLLBACK.md`
- Complete rollback procedure (3 options)
- Validation steps and success criteria
- Troubleshooting guide
- Communication templates
- Post-rollback actions

### 2. This README
- Rollback authorization criteria
- Quick merge instructions
- Safety guardrails

---

## Quick Rollback Execution

If this PR needs to be merged for emergency rollback:

### Option 1: Merge This PR (Fastest - 2 minutes)
```bash
# 1. Merge with admin override
gh pr merge <this-pr-number> --merge --admin --body "Emergency rollback for incident #<issue-number>"

# 2. Verify shim restored
git pull origin main
ls -la MATRIZ/__init__.py

# 3. Run smoke tests
make smoke

# 4. Monitor CI
gh run watch

# 5. Update incident ticket
gh issue comment <issue-number> --body "✅ MATRIZ shim restored via PR #<this-pr-number>"
```

### Option 2: Manual Revert (5-10 minutes)
```bash
# If PR unavailable, use manual revert
# See docs/runbooks/MATRIZ_SHIM_ROLLBACK.md for complete instructions

# Quick version:
git revert <commit-that-removed-shim>
make smoke
git push origin main
```

---

## Rollback Authorization

**Authority to Merge**:
- Incident Commander during P0/P1 incidents
- Platform Lead
- Any SRE team member with admin access

**Required Approvals**: None (emergency use)

**Communication Required**: Yes - notify #lukhas-ops channel

---

## Safety Guardrails

Before merging this PR, confirm:

- [ ] **Incident severity**: P0 or P1 (production impact)
- [ ] **Root cause confirmed**: Issue is due to MATRIZ shim removal
- [ ] **Alternative fixes considered**: Rollback is fastest option
- [ ] **Incident ticket created**: #\_\_\_\_\_
- [ ] **Communication sent**: #lukhas-ops notified
- [ ] **Backup recorded**: Current HEAD commit: \_\_\_\_\_\_\_\_

---

## What Happens After Rollback

### Immediate Actions (within 15 min)
1. Verify shim restored: `test -f MATRIZ/__init__.py`
2. Run smoke tests: `make smoke` (expect 15/15 pass)
3. Check CI status: `gh run list --limit 5`
4. Update incident ticket with rollback status

### Follow-Up Actions (within 24h)
5. Create post-incident review issue
6. Identify why shim removal failed
7. Update migration checklist with missing validations
8. Plan proper migration approach

### Long-Term Actions
9. Keep this PR open as rollback template
10. Update runbook based on actual rollback experience
11. Enhance pre-migration testing to prevent future rollbacks

---

## Rollback Validation Checklist

After merging this PR, verify:

- [ ] `MATRIZ/__init__.py` file exists (104 lines)
- [ ] `python3 -c "import MATRIZ"` works
- [ ] `python3 -c "import matriz"` emits DeprecationWarning
- [ ] `make smoke` passes (15/15)
- [ ] `./scripts/run_lane_guard_worktree.sh` passes (0 violations)
- [ ] CI workflows green (last 5 runs)
- [ ] Import error rate <0.1%
- [ ] No new production incidents

**Target Time to Recovery**: <30 minutes

---

## Rollback Command Reference

### Quick Commands
```bash
# Check if shim exists
ls -la MATRIZ/__init__.py

# Test imports
python3 -c "import MATRIZ; print('✅ MATRIZ works')"
python3 -c "import matriz; print('✅ matriz works')"

# Run validations
make smoke
./scripts/run_lane_guard_worktree.sh

# Monitor CI
gh run list --limit 10
gh run watch
```

### Rollback Metrics
Monitor these after rollback:
- **Import error rate**: Should drop to <0.1%
- **CI success rate**: Should return to >95%
- **Module failures**: Should return to 0
- **Test pass rate**: Should return to >99%

---

## Related MATRIZ Migration Tasks

This PR supports the following migration tasks:
- **T20251112022**: Run MATRIZ import inventory
- **T20251112023**: Ensure MATRIZ compatibility shim exists & tested
- **T20251112024-032**: MATRIZ package migrations (serve/, core/, orchestrator/, tests/)
- **T20251112033**: Remove MATRIZ/__init__ compatibility shim (only after 48-72h stability)

**Pre-Condition**: All migrations must pass pre-flight checks before shim removal
**Post-Condition**: This PR provides emergency recovery if removal fails

---

## Communication Templates

### When Rollback Initiated
Post in #lukhas-ops:
```
🚨 MATRIZ SHIM ROLLBACK IN PROGRESS

Incident: #<issue-number>
Severity: P0
Action: Merging PR #<this-pr-number> to restore MATRIZ/__init__.py
ETA: 15-30 minutes
Commander: @<name>

Impact: Import failures across <N> modules
Status: Executing rollback, will update in 15min
```

### When Rollback Complete
Post in #lukhas-ops:
```
✅ MATRIZ SHIM ROLLBACK COMPLETE

Incident: #<issue-number>
Duration: <N> minutes
Status: Shim restored, tests passing

Validation:
✅ Smoke tests: 15/15 pass
✅ CI workflows: Green
✅ Import errors: Resolved

Next: Post-incident review within 24h
```

---

## Runbook Location

**Full Rollback Instructions**: `docs/runbooks/MATRIZ_SHIM_ROLLBACK.md`

This runbook contains:
- 3 rollback execution options
- Step-by-step procedures
- Validation matrix
- Troubleshooting guide
- Post-rollback actions

---

## Emergency Contacts

**Primary**: #lukhas-ops Slack channel
**Escalation**: @platform-oncall
**Incident Commander**: Assign at incident start

---

## History

| Date | Action | Executor | Outcome |
|------|--------|----------|---------|
| 2025-11-12 | PR created | Claude Code | Draft ready for emergency use |

---

## Important Notes

1. **DO NOT MERGE** this PR unless actively responding to a MATRIZ migration incident
2. **KEEP AS DRAFT** - this is a safety mechanism, not a feature PR
3. **UPDATE RUNBOOK** after any actual rollback with lessons learned
4. **REVIEW QUARTERLY** to ensure rollback procedure stays current

---

**This PR is part of T4 MATRIZ migration safety infrastructure (T20251112041)**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
