---
title: lukhas_context
slug: interfaces.lukhas_context
owner: T4
lane: labs
star:
stability: experimental
last_reviewed: 2025-10-24
constellation_stars: "⚛️ Anchor · 🔬 Horizon · ✦ Trail"
related_modules: "api_server, router, traces_router"
manifests: "../node_contract.py, ../matriz_node_v1.json"
links: "api_server.py, router.py, traces_router.py"
contracts: "[MatrizNode, MatrizMessage, MatrizResult, MatrizAPI]"
domain: integration, api
stars: "[Skill]"
status: active
tier: T2
updated: 2025-10-24
version: 1.0.0
contract_version: 1.0.0
---
# MATRIZ API Interfaces
## RESTful & WebSocket APIs for External Integration

### Interfaces Module Overview

**Interfaces Module Location**: [matriz/interfaces/](../interfaces/)

- **Purpose**: External API interfaces for MATRIZ cognitive engine integration
- **Architecture**: FastAPI-based REST and WebSocket servers with complete MATRIZ contract support
- **Integration**: Exposes MATRIZ cognitive processing to external systems and applications
- **Contract**: All API endpoints process FROZEN v1.0.0 [node_contract.py](../node_contract.py:1) MatrizMessage/MatrizResult

## Core Interface Components

### **MatrizAPI Server** ([api_server.py:1](api_server.py:1))

**Purpose**: FastAPI REST and WebSocket server for MATRIZ cognitive engine

**Capabilities:**
- RESTful endpoints for synchronous MATRIZ node processing
- WebSocket connections for real-time cognitive streaming
- Query interpretation and natural language processing
- Node management and capability discovery
- Reasoning chain retrieval and provenance querying
- Visualization services and graph rendering

**API Endpoints:**

#### **POST /matriz/process**
Process a MATRIZ message through cognitive pipeline

```bash
curl -X POST https://matriz.lukhas.ai/matriz/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LUKHAS_TOKEN}" \
  -d '{
    "msg_id": "550e8400-e29b-41d4-a716-446655440000",
    "ts": "2025-10-24T10:30:00Z",
    "lane": "prod",
    "glyph": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "kind": "DECISION",
      "version": "1.0.0",
      "tags": {"priority": "high"}
    },
    "payload": {"query": "What is 5 + 3?"},
    "topic": "RESOURCE",
    "guardian_token": "lukhas:prod:api:550e:1729762200000"
  }'

# Response
{
  "ok": true,
  "reasons": ["Processed by math-node v1.0.0"],
  "payload": {"result": 8, "steps": ["5 + 3 = 8"]},
  "trace": {
    "node": "math-node",
    "msg_id": "550e8400-e29b-41d4-a716-446655440000",
    "glyph_kind": "DECISION",
    "processing_time_ms": 42
  },
  "guardian_log": [
    "Guardian validated math-node operation",
    "Topic: RESOURCE, Lane: prod"
  ]
}
```

#### **POST /matriz/query**
Natural language query processing

```bash
curl -X POST https://matriz.lukhas.ai/matriz/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calculate the sum of 5 and 3",
    "context": {"user_id": "user123"},
    "lane": "prod"
  }'

# Automatically converts to MatrizMessage and routes to appropriate node
```

#### **GET /matriz/nodes**
List available MATRIZ nodes and their capabilities

```bash
curl https://matriz.lukhas.ai/matriz/nodes

# Response
{
  "nodes": [
    {
      "name": "math-node",
      "version": "1.0.0",
      "capabilities": ["arithmetic", "algebra", "symbolic"],
      "glyph_kinds": ["DECISION", "THOUGHT"],
      "topics": ["RESOURCE", "TREND"],
      "status": "healthy"
    },
    {
      "name": "fact-node",
      "version": "1.0.0",
      "capabilities": ["knowledge", "semantic", "graph"],
      "glyph_kinds": ["MEMORY", "CONTEXT"],
      "topics": ["RESOURCE", "BREAKTHROUGH"],
      "status": "healthy"
    }
  ]
}
```

#### **GET /matriz/trace/{msg_id}**
Retrieve complete reasoning trace for a processed message

```bash
curl https://matriz.lukhas.ai/matriz/trace/550e8400-e29b-41d4-a716-446655440000

# Response
{
  "msg_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_chain": [
    {
      "node": "query-processor",
      "timestamp": "2025-10-24T10:30:00.100Z",
      "action": "parse_query"
    },
    {
      "node": "math-node",
      "timestamp": "2025-10-24T10:30:00.142Z",
      "action": "arithmetic_operation",
      "details": {"operation": "add", "operands": [5, 3]}
    }
  ],
  "causal_links": [
    {"from": "query-processor", "to": "math-node", "type": "REASONING"}
  ],
  "guardian_validations": [
    {"timestamp": "2025-10-24T10:30:00.095Z", "result": "approved"}
  ]
}
```

#### **WebSocket /matriz/stream**
Real-time cognitive processing stream

```javascript
const ws = new WebSocket('wss://matriz.lukhas.ai/matriz/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    filters: {
      glyph_kinds: ['DECISION', 'INTENT'],
      topics: ['BREAKTHROUGH']
    }
  }));
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('MATRIZ Result:', result);
  // Real-time cognitive processing results
};
```

### **Router** ([router.py:1](router.py:1))

**Purpose**: Intelligent routing of MatrizMessages to appropriate nodes

**Capabilities:**
- Topic-based routing with configurable rules
- GLYPH kind-based node selection
- Load balancing across multiple node instances
- Fallback routing and error handling
- Performance-based routing optimization

**Routing Logic:**
```python
def route_message(msg: MatrizMessage) -> MatrizNode:
    """
    Route MatrizMessage to optimal node based on:
    1. GLYPH kind (MEMORY → FactNode, DECISION → MathNode)
    2. Topic (RESOURCE, TREND, BREAKTHROUGH, CONTRADICTION)
    3. Node capabilities and health status
    4. Current load and performance metrics
    """
    candidates = registry.find_nodes(
        glyph_kind=msg.glyph.kind,
        topic=msg.topic,
        min_health_score=0.8
    )

    # Load-balance across healthy nodes
    return select_least_loaded(candidates)
```

### **TracesRouter** ([traces_router.py:1](traces_router.py:1))

**Purpose**: Complete reasoning path capture and provenance navigation (11KB)

**Capabilities:**
- Real-time cognitive process logging and tracing
- Provenance tracking with causal relationship mapping
- Step-by-step thought process reconstruction
- Causal analysis and reasoning chain exploration
- Export traces for external analysis and auditing

**Trace Data Structure:**
```python
{
  "trace_id": "trace-550e8400",
  "msg_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp_start": "2025-10-24T10:30:00.000Z",
  "timestamp_end": "2025-10-24T10:30:00.200Z",
  "duration_ms": 200,
  "nodes_visited": [
    {
      "node": "query-processor",
      "duration_ms": 50,
      "input": {"query": "What is 5 + 3?"},
      "output": {"parsed": {"operation": "add", "operands": [5, 3]}}
    },
    {
      "node": "math-node",
      "duration_ms": 42,
      "input": {"operation": "add", "operands": [5, 3]},
      "output": {"result": 8, "steps": ["5 + 3 = 8"]}
    }
  ],
  "causal_links": [
    {
      "from": "query-processor",
      "to": "math-node",
      "type": "TEMPORAL",
      "reason": "Query parsing resulted in math operation"
    }
  ],
  "guardian_events": [
    {
      "timestamp": "2025-10-24T10:30:00.095Z",
      "validation": "approved",
      "reason": "Mathematical operation within constraints"
    }
  ]
}
```

## API Architecture

### **Request/Response Flow**

```
External Client → FastAPI Server → MatrizMessage Creation → Router
        │               │                  │                   │
   HTTP/WS ← JSON ← MatrizResult ← Node Processing
        │               │                  │                   │
  Response ← Serialize ← Trace Capture ← Guardian Validation
```

### **Authentication & Authorization**

**Bearer Token Authentication:**
```bash
Authorization: Bearer ${LUKHAS_TOKEN}
```

**Guardian Token Generation:**
```python
from matriz.node_contract import mk_guardian_token
import uuid

guardian_token = mk_guardian_token(
    node_name="api-gateway",
    lane="prod",
    msg_id=uuid.uuid4(),
    epoch_ms=int(time.time() * 1000)
)
# Result: "lukhas:prod:api-gateway:550e8400:1729762200000"
```

**Lane-Based Access Control:**
- **Experimental Lane**: Open access for research
- **Candidate Lane**: Requires basic authentication
- **Production Lane**: Requires full authentication + Guardian validation

## Performance & Quality

### **Performance Targets**

- **API Latency**: <50ms overhead on top of MATRIZ processing
- **Throughput**: 1000+ requests per second sustained
- **WebSocket Latency**: <10ms for real-time streaming
- **Concurrent Connections**: 10,000+ WebSocket connections

### **Quality Standards**

- **99.9% Uptime**: High availability for production deployments
- **Complete API Documentation**: OpenAPI/Swagger specification
- **Type Safety**: Full TypeScript types for client libraries
- **Error Handling**: Graceful degradation with informative errors

## Production Readiness

**Interfaces Module Status**: 65% production ready

### ✅ Completed

- [x] FastAPI server with REST endpoints
- [x] WebSocket support for real-time streaming
- [x] MatrizMessage/MatrizResult serialization
- [x] Intelligent routing with load balancing
- [x] TracesRouter with complete provenance (11KB)
- [x] Guardian token integration
- [x] OpenAPI/Swagger documentation
- [x] Health check endpoints

### 🔄 In Progress

- [ ] Rate limiting and throttling
- [ ] Advanced caching strategies
- [ ] Distributed API gateway for horizontal scaling
- [ ] Client SDKs (Python, JavaScript, Go)

### 📋 Pending

- [ ] Production deployment configurations
- [ ] Enterprise security audit
- [ ] Load testing and capacity planning
- [ ] Comprehensive API versioning strategy

## API Documentation

**Full API Documentation**: [API_README.md](../API_README.md:1)

**OpenAPI Specification:** Available at `/matriz/docs` endpoint

```bash
# Access interactive API docs
open https://matriz.lukhas.ai/matriz/docs

# Download OpenAPI spec
curl https://matriz.lukhas.ai/matriz/openapi.json > matriz-api.json
```

## Related Documentation

### **Interface Contexts**

- [../lukhas_context.md](../lukhas_context.md:1) - MATRIZ cognitive engine overview
- [../core/lukhas_context.md](../core/lukhas_context.md:1) - Core orchestration
- [../adapters/lukhas_context.md](../adapters/lukhas_context.md:1) - Adapter integration
- [../nodes/lukhas_context.md](../nodes/lukhas_context.md:1) - Specialized nodes
- [../visualization/lukhas_context.md](../visualization/lukhas_context.md:1) - Visualization APIs

### **Technical Specifications**

- [../node_contract.py](../node_contract.py:1) - FROZEN v1.0.0 canonical interface
- [../matriz_node_v1.json](../matriz_node_v1.json:1) - JSON Schema v1.1
- [../API_README.md](../API_README.md:1) - Complete API documentation
- [../the_plan.md](../the_plan.md:1) - Implementation plan

### **Integration Documentation**

- [../../audit/MATRIZ_READINESS.md](../../audit/MATRIZ_READINESS.md:1) - Production readiness
- [../../branding/MATRIZ_BRAND_GUIDE.md](../../branding/MATRIZ_BRAND_GUIDE.md:1) - API naming conventions
- [../../docs/MATRIZ_TAIL_LATENCY_OPTIMIZATION.md](../../docs/MATRIZ_TAIL_LATENCY_OPTIMIZATION.md:1) - Performance optimization

---

**Interfaces Module**: FastAPI REST + WebSocket | **Contract**: v1.0.0 (FROZEN)
**Features**: Node routing, trace capture, real-time streaming | **Production**: 65% ready
**Performance**: <50ms overhead, 1000+ req/s | **Uptime**: 99.9% target | **Docs**: OpenAPI/Swagger
