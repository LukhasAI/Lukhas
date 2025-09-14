# tests/integration/adapters/conftest.py
import sys, types, pytest

def _stub(modname, **attrs):
    if modname not in sys.modules:
        m = types.ModuleType(modname)
        for k, v in attrs.items(): setattr(m, k, v)
        sys.modules[modname] = m

@pytest.fixture(autouse=True)
def _stub_numpy(monkeypatch):
    if "numpy" not in sys.modules:
        sys.modules["numpy"] = types.SimpleNamespace()

@pytest.fixture(autouse=True)
def _adapters_sandbox(monkeypatch):
    # Gmail / Google API stubs if SDK not installed
    _stub("googleapiclient.discovery", build=lambda *a, **k: types.SimpleNamespace(users=types.SimpleNamespace().__dict__))
    _stub("google.oauth2.credentials", Credentials=object)
    # Dropbox SDK stub
    _stub("dropbox", Dropbox=lambda *a, **k: types.SimpleNamespace(files=types.SimpleNamespace(list_folder=lambda *a, **k: {"entries": []})))
    # HTTP layer guard
    monkeypatch.setenv("NO_NETWORK", "1")
    yield
