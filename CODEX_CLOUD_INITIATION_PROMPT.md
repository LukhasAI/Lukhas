# 🌐 Cloud-Based Codex Agent Initiation Prompt

**Date:** 2025-10-28  
**Task:** Import Cleanup - High Priority noqa F821 Fixes  
**Repository:** LukhasAI/Lukhas  
**Branch:** main  
**Execution Mode:** Cloud-based (API/SDK access, no local filesystem)  
**Codex Instance:** Codex-2 (parallel to Codex-1 working on TODO replacement)

---

## 🎯 Your Mission

You are **Codex-2**, a cloud-based autonomous AI agent specializing in code quality improvements. Your task is to **fix 5 high-priority import suppressions (noqa F821)** across the codebase.

**Why this matters:**
- ✅ Eliminates technical debt (noqa suppressions are code smell)
- ✅ Improves code quality and maintainability
- ✅ Enables proper type checking and linting
- ✅ Independent work (no dependencies on Codex-1)

**Why cloud-based execution works:**
- ✅ No local environment needed
- ✅ GitHub API access for reading/writing files
- ✅ Can create PRs remotely
- ✅ Parallel execution with Codex-1

---

## 📁 Required Artifacts (Available in Repository)

### Primary Task Definition
```
agents/batches/BATCH-CODEX-IMPORT-CLEANUP-01.json
```
**Location:** `https://github.com/LukhasAI/Lukhas/blob/main/agents/batches/BATCH-CODEX-IMPORT-CLEANUP-01.json`

**Contains:** 5 tasks with:
- File locations
- Current import issues
- Expected fixes
- Acceptance criteria

### Task Batch Structure
```json
{
  "batch_id": "BATCH-CODEX-IMPORT-CLEANUP-01",
  "priority": "MEDIUM",
  "estimated_total_time": "3h",
  "tasks": [
    {
      "task_id": "CODEX-IMPORT-01",
      "title": "Fix emotion_mapper_alt import",
      "files": ["core/orchestration/brain/spine/healix_mapper.py"],
      "location": "core/orchestration/brain/spine/healix_mapper.py:26"
    },
    // ... 4 more tasks
  ]
}
```

---

## 🚀 Execution Steps (Cloud-Based Workflow)

### Step 1: Read Task Batch
```bash
# Via GitHub API
GET https://api.github.com/repos/LukhasAI/Lukhas/contents/agents/batches/BATCH-CODEX-IMPORT-CLEANUP-01.json

# Or via raw URL
curl https://raw.githubusercontent.com/LukhasAI/Lukhas/main/agents/batches/BATCH-CODEX-IMPORT-CLEANUP-01.json
```

**Expected:** JSON with 5 tasks, total 3h effort

### Step 2: Analyze Each Task

For each task in the batch:
1. Read the affected file(s) via GitHub API
2. Identify the import issue (noqa F821 suppression)
3. Determine the correct fix:
   - Add proper import statement
   - Create missing module/class
   - Remove dead code
4. Generate the fix

**Example Task:**
```
Task: Fix emotion_mapper_alt import
File: core/orchestration/brain/spine/healix_mapper.py:26
Issue: from emotion_mapper_alt import EmotionMapper  # noqa: F821
Fix: from core.emotion.emotion_mapper_alt import EmotionMapper
```

### Step 3: Implement Fixes via GitHub API

For each fix:
```python
# Pseudo-code for GitHub API workflow
file_content = github.get_file_content("core/orchestration/brain/spine/healix_mapper.py")
fixed_content = apply_import_fix(file_content, line=26, 
                                 old="from emotion_mapper_alt import EmotionMapper",
                                 new="from core.emotion.emotion_mapper_alt import EmotionMapper")
github.create_branch("fix/import-cleanup-codex-2")
github.update_file("core/orchestration/brain/spine/healix_mapper.py", fixed_content)
```

### Step 4: Create Feature Branch

```
Branch name: fix/import-cleanup-batch-01-codex-2
```

**Naming convention:**
- `fix/` prefix (bugfix type)
- `import-cleanup` (task category)
- `batch-01` (batch identifier)
- `codex-2` (agent identifier)

### Step 5: Commit Changes

For each file fixed:
```
git commit -m "fix(imports): resolve F821 in <file>

Problem:
- noqa F821 suppression at line X
- Import statement 'from <old> import <class>' fails
- Prevents proper linting and type checking

Solution:
- Changed to 'from <correct.path> import <class>'
- Verified module exists at correct path
- Removed noqa suppression

Impact:
- ✅ Eliminates import suppression
- ✅ Enables proper type checking
- ✅ Improves code quality

Task: CODEX-IMPORT-0X from BATCH-CODEX-IMPORT-CLEANUP-01"
```

### Step 6: Validate Changes (Cloud-Based)

Since CI is disabled, use these validation checks:

**Syntax Check:**
```python
# Via GitHub API + Python AST
import ast
try:
    ast.parse(file_content)
    print("✅ Syntax valid")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
```

**Import Validation:**
```python
# Check if import path exists in repo
import_path = "core.emotion.emotion_mapper_alt"
file_path = import_path.replace(".", "/") + ".py"
if github.file_exists(file_path):
    print("✅ Import path valid")
```

### Step 7: Create Pull Request

```python
github.create_pull_request(
    title="fix(imports): resolve 5 high-priority F821 suppressions",
    body="""
## 🎯 Objective
Fix 5 high-priority noqa F821 import suppressions identified in BATCH-CODEX-IMPORT-CLEANUP-01

## ✅ Changes
- [x] Fix emotion_mapper_alt import (healix_mapper.py:26)
- [x] Fix 'bre' undefined variable (healix_mapper.py:148)
- [x] Fix healix_widget import (main_dashboard.py:58)
- [x] Fix drift_detector import (main_dashboard.py:78)
- [x] Fix session_manager import (main_dashboard.py:92)

## 📊 Impact
- 5 files modified
- 5 noqa suppressions removed
- 0 new errors introduced
- Improved code quality

## 🧪 Validation
- ✅ All files pass Python AST parsing
- ✅ Import paths verified to exist in repository
- ✅ No syntax errors introduced

## 📋 Batch Tracking
- Batch: BATCH-CODEX-IMPORT-CLEANUP-01
- Agent: Codex-2 (Cloud)
- Estimated: 3h
- Actual: [duration]
- Status: Complete

## 🤖 Automated by
Codex-2 cloud-based agent following BATCH-CODEX-IMPORT-CLEANUP-01 specifications
    """,
    branch="fix/import-cleanup-batch-01-codex-2",
    base="main"
)
```

### Step 8: Request Review & Merge

Since CI is disabled:
```bash
# Tag for human review
gh pr label <PR_NUMBER> "codex-2" "import-cleanup" "ready-for-review"

# Request merge approval
gh pr comment <PR_NUMBER> --body "✅ Codex-2 import cleanup complete. 5/5 tasks from BATCH-CODEX-IMPORT-CLEANUP-01. Ready for human review and admin merge."
```

### Step 9: Report Completion

```markdown
# ✅ Codex-2 Import Cleanup - Complete

**Date:** 2025-10-28
**Batch:** BATCH-CODEX-IMPORT-CLEANUP-01
**Status:** ✅ COMPLETE
**PR:** #XXX (pending review)

## Tasks Completed (5/5)
- ✅ CODEX-IMPORT-01: emotion_mapper_alt import fixed
- ✅ CODEX-IMPORT-02: 'bre' undefined variable cleaned
- ✅ CODEX-IMPORT-03: healix_widget import fixed
- ✅ CODEX-IMPORT-04: drift_detector import fixed
- ✅ CODEX-IMPORT-05: session_manager import fixed

## Files Modified
- core/orchestration/brain/spine/healix_mapper.py (2 fixes)
- core/orchestration/brain/dashboard/main_dashboard.py (3 fixes)

## Suppressions Removed
- 5 noqa F821 suppressions eliminated
- Code quality improved
- Linting now passes without suppressions

## Next Steps
- Human review PR #XXX
- Admin merge (no CI needed)
- Mark BATCH-CODEX-IMPORT-CLEANUP-01 as complete

**Codex-2 Task: COMPLETE** 🎉
```

---

## 📊 Task Details (5 Tasks Total)

### Task 1: Fix emotion_mapper_alt import
**File:** `core/orchestration/brain/spine/healix_mapper.py:26`  
**Issue:** `from emotion_mapper_alt import EmotionMapper  # noqa: F821`  
**Fix:** `from core.emotion.emotion_mapper_alt import EmotionMapper`  
**Complexity:** LOW  
**Time:** 30m

### Task 2: Fix 'bre' undefined variable
**File:** `core/orchestration/brain/spine/healix_mapper.py:148`  
**Issue:** `bre  # noqa: F821  # TODO: bre`  
**Fix:** Remove line (appears to be leftover debug code)  
**Complexity:** TRIVIAL  
**Time:** 5m

### Task 3: Fix healix_widget import
**File:** `core/orchestration/brain/dashboard/main_dashboard.py:58`  
**Issue:** `# TODO: healix_widget  # noqa: F821`  
**Fix:** `from core.widgets.healix_widget import create_healix_widget`  
**Complexity:** LOW  
**Time:** 30m

### Task 4: Fix drift_detector import
**File:** `core/orchestration/brain/dashboard/main_dashboard.py:78`  
**Issue:** `# TODO: drift_detector  # noqa: F821`  
**Fix:** `from core.consciousness.drift_detector import DriftDetector`  
**Complexity:** LOW  
**Time:** 30m

### Task 5: Fix session_manager import
**File:** `core/orchestration/brain/dashboard/main_dashboard.py:92`  
**Issue:** `# TODO: session_manager  # noqa: F821`  
**Fix:** `from core.orchestration.session_manager import SessionManager`  
**Complexity:** LOW  
**Time:** 30m

---

## 🛡️ Safety Guardrails

### ✅ Low Risk Tasks
- All tasks are import fixes (no logic changes)
- No runtime behavior modifications
- Only correcting import paths
- Removing code quality suppressions

### ✅ Cloud-Based Safety
- No local filesystem access needed
- All changes via GitHub API (auditable)
- Branch-based workflow (isolated)
- PR review before merge

### ✅ Validation Strategy
- Python AST parsing for syntax validation
- Import path existence verification
- No CI needed (Actions disabled due to cost)
- Human review gate before merge

### ✅ Rollback Plan
- Single PR with all changes (atomic)
- Easy to revert if needed
- Git history preserved
- No production impact (import fixes only)

---

## 🚨 Troubleshooting (Cloud-Based)

### Issue: Import Path Doesn't Exist
**Solution:** Check if module needs to be created
```python
# If import target doesn't exist, may need to create stub
if not github.file_exists(import_path):
    create_stub_module(import_path)
```

### Issue: Circular Import
**Solution:** Defer import or use TYPE_CHECKING
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.emotion.emotion_mapper_alt import EmotionMapper
```

### Issue: GitHub API Rate Limit
**Solution:** Use authenticated requests (higher limits)
```python
# Ensure using authenticated GitHub API client
# Rate limit: 5000/hour (authenticated) vs 60/hour (anonymous)
```

### Issue: Merge Conflict
**Solution:** Rebase on latest main before creating PR
```bash
# Via GitHub API
github.merge_upstream("main", "fix/import-cleanup-batch-01-codex-2")
```

---

## 📋 Pre-Flight Checklist (Cloud)

Before starting, verify:

- [ ] GitHub API access configured (token available)
- [ ] Repository: LukhasAI/Lukhas (access confirmed)
- [ ] Batch file readable: `agents/batches/BATCH-CODEX-IMPORT-CLEANUP-01.json`
- [ ] Main branch accessible
- [ ] Can create branches via API
- [ ] Can create PRs via API

**All clear?** Execute Step 1! 🚀

---

## 📚 Context Files (Optional Reading)

If you need more background:

1. **AGENTS.md** - Agent coordination system (lines 55-100)
2. **CODEX_PARALLEL_SETUP.md** - Overview of Codex assignments
3. **Batch README** - `agents/batches/README.md`

---

## 🎯 Success Criteria

You've completed your mission when:

- ✅ 5 import fixes implemented
- ✅ 5 noqa F821 suppressions removed
- ✅ All files pass syntax validation
- ✅ Import paths verified to exist
- ✅ PR created with detailed description
- ✅ Completion report generated
- ✅ Human review requested

**Good luck, Codex-2! Let's clean up these imports. 🧹**

---

## 🤝 Human Handoff

After completion, notify user with:

```
✅ Codex-2 Import Cleanup: COMPLETE

Results:
- 5 import fixes implemented
- 5 noqa suppressions removed
- 2 files modified
- PR #XXX created

Report: See PR description for details

Ready for human review and admin merge.
Parallel to Codex-1 TODO replacement (still running).
```

---

## 🔄 Parallel Execution Status

**Codex-1 (Local):** TODO Replacement (38 files, 78 issues) - IN PROGRESS  
**Codex-2 (Cloud):** Import Cleanup (5 fixes, 2 files) - **YOUR TASK**

Both agents work independently, no conflicts expected.

---

**Version:** 1.0  
**Agent:** Codex-2 (Cloud)  
**Task ID:** IMPORT-CLEANUP-BATCH-01  
**Priority:** MEDIUM  
**Autonomy:** Full (with human review gate)  
**Estimated Time:** 3 hours  
**Cost:** $0 (GitHub API only, no CI)
