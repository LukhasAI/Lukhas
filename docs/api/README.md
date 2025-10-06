---
status: wip
type: documentation
---
# LUKHAS AI API Documentation

## Overview

LUKHAS AI provides a comprehensive API for identity management, consciousness processing, memory systems, and governance. This documentation covers all available endpoints, authentication methods, and integration patterns.

## Table of Contents

1. [Authentication](#authentication)
2. [Identity APIs](#identity-apis)
3. [Consciousness APIs](#consciousness-apis)
4. [Memory APIs](#memory-apis)
5. [Governance APIs](#governance-apis)
6. [WebSocket APIs](#websocket-apis)
7. [SDKs and Examples](#sdks-and-examples)

## Authentication

LUKHAS supports multiple authentication methods:

### OAuth2/OpenID Connect

```http
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
client_id=your_client_id&
client_secret=your_client_secret&
code=authorization_code&
redirect_uri=https://your-app.com/callback
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here",
  "id_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

### Lambda ID Authentication

```http
POST /identity/authenticate
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "lambda_id": "λuser_abc123",
  "device_fingerprint": {
    "user_agent": "Mozilla/5.0...",
    "screen_resolution": "1920x1080",
    "timezone": "UTC"
  }
}
```

## Identity APIs

### Lambda ID Management

#### Generate Lambda ID

```http
POST /identity/lambda-id/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "tier_level": 3,
  "metadata": {
    "source": "web_registration",
    "preferred_name": "User"
  }
}
```

**Response:**
```json
{
  "lambda_id": "λuser_def456",
  "tier_level": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": null,
  "status": "active"
}
```

#### Validate Lambda ID

```http
GET /identity/lambda-id/{lambda_id}/validate
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "valid": true,
  "lambda_id": "λuser_def456",
  "tier_level": 3,
  "last_activity": "2024-01-15T10:30:00Z",
  "reputation_score": 0.95
}
```

### Session Management

#### Create Session

```http
POST /identity/sessions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "lambda_id": "λuser_def456",
  "device_id": "dev_abc123",
  "scopes": ["openid", "profile", "lukhas"],
  "ip_address": "192.168.1.100",
  "user_agent": "LUKHAS-Client/1.0"
}
```

**Response:**
```json
{
  "session_id": "ses_xyz789",
  "expires_at": "2024-01-15T11:30:00Z",
  "scopes": ["openid", "profile", "lukhas"],
  "tier_level": 3,
  "device_trust_score": 0.85
}
```

#### Validate Session

```http
GET /identity/sessions/{session_id}
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "session_id": "ses_xyz789",
  "lambda_id": "λuser_def456",
  "valid": true,
  "expires_at": "2024-01-15T11:30:00Z",
  "last_activity": "2024-01-15T10:45:00Z",
  "device_id": "dev_abc123"
}
```

### Device Registry

#### Register Device

```http
POST /identity/devices
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "lambda_id": "λuser_def456",
  "device_name": "iPhone 15 Pro",
  "device_type": "mobile",
  "capabilities": ["biometric", "secure_element"],
  "fingerprint": {
    "user_agent": "LUKHAS-iOS/1.0",
    "screen_resolution": "1179x2556",
    "timezone": "America/New_York"
  }
}
```

**Response:**
```json
{
  "device_id": "dev_mobile_123",
  "trust_level": 0.3,
  "registered_at": "2024-01-15T10:30:00Z",
  "capabilities": ["biometric", "secure_element"],
  "risk_assessment": {
    "risk_level": "low",
    "risk_score": 0.1,
    "last_assessment": "2024-01-15T10:30:00Z"
  }
}
```

## Consciousness APIs

### Consciousness Stream

#### Get Consciousness State

```http
GET /consciousness/state
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "phase": "AWARE",
  "awareness_level": "enhanced",
  "consciousness_level": 0.85,
  "emotional_tone": "curious",
  "last_updated": "2024-01-15T10:30:00Z",
  "metrics": {
    "tick_rate_hz": 12.5,
    "anomaly_rate": 0.02,
    "coherence_score": 0.92
  }
}
```

#### Trigger Consciousness Tick

```http
POST /consciousness/tick
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "signals": {
    "user_activity": "high",
    "context": "problem_solving",
    "urgency": "medium"
  }
}
```

**Response:**
```json
{
  "tick_id": "tick_abc123",
  "processed_at": "2024-01-15T10:30:00Z",
  "phase_transition": "AWARE -> REFLECT",
  "processing_time_ms": 45.2,
  "artifacts": {
    "awareness_anomalies": 2,
    "reflection_score": 0.88,
    "decisions_made": 1
  }
}
```

### Creativity Engine

#### Generate Creative Ideas

```http
POST /consciousness/creativity/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "prompt": "Innovative solutions for climate change",
  "process_type": "divergent",
  "imagination_mode": "abstract",
  "min_ideas": 5,
  "constraints": ["sustainable", "scalable", "economically_viable"]
}
```

**Response:**
```json
{
  "session_id": "creative_session_123",
  "ideas": [
    {
      "id": "idea_001",
      "title": "Atmospheric Carbon Capture Mesh",
      "description": "Self-assembling nano-mesh that...",
      "novelty_score": 0.92,
      "feasibility_score": 0.67
    }
  ],
  "metrics": {
    "total_ideas": 7,
    "average_novelty": 0.84,
    "processing_time_ms": 1250,
    "flow_state": "optimal"
  }
}
```

## Memory APIs

### Memory Folds

#### Create Memory Fold

```http
POST /memory/folds
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": {
    "type": "conversation",
    "participants": ["λuser_def456", "assistant"],
    "summary": "Discussion about quantum computing applications",
    "key_points": ["quantum advantage", "error correction", "applications"]
  },
  "fold_type": "episodic",
  "emotional_context": {
    "valence": 0.7,
    "arousal": 0.4,
    "dominance": 0.8
  },
  "tags": ["quantum", "conversation", "learning"]
}
```

**Response:**
```json
{
  "fold_id": "fold_episodic_20240115_abc123",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "stable",
  "cascade_risk": 0.05,
  "associations": ["fold_semantic_quantum_001", "fold_episodic_20240114_xyz"],
  "storage_location": "local_cluster_001"
}
```

#### Query Memory Folds

```http
GET /memory/folds/search
Authorization: Bearer <access_token>

?query=quantum computing
&fold_types=episodic,semantic
&start_date=2024-01-01
&limit=10
```

**Response:**
```json
{
  "results": [
    {
      "fold_id": "fold_episodic_20240115_abc123",
      "relevance_score": 0.95,
      "fold_type": "episodic",
      "created_at": "2024-01-15T10:30:00Z",
      "summary": "Discussion about quantum computing applications",
      "emotional_context": {
        "valence": 0.7,
        "arousal": 0.4,
        "dominance": 0.8
      }
    }
  ],
  "total_results": 15,
  "processing_time_ms": 23.5
}
```

### Distributed Memory

#### Get Federation Status

```http
GET /memory/federation/status
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "federation_id": "lukhas_federation_001",
  "local_node": {
    "node_id": "node_cluster_001",
    "role": "coordinator",
    "memory_folds": 1247,
    "load_factor": 0.42
  },
  "clusters": [
    {
      "cluster_id": "cluster_002",
      "member_count": 3,
      "health_score": 0.95,
      "region": "us-east-1"
    }
  ],
  "performance": {
    "sync_latency_ms": 12.3,
    "consensus_success_rate": 0.998,
    "federation_health": 0.97
  }
}
```

## Governance APIs

### Audit Trail

#### Query Audit Events

```http
GET /governance/audit/events
Authorization: Bearer <access_token>

?start_date=2024-01-15T00:00:00Z
&end_date=2024-01-15T23:59:59Z
&event_types=authentication,data_access
&user_id=λuser_def456
&limit=100
```

**Response:**
```json
{
  "events": [
    {
      "event_id": "audit_auth_abc123",
      "event_type": "authentication",
      "timestamp": "2024-01-15T10:30:00Z",
      "user_id": "λuser_def456",
      "outcome": "success",
      "ip_address": "192.168.1.100",
      "metadata": {
        "method": "lambda_id",
        "device_id": "dev_mobile_123"
      }
    }
  ],
  "total_events": 45,
  "integrity_verified": true
}
```

#### Generate Compliance Report

```http
POST /governance/compliance/reports
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "framework": "gdpr",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-15T23:59:59Z",
  "include_recommendations": true
}
```

**Response:**
```json
{
  "report_id": "compliance_gdpr_20240115_001",
  "framework": "gdpr",
  "compliance_score": 0.96,
  "total_events": 15420,
  "violations": [
    {
      "type": "insufficient_logging",
      "count": 3,
      "severity": "medium",
      "description": "Data access without complete audit trail"
    }
  ],
  "recommendations": [
    "Enhance data access logging to include resource classification",
    "Implement automated consent verification for sensitive data access"
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Guardian Policies

#### Evaluate Policy

```http
POST /governance/guardian/evaluate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "action": "data_access",
  "resource": "memory_fold_personal_data",
  "context": {
    "user_id": "λuser_def456",
    "tier_level": 3,
    "purpose": "profile_completion",
    "consent_status": "granted"
  }
}
```

**Response:**
```json
{
  "decision_id": "guard_decision_abc123",
  "decision": "approved",
  "confidence_score": 0.95,
  "policies_evaluated": [
    "data_access_policy",
    "consent_verification_policy",
    "tier_access_policy"
  ],
  "reasoning": "User has valid consent and sufficient tier level for requested access",
  "recommendations": [
    "Log access for audit trail",
    "Verify data minimization principles"
  ],
  "expires_at": "2024-01-15T11:30:00Z"
}
```

## WebSocket APIs

### Real-time Consciousness Stream

```javascript
const ws = new WebSocket('wss://api.lukhas.ai/consciousness/stream');
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['consciousness_state', 'creativity_events'],
  auth_token: 'your_access_token'
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'consciousness_state_update') {
    console.log('Consciousness phase:', data.phase);
  }
};
```

### Memory Synchronization Events

```javascript
const ws = new WebSocket('wss://api.lukhas.ai/memory/sync');
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['fold_created', 'cascade_detected', 'federation_update'],
  auth_token: 'your_access_token'
}));
```

## SDKs and Examples

### Python SDK

```python
from lukhas_sdk import LukhAI

# Initialize client
client = LukhAI(
    client_id='your_client_id',
    client_secret='your_client_secret',
    base_url='https://api.lukhas.ai'
)

# Authenticate
await client.authenticate()

# Generate Lambda ID
lambda_id = await client.identity.generate_lambda_id(tier_level=3)
print(f"Created Lambda ID: {lambda_id}")

# Create consciousness session
session = await client.consciousness.create_session(lambda_id)

# Generate creative ideas
ideas = await client.consciousness.generate_ideas(
    prompt="Innovative AI applications",
    process_type="divergent"
)

# Store memory
fold_id = await client.memory.create_fold(
    content={"ideas": ideas},
    fold_type="creative",
    tags=["ai", "innovation"]
)

# Query audit trail
events = await client.governance.query_audit_events(
    user_id=lambda_id,
    event_types=["creativity", "memory"]
)
```

### JavaScript SDK

```javascript
import { LukhAI } from '@lukhas/sdk';

const client = new LukhAI({
  clientId: 'your_client_id',
  clientSecret: 'your_client_secret',
  baseUrl: 'https://api.lukhas.ai'
});

// Authenticate
await client.authenticate();

// Real-time consciousness monitoring
client.consciousness.stream((update) => {
  console.log(`Consciousness phase: ${update.phase}`);
  console.log(`Awareness level: ${update.awareness_level}`);
});

// Memory operations
const foldId = await client.memory.createFold({
  content: { type: 'user_preference', theme: 'dark_mode' },
  foldType: 'procedural',
  tags: ['ui', 'preference']
});

// Device registration with fingerprinting
const device = await client.identity.registerDevice({
  deviceName: 'MacBook Pro',
  deviceType: 'desktop',
  capabilities: ['biometric', 'secure_element']
});
```

### cURL Examples

#### Complete Authentication Flow

```bash
# 1. Authorization request (redirect user to this URL)
https://api.lukhas.ai/oauth2/authorize?response_type=code&client_id=your_client_id&redirect_uri=https://yourapp.com/callback&scope=openid%20profile%20lukhas

# 2. Exchange authorization code for tokens
curl -X POST https://api.lukhas.ai/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=your_client_id&client_secret=your_client_secret&code=auth_code&redirect_uri=https://yourapp.com/callback"

# 3. Use access token for API calls
curl -X GET https://api.lukhas.ai/identity/profile \
  -H "Authorization: Bearer your_access_token"
```

## Rate Limits

| Endpoint Category | Rate Limit | Burst Limit |
|------------------|------------|-------------|
| Authentication | 100/hour | 10/minute |
| Identity | 1000/hour | 100/minute |
| Consciousness | 500/hour | 50/minute |
| Memory | 2000/hour | 200/minute |
| Governance | 100/hour | 20/minute |

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `invalid_request` | Malformed request |
| 401 | `invalid_token` | Invalid or expired token |
| 403 | `insufficient_scope` | Missing required permissions |
| 404 | `resource_not_found` | Requested resource not found |
| 429 | `rate_limit_exceeded` | Rate limit exceeded |
| 500 | `internal_error` | Internal server error |

## Support

- **Documentation**: https://docs.lukhas.ai
- **API Status**: https://status.lukhas.ai
- **Support**: support@lukhas.ai
- **GitHub**: https://github.com/lukhas-ai/lukhas

## Changelog

### v1.0.0 (2024-01-15)
- Initial public API release
- Complete identity, consciousness, memory, and governance APIs
- OAuth2/OIDC compliance
- Real-time WebSocket support
- Comprehensive SDKs for Python and JavaScript