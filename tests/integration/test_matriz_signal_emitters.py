"""Integration smoke for matriz_signal_emitters import."""


def test_matriz_signal_emitters_module_imports():
    mod = __import__("core.matriz_signal_emitters", fromlist=["*"])
    assert mod is not None

