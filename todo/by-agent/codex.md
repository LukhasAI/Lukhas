# CODEX (Deep System Infrastructure) Tasks

**Agent**: CODEX (Deep System Infrastructure)
**Specialty**: Python infrastructure, registries, orchestrator, performance

**Last Updated**: Auto-synced from TODO/MASTER_LOG.md

---

## Quick Stats

- **P0 (Critical)**: 4 tasks
- **P1 (High)**: 9 tasks
- **P2 (Medium)**: 6 tasks
- **P3 (Low)**: 0 tasks
- **Total**: 19 tasks

---

## Priority 0 (Critical - Drop Everything) ⚠️

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| SG001 | Enable Guardian DSL enforcement in canary mode | PENDING | S | 10% canary traffic |
| SG002 | Implement Guardian emergency kill-switch | PENDING | S | /tmp/guardian_emergency_disable |
| MS001 | Implement missing MATRIZ cognitive nodes | PENDING | L | Complete node registry |
| MP001 | Complete async orchestrator timeouts | PENDING | M | Timeout handling |

---

## Priority 1 (High - This Sprint) 🔥

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| SG005 | Fix consent ledger schema | PENDING | M | Add consent tracking |
| MS004 | Optimize memory embeddings performance | PENDING | M | <100ms target |
| MP002 | Implement adaptive node routing | PENDING | M | Dynamic routing |
| MP004 | Create pipeline stage interfaces | PENDING | S | Interface contracts |
| MP007 | Implement orchestrator cancellation | PENDING | M | Cancellation support |
| MP011 | Add orchestrator error recovery | PENDING | M | Error handling |
| OB003 | Replace metric stubs | PENDING | M | Real implementations |
| LM001 | Enforce lane import restrictions | PENDING | S | Import linter |
| TP002 | Implement performance benchmarks | PENDING | M | Benchmark suite |

---

## Priority 2 (Medium - Next Sprint) 📋

| ID | Task | Status | Effort | Notes |
|----|------|--------|--------|-------|
| MS006 | Implement soft-delete for memory | PENDING | S | Soft delete pattern |
| MS007 | Add memory metrics to Prometheus | PENDING | S | Metrics export |
| MP005 | Implement pipeline stage metrics | PENDING | S | Per-stage metrics |
| MP009 | Create orchestrator health checks | PENDING | S | Health endpoint |
| LM004 | Add lane labels to metrics | PENDING | S | Lane tagging |
| DC001 | Complete Trinity→Constellation migration | PENDING | S | Naming migration |

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
