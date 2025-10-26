"""
LLM Guardrail Module

Provides safe LLM call wrapper with JSON schema validation.
Dark-merged module - present but unused by default until adapter PR lands.

Usage:
    from core.bridge.llm_guardrail import call_llm

    schema = {"type": "object", "properties": {"score": {"type": "number"}}}
    result = call_llm("Analyze this", schema=schema, llm=my_llm_func)
"""

import json
import logging
import os
import time
from typing import Any, Callable, Dict, Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None

try:  # pragma: no cover - optional dependency
    from prometheus_client import Counter, Histogram
except Exception:
    Counter = None  # type: ignore[assignment]
    Histogram = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)


class _NoopMetric:
    """Graceful fallback when Prometheus client is unavailable."""

    def labels(self, **_: Any) -> "_NoopMetric":  # - simple shim
        return self

    def inc(self, amount: float = 1.0) -> None:  # pragma: no cover - noop
        _ = amount

    def observe(self, value: float) -> None:  # pragma: no cover - noop
        _ = value


def _counter(name: str, description: str, labelnames: tuple[str, ...]) -> Any:
    if Counter is None:
        logger.warning(
            "Prometheus client unavailable for counter", extra={"metric": name}
        )
        return _NoopMetric()
    return Counter(name, description, labelnames=labelnames)


def _histogram(name: str, description: str, labelnames: tuple[str, ...]) -> Any:
    if Histogram is None:
        logger.warning(
            "Prometheus client unavailable for histogram", extra={"metric": name}
        )
        return _NoopMetric()
    return Histogram(
        name,
        description,
        labelnames=labelnames,
        buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0),
    )


# ΛTAG: observability_metrics
LLM_GUARDRAIL_ATTEMPTS = _counter(
    "llm_guardrail_attempt_total",
    "Number of LLM guardrail evaluation attempts",
    ("lane", "schema"),
)
LLM_GUARDRAIL_REJECTS = _counter(
    "llm_guardrail_reject_total",
    "Number of guardrail rejections",
    ("lane", "reason"),
)
LLM_GUARDRAIL_LATENCY = _histogram(
    "llm_guardrail_latency_seconds",
    "Latency of guardrail evaluation",
    ("lane",),
)


def call_llm(
    prompt: str,
    schema: Dict[str, Any],
    llm: Optional[Callable[[str], Dict[str, Any]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Safe LLM call with JSON schema validation.

    Args:
        prompt: Input prompt for the LLM
        schema: JSON schema to validate response against
        llm: LLM function that takes prompt and returns dict
        **kwargs: Additional arguments for the LLM

    Returns:
        Dict containing LLM response or rejection details

    Raises:
        Exception: If schema validation fails or other errors occur
    """
    start_time = time.time()
    lane = os.getenv("LUKHAS_LANE", "experimental")

    try:
        LLM_GUARDRAIL_ATTEMPTS.labels(lane=lane, schema=_schema_fingerprint(schema)).inc()

        # Check if guardrail is enabled
        if os.getenv("ENABLE_LLM_GUARDRAIL", "0") != "1":
            raise RuntimeError("LLM guardrail not enabled. Set ENABLE_LLM_GUARDRAIL=1")

        # Validate schema availability
        if jsonschema is None:
            raise ImportError("jsonschema package required for LLM guardrail")

        # Pre-validate schema
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except Exception as e:
            LLM_GUARDRAIL_REJECTS.labels(reason="invalid_schema", lane=lane).inc()
            raise ValueError(f"Invalid JSON schema: {e}")

        # Call LLM if provided
        if llm is None:
            # Stub response for testing
            response = {"_stub": True, "message": "LLM guardrail active"}
        else:
            response = llm(prompt, **kwargs)

        # Validate response against schema
        try:
            jsonschema.validate(response, schema)
        except jsonschema.ValidationError as e:
            LLM_GUARDRAIL_REJECTS.labels(reason="schema", lane=lane).inc()
            raise ValueError(f"LLM response failed schema validation: {e.message}")
        except Exception as e:
            LLM_GUARDRAIL_REJECTS.labels(reason="validation_error", lane=lane).inc()
            raise ValueError(f"Schema validation error: {e}")

        return response

    finally:
        duration = time.time() - start_time
        LLM_GUARDRAIL_LATENCY.labels(lane=lane).observe(duration)


def _schema_fingerprint(schema: Dict[str, Any]) -> str:
    """Create a stable fingerprint for schema metrics."""
    # Simple hash to avoid cardinality explosion
    schema_str = json.dumps(schema, sort_keys=True)
    return f"schema_{abs(hash(schema_str)) % 1000:03d}"


# Health check function
def guardrail_health() -> Dict[str, Any]:
    """Return guardrail health status."""
    return {
        "enabled": os.getenv("ENABLE_LLM_GUARDRAIL", "0") == "1",
        "jsonschema_available": jsonschema is not None,
        "lane": os.getenv("LUKHAS_LANE", "experimental"),
        "version": "1.0.0"
    }
