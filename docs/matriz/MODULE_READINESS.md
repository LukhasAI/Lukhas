---
status: wip
type: documentation
owner: unknown
module: matriz
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# MODULE READINESS — MATRIZ (per-module protocol)

## Checklist
- `module.lane.yaml` present (owner, lane, SLO p95s, gates, artifacts).
- **Perf:** unit (N=10k) vs E2E (N=2k) with bootstrap CI95%; artifacts attached.
- **Safety:** Guardian default-ON; kill-switch drill evidence.
- **Chaos:** partial failure, timeouts, brownout, clock skew; <10% regression; rollback ≤30s.
- **Telemetry:** prom rules + tests; labels `{lane,component,operation}`; no dynamic IDs in labels.
- **Security:** bandit/semgrep/pip-audit strict = PASS; SBOM archived.
- **Schema:** JSON schema + snapshot; drift test blocks breaking changes.
- **Docs:** public API + flags + runbook updated.

**Definition of Done:** all green + import-linter ✅ + signed evidence bundle.
