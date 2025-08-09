# Serve Layer — Trinity-Aligned API Surface
## FastAPI boundary for Identity (⚛️), Consciousness (🧠), and Guardian (🛡️)

Purpose & vision
- Provide a clean, stable HTTP interface that exposes modulated LLM capabilities and symbolic services without leaking vendor details.
- Keep API contracts steady while internals (models, modulation, retrieval, guardrails) evolve safely.

What’s here
- App entry: `serve/main.py`
- OpenAI routes: `serve/openai_routes.py` — POST `/openai/chat`, POST `/openai/chat/stream`, GET `/openai/metrics`
- Schemas: `serve/schemas.py` — request/response DTOs with modulation metadata
- Other routers (if present): core symbolic endpoints (dreams, glyphs, tiers)

Why it matters
- Consistent boundary for products and tools; swap providers behind the bridge.
- Signal-aware behavior improves quality under stress/urgency while maintaining safety.

How it connects
- serve → bridge/llm_wrappers → external providers
- serve → orchestration/signals → Homeostasis + Prompt Modulation
- Guardian hooks (pre/post moderation) wrap provider calls where enabled

Key features
- Modulated chat: injects signal-driven parameters and optional retrieval context
- Streaming: token-yielding responses via FastAPI StreamingResponse
- Metrics: lightweight counters for requests/streams/blocks via `/openai/metrics`
- Testability: fake clients/services enable network-free unit tests

Contracts (abridged)
- POST `/openai/chat` → { text, model, modulation, usage? }
- POST `/openai/chat/stream` → text/plain chunked tokens
- GET `/openai/metrics` → { requests, streams, moderation_blocks }
See `docs/OPENAI_ENDPOINTS.md` for full payloads and examples.

Operational notes
- Requires `OPENAI_API_KEY` to hit real backends; tests use fakes (no network).
- Streaming path is isolated; add a fake streaming iterator for test coverage.

Roadmap links
- Endpoint reference: `docs/OPENAI_ENDPOINTS.md`
- Multimodal plan: `docs/MULTIMODAL_LANGUAGE_PLAN.md`

Trinity alignment
- ⚛️ Identity: stable contracts and auth hooks at the boundary
- 🧠 Consciousness: signal-informed modulation and context weaving
- 🛡️ Guardian: pre/post moderation and safe fallbacks
