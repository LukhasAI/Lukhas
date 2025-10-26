# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# consent Module

**Privacy-First Consent Management System**

The `consent` module provides comprehensive consent management for LUKHAS AI, implementing GDPR/CCPA-compliant consent tracking, capability tokens, purpose-based data access, and escalation management with full audit trail support.

## Core Purpose

**Consent Ledger**: Privacy-first consent management with granular control over data usage, purpose validation, capability tokens, and automatic escalation for sensitive operations.

**Lane**: L2 Integration
**Dependencies**: None (foundational governance)
**Entrypoints**: 20 (10 API + 10 service)

---

## Quick Start

```python
from consent.service import ConsentService, Purpose, DataCategory
from consent.api import GrantConsentRequest, VerifyTokenRequest

# Initialize consent service
consent = ConsentService()

# Grant consent
request = GrantConsentRequest(
    user_id="user_123",
    purpose=Purpose.PERSONALIZATION,
    data_category=DataCategory.PERSONAL,
    scopes=["email", "preferences"],
    ttl=86400  # 24 hours
)
response = consent.grant_consent(request)
token = response.capability_token

# Verify token before data access
verify = VerifyTokenRequest(token=token)
if consent.verify_token(verify).valid:
    # Access data
    pass
```

---

## Component Architecture

### 1. Consent Service (`consent.service`)

**10 Service Components**:
- ConsentService
- ConsentGrantRequest
- ConsentRevokeRequest
- CapabilityToken
- Purpose
- DataCategory
- ConsentLedgerEntry
- EscalationLevel
- validate_scopes
- validate_ttl

**ConsentService**:
```python
from consent.service import ConsentService, Purpose, DataCategory

service = ConsentService()

# Grant consent
from consent.service import ConsentGrantRequest

request = ConsentGrantRequest(
    user_id="user_123",
    purpose=Purpose.ANALYTICS,
    data_category=DataCategory.BEHAVIORAL,
    scopes=["session_data", "interaction_logs"],
    ttl=3600  # 1 hour
)

result = service.grant_consent(request)
print(f"Token: {result.capability_token}")
print(f"Expiry: {result.expiry_timestamp}")
```

**CapabilityToken**:
```python
from consent.service import CapabilityToken

token = CapabilityToken(
    token_id="cap_abc123",
    user_id="user_123",
    purpose=Purpose.PERSONALIZATION,
    scopes=["email", "name"],
    issued_at=1696320000,
    expires_at=1696406400
)

# Validate token
if token.is_valid():
    if "email" in token.scopes:
        # Access email data
        pass
```

**Purpose Enum**:
```python
from consent.service import Purpose

# Valid purposes
Purpose.PERSONALIZATION      # Personalize user experience
Purpose.ANALYTICS            # Analytics and insights
Purpose.SYSTEM_OPERATION     # Core system functionality
Purpose.RESEARCH             # Research and development
Purpose.MARKETING            # Marketing communications
```

**DataCategory Enum**:
```python
from consent.service import DataCategory

# Data categories
DataCategory.PERSONAL        # PII (name, email, etc.)
DataCategory.BEHAVIORAL      # Usage patterns, interactions
DataCategory.TECHNICAL       # Device info, IP address
DataCategory.SENSITIVE       # Health, financial, biometric
```

**EscalationLevel**:
```python
from consent.service import EscalationLevel

# Escalation levels
EscalationLevel.LOW          # Routine operations
EscalationLevel.MEDIUM       # Increased scrutiny
EscalationLevel.HIGH         # Sensitive operations
EscalationLevel.CRITICAL     # Requires explicit user approval
```

### 2. Consent API (`consent.api`)

**10 API Components**:
- GrantConsentRequest
- GrantConsentResponse
- RevokeConsentRequest
- RevokeConsentResponse
- LedgerResponse
- EscalateRequest
- EscalateResponse
- VerifyTokenRequest
- VerifyTokenResponse
- ConsentStatsResponse
- get_client_ip
- get_client_context

**Grant Consent API**:
```python
from consent.api import GrantConsentRequest, GrantConsentResponse

# API request
request = GrantConsentRequest(
    user_id="user_123",
    purpose="personalization",
    data_category="personal",
    scopes=["email", "preferences"],
    ttl=86400
)

# API response
response = GrantConsentResponse(
    success=True,
    capability_token="cap_abc123",
    expiry_timestamp=1696406400,
    ledger_entry_id="ledger_xyz789"
)
```

**Revoke Consent API**:
```python
from consent.api import RevokeConsentRequest, RevokeConsentResponse

# Revoke consent
revoke_request = RevokeConsentRequest(
    user_id="user_123",
    capability_token="cap_abc123",
    reason="user_request"
)

revoke_response = RevokeConsentResponse(
    success=True,
    revoked_at=1696320500
)
```

**Verify Token API**:
```python
from consent.api import VerifyTokenRequest, VerifyTokenResponse

# Verify token validity
verify_request = VerifyTokenRequest(token="cap_abc123")

verify_response = VerifyTokenResponse(
    valid=True,
    user_id="user_123",
    purpose="personalization",
    scopes=["email", "preferences"],
    expires_at=1696406400
)
```

**Escalate Request API**:
```python
from consent.api import EscalateRequest, EscalateResponse

# Escalate sensitive operation
escalate_request = EscalateRequest(
    user_id="user_123",
    operation="access_sensitive_data",
    data_category="sensitive",
    reason="compliance_requirement"
)

escalate_response = EscalateResponse(
    escalation_id="esc_123",
    level="HIGH",
    requires_approval=True,
    approval_url="/approve/esc_123"
)
```

**Ledger Query API**:
```python
from consent.api import LedgerResponse

# Query consent ledger
ledger = LedgerResponse(
    user_id="user_123",
    entries=[
        {
            "entry_id": "ledger_xyz789",
            "action": "grant",
            "purpose": "personalization",
            "timestamp": 1696320000
        }
    ],
    total_count=15
)
```

**Consent Stats API**:
```python
from consent.api import ConsentStatsResponse

# Get consent statistics
stats = ConsentStatsResponse(
    total_grants=1500,
    total_revokes=50,
    active_tokens=1200,
    expired_tokens=250,
    by_purpose={
        "personalization": 800,
        "analytics": 400,
        "marketing": 300
    }
)
```

**Client Context Helpers**:
```python
from consent.api import get_client_ip, get_client_context

# Get client IP for audit
ip_address = get_client_ip(request)

# Get full client context
context = get_client_context(request)
# Returns: {
#   "ip": "192.168.1.1",
#   "user_agent": "Mozilla/5.0...",
#   "timestamp": 1696320000
# }
```

---

## ConsentLedgerEntry

**Immutable Audit Trail**:
```python
from consent.service import ConsentLedgerEntry

entry = ConsentLedgerEntry(
    entry_id="ledger_xyz789",
    user_id="user_123",
    action="grant",  # or "revoke"
    purpose=Purpose.PERSONALIZATION,
    data_category=DataCategory.PERSONAL,
    scopes=["email", "preferences"],
    capability_token="cap_abc123",
    timestamp=1696320000,
    client_context={"ip": "192.168.1.1"}
)

# Ledger entries are immutable and cryptographically signed
# Retention: 7 years (GDPR compliance)
```

---

## Validation Functions

**Scope Validation**:
```python
from consent.service import validate_scopes

# Validate scope format
valid = validate_scopes(["email", "preferences"])
# Returns: True if valid, raises ValueError if invalid
```

**TTL Validation**:
```python
from consent.service import validate_ttl

# Validate time-to-live
validate_ttl(86400)  # 24 hours - OK
validate_ttl(31536000)  # 1 year - raises ValueError (max 30 days)
```

---

## OpenTelemetry Spans

**Required Span**: `lukhas.consent.operation`

```python
from telemetry import create_tracer

tracer = create_tracer("lukhas.consent")

# Grant consent with tracing
with tracer.start_span("consent.grant"):
    response = service.grant_consent(request)

# Verify token with tracing
with tracer.start_span("consent.verify"):
    valid = service.verify_token(verify_request)

# Revoke consent with tracing
with tracer.start_span("consent.revoke"):
    service.revoke_consent(revoke_request)
```

---

## Performance Targets

- **Grant consent**: <50ms
- **Verify token**: <10ms
- **Revoke consent**: <50ms
- **Ledger query**: <100ms
- **Escalation**: <200ms
- **Stats aggregation**: <500ms

---

## Configuration

**No configuration files** - consent service operates with programmatic configuration for maximum flexibility and security.

---

## Common Use Cases

### 1. GDPR-Compliant Data Access
```python
from consent.service import ConsentService, Purpose, DataCategory
from consent.api import GrantConsentRequest, VerifyTokenRequest

service = ConsentService()

# User grants consent for personalization
grant_request = GrantConsentRequest(
    user_id="user_123",
    purpose=Purpose.PERSONALIZATION,
    data_category=DataCategory.PERSONAL,
    scopes=["email", "name", "preferences"],
    ttl=86400
)
grant_response = service.grant_consent(grant_request)

# Before accessing data, verify token
verify_request = VerifyTokenRequest(token=grant_response.capability_token)
verify_response = service.verify_token(verify_request)

if verify_response.valid and "email" in verify_response.scopes:
    # Access email data
    user_email = get_user_email(user_id)
else:
    raise PermissionError("No consent for email access")
```

### 2. Sensitive Data Escalation
```python
from consent.api import EscalateRequest
from consent.service import EscalationLevel, DataCategory

# Accessing sensitive data requires escalation
escalate_request = EscalateRequest(
    user_id="user_123",
    operation="access_health_data",
    data_category=DataCategory.SENSITIVE,
    reason="treatment_recommendation"
)

escalate_response = service.escalate(escalate_request)

if escalate_response.level == EscalationLevel.CRITICAL:
    # Redirect user to approval flow
    redirect_to(escalate_response.approval_url)
```

### 3. Consent Revocation with Audit Trail
```python
from consent.api import RevokeConsentRequest

# User revokes consent
revoke_request = RevokeConsentRequest(
    user_id="user_123",
    capability_token="cap_abc123",
    reason="user_request"
)

revoke_response = service.revoke_consent(revoke_request)

# Ledger automatically records revocation
# All access attempts with revoked token will fail
# Audit trail preserved for 7 years
```

### 4. Purpose-Based Access Control
```python
from consent.service import Purpose

# Different purposes require different consents
personalization_token = service.grant_consent(
    user_id="user_123",
    purpose=Purpose.PERSONALIZATION,
    scopes=["email", "preferences"]
)

analytics_token = service.grant_consent(
    user_id="user_123",
    purpose=Purpose.ANALYTICS,
    scopes=["session_data", "interaction_logs"]
)

# Token for personalization cannot be used for analytics
verify_analytics = service.verify_token(personalization_token)
# Returns: valid=False (wrong purpose)
```

---

## Compliance Features

### GDPR Compliance
- ✅ Explicit user consent required
- ✅ Purpose limitation enforced
- ✅ Data minimization (scope-based)
- ✅ Right to revoke (instant)
- ✅ 7-year audit trail
- ✅ Granular data categories

### CCPA Compliance
- ✅ Opt-out mechanism (revoke)
- ✅ Data usage transparency
- ✅ Access control logs
- ✅ Deletion support
- ✅ Third-party disclosure tracking

### SOC2 Compliance
- ✅ Access controls
- ✅ Audit trails
- ✅ Encryption at rest/transit
- ✅ Token expiration
- ✅ Escalation procedures

---

## T4/0.01% Quality Standards

- ✅ **Component Count**: 22 components (10 API + 10 service + 2 helpers)
- ✅ **Test Coverage**: 85%
- ✅ **Compliance**: GDPR/CCPA/SOC2
- ✅ **Performance**: All operations <500ms
- ✅ **Audit Trail**: 7-year retention with cryptographic integrity
- ✅ **Security**: Capability tokens with TTL, purpose validation, scope enforcement

---

## Module Metadata

- **Lane**: L2 Integration
- **Schema Version**: 3.0.0
- **Dependencies**: None (foundational)
- **Entrypoints**: 20 (10 API + 10 service)
- **Python Files**: 2 (service.py, api.py)
- **Components**: 22 total
- **OpenTelemetry**: 1.37.0 semantic conventions
- **Test Coverage**: 85%
- **T4 Compliance**: 0.65 (experimental)

---

## Constellation Framework Integration

**Tags**: consent, governance, privacy, compliance

**Integration Points**:
- 🛡️ **GUARDIAN**: Privacy protection and safety
- ⚖️ **ETHICS**: Ethical data usage
- ⚛️ **IDENTITY**: User identity and consent linkage
- 🔬 **VISION**: Compliance monitoring and analysis

---

## Related Modules

- **governance**: Governance framework integration
- **audit**: Audit trail integration
- **policies**: Policy enforcement
- **identity**: Identity management
- **security**: Security and encryption

---

**Documentation Status**: ✅ Complete
**Last Updated**: 2025-10-18
**Maintainer**: LUKHAS Governance Team


## 🚀 GA Deployment Status

**Current Status**: 66.7% Ready (6/9 tasks complete)

### Recent Milestones
- ✅ **RC Soak Testing**: 60-hour stability validation (99.985% success rate)
- ✅ **Dependency Audit**: 196 packages, 0 CVEs
- ✅ **OpenAI Façade**: Full SDK compatibility validated
- ✅ **Guardian MCP**: Production-ready deployment
- ✅ **OpenAPI Schema**: Validated and documented

### New Documentation
- docs/GA_DEPLOYMENT_RUNBOOK.md - Comprehensive GA deployment procedures
- docs/DEPENDENCY_AUDIT.md - 196 packages, 0 CVEs, 100% license compliance
- docs/RC_SOAK_TEST_RESULTS.md - 60-hour stability validation (99.985% success)

### Recent Updates
- E402 linting cleanup - 86/1,226 violations fixed (batches 1-8)
- OpenAI façade validation - Full SDK compatibility
- Guardian MCP server deployment - Production ready
- Shadow diff harness - Pre-audit validation framework
- MATRIZ evaluation harness - Comprehensive testing

**Reference**: See [GA_DEPLOYMENT_RUNBOOK.md](./docs/GA_DEPLOYMENT_RUNBOOK.md) for deployment procedures.

---
