---
status: wip
type: documentation
owner: unknown
module: planning
redirect: false
moved_to: null
---

# LUKHAS Capability Promotion Plan

## Current State
- **Accepted (lukhas/)**: Minimal interfaces-only nucleus with MATRIZ instrumentation
- **Candidate (candidate/)**: 2,171+ files awaiting promotion by capability slice

## First Wave Promotions

### 1. Consent Ledger Implementation ✅
**Files to promote:**
- `candidate/governance/consent_ledger/ledger_v1.py` → `lukhas/governance/consent_ledger_impl.py`

**Integration steps:**
1. Wire implementation behind the dry_run interface in `lukhas/governance/consent_ledger.py`
2. Add feature flag: `CONSENT_LEDGER_ACTIVE=true`
3. Add MATRIZ instrumentation to key methods
4. Create tests: `tests/test_consent_ledger_integration.py`

**Success criteria:**
- Consent recording working in non-dry_run mode
- MATRIZ AWARENESS nodes emitted with proper provenance
- <40ms p95 latency maintained
- GDPR Article 7 compliance verified

### 2. WebAuthn/Passkey Authentication 🔐
**Files to promote:**
- `candidate/governance/identity/core/auth/webauthn_manager.py` → `lukhas/identity/webauthn.py`

**Integration steps:**
1. Add `verify_passkey()` method to `lukhas/identity/lambda_id.py`
2. Import WebAuthnManager conditionally
3. Add MATRIZ instrumentation: `@instrument("DECISION", label="auth:passkey")`
4. Create tests: `tests/test_webauthn_integration.py`

**Success criteria:**
- Passkey registration and verification working
- FIDO2 compliance maintained
- <100ms p95 latency for verification
- Tier-based authentication levels supported

### 3. Context Bus Handoff 🚌
**Files to promote:**
- `candidate/orchestration/core/handoff_manager.py` → `lukhas/orchestration/handoff.py`

**Integration steps:**
1. Add `handoff()` method to `lukhas/orchestration/context_bus.py`
2. Implement context passing to policy layer
3. Add MATRIZ instrumentation: `@instrument("CONTEXT", label="orchestration:handoff")`
4. Create tests: `tests/test_context_handoff.py`

**Success criteria:**
- Context successfully passed between modules
- Policy hints preserved in handoff
- <50ms p95 latency maintained
- Trace ID propagated correctly

## Promotion Process (Per Slice)

1. **Create feature branch**: `git checkout -b promote/[capability-name]`
2. **Copy implementation**: Move from candidate/ to lukhas/
3. **Add MATRIZ instrumentation**: Decorate key functions
4. **Update MODULE_MANIFEST.json**: Add new capabilities
5. **Write integration tests**: Verify boundary behavior
6. **Run acceptance gate**: `python tools/acceptance_gate.py`
7. **Create PR**: With test results and MATRIZ validation
8. **Merge after CI passes**

## Next Wave Candidates (After First Three)

### Wave 2: Core Services
- GLYPH engine (`candidate/core/glyph/`)
- Symbolic router (`candidate/core/symbolic/`)
- Actor system (`candidate/core/actor_system.py`)

### Wave 3: Memory Systems
- Fold manager (`candidate/memory/folds/`)
- Causal chains (`candidate/memory/causal/`)
- Memory consolidation (`candidate/memory/consolidation/`)

### Wave 4: Consciousness
- Awareness engine (`candidate/consciousness/awareness/`)
- Dream states (`candidate/consciousness/dream/`)
- Creativity engine (`candidate/consciousness/creativity/`)

### Wave 5: Advanced Processing
- Quantum-inspired algorithms (`candidate/qi/`)
- Bio-inspired adaptation (`candidate/bio/`)
- Emotion VAD system (`candidate/emotion/`)

## Validation Checklist

Before each promotion:
- [ ] No imports from candidate/quarantine/archive
- [ ] MODULE_MANIFEST.json present and valid
- [ ] MATRIZ instrumentation added
- [ ] Tests cover happy and sad paths
- [ ] Performance targets met (SLA in manifest)
- [ ] Constellation Framework compliance verified
- [ ] No vendor SDKs in accepted lane
- [ ] Feature flags for gradual rollout

## Monitoring

After promotion:
- Check MATRIZ node emission
- Monitor performance metrics
- Verify no import errors
- Track feature flag usage
- Review Guardian System drift scores

## Rollback Plan

If issues arise:
1. Disable feature flag immediately
2. Revert to dry_run mode
3. Move file back to candidate/
4. Fix issues and re-test
5. Re-attempt promotion

---

Generated: 2025-08-22
Status: Ready for first wave promotions
