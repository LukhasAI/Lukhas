Title: Integrate AsyncCognitiveOrchestrator and enable streaming-ready pathway

Objective
- Replace synchronous routing with `AsyncCognitiveOrchestrator` where appropriate, preserving lane boundaries and current API behavior. Prepare a clean seam for future SSE streaming without changing public contracts.

Context
- Lane rules: LUKHAS may import `core/`, `matriz/`, not `candidate/`.
- The async orchestrator lives at `matriz/core/async_orchestrator.py:277` and is re-exported via shim `matriz/orchestration/async_orchestrator.py:1`.
- Current public app: `serve/main.py:1` includes OpenAI façade endpoints (`/v1/models`, `/v1/embeddings`, `/v1/responses`). Keep their current interface stable.

Deliverables
- A new internal service module (no public API change) that:
  - Instantiates `AsyncCognitiveOrchestrator` once
  - Provides an async function `run_async_matriz(query: str) -> dict` invoking the pipeline
  - Adapts user input to node-specific schemas (math: `{"expression": ...}`, facts: `{"question": ...}`) before `node.process`
  - Gracefully handles timeouts and returns orchestrator metrics
- Wire this module so `serve/main.py` can optionally call it (guarded by env flag `LUKHAS_ASYNC_ORCH=1`) while defaulting to current stub behavior.
- Unit tests for the adapter logic (mapping query->node input) and a basic async processing smoke using the math/facts nodes.

Constraints
- No public schema changes at `/v1/*`.
- Respect lane boundaries. Do not import `candidate/*`.
- Avoid heavy refactors; keep changes surgical and additive.

Suggested Steps
1) Read orchestrator and nodes
   - `matriz/core/async_orchestrator.py:277`
   - `matriz/nodes/math_node.py:1`, `matriz/nodes/fact_node.py:1`, `matriz/nodes/validator_node.py:1`
2) Add module `matriz/orchestration/service_async.py` exposing:
   - `get_async_orchestrator()` singleton initializer
   - `async run_async_matriz(user_input: str) -> dict`
   - internal adapter to map user_input -> node-specific input
3) Update `serve/main.py:1` to conditionally import and use `run_async_matriz` when `LUKHAS_ASYNC_ORCH=1`, else current path.
4) Tests
   - Add `tests/unit/test_async_orchestrator_adapter.py` covering adapter mapping and a simple async end-to-end call (math and facts).

Verification
- `make codex-bootcheck`
- `pytest -q tests/unit/test_async_orchestrator_adapter.py`
- Optional manual: start app and POST `/v1/responses` with `LUKHAS_ASYNC_ORCH=1` to ensure no contract change.

Acceptance Criteria
- Builds and tests pass.
- No change to `/v1/*` response envelopes.
- Env-toggle works: with `LUKHAS_ASYNC_ORCH=1`, responses are produced by async orchestrator; without, existing behavior remains.

Commit (T4)
feat(matriz): add async orchestrator service seam with env toggle

