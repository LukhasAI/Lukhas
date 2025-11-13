"""
Distributed Tracing with OpenTelemetry.

Provides decorators and context propagation helpers for MATRIZ nodes and orchestrators.
This module safely handles cases where OpenTelemetry is not installed.
"""

from __future__ import annotations

from functools import wraps, lru_cache
from typing import Any, Callable

# Attempt to import OpenTelemetry modules.
@lru_cache(maxsize=1)
def is_otel_available() -> bool:
    """Checks if the OpenTelemetry SDK is installed and available."""
    try:
        import opentelemetry
        return True
    except ImportError:
        return False

# Import OTel modules dynamically for type hinting and functionality.
if is_otel_available():
    from opentelemetry import context, propagate, trace
    from opentelemetry.propagate.textmap import CarrierT, Setter, Getter
    from opentelemetry.trace import Tracer

    class DictGetter(Getter[CarrierT]):
        def get(self, carrier: CarrierT, key: str) -> list[str] | None:
            return [carrier.get(key)] if key in carrier else None
        def keys(self, carrier: CarrierT) -> list[str]:
            return list(carrier.keys())

    class DictSetter(Setter[CarrierT]):
        def set(self, carrier: CarrierT, key: str, value: str) -> None:
            carrier[key] = value

    _getter = DictGetter()
    _setter = DictSetter()
else:
    # Define dummy classes for type checking when OTel is not available.
    class _NoOpTracer:
        def start_as_current_span(self, *args, **kwargs):
            class _NoOpSpan:
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def set_attribute(self, key, value): pass
                def record_exception(self, exception): pass
                def set_status(self, status, description=None): pass
            return _NoOpSpan()
    Tracer = _NoOpTracer


def get_tracer(name: str = "lukhas.matriz") -> "Tracer":
    """Get a tracer instance. Returns a no-op tracer if OTel is unavailable."""
    if not is_otel_available():
        return _NoOpTracer()
    return trace.get_tracer(name)


def extract_context(carrier: dict) -> "context.Context" | None:
    """Extracts a trace context from a dictionary."""
    if not is_otel_available():
        return None
    return propagate.extract(carrier, getter=_getter)

def inject_context(carrier: dict, ctx: "context.Context" | None = None) -> None:
    """Injects the current trace context into a dictionary."""
    if not is_otel_available():
        return
    propagate.inject(carrier, context=ctx, setter=_setter)


def trace_node_process(func: Callable) -> Callable:
    """Decorator to automatically trace the `process` method of an ICognitiveNode."""
    @wraps(func)
    async def wrapper(self, ctx: dict[str, Any], *args, **kwargs) -> Any:
        if not is_otel_available():
            return await func(self, ctx, *args, **kwargs)

        # Import trace status codes here to avoid circular dependency issues at module level
        from opentelemetry.trace import StatusCode

        node_name = getattr(self, 'name', 'unnamed_node')
        tracer = get_tracer()
        parent_context = extract_context(ctx.get("_trace_context", {}))

        with tracer.start_as_current_span(f"matriz.node.{node_name}", context=parent_context) as span:
            span.set_attribute("matriz.node.name", node_name)
            if "query" in ctx:
                span.set_attribute("matriz.node.query", str(ctx["query"]))

            try:
                result = await func(self, ctx, *args, **kwargs)
                if isinstance(result, dict):
                    trace_context = {}
                    inject_context(trace_context)
                    result["_trace_context"] = trace_context
                span.set_status(StatusCode.OK)
                return result
            except Exception as e:
                span.set_status(StatusCode.ERROR, description=str(e))
                span.record_exception(e)
                raise
    return wrapper
