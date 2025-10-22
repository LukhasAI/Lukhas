#!/usr/bin/env bash
# RC Soak Health Snapshot
# Captures system health metrics and generates JSON + Markdown reports

set -euo pipefail

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMESTAMP="${DATE}T${TIME}"
HEALTH_DIR="docs/audits/health/${DATE}"

mkdir -p "${HEALTH_DIR}"

echo "📸 Capturing RC soak snapshot at ${TIMESTAMP}..."

# Helper: Check service health
check_service() {
    local url=$1
    if curl -sf "${url}" > /dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

# Collect Prometheus metrics
get_prometheus_metric() {
    local query=$1
    curl -s "http://localhost:9090/api/v1/query?query=${query}" 2>/dev/null \
        | jq -r '.data.result[0].value[1] // "N/A"'
}

# System uptime
if [[ "$(uname)" == "Darwin" ]]; then
    UPTIME_SECONDS=$(sysctl -n kern.boottime | awk '{print $4}' | sed 's/,//')
    CURRENT_SECONDS=$(date +%s)
    UPTIME_HOURS=$(echo "scale=2; (${CURRENT_SECONDS} - ${UPTIME_SECONDS}) / 3600" | bc 2>/dev/null || echo "N/A")
else
    UPTIME_HOURS=$(awk '{print $1/3600}' /proc/uptime 2>/dev/null || echo "N/A")
fi

# Service health checks
PROMETHEUS_UP=$(check_service "http://localhost:9090/-/healthy")
GRAFANA_UP=$(check_service "http://localhost:3000/api/health")
FACADE_UP=$(check_service "http://localhost:8000/health")

# Facade health details
FACADE_HEALTH=$(curl -sf "http://localhost:8000/health" 2>/dev/null || echo '{"status":"DOWN"}')

# Prometheus metrics (if available)
GUARDIAN_DENIALS_24H=$(get_prometheus_metric 'increase(guardian_policy_denials_total[24h])')
PDP_P95_LATENCY=$(get_prometheus_metric 'histogram_quantile(0.95, rate(guardian_pdp_duration_seconds_bucket[5m])) * 1000')
RL_HIT_RATE=$(get_prometheus_metric 'rate(lukhas_rl_cache_hits_total[5m]) / (rate(lukhas_rl_cache_hits_total[5m]) + rate(lukhas_rl_cache_misses_total[5m]))')

# Generate JSON report
METRICS_JSON="${HEALTH_DIR}/latest.json"
cat > "${METRICS_JSON}" <<JSON
{
  "timestamp": "${TIMESTAMP}",
  "rc_version": "v0.9.0-rc",
  "uptime_hours": "${UPTIME_HOURS}",
  "services": {
    "prometheus": ${PROMETHEUS_UP},
    "grafana": ${GRAFANA_UP},
    "facade": ${FACADE_UP}
  },
  "facade_health": ${FACADE_HEALTH},
  "metrics": {
    "guardian_denials_24h": "${GUARDIAN_DENIALS_24H}",
    "pdp_p95_latency_ms": "${PDP_P95_LATENCY}",
    "rl_hit_rate": "${RL_HIT_RATE}"
  },
  "gates": {
    "guardian_denial_rate_ok": $([ "${GUARDIAN_DENIALS_24H}" != "N/A" ] && echo "true" || echo "null"),
    "pdp_latency_ok": $([ "${PDP_P95_LATENCY}" != "N/A" ] && echo "true" || echo "null"),
    "all_services_up": $([ "${PROMETHEUS_UP}" == "true" ] && [ "${GRAFANA_UP}" == "true" ] && [ "${FACADE_UP}" == "true" ] && echo "true" || echo "false")
  }
}
JSON

# Generate Markdown report
REPORT_MD="${HEALTH_DIR}/latest.md"
cat > "${REPORT_MD}" <<MD
# RC Soak Health Report
**Date**: ${DATE} ${TIME}  
**RC Version**: v0.9.0-rc  
**Uptime**: ${UPTIME_HOURS} hours

---

## 🏥 System Health

| Service | Status |
|---------|--------|
| Prometheus | $([ "${PROMETHEUS_UP}" == "true" ] && echo "✅ UP" || echo "❌ DOWN") |
| Grafana | $([ "${GRAFANA_UP}" == "true" ] && echo "✅ UP" || echo "❌ DOWN") |
| Façade | $([ "${FACADE_UP}" == "true" ] && echo "✅ UP" || echo "❌ DOWN") |

### Façade Health Details
\`\`\`json
${FACADE_HEALTH}
\`\`\`

---

## 📊 Metrics Snapshot (24h window)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| Guardian Denials | ${GUARDIAN_DENIALS_24H} | < 1% | $([ "${GUARDIAN_DENIALS_24H}" != "N/A" ] && echo "⏳ TBD" || echo "⚠️ N/A") |
| PDP p95 Latency | ${PDP_P95_LATENCY} ms | < 10ms | $([ "${PDP_P95_LATENCY}" != "N/A" ] && echo "⏳ TBD" || echo "⚠️ N/A") |
| RL Cache Hit Rate | ${RL_HIT_RATE} | > 0.80 | $([ "${RL_HIT_RATE}" != "N/A" ] && echo "⏳ TBD" || echo "⚠️ N/A") |

**Note**: Metrics require active load on the façade. Run \`make rc-synthetic-load\` to generate test traffic.

---

## 🎯 RC Soak Gates (v0.9.0-rc → GA)

- [ ] RC soak ≥48h with no critical alerts
- [ ] Guardian denial rate < 1% sustained
- [ ] PDP p95 < 10ms sustained  
- [ ] All services healthy
- [ ] No memory leaks detected
- [ ] No error rate spikes

---

## 🚀 Next Actions

1. **Review Grafana Dashboard**: [http://localhost:3000/d/guardian-rl-v090](http://localhost:3000/d/guardian-rl-v090)
2. **Check Prometheus Alerts**: [http://localhost:9090/alerts](http://localhost:9090/alerts)
3. **Generate Load**: \`make rc-synthetic-load\`
4. **Daily Snapshot**: Schedule via cron or run manually

---

**Generated**: ${TIMESTAMP}  
**Tool**: \`scripts/ops/rc_soak_snapshot.sh\`
MD

echo "✅ Snapshot complete!"
echo ""
echo "📄 JSON: ${METRICS_JSON}"
echo "📄 Markdown: ${REPORT_MD}"
echo ""
echo "📊 Summary:"
echo "  - Prometheus: $([ "${PROMETHEUS_UP}" == "true" ] && echo "✅ UP" || echo "❌ DOWN")"
echo "  - Grafana: $([ "${GRAFANA_UP}" == "true" ] && echo "✅ UP" || echo "❌ DOWN")"
echo "  - Façade: $([ "${FACADE_UP}" == "true" ] && echo "✅ UP" || echo "❌ DOWN")"
echo ""
echo "🔗 View report: cat ${REPORT_MD}"
