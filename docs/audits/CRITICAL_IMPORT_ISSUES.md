---
status: wip
type: documentation
---
# Critical Import Issues - Root Cause Analysis

## Primary Issue: Circular Import Dependencies

### The Problem
The codebase has a fundamental architecture issue where:

1. **Tests import from `lukhas.*`**
   ```python
   from lukhas.bridge.api_gateway.route_handlers import RouteHandlers
   ```

2. **The `lukhas` package tries to proxy to root modules**
   ```python
   # lukhas/__init__.py tries to map lukhas.bridge → bridge
   ```

3. **BUT the root modules themselves import using `lukhas.*`**
   ```python
   # Inside bridge/orchestration/multi_ai_orchestrator.py
   from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
   ```

This creates a circular dependency:
- Test wants `lukhas.bridge` → lukhas package maps to `bridge` → bridge imports `lukhas.bridge` → infinite loop/error

## Evidence

### File: `/Users/agi_dev/LOCAL-REPOS/Lukhas/bridge/orchestration/multi_ai_orchestrator.py`
```python
from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
```

This import fails because `lukhas.bridge` doesn't exist as a real module path.

### File: `/Users/agi_dev/LOCAL-REPOS/Lukhas/bridge/api_gateway/unified_api_gateway.py`
```python
from ..orchestration import (...)
```

This tries to import orchestration, which then fails on its lukhas.bridge import.

## Root Causes

### 1. Incomplete Migration
The codebase appears to be mid-migration from:
- Old structure: Everything under `lukhas.*` namespace
- New structure: Modules at root level or in `candidate/`
- Problem: Internal module imports still use old `lukhas.*` paths

### 2. Inconsistent Import Patterns
Three different import patterns coexist:
- **Pattern A**: `from lukhas.X import Y` (tests, old code)
- **Pattern B**: `from X import Y` (some modules)
- **Pattern C**: `from candidate.X import Y` (development code)

### 3. Incomplete Compatibility Layer
The `lukhas/__init__.py` compatibility layer:
- Only handles top-level attribute access (`lukhas.bridge`)
- Doesn't handle import statements properly
- Doesn't fix internal module imports

## Impact Assessment

### High Impact (Blocking)
1. **~230 test files cannot be collected** - tests fail before even running
2. **Bridge module is broken** - cannot be imported at all due to circular deps
3. **Many core modules unusable** - consciousness, orchestration, etc.

### Medium Impact
1. **Lane isolation violated** - unclear boundaries between candidate/core/production
2. **Development workflow broken** - cannot run tests for features
3. **CI/CD likely broken** - test suite cannot execute

### Low Impact (Cosmetic)
1. **Import inconsistency** - hard to know correct import path
2. **Documentation outdated** - import examples don't work

## Solutions

### Solution 1: Complete Internal Import Rewrite (RECOMMENDED)
**Effort**: High | **Risk**: Medium | **Impact**: Permanent fix

1. **Find all `lukhas.*` imports in source code**:
   ```bash
   grep -r "from lukhas\." /Users/agi_dev/LOCAL-REPOS/Lukhas --include="*.py" | \
     grep -v ".venv" | grep -v "tests/" > lukhas_imports.txt
   ```

2. **Replace with correct paths**:
   - `lukhas.bridge.*` → `bridge.*` (for bridge module internals)
   - `lukhas.consciousness.*` → `candidate.consciousness.*` or `consciousness.*`
   - etc.

3. **Update all test imports** to match new structure

### Solution 2: Create Full lukhas Package (QUICK FIX)
**Effort**: Medium | **Risk**: High | **Impact**: Temporary workaround

1. Copy ALL modules into `lukhas/` package:
   ```bash
   cp -r bridge/ lukhas/bridge/
   cp -r consciousness/ lukhas/consciousness/
   cp -r governance/ lukhas/governance/
   # etc for all modules
   ```

2. This makes all `lukhas.*` imports work
3. BUT violates lane architecture and duplicates code

### Solution 3: Fix Compatibility Layer (COMPLEX)
**Effort**: High | **Risk**: High | **Impact**: May not work

1. Enhance `lukhas/__init__.py` to:
   - Intercept ALL imports, not just attributes
   - Rewrite import paths on-the-fly
   - Handle nested submodule imports

2. Very complex, may have edge cases

### Solution 4: Namespace Package (ARCHITECTURAL)
**Effort**: Very High | **Risk**: Medium | **Impact**: Proper fix

1. Make `lukhas/` a proper namespace package
2. Move modules under it properly
3. Restructure entire codebase
4. Update all imports everywhere

## Immediate Actions

### Action 1: Fix Internal Bridge Imports
Find and fix the `lukhas.bridge` imports inside bridge module:

```bash
# Find the problematic imports
grep -r "from lukhas\.bridge" /Users/agi_dev/LOCAL-REPOS/Lukhas/bridge --include="*.py"

# Replace with relative imports
find /Users/agi_dev/LOCAL-REPOS/Lukhas/bridge -name "*.py" -exec \
  sed -i '' 's/from lukhas\.bridge\./from ./g' {} \;
```

### Action 2: Document Import Standards
Create IMPORT_STANDARDS.md that clearly defines:
- How to import each module
- Which patterns are allowed
- Migration status of each module

### Action 3: Gradual Migration Plan
1. **Phase 1**: Fix bridge module (highest priority)
2. **Phase 2**: Fix consciousness module
3. **Phase 3**: Fix governance module
4. **Phase 4**: Fix remaining modules
5. **Phase 5**: Update all test imports

## Module Import Status

### ✅ Working (can be imported)
- `matriz` - standalone, no lukhas dependencies
- `qi` - minimal dependencies
- Basic standalone utilities

### ⚠️ Partially Working (some imports fail)
- `memory` - basic import works, some submodules fail
- `governance` - root module works, submodules fail
- `consciousness` - root module works, submodules fail

### ❌ Broken (cannot be imported)
- `bridge` - circular lukhas.bridge imports
- `lukhas.core.orchestration` - missing modules
- `lukhas.consciousness.dream` - incomplete root module
- `lukhas.api` - doesn't exist

## Testing Recommendations

### Before Any Fixes
1. Document current state: `pytest --collect-only -q > test_collection_before.txt 2>&1`
2. Count errors: `grep "ERROR collecting" test_collection_before.txt | wc -l`
3. Categorize error types

### During Fixes
1. Fix one module at a time
2. Verify with: `pytest module/tests/ --collect-only`
3. Run actual tests: `pytest module/tests/ -v`
4. Document what was changed

### After Fixes
1. Full collection: `pytest --collect-only -q > test_collection_after.txt 2>&1`
2. Compare: `diff test_collection_before.txt test_collection_after.txt`
3. Run full test suite: `pytest -v`

## Priority Order

1. **CRITICAL**: Fix bridge module internal imports (blocks everything)
2. **HIGH**: Fix test imports for core modules (enables testing)
3. **MEDIUM**: Fix candidate module imports (enables development)
4. **LOW**: Clean up import inconsistencies (technical debt)

## Files That Need Immediate Attention

### Bridge Module
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/bridge/orchestration/multi_ai_orchestrator.py`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/bridge/orchestration/__init__.py`
- Any other files with `from lukhas.bridge` imports

### Test Files (already attempted fixes)
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/bridge/test_route_handlers.py`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/bridge/test_trace_logger.py`
- (Need to revert to lukhas.bridge or wait for bridge fix)

## Conclusion

The import errors are not simple path issues but a **fundamental architectural problem** stemming from incomplete migration from `lukhas.*` namespace to root/candidate structure.

**Recommended Path Forward**:
1. Fix bridge module internal imports (remove lukhas. prefix)
2. Document correct import pattern for each module
3. Create migration script to update all imports systematically
4. Run migration in phases (bridge → consciousness → governance → others)
5. Update tests last, after modules are fixed

**Estimated Effort**:
- Bridge fix: 2-4 hours
- Full migration script: 4-8 hours
- Testing and validation: 4-8 hours
- **Total**: 10-20 hours of focused work

**DO NOT**: Attempt quick fixes by copying modules or creating complex compatibility layers. These will create more technical debt.
