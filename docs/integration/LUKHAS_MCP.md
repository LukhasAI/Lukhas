---
status: wip
type: documentation
owner: unknown
module: integration
redirect: false
moved_to: null
---

# LUKHAS–MCP Integration

## TL;DR
1) Ensure your MCP host (e.g., Claude Code) points at `lukhas-mcp/config.yaml`.
2) Run `make mcp-ready`. If it's green, all tools are callable via MCP.
3) In Claude Code, call tools by name (e.g., `lukhas.docs.registry.refresh`).

## Environment
- `LUKHAS_MCP_MODE` = `stdio` or `websocket`
- `LUKHAS_MCP_CMD`  = stdio server command (if stdio)
- `LUKHAS_MCP_ENDPOINT` = ws(s) URL (if websocket)

## Tool Names
- `lukhas.manifests.validate|lock`
- `lukhas.registry.build|diff`
- `lukhas.docs.registry.refresh` / `lukhas.docs.frontmatter.guard`
- `lukhas.conveyor.plan|execute`
- `lukhas.sim.schedule|collect`
- `lukhas.audit.export`

## Health
- `make mcp-selftest` proves end-to-end readiness.
- CI `mcp-smoke.yml` blocks merges when MCP breaks.