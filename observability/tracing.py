"""
OpenTelemetry helpers for LUKHAS MATRIZ pipeline.
Use spanify() to wrap each stage with automatic exception recording.
"""
from contextlib import contextmanager
from typing import Any, Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Span

tracer = trace.get_tracer("lukhas.matriz")


@contextmanager
def spanify(module: str, op: str, **attrs: Any):
    """
    Create a named span with automatic exception recording.

    Args:
        module: Module name (e.g., "Memory", "Intent", "Guardian")
        op: Operation name (e.g., "retrieve", "analyze", "validate")
        **attrs: Additional span attributes

    Yields:
        Span: Active OpenTelemetry span

    Example:
        with spanify("Memory", "retrieve", fold_count=950) as span:
            memories = retrieve_relevant_memories()
            span.set_attribute("results_count", len(memories))
    """
    span_name = f"{module}.{op}"
    with tracer.start_as_current_span(span_name) as span:
        # Set provided attributes
        for k, v in attrs.items():
            try:
                # Only set JSON-serializable values
                if isinstance(v, (str, int, float, bool)):
                    span.set_attribute(str(k), v)
                else:
                    span.set_attribute(str(k), str(v))
            except Exception:
                # Never fail operation due to telemetry
                pass

        try:
            yield span
        except Exception as e:
            # Record exception on span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


@contextmanager
def matriz_stage(stage_name: str, **attrs: Any):
    """
    Convenience wrapper for MATRIZ pipeline stages.

    Args:
        stage_name: One of Memory, Attention, Thought, Risk, Intent, Action, Zen
        **attrs: Additional span attributes

    Example:
        with matriz_stage("Memory", user_id="user_123"):
            memories = memory_retrieval()
    """
    with spanify("MATRIZ", stage_name.lower(), **attrs) as span:
        yield span


def set_trace_metadata(trace_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None):
    """
    Set metadata on current trace.

    Args:
        trace_id: Unique trace identifier
        user_id: Optional user identifier
        session_id: Optional session identifier
    """
    current_span = trace.get_current_span()
    if current_span:
        current_span.set_attribute("trace.id", trace_id)
        if user_id:
            current_span.set_attribute("user.id", user_id)
        if session_id:
            current_span.set_attribute("session.id", session_id)
