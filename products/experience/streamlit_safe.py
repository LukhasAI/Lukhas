"""Safe Streamlit import helper for experience modules."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

# ΛTAG: streamlit_fallback

logger = logging.getLogger("ΛTRACE.products.experience.streamlit")


@dataclass
class StreamlitCall:
    """Record of a Streamlit invocation for deterministic testing."""

    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class StreamlitFacade:
    """Proxy object that wraps a real Streamlit module when available."""

    def __init__(self, real_streamlit: Optional[Any] = None):
        self._real = real_streamlit
        self.calls: list[StreamlitCall] = []

    def _record(self, method: str, *args: Any, **kwargs: Any) -> StreamlitCall:
        call = StreamlitCall(method=method, args=args, kwargs=kwargs)
        self.calls.append(call)
        logger.debug("Streamlit facade call", extra={"method": method, "args": args, "kwargs": kwargs})
        return call

    def reset(self) -> None:
        """Clear recorded calls."""

        self.calls.clear()

    def title(self, text: str) -> Any:
        record = self._record("title", text)
        if self._real is not None:
            return self._real.title(text)
        return record

    def header(self, text: str) -> Any:
        record = self._record("header", text)
        if self._real is not None:
            return self._real.header(text)
        return record

    def metric(self, label: str, value: Any, *args: Any, **kwargs: Any) -> Any:
        record = self._record("metric", label, value, *args, **kwargs)
        if self._real is not None:
            return self._real.metric(label, value, *args, **kwargs)
        return record

    def __getattr__(self, item: str) -> Callable[..., Any]:
        real_attr = getattr(self._real, item, None) if self._real is not None else None

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self._record(item, *args, **kwargs)
            if callable(real_attr):
                return real_attr(*args, **kwargs)
            return None

        return wrapper


try:  # pragma: no cover - import guard exercised indirectly
    import streamlit as _streamlit

    STREAMLIT_AVAILABLE = True
    _FACADE = StreamlitFacade(_streamlit)
except Exception:  # pragma: no cover - fallback path exercised in tests
    STREAMLIT_AVAILABLE = False
    _FACADE = StreamlitFacade()
    logger.info("Streamlit not available, using console facade")


def get_streamlit() -> StreamlitFacade:
    """Return the shared Streamlit facade instance."""

    return _FACADE


__all__ = ["StreamlitFacade", "StreamlitCall", "STREAMLIT_AVAILABLE", "get_streamlit"]
