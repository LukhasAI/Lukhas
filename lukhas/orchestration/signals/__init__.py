"""LUKHAS Orchestration Signals Module."""

from __future__ import annotations

from importlib import import_module

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.orchestration.signals",
    "labs.orchestration.signals",
    "orchestration.signals",
)

_backend = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)


if "DiagnosticSignalType" not in globals():
    from enum import Enum

    class DiagnosticSignalType(Enum):
        INFO = "info"
        WARNING = "warning"
        CRITICAL = "critical"

    __all__.append("DiagnosticSignalType")
