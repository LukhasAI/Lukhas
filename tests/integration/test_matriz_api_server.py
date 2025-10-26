"""Import-smoke for matriz.interfaces.api_server (VERIFY)."""

def test_matriz_api_server_imports():
    mod = __import__("matriz.interfaces.api_server", fromlist=["*"])
    assert mod is not None
