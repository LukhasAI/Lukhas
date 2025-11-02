---
status: ready-to-execute
type: gemini-code-assist-tasks
owner: agi_dev
created: 2025-11-01

---
# Gemini Code Assist Tasks for LUKHAS
---

## Task 1: Token Infrastructure (#586, #587) ⚡ FASTEST

**Priority**: P2 - Quick Win (1-2 hours)
**Issues**: #586 (TokenClaims), #587 (TokenIntrospection)
**Why Gemini**: Simple TypedDict definitions, perfect for Gemini

### Gemini Prompt

```
I need to implement TokenClaims and TokenIntrospection TypedDict definitions for OAuth 2.0 token management.

CONTEXT:
- Follow the pattern in core/ports/openai_provider.py (TypedDict with NotRequired)
- We need these for lukhas/identity/ token management
- Must comply with JWT RFC 7519 and OAuth 2.0 RFC 7662

REQUIREMENTS:

1. Create lukhas/identity/token_types.py with:

TokenClaims TypedDict (JWT standard claims):
- iss: str (issuer)
- sub: str (subject)
- aud: str | list[str] (audience)
- exp: int (expiration timestamp)
- nbf: NotRequired[int] (not before)
- iat: NotRequired[int] (issued at)
- jti: NotRequired[str] (JWT ID)
- scope: NotRequired[str] (OAuth scope)

TokenIntrospection TypedDict (RFC 7662):
- active: bool (token is active)
- scope: NotRequired[str] (OAuth scope)
- client_id: NotRequired[str] (client identifier)
- username: NotRequired[str] (human-readable identifier)
- token_type: NotRequired[str] (type of token)
- exp: NotRequired[int] (expiration timestamp)
- iat: NotRequired[int] (issued at)
- nbf: NotRequired[int] (not before)
- sub: NotRequired[str] (subject)
- aud: NotRequired[str | list[str]] (audience)
- iss: NotRequired[str] (issuer)
- jti: NotRequired[str] (JWT ID)

2. Add validation functions:
- validate_token_claims(claims: dict) -> TokenClaims
- validate_token_introspection(response: dict) -> TokenIntrospection
- is_token_expired(claims: TokenClaims) -> bool
- get_remaining_lifetime(claims: TokenClaims) -> timedelta

3. Create tests/unit/identity/test_token_types.py:
- Test TokenClaims with all fields
- Test TokenClaims with minimal required fields
- Test TokenIntrospection for active/inactive tokens
- Test validation functions
- Test expiration checking
- Test RFC 7662 compliance

ACCEPTANCE CRITERIA:
- TokenClaims TypedDict matches JWT standard
- TokenIntrospection TypedDict matches RFC 7662
- Validation functions handle valid/invalid data
- Expiration checking works correctly
- Type hints work with mypy/pyright
- 100% test coverage
- All tests pass

FILES TO CREATE:
- lukhas/identity/token_types.py
- tests/unit/identity/test_token_types.py

REFERENCE:
- OAuth 2.0 RFC 7662: https://datatracker.ietf.org/doc/html/rfc7662
- JWT RFC 7519: https://datatracker.ietf.org/doc/html/rfc7519
- Pattern: core/ports/openai_provider.py
```

### After Gemini Completes

```bash
# Test
pytest tests/unit/identity/test_token_types.py -v

# Type check
mypy lukhas/identity/token_types.py

# Commit
git add lukhas/identity/token_types.py tests/unit/identity/test_token_types.py
git commit -m "feat(identity): add TokenClaims and TokenIntrospection types

Problem:
- Missing type definitions for OAuth 2.0 token management
- No validation functions for JWT claims and token introspection
- Issues #586 and #587 open

Solution:
- Created TokenClaims TypedDict (JWT RFC 7519)
- Created TokenIntrospection TypedDict (OAuth 2.0 RFC 7662)
- Added validation and expiration checking functions
- Comprehensive test coverage

Impact:
- Type-safe token handling
- RFC-compliant token management
- Closes #586, #587"
```

---

## Task 2: WebAuthn Documentation (#563) 📚

**Priority**: P3 - Documentation (2-3 hours)
**Issue**: #563
**Why Gemini**: Documentation generation, Gemini excels at this

### Gemini Prompt

```
I need comprehensive WebAuthn developer documentation based on our implementation in lukhas/identity/.

CONTEXT:
- WebAuthn types are implemented in lukhas_website/lukhas/identity/webauthn_types.py
- 14 TypedDict definitions, 220 lines, W3C WebAuthn Level 2 compliant
- Need developer guide for using WebAuthn in LUKHAS

REQUIREMENTS:

Create docs/identity/WEBAUTHN_GUIDE.md with:

# WebAuthn in LUKHAS: Developer Guide

## Table of Contents
- Overview
- Quick Start
- Registration Flow
- Authentication Flow
- Credential Management
- API Reference
- Troubleshooting
- Security Best Practices
- W3C Spec Compliance

## Overview
What is WebAuthn and how it works in LUKHAS

## Quick Start
Minimal example to get started

## Registration Flow

### Backend (Python)
Step-by-step with code examples:
1. Generate registration options
2. Send to frontend
3. Receive and verify attestation
4. Store credential

```python
from lukhas.identity.webauthn_types import (
    CredentialCreationOptions,
    PublicKeyCredentialCreation,
    VerifiedRegistration
)

# Example code showing actual usage
```

### Frontend (TypeScript)
```typescript
// Registration example with navigator.credentials.create()
```

## Authentication Flow

### Backend (Python)
1. Generate authentication options
2. Send challenge to frontend
3. Verify assertion
4. Return auth result

### Frontend (TypeScript)
```typescript
// Authentication example with navigator.credentials.get()
```

## Credential Management
- List user credentials
- Remove credentials
- Update credential metadata

## API Reference
All TypedDict definitions from webauthn_types.py with descriptions

## Troubleshooting
Common issues:
- "NotAllowedError" during registration
- "InvalidStateError" during authentication
- Browser compatibility issues
- HTTPS requirement

## Security Best Practices
- Challenge randomness
- Timeout values
- User verification requirements
- Attestation handling

## W3C Spec Compliance
- WebAuthn Level 2 compliance
- FIDO2 CTAP2 support
- Supported authenticator types

Also create:
- docs/identity/WEBAUTHN_API_REFERENCE.md (complete API reference)
- docs/identity/examples/webauthn-registration.py
- docs/identity/examples/webauthn-authentication.py
- docs/identity/examples/webauthn-frontend.ts

ACCEPTANCE CRITERIA:
- Complete developer guide with all sections
- Code examples for registration and authentication
- Both Python and TypeScript examples
- API reference for all endpoints and types
- Troubleshooting section
- Security best practices documented
- Links to W3C WebAuthn spec
- Clear, step-by-step instructions

FILES TO CREATE:
- docs/identity/WEBAUTHN_GUIDE.md
- docs/identity/WEBAUTHN_API_REFERENCE.md
- docs/identity/examples/webauthn-registration.py
- docs/identity/examples/webauthn-authentication.py
- docs/identity/examples/webauthn-frontend.ts

REFERENCE:
- lukhas/identity/webauthn_types.py (14 types, 220 lines)
- lukhas/identity/webauthn_production.py
- W3C WebAuthn Spec: https://www.w3.org/TR/webauthn-2/
```

### After Gemini Completes

```bash
# Verify files created
ls -la docs/identity/WEBAUTHN_*.md
ls -la docs/identity/examples/webauthn-*

# Commit
git add docs/identity/
git commit -m "docs(identity): add comprehensive WebAuthn developer guide

Problem:
- No developer documentation for WebAuthn in LUKHAS
- Developers unclear how to use WebAuthn types
- Issue #563 open

Solution:
- Created WEBAUTHN_GUIDE.md with complete developer guide
- Added WEBAUTHN_API_REFERENCE.md with all type definitions
- Included Python and TypeScript code examples
- Added troubleshooting and security best practices

Impact:
- Developers can implement WebAuthn flows quickly
- Clear examples for registration and authentication
- W3C spec compliance documented
- Closes #563"
```

---

## Task 3: Governance Example (#557) 🛡️

**Priority**: P3 - Documentation + Example (2-3 hours)
**Issue**: #557
**Why Gemini**: Creative example generation

### Gemini Prompt

```
I need a comprehensive governance example showing how to use the Guardian system for consent management and policy enforcement.

CONTEXT:
- Guardian system in governance/guardian/ handles constitutional AI and policy enforcement
- Need practical example for developers
- Real-world use case demonstration

REQUIREMENTS:

Create docs/governance/GUARDIAN_EXAMPLE.md:

# Guardian System Example: Consent Management

## Overview
Healthcare app collecting patient data for research

## Use Case
Patient consent collection, policy enforcement, audit trail

## Step-by-Step Implementation

### 1. Define Data Usage Policy
```python
# Example policy definition using Guardian
```

### 2. Collect User Consent
```python
# Example consent flow
```

### 3. Enforce Policy
```python
# Example policy enforcement
```

### 4. Verify Consent
```python
# Example consent verification before data access
```

### 5. Access Audit Trail
```python
# Example audit access
```

## Complete Working Example
Full code with imports

## Testing
How to test the example

## Common Patterns
- Consent revocation
- Policy updates
- Multi-jurisdiction consent

Also create:
- examples/governance/consent_example.py (working code)
- examples/governance/__init__.py
- tests/examples/test_governance_example.py

The example should demonstrate:
1. Policy definition using GuardianPolicy
2. Consent collection and storage
3. Policy enforcement on data access
4. Consent verification before operations
5. Audit trail generation
6. Error handling

Example flow:
```python
# 1. Define policy
policy = GuardianPolicy(
    purpose="research",
    data_types=["health_records"],
    retention_days=365,
    jurisdictions=["US", "EU"]
)

# 2. Collect consent
consent = collect_user_consent(user_id, policy)

# 3. Verify before access
if verify_consent(user_id, "health_records"):
    data = access_health_records(user_id)
else:
    raise ConsentDeniedException()

# 4. Audit
audit_trail = get_audit_trail(user_id)
```

ACCEPTANCE CRITERIA:
- Complete governance example with explanation
- Working code in examples/governance/
- Demonstrates all key Guardian features
- Covers real-world use case (healthcare/research)
- Includes error handling and edge cases
- Test coverage for example code
- Clear step-by-step guide
- Example runs without errors

FILES TO CREATE:
- docs/governance/GUARDIAN_EXAMPLE.md
- examples/governance/consent_example.py
- examples/governance/__init__.py
- tests/examples/test_governance_example.py

REFERENCE:
- governance/guardian/ for Guardian implementation
- qi/privacy/ for privacy components
```

### After Gemini Completes

```bash
# Test the example
python examples/governance/consent_example.py
pytest tests/examples/test_governance_example.py -v

# Commit
git add docs/governance/ examples/governance/ tests/examples/
git commit -m "docs(governance): add Guardian consent management example

Problem:
- No practical example for Guardian system usage
- Developers unclear on consent management flow
- Issue #557 open

Solution:
- Created comprehensive consent management example
- Added working code with healthcare use case
- Included step-by-step guide and tests
- Covered policy definition, consent, enforcement, audit

Impact:
- Developers can implement governance quickly
- Real-world healthcare example provided
- All Guardian features demonstrated
- Closes #557"
```

---

## 📊 Recommended Execution Order

1. **Start with Task 1** (Token Infrastructure) - Fastest, 1-2 hours
2. **Then Task 2** (WebAuthn Docs) - Documentation, 2-3 hours
3. **Finally Task 3** (Governance Example) - Most complex, 2-3 hours

**Total: 5-8 hours of Gemini work, can run in parallel with Jules!**

---

## ✅ Success Metrics

**Task 1 (Token Infrastructure)**:
- 2 TypedDict definitions
- 4 validation functions
- 15+ unit tests
- 100% test pass rate
- Closes #586, #587

**Task 2 (WebAuthn Docs)**:
- 1 developer guide (8+ sections)
- 1 API reference
- 3+ code examples (Python + TypeScript)
- Troubleshooting section
- Closes #563

**Task 3 (Governance Example)**:
- 1 comprehensive guide
- 1 working code example
- 10+ unit tests
- Example runs without errors
- Closes #557

---

**🎯 Ready to execute in VS Code! Copy any prompt above into Gemini Code Assist panel.**
