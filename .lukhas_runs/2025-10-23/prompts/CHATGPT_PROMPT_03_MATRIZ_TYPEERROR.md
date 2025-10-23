Title: Eliminate MATRIZ node TypeErrors and align orchestrator input contracts

Objective
- Systematically find and fix any TypeError/mismatch between orchestrator pipeline calls and node `process()` input schemas. Add adapter logic plus tests to lock the contract.

Context
- Nodes expect typed inputs:
  - MathNode: `{"expression": str}` (matriz/nodes/math_node.py:1)
  - FactNode: `{"question": str}` (matriz/nodes/fact_node.py:1)
  - ValidatorNode: `{"target_output": dict, ...}` (matriz/nodes/validator_node.py:1)
- Async orchestrator currently calls `node.process({"query": user_input})`, which can lead to incorrect handling even if not always a TypeError.

Deliverables
- A small adapter inside orchestration that maps raw `user_input: str` → node-specific dict before `node.process`.
- Defensive checks in orchestrator to avoid passing wrong shapes.
- Tests that would fail pre-fix and pass post-fix:
  - math: string like `"(2+3)*4"` produces numeric result
  - facts: `"What is the capital of France?"` returns known answer with confidence
  - validator: accepts a math output and returns True

Constraints
- No changes to public HTTP schemas.
- Keep orchestrator performance budget in mind; adapter must be O(len(user_input)).
- Avoid lane boundary violations.

Suggested Steps
1) Add `_adapt_input_for_node(node_name: str, user_input: str) -> dict` to `matriz/core/async_orchestrator.py:277` or a sibling helper imported there.
   - If node == "math": return `{ "expression": user_input }`
   - If node == "facts": return `{ "question": user_input }`
   - Else: return `{ "query": user_input }`
2) Use this adapter before `_process_node_async(...)` so the executor receives node-appropriate input.
3) Tests in `tests/unit/test_matriz_input_adapter.py` for adapter + minimal pipeline passes.

Search & Probe
- `rg -n "TypeError|process\(self, input_data" matriz`
- Confirm no remaining `from MATRIZ...` import casing issues.

Verification
- `make codex-bootcheck`
- `pytest -q tests/unit/test_matriz_input_adapter.py`

Acceptance Criteria
- No TypeError triggered by contract mismatch in adapter tests.
- Math and Facts happy paths green; validator receives correct structure.

Commit (T4)
fix(matriz): align orchestrator→node input schema with adapter and tests

