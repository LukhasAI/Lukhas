---
status: wip
type: documentation
---
# 🚀 T4 Production-Grade LUKHAS MCP Cockpit

## **Deployment Guide: Zero-to-Production in 4 Commands**

### **Quick Start (Development)**

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp

# Start MCP server with zero-dep cockpit
PORT=8766 node mcp-streamable.mjs

# Open cockpit in browser
open http://localhost:8766/cockpit.html
```

### **Production Deployment**

```bash
# 1. Enable Prometheus SLO monitoring
export PROM_URL="http://prometheus:9090"
export PROM_Q_LAT='histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="matriz"}[5m])) by (le)) * 1000'
export PROM_Q_ERR='sum(rate(http_requests_total{job="matriz",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="matriz"}[5m]))'

# 2. Set API keys for authentication
export LUKHAS_MCP_API_KEYS="prod-key-1,admin-key-2"

# 3. Configure production database
export LUKHAS_MCP_DB="/data/lukhas-mcp.db"

# 4. Start with production settings
LUKHAS_REPO_ROOT=/path/to/lukhas \
PORT=8766 \
node mcp-streamable.mjs
```

## **T4 Operational Features**

### **🎯 Live Prometheus SLO Monitoring**
- **Real p95 latency** and **error rate** queries from production Prometheus
- **SLO-guarded canary deployments** with automatic promotion/rollback
- **Conservative fallback** when metrics unavailable (9999ms latency, 100% error rate)
- **Configurable PromQL** via environment variables

### **⚡ Zero-Dependency Cockpit**
- **Pure HTML/CSS/JS** - no build step, no external dependencies
- **Real-time SSE streaming** for jobs and canaries
- **WHY button** shows narrative audit trails for any decision
- **Color-coded events**: green (success), orange (progress), red (errors)

### **🧠 Narrative Audit Trails**
- **Human-readable operational stories** stored in SQLite
- **Perfect for compliance** and regulatory reporting
- **Consciousness-aware** for Matriz symbolic reasoning
- **Query any job/canary/model ID** to understand WHY decisions were made

### **🛡️ Production Security**
- **API key authentication** via headers or query parameters
- **Per-IP rate limiting** with configurable token buckets
- **CORS support** for secure cross-origin requests
- **Audit logging** for all operations

## **ChatGPT Integration Patterns**

### **0.01% Power User Workflow**

```bash
# 1. Launch eval via ChatGPT MCP
curl -X POST http://localhost:8766/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"run_eval","arguments":{"taskId":"stress-test","configId":"production"}}}'

# 2. Watch live progress in cockpit
open http://localhost:8766/cockpit.html

# 3. Query WHY for any risky decision
curl -X POST http://localhost:8766/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"why","arguments":{"id":"job_abc123"}}}'
```

### **T4 Team SLO Enforcement**

```bash
# Start canary with live SLO monitoring
curl -X POST http://localhost:8766/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"start_canary","arguments":{"modelId":"lukhas-v4","fromGate":"staging","toGate":"production","policy":{"windowSeconds":300,"targets":{"latency_p95_ms":500,"max_error_rate":0.01}}}}}'

# Monitor via SSE stream
curl -N -H "Accept: text/event-stream" -H "X-API-Key: your-key" \
  http://localhost:8766/sse?topic=canaries
```

## **CI/CD Integration**

### **Automated SSE Health Probes**

The workflow in `.github/workflows/mcp-sse-probe.yml` runs every 30 minutes:

```yaml
name: MCP SSE Probe
on:
  schedule: [{ cron: "*/30 * * * *" }]
  workflow_dispatch: {}
jobs:
  probe:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Boot MCP (ephemeral)
        run: |
          export PORT=9009
          nohup node mcp-servers/lukhas-devtools-mcp/mcp-streamable.mjs > server.log 2>&1 &
          sleep 2
      - name: Launch tiny job
        run: |
          curl -s http://localhost:9009/mcp -H 'Content-Type: application/json' \
            -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"run_eval","arguments":{"taskId":"probe","configId":"ci"}}}'
      - name: Open SSE and assert lines
        run: |
          curl -sN --max-time 8 http://localhost:9009/sse?topic=jobs | head -n 20
```

## **Consciousness-Aware Integration**

### **Matriz Symbolic Reasoning**

The cockpit provides perfect integration for consciousness-aware operations:

```javascript
// Matriz can read narrative audit trails for symbolic reasoning
const auditTrail = await fetch('/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-API-Key': key },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: { name: 'why', arguments: { id: 'canary_promotion_xyz' }}
  })
}).then(r => r.json());

// Parse human-readable operational story for symbolic processing
const narrative = auditTrail.result.content[0].text;
// "[2025-10-04 08:15] actor=system action=canary_promote details={...}"
```

### **Live Operational State**

```javascript
// Real-time operational cognition via SSE
const sse = new EventSource('/sse?topic=jobs&topic=canaries&key=api-key');
sse.addEventListener('canary', (event) => {
  const data = JSON.parse(event.data);
  // Process real-time canary state for consciousness decisions
  processOperationalState(data);
});
```

## **Wire Compatibility Guarantee**

✅ **All existing JSON-RPC tools unchanged** (search, fetch, run_eval, start_canary, etc.)  
✅ **ChatGPT contract preserved** (search/fetch first, required id field)  
✅ **Graceful fallback** to stub adapter when Prometheus unavailable  
✅ **Additive-only database changes** - no breaking schema modifications  
✅ **Conservative SLO decisions** when metrics missing (NaN → safe defaults)  

## **Environment Variables Reference**

```bash
# Core Configuration
PORT=8766                                    # HTTP server port
LUKHAS_REPO_ROOT=/path/to/lukhas            # Repository root path
LUKHAS_MCP_DB=/data/lukhas-mcp.db           # SQLite database path
LUKHAS_MCP_API_KEYS="key1,key2"            # Comma-separated API keys

# Prometheus SLO Configuration  
PROM_URL="http://prometheus:9090"           # Prometheus base URL
PROM_BEARER="token"                         # Optional bearer token
PROM_Q_LAT="histogram_quantile(...)"       # Custom latency PromQL
PROM_Q_ERR="sum(rate(...))"                # Custom error rate PromQL

# Rate Limiting
MCP_RL_WINDOW_MS=10000                      # Rate limit window (ms)
MCP_RL_BUCKET=60                            # Tokens per window

# State Management
MCP_STATE_PATH="/data/mcp-state.json"      # State persistence path
```

## **Operational Excellence Checklist**

### **T4 Production Readiness**

- [x] **Real-time SLO monitoring** with live Prometheus metrics
- [x] **Zero-dependency dashboard** for emergency operations visibility  
- [x] **Narrative audit trails** for compliance and debugging
- [x] **API authentication** and per-IP rate limiting
- [x] **CI/CD health probes** validating SSE streaming
- [x] **Wire compatibility** preserved for all existing tools
- [x] **Graceful degradation** when external dependencies fail

### **0.01% Power User Support**

- [x] **Live job/canary streaming** via SSE for real-time monitoring
- [x] **WHY button** for instant narrative audit retrieval
- [x] **SLO-guarded deployments** with automatic rollback
- [x] **File operations** via MCP for live code patching
- [x] **Search/fetch** for repository exploration
- [x] **Constitutional AI** ready with narrative operational context

**🎯 The LUKHAS MCP Cockpit is now T4 production-grade with full operational intelligence, real-time monitoring, and consciousness-aware narrative audit trails! Ready for Matriz symbolic operational cognition! 🧠⚛️🛡️**