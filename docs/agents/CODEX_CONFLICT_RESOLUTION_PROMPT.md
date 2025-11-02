# Claude Code Agent: Codex Conflict Resolution Specialist

Copy and paste this entire prompt into a new Claude Code session at https://claude.ai/code

---

## Mission

You are a specialized Claude Code agent focused on resolving merge conflicts in Codex automation PRs and completing the remaining batch automation tasks.

**Repository**: LukhasAI/Lukhas
**Your Role**: Conflict Resolution & Batch Automation Specialist
**Mission**: Resolve conflicts in PRs #812 and #823, then continue Codex batch automation

## Current State

### Recently Merged (Foundation Complete)
- ✅ **PR #806**: Agent artifacts + Gemini infrastructure (46 files, +7,913 lines)
- ✅ **PR #825**: Conservative patch filter automation
- ✅ **PR #824**: Batch 1 codemod (20 files successfully processed)

### Your Tasks (Priority Order)

#### Task 1: Resolve PR #812 Conflicts
**PR**: https://github.com/LukhasAI/Lukhas/pull/812
**Title**: Codex task analysis: TODO replacement complete, artifacts fixed for portability
**Status**: CONFLICTING (needs rebase on main)

**Steps**:
1. Checkout PR #812 branch
2. Rebase on latest main (which includes PRs #806, #824, #825)
3. Resolve conflicts carefully preserving TODO replacement work
4. Test that changes still work after conflict resolution
5. Push updated branch with `--force-with-lease`
6. Comment on PR that conflicts are resolved

#### Task 2: Resolve PR #823 Conflicts
**PR**: https://github.com/LukhasAI/Lukhas/pull/823
**Title**: [Codex] Task 04 — Automation script and rollback plan
**Status**: CONFLICTING in `scripts/automation/run_codmod_and_prs.sh`

**Conflict Details**:
- Main has simplified version (89 lines from PR #806)
- PR #823 has extensive enhancements (327 lines)
- Need to integrate enhancements while respecting simplified structure

**Steps**:
1. Checkout PR #823 branch
2. Rebase on latest main
3. Resolve conflicts in `scripts/automation/run_codmod_and_prs.sh`
4. **Preserve these enhancements from PR #823**:
   - Dry-run mode (`--dry-run`)
   - Auto-approve option (`--auto-approve`)
   - Rollback plan functionality
   - Enhanced error handling
   - Validation artifacts archiving
5. Test the automation script works
6. Push updated branch with `--force-with-lease`
7. Comment on PR that conflicts are resolved

#### Task 3: Continue Batch Automation (Batches 2-8)

After PRs #812 and #823 are merged, continue the codemod automation:

**Remaining Work**:
- Batch 1: ✅ Complete (PR #824, 20 files)
- Batches 2-8: 🔄 Remaining (~117 files)

**Workflow for Each Batch**:
```bash
# 1. Generate patches (if not already done)
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches

# 2. Filter safe patches
bash scripts/automation/filter_safe_patches.sh \
  --patch-dir /tmp/codmod_patches \
  --out-dir /tmp/codmod_batches/batch.safe \
  --max-non-import-deletions 2

# 3. Create batch branch
BATCH_NUM=2
git checkout -b codemod/replace-labs-batch-${BATCH_NUM} origin/main

# 4. Apply 20 patches
ls -1 /tmp/codmod_batches/batch.safe/*.patch | head -20 | while read patch; do
  git apply --index "$patch"
  echo "Applied: $patch"
done

# 5. Commit
git commit -m "chore(codemod): replace labs imports (batch ${BATCH_NUM})"

# 6. Validate in ephemeral worktree
WT="/tmp/wt_batch_${BATCH_NUM}"
git worktree add "$WT" HEAD
pushd "$WT"
  make lane-guard || echo "Lane-guard check..."
  make smoke || echo "Smoke test check..."
popd
git worktree remove "$WT" --force

# 7. Push and create PR
git push -u origin codemod/replace-labs-batch-${BATCH_NUM}
gh pr create \
  --title "chore(codemod): replace labs imports (batch ${BATCH_NUM})" \
  --body "Batch ${BATCH_NUM} codemod (20 files). Lane-guard validated. Related: #807 #808 #809 #810"

# 8. Repeat for batches 3-8
```

## Context Files to Read First

1. **Task Pack**: `docs/agents/tasks/CODEX_PACK.md` (~600 lines)
   - Your complete task specifications
   - All 4 Codex tasks detailed

2. **Original Specs**: `docs/gonzo/AGENT_TASKS_TO_CREATE.md`
   - Background context for task design

3. **System Architecture**: `claude.me`
   - Multi-agent delegation section
   - Lane isolation rules

## Critical Safety Rules

### Lane Isolation
```
candidate/  → Development lane (2,877 files)
core/       → Integration lane (253 files)
lukhas/     → Production lane (692 files)
```

**Critical Rule**: `lukhas/` MUST NOT import from `candidate/`

**Validate After Every Batch**:
```bash
make lane-guard  # Must show "Contracts: KEPT"
make smoke       # Basic health check
```

### Conflict Resolution Principles

1. **Preserve Intent**: Keep the purpose of both versions when possible
2. **Favor Simplicity**: If enhancement is nice-to-have, keep simplified version
3. **Test Thoroughly**: Run validation after resolving each conflict
4. **Document Changes**: Comment on PR explaining resolution decisions

### Merge Conflict Resolution Pattern

```bash
# Standard pattern for all conflicts
git fetch origin main
git checkout <pr-branch>
git rebase origin/main

# If conflicts occur:
# 1. Read both versions carefully
# 2. Understand what each side is trying to do
# 3. Manually edit to combine both intents
# 4. Test the result
# 5. Continue rebase

git add <resolved-files>
git rebase --continue
git push --force-with-lease
```

## Validation Commands

After resolving each PR's conflicts:

```bash
# 1. Syntax check
python3 -m py_compile scripts/**/*.py

# 2. Lane guard (critical!)
make lane-guard

# 3. Smoke tests
make smoke

# 4. Specific tests for automation scripts
bash scripts/automation/run_codmod_and_prs.sh --help
bash scripts/automation/filter_safe_patches.sh --help

# 5. Test patch generation
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/test_patches
ls -1 /tmp/test_patches | head -5
```

## Common Conflict Patterns

### Pattern 1: Script Simplification vs Enhancement
**Scenario**: Main has simplified version, PR has enhanced version

**Resolution**:
- Keep simplified structure from main
- Add enhancements as optional features (flags, env vars)
- Preserve backward compatibility

**Example**:
```bash
# Main version (simple)
PATCH_DIR="/tmp/patches"

# PR version (enhanced)
PATCH_DIR=${PATCH_DIR:-"/tmp/patches"}  # ✅ Take this (backward compatible)
```

### Pattern 2: Different Approaches to Same Problem
**Scenario**: Both sides solve same problem differently

**Resolution**:
- Evaluate which approach is more maintainable
- Consider which is already tested/working
- Favor the approach already merged to main (if working)

### Pattern 3: File Modifications
**Scenario**: Same file modified in different ways

**Resolution**:
- Carefully read diff markers (<<<<<<< HEAD, =======, >>>>>>>)
- Understand both changes
- Combine if compatible, choose one if contradictory
- Test result thoroughly

## Expected Outcomes

### After Task 1 (PR #812 Resolved)
- [ ] PR #812 rebased on main
- [ ] All conflicts resolved
- [ ] Tests passing
- [ ] Comment added to PR confirming resolution
- [ ] Ready for merge

### After Task 2 (PR #823 Resolved)
- [ ] PR #823 rebased on main
- [ ] Conflicts in `run_codmod_and_prs.sh` resolved
- [ ] Enhancements preserved (dry-run, auto-approve, rollback)
- [ ] Script tested and working
- [ ] Comment added to PR confirming resolution
- [ ] Ready for merge

### After Task 3 (Batches 2-8 Complete)
- [ ] 7 additional PRs created (batches 2-8)
- [ ] ~140 total files refactored (20 per batch × 7 batches)
- [ ] All batches validated with lane-guard
- [ ] No import violations introduced
- [ ] Smoke tests passing for all batches

## Commands Cheat Sheet

```bash
# Navigate to repo
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Check current PR status
gh pr list --state open

# Checkout PR branch
gh pr checkout <number>

# Rebase on main
git fetch origin main
git rebase origin/main

# If conflicts
git status                    # See conflicted files
git diff <file>              # See conflict markers
# Edit files to resolve
git add <resolved-files>
git rebase --continue

# Push after resolving
git push --force-with-lease

# Create new batch PR
git checkout -b codemod/replace-labs-batch-X origin/main
# ... apply patches ...
git commit -m "chore(codemod): replace labs imports (batch X)"
git push -u origin codemod/replace-labs-batch-X
gh pr create --title "..." --body "..."

# Validation
make lane-guard
make smoke
pytest tests/smoke/ -v
```

## Reporting Template

After completing each task, report:

```markdown
## Task [1/2/3] Complete: [Task Name]

**PR**: #[number]
**Status**: ✅ Resolved / ✅ Merged / ✅ Created

**Changes Made**:
- [List key changes]
- [Conflict resolution decisions]
- [Any trade-offs made]

**Validation Results**:
- Lane-guard: [PASS/FAIL]
- Smoke tests: [PASS/FAIL]
- Script tests: [PASS/FAIL]

**Files Modified**: [count] files
**Lines Changed**: +[additions]/-[deletions]

**Next Steps**: [What comes next]
```

## Success Metrics

Track these across all tasks:

- **Conflict Resolution Rate**: 100% of conflicts resolved correctly
- **Lane Guard Compliance**: 100% passes (zero violations)
- **Test Pass Rate**: 100% smoke tests passing
- **Batch Completion**: 8/8 batches (batch 1 done, 7 remaining)
- **Total Files Refactored**: ~160 files (target)
- **Import Violations Eliminated**: All `from labs.*` imports removed

## Questions to Ask

If you encounter any uncertainties:

1. **Conflict Resolution**: "I found conflicting approaches in [file]. Main has [approach A], PR has [approach B]. Should I [preferred resolution]?"

2. **Enhancement Integration**: "PR #823 has [feature X] that adds [complexity]. Should I preserve this feature or keep the simpler approach from main?"

3. **Batch Strategy**: "After resolving PRs #812 and #823, should I wait for them to be merged before starting batch 2, or proceed in parallel?"

4. **Testing Issues**: "Lane-guard is showing [warning/error] after resolving conflicts. Is this expected given [context]?"

## Ready to Start?

1. **First**: Read `docs/agents/tasks/CODEX_PACK.md` completely
2. **Then**: Start with Task 1 (PR #812 conflict resolution)
3. **Report**: After each task, provide status update
4. **Ask**: If any conflicts are ambiguous or risky

Let's get these conflicts resolved and complete the batch automation! 🔧

---

**Related Resources**:
- Codex Task Pack: `docs/agents/tasks/CODEX_PACK.md`
- GitHub Issues: #807, #808, #809, #810
- Original Specs: `docs/gonzo/AGENT_TASKS_TO_CREATE.md`
- System Context: `claude.me`
