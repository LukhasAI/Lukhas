def test_module_smoke_import():
    import importlib

    # Resolves the module's top-level package (fail loud if packaging is broken)
    assert importlib.import_module("consciousness.simulation")
