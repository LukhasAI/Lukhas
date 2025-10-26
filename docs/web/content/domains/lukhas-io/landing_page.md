# lukhas.io: API Gateway for Consciousness-Aware Intelligence

Software systems increasingly orchestrate capabilities across distributed services, composing functionality through API calls rather than monolithic deployment. lukhas.io delivers programmatic access to LUKHAS consciousness-aware intelligence through production-grade APIs designed for reliability, performance, and developer productivity. Whether you're building mobile applications requiring MATRIZ reasoning on device, backend services integrating consciousness-aware capabilities into existing workflows, IoT systems processing sensor streams with cognitive intelligence, or real-time platforms demanding sub-second response latencies, lukhas.io provides the interface architecture and operational infrastructure to succeed at scale.

This is API design informed by operating consciousness-aware systems in production—comprehensive versioning preventing breaking changes from disrupting deployments, intelligent rate limiting that adapts to usage patterns rather than applying rigid quotas, streaming protocols for applications requiring continuous inference, and observability primitives that make debugging distributed systems tractable. lukhas.io isn't merely a gateway exposing functionality; it's infrastructure purpose-built for production deployment of consciousness-aware intelligence across diverse technical environments and operational requirements.

## REST APIs: Familiar, Powerful, Production-Ready

RESTful interfaces provide the foundation for programmatic access, offering intuitive resource-oriented design that developers understand immediately while exposing sophisticated consciousness-aware capabilities.

### MATRIZ Pipeline API

The core of consciousness-aware processing, the MATRIZ Pipeline API orchestrates Memory → Attention → Thought → Risk → Intent → Action cognitive flows through simple HTTP requests:

```http
POST https://api.lukhas.io/v2/matriz/pipeline
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "memory_scope": "conversation:mobile_app_session_xyz",
  "attention_focus": ["weather_patterns", "solar_irradiance", "energy_prices"],
  "thought": {
    "model": "reasoning-fast",
    "prompt": "Should I charge my electric vehicle now or wait for tonight?",
    "context": {
      "current_battery": 45,
      "target_charge": 80,
      "departure_time": "2025-10-27T07:00:00Z",
      "location": "37.7749,-122.4194"
    }
  },
  "risk_tolerance": 0.4,
  "intent_alignment": "minimize_cost_while_ensuring_readiness",
  "action_constraints": ["charging_complete_before_departure"]
}
```

Response includes complete cognitive processing results with structured data optimized for programmatic consumption:

```json
{
  "pipeline_id": "pip_abc123xyz",
  "status": "completed",
  "latency_ms": 247,
  "memory": {
    "retrieved_folds": ["user_preferences", "historical_charging_patterns"],
    "context_items": 23
  },
  "attention": {
    "weights": {
      "weather_patterns": 0.15,
      "solar_irradiance": 0.08,
      "energy_prices": 0.77
    },
    "focused_data": ["utility_time_of_use_rates", "forecasted_solar_generation"]
  },
  "thought": {
    "model_used": "reasoning-fast",
    "reasoning": "Energy prices reach overnight minimum 11pm-6am at $0.12/kWh vs. current $0.31/kWh. Vehicle requires ~4 hours charging from 45% to 80%. Charging tonight 11pm-3am achieves target charge before 7am departure while minimizing cost.",
    "confidence": 0.89
  },
  "risk": {
    "identified_risks": [
      {
        "type": "charging_interruption",
        "likelihood": "low",
        "mitigation": "Utility grid reliability >99.9% historically"
      }
    ],
    "risk_score": 0.12
  },
  "action": {
    "recommendation": "delay_charging_until_23:00",
    "estimated_cost_savings": 6.37,
    "estimated_cost_savings_currency": "USD"
  }
}
```

This example demonstrates consciousness-aware reasoning applied to IoT smart home optimization—the mobile app backend sends a simple query with context, lukhas.io orchestrates MATRIZ pipeline processing with appropriate attention to relevant data sources, applies reasoning considering multiple factors, assesses risks, and delivers actionable recommendations with cost estimates. The application presents results to users without implementing complex energy market logic, weather forecasting, or optimization algorithms.

### Resource-Oriented Endpoints

Beyond pipeline orchestration, lukhas.io exposes specific Constellation Framework capabilities through focused APIs:

**Memory Management** (`/v2/memory/*`) for storing, retrieving, organizing, and searching fold-based memory:

```http
POST https://api.lukhas.io/v2/memory/folds
{
  "fold_name": "iot_sensor_telemetry",
  "namespace": "industrial_monitoring",
  "data": {
    "timestamp": "2025-10-26T14:32:18Z",
    "sensor_id": "turbine_17_vibration",
    "readings": [0.023, 0.025, 0.024, 0.029, 0.031],
    "anomaly_detected": false
  },
  "retention_policy": "90_days",
  "tags": ["manufacturing", "predictive_maintenance", "vibration_analysis"]
}
```

**Identity Operations** (`/v2/identity/*`) for ΛiD authentication, authorization, and user management:

```http
POST https://api.lukhas.io/v2/identity/authenticate
{
  "credentials": {
    "type": "webauthn_assertion",
    "credential_id": "cred_xyz789",
    "client_data_json": "<base64>",
    "authenticator_data": "<base64>",
    "signature": "<base64>"
  },
  "context": {
    "ip_address": "203.0.113.42",
    "user_agent": "MobileApp/2.3.1 iOS/17.1",
    "device_id": "device_abc123"
  }
}
```

**Guardian Policy Evaluation** (`/v2/guardian/*`) for ethical constraint checking and safety validation:

```http
POST https://api.lukhas.io/v2/guardian/evaluate
{
  "action": "send_marketing_email",
  "context": {
    "user_id": "user_12345",
    "email_content": "...",
    "user_preferences": {"marketing_emails": "opted_out"}
  },
  "policies": ["respect_communication_preferences", "gdpr_consent_required"]
}

// Response indicates policy violation
{
  "allowed": false,
  "violations": [
    {
      "policy": "respect_communication_preferences",
      "reason": "User has opted out of marketing emails",
      "severity": "blocking"
    }
  ]
}
```

## GraphQL: Flexible Query Interface

REST APIs excel for discrete operations but require multiple round-trips when applications need related data from multiple resources. lukhas.io GraphQL endpoint enables precise data fetching with single requests, reducing latency and bandwidth consumption for data-intensive applications.

```graphql
query UserContextAndRecommendations($userId: ID!) {
  user(id: $userId) {
    identity {
      id
      namespace
      attributes {
        preferences
        role
      }
      recentAuthentications(limit: 5) {
        timestamp
        context {
          location
          device
        }
      }
    }

    memory {
      activeFolds {
        name
        itemCount
        lastUpdated
      }
      recentInteractions(limit: 10) {
        timestamp
        content
        tags
      }
    }

    recommendations {
      matriz(
        intent: "personalized_content_discovery",
        riskTolerance: 0.5
      ) {
        items {
          content
          relevanceScore
          reasoning
        }
      }
    }
  }
}
```

This single GraphQL query retrieves user identity, recent authentication history, active memory folds, recent interactions, and personalized content recommendations—data that would require 5-7 separate REST API calls. Mobile applications with limited bandwidth and real-time systems minimizing latency particularly benefit from GraphQL's efficiency.

The lukhas.io GraphQL schema exposes complete Constellation Framework capabilities with strongly-typed interfaces, enabling tools like GraphiQL for interactive exploration, automatic client generation for type-safe integration, and query optimization through field-level performance annotations.

## Streaming APIs: Real-Time Consciousness

Applications requiring continuous inference—real-time trading systems responding to market changes, autonomous vehicle control loops processing sensor streams, live content moderation for social platforms, industrial control systems maintaining process parameters—cannot afford request-response latency. lukhas.io streaming APIs provide persistent connections delivering continuous cognitive processing.

### Server-Sent Events

For server-to-client streaming where the server pushes updates as they become available, SSE provides simple, HTTP-based streaming:

```javascript
const eventSource = new EventSource(
  'https://api.lukhas.io/v2/stream/matriz?api_key=<key>',
  {
    headers: {
      'Accept': 'text/event-stream'
    }
  }
);

eventSource.addEventListener('thought', (event) => {
  const thought = JSON.parse(event.data);
  console.log(`MATRIZ reasoning: ${thought.content}`);
  updateUI(thought);
});

eventSource.addEventListener('action', (event) => {
  const action = JSON.parse(event.data);
  console.log(`Recommended action: ${action.recommendation}`);
  executeAction(action);
});

// Server streams incremental pipeline results as they complete
// Event: thought
// {"model": "reasoning-fast", "partial": "Analyzing market conditions..."}
// Event: thought
// {"model": "reasoning-fast", "complete": "Price momentum suggests..."}
// Event: action
// {"recommendation": "execute_trade", "confidence": 0.87}
```

SSE works elegantly for dashboards, monitoring interfaces, and applications where server-initiated updates drive client behavior.

### WebSocket Bidirectional Streaming

Applications requiring bidirectional communication—conversational AI maintaining dialogue state, collaborative editing with multi-user awareness, gaming systems with continuous state synchronization—use WebSocket connections enabling both client and server to send messages asynchronously:

```python
import asyncio
import websockets
import json

async def consciousness_stream():
    uri = "wss://api.lukhas.io/v2/stream/conversation"

    async with websockets.connect(uri) as websocket:
        # Authenticate connection
        await websocket.send(json.dumps({
            "type": "auth",
            "api_key": os.environ["LUKHAS_API_KEY"],
            "session_id": "conv_xyz123"
        }))

        # Send user message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "What are the key risk factors in our Q3 financial projections?",
            "context": {
                "document_ids": ["fin_proj_q3_2025"],
                "user_role": "cfo"
            }
        }))

        # Receive streaming response
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "thought_progress":
                print(f"Thinking: {data['status']}")
            elif data["type"] == "response_chunk":
                print(data["content"], end="", flush=True)
            elif data["type"] == "response_complete":
                print(f"\nConfidence: {data['confidence']}")
                break
```

WebSocket streams maintain conversational context across multi-turn dialogues, enable real-time collaboration where multiple users interact with shared consciousness-aware systems, and support latency-sensitive applications where sub-second response times matter.

### gRPC High-Performance Streaming

For maximum throughput and minimum latency in backend service-to-service communication, lukhas.io provides gRPC endpoints with Protocol Buffer serialization and HTTP/2 multiplexing:

```protobuf
service MatrizStream {
  rpc ContinuousInference(stream InferenceRequest) returns (stream InferenceResponse);
}

message InferenceRequest {
  string session_id = 1;
  repeated float sensor_readings = 2;
  int64 timestamp_ns = 3;
}

message InferenceResponse {
  string session_id = 1;
  repeated Prediction predictions = 2;
  float confidence = 3;
  int64 latency_us = 4;
}
```

gRPC streaming achieves 10-100× higher throughput than REST for high-volume workloads while maintaining sub-millisecond serialization overhead through binary Protocol Buffer encoding. Autonomous systems processing thousands of sensor readings per second, high-frequency trading systems requiring microsecond latencies, and backend microservices orchestrating complex workflows benefit from gRPC performance characteristics.

## Rate Limiting & Quotas: Fair, Adaptive, Predictable

API platforms must balance competing concerns—preventing abuse that degrades service for all users, ensuring fair resource allocation across customers, and avoiding rigid limits that unnecessarily constrain legitimate usage. lukhas.io implements intelligent rate limiting that adapts to usage patterns while maintaining predictability.

### Adaptive Rate Windows

Traditional rate limiting applies fixed quotas (1000 requests/hour) causing friction when legitimate usage briefly spikes—a batch job processing accumulated data, a viral feature driving user engagement, or legitimate testing during development. lukhas.io adaptive rate limiting tracks usage patterns over time, allowing burst capacity for trusted accounts while still preventing sustained abuse:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 8734
X-RateLimit-Reset: 1698264000
X-RateLimit-Burst-Capacity: 2500
X-RateLimit-Burst-Remaining: 2341
```

Base rate limits (10,000 requests/hour) apply to sustained usage; burst capacity allows temporary exceedance for short periods. A batch processing job can consume burst capacity to process accumulated work quickly, then return to normal sustained rate. This flexibility accommodates real-world usage patterns without requiring constant quota adjustment or payment for peak capacity needed only occasionally.

### Cost-Based Quotas

Different API operations consume vastly different computational resources—simple memory retrieval completes in milliseconds with minimal CPU, while deep MATRIZ reasoning with extensive memory search and creative synthesis might require seconds of GPU time. Flat rate limiting (all operations count equally) either permits abuse of expensive operations or unnecessarily restricts cheap ones. lukhas.io implements cost-based quotas where operations consume quota proportional to resource usage:

```json
{
  "operation": "matriz_pipeline",
  "thought_model": "reasoning-deep",
  "cost_units": 15,
  "quota_remaining": 85000
}

{
  "operation": "memory_retrieve",
  "cost_units": 1,
  "quota_remaining": 84999
}
```

Accounts receive cost-unit quotas; operations deduct units based on actual resource consumption. This enables fine-grained usage optimization—applications can choose faster, more expensive models for latency-critical paths while using cheaper models for background processing, maximizing quota efficiency.

### Quota Management APIs

Applications monitor quota usage, predict exhaustion, and request quota increases programmatically:

```http
GET https://api.lukhas.io/v2/quota/status

{
  "period": "monthly",
  "allocated": 1000000,
  "consumed": 673421,
  "remaining": 326579,
  "reset_at": "2025-11-01T00:00:00Z",
  "projected_exhaustion": "2025-10-29T14:23:00Z",
  "recommendation": "current_usage_pace_will_exhaust_quota_2_days_early"
}
```

When quotas approach exhaustion, applications receive webhooks enabling proactive responses—reducing request rates, switching to cheaper processing modes, or requesting temporary quota increases for critical periods.

## API Versioning: Stability & Evolution

APIs must evolve to support new capabilities while maintaining stability for existing integrations. lukhas.io implements comprehensive versioning ensuring backward compatibility while enabling continuous improvement.

### Semantic Versioning

API versions follow semantic versioning semantics: `/v2/matriz/pipeline` indicates major version 2. Major versions receive long-term support (minimum 24 months after superseding version releases), enabling leisurely migration. Minor version improvements (new optional parameters, additional response fields, new endpoints) deploy within existing major versions without requiring code changes.

```http
# Current production version
POST https://api.lukhas.io/v2/matriz/pipeline

# Beta features for early adopters
POST https://api.lukhas.io/v3-beta/matriz/pipeline

# Deprecated but still supported
POST https://api.lukhas.io/v1/matriz/pipeline
# Returns: X-API-Deprecated: true
# Returns: X-API-Sunset: 2026-06-01T00:00:00Z
```

Deprecation follows clear timelines announced minimum 12 months in advance, with sunset dates published in API responses, documented in changelogs, and communicated through developer notifications.

### Feature Flags

New capabilities deploy behind feature flags, enabling opt-in adoption before general availability:

```http
POST https://api.lukhas.io/v2/matriz/pipeline
X-LUKHAS-Features: quantum-inspired-optimization,multimodal-vision-v2

{
  "thought": {
    "model": "reasoning-quantum-enhanced",  // Requires feature flag
    "prompt": "Optimize delivery routes..."
  }
}
```

Early adopters enable experimental features, provide feedback, and influence design before features lock into stable APIs. Production applications stick to stable features, avoiding disruption from evolving capabilities.

## Observability: Understanding System Behavior

Distributed systems debugging requires visibility into request flows, performance characteristics, and failure modes. lukhas.io provides comprehensive observability primitives enabling effective troubleshooting and performance optimization.

### Distributed Tracing

Every API request receives a unique trace ID propagating through LUKHAS infrastructure, enabling correlation of frontend requests with backend processing:

```http
POST https://api.lukhas.io/v2/matriz/pipeline
X-Trace-ID: trace_abc123xyz

# Response includes timing breakdown
HTTP/1.1 200 OK
X-Trace-ID: trace_abc123xyz
X-Trace-Url: https://observability.lukhas.io/traces/trace_abc123xyz

{
  "result": {...},
  "performance": {
    "total_latency_ms": 247,
    "breakdown": {
      "authentication": 3,
      "memory_retrieval": 18,
      "attention_focusing": 12,
      "thought_processing": 189,
      "risk_assessment": 15,
      "response_serialization": 10
    }
  }
}
```

Trace URLs link to detailed timeline visualizations showing exactly where time was spent, which services were invoked, where bottlenecks occurred, and how to optimize performance. Applications experiencing slow responses can share trace URLs with support teams, enabling rapid diagnosis without requiring log aggregation or system access.

### Webhook Notifications

Long-running operations, quota warnings, security events, and system incidents trigger webhook notifications enabling applications to respond programmatically:

```json
POST https://your-app.com/webhooks/lukhas
X-LUKHAS-Event: quota.warning

{
  "event_type": "quota.warning",
  "timestamp": "2025-10-26T15:47:23Z",
  "account_id": "acct_xyz789",
  "data": {
    "quota_type": "api_calls",
    "threshold_percentage": 80,
    "current_usage": 834123,
    "quota_limit": 1000000,
    "projected_exhaustion": "2025-10-29T11:15:00Z"
  }
}
```

Applications subscribe to relevant event types, receiving real-time notifications enabling proactive responses rather than reactive error handling after quotas exhaust or issues arise.

## Integration Patterns: Common Use Cases

lukhas.io supports diverse integration patterns matching various architectural styles and operational requirements.

### Synchronous Request-Response

Traditional request-response works for interactive applications requiring immediate results:

```javascript
async function getRecommendation(userId, context) {
  const response = await fetch('https://api.lukhas.io/v2/matriz/pipeline', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      memory_scope: `user:${userId}`,
      thought: {
        model: 'reasoning-fast',
        prompt: 'Recommend next action based on user context',
        context
      }
    })
  });

  return await response.json();
}
```

### Asynchronous Job Processing

Long-running batch operations submit jobs returning immediately, then poll for completion:

```http
POST https://api.lukhas.io/v2/jobs
{
  "type": "bulk_document_analysis",
  "parameters": {
    "document_ids": ["doc1", "doc2", ..., "doc10000"],
    "analysis_depth": "comprehensive"
  }
}

# Response includes job ID
{
  "job_id": "job_xyz123",
  "status": "queued",
  "estimated_completion": "2025-10-26T16:30:00Z"
}

# Poll for completion
GET https://api.lukhas.io/v2/jobs/job_xyz123
{
  "job_id": "job_xyz123",
  "status": "completed",
  "result_url": "https://api.lukhas.io/v2/jobs/job_xyz123/results"
}
```

### Event-Driven Webhooks

Event-driven architectures configure webhooks receiving notifications when processing completes:

```http
POST https://api.lukhas.io/v2/jobs
{
  "type": "video_content_moderation",
  "parameters": {
    "video_url": "https://cdn.example.com/uploads/video_xyz.mp4"
  },
  "webhook_url": "https://yourapp.com/webhooks/moderation-complete"
}

# LUKHAS posts results when complete
POST https://yourapp.com/webhooks/moderation-complete
{
  "job_id": "job_abc456",
  "status": "completed",
  "result": {
    "violations_detected": false,
    "content_rating": "general_audiences",
    "processing_time_seconds": 47
  }
}
```

## Performance & Reliability

Production APIs must deliver consistent performance under load while maintaining availability through failures.

**Global Edge Network** deploys lukhas.io endpoints across 25+ regions, routing requests to geographically proximate infrastructure reducing latency. Applications in Europe, Asia, and Americas experience <50ms network latency to API endpoints.

**Redundancy & Failover** replicates services across availability zones with automatic failover when failures occur. lukhas.io maintains 99.95% uptime SLA (standard tier) or 99.99% SLA (premium tier) through redundant infrastructure, automatic failure detection, and rapid traffic rerouting.

**Caching & CDN** serves frequently accessed, cacheable responses from edge caches reducing backend load and improving response times for repeated queries.

**Performance Targets** measured and published quarterly: p50 latency <100ms for simple operations, p95 latency <250ms for MATRIZ pipeline processing, p99 latency <1000ms for complex cognitive workflows.

## Get Started with lukhas.io

Programmatic access to consciousness-aware intelligence transforms what's possible in modern applications, enabling capabilities that seemed distant just years ago.

**Create API credentials** at lukhas.io/console, select quota tier matching your needs, receive keys immediately.

**Explore API documentation** at lukhas.io/docs with comprehensive references, interactive examples, and integration guides for major languages and frameworks.

**Join developer community** at community.lukhas.io for technical discussions, integration patterns, and support from engineers building on lukhas.io.

The future of software integrates intelligence as a foundational capability, not a special feature. Build that future through lukhas.io.

**Visit lukhas.io today.** Access consciousness-aware intelligence. Build extraordinary applications.

Welcome to programmatic consciousness. Welcome to lukhas.io.
