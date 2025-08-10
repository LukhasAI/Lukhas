"""Tests for dream repair loops triggered by sadness."""

from datetime import datetime

from consciousness.systems.dream_engine.dream_reflection_loop import (
    DreamReflectionConfig,
    DreamReflectionLoop,
    DreamState,
)


def _loop_with_state(sadness: float, threshold: float) -> DreamReflectionLoop:
    cfg = DreamReflectionConfig(sadness_repair_threshold=threshold)
    loop = DreamReflectionLoop(config=cfg, enable_logging=False)
    state = DreamState(
        dream_id="d1",
        content={"emotions": {"sadness": sadness}},
        timestamp=datetime.now(),
    )
    loop.current_dreams.append(state)
    return loop


def test_repair_injected_when_sadness_high():
    loop = _loop_with_state(0.8, 0.6)
    result = loop.synthesize_dream()
    assert result["dream"]["repair_injected"] is True


def test_repair_not_triggered_when_sadness_low():
    loop = _loop_with_state(0.4, 0.6)
    result = loop.synthesize_dream()
    assert result["dream"]["repair_injected"] is False
