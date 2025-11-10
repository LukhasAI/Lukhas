# LUKHΛS Test Surgeon — MATRIZ module (complex logic)

**File:** `matriz/adapters/llm_adapter.py`
**Goal:** ≥70% coverage with **metamorphic** checks when possible.

Focus:
- Pipeline invariants (same input class → consistent phase transitions)
- Round-trips / idempotence for symbolic structures
- Error handling for degenerate inputs

Constraints:
- No network; freeze time; pin seeds
- Mock LLM/vector store calls
