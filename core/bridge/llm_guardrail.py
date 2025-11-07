"""Safe LLM invocation wrapper with schema validation."""
from __future__ import annotations

import logging
import os
import time
from statistics import quantiles
from typing import Any, Callable, Dict

from jsonschema import Draft7Validator, ValidationError
from jsonschema.exceptions import SchemaError

# ΛTAG: guardrail
_logger = logging.getLogger(__name__)

_LLM_CALLABLE: Callable[[str], dict[str, Any]] | None = None
_metrics = {
    "attempts": 0,
    "successes": 0,
    "denials": 0,
    "latencies": [],
}


def register_llm_callable(func: Callable[[str], dict[str, Any]]) -> None:
    """Register an injectable callable used to obtain candidate model output."""
    global _LLM_CALLABLE
    _logger.debug("ΛTRACE: registering custom LLM callable %s", func)
    _LLM_CALLABLE = func


def _invoke_llm(prompt: str) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        if _LLM_CALLABLE is None:
            _logger.info("ΛTRACE: Default guardrail stub invoked; returning sentinel payload.")
            # ✅ TODO: wire real LLM client once approved for candidate lane.
            return {"_rejected": True, "reason": "stub"}
        return _LLM_CALLABLE(prompt)
    finally:
        _metrics["latencies"].append(time.perf_counter() - start)


def _schema_is_valid(schema: dict[str, Any]) -> bool:
    try:
        Draft7Validator.check_schema(schema)
    except SchemaError as exc:
        _logger.warning("ΛTRACE: Guardrail schema invalid - %s", exc)
        return False
    return True


def _should_guard() -> bool:
    return os.getenv("ENABLE_LLM_GUARDRAIL", "1") == "1"


def call_llm(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    """Call the guarded LLM and enforce JSON Schema compliance."""
    _metrics["attempts"] += 1

    if not _schema_is_valid(schema):
        _metrics["denials"] += 1
        return {"_rejected": True, "reason": "schema"}

    if not _should_guard():
        _logger.info("ΛTRACE: Guardrail disabled via environment; delegating call.")
        payload = _invoke_llm(prompt)
        _metrics["successes"] += 1
        return payload

    candidate = _invoke_llm(prompt)
    try:
        Draft7Validator(schema).validate(candidate)
    except ValidationError as exc:
        _logger.warning("ΛTRACE: Candidate payload rejected - %s", exc.message)
        _metrics["denials"] += 1
        rejection = {"_rejected": True, "reason": "schema", "details": exc.message}
        return rejection

    _metrics["successes"] += 1
    _logger.info("ΛTRACE: Guardrail passed for prompt hash=%s", hash(prompt))
    return candidate


def get_guardrail_metrics() -> dict[str, Any]:
    """Return an immutable snapshot of guardrail counters and latency p95."""
    latencies = list(_metrics["latencies"])
    if len(latencies) >= 20:
        p95 = quantiles(latencies, n=20)[-1]
    elif latencies:
        p95 = max(latencies)
    else:
        p95 = 0.0
    snapshot = {
        "attempts": _metrics["attempts"],
        "successes": _metrics["successes"],
        "denials": _metrics["denials"],
        "p95_latency": p95,
    }
    return snapshot
