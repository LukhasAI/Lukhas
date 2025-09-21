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
import os
import time
from typing import Dict, Any, Callable, Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None

# Telemetry counters (no-op for dark merge)
class TelemetryCounter:
    def __init__(self, name: str):
        self.name = name
        self.value = 0

    def labels(self, **kwargs):
        return self

    def inc(self):
        self.value += 1

    def observe(self, value: float):
        pass

# Metrics (stubbed for dark merge)
LLM_GUARDRAIL_ATTEMPTS = TelemetryCounter("llm_guardrail_attempt_total")
LLM_GUARDRAIL_REJECTS = TelemetryCounter("llm_guardrail_reject_total")
LLM_GUARDRAIL_LATENCY = TelemetryCounter("llm_guardrail_latency_seconds")


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