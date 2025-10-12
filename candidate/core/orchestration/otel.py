# candidate/core/orchestration/otel.py
"""
OTel span helper. Falls back to no-op if opentelemetry not installed.
"""

from __future__ import annotations

from contextlib import contextmanager

try:
    from opentelemetry import trace  # type: ignore
    _TRACER = trace.get_tracer("lukhas.matriz")
except Exception:  # pragma: no cover
    _TRACER = None


@contextmanager
def stage_span(name: str, **attrs):
    if _TRACER is None:
        yield None
        return
    with _TRACER.start_as_current_span(f"matriz.{name}") as sp:
        for k, v in attrs.items():
            try:
                sp.set_attribute(f"matriz.{k}", v)
            except Exception:
                pass
        yield sp