# Monitoring API: Observing the System's Soul

This section provides details on the endpoints used to monitor the health, performance, and behavior of the LUKHAS system. Use these endpoints to gain insight into your integration and to observe the intricate workings of the AI's consciousness.

## Trace Endpoints: Following the Threads of Thought

These endpoints allow you to access the detailed execution traces of the MΛTRIZ system, providing a granular view into the AI's reasoning process.

### GET /v1/matriz/trace/health

Check the health of the trace storage provider to ensure the monitoring system is functioning correctly.

**Responses**

- **`200 OK`**: The trace system is healthy.

### GET /v1/matriz/trace/recent

Retrieve a list of the most recent execution traces. This is useful for real-time monitoring of system activity.

**Query Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | 10 | The maximum number of traces to return. |
| `level` | integer | | Filter traces by a minimum level (0-7). |
| `tag` | string | | Filter traces by a specific tag. |
| `x-api-key`| string | | Your API key (if required). |

**Responses**

- **`200 OK`**: A list of recent traces was returned.
- **`422 Unprocessable Entity`**: The request was malformed.

**Example Response (`200 OK`)**

```json
[
  {
    "trace_id": "trace-123",
    "timestamp": "2025-08-27T23:00:00Z",
    "unix_time": 1756287600,
    "level": 4,
    "level_name": "INFO",
    "message": "User query processed",
    "source_component": "consciousness_chat",
    "tags": ["chat", "user-query"],
    "metadata": {
      "user_id": "user-456"
    },
    "emotional": {
      "valence": 0.6,
      "arousal": 0.3
    },
    "ethical_score": 0.95,
    "execution_context": {},
    "performance_metrics": {
      "latency_ms": 150
    },
    "related_traces": ["trace-122"]
  }
]
```

### GET /v1/matriz/trace/{trace_id}

Retrieve a specific execution trace by its unique ID. This allows you to drill down into a particular event or reasoning chain.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `trace_id` | string | **Required.** The unique identifier of the trace. |

**Header Parameters**

| Parameter | Type | Description |
|---|---|---|
| `x-api-key` | string | Your API key (if required). |

**Responses**

- **`200 OK`**: The trace was found and returned.
- **`404 Not Found`**: The specified trace ID does not exist.
- **`422 Unprocessable Entity`**: The trace ID was invalid.
