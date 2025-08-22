# Bridge Layer — Provider Adapters with Endocrine Modulation
## Where vendor SDKs meet our Trinity patterns (⚛️🧠🛡️)

Purpose
- Centralize provider logic (OpenAI, Anthropic, Azure, Gemini) and keep serve/orchestration clean.
- Compose signals → homeostasis → prompt modulation → provider calls, with safety and metrics.

What’s here
- `llm_wrappers/` — provider-specific clients and services
- `openai_modulated_service.py` — orchestrates signals, retrieval v1, moderation, streaming
- `unified_openai_client.py` — async OpenAI client with retries and task model mapping

Why it matters
- Swap providers without touching API or orchestration logic.
- Enforce best practices (retries, rate handling, safety) in one place.

How it connects
- serve → bridge/llm_wrappers → external LLMs
- orchestration/signals → modulation inputs (stress/urgency/trust)
- Guardian moderation hooks (pre/post) wrap outbound and inbound content

Key features
- Modulation: styles/params tuned by signals and homeostasis
- Retrieval v1: simple context notes injection; pluggable retriever later
- Streaming: token generator with post-moderation of concatenated text
- Metrics: counters for requests/streams/blocks; exposed via serve
- Testability: fake clients keep unit tests network-free

Trinity alignment
- ⚛️ Identity: stable adapter interfaces and traceable model choices
- 🧠 Consciousness: context weaving and modulation under dynamic conditions
- 🛡️ Guardian: moderation-first design with safe fallbacks
