import pytest
from labs.consciousness.awareness.awareness_engine import AwarenessEngine

# ΛTAG: awareness_setup_test


@pytest.mark.asyncio
async def test_initialize_sets_baseline_metrics():
    """Test that initialization sets up consciousness state properly."""
    engine = AwarenessEngine(config={"custom_setting": "value"})
    result = await engine.initialize(user_id="tester")
    assert result is True
    assert engine.is_initialized is True
    assert engine.status == "active"
    assert hasattr(engine, "consciousness_state")
    assert "awareness_level" in engine.consciousness_state
    assert "attention_focus" in engine.consciousness_state


@pytest.mark.asyncio
async def test_initialize_defaults_consciousness_state():
    """Test that initialization creates default consciousness state."""
    engine = AwarenessEngine()
    await engine.initialize()
    assert engine.consciousness_state is not None
    # After calibration, awareness_level defaults to 0.5 (neutral awareness)
    assert engine.consciousness_state["awareness_level"] == 0.5
    assert isinstance(engine.consciousness_state["attention_focus"], list)


@pytest.mark.asyncio
async def test_validate_confirms_active_component():
    """Test that validate confirms initialized component is healthy."""
    engine = AwarenessEngine()
    await engine.initialize(user_id="validator")

    assert await engine.validate(user_id="validator") is True


@pytest.mark.asyncio
async def test_validate_detects_uninitialized_component():
    """Test that validate detects uninitialized component."""
    engine = AwarenessEngine()
    # Don't initialize
    assert await engine.validate() is False


@pytest.mark.asyncio
async def test_get_status_returns_component_info():
    """Test that get_status returns proper component information."""
    engine = AwarenessEngine(user_id_context="test_user")
    await engine.initialize()

    status = engine.get_status()
    assert "component_name" in status
    assert status["component_name"] == "AwarenessEngine"
    assert "current_status" in status
    assert status["current_status"] == "active"
