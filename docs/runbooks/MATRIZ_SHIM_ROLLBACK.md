# MATRIZ Shim Rollback Runbook

**Purpose**: Emergency rollback procedure to reinstate MATRIZ/__init__.py compatibility shim
**Priority**: P0 - Critical (blocks MATRIZ migration safety)
**Owner**: SRE/Platform Team
**Last Updated**: 2025-11-12

---

## When to Use This Runbook

Execute this rollback if:
- **Import failures** after MATRIZ shim removal
- **Cascade of module import errors** across candidate/, core/, serve/
- **CI failures** due to lowercase 'matriz' imports
- **Production incidents** related to MATRIZ module loading
- **>15% drift** in post-migration validation tests

**DO NOT execute if**:
- All migrations completed successfully and smoke tests pass
- Only individual test failures (isolate and fix instead)
- Issue can be fixed with forward patch (prefer forward fixes)

---

## Pre-Rollback Checklist

Before executing rollback:

- [ ] **Severity confirmed**: P0/P1 incident with widespread impact
- [ ] **Root cause identified**: Confirmed related to MATRIZ shim removal
- [ ] **Incident commander assigned**: Name: \_\_\_\_\_\_\_ (approve rollback)
- [ ] **Communication sent**: Notified #lukhas-ops, #lukhas-dev channels
- [ ] **Rollback PR available**: This PR (revert/matriz-shim) ready
- [ ] **Backup commit identified**: Record current HEAD: `git rev-parse HEAD`

**Incident Severity Guidelines**:
- **P0** (Execute immediately): Production outage, >50% import failures, CI completely broken
- **P1** (Execute within 1 hour): Partial service degradation, >25% import failures, smoke tests failing
- **P2** (Scheduled rollback): Minor issues, <10% failures, can wait for fix

---

## Rollback Procedure

### Option A: Revert Specific Commit (Recommended)

**Use when**: Shim removal was a single, identifiable commit

```bash
# 1. Identify the commit that removed MATRIZ/__init__.py
git log --oneline --all -20 -- MATRIZ/__init__.py

# Expected output pattern:
# <commit-hash> chore(matriz): remove compatibility shim
# <prior-hash> feat(matriz): update shim for ...

# 2. Record the removal commit hash
REMOVAL_COMMIT="<commit-hash-that-removed-shim>"

# 3. Create revert commit
git revert $REMOVAL_COMMIT --no-edit

# 4. Verify shim restored
ls -la MATRIZ/__init__.py
# Expected: File should exist with ~104 lines

# 5. Run smoke tests
make smoke
# Expected: 15/15 tests pass

# 6. Run lane guard
./scripts/run_lane_guard_worktree.sh
# Expected: No violations

# 7. Push revert commit
git push origin main

# 8. Monitor CI
gh run watch
# Expected: All workflows pass
```

### Option B: Cherry-Pick from History (Fallback)

**Use when**: Multiple commits affected shim, or revert creates conflicts

```bash
# 1. Find last good commit with working shim
git log --oneline --all -50 -- MATRIZ/__init__.py | head -5

# 2. Identify commit hash before removal
LAST_GOOD_COMMIT="<hash-before-removal>"

# 3. Extract shim file
git show $LAST_GOOD_COMMIT:MATRIZ/__init__.py > /tmp/matriz_init_backup.py

# 4. Restore file
cp /tmp/matriz_init_backup.py MATRIZ/__init__.py

# 5. Create commit
git add MATRIZ/__init__.py
git commit -m "fix(matriz): restore compatibility shim for import safety

## Problem
MATRIZ shim removal caused widespread import failures:
- Candidate lane: <N> modules broken
- Core lane: <N> modules broken
- Serve API: <N> modules broken

## Solution
Restored MATRIZ/__init__.py from commit $LAST_GOOD_COMMIT

## Impact
- Reinstates uppercase/lowercase import aliasing
- Resolves <N> import errors
- Restores CI/CD pipeline functionality

## Rollback of Rollback
If this revert needs reverting:
\`\`\`bash
git revert HEAD
make smoke && make lint
git push origin main
\`\`\`

## Next Steps
1. Complete code migrations using AST rewriter
2. Remove shim only after 48-72h stability
3. Keep this PR as reference for future rollbacks

Closes: #<incident-issue-number>
Refs: T20251112041 (Rollback PR creation task)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 6. Push and monitor
git push origin main
gh run watch
```

### Option C: Use This PR (Emergency)

**Use when**: Fastest rollback needed, this PR is pre-approved

```bash
# 1. Fetch this rollback branch
git fetch origin revert/matriz-shim

# 2. Merge rollback PR
gh pr merge <this-pr-number> --merge --admin

# 3. Pull latest
git pull origin main

# 4. Verify and test
ls -la MATRIZ/__init__.py
make smoke

# 5. Monitor deployment
gh run watch
```

---

## Validation Steps

After rollback execution, validate:

### 1. File Restored
```bash
# Verify file exists
test -f MATRIZ/__init__.py && echo "✅ File exists" || echo "❌ File missing"

# Check file size (should be ~3KB, 104 lines)
wc -l MATRIZ/__init__.py
# Expected: 104 MATRIZ/__init__.py

# Verify aliasing logic present
grep -q "sys.modules aliasing" MATRIZ/__init__.py && echo "✅ Aliasing present"
```

### 2. Import Tests Pass
```bash
# Test uppercase import
python3 -c "import MATRIZ; print('✅ MATRIZ import works')"

# Test lowercase import (should emit deprecation warning)
python3 -c "import matriz; print('✅ matriz import works (compat)')" 2>&1 | grep -q "DeprecationWarning"

# Test submodule aliasing
python3 -c "from MATRIZ.core import *; print('✅ Submodule aliasing works')"
```

### 3. Smoke Tests Pass
```bash
# Run full smoke test suite
make smoke 2>&1 | tee /tmp/smoke_rollback.log

# Expected result: 15/15 pass
grep -E "passed|PASSED" /tmp/smoke_rollback.log | wc -l
# Should show: 15
```

### 4. Lane Guard Passes
```bash
# Validate lane import restrictions
./scripts/run_lane_guard_worktree.sh 2>&1 | tee /tmp/lane_guard_rollback.log

# Expected: No violations
grep -E "ERROR|FAIL" /tmp/lane_guard_rollback.log
# Should have no output
```

### 5. CI Pipeline Healthy
```bash
# Check workflow status
gh run list --limit 5

# All workflows should be green
# Expected statuses: completed + success
```

---

## Post-Rollback Actions

### Immediate (within 15 minutes)
1. **Update incident ticket**: Document rollback execution, attach logs
2. **Notify stakeholders**: Post update in #lukhas-ops, #lukhas-dev
3. **Monitor metrics**:
   - Error rate: Should drop to <1%
   - Import failure rate: Should return to 0%
   - CI success rate: Should return to >95%

### Within 1 hour
4. **Create post-incident review issue**: Use template `.github/ISSUE_TEMPLATE/postmortem.md`
5. **Identify root cause**: Why did shim removal cause failures?
6. **Plan forward fix**: Create tasks for proper migration preparation

### Within 24 hours
7. **Update migration checklist**: Add missing validation steps
8. **Enhance pre-migration tests**: Prevent future rollback scenarios
9. **Document lessons learned**: Update MATRIZ migration runbooks

---

## Rollback Verification Matrix

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| File exists | `ls MATRIZ/__init__.py` | File present, ~3KB | ⬜ |
| Uppercase import | `python3 -c "import MATRIZ"` | No errors | ⬜ |
| Lowercase import | `python3 -c "import matriz"` | DeprecationWarning | ⬜ |
| Submodule alias | `python3 -c "from MATRIZ.core import *"` | No errors | ⬜ |
| Smoke tests | `make smoke` | 15/15 pass | ⬜ |
| Lane guard | `./scripts/run_lane_guard_worktree.sh` | 0 violations | ⬜ |
| CI workflows | `gh run list --limit 5` | All green | ⬜ |
| Import errors | Check logs | 0 import errors | ⬜ |

**Rollback Status**: ⬜ Not Started / 🟡 In Progress / ✅ Complete / ❌ Failed

---

## Troubleshooting

### Issue: Git revert conflicts
**Symptom**: `git revert` fails with merge conflicts

**Solution**:
```bash
# Abort revert
git revert --abort

# Use Option B (cherry-pick) instead
# Extract shim from last known good commit
git log --oneline --all -50 -- MATRIZ/__init__.py
git show <last-good-hash>:MATRIZ/__init__.py > MATRIZ/__init__.py
git add MATRIZ/__init__.py
git commit -m "fix(matriz): restore compatibility shim (manual)"
```

### Issue: Smoke tests still failing after rollback
**Symptom**: `make smoke` shows failures even with shim restored

**Diagnosis**:
```bash
# Check which tests are failing
make smoke 2>&1 | grep -E "FAILED|ERROR"

# Verify shim content
diff MATRIZ/__init__.py <(git show HEAD~10:MATRIZ/__init__.py)
# If differences found, shim may have been updated before removal
```

**Solution**: Cherry-pick the exact shim version from working commit

### Issue: CI still failing after rollback
**Symptom**: GitHub Actions workflows continue to fail

**Diagnosis**:
```bash
# Check recent workflow runs
gh run list --limit 10 --json conclusion,name,headSha

# View failure details
gh run view <run-id> --log-failed
```

**Possible causes**:
1. **Cache issues**: Clear GitHub Actions cache
2. **Concurrent PR merged**: Another change introduced new failures
3. **Dependency changes**: Requirements updated incompatibly

**Solution**: Isolate root cause before assuming rollback didn't work

---

## Rollback Success Criteria

Rollback considered successful when ALL of:
- ✅ MATRIZ/__init__.py file restored (104 lines)
- ✅ Smoke tests: 15/15 pass
- ✅ Lane guard: 0 violations
- ✅ CI workflows: >95% success rate (last 5 runs)
- ✅ Import error rate: <0.1% (from logs)
- ✅ Production metrics stable: No error spikes
- ✅ No new incidents reported

**Time to Recovery Target**: <30 minutes from rollback initiation

---

## Communication Templates

### Rollback Initiated
```
🚨 INCIDENT UPDATE - MATRIZ Shim Rollback Initiated

**Incident**: #<issue-number>
**Severity**: P0
**Action**: Restoring MATRIZ/__init__.py compatibility shim
**ETA**: 15-30 minutes
**Commander**: @<name>

**Impact**:
- Import failures across candidate/, core/, serve/ lanes
- CI/CD pipeline disrupted
- <N> modules affected

**Next Update**: 15 minutes
```

### Rollback Complete
```
✅ ROLLBACK COMPLETE - MATRIZ Shim Restored

**Incident**: #<issue-number>
**Rollback Duration**: <N> minutes
**Status**: Shim restored, tests passing

**Validation Results**:
✅ File restored: MATRIZ/__init__.py
✅ Smoke tests: 15/15 pass
✅ Lane guard: 0 violations
✅ CI workflows: Healthy
✅ Import errors: Resolved

**Next Steps**:
1. Post-incident review (within 24h)
2. Migration checklist update
3. Forward fix planning

**Incident Commander**: @<name>
```

---

## Rollback of Rollback (Forward Fix)

If rollback needs reverting (shim removal retry):

```bash
# Wait for proper migration completion first
# Ensure ALL of:
# - AST migrations complete for serve/, core/, orchestrator/
# - 48-72h stability period observed
# - All smoke tests pass consistently
# - Lane guard shows 0 violations

# Then remove shim again
git revert <rollback-commit-hash>
make smoke && make lint
git push origin main

# Monitor for 72 hours before considering stable
```

---

## Related Documentation

- **Migration Runbooks**: `docs/runbooks/MATRIZ_MIGRATION_*.md`
- **AST Rewriter**: `scripts/consolidation/rewrite_matriz_imports.py`
- **Import Inventory**: `scripts/migration/matriz_inventory.sh`
- **Pre-Migration Checklist**: `TODO/MASTER_LOG.md` (Tasks T20251112022-033)
- **Incident Response**: `docs/runbooks/INCIDENT_RESPONSE.md`

---

## Rollback History

| Date | Executor | Reason | Duration | Outcome |
|------|----------|--------|----------|---------|
| - | - | - | - | - |

*No rollbacks executed yet (preparatory runbook)*

---

**Version**: 1.0
**Created**: 2025-11-12
**Last Tested**: Not yet tested (pre-incident preparation)
**Next Review**: After first MATRIZ migration attempt

---

## Approval & Sign-Off

**Runbook Reviewed By**:
- [ ] Platform Lead: \_\_\_\_\_\_\_\_
- [ ] SRE Team: \_\_\_\_\_\_\_\_
- [ ] Security Team: \_\_\_\_\_\_\_\_

**Rollback Authority**: Any SRE team member or Incident Commander during P0/P1 incidents

**Emergency Contact**: #lukhas-ops Slack channel, @platform-oncall
