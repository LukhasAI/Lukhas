---
status: active
type: agent-setup
owner: claude
platform: google-jules
updated: 2025-11-01
---

# Agent Jules Setup & Execution Guide

Complete setup instructions for Google's Jules AI coding agent with precise prompts for 7 ready tasks.

**Reference**: https://developers.google.com/jules/api

---

## 🔐 Step 1: Secure API Key Storage

### Option A: Local .env File (Recommended for Development)

```bash
# In repo root
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create .env.local (gitignored)
cat > .env.local <<EOF
# Google Jules API Key
JULES_API_KEY=your_api_key_here

# Optional: Jules Configuration
JULES_MODEL=gemini-2.0-flash-thinking-exp-1219  # Default model
JULES_TEMPERATURE=0.7
JULES_MAX_TOKENS=8192
EOF

# Secure the file
chmod 600 .env.local

# Verify it's gitignored
git check-ignore .env.local  # Should output: .env.local
```

### Option B: Environment Variable (Recommended for Production)

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export JULES_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $JULES_API_KEY  # Should show your key
```

### Option C: macOS Keychain (Most Secure)

```bash
# Store in keychain
security add-generic-password \
  -a "$USER" \
  -s "jules-api-key" \
  -w "your_api_key_here"

# Retrieve when needed
export JULES_API_KEY=$(security find-generic-password \
  -a "$USER" \
  -s "jules-api-key" \
  -w)
```

---

## 📋 Step 2: Check Open PRs (Codex Already Working!)

Codex has already created **8 PRs** - all MERGEABLE:

```bash
gh pr list --state open
```

**Active PRs**:
- #794: SecurityMonitor (issue #619) ✅
- #793: MultiJurisdictionComplianceEngine (issue #607) ✅
- #792: Security posture overlays
- #791: PQC liboqs in CI (issue #492) ✅
- #790: Reliability lint cleanup
- #789: E402/E70x adapters (issue #388) ✅
- #788: Dilithium2 checkpoint (issue #490) ✅
- #787: pip CVE fix (issue #399) ✅

**Action**: Review and merge these PRs first before Jules starts new work to avoid conflicts.

---

## 🎯 Step 3: Jules Task Assignments (7 Tasks)

Based on [AGENT_DELEGATION_PLAN_2025-11-01.md](./AGENT_DELEGATION_PLAN_2025-11-01.md), here are Jules-optimized tasks:

### Priority Order (Execute in Sequence)

1. **#584**: Admin Authentication (4h) - **START FIRST**
2. **#581**: WebAuthn Challenge/Verify (5h) - Dependency ✅ met
3. **#601**: PrivacyStatement (3h)
4. **#600**: Token Store Validation (4h)
5. **#604**: ComplianceReport (5h)
6. **#605**: SecurityMesh (6h)
7. **#574**: Consciousness Token Mapping (6h) - Research/Experimental

---

## 🚀 Jules Prompt Templates

### Task 1: Admin Authentication (#584) - START FIRST

**Issue**: https://github.com/LukhasAI/Lukhas/issues/584
**Priority**: P1 - HIGH
**Estimate**: 3-4 hours
**Dependency**: Core auth patterns established

```jules-prompt
TASK: Implement admin authentication for LUKHAS API routing
ISSUE: #584
REPO: https://github.com/LukhasAI/Lukhas
BRANCH: feat/admin-auth-584

CONTEXT:
- Admin routes in lukhas_website/lukhas/api/routing_admin.py need authentication
- Currently has TODO at line 103: "Implement proper admin authentication"
- Must integrate with existing ΛiD identity system in lukhas/identity/
- Follow Protocol pattern from core/ports/openai_provider.py

REQUIREMENTS:

1. CREATE lukhas_website/lukhas/api/middleware/admin_auth.py:
   - AdminAuthMiddleware class
   - Role-based access control (RBAC)
   - Roles: admin, superadmin
   - Integration with ΛiD identity system

2. IMPLEMENT authentication decorator:
   ```python
   from functools import wraps
   from typing import Callable

   def require_admin(roles: list[str] = ["admin"]):
       """Decorator to require admin authentication with specific roles."""
       def decorator(func: Callable):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               # Verify admin authentication
               # Check role permissions
               # Return 401 if not authenticated
               # Return 403 if authenticated but insufficient permissions
               return await func(*args, **kwargs)
           return wrapper
       return decorator
   ```

3. UPDATE lukhas_website/lukhas/api/routing_admin.py:
   - Apply @require_admin decorator to admin routes
   - Remove TODO at line 103
   - Add proper error responses (401/403)

4. CREATE tests/integration/api/test_admin_auth.py:
   - Test admin authentication flow
   - Test role verification (admin vs superadmin)
   - Test 401 response for unauthenticated requests
   - Test 403 response for insufficient permissions
   - Test successful admin access with valid credentials

INTEGRATION POINTS:
- lukhas/identity/ for authentication verification
- governance/guardian/ for policy enforcement (optional)
- observability/metrics.py for auth metrics

FILES TO CREATE:
- lukhas_website/lukhas/api/middleware/admin_auth.py
- lukhas_website/lukhas/api/middleware/__init__.py
- tests/integration/api/test_admin_auth.py

FILES TO MODIFY:
- lukhas_website/lukhas/api/routing_admin.py (line 103)

ACCEPTANCE CRITERIA:
- [ ] AdminAuthMiddleware implemented with RBAC
- [ ] @require_admin decorator working
- [ ] Admin routes protected (return 401/403 appropriately)
- [ ] Integration with ΛiD identity system
- [ ] All integration tests passing
- [ ] Type hints and mypy compliance
- [ ] No hardcoded credentials

COMMANDS TO RUN AFTER IMPLEMENTATION:
```bash
# Run tests
pytest tests/integration/api/test_admin_auth.py -v

# Type check
mypy lukhas_website/lukhas/api/middleware/admin_auth.py

# Run all API tests
pytest tests/integration/api/ -v

# Smoke test
make smoke
```

COMMIT MESSAGE TEMPLATE:
```
feat(api): implement admin authentication with RBAC

Problem:
- Admin routes lacked authentication (lukhas_website/lukhas/api/routing_admin.py:103)
- No role-based access control
- Security risk: unauthenticated admin access

Solution:
- Created AdminAuthMiddleware with RBAC
- Added @require_admin decorator for admin/superadmin roles
- Integrated with ΛiD identity system
- Returns 401/403 appropriately

Impact:
- Secured all admin routes
- Role-based permissions working
- Integration tests verify auth flow
- Closes #584

🤖 Generated with Agent Jules
```

CREATE PR: Yes
PR TITLE: feat(api): implement admin authentication with RBAC (#584)
PR BODY:
```markdown
Implements admin authentication for API admin routes.

## Changes
- ✅ AdminAuthMiddleware with role-based access control
- ✅ @require_admin decorator for route protection
- ✅ Integration with ΛiD identity system
- ✅ 401/403 error responses
- ✅ Integration tests

## Testing
```bash
pytest tests/integration/api/test_admin_auth.py -v
```

## Security Impact
- Secures admin routes requiring authentication
- Role-based permissions (admin, superadmin)
- No hardcoded credentials

Closes #584
```
```

---

### Task 2: WebAuthn Challenge/Verify (#581)

**Issue**: https://github.com/LukhasAI/Lukhas/issues/581
**Priority**: P1 - HIGH
**Estimate**: 4-5 hours
**Dependency**: #591 WebAuthn types ✅ COMPLETE

```jules-prompt
TASK: Implement WebAuthn challenge generation and verification
ISSUE: #581
REPO: https://github.com/LukhasAI/Lukhas
BRANCH: feat/webauthn-challenge-581

CONTEXT:
- WebAuthn types are implemented in lukhas_website/lukhas/identity/webauthn_types.py ✅
- Frontend component at lukhas_website/components/qrg-envelope.tsx:23 needs real WebAuthn
- Currently using placeholder authentication
- Must implement cryptographically secure challenge/verify flow

REQUIREMENTS:

1. CREATE lukhas_website/lukhas/identity/webauthn_challenge.py:

   ```python
   from lukhas.identity.webauthn_types import (
       CredentialCreationOptions,
       CredentialRequestOptions,
       PublicKeyCredentialCreation,
       PublicKeyCredentialAssertion,
       VerifiedRegistration,
       VerifiedAuthentication
   )

   class WebAuthnChallenge:
       """WebAuthn challenge generation and verification."""

       def generate_registration_options(
           self,
           user_id: str,
           username: str,
           display_name: str
       ) -> CredentialCreationOptions:
           """Generate options for WebAuthn registration."""
           # Generate cryptographically secure challenge (32 bytes)
           # Create RP entity (relying party)
           # Create user entity
           # Return CredentialCreationOptions

       def verify_registration(
           self,
           credential: PublicKeyCredentialCreation,
           expected_challenge: bytes
       ) -> VerifiedRegistration:
           """Verify WebAuthn registration response."""
           # Verify challenge matches
           # Verify attestation
           # Extract and store public key
           # Return VerifiedRegistration

       def generate_authentication_options(
           self,
           user_id: str
       ) -> CredentialRequestOptions:
           """Generate options for WebAuthn authentication."""
           # Generate cryptographically secure challenge
           # Retrieve user's credential IDs
           # Return CredentialRequestOptions

       def verify_authentication(
           self,
           credential: PublicKeyCredentialAssertion,
           expected_challenge: bytes,
           stored_public_key: bytes
       ) -> VerifiedAuthentication:
           """Verify WebAuthn authentication response."""
           # Verify challenge matches
           # Verify signature with stored public key
           # Return VerifiedAuthentication
   ```

2. CREATE API ENDPOINTS in lukhas_website/lukhas/api/routing_webauthn.py:
   - POST /api/webauthn/register/options - Generate registration challenge
   - POST /api/webauthn/register/verify - Verify registration
   - POST /api/webauthn/auth/options - Generate authentication challenge
   - POST /api/webauthn/auth/verify - Verify authentication

3. UPDATE lukhas_website/components/qrg-envelope.tsx:
   - Replace placeholder authentication at line 23
   - Use real WebAuthn API (navigator.credentials.create/get)
   - Call backend endpoints for challenge/verify
   - Handle errors gracefully

4. CREATE tests/integration/identity/test_webauthn_e2e.py:
   - Test full registration flow (challenge → response → verify)
   - Test full authentication flow
   - Test challenge expiration (5 minute timeout)
   - Test invalid signature rejection
   - Test replay attack prevention

SECURITY REQUIREMENTS:
- Challenges must be cryptographically random (os.urandom or secrets module)
- Challenges expire after 5 minutes
- Challenges used once only (prevent replay attacks)
- Signature verification using stored public key
- HTTPS required (WebAuthn security requirement)

FILES TO CREATE:
- lukhas_website/lukhas/identity/webauthn_challenge.py
- lukhas_website/lukhas/api/routing_webauthn.py
- tests/integration/identity/test_webauthn_e2e.py

FILES TO MODIFY:
- lukhas_website/components/qrg-envelope.tsx (line 23)

DEPENDENCIES:
- py-webauthn library (add to requirements.txt if needed)
- WebAuthn types from lukhas_website/lukhas/identity/webauthn_types.py ✅

ACCEPTANCE CRITERIA:
- [ ] Challenge generation with cryptographic randomness
- [ ] Registration flow working (challenge → response → verify)
- [ ] Authentication flow working
- [ ] Frontend component using real WebAuthn API
- [ ] Signature verification correct
- [ ] Challenge expiration and replay prevention
- [ ] E2E tests passing
- [ ] Works with standard WebAuthn devices (YubiKey, TouchID, etc.)

COMMANDS TO RUN:
```bash
# Run E2E tests
pytest tests/integration/identity/test_webauthn_e2e.py -v

# Type check
mypy lukhas_website/lukhas/identity/webauthn_challenge.py

# Smoke test
make smoke
```

COMMIT MESSAGE TEMPLATE:
```
feat(identity): implement WebAuthn challenge/verify flow

Problem:
- Frontend had placeholder WebAuthn (lukhas_website/components/qrg-envelope.tsx:23)
- No real challenge generation or verification
- Security risk: no actual authentication

Solution:
- Implemented WebAuthnChallenge with crypto-secure random challenges
- Created registration and authentication endpoints
- Updated frontend to use real WebAuthn API (navigator.credentials)
- Added challenge expiration (5 min) and replay prevention
- Signature verification with stored public keys

Impact:
- Real WebAuthn authentication working
- Compatible with YubiKey, TouchID, Windows Hello
- E2E tests verify full flow
- Closes #581

🤖 Generated with Agent Jules
```

CREATE PR: Yes
PR TITLE: feat(identity): implement WebAuthn challenge/verify flow (#581)
```

---

### Task 3: PrivacyStatement (#601)

**Issue**: https://github.com/LukhasAI/Lukhas/issues/601
**Priority**: P2
**Estimate**: 2-3 hours

```jules-prompt
TASK: Implement PrivacyStatement for QI privacy compliance
ISSUE: #601
REPO: https://github.com/LukhasAI/Lukhas
BRANCH: feat/privacy-statement-601

CONTEXT:
- QI system in qi/privacy/zero_knowledge_system.py needs privacy statements
- Line 55 has TODO: "PrivacyStatement"
- Required for GDPR/CCPA compliance metadata
- Integration with zero-knowledge proof system

REQUIREMENTS:

1. CREATE qi/privacy/privacy_statement.py:

   ```python
   from dataclasses import dataclass
   from datetime import timedelta
   from typing import List

   @dataclass(frozen=True)
   class PrivacyStatement:
       """Privacy statement for data processing compliance."""

       purpose: str  # Purpose of data collection (research, analytics, etc.)
       data_types: List[str]  # Types of data collected (health_records, pii, etc.)
       retention_period: timedelta  # How long data is retained
       jurisdictions: List[str]  # Applicable jurisdictions (US, EU, etc.)
       consent_required: bool  # Whether explicit consent is required
       zk_compatible: bool  # Compatible with zero-knowledge proofs

       # Optional fields
       data_processor: str = "LUKHAS AI"
       legal_basis: str = "consent"  # GDPR legal basis (consent, legitimate_interest, etc.)
       user_rights: List[str] = None  # User rights (access, rectification, erasure, etc.)

       def __post_init__(self):
           # Validate fields
           # Set defaults

       def to_dict(self) -> dict:
           """Serialize to dictionary for JSON export."""

       @classmethod
       def from_dict(cls, data: dict) -> "PrivacyStatement":
           """Deserialize from dictionary."""

       def is_gdpr_compliant(self) -> bool:
           """Check if statement meets GDPR requirements."""

       def is_ccpa_compliant(self) -> bool:
           """Check if statement meets CCPA requirements."""
   ```

2. UPDATE qi/privacy/zero_knowledge_system.py:
   - Remove TODO at line 55
   - Import and use PrivacyStatement
   - Add privacy_statement parameter to relevant methods
   - Validate privacy constraints in ZK proof generation

3. CREATE tests/unit/qi/test_privacy_statement.py:
   - Test PrivacyStatement creation with all fields
   - Test with minimal required fields
   - Test GDPR compliance checking
   - Test CCPA compliance checking
   - Test JSON serialization/deserialization
   - Test validation (invalid retention period, etc.)
   - Test integration with zero-knowledge system

FILES TO CREATE:
- qi/privacy/privacy_statement.py
- tests/unit/qi/test_privacy_statement.py

FILES TO MODIFY:
- qi/privacy/zero_knowledge_system.py (line 55)

ACCEPTANCE CRITERIA:
- [ ] PrivacyStatement dataclass with all required fields
- [ ] GDPR and CCPA compliance validation
- [ ] JSON serialization working
- [ ] Integration with zero_knowledge_system.py
- [ ] Type hints and frozen dataclass (immutable)
- [ ] All unit tests passing (15+ tests)
- [ ] Validation for invalid data

COMMANDS TO RUN:
```bash
pytest tests/unit/qi/test_privacy_statement.py -v
mypy qi/privacy/privacy_statement.py
make smoke
```

COMMIT MESSAGE:
```
feat(qi): implement PrivacyStatement for compliance metadata

Problem:
- qi/privacy/zero_knowledge_system.py:55 had TODO for PrivacyStatement
- No structured privacy compliance metadata
- GDPR/CCPA compliance checking manual

Solution:
- Implemented frozen PrivacyStatement dataclass
- Added GDPR and CCPA compliance validation
- JSON serialization for audit trails
- Integration with zero-knowledge proof system

Impact:
- Structured privacy metadata for all data processing
- Automated GDPR/CCPA compliance checking
- Closes #601

🤖 Generated with Agent Jules
```

CREATE PR: Yes
```

---

### Remaining Tasks (4-7) - Summary Prompts

**Task 4: Token Store Validation (#600)** - 4 hours
```jules-prompt
Implement token store validation in lukhas/identity/token_store.py
- Persistent token storage (Redis preferred, SQLite fallback)
- Token validation against stored tokens
- Revocation support
- Automatic expiration cleanup
See AGENT_DELEGATION_PLAN Task 12 for full spec
```

**Task 5: ComplianceReport (#604)** - 5 hours
```jules-prompt
Implement ComplianceReport in qi/compliance/compliance_report.py
- Generate GDPR/CCPA/HIPAA reports
- Track consent, data access, retention
- JSON/PDF export
- Integration with Guardian audit trail
See AGENT_DELEGATION_PLAN Task 9 for full spec
```

**Task 6: SecurityMesh (#605)** - 6 hours
```jules-prompt
Implement SecurityMesh in qi/security/security_mesh.py
- Multi-layer security coordination
- Policy enforcement mesh
- Distributed trust verification
- <10ms overhead per request
See AGENT_DELEGATION_PLAN Task 10 for full spec
```

**Task 7: Consciousness Token Mapping (#574)** - 6 hours (RESEARCH)
```jules-prompt
Implement consciousness token mapping in candidate/consciousness/token_mapper.py
- Map consciousness states to token representations
- Emotional state encoding
- STAYS IN CANDIDATE LANE (not production)
- Research/experimental only
See AGENT_DELEGATION_PLAN Task 17 for full spec
```

---

## 📊 Execution Strategy

### Recommended Sequence

**Day 1** (Start Now):
1. Review and merge Codex PRs (#787-#794) - 30 minutes
2. Launch Jules Task 1 (#584 Admin Auth) - 4 hours
3. Launch Jules Task 2 (#581 WebAuthn) - 5 hours

**Day 2**:
4. Launch Jules Task 3 (#601 PrivacyStatement) - 3 hours
5. Launch Jules Task 4 (#600 Token Store) - 4 hours

**Day 3**:
6. Launch Jules Task 5 (#604 ComplianceReport) - 5 hours
7. Launch Jules Task 6 (#605 SecurityMesh) - 6 hours

**Day 4** (Optional Research):
8. Launch Jules Task 7 (#574 Consciousness) - 6 hours

**Total**: 33 hours over 4 days

---

## ✅ Quality Checklist (After Each Task)

- [ ] All tests passing
- [ ] Type checking clean (mypy)
- [ ] No hardcoded secrets
- [ ] Integration tests included
- [ ] Documentation updated
- [ ] Follows existing patterns
- [ ] T4 commit message
- [ ] PR created with proper description
- [ ] GitHub issue updated

---

## 🔧 Jules CLI Commands (If Using CLI)

```bash
# Set API key
export JULES_API_KEY="your_key_here"

# Execute task
jules --repo /Users/agi_dev/LOCAL-REPOS/Lukhas \
      --issue 584 \
      --prompt "$(cat prompt.txt)"

# Monitor progress
jules --status

# Review changes
jules --diff

# Create PR
jules --pr --title "feat(api): implement admin authentication"
```

---

## 📚 References

- **API Docs**: https://developers.google.com/jules/api
- **Delegation Plan**: [AGENT_DELEGATION_PLAN_2025-11-01.md](./AGENT_DELEGATION_PLAN_2025-11-01.md)
- **Orchestration Guide**: [MULTI_AGENT_ORCHESTRATION_GUIDE.md](./MULTI_AGENT_ORCHESTRATION_GUIDE.md)
- **GitHub Issues Audit**: [../audits/GITHUB_ISSUES_AUDIT_2025-11-01.md](../audits/GITHUB_ISSUES_AUDIT_2025-11-01.md)

---

## 🚨 Important Notes

1. **Merge Codex PRs First**: 8 PRs are ready to merge - do this before Jules starts to avoid conflicts
2. **API Key Security**: NEVER commit .env.local - it's gitignored
3. **Sequential Execution**: Complete Task 1 before starting Task 2 (dependency chain)
4. **Test Everything**: All Jules implementations must include comprehensive tests
5. **Review PRs**: Jules will create PRs - review before merging to ensure quality
