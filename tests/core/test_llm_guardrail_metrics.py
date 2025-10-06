from __future__ import annotations

import pytest

# ΛTAG: observability_metrics_test
prom = pytest.importorskip("prometheus_client")

from core.bridge import llm_guardrail


def test_llm_guardrail_metrics_are_real() -> None:
    assert isinstance(llm_guardrail.LLM_GUARDRAIL_ATTEMPTS, prom.Counter)
    assert isinstance(llm_guardrail.LLM_GUARDRAIL_REJECTS, prom.Counter)
    assert isinstance(llm_guardrail.LLM_GUARDRAIL_LATENCY, prom.Histogram)
