from __future__ import annotations

import os
from contextlib import contextmanager

import pytest
from core.bridge.llm_guardrail import (
    call_llm,
    get_guardrail_metrics,
    register_llm_callable,
)


@contextmanager
def guardrail_env(enabled: str) -> None:
    previous = os.environ.get("ENABLE_LLM_GUARDRAIL")
    os.environ["ENABLE_LLM_GUARDRAIL"] = enabled
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("ENABLE_LLM_GUARDRAIL", None)
        else:
            os.environ["ENABLE_LLM_GUARDRAIL"] = previous


@pytest.fixture(autouse=True)
def _reset_guardrail_callable() -> None:
    register_llm_callable(lambda prompt: {"value": prompt})


def test_invalid_payload_rejected() -> None:
    """Guardrail rejects schema violations without downstream side effects."""
    register_llm_callable(lambda prompt: {"value": "bad"})
    schema = {"type": "object", "properties": {"value": {"type": "number"}}, "required": ["value"]}

    with guardrail_env("1"):
        response = call_llm("demo", schema)

    assert response["_rejected"] is True
    assert response["reason"] == "schema"
    metrics = get_guardrail_metrics()
    assert metrics["denials"] >= 1


def test_schema_invalid_short_circuits_llm() -> None:
    called = False

    def _llm(prompt: str):
        nonlocal called
        called = True
        return {"value": 1}

    register_llm_callable(_llm)
    bad_schema = {"type": "object", "properties": {"value": "not-a-schema"}}

    with guardrail_env("1"):
        response = call_llm("demo", bad_schema)

    assert response == {"_rejected": True, "reason": "schema"}
    assert called is False
