import importlib
import time


def test_core_import_under_250ms():
    """Keep alias import cost reasonable for large codebase."""
    t0 = time.perf_counter()
    importlib.import_module("core")  # alias shim path
    importlib.import_module("core.trace")
    dt = (time.perf_counter() - t0) * 1000
    assert dt < 250, f"core alias import too slow: {dt:.2f}ms (target: <250ms)"
