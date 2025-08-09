# Documentation Hub — Trinity Guide and References
## Endpoints, modulation, multimodal roadmap (⚛️🧠🛡️)

Scope
- Central index for API docs, architectural notes, and alignment plans.

Key docs
- `OPENAI_ENDPOINTS.md` — `/openai` routes; request/response shapes; streaming and metrics
- `MULTIMODAL_LANGUAGE_PLAN.md` — staged plan for emojis, images, audio, gestures
- `ROADMAP_OPENAI_ALIGNMENT.md` — strategy and milestones (linked from root README)

System mapping
- serve (API boundary) ↔ bridge (providers) ↔ orchestration/signals (endocrine)
- Guardian moderation woven before/after provider calls

Contributing
- Prefer network-free examples with fakes; keep payloads copy-paste friendly.
