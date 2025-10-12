"""Feature flag bridge for lukhas.flags.ff."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.flags.ff",
    "labs.flags.ff",
    "flags.ff",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class Flags:  # type: ignore[misc]
    def __init__(self, **values):
        self._values = values

    def is_enabled(self, name: str) -> bool:
        return bool(self._values.get(name, False))
