---
status: proposed
type: documentation
owner: codex
module: adapters.redirect
redirect: false
moved_to: null
---

![Status: Proposed](https://img.shields.io/badge/status-proposed-blue)

# ADR-0003: DAST Adapter Messaging Interface
Date: 2025-11-09
Status: Proposed

## Context
The DAST orchestrator (`dast.or.py`) emits and consumes loosely structured task
messages when collaborating with MATRIZ services. Divergent payload shapes make
it difficult to unit test integrations and to reason about how metadata is
propagated through orchestration hops.

## Decision
Introduce a lightweight adapter module (`lukhas.adapters.dast_adapter`) that
centralizes the normalization rules for requests and responses exchanged with
the orchestrator. The adapter:

- Defines typed envelopes for outgoing and incoming messages (`TaskEnvelope`,
  `TaskResponse`).
- Applies default metadata and merges caller-provided overrides before dispatch.
- Validates orchestrator responses to guarantee the presence of `task_id` and
  `status` keys while preserving structured payloads.

## Consequences
**Positive effects**
- Cleaner tests: unit and integration tests can mock the protocol instead of
  crafting ad-hoc message dictionaries.
- Fewer edge cases: consumers rely on a single normalization path, preventing
  missing identifiers or malformed metadata blocks.
- Type-safety: downstream tooling gains explicit structures for IDEs and static
  analysis.

**Negative effects**
- Slight indirection for callers that previously interacted with the
  orchestrator directly.

## Alternatives Considered
- Continue inlining message normalization across call sites – rejected because
  drifted conventions have already produced subtle bugs.
- Introduce a full client SDK – rejected as overkill for the immediate wiring
  tasks and would require broader stewardship.

## Rollout Plan
1. Ship adapter and tests.
2. Incrementally migrate MATRIZ and orchestrator call sites to use the adapter.
3. Monitor metrics for task dispatch failures; expand adapter as new fields are
   standardized.

## Rollback Plan
- Revert the adapter module and restore previous direct orchestrator calls.
- Tests introduced alongside the adapter can be removed if the interface is
  rolled back.
