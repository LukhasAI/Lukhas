# GitHub Copilot: M1 Conflicts Resolution Brief

**Target**: GitHub Copilot in VS Code
**Access**: `origin/main` branch only
**Mission**: Resolve merge conflicts in 4 M1 PRs step-by-step

---

## Overview

You have access to `origin/main` and need to resolve conflicts in 4 M1-related PRs:
- PR #820: Tags lazy-proxy (43 files, +19,832 lines)
- PR #813: Identity lazy-load (43 files, +19,779 lines)
- PR #811: Agent pack system (5 files, +701 lines) ✅ MERGEABLE
- PR #805: Complete M1 branch (41 files, +19,740 lines)

**Note**: You cannot access the M1 branch directly, but you can see the PR diffs and conflicting files.

---

## Task 1: Analyze PR #811 (Ready to Merge!)

**Status**: ✅ MERGEABLE - No conflicts!

**Action**: Review and approve (no work needed)

```bash
# In VS Code terminal:
gh pr view 811 --web
# Review the changes, then approve
```

**What's in PR #811**:
- M1 parallel agent pack system
- 5 files: agent task documentation
- Clean addition, no conflicts
- Safe to merge immediately

**Copilot Action**: Just review and comment "LGTM" if the agent pack structure looks good.

---

## Task 2: Resolve PR #820 Conflicts (Tags Lazy-Proxy)

**PR**: #820
**Title**: chore(tags): lazy-proxy re-exports in core/tags/__init__.py (M1)
**Base**: main ← **Head**: task/claude-lazy-init-tags-M1
**Files**: 43 files, +19,832 lines
**Status**: CONFLICTING

### Step 2.1: View PR Diff

```bash
# In VS Code:
gh pr view 820 --web
# Or see the diff:
gh pr diff 820 > /tmp/pr820.diff
code /tmp/pr820.diff
```

### Step 2.2: Identify Conflict Files

```bash
gh pr view 820 --json files --jq '.files[] | select(.additions > 0) | .path' | head -20
```

### Step 2.3: Understand the Pattern

Look for this pattern in the diff:
```python
# BEFORE (direct import - causes import-time dependency):
from labs.something import SomeClass

# AFTER (lazy proxy pattern):
try:
    import importlib
    _mod = importlib.import_module("labs.something")
    SomeClass = getattr(_mod, "SomeClass")
except Exception:
    SomeClass = None
```

### Step 2.4: Conflict Resolution Strategy

**For each conflicting file**:

1. **Open the file in VS Code**
2. **Look for conflict markers**:
   ```
   <<<<<<< HEAD (current main)
   # Main's version
   =======
   # PR #820's version
   >>>>>>> task/claude-lazy-init-tags-M1
   ```

3. **Apply this decision tree**:
   - If **main has recent fixes** (from PR #806, #824, #825) → **Keep main's version** but add lazy-proxy pattern from #820
   - If **#820 has lazy-proxy pattern** → **Take #820's version**
   - If **both are refactored** → Manually merge both improvements

4. **Example resolution**:
   ```python
   # Conflict in core/tags/__init__.py
   <<<<<<< HEAD
   # Main version (already has provider pattern from PR #806)
   from core.adapters.provider_registry import ProviderRegistry
   =======
   # PR #820 version (has lazy-proxy for tags)
   try:
       import importlib
       _tags_mod = importlib.import_module("core.tags.registry")
       TagRegistry = getattr(_tags_mod, "TagRegistry")
   except Exception:
       TagRegistry = None
   >>>>>>> task/claude-lazy-init-tags-M1

   # RESOLUTION: Keep both patterns
   from core.adapters.provider_registry import ProviderRegistry

   try:
       import importlib
       _tags_mod = importlib.import_module("core.tags.registry")
       TagRegistry = getattr(_tags_mod, "TagRegistry")
   except Exception:
       TagRegistry = None
   ```

### Step 2.5: Validate Resolution

After resolving each file:

```bash
# Check syntax
python3 -m py_compile <resolved_file.py>

# Run lane-guard
make lane-guard

# Run smoke tests
make smoke
```

### Step 2.6: Comment on PR

After resolving all conflicts in PR #820:

```bash
gh pr comment 820 --body "@copilot

✅ Conflicts resolved in PR #820

**Files Updated**: [list files]
**Resolution Strategy**: Merged lazy-proxy pattern with recent main changes
**Validation**:
- ✅ Syntax check passed
- ✅ Lane-guard passed
- ✅ Smoke tests passed

Ready for review and merge."
```

---

## Task 3: Resolve PR #813 Conflicts (Identity Lazy-Load)

**PR**: #813
**Title**: refactor(provider): lazy-load labs in core/identity (M1)
**Base**: main ← **Head**: task/claude-lazy-load-identity-M1
**Files**: 43 files, +19,779 lines
**Status**: CONFLICTING

### Step 3.1: Same Analysis Process

Follow the same steps as Task 2:
1. View PR diff
2. Identify conflict files
3. Understand the lazy-load pattern
4. Resolve conflicts file-by-file
5. Validate each resolution
6. Comment when complete

### Step 3.2: Identity-Specific Patterns

Look for these patterns in `core/identity/`:

```python
# BEFORE (import-time):
from labs.identity import IdentityProvider

# AFTER (lazy-load):
def _get_identity_provider():
    """Lazy-load identity provider at runtime."""
    try:
        import importlib
        mod = importlib.import_module("labs.identity")
        return getattr(mod, "IdentityProvider")
    except Exception:
        return None
```

### Step 3.3: Key Files to Focus On

Priority files in PR #813:
- `core/identity/lambda_id.py`
- `core/identity/__init__.py`
- `core/identity/auth/*.py`

### Step 3.4: Validation Checklist

- [ ] No `from labs.*` imports remain
- [ ] Lazy-load pattern applied consistently
- [ ] No import-time dependencies
- [ ] Lane-guard passes
- [ ] Smoke tests pass

---

## Task 4: Resolve PR #805 Conflicts (Complete M1 Branch)

**PR**: #805
**Title**: 🚀 LUKHAS M1 Branch - Complete Platform Enhancements
**Base**: main ← **Head**: M1
**Files**: 41 files, +19,740 lines, 23 commits
**Status**: CONFLICTING

### Step 4.1: Large Branch Strategy

This PR is the parent M1 branch. Strategy:

**Option A** (Recommended): Merge #820 and #813 first, then #805
- Rationale: #805 includes changes from #820 and #813
- After merging those, #805 will have fewer conflicts

**Option B**: Resolve #805 directly
- More conflicts to resolve
- But consolidates all M1 work at once

### Step 4.2: If Choosing Option A (Recommended)

1. Complete Task 2 (PR #820) ✅
2. Merge #820 to main
3. Complete Task 3 (PR #813) ✅
4. Merge #813 to main
5. Return to #805 - conflicts should be reduced

### Step 4.3: If Choosing Option B

Follow same conflict resolution process:
1. View all 41 files with conflicts
2. Create checklist of files to resolve
3. Resolve in batches (10 files at a time)
4. Validate after each batch
5. Comment on progress

---

## General Conflict Resolution Patterns

### Pattern 1: Import Statement Conflicts

```python
# Conflict type: Import style mismatch

<<<<<<< HEAD (main)
from core.adapters.provider_registry import ProviderRegistry
=======
import importlib
>>>>>>> M1 branch

# RESOLUTION: Keep both if they serve different purposes
from core.adapters.provider_registry import ProviderRegistry
import importlib
```

### Pattern 2: Function Refactoring Conflicts

```python
# Conflict type: Function signature changed in both branches

<<<<<<< HEAD
def process_identity(user_id: str) -> Identity:
    """Process identity with provider pattern."""
    provider = _get_identity_provider()
    return provider.get_identity(user_id)
=======
def process_identity(user_id: str, lazy: bool = True) -> Identity:
    """Process identity with lazy-load pattern."""
    if lazy:
        provider = _lazy_get_identity_provider()
    else:
        provider = _get_identity_provider()
    return provider.get_identity(user_id)
>>>>>>> M1 branch

# RESOLUTION: Combine both improvements
def process_identity(user_id: str, lazy: bool = True) -> Identity:
    """Process identity with provider and lazy-load patterns."""
    if lazy:
        provider = _lazy_get_identity_provider()
    else:
        provider = _get_identity_provider()
    return provider.get_identity(user_id)
```

### Pattern 3: Configuration File Conflicts

```yaml
# Conflict type: Config values differ

<<<<<<< HEAD
timeout: 30
max_retries: 3
=======
timeout: 60
max_retries: 5
use_cache: true
>>>>>>> M1 branch

# RESOLUTION: Take higher values + new features
timeout: 60
max_retries: 5
use_cache: true
```

---

## Validation Commands (Run After Each File)

```bash
# 1. Syntax check
python3 -m py_compile <file.py>

# 2. Import check
python3 -c "import <module_path>"

# 3. Lane-guard (critical!)
make lane-guard

# 4. Smoke tests
make smoke

# 5. Specific module tests
pytest tests/unit/test_<module>.py -v
```

---

## Progress Tracking Template

Create a checklist in VS Code (or GitHub PR comment):

```markdown
## PR #820 Conflict Resolution Progress

### Batch 1 (Files 1-10)
- [ ] core/tags/__init__.py
- [ ] core/tags/registry.py
- [ ] core/tags/lazy_proxy.py
- [ ] ...

**Validation**:
- [ ] Syntax check passed
- [ ] Lane-guard passed
- [ ] Smoke tests passed

### Batch 2 (Files 11-20)
...
```

---

## Emergency Rollback

If a resolution causes issues:

```bash
# Abort current resolution
git merge --abort

# Or reset specific file
git checkout origin/main -- <file_path>

# Or create new branch and start over
git checkout -b fix/pr820-attempt2 origin/main
```

---

## Success Criteria (For Each PR)

Before marking a PR as "resolved":

- [ ] All conflict markers removed (`<<<<<<< HEAD`, `=======`, `>>>>>>>`)
- [ ] All files compile (`python3 -m py_compile`)
- [ ] No `from labs.*` imports remain (run: `rg "from labs\." --type py`)
- [ ] Lane-guard passes (`make lane-guard`)
- [ ] Smoke tests pass (`make smoke`)
- [ ] No new imports from `candidate/` into `lukhas/`
- [ ] Comment added to PR with resolution summary

---

## Communication Template

After completing each PR:

```markdown
@copilot

## ✅ PR #[number] Conflicts Resolved

**Resolution Summary**:
- Files resolved: [count]
- Conflicts resolved: [count]
- Resolution strategy: [describe approach]

**Validation Results**:
- ✅ Syntax checks: All passing
- ✅ Lane-guard: Zero violations
- ✅ Smoke tests: All passing
- ✅ Import safety: No labs imports remaining

**Key Decisions**:
1. [Decision 1 and rationale]
2. [Decision 2 and rationale]

**Ready for**: Human review and merge

**Next Steps**: [Link to next PR if applicable]
```

---

## Recommended Order

1. ✅ **PR #811** - Merge immediately (no conflicts)
2. 🔧 **PR #820** - Resolve conflicts (tags lazy-proxy)
3. 🔧 **PR #813** - Resolve conflicts (identity lazy-load)
4. 🔧 **PR #805** - Resolve conflicts (complete M1) OR close if #820 & #813 cover it

---

## Important Reminders

**Lane Isolation Rules**:
- ✅ `lukhas/` can import from `core/`, `matriz/`
- ❌ `lukhas/` CANNOT import from `candidate/`
- ✅ `candidate/` can import from `core/`, `matriz/`

**Conservative Approach**:
- When in doubt, favor main's recent changes (they're tested)
- Add M1 improvements incrementally
- Test after every batch of 5-10 files
- Don't hesitate to ask for human review

**No Auto-Merge**:
- All PR resolutions require human approval
- Tag @human-reviewer when ready
- Include validation results in comment

---

## Questions to Ask

If you encounter these situations:

1. **Conflicting logic**: "Main has approach A, M1 has approach B. Both seem valid. Which should I keep?"
2. **Missing context**: "This conflict references code I don't see in main or M1. Where is it from?"
3. **Breaking change**: "This resolution might break compatibility. Should I proceed?"
4. **Large refactor**: "This file has 200+ line conflict. Should I resolve or recreate?"

**Ask the human** before proceeding with complex decisions.

---

## Ready to Start?

**Immediate Actions**:
1. Open VS Code
2. Ensure you're on `origin/main` branch
3. Start with PR #811 (review only, no conflicts)
4. Then proceed to PR #820 (first conflict resolution)

Let's resolve these M1 conflicts systematically! 🛠️
