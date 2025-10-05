# Lukhas DevTools MCP Server

Single-source tool catalog for ChatGPT and CI.

## Quickstart
```bash
python3 server.py  # stdio JSON-RPC
# in another shell:
python3 tools/mcp/poke_server.py
```

## Contract

* Catalog: `tooling/catalog.json`
* Names are advertised as `lukhas.<name>`
* Tool result envelope: `{"code": int, "stdout": str, "stderr": str}`

## Policies

* `MCP_CONVEYOR_DISABLED=1` blocks `conveyor.execute` in CI
* Latency SLO: p95 ≤ ${MCP_P95_LIMIT_MS:-2500} ms

## Tool Catalog

The server exposes 11 tools from the canonical catalog:

- `lukhas.manifests.validate` - Validate module manifests
- `lukhas.manifests.lock` - Generate manifest locks
- `lukhas.registry.build` - Build module registry
- `lukhas.registry.diff` - Compare registry versions
- `lukhas.docs.registry.refresh` - Refresh documentation registry
- `lukhas.docs.frontmatter.guard` - Validate documentation frontmatter
- `lukhas.conveyor.plan` - Generate promotion plans
- `lukhas.conveyor.execute` - Execute promotions (RBAC protected)
- `lukhas.sim.schedule` - Schedule consciousness simulations
- `lukhas.sim.collect` - Collect simulation results
- `lukhas.audit.export` - Export audit trails

## Development

```bash
# Contract validation
make mcp-contract

# Smoke tests
make mcp-smoke

# Full validation
make mcp-ready

# Docker build
make mcp-docker-build

# Docker run
make mcp-docker-run
```