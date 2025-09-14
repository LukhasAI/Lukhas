import pytest


@pytest.mark.integration
def test_mcp_server_initializes_without_crash():
    # Import inside test to avoid import-time failures if MCP is absent
    from mcp_servers.lukhas_mcp_server import LUKHASMCPServer, MCP_AVAILABLE

    # Always ensure server can be constructed without raising
    # If MCP is unavailable, the module falls back to demo mode
    srv = LUKHASMCPServer(workspace_root=".")
    assert srv is not None

    # If MCP is available, we expect the server to have a real Server attached
    if MCP_AVAILABLE:
        assert hasattr(srv, "server")
