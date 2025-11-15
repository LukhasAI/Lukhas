import asyncio
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from labs.consciousness.reflection.self_reflection_engine import (
    ContextProvider,
    ReflectionReport,
    SelfReflectionEngine,
    create_and_initialize_reflection_engine,
)
from labs.consciousness.systems.state import ConsciousnessState

# Mock for dependencies
mock_logger = MagicMock()

@pytest.fixture
def mock_otel(monkeypatch):
    """Fixture to mock OpenTelemetry modules."""
    monkeypatch.setenv("CONSC_REFLECTION_ENABLED", "1")
    mock_trace = MagicMock()
    mock_metrics = MagicMock()
    monkeypatch.setattr(
        "labs.consciousness.reflection.self_reflection_engine.trace", mock_trace
    )
    monkeypatch.setattr(
        "labs.consciousness.reflection.self_reflection_engine.metrics", mock_metrics
    )
    monkeypatch.setattr(
        "labs.consciousness.reflection.self_reflection_engine.OTEL_AVAILABLE", True
    )
    return mock_trace, mock_metrics


@pytest.fixture
def mock_consciousness_state():
    """Fixture for a mock ConsciousnessState."""
    state = MagicMock(spec=ConsciousnessState)
    state.level = 0.8
    state.awareness_type = "enhanced"
    state.emotional_tone = "positive"
    return state


@pytest.fixture
def engine(mock_otel):
    """Fixture for a SelfReflectionEngine instance."""
    with patch(
        "labs.consciousness.reflection.self_reflection_engine.get_logger",
        return_value=mock_logger,
    ):
        engine = SelfReflectionEngine()
        yield engine

@pytest.mark.asyncio
async def test_reflection_report_initialization():
    """Test ReflectionReport dataclass initialization."""
    report = ReflectionReport()
    assert report.schema_version == "1.0.0"
    assert report.coherence_score == 0.0
    assert report.anomaly_count == 0
    assert len(report.anomalies) == 0
    assert time.time() - report.timestamp < 1


@pytest.mark.asyncio
async def test_reflection_report_add_anomaly():
    """Test adding anomalies to a ReflectionReport."""
    report = ReflectionReport()
    report.add_anomaly("test_anomaly", "low", "A test anomaly occurred.")
    assert report.anomaly_count == 1
    assert len(report.anomalies) == 1
    anomaly = report.anomalies[0]
    assert anomaly["type"] == "test_anomaly"
    assert anomaly["severity"] == "low"
    assert anomaly["details"] == "A test anomaly occurred."


@pytest.mark.asyncio
async def test_engine_initialization_and_shutdown(engine):
    """Test engine initialization and shutdown."""
    assert not engine.is_initialized
    assert engine.status == "inactive"

    class MockContextProvider(ContextProvider):
        async def get_context(self):
            return {"test_context": "value"}

    providers = [MockContextProvider()]
    initialized = await engine.init(providers)

    assert initialized
    assert engine.is_initialized
    assert engine.status == "active"
    assert len(engine.context_providers) == 1

    await engine.shutdown()
    assert not engine.is_initialized
    assert engine.status == "inactive"
    assert len(engine.context_providers) == 0


@pytest.mark.asyncio
async def test_engine_disabled_by_flag(mock_otel, monkeypatch):
    """Test that the engine can be disabled with a feature flag."""
    monkeypatch.setattr(
        "labs.consciousness.reflection.self_reflection_engine.REFLECTION_ENABLED", False
    )
    engine = SelfReflectionEngine()
    initialized = await engine.init([])
    assert initialized
    assert engine.status == "disabled"

    state = MagicMock(spec=ConsciousnessState)
    report = await engine.reflect(state)
    assert report.anomaly_count == 1
    assert report.anomalies[0]["details"] == "Engine not initialized"


@pytest.mark.asyncio
async def test_reflection_cycle(engine, mock_consciousness_state):
    """Test a single reflection cycle."""
    await engine.init([])
    report = await engine.reflect(mock_consciousness_state)

    assert isinstance(report, ReflectionReport)
    assert report.coherence_score == 1.0  # First reflection
    assert report.reflection_duration_ms > 0
    assert report.anomaly_count == 0


@pytest.mark.asyncio
async def test_coherence_and_drift_calculation(engine, mock_consciousness_state):
    """Test coherence score and drift EMA calculation."""
    await engine.init([])

    # First reflection
    await engine.reflect(mock_consciousness_state)

    # Second reflection with a small change
    next_state = MagicMock(spec=ConsciousnessState)
    next_state.level = 0.82
    next_state.awareness_type = "enhanced"
    next_state.emotional_tone = "positive"

    report = await engine.reflect(next_state)

    assert 0.9 < report.coherence_score < 1.0
    assert report.drift_ema > 0
    assert report.state_delta_magnitude == pytest.approx(0.02)


@pytest.mark.asyncio
async def test_anomaly_detection_low_coherence(engine, mock_consciousness_state):
    """Test anomaly detection for low coherence."""
    await engine.init([])
    await engine.reflect(mock_consciousness_state)

    # A large state change to trigger low coherence
    next_state = MagicMock(spec=ConsciousnessState)
    next_state.level = 0.2
    next_state.awareness_type = "basic"
    next_state.emotional_tone = "negative"

    report = await engine.reflect(next_state)

    assert report.anomaly_count > 0
    assert any(a["type"] == "low_coherence" for a in report.anomalies)


@pytest.mark.asyncio
async def test_anomaly_detection_invalid_state(engine, mock_consciousness_state):
    """Test anomaly detection for invalid consciousness level."""
    await engine.init([])
    # First, establish a baseline state
    await engine.reflect(mock_consciousness_state)

    invalid_state = MagicMock(spec=ConsciousnessState)
    invalid_state.level = 1.5  # Invalid level
    invalid_state.awareness_type = "enhanced"
    invalid_state.emotional_tone = "positive"

    report = await engine.reflect(invalid_state)

    assert report.anomaly_count > 0
    assert any(a["type"] == "invalid_consciousness_level" for a in report.anomalies)


@pytest.mark.asyncio
async def test_context_provider_integration(engine, mock_consciousness_state):
    """Test that context providers are called and data is gathered."""
    mock_provider = AsyncMock(spec=ContextProvider)
    mock_provider.get_context.return_value = {"custom_metric": 42}

    await engine.init([mock_provider])
    await engine.reflect(mock_consciousness_state)

    mock_provider.get_context.assert_awaited_once()


@pytest.mark.asyncio
async def test_performance_metrics_tracking(engine, mock_consciousness_state):
    """Test that performance metrics are tracked correctly."""
    await engine.init([])

    for _ in range(5):
        await engine.reflect(mock_consciousness_state)

    stats = engine.get_performance_stats()
    assert stats["sample_count"] == 5
    assert stats["mean_latency_ms"] > 0
    assert "p95_latency_ms" in stats


@pytest.mark.asyncio
async def test_create_and_initialize_reflection_engine_factory():
    """Test the factory function for creating and initializing an engine."""
    with patch("labs.consciousness.reflection.self_reflection_engine.SelfReflectionEngine") as mock_engine_cls:
        mock_engine_instance = AsyncMock()
        mock_engine_cls.return_value = mock_engine_instance

        providers = [AsyncMock(spec=ContextProvider)]
        engine = await create_and_initialize_reflection_engine(context_providers=providers)

        mock_engine_cls.assert_called_once()
        mock_engine_instance.init.assert_awaited_once_with(providers)
        assert engine is mock_engine_instance

@pytest.mark.asyncio
async def test_validation_logic(engine, mock_consciousness_state):
    """Test the validation logic for performance compliance."""
    await engine.init([])

    # Simulate some reflections to populate performance buffer
    for i in range(10):
        # Alternate between fast and slow reflections
        duration = 1 if i % 2 == 0 else 15
        with patch("time.perf_counter", side_effect=[time.perf_counter(), time.perf_counter() + duration / 1000]):
            await engine.reflect(mock_consciousness_state)

    # With slow reflections, validation should fail
    is_valid = await engine.validate()
    assert not is_valid

    # Now, simulate only fast reflections
    engine.performance_buffer.clear()
    for _ in range(10):
        with patch("time.perf_counter", side_effect=[time.perf_counter(), time.perf_counter() + 0.001]):
            await engine.reflect(mock_consciousness_state)

    # With fast reflections, validation should pass
    is_valid_fast = await engine.validate()
    assert is_valid_fast