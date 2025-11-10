from __future__ import annotations

# ΛTAG: observability_metrics_test
import pytest
from core.bridge import llm_guardrail

prom = pytest.importorskip("prometheus_client")


def test_llm_guardrail_metrics_are_real() -> None:
    assert isinstance(llm_guardrail.LLM_GUARDRAIL_ATTEMPTS, prom.Counter)
    assert isinstance(llm_guardrail.LLM_GUARDRAIL_REJECTS, prom.Counter)
    assert isinstance(llm_guardrail.LLM_GUARDRAIL_LATENCY, prom.Histogram)
