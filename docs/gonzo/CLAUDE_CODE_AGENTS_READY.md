---
status: ready-to-execute
type: claude-code-agent-delegation
owner: agi_dev
created: 2025-11-01
---

# Claude Code Agents - Ready to Execute Tasks

Based on our successful parallel execution (3 agents completed in <3 hours), here are the **best tasks for Claude Code specialized agents**.

---

## ✅ Proven Success Pattern

**What worked brilliantly**:
- **identity-auth-specialist** → #591 WebAuthn types (220 lines + 538 test lines, 30 tests passing)
- **agent-lukhas-specialist** → #614 EncryptionAlgorithm (343 lines + 656 test lines, 48 tests passing)
- **general-purpose (haiku)** → #610 Vague TODO investigation (documentation fix)

**Total**: ~1,800 lines of production code + tests in <3 hours parallel execution ✅

---

## 🎯 High-Priority Tasks for Claude Code Agents

### 1. WebAuthn Credential Implementation (#589, #597, #599) - identity-auth-specialist

**Prerequisites**: ✅ COMPLETE (#591 WebAuthn types done!)
**Estimate**: 6-8 hours (can run in parallel as 3 separate tasks)
**Priority**: P1 - HIGH (authentication critical path)

**Task A: WebAuthn Credential Storage (#589)**
```bash
# Launch identity-auth-specialist agent
Agent: identity-auth-specialist
Model: sonnet
Task: Implement WebAuthn credential storage system

CONTEXT:
- WebAuthn types complete in lukhas_website/lukhas/identity/webauthn_types.py ✅
- Need credential storage, retrieval, and management
- Follow ΛiD identity system patterns

REQUIREMENTS:
1. CREATE lukhas/identity/webauthn_credential.py:
   - WebAuthnCredentialStore class
   - store_credential(user_id, credential) -> None
   - get_credential(credential_id) -> WebAuthnCredential
   - list_credentials(user_id) -> list[WebAuthnCredential]
   - delete_credential(credential_id) -> None
   - Use WebAuthnCredential TypedDict from webauthn_types.py

2. STORAGE:
   - In-memory store for now (dict-based)
   - Thread-safe operations (use threading.Lock)
   - Credential metadata: user_id, credential_id, public_key, counter, created_at

3. CREATE tests/unit/identity/test_webauthn_credential.py:
   - Test store/retrieve/list/delete operations
   - Test thread safety (concurrent access)
   - Test credential not found errors
   - Test duplicate credential handling

ACCEPTANCE CRITERIA:
- WebAuthnCredentialStore implemented with all CRUD operations
- Thread-safe implementation
- 100% test coverage
- All tests passing
- Type hints and mypy compliance

FILES TO CREATE:
- lukhas/identity/webauthn_credential.py
- tests/unit/identity/test_webauthn_credential.py

Closes #589
```

**Task B: Credential Lookup (#597)**
```bash
Agent: identity-auth-specialist
Model: sonnet
Task: Implement WebAuthn credential lookup by user

CONTEXT:
- Builds on #589 credential storage
- Need efficient user-to-credentials mapping
- Support multiple credentials per user

REQUIREMENTS:
1. ENHANCE lukhas/identity/webauthn_credential.py:
   - Add user_id index for fast lookup
   - get_credentials_by_user(user_id) -> list[WebAuthnCredential]
   - get_credential_by_id(user_id, credential_id) -> WebAuthnCredential | None

2. OPTIMIZATION:
   - O(1) lookup by credential_id
   - O(1) lookup by user_id (maintain secondary index)
   - Handle user with no credentials

3. ADD TESTS:
   - Test multi-credential scenarios
   - Test lookup performance
   - Test index consistency

Closes #597
```

**Task C: Assertion Verification (#599)**
```bash
Agent: identity-auth-specialist
Model: sonnet
Task: Implement WebAuthn assertion verification

CONTEXT:
- Complete WebAuthn authentication flow
- Verify signatures using stored public keys
- Implements W3C WebAuthn Level 2 verification

REQUIREMENTS:
1. CREATE lukhas/identity/webauthn_verify.py:
   - verify_assertion(assertion, credential) -> VerifiedAuthentication
   - Check signature validity
   - Verify challenge matches
   - Check counter > stored_counter (prevent replay)
   - Update counter after successful verification

2. USE webauthn_types.py:
   - PublicKeyCredentialAssertion (input)
   - VerifiedAuthentication (output)

3. SECURITY:
   - Constant-time comparison for sensitive data
   - Prevent timing attacks
   - Validate all assertion fields

4. CREATE tests/unit/identity/test_webauthn_verify.py:
   - Test valid assertion verification
   - Test invalid signature rejection
   - Test counter validation
   - Test replay attack prevention

Closes #599
```

---

### 2. Security & Compliance Tasks - agent-lukhas-specialist

**Task D: EncryptionManager (#613)**
**Prerequisites**: ✅ COMPLETE (#614 EncryptionAlgorithm done!)
**Estimate**: 4-5 hours
**Priority**: P1 - HIGH

```bash
Agent: agent-lukhas-specialist
Model: sonnet
Task: Implement centralized EncryptionManager

CONTEXT:
- EncryptionAlgorithm enum complete in core/security/encryption_types.py ✅
- Need unified encryption interface for all LUKHAS components
- Use AEAD (Authenticated Encryption with Associated Data) only

REQUIREMENTS:
1. CREATE core/security/encryption_manager.py:
   - EncryptionManager class
   - encrypt(data: bytes, algorithm: EncryptionAlgorithm) -> EncryptedData
   - decrypt(encrypted: EncryptedData) -> bytes
   - generate_key(algorithm: EncryptionAlgorithm) -> bytes
   - rotate_key(old_key_id: str, new_algorithm: EncryptionAlgorithm) -> None

2. SUPPORT ALGORITHMS (from EncryptionAlgorithm enum):
   - AES_256_GCM (primary)
   - CHACHA20_POLY1305 (alternative)
   - KYBER768, KYBER1024 (post-quantum, future)

3. KEY MANAGEMENT:
   - Generate cryptographically secure keys
   - Support key rotation
   - Never log keys or sensitive data

4. CREATE tests/unit/security/test_encryption_manager.py:
   - Test encrypt/decrypt round-trip for each algorithm
   - Test key generation
   - Test key rotation
   - Test error handling (invalid keys, corrupted data)
   - Test AEAD tag verification

ACCEPTANCE CRITERIA:
- Supports AES-256-GCM and ChaCha20-Poly1305
- Authenticated encryption only (AEAD)
- Key rotation working
- 100% test coverage
- No keys in code or logs
- Mypy compliant

Closes #613
```

---

### 3. Compliance & Privacy - governance-ethics-specialist

**Task E: PrivacyStatement Generator (#601)**
**Estimate**: 3-4 hours
**Priority**: P2 - MEDIUM

```bash
Agent: governance-ethics-specialist
Model: sonnet
Task: Implement PrivacyStatement generator for GDPR/CCPA compliance

CONTEXT:
- Need automatic privacy statement generation
- Support GDPR, CCPA, PIPEDA, LGPD
- Template-based with customization

REQUIREMENTS:
1. CREATE qi/compliance/privacy_statement.py:
   - PrivacyStatementGenerator class
   - generate(jurisdiction: str, data_types: list[str]) -> str
   - Templates for each jurisdiction
   - Support HTML and plain text output

2. JURISDICTIONS:
   - GDPR (EU)
   - CCPA (California)
   - PIPEDA (Canada)
   - LGPD (Brazil)

3. INCLUDE SECTIONS:
   - Data collection notice
   - Purpose of processing
   - Data retention period
   - User rights (access, deletion, portability)
   - Contact information

4. CREATE tests/unit/qi/test_privacy_statement.py:
   - Test statement generation for each jurisdiction
   - Test required sections present
   - Test data type inclusion
   - Test HTML/text output formats

ACCEPTANCE CRITERIA:
- Generates valid privacy statements for 4 jurisdictions
- All required sections included
- Supports HTML and plain text
- Tests verify compliance requirements
- Clear, user-friendly language

Closes #601
```

**Task F: ComplianceReport Generator (#604)**
**Estimate**: 5-6 hours
**Priority**: P2 - MEDIUM

```bash
Agent: governance-ethics-specialist
Model: sonnet
Task: Implement ComplianceReport for multi-jurisdiction audit trails

CONTEXT:
- Track consent, data access, retention across all systems
- Generate compliance reports (JSON/PDF export)
- Integration with Guardian audit trail

REQUIREMENTS:
1. CREATE qi/compliance/compliance_report.py:
   - ComplianceReportGenerator class
   - generate_report(user_id, jurisdiction, date_range) -> ComplianceReport
   - Track: consents, data accesses, retention, deletions
   - Export formats: JSON, PDF

2. INTEGRATE WITH:
   - governance/guardian/ for audit trail
   - qi/privacy/ for consent records
   - identity/ for access logs

3. REPORT SECTIONS:
   - Consent history
   - Data access log
   - Retention compliance
   - Deletion requests
   - Third-party disclosures

4. CREATE tests/unit/qi/test_compliance_report.py:
   - Test report generation
   - Test JSON export
   - Test date range filtering
   - Test multi-jurisdiction scenarios

ACCEPTANCE CRITERIA:
- Generates complete compliance reports
- JSON export working
- Integrates with Guardian audit trail
- Covers all compliance requirements
- Tests verify report completeness

Closes #604
```

---

### 4. Documentation Tasks - general-purpose (haiku)

**Task G: OAuth Library Evaluation (#564)**
**Estimate**: 2-3 hours
**Priority**: P3 - DOCUMENTATION

```bash
Agent: general-purpose
Model: haiku (fast, cost-effective)
Task: Analyze requests-oauthlib vs authlib for OAuth 2.1 migration

CONTEXT:
- Current: requests-oauthlib for OAuth 2.0
- Consider: authlib (more modern, OAuth 2.1 support)
- Need migration decision and plan

REQUIREMENTS:
1. ANALYZE current usage:
   - Search codebase for requests-oauthlib imports
   - Identify OAuth flows used
   - Check for deprecated features

2. COMPARE libraries:
   - OAuth 2.0 / 2.1 support
   - Security features (PKCE, token validation)
   - Maintenance status
   - Type hints / mypy support
   - Performance

3. CREATE docs/decisions/ADR-001-oauth-library-selection.md:
   - Context: current state
   - Decision: stay/migrate/hybrid
   - Rationale: security, maintenance, features
   - Consequences: effort, breaking changes, benefits
   - Implementation plan (if migrating)

ACCEPTANCE CRITERIA:
- Complete analysis of current usage
- Feature comparison table
- Security comparison
- Clear recommendation with rationale
- Migration plan if applicable

Closes #564
```

**Task H: WebAuthn Documentation (#563)**
**Estimate**: 2-3 hours
**Priority**: P3 - DOCUMENTATION

```bash
Agent: general-purpose
Model: haiku
Task: Create comprehensive WebAuthn developer guide

CONTEXT:
- WebAuthn types complete in webauthn_types.py ✅
- Need developer documentation
- Cover registration, authentication, credential management

REQUIREMENTS:
1. CREATE docs/identity/WEBAUTHN_GUIDE.md:
   - Overview
   - Quick Start
   - Registration Flow (backend + frontend)
   - Authentication Flow (backend + frontend)
   - Credential Management
   - API Reference
   - Troubleshooting
   - Security Best Practices

2. CODE EXAMPLES:
   - Python backend examples
   - TypeScript frontend examples
   - Complete working examples

3. REFERENCE:
   - Use actual types from webauthn_types.py
   - Link to W3C WebAuthn spec
   - Browser compatibility notes

ACCEPTANCE CRITERIA:
- Complete developer guide
- Code examples for registration/authentication
- Python and TypeScript examples
- Troubleshooting section
- Security best practices
- Links to W3C spec

Closes #563
```

---

## 🚀 Execution Strategy

### Parallel Execution (Maximum Speed)

**Launch 3 agents in parallel** (proven to work!):

```bash
# Terminal 1: Identity specialist
claude code agent identity-auth-specialist --task "WebAuthn Credential Storage #589"

# Terminal 2: Security specialist
claude code agent agent-lukhas-specialist --task "EncryptionManager #613"

# Terminal 3: Documentation specialist
claude code agent general-purpose --model haiku --task "OAuth Library Evaluation #564"
```

**Estimated Total Time**: 4-6 hours (all 3 tasks complete in parallel)

---

### Sequential Execution (For Dependencies)

**Phase 1** (No dependencies):
1. #589 (WebAuthn Credential) + #613 (EncryptionManager) + #564 (OAuth Eval) - **Parallel**

**Phase 2** (Depends on Phase 1):
2. #597 (Credential Lookup, needs #589) + #601 (PrivacyStatement) + #563 (WebAuthn Docs) - **Parallel**

**Phase 3** (Depends on Phase 2):
3. #599 (Assertion Verify, needs #597) + #604 (ComplianceReport) - **Parallel**

**Total Estimated Time**: 12-15 hours across 3 phases (4-5 hours per phase in parallel)

---

## 📊 Expected Results

**After Parallel Execution (3 agents)**:
- 3 issues closed
- ~1,500-2,000 lines of code + tests
- 100% test pass rate (based on previous success)
- Type-safe, production-ready implementations

**After All 8 Tasks**:
- 8 issues closed
- 29 → 21 open issues (28% reduction)
- Complete WebAuthn authentication system
- Centralized encryption management
- Compliance reporting infrastructure
- Comprehensive documentation

---

## ✅ Quality Checklist (For Each Task)

After each agent completes:
- [ ] All files created as specified
- [ ] Tests written and passing (100% for new code)
- [ ] Type hints added (mypy compliant)
- [ ] Code follows existing patterns
- [ ] Documentation clear and complete
- [ ] No hardcoded secrets or keys
- [ ] Security review for security-related tasks

---

## 🎯 Success Metrics

**Based on previous execution**:
- ✅ 100% test pass rate
- ✅ W3C/RFC spec compliance
- ✅ Type-safe implementations
- ✅ Comprehensive test coverage
- ✅ Production-ready code quality

**Target for this batch**:
- Close 8 issues (29 → 21 open)
- Add ~4,000 lines of production code + tests
- Complete WebAuthn authentication
- Complete encryption infrastructure
- Complete compliance reporting

---

**Ready to launch! Start with any task above using Claude Code agents.** 🚀
