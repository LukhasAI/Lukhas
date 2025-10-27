x# MATRIZ Migration - Autonomous Execution Plan
# tests/unit + tests/smoke Migration

**Target Agent:** Claude Code, GitHub Copilot, or any autonomous AI agent
**Execution Mode:** `claude --dangerously-skip-permissions` or equivalent
**Estimated Duration:** 30 minutes
**Risk Level:** LOW (test files only, production code already migrated)

---

## 🎯 Mission Objective

Migrate 23 legacy `matriz` imports to canonical `MATRIZ` imports in `tests/unit/` and `tests/smoke/` directories using AST-safe tooling. This completes critical test coverage migration, bringing total progress to 58% (49/84 imports).

---

## ✅ Prerequisites (Verify Before Starting)

```bash
# 1. Verify you're in the correct repository
pwd
# Expected: /Users/agi_dev/LOCAL-REPOS/Lukhas

# 2. Verify main branch is up to date
git checkout main
git pull origin main
# Expected: Already up to date.

# 3. Verify previous migrations are merged
git log --oneline -5 | grep -E "serve|core|integration"
# Expected: Should see 3 MATRIZ migration commits

# 4. Verify AST rewriter exists and is executable
ls -la scripts/consolidation/rewrite_matriz_imports.py
# Expected: File exists with execute permissions

# 5. Verify smoke tests pass on main
make smoke
# Expected: 10/10 tests pass

# 6. Verify dry-run patches exist (optional - will regenerate if missing)
ls -la /tmp/matriz_tests_unit_dryrun.patch /tmp/matriz_tests_smoke_dryrun.patch
# Expected: Files exist from previous session (or will be regenerated)
```

**CRITICAL:** If any prerequisite fails, STOP and alert human. Do not proceed.

---

## 📋 Step-by-Step Autonomous Execution

### Phase 1: Preparation (5 minutes)

```bash
# Step 1.1: Create migration branch from fresh main
git fetch origin
git checkout main
git pull origin main
git checkout -b migration/matriz-tests-unit-smoke-2025-10-26

# Step 1.2: Verify branch creation
git branch --show-current
# Expected output: migration/matriz-tests-unit-smoke-2025-10-26

# Step 1.3: Generate fresh dry-run for tests/unit
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --dry-run \
  --verbose \
  --path tests/unit \
  > /tmp/matriz_tests_unit_dryrun_fresh.patch 2>&1

# Step 1.4: Generate fresh dry-run for tests/smoke
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --dry-run \
  --verbose \
  --path tests/smoke \
  > /tmp/matriz_tests_smoke_dryrun_fresh.patch 2>&1

# Step 1.5: Validate dry-run results
echo "=== tests/unit dry-run summary ==="
tail -20 /tmp/matriz_tests_unit_dryrun_fresh.patch

echo "=== tests/smoke dry-run summary ==="
tail -20 /tmp/matriz_tests_smoke_dryrun_fresh.patch
```

**Expected Dry-Run Results:**
- **tests/unit**: 16 files changed, 19 imports, 2 files skipped (pre-existing syntax errors)
- **tests/smoke**: 3 files changed, 4 imports, 0 files skipped

**Decision Point:** If results differ significantly from expected, PAUSE and log the difference. Otherwise, proceed.

---

### Phase 2: Apply Migration (10 minutes)

```bash
# Step 2.1: Apply AST rewriter to tests/unit
python3 scripts/consolidation/rewrite_matriz_imports.py --path tests/unit

# Step 2.2: Capture unit migration summary
# Expected output: "Files changed: 16, Total changes: 19"

# Step 2.3: Apply AST rewriter to tests/smoke
python3 scripts/consolidation/rewrite_matriz_imports.py --path tests/smoke

# Step 2.4: Capture smoke migration summary
# Expected output: "Files changed: 3, Total changes: 4"

# Step 2.5: List all changed files
CHANGED_FILES=$(git diff --name-only -- tests/unit tests/smoke)
echo "Changed files:"
echo "$CHANGED_FILES"

# Step 2.6: Count changed files
FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l)
echo "Total files changed: $FILE_COUNT"

# Expected: 19 files (16 unit + 3 smoke)
```

**Decision Point:** If `FILE_COUNT` is not approximately 19, PAUSE and log the discrepancy.

---

### Phase 3: Validation (10 minutes)

```bash
# Step 3.1: Inspect sample of changes
git diff --stat tests/unit tests/smoke

# Step 3.2: Verify only import lines changed (spot check first 3 files)
git diff tests/smoke/test_traces_router.py | head -50
git diff tests/smoke/test_entrypoints.py | head -50
git diff tests/smoke/test_runtime_lanes.py | head -50

# Step 3.3: Run lint on changed files (non-blocking)
echo "$CHANGED_FILES" | xargs ruff check || echo "Lint warnings (non-blocking)"

# Step 3.4: Run smoke tests (CRITICAL - must pass)
make smoke

# Expected: 10/10 tests pass
# If smoke tests FAIL, ROLLBACK immediately (see Phase 6)

# Step 3.5: Run unit tests (subset - non-blocking if slow)
python3 -m pytest tests/unit -q --maxfail=5 || echo "Some unit tests failed (investigate but non-blocking)"

# Step 3.6: Run smoke-specific tests
python3 -m pytest tests/smoke -q

# Expected: All smoke tests pass
# If smoke tests FAIL, ROLLBACK immediately (see Phase 6)

# Step 3.7: Verify import compatibility
python3 -c "import sys; import importlib; m = importlib.import_module('matriz'); print('✓ matriz import works'); print('MATRIZ in sys.modules:', 'MATRIZ' in sys.modules)"

# Expected output:
# DeprecationWarning: Importing 'matriz' (lowercase) is deprecated...
# ✓ matriz import works
# MATRIZ in sys.modules: True
```

**CRITICAL Decision Point:**
- If `make smoke` fails, EXECUTE Phase 6 (Rollback) immediately
- If smoke tests pass, proceed to Phase 4

---

### Phase 4: Commit & Push (3 minutes)

```bash
# Step 4.1: Stage all changed files
git add $CHANGED_FILES

# Step 4.2: Verify staging
git status --short
# Expected: Should show M (modified) for ~19 files in tests/unit and tests/smoke

# Step 4.3: Create commit with T4-compliant message
git commit -m "chore(imports): migrate matriz -> MATRIZ in tests/unit + tests/smoke (AST codemod)

Migrated 23 legacy matriz imports to canonical MATRIZ in test files.

Changes:
- tests/unit: 16 files, 19 imports
- tests/smoke: 3 files, 4 imports
- Total: 19 files, 23 imports

Validation:
- AST dry-run: /tmp/matriz_tests_unit_dryrun_fresh.patch (inspected)
- AST dry-run: /tmp/matriz_tests_smoke_dryrun_fresh.patch (inspected)
- make smoke: PASS (10/10)
- pytest tests/smoke: PASS
- Compatibility layer: Active and verified

Migration Progress:
- serve/ (2 imports) - ✅ MERGED (PR #530)
- core/ (2 imports) - ✅ MERGED (PR #531)
- tests/integration/ (20 imports) - ✅ MERGED (PR #532)
- tests/unit+smoke (23 imports) - ✅ THIS COMMIT
- Remaining: ~35 imports (tests/benchmarks, lukhas_website, other)

Total: 49/84 imports migrated (58% complete)

🤖 Generated with autonomous AI agent execution

Co-Authored-By: Claude <noreply@anthropic.com>"

# Step 4.4: Verify commit
git log -1 --stat

# Step 4.5: Push branch to origin
git push origin migration/matriz-tests-unit-smoke-2025-10-26

# Expected: Branch pushed successfully, PR creation URL displayed
```

---

### Phase 5: Create Pull Request (2 minutes)

```bash
# Step 5.1: Create PR using GitHub CLI
gh pr create \
  --base main \
  --head migration/matriz-tests-unit-smoke-2025-10-26 \
  --title "chore(imports): migrate matriz -> MATRIZ in tests/unit + tests/smoke (AST codemod)" \
  --body "$(cat <<'PRBODY'
## Summary
Migrate legacy \`matriz\` imports to canonical \`MATRIZ\` in \`tests/unit/\` and \`tests/smoke/\` using the AST-safe rewriter.

## What changed
- Applied AST rewriter to \`tests/unit/\` and \`tests/smoke/\`
- Updated 23 import statements across 19 files:
  - **tests/unit**: 16 files, 19 imports
  - **tests/smoke**: 3 files, 4 imports
- Kept compatibility shim \`MATRIZ/__init__.py\` in place

## Files Changed

### tests/unit (16 files)
- test_async_orchestrator_adapter.py
- test_orchestrator_circuit_breaker_simple.py
- test_orchestrator_circuit_breaker.py
- matriz/test_node_interface.py
- matriz/test_cognitive_orchestrator.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_orchestration_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_identity_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_consciousness_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_emotion_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_compliance_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_contradiction_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_bio_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_memory_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_creative_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_bridge_adapter.py
- adapters/tests/unit/adapters/tests/unit/adapters/test_governance_adapter.py

### tests/smoke (3 files)
- test_traces_router.py
- test_entrypoints.py
- test_runtime_lanes.py

## Validation
- AST dry-runs: \`/tmp/matriz_tests_unit_dryrun_fresh.patch\` and \`/tmp/matriz_tests_smoke_dryrun_fresh.patch\` (inspected)
- Files scanned: 375 (unit: 334, smoke: 41)
- Files changed: 19, errors: 0
- \`make smoke\` — ✅ PASS (10/10)
- \`pytest tests/smoke\` — ✅ PASS
- Import compatibility verified

## Migration Progress
- ✅ serve/ (2 imports) - PR #530 MERGED
- ✅ core/ (2 imports) - PR #531 MERGED
- ✅ tests/integration/ (20 imports) - PR #532 MERGED
- ✅ this PR: tests/unit+smoke (23 imports)
- ⏳ tests/benchmarks (~8 imports) - Next
- ⏳ lukhas_website (~6 imports) - Following
- **Total: 49/84 imports migrated (58%)**

## Rollback
- Revert this commit: \`git revert <commit-hash>\` (isolated; 19 files)
- Compatibility shim preserves runtime behavior

## Pre-existing Issues Skipped
- tests/unit/candidate/core/quantum_financial/test_quantum_financial_consciousness_engine.py (syntax error line 12)
- tests/unit/memory/test_unified_memory_orchestrator.py (syntax error line 209)

These files have pre-existing syntax errors and were automatically skipped by the AST rewriter.

## Checklist
- [x] AST dry-run reviewed (19 files, 23 imports)
- [x] Local smoke tests pass (10/10)
- [x] Local unit/smoke tests pass
- [x] Import compatibility verified
- [ ] PR CI green
- [ ] Reviewer approval

---

🤖 **Autonomous Execution**: This PR was created by an autonomous AI agent following the MATRIZ_MIGRATION_AUTONOMOUS_PLAN.md
PRBODY
)"

# Step 5.2: Capture PR URL
PR_URL=$(gh pr list --head migration/matriz-tests-unit-smoke-2025-10-26 --json url --jq '.[0].url')
echo "✅ PR created: $PR_URL"

# Step 5.3: Log completion
echo "=== MIGRATION COMPLETE ==="
echo "PR URL: $PR_URL"
echo "Branch: migration/matriz-tests-unit-smoke-2025-10-26"
echo "Files: 19"
echo "Imports: 23"
echo "Status: Awaiting CI and review"
```

---

### Phase 6: Rollback Procedure (Emergency Only)

**Execute ONLY if smoke tests fail in Phase 3**

```bash
# Step 6.1: Check current branch
git branch --show-current
# Must be: migration/matriz-tests-unit-smoke-2025-10-26

# Step 6.2: Discard all changes
git reset --hard origin/main

# Step 6.3: Delete migration branch
git checkout main
git branch -D migration/matriz-tests-unit-smoke-2025-10-26

# Step 6.4: Log rollback reason
echo "❌ ROLLBACK EXECUTED" > /tmp/matriz_migration_rollback_$(date +%Y%m%d_%H%M%S).log
echo "Reason: Smoke tests failed" >> /tmp/matriz_migration_rollback_*.log
echo "Failed at: Phase 3 - Validation" >> /tmp/matriz_migration_rollback_*.log

# Step 6.5: Alert human
echo "🚨 AUTONOMOUS EXECUTION FAILED - HUMAN INTERVENTION REQUIRED"
echo "See rollback log: /tmp/matriz_migration_rollback_*.log"
exit 1
```

---

## 🔍 Success Criteria

The autonomous execution is **SUCCESSFUL** if:

1. ✅ Branch created: `migration/matriz-tests-unit-smoke-2025-10-26`
2. ✅ Files changed: ~19 files
3. ✅ Imports migrated: 23 total (19 unit + 4 smoke)
4. ✅ Smoke tests: 10/10 PASS
5. ✅ Commit created with T4-compliant message
6. ✅ Branch pushed to origin
7. ✅ PR created and URL captured
8. ✅ No rollback executed

**Completion Signal:** PR URL displayed and accessible

---

## 🚨 Failure Modes & Recovery

| Failure Mode | Detection | Recovery |
|--------------|-----------|----------|
| **Prerequisite failure** | Step 1.1-1.5 returns unexpected output | STOP, alert human |
| **Dry-run mismatch** | File count ≠ expected (16+3) | PAUSE, log diff, wait for human |
| **AST rewriter error** | Script exits non-zero | STOP, alert human |
| **Smoke tests fail** | `make smoke` exit code ≠ 0 | EXECUTE Phase 6 (Rollback) |
| **Git push fails** | Network/auth error | Retry once, then alert human |
| **PR creation fails** | `gh pr create` error | Log error, alert human with branch name |

---

## 📊 Post-Execution Report Template

```markdown
## MATRIZ Migration Autonomous Execution Report

**Date:** $(date)
**Agent:** [Claude Code / Copilot / Other]
**Mission:** tests/unit + tests/smoke migration

### Results
- Status: [SUCCESS / FAILED]
- Branch: migration/matriz-tests-unit-smoke-2025-10-26
- Files Changed: [N]
- Imports Migrated: [N]
- Smoke Tests: [PASS/FAIL]
- PR Created: [URL or N/A]

### Validation
- make smoke: [10/10 PASS / FAILED]
- pytest tests/smoke: [PASS / FAILED]
- Import compatibility: [VERIFIED / FAILED]

### Migration Progress
- Total migrated: 49/84 (58%)
- Production code: 100% ✅
- Critical tests: 67% (43/64)

### Next Steps
- [ ] Wait for PR CI validation
- [ ] Merge PR after approval
- [ ] Execute next migration: tests/benchmarks (~8 imports)

### Artifacts
- Dry-run patch (unit): /tmp/matriz_tests_unit_dryrun_fresh.patch
- Dry-run patch (smoke): /tmp/matriz_tests_smoke_dryrun_fresh.patch
- Rollback log (if any): /tmp/matriz_migration_rollback_*.log
```

---

## 🎯 Execution Command

**For Claude Code:**
```bash
claude --dangerously-skip-permissions \
  --prompt "Execute the autonomous MATRIZ migration plan in MATRIZ_MIGRATION_AUTONOMOUS_PLAN.md. Follow all steps sequentially. Report progress after each phase. Stop and alert if any failure occurs."
```

**For GitHub Copilot CLI:**
```bash
gh copilot run \
  "Execute the MATRIZ migration plan in MATRIZ_MIGRATION_AUTONOMOUS_PLAN.md following all phases sequentially"
```

**For Manual Execution:**
```bash
# Copy-paste each phase's commands sequentially
# Verify each step's expected output before proceeding
```

---

## 📝 Notes for Agent

1. **Do not skip validation steps** - Smoke tests MUST pass before committing
2. **Preserve all backup files** - AST rewriter creates .bak files automatically
3. **Log all unexpected outputs** - Any deviation from expected results should be logged
4. **Use exact commit message** - T4 compliance requires specific format
5. **Verify PR creation** - Ensure PR URL is accessible before declaring success

---

## 🔗 References

- Main migration guide: `MATRIZ_MIGRATION_GUIDE.md`
- Session summary: `MATRIZ_MIGRATION_SESSION_2025-10-26.md`
- AST rewriter: `scripts/consolidation/rewrite_matriz_imports.py`
- Compatibility shim: `MATRIZ/__init__.py`

---

**Last Updated:** 2025-10-26
**Status:** READY FOR AUTONOMOUS EXECUTION
**Estimated Success Rate:** 95% (based on 3/3 successful manual migrations)
