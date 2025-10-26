HANDOFF B→C: No-Op guard verification

Deliverables:
- scripts/batch_next.sh contains detect_and_handle_noop()
- tests: integration test test_noop_guard_integration.py added

Agent C tasks:
- Ensure integration test covers chmod-only and audit log behavior.
- Add README snippet on guard semantics.

Agent D tasks:
- Ensure `registry-smoke` target and `registry-smoke.yml` do not falsely interact with batch runner.
- Wire a small CI job to run `pytest services/registry/tests/test_noop_guard_integration.py`.

Local check:
- pytest services/registry/tests/test_noop_guard_integration.py -q

HANDOFF B→C complete.
