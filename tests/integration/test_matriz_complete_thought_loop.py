#!/usr/bin/env python3
"""
LUKHAS Integration Tests: Complete MATRIZ Thought Loop
======================================================

Comprehensive integration tests for the complete MATRIZ thought loop,
validating end-to-end functionality of all integrated cognitive components.

Tests include:
- Complete thought loop processing with all advanced features
- T4/0.01% performance compliance validation
- Edge case handling and stress scenarios
- Property-based testing for reasoning edge cases
- Memory-reasoning consistency validation
- Meta-cognitive assessment integration
- Circuit breaker and overload protection

Constellation Framework: 🌊 Flow Star Integration Testing
"""

import asyncio
import time
import pytest
import logging
from unittest.mock import patch

from lukhas.consciousness.matriz_thought_loop import MATRIZThoughtLoop
from lukhas.consciousness.types import (
    ConsciousnessState, ThoughtLoopContext, ThoughtLoopResult
)
from lukhas.consciousness.meta_cognitive_assessor import (
    MetaCognitiveAssessment, CognitiveLoadLevel
)

# Test configuration
pytestmark = pytest.mark.asyncio
logger = logging.getLogger(__name__)

# Performance targets for T4/0.01% compliance
T4_PERFORMANCE_TARGETS = {
    'complete_thought_loop_p95_ms': 250,
    'deep_inference_p95_ms': 100,
    'contradiction_detection_p95_ms': 50,
    'memory_validation_p95_ms': 30,
    'awareness_update_p95_ms': 25,
    'meta_assessment_p95_ms': 50
}


class TestMATRIZCompleteThoughtLoop:
    """Test suite for complete MATRIZ thought loop integration."""

    @pytest.fixture
    async def thought_loop(self):
        """Create configured MATRIZ thought loop for testing."""
        config = {
            'max_inference_depth': 12,
            'enable_contradiction_detection': True,
            'enable_meta_cognitive_assessment': True,
            'enable_memory_validation': True,
            'performance_tracking': True,
            'circuit_breaker_threshold': 10,
            'timeout_ms': 5000
        }

        loop = MATRIZThoughtLoop(config=config)
        await loop.initialize()
        return loop

    @pytest.fixture
    def sample_context(self):
        """Create sample thought loop context."""
        return ThoughtLoopContext(
            session_id="test_session_001",
            query="Analyze the implications of consciousness emergence in distributed systems",
            context_data={
                'domain': 'cognitive_architecture',
                'complexity_level': 'high',
                'reasoning_depth': 'deep',
                'memory_context': ['consciousness', 'emergence', 'distributed_systems']
            },
            time_budget_ms=1000,
            quality_threshold=0.8,
            tenant="test_tenant"
        )

    @pytest.fixture
    def consciousness_state(self):
        """Create sample consciousness state."""
        return ConsciousnessState(
            awareness_level=0.8,
            cognitive_load=0.6,
            focus_intensity=0.7,
            memory_coherence=0.9,
            reasoning_depth=0.8,
            contradiction_tension=0.2,
            meta_awareness=0.7,
            timestamp=time.time()
        )

    async def test_complete_thought_loop_basic_functionality(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test basic complete thought loop functionality."""
        # Execute complete thought loop
        result = await thought_loop.process_complete_thought_loop(
            context=sample_context,
            consciousness_state=consciousness_state
        )

        # Validate result structure
        assert isinstance(result, ThoughtLoopResult)
        assert result.success is True
        assert result.thought_synthesis is not None
        assert result.inference_results is not None
        assert len(result.inference_results) > 0
        assert result.contradiction_analysis is not None
        assert result.memory_validation is not None
        assert result.awareness_snapshot is not None
        assert result.meta_assessment is not None

        # Validate quality metrics
        assert result.overall_quality_score >= 0.8
        assert result.reasoning_confidence >= 0.7
        assert result.contradiction_score <= 0.3

        # Validate performance
        assert result.total_processing_time_ms < T4_PERFORMANCE_TARGETS['complete_thought_loop_p95_ms']

    async def test_deep_inference_integration(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test deep inference engine integration with 10+ levels."""
        # Configure for deep reasoning
        deep_context = sample_context
        deep_context.context_data['reasoning_depth'] = 'maximum'
        deep_context.time_budget_ms = 2000

        result = await thought_loop.process_complete_thought_loop(
            context=deep_context,
            consciousness_state=consciousness_state
        )

        # Validate deep inference was used
        assert len(result.inference_results) >= 10

        # Check inference depth progression
        depths = [inf.depth_level for inf in result.inference_results]
        assert max(depths) >= 10
        assert min(depths) >= 1

        # Validate inference quality improves with depth
        early_inferences = [inf for inf in result.inference_results if inf.depth_level <= 3]
        deep_inferences = [inf for inf in result.inference_results if inf.depth_level >= 8]

        early_quality = sum(inf.quality_score for inf in early_inferences) / len(early_inferences)
        deep_quality = sum(inf.quality_score for inf in deep_inferences) / len(deep_inferences)

        # Deep inferences should generally have higher quality
        assert deep_quality >= early_quality * 0.9  # Allow some variance

    async def test_contradiction_detection_accuracy(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test 98% contradiction detection mechanism."""
        # Create context with intentional contradictions
        contradictory_context = sample_context
        contradictory_context.context_data.update({
            'statements': [
                "The system is completely deterministic",
                "The system exhibits truly random behavior",
                "All components operate synchronously",
                "Asynchronous processing is fundamental to the architecture"
            ]
        })

        result = await thought_loop.process_complete_thought_loop(
            context=contradictory_context,
            consciousness_state=consciousness_state
        )

        # Validate contradiction detection
        contradiction_analysis = result.contradiction_analysis
        assert contradiction_analysis is not None
        assert len(contradiction_analysis.detected_contradictions) >= 2

        # Check detection accuracy
        assert contradiction_analysis.detection_confidence >= 0.98
        assert contradiction_analysis.resolution_suggestions is not None

        # Validate performance
        assert contradiction_analysis.processing_time_ms < T4_PERFORMANCE_TARGETS['contradiction_detection_p95_ms']

    async def test_meta_cognitive_self_checks(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test meta-cognitive self-assessment integration."""
        result = await thought_loop.process_complete_thought_loop(
            context=sample_context,
            consciousness_state=consciousness_state
        )

        # Validate meta-cognitive assessment
        meta_assessment = result.meta_assessment
        assert meta_assessment is not None
        assert isinstance(meta_assessment, MetaCognitiveAssessment)

        # Check assessment quality
        assert 0.0 <= meta_assessment.self_awareness_score <= 1.0
        assert 0.0 <= meta_assessment.meta_reasoning_quality <= 1.0
        assert meta_assessment.cognitive_load_assessment in list(CognitiveLoadLevel)

        # Validate insights and recommendations
        assert len(meta_assessment.insights) >= 1
        assert len(meta_assessment.recommended_adjustments) >= 1

        # Check performance metrics
        perf_metrics = meta_assessment.performance_metrics
        assert 0.0 <= perf_metrics.reasoning_accuracy <= 1.0
        assert 0.0 <= perf_metrics.confidence_calibration <= 1.0
        assert 0.0 <= perf_metrics.processing_efficiency <= 1.0

    async def test_memory_reasoning_consistency(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test memory-reasoning consistency validation."""
        result = await thought_loop.process_complete_thought_loop(
            context=sample_context,
            consciousness_state=consciousness_state
        )

        # Validate memory validation results
        memory_validation = result.memory_validation
        assert memory_validation is not None
        assert memory_validation.consistency_score >= 0.8
        assert memory_validation.conflicts_detected is not None

        # Check memory-reasoning alignment
        if len(memory_validation.conflicts_detected) > 0:
            # If conflicts detected, they should be resolved or flagged
            for conflict in memory_validation.conflicts_detected:
                assert conflict.severity is not None
                assert conflict.resolution_strategy is not None

        # Validate performance
        assert memory_validation.validation_time_ms < T4_PERFORMANCE_TARGETS['memory_validation_p95_ms']

    async def test_circuit_breaker_protection(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test circuit breaker protection under overload."""
        # Configure for potential overload
        overload_context = sample_context
        overload_context.time_budget_ms = 50  # Very tight budget
        overload_context.context_data.update({
            'complexity_level': 'extreme',
            'reasoning_depth': 'maximum',
            'stress_test': True
        })

        # Execute multiple rapid requests to trigger circuit breaker
        results = []
        for i in range(15):  # Exceed circuit breaker threshold
            try:
                result = await thought_loop.process_complete_thought_loop(
                    context=overload_context,
                    consciousness_state=consciousness_state
                )
                results.append(result)
            except Exception as e:
                # Circuit breaker should gracefully handle overload
                assert "circuit breaker" in str(e).lower() or "overload" in str(e).lower()

        # At least some requests should succeed before circuit breaker activates
        assert len(results) >= 5

        # Successful results should still meet quality standards
        for result in results:
            if result.success:
                assert result.overall_quality_score >= 0.6  # Relaxed under stress

    async def test_edge_case_reasoning_scenarios(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test reasoning edge cases and novel situations."""
        edge_cases = [
            {
                'name': 'empty_context',
                'context_data': {},
                'expected_graceful_degradation': True
            },
            {
                'name': 'contradictory_goals',
                'context_data': {
                    'goals': ['maximize_accuracy', 'minimize_processing_time'],
                    'constraints': ['unlimited_resources', 'resource_constrained']
                },
                'expected_contradiction_detection': True
            },
            {
                'name': 'recursive_self_reference',
                'context_data': {
                    'query': 'Analyze how this analysis affects the analysis itself',
                    'self_reference_level': 'high'
                },
                'expected_meta_reasoning': True
            },
            {
                'name': 'extreme_complexity',
                'context_data': {
                    'complexity_factors': list(range(100)),  # Many factors
                    'interaction_matrix': [[i*j for j in range(10)] for i in range(10)]
                },
                'expected_complexity_management': True
            }
        ]

        for edge_case in edge_cases:
            test_context = sample_context
            test_context.context_data.update(edge_case['context_data'])

            result = await thought_loop.process_complete_thought_loop(
                context=test_context,
                consciousness_state=consciousness_state
            )

            # Validate edge case handling
            assert result is not None

            if edge_case.get('expected_graceful_degradation'):
                # Should handle empty context gracefully
                assert result.success is True
                assert result.overall_quality_score >= 0.3

            if edge_case.get('expected_contradiction_detection'):
                # Should detect contradictions
                assert len(result.contradiction_analysis.detected_contradictions) > 0

            if edge_case.get('expected_meta_reasoning'):
                # Should engage meta-reasoning
                assert result.meta_assessment.meta_reasoning_quality >= 0.7

            if edge_case.get('expected_complexity_management'):
                # Should manage complexity appropriately
                assert result.meta_assessment.cognitive_load_assessment in [
                    CognitiveLoadLevel.HIGH, CognitiveLoadLevel.EXCESSIVE
                ]

    async def test_performance_compliance_stress(self, thought_loop):
        """Test T4/0.01% performance compliance under stress."""
        # Run multiple concurrent thought loops
        contexts = []
        consciousness_states = []

        for i in range(20):  # Stress test with multiple concurrent requests
            context = ThoughtLoopContext(
                session_id=f"stress_session_{i:03d}",
                query=f"Complex reasoning task {i} with multiple inference levels",
                context_data={
                    'complexity_level': 'high',
                    'reasoning_depth': 'deep',
                    'concurrent_id': i
                },
                time_budget_ms=500,
                quality_threshold=0.75,
                tenant=f"stress_tenant_{i % 5}"
            )
            contexts.append(context)

            state = ConsciousnessState(
                awareness_level=0.7 + (i % 3) * 0.1,
                cognitive_load=0.4 + (i % 5) * 0.1,
                focus_intensity=0.6 + (i % 4) * 0.1,
                memory_coherence=0.8,
                reasoning_depth=0.7,
                contradiction_tension=0.1 + (i % 2) * 0.1,
                meta_awareness=0.6,
                timestamp=time.time()
            )
            consciousness_states.append(state)

        # Execute all requests concurrently
        start_time = time.time()
        tasks = [
            thought_loop.process_complete_thought_loop(context, state)
            for context, state in zip(contexts, consciousness_states)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.time() - start_time) * 1000

        # Validate results
        successful_results = [r for r in results if isinstance(r, ThoughtLoopResult) and r.success]
        assert len(successful_results) >= 15  # At least 75% success rate under stress

        # Check performance targets
        processing_times = [r.total_processing_time_ms for r in successful_results]
        p95_time = sorted(processing_times)[int(0.95 * len(processing_times))]
        assert p95_time < T4_PERFORMANCE_TARGETS['complete_thought_loop_p95_ms']

        # Check quality maintenance under stress
        quality_scores = [r.overall_quality_score for r in successful_results]
        avg_quality = sum(quality_scores) / len(quality_scores)
        assert avg_quality >= 0.7  # Quality should be maintained under stress

    async def test_thought_loop_state_consistency(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test state consistency across multiple thought loop executions."""
        results = []

        # Execute multiple thought loops with same context
        for i in range(5):
            result = await thought_loop.process_complete_thought_loop(
                context=sample_context,
                consciousness_state=consciousness_state
            )
            results.append(result)

        # Validate consistency
        quality_scores = [r.overall_quality_score for r in results]
        quality_variance = max(quality_scores) - min(quality_scores)
        assert quality_variance < 0.3  # Quality should be relatively consistent

        # Validate reasoning patterns
        inference_counts = [len(r.inference_results) for r in results]
        count_variance = max(inference_counts) - min(inference_counts)
        assert count_variance <= 2  # Inference count should be stable

        # All results should be successful
        assert all(r.success for r in results)

    async def test_awareness_integration_feedback_loop(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test awareness engine integration and feedback loop."""
        result = await thought_loop.process_complete_thought_loop(
            context=sample_context,
            consciousness_state=consciousness_state
        )

        # Validate awareness snapshot
        awareness_snapshot = result.awareness_snapshot
        assert awareness_snapshot is not None

        # Check awareness metrics
        assert 0.0 <= awareness_snapshot.base_snapshot.drift_ema <= 1.0
        assert 0.0 <= awareness_snapshot.base_snapshot.load_factor <= 2.0
        assert awareness_snapshot.base_snapshot.signal_strength >= 0.0

        # Validate enhanced awareness features
        assert 0.0 <= awareness_snapshot.self_awareness_score <= 1.0
        assert 0.0 <= awareness_snapshot.meta_reasoning_quality <= 1.0
        assert len(awareness_snapshot.actionable_insights) >= 0
        assert len(awareness_snapshot.cognitive_adjustments) >= 1

        # Check performance metrics
        assert awareness_snapshot.base_snapshot.processing_time_ms < T4_PERFORMANCE_TARGETS['awareness_update_p95_ms']

    def test_thought_loop_configuration_validation(self):
        """Test thought loop configuration validation."""
        # Test valid configuration
        valid_config = {
            'max_inference_depth': 10,
            'enable_contradiction_detection': True,
            'enable_meta_cognitive_assessment': True,
            'performance_tracking': True
        }

        loop = MATRIZThoughtLoop(config=valid_config)
        assert loop.config['max_inference_depth'] == 10

        # Test invalid configuration handling
        invalid_config = {
            'max_inference_depth': 0,  # Invalid
            'timeout_ms': -100  # Invalid
        }

        with pytest.raises(ValueError):
            MATRIZThoughtLoop(config=invalid_config)

    async def test_error_recovery_and_graceful_degradation(
        self, thought_loop, sample_context, consciousness_state
    ):
        """Test error recovery and graceful degradation."""
        # Simulate component failures
        with patch.object(thought_loop.enhanced_thought_node, 'process_enhanced_thought',
                         side_effect=Exception("Simulated failure")):

            result = await thought_loop.process_complete_thought_loop(
                context=sample_context,
                consciousness_state=consciousness_state
            )

            # Should gracefully handle failure
            assert result is not None
            # Quality should be degraded but system should continue
            assert result.overall_quality_score >= 0.2  # Minimum acceptable quality

    async def test_tenant_isolation_and_resource_management(self, thought_loop):
        """Test multi-tenant isolation and resource management."""
        contexts = []
        for tenant_id in ['tenant_a', 'tenant_b', 'tenant_c']:
            context = ThoughtLoopContext(
                session_id=f"{tenant_id}_session",
                query=f"Tenant-specific query for {tenant_id}",
                context_data={'tenant_data': f"sensitive_{tenant_id}"},
                time_budget_ms=200,
                quality_threshold=0.7,
                tenant=tenant_id
            )
            contexts.append(context)

        consciousness_state = ConsciousnessState(
            awareness_level=0.8, cognitive_load=0.5, focus_intensity=0.7,
            memory_coherence=0.9, reasoning_depth=0.8, contradiction_tension=0.2,
            meta_awareness=0.7, timestamp=time.time()
        )

        # Execute for different tenants
        results = []
        for context in contexts:
            result = await thought_loop.process_complete_thought_loop(
                context=context,
                consciousness_state=consciousness_state
            )
            results.append(result)

        # Validate tenant isolation
        assert all(r.success for r in results)

        # Each result should be independent
        for i, result in enumerate(results):
            # Results should not contain data from other tenants
            result_str = str(result)
            for j, other_context in enumerate(contexts):
                if i != j:
                    assert other_context.context_data['tenant_data'] not in result_str


# Property-based testing for edge cases
try:
    from hypothesis import given, strategies as st

    class TestThoughtLoopPropertyBased:
        """Property-based tests for thought loop edge cases."""

        @given(
            awareness_level=st.floats(min_value=0.0, max_value=1.0),
            cognitive_load=st.floats(min_value=0.0, max_value=2.0),
            quality_threshold=st.floats(min_value=0.1, max_value=1.0)
        )
        async def test_varying_consciousness_states(
            self, awareness_level, cognitive_load, quality_threshold
        ):
            """Test thought loop with varying consciousness state parameters."""
            thought_loop = MATRIZThoughtLoop()
            await thought_loop.initialize()

            context = ThoughtLoopContext(
                session_id="property_test",
                query="Test query",
                context_data={},
                time_budget_ms=1000,
                quality_threshold=quality_threshold,
                tenant="test"
            )

            consciousness_state = ConsciousnessState(
                awareness_level=awareness_level,
                cognitive_load=cognitive_load,
                focus_intensity=0.7,
                memory_coherence=0.8,
                reasoning_depth=0.7,
                contradiction_tension=0.2,
                meta_awareness=0.6,
                timestamp=time.time()
            )

            result = await thought_loop.process_complete_thought_loop(
                context=context,
                consciousness_state=consciousness_state
            )

            # Properties that should always hold
            assert result is not None
            assert 0.0 <= result.overall_quality_score <= 1.0
            assert result.total_processing_time_ms > 0

        @given(
            inference_depth=st.integers(min_value=1, max_value=20),
            time_budget=st.integers(min_value=50, max_value=5000)
        )
        async def test_varying_processing_parameters(
            self, inference_depth, time_budget
        ):
            """Test thought loop with varying processing parameters."""
            config = {
                'max_inference_depth': inference_depth,
                'timeout_ms': time_budget + 1000
            }

            thought_loop = MATRIZThoughtLoop(config=config)
            await thought_loop.initialize()

            context = ThoughtLoopContext(
                session_id="property_test",
                query="Depth test query",
                context_data={'reasoning_depth': 'adaptive'},
                time_budget_ms=time_budget,
                quality_threshold=0.6,
                tenant="test"
            )

            consciousness_state = ConsciousnessState(
                awareness_level=0.7, cognitive_load=0.5, focus_intensity=0.7,
                memory_coherence=0.8, reasoning_depth=0.8, contradiction_tension=0.2,
                meta_awareness=0.6, timestamp=time.time()
            )

            result = await thought_loop.process_complete_thought_loop(
                context=context,
                consciousness_state=consciousness_state
            )

            # Properties for varying parameters
            assert result is not None
            assert result.total_processing_time_ms <= time_budget * 2  # Allow some overhead

            if result.success:
                # If successful, should have reasonable inference depth
                assert len(result.inference_results) <= inference_depth

except ImportError:
    # Hypothesis not available - skip property-based tests
    pass


# Performance benchmarking
class TestThoughtLoopPerformanceBenchmarks:
    """Performance benchmarks for T4/0.01% compliance validation."""

    async def test_throughput_benchmark(self, thought_loop):
        """Benchmark throughput for T4 compliance."""
        num_requests = 100
        start_time = time.time()

        context = ThoughtLoopContext(
            session_id="benchmark",
            query="Standard benchmark query",
            context_data={'benchmark': True},
            time_budget_ms=200,
            quality_threshold=0.7,
            tenant="benchmark"
        )

        consciousness_state = ConsciousnessState(
            awareness_level=0.7, cognitive_load=0.5, focus_intensity=0.7,
            memory_coherence=0.8, reasoning_depth=0.7, contradiction_tension=0.2,
            meta_awareness=0.6, timestamp=time.time()
        )

        # Execute benchmark
        successful_requests = 0
        for _ in range(num_requests):
            try:
                result = await thought_loop.process_complete_thought_loop(
                    context=context,
                    consciousness_state=consciousness_state
                )
                if result.success:
                    successful_requests += 1
            except Exception:
                pass  # Count failures

        total_time = time.time() - start_time
        throughput = successful_requests / total_time

        # T4 compliance: should handle reasonable throughput
        assert throughput >= 5.0  # At least 5 requests per second
        assert successful_requests >= num_requests * 0.9  # 90% success rate


if __name__ == "__main__":
    # Run basic smoke test
    async def smoke_test():
        """Basic smoke test for manual execution."""
        thought_loop = MATRIZThoughtLoop()
        await thought_loop.initialize()

        context = ThoughtLoopContext(
            session_id="smoke_test",
            query="Test consciousness emergence",
            context_data={'test': True},
            time_budget_ms=1000,
            quality_threshold=0.7,
            tenant="smoke"
        )

        consciousness_state = ConsciousnessState(
            awareness_level=0.8, cognitive_load=0.5, focus_intensity=0.7,
            memory_coherence=0.9, reasoning_depth=0.8, contradiction_tension=0.2,
            meta_awareness=0.7, timestamp=time.time()
        )

        result = await thought_loop.process_complete_thought_loop(
            context=context,
            consciousness_state=consciousness_state
        )

        print(f"Smoke test result: success={result.success}, quality={result.overall_quality_score}")
        return result

    # Run smoke test
    result = asyncio.run(smoke_test())
    print("Integration tests module loaded successfully")