# Gemini Task: Fix 128 Real Syntax Errors in Production Code

**Agent:** Gemini Code Assist
**Priority:** P0 - CRITICAL (Blocking)
**Estimated Duration:** 3-4 hours
**Created:** November 2, 2025
**Status:** Ready to start

---

## Task Objective

Fix 128 real syntax errors in production code that prevent files from compiling. These errors remained after Black formatter (PR #870) and are primarily indentation issues, orphaned code blocks, and incomplete imports.

---

## Background Context

### What's Been Done Today
1. ✅ Applied Black formatter (PR #870)
2. ✅ Reduced syntax errors from 2,569 → 878 (65.8% reduction)
3. ✅ Identified remaining 878 errors by location:
   - **Production code**: 128 errors (priority)
   - Worktrees (b1db8919, gemini-dev): 586 errors (defer)
   - Experimental (labs/): 164 errors (defer)

### Current Blocker
**128 syntax errors** in production code prevent:
- Code compilation and execution
- Proper linting analysis
- Automated refactoring
- Import dependency analysis

---

## Task Breakdown

### Phase 1: Analyze Syntax Errors

**1.1 Get Full Error List**
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

python3 << 'SCRIPT'
import ast
from pathlib import Path

production_errors = []
exclude = ['.venv', 'node_modules', 'archive', 'quarantine', 'products',
           'dreamweaver', 'b1db8919', 'gemini-dev', 'labs']

for f in Path('.').rglob('*.py'):
    if any(x in str(f) for x in exclude):
        continue
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        production_errors.append({
            'file': str(f),
            'line': e.lineno,
            'msg': e.msg,
            'text': e.text.strip() if e.text else ''
        })

# Group by error type
from collections import defaultdict
by_type = defaultdict(list)
for err in production_errors:
    by_type[err['msg']].append(err)

print(f"Total production syntax errors: {len(production_errors)}\n")
for msg, errors in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{len(errors):3d} - {msg}")
    # Show first 5 examples
    for err in errors[:5]:
        print(f"      {err['file']}:{err['line']}")
SCRIPT
```

**Expected Output:**
```
Total production syntax errors: 128

 80 - unexpected indent
      bridge/integration_bridge.py:1
      core/consciousness/chaos_engineering_framework.py:50
      ...
 24 - invalid syntax
      core/consciousness/async_client.py:48
      matriz/consciousness/dream/parallel_reality_simulator.py:33
      ...
 18 - expected an indented block
      core/consciousness/bridge.py:274
      core/consciousness/collapse_governance_system.py:38
      ...
```

**1.2 Categorize by Subsystem**
```bash
python3 -c "
import ast
from pathlib import Path
from collections import defaultdict

errors_by_dir = defaultdict(list)
exclude = ['.venv', 'node_modules', 'archive', 'quarantine', 'products',
           'dreamweaver', 'b1db8919', 'gemini-dev', 'labs']

for f in Path('.').rglob('*.py'):
    if any(x in str(f) for x in exclude):
        continue
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        parts = str(f).split('/')
        top_dir = parts[0] if len(parts) > 1 else 'root'
        errors_by_dir[top_dir].append(str(f))

# Priority order
priority = ['core', 'matriz', 'lukhas_website', 'qi', 'bridge', 'vivox', 'tools', 'tests']
for dir_name in priority:
    if dir_name in errors_by_dir:
        print(f'{dir_name}/: {len(errors_by_dir[dir_name])} files')
"
```

---

### Phase 2: Fix Errors by Pattern

**2.1 Fix Pattern 1: Indented Docstrings (Lines 1-5)**

Many files start with indented docstrings. Fix by removing leading indentation:

```python
# Find files with indented start
python3 << 'SCRIPT'
import ast
from pathlib import Path

for f in Path('.').rglob('*.py'):
    if any(x in str(f) for x in ['.venv', 'b1db8919', 'gemini-dev', 'labs']):
        continue
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        if e.msg == "unexpected indent" and e.lineno and e.lineno <= 5:
            print(f"{f}:{e.lineno}")
SCRIPT

# Example fix for integration_bridge.py
# Before (line 1):
    """
    Adapts a LUKHΛS Plugin...

# After (line 1):
"""
Adapts a LUKHΛS Plugin...
```

**2.2 Fix Pattern 2: Orphaned Try Blocks**

Many files have `try:` statements without proper function/class context:

```bash
# Find orphaned try blocks
grep -n "^        try:$" core/**/*.py matriz/**/*.py | head -20
```

**Common Pattern:**
```python
# BROKEN (unexpected indent at line 33):
        try:
            logger.info("Initializing...")
            self.consciousness_service = get_service("consciousness_service")
        except Exception as e:
            logger.error(f"Error: {e}")

# Should be part of a method:
    async def initialize(self):
        """Initialize the interface."""
        try:
            logger.info("Initializing...")
            self.consciousness_service = get_service("consciousness_service")
        except Exception as e:
            logger.error(f"Error: {e}")
```

**Action:** For each file, check git history to find the missing function/class context:
```bash
git log --oneline -5 -- path/to/file.py
git show COMMIT:path/to/file.py | grep -B 10 "try:"
```

**2.3 Fix Pattern 3: Incomplete Imports**

Files like `core/consciousness/async_client.py` have incomplete multiline imports:

```python
# BROKEN (line 47-49):
from huggingface_hub.inference._common import (
from huggingface_hub.inference._generated.types import (
from huggingface_hub.inference._providers import (

# Should be (check original file or remove if unused):
from huggingface_hub.inference._common import INFERENCE_ENDPOINT
from huggingface_hub.inference._generated.types import (
    ConversationalOutput,
    ImageClassification,
    # ... other types
)
from huggingface_hub.inference._providers import get_provider
```

**Action:** Check if these files are actively used:
```bash
# Find imports of async_client
grep -r "from core.consciousness import async_client" . --exclude-dir=.venv
grep -r "import async_client" . --exclude-dir=.venv

# If unused, comment out or fix based on git history
git show HEAD~10:core/consciousness/async_client.py | grep -A 5 "from huggingface_hub"
```

**2.4 Fix Pattern 4: Missing Code After Except**

```python
# BROKEN (bridge.py:272):
except Exception as e:


logger = logging.getLogger(__name__)

# Should be:
except Exception as e:
    logger.error(f"Failed to load config: {e}")
    return {"error": str(e)}

logger = logging.getLogger(__name__)
```

---

### Phase 3: Automated Fixes

**3.1 Use autopep8 for Simple Indentation**

Try automated fixing for simple indentation issues:

```bash
# Install autopep8 if needed
pip install autopep8

# Test on a few files
autopep8 --in-place --select=E101,E111,E112,E113,E114,E115,E116,E117 \
  core/consciousness/natural_language_interface.py

# Verify it compiles
python3 -m py_compile core/consciousness/natural_language_interface.py
```

**3.2 Bulk Fix Simple Cases**

```bash
# Get list of files with only "unexpected indent" errors
python3 -c "
import ast
from pathlib import Path

simple_files = []
exclude = ['.venv', 'b1db8919', 'gemini-dev', 'labs']

for f in Path('.').rglob('*.py'):
    if any(x in str(f) for x in exclude):
        continue
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        if e.msg == 'unexpected indent':
            simple_files.append(str(f))

for f in simple_files[:20]:  # First 20
    print(f)
" > /tmp/simple_indent_files.txt

# Apply autopep8 to these files
while read file; do
    autopep8 --in-place --select=E101,E111,E112,E113,E114,E115,E116,E117 "$file"
    # Verify compilation
    python3 -m py_compile "$file" 2>&1 || echo "FAILED: $file"
done < /tmp/simple_indent_files.txt
```

---

### Phase 4: Manual Fixes for Complex Cases

**4.1 Prioritize Critical Files**

Focus on files most likely to be used:

```bash
# Check import frequency
for dir in core matriz lukhas_website qi; do
    echo "=== $dir/ ==="
    find $dir -name "*.py" -type f | while read f; do
        count=$(grep -r "from $f" . --exclude-dir=.venv 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            echo "$count imports: $f"
        fi
    done | sort -rn | head -10
done
```

**4.2 Fix High-Priority Files**

For each critical file with syntax errors:

1. Read the file to understand context
2. Check git history for recent changes:
   ```bash
   git log -p --follow -n 5 -- path/to/file.py
   ```
3. Restore missing context or comment out broken sections:
   ```python
   # TODO(gemini): Restore this section - broken during refactoring
   # Original context lost, needs manual review
   # try:
   #     logger.info("Initializing...")
   ```
4. Compile and verify:
   ```bash
   python3 -m py_compile path/to/file.py
   ```

**4.3 Document Unfixable Cases**

If a file cannot be fixed (too corrupted, unclear intent):

```bash
# Create issue tracking file
cat >> /tmp/unfixable_syntax_errors.md << EOF
# Unfixable Syntax Errors

## core/consciousness/async_client.py
- **Issue**: Incomplete multiline imports (lines 47-49)
- **Impact**: File cannot compile
- **Recommendation**: Remove file if unused, or restore from earlier commit
- **Check usage**: \`grep -r "async_client" . --exclude-dir=.venv\`

EOF
```

---

### Phase 5: Validation

**5.1 Verify All Fixes Compile**

```bash
# Test compilation of all modified files
git diff --name-only | grep "\.py$" | while read file; do
    python3 -m py_compile "$file" 2>&1 || echo "❌ FAILED: $file"
done
```

**5.2 Run Smoke Tests**

```bash
make smoke
# MUST show: 10/10 PASSING
```

**5.3 Check Syntax Error Reduction**

```bash
python3 -c "
import ast
from pathlib import Path

count = 0
exclude = ['.venv', 'node_modules', 'b1db8919', 'gemini-dev', 'labs']

for f in Path('.').rglob('*.py'):
    if any(x in str(f) for x in exclude):
        continue
    try:
        ast.parse(f.read_text())
    except SyntaxError:
        count += 1

print(f'Remaining syntax errors: {count}')
print(f'Fixed: {128 - count} out of 128')
print(f'Success rate: {((128 - count) / 128 * 100):.1f}%')
"
```

**Success Criteria:**
- ✅ Fixed at least 100/128 errors (78%+ success rate)
- ✅ All critical files (core/, matriz/) compile
- ✅ Smoke tests passing (10/10)

---

### Phase 6: Commit and Report

**6.1 Review Changes**

```bash
# Check what was modified
git status --short
git diff --stat

# Spot-check 5 random files
git diff core/consciousness/natural_language_interface.py | head -50
git diff matriz/consciousness/reflection/awareness_system.py | head -50
```

**6.2 Commit Fixes**

```bash
git add -A

git commit -m "$(cat <<'EOF'
fix(syntax): resolve 128 production syntax errors across 8 subsystems

Problem:
- 128 real syntax errors blocking code compilation
- Errors remained after Black formatter (PR #870)
- Primary issues: unexpected indents (80), invalid syntax (24), missing blocks (18)
- Files unusable for imports, linting, or refactoring

Solution:
- Fixed indented docstrings at file start
- Restored missing function/class context for orphaned try blocks
- Completed or removed incomplete multiline imports
- Added missing code after except blocks
- Applied autopep8 for simple indentation fixes
- Documented unfixable cases for manual review

Impact:
- Files fixed: X/128 (Y% success rate)
- Subsystems affected: core/, matriz/, lukhas_website/, qi/, bridge/, vivox/
- Smoke tests: ✅ 10/10 passing
- Remaining syntax errors: X (down from 128)

Breakdown by subsystem:
- core/: X/44 fixed
- matriz/: X/28 fixed
- lukhas_website/: X/10 fixed
- qi/: X/28 fixed
- bridge/: X/8 fixed
- vivox/: X/8 fixed
- tools/: X/1 fixed
- tests/: X/1 fixed

Validation:
\`\`\`bash
# Before
python3 -c "import ast; count=0; [count:=count+1 for f in Path('.').rglob('*.py') if not any(x in str(f) for x in ['.venv','b1db8919','gemini']) try: ast.parse(f.read_text()) except: pass]; print(count)" → 128 errors

# After
python3 -m py_compile [modified files] → X files compile successfully
make smoke → 10/10 PASSED
\`\`\`

Remaining Work:
- X files documented in /tmp/unfixable_syntax_errors.md
- May require manual review or removal if unused

🤖 Generated with Gemini Code Assist
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

**6.3 Create Summary Report**

```bash
cat > /tmp/syntax_fix_report.md << 'EOF'
# Syntax Error Fix Report - November 2, 2025

## Summary
- **Total Errors**: 128 production syntax errors
- **Fixed**: X errors (Y%)
- **Remaining**: X errors
- **Time Taken**: ~3 hours

## Fixes by Pattern

### Pattern 1: Indented Docstrings (X files)
- Removed leading indentation from file-start docstrings
- Examples: integration_bridge.py, plugin_loader.py

### Pattern 2: Orphaned Try Blocks (X files)
- Restored missing function/class context
- Added proper method definitions around orphaned code

### Pattern 3: Incomplete Imports (X files)
- Fixed multiline import syntax
- Removed or commented unused imports

### Pattern 4: Missing Except Bodies (X files)
- Added proper error handling code
- Logged exceptions appropriately

## Validation Results
\`\`\`bash
make smoke → 10/10 PASSED ✅
Files compiled: X/X ✅
Import errors: 0 ✅
\`\`\`

## Next Steps
1. Review unfixable cases: /tmp/unfixable_syntax_errors.md
2. Consider removing unused corrupted files
3. Continue with remaining linting improvements

---
🤖 Generated by Gemini Code Assist
📅 November 2, 2025
EOF

cat /tmp/syntax_fix_report.md
```

---

## Error Patterns Reference

### Pattern 1: Indented File Start
```python
# BROKEN
    """
    Module docstring
    """

# FIXED
"""
Module docstring
"""
```

### Pattern 2: Orphaned Try Block
```python
# BROKEN (missing function context)
        try:
            do_something()
        except Exception as e:
            log_error(e)

# FIXED (add method wrapper)
    async def initialize(self):
        """Initialize component."""
        try:
            do_something()
        except Exception as e:
            log_error(e)
```

### Pattern 3: Incomplete Import
```python
# BROKEN
from module import (

# FIXED (option 1: complete it)
from module import (
    Thing1,
    Thing2,
)

# FIXED (option 2: remove if unused)
# from module import ...  # TODO: Complete or remove
```

### Pattern 4: Empty Except
```python
# BROKEN
except Exception as e:


next_code()

# FIXED
except Exception as e:
    logger.error(f"Error: {e}")
    # Or: pass  # Intentionally ignore

next_code()
```

---

## Success Criteria

### Required (Must Pass)
- ✅ At least 100/128 errors fixed (78%+ success rate)
- ✅ All core/ files compile (44 files)
- ✅ All matriz/ files compile (28 files)
- ✅ Smoke tests passing (10/10)
- ✅ No import errors introduced
- ✅ Changes committed with proper message

### Desired (Nice to Have)
- ✅ 110+/128 errors fixed (85%+ success rate)
- ✅ All subsystems fully working (core, matriz, lukhas_website, qi)
- ✅ Documentation for unfixable cases
- ✅ Automated fix script created for future use

---

## Common Issues & Solutions

### Issue 1: autopep8 Doesn't Fix
**Solution:** Manual inspection needed. Check git history:
```bash
git log -p --follow -- path/to/file.py | less
```

### Issue 2: File Seems Unused
**Solution:** Check usage before deleting:
```bash
grep -r "from path.to.module import" . --exclude-dir=.venv
grep -r "import path.to.module" . --exclude-dir=.venv
# If 0 results, safe to comment out or remove
```

### Issue 3: Unclear Original Intent
**Solution:** Add TODO comment and move on:
```python
# TODO(gemini): File corrupted during refactoring
# Original intent unclear - needs manual review
# See: /tmp/unfixable_syntax_errors.md
```

### Issue 4: Smoke Tests Fail
**Solution:** STOP immediately. Revert changes:
```bash
git status
git diff > /tmp/attempted_fixes.patch
git restore .
# Report failure
```

---

## Communication Protocol

### Progress Updates
Report after each phase:
1. **Analysis complete**: "✅ Found 128 errors: 80 indent, 24 syntax, 18 blocks"
2. **Pattern fixes**: "✅ Fixed X indented docstrings, Y orphaned blocks"
3. **Automated fixes**: "✅ autopep8 fixed X files"
4. **Manual fixes**: "✅ Manually fixed X critical files"
5. **Validation**: "✅ X/128 fixed (Y%), smoke tests passing"
6. **Committed**: "✅ Changes committed, report generated"

### Issues/Blockers
- **Smoke tests fail**: STOP, revert, report
- **Too many unfixable**: Continue to 100 fixes minimum, document rest
- **Unclear patterns**: Document in /tmp/unfixable_syntax_errors.md

---

## Expected Deliverables

1. **Git Commit** (today)
   - X files fixed
   - Comprehensive commit message
   - All changes validated

2. **Summary Report** (today)
   - /tmp/syntax_fix_report.md
   - Breakdown by pattern and subsystem
   - Validation results

3. **Unfixable Cases Doc** (if needed)
   - /tmp/unfixable_syntax_errors.md
   - List of files that need manual review
   - Recommendations for each

---

## Notes

- **Timeline**: 3-4 hours including validation
- **Risk Level**: MEDIUM - syntax fixes can break code
- **Dependencies**: None - can start immediately
- **Blocking**: Unblocks all further linting/refactoring work
- **Review**: Validate each fix compiles before moving on

---

**Ready to begin?** Start with Phase 1 analysis and report findings!

🤖 Task created by Claude Code for Gemini Code Assist
📅 Created: November 2, 2025
⏰ Expected completion: Same day
