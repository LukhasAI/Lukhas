#!/usr/bin/env python3
"""
Tests for MATRIZ Cognitive Pipeline Observability Integration

Tests comprehensive observability functionality including:
- Cognitive stage instrumentation
- Memory cascade risk detection
- Focus drift monitoring
- Thought complexity tracking
- Decision confidence measurement
- Anomaly detection
- Performance metrics
- SLO compliance
"""

import asyncio
import time
from typing import Any
from unittest.mock import Mock, patch

import pytest
from core.matriz.optimized_orchestrator import OptimizedAsyncOrchestrator
from observability.matriz_instrumentation import (
    cognitive_pipeline_span,
    get_cognitive_instrumentation_status,
    initialize_cognitive_instrumentation,
    instrument_cognitive_stage,
    record_decision_confidence,
    record_focus_drift,
    record_memory_cascade_risk,
    record_thought_complexity,
)
from observability.otel_instrumentation import instrument_cognitive_event


class TestCognitiveInstrumentationInitialization:
    """Test initialization and configuration of cognitive instrumentation"""

    def test_initialization_success(self):
        """Test successful initialization of cognitive instrumentation"""
        with patch('observability.matriz_instrumentation.OTEL_AVAILABLE', True), \
             patch('observability.matriz_instrumentation._metrics_initialized', True):

            result = initialize_cognitive_instrumentation(enable_metrics=True)
            assert result is True

            status = get_cognitive_instrumentation_status()
            assert status["cognitive_initialized"] is True

    def test_initialization_failure_no_otel(self):
        """Test initialization failure when OTel is not available"""
        with patch('observability.matriz_instrumentation.OTEL_AVAILABLE', False):
            result = initialize_cognitive_instrumentation(enable_metrics=True)
            assert result is False

            status = get_cognitive_instrumentation_status()
            assert status["cognitive_initialized"] is False

    def test_initialization_failure_no_base_metrics(self):
        """Test initialization failure when base metrics are not initialized"""
        with patch('observability.matriz_instrumentation.OTEL_AVAILABLE', True), \
             patch('observability.matriz_instrumentation._metrics_initialized', False):

            result = initialize_cognitive_instrumentation(enable_metrics=True)
            assert result is False


class TestCognitiveStageInstrumentation:
    """Test cognitive stage instrumentation decorators and metrics"""

    @pytest.fixture
    def mock_cognitive_metrics(self):
        """Mock cognitive metrics for testing"""
        with patch('observability.matriz_instrumentation._cognitive_initialized', True), \
             patch('observability.matriz_instrumentation._cognitive_metrics') as mock_metrics:

            # Mock all metric objects
            mock_metrics.stage_duration_histogram = Mock()
            mock_metrics.stage_events_counter = Mock()
            mock_metrics.focus_drift_gauge = Mock()
            mock_metrics.memory_cascade_risk_gauge = Mock()
            mock_metrics.thought_complexity_gauge = Mock()
            mock_metrics.decision_confidence_gauge = Mock()
            mock_metrics.anomaly_detection_counter = Mock()

            yield mock_metrics

    def test_cognitive_stage_decorator_success(self, mock_cognitive_metrics):
        """Test successful cognitive stage decoration"""
        @instrument_cognitive_stage("memory", node_id="test_node", slo_target_ms=50.0)
        def test_function(data: str):
            time.sleep(0.01)  # Simulate processing time
            return {"result": "processed", "confidence": 0.8}

        result = test_function("test data")

        assert result["result"] == "processed"
        assert result["confidence"] == 0.8

        # Verify metrics were recorded
        mock_cognitive_metrics.stage_duration_histogram.record.assert_called()
        mock_cognitive_metrics.stage_events_counter.add.assert_called()

    @pytest.mark.asyncio
    async def test_cognitive_stage_decorator_async(self, mock_cognitive_metrics):
        """Test cognitive stage decoration with async functions"""
        @instrument_cognitive_stage("thought", node_id="async_node", slo_target_ms=100.0)
        async def test_async_function(query: str):
            await asyncio.sleep(0.02)  # Simulate async processing
            return {"answer": "42", "reasoning_depth": 5}

        result = await test_async_function("what is the answer?")

        assert result["answer"] == "42"
        assert result["reasoning_depth"] == 5

        # Verify async execution was instrumented
        mock_cognitive_metrics.stage_duration_histogram.record.assert_called()

    def test_cognitive_stage_decorator_error_handling(self, mock_cognitive_metrics):
        """Test error handling in cognitive stage decoration"""
        @instrument_cognitive_stage("decision", node_id="error_node")
        def failing_function():
            raise ValueError("Simulated processing error")

        with pytest.raises(ValueError, match="Simulated processing error"):
            failing_function()

        # Verify error metrics were recorded
        mock_cognitive_metrics.stage_events_counter.add.assert_called()
        mock_cognitive_metrics.anomaly_detection_counter.add.assert_called()

    def test_cognitive_stage_slo_violation_detection(self, mock_cognitive_metrics):
        """Test SLO violation detection and anomaly recording"""
        @instrument_cognitive_stage("attention", node_id="slow_node", slo_target_ms=10.0, anomaly_detection=True)
        def slow_function():
            time.sleep(0.05)  # Exceed SLO target
            return {"result": "slow processing"}

        result = slow_function()

        assert result["result"] == "slow processing"

        # Verify anomaly was detected for SLO violation
        mock_cognitive_metrics.anomaly_detection_counter.add.assert_called()


class TestCognitivePipelineSpan:
    """Test cognitive pipeline span context manager"""

    @pytest.mark.asyncio
    async def test_pipeline_span_success(self):
        """Test successful pipeline span execution"""
        with patch('observability.matriz_instrumentation._cognitive_initialized', True), \
             patch('observability.matriz_instrumentation._tracer') as mock_tracer:

            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

            expected_stages = ["memory", "attention", "thought", "decision"]

            async with cognitive_pipeline_span(
                "test_pipeline",
                "test query",
                expected_stages=expected_stages,
                target_slo_ms=200.0
            ):
                await asyncio.sleep(0.01)  # Simulate pipeline processing

            # Verify span was created with correct attributes
            mock_tracer.start_as_current_span.assert_called()
            mock_span.set_attributes.assert_called()

    @pytest.mark.asyncio
    async def test_pipeline_span_error_handling(self):
        """Test pipeline span error handling"""
        with patch('observability.matriz_instrumentation._cognitive_initialized', True), \
             patch('observability.matriz_instrumentation._tracer') as mock_tracer:

            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

            with pytest.raises(RuntimeError, match="Pipeline simulation error"):
                async with cognitive_pipeline_span("error_pipeline", "error query"):
                    raise RuntimeError("Pipeline simulation error")

            # Verify error was recorded in span
            mock_span.set_status.assert_called()


class TestCognitiveMetricsRecording:
    """Test individual cognitive metrics recording functions"""

    @pytest.fixture
    def mock_metrics(self):
        """Mock cognitive metrics objects"""
        with patch('observability.matriz_instrumentation._cognitive_initialized', True), \
             patch('observability.matriz_instrumentation._cognitive_metrics') as mock_metrics:

            mock_metrics.focus_drift_gauge = Mock()
            mock_metrics.memory_cascade_risk_gauge = Mock()
            mock_metrics.thought_complexity_gauge = Mock()
            mock_metrics.decision_confidence_gauge = Mock()
            mock_metrics.reasoning_depth_histogram = Mock()
            mock_metrics.anomaly_detection_counter = Mock()

            yield mock_metrics

    def test_focus_drift_recording(self, mock_metrics):
        """Test focus drift metric recording"""
        attention_weights = [0.8, 0.7, 0.9, 0.6, 0.8]

        record_focus_drift("attention_node", attention_weights, window_size=5)

        # Verify focus drift gauge was updated
        mock_metrics.focus_drift_gauge.add.assert_called()

        # Test anomaly detection for high drift
        high_drift_weights = [0.9, 0.1, 0.8, 0.2, 0.7]  # High variance
        record_focus_drift("drift_node", high_drift_weights)

        # Verify anomaly was recorded
        mock_metrics.anomaly_detection_counter.add.assert_called()

    def test_memory_cascade_risk_recording(self, mock_metrics):
        """Test memory cascade risk metric recording"""
        # Normal memory usage
        record_memory_cascade_risk(fold_count=500, retrieval_depth=10, cascade_detected=False)
        mock_metrics.memory_cascade_risk_gauge.add.assert_called()

        # High risk scenario
        record_memory_cascade_risk(fold_count=950, retrieval_depth=25, cascade_detected=True)

        # Verify anomaly was recorded for high risk
        mock_metrics.anomaly_detection_counter.add.assert_called()

    def test_thought_complexity_recording(self, mock_metrics):
        """Test thought complexity metric recording"""
        # Normal complexity
        record_thought_complexity(reasoning_depth=5, logic_chains=2, inference_steps=15)
        mock_metrics.thought_complexity_gauge.add.assert_called()
        mock_metrics.reasoning_depth_histogram.record.assert_called()

        # High complexity scenario
        record_thought_complexity(reasoning_depth=20, logic_chains=10, inference_steps=200)

        # Verify anomaly was recorded for extreme complexity
        mock_metrics.anomaly_detection_counter.add.assert_called()

    def test_decision_confidence_recording(self, mock_metrics):
        """Test decision confidence metric recording"""
        # High confidence decision
        record_decision_confidence(confidence_score=0.9, decision_type="node_selection", node_id="decision_node")
        mock_metrics.decision_confidence_gauge.add.assert_called()

        # Low confidence decision
        record_decision_confidence(confidence_score=0.2, decision_type="critical_decision", node_id="low_conf_node")

        # Verify anomaly was recorded for low confidence
        mock_metrics.anomaly_detection_counter.add.assert_called()


class TestCognitiveEventInstrumentation:
    """Test cognitive event instrumentation (e.g., process_matriz_event)"""

    def test_cognitive_event_decorator_with_event_data(self):
        """Test cognitive event decoration with event data extraction"""
        @instrument_cognitive_event("process_matriz_event", slo_target_ms=100.0)
        def process_event(event: dict[str, Any]):
            # Simulate MATRIZ event processing
            stage = event.get('node_type', 'unknown').lower()
            node_id = event.get('id', 'unknown')

            return {
                "processed": True,
                "stage": stage,
                "node_id": node_id,
                "confidence": 0.8
            }

        # Test event data
        test_event = {
            "id": "test_node_123",
            "node_type": "MEMORY",
            "data": {"query": "test query"},
            "connections": ["node_456"],
            "timestamp": time.time(),
            "metadata": {"priority": "high"}
        }

        with patch('observability.otel_instrumentation._metrics_initialized', True), \
             patch('observability.otel_instrumentation._tracer') as mock_tracer:

            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

            result = process_event(test_event)

            assert result["processed"] is True
            assert result["stage"] == "memory"
            assert result["node_id"] == "test_node_123"

            # Verify span was created with cognitive context
            mock_tracer.start_as_current_span.assert_called()
            mock_span.set_attributes.assert_called()

    def test_cognitive_event_custom_node_id_extractor(self):
        """Test custom node ID extraction in cognitive event instrumentation"""
        def custom_extractor(event_data: dict) -> str:
            return f"custom_{event_data.get('uuid', 'unknown')}"

        @instrument_cognitive_event("custom_event", node_id_extractor=custom_extractor)
        def custom_event_processor(event: dict):
            return {"custom_processed": True}

        test_event = {"uuid": "abc123", "type": "custom"}

        with patch('observability.otel_instrumentation._metrics_initialized', True), \
             patch('observability.otel_instrumentation._tracer') as mock_tracer:

            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

            result = custom_event_processor(test_event)

            assert result["custom_processed"] is True

            # Verify custom node ID extraction was used
            call_args = mock_tracer.start_as_current_span.call_args
            attributes = call_args[1]["attributes"]
            assert attributes["matriz.event.node_id"] == "custom_abc123"


class TestOptimizedOrchestratorIntegration:
    """Test integration of cognitive observability with OptimizedAsyncOrchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create optimized orchestrator with cognitive instrumentation enabled"""
        with patch('observability.matriz_instrumentation.initialize_cognitive_instrumentation') as mock_init:
            mock_init.return_value = True

            orchestrator = OptimizedAsyncOrchestrator(
                cache_enabled=True,
                metrics_enabled=True,
                total_timeout=0.5
            )

            return orchestrator

    @pytest.mark.asyncio
    async def test_orchestrator_cognitive_pipeline_span(self, orchestrator):
        """Test that orchestrator uses cognitive pipeline spans"""
        with patch('observability.matriz_instrumentation.cognitive_pipeline_span') as mock_span:
            mock_span.return_value.__aenter__.return_value = Mock()
            mock_span.return_value.__aexit__.return_value = None

            # Mock the internal processing method
            with patch.object(orchestrator, '_process_query_with_observability') as mock_process:
                mock_process.return_value = {"answer": "test result", "metrics": {}}

                result = await orchestrator.process_query("test query")

                # Verify cognitive pipeline span was used
                mock_span.assert_called_once()
                assert "answer" in result

    def test_orchestrator_cognitive_stage_instrumentation(self, orchestrator):
        """Test that orchestrator methods are properly instrumented"""
        # Check that methods have been decorated
        assert hasattr(orchestrator._optimized_analyze_intent, '__wrapped__')
        assert hasattr(orchestrator._optimized_select_node, '__wrapped__')
        assert hasattr(orchestrator._optimized_process_node, '__wrapped__')

    @pytest.mark.asyncio
    async def test_orchestrator_cognitive_metrics_recording(self, orchestrator):
        """Test that orchestrator records cognitive metrics during processing"""
        with patch('observability.matriz_instrumentation.record_focus_drift'), \
             patch('observability.matriz_instrumentation.record_decision_confidence'), \
             patch('observability.matriz_instrumentation.record_thought_complexity'):

            # Mock successful processing
            with patch.object(orchestrator, '_process_query_with_observability') as mock_process:
                mock_process.return_value = {
                    "answer": "test answer",
                    "confidence": 0.9,
                    "metrics": {"total_duration_ms": 50}
                }

                result = await orchestrator.process_query("2 + 2 = ?")

                assert result["answer"] == "test answer"


class TestAnomalyDetection:
    """Test anomaly detection capabilities for 1-in-10,000 events"""

    @pytest.fixture
    def mock_metrics_with_anomaly(self):
        """Mock metrics with anomaly detection"""
        with patch('observability.matriz_instrumentation._cognitive_initialized', True), \
             patch('observability.matriz_instrumentation._cognitive_metrics') as mock_metrics:

            mock_metrics.anomaly_detection_counter = Mock()
            yield mock_metrics

    def test_performance_outlier_detection(self, mock_metrics_with_anomaly):
        """Test detection of performance outliers"""
        @instrument_cognitive_stage("memory", node_id="outlier_test", slo_target_ms=50.0, anomaly_detection=True)
        def slow_memory_function():
            time.sleep(0.15)  # 150ms - 3x the SLO target
            return {"retrieved": True}

        result = slow_memory_function()

        assert result["retrieved"] is True

        # Verify performance outlier anomaly was recorded
        mock_metrics_with_anomaly.anomaly_detection_counter.add.assert_called()

    def test_focus_drift_anomaly_detection(self, mock_metrics_with_anomaly):
        """Test focus drift anomaly detection"""
        # Simulate extreme focus drift
        extreme_drift_weights = [0.1, 0.9, 0.05, 0.95, 0.01]  # Very high variance

        record_focus_drift("drift_test_node", extreme_drift_weights)

        # Verify anomaly was detected
        mock_metrics_with_anomaly.anomaly_detection_counter.add.assert_called()

    def test_memory_cascade_anomaly_detection(self, mock_metrics_with_anomaly):
        """Test memory cascade risk anomaly detection"""
        # Simulate critical memory cascade conditions
        record_memory_cascade_risk(fold_count=995, retrieval_depth=50, cascade_detected=True)

        # Verify critical anomaly was recorded
        mock_metrics_with_anomaly.anomaly_detection_counter.add.assert_called()

    def test_thought_complexity_anomaly_detection(self, mock_metrics_with_anomaly):
        """Test thought complexity anomaly detection"""
        # Simulate extremely complex reasoning
        record_thought_complexity(reasoning_depth=25, logic_chains=15, inference_steps=500)

        # Verify complexity anomaly was recorded
        mock_metrics_with_anomaly.anomaly_detection_counter.add.assert_called()

    def test_decision_confidence_anomaly_detection(self, mock_metrics_with_anomaly):
        """Test low decision confidence anomaly detection"""
        # Simulate very low confidence decision
        record_decision_confidence(confidence_score=0.1, decision_type="critical", node_id="low_conf_test")

        # Verify low confidence anomaly was recorded
        mock_metrics_with_anomaly.anomaly_detection_counter.add.assert_called()


class TestPerformanceImpact:
    """Test that observability has minimal performance impact"""

    def test_instrumentation_overhead_minimal(self):
        """Test that instrumentation adds minimal overhead"""
        @instrument_cognitive_stage("performance_test", node_id="perf_node")
        def simple_function():
            return {"result": "done"}

        # Measure time without instrumentation
        start_time = time.perf_counter()
        for _ in range(1000):
            {"result": "done"}  # Direct execution
        direct_duration = time.perf_counter() - start_time

        # Measure time with instrumentation (but disabled)
        with patch('observability.matriz_instrumentation._cognitive_initialized', False):
            start_time = time.perf_counter()
            for _ in range(1000):
                simple_function()
            instrumented_duration = time.perf_counter() - start_time

        # Overhead should be less than 5%
        overhead_ratio = (instrumented_duration - direct_duration) / direct_duration
        assert overhead_ratio < 0.05, f"Instrumentation overhead {overhead_ratio:.2%} exceeds 5%"

    @pytest.mark.asyncio
    async def test_cognitive_pipeline_span_performance(self):
        """Test cognitive pipeline span performance impact"""
        async def simple_pipeline():
            await asyncio.sleep(0.01)
            return {"processed": True}

        # Test with span disabled
        with patch('observability.matriz_instrumentation._cognitive_initialized', False):
            start_time = time.perf_counter()
            async with cognitive_pipeline_span("perf_test", "test query"):
                result = await simple_pipeline()
            span_duration = time.perf_counter() - start_time

        assert result["processed"] is True
        assert span_duration < 0.05  # Should complete in under 50ms


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
