# Branch Status Report - 2025-10-22

**Current State**: 380 total branches (162 local + 218 remote)

## Critical Issues Found

### 1. Branches with Unpushed Commits (11 branches)

| Branch | Status | Issue | Action Needed |
|--------|--------|-------|---------------|
| `chore/claude/coordination-dashboard` | ahead 1 | Valid unpushed commit | PUSH or ABANDON |
| `chore/constellation-codemod-apply` | ahead 1 | Valid unpushed commit | PUSH or ABANDON |
| `chore/dream-alignment-hardening` | ahead ?? | **BROKEN COMMIT** (editor template in message) | FIX or DELETE |
| `chore/dream-import-hardening` | ahead ?? | **BROKEN COMMIT** (editor template in message) | FIX or DELETE |
| `ci/add-lockfiles-and-ci-guidance` | ahead 3 | Valid unpushed commits | PUSH or ABANDON |
| `codex/build-wallet-integration-placeholders` | ahead 90 | **HUGE DIVERGENCE** (90 commits!) | REVIEW or DELETE |
| `codex/resolve-circular-dependencies-in-imports` | ahead 10 | Significant unpushed work | REVIEW or DELETE |
| `feat/t4-phase4-stream` | ahead ?? | **BROKEN COMMIT** (editor template in message) | FIX or DELETE |
| `feature/unified-compliance-service` | ahead 8, behind 1 | Needs rebase + push | REBASE + PUSH or ABANDON |
| `fix/codex10/ruffB1` | ahead 1, behind 21 | Very outdated | DELETE (too far behind) |
| `fix/identity-timezone-batch-1` | ahead 1 | Valid unpushed commit | PUSH or ABANDON |

### 2. Broken Commit Messages (3 branches)

These branches have commit editor templates instead of real messages:

```
chore/dream-alignment-hardening
chore/dream-import-hardening
feat/t4-phase4-stream
```

**Issue**: Commits show "# Please enter the commit message..." - indicates aborted/incomplete commits

### 3. Severely Outdated Branches

| Branch | Status | Age |
|--------|--------|-----|
| `feat/jules-docs-completion` | behind 14 | Needs rebase |
| `feature/consent-audit` | behind 17 | Needs rebase |
| `feature/ethics-audit` | behind 17 | Needs rebase |
| `feature/guardian-resilience` | behind 17 | Needs rebase |
| `feature/perf-smoke` | behind 17 | Needs rebase |
| `fix/codex10/ruffB1` | behind 21 | **DELETE** (too far behind) |

## Recommendations

### Immediate Actions

**1. Fix Broken Commits** (3 branches)
```bash
# Option A: Fix the commits
git checkout chore/dream-alignment-hardening
git commit --amend -m "proper message"

# Option B: Delete if not valuable
git branch -D chore/dream-alignment-hardening
git push origin --delete chore/dream-alignment-hardening
```

**2. Handle Huge Divergence** (90 commits ahead!)
```bash
# Review codex/build-wallet-integration-placeholders
git log main..codex/build-wallet-integration-placeholders --oneline | wc -l
# If valuable: rebase and push
# If abandoned: delete
```

**3. Push Valid Work or Abandon**
```bash
# Branches with clean unpushed commits:
# - chore/claude/coordination-dashboard (1 commit)
# - chore/constellation-codemod-apply (1 commit)
# - ci/add-lockfiles-and-ci-guidance (3 commits)
# - fix/identity-timezone-batch-1 (1 commit)

# Either push them:
git push origin <branch-name>

# Or delete them:
git branch -D <branch-name>
git push origin --delete <branch-name>
```

**4. Delete Severely Outdated**
```bash
# These are >17-21 commits behind main:
git branch -D fix/codex10/ruffB1
git push origin --delete fix/codex10/ruffB1
```

## Previous Cleanup Recap

In our earlier session, we:
- ✅ Deleted 15 safe branches (tmp, backup, old PR)
- ✅ Deleted 9 E402 branches (work on main)
- ✅ Deleted 12 ancient Jules branches
- ✅ Merged PR #445

**But**: We only deleted **local** copies, not remote branches!

## Current Total

- **380 total branches** (vs ~410 before)
- **218 remote branches** (still need cleanup)
- **162 local branches** (includes unpushed work)
- **11 branches with unpushed commits** (need decisions)
- **3 branches with broken commits** (need fixing or deletion)

## Next Steps

### Quick Win: Delete Remote Branches We Already Deleted Locally

```bash
# Find branches that exist on remote but not locally
git fetch --prune

# Delete specific old branches from remote:
git push origin --delete <branch-name>
```

### Strategic Decision Points

1. **codex/build-wallet-integration-placeholders** (ahead 90)
   - Review: Is this valuable ongoing work?
   - If yes: Rebase onto main, resolve conflicts, push
   - If no: Delete both local and remote

2. **Broken commit branches** (3 branches)
   - Check if work is valuable with `git diff`
   - Fix commits or delete branches

3. **Outdated feature branches** (behind 14-21 commits)
   - Rebase or delete based on value

4. **Remote cleanup**
   - Delete remote branches we already cleaned locally
   - Review and delete stale remote branches

## Proposed Cleanup Strategy

### Phase 1: Fix Critical Issues (10 min)
- Fix or delete 3 broken commit branches
- Decide on codex/build-wallet-integration-placeholders
- Push or delete 7 clean branches with unpushed work

### Phase 2: Remote Cleanup (15 min)
- Delete remote branches already removed locally
- Prune obsolete remote tracking branches

### Phase 3: Outdated Branch Review (20 min)
- Review branches behind >10 commits
- Rebase valuable ones, delete rest

**Target**: Reduce from 380 → ~50-100 active branches
