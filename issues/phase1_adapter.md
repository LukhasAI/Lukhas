# Phase 1: QRG Adapter & Sandbox Implementation

**Status**: Ready for assignment (after Phase 0 approval)
**Depends on**: Phase 0 spec approval (docs/specs/QRG_SPEC.md, docs/ADR/000-qrg-spec-adr.md)
**Related Spec**: [QRG_SPEC.md](../docs/specs/QRG_SPEC.md)
**Related ADR**: [000-qrg-spec-adr.md](../docs/ADR/000-qrg-spec-adr.md)
**Estimated Duration**: 3-4 weeks
**Owner**: TBD (Identity Team Lead or Platform Team Lead)

---

## Overview

Implement the QRGAdapter protocol interface and MockQRGAdapter implementation for safe development and testing of Quantum Reality Generation capabilities. This phase establishes the contract between QRG and LUKHAS core systems without requiring production dependencies (consciousness, safety gates, provenance services).

---

## Goals

1. **Define QRGAdapter Protocol** - Type-safe contract for QRG implementations
2. **Build MockQRGAdapter** - Deterministic sandbox implementation for testing
3. **Feature Flags** - Enable gradual rollout and emergency disable
4. **Testing Infrastructure** - Unit tests, integration tests, canary tests
5. **Developer Documentation** - Guide for using mock vs production adapters

---

## Deliverables

### 1. Adapter Protocol Interface

**File**: `lukhas/quantum/qrg_adapter.py`

**Contents**:
- `QRGAdapter` Protocol class (typed, documented)
- `BaseQRGAdapter` ABC with common functionality
- Custom exceptions:
  - `QRGGenerationError`
  - `QRGSafetyRejection`
  - `QRGTimeoutError`

**Methods**:
- `async def generate(user_id, seed, context, options) -> Dict[str, Any]`
- `async def validate(qrg_id, expected_hash) -> Dict[str, bool]`
- `async def health() -> Dict[str, Any]`

**Acceptance Criteria**:
- [ ] Protocol interface fully typed (mypy passes)
- [ ] Docstrings for all public methods (numpy style)
- [ ] Type hints for all parameters and return values
- [ ] Custom exceptions inherit from base Exception
- [ ] Protocol conforms to QRG_SPEC.md Section 5

---

### 2. Mock Adapter Implementation

**File**: `lukhas/quantum/qrg_mock.py`

**Contents**:
- `MockQRGAdapter` class implementing `QRGAdapter` protocol
- Deterministic artifact generation (seed-based)
- Mock safety gate simulation (approve/reject)
- Mock provenance block generation (SBOM refs, attestations)

**Behavior**:
- **Deterministic**: Same seed → same QRG ID, tokens, affect vector
- **Sandbox-only**: Never used in production code paths
- **Predictable**: All tests produce reproducible results
- **Fast**: No external dependencies, <100ms per request

**Acceptance Criteria**:
- [ ] Implements all QRGAdapter protocol methods
- [ ] Deterministic mode: same seed produces same output
- [ ] Safety gate simulation: approve by default, reject via context flag
- [ ] Provenance block: includes mock SBOM ref, attestation ref, signature
- [ ] No external dependencies (no real consciousness, safety, or provenance services)
- [ ] Documentation clearly states "SANDBOX-ONLY" in docstrings and comments

---

### 3. Feature Flags

**File**: Configuration via environment variables or config file

**Flags**:
```python
QRG_ENABLED = os.environ.get("QRG_ENABLED", "false").lower() == "true"
QRG_CONSCIOUSNESS_ENABLED = os.environ.get("QRG_CONSCIOUSNESS_ENABLED", "false").lower() == "true"
QRG_CONSENSUS_ENABLED = os.environ.get("QRG_CONSENSUS_ENABLED", "false").lower() == "true"
```

**Behavior**:
- `QRG_ENABLED=false` → QRG endpoints return 404 or feature disabled error
- `QRG_ENABLED=true` + `QRG_CONSCIOUSNESS_ENABLED=false` → Use static artifacts (no consciousness adaptation)
- `QRG_ENABLED=true` + `QRG_CONSCIOUSNESS_ENABLED=true` → Use real consciousness engine (Phase 2+)

**Acceptance Criteria**:
- [ ] Feature flags documented in README or ENV_VARS.md
- [ ] Flags default to `false` (opt-in, not opt-out)
- [ ] Graceful degradation if flags disabled mid-request
- [ ] Logs emitted when flags are toggled
- [ ] Admin API or script to check current flag values

---

### 4. Unit Tests

**File**: `tests/unit/quantum/test_qrg_adapter.py`

**Test Coverage** (target: ≥90%):
- QRGAdapter protocol compliance
- MockQRGAdapter generate() method
  - Basic generation with minimal context
  - Deterministic QRG ID from seed
  - Different seeds → different QRG IDs
  - Artifact structure validation
  - Symbolic payload determinism
  - Safety gate approval/rejection
  - Provenance block structure
  - Metrics block structure
- MockQRGAdapter validate() method
- MockQRGAdapter health() method
- Edge cases:
  - Empty context
  - Minimal seed length (16 chars)
  - Maximum seed length (256 chars)
  - All options specified

**Tools**:
- pytest
- pytest-asyncio
- pytest-cov (coverage reporting)

**Acceptance Criteria**:
- [ ] ≥90% code coverage for QRGAdapter and MockQRGAdapter
- [ ] All tests pass (no skips, no xfail)
- [ ] Tests run in <5 seconds total
- [ ] Determinism validated (same seed → same output across 10 runs)
- [ ] Coverage report generated (HTML or terminal)

---

### 5. Integration Tests

**File**: `tests/integration/quantum/test_qrg_integration.py`

**Test Scenarios**:
- API endpoint integration (`POST /api/v1/qrg/generate`)
- Feature flag toggling (enable/disable QRG)
- Sandbox endpoint testing (mock adapter only)
- Error handling (400, 403, 500, 504)
- Rate limiting simulation

**Requirements**:
- Spin up test server (FastAPI / Flask test client)
- Use MockQRGAdapter (no production dependencies)
- Test all OpenAPI endpoints from `docs/examples/qrg_openapi_snippet.yaml`

**Acceptance Criteria**:
- [ ] All OpenAPI endpoints tested (generate, health)
- [ ] Feature flags respected (404 when disabled)
- [ ] Error responses match OpenAPI spec (400, 403, 500, 504)
- [ ] Rate limiting enforced (429 after N requests)
- [ ] Integration tests run in <30 seconds total

---

### 6. Canary Test Suite

**File**: `tests/canary/quantum/test_qrg_canary.py`

**Purpose**: Validate MockQRGAdapter determinism for production readiness.

**Test Scenarios**:
- Determinism across 100 seeds
- Consistency across restarts (save artifacts, restart, regenerate, compare)
- Performance benchmarks (p50, p95, p99 latency)
- Concurrency testing (10 concurrent requests, no race conditions)

**Acceptance Criteria**:
- [ ] Determinism validated across 100 unique seeds
- [ ] Consistency validated across 3 restarts
- [ ] Performance benchmarks logged (p50 <50ms, p95 <100ms)
- [ ] Concurrency test passes (no race conditions, no deadlocks)

---

### 7. Developer Documentation

**File**: `docs/developer/qrg_adapter_guide.md`

**Contents**:
- How to use MockQRGAdapter for local development
- How to write tests against QRGAdapter protocol
- Feature flag configuration guide
- Troubleshooting common issues (import errors, determinism failures)
- Transition plan from mock to production adapter (Phase 2)

**Acceptance Criteria**:
- [ ] Step-by-step guide for local development
- [ ] Example code snippets for common use cases
- [ ] Feature flag configuration examples
- [ ] Troubleshooting section with ≥5 common issues
- [ ] Reviewed by Identity Team Lead

---

### 8. Sandbox Endpoints

**Files**: `serve/routes/qrg.py` (or equivalent)

**Endpoints**:
- `POST /api/v1/qrg/generate` → MockQRGAdapter.generate()
- `GET /api/v1/qrg/health` → MockQRGAdapter.health()

**Behavior**:
- Feature flag gated (`QRG_ENABLED` must be true)
- Authentication required (Lambda ID JWT)
- Rate limiting enforced (10 req/min for T4 users)
- CORS enabled for web clients

**Acceptance Criteria**:
- [ ] Endpoints return 404 when `QRG_ENABLED=false`
- [ ] Endpoints require valid JWT (401 if missing/invalid)
- [ ] Rate limiting enforced (429 after limit exceeded)
- [ ] OpenAPI spec matches implementation (contract tests pass)
- [ ] CORS headers present (OPTIONS preflight works)

---

## Acceptance Criteria (Phase 1 → Phase 2 Gate)

**Must complete before Phase 2 starts:**

- [ ] **QRGAdapter protocol** fully documented and tested
- [ ] **MockQRGAdapter** passes all unit tests with deterministic outputs
- [ ] **Feature flags** functional in development environment
- [ ] **Unit tests** achieve ≥90% coverage
- [ ] **Integration tests** pass (API endpoints + feature flags)
- [ ] **Canary tests** validate determinism and concurrency
- [ ] **Developer documentation** reviewed by Identity Team Lead
- [ ] **Sandbox endpoints** deployed to dev environment
- [ ] **No production code depends on mocks** (only tests and sandbox)
- [ ] **CTO sign-off** on adapter design and Phase 2 plan

---

## Non-Goals (Phase 1)

**DO NOT implement in Phase 1:**

- ❌ Real consciousness engine integration
- ❌ Real safety gate integration (Constitutional, Cultural, Cognitive)
- ❌ Real provenance service (SLSA, SBOM, cosign)
- ❌ PQC cryptography (Kyber, Dilithium)
- ❌ KMS key management
- ❌ Production deployment (staging/prod environments)
- ❌ Mesh consensus coordination
- ❌ Quantum RNG integration

**Rationale**: Phase 1 focuses on adapter interface and mock implementation only. Production wiring happens in Phase 2.

---

## Dependencies

**Before Phase 1 starts:**
- [ ] Phase 0 spec approved (QRG_SPEC.md + ADR)
- [ ] Security steward sign-off
- [ ] Safety steward sign-off
- [ ] Consciousness steward sign-off
- [ ] Cryptography reviewer assigned (for Phase 2 guidance)

**During Phase 1:**
- Access to dev environment for sandbox deployment
- pytest + pytest-asyncio + pytest-cov installed
- mypy for type checking
- OpenAPI validator tool (e.g., openapi-spec-validator)

---

## Timeline

**Estimated Duration**: 3-4 weeks

**Week 1**:
- [ ] Implement QRGAdapter protocol interface (`lukhas/quantum/qrg_adapter.py`)
- [ ] Implement MockQRGAdapter (`lukhas/quantum/qrg_mock.py`)
- [ ] Write unit tests (`tests/unit/quantum/test_qrg_adapter.py`)

**Week 2**:
- [ ] Implement feature flags (env vars or config)
- [ ] Write integration tests (`tests/integration/quantum/test_qrg_integration.py`)
- [ ] Implement sandbox endpoints (`serve/routes/qrg.py`)

**Week 3**:
- [ ] Write canary tests (`tests/canary/quantum/test_qrg_canary.py`)
- [ ] Write developer documentation (`docs/developer/qrg_adapter_guide.md`)
- [ ] Deploy sandbox endpoints to dev environment

**Week 4**:
- [ ] Code review (Security + Identity teams)
- [ ] Fix any issues from review
- [ ] CTO sign-off for Phase 2 transition

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Protocol interface unstable** | High | Freeze protocol after week 1; any changes require ADR update |
| **MockQRGAdapter not deterministic** | Medium | Add determinism validation test early (week 1); debug before proceeding |
| **Feature flags not respected** | Medium | Integration tests for flag toggling; manual testing in dev |
| **Unit test coverage <90%** | Low | Use pytest-cov early; refactor to increase coverage as needed |
| **Sandbox endpoints 5xx errors** | Medium | Health checks in integration tests; debug logs for failures |

---

## Exit Criteria Summary

**Phase 1 is complete when:**

1. All deliverables merged to main branch
2. All tests passing (unit + integration + canary)
3. Developer documentation reviewed and approved
4. Sandbox endpoints deployed to dev environment
5. CTO sign-off obtained

**After Phase 1 completion:**

→ Create Phase 2 GitHub issue from `issues/phase2_governance.md` template

---

## Related Issues

- [ ] Phase 0 Spec Approval (prerequisite)
- [ ] Phase 2 Production Implementation (successor)

---

**Owner**: TBD
**Reviewers**: Security Lead, Identity Lead, Platform Lead
**Approver**: CTO (for Phase 1 → Phase 2 transition)

---

**Created**: 2025-11-10
**Last Updated**: 2025-11-10
