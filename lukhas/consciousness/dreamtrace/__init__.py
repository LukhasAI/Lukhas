"""DreamTrace alias module."""

from __future__ import annotations

try:
    from ..dream.trace import DreamTrace  # type: ignore  # noqa: TID252 (relative imports in __init__.py are idiomatic)
except Exception:
    class DreamTrace:
        def __init__(self):
            self._events = []

        def record(self, event):
            self._events.append(event)

        def events(self):
            return tuple(self._events)

__all__ = ["DreamTrace"]
