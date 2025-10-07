---
status: wip
type: documentation
owner: unknown
module: api
redirect: false
moved_to: null
---

# OpenAI Modulated Endpoints

This document describes the new FastAPI endpoints that expose the LUKHAS OpenAI Modulated Service.

## Overview

- Base router: `/openai`
- Core idea: Thread LUKHAS signal-based modulation (Homeostasis + PromptModulator) into OpenAI calls.
- Safety: Pre/Post moderation hooks are present as stubs to integrate with Guardian.

## Endpoints

### POST /openai/chat

Generate content from OpenAI with LUKHAS modulation applied.

Request body:

```
{
  "prompt": "string",
  "context": { "any": "json" },  // optional
  "task": "general|reasoning|creativity|coding|..." // optional
}
```

Response body:

```
{
  "content": "string",               // assistant content
  "raw": { /* raw OpenAI response */ },
  "modulation": {
    "style": "DEFAULT|...",
    "params": { "temperature": 0.7, "max_tokens": 2000, ... },
    "signal_levels": { "NOVELTY": 0.8, ... }
  },
  "metadata": { "moderation": "safe", ... }
}
```

Notes:
- `task` maps to model selection via `UnifiedOpenAIClient.TASK_MODELS`.
- `context` is passed to the modulator; homeostasis derives params when not provided.
- The service performs only stub moderation; wire Guardian or OpenAI moderation next.

## Environment

- Requires `OPENAI_API_KEY` at runtime.
- Optional: `OPENAI_ORGANIZATION_ID`, `OPENAI_PROJECT`.

## Implementation Pointers

- Code:
  - Router: `serve/openai_routes.py`
  - Schemas: `serve/schemas.py` (`ModulatedChatRequest`/`ModulatedChatResponse`)
  - Service: `bridge/llm_wrappers/openai_modulated_service.py`
  - Unified client: `bridge/llm_wrappers/unified_openai_client.py`
- App entrypoint includes the router: `serve/main.py`.

## Roadmap Add-ons

- Moderation: Implement Guardian hooks in `_pre_moderation_check` and `_post_moderation_check`.
- Retrieval v1: Inject retrieved context when `retrieval_k` is set in modulation params.
- Streaming: Add a `/openai/chat/stream` SSE/WS endpoint returning token chunks.
- Metrics: Log modulation and result metadata to `data/` for monitoring.

## Try It (local)

- Start FastAPI app (example):
  - `uvicorn serve.main:app --reload` (optional)
- POST example:
  - `curl -X POST http://localhost:8000/openai/chat -H 'Content-Type: application/json' -d '{"prompt":"hello"}'`
