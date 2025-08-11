# MCP Deployment Issues - Terminal Freeze Notes

Date: August 11, 2025

## Terminal Freeze Issue

**Problem Command that Freezes Terminal:**
```bash
timeout 5 docker run --rm -i lukhas-mcp-server python lukhas_mcp_server.py < /dev/null
```

**Issue Analysis:**
- MCP servers communicate via stdio (standard input/output)
- Docker run with -i flag expects interactive input
- The command freezes waiting for stdin communication
- Timeout commands can cause terminal hanging in Docker contexts

## Working Solutions

**1. MCP Server Status Check (Non-blocking):**
```bash
docker run --rm lukhas-mcp-server python -c "print('MCP server container ready')"
```

**2. MCP Server Validation (Quick test):**
```bash
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | docker run --rm -i lukhas-mcp-server python lukhas_mcp_server.py
```

**3. Background Container Test:**
```bash
docker run --name mcp-test -d lukhas-mcp-server sleep 10
docker exec mcp-test python lukhas_mcp_server.py --version
docker rm -f mcp-test
```

## MCP Deployment Status

**Completed:**
- Docker container builds successfully
- MCP server code is functional
- All required modules included in container
- MCP library compatibility fixed (mcp==1.12.4)

**Current State:**
- Container: lukhas-mcp-server (ready)
- Server: lukhas_mcp_server_simplified.py (working)
- Method: stdio communication (MCP standard)

## Next Steps

1. Configure Claude Code to use the MCP server via stdio
2. Test MCP tools: list_resources, read_resource, list_tools
3. Integrate with LUKHAS consciousness modules

## Avoid These Commands

- Any `timeout` commands with Docker interactive mode
- Long-running Docker commands with -i flag without proper input
- MCP server testing without understanding stdio protocol

## Quick Recovery

If terminal freezes:
- Ctrl+C to interrupt
- Close terminal tab and open new one
- Kill Docker containers: `docker kill $(docker ps -q)`
