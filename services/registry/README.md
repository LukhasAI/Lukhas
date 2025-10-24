# Hybrid Registry Prototype

**Status**: Prototype (TG-002) | **Schema**: NodeSpec v1

## Overview

Minimal FastAPI service that validates NodeSpec v1 and manages a hybrid static/dynamic registry with signed checkpoints.

## Features

- **POST /api/v1/registry/register** - Register node (requires GLYMPH provenance)
- **POST /api/v1/registry/validate** - Validate NodeSpec without registration
- **GET /api/v1/registry/query** - Query by signal or capability
- **DELETE /api/v1/registry/{id}** - Deregister node
- **Checkpoints** - HMAC-signed state snapshots (TODO: migrate to Dilithium2)

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r services/registry/requirements.txt
uvicorn services.registry.main:app --reload --port 8080
```

Or via Makefile:

```bash
make registry-up
```

## Test

```bash
pytest services/registry/tests -q
```

Or via Makefile:

```bash
make registry-test
```

## Example Usage

```bash
# Validate a NodeSpec
curl -X POST http://localhost:8080/api/v1/registry/validate \
  -H "Content-Type: application/json" \
  -d @docs/schemas/examples/memory_adapter.json

# Register a node
curl -X POST http://localhost:8080/api/v1/registry/register \
  -H "Content-Type: application/json" \
  -d '{"node_spec": <nodespec>, "mode": "dynamic"}'

# Query by signal
curl http://localhost:8080/api/v1/registry/query?signal=memory_stored

# Query by capability
curl http://localhost:8080/api/v1/registry/query?capability=memory/episodic
```

## Architecture

### Validation

Uses `jsonschema` to validate NodeSpec v1 against [docs/schemas/nodespec_schema.json](../../docs/schemas/nodespec_schema.json).

### Provenance

Registration requires `provenance_manifest.glymph_enabled = true`. Nodes without GLYMPH provenance are rejected with HTTP 403.

### Checkpoints

Registry state is periodically saved to `services/registry/registry_store.json` with HMAC signature in `checkpoint.sig`.

**TODO**: Replace HMAC with Dilithium2 post-quantum signatures.

### Query Filters

- **signal**: Match nodes that emit or subscribe to a signal
- **capability**: Match nodes with capability in their allow list

## Notes

- Checkpoints are HMAC-signed (prototype). Replace with Dilithium2 in production.
- Validates NodeSpec v1 from `docs/schemas/nodespec_schema.json`.
- In-memory store; restart clears registry (checkpoint persistence TODO).

## Security Considerations

- **HMAC Key**: Set `REGISTRY_HMAC_KEY` environment variable (defaults to test key)
- **PQC Migration**: Follow-up ticket (MATRIZ-007) for Dilithium2 signing
- **Rate Limiting**: Not implemented (add in production)
- **Authentication**: Not implemented (add in production)

## Related

- **TG-001**: NodeSpec v1 schema definition
- **MATRIZ-002**: Production Hybrid Registry MVP
- **MATRIZ-007**: GLYMPH attestation chain verifier
