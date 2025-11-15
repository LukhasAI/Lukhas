# Claude Code Web Prompts - Missing Module Implementations

**Generated**: 2025-11-15
**Purpose**: Ready-to-use Claude Code Web prompts for implementing missing LUKHAS modules
**Reference**: See TODO/MASTER_LOG.md for full technical specifications

---

## Usage Instructions

1. Copy the prompt for the module you want to implement
2. Open Claude Code Web at https://claude.com/claude-code
3. Paste the prompt
4. Claude will create the implementation in a new feature branch
5. Review, test, and merge the PR

---

## Phase 1: Critical Infrastructure (Highest Priority)

### Prompt 1: QRG (Quantum-Resistant Governance) Generator

```markdown
# Implement Quantum-Resistant Governance Token Generator

**Context**: LUKHAS AI is a consciousness-aware AI development platform. We need post-quantum cryptographic tokens for secure authentication that will resist future quantum computer attacks.

**Module**: `governance/identity/core/qrs/qrg_generator.py`

**Requirements**:

Create a `QRGGenerator` class that generates quantum-resistant governance tokens using CRYSTALS-Dilithium (NIST PQC winner):

```python
class QRGGenerator:
    """
    Quantum-resistant governance token generator.

    Requirements:
    - Use CRYSTALS-Dilithium for post-quantum signatures
    - Generate tokens with format: QRG_<32-char-hex>
    - Embed user scopes in token claims
    - Support token lifecycle (generation, verification, rotation, revocation)
    - TTL-based expiration (default 1 hour)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with PQC algorithm config."""

    def generate_qrg_token(self, user_id: str, scopes: List[str],
                          ttl_seconds: int = 3600) -> str:
        """Generate QRG token with embedded scopes."""

    def verify_token(self, token: str, required_scopes: List[str] = None) -> bool:
        """Verify token signature and scope permissions."""

    def rotate_token(self, old_token: str) -> str:
        """Rotate token while preserving scopes."""

    def revoke_token(self, token: str) -> bool:
        """Immediately revoke token."""

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode token to extract claims."""
```

**Implementation Details**:
- Use `pqcrypto-dilithium` or `liboqs-python` library for CRYSTALS-Dilithium
- Token format: `QRG_` + base64url(user_id + scopes + expiry + signature)
- Store revoked tokens in-memory set (or Redis for production)
- Security level: NIST Level 2 (equivalent to AES-128)

**Testing Requirements**:
1. Token generation uniqueness
2. Signature verification accuracy
3. Scope permission checks
4. Rotation preserves scopes
5. Revocation prevents verification
6. Expired tokens fail verification

**Files to Create**:
1. `governance/identity/core/qrs/qrg_generator.py` - Main implementation
2. `governance/identity/core/qrs/__init__.py` - Package init
3. `tests/unit/governance/identity/core/qrs/test_qrg_generator.py` - Tests

**Acceptance Criteria**:
- [ ] All methods implemented with type hints
- [ ] Unit tests with >85% coverage
- [ ] Token generation < 50ms
- [ ] Verification < 10ms
- [ ] Documentation in docstrings
- [ ] No hardcoded secrets

**Dependencies**:
```bash
pip install pqcrypto-dilithium
```

Please implement following LUKHAS coding standards (type hints, docstrings, error handling).
```

---

### Prompt 2: Consent History Manager (GDPR Compliance)

```markdown
# Implement GDPR Consent History Manager

**Context**: LUKHAS AI needs GDPR Article 7(1) compliant consent record keeping with cryptographic audit trails.

**Module**: `governance/identity/core/sent/consent_history.py`

**Requirements**:

Create a `ConsentHistoryManager` class for managing user consent with audit trails:

```python
class ConsentHistoryManager:
    """
    GDPR-compliant consent history manager.

    Requirements:
    - Deterministic SHA-256 hashing of consent records
    - Chronological storage with timestamps
    - Activity tracing for audit compliance
    - Support for consent grant, withdrawal, revocation
    - Immutable record keeping
    """

    def __init__(self, config: Dict[str, Any], trace_logger: TraceLogger):
        """Initialize with config and trace logger."""

    def _generate_record_hash(self, record: Dict, user_id: str) -> str:
        """Generate deterministic hash using SHA-256."""

    def add_record(self, user_id: str, event_type: str,
                   scope_data: Dict, metadata: Dict = None) -> str:
        """Add consent event and return hash."""

    def get_history(self, user_id: str,
                    start_time: datetime = None) -> List[Dict]:
        """Get consent history for user."""

    def verify_consent(self, user_id: str, scope: str) -> bool:
        """Verify active consent for scope."""

    def revoke_consent(self, user_id: str, scope: str,
                      reason: str = None) -> str:
        """Record consent revocation."""

    def export_history(self, user_id: str) -> bytes:
        """Export consent history (GDPR Article 20 - data portability)."""
```

**Event Types**:
- `granted` - Consent granted for scope
- `withdrawn` - Consent withdrawn by user
- `revoked` - Consent administratively revoked
- `updated` - Consent scope updated

**Storage**:
- In-memory dict for testing
- SQLite for development
- PostgreSQL for production

**Testing Requirements**:
1. Hash determinism (same input = same hash)
2. Chronological ordering preserved
3. Consent verification logic correct
4. Withdrawal/revocation recorded properly
5. Export format valid (JSON)

**Files to Create**:
1. `governance/identity/core/sent/consent_history.py` - Implementation
2. `governance/identity/core/sent/__init__.py` - Package init
3. `tests/unit/governance/identity/core/sent/test_consent_history.py` - Tests

**Acceptance Criteria**:
- [ ] All methods with type hints
- [ ] >80% test coverage
- [ ] GDPR Article 7(1) compliant
- [ ] Audit trail complete
- [ ] Documentation complete

Please implement with proper error handling and logging.
```

---

### Prompt 3: Identity API (ΛiD Authentication Routes)

```markdown
# Implement ΛiD Identity API Routes

**Context**: LUKHAS uses ΛiD (Lambda ID) authentication system. We need FastAPI routes for authentication, token refresh, and profile management.

**Module**: `serve/identity_api.py`

**Requirements**:

Create FastAPI router with ΛiD authentication endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/identity", tags=["identity"])

# Request/Response Models
class AuthCredentials(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserProfile(BaseModel):
    user_id: str
    username: str
    scopes: List[str]
    created_at: datetime

# Routes
@router.post("/auth", response_model=AuthResponse)
async def authenticate(credentials: AuthCredentials) -> AuthResponse:
    """Authenticate with ΛiD and return tokens."""
    # 1. Validate credentials
    # 2. Generate access token (JWT, 1 hour TTL)
    # 3. Generate refresh token (7 days TTL)
    # 4. Store refresh token in session store
    # 5. Return tokens

@router.post("/token/refresh", response_model=AuthResponse)
async def refresh_token(request: TokenRefreshRequest) -> AuthResponse:
    """Refresh access token using refresh token."""
    # 1. Verify refresh token
    # 2. Check not revoked
    # 3. Generate new access token
    # 4. Optionally rotate refresh token
    # 5. Return new tokens

@router.get("/profile", response_model=UserProfile)
async def get_profile(user: User = Depends(get_current_user)) -> UserProfile:
    """Get current user profile."""
    # 1. Extract user from auth token
    # 2. Fetch profile from database
    # 3. Return profile

@router.post("/logout")
async def logout(user: User = Depends(get_current_user)) -> Dict:
    """Logout and revoke tokens."""
    # 1. Revoke refresh token
    # 2. Add access token to revocation list
    # 3. Return success
```

**Authentication Flow**:
1. POST /identity/auth with credentials → receive tokens
2. Use access token: `Authorization: Bearer {access_token}`
3. Before expiry: POST /identity/token/refresh → new tokens
4. Logout: POST /identity/logout

**Integration**:
- Connect to `governance.identity` for user lookup
- Use `governance.identity.auth_integrations.qrg_bridge` for QRG tokens
- Integrate with `serve.middleware.strict_auth`

**Testing**:
1. Successful authentication flow
2. Invalid credentials rejected
3. Token refresh works
4. Expired tokens rejected
5. Revoked tokens rejected
6. Profile retrieval requires valid token

**Files to Create**:
1. `serve/identity_api.py` - Router implementation
2. `tests/unit/serve/test_identity_api.py` - Tests

**Dependencies**:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from governance.identity import ΛiD
```

Please implement with proper error handling (HTTP 401, 403, 404) and logging.
```

---

### Prompt 4: Guardian API (Policy Validation)

```markdown
# Implement Guardian Policy Validation API

**Context**: LUKHAS uses a Guardian system for ethical AI constraints. Need API routes for action validation and policy management.

**Module**: `serve/guardian_api.py`

**Requirements**:

Create FastAPI router for Guardian policy enforcement:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/guardian", tags=["guardian"])

class ActionRequest(BaseModel):
    action: str
    context: Dict[str, Any]
    user_id: Optional[str] = None

class ValidationResponse(BaseModel):
    valid: bool
    score: float  # 0.0-1.0, higher = more compliant
    violations: List[str]
    explanation: Optional[str] = None
    veto: bool

class Policy(BaseModel):
    policy_id: str
    name: str
    description: str
    active: bool
    severity: str  # "low", "medium", "high", "critical"

class HealthStatus(BaseModel):
    status: str  # "healthy", "degraded", "down"
    active_policies: int
    last_check: datetime
    drift_detected: bool

@router.post("/validate", response_model=ValidationResponse)
async def validate_action(
    action: ActionRequest,
    user: User = Depends(get_current_user)
) -> ValidationResponse:
    """Validate action against Guardian policies."""
    # 1. Load active policies
    # 2. Run action through Guardian
    # 3. Check constitutional AI constraints
    # 4. Return validation result with explanation

@router.get("/policies", response_model=List[Policy])
async def list_policies(
    active_only: bool = True
) -> List[Policy]:
    """List Guardian policies."""

@router.get("/health", response_model=HealthStatus)
async def guardian_health() -> HealthStatus:
    """Guardian system health check."""

@router.post("/veto")
async def record_veto(
    action_id: str,
    reason: str,
    explanation: str
) -> Dict:
    """Record policy veto with explanation."""
```

**Validation Flow**:
1. Receive action + context
2. Check Guardian policies
3. Run Constitutional AI critique
4. Calculate compliance score
5. Return validation + explanation

**Integration**:
- `governance.guardian.core` - Core Guardian system
- `governance.ethics.constitutional_ai` - Constitutional AI
- `governance.oversight` - Policy management

**Testing**:
1. Valid action passes
2. Policy violation detected
3. Veto recorded properly
4. Health check accurate
5. Policy listing correct

**Files to Create**:
1. `serve/guardian_api.py` - Router
2. `tests/unit/serve/test_guardian_api.py` - Tests

Please implement with comprehensive logging of all validation decisions for audit trails.
```

---

### Prompt 5: Strict Authentication Middleware

```markdown
# Implement Strict Authentication Middleware for Production API

**Context**: LUKHAS production API needs strict authentication enforcement with ΛiD token validation, scope checking, and rate limiting.

**Module**: `serve/middleware/strict_auth.py`

**Requirements**:

Create Starlette middleware for comprehensive authentication:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from typing import Callable, List

class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Strict authentication enforcement middleware.

    Responsibilities:
    - ΛiD token validation
    - JWT signature verification
    - Scope-based access control
    - Rate limiting per user
    - Audit logging
    """

    def __init__(
        self,
        app,
        exempted_paths: List[str] = None,
        require_https: bool = True
    ):
        super().__init__(app)
        self.exempted_paths = exempted_paths or ["/health", "/docs", "/openapi.json"]
        self.require_https = require_https

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Authentication enforcement pipeline:
        1. Check if path exempted
        2. Enforce HTTPS (production)
        3. Extract Authorization header
        4. Validate JWT signature
        5. Check token expiry
        6. Verify issuer/audience
        7. Check scope permissions
        8. Rate limit check
        9. Attach user context to request
        10. Log auth event
        """

        # 1. Check exemption
        if request.url.path in self.exempted_paths:
            return await call_next(request)

        # 2. HTTPS check
        if self.require_https and request.url.scheme != "https":
            return JSONResponse(
                {"error": "HTTPS required"},
                status_code=403
            )

        # 3. Extract token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing or invalid Authorization header"},
                status_code=401
            )

        token = auth_header[7:]  # Remove "Bearer "

        # 4-7. Validate token
        try:
            user_context = await self._validate_token(token, request)
        except TokenExpiredError:
            return JSONResponse({"error": "Token expired"}, status_code=401)
        except TokenInvalidError as e:
            return JSONResponse({"error": str(e)}, status_code=401)

        # 8. Rate limit
        if not await self._check_rate_limit(user_context.user_id):
            return JSONResponse(
                {"error": "Rate limit exceeded"},
                status_code=429
            )

        # 9. Attach user context
        request.state.user = user_context

        # 10. Log auth event
        await self._log_auth_event(request, user_context, success=True)

        response = await call_next(request)
        return response

    async def _validate_token(self, token: str, request: Request) -> UserContext:
        """Validate JWT token."""
        # Implement JWT validation
        # - Decode token
        # - Verify signature with ΛiD public key
        # - Check expiry
        # - Verify issuer: "lukhas.id"
        # - Verify audience matches request
        # - Check not revoked
        # Return UserContext(user_id, scopes, etc.)

    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check rate limit for user."""
        # Implement rate limiting
        # - Default: 100 req/min per user
        # - Use sliding window
        # - Store in Redis or memory

    async def _log_auth_event(
        self,
        request: Request,
        user: UserContext,
        success: bool
    ):
        """Log authentication event for audit."""
        # Log to audit system
```

**Integration**:
- `governance.identity` - Token validation
- `lukhas.governance.rate_limit` - Rate limiting
- `lukhas.governance.audit` - Audit logging

**Testing**:
1. Valid token allows access
2. Missing token rejected (401)
3. Expired token rejected (401)
4. Invalid signature rejected (401)
5. Rate limit enforced (429)
6. Exempted paths bypass auth
7. HTTPS enforced in production

**Files to Create**:
1. `serve/middleware/strict_auth.py` - Middleware
2. `serve/middleware/__init__.py` - Package init
3. `tests/unit/serve/middleware/test_strict_auth.py` - Tests

**Dependencies**:
```python
from jose import jwt, JWTError  # JWT handling
from starlette.middleware.base import BaseHTTPMiddleware
```

Please implement with comprehensive error handling and security logging.
```

---

## Phase 2: Memory & Consciousness

### Prompt 6: Unified Memory Orchestrator

```markdown
# Implement Unified Memory Orchestrator

**Context**: LUKHAS needs a multi-tier memory system mimicking human memory (working, episodic, semantic, long-term folds).

**Module**: `memory/core/unified_memory_orchestrator.py`

**Requirements**:

Create `UnifiedMemoryOrchestrator` class managing 4 memory tiers:

```python
class UnifiedMemoryOrchestrator:
    """
    Multi-tier unified memory orchestrator.

    Memory Tiers:
    1. Working Memory: Active, fast (in-memory/Redis)
    2. Episodic Memory: Time-ordered events (PostgreSQL)
    3. Semantic Memory: Concept relationships (vector DB)
    4. Fold Storage: Compressed archives (filesystem/S3)

    Consolidation:
    - Every 15 min: working → episodic
    - Every 6 hours: episodic → semantic + folds
    - Weekly: Fold compression
    """

    def __init__(self, config: Dict):
        self.working_memory: Dict[str, Any] = {}
        self.episodic_store: EpisodicMemory = ...
        self.semantic_store: SemanticMemory = ...
        self.fold_engine: FoldEngine = ...

    def store(self, key: str, value: Any, memory_type: MemoryType) -> str:
        """Store in appropriate tier based on memory_type."""

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from any tier (search all)."""

    def consolidate(self) -> ConsolidationResult:
        """Run memory consolidation (working→episodic→semantic)."""

    def search_semantic(self, query: str, limit: int = 10) -> List[Memory]:
        """Semantic similarity search using vector embeddings."""

    def create_fold(self, memories: List[Memory]) -> str:
        """Create compressed memory fold."""
```

**Memory Types**:
```python
from enum import Enum

class MemoryType(str, Enum):
    WORKING = "working"  # Active, < 15 min lifetime
    EPISODIC = "episodic"  # Time-stamped events
    SEMANTIC = "semantic"  # Concepts, relationships
    FOLD = "fold"  # Compressed archives
```

**Consolidation Algorithm**:
1. Identify working memories older than 15 minutes
2. Move to episodic with timestamp
3. Extract concepts and relationships
4. Add to semantic store with vector embeddings
5. Create folds for episodic memories older than 7 days

**Integration**:
- `memory.folds.fold_engine` - Fold creation
- `lukhas.memory.index` - Fast indexing
- Vector database (Qdrant, Weaviate, or simple embeddings)

**Testing**:
1. Store/retrieve from each tier
2. Automatic tier promotion
3. Consolidation runs correctly
4. Semantic search accuracy
5. Fold creation & retrieval

**Files to Create**:
1. `memory/core/unified_memory_orchestrator.py` - Orchestrator
2. `memory/core/__init__.py` - Package init
3. `tests/unit/memory/core/test_unified_memory_orchestrator.py` - Tests

**Dependencies**:
```bash
pip install sentence-transformers  # For embeddings
```

Please implement with proper async/await for I/O operations.
```

---

### Prompt 7: Consciousness API

```markdown
# Implement Consciousness System API

**Context**: LUKHAS consciousness system needs API endpoints for status monitoring, awareness updates, and drift detection.

**Module**: `serve/consciousness_api.py`

**Requirements**:

Create FastAPI router for consciousness system:

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/consciousness", tags=["consciousness"])

class ConsciousnessStatus(BaseModel):
    status: str  # "active", "idle", "degraded"
    awareness_level: float  # 0.0-1.0
    active_threads: int
    last_update: datetime
    subsystems: Dict[str, bool]  # subsystem → active
    drift_score: float  # Current drift level

class AwarenessUpdate(BaseModel):
    new_level: float
    reason: str
    metadata: Dict[str, Any] = {}

class DriftDetectionRequest(BaseModel):
    baseline_state: Dict[str, Any]
    current_state: Dict[str, Any]

@router.get("/status", response_model=ConsciousnessStatus)
async def get_consciousness_status() -> ConsciousnessStatus:
    """Get current consciousness system status."""
    # 1. Query consciousness subsystems
    # 2. Get current awareness level
    # 3. Check drift detector
    # 4. Return comprehensive status

@router.post("/awareness/update")
async def update_awareness(
    data: AwarenessUpdate,
    user: User = Depends(require_admin)
) -> Dict:
    """Update system awareness level (admin only)."""
    # 1. Validate new level (0.0-1.0)
    # 2. Update consciousness system
    # 3. Log change
    # 4. Return confirmation

@router.get("/metrics")
async def get_consciousness_metrics() -> Dict:
    """Get consciousness performance metrics."""
    # Return: processing time, memory usage, drift history

@router.post("/drift/detect")
async def detect_drift(
    request: DriftDetectionRequest
) -> Dict:
    """Trigger drift detection."""
    # 1. Call drift detector
    # 2. Compare baseline vs current
    # 3. Return drift score + details
```

**Integration**:
- `core.consciousness.drift_detector` - Drift detection
- `matriz.consciousness` - MATRIZ cognitive core
- `lukhas.governance.guardian` - Policy enforcement

**Testing**:
1. Status endpoint returns valid data
2. Awareness update requires admin
3. Drift detection works correctly
4. Metrics endpoint performance

**Files to Create**:
1. `serve/consciousness_api.py` - Router
2. `tests/unit/serve/test_consciousness_api.py` - Tests

Please implement with proper authorization checks (admin-only for updates).
```

---

## Phase 3: Advanced Features

### Prompt 8: Constitutional AI Safety

```markdown
# Implement Constitutional AI Safety System

**Context**: LUKHAS implements Anthropic's Constitutional AI principles for ethical constraints. Need critique-revision loop and safety enforcement.

**Module**: `governance/safety/constitutional_ai_safety.py`

**Requirements**:

Create Constitutional AI safety validator:

```python
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ConstitutionalPrinciple:
    """Single constitutional principle."""
    id: str
    category: str  # "harmlessness", "helpfulness", "honesty", "transparency"
    principle: str  # Natural language principle
    critique_prompt: str  # Prompt for critique
    revision_prompt: str  # Prompt for revision

class ConstitutionalAISafety:
    """
    Constitutional AI safety system.

    Implements:
    - Multi-principle validation
    - Critique-revision loop
    - Harmlessness/helpfulness balancing
    - Transparent constraint application
    """

    def __init__(self, constitution: List[ConstitutionalPrinciple]):
        self.constitution = constitution
        self.violation_log: List[Dict] = []

    def validate_action(
        self,
        action: str,
        context: Dict
    ) -> ValidationResult:
        """
        Validate action against constitutional principles.

        Process:
        1. Check each principle
        2. Identify violations
        3. Calculate scores
        4. Return validation result
        """

    def critique_and_revise(
        self,
        response: str,
        max_iterations: int = 3
    ) -> RevisedResponse:
        """
        Constitutional AI critique-revision loop.

        Process:
        1. Generate critique against principles
        2. Revise response based on critique
        3. Repeat until compliant or max iterations
        4. Return final revised response
        """

    def enforce_safety_constraints(
        self,
        prompt: str
    ) -> ConstrainedPrompt:
        """Apply safety constraints to prompt before execution."""

@dataclass
class ValidationResult:
    valid: bool
    constitutional_score: float  # 0.0-1.0
    violations: List[str]
    principles_checked: List[str]
    explanation: str

@dataclass
class RevisedResponse:
    original: str
    revised: str
    iterations: int
    improvements: List[str]
    final_score: float
```

**Default Constitutional Principles** (from Anthropic):

1. **Harmlessness**: "Do not generate harmful, unethical, racist, sexist, toxic, dangerous, or illegal content."
2. **Helpfulness**: "Provide useful, informative, and relevant responses to the user's query."
3. **Honesty**: "Be truthful and accurate. Acknowledge limitations and uncertainties."
4. **Transparency**: "Explain reasoning and constraints when applied."

**Testing**:
1. Harmful content rejected
2. Helpful responses promoted
3. Critique-revision improves safety
4. Transparency in explanations
5. Edge cases (adversarial prompts)

**Files to Create**:
1. `governance/safety/constitutional_ai_safety.py` - Implementation
2. `governance/safety/__init__.py` - Package init
3. `tests/unit/governance/safety/test_constitutional_ai_safety.py` - Tests

Please implement with detailed logging of all validation decisions.
```

---

### Prompt 9: Privacy-Preserving Analytics Client

```markdown
# Implement Privacy-Preserving Analytics with Differential Privacy

**Context**: LUKHAS needs privacy-preserving analytics that complies with GDPR while providing useful aggregate statistics.

**Module**: `lukhas/analytics/privacy_client.py`

**Requirements**:

Create differential privacy analytics client:

```python
from typing import Dict, Any
from dataclasses import dataclass

class PrivacyClient:
    """
    Privacy-preserving analytics client with differential privacy.

    Implements:
    - ε-differential privacy (epsilon-DP)
    - Local data minimization
    - Automatic anonymization
    - GDPR Article 25 (privacy by design)
    """

    def __init__(
        self,
        epsilon: float = 1.0,  # Privacy budget
        delta: float = 1e-5,   # Privacy loss probability
        mechanism: str = "laplace"
    ):
        self.epsilon = epsilon
        self.delta = delta
        self.mechanism = mechanism
        self.events: List[Dict] = []
        self.privacy_budget_used = 0.0

    def log_event(
        self,
        event: Dict[str, Any],
        anonymize: bool = True
    ) -> None:
        """
        Log event with automatic anonymization.

        Anonymization steps:
        1. Remove PII (email, IP, user_id)
        2. Generalize timestamps (hour granularity)
        3. Hash identifiers
        """

    def get_stats(
        self,
        aggregation_type: str,
        column: str = None
    ) -> AggregateStats:
        """
        Get differentially private aggregate statistics.

        Supported aggregations:
        - count: Noisy count
        - mean: Noisy mean
        - sum: Noisy sum
        - histogram: Noisy histogram

        Noise Mechanism:
        - Laplace: noise = Laplace(sensitivity / epsilon)
        - Gaussian: noise = Gaussian(sensitivity * sqrt(2*ln(1.25/delta)) / epsilon)
        """

    def check_privacy_budget(self) -> float:
        """Return remaining privacy budget (epsilon - used)."""

    def clear_local_data(self) -> None:
        """Clear local analytics data (GDPR right to erasure)."""

@dataclass
class AggregateStats:
    aggregation_type: str
    value: float  # Noisy value
    noise_added: float
    epsilon_used: float
    count: int  # Noisy count
```

**Differential Privacy Math**:
- **Laplace Mechanism**: Add noise ~ Laplace(sensitivity / ε)
- **Sensitivity**: Maximum change one individual can cause
- **Composition**: Total ε = sum of query ε values

**Implementation**:
```python
import numpy as np

def add_laplace_noise(value: float, sensitivity: float, epsilon: float) -> float:
    """Add Laplace noise for ε-DP."""
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise
```

**Testing**:
1. Anonymization removes PII
2. Noisy counts within expected range
3. Privacy budget tracking correct
4. Multiple queries compose properly
5. GDPR erasure works

**Files to Create**:
1. `lukhas/analytics/privacy_client.py` - Client
2. `lukhas/analytics/__init__.py` - Package init
3. `tests/unit/lukhas/analytics/test_privacy_client.py` - Tests

**Dependencies**:
```bash
pip install diffprivlib numpy
```

Please implement with proper privacy budget tracking and warnings when budget exhausted.
```

---

## Quick Implementation Checklist Template

For each module implementation, ensure:

- [ ] **Type Hints**: All functions have complete type annotations
- [ ] **Docstrings**: Google-style docstrings for all public methods
- [ ] **Error Handling**: Proper exception handling with custom exceptions
- [ ] **Logging**: Structured logging with appropriate levels
- [ ] **Tests**: Unit tests with >80% coverage
- [ ] **Integration Tests**: At least 2-3 integration test scenarios
- [ ] **Security**: No hardcoded secrets, proper input validation
- [ ] **Performance**: Meet performance targets from specs
- [ ] **Documentation**: README or usage examples
- [ ] **Code Review**: Self-review checklist completed

---

## Implementation Tips

### 1. Start Small
Begin with the simplest method and build up complexity incrementally.

### 2. Test-Driven Development
Write tests first for critical functionality, then implement to pass tests.

### 3. Use Type Hints
Leverage mypy for type checking:
```bash
mypy governance/identity/core/qrs/qrg_generator.py
```

### 4. Structured Logging
Use structlog for better observability:
```python
import structlog

logger = structlog.get_logger(__name__)
logger.info("token_generated", user_id=user_id, token_prefix=token[:10])
```

### 5. Configuration
Use pydantic for configuration validation:
```python
from pydantic import BaseModel

class QRGConfig(BaseModel):
    algorithm: str = "dilithium2"
    ttl_seconds: int = 3600
    security_level: int = 2
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Total Prompts**: 9 (covering 15 modules)
**Estimated Total Effort**: 6-8 weeks for all modules

