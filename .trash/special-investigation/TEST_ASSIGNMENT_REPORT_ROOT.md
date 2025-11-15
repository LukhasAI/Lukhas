# LUKHAS Test Coverage Assignment Report

**Report Date**: 2025-11-06
**Total Test Tasks**: 50+ modules needing coverage
**Current Coverage**: ~30% (Target: 75%+)
**Test Assignment System**: For Jules AI Agent

**Related Documents**:
- **bug_report.md** - Bug fixes and functionality issues
- **TEST_COVERAGE_REPORT.md** - Raw coverage gaps (from PR #949)
- **TEST_COVERAGE_IMPROVEMENT_SUMMARY.md** - Previous test additions

---

## 📍 Repository Navigation for Test Writing

### Essential Context Files (Read FIRST Before Writing Tests)

Agents **MUST** read these context files before writing any tests:

- **Master Context**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` - Complete system overview
- **Testing Guide**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/` - Test patterns and fixtures
- **Module Contexts**: Each module has its own `claude.me` file with domain knowledge
- **Test Examples**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/core/test_agent_tracer.py` - Good example

### Critical Testing Rules

**Test Organization**:
- Unit tests: `tests/unit/{module}/test_{filename}.py`
- Integration tests: `tests/integration/{module}/test_{filename}_integration.py`
- Smoke tests: `tests/smoke/test_{feature}.py`

**Coverage Requirements**:
- Unit tests: 75%+ coverage for production lane (`lukhas/`)
- Integration tests: 50%+ coverage for critical paths
- Smoke tests: 100% of API endpoints

**Lane Rules for Testing**:
- Tests CAN import from any lane (no restrictions)
- Test `lukhas/` production code thoroughly
- Test `core/` integration code comprehensively
- Test `candidate/` experimental code lightly

### Quality Thresholds

| Metric | Requirement | Purpose |
|--------|-------------|---------|
| Coverage | 75%+ | Production readiness |
| Test Isolation | 100% | No test interdependencies |
| Mock External Deps | Required | Fast, reliable tests |
| Assertions | 3+ per test | Comprehensive validation |
| Edge Cases | Required | Robustness |

---

## 📊 Current Test Health Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Overall Coverage** | ~30% | 75% | 🔴 CRITICAL |
| **Lukhas/ Coverage** | ~40% | 75% | 🔴 CRITICAL |
| **Core/ Coverage** | ~35% | 60% | 🔴 HIGH |
| **Test Count** | 807 files | 1200+ | 🟡 MEDIUM |
| **Collection Errors** | 223 | 0 | 🔴 CRITICAL |
| **Passing Tests** | 187/345 (54%) | >95% | 🔴 CRITICAL |

---

## 🔴 HIGH PRIORITY Test Tasks (15 tasks)

### TEST-001: Core Orchestration Tests (P1 HIGH)
- **Module**: `core/orchestration/`
- **Files Needing Tests**: 11 files
- **Current Coverage**: 0%
- **Target Coverage**: 75%
- **Priority**: HIGH - Core system functionality

**Files to Test**:
1. `core/orchestration/agent.py` - Agent coordination
2. `core/orchestration/brain.py` - Decision making
3. `core/orchestration/flow.py` - Workflow management
4. `core/orchestration/orchestrator.py` - Main orchestrator
5. `core/orchestration/planner.py` - Task planning
6. `core/orchestration/prompt.py` - Prompt generation
7. `core/orchestration/react.py` - ReAct pattern
8. `core/orchestration/task.py` - Task management
9. `core/orchestration/tool.py` - Tool integration
10. `core/orchestration/workflow.py` - Workflow execution
11. `core/orchestration/worker.py` - Worker management

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/core/orchestration/` - Implementation
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` - Architecture
- **Lane Location**: Core (integration layer)
- **Architecture Impact**: Critical - orchestrates all agent workflows
- **Related Components**: MATRIZ, consciousness, memory

**Test Strategy**:
```python
# tests/unit/core/orchestration/test_orchestrator.py
import pytest
from core.orchestration.orchestrator import Orchestrator

def test_orchestrator_initialization():
    """Test orchestrator initializes with default config"""
    orch = Orchestrator()
    assert orch is not None
    assert orch.config is not None

def test_orchestrator_task_execution():
    """Test orchestrator can execute simple task"""
    orch = Orchestrator()
    result = orch.execute_task({"type": "test", "input": "data"})
    assert result["status"] == "success"

def test_orchestrator_multi_agent_coordination():
    """Test orchestrator coordinates multiple agents"""
    orch = Orchestrator()
    agents = [MockAgent("agent1"), MockAgent("agent2")]
    result = orch.coordinate(agents, task="test_task")
    assert len(result["agent_results"]) == 2

# Add 20+ tests per file covering:
# - Initialization
# - Happy path execution
# - Error handling
# - Edge cases (empty input, invalid config)
# - Integration with other components
```

**Validation**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/unit/core/orchestration/ -v --cov=core/orchestration
# Target: 75%+ coverage
```

---

### TEST-002: Core Interfaces Tests (P1 HIGH)
- **Module**: `core/interfaces/`
- **Files Needing Tests**: 12 files
- **Current Coverage**: 0%
- **Target Coverage**: 80%
- **Priority**: HIGH - Interface contracts critical

**Files to Test**:
1. `core/interfaces/agents.py`
2. `core/interfaces/consciousness.py`
3. `core/interfaces/database.py`
4. `core/interfaces/event_bus.py`
5. `core/interfaces/identity.py`
6. `core/interfaces/language_model.py`
7. `core/interfaces/logger.py`
8. `core/interfaces/memory.py`
9. `core/interfaces/monitoring.py`
10. `core/interfaces/realtime.py`
11. `core/interfaces/storage.py`
12. `core/interfaces/task_queue.py`

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/core/interfaces/`
- **Lane Location**: Core interfaces
- **Architecture Impact**: HIGH - Defines all system contracts
- **Related Components**: All subsystems depend on these

**Test Pattern** (for interfaces):
```python
# tests/unit/core/interfaces/test_memory.py
import pytest
from core.interfaces.memory import MemoryInterface, MemoryBackend

def test_memory_interface_contract():
    """Test MemoryInterface defines required methods"""
    assert hasattr(MemoryInterface, 'store')
    assert hasattr(MemoryInterface, 'retrieve')
    assert hasattr(MemoryInterface, 'search')

def test_memory_backend_implementation():
    """Test MemoryBackend implements interface"""
    backend = MemoryBackend()
    assert isinstance(backend, MemoryInterface)

def test_memory_store_and_retrieve():
    """Test basic store/retrieve workflow"""
    backend = MemoryBackend()
    key = backend.store({"data": "test"})
    result = backend.retrieve(key)
    assert result["data"] == "test"

# Test all interface methods
# Test error handling
# Test edge cases
```

**Validation**:
```bash
pytest tests/unit/core/interfaces/ -v --cov=core/interfaces
```

---

### TEST-003: LUKHAS Identity System Tests (P1 HIGH)
- **Module**: `lukhas/identity/`
- **Files Needing Tests**: 4 files
- **Current Coverage**: ~20%
- **Target Coverage**: 80%
- **Priority**: HIGH - Security critical

**Files to Test**:
1. `lukhas/identity/token_types.py` - Token validation
2. `lukhas/identity/webauthn_credential.py` - WebAuthn support
3. `lukhas/identity/webauthn_verify.py` - Verification logic

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/identity/claude.me`
- **Lane Location**: Production (lukhas/)
- **Architecture Impact**: CRITICAL - Security/authentication
- **Constellation Star**: ⚛️ Identity
- **Related Components**: Auth middleware, API security

**Security Test Requirements**:
```python
# tests/unit/lukhas/identity/test_token_types.py
import pytest
from lukhas.identity.token_types import TokenValidator

def test_token_validation_rejects_invalid():
    """SECURITY: Invalid tokens must be rejected"""
    validator = TokenValidator()
    assert validator.validate("invalid_token") is False

def test_token_validation_accepts_valid():
    """Treat valid tokens must be accepted"""
    validator = TokenValidator()
    valid_token = validator.generate_token("user123")
    assert validator.validate(valid_token) is True

def test_token_expiration():
    """Expired tokens must be rejected"""
    validator = TokenValidator()
    expired_token = create_expired_token()
    assert validator.validate(expired_token) is False

# Must test:
# - Token validation
# - Expiration handling
# - Signature verification
# - Token tampering detection
# - Edge cases (malformed, empty, null)
```

**Validation**:
```bash
pytest tests/unit/lukhas/identity/ -v --cov=lukhas/identity
make security-scan  # Verify no security regressions
```

---

### TEST-004: LUKHAS Memory System Tests (P1 HIGH)
- **Module**: `lukhas/memory/`
- **Files Needing Tests**: 2 files
- **Current Coverage**: ~50%
- **Target Coverage**: 80%
- **Priority**: HIGH - Recently added vector indexing (PR #963)

**Files to Test**:
1. `lukhas/memory/index.py` - Vector indexing (NEW from PR #963)
2. `lukhas/memory/__init__.py` - Memory exports

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/`
- **Lane Location**: Production (lukhas/)
- **Architecture Impact**: HIGH - Core memory functionality
- **Constellation Star**: ✦ Memory
- **Recent Changes**: Vector indexing just added (ISSUE-021)

**Test Requirements**:
```python
# tests/unit/lukhas/memory/test_index.py
import pytest
from lukhas.memory.index import EmbeddingIndex, IndexManager

def test_embedding_index_creation():
    """Test EmbeddingIndex initializes correctly"""
    index = EmbeddingIndex(dimension=384)
    assert index.dimension == 384
    assert index.size() == 0

def test_embedding_index_add_vectors():
    """Test adding vectors to index"""
    index = EmbeddingIndex(dimension=384)
    vectors = [[0.1] * 384, [0.2] * 384]
    ids = index.add(vectors)
    assert len(ids) == 2
    assert index.size() == 2

def test_embedding_index_search():
    """Test vector search functionality"""
    index = EmbeddingIndex(dimension=384)
    vectors = [[0.1] * 384, [0.2] * 384]
    index.add(vectors)

    query = [0.15] * 384
    results = index.search(query, k=1)
    assert len(results) == 1

def test_embedding_index_persistence():
    """Test index can be saved and loaded"""
    index = EmbeddingIndex(dimension=384)
    index.add([[0.1] * 384])

    index.save("/tmp/test_index")
    loaded = EmbeddingIndex.load("/tmp/test_index")
    assert loaded.size() == 1

# Must test:
# - Vector addition
# - Search accuracy
# - Persistence
# - Edge cases (empty index, invalid dimensions)
# - Performance (1000+ vectors)
```

**Validation**:
```bash
pytest tests/unit/lukhas/memory/ -v --cov=lukhas/memory
# Should unblock 17 skipped tests from ISSUE-021
```

---

### TEST-005: Core Blockchain Tests (P1 HIGH)
- **Module**: `core/blockchain/`
- **Files Needing Tests**: 2 files
- **Current Coverage**: 0%
- **Target Coverage**: 75%

**Files to Test**:
1. `core/blockchain/state.py`
2. `core/blockchain/utils.py`

**Test Strategy**:
```python
# tests/unit/core/blockchain/test_state.py
def test_blockchain_state_initialization():
    """Test blockchain state initializes with genesis block"""

def test_blockchain_state_add_block():
    """Test adding new block to chain"""

def test_blockchain_state_validation():
    """Test chain validation detects tampering"""

# Test blockchain immutability
# Test consensus mechanisms
```

---

### TEST-006: Core Emotion Tests (P2 MEDIUM)
- **Module**: `core/emotion/`
- **Files Needing Tests**: 1 file
- **Current Coverage**: 0%
- **Target Coverage**: 75%

**Files to Test**:
1. `core/emotion/emotion_models.py`

---

### TEST-007: API Endpoints Integration Tests (P1 HIGH)
- **Module**: `serve/main.py` and routers
- **Current Coverage**: ~40%
- **Target Coverage**: 85%
- **Priority**: HIGH - User-facing API

**Endpoints Needing Tests**:
1. `/v1/models` - Model listing
2. `/v1/chat/completions` - Chat API
3. `/v1/embeddings` - Embeddings API
4. `/v1/dreams` - Dreams API (NEW from PR #965)
5. `/healthz` - Health checks
6. `/readyz` - Readiness probes
7. `/metrics` - Prometheus metrics

**Test Pattern**:
```python
# tests/integration/api/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from serve.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_models_endpoint_returns_lista(client):
    """Test /v1/models returns model list"""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

def test_models_endpoint_includes_matriz(client):
    """Test lukhas-matriz model is in list"""
    response = client.get("/v1/models")
    models = response.json()["data"]
    model_ids = [m["id"] for m in models]
    assert "lukhas-matriz-v1" in model_ids

def test_chat_completions_endpoint(client):
    """Test /v1/chat/completions works"""
    payload = {
        "model": "lukhas-matriz-v1",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200

# Test all endpoints
# Test auth requirements
# Test error cases
# Test OpenAI compatibility
```

---

### TEST-008: Fix Collection Errors (P1 CRITICAL)
- **Issue**: 223 test collection errors blocking accurate coverage measurement
- **Priority**: CRITICAL - Must fix before other test work
- **Impact**: Cannot measure true coverage with broken imports

**Common Collection Error Patterns**:

1. **Missing Module Imports** (50+ errors):
   - `ModuleNotFoundError: No module named 'qi.qi_entanglement'`
   - `ModuleNotFoundError: No module named 'lukhas_website.core'`

2. **Recursion Errors** (30+ errors):
   - `RecursionError` in `cognitive_core/reasoning/deep_inference_engine`

3. **Import Errors** (40+ errors):
   - `ImportError: cannot import name 'AutoConsciousness' from 'consciousness'`

**Fix Strategy**:
```bash
# 1. Find all collection errors
pytest --co -q 2>&1 | grep "ERROR" > /tmp/collection_errors.txt

# 2. Group by error type
grep "ModuleNotFoundError" /tmp/collection_errors.txt
grep "RecursionError" /tmp/collection_errors.txt
grep "ImportError" /tmp/collection_errors.txt

# 3. Fix each category:
# - Add missing __init__.py files
# - Fix circular imports
# - Update import paths
# - Skip broken tests temporarily

# 4. Validate
pytest --co -q  # Should show 0 errors
```

---

### TEST-009 through TEST-015: Additional High Priority Modules

**TEST-009**: Core Memory Tests (`core/memory/` - 5 files)
**TEST-010**: Core Quantum Tests (`core/quantum_financial/` - 3 files)
**TEST-011**: Core Colonies Tests (`core/colonies/` - 5 files)
**TEST-012**: Serve API Tests (Full API coverage)
**TEST-013**: Integration Tests (Cross-component workflows)
**TEST-014**: Smoke Tests (All critical paths)
**TEST-015**: Performance Tests (Load, stress, benchmarks)

---

## 🟡 MEDIUM PRIORITY Test Tasks (20 tasks)

### TEST-016 through TEST-035: Module Coverage

- **TEST-016**: `candidate/consciousness/` tests
- **TEST-017**: `candidate/bio/` tests
- **TEST-018**: `candidate/quantum/` tests
- **TEST-019**: `labs/memory/` tests
- **TEST-020**: `labs/governance/` tests
- *... (additional 15 modules)*

---

## 🟢 LOW PRIORITY Test Tasks (15 tasks)

- **TEST-036**: Legacy code tests
- **TEST-037**: Example code tests
- **TEST-038**: Documentation tests
- **TEST-039**: Script tests
- **TEST-040**: Tool tests
- *... (additional 10 tasks)*

---

## 📋 Test Assignment Template for Jules

### Standard Assignment Format

```
Write comprehensive tests for {MODULE_NAME}

File: {FILE_PATH}
Target Coverage: {COVERAGE_PERCENTAGE}%
Priority: {HIGH/MEDIUM/LOW}

Context Files to Read:
- /Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me
- {MODULE_SPECIFIC_CONTEXT_FILE}

Test Requirements:
- Unit tests in tests/unit/{module}/test_{filename}.py
- Target {COVERAGE_PERCENTAGE}% coverage
- Include:
  - Initialization tests
  - Happy path tests
  - Error handling tests
  - Edge case tests
  - Integration tests (if applicable)

Validation:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/unit/{module}/ -v --cov={module}
```

Expected Outcome:
- {COVERAGE_PERCENTAGE}%+ coverage
- All tests passing
- No new collection errors
```

---

## 🎯 Quick Assignment Commands for Jules

### Example 1: Assign Core Orchestration Tests
```
Write comprehensive tests for core orchestration module.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/TEST_ASSIGNMENT_REPORT.md, find TEST-001, read all context files listed, write tests for all 11 files in core/orchestration/, target 75%+ coverage, validate with pytest.
```

### Example 2: Assign Identity Tests
```
Write comprehensive tests for lukhas identity module.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-003, write security-focused tests for lukhas/identity/, target 80%+ coverage, include token validation, WebAuthn, edge cases, run make security-scan after.
```

### Example 3: Fix Collection Errors
```
Fix all pytest collection errors.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-008, run pytest --co -q to find errors, group by type, fix ModuleNotFoundError, RecursionError, ImportError issues, validate with pytest --co -q (must show 0 errors).
```

---

## 📊 Success Metrics

Track progress using these metrics:

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Overall Coverage | 30% | 75% | 8 weeks |
| Lukhas/ Coverage | 40% | 80% | 4 weeks |
| Core/ Coverage | 35% | 65% | 6 weeks |
| Collection Errors | 223 | 0 | 2 weeks |
| Test Count | 807 | 1500+ | 8 weeks |
| Passing Rate | 54% | >95% | 4 weeks |

---

## 🔧 Testing Best Practices

### Test Structure
```python
def test_{feature}_{scenario}():
    """Test {what is being tested}"""
    # Arrange
    setup_code()

    # Act
    result = function_under_test()

    # Assert
    assert result == expected
    assert side_effect_occurred()
    assert no_errors_raised()
```

### Required Test Categories

1. **Happy Path**: Normal successful execution
2. **Error Cases**: Invalid input, exceptions, failures
3. **Edge Cases**: Empty, null, boundary values
4. **Integration**: Interaction with other components
5. **Performance**: Speed, memory, scalability

### Mock External Dependencies

```python
from unittest.mock import patch, MagicMock

@patch('external.service.call')
def test_with_mocked_external(mock_call):
    mock_call.return_value = {"status": "success"}
    result = my_function()
    assert result is not None
```

---

## 📝 Commit Message Template for Tests

```
test({module}): add comprehensive test coverage for {component}

Problem:
- {module} had {X}% coverage (target: {Y}%)
- {N} critical functions untested
- Missing edge case validation

Solution:
- Created tests/unit/{module}/test_{file}.py
- Added {N} test cases covering:
  - Initialization and configuration
  - Happy path execution
  - Error handling
  - Edge cases
  - Integration scenarios

Impact:
- Coverage: {X}% → {Y}% ({improvement}%)
- {N} tests passing
- All critical paths validated
- {feature} now production-ready

Validation:
- pytest tests/unit/{module}/ -v --cov={module}
- Coverage: {Y}%

Closes: TEST-{NUMBER}

🤖 Generated by Jules

Co-Authored-By: Jules <noreply@google.com>
```

---

## 🚀 Getting Started Guide for Jules

### Week 1: Foundation
1. Read this entire document
2. Fix collection errors (TEST-008)
3. Write tests for 2 high-priority modules
4. Validate coverage improvements

### Week 2-3: Core Systems
5. Complete all core/orchestration tests (TEST-001)
6. Complete all core/interfaces tests (TEST-002)
7. Complete identity tests (TEST-003)
8. Complete memory tests (TEST-004)

### Week 4-6: Comprehensive Coverage
9. Complete all HIGH priority tasks (TEST-001 through TEST-015)
10. Begin MEDIUM priority tasks
11. Achieve 60%+ overall coverage

### Week 7-8: Polish
12. Complete remaining MEDIUM tasks
13. Fix any failing tests
14. Achieve 75%+ overall coverage
15. Production readiness

---

**Report Generated**: 2025-11-06
**Location**: `/Users/agi_dev/LOCAL-REPOS/Lukhas-test-audit/TEST_ASSIGNMENT_REPORT.md`
**Branch**: feat/test-coverage-audit (in worktree)
**Related PRs**: #949 (Test Coverage Report - merging soon)
**For**: Jules AI Agent - systematic test coverage improvement
