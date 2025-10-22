# RC Soak Health Report
**Date**: 2025-10-22 21:41:21  
**RC Version**: v0.9.0-rc  
**Uptime**: 5.39 hours

---

## 🏥 System Health

| Service | Status |
|---------|--------|
| Prometheus | ❌ DOWN |
| Grafana | ❌ DOWN |
| Façade | ✅ UP |

### Façade Health Details
```json
{"status":"ok","voice_mode":"degraded","matriz":{"version":"unknown","rollout":"disabled","enabled":false},"lane":"prod","modules":{"manifest_count":1713}}
```

---

## 📊 Metrics Snapshot (24h window)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| Guardian Denials | N/A | < 1% | ⚠️ N/A |
| PDP p95 Latency | N/A ms | < 10ms | ⚠️ N/A |
| RL Cache Hit Rate | N/A | > 0.80 | ⚠️ N/A |

**Note**: Metrics require active load on the façade. Run `make rc-synthetic-load` to generate test traffic.

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
3. **Generate Load**: `make rc-synthetic-load`
4. **Daily Snapshot**: Schedule via cron or run manually

---

**Generated**: 2025-10-22T21:41:21  
**Tool**: `scripts/ops/rc_soak_snapshot.sh`
