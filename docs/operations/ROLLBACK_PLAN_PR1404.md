# Rollback Plan - PR #1404 Multi-Task Core Features

**PR**: #1404
**Ledger ID**: `LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS`
**Date Created**: 2025-11-13
**Status**: Ready for Execution (if needed)

---

## Executive Summary

This document provides a comprehensive rollback plan for PR #1404, which introduces 40 core feature tasks across 8 subsystems. All changes are **additive** (new directories and files), making rollback straightforward with minimal risk.

**Rollback Complexity**: LOW (simple git revert, no data migrations, no breaking changes)

---

## When to Rollback

### Criteria for Rollback

Execute this rollback plan if **any** of the following conditions are met:

1. **Critical Production Failure** (Severity: P0)
   - System unavailable or degraded performance affecting users
   - Data corruption or loss detected
   - Security vulnerability introduced

2. **Test Failures** (Severity: P1)
   - Smoke tests failing after merge (>10% failure rate)
   - Critical integration tests broken
   - Performance regression >20%

3. **Observability Issues** (Severity: P1)
   - Guardian metrics (`lukhas_guardian_decision_total`) not reporting
   - Memory metrics broken or incorrect
   - Dashboard panels showing errors

4. **Module Registry Conflicts** (Severity: P2)
   - New modules conflicting with existing tier enforcement
   - Import errors from module registration
   - Tier validation failures

---

## Pre-Rollback Checklist

Before executing rollback, complete these steps:

- [ ] **Capture Current State**: Create snapshot of logs and metrics
- [ ] **Verify Issue**: Confirm the issue is caused by PR #1404 changes
- [ ] **Notify Stakeholders**: Alert team in #lukhas-operations channel
- [ ] **Check Dependencies**: Verify no other PRs depend on PR #1404 changes
- [ ] **Backup Data**: Export any new data created by PR #1404 features (dreams, audit logs)

---

## Rollback Procedures

### Option 1: Immediate Git Revert (Recommended)

**Use when**: Quick rollback needed (<1 hour after merge)

**Risk**: LOW
**Duration**: 5-10 minutes
**Requires**: Git commit access to main branch

```bash
# Step 1: Navigate to repository
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Step 2: Ensure you're on main branch
git checkout main
git pull origin main

# Step 3: Identify commits to revert
git log --oneline -10
# Look for:
# - d02bab95: test fixes
# - 468fe4781: 40 feature tasks

# Step 4: Revert commits (in reverse order)
git revert d02bab95 --no-edit
git revert 468fe4781 --no-edit

# Step 5: Verify revert
git status
git diff HEAD~2

# Step 6: Push revert
git push origin main
```

**Expected Output**:
```
[main abc1234] Revert "test(smoke): fix auth tests to use valid JWT tokens"
[main def5678] Revert "feat: complete remaining core features (tasks 33-40)"
```

**Verification**:
```bash
# Verify files removed
ls -la oneiric/ lid/ dast/ eqnox/  # Should show "No such file or directory"

# Verify module registry reverted
grep "oneiric" core/module_registry.py  # Should return no results

# Run smoke tests
make smoke  # Should pass
```

---

### Option 2: Targeted File Removal

**Use when**: Specific features causing issues (partial rollback)

**Risk**: MEDIUM (requires manual file management)
**Duration**: 15-20 minutes

```bash
# Step 1: Remove specific new directories
git rm -r oneiric/          # Dream generation system
git rm -r lid/              # Lambda Identity system
git rm -r dast/             # DAST orchestrator
git rm -r eqnox/            # EQNOX glyph system
git rm -r MATRIZ/analysis/  # MATRIZ analysis tools
git rm -r MATRIZ/tools/     # MATRIZ probes

# Step 2: Revert module registry changes
git checkout HEAD~1 -- core/module_registry.py

# Step 3: Revert test file changes (if needed)
git checkout HEAD~1 -- tests/smoke/test_api_acl.py
git checkout HEAD~1 -- tests/smoke/test_auth_errors.py

# Step 4: Revert specific core system enhancements
git checkout HEAD~1 -- core/memory/strand.py
git checkout HEAD~1 -- core/memory/folds.py
git checkout HEAD~1 -- core/memory/hooks.py
git checkout HEAD~1 -- core/memory/metrics.py
git checkout HEAD~1 -- core/guardian/explain.py
git checkout HEAD~1 -- core/guardian/policies.py
git checkout HEAD~1 -- core/guardian/strings.py

# Step 5: Commit the rollback
git commit -m "rollback(pr1404): remove PR #1404 features due to [ISSUE]

See rollback plan: docs/operations/ROLLBACK_PLAN_PR1404.md
Ledger ID: LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS"

# Step 6: Push
git push origin main
```

---

### Option 3: Branch Rollback (Safest)

**Use when**: Maximum caution required or testing rollback first

**Risk**: LOWEST (isolated testing environment)
**Duration**: 30-45 minutes

```bash
# Step 1: Create rollback branch
git checkout main
git checkout -b rollback/pr1404-$(date +%Y%m%d)

# Step 2: Revert changes on rollback branch
git revert d02bab95 --no-edit
git revert 468fe4781 --no-edit

# Step 3: Push rollback branch
git push origin rollback/pr1404-$(date +%Y%m%d)

# Step 4: Test rollback branch
git checkout rollback/pr1404-$(date +%Y%m%d)
make smoke
make test-tier1
pytest tests/

# Step 5: If tests pass, merge to main
gh pr create --title "Rollback PR #1404" \
  --body "Rollback of PR #1404 due to [ISSUE].

See rollback plan: docs/operations/ROLLBACK_PLAN_PR1404.md
Ledger ID: LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS

Verified: Smoke tests pass, Tier1 tests pass"

# Step 6: Merge after approval
gh pr merge --squash --admin
```

---

## Post-Rollback Verification

After executing rollback, verify system health:

### 1. Test Suite Verification
```bash
# Run full test suite
make smoke              # Should pass all smoke tests
make test-tier1         # Should pass all critical tests
pytest tests/           # Full test suite

# Expected: All tests passing (same as pre-PR #1404)
```

### 2. Module Registry Check
```bash
# Verify new modules removed
python3 -c "
from core.module_registry import ModuleRegistry
registry = ModuleRegistry()
assert 'oneiric' not in registry.MODULE_TIER_REQUIREMENTS
assert 'lid' not in registry.MODULE_TIER_REQUIREMENTS
assert 'dast' not in registry.MODULE_TIER_REQUIREMENTS
assert 'eqnox' not in registry.MODULE_TIER_REQUIREMENTS
print('✅ Module registry rollback verified')
"
```

### 3. Import Safety Check
```bash
# Verify removed modules don't import
python3 -c "
try:
    import oneiric
    print('❌ FAIL: oneiric still importable')
except ModuleNotFoundError:
    print('✅ PASS: oneiric removed')

try:
    import lid
    print('❌ FAIL: lid still importable')
except ModuleNotFoundError:
    print('✅ PASS: lid removed')

try:
    import dast
    print('❌ FAIL: dast still importable')
except ModuleNotFoundError:
    print('✅ PASS: dast removed')
"
```

### 4. Observability Verification
```bash
# Verify existing metrics still working
curl -s http://localhost:8000/metrics | grep lukhas_guardian_decision_total
# Expected: Counter present and incrementing

curl -s http://localhost:8000/metrics | grep lukhas_memory_operations_total
# Expected: Counter present and incrementing

# Verify new metrics removed
curl -s http://localhost:8000/metrics | grep lukhas_dream_generated_total
# Expected: No results (metric removed)
```

### 5. API Health Check
```bash
# Verify API endpoints still working
curl -s http://localhost:8000/health
# Expected: {"status": "healthy"}

curl -s http://localhost:8000/healthz
# Expected: {"status": "ok"}

# Verify removed endpoints gone
curl -s http://localhost:8000/debug/last-directive
# Expected: 404 Not Found
```

---

## Data Cleanup

If PR #1404 features were used before rollback, clean up residual data:

### 1. Dream Generation Data
```bash
# Find and archive dream data (if dream persistence was used)
find . -name "*.dream" -type f
# Archive to: /tmp/pr1404_rollback_dreams_$(date +%Y%m%d).tar.gz

tar czf /tmp/pr1404_rollback_dreams_$(date +%Y%m%d).tar.gz \
  $(find . -name "*.dream" -type f)

# Remove dream files
find . -name "*.dream" -type f -delete
```

### 2. Audit Logs (JSONL)
```bash
# Archive audit logs created by PR #1404
if [ -f logs/audit.jsonl ]; then
  cp logs/audit.jsonl /tmp/pr1404_rollback_audit_$(date +%Y%m%d).jsonl
  echo "Archived audit log to /tmp/"
fi

# Clean audit log entries (optional - may want to keep for forensics)
# grep -v "oneiric\|lid\|dast\|eqnox" logs/audit.jsonl > logs/audit_cleaned.jsonl
```

### 3. Memory Folds
```bash
# Check for double-strand memory folds
python3 -c "
import os
import glob
fold_files = glob.glob('data/memory/folds/*.json')
pr1404_folds = [f for f in fold_files if 'double_strand' in open(f).read()]
print(f'Found {len(pr1404_folds)} PR #1404 memory folds')
print('Archive before cleanup: /tmp/pr1404_rollback_folds_$(date +%Y%m%d).tar.gz')
"
```

---

## Rollback Timeline

**Target Rollback Completion**: <30 minutes from decision

| Phase | Duration | Action |
|-------|----------|--------|
| 0 | 0-5 min | Decision to rollback + stakeholder notification |
| 1 | 5-10 min | Execute git revert (Option 1) |
| 2 | 10-15 min | Verify rollback with smoke tests |
| 3 | 15-20 min | Verify observability and metrics |
| 4 | 20-25 min | Data cleanup (if needed) |
| 5 | 25-30 min | Final verification and stakeholder update |

---

## Re-Introduction Plan

If PR #1404 needs to be re-introduced after fixes:

### 1. Root Cause Analysis
- Document issue that caused rollback
- Identify specific component(s) at fault
- Create reproduction steps

### 2. Targeted Fixes
- Fix identified issues in feature branch
- Add regression tests for the issue
- Verify all T4 checklist items

### 3. Phased Re-Introduction
**Week 1**: Re-introduce 1-2 subsystems at a time
- Start with lowest-risk modules (MATRIZ tools, EQNOX)
- Monitor for issues before proceeding

**Week 2**: Re-introduce medium-risk modules
- Oneiric (dream generation)
- DAST (orchestrator)

**Week 3**: Re-introduce high-impact modules
- ΛiD (authentication changes)
- Guardian enhancements
- Memory double-strand

### 4. Validation Gates
Each phase requires:
- [ ] Smoke tests passing (100%)
- [ ] Integration tests passing (>95%)
- [ ] Performance benchmarks within 10% of baseline
- [ ] No observability metric disruptions
- [ ] 24-hour monitoring period with no incidents

---

## Contact Information

### Rollback Authority
**Primary**: @agi_dev (Technical Lead)
**Secondary**: [Guardian System Owner]

### Escalation Path
1. Alert #lukhas-operations Slack channel
2. Page on-call engineer (if after hours)
3. Create incident ticket: `INC-ROLLBACK-PR1404-YYYYMMDD`

### Rollback Decision Matrix

| Severity | Impact | Decision Time | Approval Required |
|----------|--------|---------------|-------------------|
| P0 | Production down | Immediate | On-call engineer |
| P1 | Major feature broken | <30 minutes | Technical lead |
| P2 | Minor feature broken | <2 hours | Team consensus |
| P3 | Documentation issue | Next sprint | Product owner |

---

## Audit Trail

All rollback actions must be recorded:

```bash
# Create rollback audit log
cat <<EOF > docs/audits/ROLLBACK_AUDIT_PR1404_$(date +%Y%m%d_%H%M%S).md
# Rollback Audit - PR #1404

**Executed By**: \$(whoami)
**Date**: \$(date -Iseconds)
**Reason**: [REASON FOR ROLLBACK]
**Method**: [Option 1/2/3]
**Duration**: [X minutes]
**Data Archived**: [Yes/No]

## Actions Taken
1. [Action 1]
2. [Action 2]
...

## Verification Results
- [ ] Smoke tests: [PASS/FAIL]
- [ ] Module registry: [PASS/FAIL]
- [ ] Observability: [PASS/FAIL]
- [ ] API health: [PASS/FAIL]

## Post-Rollback Status
System Status: [HEALTHY/DEGRADED]
Notes: [Any additional notes]

**Ledger ID**: LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS
**Rollback Plan**: docs/operations/ROLLBACK_PLAN_PR1404.md
EOF
```

---

## Success Criteria

Rollback is considered **successful** when:

✅ All smoke tests passing (378 tests)
✅ All Tier1 critical tests passing
✅ Module registry restored to pre-PR state
✅ Observability metrics reporting correctly
✅ API endpoints responding normally
✅ No import errors from removed modules
✅ Data archived (if features were used)
✅ Rollback audit log created

---

## Document Control

**Version**: 1.0
**Created**: 2025-11-13
**Last Updated**: 2025-11-13
**Maintained By**: LUKHAS Operations Team
**Review Schedule**: After each PR #1404 rollback exercise

**Related Documents**:
- State Snapshot: `docs/audits/STATE_SNAPSHOT_PR1404.md`
- T4 Checklist: PR #1404 description
- Module Registry: `core/module_registry.py`

---

**Generated with Claude Code** (https://claude.com/claude-code)
