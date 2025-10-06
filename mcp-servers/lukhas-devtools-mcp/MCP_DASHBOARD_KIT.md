---
status: wip
type: documentation
---
# 🎯 MCP Dashboard Kit

**Real-time SSE streaming + SLO-guarded canary cockpit for production operations**

## 🚀 Quick Start

### 1. Launch Enhanced MCP Server

```bash
# Basic (stub SLO monitor)
LUKHAS_REPO_ROOT=/path/to/lukhas \
LUKHAS_MCP_API_KEYS="your-api-key" \
node mcp-streamable.mjs

# Production (Prometheus SLO monitor)
PROM_URL="https://prometheus.lukhas.ai" \
PROM_BEARER="your-token" \
LUKHAS_REPO_ROOT=/path/to/lukhas \
LUKHAS_MCP_API_KEYS="your-api-key" \
node mcp-streamable.mjs
```

### 2. Open SSE Probe Dashboard

```bash
# Open the zero-dependency dashboard
open docs/mcp/sse_probe.html

# Or serve via HTTP
python -m http.server 3000 -d docs/mcp/
# Navigate to http://localhost:3000/sse_probe.html
```

### 3. Test Real-Time Streaming

```bash
# Create a job and watch events
JOB=$(curl -s localhost:8766/mcp -H 'X-API-Key: your-key' \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"run_eval","arguments":{"taskId":"demo","configId":"default"}}}' \
  | jq -r '.result.content[0].text' | jq -r '.jobId')

# Stream job events
curl -N "localhost:8766/sse?topic=job/$JOB" -H "X-API-Key: your-key"
```

## 📊 Dashboard Components

### SSE Probe (`docs/mcp/sse_probe.html`)
- **Zero dependencies** - pure HTML/CSS/JS
- **Real-time events** - connects to any topic (job/*, canary/*)
- **Color-coded logs** - green (success), orange (progress), red (errors)
- **API key support** - paste your key for authenticated streams

### Cockpit Client (`dashboard/sseClient.js`)
- **Structured + Narrative events** - machine data + human stories
- **Topic subscriptions** - `job/<id>`, `canary/<id>`, or `*` (all)
- **Event forwarding** - perfect for Matriz UI integration
- **Auto-reconnect** - handles network drops gracefully

### Example Integration

```javascript
// Initialize cockpit
const cockpit = new LukhasMCPCockpit('http://localhost:8766', 'your-api-key');

// Listen to narrative events for human display
cockpit.on('completed', (event) => {
  console.log(event.narrative);
  // "[2025-10-03 14:21] job_9hd → completed successfully (23s)"
});

// Listen to structured events for metrics
cockpit.on('metric', (event) => {
  updateLatencyChart(event.data.latency_p95_ms);
  updateErrorChart(event.data.error_rate);
});

// Subscribe to all canary events
cockpit.subscribe('canary/*');
```

## 🔧 Prometheus Integration

### Environment Variables

```bash
# Prometheus connection
export PROM_URL="https://prometheus.lukhas.ai"
export PROM_BEARER="Bearer your-token"  # optional

# Custom PromQL queries (optional)
export PROM_QUERY_LAT='histogram_quantile(0.95, sum(rate(model_latency_bucket{gate="$__gate"}[$__window])) by (le))'
export PROM_QUERY_ERR='sum(rate(model_errors_total{gate="$__gate"}[$__window])) / clamp_min(sum(rate(model_requests_total{gate="$__gate"}[$__window])),1)'
```

### Required Metrics

Your Prometheus should expose:

```promql
# Latency histogram (for p95 calculation)
model_latency_bucket{gate="stage",le="100"} 42
model_latency_bucket{gate="stage",le="500"} 98
model_latency_bucket{gate="stage",le="+Inf"} 100

# Error and request counters (for error rate)
model_errors_total{gate="stage"} 3
model_requests_total{gate="stage"} 100
```

## 📋 CI/CD Integration

### Scheduled Health Checks

Add to `.github/workflows/mcp-smoke.yml`:

```yaml
on:
  schedule:
    - cron: "*/30 * * * *"   # every 30 minutes
  workflow_dispatch:

jobs:
  mcp-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start MCP Server
        run: |
          LUKHAS_REPO_ROOT=$PWD \
          LUKHAS_MCP_API_KEYS="ci-test-key" \
          node mcp-servers/lukhas-devtools-mcp/mcp-streamable.mjs &
          sleep 2
      
      - name: SSE Quick Probe
        run: |
          set -e
          H=http://localhost:8766
          K="ci-test-key"
          
          # Create job and stream events
          JOB=$(curl -s $H/mcp -H "X-API-Key: $K" -H 'Content-Type: application/json' \
            -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"run_eval","arguments":{"taskId":"probe","configId":"default"}}}' \
            | jq -r '.result.content[0].text' | jq -r '.jobId')
          
          # Verify SSE streaming works
          timeout 3s bash -c "curl -N \"$H/sse?topic=job/$JOB\" -H \"X-API-Key: $K\" | sed -n '1,6p'"
          echo "✅ SSE streaming healthy"
```

## 🔍 Operational Workflows

### 1. Monitor Job Progress

```bash
# Start a long-running eval
JOB=$(curl -s localhost:8766/mcp -H 'X-API-Key: key' \
  -d '{...run_eval...}' | jq -r '.result.content[0].text' | jq -r '.jobId')

# Watch real-time progress
curl -N "localhost:8766/sse?topic=job/$JOB" -H "X-API-Key: key"
# data: {"jobId":"job_abc","status":"running","progress":0.3}
# data: {"jobId":"job_abc","status":"completed","result":{...}}
```

### 2. Canary Deployment with SLO Monitoring

```bash
# Start canary promotion
CANARY=$(curl -s localhost:8766/mcp -H 'X-API-Key: key' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"start_canary","arguments":{"modelId":"lukhas-v2","fromGate":"stage","toGate":"production","sloPolicy":{"latency_p95_ms":800,"error_rate":0.01}}}}' \
  | jq -r '.result.content[0].text' | jq -r '.canaryId')

# Watch SLO metrics and promotion
curl -N "localhost:8766/sse?topic=canary/$CANARY" -H "X-API-Key: key"
# event: metric
# data: {"canaryId":"canary_xyz","latency_p95_ms":650,"error_rate":0.005,"gate":"production"}
# event: promoted
# data: {"canaryId":"canary_xyz","modelId":"lukhas-v2","toGate":"production"}
```

### 3. Emergency Rollback

```bash
# Manual abort if SLO breach detected
curl -s localhost:8766/mcp -H 'X-API-Key: key' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"abort_canary","arguments":{"canaryId":"canary_xyz","reason":"manual override"}}}'

# Watch rollback events
# event: rolled_back
# data: {"canaryId":"canary_xyz","reason":"manual override","duration":"12m"}
```

## 📈 Audit Trail Queries

Query the SQLite database for operational insights:

```sql
-- Recent job activity
SELECT created_at, job_id, status, result 
FROM jobs 
WHERE created_at > datetime('now', '-1 hour') 
ORDER BY created_at DESC;

-- Canary success rate
SELECT 
  status,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM canaries 
WHERE created_at > datetime('now', '-24 hours')
GROUP BY status;

-- SLO breach analysis
SELECT 
  cm.canary_id,
  cm.latency_p95_ms,
  cm.error_rate,
  c.from_gate,
  c.to_gate,
  c.status
FROM canary_metrics cm
JOIN canaries c ON cm.canary_id = c.id
WHERE cm.latency_p95_ms > 800 OR cm.error_rate > 0.01
ORDER BY cm.created_at DESC
LIMIT 20;
```

## 🎯 Next Steps

### For Matriz UI Integration
1. Import `dashboard/sseClient.js` into your frontend
2. Subscribe to `canary/*` and `job/*` topics
3. Display narrative events in a scrolling ledger
4. Show structured metrics in real-time charts

### For Grafana Integration
1. Connect Grafana to the SQLite database
2. Create panels for job throughput, canary success rate
3. Set up alerts for SLO breaches and rollbacks
4. Use the narrative audit trail for incident timelines

### For Production Deployment
1. Wire Prometheus backend with your actual metrics
2. Configure SLO policies per model/gate combination
3. Set up log aggregation for audit trails
4. Deploy SSE dashboard behind authentication

---

**The MCP cockpit is now live with real-time SSE streaming, SLO-guarded deployments, and comprehensive audit trails. Ready for production operations! 🚀**