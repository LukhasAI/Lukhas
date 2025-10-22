# RC Soak Operations Guide
**Version**: v0.9.0-rc  
**Purpose**: 48-72h monitoring window for GA readiness validation

---

## 🎯 Overview

The RC Soak Operations package provides automated tooling for monitoring LUKHAS v0.9.0-rc during the final validation window before General Availability (GA).

### What's Included

- **Makefile Targets**: Quick commands for soak operations
- **Snapshot Script**: Daily health artifact generation
- **Synthetic Load**: Realistic traffic generator
- **Health Reports**: JSON + Markdown artifacts

---

## 🚀 Quick Start

### 1. Start RC Soak Server

```bash
make rc-soak-start
```

This starts the LUKHAS façade on `http://localhost:8000` and logs to `/tmp/lukhas-logs/rc-soak.log`.

**Endpoints**:
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics (Prometheus format)
- API: http://localhost:8000/v1/*

### 2. Generate Synthetic Load

```bash
make rc-synthetic-load
# Or with custom request count:
make rc-synthetic-load REQUESTS=500
```

This generates realistic traffic patterns:
- Embeddings requests (`/v1/embeddings`)
- Chat completions (`/v1/chat/completions`)
- Health checks (`/health`)

### 3. Capture Daily Snapshot

```bash
make rc-soak-snapshot
```

Generates artifacts in `docs/audits/health/<date>/`:
- `latest.json` - Machine-readable metrics
- `latest.md` - Human-readable report

### 4. Stop RC Soak

```bash
make rc-soak-stop
```

---

## 📊 Health Artifacts

### JSON Structure

```json
{
  "timestamp": "2025-10-15T12:00:00",
  "rc_version": "v0.9.0-rc",
  "uptime_hours": "24.5",
  "services": {
    "prometheus": true,
    "grafana": true,
    "facade": true
  },
  "metrics": {
    "guardian_denials_24h": "12",
    "pdp_p95_latency_ms": "8.5",
    "rl_hit_rate": "0.92"
  },
  "gates": {
    "guardian_denial_rate_ok": true,
    "pdp_latency_ok": true,
    "all_services_up": true
  }
}
```

### Markdown Report

See `docs/audits/health/<date>/latest.md` for:
- System health dashboard
- Metrics snapshot with gate checks
- RC soak checklist
- Next actions

---

## 🎯 GA Readiness Gates

Monitor these during the 48-72h window:

- ✅ **RC soak ≥48h** with no critical alerts
- ✅ **Guardian denial rate** < 1% sustained
- ✅ **PDP p95 latency** < 10ms sustained
- ✅ **RL cache hit rate** > 80%
- ✅ **All services healthy** (Prometheus, Grafana, Façade)
- ✅ **No memory leaks** detected
- ✅ **No error rate spikes**

---

## 📈 Monitoring Stack

### Prometheus (localhost:9090)

- **Metrics**: http://localhost:9090/metrics
- **Alerts**: http://localhost:9090/alerts
- **Targets**: http://localhost:9090/targets

### Grafana (localhost:3000)

- **Dashboard**: http://localhost:3000/d/guardian-rl-v090
- **Credentials**: admin/admin (first login)

### Dashboard Panels

1. **PDP Latency** (p95, p99)
2. **Guardian Denial Rate** (24h window)
3. **RL Cache Hit Rate**
4. **Health Score** (composite)
5. **Request Rate** (embeddings, chat, dreams)
6. **Error Rate** (4xx, 5xx)
7. **System Resources** (CPU, memory)

---

## 🔄 Daily Workflow

### Morning (09:00)

```bash
# Check overnight health
make rc-soak-snapshot

# Review artifacts
cat docs/audits/health/$(date +%Y-%m-%d)/latest.md

# Check Grafana for anomalies
open http://localhost:3000/d/guardian-rl-v090
```

### Midday (12:00)

```bash
# Generate synthetic load
make rc-synthetic-load REQUESTS=500

# Wait 5 minutes for metrics to populate
sleep 300

# Capture snapshot
make rc-soak-snapshot
```

### Evening (18:00)

```bash
# Final snapshot of the day
make rc-soak-snapshot

# Check for alerts
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | select(.state=="firing")'
```

---

## 🛠️ Troubleshooting

### Façade Won't Start

```bash
# Check logs
tail -f /tmp/lukhas-logs/rc-soak.log

# Check port availability
lsof -i :8000

# Kill existing process
make rc-soak-stop
```

### Metrics Not Appearing

```bash
# Check Prometheus scrape targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'

# Verify façade metrics endpoint
curl http://localhost:8000/metrics | grep -c "guardian_"
```

### Snapshot Script Fails

```bash
# Check service health manually
curl http://localhost:8000/health
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health

# Run snapshot with debug
bash -x scripts/ops/rc_soak_snapshot.sh
```

---

## 📝 Automation (Optional)

### Cron Job for Daily Snapshots

```bash
# Add to crontab (09:00, 12:00, 18:00 daily)
0 9,12,18 * * * cd /Users/agi_dev/LOCAL-REPOS/Lukhas && make rc-soak-snapshot >> /tmp/lukhas-logs/cron.log 2>&1
```

### GitHub Actions (Future)

See `.github/workflows/rc-soak-daily.yml` for automated daily checks (not yet implemented).

---

## 🔗 Related Documents

- **Green Light Plan**: `docs/gonzo/GREEN_LIGHT_PLAN.md`
- **Monitoring Deployment**: `LOCAL_DEPLOYMENT_COMPLETE.md`
- **Parallel Execution Plan**: `docs/plans/PARALLEL_AGENT_EXECUTION_PLAN.md`

---

## 📞 Support

For issues or questions:
1. Check Grafana dashboard for visual insights
2. Review Prometheus alerts
3. Check façade logs: `/tmp/lukhas-logs/rc-soak.log`
4. Run health diagnostics: `make doctor`

---

**Last Updated**: 2025-10-15  
**Maintainer**: Copilot (Track D)
