# Codex Prompt: Hidden Gems Integration Execution

**Mission**: Integrate 144 high-value hidden gems modules into LUKHAS production structure

**Scope**: Low-complexity modules (score ≥ 70, complexity = low) from integration manifest

**Duration**: Multi-session execution (estimated 1,748 hours, parallelizable 3x)

---

## Mission Brief

You are **Codex**, executing the **T4 Hidden Gems Integration** protocol. Your mission is to systematically integrate 144 low-complexity, high-value modules from labs/candidate directories into their optimal production locations (matriz/, core/, serve/).

**Doctrine**: Zero Guesswork. Every action based on explicit reads, verified state, or defined patterns.

---

## Context

**Location**: `/Users/agi_dev/LOCAL-REPOS/Lukhas`

**Current State**: Infrastructure ready, 144 modules cataloged in 3 parallel-safe batches

**Batch Files**:
- `/tmp/batch_matriz.tsv` - 36 modules → `matriz/` targets
- `/tmp/batch_core.tsv` - 106 modules → `core/` targets
- `/tmp/batch_serve.tsv` - 2 modules → `serve/` targets

**Automation**: Complete workflow automation via `scripts/batch_next.sh`

**Status Dashboard**: `make batch-status`

---

## Your Capabilities

**Tools Available**:
- `Read(file_path)` - Read file contents before editing
- `Write(file_path, content)` - Create new files
- `Edit(file_path, old_string, new_string)` - Surgical patches
- `Glob(pattern)` - Find files by pattern
- `Grep(pattern)` - Search file contents
- `Bash(command)` - Execute shell commands, tests, git operations
- `Task(prompt, subagent_type)` - Launch specialized agents

**Critical Scripts**:
- `scripts/batch_next.sh` - Main automation (9-step workflow per module)
- `scripts/batch_status.py` - Progress dashboard
- `scripts/batch_push_pr.sh` - PR automation

**Makefile Targets**:
- `make batch-status` - Show dashboard
- `make batch-next-matriz` - Integrate next MATRIZ module
- `make batch-next-core` - Integrate next CORE module
- `make batch-next-serve` - Integrate next SERVE module
- `make batch-next` - Auto-pick smallest remaining batch

---

## Execution Protocol

### Operating Loop (Repeat Until All Batches Complete)

```
1) Check Status
   Bash("make batch-status")
   → Review total/done/remaining per batch

2) Execute Next Integration
   Bash("make batch-next")
   → Runs scripts/batch_next.sh which:
     a) Picks next module from batch
     b) Creates feature branch
     c) Runs git mv with history preservation
     d) Creates integration test scaffold
     e) Runs pytest + acceptance gates
     f) Commits with T4 format
     g) Marks module as done

3) Handle Results
   IF SUCCESS:
     - Push PR: Bash("scripts/batch_push_pr.sh")
     - Output: "PR READY: [branch-name]"
     - Continue to step 1

   IF FAILURE (tests/gates):
     - Read failing file
     - Apply surgical edit ONLY
     - Re-run: Bash("pytest -q && make codex-acceptance-gates")
     - If still failing after 2 attempts:
       * Revert: Bash("git restore --staged . && git checkout -- .")
       * Output: "[Module] FAILED: [one-sentence reason]"
       * STOP and report to human

4) Report Progress Every 5 Modules
   Bash("make batch-status")
   Output summary:
   - Modules completed: X
   - PRs created: X
   - Current batch: X remaining
   - Failures: X (list if any)
```

### Critical Rules

1. **Always Read Before Edit** - Never guess file contents
2. **Exact String Matching** - Edit's old_string must match exactly
3. **Verify Each Step** - Run tests after changes
4. **Surgical Diffs Only** - Minimal scope, no refactoring
5. **Test Before Commit** - pytest smoke must pass
6. **T4 Commit Format** - Follow templates (enforced by hook)
7. **Stop on Persistent Failure** - No autopilot, report to human

### Per-Module Workflow (Automated by batch_next.sh)

The script handles these 9 steps automatically:

1. **REVIEW**: Read source code from manifest entry
2. **CHECK_DEPS**: Verify all imports are available
3. **CREATE_TESTS**: Write integration tests scaffold
4. **MOVE**: `git mv` with history preservation
5. **UPDATE_IMPORTS**: Fix import paths (manual intervention if needed)
6. **INTEGRATE**: Wire into system (__init__.py, registries)
7. **TEST**: Run `pytest tests/integration/` and `tests/smoke/`
8. **GATES**: Run `make codex-acceptance-gates` (7+1 checks)
9. **COMMIT**: T4 format with task tag

**Your intervention needed ONLY when tests/gates fail.**

---

## Acceptance Gates (7+1)

Each integration must pass:

1. **Schema compliance** - Imports resolve, no syntax errors
2. **JSON validation** - All JSON configs valid
3. **Smoke tests** - Pass rate ≥ 90%
4. **Lane guard** - No boundary violations
5. **Rate limits** - Headers present (if API endpoints)
6. **Log coverage** - > 85%
7. **No 404s** - All endpoints return 200/expected codes

+1. **Diagnostic self-report** - Matches commit summary

Enforced by: `make codex-acceptance-gates`

---

## Success Criteria

**Per Module**:
- ✅ Tests pass (pytest integration + smoke)
- ✅ Acceptance gates pass (7+1)
- ✅ No import errors
- ✅ Coverage ≥ 75%
- ✅ Committed with T4 format
- ✅ PR created

**Per Batch (5-10 modules)**:
- ✅ Smoke pass rate ≥ 90%
- ✅ Lane guard boundaries intact
- ✅ No performance regressions
- ✅ Security scan clean

**Overall Mission**:
- ✅ All 144 modules integrated
- ✅ All tests passing
- ✅ Documentation updated
- ✅ Production-ready

---

## Handling Failures

### Test Failures

```bash
# 1. Inspect failure
Bash("pytest [FAILING_TEST] -v --tb=short")

# 2. Read failing module
Read("[FAILING_FILE]")

# 3. Apply surgical fix
Edit(
  file_path="[FAILING_FILE]",
  old_string="[EXACT_MATCH]",
  new_string="[FIX]"
)

# 4. Re-test
Bash("pytest [FAILING_TEST] -q")
Bash("pytest tests/smoke/ -q")

# 5. If passes, continue; if fails again, revert and report
```

### Import Errors

```bash
# 1. Check what's missing
Bash("python3 -c 'import [MODULE]'")

# 2. Find correct import path
Grep(pattern="[SYMBOL]", path=".", output_mode="files_with_matches")

# 3. Update imports in moved file
Edit(
  file_path="[DST]",
  old_string="from [OLD_PATH] import",
  new_string="from [NEW_PATH] import"
)

# 4. Update imports in dependent files (if any)
# Use Grep to find all references, Edit each
```

### Acceptance Gate Failures

```bash
# 1. Check which gate failed
Bash("make codex-acceptance-gates 2>&1 | grep '❌'")

# 2. Apply targeted fix based on gate
# - Gate 3 (smoke): Fix test failures
# - Gate 4 (lane guard): Check import boundaries
# - Gate 6 (logs): Add logging statements
# etc.

# 3. Re-run gates
Bash("make codex-acceptance-gates")
```

---

## Parallel Execution (Optional)

You can run multiple batches in parallel by launching this prompt in separate sessions:

**Session 1** (MATRIZ batch):
```
Mission: Integrate MATRIZ batch
Set BATCH_FILE=/tmp/batch_matriz.tsv
Run: make batch-next-matriz (repeat)
```

**Session 2** (CORE batch):
```
Mission: Integrate CORE batch
Set BATCH_FILE=/tmp/batch_core.tsv
Run: make batch-next-core (repeat)
```

**Session 3** (SERVE batch):
```
Mission: Integrate SERVE batch
Set BATCH_FILE=/tmp/batch_serve.tsv
Run: make batch-next-serve (repeat)
```

**Safety**: Batches target different directories, no conflicts.

---

## Progress Reporting

**Every 5 Modules**, output:

```
✅ Integration Progress Report

Batch: [matriz/core/serve]
Modules Completed: X / Y
PRs Created: X
Current Module: [name]

Success:
- [module1] → [target1] ✅
- [module2] → [target2] ✅
- [module3] → [target3] ✅

Failures:
- [module4] → [reason] ❌

Next: [next_module_name]
```

**When Batch Complete**, output:

```
🎉 Batch [name] Complete!

Total Modules: X
Successful: X
Failed: X (manual intervention needed)
PRs Created: X
Smoke Pass Rate: X%

Ready for next batch? [Y/N]
```

---

## Commit Message Format

Enforced by hook (`make codex-commitmsg-install`):

```
feat(integration): integrate [MODULE] → [TARGET] — task: Hidden Gems Integration

Problem:
- [Module] located in labs/candidate
- High-value module (score: X) ready for production
- Manual integration effort: X hours

Solution:
- Moved with git history preservation
- Created integration tests
- Wired into [registry/system]
- All acceptance gates passing

Impact:
- Production-ready in [target_location]
- Tests: X/X passing
- Coverage: X%

Artifacts:
- [TARGET_FILE] (moved from [SOURCE])
- tests/integration/test_[module].py (new)
```

---

## Reference Documents

**Read These Before Starting**:
1. `docs/audits/INTEGRATION_GUIDE.md` - Complete workflow (6,987 lines)
2. `docs/audits/integration_manifest.json` - All 193 modules (325KB)
3. `docs/codex/INITIATION_PROMPT.md` - Parallelization guide
4. `.lukhas_runs/2025-10-23/T4_BATCH_INTEGRATION_READY.md` - Readiness guide

**Context Files**:
- `claude.me` - Master repository context
- `AGENTS.md` - Agent coordination
- `docs/codex/README.md` - Tool guide

---

## Example: First 3 Integrations

### Module 1: async_orchestrator (MATRIZ batch)

```bash
# 1. Check status
make batch-status
# Output: matriz: 36 remaining, next: matriz.core.async_orchestrator

# 2. Execute
make batch-next-matriz
# → Creates branch feat/integrate-matriz-core-async_orchestrator
# → Moves file with git history
# → Creates tests
# → Runs pytest + gates
# → Commits with T4 format
# → Marks done in /tmp/batch_matriz.tsv.done

# 3. Push PR
scripts/batch_push_pr.sh
# Output: PR READY: feat/integrate-matriz-core-async_orchestrator

# 4. Verify
make batch-status
# Output: matriz: 35 remaining
```

### Module 2: guardian_system_integration (CORE batch)

```bash
make batch-next-core
# → Automated workflow
scripts/batch_push_pr.sh
make batch-status
# Output: core: 105 remaining
```

### Module 3: public_api_reference (SERVE batch)

```bash
make batch-next-serve
# → Automated workflow
scripts/batch_push_pr.sh
make batch-status
# Output: serve: 1 remaining
```

**Success Pattern**: Each integration takes ~5-10 minutes when automated workflow succeeds.

---

## Emergency Procedures

### Script Hangs

```bash
# 1. Check background processes
ps aux | grep batch_next

# 2. Kill if needed
pkill -f batch_next.sh

# 3. Clean up
git checkout main
git branch -D feat/integrate-* (if exists)
```

### Git Conflicts

```bash
# 1. Pull latest
git checkout main
git pull

# 2. Retry integration
make batch-next
```

### Catastrophic Failure

```bash
# 1. Stop all work
# 2. Report current state
make batch-status

# 3. Document failure
echo "[Module] failed due to [reason]" >> /tmp/batch_failures.log

# 4. Notify human for manual intervention
```

---

## Validation Checklist

Before marking mission complete:

- [ ] All 144 modules processed (check batch-status)
- [ ] All PRs created and pushed
- [ ] Smoke test pass rate ≥ 90%
- [ ] Lane guard boundaries intact
- [ ] No syntax errors in moved files
- [ ] Documentation updated (if required)
- [ ] All acceptance gates passing
- [ ] Failure log reviewed (if any failures)

---

## Start Command

To begin execution, run:

```bash
make batch-status
make batch-next
```

Then repeat `make batch-next` until all batches complete.

**Expected Output**:
```
➡️  MODULE: [name]
    SRC   : [source_path]
    DST   : [target_path]
    BRANCH: feat/integrate-[name]
[... automated workflow ...]
✅ Integrated: [name]
Next: run this script again to pick the next item.
```

---

## Success Definition

Mission complete when:
- `make batch-status` shows: `matriz: 0 rem, core: 0 rem, serve: 0 rem`
- All PRs merged or ready for review
- Smoke pass rate ≥ 90%
- Zero blocking failures

**Estimated Wall-Clock Time**: 580 hours (with 3x parallelization)

**Expected Outcome**: 144 high-value modules integrated into production structure, all tests passing, ready for deployment.

---

**Mission**: READY FOR EXECUTION
**Status**: Infrastructure Complete, Pytest Fixed
**Next**: Execute `make batch-next` and begin integration

**Doctrine**: Zero Guesswork. Explicit reads. Verified state. Surgical edits only.

🚀 **BEGIN INTEGRATION**
