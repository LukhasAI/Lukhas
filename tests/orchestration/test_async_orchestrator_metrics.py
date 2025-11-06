#!/usr/bin/env python3
"""
Metrics instrumentation tests for the async orchestrator.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

import pytest
from core.interfaces import CognitiveNodeBase
from core.registry import _REG, register
from labs.core.orchestration.async_orchestrator import AsyncOrchestrator
from prometheus_client import REGISTRY


def _collect_metric_value(metric_name: str, labels: Mapping[str, str], sample_suffix: str | None = "total") -> float:
    """Return the current metric sample value for the provided labels."""
    if sample_suffix is None or (metric_name.endswith("_total") and sample_suffix == "total"):
        target_sample = metric_name
    else:
        target_sample = f"{metric_name}_{sample_suffix}"
    candidate_names = {metric_name}
    if metric_name.endswith("_total"):
        candidate_names.add(metric_name[:-6])

    for metric in REGISTRY.collect():
        if metric.name not in candidate_names:
            continue
        for sample in metric.samples:
            if sample.name != target_sample:
                continue
            if all(sample.labels.get(key) == value for key, value in labels.items()):
                return float(sample.value)
    return 0.0


@pytest.fixture(autouse=True)
def restore_registry():
    """Ensure registry mutations do not leak between tests."""
    snapshot = dict(_REG)
    try:
        yield
    finally:
        _REG.clear()
        _REG.update(snapshot)


class _FastNode(CognitiveNodeBase):
    name = "metrics_success"

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        await asyncio.sleep(0)
        return {"status": "ok", "confidence": 0.9}


class _TimeoutNode(CognitiveNodeBase):
    name = "metrics_timeout"

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        await asyncio.sleep(0.05)
        return {"status": "slow"}


class _TransientFailure(Exception):
    transient = True


class _FlakyNode(CognitiveNodeBase):
    name = "metrics_flaky"

    def __init__(self) -> None:
        self._calls = 0

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        self._calls += 1
        if self._calls == 1:
            raise _TransientFailure("transient failure")
        return {"status": "recovered"}


def test_stage_duration_success_metric_increments():
    register("node:metrics_success", _FastNode())
    orchestrator = AsyncOrchestrator({"MATRIZ_ASYNC": "1"})
    orchestrator.configure_stages([
        {"name": "METRIC_SUCCESS", "timeout_ms": 80, "node": "metrics_success"}
    ])

    labels = {"stage": "METRIC_SUCCESS", "node": "metrics_success", "outcome": "success"}
    before = _collect_metric_value("mtrx_stage_duration_seconds", labels, sample_suffix="count")

    result = asyncio.run(orchestrator.process_query({"query": "ping"}))

    after = _collect_metric_value("mtrx_stage_duration_seconds", labels, sample_suffix="count")

    assert result.success is True
    assert after == pytest.approx(before + 1)


def test_timeout_metrics_emit_failure_and_circuit_breaker():
    register("node:metrics_timeout", _TimeoutNode())
    orchestrator = AsyncOrchestrator({"MATRIZ_ASYNC": "1"})
    orchestrator.configure_stages([
        {
            "name": "METRIC_TIMEOUT",
            "timeout_ms": 10,
            "max_retries": 1,
            "node": "metrics_timeout",
            "backoff_base_ms": 5,
        }
    ])

    hist_labels = {"stage": "METRIC_TIMEOUT", "node": "metrics_timeout", "outcome": "failure"}
    timeout_labels = {"stage": "METRIC_TIMEOUT"}
    circuit_labels = {"stage": "METRIC_TIMEOUT", "node": "metrics_timeout"}

    before_hist = _collect_metric_value("mtrx_stage_duration_seconds", hist_labels, sample_suffix="count")
    before_timeouts = _collect_metric_value("mtrx_orch_timeout_total", timeout_labels)
    before_circuit = _collect_metric_value("mtrx_orch_circuit_open_total", circuit_labels)

    result = asyncio.run(orchestrator.process_query({"query": "slow"}))

    after_hist = _collect_metric_value("mtrx_stage_duration_seconds", hist_labels, sample_suffix="count")
    after_timeouts = _collect_metric_value("mtrx_orch_timeout_total", timeout_labels)
    after_circuit = _collect_metric_value("mtrx_orch_circuit_open_total", circuit_labels)

    assert result.output.get("action") == "timeout"
    assert after_hist == pytest.approx(before_hist + 1)
    assert after_timeouts == pytest.approx(before_timeouts + 1)
    assert after_circuit == pytest.approx(before_circuit + 1)


def test_retry_metric_increments_on_transient_failure():
    register("node:metrics_flaky", _FlakyNode())
    orchestrator = AsyncOrchestrator({"MATRIZ_ASYNC": "1"})
    orchestrator.configure_stages([
        {
            "name": "METRIC_RETRY",
            "timeout_ms": 100,
            "max_retries": 3,
            "backoff_base_ms": 5,
            "node": "metrics_flaky",
        }
    ])

    retry_labels = {"stage": "METRIC_RETRY", "reason": "_TransientFailure"}
    before = _collect_metric_value("mtrx_orch_retry_total", retry_labels)

    result = asyncio.run(orchestrator.process_query({"query": "unstable"}))

    after = _collect_metric_value("mtrx_orch_retry_total", retry_labels)

    assert result.success is True
    assert after == pytest.approx(before + 1)
