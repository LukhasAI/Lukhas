"""Bridge for candidate.aka_qualia.observability."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "labs.candidate.aka_qualia.observability",
    "lukhas_website.lukhas.aka_qualia.observability",
    "aka_qualia.observability",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class ObservabilityDashboard:  # type: ignore[misc]
    def render(self):
        return "observability"
