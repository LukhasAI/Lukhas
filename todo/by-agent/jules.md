# Jules (Google AI Agent) Tasks

**Agent**: Jules (Google AI Agent)
**Specialty**: CI/CD, observability, security, monitoring

**Last Updated**: Auto-synced from TODO/MASTER_LOG.md

---

## Quick Stats

- **P0 (Critical)**: 3 tasks
- **P1 (High)**: 8 tasks
- **P2 (Medium)**: 5 tasks
- **P3 (Low)**: 1 tasks
- **Total**: 17 tasks

---

## Priority 0 (Critical - Drop Everything) ⚠️

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| SG001 | Enable Guardian DSL enforcement in canary mode | ASSIGNED | S | 10% canary traffic |
| SC003 | Add secret scanning | ASSIGNED | S | Gitleaks integration |
| SG006 | Gradual Guardian enforcement rollout | ASSIGNED | M | Gradual rollout strategy |

---

## Priority 1 (High - This Sprint) 🔥

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| SG007 | Create Guardian metrics dashboard | PENDING | S | Grafana dashboard |
| MP006 | Add orchestrator distributed tracing | PENDING | M | OpenTelemetry |
| OB001 | Enable Prometheus metrics export | PENDING | S | /metrics endpoint |
| OB002 | Initialize OpenTelemetry tracing | PENDING | M | Distributed tracing |
| OB005 | Implement SLO monitoring | PENDING | S | SLI/SLO definitions |
| SC001 | Integrate SBOM generation | PENDING | S | Supply chain security |
| SC002 | Implement license policy | PENDING | S | OSS compliance |
| LM002 | Implement canary deployment | PENDING | M | Gradual rollout |

---

## Priority 2 (Medium - Next Sprint) 📋

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| OB006 | Add custom application metrics | PENDING | M | Business metrics |
| OB007 | Implement log aggregation | PENDING | M | Centralized logging |
| OB008 | Run observability drill | PENDING | S | Incident simulation |
| SC004 | Harden GitHub Actions | PENDING | S | Action security |
| SC005 | Implement dependency freshness | PENDING | S | Dependabot config |

---

## Priority 3 (Low - Backlog) 💭

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| TP003 | Add load testing | PENDING | M | Performance testing |

---

## How to Use This View

1. **Pick a task** from the highest priority section with `PENDING` status
2. **Read the full details** in TODO/MASTER_LOG.md
3. **Update status** to `IN_PROGRESS` in MASTER_LOG when you start
4. **Complete the work** following LUKHAS standards
5. **Update status** to `COMPLETED` and add PR link when done
6. **Run sync** to update this view: `python3 scripts/todo/sync_agents.py`

---

**Note**: This file is auto-generated from MASTER_LOG.md. Do not edit manually.
To add or modify tasks, edit TODO/MASTER_LOG.md and run `python3 scripts/todo/sync_agents.py`.

**View more**: [TODO/MASTER_LOG.md](../MASTER_LOG.md) | [TODO/RULES_FOR_AGENTS.md](../RULES_FOR_AGENTS.md)
