"""Tombstone stores bridge with graceful stubs."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.memory.tombstones",
    "candidate.memory.tombstones",
    "memory.tombstones",
)

_backend: ModuleType | None = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:  # pragma: no cover - best effort bridge
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)
else:

    class FileTombstoneStore:
        """Fallback file-based tombstone registry."""

        def __init__(self, path: str = ".tombstones"):
            self.path = path
            self._entries: set[str] = set()

        def add(self, key: str) -> None:
            self._entries.add(key)

        def has(self, key: str) -> bool:
            return key in self._entries

    class GDPRTombstone(FileTombstoneStore):
        """Fallback GDPR tombstone store inheriting file behaviour."""

    __all__ = ["FileTombstoneStore", "GDPRTombstone"]
