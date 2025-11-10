# Dream Engine API - Complete Documentation

**Version**: 1.0.0
**Status**: Production Ready
**Base URL**: `http://localhost:8000` (development) | `https://api.lukhas.ai/dream` (production)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Process Dream](#process-dream)
  - [Get Dream](#get-dream)
  - [List Dreams](#list-dreams)
  - [Engine Status](#engine-status)
  - [Memory Snapshot](#memory-snapshot)
  - [Get Fold Snapshots](#get-fold-snapshots)
  - [Get Fold Statistics](#get-fold-statistics)
  - [Sync Memory Fold](#sync-memory-fold)
- [Data Models](#data-models)
- [Code Examples](#code-examples)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [OpenAPI Specification](#openapi-specification)
- [Interactive Documentation](#interactive-documentation)
- [Deployment Guide](#deployment-guide)

---

## Overview

The **LUKHAS Dream Engine API** provides FastAPI-powered endpoints for quantum-enhanced dream processing, memory consolidation, and consciousness simulation. It combines cutting-edge cognitive science with practical AI applications.

### Key Capabilities

- **Quantum-Inspired Processing**: Leverage bio-oscillators for enhanced dream analysis
- **Memory Consolidation**: Transform short-term memories into long-term insights
- **Symbolic Analysis**: Extract symbolic meaning and emotional patterns
- **Dream Reflection**: Multi-layer introspective processing
- **Memory Recurrence**: Persistent dream snapshots with fold-based organization
- **Real-time Status**: Monitor dream engine activity and quantum coherence

### Architecture

```
┌─────────────────┐
│  FastAPI Server │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Dream   │──► Quantum-Inspired
    │  Engine  │    Processing (QI)
    └────┬─────┘
         │
    ┌────▼─────────┐
    │   Memory     │──► Reflection Loop
    │ Consolidation│    Bio-Rhythm Sync
    └──────────────┘
```

---

## Features

### ⭐ Tier-Based Access (Planned)

| Tier | Features | Status |
|------|----------|--------|
| **Tier 1** | Basic dream processing, standard reflection | TODO |
| **Tier 2** | Quantum enhancement, memory snapshots | TODO |
| **Tier 3** | Advanced symbolics, fold management, custom processing | TODO |

**Note**: Tier validation is planned but not yet implemented. See TODOs in implementation for roadmap.

### 🔬 Processing Features

- **Quantum Coherence**: Configurable coherence thresholds for dream state analysis
- **Emotional Enhancement**: Bio-oscillator-based emotional state processing
- **Symbolic Tagging**: Custom symbolic annotations for dream content
- **Memory Folds**: Organize dreams into persistent memory structures
- **Drift Monitoring**: Track convergence and drift metrics over time

---

## Authentication

### Current Status: ⚠️ OPEN ACCESS

**Important**: The current implementation does **NOT** have authentication enabled. All endpoints are publicly accessible.

### Planned Authentication System

```python
# Future implementation with tier-based auth
from matriz.consciousness.dream.oneiric.auth import oneiric_tier_required

@app.post("/dream/process")
@oneiric_tier_required(tier=2)  # Requires Tier 2 access
async def process_dream(request: DreamRequest, user: User = Depends(get_current_user)):
    user_id = user.id
    tier = user.tier
    # ... tier-based processing
```

**Roadmap**:
1. Add JWT/bearer token authentication
2. Implement `@oneiric_tier_required` decorator
3. Add consent checking for memory operations
4. Integrate with LUKHAS identity system (ΛiD)

---

## API Endpoints

### Health Check

**`GET /`**

Check API health and version information.

**Response**:
```json
{
  "status": "healthy",
  "service": "LUKHAS Dream Engine API",
  "version": "1.0.0",
  "timestamp": "2025-01-08T12:34:56.789Z"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/
```

---

### Process Dream

**`POST /dream/process`**

Process a dream using the quantum-enhanced dream engine.

**Request Body** (`DreamRequest`):
```json
{
  "dream_content": "I was flying over a vast ocean...",
  "qi_enhanced": true,
  "reflection_enabled": true,
  "symbolic_tags": ["flight", "water", "freedom"]
}
```

**Parameters**:
- `dream_content` (string, **required**): The dream narrative to process
- `qi_enhanced` (boolean, optional, default: `true`): Enable quantum-inspired processing
- `reflection_enabled` (boolean, optional, default: `true`): Enable dream reflection loop
- `symbolic_tags` (array[string], optional): Symbolic annotations for the dream

**Response** (`DreamResponse`):
```json
{
  "dream_id": "dream_1736338496789",
  "processed_content": "Processed: I was flying over a vast ocean...",
  "qi_metrics": {
    "coherence": 0.87,
    "entanglement": 0.65,
    "confidence": 0.5655
  },
  "reflection_results": {
    "emotional_state": {
      "dominant": "wonder",
      "intensity": 0.82
    },
    "symbolic_patterns": ["transcendence", "exploration"]
  },
  "symbolic_analysis": {
    "tags": ["flight", "water", "freedom"],
    "extracted_symbols": ["sky", "ocean", "wings"]
  },
  "processing_time": 0.234
}
```

**Error Responses**:
- `500 Internal Server Error`: Dream processing failed

**cURL Example**:
```bash
curl -X POST http://localhost:8000/dream/process \
  -H "Content-Type: application/json" \
  -d '{
    "dream_content": "I was flying over a vast ocean...",
    "qi_enhanced": true,
    "reflection_enabled": true,
    "symbolic_tags": ["flight", "water", "freedom"]
  }'
```

**Python Example**:
```python
import httpx
import asyncio

async def process_dream():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/dream/process",
            json={
                "dream_content": "I was flying over a vast ocean...",
                "qi_enhanced": True,
                "reflection_enabled": True,
                "symbolic_tags": ["flight", "water", "freedom"]
            }
        )
        return response.json()

result = asyncio.run(process_dream())
print(f"Dream ID: {result['dream_id']}")
print(f"Processing time: {result['processing_time']}s")
```

---

### Get Dream

**`GET /dream/{dream_id}`**

Retrieve a processed dream by ID.

**Path Parameters**:
- `dream_id` (string, **required**): Unique dream identifier

**Response**:
```json
{
  "id": "dream_1736338496789",
  "content": "I was flying over a vast ocean...",
  "state": "consolidated",
  "qi_metrics": { ... },
  "emotional_context": { ... },
  "metadata": {
    "processed_at": "2025-01-08T12:34:56.789Z",
    "qi_coherence": 0.87
  }
}
```

**Fallback Response** (if not found):
```json
{
  "id": "dream_1736338496789",
  "status": "not_found",
  "message": "Dream not found or retrieval not implemented"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/dream/dream_1736338496789
```

---

### List Dreams

**`GET /dreams`**

List processed dreams with pagination.

**Query Parameters**:
- `limit` (integer, optional, default: `10`): Maximum number of dreams to return
- `offset` (integer, optional, default: `0`): Number of dreams to skip

**Response**:
```json
{
  "dreams": [
    {
      "id": "dream_1736338496789",
      "content": "I was flying...",
      "state": "consolidated"
    },
    {
      "id": "dream_1736338496790",
      "content": "I was underwater...",
      "state": "processing"
    }
  ],
  "limit": 10,
  "offset": 0,
  "count": 2
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/dreams?limit=20&offset=0"
```

---

### Engine Status

**`GET /status`**

Get the current status of the dream engine.

**Response**:
```json
{
  "status": "active",
  "engine_type": "EnhancedDreamEngine",
  "qi_enabled": true,
  "reflection_enabled": true,
  "timestamp": "2025-01-08T12:34:56.789Z"
}
```

**Status Values**:
- `active`: Engine is running and processing dreams
- `inactive`: Engine is stopped

**cURL Example**:
```bash
curl http://localhost:8000/status
```

---

### Memory Snapshot

**`POST /memory/snapshot`**

Create a dream snapshot with symbolic annotation for memory recurrence (Phase 3B).

**Request Body** (`SnapshotRequest`):
```json
{
  "fold_id": "fold_2025_01_08",
  "dream_state": {
    "coherence": 0.87,
    "emotional_valence": 0.65,
    "narrative_complexity": 0.72
  },
  "introspective_content": {
    "insights": ["pattern recognition", "emotional processing"],
    "depth_level": 3
  },
  "symbolic_annotations": {
    "primary_symbols": ["water", "flight"],
    "archetypal_patterns": ["journey", "transformation"]
  }
}
```

**Parameters**:
- `fold_id` (string, **required**): Memory fold identifier for organization
- `dream_state` (object, **required**): Current dream state metrics
- `introspective_content` (object, **required**): Introspective analysis results
- `symbolic_annotations` (object, optional): Symbolic annotations

**Response** (`SnapshotResponse`):
```json
{
  "snapshot_id": "snapshot_1736338496789",
  "fold_id": "fold_2025_01_08",
  "timestamp": "2025-01-08T12:34:56.789Z",
  "status": "created"
}
```

**Error Responses**:
- `503 Service Unavailable`: Dream reflection loop not available
- `500 Internal Server Error`: Snapshot creation failed

**cURL Example**:
```bash
curl -X POST http://localhost:8000/memory/snapshot \
  -H "Content-Type: application/json" \
  -d '{
    "fold_id": "fold_2025_01_08",
    "dream_state": {
      "coherence": 0.87,
      "emotional_valence": 0.65
    },
    "introspective_content": {
      "insights": ["pattern recognition"],
      "depth_level": 3
    }
  }'
```

---

### Get Fold Snapshots

**`GET /memory/fold/{fold_id}/snapshots`**

Get all snapshots for a memory fold.

**Path Parameters**:
- `fold_id` (string, **required**): Memory fold identifier

**Response**:
```json
{
  "fold_id": "fold_2025_01_08",
  "snapshot_count": 5,
  "snapshots": [
    {
      "snapshot_id": "snapshot_1736338496789",
      "timestamp": "2025-01-08T12:34:56.789Z",
      "dream_state": { ... },
      "introspective_content": { ... }
    }
  ],
  "timestamp": "2025-01-08T12:34:56.789Z"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/memory/fold/fold_2025_01_08/snapshots
```

---

### Get Fold Statistics

**`GET /memory/fold/{fold_id}/statistics`**

Get statistics and metrics for a memory fold.

**Path Parameters**:
- `fold_id` (string, **required**): Memory fold identifier

**Response**:
```json
{
  "fold_id": "fold_2025_01_08",
  "statistics": {
    "total_snapshots": 5,
    "average_coherence": 0.85,
    "convergence_score": 0.92,
    "drift_metrics": {
      "delta": 0.03,
      "trend": "stable"
    },
    "symbolic_coverage": {
      "unique_symbols": 12,
      "archetypal_patterns": 4
    }
  },
  "timestamp": "2025-01-08T12:34:56.789Z"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/memory/fold/fold_2025_01_08/statistics
```

---

### Sync Memory Fold

**`POST /memory/fold/{fold_id}/sync`**

Synchronize a memory fold with persistent storage.

**Path Parameters**:
- `fold_id` (string, **required**): Memory fold identifier

**Response**:
```json
{
  "fold_id": "fold_2025_01_08",
  "sync_successful": true,
  "timestamp": "2025-01-08T12:34:56.789Z",
  "status": "synchronized"
}
```

**Status Values**:
- `synchronized`: Fold successfully synced to storage
- `failed`: Synchronization failed

**cURL Example**:
```bash
curl -X POST http://localhost:8000/memory/fold/fold_2025_01_08/sync
```

---

## Data Models

### DreamRequest

```python
class DreamRequest(BaseModel):
    dream_content: str  # Required
    qi_enhanced: bool = True
    reflection_enabled: bool = True
    symbolic_tags: list[str] = []
```

### DreamResponse

```python
class DreamResponse(BaseModel):
    dream_id: str
    processed_content: str
    qi_metrics: dict[str, Any]
    reflection_results: dict[str, Any]
    symbolic_analysis: dict[str, Any]
    processing_time: float
```

### SnapshotRequest

```python
class SnapshotRequest(BaseModel):
    fold_id: str  # Required
    dream_state: dict[str, Any]  # Required
    introspective_content: dict[str, Any]  # Required
    symbolic_annotations: Optional[dict[str, Any]] = None
```

### SnapshotResponse

```python
class SnapshotResponse(BaseModel):
    snapshot_id: str
    fold_id: str
    timestamp: str
    status: str
```

---

## Code Examples

### Python with httpx

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Process a dream
        dream_response = await client.post(
            "http://localhost:8000/dream/process",
            json={
                "dream_content": "I was flying through colors...",
                "qi_enhanced": True,
                "symbolic_tags": ["synesthesia", "flight"]
            }
        )
        dream_data = dream_response.json()
        dream_id = dream_data["dream_id"]

        # Get dream status
        status_response = await client.get("http://localhost:8000/status")
        print(f"Engine Status: {status_response.json()['status']}")

        # Create memory snapshot
        snapshot_response = await client.post(
            "http://localhost:8000/memory/snapshot",
            json={
                "fold_id": "fold_synesthesia_study",
                "dream_state": dream_data["qi_metrics"],
                "introspective_content": dream_data["reflection_results"]
            }
        )
        print(f"Snapshot created: {snapshot_response.json()['snapshot_id']}")

asyncio.run(main())
```

### JavaScript/TypeScript with fetch

```typescript
async function processDream() {
  const response = await fetch('http://localhost:8000/dream/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      dream_content: 'I was flying through colors...',
      qi_enhanced: true,
      symbolic_tags: ['synesthesia', 'flight']
    })
  });

  const data = await response.json();
  console.log(`Dream ID: ${data.dream_id}`);
  console.log(`QI Coherence: ${data.qi_metrics.coherence}`);

  return data;
}
```

### cURL batch processing

```bash
#!/bin/bash
# Batch dream processing script

DREAMS=(
  "I was swimming in a sea of stars"
  "I spoke with an ancient tree"
  "I flew through rainbow clouds"
)

for dream in "${DREAMS[@]}"; do
  curl -X POST http://localhost:8000/dream/process \
    -H "Content-Type: application/json" \
    -d "{\"dream_content\": \"$dream\", \"qi_enhanced\": true}" \
    | jq '.dream_id, .qi_metrics.coherence'
done
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | OK | Request successful |
| `500` | Internal Server Error | Processing failure, engine error |
| `503` | Service Unavailable | Dream reflection loop unavailable |

### Error Response Format

```json
{
  "detail": "Dream processing failed: Insufficient coherence"
}
```

### Best Practices

1. **Check Engine Status First**: Always verify the engine is active before processing
2. **Handle 503 Gracefully**: Reflection loop may not be available initially
3. **Retry Logic**: Implement exponential backoff for 500 errors
4. **Validate Input**: Ensure dream_content is non-empty before submission

---

## Rate Limiting

**Current Status**: ⚠️ No rate limiting implemented

**Planned Limits** (per tier):
- **Tier 1**: 100 requests/hour
- **Tier 2**: 1,000 requests/hour
- **Tier 3**: 10,000 requests/hour

---

## OpenAPI Specification

### Generate OpenAPI Schema

The FastAPI application auto-generates OpenAPI 3.0 schema at:
- **JSON**: `http://localhost:8000/openapi.json`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

### Download Schema

```bash
curl http://localhost:8000/openapi.json > dream_engine_openapi.json
```

### Full OpenAPI Spec (abbreviated)

```yaml
openapi: 3.0.0
info:
  title: LUKHAS Dream Engine API
  description: FastAPI interface for the enhanced dream engine system
  version: 1.0.0
servers:
  - url: http://localhost:8000
    description: Development server
paths:
  /:
    get:
      summary: API Health Check
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  service:
                    type: string
                  version:
                    type: string
  /dream/process:
    post:
      summary: Process Dream
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DreamRequest'
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DreamResponse'
components:
  schemas:
    DreamRequest:
      type: object
      required:
        - dream_content
      properties:
        dream_content:
          type: string
        qi_enhanced:
          type: boolean
          default: true
        reflection_enabled:
          type: boolean
          default: true
        symbolic_tags:
          type: array
          items:
            type: string
```

---

## Interactive Documentation

### Setup Swagger UI

FastAPI provides **automatic interactive documentation** at `/docs`:

1. Start the server:
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas
   python matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py
   ```

2. Open browser to `http://localhost:8000/docs`

3. **Features**:
   - Try all endpoints interactively
   - View request/response schemas
   - Execute API calls directly from browser
   - Download OpenAPI schema

### Setup ReDoc

Alternative documentation UI at `/redoc`:

1. Navigate to `http://localhost:8000/redoc`

2. **Features**:
   - Clean three-panel layout
   - Search functionality
   - Deep linking to endpoints
   - Printable documentation

### Custom Documentation Portal

To create a standalone documentation site:

```bash
# Install Swagger UI
npm install -g swagger-ui-dist

# Serve the OpenAPI spec
swagger-ui-serve dream_engine_openapi.json
```

---

## Deployment Guide

### Development Deployment

```bash
# Navigate to project root
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Run the Dream Engine server
python matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py
```

Server starts on `http://0.0.0.0:8000` with auto-reload enabled.

### Production Deployment

#### Using Uvicorn (Recommended)

```bash
# Install production dependencies
pip install uvicorn[standard] gunicorn

# Run with Uvicorn
uvicorn matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

#### Using Gunicorn + Uvicorn Workers

```bash
gunicorn matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY matriz/ matriz/
COPY candidate/ candidate/
COPY core/ core/

EXPOSE 8000

CMD ["uvicorn", "matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
docker build -t lukhas-dream-engine .
docker run -p 8000:8000 lukhas-dream-engine
```

### Environment Variables

```bash
# Optional configuration
export DREAM_ENGINE_PORT=8000
export DREAM_ENGINE_HOST="0.0.0.0"
export DREAM_ENGINE_LOG_LEVEL="info"
export DREAM_ENGINE_WORKERS=4

# Future authentication
export DREAM_ENGINE_API_KEY="your-secret-key"
export DREAM_ENGINE_JWT_SECRET="your-jwt-secret"
```

### Health Checks

```bash
# Kubernetes/Docker health check
curl -f http://localhost:8000/ || exit 1
```

### Monitoring

Integrate with Prometheus (see merged PR #1200):

```python
from serve.metrics import matriz_operations_total, matriz_operation_duration_ms

# In dream processing endpoint
matriz_operations_total.labels(operation_type="dream_process", status="success").inc()
matriz_operation_duration_ms.labels(operation_type="dream_process").observe(processing_time * 1000)
```

---

## Performance Targets

Based on MATRIZ cognitive engine specifications:

- **Latency**: <250ms p95 for dream processing
- **Throughput**: 50+ operations/second
- **Memory**: <100MB per worker process
- **Uptime**: 99.9% availability

### Monitoring Endpoints

- **Metrics**: `/metrics` (Prometheus format)
- **Health**: `/` (basic health check)
- **Status**: `/status` (detailed engine status)

---

## Roadmap

### Phase 1 (Current) ✅
- [x] Basic dream processing
- [x] Quantum-inspired enhancement
- [x] Memory snapshot creation
- [x] Fold-based organization
- [x] Interactive documentation

### Phase 2 (Q1 2025)
- [ ] Tier-based authentication
- [ ] Rate limiting per tier
- [ ] User consent checking
- [ ] Persistent storage integration
- [ ] WebSocket streaming

### Phase 3 (Q2 2025)
- [ ] Advanced symbolic analysis
- [ ] Multi-language dream support
- [ ] Dream correlation analytics
- [ ] Custom processing pipelines
- [ ] GraphQL API layer

---

## Support

- **Documentation**: `docs/consciousness/`
- **API Issues**: [GitHub Issues](https://github.com/LukhasAI/Lukhas/issues)
- **Architecture**: See `matriz/consciousness/dream/oneiric/`
- **Community**: LUKHAS AI Discord (coming soon)

---

**Last Updated**: 2025-01-08
**API Version**: 1.0.0
**Implementation**: `matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py`

🤖 Generated with Claude Code
