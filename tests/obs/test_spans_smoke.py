# tests/obs/test_spans_smoke.py
import contextlib

from lukhas.core.orchestration.otel import stage_span


def test_span_noop_ok():
    # Works even if opentelemetry is not installed
    with contextlib.ExitStack() as s:
        s.enter_context(stage_span("INTENT", node="dummy"))
