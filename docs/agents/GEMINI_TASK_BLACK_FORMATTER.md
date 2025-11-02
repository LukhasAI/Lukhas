# Gemini Task: Black Formatter & Syntax Error Resolution

**Agent:** Gemini Code Assist
**Priority:** CRITICAL (P0 - Blocking)
**Estimated Duration:** 2-3 hours
**Created:** November 2, 2025
**Status:** Ready to start

---

## Task Objective

Run Black formatter across the codebase to fix 2,569 syntax errors that are blocking other linting fixes, then create a PR for review.

---

## Background Context

### What's Been Done Today
1. ✅ Fixed Ruff Python 3.9 configuration bug (UP006/UP007)
2. ✅ Applied 599 safe auto-fixes (PR #867)
3. ✅ Fixed 72 deprecated imports (PR #868)
4. ✅ Total error reduction: 71% (13,317 → ~3,800)

### Current Blocker
**2,569 syntax errors** prevent Ruff from analyzing/fixing many files. These are primarily:
- Indentation errors (inconsistent spacing)
- Line continuation issues
- Quote consistency problems
- Trailing comma formatting

### Previous Black Formatter Attempt
- **PR #829** was created but closed due to 40+ merge conflicts
- Main branch moved forward with other PRs
- Fresh run on current main is cleaner than resolving conflicts

---

## Task Breakdown

### Phase 1: Setup and Validation

**1.1 Create Clean Branch**
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout main
git pull origin main
git checkout -b fix/black-formatter-v3
```

**1.2 Verify Current State**
```bash
# Check current syntax error count
python3 -m ruff check . 2>&1 | grep "syntax-error" | wc -l
# Expected: ~2,569 errors

# Baseline smoke tests
make smoke
# Expected: 10/10 PASSING
```

**1.3 Review Black Configuration**
```bash
# Check pyproject.toml [tool.black] section
grep -A 5 "\[tool.black\]" pyproject.toml
```

**Current config:**
```toml
[tool.black]
line-length = 100
target-version = ['py311']  # Note: Should be ['py39'] to match project
include = '\.pyi?$'
```

**⚠️ Configuration Issue:** `target-version` is `py311` but project requires Python 3.9+. This is OK for Black (it's for syntax features), but be aware.

---

### Phase 2: Run Black Formatter

**2.1 Test Exclusion Pattern First**
```bash
# Test dry-run with proper exclusions
python3 -m black . \
  --check \
  --extend-exclude='(archive|quarantine|products|dreamweaver_helpers_bundle|gemini-dev|b1db8919.*|\.venv|\.copilot-venv|node_modules)' \
  2>&1 | head -100
```

**Expected exclusions:**
- `archive/` - Legacy code
- `quarantine/` - Broken code isolation
- `products/` - Production deployments
- `dreamweaver_helpers_bundle/` - Third-party
- `gemini-dev/` - Your previous worktree
- `b1db8919.*` - Copilot worktree
- `.venv/`, `.copilot-venv/` - Virtual environments
- `node_modules/` - NPM packages

**2.2 Run Black Formatter (Full)**
```bash
# Apply formatting
python3 -m black . \
  --extend-exclude='(archive|quarantine|products|dreamweaver_helpers_bundle|gemini-dev|b1db8919.*|\.venv|\.copilot-venv|node_modules)' \
  2>&1 | tee /tmp/black_formatter_output.txt
```

**Expected:**
- Will format 500-800 files
- Takes 3-5 minutes
- Output shows "reformatted X files"

**2.3 Verify Changes**
```bash
# Count modified files
git status --short | wc -l

# Get diff stats
git diff --stat | tail -1

# Check if syntax errors reduced
python3 -m ruff check . 2>&1 | grep "syntax-error" | wc -l
# Expected: Significantly reduced (ideally < 100)
```

---

### Phase 3: Validation

**3.1 Smoke Tests (Critical)**
```bash
make smoke
# MUST show: 10/10 PASSING
# If ANY test fails, STOP and report
```

**3.2 Import Validation**
```bash
# Test that major modules still import
python3 -c "import lukhas; import matriz; import core"
python3 -c "from lukhas.identity import core"
python3 -c "from matriz.core import async_orchestrator"
```

**3.3 Compilation Check**
```bash
# Sample compilation checks
python3 -m py_compile matriz/traces_router.py
python3 -m py_compile core/identity/manager.py
python3 -m py_compile lukhas_website/lukhas/identity/core.py
```

---

### Phase 4: Commit and PR

**4.1 Review Changes**
```bash
# Look at sample of changes
git diff core/identity/manager.py | head -50
git diff matriz/core/async_orchestrator.py | head -50

# Check for any unexpected changes
git diff --name-only | grep -E "(\.env|secrets|credentials)" || echo "✓ No secrets files modified"
```

**4.2 Commit Changes**
```bash
git add -A
git commit -m "$(cat <<'EOF'
fix(lint): apply Black formatter to resolve 2,569 syntax errors

Problem:
- 2,569 syntax errors blocking Ruff analysis and auto-fixes
- Inconsistent indentation, quote styles, line continuations
- Previous Black formatter PR (#829) had merge conflicts

Solution:
- Applied Black formatter with proper exclusions
- Formatted X files across entire codebase
- Fixed indentation, quotes, trailing commas, line breaks

Impact:
- Files modified: X
- Lines changed: +X/-X
- Syntax errors fixed: 2,569 → X (Y% reduction)
- Smoke tests: ✅ 10/10 passing
- Python 3.9 compatibility: ✅ Maintained

Exclusions:
- archive/, quarantine/ (legacy code)
- products/ (production deployments)
- .venv/, node_modules/ (dependencies)
- gemini-dev/, b1db8919* (worktrees)

Validation:
```bash
# Before
ruff check . → 2,569 syntax errors

# After
ruff check . → X syntax errors (Y% fixed)
make smoke → 10/10 PASSED
```

Related Work:
- Replaces closed PR #829 (had conflicts)
- Unblocks: E402, F821, UP035 batch fixes
- Part of comprehensive linting cleanup initiative

🤖 Generated with Gemini Code Assist
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

**4.3 Push and Create PR**
```bash
git push -u origin fix/black-formatter-v3

gh pr create \
  --title "fix(lint): apply Black formatter to resolve 2,569 syntax errors" \
  --body "$(cat <<'EOF'
## Summary
Applies Black formatter across the codebase to fix 2,569 syntax errors blocking further linting improvements.

## Changes
- **Indentation:** Consistent 4-space indentation throughout
- **Quotes:** Standardized to double quotes (Black default)
- **Line Breaks:** Fixed line continuation and trailing commas
- **Whitespace:** Cleaned trailing whitespace and blank lines

## Impact
- **Files modified:** X (estimate: 500-800)
- **Syntax errors fixed:** 2,569 → X (target: <100)
- **Lines changed:** Will be substantial but purely formatting
- **Smoke tests:** ✅ 10/10 passing
- **Python 3.9 compatibility:** ✅ Maintained

## Why This Matters
These syntax errors block Ruff from analyzing code properly. Fixing them unblocks:
- E402 import ordering fixes (156 files)
- F821 undefined name fixes (143 files)
- UP035 remaining deprecated imports (1,144 files)
- Manual code review and refactoring

## Previous Attempt
- PR #829 was closed due to 40+ merge conflicts
- This is a fresh run on current main (post-PRs #867, #868)
- Cleaner approach than resolving old conflicts

## Validation
```bash
# Error reduction
Before: ruff check . → 2,569 syntax errors
After:  ruff check . → X syntax errors

# Test validation
make smoke → 10/10 PASSED

# Import checks
python3 -c "import lukhas; import matriz; import core" → ✅ OK
```

## Exclusions
Properly excluded from formatting:
- `archive/`, `quarantine/` - Legacy/broken code
- `products/` - Production deployments
- `.venv/`, `node_modules/` - Dependencies
- `gemini-dev/`, `b1db8919*` - Worktrees

## Review Notes
⚠️ **Large PR Warning:** This will touch 500-800 files with formatting changes. Review strategy:
1. Spot-check 5-10 random files for correctness
2. Verify smoke tests pass (already done)
3. Confirm exclusions worked correctly
4. Merge confidently - Black is deterministic and safe

---
🤖 Generated with Gemini Code Assist
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)" \
  --base main \
  --head fix/black-formatter-v3
```

**4.4 Report Completion**
```markdown
✅ **Black Formatter Task Complete**

**PR Created:** #XXX
**Branch:** fix/black-formatter-v3
**Files Modified:** X
**Syntax Errors Fixed:** 2,569 → X (Y% reduction)
**Smoke Tests:** 10/10 PASSING ✅

**Next Steps:**
- PR ready for review and merge
- Unblocks E402, F821, UP035 batch fixes
- Recommend merge before weekend
```

---

## Success Criteria

### Required (Must Pass)
- ✅ Black formatter runs successfully without errors
- ✅ All smoke tests passing (10/10)
- ✅ Syntax errors reduced by >90% (target: <250 remaining)
- ✅ No test files, credentials, or secrets modified
- ✅ PR created with comprehensive description

### Desired (Nice to Have)
- ✅ Syntax errors reduced by >95% (target: <100 remaining)
- ✅ No import errors in core modules
- ✅ Excluded directories verified untouched
- ✅ Commit message follows T4 standards

---

## Common Issues & Solutions

### Issue 1: Black Formatting Fails
**Symptom:** Black exits with syntax errors
**Solution:**
```bash
# Find which files have syntax errors BEFORE Black
python3 -m ruff check . --select E999 --output-format=json > /tmp/syntax_errors.json

# Review the problem files
python3 -c "import json; print('\n'.join([x['filename'] for x in json.load(open('/tmp/syntax_errors.json'))]))"

# Consider excluding problem files temporarily
```

### Issue 2: Smoke Tests Fail After Formatting
**Symptom:** Tests that passed before now fail
**Solution:**
```bash
# Identify which test failed
make smoke

# Run specific test with details
pytest tests/smoke/test_entrypoints.py -v

# Check if it's an import issue
python3 -c "import matriz.traces_router"

# STOP and report - do not create PR
```

### Issue 3: Too Many Files Changed
**Symptom:** Git reports >1000 files modified
**Solution:**
```bash
# Check if exclusions worked
git status | grep -E "(archive|quarantine|products|\.venv)" && echo "❌ Exclusions failed"

# Review what changed
git diff --name-only | head -20

# If worktrees/dependencies touched, abort:
git reset --hard HEAD
# Fix exclusion pattern and retry
```

### Issue 4: Syntax Errors Still High (>500)
**Symptom:** Black runs but syntax errors only drop to 500-1000
**Solution:**
- This is OK - Black can't fix all syntax errors (e.g., undefined names)
- Document which errors remain
- Create PR anyway if smoke tests pass
- Report in PR description what remains

---

## Validation Commands

### Before Starting
```bash
# Record baseline
python3 -m ruff check . 2>&1 | grep "Found" | tail -1 > /tmp/errors_before.txt
make smoke 2>&1 | grep -E "passed|failed" > /tmp/smoke_before.txt
```

### After Black Formatting
```bash
# Compare error counts
python3 -m ruff check . 2>&1 | grep "Found" | tail -1 > /tmp/errors_after.txt
diff /tmp/errors_before.txt /tmp/errors_after.txt

# Verify smoke tests
make smoke 2>&1 | grep -E "passed|failed" > /tmp/smoke_after.txt
diff /tmp/smoke_before.txt /tmp/smoke_after.txt
```

### Before Creating PR
```bash
# Final checks
echo "Files modified: $(git status --short | wc -l)"
echo "Lines changed: $(git diff --shortstat)"
echo "Smoke tests: $(make smoke 2>&1 | grep -E '\[100%\]')"
echo "Syntax errors: $(python3 -m ruff check . 2>&1 | grep syntax-error | wc -l)"
```

---

## Resources

- **Black Docs:** https://black.readthedocs.io/en/stable/
- **pyproject.toml:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/pyproject.toml` (lines 194-199)
- **Previous PR:** #829 (closed, for reference only)
- **Session Doc:** `SESSION_FINAL_SUMMARY_2025-11-02.md`
- **Error Log:** `ERROR_LOG_2025-11-02.md`

---

## Communication Protocol

### Progress Updates
Report after each major phase:
1. **Setup complete:** "✅ Branch created, baseline recorded"
2. **Black running:** "🔄 Formatting X files, estimated Y minutes"
3. **Validation:** "✅ Smoke tests: 10/10, syntax errors: A → B"
4. **PR created:** "✅ PR #XXX ready for review"

### Issues/Blockers
If you encounter issues:
- **Smoke tests fail:** STOP immediately, report which test and error message
- **Black fails:** Document which files cause issues, consider excluding them
- **Syntax errors still high (>1000):** Report but continue if smoke tests pass
- **Git issues:** Check exclusions, may need to adjust pattern

### Questions
If unsure about:
- **Should I format file X?** → Check if it's in exclusion list
- **Test failed, should I continue?** → NO, stop and report
- **Too many files changed?** → Expected, verify exclusions worked
- **Syntax errors not all fixed?** → Expected, Black can't fix everything

---

## Expected Deliverables

1. **Git Branch** (today)
   - Name: `fix/black-formatter-v3`
   - Commit: Single commit with all formatting changes
   - Status: Pushed to origin

2. **Pull Request** (today)
   - Number: Will be assigned by GitHub
   - Title: "fix(lint): apply Black formatter to resolve 2,569 syntax errors"
   - Body: Comprehensive description with validation results
   - Labels: `lint`, `formatting`, `P0`, `ready-for-review`

3. **Validation Report** (today)
   - Before/after error counts
   - Smoke test results
   - Files modified count
   - Any issues encountered

---

## Notes

- **Timeline:** Should take 2-3 hours including validation
- **Risk Level:** LOW - Black is deterministic and safe
- **Dependencies:** None - can start immediately
- **Blocking:** This unblocks many other linting tasks
- **Review:** Large PR but mechanical changes only

---

**Ready to begin?** Follow Phase 1 setup and report back when ready to run Black!

🤖 Task created by Claude Code for Gemini Code Assist
📅 Created: November 2, 2025
⏰ Expected completion: Same day
