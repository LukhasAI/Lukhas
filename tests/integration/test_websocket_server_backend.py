"""Import-smoke for core.governance.identity.auth_backend.websocket_server."""


def test_websocket_server_backend_imports():
    mod = __import__("core.governance.identity.auth_backend.websocket_server", fromlist=["*"])
    assert mod is not None
