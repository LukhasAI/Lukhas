"""Retention rule surface expected by tests."""

from __future__ import annotations

from enum import Enum
from importlib import import_module
from types import ModuleType
from typing import Any

__all__: list[str] = []

_CANDIDATES = (
    "labs.memory.retention",
    "memory.retention",
    "lukhas_website.memory.retention",
)

_backend: ModuleType | None = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:  # pragma: no cover
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)
else:

    class RetentionSeverity(Enum):
        """Fallback retention severity."""

        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class RetentionAction(Enum):
        """Fallback retention actions."""

        KEEP = "keep"
        ARCHIVE = "archive"
        PURGE = "purge"
        TOMBSTONE = "tombstone"

    class RetentionRule:
        """Fallback retention rule."""

        def __init__(self, name: str, severity: RetentionSeverity, action: RetentionAction):
            self.name = name
            self.severity = severity
            self.action = action

        def matches(self, doc: Any) -> bool:
            """Trivial matcher that looks for positive score."""
            return bool(getattr(doc, "score", 0) > 0)

    __all__ = ["RetentionAction", "RetentionRule", "RetentionSeverity"]

# --- retention aliases: ArchivalTier / AbstractArchivalBackend (safe append) ---
try:
    ArchivalTier
except NameError:
    from enum import Enum

    class ArchivalTier(Enum):
        HOT = "hot"
        WARM = "warm"
        COLD = "cold"
        GLACIAL = "glacial"

    __all__ = list(set(globals().get("__all__", []) or []) | {"ArchivalTier"})

try:
    AbstractArchivalBackend
except NameError:

    class AbstractArchivalBackend:
        """Minimal abstract backend surface."""

        def archive(self, doc: Any) -> None:  # pragma: no cover - fallback
            raise NotImplementedError

        def retrieve(self, doc_id: str) -> Any:
            raise NotImplementedError

        def tombstone(self, doc_id: str) -> None:
            raise NotImplementedError

    __all__ = list(set(globals().get("__all__", []) or []) | {"AbstractArchivalBackend"})
