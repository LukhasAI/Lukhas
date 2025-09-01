# Jules Safe Test Tasks (Parallel Development Mode)

## 🎯 Safe Focus Areas (No Conflicts)

### ✅ COMPLETED: TODO[T4-AUTOFIX] Resolution (PR #100)
**Location**: `tools/dev/t4_test_validation.py` + additional files
- ✅ Line 10: Use list comprehension (DONE)
- ✅ Line 16: Use pathlib.Path (DONE) 
- ✅ Line 21: Remove unused variable (DONE)
- ✅ `system_status_comprehensive_report.py`: Fixed syntax errors (DONE)
- ✅ `fold_lineage_tracker.py`: Added missing logger (DONE)

### 🟡 Priority 1: Missing Tests for Stable lukhas/ Modules

#### `lukhas/bridge/` - Missing Test Coverage
1. **lukhas/bridge/llm_wrappers/unified_openai_client.py**
   - Create: `tests/lukhas/bridge/test_unified_openai_client.py`
   - Test: API client initialization, error handling, config validation
   
2. **lukhas/bridge/universal_bridge.py** 
   - Create: `tests/lukhas/bridge/test_universal_bridge.py`
   - Test: Bridge connections, fallbacks, protocol validation

3. **lukhas/core/distributed_tracing.py**
   - Create: `tests/lukhas/core/test_distributed_tracing.py`
   - Test: Correlation ID generation, trace propagation

#### `lukhas/matriz/` - Runtime Components
4. **lukhas/matriz/runtime/policy.py**
   - Create: `tests/lukhas/matriz/test_runtime_policy.py`
   - Test: Constitutional engine binding, policy evaluation

#### `serve/` - API Endpoints
5. **serve/api/health.py** (if exists)
   - Create: `tests/serve/api/test_health.py`
   - Test: Health check endpoints, status reporting

### ✅ Priority 3: Import Fix Batch Processing
**Location**: `docs/project_status/JULES_TODO_BATCHES.md` - BATCH 1
- Focus on `candidate/core/` import fixes (avoid aka_qualia/)
- Safe import resolution for missing dependencies
- Add proper error handling for missing modules

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
- All 3 TODO[T4-AUTOFIX] items resolved
- +5 new test files in tests/lukhas/ or tests/serve/
- Coverage increase on stable lukhas/ modules
- Zero conflicts with Wave C parallel development
- All quality gates pass (`make jules-gate`)

---
*This task list ensures Jules can work productively without interfering with Wave C development*