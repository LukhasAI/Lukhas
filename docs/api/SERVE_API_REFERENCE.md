# LUKHAS Serve API Reference

This document provides a comprehensive reference for the LUKHAS Serve API.

## Dream API

### POST /api/v1/dreams/simulate

**Summary:** Create Dream Simulation

**Description:** This endpoint generates a new dream sequence based on an optional seed and constraints.

**Authentication:** Requires a valid API key passed in the `X-API-Key` header.

**Request Body:**

```json
{
  "seed": "string",
  "context": "object (optional)",
  "parallel": "boolean (optional, default: false)"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/dreams/simulate" \
-H "Content-Type: application/json" \
-H "X-API-Key: YOUR_API_KEY" \
-d '{
  "seed": "example_seed"
}'
```

**Responses:**

*   **200 OK:** Dream sequence generated successfully.
*   **422 Unprocessable Entity:** Validation error.

## OpenAI Compatibility API

These endpoints provide compatibility with the OpenAI API format.

**Authentication:** Requires a bearer token passed in the `Authorization` header (e.g., `Authorization: Bearer YOUR_TOKEN`).

**Rate Limiting:** All responses include the following headers to provide information about rate limits:
*   `X-RateLimit-Limit`: The maximum number of requests you're permitted to make per minute.
*   `X-RateLimit-Remaining`: The number of requests remaining in the current rate limit window.
*   `X-RateLimit-Reset`: The time at which the current rate limit window resets, in UTC epoch seconds.

### GET /v1/models

**Summary:** List Models

**Description:** Retrieves a list of available models.

**Example Request:**

```bash
curl -X GET "http://localhost:8000/v1/models" \
-H "Authorization: Bearer YOUR_TOKEN"
```

**Responses:**

*   **200 OK:** A list of available models.

    ```json
    {
      "object": "list",
      "data": [
        {
          "id": "lukhas-mini",
          "object": "model",
          "owned_by": "lukhas"
        },
        {
          "id": "lukhas-embed-1",
          "object": "model",
          "owned_by": "lukhas"
        },
        {
          "id": "text-embedding-ada-002",
          "object": "model",
          "owned_by": "lukhas"
        },
        {
          "id": "gpt-4",
          "object": "model",
          "owned_by": "lukhas"
        }
      ]
    }
    ```

### POST /v1/embeddings

**Summary:** Create Embeddings

**Description:** Creates deterministic embeddings from input text.

**Request Body:**

```json
{
  "input": "Your text to embed",
  "model": "text-embedding-ada-002",
  "dimensions": 1536
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/v1/embeddings" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "input": "hello world",
  "model": "text-embedding-ada-002"
}'
```

**Responses:**

*   **200 OK:** Embeddings created successfully.

    ```json
    {
      "object": "list",
      "data": [
        {
          "object": "embedding",
          "embedding": [
            0.5019607843137255,
            ...
          ],
          "index": 0
        }
      ],
      "model": "text-embedding-ada-002",
      "usage": {
        "prompt_tokens": 2,
        "total_tokens": 2
      }
    }
    ```

### POST /v1/chat/completions

**Summary:** Create Chat Completion (Stub)

**Description:** A stub endpoint for chat completions, primarily for soak testing. It returns a fixed response.

**Request Body:**

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    }
  ]
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "Hello!"}]
}'
```

**Responses:**

*   **200 OK:** A stub chat completion response.

    ```json
    {
      "id": "chatcmpl-1633891200",
      "object": "chat.completion",
      "created": 1633891200,
      "model": "gpt-4",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "This is a stub response for RC soak testing."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 1,
        "completion_tokens": 8,
        "total_tokens": 9
      }
    }
    ```

### POST /v1/responses

**Summary:** Create Response

**Description:** LUKHAS-specific responses endpoint that provides both streaming and non-streaming chat responses in an OpenAI-compatible format.

**Request Body:**

```json
{
  "model": "lukhas-mini",
  "input": "Tell me a joke.",
  "stream": false
}
```

**Example Request (non-streaming):**

```bash
curl -X POST "http://localhost:8000/v1/responses" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "model": "lukhas-mini",
  "input": "Tell me a joke."
}'
```

**Example Request (streaming):**

```bash
curl -X POST "http://localhost:8000/v1/responses" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_TOKEN" \
-d '{
  "model": "lukhas-mini",
  "input": "Tell me a joke.",
  "stream": true
}'
```

**Responses:**

*   **200 OK (non-streaming):**

    ```json
    {
      "id": "resp_abc123",
      "object": "chat.completion",
      "created": 1633891200,
      "model": "lukhas-mini",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "[stub] Tell me a joke."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 4,
        "completion_tokens": 5,
        "total_tokens": 9
      }
    }
    ```

*   **200 OK (streaming):** A Server-Sent Events (SSE) stream.

    ```
    data: {"id":"resp_abc123", "object":"chat.completion.chunk", ...}

    data: {"id":"resp_abc123", "object":"chat.completion.chunk", ...}

    data: [DONE]
    ```
*   **400 Bad Request:** Missing or empty input.

## Feedback API

The Feedback API allows for human-in-the-loop learning by capturing user feedback on AI actions.

### POST /feedback/capture

**Summary:** Capture Feedback

**Description:** Captures user feedback for a single AI action.

**Request Body:**

```json
{
  "action_id": "string",
  "rating": "integer (1-5)",
  "note": "string (optional)",
  "symbols": ["string"],
  "context": {},
  "user_id": "string (optional)"
}
```

**Responses:**

*   **200 OK:**

    ```json
    {
      "card_id": "card_123",
      "rating": 5,
      "timestamp": 1730000000.0,
      "message": "Feedback captured successfully"
    }
    ```
*   **500 Internal Server Error**

### POST /feedback/batch

**Summary:** Capture Batch Feedback

**Description:** Captures multiple feedback cards at once.

**Request Body:** An array of feedback capture objects (see `/feedback/capture`).

**Responses:**

*   **200 OK:** An array of feedback responses.
*   **500 Internal Server Error**

### GET /feedback/report/{user_id}

**Summary:** Get Learning Report

**Description:** Generates a learning report for a specific user, explaining what the system has learned from their feedback.

**Responses:**

*   **200 OK:**

    ```json
    {
      "user_id_hash": "hashed_user_id",
      "total_feedback_cards": 10,
      "overall_satisfaction": 4.5,
      "improvement_trend": 0.2,
      "preferred_styles": ["direct", "concise"],
      "summary": "Based on 10 feedback cards...",
      "recommendations": {
        "tone": "more formal"
      }
    }
    ```
*   **500 Internal Server Error**

### GET /feedback/metrics

**Summary:** Get System Metrics

**Description:** Retrieves overall feedback system metrics.

**Responses:**

*   **200 OK:**

    ```json
    {
      "cards_captured": 100,
      "patterns_identified": 20,
      "policies_updated": 5,
      "validations_passed": 5,
      "validations_failed": 0,
      "total_cards": 500,
      "total_patterns": 50,
      "total_updates": 10
    }
    ```
*   **500 Internal Server Error**

### POST /feedback/trigger-learning

**Summary:** Trigger Learning Cycle

**Description:** Manually triggers a learning cycle to extract patterns from recent feedback and generate policy updates.

**Responses:**

*   **200 OK:**

    ```json
    {
      "status": "triggered",
      "message": "Learning cycle triggered with 50 feedback cards"
    }
    ```
*   **500 Internal Server Error**

### GET /feedback/health

**Summary:** Health Check

**Description:** Checks the health of the feedback system.

**Responses:**

*   **200 OK:** System is healthy.
*   **503 Service Unavailable:** System is unhealthy.

## Tracing API

The Tracing API provides endpoints for retrieving trace data from the MATRIZ system.

**Authentication:** No authentication required.

### GET /traces/latest

**Summary:** Get latest MATRIZ trace

**Description:** Retrieve the most recent trace from the MATRIZ traces directory.

**Responses:**

*   **200 OK:** JSON trace data with trace_id.
*   **404 Not Found:** No traces available.

### GET /traces/{trace_id}

**Summary:** Get trace by ID

**Description:** Retrieve a specific trace by its ID.

**Responses:**

*   **200 OK:** The requested trace data.
*   **404 Not Found:** Trace not found.

### GET /traces/

**Summary:** List available traces with metadata

**Description:** List traces across sources with paging and filters.

**Query Parameters:**

*   `offset`: `integer` (optional, default: 0)
*   `limit`: `integer` (optional, default: 100, max: 200)
*   `source`: `string` (optional, enum: "env", "live", "golden")
*   `q`: `string` (optional) - Substring match on ID or filename.

**Responses:**

*   **200 OK:** A list of traces.

## Health and Metrics API

These endpoints provide information about the health and performance of the LUKHAS API.

### GET /healthz

**Summary:** Health Check

**Description:** A health check endpoint for monitoring systems. It always returns a 200 OK response and provides detailed status information in the response body.

**Responses:**

*   **200 OK:**

    ```json
    {
      "status": "ok",
      "voice_mode": "degraded",
      "degraded_reasons": ["voice"],
      "matriz": {
        "version": "1.2.3",
        "rollout": "enabled",
        "enabled": true
      },
      "lane": "prod",
      "modules": {
        "manifest_count": 10
      }
    }
    ```

### GET /health

**Summary:** Health Check (Alias)

**Description:** An alias for `/healthz` for compatibility with older operational scripts.

### GET /readyz

**Summary:** Readiness Check

**Description:** A readiness check endpoint for Kubernetes and other orchestration systems. Returns a 200 OK response with `{"status": "ready"}` if the service is ready to accept traffic, and a non-200 response otherwise.

### GET /metrics

**Summary:** Prometheus Metrics

**Description:** Exposes a wide range of performance and operational metrics in the Prometheus format.
