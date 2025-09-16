"""Streamlit interface for visualizing Lucs' symbolic dreams."""
from __future__ import annotations

import logging
from collections.abc import Iterable
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


try:  # pragma: no cover - exercised in integration environments with Streamlit
    import streamlit as st  # type: ignore

    STREAMLIT_AVAILABLE = True
except ImportError:  # pragma: no cover - we cover the stub via unit tests
    STREAMLIT_AVAILABLE = False

    @dataclass
    class _SidebarStub:
        """Fallback sidebar implementation preserving call semantics."""

        _events: list[dict[str, Any]] = field(default_factory=list)

        def header(self, title: str) -> None:
            self._events.append({"action": "header", "title": title})

        def selectbox(self, label: str, options: Iterable[Any], index: int = 0) -> Any:
            options = list(options)
            choice = options[index] if options else None
            self._events.append({"action": "selectbox", "label": label, "choice": choice})
            return choice

        def checkbox(self, label: str, value: bool = False) -> bool:
            self._events.append({"action": "checkbox", "label": label, "value": value})
            return value

        def slider(
            self,
            label: str,
            min_value: float,
            max_value: float,
            value: float,
            step: float,
        ) -> float:
            self._events.append(
                {
                    "action": "slider",
                    "label": label,
                    "value": value,
                    "range": (min_value, max_value),
                    "step": step,
                }
            )
            return value

    class _ContainerStub(AbstractContextManager["_ContainerStub"]):
        """Context manager stub used for ``with st.container()`` blocks."""

        def __init__(self, buffer: list[dict[str, Any]]):
            self._buffer = buffer

        def __enter__(self) -> _ContainerStub:  # noqa: D401 - standard context protocol
            return self

        def __exit__(self, exc_type, exc, exc_tb) -> bool:
            return False

        def markdown(self, content: str) -> None:
            self._buffer.append({"action": "markdown", "content": content})

    @dataclass
    class _StreamlitStub:
        """Deterministic substitute mirroring Streamlit API used in this module."""

        events: list[dict[str, Any]] = field(default_factory=list)
        sidebar: _SidebarStub = field(default_factory=_SidebarStub)

        def __post_init__(self) -> None:
            self.sidebar = _SidebarStub(self.events)

        # ΛTAG: streamlit_stub
        def set_page_config(self, page_title: str, layout: str = "centered") -> None:
            self.events.append({"action": "set_page_config", "page_title": page_title, "layout": layout})

        def title(self, value: str) -> None:
            self.events.append({"action": "title", "value": value})

        def caption(self, value: str) -> None:
            self.events.append({"action": "caption", "value": value})

        def subheader(self, value: str) -> None:
            self.events.append({"action": "subheader", "value": value})

        def json(self, value: Any) -> None:
            self.events.append({"action": "json", "value": value})

        def info(self, value: str) -> None:
            self.events.append({"action": "info", "value": value})

        def container(self) -> AbstractContextManager[_ContainerStub]:
            return _ContainerStub(self.events)

        @property
        def sidebar(self) -> _SidebarStub:  # type: ignore[override]
            return self._sidebar

        @sidebar.setter
        def sidebar(self, value: _SidebarStub) -> None:
            self._sidebar = value

        def markdown(self, value: str) -> None:
            self.events.append({"action": "markdown", "value": value})

    st = _StreamlitStub()  # type: ignore
    logger.warning("Streamlit not installed; using deterministic stub for Lucs LiDAR dashboard")


def load_dreams() -> list[dict[str, Any]]:
    """Mock load_dreams function."""

    # ΛTAG: dream_loader
    return []


def filter_dreams(
    dreams: list[dict[str, Any]],
    phase: str | None = None,
    collapse_only: bool = False,
    min_resonance: float = 0.0,
) -> list[dict[str, Any]]:
    """Mock filter_dreams function."""

    return dreams


def summarize_dreams(dreams: list[dict[str, Any]]) -> dict[str, Any]:
    """Mock summarize_dreams function."""

    return {"total": len(dreams), "phases": {}, "avg_resonance": 0.0}


# Page setup
st.set_page_config(page_title="Lucs LiDAR", layout="wide")
st.title(" Lucs: Symbolic LiDAR Interpreter")
st.caption("Dreams. Collapses. Resonance.")

# Sidebar filters
st.sidebar.header(" Dream Filters")
phase = st.sidebar.selectbox("Filter by REM Phase", ["All", "1", "2", "3"])
collapse_only = st.sidebar.checkbox("Collapse only", False)
min_res = st.sidebar.slider("Min Resonance", 0.0, 1.0, 0.0, 0.01)

# Load dreams
dreams = load_dreams()

# Filter dreams
filtered = filter_dreams(
    dreams,
    phase=None if phase == "All" else phase,
    collapse_only=collapse_only,
    min_resonance=min_res,
)

# Display stats
st.subheader(" Summary")
stats = summarize_dreams(filtered)  # Pass filtered dreams to summarize_dreams
st.json(stats)

# Dream cards
st.subheader(" Recent Dreams")
if not filtered:
    st.info("No matching dreams found.")
else:
    for d in filtered[-10:]:
        with st.container():
            st.markdown(
                f"""
                **REM Phase {d.get("phase", "?")}**
                - **Resonance**: {d.get("resonance", 0.0)}
                - **Collapse**: {d.get("collapse_id", "-")}
                - **Dream**: {d.get("dream", "")}
                - *Token ID*: `{d.get("source_token", "-")}`
                - *Timestamp*: `{d.get("timestamp", "")}`
            """
            )
# SYNTAX_ERROR_FIXED: ```
