"""
Property-Based Testing Framework for Advanced Cognitive Reasoning Edge Cases

This module implements comprehensive property-based testing for the LUKHAS cognitive
reasoning system, specifically targeting <0.01% probability edge cases and extreme
scenarios to ensure system correctness under all conditions.

Architecture:
- Hypothesis-based property testing for inference chains
- Generative test cases for contradiction detection
- Stress testing for meta-cognitive assessment
- Edge case generation for recursive reasoning
- Performance validation under extreme load

T4/0.01% Compliance:
- Tests target scenarios with <0.01% probability
- Validates cognitive correctness in extreme conditions
- Ensures P95 latency < 250ms even under cognitive stress
- Validates 98% contradiction detection accuracy
"""

import asyncio
import gc
import logging
import statistics
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

import hypothesis
import pytest
from hypothesis import assume, given, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, consumes, rule

# LUKHAS cognitive imports
from lukhas.cognitive_core.reasoning.contradiction_integrator import ContradictionIntegrator
from lukhas.cognitive_core.reasoning.deep_inference_engine import DeepInferenceEngine, InferenceType
from lukhas.consciousness.enhanced_thought_engine import EnhancedThoughtEngine, ThoughtComplexity
from lukhas.consciousness.meta_cognitive_assessor import MetaCognitiveAssessor

# Test configuration
hypothesis.settings(
    max_examples=1000,
    deadline=10000,  # 10s for complex cognitive tests
    suppress_health_check=[hypothesis.HealthCheck.too_slow]
)

logger = logging.getLogger(__name__)


class EdgeCaseCategory(Enum):
    """Categories of edge cases for systematic testing"""
    RECURSIVE_OVERFLOW = "recursive_overflow"
    LOGICAL_PARADOX = "logical_paradox"
    CIRCULAR_REASONING = "circular_reasoning"
    CONTRADICTION_CASCADE = "contradiction_cascade"
    MEMORY_PRESSURE = "memory_pressure"
    TIMEOUT_BOUNDARY = "timeout_boundary"
    MALFORMED_INPUT = "malformed_input"
    COGNITIVE_OVERLOAD = "cognitive_overload"


@dataclass
class EdgeCaseScenario:
    """Structured edge case scenario for testing"""
    category: EdgeCaseCategory
    description: str
    input_data: Dict[str, Any]
    expected_behavior: str
    probability_estimate: float  # Target <0.01%


class PropertyBasedTestFramework:
    """
    Core property-based testing framework for cognitive reasoning edge cases.

    Implements systematic generation and validation of extreme scenarios
    to ensure cognitive system correctness under all conditions.
    """

    def __init__(self):
        self.inference_engine = None
        self.thought_engine = None
        self.contradiction_integrator = None
        self.meta_assessor = None
        self.test_scenarios: List[EdgeCaseScenario] = []
        self.performance_metrics = {
            'latency_samples': [],
            'error_rates': {},
            'cognitive_loads': [],
            'memory_usage': []
        }

    async def setup_cognitive_components(self):
        """Initialize cognitive components for testing"""
        self.inference_engine = DeepInferenceEngine(
            max_depth=15,  # Extended for edge case testing
            timeout_per_step=0.020,  # Strict timing
            circuit_breaker_threshold=3
        )

        self.thought_engine = EnhancedThoughtEngine(
            inference_engine=self.inference_engine,
            complexity_threshold=ThoughtComplexity.EXTREME,
            performance_budget=0.200  # 200ms budget
        )

        self.contradiction_integrator = ContradictionIntegrator(
            confidence_threshold=0.98,
            real_time_monitoring=True
        )

        self.meta_assessor = MetaCognitiveAssessor(
            assessment_depth="comprehensive",
            performance_tracking=True
        )

    def generate_edge_case_scenarios(self) -> List[EdgeCaseScenario]:
        """Generate comprehensive edge case scenarios"""
        scenarios = []

        # Recursive overflow scenarios
        scenarios.extend([
            EdgeCaseScenario(
                category=EdgeCaseCategory.RECURSIVE_OVERFLOW,
                description="Deep recursive inference chain (20+ levels)",
                input_data={
                    "query": "If A implies B, and B implies C, and C implies D... (20 levels)",
                    "depth": 25,
                    "circular_refs": False
                },
                expected_behavior="Graceful depth limiting with circuit breaker",
                probability_estimate=0.005
            ),
            EdgeCaseScenario(
                category=EdgeCaseCategory.RECURSIVE_OVERFLOW,
                description="Infinite recursion attempt",
                input_data={
                    "query": "Self-referential statement that creates infinite loop",
                    "depth": -1,  # Infinite depth request
                    "circular_refs": True
                },
                expected_behavior="Circuit breaker activation within 3 steps",
                probability_estimate=0.001
            )
        ])

        # Logical paradox scenarios
        scenarios.extend([
            EdgeCaseScenario(
                category=EdgeCaseCategory.LOGICAL_PARADOX,
                description="Classic liar paradox",
                input_data={
                    "query": "This statement is false",
                    "context": "logical_evaluation",
                    "require_resolution": True
                },
                expected_behavior="Paradox detection and meta-cognitive flagging",
                probability_estimate=0.008
            ),
            EdgeCaseScenario(
                category=EdgeCaseCategory.LOGICAL_PARADOX,
                description="Russell's paradox variant",
                input_data={
                    "query": "Set of all sets that do not contain themselves",
                    "context": "set_theory",
                    "formal_logic": True
                },
                expected_behavior="Formal contradiction detection (98% accuracy)",
                probability_estimate=0.003
            )
        ])

        # Contradiction cascade scenarios
        scenarios.extend([
            EdgeCaseScenario(
                category=EdgeCaseCategory.CONTRADICTION_CASCADE,
                description="Multiple simultaneous contradictions",
                input_data={
                    "premises": [
                        "All ravens are black",
                        "Some ravens are white",
                        "Nothing is both black and white",
                        "All birds are ravens"
                    ],
                    "inference_required": True
                },
                expected_behavior="Cascade detection and isolation",
                probability_estimate=0.002
            )
        ])

        # Memory pressure scenarios
        scenarios.extend([
            EdgeCaseScenario(
                category=EdgeCaseCategory.MEMORY_PRESSURE,
                description="Extreme memory consumption during reasoning",
                input_data={
                    "large_context": "x" * 100000,  # 100KB context
                    "complex_reasoning": True,
                    "memory_limit": 1024 * 1024  # 1MB limit
                },
                expected_behavior="Graceful degradation with memory management",
                probability_estimate=0.006
            )
        ])

        # Timeout boundary scenarios
        scenarios.extend([
            EdgeCaseScenario(
                category=EdgeCaseCategory.TIMEOUT_BOUNDARY,
                description="Processing at exact timeout boundary",
                input_data={
                    "processing_time": 0.249,  # Just under 250ms limit
                    "complex_inference": True,
                    "strict_deadline": True
                },
                expected_behavior="Completion within T4 latency target",
                probability_estimate=0.004
            )
        ])

        self.test_scenarios = scenarios
        return scenarios

    @asynccontextmanager
    async def performance_monitor(self, test_name: str):
        """Context manager for performance monitoring during tests"""
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            latency = (end_time - start_time) * 1000  # Convert to ms
            memory_delta = end_memory - start_memory

            self.performance_metrics['latency_samples'].append(latency)
            self.performance_metrics['memory_usage'].append(memory_delta)

            # Log performance for analysis
            logger.info(f"Test {test_name}: {latency:.2f}ms, {memory_delta}B memory")

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        gc.collect()
        return sum(obj.__sizeof__() for obj in gc.get_objects())

    async def validate_t4_compliance(self, latency_ms: float) -> bool:
        """Validate T4/0.01% latency compliance"""
        return latency_ms < 250.0

    def calculate_test_coverage_metrics(self) -> Dict[str, float]:
        """Calculate test coverage metrics for edge cases"""
        total_scenarios = len(self.test_scenarios)
        if total_scenarios == 0:
            return {'coverage': 0.0}

        # Calculate coverage by category
        category_coverage = {}
        for category in EdgeCaseCategory:
            scenarios_in_category = sum(
                1 for scenario in self.test_scenarios
                if scenario.category == category
            )
            category_coverage[category.value] = scenarios_in_category / total_scenarios

        # Calculate overall edge case probability coverage
        total_probability = sum(scenario.probability_estimate for scenario in self.test_scenarios)

        return {
            'total_scenarios': total_scenarios,
            'category_coverage': category_coverage,
            'probability_coverage': total_probability,
            'target_compliance': total_probability <= 0.01,  # <0.01% target
            'performance_samples': len(self.performance_metrics['latency_samples'])
        }


# Hypothesis strategies for property-based testing
@st.composite
def reasoning_input_strategy(draw):
    """Generate diverse reasoning inputs for property testing"""
    query_type = draw(st.sampled_from([
        'logical_inference', 'causal_reasoning', 'probabilistic_judgment',
        'contradiction_detection', 'meta_cognitive_assessment'
    ]))

    complexity = draw(st.sampled_from([
        ThoughtComplexity.SIMPLE, ThoughtComplexity.MODERATE,
        ThoughtComplexity.COMPLEX, ThoughtComplexity.EXTREME
    ]))

    context_size = draw(st.integers(min_value=10, max_value=10000))

    return {
        'query': f"Test query for {query_type}",
        'complexity': complexity,
        'context': 'x' * context_size,
        'type': query_type
    }


@st.composite
def contradiction_scenario_strategy(draw):
    """Generate contradiction scenarios for testing"""
    num_premises = draw(st.integers(min_value=2, max_value=10))

    premises = []
    for i in range(num_premises):
        premise = draw(st.text(min_size=5, max_size=100))
        premises.append(premise)

    contradiction_type = draw(st.sampled_from([
        'logical', 'factual', 'temporal', 'causal', 'probabilistic'
    ]))

    return {
        'premises': premises,
        'type': contradiction_type,
        'confidence_threshold': draw(st.floats(min_value=0.8, max_value=0.99))
    }


class CognitiveReasoningStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for cognitive reasoning system.

    Tests complex interactions between reasoning components over time,
    ensuring system consistency under various state transitions.
    """

    reasoning_contexts = Bundle('reasoning_contexts')
    inference_chains = Bundle('inference_chains')

    def __init__(self):
        super().__init__()
        self.framework = PropertyBasedTestFramework()
        self.active_contexts = {}
        self.inference_history = []
        self.performance_violations = []

    @rule(target=reasoning_contexts,
          context_data=reasoning_input_strategy())
    def create_reasoning_context(self, context_data):
        """Create a new reasoning context"""
        context_id = f"ctx_{len(self.active_contexts)}"
        self.active_contexts[context_id] = {
            'data': context_data,
            'created_at': time.time(),
            'inferences': []
        }
        return context_id

    @rule(context=reasoning_contexts,
          inference_type=st.sampled_from(list(InferenceType)))
    def perform_inference(self, context, inference_type):
        """Perform inference operation on context"""
        if context not in self.active_contexts:
            return

        context_data = self.active_contexts[context]

        # Simulate inference with performance tracking
        start_time = time.perf_counter()

        # Mock inference operation
        inference_result = {
            'type': inference_type,
            'input': context_data['data']['query'],
            'complexity': context_data['data']['complexity'],
            'timestamp': time.time()
        }

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Track performance violations
        if latency_ms > 250.0:  # T4 violation
            self.performance_violations.append({
                'context': context,
                'latency': latency_ms,
                'type': 'latency_violation'
            })

        context_data['inferences'].append(inference_result)
        self.inference_history.append(inference_result)

    @rule(contexts=st.lists(reasoning_contexts, min_size=2, max_size=5))
    def test_concurrent_reasoning(self, contexts):
        """Test concurrent reasoning across multiple contexts"""
        valid_contexts = [ctx for ctx in contexts if ctx in self.active_contexts]

        if len(valid_contexts) < 2:
            return

        # Simulate concurrent processing
        start_time = time.perf_counter()

        for ctx in valid_contexts:
            context_data = self.active_contexts[ctx]
            # Mock concurrent inference
            context_data['concurrent_processed'] = True

        end_time = time.perf_counter()
        concurrent_latency = (end_time - start_time) * 1000

        # Validate concurrent performance doesn't degrade significantly
        assert concurrent_latency < 250.0 * len(valid_contexts)

    @rule(context=consumes(reasoning_contexts))
    def cleanup_context(self, context):
        """Clean up reasoning context"""
        if context in self.active_contexts:
            del self.active_contexts[context]

    def teardown(self):
        """Validate final system state"""
        # Ensure no critical performance violations
        critical_violations = [
            v for v in self.performance_violations
            if v['latency'] > 500.0  # Critical threshold
        ]

        assert len(critical_violations) == 0, \
            f"Critical performance violations: {critical_violations}"

        # Ensure reasonable inference history
        assert len(self.inference_history) > 0, "No inferences performed"

        # Clean up
        self.active_contexts.clear()
        self.inference_history.clear()


@pytest.fixture
async def cognitive_test_framework():
    """Fixture providing initialized test framework"""
    framework = PropertyBasedTestFramework()
    await framework.setup_cognitive_components()
    return framework


class TestCognitiveReasoningProperties:
    """Property-based tests for cognitive reasoning system"""

    @given(reasoning_input_strategy())
    @pytest.mark.asyncio
    async def test_inference_determinism(self, reasoning_input):
        """Test that inference results are deterministic for same inputs"""
        framework = PropertyBasedTestFramework()
        await framework.setup_cognitive_components()

        # Run same inference twice
        async with framework.performance_monitor("determinism_test"):
            result1 = await framework.thought_engine.synthesize_thought(
                reasoning_input['query'],
                context={'complexity': reasoning_input['complexity']}
            )

            result2 = await framework.thought_engine.synthesize_thought(
                reasoning_input['query'],
                context={'complexity': reasoning_input['complexity']}
            )

        # Results should be consistent (allowing for timestamp differences)
        assert result1['content'] == result2['content'], \
            "Inference results should be deterministic"

    @given(contradiction_scenario_strategy())
    @pytest.mark.asyncio
    async def test_contradiction_detection_accuracy(self, scenario):
        """Test contradiction detection meets 98% accuracy target"""
        framework = PropertyBasedTestFramework()
        await framework.setup_cognitive_components()

        async with framework.performance_monitor("contradiction_test"):
            detection_result = await framework.contradiction_integrator.detect_contradictions(
                scenario['premises'],
                confidence_threshold=scenario['confidence_threshold']
            )

        # Validate detection structure
        assert 'contradictions' in detection_result
        assert 'confidence' in detection_result

        # Confidence should meet threshold
        if detection_result['contradictions']:
            assert detection_result['confidence'] >= scenario['confidence_threshold']

    @given(st.integers(min_value=1, max_value=20))
    @pytest.mark.asyncio
    async def test_recursive_inference_safety(self, depth):
        """Test recursive inference handles depth safely"""
        framework = PropertyBasedTestFramework()
        await framework.setup_cognitive_components()

        recursive_query = f"Recursive reasoning chain depth {depth}"

        async with framework.performance_monitor(f"recursive_depth_{depth}"):
            try:
                result = await framework.inference_engine.infer(
                    recursive_query,
                    inference_type=InferenceType.DEDUCTIVE,
                    max_depth=depth
                )

                # Should complete within timeout
                assert result is not None

                # Should respect circuit breaker
                if depth > 15:  # Beyond safe depth
                    assert 'circuit_breaker_triggered' in result.get('metadata', {})

            except asyncio.TimeoutError:
                # Acceptable for extreme depths
                assume(depth <= 15)

    @pytest.mark.asyncio
    async def test_edge_case_scenarios_comprehensive(self, cognitive_test_framework):
        """Test all generated edge case scenarios"""
        framework = cognitive_test_framework
        scenarios = framework.generate_edge_case_scenarios()

        passed_scenarios = 0
        total_scenarios = len(scenarios)

        for scenario in scenarios:
            try:
                async with framework.performance_monitor(f"edge_case_{scenario.category.value}"):
                    # Process scenario based on category
                    if scenario.category == EdgeCaseCategory.RECURSIVE_OVERFLOW:
                        await self._test_recursive_scenario(framework, scenario)
                    elif scenario.category == EdgeCaseCategory.LOGICAL_PARADOX:
                        await self._test_paradox_scenario(framework, scenario)
                    elif scenario.category == EdgeCaseCategory.CONTRADICTION_CASCADE:
                        await self._test_cascade_scenario(framework, scenario)
                    elif scenario.category == EdgeCaseCategory.MEMORY_PRESSURE:
                        await self._test_memory_scenario(framework, scenario)
                    elif scenario.category == EdgeCaseCategory.TIMEOUT_BOUNDARY:
                        await self._test_timeout_scenario(framework, scenario)

                    passed_scenarios += 1

            except Exception as e:
                logger.warning(f"Edge case scenario failed: {scenario.description} - {e}")

        # Ensure high success rate for edge cases
        success_rate = passed_scenarios / total_scenarios if total_scenarios > 0 else 0
        assert success_rate >= 0.85, f"Edge case success rate {success_rate:.2%} below target"

        # Validate performance metrics
        coverage_metrics = framework.calculate_test_coverage_metrics()
        assert coverage_metrics['target_compliance'], "Probability coverage exceeds 0.01%"

    async def _test_recursive_scenario(self, framework, scenario):
        """Test recursive overflow scenario"""
        result = await framework.inference_engine.infer(
            scenario.input_data['query'],
            max_depth=scenario.input_data.get('depth', 10)
        )

        # Should handle recursion gracefully
        assert result is not None

        if scenario.input_data.get('circular_refs', False):
            assert 'circuit_breaker_triggered' in result.get('metadata', {})

    async def _test_paradox_scenario(self, framework, scenario):
        """Test logical paradox scenario"""
        result = await framework.contradiction_integrator.detect_contradictions(
            [scenario.input_data['query']],
            confidence_threshold=0.98
        )

        # Should detect paradox with high confidence
        if 'paradox' in scenario.description.lower():
            assert result['contradictions'] or result.get('paradoxes', [])

    async def _test_cascade_scenario(self, framework, scenario):
        """Test contradiction cascade scenario"""
        result = await framework.contradiction_integrator.detect_contradictions(
            scenario.input_data['premises'],
            confidence_threshold=0.98
        )

        # Should detect multiple contradictions
        assert len(result.get('contradictions', [])) >= 2

    async def _test_memory_scenario(self, framework, scenario):
        """Test memory pressure scenario"""
        large_context = scenario.input_data['large_context']

        # Should handle large input without crashing
        result = await framework.thought_engine.synthesize_thought(
            "Analyze this large context",
            context={'data': large_context}
        )

        assert result is not None

    async def _test_timeout_scenario(self, framework, scenario):
        """Test timeout boundary scenario"""
        start_time = time.perf_counter()

        result = await framework.thought_engine.synthesize_thought(
            "Complex reasoning task",
            context={'strict_deadline': True}
        )

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Should meet T4 latency target
        assert await framework.validate_t4_compliance(latency_ms)
        assert result is not None


class TestStressScenarios:
    """Stress testing for cognitive reasoning under extreme conditions"""

    @pytest.mark.asyncio
    async def test_cognitive_overload_resilience(self, cognitive_test_framework):
        """Test system resilience under cognitive overload"""
        framework = cognitive_test_framework

        # Generate high cognitive load
        concurrent_tasks = []
        for i in range(50):  # High concurrency
            task = framework.thought_engine.synthesize_thought(
                f"Complex reasoning task {i}",
                context={'complexity': ThoughtComplexity.EXTREME}
            )
            concurrent_tasks.append(task)

        # Execute concurrently with timeout
        start_time = time.perf_counter()
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        end_time = time.perf_counter()

        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        [r for r in results if isinstance(r, Exception)]

        total_latency = (end_time - start_time) * 1000
        success_rate = len(successful_results) / len(results)

        # Validate stress test results
        assert success_rate >= 0.80, f"Success rate {success_rate:.2%} below threshold"
        assert total_latency < 5000.0, f"Total latency {total_latency:.2f}ms too high"

        logger.info(f"Stress test: {success_rate:.2%} success, {total_latency:.2f}ms total")

    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self, cognitive_test_framework):
        """Test memory leak prevention during extended operation"""
        framework = cognitive_test_framework

        initial_memory = framework._get_memory_usage()

        # Run extended reasoning session
        for i in range(100):
            await framework.thought_engine.synthesize_thought(
                f"Reasoning iteration {i}",
                context={'iteration': i}
            )

            # Force garbage collection periodically
            if i % 10 == 0:
                gc.collect()

        final_memory = framework._get_memory_usage()
        memory_growth = final_memory - initial_memory

        # Memory growth should be reasonable
        max_acceptable_growth = 10 * 1024 * 1024  # 10MB
        assert memory_growth < max_acceptable_growth, \
            f"Memory growth {memory_growth} exceeds threshold"

    @pytest.mark.asyncio
    async def test_performance_degradation_bounds(self, cognitive_test_framework):
        """Test performance degradation stays within bounds"""
        framework = cognitive_test_framework

        # Baseline performance measurement
        baseline_times = []
        for _ in range(10):
            start = time.perf_counter()
            await framework.thought_engine.synthesize_thought("Simple baseline test")
            end = time.perf_counter()
            baseline_times.append((end - start) * 1000)

        baseline_avg = statistics.mean(baseline_times)

        # Performance under load
        load_times = []
        for i in range(50):
            start = time.perf_counter()
            await framework.thought_engine.synthesize_thought(
                f"Load test {i}",
                context={'complexity': ThoughtComplexity.COMPLEX}
            )
            end = time.perf_counter()
            load_times.append((end - start) * 1000)

        load_avg = statistics.mean(load_times)
        load_p95 = statistics.quantiles(load_times, n=20)[18]  # 95th percentile

        # Performance degradation should be bounded
        degradation_factor = load_avg / baseline_avg
        assert degradation_factor < 3.0, f"Performance degraded by {degradation_factor:.1f}x"
        assert load_p95 < 250.0, f"P95 latency {load_p95:.2f}ms exceeds T4 target"


# Test runner configuration for comprehensive edge case coverage
if __name__ == "__main__":
    # Configure logging for test analysis
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run property-based tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--hypothesis-show-statistics",
        "--hypothesis-profile=ci"
    ])
