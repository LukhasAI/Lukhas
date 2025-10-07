---
status: wip
type: documentation
owner: unknown
module: planning
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Phase 3: First Real Promotions Plan

## Overview
This document outlines the plan for the first real module promotions from candidate to accepted, following the 6-point acceptance criteria established in our reality check.

## Acceptance Criteria (All Must Pass)
1. ✅ Lane: Module physically in lukhas/ directory
2. ✅ No banned imports (verified by AST gate)
3. ⚠️ MATRIZ instrumentation at public APIs
4. ⚠️ Tests passing in CI (beyond dry-run)
5. ❌ P95 latency meets SLA on reference machine
6. ✅ Dry-run default + consent gates

## Promotion Order & Rationale

### 1. Observability (MATRIZ utilities) - Week 1
**Why First**: Already in accepted, lowest risk, enables monitoring for other promotions

**Tasks**:
- [ ] Add MATRIZ decorators to 2-3 more endpoints
- [ ] Create unit tests for MATRIZ emissions
- [ ] Verify event format and routing
- [ ] Document MATRIZ event schema

**Success Criteria**:
- All public APIs emit MATRIZ events
- Events contain required metadata (operation, timestamp, duration)
- Tests verify event emission
- No performance degradation

**Files to Update**:
- `lukhas/observability/matriz_decorators.py` - Add more decorator variants
- `tests/test_matriz_observability.py` - Create comprehensive tests

---

### 2. Governance/Consent Ledger - Week 2
**Why Second**: Critical for compliance, relatively isolated, clear interfaces

**Tasks**:
- [ ] Create candidate implementation registration file
- [ ] Wire consent ledger implementation to registry
- [ ] Add feature flag FEATURE_GOVERNANCE_LEDGER
- [ ] Create integration tests (happy path + sad path)
- [ ] Verify audit trail generation
- [ ] Test GDPR/CCPA compliance flows

**Implementation Plan**:
```python
# candidate/governance/consent_ledger_impl.py
from lukhas.governance.consent_ledger import register_consent_engine

class ConsentLedgerImpl:
    def record_consent(self, consent_data):
        # Real implementation
        return {"ok": True, "id": "consent_123"}

    def verify_consent(self, subject, scope):
        # Real verification
        return {"valid": True}

# Register when feature flag enabled
if os.getenv("FEATURE_GOVERNANCE_LEDGER") == "true":
    register_consent_engine(ConsentLedgerImpl())
```

**Success Criteria**:
- Consent recording works with feature flag enabled
- Audit trail properly generated
- MATRIZ events include consent metadata
- Tests verify consent persistence
- P95 latency < 50ms

---

### 3. Identity/Passkey Verify - Week 3
**Why Third**: User-facing, clear value proposition, builds on consent ledger

**Tasks**:
- [ ] Implement WebAuthn passkey verification
- [ ] Create identity registry and wire implementation
- [ ] Add feature flag FEATURE_IDENTITY_PASSKEY
- [ ] Create authentication flow tests
- [ ] Ensure no PII is logged or persisted inappropriately
- [ ] Test with multiple authenticator types

**Implementation Plan**:
```python
# candidate/identity/passkey_impl.py
from lukhas.identity.lambda_id import register_authenticator

class PasskeyAuthenticator:
    def verify_passkey(self, request):
        # WebAuthn verification
        return {"verified": True, "user_id": "hashed_id"}

if os.getenv("FEATURE_IDENTITY_PASSKEY") == "true":
    register_authenticator("passkey", PasskeyAuthenticator())
```

**Success Criteria**:
- Passkey verification works end-to-end
- No PII in logs or non-encrypted storage
- Authentication latency < 100ms p95
- Support for platform authenticators
- Fallback to password works

---

### 4. Orchestration/Context Handoff - Week 4
**Why Fourth**: Most complex, depends on other modules, highest risk

**Tasks**:
- [ ] Implement context bus with measured handoff
- [ ] Create pipeline manager for workflows
- [ ] Add backpressure simulation and testing
- [ ] Wire orchestration implementation to registry
- [ ] Create performance benchmarks
- [ ] Test multi-model orchestration

**Implementation Plan**:
```python
# candidate/orchestration/context_impl.py
from lukhas.orchestration.context_bus import register_context_handler

class ContextBusImpl:
    async def handoff(self, context, target):
        # Measure and execute handoff
        start = time.time()
        result = await self._execute_handoff(context, target)
        duration = (time.time() - start) * 1000

        if duration > 250:  # SLA breach
            logger.warning(f"Handoff exceeded 250ms: {duration}ms")

        return result

if os.getenv("FEATURE_ORCHESTRATION_HANDOFF") == "true":
    register_context_handler(ContextBusImpl())
```

**Success Criteria**:
- Context handoff p95 < 250ms
- Backpressure properly handled
- No context loss between handoffs
- Pipeline workflows execute correctly
- Monitoring shows handoff metrics

---

## Testing Strategy

### For Each Promotion:
1. **Unit Tests**: Test component in isolation
2. **Integration Tests**: Test with other accepted modules
3. **Performance Tests**: Measure p95 latency
4. **Safety Tests**: Verify dry-run mode works
5. **Feature Flag Tests**: Verify on/off behavior

### Test Template:
```python
@pytest.mark.integration
def test_module_with_feature_flag():
    # Test with flag disabled (dry-run)
    os.environ["FEATURE_X"] = "false"
    result = module.operation()
    assert result["mode"] == "dry_run"

    # Test with flag enabled (real)
    os.environ["FEATURE_X"] = "true"
    result = module.operation()
    assert result["ok"] == True
    assert "dry_run" not in result
```

---

## Rollback Plan

If any promotion causes issues:

1. **Immediate**: Set feature flag to false
2. **Quick**: Revert registry registration
3. **Full**: Move module back to candidate/

```bash
# Emergency rollback
export FEATURE_GOVERNANCE_LEDGER=false
export FEATURE_IDENTITY_PASSKEY=false
export FEATURE_ORCHESTRATION_HANDOFF=false
```

---

## Success Metrics

### Per Module:
- ✅ All 6 acceptance criteria met
- ✅ Zero acceptance gate violations
- ✅ P95 latency within SLA
- ✅ Feature flag controls work
- ✅ Tests passing (unit + integration)

### Overall:
- System stability maintained
- No performance degradation
- Clean rollback capability
- Documentation updated

---

## Timeline

**Week 1**: Observability enhancement
**Week 2**: Governance/Consent Ledger
**Week 3**: Identity/Passkey
**Week 4**: Orchestration/Context
**Week 5**: Integration testing & optimization
**Week 6**: Documentation & handoff

---

## Next Steps

1. Create candidate implementation files
2. Add registry functions to accepted modules
3. Write comprehensive tests
4. Set up performance monitoring
5. Document each promotion

This plan ensures we move from "interfaces only" to "real implementations" in a controlled, measurable way that would meet the standards of Sam Altman (scale), Dario Amodei (safety), and Demis Hassabis (rigor).
