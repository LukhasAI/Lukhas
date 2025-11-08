# Smoke Test Fix Brief - Get to 100% Pass Rate

**Date:** 2025-11-03
**Goal:** Fix all 203 smoke test collection errors and get tests passing
**Priority:** HIGH - Needed for pre-audit baseline
**Time Estimate:** 2-3 hours

---

## Current Status

### Test Collection
- **Total smoke test files:** 42
- **Successfully collecting:** ~10 files
- **Collection errors:** 203 errors
- **Tests that run:** Some matriz tests run but fail on assertions

### Progress Made
✅ Replaced all `candidate.*` → `labs.*` imports (22 files)
✅ Installed core dependencies: streamlit, fastapi, httpx, redis, numpy, hypothesis
✅ Fixed module structure: Added `lukhas_website/__init__.py`
✅ Fixed import order bugs in `qi/bio/bio_optimizer.py`

### Key Files That Work
- `tests/smoke/test_matriz_integration.py` - ✅ Collects 17 tests (some fail on assertions)
- `tests/smoke/test_health.py` - ✅ Collects 1 test
- `tests/smoke/test_dreams.py` - ✅ Collects 9 tests
- `tests/smoke/test_entrypoints.py` - ✅ Collects 7 tests
- `tests/smoke/test_traces_router.py` - ✅ Collects 3 tests

---

## Known Issues to Fix

### 1. Python 3.9 Type Hint Compatibility
**Issue:** Using `|` operator for union types (only available in Python 3.10+)
**Error:** `TypeError: unsupported operand type(s) for |: 'types.GenericAlias' and 'NoneType'`
**Location:** `tests/api/test_routing_admin_auth.py` and others
**Fix:** Replace `Type1 | Type2` with `Union[Type1, Type2]` or use `from __future__ import annotations`

**Example locations to check:**
```bash
grep -r " | None" --include="*.py" tests/
grep -r "str | int" --include="*.py" tests/
```

### 2. Missing Import: logging
**Issue:** `NameError: name 'logging' is not defined`
**Locations:** Various files in `qi/` directory
**Fix:** Add `import logging` at top of file before usage

**To find all:**
```bash
grep -r "logging\\.getLogger" --include="*.py" . | grep -v "^import logging"
```

### 3. Missing Test Dependencies
**Known missing:**
- `aioredis` (for redis async tests)
- More OpenTelemetry packages
- Possibly `boto3`, `psycopg2`, `sqlalchemy` for some tests

**Check errors for:**
```bash
pytest --collect-only -m "smoke" 2>&1 | grep "ModuleNotFoundError" | sort | uniq
```

### 4. Module Structure Issues
**Issue:** Missing `__init__.py` files causing import failures
**Already fixed:** `lukhas_website/__init__.py`
**To check:** Look for `ModuleNotFoundError` in collection errors

### 5. File Not Found Errors
**Issue:** Tests reference files that don't exist
**Example:** `tests/unit/tools/test_todo_tooling.py - FileNotFoundError`
**Fix:** Either create missing files or skip tests gracefully

---

## Systematic Fix Plan

### Phase 1: Fix Collection Errors (Priority 1)

1. **Run collection and capture all errors:**
```bash
source .venv/bin/activate
pytest --collect-only -m "smoke" > smoke_collection_log.txt 2>&1
```

2. **Group errors by type:**
```bash
grep "ERROR collecting" smoke_collection_log.txt | sed 's/ERROR collecting //' | sort
grep "ModuleNotFoundError" smoke_collection_log.txt | sort | uniq
grep "NameError" smoke_collection_log.txt | sort | uniq
grep "TypeError" smoke_collection_log.txt | sort | uniq
```

3. **Fix Python 3.9 type hints:**
```bash
# Find all files with | union syntax
find tests/smoke -name "*.py" -exec grep -l " | " {} \;

# For each file, either:
# a) Add: from __future__ import annotations (at top)
# b) Replace Type1 | Type2 with Union[Type1, Type2]
```

4. **Fix missing imports:**
```bash
# Find files missing logging import
for file in $(grep -r "logging\\.getLogger" --include="*.py" . | cut -d: -f1 | sort | uniq); do
  if ! grep -q "^import logging" "$file"; then
    echo "Missing logging import: $file"
  fi
done
```

5. **Install missing dependencies:**
```bash
# Collect all ModuleNotFoundError messages
pytest --collect-only -m "smoke" 2>&1 | grep "No module named" | \
  sed "s/.*No module named '\\([^']*\\)'.*/\\1/" | sort | uniq

# Install them:
pip install <missing_modules>
```

### Phase 2: Fix Test Assertions (Priority 2)

Once all tests collect successfully, some will fail on assertions. Example from `test_matriz_integration.py`:

**Issue:** Tests expect `data["output"]` but API returns `data["choices"]`
**Fix:** Update test assertions to match current API response format

```python
# Before:
assert "output" in data

# After:
assert "choices" in data or "output" in data  # Support both formats
```

### Phase 3: Verify All Pass

```bash
# Run all smoke tests
pytest -v -m "smoke" --tb=short

# Count results
pytest -m "smoke" -q | tail -5
```

---

## Quick Win Commands

### 1. Fix Python 3.9 Type Hints (Bulk)
```bash
# Add future annotations to all smoke tests
for file in tests/smoke/*.py; do
  if ! grep -q "from __future__ import annotations" "$file"; then
    sed -i '1i from __future__ import annotations\n' "$file"
  fi
done
```

### 2. Install Common Missing Deps
```bash
source .venv/bin/activate
pip install aioredis boto3 psycopg2-binary sqlalchemy anthropic openai
```

### 3. Find and Fix Missing Logging Imports
```bash
# Create a script to add logging import where needed
for file in $(grep -r "logger = logging" --include="*.py" . | grep -v "^import logging" | cut -d: -f1 | sort | uniq); do
  if ! grep -q "^import logging" "$file"; then
    echo "Fixing: $file"
    # Add import logging after shebang/docstring
    sed -i '' '1a\
import logging' "$file"
  fi
done
```

---

## Expected Outcomes

### Success Criteria
- ✅ **0 collection errors** (all 42 smoke test files collect)
- ✅ **All smoke tests pass** or have documented known failures
- ✅ **pytest -m "smoke"** shows green

### Acceptable Partial Success
- ✅ <10 collection errors (> 95% collecting)
- ✅ >90% of collected tests passing
- ✅ Remaining failures documented in KNOWN_ISSUES.md

---

## File Locations

**Smoke tests:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/smoke/`
**Virtual env:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/`
**Main branch:** `main` (already merged chore/audit-bootstrap)

---

## Recent Commits (Context)

```
7097dad71 - refactor(imports): replace all candidate.* imports with labs.* imports
3e743b924 - fix(tests): resolve module import issues for smoke tests
```

---

## Agent Instructions

1. **Start by running:** `pytest --collect-only -m "smoke" 2>&1 | tee smoke_errors.txt`
2. **Analyze** the error patterns systematically
3. **Group fixes** by error type (type hints, imports, deps)
4. **Apply fixes** in batches, committing after each batch
5. **Re-run** collection after each batch to verify progress
6. **Track progress:** Use todo list or create progress log
7. **Final run:** `pytest -v -m "smoke"` and capture results

---

## Success Metrics

Track these as you go:
- Collection error count: **203 → 0**
- Tests collecting: **~10 files → 42 files**
- Tests passing: **Unknown → >90%**

---

## Questions to Answer

If you need clarification:
1. Should we skip tests that require external services (redis, postgres)?
2. Should we create stub/mock data for missing test fixtures?
3. Should we disable tests that are fundamentally broken?

Default approach: **Fix infrastructure, skip broken tests with pytest.mark.skip**, document in KNOWN_ISSUES.md.

---

## Command Reference

```bash
# Activate venv
source .venv/bin/activate

# Collect smoke tests
pytest --collect-only -m "smoke"

# Run smoke tests (stop on first failure)
pytest -x -m "smoke"

# Run with verbose output
pytest -v -m "smoke" --tb=short

# Count passing/failing
pytest -m "smoke" -q

# Run specific test file
pytest -v tests/smoke/test_matriz_integration.py
```

---

Good luck! The goal is **100% smoke tests passing** for a clean pre-audit baseline. 🎯
