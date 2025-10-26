HANDOFF B→C: Registry CI & tests status

Deliverables:
- services/registry/tests/test_registry_negative.py (negative tests)
- registry_examples.md (curl examples)
- README.md updated (PQC local testing & CI notes)
- pqc-sign-verify.yml (PQC CI)

Agent C tasks:
- Refine negative tests for signature tampering (placeholder uses HMAC).
- Add usage doc examples for deregister & capability query.
- Confirm README PQC notes.

Agent D tasks:
- Add Makefile targets: registry-smoke & registry-ci.
- Wire .github/workflows/registry-smoke.yml into PR checks.

Verification:
- Run `make registry-up` locally, then `make registry-smoke` or `./scripts/ci_verify_registry.sh`.
- Run `pytest services/registry/tests -q`.

HANDOFF B→C complete.
