# LLM Wrappers — Unified Clients and Modulated Services
## Swappable providers with retries, streaming, and safety (⚛️🧠🛡️)

Purpose
- Provide thin, testable wrappers for provider SDKs and compose them into higher-level, signal-aware services.

Primary components
- `UnifiedOpenAIClient` — async client; retries; task-based model mapping; streaming support
- `OpenAIModulatedService` — signals → modulation → retrieval v1 → moderation → OpenAI call

Contracts (abridged)
- generate(request) → { text, model, modulation, usage? }
- generate_stream(request) → async iterator[str]

Safety and observability
- Pre/post moderation hooks (Guardian-first with safe fallback)
- Metrics counters for requests/streams/blocks (surfaced by serve)

Testing
- Fake client/service adapters enable network-free unit tests for both non-stream and stream flows.

Trinity alignment
- ⚛️ Stable interfaces for identity and audit
- 🧠 Modulation and context weaving for cognition
- 🛡️ Defense-in-depth via moderation hooks
