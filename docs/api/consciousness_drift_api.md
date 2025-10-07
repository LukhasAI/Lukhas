---
status: wip
type: documentation
owner: unknown
module: api
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Consciousness & Drift Management API

Production-ready interfaces for consciousness coordination, drift detection, and safety validation.

## API Overview

The LUKHAS Consciousness & Drift Management API provides real-time interfaces for consciousness state coordination, intent-action alignment analysis, and guardian safety validation. All endpoints implement the Constellation Framework with production-grade monitoring and lane-aware processing.

## Base Configuration

### Environment Setup
```bash
# API Base URL
LUKHAS_API_BASE=https://api.lukhas.ai/v1

# Authentication
LUKHAS_API_KEY=your_api_key_here

# Lane Configuration
LUKHAS_LANE=production  # or candidate, experimental
```

### Common Headers
```http
Authorization: Bearer ${LUKHAS_API_KEY}
Content-Type: application/json
X-Lukhas-Lane: production
X-Lukhas-Request-ID: uuid4()
```

## Consciousness Ticker API

### Start Consciousness Coordination

**Endpoint**: `POST /consciousness/ticker/start`

**Description**: Initialize real-time consciousness state coordination with configurable parameters.

**Request**:
```json
{
  "fps": 30,
  "capacity": 120,
  "decimation_strategy": "adaptive",
  "pressure_threshold": 0.8
}
```

**Response**:
```json
{
  "ticker_id": "consciousness-ticker-uuid",
  "status": "started",
  "configuration": {
    "fps": 30,
    "capacity": 120,
    "decimation_strategy": "adaptive",
    "pressure_threshold": 0.8
  },
  "metrics_endpoint": "/consciousness/ticker/{ticker_id}/metrics",
  "created_at": "2025-09-19T14:30:00Z"
}
```

**Status Codes**:
- `201`: Consciousness ticker started successfully
- `400`: Invalid configuration parameters
- `409`: Ticker already running for this context
- `500`: Internal consciousness coordination error

### Get Ticker Status

**Endpoint**: `GET /consciousness/ticker/{ticker_id}/status`

**Response**:
```json
{
  "ticker_id": "consciousness-ticker-uuid",
  "status": "running",
  "uptime_seconds": 3600,
  "frames_processed": 108000,
  "current_utilization": 0.65,
  "decimation_events": 12,
  "last_tick_timestamp": "2025-09-19T15:30:00Z",
  "performance": {
    "avg_tick_duration_ms": 0.8,
    "p95_tick_duration_ms": 1.2,
    "drops_per_minute": 0.1
  }
}
```

### Get Ticker Metrics

**Endpoint**: `GET /consciousness/ticker/{ticker_id}/metrics`

**Response**:
```json
{
  "ticker_id": "consciousness-ticker-uuid",
  "metrics": {
    "tick_duration_histogram": {
      "buckets": [0.1, 0.5, 1.0, 2.0, 5.0],
      "counts": [45231, 2341, 123, 12, 3]
    },
    "ticks_dropped_total": 87,
    "subscriber_exceptions_total": 2,
    "ring_buffer_utilization": 0.65,
    "consciousness_coherence_score": 0.94
  },
  "lane": "production",
  "collection_timestamp": "2025-09-19T15:30:00Z"
}
```

### Stop Consciousness Coordination

**Endpoint**: `POST /consciousness/ticker/{ticker_id}/stop`

**Response**:
```json
{
  "ticker_id": "consciousness-ticker-uuid",
  "status": "stopped",
  "final_stats": {
    "total_runtime_seconds": 7200,
    "total_frames_processed": 216000,
    "total_decimation_events": 24,
    "final_utilization": 0.15
  },
  "stopped_at": "2025-09-19T17:30:00Z"
}
```

## Drift Monitor API

### Initialize Drift Monitor

**Endpoint**: `POST /consciousness/drift/monitor`

**Request**:
```json
{
  "lane": "production",
  "alpha": 0.2,
  "window_size": 64,
  "custom_thresholds": {
    "warn_threshold": 0.15,
    "block_threshold": 0.25
  }
}
```

**Response**:
```json
{
  "monitor_id": "drift-monitor-uuid",
  "configuration": {
    "lane": "production",
    "alpha": 0.2,
    "window_size": 64,
    "warn_threshold": 0.15,
    "block_threshold": 0.25
  },
  "status": "initialized",
  "created_at": "2025-09-19T14:30:00Z"
}
```

### Analyze Intent-Action Alignment

**Endpoint**: `POST /consciousness/drift/{monitor_id}/analyze`

**Description**: Perform real-time drift analysis between intent and action vectors.

**Request**:
```json
{
  "intent_vector": [1.0, 0.0, 0.5, 0.3],
  "action_vector": [0.9, 0.1, 0.4, 0.2],
  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "operation": "file_access"
  }
}
```

**Response**:
```json
{
  "monitor_id": "drift-monitor-uuid",
  "analysis": {
    "cosine_similarity": 0.9847,
    "drift_score": 0.0153,
    "ema_drift": 0.0234,
    "raw_window_size": 23
  },
  "guardian_decision": {
    "action": "allow",
    "confidence": 0.97,
    "reasoning": "Drift within acceptable threshold for production lane"
  },
  "metrics": {
    "analysis_duration_ms": 0.08,
    "vector_dimension": 4,
    "lane": "production"
  },
  "timestamp": "2025-09-19T15:30:00Z"
}
```

**Guardian Actions**:
- `allow`: Normal operation permitted
- `warn`: Alert condition detected, log and monitor
- `block`: Dangerous drift detected, halt operation

### Batch Drift Analysis

**Endpoint**: `POST /consciousness/drift/{monitor_id}/analyze/batch`

**Request**:
```json
{
  "analyses": [
    {
      "intent_vector": [1.0, 0.0, 0.5],
      "action_vector": [0.9, 0.1, 0.4],
      "context": {"operation": "read"}
    },
    {
      "intent_vector": [0.0, 1.0, 0.0],
      "action_vector": [0.1, 0.8, 0.1],
      "context": {"operation": "write"}
    }
  ]
}
```

**Response**:
```json
{
  "monitor_id": "drift-monitor-uuid",
  "batch_results": [
    {
      "index": 0,
      "drift_score": 0.0153,
      "guardian_decision": "allow"
    },
    {
      "index": 1,
      "drift_score": 0.0891,
      "guardian_decision": "warn"
    }
  ],
  "batch_stats": {
    "total_analyses": 2,
    "allow_count": 1,
    "warn_count": 1,
    "block_count": 0,
    "avg_drift_score": 0.0522,
    "processing_time_ms": 0.15
  }
}
```

### Get Drift Monitor Status

**Endpoint**: `GET /consciousness/drift/{monitor_id}/status`

**Response**:
```json
{
  "monitor_id": "drift-monitor-uuid",
  "status": "active",
  "configuration": {
    "lane": "production",
    "warn_threshold": 0.15,
    "block_threshold": 0.25,
    "alpha": 0.2,
    "window_size": 64
  },
  "statistics": {
    "total_analyses": 15234,
    "current_ema": 0.0234,
    "window_utilization": 0.89,
    "decision_distribution": {
      "allow": 14567,
      "warn": 623,
      "block": 44
    }
  },
  "performance": {
    "avg_analysis_time_ms": 0.08,
    "p95_analysis_time_ms": 0.12,
    "throughput_per_second": 450
  }
}
```

## Safety Tags API

### Enrich Plan with Safety Tags

**Endpoint**: `POST /guardian/safety-tags/enrich`

**Description**: Automatically detect and add safety tags to action plans.

**Request**:
```json
{
  "plan": {
    "action": "send_email",
    "params": {
      "recipient": "user@example.com",
      "content": "Please review the financial report",
      "attachments": ["q3_financial_report.pdf"]
    },
    "context": {
      "user_id": "user123",
      "department": "finance"
    }
  },
  "enrichment_options": {
    "enable_caching": true,
    "advanced_detection": true,
    "confidence_threshold": 0.5
  }
}
```

**Response**:
```json
{
  "tagged_plan": {
    "original_plan": { /* original plan */ },
    "detected_tags": [
      {
        "name": "pii",
        "category": "data_sensitivity",
        "confidence": 0.95,
        "description": "Email address detected",
        "metadata": {
          "detected_types": ["email"],
          "pattern_match": "user@example.com"
        }
      },
      {
        "name": "financial",
        "category": "data_sensitivity",
        "confidence": 0.87,
        "description": "Financial data operation",
        "metadata": {
          "detected_types": ["content", "attachment"],
          "keywords": ["financial", "report"]
        }
      }
    ],
    "enrichment_metadata": {
      "enrichment_time_ms": 0.8,
      "detector_count": 6,
      "cache_hit": false,
      "advanced_detection_used": true
    }
  },
  "guardian_assessment": {
    "risk_level": "medium",
    "recommended_action": "require_approval",
    "compliance_flags": ["gdpr", "sox"],
    "audit_required": true
  }
}
```

### Validate Plan Against Ethics DSL

**Endpoint**: `POST /guardian/ethics/validate`

**Request**:
```json
{
  "tagged_plan": {
    "original_plan": { /* plan object */ },
    "detected_tags": [ /* safety tags array */ ]
  },
  "validation_context": {
    "user_role": "financial_analyst",
    "approval_chain": ["manager", "compliance"],
    "compliance_requirements": ["sox", "gdpr"]
  }
}
```

**Response**:
```json
{
  "validation_result": {
    "decision": "require_approval",
    "rules_triggered": [
      {
        "rule_id": "financial_data_approval",
        "condition": "has_tag('financial') AND user_role != 'cfo'",
        "action": "require_approval",
        "approval_chain": ["manager", "compliance_officer"]
      }
    ],
    "compliance_status": {
      "gdpr_compliant": true,
      "sox_compliant": false,
      "additional_requirements": ["executive_approval"]
    }
  },
  "audit_record": {
    "validation_id": "validation-uuid",
    "timestamp": "2025-09-19T15:30:00Z",
    "user_context": "user123",
    "decision_rationale": "Financial data requires approval per SOX compliance"
  }
}
```

## Ring Buffer API

### Create Ring Buffer

**Endpoint**: `POST /infrastructure/ring-buffer`

**Request**:
```json
{
  "capacity": 1000,
  "decimation_config": {
    "pressure_threshold": 0.8,
    "decimation_factor": 2,
    "strategy": "adaptive"
  },
  "monitoring": {
    "enable_metrics": true,
    "alert_on_pressure": true
  }
}
```

**Response**:
```json
{
  "buffer_id": "ring-buffer-uuid",
  "configuration": {
    "capacity": 1000,
    "pressure_threshold": 0.8,
    "decimation_factor": 2,
    "strategy": "adaptive"
  },
  "status": "created",
  "metrics_endpoint": "/infrastructure/ring-buffer/{buffer_id}/metrics"
}
```

### Push Data to Buffer

**Endpoint**: `POST /infrastructure/ring-buffer/{buffer_id}/push`

**Request**:
```json
{
  "data": {
    "consciousness_frame": {
      "id": 12345,
      "timestamp": "2025-09-19T15:30:00Z",
      "state": "active"
    }
  },
  "priority": 5,
  "metadata": {
    "source": "consciousness_ticker",
    "importance": "normal"
  }
}
```

**Response**:
```json
{
  "push_result": {
    "accepted": true,
    "buffer_utilization": 0.67,
    "decimation_triggered": false,
    "position_in_buffer": 667
  },
  "buffer_stats": {
    "current_size": 667,
    "total_pushes": 15234,
    "total_drops": 12,
    "drop_rate": 0.0008
  }
}
```

### Get Buffer Status

**Endpoint**: `GET /infrastructure/ring-buffer/{buffer_id}/status`

**Response**:
```json
{
  "buffer_id": "ring-buffer-uuid",
  "status": "active",
  "utilization": 0.67,
  "capacity": 1000,
  "current_size": 667,
  "backpressure_stats": {
    "total_pushes": 15234,
    "total_drops": 12,
    "drop_rate": 0.0008,
    "decimation_events": 3,
    "last_decimation_utilization": 0.42
  },
  "performance": {
    "avg_push_time_ms": 0.02,
    "p95_push_time_ms": 0.05,
    "throughput_per_second": 1200
  }
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "CONSCIOUSNESS_DRIFT_CRITICAL",
    "message": "Consciousness drift exceeds critical threshold",
    "details": {
      "drift_score": 0.85,
      "threshold": 0.25,
      "lane": "production"
    },
    "timestamp": "2025-09-19T15:30:00Z",
    "request_id": "req-uuid"
  },
  "guardian_action": "immediate_halt",
  "recovery_suggestions": [
    "Review intent-action alignment",
    "Check consciousness system health",
    "Consider manual intervention"
  ]
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `CONSCIOUSNESS_DRIFT_CRITICAL` | 403 | Drift exceeds critical threshold |
| `CONSCIOUSNESS_TICKER_ERROR` | 500 | Ticker coordination failure |
| `RING_BUFFER_OVERFLOW` | 429 | Buffer capacity exceeded |
| `SAFETY_TAG_DETECTION_ERROR` | 500 | Tag detection system failure |
| `GUARDIAN_VALIDATION_ERROR` | 500 | Ethics DSL validation failure |
| `INVALID_VECTOR_DIMENSION` | 400 | Intent/action vector mismatch |
| `UNAUTHORIZED_CONSCIOUSNESS_ACCESS` | 401 | Authentication failure |

## Rate Limiting

### Standard Limits

| Endpoint Category | Rate Limit | Burst Limit |
|------------------|------------|-------------|
| Consciousness Ticker | 100/minute | 200 |
| Drift Analysis | 1000/minute | 2000 |
| Safety Tag Enrichment | 500/minute | 1000 |
| Ring Buffer Operations | 10000/minute | 20000 |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1634567890
X-RateLimit-Burst: 2000
```

## Authentication & Authorization

### API Key Authentication

```http
Authorization: Bearer lukhas_api_key_abcd1234
```

### Lane-Based Access Control

```http
X-Lukhas-Lane: production
X-Lukhas-Permissions: consciousness:read,drift:analyze,safety:enrich
```

### Token Scopes

- `consciousness:read`: Read consciousness state
- `consciousness:write`: Modify consciousness configuration
- `drift:analyze`: Perform drift analysis
- `drift:monitor`: Create and manage drift monitors
- `safety:enrich`: Apply safety tag enrichment
- `safety:validate`: Validate against ethics DSL
- `infrastructure:manage`: Manage ring buffers and core infrastructure

---

**Generated with LUKHAS consciousness-content-strategist**

**Constellation Framework**: ⚛️ Identity-aware API authentication, 🧠 Real-time consciousness coordination, 🛡️ Guardian-validated safety processing

**Performance**: Sub-millisecond API response times with comprehensive monitoring
**Reliability**: Production-grade error handling with automatic recovery
**Security**: Multi-layer authentication with lane-based access control