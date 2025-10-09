"""Bridge for lukhas.orchestration.context_bus."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.orchestration.context_bus",
    "orchestration.context_bus",
    "candidate.orchestration.context_bus",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class ContextBusOrchestrator:  # type: ignore[misc]
    def dispatch(self, message):
        return message
