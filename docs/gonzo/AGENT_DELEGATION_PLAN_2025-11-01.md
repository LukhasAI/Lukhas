---
status: active
type: delegation-plan
owner: claude
updated: 2025-11-01
---

# Multi-Agent Delegation Plan (2025-11-01)

Based on the comprehensive GitHub issues audit, here are **ready-to-delegate** tasks for specialized agents. All tasks are well-scoped, have clear acceptance criteria, and can be executed in parallel.

---

## 🔐 Identity & Authentication Specialist Agent

**Issues to Tackle**: #552, #584, #581, #591 (P0/P1 Security)

### Task 1: Implement Core Authentication System (#552)
**Location**: `.semgrep/lukhas-security.yaml:547`
**Priority**: P0 - CRITICAL
**Scope**: Security-critical authentication foundation

**Context**:
- Read [core/ports/openai_provider.py](../core/ports/openai_provider.py) for Protocol pattern
- Read [tests/unit/core/test_openai_provider_protocol.py](../tests/unit/core/test_openai_provider_protocol.py) for examples
- Existing ΛiD system in `lukhas/identity/`

**Deliverables**:
1. Create `core/ports/auth_provider.py` with Protocol-based AuthProvider interface
2. Implement `AuthProvider` with methods:
   - `authenticate(credentials: dict) -> AuthResult`
   - `verify_token(token: str) -> TokenPayload`
   - `refresh_token(refresh_token: str) -> AuthResult`
3. Create tests in `tests/unit/core/test_auth_provider.py`
4. Update `.semgrep/lukhas-security.yaml:547` to remove TODO

**Acceptance Criteria**:
- [ ] Protocol-based design (structural typing, not inheritance)
- [ ] Mock implementation for testing
- [ ] 100% test coverage for Protocol contract
- [ ] No hardcoded secrets

**Time Estimate**: 2-3 hours

---

### Task 2: Implement Admin Authentication (#584)
**Location**: `lukhas_website/lukhas/api/routing_admin.py:103`
**Priority**: P1 - HIGH
**Dependency**: #552 (AuthProvider)

**Context**:
- Admin routes currently have TODO for authentication
- Need role-based access control (RBAC)
- Must integrate with ΛiD system

**Deliverables**:
1. Create `lukhas/api/middleware/admin_auth.py`
2. Implement admin authentication decorator/middleware
3. Add role verification (admin, superadmin roles)
4. Update `routing_admin.py:103` to use middleware
5. Add integration tests in `tests/integration/api/test_admin_auth.py`

**Acceptance Criteria**:
- [ ] Only authenticated admins can access admin routes
- [ ] Role-based access control working
- [ ] Failed auth returns 401/403 appropriately
- [ ] Integration tests verify auth flow

**Time Estimate**: 3-4 hours

---

### Task 3: Implement WebAuthn Challenge/Verify (#581)
**Location**: `lukhas_website/components/qrg-envelope.tsx:23`
**Priority**: P1 - HIGH
**Dependency**: #591 (WebAuthn types)

**Context**:
- Frontend component needs real WebAuthn challenge
- Currently using placeholder authentication
- py_webauthn library likely available

**Deliverables**:
1. Create `lukhas/identity/webauthn_challenge.py`
2. Implement challenge generation endpoint
3. Implement verification endpoint
4. Update TypeScript component to use real challenge
5. Add E2E tests for WebAuthn flow

**Acceptance Criteria**:
- [ ] Challenge generated with proper cryptographic randomness
- [ ] Verification validates signature correctly
- [ ] Works with standard WebAuthn-compatible devices
- [ ] E2E test covers full registration + authentication flow

**Time Estimate**: 4-5 hours

---

### Task 4: Define WebAuthn Types (#591)
**Location**: `lukhas_website/lukhas/identity/webauthn_production.py:72`
**Priority**: P1 - PREREQUISITE for #581, #589, #597, #599

**Context**:
- Missing `webauthn.helpers.structs.PublicKeyCredential` types
- Consolidates 4 duplicate issues (#591-594)

**Deliverables**:
1. Create `lukhas/identity/webauthn_types.py` with TypedDict definitions:
   - `PublicKeyCredential`
   - `AuthenticatorAttestationResponse`
   - `AuthenticatorAssertionResponse`
   - `CredentialCreationOptions`
   - `CredentialRequestOptions`
2. Update `webauthn_production.py:72` to import types
3. Add type validation tests

**Acceptance Criteria**:
- [ ] All WebAuthn types properly defined with TypedDict
- [ ] Matches W3C WebAuthn spec structure
- [ ] Type checking passes with mypy/pyright
- [ ] Can parse real WebAuthn responses

**Time Estimate**: 2 hours

---

## 🛡️ Security Infrastructure Specialist Agent

**Issues to Tackle**: #613, #614, #619 (P2 Security Infrastructure)

### Task 5: Implement EncryptionManager (#613)
**Location**: `security/tests/test_security_suite.py:299`
**Priority**: P2
**Scope**: Centralized encryption management

**Context**:
- Consolidates 4 duplicate issues (#613, #615-617)
- Need consistent encryption interface across system
- Should support multiple algorithms

**Deliverables**:
1. Create `core/security/encryption_manager.py`:
   - `EncryptionManager` class with methods:
     - `encrypt(data: bytes, algorithm: EncryptionAlgorithm) -> bytes`
     - `decrypt(encrypted: bytes, algorithm: EncryptionAlgorithm) -> bytes`
     - `generate_key(algorithm: EncryptionAlgorithm) -> bytes`
2. Create `core/security/encryption_types.py` with `EncryptionAlgorithm` enum
3. Support AES-256-GCM, ChaCha20-Poly1305 (minimum)
4. Key rotation support
5. Tests in `tests/unit/security/test_encryption_manager.py`

**Acceptance Criteria**:
- [ ] Multiple encryption algorithms supported
- [ ] Key management (generation, storage, rotation)
- [ ] Authenticated encryption (AEAD) only
- [ ] 100% test coverage including error cases
- [ ] No keys in code/logs

**Time Estimate**: 4-5 hours

---

### Task 6: Define EncryptionAlgorithm Enum (#614)
**Location**: `security/tests/test_security_suite.py:299` (related)
**Priority**: P2 - PREREQUISITE for #613
**Scope**: Type-safe algorithm selection

**Deliverables**:
1. Create `core/security/encryption_types.py`:
   ```python
   from enum import Enum

   class EncryptionAlgorithm(Enum):
       AES_256_GCM = "aes-256-gcm"
       CHACHA20_POLY1305 = "chacha20-poly1305"
       # Post-quantum ready
       KYBER768 = "kyber768"  # Future
   ```
2. Add algorithm metadata (key size, nonce size, tag size)
3. Type hints for all crypto operations

**Acceptance Criteria**:
- [ ] Enum covers current and planned algorithms
- [ ] Type-safe selection prevents string typos
- [ ] Metadata available for each algorithm

**Time Estimate**: 1 hour

---

### Task 7: Implement SecurityMonitor (#619)
**Location**: TBD (new component)
**Priority**: P2
**Scope**: Runtime security monitoring

**Deliverables**:
1. Create `core/security/security_monitor.py`:
   - Real-time security event monitoring
   - Integration with observability/ metrics
   - Alert on anomalies (failed auth, rate limits, etc.)
2. Hook into authentication flow
3. Dashboard integration (Prometheus metrics)
4. Tests in `tests/unit/security/test_security_monitor.py`

**Acceptance Criteria**:
- [ ] Monitors auth failures, rate limit violations
- [ ] Exports Prometheus metrics
- [ ] Configurable alert thresholds
- [ ] Low performance overhead (<5ms p95)

**Time Estimate**: 3-4 hours

---

## 🔒 QI Privacy & Compliance Specialist Agent

**Issues to Tackle**: #601, #604, #605, #607, #600 (P2 Compliance)

### Task 8: Implement PrivacyStatement (#601)
**Location**: `qi/privacy/zero_knowledge_system.py:55`
**Priority**: P2
**Scope**: Privacy compliance metadata

**Context**:
- Consolidates 2 duplicate issues (#601, #602)
- QI system needs privacy statements for zero-knowledge proofs

**Deliverables**:
1. Create `qi/privacy/privacy_statement.py`:
   ```python
   @dataclass
   class PrivacyStatement:
       purpose: str
       data_types: list[str]
       retention_period: timedelta
       jurisdictions: list[str]
       consent_required: bool
       zk_compatible: bool
   ```
2. Update `zero_knowledge_system.py:55` to use PrivacyStatement
3. Add validation logic
4. Tests in `tests/unit/qi/test_privacy_statement.py`

**Acceptance Criteria**:
- [ ] PrivacyStatement dataclass with all required fields
- [ ] Validation ensures GDPR/CCPA compliance
- [ ] Integration with zero-knowledge system
- [ ] JSON serialization support

**Time Estimate**: 2-3 hours

---

### Task 9: Implement ComplianceReport (#604)
**Location**: TBD (new component in qi/)
**Priority**: P2
**Scope**: Compliance reporting infrastructure

**Deliverables**:
1. Create `qi/compliance/compliance_report.py`:
   - Generate compliance reports (GDPR, CCPA, HIPAA)
   - Track consent, data access, retention
   - Export to JSON/PDF
2. Integration with Guardian system
3. Tests in `tests/unit/qi/test_compliance_report.py`

**Acceptance Criteria**:
- [ ] Generates multi-jurisdiction compliance reports
- [ ] Tracks all required metadata
- [ ] Exportable to standard formats
- [ ] Audit trail preserved

**Time Estimate**: 4-5 hours

---

### Task 10: Implement SecurityMesh (#605)
**Location**: TBD (new component in qi/)
**Priority**: P2
**Scope**: Multi-layer security coordination

**Deliverables**:
1. Create `qi/security/security_mesh.py`:
   - Coordinate security across multiple layers
   - Policy enforcement mesh
   - Distributed trust verification
2. Integration with Guardian and QI systems
3. Tests in `tests/unit/qi/test_security_mesh.py`

**Acceptance Criteria**:
- [ ] Multi-layer security coordination working
- [ ] Policy enforcement mesh operational
- [ ] Integration with existing security systems
- [ ] Performance: <10ms overhead per request

**Time Estimate**: 5-6 hours

---

### Task 11: Implement MultiJurisdictionComplianceEngine (#607)
**Location**: TBD (new component in qi/)
**Priority**: P2
**Scope**: Cross-jurisdiction compliance handling

**Deliverables**:
1. Create `qi/compliance/multi_jurisdiction_engine.py`:
   - Handle GDPR, CCPA, PIPEDA, LGPD simultaneously
   - Automatic jurisdiction detection
   - Most-restrictive policy application
2. Rule engine for compliance policies
3. Tests covering all major jurisdictions

**Acceptance Criteria**:
- [ ] Supports 4+ major jurisdictions (GDPR, CCPA, PIPEDA, LGPD)
- [ ] Automatic jurisdiction detection from user data
- [ ] Applies most restrictive applicable rules
- [ ] Configurable policy overrides

**Time Estimate**: 6-8 hours

---

### Task 12: Implement Token Store Validation (#600)
**Location**: TBD (likely in `lukhas/identity/`)
**Priority**: P2
**Scope**: Token storage and validation

**Context**:
- Consolidates 2 issues (#600, #558)
- Need persistent token storage with validation

**Deliverables**:
1. Create `lukhas/identity/token_store.py`:
   - Token persistence (Redis or SQLite)
   - Validation against stored tokens
   - Token revocation support
   - Expiration handling
2. Integration with AuthProvider
3. Tests in `tests/unit/identity/test_token_store.py`

**Acceptance Criteria**:
- [ ] Persistent token storage (Redis preferred)
- [ ] Token validation working
- [ ] Revocation support
- [ ] Automatic expiration cleanup

**Time Estimate**: 3-4 hours

---

## 🔍 Investigation & Cleanup Specialist

**Issues to Tackle**: #610 (Investigation required)

### Task 13: Investigate and Resolve Vague TODO (#610)
**Location**: `scripts/todo_migration/generate_todo_inventory.py:8`
**Priority**: P3
**Scope**: Code cleanup

**Context**:
- TODO just says "message" - unclear intent
- May be a leftover from debugging

**Deliverables**:
1. Read `scripts/todo_migration/generate_todo_inventory.py` line 8 context
2. Determine if TODO is still relevant
3. Either:
   - Implement proper message if needed
   - Remove TODO if obsolete
   - Add clarifying comment if deferred
4. Close issue with explanation

**Acceptance Criteria**:
- [ ] TODO resolved (implemented, removed, or clarified)
- [ ] Code context understood and documented
- [ ] Issue closed with clear explanation

**Time Estimate**: 30 minutes

---

## 📚 Documentation Specialist

**Issues to Tackle**: #563, #564, #557 (Documentation)

### Task 14: Document WebAuthn Challenge/Verify (#563)
**Location**: TBD (docs/)
**Priority**: P3
**Scope**: Developer documentation

**Deliverables**:
1. Create `docs/identity/WEBAUTHN_GUIDE.md`:
   - How WebAuthn works in LUKHAS
   - Registration flow
   - Authentication flow
   - Troubleshooting common issues
2. Add code examples
3. API reference for endpoints

**Acceptance Criteria**:
- [ ] Complete WebAuthn developer guide
- [ ] Code examples for registration + auth
- [ ] Troubleshooting section
- [ ] Links to W3C spec

**Time Estimate**: 2-3 hours

---

### Task 15: Evaluate OAuth Library Strategy (#564)
**Location**: Multiple files using `requests_oauthlib`
**Priority**: P3
**Scope**: Technical decision documentation

**Context**:
- Currently using `requests_oauthlib`
- Consider migration to `authlib` (more modern, better maintained)

**Deliverables**:
1. Create `docs/decisions/ADR-001-oauth-library-selection.md`:
   - Compare requests_oauthlib vs authlib
   - Migration effort estimate
   - Security comparison
   - Recommendation with rationale
2. Update dependencies if migration recommended
3. Create migration plan if needed

**Acceptance Criteria**:
- [ ] ADR document with clear recommendation
- [ ] Comparison table (features, security, maintenance)
- [ ] Migration plan if changing libraries
- [ ] Decision documented for future reference

**Time Estimate**: 2-3 hours

---

### Task 16: Add Governance Example (#557)
**Location**: TBD (docs/governance/)
**Priority**: P3
**Scope**: Documentation + example code

**Deliverables**:
1. Create `docs/governance/GUARDIAN_EXAMPLE.md`
2. Add working code example in `examples/governance/`
3. Cover basic governance scenario (consent, policy enforcement)

**Acceptance Criteria**:
- [ ] Complete governance example with explanation
- [ ] Working code that runs
- [ ] Covers key Guardian features
- [ ] Includes test coverage

**Time Estimate**: 2-3 hours

---

## ⚗️ Labs Research Specialist

**Issues to Tackle**: #574 (Experimental/Research)

### Task 17: Consciousness Token Mapping (#574)
**Location**: TBD (candidate/consciousness/)
**Priority**: P3 - RESEARCH
**Scope**: Experimental consciousness features

**Context**:
- Implement consciousness token mapping with emotional state
- Research/experimental feature for candidate lane only
- NOT for production use

**Deliverables**:
1. Create `candidate/consciousness/token_mapper.py`:
   - Map consciousness states to token representations
   - Emotional state encoding
   - Integration with existing consciousness framework
2. Research documentation in `docs/research/`
3. Prototype tests

**Acceptance Criteria**:
- [ ] Consciousness states map to tokens
- [ ] Emotional dimensions encoded
- [ ] Stays in candidate/ lane (NOT production)
- [ ] Research documentation complete

**Time Estimate**: 4-6 hours (exploratory)

---

## 🚀 Recommended Parallel Execution Plan

### Phase 1 (Week 1) - Security Foundation
Run in parallel:
1. **Identity Agent**: Task 4 (#591 WebAuthn types) → PREREQUISITE
2. **Security Agent**: Task 6 (#614 EncryptionAlgorithm) → PREREQUISITE
3. **Investigation Agent**: Task 13 (#610 Investigate vague TODO)

### Phase 2 (Week 1-2) - Core Implementation
After Phase 1 prerequisites complete:
1. **Identity Agent**: Tasks 1, 2, 3 (#552, #584, #581) - Auth system
2. **Security Agent**: Tasks 5, 7 (#613, #619) - Encryption + Monitoring
3. **QI Agent**: Task 8 (#601 PrivacyStatement)

### Phase 3 (Week 2-3) - Compliance & Documentation
1. **QI Agent**: Tasks 9, 10, 11, 12 (#604, #605, #607, #600)
2. **Documentation Agent**: Tasks 14, 15, 16 (#563, #564, #557)
3. **Labs Agent**: Task 17 (#574) - Research parallel track

---

## Agent Coordination Commands

### Delegate to Identity Agent
```bash
# Tag issue for identity agent
gh issue comment 552 --body "@identity-agent Please implement core authentication system using Protocol pattern. See Task 1 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md for full specification."

gh issue comment 584 --body "@identity-agent Please implement admin authentication. Depends on #552. See Task 2 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 581 --body "@identity-agent Please implement WebAuthn challenge/verify. Depends on #591. See Task 3 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 591 --body "@identity-agent Please define WebAuthn types (PREREQUISITE). See Task 4 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"
```

### Delegate to Security Agent
```bash
gh issue comment 613 --body "@security-agent Please implement EncryptionManager. See Task 5 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 614 --body "@security-agent Please define EncryptionAlgorithm enum (PREREQUISITE). See Task 6 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 619 --body "@security-agent Please implement SecurityMonitor. See Task 7 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"
```

### Delegate to QI/Compliance Agent
```bash
gh issue comment 601 --body "@compliance-agent Please implement PrivacyStatement. See Task 8 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 604 --body "@compliance-agent Please implement ComplianceReport. See Task 9 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 605 --body "@compliance-agent Please implement SecurityMesh. See Task 10 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 607 --body "@compliance-agent Please implement MultiJurisdictionComplianceEngine. See Task 11 in docs/gongo/AGENT_DELEGATION_PLAN_2025-11-01.md"

gh issue comment 600 --body "@compliance-agent Please implement token store validation. See Task 12 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md"
```

---

## Success Metrics

- **Week 1**: 7 issues resolved (prerequisites + quick wins)
- **Week 2**: 8 issues resolved (core implementations)
- **Week 3**: 7 issues resolved (compliance + docs)
- **Total**: 22/37 issues resolved (59% of Claude issues)

Combined with @codex work on 12 automation issues, target: **<10 open issues by end of month**.

---

## Notes

- All tasks follow T4 standards (conservative, tested, documented, reversible)
- Each task has clear acceptance criteria and time estimates
- Dependencies explicitly mapped (e.g., #591 before #581)
- Phase 1 prerequisites must complete before Phase 2
- Agents can work in parallel within each phase
- All implementations require tests (unit + integration where applicable)
- Security tasks require security review before merge
