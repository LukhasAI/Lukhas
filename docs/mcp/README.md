# Lukhas MCP: Contract & Smoke

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