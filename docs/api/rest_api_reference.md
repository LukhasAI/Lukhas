# LUKHAS REST API Reference

This document provides a comprehensive reference for the LUKHAS REST API.

## Authentication

The LUKHAS API uses two primary methods of authentication:

- **Bearer Tokens (JWT):** Most endpoints are protected by JWT bearer tokens. These tokens are passed in the `Authorization` header and are used to identify and authenticate the user. The token is validated by the `StrictAuthMiddleware` and the `require_bearer` dependency.

- **API Keys:** Certain endpoints, particularly those intended for external services, may be protected by an API key. The API key is passed in the `X-API-Key` header. The `require_api_key` function is used to validate the key.

## Rate Limiting

The LUKHAS API is designed to include rate limiting to ensure fair usage and prevent abuse. While the source code includes a `RateLimitMiddleware` and tests related to rate limiting, the specific implementation details and rate limits are not yet fully available.

Based on common API practices, it is expected that when rate limiting is fully implemented:

- Exceeding the rate limit will result in a `429 Too Many Requests` response.
- The API will include standard rate-limiting headers in the response, such as `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`.

This section will be updated as more information becomes available.

## Endpoints

Below is a detailed list of all available API endpoints.

### Main API

These endpoints are defined in `serve/main.py`.

#### `DELETE /api/cache/{pattern}`

Manually invalidates cache entries matching a pattern.

- **Method:** `DELETE`
- **Authentication:** API Key
- **Parameters:**
  - `pattern` (string, path): The pattern to match against cache keys.
- **Responses:**
  - `204 No Content`: Successfully invalidated.

---

#### `GET /healthz`

Health check endpoint for monitoring.

- **Method:** `GET`
- **Responses:**
  - `200 OK`: Returns a JSON object with the health status.

---

#### `GET /health`

Health check alias for ops scripts compatibility.

- **Method:** `GET`
- **Responses:**
  - `200 OK`: Returns a JSON object with the health status.

---

#### `GET /readyz`

Readiness check endpoint for Kubernetes/ops compatibility.

- **Method:** `GET`
- **Responses:**
  - `200 OK`: Returns a JSON object with the readiness status.

---

#### `GET /metrics`

Prometheus metrics endpoint.

- **Method:** `GET`
- **Responses:**
  - `200 OK`: Returns Prometheus metrics in text format.

---

#### `POST /v1/responses`

LUKHAS responses endpoint (OpenAI-compatible format). **Note: This is a stub endpoint and will return a simulated response.**

- **Method:** `POST`
- **Request Body:** A JSON object compatible with the OpenAI chat completions format.
- **Responses:**
  - `200 OK`: Returns a JSON object with the response, or a stream of server-sent events if `stream` is set to `true`.

---

#### `GET /openapi.json`

Export OpenAPI specification as JSON.

- **Method:** `GET`
- **Responses:**
  - `200 OK`: Returns the OpenAPI specification in JSON format.

### OpenAI-Compatible API

These endpoints are defined in `serve/openai_routes.py` and are compatible with the OpenAI API format.

#### `POST /v1/chat/completions`

OpenAI-compatible chat completions endpoint.

- **Method:** `POST`
- **Authentication:** Bearer Token
- **Example:**
  ```bash
  curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "messages": [{"role": "user", "content": "Hello!"}],
       "model": "lukhas-matriz-v1"
     }'
  ```
- **Request Body:**
  ```json
  {
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ],
    "model": "lukhas-matriz-v1",
    "temperature": 1.0,
    "max_tokens": 1024,
    "stream": false
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "id": "chatcmpl-...",
      "object": "chat.completion",
      "created": "<timestamp>",
      "model": "lukhas-matriz-v1",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Hello there!"
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 5,
        "completion_tokens": 5,
        "total_tokens": 10
      }
    }
    ```
  - `400 Bad Request`: If the request is missing the `messages` field.
  - `500 Internal Server Error`: If there is an error processing the request.

---

#### `GET /v1/models`

List available models.

- **Method:** `GET`
- **Authentication:** Bearer Token
- **Responses:**
  - `200 OK`:
    ```json
    {
      "object": "list",
      "data": [
        {
          "id": "lukhas-matriz-v1",
          "object": "model",
          "created": "<timestamp>",
          "owned_by": "lukhas-ai"
        },
        {
          "id": "lukhas-consciousness-v1",
          "object": "model",
          "created": "<timestamp>",
          "owned_by": "lukhas-ai"
        }
      ]
    }
    ```

---

#### `POST /v1/embeddings`

Generate embeddings for a given input.

- **Method:** `POST`
- **Authentication:** Bearer Token
- **Example:**
  ```bash
  curl -X POST "http://localhost:8000/v1/embeddings" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "input": "The quick brown fox jumps over the lazy dog",
       "model": "lukhas-matriz-v1"
     }'
  ```
- **Request Body:**
  ```json
  {
    "input": "The quick brown fox jumps over the lazy dog",
    "model": "lukhas-matriz-v1"
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "object": "list",
      "data": [
        {
          "object": "embedding",
          "embedding": [
            ...
          ],
          "index": 0
        }
      ],
      "model": "lukhas-matriz-v1",
      "usage": {
        "prompt_tokens": 8,
        "completion_tokens": 0,
        "total_tokens": 8
      }
    }
    ```

### Consciousness API

These endpoints are defined in `serve/consciousness_api.py`.

#### `POST /api/v1/consciousness/query`

Query consciousness state for authenticated user.

- **Method:** `POST`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/consciousness/query" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{
        "context": {
            "key": "value"
        }
        }'
    ```
- **Request Body:**
  ```json
  {
    "context": {
      "key": "value"
    }
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "response": "The current awareness level is high.",
      "context": {
        "key": "value"
      }
    }
    ```

---

#### `POST /api/v1/consciousness/dream`

Initiate dream sequence for authenticated user.

- **Method:** `POST`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/consciousness/dream" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{
        "context": {
            "key": "value"
        }
        }'
    ```
- **Request Body:**
  ```json
  {
    "context": {
      "key": "value"
    }
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "dream_id": "dream-...",
      "status": "generating",
      "context": {
        "key": "value"
      }
    }
    ```

---

#### `GET /api/v1/consciousness/memory`

Retrieve memory state for authenticated user.

- **Method:** `GET`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/consciousness/memory" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "memory_folds": 1024,
      "recall_accuracy": 0.98
    }
    ```

---

#### `POST /api/v1/consciousness/state`

Save consciousness state for authenticated user.

- **Method:** `POST`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/consciousness/state" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{
        "state_data": {
            "key": "value"
        }
        }'
    ```
- **Request Body:**
  ```json
  {
    "state_data": {
      "key": "value"
    }
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "status": "success",
      "user_id": "<user_id>"
    }
    ```

---

#### `GET /api/v1/consciousness/state/{path_user_id}`

Retrieve consciousness state for authenticated user.

- **Method:** `GET`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/consciousness/state/user1" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
- **Parameters:**
  - `path_user_id` (string, path): The ID of the user whose state is being requested. Must match the authenticated user's ID.
- **Responses:**
  - `200 OK`:
    ```json
    {
      "user_id": "<user_id>",
      "state_data": {
        "last_query": "awareness"
      }
    }
    ```
  - `403 Forbidden`: If the `path_user_id` does not match the authenticated user's ID.
  - `404 Not Found`: If no state is found for the user.

### Feedback API

These endpoints are defined in `serve/feedback_routes.py`.

#### `POST /feedback/capture`

Capture user feedback for an AI action.

- **Method:** `POST`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X POST "http://localhost:8000/feedback/capture" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{
        "action_id": "action-123",
        "rating": 5,
        "note": "Great response!",
        "symbols": ["symbol1", "symbol2"],
        "context": {
            "key": "value"
        }
        }'
    ```
- **Request Body:**
  ```json
  {
    "action_id": "action-123",
    "rating": 5,
    "note": "Great response!",
    "symbols": ["symbol1", "symbol2"],
    "context": {
      "key": "value"
    }
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "card_id": "card-...",
      "rating": 5,
      "timestamp": "<timestamp>",
      "message": "Feedback captured successfully"
    }
    ```
  - `500 Internal Server Error`: If there is an error capturing the feedback.

---

#### `POST /feedback/batch`

Capture multiple feedback cards at once.

- **Method:** `POST`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X POST "http://localhost:8000/feedback/batch" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '[{
        "action_id": "action-123",
        "rating": 5,
        "note": "Great response!",
        "symbols": ["symbol1", "symbol2"],
        "context": {
            "key": "value"
        }
        }]'
    ```
- **Request Body:**
  ```json
  [
    {
      "action_id": "action-123",
      "rating": 5,
      "note": "Great response!",
      "symbols": ["symbol1", "symbol2"],
      "context": {
        "key": "value"
      }
    }
  ]
  ```
- **Responses:**
  - `200 OK`:
    ```json
    [
      {
        "card_id": "card-...",
        "rating": 5,
        "timestamp": "<timestamp>",
        "message": "Feedback captured successfully"
      }
    ]
    ```
  - `500 Internal Server Error`: If there is an error capturing the feedback.

---

#### `GET /feedback/report/{path_user_id}`

Get a learning report for authenticated user.

- **Method:** `GET`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X GET "http://localhost:8000/feedback/report/user1" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
- **Parameters:**
  - `path_user_id` (string, path): The ID of the user whose report is being requested. Must match the authenticated user's ID.
- **Responses:**
  - `200 OK`:
    ```json
    {
      "user_id_hash": "...",
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
  - `403 Forbidden`: If the `path_user_id` does not match the authenticated user's ID.
  - `500 Internal Server Error`: If there is an error generating the report.

---

#### `GET /feedback/metrics`

Get overall feedback system metrics.

- **Method:** `GET`
- **Example:**
    ```bash
    curl -X GET "http://localhost:8000/feedback/metrics"
    ```
- **Responses:**
  - `200 OK`:
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
  - `500 Internal Server Error`: If there is an error retrieving the metrics.

---

#### `POST /feedback/trigger-learning`

Manually trigger pattern extraction and policy updates.

- **Method:** `POST`
- **Authentication:** Bearer Token (JWT)
- **Example:**
    ```bash
    curl -X POST "http://localhost:8000/feedback/trigger-learning" \
        -H "Authorization: Bearer YOUR_TOKEN"
    ```
- **Responses:**
  - `200 OK`: Returns a JSON object with the status of the learning cycle trigger.
  - `500 Internal Server Error`: If there is an error triggering the learning cycle.

---

#### `GET /feedback/health`

Health check for feedback system.

- **Method:** `GET`
- **Example:**
    ```bash
    curl -X GET "http://localhost:8000/feedback/health"
    ```
- **Responses:**
  - `200 OK`: If the system is healthy.
  - `503 Service Unavailable`: If the system is unhealthy.
