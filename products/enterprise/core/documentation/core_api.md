---
status: wip
type: documentation
---
# Core API: The Heart of Interaction

This section details the primary endpoints for interacting with the LUKHAS platform, including chat and feedback systems. These are the most commonly used endpoints for building user-facing applications.

## OpenAI Endpoints: The Modulated Conversation

These endpoints provide access to OpenAI's powerful models, enhanced and governed by the LUKHAS modulation and safety systems.

### POST /openai/chat

This is the primary endpoint for stateful, modulated chat conversations. It takes a user's prompt and returns a response that has been processed through the LUKHAS cognitive architecture, ensuring safety, coherence, and alignment with the system's principles.

**Request Body**

`application/json`

| Field | Type | Description |
|---|---|---|
| `prompt` | string | **Required.** The text input from the user. |
| `context` | object | Additional context for the conversation. |
| `task` | string | A specific task hint for the model. |

**Example Request**

```json
{
  "prompt": "Explain the concept of neural plasticity in simple terms.",
  "context": {
    "user_id": "user-123",
    "session_id": "session-abc"
  },
  "task": "educational_explanation"
}
```

**Responses**

- **`200 OK`**: The request was successful and a response was generated.
- **`422 Unprocessable Entity`**: The request was malformed.

**Example Response (`200 OK`)**

```json
{
  "content": "Neural plasticity is like your brain's ability to rewire itself...",
  "raw": {
    "id": "chatcmpl-...",
    "object": "chat.completion",
    "created": 1705318200,
    "model": "gpt-4o-2024-05-13",
    "choices": [...]
  },
  "modulation": {
    "safety_check_passed": true,
    "constitutional_alignment_score": 0.98
  },
  "metadata": {
    "processing_time_ms": 450
  }
}
```

### POST /openai/chat/stream

For real-time, interactive experiences, the streaming endpoint allows you to receive the response as it's being generated. This is ideal for chatbot UIs where you want to display the text token by token.

The request body is identical to the `/openai/chat` endpoint.

**Request Body**

`application/json`

| Field | Type | Description |
|---|---|---|
| `prompt` | string | **Required.** The text input from the user. |
| `context` | object | Additional context for the conversation. |
| `task` | string | A specific task hint for the model. |

**Responses**

- **`200 OK`**: The stream will begin. The response body will be a stream of Server-Sent Events (SSE).
- **`422 Unprocessable Entity`**: The request was malformed.

**Example Stream Events**

```
event: content
data: {"chunk": "Neural"}

event: content
data: {"chunk": " plasticity"}

event: content
data: {"chunk": " is"}

...

event: modulation
data: {"safety_check_passed": true, "constitutional_alignment_score": 0.98}

event: end
data: {"reason": "stop"}
```

## Feedback Endpoints: The Channels of Expression

These endpoints are the channels through which human expression flows into the LUKHAS system, enabling continuous learning and alignment. They are designed to capture the nuance of user feedback in a structured way.

### POST /feedback/capture

This is the primary endpoint for submitting feedback about a specific AI interaction. It allows for a rich, multi-faceted feedback object to be recorded against a specific action.

**Request Body**

`application/json`

| Field | Type | Description |
|---|---|---|
| `action_id` | string | **Required.** The unique identifier of the action being rated. |
| `rating` | integer | **Required.** A numerical rating from 1 to 5. |
| `note` | string | Optional text feedback providing more detail. |
| `symbols` | array of strings | Optional user-selected symbols that represent their feeling or intent. |
| `context` | object | Additional context about the feedback. |
| `user_id` | string | An identifier for the user providing feedback (will be hashed for privacy). |

**Example Request**

```json
{
  "action_id": "resp-abc-123",
  "rating": 5,
  "note": "This was an incredibly insightful and helpful response.",
  "symbols": ["clarity", "helpful", "insightful"],
  "context": {
    "ui_location": "main_chat_window"
  },
  "user_id": "user-456"
}
```

**Responses**

- **`200 OK`**: The feedback was successfully captured.
- **`422 Unprocessable Entity`**: The request was malformed.

**Example Response (`200 OK`)**

```json
{
  "card_id": "feedback-xyz-789",
  "rating": 5,
  "timestamp": 1705318200,
  "message": "Feedback captured successfully"
}
```

### POST /feedback/batch

For scenarios where feedback is collected and sent in bulk, this endpoint provides an efficient way to submit multiple feedback cards in a single request.

**Request Body**

`application/json`

The request body is an array of `FeedbackRequest` objects, as defined in the `/feedback/capture` endpoint.

**Example Request**

```json
[
  {
    "action_id": "resp-abc-123",
    "rating": 5,
    "note": "This was great.",
    "user_id": "user-456"
  },
  {
    "action_id": "resp-def-456",
    "rating": 2,
    "note": "This response was confusing.",
    "symbols": ["confusing"],
    "user_id": "user-789"
  }
]
```

**Responses**

- **`200 OK`**: The batch of feedback was successfully captured. The response is an array of `FeedbackResponse` objects.
- **`422 Unprocessable Entity`**: The request was malformed.

**Example Response (`200 OK`)**

```json
[
  {
    "card_id": "feedback-xyz-789",
    "rating": 5,
    "timestamp": 1705318200,
    "message": "Feedback captured successfully"
  },
  {
    "card_id": "feedback-uvw-123",
    "rating": 2,
    "timestamp": 1705318201,
    "message": "Feedback captured successfully"
  }
]
```

### GET /feedback/report/{user_id}

This endpoint provides a report on what the LUKHAS system has learned from a specific user's feedback. It is a window into the AI's adaptation process, showing how user preferences and patterns are identified and incorporated.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | string | **Required.** The identifier for the user. |

**Responses**

- **`200 OK`**: The learning report was successfully generated.
- **`422 Unprocessable Entity`**: The user ID was invalid.

**Example Response (`200 OK`)**

```json
{
  "user_id_hash": "hashed-user-456",
  "total_feedback_cards": 27,
  "overall_satisfaction": 4.8,
  "improvement_trend": 0.15,
  "preferred_styles": [
    "concise",
    "educational",
    "technical"
  ],
  "summary": "The user prefers detailed, technical explanations but values conciseness. They respond positively to proactive suggestions.",
  "recommendations": {
    "response_length": "medium",
    "formality": "professional"
  }
}
```

### GET /feedback/metrics

This endpoint provides a high-level overview of the feedback system's health and performance. It is useful for monitoring the overall state of the learning and alignment processes.

**Responses**

- **`200 OK`**: The system metrics were successfully retrieved.

**Example Response (`200 OK`)**

```json
{
  "cards_captured": 15234,
  "patterns_identified": 876,
  "policies_updated": 123,
  "validations_passed": 15201,
  "validations_failed": 33,
  "total_cards": 15234,
  "total_patterns": 876,
  "total_updates": 123
}
```
