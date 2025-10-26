# Registry API Usage Examples

This guide shows how to interact with the Registry API. Replace localhost:8080 if your server runs elsewhere.

## Register a node

```bash
curl -X POST http://localhost:8080/api/v1/registry/register \
  -H "Content-Type: application/json" \
  -d @docs/schemas/examples/memory_adapter.json
```

## Validate a NodeSpec

```bash
curl -X POST http://localhost:8080/api/v1/registry/validate \
  -H "Content-Type: application/json" \
  -d '{"node_spec": {}}'
```

Replace the empty object with your NodeSpec content.

## Query by signal

```bash
curl "http://localhost:8080/api/v1/registry/query?signal=memory_stored"
```

## Query by capability

```bash
curl "http://localhost:8080/api/v1/registry/query?capability=memory/episodic"
```

## Deregister a node

```bash
curl -X DELETE http://localhost:8080/api/v1/registry/<registry_id>
```

Notes:
- Ensure the server is running and the Registry API is enabled.
- For protected endpoints, include your auth headers as required by your environment.
