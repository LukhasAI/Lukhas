# Jules Safe Test Tasks (Parallel Development Mode)

## 🎯 Safe Focus Areas (No Conflicts)

### ✅ COMPLETED: TODO[T4-AUTOFIX] Resolution (PRs #100 & #101)
**All T4-AUTOFIX items resolved except one**:
- ✅ `tools/dev/t4_test_validation.py`: All 3 items fixed (DONE)
- ✅ `tools/scripts/system_status_comprehensive_report.py`: Major syntax fixes applied (DONE)
- ✅ `archive/.../fold_lineage_tracker.py`: Added missing logger (DONE)
- ✅ `tests/bridge/test_unified_openai_client.py`: Comprehensive test suite created (DONE)

### 🚨 CRITICAL: serve/ API Test Coverage Gap
**ZERO tests exist for 19 serve/ modules** - This is the highest impact work Jules can do.

### 🚨 Priority 1: serve/ API Test Coverage (CRITICAL GAP)
**19 serve/ modules with ZERO test coverage**:

1. **serve/main.py** - FastAPI application entry point
   - Create: `tests/serve/test_main.py`
   - Test: App initialization, middleware, startup/shutdown

2. **serve/consciousness_api.py** - Consciousness endpoints
   - Create: `tests/serve/test_consciousness_api.py` 
   - Test: Consciousness API endpoints, response formats

3. **serve/identity_api.py** - Identity/auth endpoints
   - Create: `tests/serve/test_identity_api.py`
   - Test: Authentication flows, JWT handling

4. **serve/guardian_api.py** - Guardian security endpoints
   - Create: `tests/serve/test_guardian_api.py`
   - Test: Security validation, ethics enforcement

5. **serve/routes.py** - General routing
   - Create: `tests/serve/test_routes.py`
   - Test: Route registration, middleware, error handling

6. **serve/openai_routes.py** - OpenAI API routes
   - Create: `tests/serve/test_openai_routes.py`
   - Test: OpenAI proxy endpoints, request/response handling

### 🟡 Priority 2: lukhas/ Missing Test Coverage

#### `lukhas/bridge/` - Additional Components
7. **lukhas/bridge/bridge_wrapper.py**
   - Create: `tests/bridge/test_bridge_wrapper.py`
   - Test: Bridge wrapper functionality, error handling

8. **lukhas/bridge/llm_wrappers/anthropic_wrapper.py**
   - Create: `tests/bridge/test_anthropic_wrapper.py`
   - Test: Anthropic API integration, response parsing

#### `lukhas/core/` and `lukhas/matriz/`
9. **lukhas/core/distributed_tracing.py**
   - Create: `tests/core/test_distributed_tracing.py`
   - Test: Trace correlation, context propagation

10. **lukhas/matriz/runtime/policy.py**
    - Create: `tests/matriz/test_runtime_policy.py`
    - Test: Policy evaluation, runtime binding

### 🟠 Priority 3: Final TODO[T4-AUTOFIX] Item
**Location**: `tools/scripts/system_status_comprehensive_report.py:1`
- **Issue**: "Extensive syntax errors throughout file"
- **Action**: Apply surgical fixes to syntax errors (missing colons, malformed f-strings)
- **Constraint**: ≤20 lines per fix, maintain existing functionality

### ✅ Priority 4: Smoke Tests for Existing Systems
6. **tests/smoke/test_lukhas_core.py**
   - Test: Core module imports work
   - Test: Basic initialization succeeds
   - Test: Configuration loading works

7. **tests/smoke/test_bridge_connectivity.py**
   - Test: Bridge modules load without errors
   - Test: API clients initialize with dummy configs

## 🚫 AVOID These Areas (Parallel Development)
- ❌ `candidate/aka_qualia/` - Wave C implementation in progress
- ❌ Any files being actively modified by parallel Claude Code agent
- ❌ New architecture implementations in candidate/

## 🛡️ Safety Guidelines
- **Stick to tests/** directory for new files
- **Use existing lukhas/** modules as test targets
- **No modifications to candidate/aka_qualia/** files
- **Focus on import fixes in stable candidate/core/** areas only
- **All patches ≤20 lines, no behavior changes**

## ✅ Success Metrics  
- **serve/ test coverage**: Minimum 5 test files created (from current 0)
- **lukhas/ additional coverage**: 3+ missing test files added
- **Final TODO[T4-AUTOFIX]**: Resolved in system status report
- **Coverage increase**: +15% on stable lukhas/ and serve/ modules
- **Zero conflicts**: No interference with Wave C development
- **All quality gates pass**: `make jules-gate` succeeds

---
*This task list ensures Jules can work productively without interfering with Wave C development*