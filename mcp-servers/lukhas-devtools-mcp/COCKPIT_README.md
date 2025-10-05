## LUKHAS MCP Cockpit (Zero-dep)

Open `cockpit.html` against a running server (same origin) to watch:
- Jobs & canaries in real time (SSE)
- Click **WHY** to retrieve narrative audit for any `jobId|canaryId|modelId`

### Dev

```bash
PORT=8766 node mcp-servers/lukhas-devtools-mcp/mcp-streamable.mjs
# then open http://localhost:8766/cockpit.html (serve static or via nginx)
```

### Production Setup

```bash
# Enable Prometheus SLO monitoring
export PROM_URL="http://prometheus:9090"
export PROM_Q_LAT='histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="matriz"}[5m])) by (le)) * 1000'
export PROM_Q_ERR='sum(rate(http_requests_total{job="matriz",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="matriz"}[5m]))'

# Start server with live SLO monitoring
LUKHAS_REPO_ROOT=/path/to/lukhas \
LUKHAS_MCP_API_KEYS="prod-key" \
node mcp-streamable.mjs
```

### Features

**Live Streaming:**
- Real-time job and canary events via SSE
- Color-coded status: green (success), orange (progress), red (errors)
- Auto-reconnecting EventSource connections

**Narrative Audits:**
- WHY button queries audit trails for any job/canary/model ID
- Human-readable operational decision history
- Perfect for compliance and debugging

**SLO-Guarded Canaries:**
- Real Prometheus p95 latency and error rate monitoring
- Automatic promotion/rollback based on live metrics
- Conservative fallback when metrics unavailable

### Zero-Dependency Design

The cockpit is pure HTML/CSS/JS with no build step or external dependencies:
- Connects directly to MCP server `/sse` endpoint
- Uses native EventSource API for streaming
- JSON-RPC calls to `/mcp` endpoint for WHY queries
- Copy-paste ready for any deployment

### Integration with Matriz

The cockpit provides consciousness-aware operational intelligence:
- Narrative audit trails for symbolic reasoning
- Real-time operational state for cognitive processing
- Human-readable decision context for constitutional AI

**Ready for T4 operational excellence and 0.01% power user workflows! 🚀⚛️🧠🛡️**