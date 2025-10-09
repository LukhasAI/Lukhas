"""Bridge for lukhas.observability.matriz_instrumentation."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.observability.matriz_instrumentation",
    "candidate.observability.matriz_instrumentation",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class MatrizObservability:  # type: ignore[misc]
    def record(self, metric: str, value: float):
        return {metric: value}
