"""Optional OpenTelemetry compatibility layer.

If OTEL is unavailable, provide harmless no-ops so importers can proceed.
"""
from __future__ import annotations

__all__ = ["trace", "metrics"]

try:
    from opentelemetry import metrics, trace  # type: ignore
except Exception:
    class _NoOp:
        def __getattr__(self, _): return self
        def __call__(self, *_, **__): return self
        def __enter__(self): return self
        def __exit__(self, *_, **__): pass
    trace = metrics = _NoOp()  # type: ignore[assignment]
