# Autonomous Guide: Expand Test Coverage to 75%+ (Production Lane)

**Goal:** Achieve 75%+ test coverage for lukhas/ production lane
**Priority:** High (Long-term)
**Estimated Time:** 20-30 hours over multiple sprints
**Compatible With:** Claude Code, Codex, Copilot

---

## Current Status
- **Test Files:** 716
- **Recent Addition:** +1,121 lines this session
- **Collection Errors:** 223 (blocking accurate measurement)
- **Target:** 75%+ coverage for lukhas/ lane

---

## Phase 1: Fix Test Collection (CRITICAL - 3 hours)

```bash
# Run pytest to identify collection errors
python3 -m pytest --co 2>&1 | grep "ERROR" > /tmp/collection_errors.txt

# Fix import errors (most common cause)
# Pattern: Add missing __init__.py files
find lukhas/ core/ -type d -exec touch {}/__init__.py \;

# Validate
python3 -m pytest --co -q
# Goal: 0 collection errors
```

---

## Phase 2: Measure Current Coverage (1 hour)

```bash
# Run coverage on production lane only
python3 -m pytest --cov=lukhas --cov-report=html --cov-report=term tests/

# View report
open htmlcov/index.html

# Identify low-coverage modules
python3 -m pytest --cov=lukhas --cov-report=term-missing | \
  grep -E "lukhas/.*\.py" | sort -k4 -n
```

---

## Phase 3: Prioritize Coverage Gaps (30 minutes)

Focus on:
1. **lukhas/core/** - Core functionality
2. **lukhas/api/** - API endpoints
3. **lukhas/identity/** - Authentication
4. **lukhas/consciousness/** - Consciousness features

Ignore for now:
- candidate/ (experimental)
- examples/ (documentation)
- tools/ (utilities)

---

## Phase 4: Write Missing Tests (15-20 hours)

### Strategy: Test File Pattern

For each uncovered module `lukhas/foo/bar.py`:
1. Create `tests/unit/lukhas/foo/test_bar.py`
2. Target 80%+ coverage for that module
3. Run smoke tests after each file
4. Commit in batches of 3-5 test files

**Example:**
```python
# tests/unit/lukhas/core/test_orchestrator.py
import pytest
from lukhas.core.orchestrator import Orchestrator

def test_orchestrator_init():
    orch = Orchestrator()
    assert orch is not None

def test_orchestrator_process():
    orch = Orchestrator()
    result = orch.process({"input": "test"})
    assert result["status"] == "success"

# Add 5-10 tests per module
```

### Batching Strategy
```bash
# Write tests for 5 modules
# Run coverage
pytest --cov=lukhas/core --cov-report=term tests/unit/lukhas/core/

# If coverage improved, commit
git add tests/unit/lukhas/core/
git commit -m "test(core): add coverage for 5 core modules

Coverage improvement:
- lukhas/core/orchestrator.py: 45% → 82%
- lukhas/core/router.py: 30% → 75%
...

Overall core/ coverage: XX% → YY%"
```

---

## Phase 5: Integration Tests (5-8 hours)

Add end-to-end tests in `tests/integration/`:
- API endpoint tests
- Multi-component workflows
- Error handling paths

---

## Success Criteria
- ✅ 0 test collection errors
- ✅ lukhas/ coverage >75%
- ✅ All critical paths covered
- ✅ Smoke tests 10/10 PASS

**Timeline:** 4-6 weeks (incremental sprints)
**Risk:** Low (additive only, no changes to production code)
