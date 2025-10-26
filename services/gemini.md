# Gemini AI Navigation Context
*This file is optimized for Gemini AI navigation and understanding*

---
title: gemini
slug: gemini.md
source: claude.me
optimized_for: gemini_ai
last_updated: 2025-10-26
---

# Services Module - LUKHAS Microservices Architecture

**Module**: services
**Lane**: L2 Integration
**Team**: Core
**Purpose**: Microservice implementations for LUKHAS system components with production-ready infrastructure

---

## Overview

The services module provides production-ready microservice implementations for LUKHAS AI components, currently featuring a complete memory service with API endpoints, circuit breakers, backpressure management, and vector store adapters.

**Key Features**:
- Memory service with full CRUD API
- Circuit breaker pattern implementation
- Backpressure management for high-load scenarios
- Vector store adapters (PostgreSQL + extensible)
- Performance and chaos testing
- Production metrics and monitoring

---

## Architecture

### Module Structure

```
services/
├── README.md                    # Module overview
├── module.manifest.json         # Module metadata
├── memory/                      # Memory microservice
│   ├── __init__.py             # Service initialization
│   ├── api_service.py          # Main service API
│   ├── api_read.py             # Read API endpoints
│   ├── api_write.py            # Write API endpoints
│   ├── backpressure.py         # Backpressure management
│   ├── circuit_breaker.py      # Circuit breaker implementation
│   ├── metrics.py              # Service metrics
│   ├── adapters/               # Storage adapters
│   │   ├── vector_store_base.py    # Base adapter interface
│   │   └── vector_store_pg.py      # PostgreSQL vector store
│   └── tests/
│       ├── test_performance.py  # Performance benchmarks
│       └── test_chaos.py        # Chaos engineering tests
├── schema/                      # Service schemas
├── docs/                        # Documentation
├── tests/                       # Integration tests
└── config/                      # Service configuration
```

---

## Core Components

### 1. Memory Microservice

**Purpose**: Production-ready memory service providing CRUD operations, vector storage, and fold management.

#### API Service (`api_service.py`)

Main service orchestration and initialization:

```python
from services.memory import MemoryService

# Create memory service
service = MemoryService(
    vector_store=postgres_adapter,
    circuit_breaker_enabled=True,
    backpressure_enabled=True,
    max_concurrent_requests=1000,
)

# Start service
await service.start()

# Service provides:
# - RESTful API endpoints
# - Circuit breaker protection
# - Backpressure management
# - Health monitoring
# - Metrics export
```

---

#### Read API (`api_read.py`)

Read operations for memory retrieval:

```python
from services.memory.api_read import (
    get_memory,
    search_memories,
    list_folds,
)

# Get specific memory
memory = await get_memory(
    memory_id="mem_abc123",
    include_metadata=True,
)

# Search memories with vector similarity
results = await search_memories(
    query_vector=query_embedding,
    top_k=10,
    filter={"fold_id": "fold_xyz"},
)

# List all memory folds
folds = await list_folds(
    limit=100,
    offset=0,
    sort_by="created_at",
)
```

**Endpoints**:
- `GET /api/v1/memory/{memory_id}` - Retrieve specific memory
- `POST /api/v1/memory/search` - Vector similarity search
- `GET /api/v1/folds` - List memory folds
- `GET /api/v1/folds/{fold_id}` - Get fold details

---

#### Write API (`api_write.py`)

Write operations for memory creation and updates:

```python
from services.memory.api_write import (
    create_memory,
    update_memory,
    delete_memory,
    create_fold,
)

# Create new memory
memory = await create_memory(
    content="Memory content here",
    vector=embedding_vector,
    fold_id="fold_xyz",
    metadata={
        "source": "consciousness",
        "timestamp": current_time,
    },
)

# Update existing memory
updated = await update_memory(
    memory_id="mem_abc123",
    updates={
        "content": "Updated content",
        "metadata": {"edited": True},
    },
)

# Delete memory
deleted = await delete_memory(memory_id="mem_abc123")

# Create new fold
fold = await create_fold(
    name="conversation_2025_10_02",
    capacity=1000,
)
```

**Endpoints**:
- `POST /api/v1/memory` - Create new memory
- `PUT /api/v1/memory/{memory_id}` - Update memory
- `DELETE /api/v1/memory/{memory_id}` - Delete memory
- `POST /api/v1/folds` - Create new fold

---

### 2. Circuit Breaker (`circuit_breaker.py`)

**Purpose**: Prevents cascade failures by temporarily blocking requests to failing services.

```python
from services.memory.circuit_breaker import CircuitBreaker, CircuitState

# Create circuit breaker
breaker = CircuitBreaker(
    failure_threshold=5,         # Open after 5 failures
    success_threshold=2,         # Close after 2 successes
    timeout=30,                  # Timeout in seconds
    half_open_max_requests=3,   # Max requests in half-open state
)

# Use circuit breaker
@breaker.protected
async def risky_operation():
    # Operation that might fail
    result = await external_api_call()
    return result

# Manual circuit control
if breaker.state == CircuitState.OPEN:
    logger.warning("Circuit breaker OPEN, rejecting requests")
    raise ServiceUnavailableError()
```

**Circuit States**:
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Too many failures, requests rejected immediately
- **HALF_OPEN**: Testing if service recovered, limited requests allowed

**Metrics**:
- Failure count
- Success count
- Circuit state transitions
- Request rejection rate

---

### 3. Backpressure Management (`backpressure.py`)

**Purpose**: Manages system load by throttling requests when capacity is reached.

```python
from services.memory.backpressure import BackpressureManager

# Create backpressure manager
backpressure = BackpressureManager(
    max_concurrent_requests=1000,
    queue_size=5000,
    shed_load_threshold=0.95,    # 95% capacity
    strategy="fifo",              # or "priority", "lifo"
)

# Use backpressure protection
@backpressure.protected
async def process_request(request):
    # Request will be queued if system at capacity
    result = await heavy_processing(request)
    return result

# Check current load
if backpressure.is_overloaded():
    logger.warning(f"System overloaded: {backpressure.current_load():.1%}")
```

**Strategies**:
- **FIFO**: First-in, first-out processing
- **Priority**: High-priority requests processed first
- **LIFO**: Last-in, first-out (newest requests prioritized)
- **Load Shedding**: Reject requests when threshold exceeded

**Metrics**:
- Current concurrent requests
- Queue depth
- Load shedding events
- Average wait time

---

### 4. Vector Store Adapters

#### Base Adapter (`adapters/vector_store_base.py`)

Abstract base for vector storage implementations:

```python
from services.memory.adapters import VectorStoreBase

class CustomVectorStore(VectorStoreBase):
    async def insert(self, vector, metadata):
        # Implement insertion
        pass

    async def search(self, query_vector, top_k):
        # Implement vector similarity search
        pass

    async def delete(self, vector_id):
        # Implement deletion
        pass

    async def update(self, vector_id, updates):
        # Implement update
        pass
```

#### PostgreSQL Adapter (`adapters/vector_store_pg.py`)

Production PostgreSQL vector store using pgvector:

```python
from services.memory.adapters import PostgreSQLVectorStore

# Create PostgreSQL vector store
store = PostgreSQLVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/lukhas",
    table_name="memory_vectors",
    vector_dimensions=1536,  # e.g., for OpenAI embeddings
    index_type="ivfflat",    # or "hnsw"
)

# Initialize database
await store.initialize()

# Insert vector
await store.insert(
    vector=embedding_vector,
    metadata={
        "memory_id": "mem_abc123",
        "fold_id": "fold_xyz",
        "content": "Memory content",
    },
)

# Search similar vectors
results = await store.search(
    query_vector=query_embedding,
    top_k=10,
    filter={"fold_id": "fold_xyz"},
)
```

**Features**:
- pgvector extension for vector similarity
- IVFFLAT and HNSW index support
- Metadata filtering
- Batch operations
- Connection pooling

---

### 5. Service Metrics (`metrics.py`)

**Purpose**: Production metrics for service monitoring.

```python
from services.memory.metrics import (
    MemoryServiceMetrics,
    track_operation,
    record_latency,
)

# Create metrics collector
metrics = MemoryServiceMetrics(
    export_interval=60,  # seconds
    backends=["prometheus"],
)

# Track operations
with track_operation("memory.create"):
    await create_memory(content, vector)

# Record latency manually
record_latency(
    operation="vector.search",
    latency_ms=45.2,
    metadata={"top_k": 10},
)

# Metrics exported:
# - memory_operations_total{operation="create|read|update|delete"}
# - memory_operation_latency_seconds{operation, percentile}
# - memory_fold_count
# - memory_vector_count
# - memory_circuit_breaker_state{state}
# - memory_backpressure_queue_depth
```

---

## Testing

### Performance Tests (`tests/test_performance.py`)

Benchmarks for service performance:

```python
# Test cases:
# - Single memory creation latency (<50ms target)
# - Batch creation throughput (>1000 ops/sec)
# - Vector search latency (<100ms for top-10)
# - Concurrent request handling (1000 concurrent)
# - Memory under load (sustained 10k req/min)

async def test_create_memory_latency():
    start = time.time()
    await create_memory(content, vector)
    latency = (time.time() - start) * 1000
    assert latency < 50, f"Create latency {latency}ms exceeds 50ms target"
```

### Chaos Tests (`tests/test_chaos.py`)

Resilience testing with failure injection:

```python
# Chaos scenarios:
# - Database connection failures
# - Network timeouts
# - Circuit breaker activation
# - Backpressure overflow
# - Vector store unavailability

async def test_circuit_breaker_opens_on_failures():
    # Inject failures
    for _ in range(10):
        with pytest.raises(ServiceError):
            await failing_operation()

    # Verify circuit breaker opened
    assert breaker.state == CircuitState.OPEN
```

---

## Configuration

```yaml
services:
  memory:
    api:
      host: "0.0.0.0"
      port: 8080
      workers: 4
      max_concurrent_requests: 1000

    vector_store:
      adapter: "postgresql"
      connection_string: "${DATABASE_URL}"
      table_name: "memory_vectors"
      vector_dimensions: 1536
      index_type: "ivfflat"
      index_lists: 100

    circuit_breaker:
      enabled: true
      failure_threshold: 5
      success_threshold: 2
      timeout: 30
      half_open_max_requests: 3

    backpressure:
      enabled: true
      max_concurrent_requests: 1000
      queue_size: 5000
      shed_load_threshold: 0.95
      strategy: "priority"

    metrics:
      enabled: true
      export_interval: 60
      backends: ["prometheus"]

    health:
      check_interval: 10  # seconds
      startup_grace_period: 30
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/ services/

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
  CMD curl -f http://localhost:8080/health || exit 1

# Run service
CMD ["python", "-m", "services.memory.api_service"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lukhas-memory-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memory-service
  template:
    metadata:
      labels:
        app: memory-service
    spec:
      containers:
      - name: memory-service
        image: lukhas/memory-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: memory-service-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## Performance Targets

### API Latency
- Memory create: <50ms p95
- Memory read: <20ms p95
- Vector search (top-10): <100ms p95
- Fold list: <30ms p95

### Throughput
- Single-node: >1,000 requests/second
- Clustered (3 nodes): >3,000 requests/second

### Reliability
- Uptime: 99.9%
- Circuit breaker recovery: <60 seconds
- Backpressure queue processing: <1 second average wait

---

## Observability

**Required Spans**:
- `lukhas.services.operation`
- `lukhas.services.memory.api`
- `lukhas.services.memory.vector_store`

**Metrics Exported**:
- Request count by endpoint
- Request latency percentiles (p50, p95, p99)
- Circuit breaker state
- Backpressure queue depth
- Vector store operation latency
- Error rate by type

---

## Future Services

Planned microservices following same architecture:

- **Consciousness Service**: Awareness processing and dream states
- **Identity Service**: Authentication and authorization
- **Guardian Service**: Safety and ethics validation
- **MATRIZ Service**: Pipeline orchestration
- **Analytics Service**: Data analysis and reporting

---

## Related Modules

- **memory/**: Core memory functionality (wrapped by this service)
- **api/**: API definitions and schemas
- **monitoring/**: Service monitoring and alerting
- **telemetry/**: Observability infrastructure
- **deployment/**: Deployment configurations

---

## Quick Reference

| Component | Purpose | Key Metric |
|-----------|---------|-----------|
| `api_service.py` | Main service orchestration | Request throughput |
| `api_read.py` | Read operations | Read latency <20ms |
| `api_write.py` | Write operations | Write latency <50ms |
| `circuit_breaker.py` | Failure protection | Circuit state |
| `backpressure.py` | Load management | Queue depth |
| `vector_store_pg.py` | Vector storage | Search latency <100ms |
| `metrics.py` | Service metrics | Metric export rate |

---

**Module Status**: L2 Integration
**Schema Version**: 1.0.0
**Production Readiness**: Beta (memory service ready for production)
**Last Updated**: 2025-10-18
**Philosophy**: Services should be resilient, observable, and production-ready from day one.


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
