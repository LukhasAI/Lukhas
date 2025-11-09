# Missing Tests - Delegation Guide for Claude.ai

**Purpose**: This document lists all modules without test coverage, prioritized for delegation to Claude.ai (claude.ai/code) for comprehensive test creation.

**Total Modules Without Tests**: 391
- **lukhas/**: 11 files (production API/features)
- **serve/**: 20 files (FastAPI routes/middleware)
- **matriz/**: 87 files (cognitive engine)
- **core/**: 273 files (integration layer)

---

## 📋 How to Use This Guide

### Option 1: Delegate to Claude.ai (Recommended)

1. **Visit**: https://claude.ai/code
2. **Upload this document** + relevant source files
3. **Use the PR templates below** to request test creation
4. **Review generated tests** and create PR
5. **Repeat** for each batch

### Option 2: Fix Existing Tests

Some tests are already written but **broken** (collection errors). Ask Claude.ai to fix them.

---

## 🎯 Priority Tiers

### Tier 1: Critical Production Code (HIGH PRIORITY)
**Target**: lukhas/ and serve/ modules (31 files, 50+ lines each)

These are actively used in production and need immediate test coverage.

### Tier 2: MATRIZ Cognitive Engine (MEDIUM PRIORITY)
**Target**: matriz/ modules (97 files, 50+ lines each)

Core cognitive engine - complex logic requiring comprehensive tests.

### Tier 3: Integration Layer (LOWER PRIORITY)
**Target**: core/ modules (273 files)

Integration and orchestration code - test after Tier 1 & 2.

---

## 📦 Tier 1: Critical Production Code (31 files)

### serve/ - FastAPI Routes & API (20 files)

#### Batch 1A: Main API Endpoints (5 files - ~2,500 lines)

**Files:**
1. `serve/api/integrated_consciousness_api.py` (769 lines)
2. `serve/reference_api/public_api_reference.py` (674 lines)
3. `serve/extreme_performance_main.py` (666 lines)
4. `serve/agi_enhanced_consciousness_api.py` (533 lines)
5. `serve/agi_orchestration_api.py` (532 lines)

**PR Request Template:**
```
# Test Suite: serve/ Main API Endpoints (Batch 1A)

Create comprehensive test suites for 5 main API endpoint modules in serve/.

## Files to Test:
- serve/api/integrated_consciousness_api.py (769 lines)
- serve/reference_api/public_api_reference.py (674 lines)
- serve/extreme_performance_main.py (666 lines)
- serve/agi_enhanced_consciousness_api.py (533 lines)
- serve/agi_orchestration_api.py (532 lines)

## Test Requirements:
- Use pytest with FastAPI TestClient
- Test all FastAPI routes (GET, POST, PUT, DELETE)
- Test authentication/authorization middleware
- Test request validation (invalid inputs, edge cases)
- Test response schemas (OpenAPI compatibility)
- Test error handling (4xx, 5xx responses)
- Mock external dependencies (MATRIZ, OpenAI, etc.)
- Target: 80%+ coverage per file

## Test File Structure:
- Create: tests/unit/serve/api/test_integrated_consciousness_api.py
- Create: tests/unit/serve/reference_api/test_public_api_reference.py
- Create: tests/unit/serve/test_extreme_performance_main.py
- Create: tests/unit/serve/test_agi_enhanced_consciousness_api.py
- Create: tests/unit/serve/test_agi_orchestration_api.py

## Example Test Pattern:
```python
import pytest
from fastapi.testclient import TestClient
from serve.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint_happy_path(client):
    response = client.get("/v1/endpoint")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_endpoint_auth_required(client):
    response = client.get("/v1/protected", headers={})
    assert response.status_code == 401
```

Please create all 5 test files with comprehensive coverage.
```

---

#### Batch 1B: OpenAI-Compatible Routes (5 files - ~1,900 lines)

**Files:**
1. `serve/openai_routes.py` (438 lines)
2. `serve/main.py` (413 lines)
3. `serve/feedback_routes.py` (400 lines)
4. `serve/routes.py` (376 lines)
5. `serve/storage/trace_provider.py` (264 lines)

**PR Request Template:**
```
# Test Suite: serve/ OpenAI-Compatible Routes (Batch 1B)

Create comprehensive test suites for OpenAI-compatible API routes and core serving infrastructure.

## Files to Test:
- serve/openai_routes.py (438 lines) - OpenAI facade endpoints
- serve/main.py (413 lines) - Main FastAPI app with middleware
- serve/feedback_routes.py (400 lines) - Feedback API
- serve/routes.py (376 lines) - Core routes
- serve/storage/trace_provider.py (264 lines) - Trace storage

## Test Requirements:
- Test OpenAI API compatibility (chat/completions, models, embeddings)
- Test middleware stack (CORS, auth, rate limiting, headers)
- Test feedback collection and validation
- Test trace storage (in-memory, persistence, retrieval)
- Mock external LLM calls
- Test streaming responses (SSE)
- Target: 80%+ coverage per file

## Test File Structure:
- Create: tests/unit/serve/test_openai_routes.py
- Create: tests/unit/serve/test_main.py
- Create: tests/unit/serve/test_feedback_routes.py
- Create: tests/unit/serve/test_routes.py
- Create: tests/unit/serve/storage/test_trace_provider.py

Please create all 5 test files with comprehensive coverage.
```

---

#### Batch 1C: Routes & Models (5 files - ~700 lines)

**Files:**
1. `serve/routes_traces.py` (258 lines)
2. `serve/schemas.py` (70 lines)
3. `serve/models/trace_models.py` (69 lines)
4. `serve/webauthn_routes.py` (68 lines)
5. `serve/consciousness_api.py` (61 lines)

**PR Request Template:**
```
# Test Suite: serve/ Routes & Models (Batch 1C)

Create comprehensive test suites for tracing routes, data models, and specialized APIs.

## Files to Test:
- serve/routes_traces.py (258 lines) - Trace retrieval API
- serve/schemas.py (70 lines) - Pydantic schemas
- serve/models/trace_models.py (69 lines) - Trace data models
- serve/webauthn_routes.py (68 lines) - WebAuthn authentication
- serve/consciousness_api.py (61 lines) - Consciousness API

## Test Requirements:
- Test trace CRUD operations (create, read, list, filter)
- Test Pydantic model validation (valid/invalid data)
- Test WebAuthn registration and verification flows
- Test consciousness API endpoints
- Mock storage backends
- Target: 85%+ coverage per file

## Test File Structure:
- Create: tests/unit/serve/test_routes_traces.py
- Create: tests/unit/serve/test_schemas.py
- Create: tests/unit/serve/models/test_trace_models.py
- Create: tests/unit/serve/test_webauthn_routes.py
- Create: tests/unit/serve/test_consciousness_api.py

Please create all 5 test files with comprehensive coverage.
```

---

#### Batch 1D: Middleware & Infrastructure (5 files - ~500 lines)

**Files:**
1. `serve/identity_api.py` (file exists, size unknown)
2. `serve/guardian_api.py` (file exists, size unknown)
3. `serve/dreams_api.py` (file exists, size unknown)
4. `serve/middleware/strict_auth.py` (file exists, size unknown)
5. `serve/middleware/headers.py` (file exists, size unknown)

**PR Request Template:**
```
# Test Suite: serve/ Middleware & Specialized APIs (Batch 1D)

Create comprehensive test suites for authentication middleware and specialized API endpoints.

## Files to Test:
- serve/identity_api.py - Identity/auth API
- serve/guardian_api.py - Guardian ethical oversight API
- serve/dreams_api.py - Dreams/creativity API
- serve/middleware/strict_auth.py - Auth middleware
- serve/middleware/headers.py - Header middleware

## Test Requirements:
- Test identity token generation/validation
- Test guardian policy enforcement
- Test dreams API endpoints
- Test strict auth middleware (401 on missing auth)
- Test header middleware (CORS, security headers, trace IDs)
- Mock authentication backends
- Target: 80%+ coverage per file

## Test File Structure:
- Create: tests/unit/serve/test_identity_api.py
- Create: tests/unit/serve/test_guardian_api.py
- Create: tests/unit/serve/test_dreams_api.py
- Create: tests/unit/serve/middleware/test_strict_auth.py
- Create: tests/unit/serve/middleware/test_headers.py

Please create all 5 test files with comprehensive coverage.
```

---

### lukhas/ - Production Features & Identity (11 files)

#### Batch 1E: Identity & Auth (4 files - ~1,600 lines)

**Files:**
1. `lukhas/identity/webauthn_verify.py` (497 lines)
2. `lukhas/analytics/privacy_client.py` (493 lines)
3. `lukhas/api/features.py` (433 lines)
4. `lukhas/features/flags_service.py` (402 lines)

**PR Request Template:**
```
# Test Suite: lukhas/ Identity & Features (Batch 1E)

Create comprehensive test suites for WebAuthn authentication and feature flags.

## Files to Test:
- lukhas/identity/webauthn_verify.py (497 lines) - WebAuthn verification
- lukhas/analytics/privacy_client.py (493 lines) - Privacy-preserving analytics
- lukhas/api/features.py (433 lines) - Feature flags API
- lukhas/features/flags_service.py (402 lines) - Feature flag service

## Test Requirements:
- Test WebAuthn challenge generation and verification
- Test privacy-preserving analytics (no PII leakage)
- Test feature flag CRUD operations
- Test flag evaluation (user targeting, rollout %)
- Mock WebAuthn authenticators
- Mock analytics backends
- Target: 85%+ coverage per file

## Test File Structure:
- Create: tests/unit/lukhas/identity/test_webauthn_verify.py
- Create: tests/unit/lukhas/analytics/test_privacy_client.py
- Create: tests/unit/lukhas/api/test_features.py
- Create: tests/unit/lukhas/features/test_flags_service.py

Please create all 4 test files with comprehensive coverage.
```

---

#### Batch 1F: API & CLI (7 files - ~1,800 lines)

**Files:**
1. `lukhas/api/analytics.py` (365 lines)
2. `lukhas/identity/webauthn_credential.py` (296 lines)
3. `lukhas/cli/troubleshoot.py` (266 lines)
4. `lukhas/cli/guided.py` (252 lines)
5. `lukhas/features/testing.py` (233 lines)
6. `lukhas/identity/token_types.py` (136 lines)
7. `lukhas/adapters/openai/api.py` (28 lines)

**PR Request Template:**
```
# Test Suite: lukhas/ API & CLI Tools (Batch 1F)

Create comprehensive test suites for analytics, CLI tools, and adapters.

## Files to Test:
- lukhas/api/analytics.py (365 lines) - Analytics API
- lukhas/identity/webauthn_credential.py (296 lines) - WebAuthn credentials
- lukhas/cli/troubleshoot.py (266 lines) - Troubleshooting CLI
- lukhas/cli/guided.py (252 lines) - Interactive guided CLI
- lukhas/features/testing.py (233 lines) - Testing utilities
- lukhas/identity/token_types.py (136 lines) - JWT token types
- lukhas/adapters/openai/api.py (28 lines) - OpenAI adapter

## Test Requirements:
- Test analytics event tracking and aggregation
- Test WebAuthn credential storage and retrieval
- Test CLI command execution (mock user input)
- Test JWT token creation/validation (mk_exp, mk_iat helpers)
- Test feature flag test harness
- Test OpenAI adapter request formatting
- Mock external services (analytics, credential store)
- Target: 80%+ coverage per file

## Test File Structure:
- Create: tests/unit/lukhas/api/test_analytics.py
- Create: tests/unit/lukhas/identity/test_webauthn_credential.py
- Create: tests/unit/lukhas/cli/test_troubleshoot.py
- Create: tests/unit/lukhas/cli/test_guided.py
- Create: tests/unit/lukhas/features/test_testing.py
- Create: tests/unit/lukhas/identity/test_token_types.py (may already exist)
- Create: tests/unit/lukhas/adapters/openai/test_api.py

Please create all 7 test files with comprehensive coverage.
```

---

## 📦 Tier 2: MATRIZ Cognitive Engine (97 files, 50+ lines)

### Batch 2A: Consciousness & Reflection (Top 20 largest files)

**Files** (showing top 10):
1. `matriz/consciousness/reflection/ethical_reasoning_system.py` (2,489 lines)
2. `matriz/consciousness/reflection/orchestration_service.py` (2,454 lines)
3. `matriz/consciousness/reflection/EthicalReasoningSystem.py` (2,139 lines)
4. `matriz/consciousness/reflection/lambda_dependa_bot.py` (2,000 lines)
5. `matriz/memory/temporal/hyperspace_dream_simulator.py` (1,898 lines)
6. `matriz/memory/core/unified_memory_orchestrator.py` (1,890 lines)
7. `matriz/consciousness/reflection/core.py` (1,800 lines)
8. `matriz/consciousness/core/engine_poetic.py` (1,778 lines)
9. `matriz/consciousness/reflection/reflection_layer.py` (1,760 lines)
10. `matriz/consciousness/awareness/awareness_engine_elevated.py` (1,621 lines)

**PR Request Template:**
```
# Test Suite: MATRIZ Consciousness Engines (Batch 2A)

Create comprehensive test suites for MATRIZ consciousness and reflection systems.

## Files to Test:
[List 5-10 files at a time from the list above]

## Test Requirements:
- Test cognitive processing pipelines (Memory → Attention → Thought → Action)
- Test symbolic DNA node processing
- Test bio-inspired adaptation mechanisms
- Test quantum-inspired superposition and entanglement
- Test ethical reasoning and decision-making
- Test reflection and meta-cognitive loops
- Mock expensive LLM calls
- Mock external dependencies (vector stores, embeddings)
- Target: 70%+ coverage per file (cognitive code is complex)

## Test File Structure:
- Create: tests/unit/matriz/consciousness/reflection/test_ethical_reasoning_system.py
- Create: tests/unit/matriz/consciousness/reflection/test_orchestration_service.py
- [... one test file per source file ...]

## Example Test Pattern:
```python
import pytest
from matriz.consciousness.core.engine import MAT RIZEngine

@pytest.fixture
def engine():
    return MATRIZEngine(mode="test", mock_llm=True)

def test_memory_attention_pipeline(engine):
    result = engine.process("test input")
    assert result.memory_retrieved is not None
    assert result.attention_focused is not None
    assert result.thought_generated is not None
```

Please create test files for the first 10 consciousness modules.
```

---

## 📦 Tier 3: Core Integration Layer (273 files)

**Recommendation**: Defer until Tier 1 & 2 are complete. Many core/ files are integration code that may be refactored.

---

## 🔧 Fixing Existing Broken Tests

### Collection Errors (207 errors)

Many tests **exist but are broken**. Ask Claude.ai to fix them:

**PR Request Template:**
```
# Fix Test Collection Errors - Python 3.9 Compatibility

Fix RecursionError and TypeError issues preventing test collection.

## Problem:
- 207 test files have collection errors
- Main issues:
  - RecursionError: Python 3.9 can't evaluate `str | None` syntax
  - TypeError: Pydantic models with modern type annotations
  - ModuleNotFoundError: Missing test dependencies

## Files Affected:
[Paste output from: python3 -m pytest tests/ --collect-only -q 2>&1 | grep ERROR]

## Required Fixes:
1. Replace `str | None` with `Optional[str]` (Python 3.9 compatibility)
2. Replace `dict[str, Any]` with `Dict[str, Any]`
3. Add `from typing import Optional, Dict, List, Union`
4. Install missing test dependencies:
   ```bash
   pip install lz4 fakeredis aioresponses mcp dropbox slowapi
   ```
5. Fix module imports (aka_qualia, ethics.core paths)

## Test:
```bash
# After fixes, this should show 0 collection errors:
python3 -m pytest tests/ --collect-only -q
```

Please fix all collection errors systematically.
```

---

## 📊 Summary Statistics

| Category | Files | Lines of Code | Estimated Test Files | Priority |
|----------|-------|---------------|---------------------|----------|
| **serve/** | 20 | ~5,000 | 20 test files | 🔴 HIGH |
| **lukhas/** | 11 | ~3,500 | 11 test files | 🔴 HIGH |
| **matriz/** | 97 | ~50,000+ | 97 test files | 🟡 MEDIUM |
| **core/** | 273 | ~100,000+ | 273 test files | 🟢 LOW |
| **TOTAL** | 401 | ~158,500+ | 401 test files | - |

---

## 🎯 Recommended Workflow

### Week 1: Tier 1 Production Code (31 files)
- **Day 1-2**: Batch 1A-1D (serve/ - 20 files)
- **Day 3-4**: Batch 1E-1F (lukhas/ - 11 files)
- **Day 5**: Review, merge, fix any issues

### Week 2: Fix Broken Tests
- **Day 1-2**: Fix collection errors (207 files)
- **Day 3**: Run full test suite, verify 0 errors
- **Day 4-5**: Fix failing tests (smoke tests, integration tests)

### Week 3-4: Tier 2 MATRIZ Engine (97 files)
- **Week 3**: Batches 2A-2C (top 50 largest files)
- **Week 4**: Remaining MATRIZ files + integration tests

### Month 2+: Tier 3 Core Integration (273 files)
- Delegate in batches of 10-20 files
- Focus on critical integration points first

---

## 🤖 Tips for Claude.ai Delegation

### Best Practices:
1. **Upload context files**:
   - Source file to test
   - Related modules (imports)
   - Existing test examples from `tests/` directory
   - This guide (MISSING_TESTS_DELEGATION_GUIDE.md)

2. **Be specific in requests**:
   - "Create tests for serve/main.py with 80%+ coverage"
   - "Test all FastAPI routes, auth middleware, error handling"
   - "Mock external dependencies (OpenAI, MATRIZ)"

3. **Iterate**:
   - Review generated tests
   - Ask Claude.ai to add missing edge cases
   - Ask to increase coverage for specific functions

4. **Verify**:
   ```bash
   # Run new tests
   pytest tests/unit/serve/test_main.py -v

   # Check coverage
   pytest tests/unit/serve/test_main.py --cov=serve/main --cov-report=term-missing
   ```

5. **Create PR**:
   - Use descriptive title: "test(serve): add comprehensive tests for main.py"
   - Include coverage report in PR description
   - Reference this guide: "Part of MISSING_TESTS_DELEGATION_GUIDE.md - Batch 1B"

---

## 📋 Tracking Progress

### Checklist:

**Tier 1 - Production Code:**
- [ ] Batch 1A: serve/ Main API Endpoints (5 files)
- [ ] Batch 1B: serve/ OpenAI Routes (5 files)
- [ ] Batch 1C: serve/ Routes & Models (5 files)
- [ ] Batch 1D: serve/ Middleware (5 files)
- [ ] Batch 1E: lukhas/ Identity (4 files)
- [ ] Batch 1F: lukhas/ API & CLI (7 files)

**Fix Broken Tests:**
- [ ] Fix 207 collection errors (Python 3.9 compatibility)
- [ ] Fix 75 failing smoke tests
- [ ] Verify 0 collection errors

**Tier 2 - MATRIZ Engine:**
- [ ] Batch 2A: Consciousness (top 10 files)
- [ ] Batch 2B: Consciousness (next 10 files)
- [ ] Batch 2C: Memory & Reflection (20 files)
- [ ] Batch 2D-2J: Remaining MATRIZ (57 files)

**Tier 3 - Core Integration:**
- [ ] Defer until Tier 1 & 2 complete

---

## 🎉 Success Criteria

After completing this delegation:
- ✅ **0 collection errors** (all tests can be collected)
- ✅ **80%+ coverage** for lukhas/ and serve/
- ✅ **70%+ coverage** for matriz/
- ✅ **All smoke tests passing** (0 failures)
- ✅ **CI/CD pipeline green** (all checks pass)

---

## 📞 Need Help?

If Claude.ai gets stuck or you need clarification:
1. Check existing test patterns in `tests/smoke/` and `tests/unit/`
2. Review pytest documentation: https://docs.pytest.org
3. Check FastAPI testing guide: https://fastapi.tiangolo.com/tutorial/testing/
4. Consult LUKHAS docs in `docs/` directory

---

**Generated**: 2025-11-09
**Purpose**: Systematic test creation delegation to Claude.ai
**Target**: 401 test files, 158,500+ lines of code coverage
**Estimated Effort**: 4-8 weeks (depends on batch size and iteration speed)
