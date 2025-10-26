HANDOFF B→C: Agent B completed schema audit and PQC CI artefact creation.

Deliverables added for Agent C:
- reports/schema_audit.md (schema gaps & recommended patches)
- NOTE: please apply the owner_id/attestation/extraplanetary schema patches in NodeSpec and add compliance tests.

Agent C tasks (per HANDOFF):
- Implement negative tests (test_registry_negative.py already added).
- Create usage guide docs (docs/usage/registry_examples.md present).
- Expand README with PQC local dev notes (done).

Next (Agent D): add Makefile registry‐smoke target and wire CI job; use .github/workflows/registry-smoke.yml as template.

Local verification commands:
- python -c "import json,jsonschema; jsonschema.validate(json.load(open('docs/schemas/examples/memory_adapter.json')), json.load(open('docs/schemas/nodespec_schema.json')))"
- pytest services/registry/tests -q

HANDOFF B→C complete.
