"""Bridge: observability.opentelemetry_tracing (no-op fallback if OTEL missing)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

try:
    __all__, _exp = bridge_from_candidates(
        "lukhas_website.observability.opentelemetry_tracing",
        "candidate.observability.opentelemetry_tracing",
        "observability.opentelemetry_tracing",
    )
    globals().update(_exp)
except Exception:
    # graceful no-op tracer
    __all__ = ["Tracer", "start_span"]

    class Tracer:
        def start_span(self, *_a, **_k):
            class _Span:
                def __enter__(self):
                    return self

                def __exit__(self, *exc):
                    return False

            return _Span()

    def start_span(*_a, **_k):
        return Tracer().start_span()
