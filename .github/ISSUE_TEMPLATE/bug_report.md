# LUKHAS Bug Report and Testing Task Allocation

This report outlines the current known bugs in the LUKHAS system and identifies areas that require additional test coverage. The tasks below are designed to be assigned to agents to improve the overall quality and stability of the codebase.

**Last Updated**: 2025-11-05
**Total Issues**: 25 (10 HIGH, 8 MEDIUM, 7 LOW)
**Test Failure Rate**: 23.7% (82/345 smoke tests failing)

---

## 📍 Repository Navigation for Agents

### Essential Context Files (Read FIRST Before Working on ANY Bug)

Agents **MUST** read these context files before starting work to understand LUKHAS architecture:

- **Master Context**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` - Complete system overview
- **Development Lane**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/claude.me` - 2,877 files for experimental work
- **Integration Lane**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/core/` - 253 components for validation
- **Production Lane**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/claude.me` - 692 production components
- **MATRIZ Engine**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/matriz/` - Cognitive engine (Memory-Attention-Thought-Action-Decision-Awareness)
- **API Layer**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/` - FastAPI endpoints
- **Known Issues**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/KNOWN_ISSUES.md` - Detailed issue documentation

### Critical Architecture Rules

**Lane-Based Development System** (MUST UNDERSTAND):
- **candidate/** → Experimental research, imports from `core/` and `matriz/` ONLY
- **core/** → Integration testing, shared components
- **lukhas/** → Production code, imports from `core/`, `matriz/`, `universal_language/`
- **FORBIDDEN**: `candidate/` importing from `lukhas/` (breaks lane isolation)

**Validation Commands**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
make lane-guard          # Validate lane boundaries (currently broken - ISSUE-007)
make smoke               # Quick health check (15 tests)
make smoke-matriz        # MATRIZ engine tests
make test-tier1          # Critical system tests
make test-all            # Full test suite (775+ tests)
```

### Quality Thresholds

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| Test Coverage | 75%+ | Production promotion requirement |
| Syntax Health | >95% | Files must compile without errors |
| TODO/FIXME Count | <1,000 | Technical debt management |
| Security | 0 secrets | No hardcoded credentials in production |
| Lane Violations | 0 | Architecture boundary enforcement |
| MATRIZ Performance | <250ms p95 | Cognitive engine latency target |

---

## 📊 Current System Health Metrics

| Metric | Current | Threshold | Status | Impact |
|--------|---------|-----------|--------|--------|
| **Test Failure Rate** | 23.7% (82/345) | <5% | 🔴 CRITICAL | Core functionality broken |
| **TODO/FIXME Count** | 1,624 items | <1,000 | 🟡 HIGH | 62% over technical debt limit |
| **Lane Violations** | 0 detected* | 0 | ⚠️ UNKNOWN | *Validation tool broken (ISSUE-007) |
| **Syntax Health** | >95% | >95% | ✅ GOOD | Files compile successfully |
| **Security Audit Needed** | 430 files | 0 | 🔴 CRITICAL | Potential hardcoded secrets |
| **Circular Imports** | 45 files | <10 | 🟡 HIGH | Architecture debt |
| **Test Coverage** | 30% | 75% | 🔴 CRITICAL | Below production threshold |
| **Import Errors** | 12+ files | 0 | 🔴 CRITICAL | governance.schema_registry missing |

**Legend**: 🔴 CRITICAL | 🟡 HIGH | 🟢 MEDIUM | ⚪ LOW | ✅ GOOD

---

## 🔴 Critical Bugs (HIGH PRIORITY - Fix Immediately)

### ISSUE-006: Missing `governance.schema_registry` Module Path (P1 HIGH)

- **Component**: Root-level import configuration
- **Status**: Critical - Breaking 12+ files
- **Severity**: HIGH - Blocks multiple modules from importing
- **Test Failures**: Import errors across governance, memory, and test suites

**Description**:
The `governance.schema_registry` module cannot be imported using the expected path. Module exists at `/lukhas_website/lukhas/governance/schema_registry.py` but imports fail with `ModuleNotFoundError`.

**Files Affected**:
- `/lukhas_website/lukhas/memory/backends/base.py`
- `/tests/observability/test_label_contracts.py`
- `/tests/governance/test_lane_consistency.py`
- 9+ additional files across governance and memory subsystems

**Root Cause**:
Missing module alias or incorrect PYTHONPATH configuration. Expected import `from governance.schema_registry import LUKHASLane` fails.

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` (module structure)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/governance/`
- **Lane Location**: Production lane (`lukhas/`)
- **Architecture Impact**: Governance system and memory backends cannot function
- **Related Components**: Memory backends, lane consistency validators, observability

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Verify module exists
ls -la lukhas_website/lukhas/governance/schema_registry.py
# Check imports
grep -r "from governance.schema_registry" . --include="*.py"
# Test fix approaches
# Option 1: Add forwarding in governance/__init__.py
# Option 2: Update all imports to use full path
```

**Proposed Solution**:
1. Add module forwarding in `/governance/__init__.py`: `from lukhas_website.lukhas.governance.schema_registry import *`
2. OR: Update all 12+ imports to use full path: `from lukhas_website.lukhas.governance.schema_registry import LUKHASLane`
3. Verify with: `python -c "from governance.schema_registry import LUKHASLane"`

**Validation**:
```bash
pytest tests/governance/test_lane_consistency.py -v
pytest tests/observability/test_label_contracts.py -v
```

---

### ISSUE-007: Lane Guard Tool Broken - Cannot Validate Architecture Boundaries (P1 HIGH)

- **Component**: Build system / import validation
- **Status**: Critical - Architecture validation disabled
- **Severity**: HIGH - Cannot enforce core architectural rules
- **Command**: `make lane-guard`

**Description**:
The lane boundary validation tool is missing, preventing verification that `candidate/` doesn't import from `lukhas/` (critical architecture rule). This is a foundational requirement for the lane-based development system.

**Error Output**:
```
/bin/sh: .venv/bin/lint-imports: No such file or directory
make: *** [lane-guard] Error 127
```

**Root Cause**:
Missing `import-linter` package or incorrect installation path.

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` (lane architecture explanation)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/pyproject.toml` (import-linter config)
- **Lane Location**: Build system (affects all lanes)
- **Architecture Impact**: Cannot enforce lane isolation - risk of architectural degradation
- **Related Components**: All lanes (candidate, core, lukhas), Makefile build system

**Lane Boundary Rules Being Validated**:
- `candidate/` MUST NOT import from `lukhas/` ❌ FORBIDDEN
- `lukhas/` MAY import from `core/`, `matriz/`, `universal_language/` ✅
- `candidate/` MAY import from `core/`, `matriz/` ✅

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Check if import-linter is installed
pip list | grep import-linter
# Check pyproject.toml for configuration
cat pyproject.toml | grep -A 20 "import-linter"
# Verify .venv exists
ls -la .venv/bin/ | grep lint
```

**Proposed Solution**:
1. Install import-linter: `pip install import-linter`
2. Verify installation: `which lint-imports` or `python -m importlinter`
3. Update Makefile if binary path changed
4. Run validation: `make lane-guard`
5. Fix any violations found

**Validation**:
```bash
make lane-guard  # Should complete without errors
# Manual check for forbidden imports
grep -r "from lukhas" candidate/ --include="*.py" | grep -v "test" | grep -v "#"
```

---

### ISSUE-008: Dreams API Completely Missing - All Endpoints Return 404 (P1 HIGH)

- **Component**: `lukhas/api/` - Dreams API endpoints
- **Status**: Critical - 10/10 tests failing (100% failure rate)
- **Severity**: HIGH - Entire Dreams API subsystem non-functional
- **Test Failures**: All dreams endpoint tests

**Description**:
All Dreams API endpoints are returning 404 Not Found instead of expected responses. The Dreams router is not registered in the FastAPI application, making the entire Dreams functionality inaccessible via API.

**Failing Tests** (10 total):
- `tests/smoke/test_dreams.py::test_dreams_happy_path` - Expected 200, got 404
- `tests/smoke/test_dreams.py::test_dreams_requires_auth` - Expected 401, got 404
- `tests/smoke/test_dreams.py::test_dreams_trace_structure` - 404 error
- `tests/smoke/test_dreams_api.py::test_create_dream` - 404 error
- `tests/smoke/test_dreams_api.py::test_get_dream` - 404 error
- `tests/smoke/test_dreams_api.py::test_list_dreams` - 404 error
- `tests/smoke/test_dreams_api.py::test_update_dream` - 404 error
- `tests/smoke/test_dreams_api.py::test_delete_dream` - 404 error
- All other dreams endpoint tests failing with 404

**Expected Endpoints**:
- `POST /dreams` - Create dream
- `GET /dreams/{dream_id}` - Retrieve dream
- `GET /dreams` - List dreams
- `PUT /dreams/{dream_id}` - Update dream
- `DELETE /dreams/{dream_id}` - Delete dream

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me` (API structure)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/consciousness/dream/` (Dreams implementation)
  - Constellation Framework: 🌙 Dream star capabilities
- **Lane Location**: API layer (production) + Dreams implementation (candidate)
- **Architecture Impact**: Constellation Framework Dream star completely inaccessible via API
- **Related Components**: Consciousness subsystem, creative synthesis, imagination patterns

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Check if Dreams router exists
find . -name "*dream*router*" -o -name "*dreams*api*" | grep -v __pycache__
# Run failing tests to see exact errors
pytest tests/smoke/test_dreams.py -v
pytest tests/smoke/test_dreams_api.py -v
# Check FastAPI app for registered routers
grep -r "include_router" lukhas/api/ --include="*.py"
```

**Proposed Solution**:
1. Locate or create Dreams router in `lukhas/api/routers/dreams.py`
2. Implement CRUD endpoints for dreams
3. Register router in main FastAPI app (`lukhas/api/app.py`): `app.include_router(dreams_router, prefix="/dreams", tags=["dreams"])`
4. Add authentication middleware
5. Connect to Dreams implementation in `candidate/consciousness/dream/`

**Validation**:
```bash
# Start API server
uvicorn lukhas.api.app:app --reload --port 8000 &
# Test endpoints
curl -X GET http://localhost:8000/dreams
pytest tests/smoke/test_dreams.py -v
pytest tests/smoke/test_dreams_api.py -v
make smoke
```

---

### ISSUE-009: MATRIZ-API Integration Incomplete - Cognitive Engine Not Accessible (P1 HIGH)

- **Component**: MATRIZ cognitive engine → API integration
- **Status**: Critical - 10/10 MATRIZ integration tests failing (100% failure rate)
- **Severity**: HIGH - Core cognitive engine not exposed via API
- **Test Failures**: All MATRIZ orchestration, pipeline, and processing tests

**Description**:
The MATRIZ cognitive engine (Memory-Attention-Thought-Action-Decision-Awareness) is not integrated with the API layer. The cognitive DNA processing, node-based reasoning, and symbolic processing are inaccessible to API consumers.

**Failing Tests** (10 total):
- `test_matriz_cognitive_orchestration` - MATRIZ orchestration not available via API
- `test_matriz_memory_attention_thought_pipeline` - M-A-T pipeline not exposed
- `test_matriz_reasoning_stage` - Reasoning stage endpoint missing
- `test_matriz_action_stage` - Action stage endpoint missing
- `test_matriz_symbolic_dna_processing` - Symbolic DNA not accessible
- `test_matriz_node_based_processing` - Node processing endpoint missing
- All MATRIZ smoke tests failing

**MATRIZ Performance Targets** (not measurable without API):
- Latency: <250ms p95
- Memory: <100MB per operation
- Throughput: 50+ ops/sec

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/matriz/` (MATRIZ implementation)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/MATRIZ_GUIDE.md` (architecture)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me` (API layer)
- **Lane Location**: MATRIZ (core engine) + API layer (production)
- **Architecture Impact**: Core cognitive processing completely inaccessible - system brain not exposed
- **Related Components**: Consciousness, reasoning, memory, attention, thought processing

**MATRIZ Components to Expose**:
- Memory stage (context loading and recall)
- Attention stage (focus and relevance)
- Thought stage (reasoning and synthesis)
- Action stage (decision execution)
- Decision stage (choice evaluation)
- Awareness stage (meta-cognition)

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Review MATRIZ architecture
cat docs/MATRIZ_GUIDE.md
# Find MATRIZ implementation
ls -la matriz/
# Run failing tests
pytest tests/smoke/test_matriz_integration.py -v
# Check for existing MATRIZ API code
find lukhas/api -name "*matriz*" -o -name "*cognitive*"
```

**Proposed Solution**:
1. Create MATRIZ API router in `lukhas/api/routers/matriz.py`
2. Implement endpoints for each MATRIZ stage:
   - `POST /matriz/process` - Full pipeline execution
   - `POST /matriz/memory` - Memory stage
   - `POST /matriz/attention` - Attention stage
   - `POST /matriz/thought` - Thought stage
   - `POST /matriz/action` - Action stage
3. Add performance monitoring (latency, memory, throughput)
4. Register router in main app
5. Implement async processing for <250ms target

**Validation**:
```bash
pytest tests/smoke/test_matriz_integration.py -v
make smoke-matriz
# Performance validation
python -c "from matriz import CognitiveEngine; engine = CognitiveEngine(); print('MATRIZ OK')"
```

---

### ISSUE-010: Authentication Middleware Not Enforcing Auth - 15+ Security Failures (P1 HIGH)

- **Component**: Authentication & Authorization middleware
- **Status**: Critical - Security vulnerability
- **Severity**: HIGH - Unprotected endpoints expose security risks
- **Test Failures**: 15+ authentication and authorization tests

**Description**:
Authentication middleware is not properly enforced across API endpoints. Protected endpoints are returning 200 OK instead of 401 Unauthorized, allowing unauthenticated access to sensitive functionality.

**Failing Tests** (15+ total):
- `test_models_requires_auth` - Expected 401, got 200 (SECURITY RISK)
- `test_dreams_requires_auth` - Expected 401, got 404 (endpoint missing, but auth also broken)
- `test_embeddings_requires_auth` - Auth bypassed
- `test_responses_requires_auth` - Auth bypassed
- `test_concurrent_auth_validation` - Concurrent auth validation failing
- `test_concurrent_tenant_isolation` - Tenant boundaries not enforced
- Rate limiting tests failing (5 tests)

**Security Implications**:
- ⚠️ Unauthorized access to AI models
- ⚠️ Potential data leakage across tenants
- ⚠️ Rate limiting bypass possible
- ⚠️ Token validation not occurring

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/identity/claude.me` (ΛiD system)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/` (middleware)
  - Constellation Framework: ⚛️ Identity star
- **Lane Location**: Production lane (lukhas/identity, lukhas/api)
- **Architecture Impact**: Core security infrastructure compromised
- **Related Components**: ΛiD authentication, tenant isolation, rate limiting

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Review identity system
cat lukhas/identity/claude.me
# Check middleware configuration
find lukhas/api -name "*middleware*" -o -name "*auth*"
# Run failing auth tests
pytest tests/smoke/test_concurrency.py::test_concurrent_auth_validation -v
pytest tests/smoke/ -k "requires_auth" -v
```

**Proposed Solution**:
1. Review and fix auth middleware in `lukhas/api/middleware/auth.py`
2. Ensure middleware is registered in FastAPI app dependencies
3. Add `Depends(get_current_user)` to protected endpoints
4. Implement proper token validation using ΛiD system
5. Add tenant isolation validation
6. Fix rate limiting enforcement

**Validation**:
```bash
# Test unauthenticated request (should fail with 401)
curl -X GET http://localhost:8000/models
# Test with invalid token (should fail with 401)
curl -X GET http://localhost:8000/models -H "Authorization: Bearer invalid"
# Run auth tests
pytest tests/smoke/ -k "auth" -v
pytest tests/smoke/test_concurrency.py -v
```

---

### ISSUE-011: Models API Metadata Incomplete - 7 Tests Failing (P1 HIGH)

- **Component**: `/models` API endpoint
- **Status**: Active - Core endpoint partially broken
- **Severity**: HIGH - OpenAI compatibility broken
- **Test Failures**: 7 tests for model metadata and capabilities

**Description**:
The `/models` endpoint is not returning complete metadata for available models. Missing capabilities, descriptions, and LUKHAS MATRIZ model not present in model list.

**Failing Tests** (7 total):
- `test_models_lukhas_matriz_present` - MATRIZ model missing from list
- `test_models_metadata_complete` - Metadata incomplete (missing fields)
- `test_models_capabilities_field` - capabilities field missing or empty
- `test_models_description_present` - Description field missing
- `test_models_openai_compatible_format` - Not following OpenAI spec
- 2+ additional metadata validation tests

**Expected Model Metadata Format** (OpenAI-compatible):
```json
{
  "id": "lukhas-matriz-v1",
  "object": "model",
  "created": 1234567890,
  "owned_by": "lukhas-ai",
  "permission": [...],
  "capabilities": {
    "consciousness": true,
    "reasoning": true,
    "memory": true
  },
  "description": "LUKHAS MATRIZ cognitive engine with consciousness-aware processing"
}
```

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me`
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/matriz/` (MATRIZ model details)
- **Lane Location**: Production API layer
- **Architecture Impact**: API consumers cannot discover MATRIZ capabilities
- **Related Components**: MATRIZ engine, model registry, OpenAI compatibility layer

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Check current models endpoint
curl -X GET http://localhost:8000/models | jq
# Run failing tests
pytest tests/smoke/ -k "models" -v
# Find models endpoint implementation
grep -r "def.*models" lukhas/api/routers/ --include="*.py"
```

**Proposed Solution**:
1. Update `/models` endpoint in `lukhas/api/routers/models.py`
2. Add LUKHAS MATRIZ model to model registry
3. Include complete metadata fields: id, object, created, owned_by, capabilities, description
4. Ensure OpenAI-compatible response format
5. Document MATRIZ-specific capabilities

**Validation**:
```bash
curl -X GET http://localhost:8000/models | jq '.models[] | select(.id == "lukhas-matriz-v1")'
pytest tests/smoke/ -k "test_models" -v
```

---

### ISSUE-012: Responses API Missing/Broken - 15 Tests Failing (P1 HIGH)

- **Component**: `/responses` or `/chat/completions` endpoint
- **Status**: Critical - Core chat endpoint non-functional
- **Severity**: HIGH - Primary AI interaction endpoint broken
- **Test Failures**: 15 tests for chat completions and responses

**Description**:
The core chat/completions endpoint is missing or broken. This is the primary interface for AI interactions, making the system unusable for chat-based workflows.

**Failing Tests** (15 total):
- `test_responses_requires_auth` - Auth not enforced
- `test_responses_happy_path` - Basic completion fails
- `test_responses_stub_mode_echo` - Stub mode not working
- `test_responses_stream_mode` - Streaming responses broken
- `test_responses_openai_compatible` - Not following OpenAI spec
- Stream chunk format tests failing
- Response envelope tests failing
- 8+ additional response endpoint tests

**Expected Endpoint**: `POST /chat/completions` (OpenAI-compatible)

**Request Format**:
```json
{
  "model": "lukhas-matriz-v1",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}
```

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me`
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/matriz/` (response generation)
- **Lane Location**: Production API layer + MATRIZ integration
- **Architecture Impact**: Core AI interaction completely broken
- **Related Components**: MATRIZ engine, streaming, authentication, OpenAI compatibility

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Test endpoint
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"lukhas-matriz-v1","messages":[{"role":"user","content":"test"}]}'
# Run failing tests
pytest tests/smoke/ -k "responses" -v
# Find responses implementation
find lukhas/api -name "*response*" -o -name "*completion*"
```

**Proposed Solution**:
1. Create `/chat/completions` endpoint in `lukhas/api/routers/chat.py`
2. Implement OpenAI-compatible request/response format
3. Integrate with MATRIZ cognitive engine
4. Add streaming support (SSE)
5. Implement stub/echo mode for testing
6. Add authentication middleware
7. Add proper error handling

**Validation**:
```bash
pytest tests/smoke/ -k "responses" -v
# Test streaming
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"lukhas-matriz-v1","messages":[{"role":"user","content":"test"}],"stream":true}'
```

---

### ISSUE-013: Error Envelope Non-Compliant with OpenAI Spec - 20+ Tests Failing (P1 HIGH)

- **Component**: Error handling middleware and response formatting
- **Status**: Active - All error responses malformed
- **Severity**: HIGH - API not OpenAI-compatible
- **Test Failures**: 20+ error format validation tests

**Description**:
Error responses are not following the OpenAI API error envelope format. This breaks compatibility with OpenAI client libraries and creates inconsistent error handling.

**Failing Tests** (20+ total):
- `test_envelope_401_minimal` - 401 error format incorrect
- `test_envelope_403_minimal` - 403 error format incorrect
- `test_400_missing_required_field_responses` - 400 format incorrect
- `test_401_error_format_openai_compatible` - Auth error format wrong
- `test_404_error_format` - Not found format wrong
- `test_500_error_format` - Server error format wrong
- Multiple envelope validation tests failing
- Error detail tests failing

**Expected OpenAI Error Format**:
```json
{
  "error": {
    "message": "Invalid authentication credentials",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_api_key"
  }
}
```

**Current Format** (incorrect):
```json
{
  "detail": "Unauthorized",
  "status_code": 401
}
```

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me`
  - OpenAI API documentation (external)
- **Lane Location**: Production API middleware
- **Architecture Impact**: All error responses break client compatibility
- **Related Components**: Exception handlers, middleware, response formatting

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Test current error format
curl -X GET http://localhost:8000/models -H "Authorization: Bearer invalid"
# Run failing tests
pytest tests/smoke/ -k "envelope" -v
pytest tests/smoke/ -k "error_format" -v
# Find error handlers
grep -r "exception_handler" lukhas/api/ --include="*.py"
```

**Proposed Solution**:
1. Create custom exception classes in `lukhas/api/exceptions.py`
2. Implement exception handler middleware
3. Format all errors as: `{"error": {"message": str, "type": str, "param": str, "code": str}}`
4. Map HTTP status codes to OpenAI error types:
   - 400 → `invalid_request_error`
   - 401 → `authentication_error`
   - 403 → `permission_error`
   - 404 → `not_found_error`
   - 500 → `server_error`
5. Register exception handlers in FastAPI app

**Validation**:
```bash
pytest tests/smoke/ -k "envelope" -v
pytest tests/smoke/ -k "error" -v
# Manual validation
curl -X GET http://localhost:8000/invalid-endpoint | jq
```

---

### ISSUE-014: Missing `lz4` Dependency - Guardian Serialization Broken (P1 HIGH)

- **Component**: Guardian system serializers
- **Status**: Blocked - Phase 7 Guardian features unavailable
- **Severity**: HIGH - Guardian constitutional AI serialization broken
- **Error**: `Phase 7 Guardian Serializers not available: No module named 'lz4'`

**Description**:
The Guardian system's Phase 7 serializers require the `lz4` compression library, which is not installed. This breaks efficient state serialization for the constitutional AI system.

**Guardian Impact**:
- Cannot serialize Guardian state efficiently
- Constitutional validation history not persisted properly
- Potential memory bloat without compression

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/governance/claude.me`
  - Constellation Framework: 🛡️ Guardian star
- **Lane Location**: Production governance layer
- **Architecture Impact**: Guardian state management inefficient/broken
- **Related Components**: Constitutional AI, ethical enforcement, Guardian serialization

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Check current dependencies
pip list | grep lz4
# Review requirements
cat requirements.txt | grep lz4
cat pyproject.toml | grep lz4
# Find Guardian serializer code
find lukhas/governance -name "*serial*" -o -name "*guardian*"
```

**Proposed Solution**:
1. Add `lz4` to `requirements.txt`: `lz4>=4.0.0`
2. Add to `pyproject.toml` dependencies: `"lz4>=4.0.0"`
3. Install: `pip install lz4`
4. Verify Phase 7 serializers load: `python -c "from lukhas.governance.guardian import serializers"`
5. Test Guardian state serialization

**Validation**:
```bash
pip install lz4
python -c "import lz4; print('lz4 OK')"
# Test Guardian serialization
pytest tests/unit/governance/ -k "serial" -v
```

---

### ISSUE-015: 430 Files Flagged for Potential Hardcoded Secrets - SECURITY AUDIT NEEDED (P1 HIGH)

- **Component**: Codebase-wide security audit
- **Status**: Active - Requires manual security review
- **Severity**: HIGH - Potential credential exposure
- **Files**: 430 files contain patterns: `password=`, `secret=`, `api_key=`, `token=`, `credential=`

**Description**:
Automated security scan found 430 files with potential hardcoded secrets. While many may be false positives (test fixtures, comments, variable names), a comprehensive audit is required to ensure no actual credentials are committed.

**High-Risk Areas**:
- `/config/` directory (configuration files)
- `/tests/` fixtures (test credentials)
- Bridge adapters (OAuth managers)
- Environment variable defaults
- Database connection strings

**Security Risk**:
- Credentials in version control
- API keys exposed in source code
- Database passwords hardcoded
- OAuth secrets committed

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` (security standards)
- **Lane Location**: All lanes (candidate, core, lukhas)
- **Architecture Impact**: Potential security breach if real secrets found
- **Related Components**: All authentication systems, external integrations

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Run security scan
make security-scan
# Search for patterns (sample)
grep -r "password=" . --include="*.py" | grep -v "test" | head -20
grep -r "api_key=" . --include="*.py" | grep -v "test" | head -20
# Check for actual secrets (not just variable names)
grep -rE "password\s*=\s*['\"]" . --include="*.py" | grep -v "your_password"
```

**Manual Audit Required for**:
- Any actual credential values (not variable names)
- Database connection strings with embedded credentials
- API keys in configuration files
- OAuth client secrets
- Encryption keys or tokens

**Proposed Solution**:
1. Review all 430 files manually or with specialized security agent
2. Move any real secrets to environment variables
3. Update code to use `os.environ.get()` for credentials
4. Add `.env.example` with placeholder values
5. Update `.gitignore` to exclude `.env` files
6. Document required environment variables in README
7. Use secrets management (HashiCorp Vault, AWS Secrets Manager)

**Validation**:
```bash
# Ensure no real secrets remain
make security-scan
# Check .env is gitignored
git check-ignore .env
# Verify environment variable usage
grep -r "os.environ" lukhas/ --include="*.py" | grep -i "password\|secret\|key"
```

---

## 🟡 High Priority Bugs (MEDIUM PRIORITY - Fix This Sprint)

### ISSUE-001: Fix MCP Server Test Fixture Incompatibility (P2 MEDIUM)

- **Component**: `tests/integration/tools/test_lukhas_mcp_server.py`
- **Status**: Blocked
- **Severity**: MEDIUM - Integration tests blocked
- **Test Failures**: 6 MCP server tests

**Description**:
The MCP Server tests are failing due to a missing `mcp` library and an incompatible test fixture design. This blocks all integration tests for the MCP (Model Context Protocol) server that enables Claude Desktop integration.

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/` (MCP server implementations)
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/KNOWN_ISSUES.md` (detailed solutions)
- **Lane Location**: Integration tests + MCP tools
- **Architecture Impact**: Claude Desktop integration cannot be validated
- **Related Components**: 5 MCP servers (filesystem, git, postgres, sequential, github)

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Check MCP library
pip list | grep mcp
# Run failing tests
pytest tests/integration/tools/test_lukhas_mcp_server.py -v
# Review MCP servers
ls -la mcp-servers/
```

**Task**:
- Install the `mcp` library as a development dependency
- Refactor tests to use proper mocking strategy (see `tests/KNOWN_ISSUES.md`)
- Ensure all 6 MCP server tests pass without requiring external dependencies

**Validation**:
```bash
pip install mcp-server
pytest tests/integration/tools/test_lukhas_mcp_server.py -v
```

---

### ISSUE-002: Correct Consent Expiration Validation Message (P2 MEDIUM)

- **Component**: `tests/unit/governance/compliance/test_consent_manager.py`
- **Status**: Active
- **Severity**: MEDIUM - Consent validation logic incorrect
- **Test Failures**: 1 test (`test_consent_expiration_and_cleanup`)

**Description**:
The `test_consent_expiration_and_cleanup` test is failing because the validation logic returns "No active consent found" instead of the expected "Consent has expired." This indicates incorrect validation priority in the consent manager.

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/governance/claude.me`
  - Constellation Framework: 🛡️ Guardian star (compliance)
- **Lane Location**: Production governance layer
- **Architecture Impact**: Consent management provides incorrect user feedback
- **Related Components**: GDPR compliance, consent management, data governance

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Run failing test
pytest tests/unit/governance/compliance/test_consent_manager.py::test_consent_expiration_and_cleanup -v
# Find consent manager implementation
find lukhas/governance -name "*consent*"
```

**Task**:
- Update the `validate_consent()` function to prioritize checking for expiration before checking for the existence of active consent
- OR: Update test's expectations to match current behavior if semantically correct
- Ensure user-facing error messages are clear and actionable

**Validation**:
```bash
pytest tests/unit/governance/compliance/test_consent_manager.py -v
```

---

### ISSUE-003: Calibrate Constitutional AI Safety Levels (P2 MEDIUM)

- **Component**: `tests/unit/governance/ethics/test_constitutional_ai.py`
- **Status**: Active
- **Severity**: MEDIUM - Safety thresholds misconfigured
- **Test Failures**: Multiple Constitutional AI tests

**Description**:
Multiple tests are failing because the Constitutional AI's safety level assessments do not align with the expected outcomes. The current thresholds may be too conservative, or the test data may be unclear.

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/governance/claude.me`
  - Constellation Framework: ⚖️ Ethics + 🛡️ Guardian stars
- **Lane Location**: Production governance layer
- **Architecture Impact**: Constitutional AI may be over/under-restrictive
- **Related Components**: Ethical guardian, value alignment, constitutional enforcement

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Run failing tests
pytest tests/unit/governance/ethics/test_constitutional_ai.py -v
# Find Constitutional AI implementation
find lukhas/governance/ethics -name "*constitutional*"
```

**Task**:
- Review and adjust safety thresholds to better align with realistic scenarios
- Enhance test data to provide clearer examples of safe and unsafe content
- Consider adding configuration for thresholds to make system more flexible for testing
- Document threshold rationale

**Validation**:
```bash
pytest tests/unit/governance/ethics/test_constitutional_ai.py -v
```

---

### ISSUE-016: Embeddings API Auth Bypass and Error Handling (P2 MEDIUM)

- **Component**: `/embeddings` endpoint
- **Status**: Active
- **Severity**: MEDIUM - Auth and validation issues
- **Test Failures**: 4 tests

**Failing Tests**:
- `test_embeddings_empty_input_handled` - Empty input not validated
- `test_embeddings_missing_input_field` - Missing field error not proper
- `test_embeddings_requires_auth` - Auth not enforced

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me`
- **Lane Location**: Production API layer
- **Architecture Impact**: Embeddings endpoint has security and validation gaps

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/smoke/ -k "embeddings" -v
find lukhas/api -name "*embedding*"
```

**Proposed Solution**:
- Add authentication middleware
- Implement input validation for empty/missing fields
- Return proper error envelopes (ISSUE-013)

---

### ISSUE-017: Rate Limiting Not Enforced (P2 MEDIUM)

- **Component**: Rate limiting middleware
- **Status**: Active
- **Severity**: MEDIUM - DoS protection missing
- **Test Failures**: 5 rate limiting tests

**Failing Tests**:
- `test_rate_limiting_requests_per_minute`
- `test_rate_limiting_token_bucket`
- `test_rate_limiting_burst_protection`
- 2+ additional rate limit tests

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/api/claude.me`
- **Lane Location**: Production API middleware
- **Architecture Impact**: API vulnerable to abuse/DoS

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/smoke/test_rate_limiting.py -v
find lukhas/api -name "*rate*" -o -name "*limit*"
```

**Proposed Solution**:
- Implement rate limiting middleware (token bucket algorithm)
- Add Redis backend for distributed rate limiting
- Configure per-endpoint limits
- Add rate limit headers (X-RateLimit-Remaining, etc.)

---

### ISSUE-018: Metrics and Observability Endpoints Missing (P2 MEDIUM)

- **Component**: Observability layer
- **Status**: Active
- **Severity**: MEDIUM - Monitoring blind spots
- **Test Failures**: 5 metrics/health tests

**Failing Tests**:
- `test_metrics_track_requests` - Request metrics not tracked
- `test_metrics_track_latency` - Latency metrics missing
- `test_healthz_includes_checks` - Health checks incomplete
- `test_readyz_validates_dependencies` - Readiness probe broken
- `test_error_tracking` - Error tracking not implemented

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/monitoring/`
- **Lane Location**: Production monitoring layer
- **Architecture Impact**: Cannot monitor system health/performance

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/smoke/ -k "metrics\|health" -v
find lukhas -name "*metric*" -o -name "*health*"
```

**Proposed Solution**:
- Implement Prometheus metrics endpoint at `/metrics`
- Add comprehensive health checks at `/healthz` and `/readyz`
- Track: request count, latency (p50/p95/p99), error rate, active connections
- Integrate with MATRIZ performance monitoring

---

### ISSUE-019: Circular Import Refactoring Needed (P2 MEDIUM)

- **Component**: 45 files with circular import patterns
- **Status**: Active - Architecture debt
- **Severity**: MEDIUM - Maintenance burden and potential runtime issues

**Files Affected** (45 total, key examples):
- `/tools/automation/comprehensive_import_fixer.py`
- `/tools/analysis/circular_dependency_analysis.py`
- `/lukhas_website/lukhas/memory/lifecycle.py`
- `/labs/memory/systems/memory_comprehensive.py`
- `/labs/governance/guardian/core.py`
- 40+ additional files

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me` (architecture principles)
- **Lane Location**: All lanes
- **Architecture Impact**: Tight coupling, difficult refactoring, potential import errors

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Find circular imports
grep -r "circular" tools/analysis/ --include="*.py"
# Run analysis
python tools/analysis/circular_dependency_analysis.py
```

**Proposed Solution**:
- Refactor to use dependency injection pattern
- Move shared interfaces to separate modules
- Use late imports (import inside functions) as temporary fix
- Apply single responsibility principle
- Consider architectural refactoring for tightly coupled modules

---

### ISSUE-020: Makefile Duplicate Target Warnings (P2 MEDIUM)

- **Component**: Build system (Makefile)
- **Status**: Active - Build confusion
- **Severity**: MEDIUM - Some targets may not execute as expected
- **Warnings**: 15 duplicate target definitions

**Duplicate Targets**:
- `sbom` (defined in 2 places)
- `smoke` (defined in 2 places)
- `test` (defined in 2 places)
- `audit` (defined in 2 places)
- `lint` (defined in 2 places)
- 10+ additional duplicates

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/Makefile`
- **Lane Location**: Build system
- **Architecture Impact**: Build commands may not execute expected actions

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Check for duplicate targets
make -p | grep "^[a-z]" | sort | uniq -d
# Review Makefile
cat Makefile | grep "^[a-z].*:"
```

**Proposed Solution**:
- Consolidate duplicate targets into single definitions
- Use target-specific variables if multiple behaviors needed
- Consider splitting into multiple Makefiles with includes
- Document target precedence rules

---

## 🟢 Medium Priority Issues (NEXT SPRINT)

### ISSUE-005: Investigate Bio-Symbolic Integration Coherence Calculation (P3 LOW)

- **Component**: `tests/unit/bio/core/test_bio_symbolic.py`
- **Status**: Active
- **Severity**: LOW - Algorithm behavior unclear
- **Test Failures**: 1 test (`test_integrate`)

**Description**:
The `test_integrate` test is failing because the coherence calculation returns `0.75` instead of the expected `1.0`. This may indicate either incorrect test expectations or an actual algorithmic issue.

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/bio/claude.me`
  - Constellation Framework: 🌱 Bio star
- **Lane Location**: Development lane (candidate/bio)
- **Architecture Impact**: Bio-symbolic integration coherence unclear
- **Related Components**: Bio-inspired adaptation, symbolic processing

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/unit/bio/core/test_bio_symbolic.py::test_integrate -v
find candidate/bio -name "*symbolic*"
```

**Task**:
- Review coherence calculation algorithm to determine if output is correct
- If algorithm is correct, update test expectations to match actual output
- Document the coherence calculation methodology to clarify expected behavior

---

### ISSUE-021: Memory Indexing Systems Not Available (P3 MEDIUM)

- **Component**: Memory subsystem
- **Status**: Skipped - Missing implementation
- **Severity**: MEDIUM - Core memory features disabled
- **Test Failures**: 17 tests skipped

**Skipped Tests**:
- All tests requiring `EmbeddingIndex`
- All tests requiring `IndexManager`
- Memory search tests
- Memory retrieval tests

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/claude.me`
  - Constellation Framework: ✦ Memory star
- **Lane Location**: Production memory layer
- **Architecture Impact**: Memory search/retrieval non-functional

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/smoke/test_memory_systems.py -v
find lukhas/memory -name "*index*"
```

**Proposed Solution**:
- Implement `EmbeddingIndex` class for vector search
- Implement `IndexManager` for index lifecycle management
- Add vector database backend (FAISS, Weaviate, Qdrant)
- Enable skipped memory tests

---

### ISSUE-022: Technical Debt - 1,624 TODO/FIXME Items (P3 MEDIUM)

- **Component**: Codebase-wide
- **Status**: Active - Technical debt accumulation
- **Severity**: MEDIUM - 62% over threshold (1000 item limit)
- **Count**: 1,624 TODO/FIXME items across 686 files

**Breakdown**:
- Test files: ~300+ TODOs
- Core modules: ~200 TODOs
- Candidate lane: ~800+ TODOs (experimental, acceptable)
- Production lane: ~300+ TODOs (concerning)

**Agent Context**:
- **Relevant Context Files**: All context files
- **Lane Location**: All lanes
- **Architecture Impact**: Indicates incomplete features and deferred work

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
# Count TODOs
grep -r "TODO\|FIXME" . --include="*.py" | wc -l
# Find high-priority TODOs
grep -r "TODO.*CRITICAL\|FIXME.*URGENT" . --include="*.py"
```

**Proposed Solution**:
- Triage all 1,624 items
- Convert to GitHub issues with proper labels
- Prioritize production lane TODOs
- Remove stale/obsolete TODOs
- Set quarterly goal: reduce to <1000 items

---

### ISSUE-023: Consciousness Pipeline Tests Skipped (P3 MEDIUM)

- **Component**: Consciousness subsystem
- **Status**: Skipped - External dependencies needed
- **Severity**: MEDIUM - Core consciousness features untested
- **Test Failures**: ~30 tests skipped

**Agent Context**:
- **Relevant Context Files**:
  - `/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/consciousness/claude.me`
  - Constellation Framework: Full 8-star system
- **Lane Location**: Development lane consciousness
- **Architecture Impact**: Consciousness features not validated

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/smoke/test_consciousness_pipeline.py -v
find candidate/consciousness -type f -name "*.py"
```

**Proposed Solution**:
- Install missing dependencies for consciousness tests
- Enable consciousness pipeline tests
- Validate consciousness processing workflows
- Document consciousness architecture

---

### ISSUE-024: External Dependencies Documentation Needed (P3 LOW)

- **Component**: Documentation
- **Status**: Active - Missing dependency docs
- **Severity**: LOW - Onboarding friction

**Missing Dependencies** (5 skipped tests):
- Redis client (caching)
- PostgreSQL driver (persistence)
- S3 backend (boto3) (cloud storage)
- CloudConsolidation (integration)
- SQLAlchemy (ORM)

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/README.md`
- **Lane Location**: Documentation
- **Architecture Impact**: New developers cannot set up full environment

**Quick Start for Agents**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
cat requirements.txt
cat pyproject.toml | grep dependencies
```

**Proposed Solution**:
- Document all optional dependencies in README
- Create `DEPENDENCIES.md` with setup instructions
- Add docker-compose for external services (Redis, PostgreSQL)
- Document which features require which dependencies

---

### ISSUE-025: Python Binary Not in PATH (P3 LOW)

- **Component**: Python environment
- **Status**: Active - Minor compatibility issue
- **Severity**: LOW - Some scripts may fail
- **Issue**: `python` command not found (only `python3` available)

**Agent Context**:
- **Relevant Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/scripts/`
- **Lane Location**: Build system
- **Architecture Impact**: Scripts with `#!/usr/bin/env python` will fail

**Quick Start for Agents**:
```bash
which python    # Not found
which python3   # Found
# Check shebang lines
grep -r "#!/usr/bin/env python" scripts/ --include="*.py"
```

**Proposed Solution**:
- Update all shebang lines to use `python3`
- OR: Create symlink: `ln -s $(which python3) /usr/local/bin/python`
- Update Makefile to use `python3` explicitly

---

## 📋 Test Suite Breakdown by Component

| Component | Total Tests | Passing | Failing | Skipped | Failure Rate |
|-----------|-------------|---------|---------|---------|--------------|
| **Dreams API** | 10 | 0 | 10 | 0 | 100% 🔴 |
| **MATRIZ Integration** | 10 | 0 | 10 | 0 | 100% 🔴 |
| **Responses API** | 15 | 0 | 15 | 0 | 100% 🔴 |
| **Error Handling** | 20 | 0 | 20 | 0 | 100% 🔴 |
| **Authentication** | 15 | 0 | 15 | 0 | 100% 🔴 |
| **Models API** | 7 | 0 | 7 | 0 | 100% 🔴 |
| **Rate Limiting** | 5 | 0 | 5 | 0 | 100% 🔴 |
| **Metrics/Health** | 5 | 0 | 5 | 0 | 100% 🔴 |
| **Embeddings API** | 4 | 0 | 4 | 0 | 100% 🔴 |
| **Memory Systems** | 17 | 0 | 0 | 17 | N/A ⚠️ |
| **Consciousness** | 30 | 0 | 0 | 30 | N/A ⚠️ |
| **Governance** | 15 | 10 | 5 | 0 | 33% 🟡 |
| **Bio-Symbolic** | 10 | 9 | 1 | 0 | 10% 🟢 |
| **MCP Integration** | 6 | 0 | 6 | 0 | 100% 🔴 |
| **Other** | 176 | 168 | 8 | 0 | 4.5% 🟢 |
| **TOTAL** | 345 | 187 | 82 | 76 | 23.7% 🔴 |

---

## 🎯 Agent Task Allocation Matrix

This matrix assigns specialized agents to priority issues for maximum efficiency:

| Agent Type | Specialization | Assigned Issues | Estimated Effort | Priority |
|------------|---------------|-----------------|------------------|----------|
| **Import/Module Specialist** | Python imports, module structure | ISSUE-006, ISSUE-007 | 2-3 hours | P1 🔴 |
| **API Integration Specialist** | FastAPI, REST endpoints | ISSUE-008, ISSUE-011, ISSUE-012, ISSUE-016 | 6-8 hours | P1 🔴 |
| **Security Specialist** | Auth, secrets management | ISSUE-010, ISSUE-015, ISSUE-017 | 4-6 hours | P1 🔴 |
| **MATRIZ Specialist** | Cognitive engine integration | ISSUE-009 | 4-5 hours | P1 🔴 |
| **Testing Specialist** | Test fixtures, error envelopes | ISSUE-013, ISSUE-001 | 3-4 hours | P1 🔴 |
| **DevOps Specialist** | Dependencies, build system | ISSUE-014, ISSUE-020, ISSUE-025 | 2-3 hours | P2 🟡 |
| **Refactoring Specialist** | Code architecture, patterns | ISSUE-019 | 8-12 hours | P2 🟡 |
| **Governance Specialist** | Constitutional AI, compliance | ISSUE-002, ISSUE-003 | 3-4 hours | P2 🟡 |
| **Observability Specialist** | Metrics, monitoring, health | ISSUE-018 | 3-4 hours | P2 🟡 |
| **Memory Systems Specialist** | Vector search, indexing | ISSUE-021 | 6-8 hours | P3 🟢 |
| **Consciousness Specialist** | Consciousness pipeline | ISSUE-023 | 4-6 hours | P3 🟢 |
| **Documentation Specialist** | Docs, onboarding | ISSUE-022, ISSUE-024 | 4-5 hours | P3 🟢 |
| **Bio-Symbolic Specialist** | Bio-inspired algorithms | ISSUE-005 | 1-2 hours | P3 🟢 |

---

## 📚 Areas Requiring New Test Coverage

### Area 1: Improve Test Coverage for Governance/Ethics

- **Component**: `governance/ethics/`
- **Current Coverage**: 60%
- **Target**: 85%
- **Status**: Needs Work

**Description**:
The Governance and Ethics component has several failing tests and low overall test coverage. This is a critical area that requires a robust test suite to ensure the system's ethical guidelines are enforced correctly.

**Task**:
- Write new unit tests for the modules in `governance/ethics/`, focusing on the `ConstitutionalAI` and `EnhancedEthicalGuardian` components
- Add integration tests to verify the interaction between different modules within governance
- Test ethical boundary enforcement
- Validate constitutional validation workflows
- Test drift detection mechanisms

**Agent Context**:
- **Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/governance/claude.me`
- **Constellation Stars**: ⚖️ Ethics + 🛡️ Guardian

**Quick Start**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/unit/governance/ethics/ -v --cov=lukhas/governance/ethics
pytest tests/integration/governance/ -v
```

---

### Area 2: Add Integration Tests for Tools

- **Component**: `tools/`
- **Current Coverage**: 14.3%
- **Target**: 75%
- **Status**: Blocked by ISSUE-001

**Description**:
The Tools integration component has critically low test coverage and is currently blocked by failing MCP server tests. Once the MCP server tests are fixed, this area needs a comprehensive suite of integration tests.

**Task**:
- After `ISSUE-001` is resolved, write new integration tests for all tools in the `tools/` directory
- Create tests that verify correct interaction between tools and other parts of LUKHAS system
- Ensure tests cover both successful and unsuccessful execution paths
- Test all 5 MCP servers (filesystem, git, postgres, sequential, github)

**Agent Context**:
- **Context Files**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/`
- **Dependencies**: Resolve ISSUE-001 first

**Quick Start**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/integration/tools/ -v --cov=tools
ls -la mcp-servers/
```

---

### Area 3: API Endpoint Test Coverage

- **Component**: `lukhas/api/`
- **Current Coverage**: ~40% (estimated)
- **Target**: 85%
- **Status**: Active

**Missing Test Areas**:
- OpenAI compatibility validation
- Streaming response handling
- Error envelope compliance across all endpoints
- Authentication edge cases
- Rate limiting validation
- Concurrent request handling
- Tenant isolation

**Quick Start**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/smoke/ -v --cov=lukhas/api
pytest tests/integration/api/ -v
```

---

### Area 4: MATRIZ Performance Testing

- **Component**: `matriz/`
- **Current Coverage**: Unknown
- **Target**: Performance benchmarks + 80% test coverage
- **Status**: Blocked by ISSUE-009

**Missing Test Areas**:
- Latency benchmarks (target: <250ms p95)
- Memory profiling (target: <100MB)
- Throughput testing (target: 50+ ops/sec)
- Cognitive pipeline stage validation
- Node-based processing correctness
- Symbolic DNA processing

**Quick Start**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/unit/matriz/ -v
pytest tests/performance/matriz/ -v
make smoke-matriz
```

---

## 🔧 Quick Commands Reference for Agents

### Essential Navigation
```bash
# Always start here
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Read master context
cat claude.me

# Check system health
make doctor
```

### Testing Commands
```bash
# Quick health check (15 tests)
make smoke

# MATRIZ engine tests
make smoke-matriz

# Critical tests
make test-tier1

# Full suite (775+ tests)
make test-all

# Specific component
pytest tests/unit/governance/ -v
pytest tests/smoke/test_dreams.py -v
```

### Validation Commands
```bash
# Lane boundaries (currently broken)
make lane-guard

# Import health
make imports-guard

# Security scan
make security-scan

# Lint and format
make lint
make format
```

### Development Commands
```bash
# Bootstrap environment
make bootstrap

# Start dev environment
make dev

# Start API server
uvicorn lukhas.api.app:app --reload --port 8000

# Run audit
make audit
```

---

## 📈 Success Metrics

Track these metrics to measure progress:

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Test Failure Rate | 23.7% | <5% | 🔴 |
| Test Coverage | 30% | 75% | 🔴 |
| TODO/FIXME Count | 1,624 | <1,000 | 🟡 |
| Circular Imports | 45 files | <10 | 🟡 |
| Security Audit | 430 files | 0 suspicious | 🔴 |
| Lane Violations | Unknown | 0 | ⚠️ |
| API Endpoints Functional | 30% | 100% | 🔴 |
| MATRIZ Integration | 0% | 100% | 🔴 |

---

## 📝 Notes for Agents

### Before Starting ANY Task:
1. ✅ Read relevant `claude.me` context file
2. ✅ Understand lane location (candidate/core/lukhas)
3. ✅ Review architecture impact
4. ✅ Check related components
5. ✅ Run tests to reproduce issue

### During Work:
1. ✅ Follow lane isolation rules
2. ✅ Write tests for fixes
3. ✅ Validate with `make smoke` or `make test-tier1`
4. ✅ Check for circular imports
5. ✅ Update documentation

### Before Completing:
1. ✅ All tests passing
2. ✅ No new lane violations
3. ✅ Coverage maintained/improved
4. ✅ Documentation updated
5. ✅ Commit with T4 format

### Git Commit Template:
```
<type>(<scope>): <imperative subject ≤72>

Problem:
- Issue description

Solution:
- Fix implementation

Impact:
- What changed and why it matters

Validation:
- Tests passing
- Coverage metrics

Closes: #ISSUE-XXX
```

---

**END OF BUG REPORT**

For detailed implementation guidance, see:
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/KNOWN_ISSUES.md`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/architecture/`
