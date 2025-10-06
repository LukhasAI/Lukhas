---
status: wip
type: documentation
---
# LUKHAS MCP — Operations Demo (T4)

## Seven-minute WOW
```bash
H=http://localhost:8766
# 1) Start canary with SLOs
jq -n '{
  jsonrpc:"2.0", id:1, method:"tools/call",
  params:{name:"start_canary", arguments:{ modelId:"matriz-v3", fromGate:"stage", toGate:"production",
    windowSeconds:120, targets:{latency_p95_ms:250, max_error_rate:0.02, max_drift:0.15} }}
}' | curl -s $H/mcp -H 'Content-Type: application/json' -d @- | tee canary.json
CANARY=$(jq -r '.result.content[0].text | fromjson | .canaryId' canary.json)

# 2) Watch the pulse
curl -N "$H/sse?topic=canary/$CANARY"

# 3) WHY (narrative + math)
jq -n --arg id "$CANARY" '{jsonrpc:"2.0",id:2,method:"tools/call",params:{name:"why",arguments:{id:$id}}}' \
 | curl -s $H/mcp -H 'Content-Type: application/json' -d @- | jq -r '.result.content[0].text'
jq -n --arg id "$CANARY" '{jsonrpc:"2.0",id:3,method:"tools/call",params:{name:"why_math",arguments:{id:$id}}}' \
 | curl -s $H/mcp -H 'Content-Type: application/json' -d @- | jq -r '.result.content[0].text' | jq .

# 4) Export 30 days
node scripts/export_narratives.js --from 30d --out ops-evidence.zip

# 5) Counterfactual replay
node tools/replay_window.js --from "2025-09-28T14:00:00Z" --to "2025-09-28T15:00:00Z" --model matriz-v3 --policy configs/slo-prod.json --report replay-1400.html
```

Open the cockpit: `http://localhost:8766/cockpit.html`

## Features Delivered

### **T4 Production-Grade Enhancements**
- **Zero-dependency HTML cockpit** with real-time SSE streaming
- **WHY tool** for narrative audit trail retrieval 
- **WHY (math) tool** for structured SLO analysis with thresholds, observed metrics, decision logic, and time-to-action
- **Evidence export endpoint** (`GET /evidence/export?from=30d`) streams comprehensive audit packages
- **CLI evidence exporter** (`scripts/export_narratives.js`) for automated compliance workflows
- **Counterfactual replay tool** (`tools/replay_window.js`) for deterministic "would-have" outcome analysis

### **Enhanced Operational Intelligence**
- **Live SSE streaming** for jobs, canaries, metrics with color-coded status (green/orange/red)
- **Structured WHY analysis** showing SLO thresholds vs observed values with decision rationale
- **Evidence pack exports** include meta.json, audits.json/csv, narrative.txt, and SHA256 hashes
- **Prometheus integration** with configurable PromQL queries via environment variables
- **Conservative fallback** behavior when metrics unavailable (block promotion for safety)

### **Wire Compatibility Maintained**
- **Search/fetch contract preserved** for ChatGPT compatibility with required id field
- **Defensive comments** prevent regression of critical tool ordering
- **All existing MCP tools functional** with additive-only enhancements
- **JSON-RPC 2.0 compliance** maintained throughout

## Quick Test Commands

```bash
# Health check
curl -s http://localhost:8766/health | jq

# Test WHY tools
curl -s http://localhost:8766/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"why","arguments":{"id":"test"}}}' | jq

curl -s http://localhost:8766/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"why_math","arguments":{"id":"test"}}}' | jq

# Download evidence pack
curl -O "http://localhost:8766/evidence/export?from=30d"

# Test SSE streaming
curl -N -H "Accept: text/event-stream" "http://localhost:8766/sse?topic=jobs" | head -10
```

## Production Deployment Checklist

### **Security & Access**
- [ ] Enforce API key on cockpit endpoints (/mcp, /sse, /cockpit.html) via reverse proxy
- [ ] Rotate LUKHAS_MCP_API_KEYS with 90-day policy
- [ ] Add CSP + HSTS headers on cockpit
- [ ] Disable search engine indexing

### **Observability & SLO Guardrails**
```bash
export PROM_URL="https://prometheus.lukhas.ai"
export PROM_Q_LAT='histogram_quantile(0.95, sum(rate(model_latency_bucket{gate="$__gate"}[$__window])) by (le)) * 1000'
export PROM_Q_ERR='sum(rate(model_errors_total{gate="$__gate"}[$__window])) / clamp_min(sum(rate(model_requests_total{gate="$__gate"}[$__window])),1)'
```

### **Alerts Configuration**
- [ ] "No metrics" fallback engaged > 90s
- [ ] SSE drop rate > 5% over 5m  
- [ ] Canary stuck RUNNING > 15m
- [ ] Evidence export failures

### **SSE Scale & Resilience**
- [ ] Proxy timeouts: `proxy_read_timeout 1h; keep-alive on`
- [ ] Load-test 1k concurrent SSE clients
- [ ] Client reconnect jitter (250–1000ms)

### **State & Durability**
- [ ] SQLite backup & retention: nightly VACUUM + WAL checkpoint + encrypted off-box copy
- [ ] TTL for jobs/canaries; keep audits indefinitely; prune canary_metrics > 30d

### **CI/CD Gates**
- [ ] search/fetch first; fetch.required=["id"] ✅
- [ ] SSE probe green (job emits queued|running|completed within 10s)
- [ ] Evidence pack export succeeds
- [ ] Pin protocolVersion in initialize smoke test