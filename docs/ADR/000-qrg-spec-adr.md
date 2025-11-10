# ADR 000: QRG Specification-First Approach

**Status**: Proposed
**Date**: 2025-11-10
**Deciders**: Identity Team, Security Team, Consciousness Team
**Related Spec**: [QRG_SPEC.md](../specs/QRG_SPEC.md)
**Tracking Issue**: #1253

---

## Context

The QRG (Quantum Resonance Glyph) system is a consciousness-aware, quantum-resistant authentication credential system that integrates:
- Post-quantum cryptography (Kyber-1024, Dilithium-5)
- Consciousness engine (emotional state adaptation)
- Cultural safety validation
- Guardian constitutional oversight
- Steganographic identity embedding

During the Lambda ID authentication audit ([PR #1244](https://github.com/LukhasAI/Lukhas/pull/1244)), we discovered that the QRG integration layer uses **mock implementations** for all consciousness-aware components when imports fail:

```python
# core/governance/identity/qrg_integration.py
except ImportError:
    print("⚠️ Core modules not available, using mock implementations")

    class MockModule:
        def __init__(self, name):
            self.name = name

        def __getattr__(self, item):
            return lambda *_args, **_kwargs: {"status": "mock", "module": self.name}
```

This creates a **production readiness gap**: the QRG system exists in `products/security/qrg/` and `core/governance/identity/`, but the wiring to consciousness, cultural safety, and Guardian systems is incomplete.

## Decision

We will adopt a **three-phase, specification-first approach** to QRG implementation:

### Phase 0: Specification (2 weeks) ← **CURRENT PHASE**

**Goal**: Document the complete QRG system before any implementation.

**Deliverables**:
- [x] `QRG_SPEC.md` (comprehensive specification)
- [x] `000-qrg-spec-adr.md` (this ADR)
- [ ] Security team review and approval
- [ ] Consciousness team review and approval
- [ ] Identity team review and approval
- [ ] Merge to main as **documentation-only** change

**Rationale**:
- Prevents "code-first, document-later" technical debt
- Ensures all stakeholders understand the system before building
- Identifies integration points, risks, and open questions early
- Establishes clear acceptance criteria for each phase

**Exit Criteria**:
- All reviewers approve spec (3/3)
- No unresolved critical questions
- Phase 1 implementation plan agreed upon

### Phase 1: Adapter + Mocks (3 weeks)

**Goal**: Build a thin adapter layer with mock implementations for safe development.

**Deliverables**:
- [ ] `lukhas/identity/qrg_adapter.py` (protocol interface)
- [ ] Mock implementations for testing (no real consciousness/Guardian deps)
- [ ] Feature flags: `QRG_ENABLED`, `QRG_CONSCIOUSNESS_ENABLED`
- [ ] Unit tests (100% coverage of adapter interface)
- [ ] Developer documentation for using mocks vs production

**Rationale**:
- Allows parallel development without blocking on consciousness system wiring
- Provides safe testing environment without production dependencies
- Establishes clear contract (protocol) between QRG and rest of system
- Enables integration testing with predictable mock behavior

**Exit Criteria**:
- `QRGAdapter` protocol fully documented and tested
- Mock implementation passes all unit tests
- Feature flags working in development environment
- Documentation reviewed by identity team
- No production code depends on mocks (only tests)

### Phase 2: Production Wiring (4-6 weeks)

**Goal**: Wire real consciousness, cultural safety, and Guardian systems into QRG.

**Deliverables**:
- [ ] Real `ConsciousnessEngine` integration (no mocks)
- [ ] Real `CulturalSafetyChecker` integration
- [ ] Real `ConstitutionalGatekeeper` integration
- [ ] PQC cryptography (Kyber-1024, Dilithium-5)
- [ ] Quantum entropy source integration
- [ ] API endpoints (`/api/v1/identity/qrg/*`)
- [ ] Database schema and migrations
- [ ] Performance benchmarks (<2s generation, <500ms auth)
- [ ] Security audit (external firm)
- [ ] SLSA provenance for PQC dependencies

**Rationale**:
- Production-ready implementation with no shortcuts
- All dependencies properly wired (no import fallbacks)
- Security-first approach (external audit before production)
- Performance validated before deployment

**Exit Criteria**:
- Zero mock implementations in production code paths
- All integration tests passing (no skips)
- Performance benchmarks met (see spec Section 7.1)
- Security audit report with no critical findings
- CISO sign-off

### Phase 3: Production Deployment (2 weeks + monitoring)

**Goal**: Deploy to production with phased consciousness feature rollout.

**Deliverables**:
- [ ] Deploy to staging (1 week bake)
- [ ] Deploy to production with `QRG_ENABLED=true`, `QRG_CONSCIOUSNESS_ENABLED=false`
- [ ] Monitor for 1 week (no P0/P1 incidents)
- [ ] Enable consciousness features: `QRG_CONSCIOUSNESS_ENABLED=true`
- [ ] Phased rollout (10% → 50% → 100% users)
- [ ] Grafana dashboards and alerts
- [ ] Incident response playbook

**Rationale**:
- Gradual rollout reduces blast radius of issues
- Consciousness features gated separately (higher risk)
- Real-world load testing in production
- Rollback plan if issues detected

**Exit Criteria**:
- 1 week production uptime with no P0/P1 incidents
- Latency p95 <2s (generation), <500ms (auth)
- Error rate <0.1%
- Consciousness features stable (if enabled)
- Product team approval for 100% rollout

---

## Consequences

### Positive

1. **Reduced Risk**: Spec-first approach catches issues before implementation
2. **Clear Contracts**: `QRGAdapter` protocol makes dependencies explicit
3. **Parallel Development**: Teams can work on consciousness, Guardian, and QRG simultaneously
4. **Testing Safety**: Mock implementations allow safe testing without production deps
5. **Security First**: External audit before production deployment
6. **Governance Compliance**: Guardian/cultural safety integrated from start (not retrofitted)

### Negative

1. **Slower Initial Delivery**: 2-week spec phase before any code
2. **More Documentation Debt**: Must keep spec in sync with implementation
3. **Review Overhead**: Three teams must review and approve spec
4. **Phased Rollout Complexity**: Requires feature flags, monitoring, and gradual deployment

### Neutral

1. **Three-Phase Timeline**: 9-13 weeks total (2 spec + 3 adapter + 4-6 wiring + 2 deployment)
2. **External Dependency**: Security audit required (budget/scheduling)
3. **Quantum RNG Dependency**: May need vendor selection (ANU vs ID Quantique vs NIST)

---

## Gating Criteria Summary

| Phase Transition | Gate | Approver | Rationale |
|------------------|------|----------|-----------|
| Phase 0 → Phase 1 | Spec approved by 3 teams | Security, Consciousness, Identity Leads | Ensures shared understanding |
| Phase 1 → Phase 2 | Mock tests pass, protocol stable | CTO | Prevents unstable interfaces from blocking wiring |
| Phase 2 → Phase 3 | Security audit clean, perf benchmarks met | CISO | Production-readiness validation |
| Phase 3 (50% rollout) | 1 week uptime, <0.1% errors | Product Lead | Real-world stability before full deployment |

---

## Alternatives Considered

### Alternative 1: Code-First Approach

**Description**: Start implementing QRG wiring immediately without spec.

**Pros**:
- Faster initial progress (no 2-week spec phase)
- Discover integration issues through implementation

**Cons**:
- Higher risk of architectural mistakes
- Harder to coordinate across 3 teams (Consciousness, Identity, Guardian)
- No clear acceptance criteria
- Documentation written after-the-fact (often incomplete)

**Rejected Because**: LUKHAS audit revealed QRG mocks are already in codebase - we don't want to repeat the pattern of "mock now, wire later" without a clear plan.

### Alternative 2: Monolithic Implementation (All-or-Nothing)

**Description**: Build entire QRG system in one PR (spec + adapter + wiring + deployment).

**Pros**:
- No intermediate states
- Single review cycle
- No feature flag complexity

**Cons**:
- Huge PR (impossible to review thoroughly)
- All-or-nothing deployment (high risk)
- Blocks parallel development
- No gradual testing

**Rejected Because**: Violates T4 "small, reviewable changes" principle and increases deployment risk.

### Alternative 3: External Service Approach

**Description**: Build QRG as separate microservice (not integrated with LUKHAS monolith).

**Pros**:
- Independent deployment
- Technology choice flexibility
- Clear service boundary

**Cons**:
- Network latency for consciousness/Guardian calls
- Duplicate authentication logic
- More operational complexity
- Harder to share MATRIZ state

**Rejected Because**: QRG is tightly coupled to consciousness engine and Guardian system - microservice boundary would introduce unnecessary latency and complexity.

---

## Open Questions & Next Steps

### Open Questions

1. **Q**: Should QRG replace WebAuthn/FIDO2 or complement it?
   **A**: Complement initially (Phase 3), evaluate replacement after 6 months of production data.

2. **Q**: What is the budget for external security audit?
   **A**: TBD - need quote from audit firms (estimate: $15K-30K for PQC + consciousness review).

3. **Q**: Which quantum RNG provider should we use?
   **A**: Phase 1 decision - evaluate NIST Randomness Beacon (free) vs ANU (research) vs ID Quantique (enterprise).

4. **Q**: How do we handle consciousness state unavailable (user blocks telemetry)?
   **A**: Graceful degradation to static QRG (see spec Section 12.1).

### Immediate Next Steps (This Week)

1. **Post this ADR + spec as Draft PR** (chore/qrg-spec branch)
   - Labels: `labot`, `qrg`, `security`, `documentation`
   - Reviewers: Security Lead, Consciousness Lead, Identity Lead

2. **Create steward review checklist** (comment on Draft PR)
   - [x] Spec completeness (15 sections)
   - [x] Security requirements documented
   - [x] Phased rollout plan clear
   - [ ] Open questions resolved
   - [ ] Reviewers assigned

3. **Schedule spec review meetings**:
   - Security team (PQC, cryptography)
   - Consciousness team (engine integration)
   - Identity team (authentication flows)

4. **Update tracking issue #1253** with link to spec PR

---

## References

- [QRG Specification](../specs/QRG_SPEC.md)
- [Lambda ID Authentication Audit (PR #1244)](https://github.com/LukhasAI/Lukhas/pull/1244)
- [Issue #1253: QRG Consciousness Wiring](https://github.com/LukhasAI/Lukhas/issues/1253)
- [NIST PQC Standards](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Guardian System Architecture](../architecture/guardian_system.md)

---

## Document History

- 2025-11-10: Initial draft (Phase 0)
