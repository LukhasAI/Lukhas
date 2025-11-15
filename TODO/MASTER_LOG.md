# MASTER LOG - Missing Module Implementations

**Generated**: 2025-11-15
**Session**: Phase 7 Test Error Reduction
**Purpose**: Full technical specifications for 38 missing modules that currently have stub implementations

---

## Status Legend
- 🔴 **STUB** - Stub implementation exists, needs full implementation
- 🟡 **PARTIAL** - Some functionality exists, needs completion
- 🟢 **COMPLETE** - Fully implemented and tested

---

## Table of Contents

1. [Governance Modules (7)](#1-governance-modules)
2. [Serve API Modules (9)](#2-serve-api-modules)
3. [Core System Modules (4)](#3-core-system-modules)
4. [Memory System Modules (3)](#4-memory-system-modules)
5. [Bridge Modules (1)](#5-bridge-modules)
6. [Labs Research Modules (2)](#6-labs-research-modules)
7. [Lukhas Production Modules (2)](#7-lukhas-production-modules)
8. [Orchestration Modules (1)](#8-orchestration-modules)
9. [Security Modules (2)](#9-security-modules)
10. [Implementation Priorities](#10-implementation-priorities)

---

## 1. Governance Modules

### 1.1 Consent History Manager 🔴

**File**: `governance/identity/core/sent/consent_history.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: Manage consent history with cryptographic hashing and activity tracing for GDPR compliance.

**Technical Specifications**:

```python
class ConsentHistoryManager:
    """
    Manages consent history for user data processing.

    Requirements:
    - Deterministic SHA-256 hashing of consent records
    - Chronological storage with timestamp verification
    - Activity tracing for audit trails
    - GDPR Article 7(1) compliance - consent record keeping
    - Support for consent withdrawal and revocation
    """

    def __init__(self, config: Dict[str, Any], trace_logger: TraceLogger):
        """
        Args:
            config: Configuration including storage backend
            trace_logger: Activity logger for consent events
        """

    def _generate_record_hash(self, record: Dict, user_id: str) -> str:
        """Generate deterministic hash for consent record."""

    def add_record(self, user_id: str, event_type: str, scope_data: Dict) -> str:
        """Add consent event and return hash."""

    def get_history(self, user_id: str) -> List[Dict]:
        """Retrieve full consent history for user."""

    def verify_consent(self, user_id: str, scope: str) -> bool:
        """Verify active consent for given scope."""

    def revoke_consent(self, user_id: str, scope: str) -> str:
        """Record consent revocation."""
```

**Integration Points**:
- `governance.identity` - ΛiD authentication system
- `lukhas.governance.gdpr` - GDPR compliance service
- `lukhas.governance.audit` - Audit logging

**Testing Requirements**:
- Hash determinism tests
- Consent verification logic
- GDPR withdrawal flow
- Audit trail completeness

**Dependencies**:
- `hashlib` (stdlib)
- `datetime` (stdlib)
- Storage backend (SQLite/PostgreSQL)

---

### 1.2 QRG (Quantum-Resistant Governance) Generator 🔴

**File**: `governance/identity/core/qrs/qrg_generator.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: Generate quantum-resistant cryptographic tokens for governance and authentication.

**Technical Specifications**:

```python
class QRGGenerator:
    """
    Quantum-resistant governance token generator.

    Requirements:
    - Post-quantum cryptography (NIST PQC finalists)
    - Token lifecycle management (generation, rotation, revocation)
    - Scope-based permissions encoding
    - Integration with ΛiD authentication
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: PQC algorithm selection, key management
        """

    def generate_qrg_token(self, user_id: str, scopes: List[str],
                          ttl_seconds: int = 3600) -> str:
        """
        Generate QRG token with embedded scopes.

        Returns:
            QRG_<token> format with embedded signature
        """

    def verify_token(self, token: str, required_scopes: List[str]) -> bool:
        """Verify token validity and scope permissions."""

    def rotate_token(self, old_token: str) -> str:
        """Rotate token while preserving scopes."""

    def revoke_token(self, token: str) -> bool:
        """Revoke token immediately."""
```

**Cryptography**:
- Algorithm: CRYSTALS-Dilithium (NIST PQC winner for signatures)
- Key size: 2048-bit public keys
- Signature size: ~2420 bytes
- Security level: NIST Level 2 (equivalent to AES-128)

**Integration Points**:
- `governance.identity.auth_integrations.qrg_bridge`
- `lukhas.api.auth_helpers` - Feature access control
- `security.encryption_manager`

**Testing Requirements**:
- Quantum resistance validation
- Token verification accuracy
- Scope permission checks
- Rotation/revocation flows

**Dependencies**:
- `pqcrypto` or `liboqs-python` (post-quantum crypto library)
- `secrets` (stdlib)

---

### 1.3 QRG Bridge 🔴

**File**: `governance/identity/auth_integrations/qrg_bridge.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: Bridge between QRG token system and authentication integrations.

**Technical Specifications**:

```python
class QRGBridge:
    """
    Authentication bridge for QRG tokens.

    Requirements:
    - Token verification middleware
    - Integration with FastAPI/Starlette auth
    - Session management with QRG tokens
    - Multi-tenant support
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with QRG generator and session store."""

    def authenticate_with_qrg(self, qrg_token: str) -> Optional[UserContext]:
        """Authenticate request using QRG token."""

    def generate_auth_token(self, user_id: str, scopes: List[str]) -> str:
        """Generate QRG auth token for user."""

    def middleware(self, request: Request, call_next: Callable) -> Response:
        """FastAPI middleware for QRG authentication."""
```

**Integration Points**:
- `governance.identity.core.qrs.qrg_generator`
- `lukhas.api.features` - Feature flags/access control
- `serve.middleware.strict_auth`

---

### 1.4 Consolidated Guardian Governance 🔴

**File**: `governance/oversight/consolidate_guardian_governance.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Unified interface for Guardian ethical constraints and Governance compliance.

**Technical Specifications**:

```python
class ConsolidatedGuardianGovernance:
    """
    Consolidates Guardian ethics and Governance policies.

    Requirements:
    - Real-time policy enforcement
    - Violation detection and logging
    - Constitutional AI compliance
    - Drift detection integration
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with Guardian and Governance configs."""

    def check_governance_compliance(self, action: Dict) -> ComplianceResult:
        """Check action against all governance policies."""

    def enforce_guardian_policy(self, policy_id: str, context: Dict) -> EnforcementResult:
        """Enforce specific guardian policy."""

    def detect_policy_drift(self, current_state: Dict) -> DriftReport:
        """Detect drift from constitutional policies."""
```

**Integration Points**:
- `governance.ethics.constitutional_ai`
- `governance.guardian.core`
- `lukhas.governance.guardian`

---

### 1.5 Constitutional AI Safety 🔴

**File**: `governance/safety/constitutional_ai_safety.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: Constitutional AI safety validator implementing Anthropic's Constitutional AI principles.

**Technical Specifications**:

```python
class ConstitutionalAISafety:
    """
    Constitutional AI safety system.

    Requirements:
    - Constitutional principles enforcement
    - Multi-stage critique and revision
    - Harmlessness and helpfulness balancing
    - Transparency in constraint application
    """

    def __init__(self, constitution: List[ConstitutionalPrinciple]):
        """
        Args:
            constitution: List of principles to enforce
        """

    def validate_action(self, action: str, context: Dict) -> ValidationResult:
        """Validate action against constitutional principles."""

    def critique_and_revise(self, response: str) -> RevisedResponse:
        """Apply Constitutional AI critique-revision loop."""

    def enforce_safety_constraints(self, prompt: str) -> ConstrainedPrompt:
        """Apply safety constraints to prompt."""
```

**Constitutional Principles** (from Anthropic CAI paper):
1. Harmlessness: Avoid harmful, unethical, or dangerous content
2. Helpfulness: Provide useful, informative responses
3. Honesty: Be truthful and acknowledge limitations
4. Transparency: Explain reasoning and constraints

**Integration Points**:
- `governance.guardian.core`
- `lukhas.api.features` - Safe feature rollout
- `matriz.orchestration` - Safe task planning

**Testing Requirements**:
- Constitutional principle coverage
- Critique-revision effectiveness
- Edge case handling (adversarial prompts)

---

### 1.6 Guardian Reflector 🔴

**File**: `labs/governance/ethics/guardian_reflector.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Meta-level reflection on Guardian decisions for continuous improvement.

**Technical Specifications**:

```python
class GuardianReflector:
    """
    Reflects on Guardian decisions for improvement.

    Requirements:
    - Decision outcome tracking
    - Pattern detection in guardian behaviors
    - Feedback loop for policy refinement
    - Meta-reasoning about ethical constraints
    """

    def __init__(self):
        """Initialize reflection system."""

    def reflect(self, decision: GuardianDecision) -> ReflectionResult:
        """Reflect on guardian decision quality."""

    def detect_patterns(self, decisions: List[GuardianDecision]) -> List[Pattern]:
        """Detect patterns in guardian behavior."""

    def suggest_improvements(self, patterns: List[Pattern]) -> List[Improvement]:
        """Suggest policy improvements based on patterns."""
```

**Integration Points**:
- `governance.guardian.core`
- `governance.metrics.confidence_calibration`

---

### 1.7 Guardian System Integration 🔴

**File**: `labs/governance/guardian_system_integration.py`
**Missing Class**: `GuardianSystemIntegration`
**Status**: PARTIAL (file exists, class missing)
**Priority**: MEDIUM

**Purpose**: Integration layer for Guardian system with other LUKHAS subsystems.

**Technical Specifications**:

```python
class GuardianSystemIntegration:
    """
    Guardian system integration orchestrator.

    Requirements:
    - Cross-system event propagation
    - Guardian state synchronization
    - Performance optimization
    - Backward compatibility
    """

    def __init__(self, config: Dict):
        """Initialize integration layer."""

    def propagate_event(self, event: GuardianEvent) -> None:
        """Propagate guardian event to integrated systems."""

    def sync_state(self) -> SyncResult:
        """Synchronize guardian state across systems."""
```

---

## 2. Serve API Modules

### 2.1 Consciousness API 🔴

**File**: `serve/consciousness_api.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: FastAPI routes for consciousness system status and control.

**Technical Specifications**:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/consciousness", tags=["consciousness"])

class ConsciousnessStatus(BaseModel):
    """Consciousness system status."""
    awareness_level: float
    active_threads: int
    last_update: datetime
    subsystems: Dict[str, bool]

@router.get("/status", response_model=ConsciousnessStatus)
async def get_consciousness_status(
    user: User = Depends(get_current_user)
) -> ConsciousnessStatus:
    """Get current consciousness system status."""

@router.post("/awareness/update")
async def update_awareness(
    data: AwarenessUpdate,
    user: User = Depends(require_admin)
) -> UpdateResult:
    """Update awareness parameters."""

@router.get("/metrics")
async def get_consciousness_metrics() -> MetricsResponse:
    """Get consciousness performance metrics."""
```

**Endpoints**:
- `GET /consciousness/status` - System status
- `POST /consciousness/awareness/update` - Update awareness
- `GET /consciousness/metrics` - Performance metrics
- `POST /consciousness/drift/detect` - Trigger drift detection

**Integration Points**:
- `core.consciousness.drift_detector`
- `matriz.consciousness`
- `lukhas.governance.guardian` - Ethical constraints

**Authentication**: Requires ΛiD token with `consciousness:read` scope

---

### 2.2 Dreams API 🔴

**File**: `serve/dreams_api.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: FastAPI routes for oneiric (dream) generation and management.

**Technical Specifications**:

```python
router = APIRouter(prefix="/dreams", tags=["dreams"])

@router.post("/dream/generate")
async def generate_dream(
    params: DreamGenerationParams,
    user: User = Depends(get_current_user)
) -> DreamResult:
    """Generate oneiric content from seed."""

@router.get("/dream/{dream_id}")
async def get_dream(dream_id: str) -> Dream:
    """Retrieve generated dream."""

@router.post("/dream/{dream_id}/feedback")
async def submit_dream_feedback(
    dream_id: str,
    feedback: DreamFeedback
) -> FeedbackResult:
    """Submit feedback on dream quality."""
```

**Dream Generation Parameters**:
- `seed`: Optional reproducibility seed
- `temperature`: Creativity level (0.0-2.0)
- `regret_signature`: Emotional signature from regret emitter
- `memory_fold_id`: Associated memory context

**Integration Points**:
- `candidate.consciousness.dream` - Dream generator
- `memory.folds` - Memory context
- `governance.guardian` - Content safety

---

### 2.3 Guardian API 🔴

**File**: `serve/guardian_api.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: FastAPI routes for Guardian policy validation and enforcement.

**Technical Specifications**:

```python
router = APIRouter(prefix="/guardian", tags=["guardian"])

@router.post("/validate")
async def validate_action(
    action: ActionRequest,
    user: User = Depends(get_current_user)
) -> ValidationResponse:
    """Validate action against Guardian policies."""

@router.get("/policies")
async def list_policies() -> List[Policy]:
    """List active guardian policies."""

@router.get("/health")
async def guardian_health() -> HealthStatus:
    """Guardian system health status."""
```

**Endpoints**:
- `POST /guardian/validate` - Validate action
- `GET /guardian/policies` - List policies
- `GET /guardian/health` - Health check
- `POST /guardian/veto` - Record veto with explanation

**Integration Points**:
- `governance.guardian.core`
- `governance.ethics.constitutional_ai`
- `serve.middleware.strict_auth` - Authentication

---

### 2.4 Identity API 🔴

**File**: `serve/identity_api.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: FastAPI routes for ΛiD authentication and identity management.

**Technical Specifications**:

```python
router = APIRouter(prefix="/identity", tags=["identity"])

@router.post("/auth")
async def authenticate(
    credentials: AuthCredentials
) -> AuthResponse:
    """Authenticate with ΛiD credentials."""

@router.post("/token/refresh")
async def refresh_token(
    refresh_token: str
) -> TokenResponse:
    """Refresh authentication token."""

@router.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user)
) -> UserProfile:
    """Get user profile."""
```

**Authentication Flow**:
1. POST /identity/auth with credentials
2. Receive ΛiD token + refresh token
3. Use token in Authorization header: `Bearer {token}`
4. Refresh before expiry with /token/refresh

**Integration Points**:
- `governance.identity` - ΛiD core
- `governance.identity.auth_integrations.qrg_bridge` - QRG tokens
- `lukhas.governance.auth` - Production auth

---

### 2.5 WebAuthn Routes 🔴

**File**: `serve/webauthn_routes.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: WebAuthn/FIDO2 passkey registration and authentication routes.

**Technical Specifications**:

```python
router = APIRouter(prefix="/webauthn", tags=["webauthn"])

@router.post("/register/begin")
async def begin_registration(
    user: User = Depends(get_current_user)
) -> RegistrationOptions:
    """Begin WebAuthn credential registration."""

@router.post("/register/complete")
async def complete_registration(
    credential: PublicKeyCredential,
    user: User = Depends(get_current_user)
) -> RegistrationResult:
    """Complete WebAuthn registration."""

@router.post("/authenticate/begin")
async def begin_authentication() -> AuthenticationOptions:
    """Begin WebAuthn authentication."""

@router.post("/authenticate/complete")
async def complete_authentication(
    credential: PublicKeyCredential
) -> AuthResponse:
    """Complete WebAuthn authentication."""
```

**WebAuthn Implementation**:
- Relying Party: `lukhas.ai`, `lukhas.id`
- Algorithms: ES256, RS256
- Authenticator types: Platform, cross-platform
- User verification: Required for sensitive operations

**Integration Points**:
- `governance.identity.core` - User identity
- `lukhas.api.auth_helpers` - Session management
- Browser WebAuthn API

**Dependencies**:
- `webauthn` library (py_webauthn)

---

### 2.6 Trace Routes 🔴

**File**: `serve/routes_traces.py`
**Status**: STUB
**Priority**: LOW

**Purpose**: Distributed tracing and observability routes.

**Technical Specifications**:

```python
router = APIRouter(prefix="/traces", tags=["traces"])

@router.get("/traces")
async def get_traces(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    service: Optional[str] = None
) -> List[Trace]:
    """Retrieve traces in time range."""

@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> TraceDetail:
    """Get detailed trace by ID."""

@router.get("/traces/search")
async def search_traces(
    query: str
) -> List[Trace]:
    """Search traces by query."""
```

**Integration Points**:
- `observability.otel_instrumentation` - OpenTelemetry
- `lukhas.monitoring` - Metrics collection

---

### 2.7 Serve Schemas 🔴

**File**: `serve/schemas.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Pydantic schemas for serve API request/response models.

**Technical Specifications**:

```python
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

class RequestSchema(BaseModel):
    """Base request schema with tracing."""
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None

class ResponseSchema(BaseModel):
    """Base response schema."""
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
    errors: Optional[List[str]] = None
    request_id: Optional[str] = None

class ValidationResponse(BaseModel):
    """Guardian validation response."""
    valid: bool
    score: float
    violations: List[str]
    explanation: Optional[str] = None
```

**Schema Categories**:
- Authentication: `AuthCredentials`, `AuthResponse`, `TokenResponse`
- Guardian: `ValidationResponse`, `PolicyViolation`
- Dreams: `DreamGenerationParams`, `DreamResult`
- Consciousness: `ConsciousnessStatus`, `AwarenessUpdate`

---

### 2.8 Strict Auth Middleware 🔴

**File**: `serve/middleware/strict_auth.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: Strict authentication middleware for production API routes.

**Technical Specifications**:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Strict authentication enforcement middleware.

    Requirements:
    - ΛiD token validation on all protected routes
    - Scope-based access control
    - Rate limiting per user/token
    - Audit logging of auth failures
    """

    def __init__(self, app, exempted_paths: List[str] = None):
        super().__init__(app)
        self.exempted_paths = exempted_paths or ["/health", "/docs"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate authentication before processing request."""
        # 1. Check if path is exempted
        # 2. Extract and validate ΛiD token
        # 3. Verify token signature
        # 4. Check scope permissions
        # 5. Check rate limits
        # 6. Attach user context to request
        # 7. Log authentication event
```

**Token Validation**:
- Extract from `Authorization: Bearer {token}` header
- Verify JWT signature with ΛiD public key
- Check expiry timestamp
- Validate issuer (`iss` claim)
- Verify audience (`aud` claim)

**Integration Points**:
- `governance.identity` - Token verification
- `lukhas.governance.rate_limit` - Rate limiting
- `lukhas.governance.audit` - Audit logging

---

### 2.9 Security Headers Middleware 🔴

**File**: `serve/middleware/headers.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Security headers middleware for OWASP compliance.

**Technical Specifications**:

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware.

    Headers Applied:
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy (CSP)
    - X-Frame-Options
    - X-Content-Type-Options
    - Referrer-Policy
    - Permissions-Policy
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # CSP: Restrict resource loading
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.lukhas.ai;"
        )

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
```

**OWASP Compliance**:
- A1:2021 Broken Access Control - Enforced by AuthMiddleware
- A2:2021 Cryptographic Failures - HSTS, secure cookies
- A3:2021 Injection - CSP headers
- A5:2021 Security Misconfiguration - Security headers

---

## 3. Core System Modules

### 3.1 Consciousness Bridge 🔴

**File**: `core/consciousness/bridge.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Bridge between consciousness subsystems for inter-system communication.

**Technical Specifications**:

```python
class ConsciousnessBridge:
    """
    Bridge for consciousness subsystem integration.

    Requirements:
    - Pub/sub event propagation between subsystems
    - State synchronization across awareness modules
    - Performance monitoring (< 50ms overhead)
    - Graceful degradation when subsystems unavailable
    """

    def __init__(self):
        self.connections: Dict[str, ConsciousnessModule] = {}
        self.event_bus: EventBus = EventBus()

    def connect(self, system_id: str, module: ConsciousnessModule) -> bool:
        """Connect consciousness module to bridge."""

    def propagate_event(self, event: ConsciousnessEvent) -> None:
        """Propagate event to all connected modules."""

    def sync_state(self) -> SyncResult:
        """Synchronize state across modules."""
```

**Supported Modules**:
- `matriz.consciousness` - MATRIZ cognitive core
- `candidate.consciousness.dream` - Oneiric system
- `core.consciousness.drift_detector` - Drift detection

**Event Types**:
- `awareness_update` - Awareness level change
- `drift_detected` - Consciousness drift event
- `memory_consolidated` - Memory consolidation complete

---

### 3.2 NIAS Dream Bridge 🔴

**File**: `core/integration/nias_dream_bridge.py`
**Status**: STUB
**Priority**: LOW

**Purpose**: Bridge between NIAS (Neural Integrated Awareness System) and Dream subsystems.

**Technical Specifications**:

```python
class NIASDreamBridge:
    """
    Bridge between NIAS and Dream systems.

    Requirements:
    - Dream-to-awareness feedback loop
    - NIAS state injection into dream generation
    - Performance target: < 100ms per dream processing
    """

    def __init__(self):
        self.active = False
        self.nias_state: Optional[NIASState] = None

    def process_dream(self, dream_data: Dict) -> ProcessedDream:
        """Process dream through NIAS awareness."""

    def inject_awareness(self, dream_params: DreamParams) -> EnhancedParams:
        """Inject NIAS awareness into dream parameters."""
```

**Integration Points**:
- `candidate.consciousness.dream`
- NIAS system (if implemented)

---

### 3.3 Config Resolver 🔴

**File**: `core/adapters/config_resolver.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Hierarchical configuration resolution from multiple sources.

**Technical Specifications**:

```python
class ConfigResolver:
    """
    Resolves configuration from multiple sources with precedence.

    Precedence Order (highest to lowest):
    1. Environment variables
    2. Command-line arguments
    3. Config files (.env, .toml)
    4. Default values

    Requirements:
    - Type coercion (str -> int, bool, etc.)
    - Nested key access (dot notation)
    - Secret redaction in logs
    - Hot-reload support
    """

    def __init__(self, config_sources: List[ConfigSource]):
        """Initialize with ordered config sources."""

    def resolve(self, key: str, default: Any = None, type_hint: Type = str) -> Any:
        """Resolve configuration value."""

    def get_nested(self, key_path: str, default: Any = None) -> Any:
        """Get nested config value (e.g., 'database.host')."""

    def reload(self) -> None:
        """Hot-reload configuration from sources."""
```

**Integration Points**:
- All LUKHAS modules requiring configuration
- `lukhas.config` - Production configuration

---

### 3.4 Energy-Aware Execution Planner 🔴

**File**: `core/utils/orchestration_energy_aware_execution_planner.py`
**Status**: STUB
**Priority**: LOW

**Purpose**: Plan task execution with energy efficiency optimization.

**Technical Specifications**:

```python
class EnergyAwareExecutionPlanner:
    """
    Plans task execution optimizing for energy efficiency.

    Requirements:
    - Energy cost estimation per task
    - Batching optimization
    - Adaptive scheduling based on load
    - Carbon-aware scheduling (prefer low-carbon hours)
    """

    def __init__(self, energy_budget: float = 1.0):
        """
        Args:
            energy_budget: Relative energy budget (0.0-1.0)
        """

    def plan_execution(self, tasks: List[Task]) -> ExecutionPlan:
        """Plan task execution within energy budget."""

    def estimate_energy(self, task: Task) -> float:
        """Estimate energy cost for task."""

    def optimize_batching(self, tasks: List[Task]) -> List[Batch]:
        """Optimize task batching for energy efficiency."""
```

**Energy Model**:
- CPU cycles → energy units
- Memory access → energy units
- Network I/O → energy units
- GPU operations → energy units (if applicable)

---

## 4. Memory System Modules

### 4.1 Unified Memory Orchestrator 🔴

**File**: `memory/core/unified_memory_orchestrator.py`
**Status**: STUB
**Priority**: HIGH

**Purpose**: Orchestrate unified memory system across short-term, long-term, and fold storage.

**Technical Specifications**:

```python
class UnifiedMemoryOrchestrator:
    """
    Orchestrates unified memory system.

    Requirements:
    - Multi-tier storage (working, episodic, semantic)
    - Automatic promotion/demotion between tiers
    - Memory consolidation (hippocampal model)
    - Vector similarity search
    - Fold-based organization
    """

    def __init__(self, config: Dict):
        self.working_memory: Dict[str, Any] = {}
        self.episodic_store: EpisodicMemory = EpisodicMemory()
        self.semantic_store: SemanticMemory = SemanticMemory()
        self.fold_engine: FoldEngine = FoldEngine()

    def store(self, key: str, value: Any, memory_type: MemoryType) -> str:
        """Store in appropriate memory tier."""

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from any memory tier."""

    def consolidate(self) -> ConsolidationResult:
        """Consolidate memories from working to long-term."""

    def search_semantic(self, query: str, limit: int = 10) -> List[Memory]:
        """Semantic similarity search."""
```

**Memory Tiers**:
1. **Working Memory**: Active, fast access (Redis/in-memory)
2. **Episodic Memory**: Time-ordered events (PostgreSQL with timestamps)
3. **Semantic Memory**: Concept relationships (vector database - Qdrant/Weaviate)
4. **Fold Storage**: Compressed memory archives (S3/filesystem)

**Consolidation Schedule**:
- Every 15 minutes: working → episodic
- Every 6 hours: episodic → semantic + folds
- Weekly: Fold compression and archival

**Integration Points**:
- `memory.folds.fold_engine`
- `lukhas.memory.index` - Memory indexing
- `matriz.memory` - MATRIZ memory integration

---

### 4.2 Memory Index 🔴

**File**: `lukhas/memory/index.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Fast indexing and search for memory system.

**Technical Specifications**:

```python
class MemoryIndex:
    """
    Fast memory indexing and search.

    Requirements:
    - Tag-based indexing
    - Time-range queries
    - Fuzzy search
    - Index persistence
    """

    def __init__(self, index_path: Path):
        """Initialize index from path."""

    def add(self, memory_id: str, tags: List[str], timestamp: datetime) -> None:
        """Add memory to index."""

    def search(self, query: IndexQuery) -> List[str]:
        """Search index with query."""

    def search_by_tag(self, tag: str) -> List[str]:
        """Search by single tag."""

    def search_by_timerange(self, start: datetime, end: datetime) -> List[str]:
        """Search by time range."""
```

**Index Structure**:
- Tag index: Dict[str, Set[memory_id]]
- Time index: B-tree sorted by timestamp
- Fuzzy index: Trigram index for partial matching

**Integration Points**:
- `memory.core.unified_memory_orchestrator`
- `lukhas.api` - Memory search API

---

### 4.3 AGI Memory Fake 🟡

**File**: `labs/memory/fakes/agimemory_fake.py`
**Status**: PARTIAL (class exists, missing __all__)
**Priority**: LOW

**Action Required**: Add `__all__ = ["AGIMemoryFake"]` (DONE in this session)

---

## 5. Bridge Modules

### 5.1 Redis Queue Bridge 🔴

**File**: `bridge/queue/redis_queue.py`
**Status**: STUB
**Priority**: LOW

**Purpose**: Redis-based queue for asynchronous bridge operations.

**Technical Specifications**:

```python
class RedisQueue:
    """
    Redis-based queue for bridge operations.

    Requirements:
    - Persistent job queue
    - Priority support
    - Dead letter queue
    - Job retry with exponential backoff
    """

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis_client = redis.Redis(host=host, port=port)

    def enqueue(self, item: Any, priority: int = 0) -> str:
        """Enqueue item with priority."""

    def dequeue(self) -> Optional[Any]:
        """Dequeue highest priority item."""

    def retry_failed(self, job_id: str) -> bool:
        """Retry failed job."""
```

**Queue Types**:
- High priority: API adapter operations
- Normal priority: Background tasks
- Low priority: Batch operations

**Integration Points**:
- `bridge.adapters` - External API adapters
- `bridge.external_adapters`

**Dependencies**:
- `redis-py`

---

## 6. Labs Research Modules

### 6.1 Qi Biometrics Engine 🔴

**File**: `labs/core/qi_biometrics/qi_biometrics_engine.py`
**Status**: STUB
**Priority**: LOW

**Purpose**: Bio-inspired Qi (life force) biometric analysis.

**Technical Specifications**:

```python
class QiBiometricsEngine:
    """
    Qi biometrics engine for bio-inspired analysis.

    Requirements:
    - Biometric pattern analysis (HRV, GSR, etc.)
    - Qi score computation
    - Personalized biometric profiles
    - Anomaly detection
    """

    def __init__(self):
        self.profiles: Dict[str, BiometricProfile] = {}

    def analyze_biometric(self, user_id: str, data: BiometricData) -> QiAnalysis:
        """Analyze biometric data and compute Qi score."""

    def create_profile(self, user_id: str, baseline_data: BiometricData) -> BiometricProfile:
        """Create baseline biometric profile."""

    def detect_anomaly(self, user_id: str, data: BiometricData) -> AnomalyResult:
        """Detect anomalies from baseline."""
```

**Biometric Signals**:
- Heart Rate Variability (HRV)
- Galvanic Skin Response (GSR)
- Respiration rate
- Body temperature
- (Future: EEG, PPG)

**Qi Score Computation**:
- 0.0-0.3: Low energy state
- 0.3-0.7: Normal energy
- 0.7-1.0: High energy/flow state

**Integration Points**:
- `labs.bio` - Bio-inspired systems
- (Future: Wearable device APIs)

---

## 7. Lukhas Production Modules

### 7.1 Privacy Client 🔴

**File**: `lukhas/analytics/privacy_client.py`
**Status**: STUB
**Priority**: MEDIUM

**Purpose**: Privacy-preserving analytics client with differential privacy.

**Technical Specifications**:

```python
class PrivacyClient:
    """
    Privacy-preserving analytics client.

    Requirements:
    - Differential privacy guarantees (ε-δ DP)
    - Local data minimization
    - Anonymization before transmission
    - GDPR Article 25 compliance (privacy by design)
    """

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Args:
            epsilon: Privacy budget
            delta: Privacy loss probability
        """

    def log_event(self, event: Dict, anonymize: bool = True) -> None:
        """Log event with privacy guarantees."""

    def get_stats(self, aggregation_type: str) -> AggregateStats:
        """Get differentially private aggregate statistics."""

    def clear_local_data(self) -> None:
        """Clear local analytics data."""
```

**Differential Privacy**:
- Algorithm: Laplace mechanism for numeric queries
- Noise calibration: Laplace(sensitivity / ε)
- Composition: Privacy budget tracking

**Integration Points**:
- `lukhas.api` - API usage analytics
- `lukhas.monitoring` - System metrics

**Dependencies**:
- `diffprivlib` (IBM differential privacy library)

---

### 7.2 Lukhas Glyphs 🔴

**File**: `lukhas/glyphs.py` (or `lukhas/glyphs/__init__.py`)
**Missing Function**: `bind_glyph`
**Status**: PARTIAL (module may exist, function missing)
**Priority**: MEDIUM

**Purpose**: GLYPH (symbolic representation) binding and management.

**Technical Specifications**:

```python
def bind_glyph(glyph_key: str, handler: Callable, metadata: Dict = None) -> GlyphBinding:
    """
    Bind GLYPH to handler function.

    Args:
        glyph_key: GLYPH identifier (e.g., "aka:red", "aoi:blue")
        handler: Handler function for GLYPH activation
        metadata: Additional GLYPH metadata

    Returns:
        GlyphBinding with activation handle
    """

class GlyphRegistry:
    """Registry of bound GLYPHs."""

    def __init__(self):
        self.bindings: Dict[str, GlyphBinding] = {}

    def register(self, glyph_key: str, handler: Callable) -> None:
        """Register GLYPH handler."""

    def activate(self, glyph_key: str, context: Dict) -> Any:
        """Activate GLYPH with context."""
```

**GLYPH Format**:
- Namespace: `aka`, `aoi`, `vigilance`, etc.
- Key: `aka:red`, `aoi:blue`
- Metadata: Symbolic attributes, tags

**Integration Points**:
- `aka_qualia` - Qualia representation
- `matriz.symbolic` - Symbolic DNA

---

## 8. Orchestration Modules

### 8.1 Kernel Bus 🔴

**File**: `orchestration/kernel_bus/__init__.py`
**Missing Class**: `KernelBus`
**Status**: PARTIAL (directory exists, class missing)
**Priority**: LOW

**Purpose**: Central event bus for orchestration kernel.

**Technical Specifications**:

```python
class KernelBus:
    """
    Central event bus for orchestration kernel.

    Requirements:
    - Pub/sub event distribution
    - Event filtering and routing
    - Backpressure handling
    - Dead letter queue
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Subscriber]] = {}

    def publish(self, event: KernelEvent) -> None:
        """Publish event to all subscribers."""

    def subscribe(self, event_type: str, handler: Callable) -> Subscription:
        """Subscribe to event type."""

    def unsubscribe(self, subscription: Subscription) -> None:
        """Unsubscribe from events."""
```

**Event Types**:
- `task.scheduled`
- `task.completed`
- `task.failed`
- `resource.allocated`

---

## 9. Security Modules

### 9.1 Encryption Error 🔴

**File**: `security/encryption_manager.py`
**Missing Class**: `EncryptionError`
**Status**: PARTIAL (file exists, class missing)
**Priority**: MEDIUM

**Purpose**: Exception class for encryption operations.

**Technical Specifications**:

```python
class EncryptionError(Exception):
    """Base exception for encryption operations."""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class KeyManagementError(EncryptionError):
    """Exception for key management failures."""

class DecryptionError(EncryptionError):
    """Exception for decryption failures."""
```

---

### 9.2 Quota Config 🔴

**File**: `core/reliability/ratelimit.py`
**Missing Class**: `QuotaConfig`
**Status**: PARTIAL (file may exist, class missing)
**Priority**: MEDIUM

**Purpose**: Rate limiting and quota configuration.

**Technical Specifications**:

```python
@dataclass
class QuotaConfig:
    """
    Rate limit and quota configuration.

    Attributes:
        requests_per_minute: Request rate limit
        requests_per_hour: Hourly quota
        requests_per_day: Daily quota
        burst_size: Burst allowance
    """
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10

    def validate(self) -> None:
        """Validate quota configuration."""
```

**Integration Points**:
- `serve.middleware.strict_auth` - API rate limiting
- `lukhas.governance.rate_limit`

---

## 10. Implementation Priorities

### Priority Matrix

| Module | Priority | Complexity | Estimated Effort | Dependencies |
|--------|----------|------------|------------------|--------------|
| **Governance - Identity** |
| ConsentHistoryManager | HIGH | Medium | 2-3 days | Storage backend |
| QRGGenerator | HIGH | High | 3-4 days | PQC library |
| QRGBridge | HIGH | Medium | 2 days | QRGGenerator |
| ConstitutionalAISafety | HIGH | High | 4-5 days | Guardian core |
| **Serve API** |
| Identity API | HIGH | Medium | 2-3 days | ΛiD core |
| Guardian API | HIGH | Low | 1-2 days | Guardian core |
| Strict Auth Middleware | HIGH | Medium | 2 days | ΛiD |
| Consciousness API | MEDIUM | Low | 1 day | Consciousness |
| Dreams API | MEDIUM | Low | 1 day | Dream system |
| **Memory** |
| UnifiedMemoryOrchestrator | HIGH | High | 5-7 days | Vector DB |
| MemoryIndex | MEDIUM | Medium | 2-3 days | Search library |
| **Core** |
| ConsciousnessBridge | MEDIUM | Medium | 2-3 days | Event bus |
| ConfigResolver | MEDIUM | Low | 1 day | None |
| **Security** |
| Privacy Client | MEDIUM | Medium | 3-4 days | diffprivlib |
| QuotaConfig | LOW | Low | 1 day | None |

### Implementation Phases

**Phase 1: Critical Infrastructure (2-3 weeks)**
1. QRGGenerator + QRGBridge (quantum-resistant auth)
2. ConsentHistoryManager (GDPR compliance)
3. Identity API + StrictAuthMiddleware
4. Guardian API

**Phase 2: Memory & Consciousness (2-3 weeks)**
5. UnifiedMemoryOrchestrator
6. MemoryIndex
7. Consciousness API
8. ConsciousnessBridge

**Phase 3: Advanced Features (2-3 weeks)**
9. ConstitutionalAISafety
10. Dreams API
11. Privacy Client
12. WebAuthn Routes

**Phase 4: Research & Optimization (1-2 weeks)**
13. Qi Biometrics Engine
14. Energy-Aware Planner
15. NIAS Dream Bridge

---

## Claude Code Web Prompts

### Template for Implementation Prompts

```markdown
# Implement [Module Name]

**Context**: LUKHAS AI consciousness platform - [brief system description]

**Module**: `[file_path]`

**Requirements**:
[Copy from technical specifications above]

**Integration Points**:
- [List dependencies and integrations]

**Testing Requirements**:
- [Key test cases]

**Acceptance Criteria**:
- [ ] All methods implemented with type hints
- [ ] Unit tests with >80% coverage
- [ ] Integration tests for key workflows
- [ ] Documentation (docstrings + README)
- [ ] Security review (if applicable)
- [ ] Performance benchmarks met

**Files to Update**:
1. Create: `[module_file]`
2. Update: `[integration_points]`
3. Tests: `tests/unit/[test_file]`

Please implement this module following LUKHAS coding standards (see CLAUDE.md).
```

---

## Next Steps

1. **Review & Prioritize**: Review this master log and confirm implementation priorities
2. **Generate Detailed Prompts**: Create detailed Claude Code Web prompts for Phase 1 modules
3. **Setup Development Branches**: Create feature branches for each module implementation
4. **Begin Implementation**: Start with QRGGenerator (highest priority, highest complexity)
5. **Continuous Integration**: Set up CI/CD for automated testing of new modules

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Maintainer**: LUKHAS Development Team
**License**: PROPRIETARY - LUKHAS AI SYSTEMS

