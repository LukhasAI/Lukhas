# 🤖 Codex Parallel Copilot Setup

**Date:** 2025-10-28  
**Status:** Ready for execution (PR #540 MERGED, CI disabled, cost-conscious mode)

---

## ✅ Codex Primary Assignments

Based on `AGENTS.md`, Codex is the **PRIMARY** agent for these autonomous guides:

### 1. MATRIZ Migration Completion ✅ **COMPLETE**
- **Guide:** `AUTONOMOUS_GUIDE_MATRIZ_COMPLETION.md`
- **Status:** ✅ **PR #540 MERGED** (commit: de28bdf9c)
- **Scope:** 17 imports standardized (matriz → MATRIZ)
- **Script:** `scripts/consolidation/rewrite_matriz_imports.py`
- **Action:** No further work needed - migration complete!

### 2. Import Organization (E402) 🔄 **READY**
- **Guide:** `AUTONOMOUS_GUIDE_IMPORT_ORGANIZATION.md`
- **Status:** Ready for execution
- **Scope:** Fix E402 linting errors (import not at top of file)
- **Script:** `scripts/consolidation/rewrite_matriz_imports.py` (reuse/mode)
- **Priority:** Medium (code quality improvement)
- **Effort:** ~10-20 files to fix

---

## 🤝 Codex Secondary Assignments

Codex is **SECONDARY** (support) for:

### 3. TODO Cleanup Campaign ✅ **78 ISSUES CREATED**
- **Primary:** GitHub Copilot (interactive)
- **Codex Role:** Automation scripts
- **Status:** ✅ 78 issues created (#552-#629), ready for parallel execution
- **Script:** `scripts/todo_migration/replace_todos_with_issues.py`
- **Action:** Can assist with bulk TODO → issue link replacement

### 4. Test Coverage Expansion 📊 **AVAILABLE**
- **Primary:** GitHub Copilot (test authoring)
- **Codex Role:** Test harness generation
- **Status:** Available for test infrastructure work
- **Scope:** Expand coverage to 75%+ for production readiness

### 5. Candidate Lane Cleanup 🧹 **AVAILABLE**
- **Primary:** GitHub Copilot (interactive fixes)
- **Codex Role:** Promotion scripts
- **Status:** Available for automation support
- **Scope:** Candidate → Core promotion workflow

---

## 🚀 Recommended Codex Workflow

### Option A: Import Organization (Primary - E402 fixes)
**Best for:** AST-based code transformations (Codex strength)

```bash
# Step 1: Check current E402 issues
ruff check . --select E402 | head -20

# Step 2: Run script in dry-run mode
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --path lukhas core serve \
  --dry-run --verbose

# Step 3: Apply fixes (after review)
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --path lukhas core serve \
  --git-apply

# Step 4: Create PR
git checkout -b fix/e402-import-organization-$(date +%Y%m%d)
git add -p  # Stage carefully
git commit -m "fix(imports): resolve E402 import organization issues"
git push origin HEAD
```

**Estimated Effort:** 2-3 hours  
**Value:** Clean linting, better code organization  
**Risk:** Low (AST transformations are mechanical)

---

### Option B: TODO Replacement (Secondary - Bulk automation)
**Best for:** Bulk file operations (Codex efficiency)

```bash
# Step 1: Check mapping file
cat artifacts/todo_to_issue_map.json | head -20

# Step 2: Run replacement script (dry-run)
python3 scripts/todo_migration/replace_todos_with_issues.py \
  --map artifacts/todo_to_issue_map.json \
  --dry-run

# Step 3: Apply replacements
python3 scripts/todo_migration/replace_todos_with_issues.py \
  --map artifacts/todo_to_issue_map.json

# Step 4: Create PR
git checkout -b chore/replace-todos-with-issue-links
git add -A
git commit -m "chore(todos): replace 78 TODOs with GitHub issue links"
git push origin HEAD
```

**Estimated Effort:** 1-2 hours  
**Value:** Clean codebase, trackable issues  
**Risk:** Very low (search & replace with validation)

---

## 💰 Cost-Conscious Execution

**Since GitHub Actions are disabled ($300 spend):**

1. **Local validation only** - No CI to burn money
2. **Manual testing** - `make smoke`, `make test-tier1`
3. **Small PRs** - Keep changes focused and reviewable
4. **Admin merge** - Use `gh pr merge --admin` to bypass checks
5. **Free parallel work** - Multiple copilots working on different issues = $0 CI cost

---

## 📊 Current Status Summary

| Task | Status | Codex Role | Effort | Value |
|------|--------|-----------|--------|-------|
| MATRIZ Migration | ✅ COMPLETE | Primary | 0h | Done! |
| Import Organization (E402) | 🔄 READY | Primary | 2-3h | Medium |
| TODO Replacement | 🔄 READY | Secondary | 1-2h | High |
| Test Coverage | 📊 AVAILABLE | Secondary | 10-20h | High |
| Candidate Cleanup | 🧹 AVAILABLE | Secondary | Variable | Medium |

---

## 🎯 Recommendation

**Start with Option B (TODO Replacement)** because:
1. ✅ **Highest value** - Makes 78 issues immediately trackable
2. ✅ **Lowest risk** - Simple search & replace
3. ✅ **Fastest** - 1-2 hours for complete automation
4. ✅ **Zero cost** - No CI, local testing only
5. ✅ **Enables parallelism** - Clears TODOs so other copilots can work on issues

**Then Option A (Import Organization)** for code quality improvements.

---

## 🤖 Next Steps

1. **Review this plan** - Does Option B → A make sense?
2. **Spawn Codex instance** - Point to this file + `artifacts/todo_to_issue_map.json`
3. **Execute Option B** - Run TODO replacement script
4. **Create PR** - Small, focused, easy to review
5. **Merge** - Admin merge (no CI needed)
6. **Continue to Option A** - Import organization cleanup

