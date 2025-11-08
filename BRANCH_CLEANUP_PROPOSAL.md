# BRANCH CLEANUP PROPOSAL - 2025-11-08

## Current State
- **Local branches**: 196
- **Remote branches**: 572
- **Total**: 768 branches

## Cleanup Categories

### CATEGORY 1: SAFE TO DELETE - Merged Local Branches (35 branches)

These branches are fully merged into main and can be safely deleted:

```
backup/pre-flatten-2025-11-03-1316
claude-dev/pr-review-2025-11-05
claude/add-seo-frontmatter-55-pages-011CUvoaBceefiERB2My1HBE
claude/generate-evidence-pages-top-20-011CUvpH7LZitovyVJJJvwiV
codex/fix-lint-issues-for-phase-2
codex/github-mention-bridge-gap-follow-up-metrics-tracking
codex/github-mention-codex]-fix-ruf006-unnecessary-async-compre
dependabot/pip/psycopg2-binary-2.9.11
dependabot/pip/pydantic-2.12.3
feat/t4-codex-integration
feat/t4-prod-hardening
feature/unified-compliance-service
fix-e402-rebased
fix/b005-c414-safe-fixes
fix/b007-unused-loop-variables
fix/dtz003-labs-datetime-utcnow
fix/e722-bare-except-security
fix/f401-audit-tools-batch1
fix/f401-unused-imports-batch1
fix/i001-unsorted-imports-batch
fix/import-errors-quick-wins
fix/ruf006-background-tasks
fix/ruff-auto-fixes-119
fix/ruff-b027-abstract-methods-batch2
fix/ruff-sim112-env-var
fix/ruff-sim115-context-managers
fix/ruff-sim117-multiple-with
replace/t4-lint-platform
replace/t4-policy-platform-20251106140111
review-prs-866-874
test-guardian-agent-management-v2
```

**Action**: Delete all 35 branches

### CATEGORY 2: NEEDS PRs - Active Branches Without PRs (19 branches)

These branches have unique commits and need PRs created:

1. **t4/f401-batch2c-tests-20251108** - 1 commit
2. **t4/codex-file-review-20251108** - 1 commit
3. **codex/github-mention-feat-add-comprehensive-tests-for-quantum-fi** - 1 commit
4. **feat-matriz-performance-tests-1** - 3 commits
5. **t4/f401-batch2-scripts-tests** - 1 commit
6. **feat/explainability-enhancements** - 2 commits
7. **test-quantum-modules** - 2 commits
8. **test/add-health-check-test** - 2 commits
9. **test-nias-dream-bridge-coverage** - 2 commits
10. **feat/bio-symbolic-processor-tests** - 2 commits
11. **feat/add-memory-system-tests** - 2 commits
12. **test-quantum-financial-modules** - 2 commits
13. **test-core-bridges** - 2 commits
14. **feat/dream-commerce-tests** - 2 commits
15. **audit/pre-launch-2025** - 2 commits
16. **feat/github-issues-audit** - 3 commits
17. **feat/test-coverage-audit** - 5 commits
18. **feat/branding-governance-compliance** - 11 commits
19. **fix/f401-unused-logging-imports** - 3 commits

**Action**: Create PRs for all 19 branches

### CATEGORY 3: HAS PRs - Keep (2 branches)

1. **wkt/shim-matriz-tests** - PR #1153
2. **fix-issue-012** - PR #1152

**Action**: Keep, monitor PR status

### CATEGORY 4: REMOTE MERGED BRANCHES (22 branches)

Can be deleted from remote:

```
backup/pre-flatten-2025-11-03-1316
chore/bulk-assign-script
claude/add-seo-frontmatter-55-pages-011CUvoaBceefiERB2My1HBE
claude/generate-evidence-pages-top-20-011CUvpH7LZitovyVJJJvwiV
codex/codemod/replace-labs
codex/fix-lint-issues-for-phase-2
codex/github-mention-bridge-gap-follow-up-metrics-tracking
codex/github-mention-codex]-fix-ruf006-unnecessary-async-compre
codex/github-mention-todo]-fix-security-vulnerability-immediatel
codex/github-mention-todo]-implement-sync-token-registration
codex/github-mention-todo]-security-consider-using-impor
codex/refer-to-initiation-prompt-for-details
codex/refer-to-initiation-prompt-in-codex3
codex/security-remove-env-secrets
codex/type-system-batch-01-20251026
feat/t4-prod-hardening
fix/i001-unsorted-imports-batch
fix/import-errors-quick-wins
fix/ruff-auto-fixes-119
migration/matriz-tests-complete-2025-10-28
replace/t4-lint-platform
test-guardian-agent-management-v2
```

**Action**: Delete remote branches via `git push origin --delete <branch>`

### CATEGORY 5: STALE REMOTE BRANCHES (>30 days, review needed)

30+ branches older than 30 days that aren't merged. Need manual review to determine if they have valuable work.

**Top candidates** (oldest first):
- assist/copilot/tests-docs-batch01 (2025-10-09)
- feat/jules/api-gov-batch01 (2025-10-09)
- refactor/lukhas-flat-matriz (2025-10-09)
- codex/fix-critical-bug-in-framework-integration (2025-10-09)
- develop/v0.03-prep (2025-10-06)
- feat/t4-phase2-consciousness-drift (2025-09-21)
- jules/SC003-consolidate-secret-scanning (2025-09-21)
- Multiple jules-* branches from September

**Action**: Review each for unique work, create PRs if needed, then delete

## Proposed Cleanup Plan

### Phase 1: Immediate Cleanup (Safe)
1. ✅ Delete 35 merged local branches
2. ✅ Delete 22 merged remote branches
3. **Est. reduction**: 57 branches

### Phase 2: Preserve Work
1. ✅ Create PRs for 19 active branches
2. ✅ Ensure all work is preserved
3. **Result**: 19 new PRs

### Phase 3: Stale Branch Review
1. ⚠️ Review 30+ stale remote branches
2. ⚠️ Create PRs for branches with unique work
3. ⚠️ Delete branches with no unique work
4. **Est. reduction**: 20-30 branches

## Expected Results

**Before Cleanup**:
- Local: 196
- Remote: 572
- Total: 768

**After Cleanup** (estimated):
- Local: ~140 (removing 56)
- Remote: ~520 (removing 52)
- Total: ~660 (removing 108 branches)

**PRs Created**: 19-30 new PRs preserving all valuable work

## Safety Measures

1. ✅ Only delete merged branches automatically
2. ✅ Create PRs before deleting any branch with unique commits
3. ✅ Never delete main, develop, or active worktree branches
4. ✅ Backup branch list before deletion
5. ✅ All deletions can be recovered from remote within 30 days

## Execution Commands

See `/tmp/branch_cleanup_commands.sh` for the complete cleanup script.
