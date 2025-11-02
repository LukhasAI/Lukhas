---
status: active
type: agent-instructions
owner: claude
platform: github-copilot
updated: 2025-11-01
---

# GitHub Copilot Agent Instructions

Ready-to-execute instructions for GitHub Copilot Workspace agents. Each task includes complete context, specifications, and acceptance criteria.

---

## Quick Start (In VS Code)

1. Open GitHub Copilot Chat (Cmd/Ctrl + Shift + I)
2. Copy the task prompt below
3. Include reference to delegation plan: `@workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md`
4. Execute and review the generated code

---

## Task 1: Token Infrastructure (#586, #587)

**Priority**: P2 - Quick Win
**Model**: GPT-5-Codex (Preview) or Claude Sonnet 4.5
**Estimate**: 2 hours
**Issues**: #586, #587

### Copilot Prompt

```
@workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md

Please implement TokenClaims and TokenIntrospection TypedDict definitions following the OAuth 2.0 RFC 7662 Token Introspection specification.

CONTEXT:
- Follow the pattern in core/ports/openai_provider.py (TypedDict with NotRequired)
- We need these for lukhas/identity/ token management
- Issues #586 (TokenClaims) and #587 (TokenIntrospection) will be resolved

REQUIREMENTS:

1. Create lukhas/identity/token_types.py with:

TokenClaims TypedDict:
- iss: str (issuer)
- sub: str (subject)
- aud: str | list[str] (audience)
- exp: int (expiration timestamp)
- nbf: NotRequired[int] (not before)
- iat: NotRequired[int] (issued at)
- jti: NotRequired[str] (JWT ID)
- scope: NotRequired[str] (OAuth scope)
- Additional custom claims as needed

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
- Test TokenClaims structure with all fields
- Test TokenClaims with minimal required fields
- Test TokenIntrospection for active and inactive tokens
- Test validation functions with valid/invalid data
- Test expiration checking
- Test RFC 7662 compliance

ACCEPTANCE CRITERIA:
- [ ] TokenClaims TypedDict matches JWT standard claims
- [ ] TokenIntrospection TypedDict matches RFC 7662
- [ ] Validation functions handle valid and invalid data
- [ ] Expiration checking works correctly
- [ ] Type hints work with mypy/pyright
- [ ] 100% test coverage
- [ ] All tests pass

FILES TO CREATE:
- lukhas/identity/token_types.py
- tests/unit/identity/test_token_types.py

REFERENCE:
- OAuth 2.0 RFC 7662: https://datatracker.ietf.org/doc/html/rfc7662
- JWT RFC 7519: https://datatracker.ietf.org/doc/html/rfc7519
- Pattern: core/ports/openai_provider.py (TypedDict usage)
```

---

## Task 2: OAuth Library Evaluation (#564)

**Priority**: P3 - Documentation
**Model**: Claude Sonnet 4.5
**Estimate**: 2-3 hours
**Issue**: #564

### Copilot Prompt

```
@workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md

Please analyze our current usage of requests-oauthlib and compare it with authlib to determine if we should migrate.

CONTEXT:
- We currently use requests-oauthlib for OAuth 2.0 flows
- authlib is more modern, better maintained, supports OAuth 2.1
- Need to decide: migrate, stay, or hybrid approach

REQUIREMENTS:

1. Analyze current requests-oauthlib usage:
   - Search codebase for all imports
   - Identify OAuth flows we use (authorization code, client credentials, etc.)
   - Check for any deprecated features we're using
   - Assess security of current implementation

2. Compare libraries:

Feature Comparison:
- OAuth 2.0 / 2.1 support
- OIDC (OpenID Connect) support
- Security features (PKCE, token validation)
- Maintenance status (last update, active issues)
- Documentation quality
- Community adoption
- Performance
- Type hints / mypy support

Security Comparison:
- Vulnerability history
- Security best practices support
- Token validation mechanisms
- PKCE support for public clients

Maintenance Comparison:
- Last release date
- Open issues / PRs
- Contributor activity
- Python version support
- Deprecation warnings

3. Create docs/decisions/ADR-001-oauth-library-selection.md:

Title: ADR-001: OAuth Library Selection (requests-oauthlib vs authlib)

Status: [Proposed/Accepted/Rejected]

Context:
- Current state: requests-oauthlib usage across codebase
- Trigger: OAuth 2.1 adoption, maintenance concerns

Decision:
- Recommendation: [Stay/Migrate/Hybrid]
- Rationale: Security, maintenance, features

Consequences:
- Migration effort estimate (if applicable)
- Breaking changes (if applicable)
- Benefits and trade-offs

Implementation Plan (if migrating):
- Phase 1: New code uses authlib
- Phase 2: Migrate critical paths
- Phase 3: Complete migration
- Rollback plan

4. If migration recommended:
   - Create migration guide
   - Identify high-risk areas
   - Estimate effort in hours
   - Suggest migration phases

ACCEPTANCE CRITERIA:
- [ ] Complete analysis of current requests-oauthlib usage
- [ ] Feature comparison table (requests-oauthlib vs authlib)
- [ ] Security comparison documented
- [ ] Maintenance status assessed
- [ ] Clear recommendation with rationale
- [ ] Migration plan if applicable
- [ ] ADR document created

FILES TO CREATE:
- docs/decisions/ADR-001-oauth-library-selection.md
- docs/decisions/oauth-library-comparison.md (detailed comparison)

SEARCH FOR:
- "import requests_oauthlib"
- "from requests_oauthlib"
- OAuth flows in branding/ directory
```

---

## Task 3: Governance Example (#557)

**Priority**: P3 - Documentation + Example
**Model**: GPT-5
**Estimate**: 2-3 hours
**Issue**: #557

### Copilot Prompt

```
@workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md

Please create a comprehensive governance example showing how to use the Guardian system for consent management and policy enforcement.

CONTEXT:
- Guardian system in governance/guardian/ handles constitutional AI and policy enforcement
- Need practical example for developers to understand consent flow
- Should demonstrate real-world use case

REQUIREMENTS:

1. Create docs/governance/GUARDIAN_EXAMPLE.md:

# Guardian System Example: Consent Management

## Overview
Brief description of what this example demonstrates

## Use Case
Healthcare app collecting patient data for research

## Components
- Patient consent collection
- Data usage policy definition
- Consent verification
- Policy enforcement
- Audit trail

## Step-by-Step Implementation

### 1. Define Data Usage Policy
```python
# Example policy definition
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
# Example consent verification
```

### 5. Access Audit Trail
```python
# Example audit access
```

## Complete Working Example
Full code example with imports

## Testing
How to test the example

## Common Patterns
- Consent revocation
- Policy updates
- Multi-jurisdiction consent

2. Create examples/governance/consent_example.py:

Working Python code demonstrating:
- Policy definition using Guardian
- Consent collection and storage
- Policy enforcement on data access
- Consent verification before operations
- Audit trail generation
- Error handling

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

3. Create tests/examples/test_governance_example.py:
- Test policy definition
- Test consent collection
- Test consent verification
- Test policy enforcement
- Test audit trail
- Test consent revocation
- Test multi-jurisdiction scenarios

ACCEPTANCE CRITERIA:
- [ ] Complete governance example with explanation
- [ ] Working code in examples/governance/
- [ ] Demonstrates all key Guardian features (consent, policy, audit)
- [ ] Covers real-world use case (healthcare/research)
- [ ] Includes error handling and edge cases
- [ ] Test coverage for example code
- [ ] Clear documentation with step-by-step guide
- [ ] Example runs without errors

FILES TO CREATE:
- docs/governance/GUARDIAN_EXAMPLE.md
- examples/governance/consent_example.py
- examples/governance/__init__.py
- tests/examples/test_governance_example.py

REFERENCE:
- governance/guardian/ for Guardian implementation
- qi/privacy/ for privacy components
```

---

## Task 4: WebAuthn Documentation (#563)

**Priority**: P3 - Documentation
**Model**: Gemini 2.5 Pro
**Estimate**: 2-3 hours
**Issue**: #563

### Copilot Prompt

```
@workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md

Please create a comprehensive WebAuthn developer guide based on our implementation in lukhas/identity/.

CONTEXT:
- WebAuthn types are now implemented in lukhas/identity/webauthn_types.py (just completed!)
- Need developer documentation for using WebAuthn in LUKHAS
- Cover registration, authentication, and credential management

REQUIREMENTS:

1. Create docs/identity/WEBAUTHN_GUIDE.md:

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

# Example code
```

### Frontend (TypeScript)
```typescript
// Registration example
```

## Authentication Flow

### Backend (Python)
1. Generate authentication options
2. Send challenge to frontend
3. Verify assertion
4. Return auth result

```python
from lukhas.identity.webauthn_types import (
    CredentialRequestOptions,
    PublicKeyCredentialAssertion,
    VerifiedAuthentication
)

# Example code
```

### Frontend (TypeScript)
```typescript
// Authentication example
```

## Credential Management
- List user credentials
- Remove credentials
- Update credential metadata

## API Reference

### Types
All TypedDict definitions from webauthn_types.py

### Endpoints
- POST /api/webauthn/register/options
- POST /api/webauthn/register/verify
- POST /api/webauthn/auth/options
- POST /api/webauthn/auth/verify

## Troubleshooting
Common issues and solutions:
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

2. Create docs/identity/WEBAUTHN_API_REFERENCE.md:

Complete API reference for all WebAuthn endpoints and types

3. Add code examples:
- docs/identity/examples/webauthn-registration.py
- docs/identity/examples/webauthn-authentication.py
- docs/identity/examples/webauthn-frontend.ts

ACCEPTANCE CRITERIA:
- [ ] Complete developer guide with all sections
- [ ] Code examples for registration and authentication
- [ ] Both Python and TypeScript examples
- [ ] API reference for all endpoints and types
- [ ] Troubleshooting section with common issues
- [ ] Security best practices documented
- [ ] Links to W3C WebAuthn spec
- [ ] Examples use actual types from webauthn_types.py
- [ ] Clear, step-by-step instructions

FILES TO CREATE:
- docs/identity/WEBAUTHN_GUIDE.md
- docs/identity/WEBAUTHN_API_REFERENCE.md
- docs/identity/examples/webauthn-registration.py
- docs/identity/examples/webauthn-authentication.py
- docs/identity/examples/webauthn-frontend.ts

REFERENCE:
- lukhas/identity/webauthn_types.py (14 types, 220 lines)
- lukhas/identity/webauthn_production.py (production implementation)
- lukhas_website/components/qrg-envelope.tsx (frontend component)
- W3C WebAuthn Spec: https://www.w3.org/TR/webauthn-2/
```

---

## Execution Instructions

### In VS Code

1. **Open Copilot Chat**: `Cmd+Shift+I` (Mac) or `Ctrl+Shift+I` (Windows/Linux)

2. **Select Model** (if available):
   - Task 1 (Token Infrastructure): GPT-5-Codex or Claude Sonnet 4.5
   - Task 2 (OAuth Evaluation): Claude Sonnet 4.5
   - Task 3 (Governance Example): GPT-5
   - Task 4 (WebAuthn Docs): Gemini 2.5 Pro

3. **Copy entire prompt** from the task above

4. **Add workspace reference**:
   ```
   @workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md
   [paste prompt here]
   ```

5. **Execute** and review generated code

6. **Verify**:
   - Run tests: `pytest tests/unit/identity/test_token_types.py -v`
   - Type check: `mypy lukhas/identity/token_types.py`
   - Lint: `ruff check lukhas/identity/token_types.py`

7. **Commit** with T4 standards:
   ```bash
   git add <files>
   git commit  # Use T4 commit message format
   ```

---

## Quality Checklist

After each Copilot agent completes:

- [ ] All files created as specified
- [ ] Tests written and passing
- [ ] Type hints added (mypy compliant)
- [ ] Code follows existing patterns
- [ ] Documentation clear and complete
- [ ] No hardcoded secrets or keys
- [ ] Imports organized correctly
- [ ] Comments explain non-obvious logic
- [ ] Edge cases handled
- [ ] Error messages are helpful

---

## Success Metrics

**Task 1 (Token Infrastructure)**:
- 2 TypedDict definitions
- 4 validation functions
- 15+ unit tests
- 100% test pass rate

**Task 2 (OAuth Evaluation)**:
- 1 ADR document
- Comparison table (5+ dimensions)
- Clear recommendation with rationale
- Migration plan if applicable

**Task 3 (Governance Example)**:
- 1 comprehensive guide
- 1 working code example
- 10+ unit tests
- Example runs without errors

**Task 4 (WebAuthn Docs)**:
- 1 developer guide (8+ sections)
- 1 API reference
- 3+ code examples (Python + TypeScript)
- Troubleshooting section

---

## Troubleshooting

**If Copilot generates incorrect code**:
1. Review the prompt for clarity
2. Add more specific examples
3. Reference existing patterns explicitly
4. Break task into smaller subtasks

**If tests fail**:
1. Check imports and dependencies
2. Verify type hints match actual usage
3. Review test assertions
4. Run single test for debugging: `pytest tests/path/to/test.py::test_name -v`

**If types don't match**:
1. Check that NotRequired is imported from typing_extensions
2. Verify Union types use correct syntax for Python 3.9+
3. Run mypy: `mypy <file> --show-error-codes`

---

## Next Steps After Completion

1. **Update GitHub issues** with completion status
2. **Close resolved issues** (#586, #587, #564, #557, #563)
3. **Update delegation plan** with completion status
4. **Run comprehensive tests**: `make test`
5. **Commit all changes** with T4 standards

---

## Contact

For questions or issues:
- Check delegation plan: docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md
- Review orchestration guide: docs/gonzo/MULTI_AGENT_ORCHESTRATION_GUIDE.md
- See GitHub issues audit: docs/audits/GITHUB_ISSUES_AUDIT_2025-11-01.md
