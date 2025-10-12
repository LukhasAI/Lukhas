"""Dream trace surface; tries backends with graceful fallback."""

from __future__ import annotations

from importlib import import_module

__all__ = ["DreamTrace"]

for _module in (
    "lukhas_website.lukhas.consciousness.dream.trace",
    "labs.consciousness.dream.trace",
    "consciousness.dream.trace",
):
    try:
        backend = import_module(_module)
        if hasattr(backend, "DreamTrace"):
            DreamTrace = getattr(backend, "DreamTrace")  # type: ignore
            break
    except Exception:
        continue
else:

    class DreamTrace:
        """Fallback dream trace recorder."""

        def __init__(self):
            self._events = []

        def record(self, event):
            self._events.append(event)

        def events(self):
            return tuple(self._events)
