# GitHub Issues Audit & Action Plan

**Audit Date**: 2025-11-06
**Total Open Issues**: 68
**Action**: Close obsolete, consolidate duplicates, assign @codex to valid issues

---

## 📊 Summary

| Category | Count | Action |
|----------|-------|--------|
| Bridge Gap Issues (Obsolete) | 26 | **CLOSE ALL** |
| CODEX Lint Issues (Valid) | 7 | **@CODEX ASSIGN** |
| TODO Migration Issues | 15 | **REVIEW & CLOSE** |
| Copilot Refactor Tasks | 7 | **REVIEW & CLOSE** |
| Codex Tasks (Old) | 4 | **CLOSE** |
| Other Issues | 9 | **EVALUATE** |

---

## 🗑️ ISSUES TO CLOSE (40+ issues)

### Bridge Gap Issues (26 issues) - **CLOSE AS "WON'T FIX"**

**Reason**: These are from the Nov 3 MATRIZ Flattening campaign which has been superseded. The `labs/` directory still exists but bridge exports are no longer the chosen approach.

**Issues to Close**:
- #903 - Bridge Gap: tools/* modules
- #902 - Bridge Gap: tests/* modules
- #901 - Bridge Gap: orchestration/* modules
- #900 - Bridge Gap: memory/* modules
- #899 - Bridge Gap: governance/* modules (Batch 3)
- #898 - Bridge Gap: governance/* modules (Batch 2)
- #897 - Bridge Gap: governance/* modules (Batch 1)
- #896 - Bridge Gap: emotion/* modules
- #895 - Bridge Gap: core/* modules (Batch 9)
- #894 - Bridge Gap: core/* modules (Batch 8)
- #893 - Bridge Gap: core/* modules (Batch 7)
- #892 - Bridge Gap: core/* modules (Batch 6)
- #891 - Bridge Gap: core/* modules (Batch 5)
- #889 - Bridge Gap: core/* modules (Batch 3)
- #888 - Bridge Gap: core/* modules (Batch 2)
- #887 - Bridge Gap: core/* modules (Batch 1)
- #885 - Bridge Gap: consciousness/* modules (Batch 2)
- #884 - Bridge Gap: consciousness/* modules (Batch 1)
- #883 - Bridge Gap: bridge/* modules
- #882 - Bridge Gap: bio/* modules
- #881 - Bridge Gap: api/* modules
- #880 - EPIC: MATRIZ Flattening Audit & Bridge Remediation Campaign
- #879 - Bridge Gap Follow-up & Metrics Tracking
- #878 - Phase 3 — Fix Test Assertions & API Compatibility
- #877 - Phase 2 — Automation: Bulk Bridge Generator for 766 Gaps
- #876 - Phase 1 — Fix High-Impact Bridges (Top 5 modules)

**Closure Message**:
```
Closing this issue as the MATRIZ flattening bridge export approach has been superseded. The `labs/` directory structure and import strategy has evolved beyond the bridge pattern described here. Collection errors and import issues are now tracked in bug_report.md (ISSUE-006 through ISSUE-025) and TEST_ASSIGNMENT_REPORT.md (TEST-008).
```

---

### Codex Tasks (4 issues) - **CLOSE AS "COMPLETED" or "SUPERSEDED"**

These appear to be old task tracking issues:

- #810 - [Codex] Task 04 — Batch-2 through Batch-8 Automation
- #809 - [Codex] Task 03 — Batch-1 Application & Ephemeral Worktree Validation
- #808 - [Codex] Task 02 — Conservative Patch Filter
- #807 - [Codex] Task 01 — Dry-Run Codemod & Patch Generation

**Closure Message**:
```
Closing as completed or superseded by newer lint cleanup issues (#945, #946, #851, #852, etc). Current linting work is tracked in [CODEX] issues with specific error codes and violation counts.
```

---

### Copilot Refactor Tasks (7 issues) - **CLOSE IF COMPLETED, otherwise UPDATE**

These are from Nov 2 lazy loading refactor work:

- #821 - feat(core): create ProviderRegistry infrastructure (BLOCKS Copilot Task 01)
- #819 - refactor(tags): investigate tags/registry.py location and refactoring needs
- #818 - refactor(governance): add __getattr__ lazy proxy for governance features
- #817 - refactor(tags): create __getattr__ lazy proxy for tag exports
- #816 - refactor(matriz): add lazy dream engine loader with fallback
- #815 - refactor(observability): enhance lazy loading in evidence_collection.py
- #814 - refactor(provider): lazy-load labs in gpt_colony_orchestrator.py

**Action**: Check if these were completed in recent PRs. If yes, close. If no, consolidate into a single tracking issue.

---

### TODO Migration Issues (15 issues) - **REVIEW & CLOSE MOST**

These are from Oct 28 TODO→Issue migration. Many are likely addressed or duplicated in bug_report.md:

- #629 - [TODO] Implement identity verification for guardian compliance
- #627 - [TODO] address security regression
- #623 - [TODO] security
- #619 - [TODO] create_security_monitor
- #611 - [TODO] security; consider using impor...
- #607 - [TODO] MultiJurisdictionComplianceEng...
- #605 - [TODO] SecurityMesh
- #600 - [TODO] Validate against token store
- #584 - [TODO] Implement proper admin authentication
- #582 - [TODO] Audit Λ-trace for security logging
- #581 - [TODO] Real authentication challenge (WebAuthn / device key)
- #574 - [TODO] - Implement full consciousness token mapping
- #560 - [TODO] .constitutional_ai_compliance....
- #552 - [TODO] implement authentication

**Action**: Close most as duplicates of bug_report.md issues or obsolete. Keep only if genuinely unique and still relevant.

---

## ✅ VALID ISSUES - ASSIGN @CODEX

### CODEX Lint Issues (7 issues) - **ASSIGN @CODEX WITH FULL INSTRUCTIONS**

These are the primary lint cleanup tasks:

#### Issue #946: Quick Wins - Small Error Types Cleanup
- **Priority**: HIGH (quick wins)
- **Errors**: 42 total (B017, F405, F823, RUF034, SIM116, B023, E722, W291)
- **Status**: Ready for execution

#### Issue #945: Phase 2 - Import Organization (E402, UP035)
- **Priority**: HIGH
- **Errors**: 2,449 total (E402: 1,233, UP035: 1,216)
- **Status**: Ready for execution

#### Issue #852: Fix F821 CRITICAL - Undefined names
- **Priority**: P0 CRITICAL
- **Errors**: 144 violations causing runtime errors
- **Status**: Highest priority

#### Issue #851: Fix E402 - Import ordering
- **Priority**: P1
- **Errors**: 189 violations
- **Status**: High priority

#### Issue #860: Fix RUF012 - Mutable class attribute defaults
- **Priority**: P1
- **Errors**: 119 violations
- **Status**: High priority

#### Issue #861: Fix RUF006 - Unnecessary async comprehension
- **Priority**: P2
- **Errors**: 80 violations
- **Status**: Medium priority

#### Issue #850: Fix SIM102 - Simplify nested if statements
- **Priority**: P3
- **Errors**: 247 violations
- **Status**: Lower priority

---

## 🔍 OTHER ISSUES TO EVALUATE (9 issues)

### High Priority

- **#859** - [COPILOT] Resolve PR #805 M1 Branch Conflicts
  - **Action**: Check if PR #805 still exists and needs resolution

- **#399** - 🔴 Security: pip Arbitrary File Overwrite (CVE-2025-8869)
  - **Action**: Check if dependencies are updated, close if fixed

- **#360** - 🛡️ Security Posture Alert: Score Below Threshold
  - **Action**: Run security scan, update or close

### Medium Priority

- **#494** - No-Op guard observation period: monitor false positives
  - **Action**: Check if monitoring is in place, close if complete

- **#492** - PQC runner provisioning: enable liboqs in CI
  - **Action**: Check CI configuration, close if enabled

- **#490** - MATRIZ-007: Migrate checkpoint signing to Dilithium2 (PQC)
  - **Action**: Check if PQC signing is implemented

- **#436** - Task A: Achieve 99% Manifest Coverage (363 Manifests Needed)
  - **Action**: Check manifest count, update or close

- **#364** - 🧹 Test Suite Cleanup: Fix 66 Collection Errors
  - **Action**: **DUPLICATE of TEST-008** in TEST_ASSIGNMENT_REPORT.md (223 errors)
  - **CLOSE as duplicate**, reference TEST-008

- **#389** - refactor(lint): E402/E70x slice 2 — reliability subset
  - **Action**: Check if superseded by #945, close if duplicate

- **#388** - refactor(lint): E402/E70x slice 1 — adapters subset
  - **Action**: Check if superseded by #945, close if duplicate

---

## 📋 @CODEX ASSIGNMENT INSTRUCTIONS

For each valid CODEX lint issue, add this comment:

### Template for @codex Assignment

```markdown
@codex please fix this lint issue using the following approach:

## Context
- **Repository**: /Users/agi_dev/LOCAL-REPOS/Lukhas
- **Python Version**: 3.11
- **Linter**: ruff (see ruff.toml for configuration)
- **Related Documents**:
  - bug_report.md - System bugs and issues
  - TEST_ASSIGNMENT_REPORT.md - Test coverage tasks
  - CLAUDE.md - Repository context and rules

## Task Requirements

1. **Analysis Phase**:
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas
   ruff check . --select {ERROR_CODE} --output-format=json > /tmp/violations.json
   ```

2. **Fix Strategy**:
   - Read full issue description for error patterns
   - Identify safe automated fixes vs manual review needed
   - Group violations by file/module for batch processing
   - Prioritize high-impact files (lukhas/, core/, serve/)

3. **Implementation**:
   - Use `ruff check --fix` for safe automated fixes
   - Manual fixes for logic-sensitive issues (B017, F821, etc.)
   - Maintain functionality - no behavior changes
   - Respect lane boundaries (see CLAUDE.md)

4. **Validation**:
   ```bash
   # After fixes, verify:
   ruff check . --select {ERROR_CODE}  # Should show reduced count
   make smoke  # Smoke tests must pass
   pytest tests/unit/ -x  # Unit tests must pass
   ```

5. **Commit Standards** (T4 Format):
   ```
   lint({scope}): fix {ERROR_CODE} violations in {module}

   Problem:
   - {ERROR_CODE} had {N} violations
   - {Impact description}

   Solution:
   - Fixed {N} violations in {files}
   - {Approach taken}

   Impact:
   - {ERROR_CODE} violations: {before} → {after}
   - All tests passing
   - No functionality changes

   Closes: #{ISSUE_NUMBER}
   ```

6. **Reporting**:
   - Comment on issue with before/after metrics
   - List files changed
   - Confirm tests passing
   - Note any manual review items

## Success Criteria
- [ ] Violations reduced by ≥80% (or target specified in issue)
- [ ] All smoke tests passing
- [ ] No new test failures introduced
- [ ] T4 commit message format
- [ ] Issue updated with results

## Priority
{P0 CRITICAL / P1 HIGH / P2 MEDIUM / P3 LOW}

## Estimated Effort
{Time estimate from issue description}

Begin when ready. Ask questions if any requirements are unclear.
```

---

## 🎯 EXECUTION PLAN

### Step 1: Bulk Close Obsolete Issues (30+ issues)

```bash
# Close all bridge gap issues
for issue in 903 902 901 900 899 898 897 896 895 894 893 892 891 889 888 887 885 884 883 882 881 880 879 878 877 876; do
  gh issue close $issue --comment "Closing this issue as the MATRIZ flattening bridge export approach has been superseded. The \`labs/\` directory structure and import strategy has evolved beyond the bridge pattern described here. Collection errors and import issues are now tracked in bug_report.md (ISSUE-006 through ISSUE-025) and TEST_ASSIGNMENT_REPORT.md (TEST-008)."
done

# Close old codex tasks
for issue in 810 809 808 807; do
  gh issue close $issue --comment "Closing as completed or superseded by newer lint cleanup issues (#945, #946, #851, #852, etc). Current linting work is tracked in [CODEX] issues with specific error codes and violation counts."
done

# Close collection errors duplicate
gh issue close 364 --comment "Closing as duplicate. Collection errors are now comprehensively tracked in TEST_ASSIGNMENT_REPORT.md (TEST-008: Fix Collection Errors - CRITICAL priority, 223 errors → 0 target)."

# Close E402 refactor slices (duplicates of #945)
gh issue close 389 --comment "Closing as duplicate of #945 (Phase 2: Import Organization - E402, UP035)."
gh issue close 388 --comment "Closing as duplicate of #945 (Phase 2: Import Organization - E402, UP035)."
```

### Step 2: Assign @codex to Valid Lint Issues

Priority order for @codex:
1. **#852** (P0 CRITICAL) - F821 undefined names (144 violations)
2. **#860** (P1) - RUF012 mutable class defaults (119 violations)
3. **#851** (P1) - E402 import ordering (189 violations)
4. **#946** (HIGH) - Quick wins small errors (42 violations)
5. **#945** (HIGH) - Phase 2 import org (2,449 violations)
6. **#861** (P2) - RUF006 async comprehension (80 violations)
7. **#850** (P3) - SIM102 nested ifs (247 violations)

### Step 3: Review TODO Migration Issues

Manually review each TODO issue to determine if:
- Solved (close)
- Duplicate of bug_report.md issue (close, reference bug_report.md)
- Still valid (update with @codex assignment or keep open)

### Step 4: Evaluate Other Issues

Check status of each:
- #859, #399, #360, #494, #492, #490, #436

---

## 📊 Expected Outcome

**Before**:
- 68 open issues (noisy, hard to track priorities)

**After**:
- ~25 open issues (clean, actionable)
- All CODEX lint issues have @codex assignments with full instructions
- Obsolete bridge gap campaign closed
- Clear priorities and next actions

---

## 📝 Notes

- All lint issues should reference ruff.toml configuration
- T4 commit message standards are mandatory
- Lane boundaries must be respected (see CLAUDE.md)
- All fixes must pass smoke tests before commit
- Close issues promptly when completed

---

**Next Action**: Execute Step 1 (bulk close obsolete issues), then assign @codex to lint issues in priority order.
