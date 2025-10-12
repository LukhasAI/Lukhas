import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for module_name in ["labs", "labs.core", "labs.core.rem.streamlit_lidar", "labs.core.notion_sync"]:
    sys.modules.pop(module_name, None)


def reload_without_streamlit(module_name: str):
    sys.modules.pop("streamlit", None)
    if module_name in sys.modules:
        sys.modules.pop(module_name)

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "streamlit":
            raise ImportError("Streamlit intentionally unavailable for test")
        return original_import(name, *args, **kwargs)

    import builtins

    builtins.__import__ = fake_import
    try:
        return importlib.import_module(module_name)
    finally:
        builtins.__import__ = original_import


def test_streamlit_lidar_stub_handles_interactions():
    module = reload_without_streamlit("labs.core.rem.streamlit_lidar")

    assert hasattr(module, "st")
    assert module.st.sidebar.checkbox("demo", value=True) is True
    with module.st.container() as container:
        container.markdown("**Test**")


def test_notion_sync_stub_exposes_sidebar(monkeypatch):
    module = reload_without_streamlit("labs.core.notion_sync")

    assert module.STREAMLIT_AVAILABLE is False
    assert module.st.sidebar.checkbox("flag", value=True) is True
    assert module.st.button("noop") is False
