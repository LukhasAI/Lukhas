import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from candidate.consciousness.resilience.circuit_breaker_framework import (
    CircuitBreakerConfig,
    CircuitBreakerState,
    MemoryCascadePreventionBreaker,
    MemoryCascadeRiskError,
)

pytestmark = pytest.mark.asyncio


async def _success_op():
    return {"status": "ok"}


async def _slow_fail_op(delay: float, msg: str):
    await asyncio.sleep(delay)
    raise RuntimeError(msg)


async def _fail_cascade_op():
    raise MemoryCascadeRiskError("cascade triggered")


@pytest.mark.timeout(2)
async def test_circuit_breaker_transitions_open_halfopen_closed(monkeypatch):
    cfg = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout_duration=0.01,
        monitoring_window=3,
    )
    br = MemoryCascadePreventionBreaker(cfg)

    # Ensure pre-check passes by lowering cascade probability
    monkeypatch.setattr(br, "_estimate_cascade_probability", lambda *a, **k: 0.0)

    # 1) Trigger immediate trip via cascade failure
    with pytest.raises(MemoryCascadeRiskError):
        await br.execute(_fail_cascade_op)
    assert br.state == CircuitBreakerState.OPEN

    # 2) While open and before timeout, request is blocked and fallback is returned
    res = await br.execute(_success_op)
    assert isinstance(res, dict) and res.get("degraded_service") is True

    # 3) Fast-forward timeout to allow half-open transition
    br.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=br.current_timeout_duration + 0.01)

    # First successful request in half-open
    out1 = await br.execute(_success_op)
    assert out1["status"] == "ok"
    assert br.state in (CircuitBreakerState.HALF_OPEN, CircuitBreakerState.CLOSED)

    # Second successful request should close the breaker
    out2 = await br.execute(_success_op)
    assert out2["status"] == "ok"
    assert br.state == CircuitBreakerState.CLOSED


@pytest.mark.timeout(2)
async def test_circuit_breaker_response_time_threshold_trips(monkeypatch):
    cfg = CircuitBreakerConfig(
        response_time_threshold=0.001,  # 1ms
        failure_threshold=5,
        timeout_duration=0.01,
    )
    br = MemoryCascadePreventionBreaker(cfg)
    monkeypatch.setattr(br, "_estimate_cascade_probability", lambda *a, **k: 0.0)

    # Operation sleeps longer than threshold then raises (to route through failure logic)
    with pytest.raises(RuntimeError):
        await br.execute(lambda: _slow_fail_op(0.01, "slow path"))

    assert br.state == CircuitBreakerState.OPEN


@pytest.mark.timeout(2)
async def test_circuit_breaker_failure_threshold_trips(monkeypatch):
    cfg = CircuitBreakerConfig(
        failure_threshold=2,  # Trip after 2 failures
        timeout_duration=0.01,
    )
    br = MemoryCascadePreventionBreaker(cfg)
    monkeypatch.setattr(br, "_estimate_cascade_probability", lambda *a, **k: 0.0)

    async def _fail():
        raise RuntimeError("generic error")

    # First failure
    with pytest.raises(RuntimeError):
        await br.execute(_fail)
    assert br.state == CircuitBreakerState.CLOSED

    # Second failure triggers open via failure_threshold
    with pytest.raises(RuntimeError):
        await br.execute(_fail)
    assert br.state == CircuitBreakerState.OPEN
