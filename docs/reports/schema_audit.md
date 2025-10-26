# Schema Audit — NodeSpec v1
**Author:** Agent B (GPT-5 Pro emulation)
**Date:** 2025-10-24 (Europe/London)
**Artifacts audited:** `docs/schemas/nodespec_schema.json`, examples `docs/schemas/examples/*.json`

---

## Executive summary — bottom line (T4)
NodeSpec v1 is *mostly complete* and covers the essentials (node_type, metadata, identity, interfaces, contracts, provenance, security, extraplanetary_policy). Two categorical gaps must be fixed before production: (A) **attestation & provenance fields** need stricter typing and freshness proofs; (B) **governance_policy_ref** and **capability policy semantics** must be formalized (policy ref schema / OPA module name / required min governance scores). Also: add machine-readable **owner_id / GLYMPH** format and schema_version pattern; add `compatibility.min_version/max_version` and `migration_guidance` fields.

---

## Top 7 findings (actionable)

### 1) **owner_id (GLYMPH) format missing**
**Issue:** schema has `owner_id: string` only. We need machine-parsable format & length + signature hint.
**Recommendation:** `owner_id` should match regex `^GLYMPH:[0-9a-f]{16,64}(:sig:[A-Za-z0-9+/=]+)?$` (base64 signature optional). Add `"pattern"` and document semantics (hash+sig).
**Test:** jsonschema: expect failure when owner_id is `foo` and success for `GLYMPH:abcd1234...:sig:BASE64`.

### 2) **attestation block absent / underspecified**
**Issue:** `security.attestation` exists but lacks `report_type`, `verifier`, `timestamp`, and `freshness_proof`.
**Recommendation:** require `attestation: {report, verifier, nonce, timestamp, proof_type, verified_boolean}`. Mandate `timestamp` ISO8601 and `nonce` / freshness field.
**Test:** CI must fail NodeSpec register if `attestation` missing for `tier >= 4` or `lane == core`.

### 3) **governance_policy_ref not required**
**Issue:** There is no required field `governance_policy_ref`. Without explicit link to an OPA policy or policy id, runtime cannot enforce constraints.
**Recommendation:** add optional `governance_policy_ref` (string) and, for `sensitive` signals, make it required with `policy_min_scores` structure.
**Test:** NodeSpec with `signals.emits` containing names in a configured sensitive set must include `governance_policy_ref`.

### 4) **extraplanetary_policy underspecified**
**Issue:** `extraplanetary_policy` is freeform. Need structured subfields: `mode (DTN|SYNC|PASSIVE)`, `checkpoint_interval_seconds`, `max_payload_bytes`, `compression (semantic|binary)`.
**Recommendation:** add explicit schema and explain DTN modes.
**Test:** CI validates presence of `checkpoint_interval_seconds` for `mode: DTN`.

### 5) **schema_version pattern / compatibility**
**Issue:** `schema_version` exists but lacks pattern and `compatibility` rule.
**Recommendation:** enforce `schema_version` pattern `^nodespec\\.v\\d+$` and add `compatibility: {min_version, max_version, migration_hint}`.
**Test:** jsonschema verifies `schema_version: nodespec.v1` and `compatibility` acceptable.

### 6) **signals block: missing canonical names & sensitivity**
**Issue:** `signals.emits[*]` has `name` and `latency_target_ms` but no `sensitivity` (e.g., `sensitivity: public|internal|personal`) or `governance_category`.
**Recommendation:** add `sensitivity` and optional `governance_category` tags for policy mapping.
**Test:** Any signal tagged `personal` requires `governance_policy_ref`.

### 7) **runtime SLOs & measurement hooks**
**Issue:** performance_hints exist but no `measurement_endpoint` or `metric_names` to tie into OTEL.
**Recommendation:** add `observability.metrics` mapping (e.g., `metrics: {latency_metric: "node.latency", drift_metric: "node.drift"}`) to bind NodeSpec to monitor.
**Test:** ensure NodeSpec includes `observability.metrics` before promotion.

---

## Minimal schema patches (copy/paste)

1. **owner_id pattern** (jsonschema snippet):

```json
"owner_id": {
  "type": "string",
  "pattern": "^GLYMPH:[0-9a-f]{16,64}(:sig:[A-Za-z0-9+/=]+)?$",
  "description":"GLYMPH identifier; optional :sig:BASE64"
}
```

2. **attestation block**:

```json
"attestation": {
  "type":"object",
  "required":["report","verifier","timestamp","nonce","verified"],
  "properties":{
    "report":{"type":"string"},
    "verifier":{"type":"string"},
    "timestamp":{"type":"string", "format":"date-time"},
    "nonce":{"type":"string"},
    "verified":{"type":"boolean"},
    "proof_type":{"type":"string", "enum":["sgx","tpm","eatt","remote"]},
    "notes":{"type":"string"}
  }
}
```

3. **governance_policy_ref**:

```json
"governance_policy_ref": {"type":"string","description":"OPA/rego policy id or URL"}
```

4. **extraplanetary_policy** (skeleton):

```json
"extraplanetary_policy": {
  "type":"object",
  "properties":{
    "mode":{"type":"string","enum":["DTN","SYNC","PASSIVE"]},
    "checkpoint_interval_seconds":{"type":"integer"},
    "max_payload_bytes":{"type":"integer"},
    "compression":{"type":"string","enum":["semantic","binary","none"]}
  }
}
```

---

## Assumptions & risk

* Assumes NodeSpec is used both at CI registration time and at runtime for policy enforcement.
* Risk: tightening schema can break older modules; mitigate with `compatibility` field and migration guidance.

---

## Recommended next steps (short)

1. Apply the minimal schema patches above in `docs/schemas/nodespec_schema.json`.
2. Add CI rule: schema must pass and examples must validate (already present).
3. Add OPA stub (`governance_policy_ref` mapping) and create a policy for `sensitivity=personal`.
4. Add NodeSpec → OTEL mapping to `observability` block.

---

## HANDOFF B→C

**HANDOFF B→C:** (Agent B → GitHub Copilot)

Implement negative tests and usage docs:
1. `services/registry/tests/test_registry_negative.py` (invalid NodeSpec, missing GLYMPH, bad signature)
2. `docs/usage/registry_examples.md` with curl commands (register, query, validate, deregister)
3. Expand README to include how to run PQC check locally (pip install python-oqs or local liboqs build)

Expected outputs:
- New test file(s) under `services/registry/tests/`
- `docs/usage/registry_examples.md`
- Updated `services/registry/README.md` with PQC local dev notes
