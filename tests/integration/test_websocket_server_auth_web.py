"""Import-smoke for core.governance.identity.auth_web.websocket_server."""

def test_websocket_server_auth_web_imports():
    mod = __import__("core.governance.identity.auth_web.websocket_server", fromlist=["*"])
    assert mod is not None
