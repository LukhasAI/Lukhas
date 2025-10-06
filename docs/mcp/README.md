---
status: wip
type: documentation
---
# Lukhas MCP: Contract & Smo# write
curl -s $H/mcp -H 'Content-Type: application/json' \\
 -d '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"write_file","arguments":{"path":"docs/mcp/hello.md","contents":"# Hello\\n","overwrite":true}}}'
```

## Security & Persistence

**Auth (recommended in prod):**
- Set `LUKHAS_MCP_API_KEYS="key1,key2,..."` and send `X-API-Key: <key>` (or `Authorization: Bearer <key>`).
- SSE supports `?key=<key>` as well as the header.

**Rate Limits:**
- Token bucket per IP. Defaults: `MCP_RL_WINDOW_MS=10000`, `MCP_RL_BUCKET=60`.

**Persistence:**
- Jobs/Models are saved to `${LUKHAS_REPO_ROOT}/.mcp-state.json` (override via `MCP_STATE_PATH`).
- Autosaves every 3 seconds if dirty; loaded on startup.

**SQLite Persistence (Production):**
- Set `LUKHAS_MCP_DB="$PWD/.mcp-state.db"` for ACID transactions.
- ACID with WAL enabled by default.
- Tables: `jobs`, `models`, `model_gates`, `audits`.
- Jobs GC: `MCP_JOB_TTL_MS` (default 7d), hourly sweep.
- Wire contract unchanged (JSON-RPC 2.0). Existing ChatGPT connectors keep working.

**Adapters:**
- `adapters/evalOrchestrator.js` → swap to your real eval backend; keep `run({taskId,configId,dryRun})`, `poll(jobId)`.
- `adapters/modelRegistry.js` → swap to your model registry; keep `promote({modelId,gate,dryRun})`.
- These adapters are intentionally thin so backend wiring doesn't ripple through the server.

**Health:**
- `HEAD /healthz` returns `200` quickly when the server is responsive.

## Example with Auth

```bash
export LUKHAS_REPO_ROOT="$PWD"
export LUKHAS_MCP_API_KEYS="dev-key-1"
node mcp-servers/lukhas-devtools-mcp/mcp-streamable.mjs &

H=http://localhost:8766
curl -s $H/mcp -H 'X-API-Key: dev-key-1' -H 'Content-Type: application/json' \\
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"dev","version":"1.0"},"capabilities":{"tools":{}}}}' | jq .
```

### Readiness & Rate-Limits
- **Readiness:** `HEAD /readyz` returns 200 when the server is ready to serve traffic.
- **Per-key quotas:** send `X-API-Key: …` (or `Authorization: Bearer …`). Limits apply per key (fallback: per IP).

### Key Rotation
Set multiple keys in `LUKHAS_MCP_API_KEYS="k1,k2,..."`. Rotate by:
1) add `k_new` → deploy
2) update clients to `k_new`
3) remove `k_old` → deploy
This document locks the wire contract for ChatGPT (MCP) and internal tools.

## Golden Curls (minimal contract)

```bash
H=${H:-http://localhost:8766}

# initialize
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"dev","version":"1.0"},"capabilities":{"tools":{}}}}' | jq '.result.serverInfo.name'

# tools include search + fetch (required for "searchable")
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | jq '.result.tools | map(.name) | index("search")'
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":3,"method":"tools/list","params":{}}' | jq '.result.tools | map(.name) | index("fetch")'

# fetch requires id
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":4,"method":"tools/list","params":{}}' | jq '.result.tools[] | select(.name=="fetch") | .inputSchema.required | index("id")'
```

## Full Smoke (authoring loop)

```bash
H=${H:-http://localhost:8766}
# write
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"write_file","arguments":{"path":"docs/mcp/hello.md","contents":"# Hello\n","overwrite":true}}}'

# fetch by repo path id
ID="lukhas-path:ZG9jcy9tY3AvaGVsbG8ubWQ="
SHA=$(curl -s $H/mcp -H 'Content-Type: application/json' \
 -d "{\"jsonrpc\":\"2.0\",\"id\":11,\"method\":\"tools/call\",\"params\":{\"name\":\"fetch\",\"arguments\":{\"id\":\"$ID\",\"fields\":[\"metadata\"]}}}" \
 | jq -r '.result.content[0].text' | jq -r '.metadata.sha256')

# patch (unified diff)
DIFF=$'--- a\n+++ b\n@@ -1,1 +1,2 @@\n-# Hello\n+# Hello\nPatched\n'
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d "{\"jsonrpc\":\"2.0\",\"id\":12,\"method\":\"tools/call\",\"params\":{\"name\":\"apply_patch\",\"arguments\":{\"path\":\"docs/mcp/hello.md\",\"patch\":$(jq -sR . <<<\"$DIFF\"),\"expectSha256\":\"$SHA\"}}}"

# commit
curl -s $H/mcp -H 'Content-Type: application/json' \
 -d '{"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"git_commit","arguments":{"message":"docs: patch hello","add":["docs/mcp/hello.md"]}}}'
```

## Eval Runner Stubs

* `run_eval({taskId, configId, dryRun?}) → { jobId, status }`
* `status({jobId}) → { status, updatedAt, result? }`
* `promote_model({modelId, gate, dryRun?}) → { currentGates, promoted }`

These are in-memory and safe; they lock the I/O shape so backend wiring can happen later.

## Real-time SSE Topics

Open a stream:
```bash
# Auth via header or ?key=...
curl -N "http://localhost:8766/sse?topic=job/<jobId>" -H 'X-API-Key: dev-key-1'
curl -N "http://localhost:8766/sse?topic=canary/<canaryId>" -H 'X-API-Key: dev-key-1'
```

Events: `queued|running|completed|update` for jobs; `started|metric|promoted|rolled_back` for canaries. Payloads are JSON.

## Canary Promotions (SLO-guarded)

Start:

```bash
curl -s $H/mcp -H 'X-API-Key: dev-key-1' -H 'Content-Type: application/json' -d '{
  "jsonrpc":"2.0","id":1,"method":"tools/call",
  "params":{"name":"start_canary","arguments":{
    "modelId":"matriz-v1","fromGate":"stage","toGate":"production",
    "windowSeconds":120,"targets":{"latency_p95_ms":250,"max_error_rate":0.02}
  }}
}'
```

Watch:

```bash
curl -N "$H/sse?topic=canary/<CANARY_ID>" -H 'X-API-Key: dev-key-1'
```

Status / abort:

```bash
curl -s $H/mcp -H 'X-API-Key: dev-key-1' -H 'Content-Type: application/json' -d '{
  "jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"canary_status","arguments":{"canaryId":"<CANARY_ID>"}}}'
curl -s $H/mcp -H 'X-API-Key: dev-key-1' -H 'Content-Type: application/json' -d '{
  "jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"abort_canary","arguments":{"canaryId":"<CANARY_ID>"}}}'
```