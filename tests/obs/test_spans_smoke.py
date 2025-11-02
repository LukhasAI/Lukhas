# tests/obs/test_spans_smoke.py
import contextlib
import importlib as _importlib

_mod = _importlib.import_module("labs.core.orchestration.otel")
stage_span = getattr(_mod, "stage_span")


def test_span_noop_ok():
    # Works even if opentelemetry is not installed
    with contextlib.ExitStack() as s:
        s.enter_context(stage_span("INTENT", node="dummy"))
