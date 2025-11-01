---
status: action-plan
type: cleanup
owner: codex
updated: 2025-11-01
---

# Worktree & Branch Cleanup Plan (2025-11-01)

## Executive Summary

**Current State**:
- **Active Worktrees**: 5 (1 main + 4 auxiliary)
- **Local Branches**: 118 branches
- **Open PRs**: 17 PRs
- **Uncommitted Changes**: 2 locations (main repo + 1 worktree)

**Cleanup Goal**: Reduce to essential worktrees/branches, commit or discard uncommitted work, consolidate open PRs.

---

## 1. Worktree Audit

### Active Worktrees

| Path | Branch | Status | Uncommitted Files | Action |
|------|--------|--------|-------------------|--------|
| `/Users/agi_dev/LOCAL-REPOS/Lukhas` | `main` | ✅ Active | `.claude/settings.local.json` (1 line) | Keep, commit settings |
| `/Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/codex-replace-labs` | `codex/codemod/replace-labs` | ✅ Clean | None | Keep (active codemod work) |
| `/Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/main` | `main-wkt` | ⚠️ Duplicate | None | **REMOVE** (duplicate of main) |
| `/Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main` | `feat/fix-lane-violation-MATRIZ-collective-lazy` | ⚠️ Stale | 12 experimental artifacts + 1 import reorder | **CLEAN** then remove |
| `/Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/wkt-shim` | `wkt/shim-matriz-tests` | ✅ Clean | None | Keep (active shim work) |

### Uncommitted Changes Detail

#### Main Repo: `.claude/settings.local.json`
```diff
+ "Bash(git worktree:*)"
```
**Analysis**: Adding git worktree to bypass permissions. Safe to commit.

#### sync-origin-main Worktree
**Modified**:
- `TODO/scripts/categorize_todos.py` (import reorder by linter)

**Untracked** (12 files in `artifacts/`):
- Import linter config files (9 .toml files)
- Import linter logs (various .log files)
- Reports directory

**Analysis**: These are experimental import-linter artifacts from October 28. No production value. Should be discarded.

---

## 2. Branch Classification

### By Category

**Active Work Branches (Keep)**: 8
- `codex/codemod/replace-labs` - Active codemod PR work
- `wkt/shim-matriz-tests` - Active consciousness shim work
- `task/lazy-load-gpt-colony-agi_dev` - PR #711 (valuable lazy loading)
- `task/add-openai-provider-protocol` - Recently merged
- `task/lazy-init-core-ethics` - Recently merged
- `task/lazy-init-core-collective` - Recently merged
- `main`, `main-wkt` - Main branches (consolidate to one)

**Codex TODO Branches (17 with open PRs)**:
- See PR list in Section 3

**Stale Feature Branches (No PRs, Old)**: ~60+
- `feat/fix-lane-violation-MATRIZ-*` (multiple variants)
- `codex/github-mention-todo]-*` (many TODO-based branches without PRs)
- `codex/implement-*`, `codex/find-*`, etc. (completed or abandoned)
- `copilot/vscode*` (temporary IDE branches)
- `migration/matriz-*` (completed migrations from Oct 26-28)
- `chore/*` (completed maintenance)

**Merge-Related Branches (Completed)**: ~20
- `codex-rebase-pr-*` (rebase branches)
- `integration/*` (integration tests)

---

## 3. Open PR Analysis (17 PRs)

All 17 open PRs are `codex/github-mention-todo]-*` branches addressing TODO comments.

### PR Categories

**Identity/Auth (7 PRs)**:
- #759 - verify-attestation, store-credential (WebAuthn registration)
- #757 - implement-credential-lookup (passkey lookup)
- #756 - verify-assertion, check-credential (WebAuthn assertions)
- #748 - .webauthn.webauthncredential (restore base import)
- #662 - .token_introspection.introspec (restore ΛiD integration)

**Security/QI (6 PRs)**:
- #755 - securitymesh (security mesh orchestration)
- #754 - privacystatement-6u7lxi (privacy statement type)
- #753 - multijurisdictioncomplianceeng (compliance engine)
- #751 - create_encryption_manager-v1ny03 (test encryption)
- #750 - encryptionalgorithm (lightweight encryption)
- #749 - create_encryption_manager-jlioxf (test encryption instantiation)
- #664 - create_encryption_manager-bt65fh (simulated encryption)
- #658 - create_security_monitor (security monitor factory)

**Other (4 PRs)**:
- #752 - message-vblupm (docs clarification)
- #713 - privacystatement (data class implementation)
- #711 - task/lazy-load-gpt-colony-agi_dev (lazy loading - **VALUABLE**)
- #667 - compliancereport-iqqhnx (compliance reporting)

### PR Recommendations

**Merge Now** (1 PR):
- #711 - `task/lazy-load-gpt-colony-agi_dev` - Aligns with our T4 lazy loading initiative

**Review for Merge** (7 PRs - Identity/Auth cluster):
- #759, #757, #756, #748, #662 - WebAuthn/passkey infrastructure
- Consider batching these as they're related

**Close as Out of Scope** (9 PRs - Security TODOs):
- #755, #754, #753, #751, #750, #749, #664, #658, #667
- These address TODO comments that may not be immediate priorities
- Tag @codex to assess if still relevant or close

**Other**:
- #752 - Review docs clarification, likely quick merge
- #713 - Review data class implementation

---

## 4. Cleanup Action Plan

### Phase 1: Commit Uncommitted Work (15 minutes)

**Step 1.1**: Commit main repo settings change
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git add .claude/settings.local.json
git commit -m "chore(config): add git worktree to bypass permissions"
```

**Step 1.2**: Clean sync-origin-main worktree
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main
# Discard import reorder (trivial linter change)
git restore TODO/scripts/categorize_todos.py
# Remove experimental artifacts
rm -rf artifacts/
```

### Phase 2: Process Open PRs (30-60 minutes)

**Step 2.1**: Merge valuable PR
```bash
gh pr merge 711 --squash
```

**Step 2.2**: Review Identity/Auth cluster (7 PRs)
```bash
# Check if these PRs are ready to merge or need rebase
for pr in 759 757 756 748 662; do
  echo "=== PR #$pr ==="
  gh pr view $pr --json title,state,mergeable
  gh pr checks $pr
done
```

**Step 2.3**: Tag @codex on security TODOs for assessment
```bash
for pr in 755 754 753 751 750 749 664 658 667; do
  gh pr comment $pr --body "@codex Please assess if this TODO is still relevant for current milestone. If not, close this PR."
done
```

### Phase 3: Remove Stale Branches (15 minutes)

**Step 3.1**: Delete completed migration branches
```bash
git branch -D migration/matriz-core-2025-10-26
git branch -D migration/matriz-serve-2025-10-26
git branch -D migration/matriz-tests-complete-2025-10-28
git branch -D migration/matriz-tests-integration-2025-10-26
git branch -D migration/matriz-tests-unit-smoke-2025-10-26
```

**Step 3.2**: Delete completed rebase branches
```bash
for pr in 640 644 646 647 648 658 659 662 664 665 666 667 670 675 676; do
  git branch -D codex-rebase-pr-$pr 2>/dev/null || true
done
```

**Step 3.3**: Delete stale copilot branches
```bash
git branch -D copilot/vscode1760829763358
git branch -D copilot/vscode1760831732615
git branch -D copilot/vscode1760835790486
git branch -D copilot/vscode1761194418079
```

**Step 3.4**: Delete completed chore branches
```bash
git branch -D chore/consolidate-dreams-2025-10-26
git branch -D chore/merge-configs-2025-10-26
git branch -D chore/standardize-MATRIZ-2025-10-26
```

### Phase 4: Clean Up Worktrees (10 minutes)

**Step 4.1**: Remove duplicate main worktree
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git worktree remove /Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/main
git branch -D main-wkt
```

**Step 4.2**: Remove sync-origin-main worktree (after cleaning in Phase 1)
```bash
git worktree remove /Users/agi_dev/LOCAL-REPOS/Lukhas-worktrees/sync-origin-main
git branch -D feat/fix-lane-violation-MATRIZ-collective-lazy
```

**Step 4.3**: Keep active worktrees
- `codex-replace-labs` - Active codemod work
- `wkt-shim` - Active shim work

---

## 5. Expected Results

**Before**:
- 5 worktrees (2 redundant)
- 118 local branches (60+ stale)
- 17 open PRs
- 2 locations with uncommitted changes

**After**:
- 3 worktrees (main + 2 active work)
- ~50 local branches (core work only)
- ~8-10 open PRs (after merges and closures)
- 0 uncommitted changes

**Cleanup Summary**:
- ✅ Commit 1 uncommitted change (settings)
- ✅ Discard experimental artifacts
- ✅ Merge 1 valuable PR (#711)
- ✅ Tag @codex on 9 security TODO PRs
- ✅ Delete ~60 stale branches
- ✅ Remove 2 redundant worktrees

---

## 6. Maintenance Recommendations

### Ongoing Branch Hygiene

1. **Delete branches immediately after PR merge**
   ```bash
   gh pr merge <number> --delete-branch --squash
   ```

2. **Weekly branch cleanup**
   ```bash
   # List merged branches
   git branch --merged main | grep -v "^\*\|main"
   # Delete them
   git branch --merged main | grep -v "^\*\|main" | xargs -n 1 git branch -d
   ```

3. **Worktree discipline**
   - Only create worktrees for parallel work that conflicts with main workspace
   - Remove worktrees immediately when work completes
   - Max 3-4 active worktrees at once

4. **PR hygiene**
   - Close stale PRs older than 14 days without activity
   - Tag @codex or assignee for decision on stale PRs
   - Use draft PRs for experimental work

---

## 7. Command Reference

### Quick Commands

```bash
# List all worktrees
git worktree list

# Remove worktree
git worktree remove <path>

# List branches merged to main
git branch --merged main

# Delete merged branches (dry run)
git branch --merged main | grep -v "^\*\|main"

# Delete merged branches (execute)
git branch --merged main | grep -v "^\*\|main" | xargs -n 1 git branch -d

# List PRs by state
gh pr list --state open --limit 50

# Check PR merge status
gh pr view <number> --json mergeable,mergeStateStatus

# Close PR with comment
gh pr close <number> --comment "Reason for closure"
```

---

**End of Report**
