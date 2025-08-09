# LUKHAS PWM × OpenAI: Augmentation-First Plan and Roadmap

Last updated: 2025-08-09

This roadmap translates the audit’s 1–5 points into a concrete, staged plan that amplifies OpenAI (and GPT‑5) rather than competing with it. Lukhas orchestrates, safeguards, personalizes, and explains; OpenAI models do the cognitive heavy lifting.

## Principles
- Augment, don’t replace: Lukhas steers; OpenAI thinks and perceives.
- Safety-by-default: Guardian and moderation gate all model I/O.
- Privacy-by-design: Personal symbols live on-device; server sees only aggregates.
- Interpretability-first: Every output has a reason trail (signals, policies, memory).

## 1) What Lukhas does without competing with OpenAI
- Orchestration: Endocrine signal bus + homeostasis adapt prompts/params/tools by state (stress, novelty, alignment_risk).
- Safety governor: Guardian rule checks, ethical frameworks, drift detection, audit trail.
- Long-horizon memory & personalization: Symbolic + vector memory, per-user policy, session stitching.
- Interpretability: Persist “why” bundles (signals fired, moderation, policy decisions).
- Bounded human learning: Feedback cards compile into constrained policy LUT deltas.
- Identity, roles, consent: Tiered permissions and usage policy enforcement.
- Private symbol language: On-device emoji/gesture → intent mapping; reversible translation in prompts.

## 2) Features that complement OpenAI
- Endocrine-driven prompt modulation (temperature/top_p/max_tokens/tool gates) within safe bounds.
- Dual safety: Guardian + OpenAI moderation, pre/post on input/output and feedback.
- Context discipline: Retrieve minimal relevant context from memory/embeddings.
- Tool orchestration: Reliable function calling, retries/backoff, idempotency, and recovery.
- Transparent reasoning: User-facing audit bundles and developer traces.
- Bounded personalization: Style/priority tuning; safety rails untouchable.
- Multimodal glue: Lukhas routes/stores; OpenAI interprets (text, audio, vision).

## 3) Fully leveraging OpenAI API (heavy lifting map)
- Chat/Assistants: Primary reasoning/planning/tool-use; Lukhas injects modulated params (temperature, top_p, max_tokens, penalties; reasoning effort when available).
- Moderations: Pre-check user inputs and feedback notes; post-check responses; escalate to strict mode and/or HITL.
- Embeddings: Index episodic/semantic/procedural memory; symbol/emoji/gesture vectors; guide retrieval.
- Files/Vector stores (Assistants): Per-user knowledge packs; hydrate prompts with minimal snippets.
- Audio (STT/TTS) and Vision: Offload speech/image understanding; Lukhas stores symbols and applies policy.
- Function calling/Tools: Define clean JSON schemas; OpenAI selects; Lukhas orchestrates/retries with guardrails.
- Batch: Nightly feedback summarization, bounded policy LUT proposals, re-embedding, analytics.
- Fine-tuning (when warranted): Style adapters or domain classifiers; keep safety outside fine-tune.
- Realtime/Streaming: Stream drafts; endocrine signals adjust decoding (e.g., lower temperature on risk).
- Routing: Smaller models for classify/extract; flagship models for synthesis/plan.

Recommended patterns
- Endocrine → parameters: stress↑ → lower temperature, cap tokens; novelty↑ & low risk → broaden search; alignment_risk↑ → strict mode + HITL.
- Dual-pass auditing: Draft with model A; audit with model B in “ethical auditor” role; Guardian has final veto.
- Retrieval discipline: Deterministic k, chunk summaries, cache by topic.
- Resilience: Exponential backoff, circuit breakers, failover models, content-addressed caching.

## 4) Hidden opportunities to amplify OpenAI
- Persistent symbol injection: Maintain per-user symbol glossary in system prompts (no fine-tune required).
- Feedback→policy compiler: Use models to summarize card notes into bounded policy deltas; Guardian approves.
- Ethical judge pass: Separate audit prompt before Guardian rules—catches subtle risks and value mismatches.
- Colony signal synthesis: Lightweight classifier model maps events → endocrine signals; large models stay on reasoning.

## 5) Roadmap (30/60/90 days)

### Milestone A (Day 0–30): Safety and Modulation Wiring
Deliverables
- Modulator → API client wiring: temperature, top_p, max_tokens, penalty controls; tool gating.
- Moderation pre/post on user input, feedback notes, model output; strict-mode escalation.
- Retrieval layer v1: embeddings for memory + symbol glossary; minimal context hydrator.
- Audit bundle v1: attach signals, moderation status, policy, memory refs to each response.
Acceptance
- All messages traverse moderation and Guardian; blocked cases return safe refusal templates.
- Param shifts reflect endocrine policy rules; logs show parameter deltas and reasons.
- Responses cite which memory snippets fed the prompt.

### Milestone B (Day 31–60): Feedback and Policy Learning (Bounded)
Deliverables
- Feedback Card pipeline: capture {target_action_id, rating 1–5, note}; store JSONL.
- Nightly batch: summarize notes with a small model; propose bounded LUT changes; Guardian approves and versions policies.
- Dual-pass auditing for “sensitive” actions (configurable): draft → audit → allow/refuse.
Acceptance
- Policy LUT diffs are bounded (style/priority only); safety rails immutable.
- Versioned policy file with change log; roll-back supported.
- Sensitive actions show both draft and audit rationale in the audit bundle.

### Milestone C (Day 61–90): Personal Symbols and Multimodal Glue
Deliverables
- On-device personal symbol/emoji/gesture mapping to compact intent vectors; encrypted at rest.
- System prompt injection of per-user symbol glossary (hidden) for persistent interpretation.
- Optional vision/audio routing via OpenAI endpoints; store symbolic summaries, not raw media.
Acceptance
- Symbols never leave device (only hashed aggregates if opted-in); privacy review signed.
- Prompts consistently interpret user symbols; test suite validates mapping accuracy.
- Multimodal inputs routed and summarized with audit trails.

## Backlog (targeted tasks)
- Identity namespace bridges; tiered permissions in Guardian checks.
- Tool schemas and idempotency keys for critical actions; retry/backoff policies.
- Cost/latency routing: small models for classification/extraction, flagship for synthesis.
- Streaming adjustments: endocrine hooks for mid-stream parameter updates.
- Developer telemetry: Prometheus counters for moderation hits, Guardian vetoes, retries, cache hit rate.

## Metrics & Quality Gates
- Safety: 100% of I/O moderated + Guardian-checked; 0 bypasses.
- Reliability: p95 response latency within target; retry success rate > 99%; zero unhandled exceptions.
- Learning hygiene: Policy deltas bounded and versioned; rollback tested; no safety regressions.
- Privacy: No personal symbols in server logs; encryption verified; DPIA documented.
- Interpretability: 100% of responses carry audit bundles; sampled bundles are coherent and complete.

## Risks & Mitigations
- Drift from safety via personalization → hard bounds, Guardian approval of LUT deltas, automated diff checks.
- Context bloat and cost → deterministic retrieval, summarization, aggressive caching.
- Model outages/limits → circuit breakers, failover models, backoff, queueing.
- Namespace/legacy code fragility → bridge modules, import tests, deprecation sweep.

## Appendix: Signal → Parameter mapping (conceptual)
- stress↑: temperature↓, top_p↓, max_tokens cap↓, safety mode strict, HITL threshold lower.
- novelty↑ (risk low): temperature↑ (bounded), top_p↑, allow exploratory tools, longer max_tokens.
- alignment_risk↑: temperature↓, top_p↓, force dual-pass auditing, tool whitelist narrow.

Notes
- Safety rails (Guardian, moderation) are never weakened by feedback or symbols.
- Personalization influences style/priority only, within documented limits.
