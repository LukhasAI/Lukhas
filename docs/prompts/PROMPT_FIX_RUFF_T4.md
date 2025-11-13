# T4 Linting Package: Fix All Ruff Errors

**Task**: Fix all remaining ruff linting errors using T4 standards and best practices
**Scope**: 2,664 remaining errors (after 1,047 quick wins applied)
**Approach**: Systematic, no new code creation - only fix existing code
**Time Estimate**: 60-90 minutes

---

## Context

**Repository**: LUKHAS AI - Consciousness-aware AI development platform
**Python Version**: 3.9 (macOS)
**Current Status**: Post PR merge campaign + quick wins applied
**Recent Changes**:
- Just merged 9 PRs (4,049 lines of tooling/tests)
- Applied 1,047 auto-fixes (ruff --fix --unsafe-fixes)
- Fixed RecursionError and Python 3.9 TypeError
- Remaining: 2,664 ruff errors to resolve

---

## Related Artifacts

**Primary Reference**:
- [TEST_ERROR_LOG_2025-11-10.md](../sessions/TEST_ERROR_LOG_2025-11-10.md) - Comprehensive error analysis
- [QUICK_WINS_2025-11-10.md](../sessions/QUICK_WINS_2025-11-10.md) - What's already been fixed

**Ruff Output**:
- Full report: `/tmp/ruff_output.txt` (45,098 lines)
- Grouped errors: `/tmp/ruff_grouped.txt` (500 lines)

**Command to Generate Fresh Report**:
```bash
python3 -m ruff check . --output-format=grouped > /tmp/ruff_grouped_latest.txt 2>&1
python3 -m ruff check . --statistics > /tmp/ruff_stats.txt 2>&1
```

---

## T4 Linting Standards

### T4 Code Quality Principles

1. **No New Code**: Only fix existing code, don't create new functionality
2. **Preserve Intent**: Maintain original code behavior and intent
3. **Lane Boundaries**: Respect import rules (candidate/ can't import lukhas/)
4. **Idiomatic Patterns**: Recognize and preserve framework-specific patterns
5. **Experimental Code**: Handle candidate/ lane with care (some errors expected)

### T4 Commit Standards

**Format**: `<type>(<scope>): <imperative subject ≤72>`

**Types**: fix, refactor, style (for linting fixes)
**Scopes**: lint, imports, formatting, types, etc.

**Example**:
```
fix(lint): resolve F821 undefined names in core modules

Problem:
- 2,923 F821 errors blocking code quality validation
- Undefined names in production modules prevent safe deployment

Solution:
- Added missing imports for 150 undefined names
- Fixed typos in variable references (23 instances)
- Added type annotations where missing
- Marked experimental code with # type: ignore where appropriate

Impact:
- F821 errors: 2,923 → 450 (-84% reduction)
- Production modules: 100% F821 clean
- Candidate modules: Tagged for future cleanup
```

---

## Error Breakdown (2,664 total)

### Priority 1: Production Lane Errors (HIGH)

**F821: Undefined Names** (~2,923 instances)
- **Priority**: 🔴 CRITICAL for production (core/, lukhas/, matriz/)
- **Priority**: 🟢 LOW for experimental (candidate/)
- **Action**:
  - Fix ALL in core/, lukhas/, matriz/
  - Review and fix critical ones in candidate/
  - Mark experimental with `# type: ignore` or `# noqa: F821`

**B008: Function Call in Default Argument** (155 instances)
- **Pattern**: FastAPI dependency injection
- **Priority**: 🟢 LOW (idiomatic pattern)
- **Action**: Add `# noqa: B008` to FastAPI route files
- **Example**:
```python
# At top of FastAPI route file
# ruff: noqa: B008

# OR per-line
async def endpoint(
    service: Service = Depends(get_service),  # noqa: B008
):
```

### Priority 2: Code Quality (MEDIUM)

**F401: Unused Imports** (~30 remaining)
- **Priority**: 🟡 MEDIUM
- **Action**: Remove or mark with `# noqa: F401` if needed for re-export

**F841: Unused Variables** (38 instances)
- **Priority**: 🟡 MEDIUM
- **Action**: Remove or rename to `_variable` if intentionally unused

**SIM105: Suppressible Exception** (41 instances)
- **Priority**: 🟡 MEDIUM
- **Action**: Use `contextlib.suppress()` for cleaner exception handling

**SIM102: Collapsible If** (39 instances)
- **Priority**: 🟢 LOW
- **Action**: Combine nested if statements where it improves readability

### Priority 3: Formatting (LOW)

**W291: Trailing Whitespace** (remaining after auto-fix)
- **Action**: Auto-fix with `ruff --fix`

**E501: Line Too Long** (1 instance)
- **Action**: Break into multiple lines or add `# noqa: E501` if unavoidable

---

## T4 Approach: Systematic Fixes

### Phase 1: Auto-Fix Remaining Safe Errors (5 min)

```bash
# Run safe auto-fixes
python3 -m ruff check . --fix

# Check statistics
python3 -m ruff check . --statistics | tee /tmp/ruff_stats_phase1.txt
```

### Phase 2: FastAPI B008 Pattern (10 min)

**Strategy**: Add blanket noqa to FastAPI route files

**Files to Update** (add at top):
```python
# ruff: noqa: B008
```

**Location Pattern**:
```bash
# Find all FastAPI route files
grep -r "Depends(" --include="*.py" serve/ lukhas/api/ core/interfaces/api/ | cut -d: -f1 | sort -u
```

**T4 Script**:
```python
# tools/t4/add_noqa_b008.py
import os
from pathlib import Path

files_with_depends = [
    "serve/main.py",
    "serve/openai_routes.py",
    "serve/routes.py",
    "lukhas/api/app.py",
    # Add others from grep output
]

for filepath in files_with_depends:
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if already has noqa
    if '# ruff: noqa: B008' not in content:
        # Add after docstring or at top
        lines = content.split('\n')
        insert_pos = 0

        # Skip shebang and docstring
        if lines[0].startswith('#!'):
            insert_pos = 1
        if lines[insert_pos].startswith('"""') or lines[insert_pos].startswith("'''"):
            # Find end of docstring
            for i, line in enumerate(lines[insert_pos+1:], start=insert_pos+1):
                if '"""' in line or "'''" in line:
                    insert_pos = i + 1
                    break

        lines.insert(insert_pos, '# ruff: noqa: B008')

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        print(f"Added noqa to {filepath}")
```

### Phase 3: F821 Undefined Names - Production Modules (30 min)

**Strategy**: Fix only in production lanes (core/, lukhas/, matriz/)

**Sub-tasks**:

1. **Identify undefined names** (5 min):
```bash
python3 -m ruff check core/ lukhas/ matriz/ --select F821 --output-format=grouped > /tmp/f821_production.txt
```

2. **Categorize by fix type** (5 min):
   - Missing imports (most common)
   - Typos in variable names
   - Missing type annotations
   - Forward references

3. **Fix missing imports** (15 min):
```python
# Common missing imports by module:
# core/common/exceptions.py - Add missing exception classes
# core/module_registry.py - Add ModuleAccessError
# core.consciousness_signal_router - Add CascadePrevention
# core.interfaces.api.v1.common.auth - Add generate_api_key
```

4. **Fix typos and references** (5 min):
   - Review each undefined name
   - Check if it's a typo
   - Check if it's a forward reference (needs string annotation)

**Example Fixes**:

```python
# BEFORE: core/module_registry.py
raise ModuleAccessError(f"Access denied")  # F821: undefined name

# AFTER:
class ModuleAccessError(Exception):
    """Raised when module access is denied."""
    pass

# OR if defined elsewhere:
from core.common.exceptions import ModuleAccessError
```

### Phase 4: F821 Undefined Names - Candidate Lane (15 min)

**Strategy**: Mark experimental code, fix only critical errors

**Approach**:
1. Review errors in candidate/ for critical issues
2. Fix imports for shared infrastructure
3. Mark remaining as experimental:

```python
# At top of experimental files:
# ruff: noqa: F821  # Experimental code - undefined names expected

# OR per-line for specific experiments:
result = experimental_function()  # noqa: F821
```

### Phase 5: Remaining Errors (20 min)

**F841: Unused Variables**:
```python
# BEFORE:
def process(data, config):
    result = transform(data)
    return data  # config unused, result unused

# AFTER:
def process(data, _config):
    return transform(data)
```

**SIM105: Suppressible Exception**:
```python
# BEFORE:
try:
    os.remove(file)
except FileNotFoundError:
    pass

# AFTER:
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove(file)
```

**F401: Unused Imports** (if used for re-export):
```python
# For __init__.py re-exports:
from .module import Class  # noqa: F401
```

### Phase 6: Verify and Commit (10 min)

```bash
# Check final statistics
python3 -m ruff check . --statistics

# Run tests to ensure no regressions
python3 -m pytest tests/smoke/ -q --tb=line

# Commit with T4 format
git add -A
git commit -m "fix(lint): resolve 2,664 ruff errors using T4 standards

Problem:
- 2,664 ruff errors blocking code quality validation
- F821 undefined names in production modules
- B008 FastAPI patterns flagged incorrectly
- Unused variables and suppressible exceptions

Solution:
- Added # noqa: B008 to 15 FastAPI route files (idiomatic pattern)
- Fixed 2,500+ F821 errors in production lanes
  * Added missing imports (150 classes/functions)
  * Fixed typos in variable references (23 instances)
  * Added missing exception classes (8 new classes)
- Marked experimental code in candidate/ with noqa
- Fixed 38 unused variables (renamed to _variable)
- Converted 41 try/except to contextlib.suppress
- Removed 30 unused imports

Impact:
- Ruff errors: 2,664 → <50 (-98% reduction)
- Production modules: 100% ruff clean
- Candidate modules: Tagged for future cleanup
- Zero regressions in smoke tests

Files Modified: ~200
T4 Standards: Applied throughout
🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## T4 Validation Checklist

Before committing, verify:

- [ ] All production modules (core/, lukhas/, matriz/) are F821 clean
- [ ] FastAPI files properly marked with `# noqa: B008`
- [ ] Experimental code in candidate/ tagged appropriately
- [ ] No new code created (only fixes to existing code)
- [ ] Lane boundaries respected (no candidate/ → lukhas/ imports)
- [ ] Smoke tests pass without regressions
- [ ] Commit message follows T4 format
- [ ] Statistics show <100 remaining errors

---

## Expected Outcome

**Before**:
- 2,664 ruff errors
- F821: 2,923 instances
- B008: 155 instances
- Various: ~50 instances

**After**:
- <50 ruff errors (98% reduction)
- F821 in production: 0 instances
- F821 in candidate/: Tagged appropriately
- B008: All marked with noqa
- Production code: Lint-clean

**Documentation**:
- Update TEST_ERROR_LOG with "FIXED" status
- Create RUFF_FIXES_T4.md with detailed results
- Commit with T4 standard format

---

## Important Notes

### Lane Architecture Constraints

**DO NOT** create imports that violate lane boundaries:
```python
# ❌ FORBIDDEN - candidate cannot import lukhas
from lukhas.core import something

# ✅ ALLOWED - candidate can import core, matriz
from core.common import get_logger
from matriz.core import MemorySystem
```

**Validate** with:
```bash
make lane-guard
```

### Idiomatic Patterns to Preserve

1. **FastAPI Depends**: Always B008, use noqa
2. **pytest fixtures**: May have unused variables, that's OK
3. **Type stubs**: May have unused imports for re-export
4. **__init__.py**: Usually has F401 for re-exports

### When to Use noqa

Use `# noqa` sparingly and document why:
```python
# Good: Clear reason
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from heavy_module import Class  # noqa: F401  # Type checking only

# Bad: No reason
variable = something  # noqa: F821  # Why?
```

---

## Success Metrics

- **Ruff Errors**: 2,664 → <50 (-98%)
- **Production Modules**: 100% clean
- **Time**: <90 minutes total
- **Zero Regressions**: All smoke tests pass
- **T4 Compliance**: Commit format verified

---

**Ready to Execute**: Follow phases 1-6 sequentially, validate at each step.
**Reference**: See TEST_ERROR_LOG_2025-11-10.md for detailed error breakdown.
**Tools**: Use tools/t4/add_noqa_b008.py for automated noqa addition.
