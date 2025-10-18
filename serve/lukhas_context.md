---
status: wip
type: documentation
---
# Serve Module Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*


**Module**: serve
**Purpose**: LUKHAS serve module implementing API serving, orchestration, and consciousness endpoints
**Lane**: L2 (Integration)
**Language**: Python
**Last Updated**: 2025-10-18

---

## Module Overview

The serve module provides comprehensive API serving capabilities for LUKHAS, including consciousness APIs, AGI orchestration, identity services, guardian integration, and feedback systems. It implements 46 components across multiple API surfaces with complete observability.

### Key Components
- **Consciousness API**: Consciousness query and dream session endpoints
- **AGI Orchestration API**: Multi-AI consensus and model capabilities
- **Identity API**: Authentication and identity management endpoints
- **Guardian API**: Ethics validation and compliance endpoints
- **Feedback Routes**: User feedback and learning reports

### Constellation Framework Integration
- **⚛️ Anchor Star (Identity)**: Identity authentication and tier management
- **🧠 Flow Star (Consciousness)**: Consciousness queries and dream sessions
- **🛡️ Watch Star (Guardian)**: Guardian validation and drift scoring
- **✦ Trail Star (Memory)**: Memory dump and retrieval endpoints

---

## Architecture

### Core Serve Components

#### Entrypoints (from manifest)
```python
from serve.agi_orchestration_api import (
    OrchestrationRequest,
    OrchestrationResponse,
    ConsensusRequest,
    ConsensusResponse,
    ModelCapabilitiesRequest,
    ModelCapabilitiesResponse,
)
```

### API Surfaces

#### 1. AGI Orchestration API
**Module**: `serve.agi_orchestration_api`
**Purpose**: Multi-AI orchestration and consensus building

```python
from serve.agi_orchestration_api import (
    OrchestrationRequest,
    OrchestrationResponse,
    ConsensusRequest,
    ConsensusResponse,
)

# Orchestrate multiple AI models
request = OrchestrationRequest(
    prompt="Complex reasoning task",
    models=["gpt-4", "claude-3", "gemini-pro"],
    consensus_required=True
)
response: OrchestrationResponse = await orchestrate(request)
```

#### 2. Cognitive Enhanced Consciousness API
**Module**: `serve.cognitive_enhanced_consciousness_api`
**Purpose**: Advanced consciousness queries and dream sessions

```python
from serve.cognitive_enhanced_consciousness_api import (
    ConsciousnessQueryRequest,
    ConsciousnessQueryResponse,
    DreamSessionRequest,
    DreamSessionResponse,
    MemoryQueryRequest,
    MemoryQueryResponse,
    LearningSessionRequest,
    LearningSessionResponse,
)

# Query consciousness state
query = ConsciousnessQueryRequest(query="awareness level")
response: ConsciousnessQueryResponse = await consciousness_query(query)

# Initiate dream session
dream = DreamSessionRequest(duration=60, mode="creative")
session: DreamSessionResponse = await dream_session(dream)
```

#### 3. Identity API
**Module**: `serve.identity_api`
**Purpose**: Authentication and identity management endpoints

```python
from serve.identity_api import authenticate, get_user_identity

# Authenticate user
result = await authenticate(credentials)

# Get identity details
identity = await get_user_identity(lambda_id)
```

#### 4. Guardian API
**Module**: `serve.guardian_api`
**Purpose**: Ethics validation and compliance endpoints

```python
from serve.guardian_api import validate_ethics, check_drift

# Validate ethics for action
validation = await validate_ethics(action, context)

# Check drift score
drift = await check_drift(behavior_pattern)
```

#### 5. Feedback Routes
**Module**: `serve.feedback_routes`
**Purpose**: User feedback and system metrics collection

```python
from serve.feedback_routes import (
    FeedbackRequest,
    FeedbackResponse,
    LearningReportResponse,
    SystemMetricsResponse,
)

# Submit feedback
feedback = FeedbackRequest(
    type="consciousness_query",
    rating=5,
    comment="Excellent awareness response"
)
response: FeedbackResponse = await submit_feedback(feedback)

# Get learning report
report: LearningReportResponse = await get_learning_report()
```

---

## API Schemas

### Request/Response Models

```python
from serve.schemas import (
    DreamRequest,
    DreamResponse,
    GlyphFeedbackRequest,
    GlyphFeedbackResponse,
    TierAuthRequest,
    TierAuthResponse,
    PluginLoadRequest,
    PluginLoadResponse,
    MemoryDumpResponse,
    ModulatedChatRequest,
    ModulatedChatResponse,
)

# Dream processing
dream_request = DreamRequest(theme="creative exploration")
dream_response: DreamResponse = await process_dream(dream_request)

# Tier authentication
auth_request = TierAuthRequest(lambda_id="ΛID-USER-001", tier=2)
auth_response: TierAuthResponse = await authenticate_tier(auth_request)
```

---

## Observability

### Required Spans

The serve module implements comprehensive OpenTelemetry tracing:

```python
# Required spans from module.manifest.json
REQUIRED_SPANS = [
    "lukhas.serve.auth",           # Authentication operations
    "lukhas.serve.consciousness",  # Consciousness API calls
    "lukhas.serve.fold",          # Memory fold operations
    "lukhas.serve.operation",     # General operations
    "lukhas.serve.retrieval",     # Data retrieval
]
```

### Instrumentation

```python
from serve.main import instrument_app

# Instrument FastAPI application
app = instrument_app(app)
```

---

## Performance Routes

### Extreme Performance Mode

**Module**: `serve.extreme_performance_main`
**Purpose**: Optimized serving for high-throughput scenarios

```python
from serve.extreme_performance_main import ExtremePerformanceServer

# Create extreme performance server
server = ExtremePerformanceServer(
    max_connections=10000,
    connection_timeout=30,
    enable_caching=True
)
await server.start()
```

---

## Utility Functions

### Route Utilities

```python
from serve.routes import compute_drift_score, compute_affect_delta

# Compute drift score
drift = compute_drift_score(current_state, baseline_state)

# Compute affect delta
affect_change = compute_affect_delta(previous_emotion, current_emotion)
```

### Trace Utilities

```python
from serve.routes_traces import (
    get_trace_storage_provider,
    validate_trace_id,
    require_api_key,
)

# Get trace storage
storage = get_trace_storage_provider()

# Validate trace ID
is_valid = validate_trace_id(trace_id)
```

### OpenAI Routes

```python
from serve.openai_routes import get_service

# Get OpenAI modulated service
service = get_service()
response = await service.chat_completion(messages)
```

---

## Health & Diagnostics

### Health Checks

```python
from serve.main import healthz

# Check system health
health_status = await healthz()
# Returns: {"status": "healthy", "services": {...}}
```

### OpenAPI Export

```python
from serve.main import openapi_export

# Export OpenAPI specification
spec = openapi_export()
```

---

## Module Structure

```
serve/
├── __init__.py                              # Module initialization
├── README.md                                # Serve overview
├── agi_orchestration_api.py                # AGI orchestration endpoints
├── cognitive_enhanced_consciousness_api.py # Enhanced consciousness API
├── consciousness_api.py                     # Core consciousness API
├── identity_api.py                          # Identity management API
├── guardian_api.py                          # Guardian validation API
├── feedback_routes.py                       # Feedback and metrics routes
├── routes.py                                # Core routing utilities
├── routes_traces.py                         # Trace management routes
├── openai_routes.py                         # OpenAI integration routes
├── extreme_performance_main.py              # High-performance serving
├── main.py                                  # Main server application
├── login.py                                 # Login endpoints
├── schemas.py                               # API schemas and models
├── config/                                  # Configuration files
├── docs/                                    # Documentation
├── models/                                  # Data models
│   └── (2 Python files)
├── storage/                                 # Storage implementations
│   └── (2 Python files)
├── reference_api/                           # Reference API implementations
│   └── (1 Python file)
└── ui/                                      # UI components
    └── (1 Python file)
```

---

## Development Guidelines

### 1. API Endpoint Development

```python
from fastapi import APIRouter
from serve.schemas import CustomRequest, CustomResponse
from serve.main import require_api_key

router = APIRouter()

@router.post("/custom-endpoint")
@require_api_key
async def custom_endpoint(request: CustomRequest) -> CustomResponse:
    # Implement endpoint logic
    return CustomResponse(result="success")
```

### 2. Observability Integration

```python
from opentelemetry import trace

tracer = trace.get_tracer("lukhas.serve")

@router.post("/monitored-endpoint")
async def monitored_endpoint(request: Request):
    with tracer.start_as_current_span("lukhas.serve.operation"):
        # Endpoint logic with tracing
        pass
```

### 3. Authentication

All protected endpoints must use `require_api_key`:

```python
from serve.main import require_api_key

@router.get("/protected")
@require_api_key
async def protected_endpoint():
    return {"status": "authenticated"}
```

---

## MATRIZ Pipeline Integration

This module operates within the MATRIZ cognitive framework:

- **M (Memory)**: Memory dump endpoints and retrieval
- **A (Attention)**: Focus on user requests and API calls
- **T (Thought)**: Processing through consciousness APIs
- **R (Risk)**: Guardian validation for all operations
- **I (Intent)**: Intent understanding through orchestration
- **A (Action)**: API response generation and delivery

---

## Performance Targets

- **API Latency**: <100ms p95 for simple endpoints
- **Consciousness Queries**: <250ms p95
- **Orchestration Requests**: <500ms p95 (multi-model)
- **Health Checks**: <10ms p95
- **Throughput**: 1000+ req/sec per instance

---

## Dependencies

**Required Modules**:
- `core` - Core system functionality
- `identity` - Authentication and identity management
- `memory` - Memory systems and fold management

---

## Related Modules

- **AI Orchestration** ([../ai_orchestration/](../ai_orchestration/)) - Orchestration logic
- **Identity** ([../identity/](../identity/)) - Identity management
- **Governance** ([../governance/](../governance/)) - Guardian system
- **Consciousness** ([../consciousness/](../consciousness/)) - Consciousness processing

---

## Documentation

- **README**: [serve/README.md](README.md) - Serve overview
- **Docs**: [serve/docs/](docs/) - API documentation and guides
- **Tests**: [serve/tests/](tests/) - Serve test suites
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#serve)

---

**Status**: Integration Lane (L2)
**Manifest**: ✓ module.manifest.json (schema v3.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**Components**: 46 components across 13 Python files + 5 subdirectories
**Test Coverage**: 85.0%
**Last Updated**: 2025-10-18
