---
status: wip
type: documentation
---
# Tasks: OpenAI Alignment Roadmap (Milestones A–C)

Track implementation tasks for ROADMAP_OPENAI_ALIGNMENT.md. Check off items as they ship.

## Milestone A (Day 0–30): Safety and Modulation Wiring
- [ ] Wire Modulator → API client (temperature, top_p, max_tokens, penalties)
- [ ] Implement tool gating based on policy and alignment_risk
- [ ] Add Moderation pre-checks (user input, feedback notes)
- [ ] Add Moderation post-checks (model output)
- [ ] Strict-mode escalation path and refusal templates
- [ ] Retrieval v1: embeddings index for memory + symbol glossary
- [ ] Minimal context hydrator (deterministic k, chunking)
- [ ] Audit bundle v1 attached to every response

## Milestone B (Day 31–60): Feedback and Policy Learning (Bounded)
- [ ] Feedback capture (JSONL): {target_action_id, rating 1–5, note}
- [ ] Nightly batch: summarize notes (small model)
- [ ] Propose bounded policy LUT changes
- [ ] Guardian approval workflow + versioned LUT file
- [ ] Dual-pass auditing for sensitive actions
- [ ] Rollback mechanism and change log

## Milestone C (Day 61–90): Personal Symbols and Multimodal Glue
- [ ] On-device personal symbol/emoji/gesture mapping (encrypted)
- [ ] Hidden system prompt injection of per-user symbol glossary
- [ ] Vision/Audio routing via OpenAI endpoints (optional)
- [ ] Symbolic summaries stored, not raw media
- [ ] Privacy review and DPIA notes committed

## Backlog
- [ ] Identity namespace bridges + tiered permissions in Guardian
- [ ] Tool idempotency keys + retry/backoff policies
- [ ] Cost/latency routing policies (small vs flagship models)
- [ ] Streaming endocrine adjustments (mid-stream param updates)
- [ ] Prometheus metrics: moderation hits, Guardian vetoes, retries, cache hit rate
