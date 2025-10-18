---
title: LUKHAS Ecosystem APIs - Public Interface Specifications
updated: 2025-10-18
version: 1.0
owner: LUKHAS API Team
status: design
schema_version: 1.1.0
contract_refs:
  - lukhas.api.public@v1
  - lukhas.api.dream@v1
  - lukhas.api.identity@v1
  - lukhas.api.drift@v1
tags: [api, public, ecosystem, dream, identity, drift, specification]
---

# LUKHAS Ecosystem APIs

This document specifies the external API interfaces for three flagship LUKHAS capabilities designed for ecosystem integration: **Dream Engine**, **Drift Synthesis**, and **ΛiD (Lambda Identity)**.

## 🎯 Design Principles

1. **REST-First**: Standard HTTP/JSON APIs for maximum compatibility
2. **Async-Ready**: Support for long-running operations (dreams, synthesis)
3. **Observable**: Built-in instrumentation and logging
4. **Secure**: OAuth2/OIDC authentication, policy enforcement
5. **Versioned**: Explicit API versioning for stability
6. **Rate-Limited**: Protect resources and ensure fair usage

---

## 🌙 Dream Engine API (Drift Star)

### Overview
The Dream Engine API enables asynchronous creative synthesis and unconscious processing. Applications can submit concept seeds, schedule dream cycles, and retrieve synthesized insights.

### Base URL
```
https://api.lukhas.ai/v1/dream
```

### Authentication
```http
Authorization: Bearer <lukhas_api_token>
```

---

### Endpoints

#### 1. Create Dream Cycle
Initiate an asynchronous dream processing cycle.

**Request**
```http
POST /v1/dream/cycles
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": "user_123",
  "seed_concepts": [
    "quantum computing",
    "biological systems",
    "creative art"
  ],
  "duration_hours": 8,
  "style": "hypnagogic",
  "temperature": 0.85,
  "constraints": {
    "max_concepts": 50,
    "min_novelty_score": 0.7,
    "preserve_coherence": true
  },
  "metadata": {
    "project_id": "proj_456",
    "tags": ["research", "innovation"]
  }
}
```

**Response**
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "dream_cycle_id": "dream_cycle_abc123",
  "status": "initiated",
  "estimated_completion": "2025-10-19T08:00:00Z",
  "seed_concepts": ["quantum computing", "biological systems", "creative art"],
  "duration_hours": 8,
  "created_at": "2025-10-18T00:00:00Z",
  "monitoring_url": "https://api.lukhas.ai/v1/dream/cycles/dream_cycle_abc123"
}
```

---

#### 2. Get Dream Cycle Status
Check the status of a running or completed dream cycle.

**Request**
```http
GET /v1/dream/cycles/{dream_cycle_id}
Authorization: Bearer <token>
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "dream_cycle_id": "dream_cycle_abc123",
  "status": "processing",
  "progress": 0.45,
  "estimated_completion": "2025-10-19T08:00:00Z",
  "elapsed_hours": 3.6,
  "insights_generated": 23,
  "created_at": "2025-10-18T00:00:00Z",
  "updated_at": "2025-10-18T03:36:00Z"
}
```

**Status Values**
- `initiated`: Dream cycle queued
- `processing`: Active dream synthesis
- `completed`: Insights ready for retrieval
- `failed`: Error during processing
- `cancelled`: User-cancelled cycle

---

#### 3. Retrieve Dream Insights
Get synthesized insights from a completed dream cycle.

**Request**
```http
GET /v1/dream/cycles/{dream_cycle_id}/insights
Authorization: Bearer <token>
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "dream_cycle_id": "dream_cycle_abc123",
  "insights": [
    {
      "insight_id": "insight_001",
      "narrative": "Quantum entanglement patterns mirror cellular communication in biological systems, suggesting a bio-quantum interface for distributed consciousness.",
      "novelty_score": 0.89,
      "coherence_score": 0.92,
      "concepts_connected": ["quantum entanglement", "cellular communication", "distributed consciousness"],
      "creative_leap": "high",
      "supporting_evidence": [
        "Quantum coherence in photosynthesis (Engel et al., 2007)",
        "Microtubule quantum processing (Penrose-Hameroff)",
        "Cellular signaling networks"
      ]
    },
    {
      "insight_id": "insight_002",
      "narrative": "Artistic representation of quantum superposition through generative biological patterns could create living, evolving artworks.",
      "novelty_score": 0.95,
      "coherence_score": 0.78,
      "concepts_connected": ["quantum superposition", "generative art", "biological growth"],
      "creative_leap": "very_high",
      "supporting_evidence": [
        "Reaction-diffusion systems in art",
        "Quantum random number generation",
        "Living sculpture precedents"
      ]
    }
  ],
  "summary": {
    "total_insights": 28,
    "average_novelty": 0.82,
    "average_coherence": 0.85,
    "top_concepts": ["quantum", "biological", "consciousness", "art", "emergence"],
    "recommended_next_steps": [
      "Explore bio-quantum interface prototyping",
      "Commission living artwork experiment",
      "Literature review on quantum biology"
    ]
  },
  "visualization_url": "https://api.lukhas.ai/v1/dream/cycles/dream_cycle_abc123/viz",
  "export_formats": ["json", "markdown", "pdf"]
}
```

---

#### 4. Cancel Dream Cycle
Stop a running dream cycle.

**Request**
```http
DELETE /v1/dream/cycles/{dream_cycle_id}
Authorization: Bearer <token>
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "dream_cycle_id": "dream_cycle_abc123",
  "status": "cancelled",
  "insights_generated": 12,
  "cancelled_at": "2025-10-18T04:00:00Z",
  "partial_results_available": true
}
```

---

#### 5. List Dream Cycles
Retrieve all dream cycles for a user.

**Request**
```http
GET /v1/dream/cycles?user_id=user_123&status=completed&limit=10
Authorization: Bearer <token>
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "cycles": [
    {
      "dream_cycle_id": "dream_cycle_abc123",
      "status": "completed",
      "seed_concepts": ["quantum", "biology", "art"],
      "insights_count": 28,
      "created_at": "2025-10-18T00:00:00Z",
      "completed_at": "2025-10-18T08:00:00Z"
    }
  ],
  "pagination": {
    "total": 47,
    "page": 1,
    "per_page": 10,
    "next_page": 2
  }
}
```

---

### Dream API Data Models

#### DreamCycleRequest
```typescript
interface DreamCycleRequest {
  user_id: string;
  seed_concepts: string[];           // 1-10 concepts
  duration_hours: number;            // 1-24 hours
  style: "hypnagogic" | "lucid" | "rem" | "deep";
  temperature: number;               // 0.0-1.0 (creativity)
  constraints?: {
    max_concepts?: number;           // Default: 100
    min_novelty_score?: number;      // Default: 0.5
    preserve_coherence?: boolean;    // Default: true
  };
  metadata?: Record<string, any>;
}
```

#### DreamInsight
```typescript
interface DreamInsight {
  insight_id: string;
  narrative: string;                 // 2-5 sentence synthesis
  novelty_score: number;             // 0.0-1.0
  coherence_score: number;           // 0.0-1.0
  concepts_connected: string[];
  creative_leap: "low" | "medium" | "high" | "very_high";
  supporting_evidence: string[];
}
```

---

### Rate Limits
- **Free Tier**: 5 dream cycles/month, max 4 hours each
- **Pro Tier**: 50 dream cycles/month, max 12 hours each
- **Enterprise**: Unlimited, custom SLAs

### Pricing (Managed Service)
- **Per Cycle**: $0.50/hour (hypnagogic), $1.00/hour (lucid)
- **Storage**: $0.10/GB for retained insights
- **Compute**: Additional charges for high-complexity seeds (10+ concepts)

---

## ⚛️ ΛiD (Lambda Identity) API (Anchor Star)

### Overview
The ΛiD API manages multi-persona identity orchestration, allowing applications to create, switch, and isolate cognitive personas with distinct memory, preferences, and behavior.

### Base URL
```
https://api.lukhas.ai/v1/identity
```

---

### Endpoints

#### 1. Create Persona
Create a new cognitive persona for a user.

**Request**
```http
POST /v1/identity/personas
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": "user_123",
  "persona_name": "researcher",
  "display_name": "Dr. Research Mode",
  "description": "Analytical persona for academic work",
  "traits": {
    "formality": 0.8,
    "creativity": 0.4,
    "verbosity": 0.6,
    "expertise_domains": ["machine learning", "cognitive science"]
  },
  "memory_isolation": "strict",
  "style_preferences": {
    "citation_format": "APA",
    "tone": "academic",
    "language_complexity": "advanced"
  },
  "metadata": {
    "department": "research",
    "access_level": "internal"
  }
}
```

**Response**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "persona_id": "persona_abc123",
  "user_id": "user_123",
  "persona_name": "researcher",
  "display_name": "Dr. Research Mode",
  "traits": { ... },
  "memory_namespace": "user_123:researcher",
  "created_at": "2025-10-18T10:00:00Z",
  "status": "active"
}
```

---

#### 2. List Personas
Get all personas for a user.

**Request**
```http
GET /v1/identity/personas?user_id=user_123
Authorization: Bearer <token>
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "personas": [
    {
      "persona_id": "persona_abc123",
      "persona_name": "researcher",
      "display_name": "Dr. Research Mode",
      "status": "active",
      "created_at": "2025-10-18T10:00:00Z",
      "last_active": "2025-10-18T15:30:00Z",
      "interaction_count": 247
    },
    {
      "persona_id": "persona_def456",
      "persona_name": "creative",
      "display_name": "Creative Explorer",
      "status": "active",
      "created_at": "2025-10-17T08:00:00Z",
      "last_active": "2025-10-18T12:00:00Z",
      "interaction_count": 89
    }
  ],
  "total": 2
}
```

---

#### 3. Switch Persona Context
Activate a specific persona for subsequent API calls.

**Request**
```http
POST /v1/identity/personas/{persona_id}/activate
Authorization: Bearer <token>

{
  "session_id": "session_xyz789",
  "transition_memory": true
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "persona_id": "persona_abc123",
  "session_id": "session_xyz789",
  "active_namespace": "user_123:researcher",
  "memory_context_loaded": true,
  "traits_applied": true,
  "activated_at": "2025-10-18T16:00:00Z"
}
```

---

#### 4. Query with Persona
Make a query using a specific persona's context and traits.

**Request**
```http
POST /v1/identity/personas/{persona_id}/query
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt": "Summarize recent advances in quantum machine learning",
  "model": "gpt-4",
  "include_persona_memory": true,
  "temperature": null  // Uses persona's default
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "response": "Recent advances in quantum machine learning include...",
  "persona_id": "persona_abc123",
  "persona_traits_applied": {
    "formality": 0.8,
    "citation_format": "APA"
  },
  "memory_entries_used": 5,
  "model": "gpt-4",
  "tokens_used": 847,
  "timestamp": "2025-10-18T16:05:00Z"
}
```

---

#### 5. Update Persona Traits
Modify persona characteristics.

**Request**
```http
PATCH /v1/identity/personas/{persona_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "traits": {
    "creativity": 0.6
  },
  "style_preferences": {
    "tone": "conversational"
  }
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "persona_id": "persona_abc123",
  "updated_fields": ["traits.creativity", "style_preferences.tone"],
  "updated_at": "2025-10-18T16:10:00Z"
}
```

---

#### 6. Delete Persona
Permanently remove a persona and its isolated memory.

**Request**
```http
DELETE /v1/identity/personas/{persona_id}
Authorization: Bearer <token>

{
  "confirm_deletion": true,
  "preserve_memory_backup": false
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "persona_id": "persona_abc123",
  "deleted_at": "2025-10-18T16:15:00Z",
  "memory_entries_deleted": 1247,
  "backup_created": false
}
```

---

### Identity API Data Models

#### Persona
```typescript
interface Persona {
  persona_id: string;
  user_id: string;
  persona_name: string;              // Unique per user
  display_name: string;
  description?: string;
  traits: PersonaTraits;
  memory_isolation: "strict" | "shared" | "read_only";
  style_preferences: StylePreferences;
  created_at: string;
  last_active: string;
  status: "active" | "archived";
}

interface PersonaTraits {
  formality: number;                 // 0.0-1.0
  creativity: number;                // 0.0-1.0
  verbosity: number;                 // 0.0-1.0
  expertise_domains: string[];
}

interface StylePreferences {
  citation_format?: "APA" | "MLA" | "Chicago";
  tone?: "academic" | "conversational" | "professional";
  language_complexity?: "simple" | "moderate" | "advanced";
}
```

---

### Rate Limits
- **Free Tier**: 3 personas, 100 queries/day per persona
- **Pro Tier**: 10 personas, 1,000 queries/day per persona
- **Enterprise**: Unlimited personas, custom rate limits

### Pricing
- **Per Persona**: $5/month (includes memory storage)
- **Queries**: $0.01/query (after included quota)
- **Memory Storage**: $0.10/GB beyond 1GB per persona

---

## 🎭 Drift Synthesis API (Creative Hybridization)

### Overview
The Drift API provides creative synthesis services that blend multiple concepts, styles, or knowledge domains into novel outputs. Unlike Dream (long-running unconscious processing), Drift offers synchronous creative hybridization.

### Base URL
```
https://api.lukhas.ai/v1/drift
```

---

### Endpoints

#### 1. Synthesize Concepts
Blend multiple concepts into a creative synthesis.

**Request**
```http
POST /v1/drift/synthesize
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_id": "user_123",
  "concepts": [
    {
      "name": "jazz improvisation",
      "weight": 0.4
    },
    {
      "name": "algorithmic composition",
      "weight": 0.3
    },
    {
      "name": "neural networks",
      "weight": 0.3
    }
  ],
  "output_format": "narrative",
  "creativity_level": 0.85,
  "constraints": {
    "preserve_feasibility": true,
    "target_domain": "music technology"
  }
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "synthesis_id": "synth_123abc",
  "narrative": "A neural network that improvises jazz in real-time, learning from human musicians' phrasing patterns and applying algorithmic composition rules to generate harmonically coherent yet spontaneous melodies...",
  "hybrid_concept": "Neural Jazz Improvisation Engine",
  "novelty_score": 0.87,
  "feasibility_score": 0.72,
  "creative_leap": "high",
  "supporting_references": [
    "Magenta Project (Google)",
    "Jazz improvisation theory",
    "Recurrent neural networks for music"
  ],
  "next_steps": [
    "Prototype RNN architecture for melody generation",
    "Study jazz chord progressions",
    "Partner with jazz musicians for training data"
  ],
  "generated_at": "2025-10-18T17:00:00Z"
}
```

---

#### 2. Generate Creative Analogies
Create analogies between disparate domains.

**Request**
```http
POST /v1/drift/analogies
Content-Type: application/json
Authorization: Bearer <token>

{
  "source_domain": "quantum computing",
  "target_domain": "urban planning",
  "depth": "deep",
  "min_insights": 3
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "analogies": [
    {
      "analogy": "Quantum superposition maps to multi-modal transportation networks where commuters exist in multiple potential routes until they 'collapse' into a chosen path at decision points.",
      "strength": 0.82,
      "insights": "Design urban transit systems with probabilistic routing that adapts in real-time to collective commuter states."
    },
    {
      "analogy": "Quantum entanglement parallels synchronized traffic light systems where state changes in one intersection instantly influence distant intersections.",
      "strength": 0.79,
      "insights": "Implement distributed traffic control with non-local correlation for city-wide optimization."
    }
  ],
  "meta": {
    "total_analogies": 2,
    "average_strength": 0.805
  }
}
```

---

### Drift API Data Models

#### SynthesisRequest
```typescript
interface SynthesisRequest {
  user_id: string;
  concepts: ConceptInput[];
  output_format: "narrative" | "bullet_points" | "diagram" | "prototype_spec";
  creativity_level: number;          // 0.0-1.0
  constraints?: {
    preserve_feasibility?: boolean;
    target_domain?: string;
    max_length?: number;
  };
}

interface ConceptInput {
  name: string;
  weight: number;                    // 0.0-1.0, must sum to 1.0
  context?: string;
}
```

---

### Rate Limits
- **Free Tier**: 20 syntheses/day
- **Pro Tier**: 500 syntheses/day
- **Enterprise**: Unlimited

### Pricing
- **Per Synthesis**: $0.05 (narrative), $0.10 (diagram/prototype)
- **Bulk Discounts**: 20% off for >1,000/month

---

## 🔐 Authentication & Authorization

### OAuth2 Flow
```http
POST https://auth.lukhas.ai/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=<your_client_id>
&client_secret=<your_client_secret>
&scope=dream:read dream:write identity:read identity:write drift:read
```

**Response**
```json
{
  "access_token": "lukhas_token_...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "dream:read dream:write identity:read identity:write drift:read"
}
```

### Scopes
- `dream:read` - Read dream cycles and insights
- `dream:write` - Create and cancel dream cycles
- `identity:read` - View personas
- `identity:write` - Create, update, delete personas
- `drift:read` - View syntheses
- `drift:write` - Create syntheses

---

## 📊 Monitoring & Observability

### Metrics Endpoint
```http
GET /v1/metrics/usage
Authorization: Bearer <token>

{
  "period": "last_30_days",
  "user_id": "user_123"
}
```

**Response**
```json
{
  "dream_cycles": {
    "total": 12,
    "hours_processed": 96,
    "insights_generated": 342
  },
  "identity": {
    "personas": 3,
    "queries": 1247,
    "namespace_switches": 89
  },
  "drift": {
    "syntheses": 156,
    "average_novelty": 0.81
  },
  "billing": {
    "total_cost_usd": 87.50,
    "breakdown": {
      "dream": 48.00,
      "identity": 31.50,
      "drift": 8.00
    }
  }
}
```

---

## 🚀 SDKs & Libraries

### Python SDK
```bash
pip install lukhas-sdk
```

```python
from lukhas import LukhasClient

client = LukhasClient(api_key="lukhas_...")

# Dream API
cycle = await client.dream.create_cycle(
    seed_concepts=["AI", "consciousness", "ethics"],
    duration_hours=8
)

insights = await client.dream.get_insights(cycle.id)

# Identity API
persona = await client.identity.create_persona(
    name="researcher",
    traits={"formality": 0.8, "creativity": 0.4}
)

response = await client.identity.query(
    persona_id=persona.id,
    prompt="Explain quantum computing"
)

# Drift API
synthesis = await client.drift.synthesize(
    concepts=["jazz", "algorithms", "neural networks"],
    creativity_level=0.85
)
```

### JavaScript/TypeScript SDK
```bash
npm install @lukhas/sdk
```

```typescript
import { LukhasClient } from '@lukhas/sdk';

const client = new LukhasClient({ apiKey: 'lukhas_...' });

// Same interface as Python SDK
const cycle = await client.dream.createCycle({
  seedConcepts: ['AI', 'consciousness', 'ethics'],
  durationHours: 8
});
```

---

## 📚 OpenAPI Specification

Full OpenAPI 3.0 specification available at:
```
https://api.lukhas.ai/v1/openapi.json
```

---

## 📞 Support & Resources

- **API Documentation**: https://docs.lukhas.ai/api
- **Developer Portal**: https://developers.lukhas.ai
- **Status Page**: https://status.lukhas.ai
- **Support Email**: api-support@lukhas.ai
- **GitHub**: https://github.com/lukhas-ai/sdk-python

---

**Last Updated**: 2025-10-18
**API Version**: v1
**Schema Version**: 1.0
**Status**: Design Specification (Pre-Production)
