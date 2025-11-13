
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# We import the class and the module separately to handle patching correctly
from labs.consciousness.reflection import self_reflection_engine
from labs.consciousness.reflection.self_reflection_engine import (
    ReflectionReport,
    SelfReflectionEngine,
    create_and_initialize_reflection_engine,
    create_reflection_engine,
)

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


# Mock/Dummy classes for testing dependencies
class MockConsciousnessState:
    def __init__(self, level=0.5, awareness_type="basic", emotional_tone="neutral"):
        self.level = level
        self.awareness_type = awareness_type
        self.emotional_tone = emotional_tone

class MockContextProvider:
    def __init__(self, context_data=None, should_fail=False):
        self._context_data = context_data or {}
        self._should_fail = should_fail

    async def get_context(self):
        if self._should_fail:
            raise ValueError("Mock context provider failed")
        return self._context_data


@pytest.fixture
def engine():
    """Provides a fresh instance of SelfReflectionEngine for each test."""
    return SelfReflectionEngine(config={"test_mode": True})


@pytest.fixture
def mock_otel():
    """Fixture to mock OpenTelemetry modules."""
    if self_reflection_engine.OTEL_AVAILABLE:
        with patch('labs.consciousness.reflection.self_reflection_engine.trace') as mock_trace, \
             patch('labs.consciousness.reflection.self_reflection_engine.get_meter') as mock_get_meter:

            mock_tracer = MagicMock()
            mock_trace.get_tracer.return_value = mock_tracer

            mock_meter = MagicMock()
            mock_get_meter.return_value = mock_meter

            mock_meter.create_histogram.return_value = MagicMock()
            mock_meter.create_counter.return_value = MagicMock()
            mock_meter.create_gauge.return_value = MagicMock()

            yield {
                "trace": mock_trace,
                "get_meter": mock_get_meter,
                "tracer": mock_tracer,
                "meter": mock_meter,
            }
    else:
        yield None


class TestSelfReflectionEngine:
    """Comprehensive tests for the SelfReflectionEngine."""

    async def test_initialization_success(self, engine):
        """Test successful initialization."""
        providers = [MockContextProvider()]
        result = await engine.init(context_providers=providers)
        assert result is True
        assert engine.is_initialized is True
        assert engine.status == "active"
        assert len(engine.context_providers) == 1

    @patch('labs.consciousness.reflection.self_reflection_engine.REFLECTION_ENABLED', False)
    async def test_initialization_with_reflection_disabled(self):
        """Test initialization when the feature flag disables reflection."""
        engine_disabled = SelfReflectionEngine()
        result = await engine_disabled.init([])
        assert result is True
        assert engine_disabled.status == "disabled"
        assert not engine_disabled.is_initialized

    async def test_reflect_when_not_initialized(self, engine):
        """Test that reflect returns an error report if the engine is not initialized."""
        state = MockConsciousnessState()
        report = await engine.reflect(state)
        assert isinstance(report, ReflectionReport)
        assert report.anomaly_count == 1
        assert report.anomalies[0]["type"] == "engine_error"

    async def test_first_reflection(self, engine):
        """Test the first reflection cycle."""
        await engine.init([])
        state = MockConsciousnessState(level=0.7)
        report = await engine.reflect(state)

        assert report.coherence_score == 1.0
        assert report.drift_ema == 0.0
        assert engine.previous_state is state

    async def test_subsequent_reflection_and_coherence(self, engine):
        """Test a second reflection cycle to check delta and coherence."""
        await engine.init([])
        await engine.reflect(MockConsciousnessState(level=0.7))
        report = await engine.reflect(MockConsciousnessState(level=0.72))

        assert report.state_delta_magnitude == pytest.approx(0.02)
        assert report.coherence_score > 0.95

    async def test_low_coherence_anomaly(self, engine):
        """Test that a large state change triggers a low coherence anomaly."""
        await engine.init([])
        await engine.reflect(MockConsciousnessState(level=0.5))
        report = await engine.reflect(MockConsciousnessState(level=0.9, awareness_type="different"))

        assert report.coherence_score < 0.85
        assert any(a["type"] == "low_coherence" for a in report.anomalies)

    async def test_gather_context_from_providers(self, engine):
        """Test that context is correctly gathered from multiple providers."""
        providers = [
            MockContextProvider({"source1": "data1"}),
            MockContextProvider({"source2": "data2"}),
            MockContextProvider(should_fail=True)
        ]
        await engine.init(providers)
        context = await engine._gather_context()
        assert context == {"source1": "data1", "source2": "data2"}

    async def test_performance_stats_and_validation(self, engine):
        """Test performance tracking and validation."""
        await engine.init([])
        for _ in range(20):
            with patch("time.perf_counter", side_effect=[0, 0.005]): # 5ms
                await engine.reflect(MockConsciousnessState())

        assert (await engine.validate()) is True
        stats = engine.get_performance_stats()
        assert stats["within_slo"] is True

        for _ in range(10):
            with patch("time.perf_counter", side_effect=[0, 0.015]): # 15ms
                await engine.reflect(MockConsciousnessState())

        assert (await engine.validate()) is False

    async def test_get_status_and_shutdown(self, engine):
        """Test the get_status and shutdown methods."""
        await engine.init([])
        await engine.reflect(MockConsciousnessState())

        status = engine.get_status()
        assert status["status"] == "active"

        await engine.shutdown()

        assert engine.status == "inactive"
        assert not engine.is_initialized

    def test_factory_create_reflection_engine(self):
        """Test the synchronous factory."""
        engine = create_reflection_engine(config={"id": 1})
        assert isinstance(engine, SelfReflectionEngine)
        assert engine.config == {"id": 1}

    async def test_factory_create_and_initialize_reflection_engine(self):
        """Test the asynchronous factory."""
        engine = await create_and_initialize_reflection_engine(
            config={"id": 2},
            context_providers=[MockContextProvider()]
        )
        assert isinstance(engine, SelfReflectionEngine)
        assert engine.is_initialized is True

    async def test_observability_metrics_recording(self, engine, mock_otel):
        """Test that metrics are recorded via OpenTelemetry mocks."""
        if not mock_otel:
            pytest.skip("OpenTelemetry not available.")

        await engine.init([])
        with patch("time.perf_counter", side_effect=[0, 0.007]):
            await engine.reflect(MockConsciousnessState())

        mock_otel["meter"].create_histogram.return_value.record.assert_called_once()
        mock_otel["meter"].create_counter.return_value.add.assert_not_called()
        mock_otel["meter"].create_gauge.return_value.set.assert_called_once()

        await engine.reflect(MockConsciousnessState(level=0.1))
        await engine.reflect(MockConsciousnessState(level=0.9))

        assert mock_otel["meter"].create_counter.return_value.add.call_count > 0

    @patch('labs.consciousness.reflection.self_reflection_engine.OTEL_AVAILABLE', False)
    async def test_observability_disabled_graceful_failure(self):
        """Test that the engine runs without error when OTEL is not available."""
        engine_no_otel = SelfReflectionEngine()
        await engine_no_otel.init([])
        report = await engine_no_otel.reflect(MockConsciousnessState())
        assert report is not None
        assert engine_no_otel.tracer is None
