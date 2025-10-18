import pytest

from consciousness.awareness.awareness_engine import AwarenessEngine

# ΛTAG: awareness_setup_test


@pytest.mark.asyncio
async def test_initialize_sets_baseline_metrics():
    engine = AwarenessEngine(config={"baseline_drift": 1.5, "baseline_affect": -0.2})
    result = await engine.initialize(user_id="tester")
    assert result is True
    assert engine.is_initialized is True
    assert engine.status == "active"
    assert engine.drift_score == 1.5
    assert engine.affect_delta == -0.2


@pytest.mark.asyncio
async def test_initialize_defaults_zero_metrics():
    engine = AwarenessEngine()
    await engine.initialize()
    assert engine.drift_score == 0.0
    assert engine.affect_delta == 0.0


@pytest.mark.asyncio
async def test_validate_confirms_active_metrics():
    engine = AwarenessEngine()
    await engine.initialize(user_id="validator")

    assert await engine.validate(user_id="validator") is True
    assert getattr(engine, "last_validation_snapshot", None)
    assert "metrics" in engine.last_validation_snapshot


@pytest.mark.asyncio
async def test_validate_detects_invalid_metric_values():
    engine = AwarenessEngine()
    await engine.initialize()

    engine.drift_score = float("nan")

    assert await engine.validate() is False


@pytest.mark.asyncio
async def test_validate_detects_unhealthy_dependencies():
    engine = AwarenessEngine(config={"dependencies": {"memory_bridge": True, "emotion_interface": False}})
    await engine.initialize()

    assert await engine.validate() is False
