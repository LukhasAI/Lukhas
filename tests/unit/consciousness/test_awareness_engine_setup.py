import pytest

from candidate.consciousness.awareness.awareness_engine import AwarenessEngine

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
