# LUKHAS IDENTITY PRODUCTION READINESS - MEGA PROMPT
# Complete Implementation Guide for AI Agents

**Version**: 1.0
**Last Updated**: 2025-11-14
**Worktree**: `/Users/agi_dev/LOCAL-REPOS/Lukhas-identity-production`
**Branch**: `feat/identity-production-readiness`
**Source**: `docs/gonzo/Lukhas_ID system improvement plan.md`

---

## ⚠️ CRITICAL SAFEGUARDS - READ FIRST

### Mandatory Constraints

1. **Worktree Isolation**: ALL work MUST be done in `/Users/agi_dev/LOCAL-REPOS/Lukhas-identity-production`
   - Never modify files in main `/Users/agi_dev/LOCAL-REPOS/Lukhas` directory
   - Verify working directory before ANY file operations

2. **Lane Boundaries**: Respect LUKHAS lane architecture
   - `core/` can import from `matriz/`, `universal_language/`
   - NO imports from `candidate/` in production code
   - Validate with `make lane-guard` before committing

3. **Test-First Development**:
   - Write tests BEFORE implementation
   - Minimum 75% coverage for new code
   - All tests must pass before committing

4. **Commit Standards (T4)**:
   - Format: `<type>(scope): <imperative subject ≤72>`
   - Types: feat|fix|docs|test|refactor|perf|security
   - Scope: identity (always for this project)
   - Include Problem/Solution/Impact in body
   - Append Claude Code attribution

5. **Security Requirements**:
   - NO hardcoded secrets or credentials
   - NO PII in logs or error messages
   - Encrypt sensitive data at rest (AES-GCM-256)
   - Follow principle of least privilege

6. **Documentation Requirements**:
   - Update docs/ for each major feature
   - Include API examples and error handling
   - Add troubleshooting sections

---

## 📊 PROJECT STATUS

### Completed Tasks ✅

- **Task 41**: Production Storage Layer (Redis + Postgres)
  - Files: `core/identity/storage/redis_token_store.py`, `webauthn_store.py`
  - Tests: `tests/identity/storage/test_*.py`
  - Docs: `docs/identity/DEPLOYMENT_STORAGE.md`

- **Task 42**: Asymmetric Key Management + JWKS
  - Files: `core/identity/keys.py`, `jwks_endpoint.py`
  - Tests: `tests/identity/crypto/test_*.py`
  - Docs: `docs/identity/JWKS_AND_KEY_ROTATION.md`

### Foundation Available ✅

- Redis token store with RFC 7662 introspection
- Encrypted Postgres credential store
- RS256/ES256 key management
- JWKS endpoint (RFC 7517)
- Comprehensive test infrastructure

---

## 🎯 REMAINING TASKS (15 Tasks)

### Priority 0 (P0) - CRITICAL - Must Complete First

#### Task 43: OAuth2 Token Introspection & Revocation
**Assignee**: api-bridge-specialist
**Complexity**: LOW-MEDIUM
**Estimated Time**: 3-5 hours
**Dependencies**: Task 41 (Redis store) - COMPLETED ✅

**Objective**: Implement RFC 7662 token introspection and RFC 7009 revocation endpoints.

**Deliverables**:
```
core/identity/introspection.py
core/identity/revocation.py
tests/identity/test_introspection.py
tests/identity/test_revocation.py
docs/identity/INTROSPECTION_AND_REVOCATION.md
```

**Implementation Requirements**:

1. **Introspection Endpoint** (`/oauth2/introspect`):
```python
from fastapi import APIRouter, Depends, HTTPException
from core.identity.storage import RedisTokenStore

router = APIRouter(prefix="/oauth2", tags=["oauth2"])

@router.post("/introspect")
async def introspect_token(
    token: str,
    token_type_hint: Optional[str] = None,
    client_id: Optional[str] = None,
    store: RedisTokenStore = Depends(get_token_store)
):
    """RFC 7662 token introspection.

    Returns:
        {
            "active": true,
            "sub": "usr_alice",
            "scope": "openid profile",
            "exp": 1699999999,
            "iat": 1699999999,
            "iss": "https://ai",
            "token_type": "Bearer"
        }
    """
    # Extract JTI from JWT
    jti = extract_jti_from_token(token)

    # Introspect via Redis store
    result = await store.introspect_token(jti)

    return result
```

2. **Revocation Endpoint** (`/oauth2/revoke`):
```python
@router.post("/revoke")
async def revoke_token(
    token: str,
    token_type_hint: Optional[str] = None,
    client_id: Optional[str] = None,
    store: RedisTokenStore = Depends(get_token_store)
):
    """RFC 7009 token revocation.

    Returns: 200 OK (always, even if token doesn't exist)
    """
    jti = extract_jti_from_token(token)
    await store.revoke_token(jti, reason="client_revocation")
    return {"status": "revoked"}
```

**Acceptance Criteria**:
- [ ] POST `/oauth2/introspect` returns RFC 7662 compliant response
- [ ] Active tokens return `active: true` with metadata
- [ ] Revoked tokens return `active: false` only
- [ ] POST `/oauth2/revoke` immediately invalidates tokens (<10ms)
- [ ] Revocation is idempotent (revoking twice succeeds)
- [ ] Client authentication required for both endpoints
- [ ] Tests cover: active tokens, revoked tokens, expired tokens, invalid tokens
- [ ] Integration tests with RedisTokenStore

**References**:
- RFC 7662: https://datatracker.ietf.org/doc/html/rfc7662
- RFC 7009: https://datatracker.ietf.org/doc/html/rfc7009
- Existing: `core/identity/storage/redis_token_store.py`

---

#### Task 44: Production WebAuthn with python-fido2
**Assignee**: identity-auth-specialist
**Complexity**: HIGH
**Estimated Time**: 6-12 hours
**Dependencies**: Task 41 (WebAuthn store) - COMPLETED ✅

**Objective**: Replace in-memory WebAuthn manager with production-grade python-fido2 integration.

**Deliverables**:
```
core/identity/webauthn.py (refactored from labs/)
tests/identity/test_webauthn_flows.py
docs/identity/WEBAUTHN_PRODUCTION.md
```

**Implementation Requirements**:

1. **Install python-fido2**:
```bash
pip install fido2==1.1.3
```

2. **WebAuthn Manager Refactor**:
```python
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, AttestationConveyancePreference
from core.identity.storage import WebAuthnStore

class ProductionWebAuthnManager:
    """Production WebAuthn manager using python-fido2."""

    def __init__(self, store: WebAuthnStore, rp_id: str = "ai"):
        self.store = store
        self.rp = PublicKeyCredentialRpEntity(id=rp_id, name="LUKHAS AI")
        self.server = Fido2Server(self.rp)

    async def begin_registration(
        self,
        user_id: str,
        username: str,
        display_name: str
    ) -> dict:
        """Start WebAuthn registration ceremony.

        Returns:
            {
                "publicKey": {
                    "challenge": "...",
                    "rp": {"id": "ai", "name": "LUKHAS AI"},
                    "user": {"id": "...", "name": "alice", "displayName": "Alice"},
                    "pubKeyCredParams": [...],
                    "timeout": 60000,
                    "attestation": "direct"
                }
            }
        """
        # Get existing credentials to exclude
        existing_creds = await self.store.get_credentials_for_user(user_id)
        exclude_credentials = [
            {"type": "public-key", "id": base64.b64decode(c.id)}
            for c in existing_creds
        ]

        # Generate registration options
        options, state = self.server.register_begin(
            user={"id": user_id.encode(), "name": username, "displayName": display_name},
            credentials=exclude_credentials,
            user_verification="preferred",
            attestation=AttestationConveyancePreference.DIRECT
        )

        # Store challenge state (Redis, 5-minute TTL)
        await self._store_challenge_state(user_id, state)

        return options

    async def complete_registration(
        self,
        user_id: str,
        credential_data: dict,
        client_data: dict
    ) -> str:
        """Complete WebAuthn registration.

        Returns:
            credential_id: Unique credential identifier
        """
        # Retrieve challenge state
        state = await self._get_challenge_state(user_id)

        # Verify attestation
        auth_data = self.server.register_complete(
            state,
            client_data,
            credential_data
        )

        # Extract credential details
        credential_id = base64url_encode(auth_data.credential_data.credential_id)
        public_key = auth_data.credential_data.public_key
        aaguid = auth_data.credential_data.aaguid

        # Store encrypted credential
        await self.store.store_credential(
            credential_id=credential_id,
            lid=user_id,
            public_key=public_key,
            aaguid=aaguid,
            attestation_format=auth_data.fmt,
            user_verified=auth_data.flags.user_verified
        )

        return credential_id

    async def begin_authentication(
        self,
        user_id: Optional[str] = None
    ) -> dict:
        """Start WebAuthn authentication ceremony.

        Returns:
            {
                "publicKey": {
                    "challenge": "...",
                    "rpId": "ai",
                    "allowCredentials": [...],
                    "timeout": 60000,
                    "userVerification": "preferred"
                }
            }
        """
        # Get user's credentials
        credentials = []
        if user_id:
            creds = await self.store.get_credentials_for_user(user_id)
            credentials = [
                {"type": "public-key", "id": base64.b64decode(c.id)}
                for c in creds
            ]

        # Generate authentication options
        options, state = self.server.authenticate_begin(
            credentials=credentials,
            user_verification="preferred"
        )

        # Store challenge state
        challenge_id = generate_challenge_id()
        await self._store_auth_state(challenge_id, state)

        return {**options, "challenge_id": challenge_id}

    async def complete_authentication(
        self,
        challenge_id: str,
        credential_id: str,
        client_data: dict,
        authenticator_data: dict,
        signature: bytes
    ) -> str:
        """Complete WebAuthn authentication.

        Returns:
            user_id: Authenticated user's ΛID

        Raises:
            ValueError: If signature counter regression detected (cloned authenticator)
        """
        # Retrieve challenge state
        state = await self._get_auth_state(challenge_id)

        # Get credential from store
        cred = await self.store.get_credential(credential_id)
        if not cred:
            raise ValueError(f"Unknown credential: {credential_id}")

        # Verify assertion
        credential = AttestedCredentialData(cred.public_key)
        auth_data = self.server.authenticate_complete(
            state,
            credentials=[credential],
            credential_id=base64.b64decode(credential_id),
            client_data=client_data,
            auth_data=authenticator_data,
            signature=signature
        )

        # Update signature counter (enforce monotonic increase)
        new_count = auth_data.counter
        old_count = await self.store.update_sign_count(credential_id, new_count)

        # If update_sign_count raises ValueError, propagate it (counter regression)

        return cred.lid
```

**Acceptance Criteria**:
- [ ] Registration ceremony creates encrypted credentials in Postgres
- [ ] Authentication ceremony verifies signatures correctly
- [ ] Attestation verification works (reject invalid attestations)
- [ ] Signature counters enforced (raise error on regression)
- [ ] Rate limiting on authentication attempts (5/minute per user)
- [ ] Challenge state stored in Redis with 5-minute TTL
- [ ] Tests use fido2 test helpers for realistic flows
- [ ] Integration tests with WebAuthnStore
- [ ] Documentation includes client-side JavaScript examples

**References**:
- python-fido2 docs: https://github.com/Yubico/python-fido2
- WebAuthn spec: https://www.w3.org/TR/webauthn-2/
- Existing: `core/identity/storage/webauthn_store.py`
- Existing prototype: `labs/governance/identity/core/auth/webauthn_manager.py`

---

### Priority 1 (P1) - HIGH PRIORITY - Essential for Production

#### Task 45: Consent Proof Store (GDPR-Safe)
**Assignee**: security-governance-specialist
**Complexity**: LOW
**Estimated Time**: 3-4 hours
**Dependencies**: None

**Objective**: Implement GDPR-compliant consent tracking using HMAC proofs (no raw TC strings).

**Deliverables**:
```
core/identity/consent.py
tests/identity/test_consent_store.py
docs/identity/CONSENT_PROCESS.md
docs/identity/DPIA_TEMPLATE.md (stub)
```

**Implementation Requirements**:

1. **Consent Proof Store**:
```python
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

class ConsentProof(BaseModel):
    """GDPR-safe consent proof (no raw TC strings)."""

    consent_id: str  # Unique identifier
    lid: str  # User ΛID
    proof_hash: str  # HMAC-SHA256 of TC string
    scope: str  # "personalization", "analytics", "marketing"
    granted_at: datetime
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str]  # For audit
    user_agent: Optional[str]

class ConsentStore:
    """GDPR-compliant consent management (HMAC proofs only)."""

    def __init__(self, salt: str, db_url: str):
        self.salt = salt.encode()
        # Use Postgres for durable consent records
        self.engine = create_engine(db_url)

    def _compute_proof(self, tc_string: str) -> str:
        """Compute HMAC proof of TC string (never store raw TC)."""
        return hmac.new(
            self.salt,
            tc_string.encode(),
            hashlib.sha256
        ).hexdigest()

    async def grant_consent(
        self,
        lid: str,
        tc_string: str,
        scope: str,
        ttl_days: int = 365,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Record consent grant (stores proof only).

        Returns:
            consent_id: Unique consent identifier
        """
        consent_id = f"consent_{uuid4().hex[:16]}"
        proof_hash = self._compute_proof(tc_string)

        consent = ConsentProof(
            consent_id=consent_id,
            lid=lid,
            proof_hash=proof_hash,
            scope=scope,
            granted_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=ttl_days),
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Store in database
        await self._save_consent(consent)

        return consent_id

    async def verify_consent(
        self,
        lid: str,
        tc_string: str,
        scope: str
    ) -> bool:
        """Verify if user has valid consent for scope.

        Returns:
            True if valid consent exists
        """
        proof_hash = self._compute_proof(tc_string)

        # Query database for matching proof
        consent = await self._get_consent_by_proof(lid, proof_hash, scope)

        if not consent:
            return False

        # Check not revoked
        if consent.revoked_at:
            return False

        # Check not expired
        if consent.expires_at and consent.expires_at < datetime.utcnow():
            return False

        return True

    async def revoke_consent(
        self,
        lid: str,
        scope: str,
        reason: str = "user_request"
    ) -> int:
        """Revoke all consents for user and scope.

        Returns:
            Number of consents revoked
        """
        # Update all matching consents
        count = await self._revoke_consents(lid, scope, reason)

        # Invalidate any personalization tokens
        # (integration with token revocation)

        return count

    async def rotate_salt(self, new_salt: str):
        """Rotate HMAC salt (requires re-consent from users).

        WARNING: This invalidates all existing consent proofs!
        """
        # This is a breaking operation
        # Document salt rotation procedure
        pass
```

**Acceptance Criteria**:
- [ ] NO raw TC strings stored anywhere
- [ ] HMAC proofs verifiable with same TC string
- [ ] TTL auto-expires consent after configured period
- [ ] Revocation immediately invalidates consent
- [ ] Audit trail includes IP and User-Agent
- [ ] Salt rotation helper provided (with warnings)
- [ ] DPIA template stub created for legal review
- [ ] Tests cover: grant, verify, revoke, expiry, salt rotation

**References**:
- GDPR Article 7: https://gdpr-info.eu/art-7-gdpr/
- IAB TCF v2: https://iabeurope.eu/tcf-2-0/

---

#### Task 46: OPA/ABAS Identity Middleware
**Assignee**: security-governance-specialist
**Complexity**: MEDIUM
**Estimated Time**: 3-5 hours
**Dependencies**: Existing OPA policies in `policies/matrix/identity.rego`

**Objective**: Integrate OPA policy enforcement for identity routes via ABAS middleware.

**Deliverables**:
```
core/identity/middleware/abas_identity.py
tests/identity/test_abas_middleware.py
policies/matrix/identity.rego (updates)
```

**Implementation Requirements**:

1. **ABAS Identity Middleware**:
```python
from fastapi import Request, HTTPException
from typing import Callable
import httpx

class ABASIdentityMiddleware:
    """ABAS (Attribute-Based Access System) middleware for identity routes."""

    def __init__(self, opa_url: str = "http://localhost:8181", cache_ttl: int = 300):
        self.opa_url = opa_url
        self.cache_ttl = cache_ttl
        self.cache = {}  # Simple in-memory cache (use Redis in production)

    async def __call__(self, request: Request, call_next: Callable):
        # Extract policy input
        input_data = {
            "path": request.url.path,
            "method": request.method,
            "user": await self._extract_user_context(request),
            "trinity": await self._get_trinity_status(),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Query OPA policy
        decision = await self._query_opa(input_data)

        if decision["result"]["allow"]:
            # Check for step-up requirement
            if decision["result"].get("step_up"):
                raise HTTPException(
                    status_code=428,
                    detail={
                        "error": "step_up_required",
                        "reason": decision["result"]["reason"]
                    }
                )

            # Allowed - proceed
            response = await call_next(request)
            return response

        else:
            # Denied
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden",
                    "reason": decision["result"]["reason"],
                    "policy": "identity.rego"
                }
            )

    async def _query_opa(self, input_data: dict) -> dict:
        """Query OPA policy decision point."""
        # Check cache first
        cache_key = self._make_cache_key(input_data)
        if cache_key in self.cache:
            cached_decision, cached_at = self.cache[cache_key]
            if (datetime.utcnow() - cached_at).seconds < self.cache_ttl:
                return cached_decision

        # Query OPA
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.opa_url}/v1/data/lukhas/identity/authorize",
                json={"input": input_data},
                timeout=0.5  # Fast timeout for PDP queries
            )

        decision = response.json()

        # Cache allow decisions only (deny decisions not cached for security)
        if decision["result"]["allow"]:
            self.cache[cache_key] = (decision, datetime.utcnow())

        return decision
```

2. **Update `policies/matrix/identity.rego`**:
```rego
package lukhas.identity

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Allow if Trinity modules are operational
allow if {
    input.trinity.identity == "on"
    input.trinity.guardian == "on"
    not requires_step_up
}

# Step-up authentication required for sensitive operations
requires_step_up if {
    input.path == "/identity/credentials/delete"
    input.user.auth_age_seconds > 300  # Re-auth required after 5 minutes
}

# Reason codes
reason = "trinity_module_offline" if {
    input.trinity.identity == "off"
}

reason = "guardian_disabled" if {
    input.trinity.guardian == "off"
}

reason = "step_up_required" if {
    requires_step_up
}
```

**Acceptance Criteria**:
- [ ] Middleware enforces allow/deny/step_up decisions
- [ ] Deny returns 403 with reason code
- [ ] Step-up returns 428 (Precondition Required)
- [ ] Allow decisions cached for TTL (300s default)
- [ ] PDP query timeout <500ms
- [ ] Tests with mocked OPA (no actual OPA server needed)
- [ ] Integration tests with real OPA policy
- [ ] Documentation includes policy debugging guide

**References**:
- OPA docs: https://www.openpolicyagent.org/docs/latest/
- Existing: `policies/matrix/identity.rego`

---

#### Task 47: Observability - Prometheus Metrics & Tracing
**Assignee**: observability-testing-specialist
**Complexity**: LOW-MEDIUM
**Estimated Time**: 2-4 hours
**Dependencies**: None

**Objective**: Add Prometheus instrumentation for identity system monitoring.

**Deliverables**:
```
core/identity/observability.py
grafana/dashboards/identity_dashboard.json
tests/identity/test_metrics.py
```

**Implementation Requirements**:

1. **Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import APIRouter

# Metrics
identity_auth_latency = Histogram(
    "identity_auth_latency_seconds",
    "Authentication latency",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

identity_lid_generation_total = Counter(
    "identity_lid_generation_total",
    "ΛID generation count",
    ["lid_type"]  # USR, AGT, SVC, SYS
)

identity_webauthn_registration_total = Counter(
    "identity_webauthn_registration_total",
    "WebAuthn registration count",
    ["result"]  # success, failure, attestation_failed
)

identity_token_issuance_total = Counter(
    "identity_oidc_token_issuance_total",
    "OIDC token issuance count"
)

identity_active_keys = Gauge(
    "identity_active_signing_keys",
    "Number of active signing keys"
)

identity_abas_pdp_latency = Histogram(
    "identity_abas_pdp_latency_seconds",
    "OPA policy decision latency",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
)

# Metrics endpoint
router = APIRouter(tags=["metrics"])

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")
```

2. **Instrumentation Examples**:
```python
# WebAuthn registration
@identity_auth_latency.time()
async def complete_registration(...):
    try:
        credential_id = await manager.complete_registration(...)
        identity_webauthn_registration_total.labels(result="success").inc()
        return credential_id
    except Exception as e:
        identity_webauthn_registration_total.labels(result="failure").inc()
        raise

# ΛID generation
def generate_lid(lid_type: str) -> str:
    lid = _generate(lid_type)
    identity_lid_generation_total.labels(lid_type=lid_type).inc()
    return lid
```

3. **X-Trace-Id Propagation**:
```python
from uuid import uuid4
from fastapi import Request

async def trace_id_middleware(request: Request, call_next):
    """Inject trace ID into requests for distributed tracing."""
    trace_id = request.headers.get("X-Trace-Id") or f"trace-{uuid4().hex[:16]}"
    request.state.trace_id = trace_id

    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id

    return response
```

**Acceptance Criteria**:
- [ ] `/metrics` endpoint returns Prometheus format
- [ ] All critical operations instrumented (auth, token issuance, etc.)
- [ ] Latency histograms track p95 targets (<100ms for auth)
- [ ] Counters track success/failure rates
- [ ] X-Trace-Id propagated through request chain
- [ ] Grafana dashboard JSON includes panels for all metrics
- [ ] Tests verify metrics increment correctly

**References**:
- Prometheus Python client: https://github.com/prometheus/client_python
- Grafana docs: https://grafana.com/docs/

---

#### Task 48: Canonical ΛID Model + Namespace Rules
**Assignee**: identity-auth-specialist
**Complexity**: LOW
**Estimated Time**: 2-3 hours
**Dependencies**: None

**Objective**: Centralize ΛID generation, validation, and namespace collision detection.

**Deliverables**:
```
core/identity/lid.py
tests/identity/test_lid_format.py
```

**Implementation Requirements**:

1. **ΛID Module**:
```python
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator

class LIDType(str, Enum):
    """ΛID namespace types."""
    USER = "USR"
    AGENT = "AGT"
    SERVICE = "SVC"
    SYSTEM = "SYS"

class LIDFormat(BaseModel):
    """ΛID format specification."""

    type: LIDType
    identifier: str
    checksum: Optional[str] = None
    metadata: Optional[dict] = None

    @validator("identifier")
    def validate_identifier(cls, v):
        """Ensure identifier is alphanumeric."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Identifier must be alphanumeric with _ or -")
        return v

    def to_string(self) -> str:
        """Format as ΛID string: {type}_{identifier}"""
        return f"{self.type.value}_{self.identifier}"

class LIDGenerator:
    """Canonical ΛID generator with namespace collision detection."""

    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.issued_lids = set()  # In-memory collision detection

    def generate(
        self,
        lid_type: LIDType,
        seed: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Generate ΛID with checksum.

        Args:
            lid_type: Namespace type
            seed: Optional seed for deterministic generation
            metadata: Optional metadata (not included in ΛID string)

        Returns:
            ΛID string (e.g., "USR_alice_a1b2c3")
        """
        # Generate identifier
        if seed:
            # Deterministic generation
            identifier = self._hash_seed(seed)
        else:
            # Random generation
            identifier = self._generate_random()

        # Add checksum
        checksum = self._compute_checksum(lid_type, identifier)

        # Format ΛID
        lid_str = f"{lid_type.value}_{identifier}_{checksum}"

        # Check for collisions
        if lid_str in self.issued_lids:
            raise ValueError(f"ΛID collision detected: {lid_str}")

        self.issued_lids.add(lid_str)

        return lid_str

    def parse(self, lid_str: str) -> LIDFormat:
        """Parse ΛID string into components.

        Raises:
            ValueError: If format is invalid
        """
        parts = lid_str.split("_")
        if len(parts) < 2:
            raise ValueError(f"Invalid ΛID format: {lid_str}")

        lid_type_str = parts[0]
        identifier = parts[1]
        checksum = parts[2] if len(parts) > 2 else None

        # Validate type
        try:
            lid_type = LIDType(lid_type_str)
        except ValueError:
            raise ValueError(f"Unknown ΛID type: {lid_type_str}")

        return LIDFormat(
            type=lid_type,
            identifier=identifier,
            checksum=checksum
        )

    def validate(self, lid_str: str) -> bool:
        """Validate ΛID format and checksum.

        Returns:
            True if valid
        """
        try:
            lid = self.parse(lid_str)

            # Verify checksum if present
            if lid.checksum:
                expected_checksum = self._compute_checksum(lid.type, lid.identifier)
                if lid.checksum != expected_checksum:
                    return False

            return True

        except ValueError:
            return False

    def _compute_checksum(self, lid_type: LIDType, identifier: str) -> str:
        """Compute BLAKE2b checksum."""
        import hashlib
        data = f"{lid_type.value}{identifier}".encode()
        return hashlib.blake2b(data, digest_size=4).hexdigest()[:6]

    def _hash_seed(self, seed: str) -> str:
        """Hash seed to identifier."""
        import hashlib
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def _generate_random(self) -> str:
        """Generate random identifier."""
        import secrets
        return secrets.token_urlsafe(12)[:16]
```

**Acceptance Criteria**:
- [ ] Generate ΛIDs for all namespace types (USR/AGT/SVC/SYS)
- [ ] Deterministic generation with same seed
- [ ] Collision detection raises ValueError
- [ ] Parse ΛID strings back to components
- [ ] Validate checksums correctly
- [ ] Cross-tenant collision detection (if tenant_id provided)
- [ ] Tests cover: generation, parsing, validation, collisions

---

#### Task 49: Agent/Service/System Identity Integration
**Assignee**: api-bridge-specialist
**Complexity**: MEDIUM
**Estimated Time**: 4-6 hours
**Dependencies**: Task 48 (ΛID model)

**Objective**: Extend identity system to support AGT/SVC/SYS identities with appropriate authentication.

**Deliverables**:
```
agents/middleware/identity.py
services/auth/service_tokens.py
systems/auth/system_keys.py
tests/identity/test_multi_actor.py
```

**Implementation Requirements**:

1. **Agent Identity Middleware**:
```python
from fastapi import Request, HTTPException, Depends
from core.identity.lid import LIDGenerator, LIDType

async def require_agent_identity(request: Request) -> str:
    """Require AGT ΛID in request.

    Returns:
        Agent ΛID

    Raises:
        HTTPException: If not an agent or invalid credentials
    """
    # Extract token from Authorization header
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    # Decode JWT
    payload = decode_jwt(token)

    # Validate ΛID is AGT type
    lid = payload.get("sub")
    lid_gen = LIDGenerator()
    parsed = lid_gen.parse(lid)

    if parsed.type != LIDType.AGENT:
        raise HTTPException(403, detail="Agent identity required")

    # Validate role claims
    roles = payload.get("roles", [])
    if "agent" not in roles:
        raise HTTPException(403, detail="Agent role required")

    return lid

# Use in routes
@router.post("/agent-only-endpoint")
async def agent_endpoint(agent_lid: str = Depends(require_agent_identity)):
    return {"message": f"Hello, {agent_lid}"}
```

2. **Service Token Issuance** (mTLS/DPoP):
```python
class ServiceTokenIssuer:
    """Issue tokens for SVC identities using mTLS or DPoP."""

    async def issue_service_token(
        self,
        service_id: str,
        client_cert: Optional[str] = None,
        dpop_proof: Optional[str] = None
    ) -> str:
        """Issue service token.

        Args:
            service_id: SVC ΛID
            client_cert: mTLS client certificate
            dpop_proof: DPoP proof JWT

        Returns:
            Service access token (JWT)
        """
        # Verify either mTLS or DPoP
        if client_cert:
            # Verify client certificate
            await self._verify_client_cert(client_cert, service_id)
        elif dpop_proof:
            # Verify DPoP proof
            await self._verify_dpop_proof(dpop_proof, service_id)
        else:
            raise ValueError("Either client_cert or dpop_proof required")

        # Issue token with SVC claims
        payload = {
            "sub": service_id,
            "iss": "https://ai",
            "aud": "lukhas_internal",
            "scope": "service",
            "lid_type": "SVC",
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp())
        }

        kid, private_key = key_manager.get_current_signing_key()
        token = jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": kid})

        return token
```

3. **System Key Rotation**:
```python
class SystemKeyManager:
    """Manage SYS identity keys with automatic rotation."""

    async def rotate_system_keys(self):
        """Rotate all system keys on schedule."""
        for system_id in self.registered_systems:
            new_key = await self._generate_system_key(system_id)
            await self._distribute_key(system_id, new_key)
            logger.info(f"Rotated key for {system_id}")
```

**Acceptance Criteria**:
- [ ] Agent middleware validates AGT ΛID + role claims
- [ ] Service tokens issued via mTLS or DPoP
- [ ] System keys rotate automatically (configurable schedule)
- [ ] All identity types (USR/AGT/SVC/SYS) supported in token claims
- [ ] Tests cover multi-actor scenarios

---

#### Task 50: Identity Event Bus + Audit Hooks
**Assignee**: observability-testing-specialist
**Complexity**: MEDIUM
**Estimated Time**: 3-5 hours
**Dependencies**: None

**Objective**: Implement event bus for identity events with Guardian/Drift integration hooks.

**Deliverables**:
```
core/identity/events.py
tests/identity/test_identity_events.py
```

**Implementation Requirements**:

1. **Identity Event Types**:
```python
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class IdentityEventType(str, Enum):
    REGISTERED = "identity.registered"
    AUTH_SUCCEEDED = "identity.auth.succeeded"
    AUTH_FAILED = "identity.auth.failed"
    TOKEN_REVOKED = "identity.token.revoked"
    CONSENT_REVOKED = "identity.consent.revoked"
    CREDENTIAL_ADDED = "identity.credential.added"
    CREDENTIAL_REMOVED = "identity.credential.removed"

class IdentityEvent(BaseModel):
    """Base identity event (privacy-safe)."""

    event_id: str
    event_type: IdentityEventType
    timestamp: datetime
    lid: str  # User ΛID (no PII)
    lid_type: str  # USR/AGT/SVC/SYS
    metadata: dict  # Event-specific metadata (NO PII!)
    trace_id: Optional[str]

class IdentityEventBus:
    """Pub/sub event bus for identity events."""

    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: IdentityEventType, handler: Callable):
        """Subscribe to identity events."""
        self.subscribers[event_type].append(handler)

    async def publish(self, event: IdentityEvent):
        """Publish identity event to subscribers."""
        # No PII validation
        self._validate_no_pii(event)

        # Publish to all subscribers
        for handler in self.subscribers[event.event_type]:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

    def _validate_no_pii(self, event: IdentityEvent):
        """Ensure no PII in event payload."""
        # Implement PII detection
        pass
```

2. **Guardian/Drift Hooks**:
```python
# Guardian drift hook example
async def guardian_drift_scorer(event: IdentityEvent):
    """Score identity event for drift detection."""
    if event.event_type == IdentityEventType.AUTH_FAILED:
        # Increment failed auth counter for user
        await drift_monitor.record_anomaly(
            lid=event.lid,
            anomaly_type="repeated_auth_failure",
            severity=0.3
        )

# Subscribe to events
event_bus.subscribe(IdentityEventType.AUTH_FAILED, guardian_drift_scorer)
```

**Acceptance Criteria**:
- [ ] Event types defined for all identity operations
- [ ] Pub/sub pattern allows multiple subscribers
- [ ] NO PII in event payloads (validation enforced)
- [ ] Guardian/Drift hooks can subscribe to events
- [ ] Async event handling (non-blocking)
- [ ] Tests verify event publishing and subscription

---

#### Task 51: OIDC Discovery + Public Documentation
**Assignee**: identity-auth-specialist
**Complexity**: LOW
**Estimated Time**: 2-3 hours
**Dependencies**: Task 42 (JWKS) - COMPLETED ✅

**Objective**: Complete OpenID Connect Discovery endpoint and public API documentation.

**Deliverables**:
```
core/identity/oidc_discovery.py (expand jwks_endpoint.py)
docs/identity/API.md
web/examples/next-auth-client.ts (optional)
```

**Implementation Requirements**:

1. **Complete `/.well-known/openid-configuration`**:
```python
@router.get("/.well-known/openid-configuration")
async def openid_configuration() -> Dict:
    """OpenID Connect Discovery (RFC 8414).

    Returns complete metadata about Lukhas Identity provider.
    """
    return {
        "issuer": "https://ai",
        "authorization_endpoint": "https://ai/oauth2/authorize",
        "token_endpoint": "https://ai/oauth2/token",
        "userinfo_endpoint": "https://ai/oauth2/userinfo",
        "jwks_uri": "https://ai/.well-known/jwks.json",
        "introspection_endpoint": "https://ai/oauth2/introspect",
        "revocation_endpoint": "https://ai/oauth2/revoke",
        "registration_endpoint": "https://ai/oauth2/register",

        # Supported features
        "response_types_supported": ["code", "token", "id_token", "code id_token"],
        "response_modes_supported": ["query", "fragment", "form_post"],
        "grant_types_supported": ["authorization_code", "implicit", "refresh_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256", "ES256"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
            "none"
        ],

        # Scopes and claims
        "scopes_supported": ["openid", "profile", "email", "offline_access"],
        "claims_supported": [
            "sub", "iss", "aud", "exp", "iat", "auth_time",
            "lid_type", "trinity", "consent_proof"
        ],

        # LUKHAS-specific
        "lid_namespaces_supported": ["USR", "AGT", "SVC", "SYS"],
        "trinity_modules": ["identity", "consciousness", "guardian"],
        "webauthn_registration_endpoint": "https://ai/webauthn/register",
        "webauthn_authentication_endpoint": "https://ai/webauthn/authenticate"
    }
```

2. **API Documentation** (`docs/identity/API.md`):
```markdown
# Lukhas Identity API Reference

## Authentication

### WebAuthn Registration
POST /webauthn/register/begin
POST /webauthn/register/complete

### WebAuthn Authentication
POST /webauthn/authenticate/begin
POST /webauthn/authenticate/complete

## OAuth2 / OIDC

### Authorization Code Flow
GET /oauth2/authorize
POST /oauth2/token

### Token Introspection
POST /oauth2/introspect

### Token Revocation
POST /oauth2/revoke

## Discovery

### OpenID Configuration
GET /.well-known/openid-configuration

### JWKS
GET /.well-known/jwks.json
```

**Acceptance Criteria**:
- [ ] Discovery endpoint returns complete RFC 8414 metadata
- [ ] All endpoints listed in discovery are implemented or stubbed
- [ ] API documentation includes request/response examples
- [ ] Optional: Next.js client example works against dev server

---

### Priority 2 (P2) - SECURITY & GOVERNANCE - Complete Last

#### Task 52: MATRIZ Readiness Suite
**Assignee**: observability-testing-specialist
**Complexity**: HIGH
**Estimated Time**: 8-12 hours
**Dependencies**: All P0/P1 tasks

**Objective**: Comprehensive performance, chaos, and privacy testing for MATRIZ certification.

**Deliverables**:
```
tests/matriz/identity/test_performance.py
tests/matriz/identity/test_chaos.py
tests/matriz/identity/test_privacy_invariants.py
.github/workflows/matriz_identity_readiness.yml
```

**Implementation Requirements**:

1. **Performance Tests** (p95 <100ms validation):
```python
import pytest
from locust import HttpUser, task, between

class IdentityLoadTest(HttpUser):
    wait_time = between(1, 2)

    @task
    def authenticate(self):
        """Simulate authentication flow."""
        self.client.post("/webauthn/authenticate/begin")
        # Measure p95 latency
```

2. **Chaos Tests** (PDP failure modes):
```python
async def test_opa_pdp_timeout():
    """Test ABAS middleware handles OPA timeout gracefully."""
    # Mock OPA to timeout
    with patch("httpx.AsyncClient.post", side_effect=asyncio.TimeoutError):
        # Should fail open or return cached decision
        response = await client.get("/protected-endpoint")
        assert response.status_code in [200, 503]
```

3. **Privacy Invariant Tests**:
```python
def test_no_pii_in_logs():
    """Grep logs for PII patterns (emails, names, etc.)."""
    log_file = "identity.log"
    patterns = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    ]

    with open(log_file) as f:
        for line in f:
            for pattern in patterns:
                assert not re.search(pattern, line), f"PII found in logs: {line}"
```

**Acceptance Criteria**:
- [ ] All performance tests pass (p95 <100ms)
- [ ] Chaos tests validate graceful degradation
- [ ] Privacy tests ensure no PII leakage
- [ ] CI workflow runs nightly
- [ ] JSON reports uploadable to MATRIZ dashboard

---

#### Task 53: Threat Model + DPIA + Red-Team Harness
**Assignee**: security-governance-specialist
**Complexity**: VERY HIGH
**Estimated Time**: 8-16 hours
**Dependencies**: All P0/P1 tasks

**Objective**: Complete security audit with threat modeling, DPIA, and red-team testing.

**Deliverables**:
```
docs/identity/THREAT_MODEL.md
docs/identity/DPIA.md
redteam/identity/test_token_replay.py
redteam/identity/test_csrf.py
redteam/identity/test_opa_dos.py
docs/identity/RISK_MATRIX.md
```

**Implementation Requirements**:

1. **Threat Model** (STRIDE/ATT&CK):
```markdown
# Threat Model: Lukhas Identity System

## Assets
- User credentials (WebAuthn private keys)
- Access tokens (JWT)
- Signing keys (RSA/ECDSA private keys)
- Consent proofs

## Threats

### Spoofing (S)
- **Threat**: Attacker impersonates user
- **Mitigation**: WebAuthn with attestation, signature counter enforcement

### Tampering (T)
- **Threat**: JWT payload modified
- **Mitigation**: Asymmetric signatures (RS256/ES256), JWKS verification

### Repudiation (R)
- **Threat**: User denies action
- **Mitigation**: Audit trail with IP/User-Agent, consent proofs

### Information Disclosure (I)
- **Threat**: PII leaked in logs/errors
- **Mitigation**: No PII in events, encrypted credentials at rest

### Denial of Service (D)
- **Threat**: OPA PDP overload
- **Mitigation**: Rate limiting, cache, circuit breaker

### Elevation of Privilege (E)
- **Threat**: Agent bypasses ABAS policy
- **Mitigation**: Middleware enforcement, no policy bypass
```

2. **DPIA Template**:
```markdown
# Data Protection Impact Assessment (DPIA)

## Processing Activity
Authentication and authorization for LUKHAS AI platform

## Data Categories
- ΛID (pseudonymous identifier)
- WebAuthn credentials (encrypted)
- Consent proofs (HMAC only, no raw TC strings)
- Audit logs (no PII)

## Legal Basis
- GDPR Article 6(1)(b) - Contract performance
- GDPR Article 9(2)(a) - Explicit consent (for special categories)

## Risks
1. **Risk**: Credential database breach
   - **Likelihood**: Low
   - **Impact**: High
   - **Mitigation**: AES-GCM encryption, KMS integration

## Recommendations
- [ ] Conduct annual security audit
- [ ] Implement right to erasure workflow
- [ ] Test consent revocation end-to-end
```

3. **Red-Team Harness**:
```python
# Test token replay attack
async def test_token_replay_attack():
    """Verify that revoked tokens cannot be replayed."""
    # Issue token
    token = await issue_token(user_id="usr_test")

    # Use token successfully
    response = await client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Revoke token
    await revoke_token(token)

    # Attempt replay
    response = await client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401, "Revoked token should not be accepted"

# Test CSRF protection
async def test_csrf_protection():
    """Verify CSRF tokens required for state-changing operations."""
    # Attempt registration without CSRF token
    response = await client.post("/webauthn/register", json={...})
    assert response.status_code == 403, "CSRF token required"
```

**Acceptance Criteria**:
- [ ] Threat model complete with STRIDE coverage
- [ ] DPIA ready for legal review
- [ ] Red-team harness finds at least 1 issue to fix
- [ ] Risk matrix documents all threats with mitigations

---

#### Task 54: Bridge Completion (Identity ↔ Core Sync)
**Assignee**: api-bridge-specialist
**Complexity**: MEDIUM
**Estimated Time**: 4-6 hours
**Dependencies**: None

**Objective**: Complete `compare_states()` and `resolve_differences()` in identity-core bridge.

**Deliverables**:
```
labs/core/bridges/identity_core_bridge.py (complete)
tests/bridges/test_identity_core_bridge.py
```

**Implementation Requirements**:

1. **Complete Bridge Implementation**:
```python
class IdentityCoreBridge:
    """Bridge for Identity ↔ Core state synchronization."""

    async def compare_states(
        self,
        identity_state: dict,
        core_state: dict
    ) -> dict:
        """Compare identity and core states.

        Returns:
            {
                "diffs": [
                    {"field": "user_count", "identity": 100, "core": 95},
                    {"field": "active_credentials", "identity": 50, "core": 48}
                ],
                "sync_required": true
            }
        """
        diffs = []

        # Compare user counts
        if identity_state["user_count"] != core_state["user_count"]:
            diffs.append({
                "field": "user_count",
                "identity": identity_state["user_count"],
                "core": core_state["user_count"]
            })

        # Compare active credentials
        if identity_state["active_credentials"] != core_state["active_credentials"]:
            diffs.append({
                "field": "active_credentials",
                "identity": identity_state["active_credentials"],
                "core": core_state["active_credentials"]
            })

        return {
            "diffs": diffs,
            "sync_required": len(diffs) > 0
        }

    async def resolve_differences(
        self,
        diffs: list,
        resolution_strategy: str = "identity_wins"
    ) -> dict:
        """Resolve state differences idempotently.

        Args:
            diffs: List of differences from compare_states()
            resolution_strategy: "identity_wins" or "core_wins"

        Returns:
            {
                "resolved": 2,
                "failed": 0,
                "actions": ["synced user_count", "synced active_credentials"]
            }
        """
        actions = []
        resolved = 0
        failed = 0

        for diff in diffs:
            try:
                if resolution_strategy == "identity_wins":
                    await self._sync_to_core(diff)
                else:
                    await self._sync_to_identity(diff)

                actions.append(f"synced {diff['field']}")
                resolved += 1

            except Exception as e:
                logger.error(f"Failed to resolve {diff['field']}: {e}")
                failed += 1

        return {
            "resolved": resolved,
            "failed": failed,
            "actions": actions
        }
```

**Acceptance Criteria**:
- [ ] `compare_states()` detects all state differences
- [ ] `resolve_differences()` is idempotent (can retry safely)
- [ ] Tests verify happy path + conflict scenarios
- [ ] Retry logic handles transient failures

---

#### Task 55: TRINITY Claims + Constellation Alignment
**Assignee**: identity-auth-specialist
**Complexity**: MEDIUM
**Estimated Time**: 3-5 hours
**Dependencies**: Task 46 (ABAS middleware)

**Objective**: Add `trinity` claim bundle to tokens with ABAS enforcement.

**Deliverables**:
```
core/identity/trinity_claims.py
policies/matrix/identity.rego (updates)
tests/identity/test_trinity_claims.py
```

**Implementation Requirements**:

1. **TRINITY Claims in Tokens**:
```python
async def issue_id_token(user_id: str, constellation_status: dict) -> str:
    """Issue ID token with TRINITY claims."""

    payload = {
        "sub": user_id,
        "iss": "https://ai",
        "aud": "lukhas_web",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),

        # TRINITY claim bundle
        "trinity": {
            "identity": constellation_status.get("identity", "off"),
            "consciousness": constellation_status.get("consciousness", "off"),
            "guardian": constellation_status.get("guardian", "off")
        },

        # Constellation modules (8-star system)
        "constellation": {
            "identity": "on",
            "memory": constellation_status.get("memory", "off"),
            "vision": constellation_status.get("vision", "off"),
            "bio": constellation_status.get("bio", "off"),
            "dream": constellation_status.get("dream", "off"),
            "ethics": constellation_status.get("ethics", "off"),
            "guardian": constellation_status.get("guardian", "off"),
            "quantum": constellation_status.get("quantum", "off")
        }
    }

    kid, private_key = key_manager.get_current_signing_key()
    token = jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": kid})

    return token
```

2. **ABAS Policy Enforcement**:
```rego
# Require Guardian module for sensitive operations
allow if {
    input.trinity.guardian == "on"
    input.path == "/identity/admin/revoke-all"
}

deny[reason] {
    input.trinity.guardian == "off"
    input.path == "/identity/admin/revoke-all"
    reason := "Guardian module required for admin operations"
}
```

**Acceptance Criteria**:
- [ ] Tokens include `trinity` section
- [ ] ABAS can deny if required module is off
- [ ] Runtime checks for ⚛️🧠🛡️ status
- [ ] Tests verify policy enforcement

---

#### Task 56: Documentation Suite
**Assignee**: security-governance-specialist
**Complexity**: MEDIUM
**Estimated Time**: 3-6 hours
**Dependencies**: All implementation tasks

**Objective**: Consolidate all documentation into comprehensive operations runbooks.

**Deliverables**:
```
docs/identity/OPERATIONS.md
docs/identity/TROUBLESHOOTING.md
docs/identity/RUNBOOKS/key_rotation.md
docs/identity/RUNBOOKS/salt_rotation.md
docs/identity/RUNBOOKS/emergency_revocation.md
docs/identity/RUNBOOKS/opa_policy_testing.md
```

**Implementation Requirements**:

Create comprehensive runbooks for:
- Key rotation procedure (manual and automated)
- Salt rotation for consent proofs
- Emergency token revocation (mass revoke)
- OPA policy testing and deployment
- Disaster recovery procedures
- Performance troubleshooting

**Acceptance Criteria**:
- [ ] All runbooks include step-by-step procedures
- [ ] Troubleshooting guide covers common errors
- [ ] Operations manual ready for production team

---

#### Task 57: Unit & Integration Test Coverage (90% Goal)
**Assignee**: observability-testing-specialist
**Complexity**: HIGH
**Estimated Time**: 8-12 hours
**Dependencies**: All implementation tasks

**Objective**: Achieve 90%+ test coverage across identity packages.

**Implementation Requirements**:

1. **Coverage Areas**:
- ΛID generation edge cases (invalid metadata, concurrency)
- OIDC token issuance/validation (all grant types)
- WebAuthn flows (registration, assertion, error cases)
- ABAS policy enforcement (allow, deny, step-up)
- Redis/Postgres store operations (TTL, revocation, encryption)
- Key rotation scenarios (grace periods, expiry)

2. **Run Coverage**:
```bash
pytest tests/identity/ --cov=core.identity --cov-report=html --cov-report=term
```

**Acceptance Criteria**:
- [ ] `pytest --maxfail=1 --disable-warnings` passes
- [ ] Coverage >= 90% for `core/identity/` packages
- [ ] All edge cases covered
- [ ] Integration tests validate end-to-end flows

---

## 📋 EXECUTION CHECKLIST

### Before Starting ANY Task

- [ ] Verify working in correct worktree: `/Users/agi_dev/LOCAL-REPOS/Lukhas-identity-production`
- [ ] Read existing foundation code (Tasks 41-42)
- [ ] Check TODO/MASTER_LOG.md for current status
- [ ] Review relevant docs/ files

### During Implementation

- [ ] Write tests FIRST (TDD approach)
- [ ] Follow existing code patterns
- [ ] Respect lane boundaries (no candidate/ imports)
- [ ] Add comprehensive docstrings
- [ ] Include error handling
- [ ] Add logging (no PII!)
- [ ] Update metrics/observability

### After Completing Task

- [ ] All tests pass locally
- [ ] Coverage meets requirements
- [ ] Documentation updated
- [ ] Update TODO/MASTER_LOG.md (mark task complete)
- [ ] Commit with T4 format
- [ ] Create PR if ready for review

---

## 🎓 SPECIALIZED AGENT ASSIGNMENTS

### api-bridge-specialist
- Task 43: OAuth2 Introspection & Revocation
- Task 49: Multi-Actor Identity Integration
- Task 54: Bridge Completion

### identity-auth-specialist (You)
- Task 44: Production WebAuthn
- Task 48: ΛID Model
- Task 51: OIDC Discovery
- Task 55: TRINITY Claims

### security-governance-specialist
- Task 45: Consent Proof Store
- Task 46: ABAS Middleware
- Task 53: Threat Model + DPIA
- Task 56: Documentation Suite

### observability-testing-specialist
- Task 47: Prometheus Metrics
- Task 50: Identity Event Bus
- Task 52: MATRIZ Readiness
- Task 57: Test Coverage (90%)

---

## 🚀 SUCCESS METRICS

**Technical Metrics**:
- p95 auth latency: <100ms ✅
- WebAuthn success rate: >98%
- ΛID generation collision rate: 0%
- JWKS availability: 99.9%
- Test coverage: >90%

**Security Metrics**:
- Threat model completeness: 100%
- DPIA readiness: Legal review approved
- Red-team findings: <3 critical, all remediated
- Audit trail coverage: 100%

**Compliance Metrics**:
- GDPR consent proofs: No raw TC strings ✅
- OPA policy enforcement: 100% of identity routes
- Key rotation: Automated, tested ✅
- Documentation: Complete (API, ops, security)

---

## 📞 SUPPORT & REFERENCES

**Existing Docs** (Already Completed):
- `docs/identity/DEPLOYMENT_STORAGE.md`
- `docs/identity/JWKS_AND_KEY_ROTATION.md`

**Architecture Docs**:
- `docs/architecture/README.md`
- `docs/gonzo/Lukhas_ID system improvement plan.md`

**Test Examples**:
- `tests/identity/storage/test_redis_token_store.py`
- `tests/identity/storage/test_webauthn_store.py`
- `tests/identity/crypto/test_key_management.py`

**Source Code References**:
- `core/identity/storage/` - Foundation complete ✅
- `core/identity/keys.py` - Key management ✅
- `core/identity/jwks_endpoint.py` - JWKS endpoint ✅

---

## ⚡ QUICK START

**For Any Agent**:
```bash
# 1. Navigate to worktree
cd /Users/agi_dev/LOCAL-REPOS/Lukhas-identity-production

# 2. Check status
git status
cat TODO/MASTER_LOG.md

# 3. Pick your assigned task
# 4. Read existing code in core/identity/
# 5. Write tests first
# 6. Implement feature
# 7. Update MASTER_LOG.md
# 8. Commit with T4 format
```

---

**Last Updated**: 2025-11-14
**Version**: 1.0
**Ready for Deployment**: YES ✅
