# 🚨 CRITICAL: 138 Jules Test Files Have Import Errors

**Priority:** P0 - Blocking  
**Component:** Tests / Import Structure  
**Affected:** Jules test suite (50+ recent test files)  
**Assignee:** @codex  

## 🔍 Problem Summary

**138 test files cannot be collected** due to `ModuleNotFoundError` and import path issues. This affects Jules' recently merged test PRs (32 PRs over last 2 days).

### Impact
- ❌ 138 test files fail at collection (can't even run)
- ❌ Zero tests executing from affected files  
- ❌ Unknown test coverage in Jules-contributed code
- ⚠️  Indicates structural import path issues

## 📊 Error Categories

### Top Missing Modules (by frequency)

| Count | Missing Module | Likely Cause |
|-------|---------------|--------------|
| 5 | `opentelemetry.exporter` | Missing optional dependency |
| 4 | `aka_qualia.core` | Incorrect import path or missing __init__.py |
| 3 | `monitoring.drift_manager` | Module moved/renamed |
| 3 | `labs.core.orchestration.async_orchestrator` | Deep import path issue |
| 3 | `governance.schema_registry` | Module not in PYTHONPATH |
| 2 | `lukhas_website.core` | Website module not accessible from tests |
| 2 | `governance.guardian_system` | Import path mismatch |
| 2 | `core.matriz` | Matriz integration issue |
| 2 | `core.ethics.guardian_drift_bands` | Deep import restructuring |
| 2 | `async_manager` | Missing dependency or moved |
| 2 | `adapters.openai.api` | Adapter import path issue |
| 2 | `_bridgeutils` | Internal bridge module not exposed |

### Additional Issues (1 occurrence each)
- `candidate.consciousness` modules
- `core.security.security_integration`
- `core.interfaces.as_agent.sys.nias.narration_controller`
- `ethics.core`
- Various script imports (`scripts.wavec_snapshot`, `scripts.todo_migration`, etc.)

## 🔬 Detailed Examples

### Example 1: test_dream_adapter.py
```python
# File: tests/core/orchestration/test_dream_adapter.py:32
from core.orchestration.brain.unified_integration.adapters.dream_adapter import DreamEngineAdapter

# Error in: core/orchestration/brain/unified_integration/adapters/dream_adapter.py:14
from ..unified_integration import UnifiedIntegration
# ModuleNotFoundError: No module named 'core.orchestration.brain.unified_integration.unified_integration'
```

**Issue:** Circular or incorrect relative import in `dream_adapter.py`

### Example 2: test_indexes_api.py  
```python
# File: tests/memory/test_indexes_api.py
from adapters.openai.api import OpenAIService

# ModuleNotFoundError: No module named 'adapters.openai.api'
```

**Issue:** Import path doesn't match actual module structure

### Example 3: test_main_api.py
```python
# File: tests/api/test_main_api.py
from _bridgeutils import ...

# ModuleNotFoundError: No module named '_bridgeutils'
```

**Issue:** Internal module not exposed or import path issue

## 🎯 Required Actions

### Phase 1: Diagnostic (URGENT)
1. **Verify module structure:**
   ```bash
   # Check if modules exist
   find . -name "unified_integration.py" -o -name "drift_manager.py" | grep -v __pycache__
   
   # Check __init__.py presence
   find core/ -type d -exec test -f {}/__init__.py \; -o -print
   ```

2. **Check PYTHONPATH configuration:**
   ```bash
   # Verify test runner PYTHONPATH
   pytest --collect-only -v tests/ 2>&1 | grep "rootdir"
   ```

3. **Identify import patterns:**
   ```bash
   # Find all imports matching error patterns
   grep -r "from core.orchestration.brain.unified_integration" tests/
   grep -r "from adapters.openai" tests/
   grep -r "from _bridgeutils" tests/
   ```

### Phase 2: Fix Patterns (SYSTEMATIC)

**Pattern A: Missing `__init__.py` files**
```bash
# Create missing __init__.py files
find core/orchestration/brain/unified_integration -type d -exec touch {}/__init__.py \;
```

**Pattern B: Incorrect relative imports**
```python
# BEFORE (dream_adapter.py:14)
from ..unified_integration import UnifiedIntegration

# AFTER - Fix depending on actual structure:
# Option 1: If unified_integration.py exists in same directory
from .unified_integration import UnifiedIntegration

# Option 2: If it's in parent directory  
from ...unified_integration import UnifiedIntegration

# Option 3: Use absolute import
from core.orchestration.brain.unified_integration_module import UnifiedIntegration
```

**Pattern C: Missing optional dependencies**
```bash
# Install missing observability deps
pip install opentelemetry-exporter-otlp opentelemetry-exporter-prometheus
```

**Pattern D: Module renamed/moved**
```bash
# Find actual location of moved modules
find . -name "drift_manager.py" -not -path "./.git/*"
# Update imports or create compatibility shim
```

### Phase 3: Validation (COMPREHENSIVE)

1. **Test collection check:**
   ```bash
   pytest --collect-only tests/ 2>&1 | tee collection_results.txt
   grep "ERROR collecting" collection_results.txt | wc -l
   # Target: 0 errors
   ```

2. **Import validation script:**
   ```python
   # tools/validate_test_imports.py
   import ast
   import sys
   from pathlib import Path
   
   def check_imports(test_file):
       """Validate all imports in test file can be resolved"""
       with open(test_file) as f:
           tree = ast.parse(f.read())
       
       for node in ast.walk(tree):
           if isinstance(node, (ast.Import, ast.ImportFrom)):
               # Validate each import
               pass
   ```

3. **Run fixed tests:**
   ```bash
   pytest tests/core/orchestration/test_dream_adapter.py -v
   pytest tests/memory/test_indexes_api.py -v
   # Verify tests execute (even if they fail - collection success!)
   ```

## 📋 Files Requiring Manual Review

### High Priority (Multiple import errors)
- `core/orchestration/brain/unified_integration/adapters/dream_adapter.py`
- `tests/core/orchestration/test_dream_adapter.py`
- `tests/memory/test_indexes_api.py`
- `tests/api/test_main_api.py`
- All tests importing from `candidate.consciousness`

### Medium Priority (Single import errors)
- Tests importing `lukhas_website.core`
- Tests importing `governance.*` modules
- Tests importing `scripts.*` modules

## 🔧 Codex-Specific Instructions

**Approach:**
1. Start with **top 5 most frequent errors** (opentelemetry, aka_qualia, monitoring, labs, governance)
2. For each error pattern:
   - Locate actual module location
   - Verify `__init__.py` chain
   - Create fix (add __init__, fix relative import, or create shim)
   - Validate with `pytest --collect-only`
3. Move to next error pattern
4. **DO NOT** skip validation between fixes

**Quality Standards:**
- ✅ Every fix must pass `pytest --collect-only` for affected tests
- ✅ Document import path decisions in comments
- ✅ Create `_compat.py` shims for major restructuring
- ✅ Update `conftest.py` if PYTHONPATH adjustments needed

**Testing Protocol:**
```bash
# After each fix batch
pytest --collect-only tests/ 2>&1 | grep "ERROR collecting" | wc -l
# Must show reduction in error count

# Final validation
pytest tests/ -v --tb=short --maxfail=10
# Aim for collection success, execution can fail
```

## 📊 Success Criteria

- [ ] **0 import errors** during test collection
- [ ] All 138 previously failing test files collect successfully
- [ ] Clear documentation of any intentional skips
- [ ] `conftest.py` updated with proper PYTHONPATH if needed
- [ ] All fixes committed with T4 annotations

## 🎯 T4 Integration

This issue represents **138 F821/E999 violations** (undefined names/syntax errors at import time).

**T4 Annotation Format:**
```python
# For files that need import path adjustments
# TODO[T4-ISSUE]: {"id":"file_py_L10","code":"F821","ticket":"GH-XXXX","owner":"codex","status":"in-progress","reason":"Import path mismatch - module restructuring needed","estimate":"2h","priority":"critical","dependencies":"PYTHONPATH,__init__"}
```

## 📎 Related Context

- **Jules Activity:** 40+ commits, 50+ test files, 32 PRs in last 2 days
- **Affected Domains:** Core, Memory, E2E, Identity, Security, Governance
- **Previous T4 Report:** `T4_JULES_TEST_INTEGRATION_STATUS.md` (134 lint issues documented)
- **Worktree:** `feat/test-integration-fixes` at commit def4b8990

## 🚀 Timeline

**Requested Completion:** Within 24 hours  
**Blocker:** Yes - prevents test execution  
**Urgency:** Critical - affects continuous integration

---

@codex Please address systematically starting with top-5 most frequent errors. Provide progress updates after each pattern fix. Use T4 annotations for any intentional compromises.

