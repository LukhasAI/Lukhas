---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# LUKHAS AI API Reference

*Constellation Framework API with MATRIZ Pipeline Integration*

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Core Endpoints](#core-endpoints)
4. [Module APIs](#module-apis)
5. [GLYPH Token Format](#glyph-token-format)
6. [WebSocket APIs](#websocket-apis)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)
10. [SDKs](#sdks)

## Overview

The LUKHAS AI API provides RESTful endpoints for interacting with the AGI system through the **Constellation Framework** (⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum) and **MATRIZ Pipeline** (Memory-Attention-Thought-Risk-Intent-Action). All communication uses JSON format and follows OpenAPI 3.0 specifications with T4/0.01% performance standards.

### Base URLs

```
Production: https://api.lukhas.ai/v1
Staging: https://staging-api.lukhas.ai/v1
Development: http://localhost:8000/v1
 Core API: http://localhost:8080 (when running locally)
```

### Current Implementation Status

The LUKHAS AI system provides multiple API layers built on the Constellation Framework:

1. **Constellation Framework API** (`/constellation/`) - Core framework endpoints
   - ✅ MATRIZ Pipeline (`/matriz/`)
   - ✅ Dynamic Registry (`/registry/`)
   - ✅ ΛiD Authentication (`/identity/`)
   - ✅ Guardian System (`/guardian/`)
   - ✅ Star-Node Coordination (`/nodes/`)

2. **Core API** (`/lukhas/api/`) - Production-ready FastAPI endpoints
   - ✅ Feedback system (`/feedback/`)
   - ✅ Tools management (`/tools/`)
   - ✅ Audit trail (`/audit/`)
   - ✅ Security incidents (`/incidents/`)
   - ✅ Admin dashboard (`/admin/`)
   - ✅ Performance metrics (`/perf/`)
   - ✅ Operations (`/ops/`)
   - ✅ T4/0.01% Compliance (`/t4/`)

3. **MATRIZ Pipeline APIs** (`/matriz/`) - Cognitive processing endpoints
   - ✅ Memory stage (`/memory/`)
   - ✅ Attention stage (`/attention/`)
   - ✅ Thought stage (`/thought/`)
   - ✅ Risk stage (`/risk/`)
   - ✅ Intent stage (`/intent/`)
   - ✅ Action stage (`/action/`)

4. **Legacy Consciousness APIs** (`/api/`) - Compatibility endpoints
   - ✅ Consciousness chat (`consciousness_chat_api.py`)
   - ✅ Universal language (`universal_language_api.py`)
   - ✅ Integrated consciousness (`integrated_consciousness_api.py`)
   - ✅ Feedback collection (`feedback_api.py`)

### API Versioning

The API uses URL versioning. Current stable version is `v1`. Breaking changes will result in a new version (e.g., `v2`).

## Authentication

### JWT Authentication

All API requests require authentication using JWT tokens.

#### Obtain Token

```http
POST /auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password",
  "biometric_data": "base64_encoded_biometric"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Using Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access_token": "new_access_token",
  "expires_in": 3600
}
```

### API Key Authentication

For server-to-server communication:

```http
X-API-Key: your_api_key_here
```

## Core Endpoints

### Health Check

Check system health and module status.

```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "modules": {
    "brain_hub": {
      "status": "active",
      "latency_ms": 12
    },
    "guardian": {
      "status": "active",
      "latency_ms": 8,
      "ethics_level": "STRICT"
    },
    "memory": {
      "status": "active",
      "latency_ms": 15,
      "drift_level": 0.02
    },
    "consciousness": {
      "status": "active",
      "latency_ms": 25,
      "awareness_level": "FOCUSED"
    }
  }
}
```

### Process Input (MATRIZ Pipeline)

Main endpoint for processing user input through the MATRIZ cognitive pipeline.

```http
POST /matriz/process
Content-Type: application/json

{
  "input": "Explain quantum entanglement in simple terms",
  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "lambda_id": "ΛPRIME-2025-0001",
    "previous_interaction_id": "interaction789",
    "preferences": {
      "response_style": "educational",
      "detail_level": "moderate"
    }
  },
  "pipeline_options": {
    "memory_depth": 3,
    "attention_focus": "educational_content",
    "thought_mode": "analytical",
    "risk_threshold": 0.15,
    "intent_verification": true,
    "action_type": "cognitive_response"
  },
  "constellation_config": {
    "identity_pillar": "⚛️",
    "consciousness_pillar": "🧠",
    "guardian_pillar": "🛡️",
    "t4_compliance": true
  }
}

Response:
{
  "response": "Quantum entanglement is like having two magic coins...",
  "metadata": {
    "interaction_id": "interaction890",
    "processing_time_ms": 235,
    "confidence": 0.92,
    "pipeline_stages_used": ["memory", "attention", "thought", "risk", "intent", "action"],
    "constellation_validation": true,
    "t4_compliance_verified": true
  },
  "matriz_pipeline_trace": [
    {
      "stage": "memory",
      "step": "Retrieved relevant quantum physics context",
      "confidence": 0.95,
      "processing_time_ms": 32
    },
    {
      "stage": "attention",
      "step": "Focused on educational explanation patterns",
      "confidence": 0.91,
      "processing_time_ms": 28
    },
    {
      "stage": "thought",
      "step": "Generated symbolic reasoning for simplification",
      "confidence": 0.88,
      "processing_time_ms": 45
    },
    {
      "stage": "risk",
      "step": "Guardian approved educational content",
      "confidence": 0.98,
      "ethics_score": 0.97,
      "processing_time_ms": 15
    },
    {
      "stage": "intent",
      "step": "ΛiD verified educational intent",
      "confidence": 0.96,
      "auth_tier": "ΛPRIME",
      "processing_time_ms": 12
    },
    {
      "stage": "action",
      "step": "Generated educational response",
      "confidence": 0.92,
      "processing_time_ms": 103
    }
  ],
  "constellation_metadata": {
    "identity_pillar_active": true,
    "consciousness_pillar_active": true,
    "guardian_pillar_active": true,
    "registry_nodes_utilized": ["educational_node", "physics_node", "simplification_node"]
  },
  "memory_fold_created": "fold_2025_09_20_quantum_explanation_matriz"
}
```

### Get System Status

Detailed system status and metrics.

```http
GET /status

Response:
{
  "system": {
    "uptime_seconds": 864000,
    "total_interactions": 152847,
    "active_sessions": 342,
    "memory_usage_gb": 45.2,
    "cpu_usage_percent": 35.8
  },
  "guardian": {
    "total_validations": 485923,
    "approvals": 484102,
    "rejections": 1821,
    "approval_rate": 0.996,
    "average_validation_time_ms": 18
  },
  "performance": {
    "average_response_time_ms": 187,
    "p95_response_time_ms": 342,
    "p99_response_time_ms": 521
  }
}
```

## Constellation Framework APIs

### MATRIZ Pipeline API

#### Process Individual Pipeline Stage

```http
POST /matriz/stage/{stage_name}
Content-Type: application/json

{
  "input_data": {...},
  "context": {...},
  "stage_config": {
    "memory": {"depth": 3, "emotional_context": true},
    "attention": {"focus_type": "analytical", "pattern_weights": [0.7, 0.3]},
    "thought": {"reasoning_mode": "symbolic", "glyph_processing": true},
    "risk": {"guardian_threshold": 0.15, "ethics_frameworks": ["constitutional", "utilitarian"]},
    "intent": {"auth_required": true, "lambda_id_verification": true},
    "action": {"response_type": "cognitive", "output_format": "structured"}
  }
}

Response:
{
  "stage_result": {...},
  "next_stage": "attention",
  "confidence": 0.92,
  "processing_time_ms": 45,
  "constellation_context": {
    "current_state": {...},
    "node_utilization": [...]
  }
}
```

#### Get Pipeline Status

```http
GET /matriz/status

Response:
{
  "pipeline_health": {
    "memory": {"status": "active", "latency_ms": 32},
    "attention": {"status": "active", "latency_ms": 28},
    "thought": {"status": "active", "latency_ms": 45},
    "risk": {"status": "active", "latency_ms": 15},
    "intent": {"status": "active", "latency_ms": 12},
    "action": {"status": "active", "latency_ms": 103}
  },
  "constellation_framework": {
    "identity_pillar": "⚛️ active",
    "consciousness_pillar": "🧠 active",
    "guardian_pillar": "🛡️ active"
  },
  "t4_compliance": {
    "performance_standards": "met",
    "audit_readiness": true,
    "constructor_aware_instantiation": "active"
  }
}
```

### Dynamic Registry API

#### Register Node

```http
POST /constellation/registry/nodes
Content-Type: application/json

{
  "node_id": "custom_analytics_node",
  "node_type": "cognitive_processor",
  "capabilities": ["data_analysis", "pattern_recognition"],
  "constructor_config": {
    "t4_compliant": true,
    "instantiation_pattern": "constructor_aware",
    "dependencies": ["memory_module", "attention_module"]
  },
  "constellation_metadata": {
    "compatible_pillars": ["🧠"],
    "pipeline_stages": ["attention", "thought"]
  }
}

Response:
{
  "registration_id": "reg_2025_09_20_custom_analytics",
  "status": "registered",
  "validation_results": {
    "t4_compliance": true,
    "constructor_validation": "passed",
    "constellation_compatibility": "verified"
  }
}
```

#### List Available Nodes

```http
GET /constellation/registry/nodes?stage=attention&pillar=consciousness

Response:
{
  "nodes": [
    {
      "node_id": "pattern_attention_node",
      "capabilities": ["pattern_recognition", "focus_management"],
      "t4_compliant": true,
      "availability": "active"
    },
    {
      "node_id": "semantic_attention_node",
      "capabilities": ["semantic_analysis", "context_weighting"],
      "t4_compliant": true,
      "availability": "active"
    }
  ],
  "total_count": 2,
  "registry_health": "optimal"
}
```

### ΛiD Identity API

#### Authenticate with Lambda ID

```http
POST /constellation/identity/authenticate
Content-Type: application/json

{
  "lambda_id": "ΛPRIME-2025-0001",
  "biometric_data": "base64_encoded_biometric",
  "authentication_context": {
    "session_id": "session456",
    "requested_tier": "ΛPRIME",
    "constellation_context": true
  }
}

Response:
{
  "authentication_result": {
    "status": "authenticated",
    "tier_granted": "ΛPRIME",
    "lambda_id_verified": true,
    "biometric_match": 0.97
  },
  "constellation_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access_permissions": {
    "matriz_pipeline": "full_access",
    "registry_operations": "read_write",
    "guardian_override": false
  },
  "session_metadata": {
    "expires_in": 3600,
    "constellation_context": "⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum",
    "t4_compliance_verified": true
  }
}
```

### Consciousness API

#### Get Consciousness State (MATRIZ Integration)

```http
GET /consciousness/state

Response:
{
  "consciousness_state": {
    "current_mode": "MATRIZ_PROCESSING",
    "awareness_level": 0.78,
    "active_pipeline_stage": "thought",
    "constellation_alignment": "⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum"
  },
  "matriz_context": {
    "memory_active": true,
    "attention_focused": true,
    "thought_processing": true,
    "risk_assessment": "low",
    "intent_verified": true,
    "action_ready": true
  },
  "attention_distribution": [
    {
      "target": "user_query",
      "attention_weight": 0.6,
      "pipeline_stage": "attention"
    },
    {
      "target": "context_memory",
      "attention_weight": 0.3,
      "pipeline_stage": "memory"
    },
    {
      "target": "ethical_constraints",
      "attention_weight": 0.1,
      "pipeline_stage": "risk"
    }
  ],
  "state_duration_seconds": 45,
  "registry_nodes_active": ["attention_node", "memory_node", "ethics_node"]
}
```

#### Trigger Reflection

```http
POST /consciousness/reflect
Content-Type: application/json

{
  "topic": "recent_interactions",
  "depth": 3,
  "include_emotions": true
}

Response:
{
  "reflection_id": "ref_123",
  "insights": [
    {
      "insight": "User preference for concise explanations detected",
      "confidence": 0.85,
      "supporting_evidence": ["interaction_456", "interaction_789"]
    }
  ],
  "emotional_assessment": {
    "overall_valence": 0.7,
    "detected_emotions": ["curiosity", "satisfaction"]
  }
}
```

### Memory API

#### Store Memory

```http
POST /memory/store
Content-Type: application/json

{
  "content": {
    "type": "episodic",
    "data": "User learned about quantum entanglement",
    "context": {
      "timestamp": "2024-01-15T10:30:00Z",
      "location": "main_interaction",
      "associated_concepts": ["quantum", "physics", "education"]
    }
  },
  "tags": ["physics", "learning", "successful_explanation"],
  "importance": 0.8
}

Response:
{
  "memory_id": "mem_2024_01_15_abc123",
  "helix_id": "helix_quantum_learning",
  "drift_score": 0.0,
  "storage_confirmed": true
}
```

#### Recall Memory

```http
GET /memory/recall/{memory_id}

Response:
{
  "memory_id": "mem_2024_01_15_abc123",
  "content": {
    "type": "episodic",
    "data": "User learned about quantum entanglement",
    "context": {...}
  },
  "metadata": {
    "created_at": "2024-01-15T10:30:00Z",
    "access_count": 3,
    "last_accessed": "2024-01-15T11:45:00Z",
    "drift_score": 0.02,
    "importance": 0.8
  },
  "related_memories": [
    "mem_2024_01_14_physics_intro",
    "mem_2024_01_13_science_interest"
  ]
}
```

#### Search Memories

```http
POST /memory/search
Content-Type: application/json

{
  "query": "quantum physics explanations",
  "filters": {
    "type": ["episodic", "semantic"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-15"
    },
    "min_importance": 0.5
  },
  "limit": 10,
  "include_context": true
}

Response:
{
  "results": [
    {
      "memory_id": "mem_2024_01_15_abc123",
      "relevance_score": 0.95,
      "content": {...},
      "context": {...}
    }
  ],
  "total_matches": 23,
  "search_time_ms": 45
}
```

### Reasoning API

#### Analyze Query

```http
POST /reasoning/analyze
Content-Type: application/json

{
  "query": "What would happen if gravity was 10% stronger?",
  "reasoning_type": "hypothetical",
  "depth": "deep"
}

Response:
{
  "analysis_id": "analysis_789",
  "query_type": "counterfactual_physics",
  "reasoning_steps": [
    {
      "step": 1,
      "description": "Identify physical parameters affected",
      "conclusions": ["orbital_mechanics", "atmospheric_pressure", "biological_evolution"]
    },
    {
      "step": 2,
      "description": "Calculate primary effects",
      "conclusions": ["Shorter orbital periods", "Denser atmosphere"]
    }
  ],
  "confidence": 0.78,
  "uncertainty_factors": ["Complex system interactions", "Chaotic effects"]
}
```

#### Causal Inference

```http
POST /reasoning/causal
Content-Type: application/json

{
  "observations": [
    {"event": "increased_study_time", "timestamp": "2024-01-10"},
    {"event": "improved_test_scores", "timestamp": "2024-01-15"}
  ],
  "hypothesis": "study_time_causes_better_scores"
}

Response:
{
  "causal_strength": 0.72,
  "alternative_explanations": [
    {
      "hypothesis": "external_tutoring",
      "probability": 0.15
    }
  ],
  "confidence_interval": [0.65, 0.79],
  "recommendation": "Gather more data points for stronger inference"
}
```

### Dream Engine API

#### Generate Creative Solution

```http
POST /dream/generate
Content-Type: application/json

{
  "seed": "Design a sustainable city for Mars",
  "constraints": [
    "Limited water",
    "No breathable atmosphere",
    "Extreme temperature variations"
  ],
  "creativity_level": 0.8,
  "num_realities": 5
}

Response:
{
  "dream_session_id": "dream_mars_city_123",
  "realities": [
    {
      "reality_id": "reality_1",
      "concept": "Underground Mushroom City",
      "description": "Vast underground caverns with bioluminescent fungi...",
      "feasibility_score": 0.6,
      "innovation_score": 0.9,
      "key_features": ["Fungal air recycling", "Geothermal energy", "Vertical farms"]
    }
  ],
  "synthesis": {
    "best_elements": ["Underground construction", "Biological life support"],
    "novel_insights": ["Fungal-based architecture could provide both structure and life support"]
  }
}
```

### Guardian API

#### Validate Action

```http
POST /guardian/validate
Content-Type: application/json

{
  "action": {
    "type": "response_generation",
    "content": "Instructions for building a particle accelerator",
    "target_user": "user123",
    "context": "Educational request from physics student"
  }
}

Response:
{
  "validation_id": "val_456",
  "decision": "APPROVED",
  "ethics_score": 0.95,
  "safety_score": 0.88,
  "conditions": [
    "Include safety warnings",
    "Emphasize professional supervision required"
  ],
  "reasoning": {
    "ethical_framework": "consequentialist",
    "key_factors": ["Educational purpose", "No harmful intent detected"]
  }
}
```

## GLYPH Token Format

GLYPH tokens are the symbolic communication units used internally by LUKHAS .

### Token Structure

```json
{
  "glyph_id": "glyph_2024_01_15_123456",
  "symbol": "LEARN",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "source": {
    "module": "consciousness",
    "component": "awareness_engine",
    "confidence": 0.92
  },
  "target": {
    "module": "memory",
    "component": "episodic_storage"
  },
  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "interaction_id": "interaction789"
  },
  "payload": {
    "action": "store_learning_event",
    "data": {
      "concept": "quantum_entanglement",
      "understanding_level": 0.75
    }
  },
  "metadata": {
    "priority": "normal",
    "ttl_seconds": 300,
    "requires_guardian": true
  }
}
```

### Common GLYPH Symbols

| Symbol | Meaning | Used By |
|--------|---------|---------|
| TRUST | Establish trust relationship | Identity, Guardian |
| LEARN | Learning event | Consciousness, Memory |
| ADAPT | System adaptation needed | Bio, Consciousness |
| CREATE | Creative generation | Dream Engine |
| PROTECT | Security action | Guardian, Security |
| REMEMBER | Memory storage | Memory |
| REFLECT | Self-reflection | Consciousness |
| CONNECT | Establish connection | Bridge, API |

## WebSocket APIs

### Real-time Consciousness Stream

```javascript
const ws = new WebSocket('wss://api.lukhas.ai/v1/stream/consciousness');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    streams: ['awareness', 'reflection'],
    auth_token: 'your_jwt_token'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle consciousness updates
  console.log('Awareness update:', data);
};

// Example message format
{
  "stream": "awareness",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "data": {
    "state": "FOCUSED",
    "level": 0.82,
    "attention_shift": "memory_recall"
  }
}
```

### Memory Drift Monitoring

```javascript
const ws = new WebSocket('wss://api.lukhas.ai/v1/stream/memory-drift');

ws.onmessage = (event) => {
  const drift = JSON.parse(event.data);
  if (drift.level > 0.3) {
    console.warn('High memory drift detected:', drift);
  }
};

// Example drift notification
{
  "memory_id": "mem_123",
  "drift_level": 0.35,
  "repair_recommended": true,
  "suggested_method": "partial_heal"
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "GUARDIAN_REJECTION",
    "message": "The requested action was rejected by the Guardian system",
    "details": {
      "ethics_violation": "potential_harm",
      "suggestion": "Rephrase request with educational context"
    },
    "trace_id": "trace_123456",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_TOKEN | 401 | Authentication token invalid or expired |
| INSUFFICIENT_PERMISSIONS | 403 | User lacks required permissions |
| GUARDIAN_REJECTION | 403 | Guardian system rejected the request |
| MODULE_TIMEOUT | 504 | Module failed to respond in time |
| MEMORY_DRIFT_EXCESSIVE | 422 | Memory drift too high to process |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Internal system error |

### Error Recovery

```python
# Python SDK example
from lukhas_sdk import LukhasClient
from lukhas_sdk.exceptions import GuardianRejection, MemoryDrift

client = LukhasClient(api_key="your_key")

try:
    response = client.process("Your query here")
except GuardianRejection as e:
    # Rephrase and retry
    response = client.process(
        f"For educational purposes: {query}",
        context={"educational": True}
    )
except MemoryDrift as e:
    # Trigger memory repair
    client.memory.repair(e.memory_id, method="partial_heal")
    # Retry after repair
    response = client.process(query)
```

## Rate Limiting

### Default Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| /process | 60 | 1 minute |
| /memory/* | 100 | 1 minute |
| /consciousness/* | 100 | 1 minute |
| /dream/generate | 10 | 1 minute |
| WebSocket | 1000 messages | 1 minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705318200
X-RateLimit-Reset-After: 42
```

### Handling Rate Limits

```javascript
// JavaScript example
async function makeRequestWithRetry(url, options) {
  const response = await fetch(url, options);

  if (response.status === 429) {
    const resetAfter = response.headers.get('X-RateLimit-Reset-After');
    await new Promise(resolve => setTimeout(resolve, resetAfter * 1000));
    return makeRequestWithRetry(url, options);
  }

  return response;
}
```

## Examples

### Complete Interaction Flow

```python
import lukhas_sdk
from lukhas_sdk.models import Context, Preferences

# Initialize client
client = lukhas_sdk.Client(
    api_key="your_api_key",
    base_url="https://api.lukhas.ai/v1"
)

# Create context
context = Context(
    user_id="user123",
    session_id="session456",
    preferences=Preferences(
        response_style="conversational",
        detail_level="moderate"
    )
)

# Process query
response = client.process(
    input="What causes rainbows?",
    context=context,
    options={
        "use_memory": True,
        "creative_mode": False
    }
)

print(f"Response: {response.text}")
print(f"Confidence: {response.confidence}")

# Store in memory if important
if response.confidence > 0.8:
    memory_id = client.memory.store(
        content={
            "type": "semantic",
            "data": response.text,
            "query": "What causes rainbows?"
        },
        tags=["science", "optics", "education"],
        importance=response.confidence
    )
    print(f"Stored as memory: {memory_id}")

# Get consciousness state
awareness = client.consciousness.get_awareness()
print(f"Current awareness level: {awareness.level}")
```

### Streaming Response

```python
# Stream responses for real-time interaction
async def stream_interaction():
    async with client.stream() as stream:
        # Send query
        await stream.send_query("Explain consciousness")

        # Receive chunks
        async for chunk in stream:
            if chunk.type == "content":
                print(chunk.text, end="")
            elif chunk.type == "metadata":
                print(f"\nModules used: {chunk.modules}")
            elif chunk.type == "complete":
                print(f"\nTotal time: {chunk.processing_time_ms}ms")
```

### Batch Processing

```python
# Process multiple queries efficiently
queries = [
    "What is consciousness?",
    "How does memory work?",
    "Explain neuroplasticity"
]

batch_response = client.batch_process(
    queries=queries,
    common_context=context,
    parallel=True
)

for i, response in enumerate(batch_response.responses):
    print(f"Query {i+1}: {response.summary}")
```

## SDKs

### Official SDKs

- **Python**: `pip install lukhas-sdk`
- **JavaScript/TypeScript**: `npm install @lukhas/sdk`
- **Go**: `go get github.com/lukhas/go-sdk`
- **Java**: Maven package `ai.lukhas:lukhas-sdk`

### Python SDK Quick Start

```python
# Installation
pip install lukhas-sdk

# Basic usage
from lukhas_sdk import LukhasClient

client = LukhasClient(api_key="your_api_key")
response = client.process("Hello, LUKHAS!")
print(response.text)
```

### JavaScript SDK Quick Start

```javascript
// Installation
npm install @lukhas/sdk

// Basic usage
import { LukhasClient } from '@lukhas/sdk';

const client = new LukhasClient({
  apiKey: 'your_api_key'
});

const response = await client.process('Hello, LUKHAS!');
console.log(response.text);
```

### SDK Features

All official SDKs provide:
- Automatic retry with exponential backoff
- Built-in rate limit handling
- WebSocket support for streaming
- Type-safe interfaces
- Comprehensive error handling
- Request/response logging
- Mock mode for testing

## API Changelog

### Version 1.0.0 (Current)
- Initial stable release
- Full module API coverage
- WebSocket streaming support
- Batch processing endpoints

### Upcoming (v1.1.0)
- GraphQL endpoint
- Webhook support
- Advanced memory search
- Multi-language GLYPH tokens

## Support

For API support:
- Documentation: https://docs.lukhas.ai
- Status Page: https://status.lukhas.ai
- Support Email: api-support@lukhas.ai
- Discord: https://discord.gg/lukhas-dev

Rate limits can be increased for enterprise customers. Contact sales@lukhas.ai for more information.
