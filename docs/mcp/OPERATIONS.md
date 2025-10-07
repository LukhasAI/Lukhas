---
status: wip
type: documentation
owner: unknown
module: mcp
redirect: false
moved_to: null
---

# LUKHAS MCP Operations (T4/0.01%)

## Fast checks
```bash
make mcp-validate-catalog  # schema + 11-tool contract
make mcp-smoke             # end-to-end stdio smoke
make mcp-health            # version, tool_count, catalog_sha, p95
```

## SLOs

* p95 latency ≤ 2500ms (red after 2 consecutive breaches)
* Catalog: exactly 11 tools, frozen SHA unless PR has `allow:mcp-catalog-bump`

## Triage SOP

1. Pull artifacts: `mcp_smoke.log`, `mcp_health.json`
2. If p95 breached: file **MCP Regression** issue, attach logs
3. If catalog drift: run `make mcp-freeze`, update SHA or revert
4. If unsafe tool blocked: confirm `ALLOW_UNSAFE_TOOLS=1` + RBAC label