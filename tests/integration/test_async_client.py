"""Import-smoke for core.consciousness.async_client."""


def test_async_client_imports():
    mod = __import__("core.consciousness.async_client", fromlist=["*"])
    assert mod is not None
