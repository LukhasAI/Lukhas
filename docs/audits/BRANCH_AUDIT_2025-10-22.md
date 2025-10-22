# LUKHAS Branch Audit Report
Date: 2025-10-22

## Summary Statistics
- **Total Branches**: 410 (198 local, 212 remote)
- **Open PRs**: 10 (all dependabot)
- **Main branch**: 1333e0ffa

## Category Breakdown
- codex: 83 branches
- feat/feature: 96 branches
- chore: 31 branches
- fix: 26 branches
- refactor: 22 branches
- dependabot: 12 branches (10 active PRs)
- jules: 11 branches
- Other: ~140 branches

---

## 🔴 HIGH PRIORITY - Recently Active Branches Ahead of Main

### Recent Refactor Work (Last 7 days)
These branches have E402 import fixes and should be reviewed for merge or abandonment:

1. **refactor/e402-simple-batch-8** (+1 commits, -106 behind)
   - Last: 4 days ago - "refactor: fix E402 violations in 3 scripts/tools files (batch 8)"

2. **refactor/e402-simple-batch-7** (+1 commits, -107 behind)
   - Last: 4 days ago - "refactor: fix E402 violations in 3 core/ files (batch 7)"

3. **refactor/e402-simple-batch-6** (+1 commits, -108 behind)
   - Last: 4 days ago - "refactor: fix E402 violations and enhance audit documentation"

4. **refactor/e402-simple-batch-5** (+1 commits, -109 behind)
   - Last: 4 days ago - "refactor: fix E402 violations in 3 qi/ files (batch 5)"

5. **refactor/e402-simple-batch-4** (+1 commits, -110 behind)
   - Last: 4 days ago - "refactor: fix E402 violations in 3 files (batch 4)"

6. **refactor/e402-simple-batch-3** (+1 commits, -111 behind)
   - Last: 4 days ago - "refactor: fix E402 violations in 5 files (batch 3)"

7. **refactor/e402-simple-batch-2** (+1 commits, -114 behind)
   - Last: 5 days ago - "refactor: fix E402 violations in 5 test files (batch 2)"

8. **refactor/e402-simple-batch** (+1 commits, -114 behind)
   - Last: 7 days ago - "refactor: fix E402 violations in 4 files (simple batch)"

9. **refactor/e402-production-final-batch** (+8 commits, -99 behind)
   - Last: 4 days ago - "refactor(hygiene): fix E402 in 6 brain/orchestration files (batch 6)"

### Operations Work (Last 9 days)
10. **ops/copilot/rc-soak-pack** (+1 commits, -130 behind)
    - Last: 8 days ago - "ops: RC soak automation + daily health artifacts"

11. **ops/cc/ga-guard-pack** (remote) (+2 commits, -163 behind)
    - Last: 9 days ago - "fix(ga): align budget messaging, retention, and add version tracking"

### Documentation Work (Last 2 days)
12. **feat/jules-docs-pass-hotfix-2-1** (remote) (+1 commits, -15 behind)
    - Last: 2 days ago - "docs(seed): add module docstrings for 347 scripts"

### Testing Consolidation (Last 7 days)
13. **test/golden-fixtures-consolidation** (remote) (+3 commits, -115 behind)
    - Last: 7 days ago - "Merge main into test/golden-fixtures-consolidation - include PR #414"

---

## 🟡 MEDIUM PRIORITY - Significant Work, Needs Decision

### Major Refactors
14. **refactor/lukhas-flat-matriz** (+1 commits, -508 behind)
    - Last: 3 weeks ago - "refactor(lukhas): complete flat-root consolidation with import rewrites"
    - **Decision needed**: Major structural change, likely superseded

15. **feat/t4-phase2-consciousness-drift** (remote) (+9 commits, -614 behind)
    - Last: 4 weeks ago - "fix(matriz): restore proper MATRIZ init after merge resolution"
    - **Decision needed**: Significant consciousness work

### Jules Work Branches (4-6 weeks old)
16. **jules/SC003-consolidate-secret-scanning** (remote) (+2 commits, -633 behind)
17. **jules-10-mcp-server-tests** (remote) (+2 commits, -1132 behind)
18. **jules-07-utc-legacy-glue** (remote) (+2 commits, -1073 behind)
19. **jules-06-pqc-signer-triage** (remote) (+2 commits, -1074 behind)
20. **jules-04-identity-consolidation** (remote) (+2 commits, -1072 behind)

---

## 🟢 SAFE TO DELETE - Stale Branches (>4 weeks, far behind)

### Ancient Jules Branches (7-8 weeks old, >1400 commits behind)
- test/pr-100-101
- rebase/jules-04-governance-ethics-tests
- pr-363-fresh / pr-363
- pr-210
- pr-164-merge
- pr-112-fixes / pr-111-fixes
- merge/pr-100-101-into-main
- merge-check-pr-210
- jules/webauthn-mypy-fixes
- jules/fix-mypy-errors-partial
- jules/fix-mypy-errors-and-tests
- jules/fix-ci-failures
- jules-syntax-fixes
- jules-2-dashboard-fixes
- jules-04-governance-ethics-tests
- jules-02-trace-audit-chain

### Old Feature Branches (8 weeks old)
- integration/identity-webauthn
- nias-transcendence (remote)
- improve-test-coverage (remote)
- fix/stigg-provider-setup (remote)
- feature/improve-ci-cd-pipeline (remote)

### Temporary/Test Branches
- _tmp_merge_54_53280
- _tmp_merge_80_53879
- _tmp_merge_81_53703
- backup-before-branch-merge-20251018
- backup-before-main-2-merge
- backup/main-before-merge
- local-main

### Old Infrastructure Branches
- infra/matriz-ci-deps
- infra/python-lint-ci
- infra/logging-guard
- infra/lint-tools-phase2
- infra/lint-serve-phase2
- infra/lint-lukhas-phase2
- infra/lint-global

---

## 📊 Codex Branches (83 branches)

Need separate analysis - appear to be automated/generated branches.
Recommendation: Review codex branch naming and retention policy.

---

## ✅ ACTIONS RECOMMENDED

### Immediate (This Week)
1. **Merge or close E402 refactor branches** (9 branches)
   - These are small, focused fixes
   - Either merge all as batch or close if work is stale

2. **Review and decide on ops branches** (2 branches)
   - ops/copilot/rc-soak-pack
   - ops/cc/ga-guard-pack

3. **Merge or close recent docs branch**
   - feat/jules-docs-pass-hotfix-2-1

### Short Term (Next 2 Weeks)
4. **Delete ancient Jules branches** (~20 branches, 7-8 weeks old, >1400 commits behind)
   - Work is clearly superseded by recent Jules PRs that were already merged

5. **Delete temporary/backup branches** (~10 branches)
   - _tmp_merge_*
   - backup-*

6. **Review and decide on major refactors**
   - refactor/lukhas-flat-matriz
   - feat/t4-phase2-consciousness-drift

### Long Term (Next Month)
7. **Implement branch retention policy**
   - Auto-delete branches >60 days old with no open PR
   - Keep codex branches for archival (separate retention)
   - Archive significant feature work before deletion

8. **Audit codex branches** (83 branches)
   - Understand purpose
   - Set retention policy
   - Consider consolidation

---

## 🎯 Quick Win: Delete These Now (Low Risk)

### Local Branches (15 branches, zero risk)
```bash
# Temporary branches
git branch -D _tmp_merge_54_53280 _tmp_merge_80_53879 _tmp_merge_81_53703

# Backup branches
git branch -D backup-before-branch-merge-20251018 backup-before-main-2-merge backup/main-before-merge local-main

# Old PR test branches (work merged or abandoned)
git branch -D test/pr-100-101 pr-363-fresh pr-363 pr-210 pr-164-merge pr-112-fixes pr-111-fixes

# Old merge branches
git branch -D merge/pr-100-101-into-main merge-check-pr-210

# Ancient infrastructure work (superseded)
git branch -D infra/python-lint-ci infra/lint-tools-phase2 infra/lint-serve-phase2 infra/lint-lukhaus-phase2
```

This would immediately clean up 15 local branches with zero risk.

### Remote Branches (Consider for deletion after local cleanup)
```bash
# Delete remote branches after confirming local cleanup successful
git push origin --delete nias-transcendence
git push origin --delete improve-test-coverage
git push origin --delete fix/stigg-provider-setup
git push origin --delete feature/improve-ci-cd-pipeline
# ... etc
```
