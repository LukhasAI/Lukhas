import sys
import types
import pytest
import importlib.util


def _ensure_stub(modname: str, attrs: dict):
    if modname not in sys.modules:
        m = types.ModuleType(modname)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[modname] = m


@pytest.fixture(autouse=True)
def _bio_safe_imports():
    # Only if your tested code imports these optionally:
    _ensure_stub("gymnasium", {"__version__": "0.0-stub"})
    _ensure_stub("torch", {"__version__": "0.0-stub"})
    yield


need_gym = pytest.mark.skipif(
    importlib.util.find_spec("gymnasium") is None, reason="gymnasium not available in focused lane"
)
