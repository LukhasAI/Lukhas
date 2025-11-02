from __future__ import annotations

import importlib
import sys
import types
from typing import Any, Sequence

import pytest


class _ColumnContext:
    def __enter__(self) -> _ColumnContext:
        return self

    def __exit__(self, *args: Any) -> None:
        return None


class _SidebarStub:
    def title(self, *args: Any, **kwargs: Any) -> None:
        return None

    def checkbox(self, *args: Any, value: bool = False, **kwargs: Any) -> bool:
        return value

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def write(self, *args: Any, **kwargs: Any) -> None:
        return None

    def success(self, *args: Any, **kwargs: Any) -> None:
        return None

    def error(self, *args: Any, **kwargs: Any) -> None:
        return None

    def info(self, *args: Any, **kwargs: Any) -> None:
        return None

    def image(self, *args: Any, **kwargs: Any) -> None:
        return None

    def button(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def selectbox(self, label: str, options: Sequence[str], index: int = 0, **kwargs: Any) -> str:
        if options:
            return options[index if 0 <= index < len(options) else 0]
        return ""


class _StreamlitStub(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.sidebar = _SidebarStub()

    def set_page_config(self, **kwargs: Any) -> None:
        return None

    def title(self, *args: Any, **kwargs: Any) -> None:
        return None

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def selectbox(self, label: str, options: Sequence[str], index: int = 0, **kwargs: Any) -> str:
        if options:
            return options[index if 0 <= index < len(options) else 0]
        return ""

    def slider(self, label: str, min_value: int, max_value: int, value: int, **kwargs: Any) -> int:
        return value

    def button(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def warning(self, *args: Any, **kwargs: Any) -> None:
        return None

    def success(self, *args: Any, **kwargs: Any) -> None:
        return None

    def json(self, *args: Any, **kwargs: Any) -> None:
        return None

    def columns(self, count: int) -> tuple[_ColumnContext, ...]:
        return tuple(_ColumnContext() for _ in range(count))

    def subheader(self, *args: Any, **kwargs: Any) -> None:
        return None

    def cache_data(self, *args: Any, **kwargs: Any):  # - simple passthrough decorator
        """Return a pass-through decorator emulating Streamlit's cache."""

        def decorator(func):
            return func

        return decorator


@pytest.fixture(autouse=True)
def _install_streamlit_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    streamlit_stub = _StreamlitStub()
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)


@pytest.fixture(autouse=True)
def _install_dashboard_settings_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    dashboard_stub = types.ModuleType("core.dashboard_settings")

    def get_paired_apps(user_id: str) -> list[str]:
        return [f"demo_app_for_{user_id}"]

    dashboard_stub.get_paired_apps = get_paired_apps  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "core.dashboard_settings", dashboard_stub)


def test_build_module_blocks_discovers_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    module_name = "core.interfaces.as_agent.streamlit.app"
    for name in list(sys.modules):
        if name.startswith(module_name):
            monkeypatch.delitem(sys.modules, name, raising=False)

    module = importlib.import_module(module_name)
    module_blocks = module.build_module_blocks()

    assert module_blocks, "Expected module blocks to be discovered"
    full_header, mod_name, body = module_blocks[0]
    assert full_header.startswith("### 📦 ")
    assert "## 📘 Header Info" in body
    assert "## 📄 Usage Guide" in body

    discovered_names = {name.lower() for _, name, _ in module_blocks}
    assert any("core" in name for name in discovered_names)
    assert any("matriz" in name for name in discovered_names)
    assert any("lukhas" in name for name in discovered_names)

    assert module.module_blocks == module_blocks
