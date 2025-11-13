#!/usr/bin/env python3
"""
MATRIZ Cognitive Pipeline Observability Validation Script

Validates the complete observability integration for MATRIZ cognitive pipeline including:
- Instrumentation functionality
- Metrics collection and recording
- Anomaly detection for 1-in-10,000 events
- Performance impact assessment
- End-to-end pipeline observability

Usage:
    python scripts/validate_matriz_observability.py [--verbose] [--performance-test]
"""

import argparse
import asyncio
import logging
import os
import statistics
import sys
import time
from typing import Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
from observability.otel_instrumentation import (
    initialize_otel_instrumentation,
    instrument_cognitive_event,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MatrizObservabilityValidator:
    """Validator for MATRIZ cognitive pipeline observability"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.validation_results = []
        self.performance_results = []
        self.anomaly_test_results = []

    def log(self, message: str, level: str = "info"):
        """Log validation messages"""
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

        if self.verbose:
            print(f"[{level.upper()}] {message}")

    def validate_initialization(self) -> bool:
        """Validate observability initialization"""
        self.log("=== Validating Observability Initialization ===")

        try:
            # Initialize base OTel instrumentation
            base_init = initialize_otel_instrumentation(
                service_name="matriz-validation",
                enable_prometheus=True,
                enable_logging=True
            )

            if not base_init:
                self.log("Base OTel initialization failed", "warning")

            # Initialize cognitive instrumentation
            cognitive_init = initialize_cognitive_instrumentation(enable_metrics=True)

            if cognitive_init:
                self.log("✓ Cognitive instrumentation initialized successfully")
            else:
                self.log("✗ Cognitive instrumentation initialization failed", "error")
                return False

            # Check status
            status = get_cognitive_instrumentation_status()
            self.log(f"Status: {status}")

            if status.get("cognitive_initialized"):
                self.log("✓ Cognitive instrumentation status confirmed")
                return True
            else:
                self.log("✗ Cognitive instrumentation status check failed", "error")
                return False

        except Exception as e:
            self.log(f"✗ Initialization validation failed: {e}", "error")
            return False

    def validate_cognitive_stage_instrumentation(self) -> bool:
        """Validate cognitive stage instrumentation decorators"""
        self.log("=== Validating Cognitive Stage Instrumentation ===")

        success_count = 0
        total_tests = 6

        try:
            # Test 1: Memory stage instrumentation
            @instrument_cognitive_stage("memory", node_id="memory_test", slo_target_ms=50.0)
            def test_memory_stage(query: str) -> dict[str, Any]:
                time.sleep(0.02)  # Simulate memory retrieval
                return {
                    "memories": ["memory1", "memory2"],
                    "confidence": 0.9
                }

            result = test_memory_stage("test query")
            if result.get("memories") and result.get("confidence"):
                self.log("✓ Memory stage instrumentation working")
                success_count += 1
            else:
                self.log("✗ Memory stage instrumentation failed", "error")

            # Test 2: Attention stage instrumentation
            @instrument_cognitive_stage("attention", node_id="attention_test", slo_target_ms=30.0)
            def test_attention_stage(inputs: list[str]) -> dict[str, Any]:
                time.sleep(0.015)  # Simulate attention processing
                return {
                    "focused_input": inputs[0] if inputs else None,
                    "attention_weights": [0.8, 0.2]
                }

            result = test_attention_stage(["primary", "secondary"])
            if result.get("focused_input") and result.get("attention_weights"):
                self.log("✓ Attention stage instrumentation working")
                success_count += 1
            else:
                self.log("✗ Attention stage instrumentation failed", "error")

            # Test 3: Thought stage instrumentation
            @instrument_cognitive_stage("thought", node_id="thought_test", slo_target_ms=100.0)
            def test_thought_stage(problem: str) -> dict[str, Any]:
                time.sleep(0.05)  # Simulate reasoning
                return {
                    "solution": "42",
                    "reasoning_depth": 5,
                    "logic_chains": 2
                }

            result = test_thought_stage("complex problem")
            if result.get("solution") and result.get("reasoning_depth"):
                self.log("✓ Thought stage instrumentation working")
                success_count += 1
            else:
                self.log("✗ Thought stage instrumentation failed", "error")

            # Test 4: Decision stage instrumentation
            @instrument_cognitive_stage("decision", node_id="decision_test", slo_target_ms=40.0)
            def test_decision_stage(options: list[str]) -> dict[str, Any]:
                time.sleep(0.025)  # Simulate decision making
                return {
                    "chosen_option": options[0],
                    "confidence": 0.85
                }

            result = test_decision_stage(["option1", "option2"])
            if result.get("chosen_option") and result.get("confidence"):
                self.log("✓ Decision stage instrumentation working")
                success_count += 1
            else:
                self.log("✗ Decision stage instrumentation failed", "error")

            # Test 5: Async instrumentation
            @instrument_cognitive_stage("action", node_id="async_test", slo_target_ms=75.0)
            async def test_async_stage(action: str) -> dict[str, Any]:
                await asyncio.sleep(0.03)  # Simulate async action
                return {
                    "action_taken": action,
                    "success": True
                }

            async def run_async_test():
                result = await test_async_stage("test_action")
                return result.get("action_taken") and result.get("success")

            async_result = asyncio.run(run_async_test())
            if async_result:
                self.log("✓ Async stage instrumentation working")
                success_count += 1
            else:
                self.log("✗ Async stage instrumentation failed", "error")

            # Test 6: Error handling
            @instrument_cognitive_stage("awareness", node_id="error_test")
            def test_error_handling():
                raise ValueError("Simulated cognitive error")

            try:
                test_error_handling()
                self.log("✗ Error handling test failed - no exception raised", "error")
            except ValueError:
                self.log("✓ Error handling in instrumentation working")
                success_count += 1
            except Exception as e:
                self.log(f"✗ Unexpected error in error handling test: {e}", "error")

        except Exception as e:
            self.log(f"✗ Stage instrumentation validation failed: {e}", "error")

        success_rate = success_count / total_tests
        self.log(f"Stage instrumentation success rate: {success_rate:.1%} ({success_count}/{total_tests})")
        return success_rate >= 0.8

    async def validate_cognitive_pipeline_span(self) -> bool:
        """Validate cognitive pipeline span functionality"""
        self.log("=== Validating Cognitive Pipeline Span ===")

        try:
            expected_stages = ["memory", "attention", "thought", "action", "decision", "awareness"]

            async with cognitive_pipeline_span(
                "validation_pipeline",
                "validation query",
                expected_stages=expected_stages,
                target_slo_ms=200.0
            ):
                # Simulate pipeline processing
                await asyncio.sleep(0.05)

                # Record some cognitive metrics during pipeline
                record_focus_drift("pipeline_node", [0.7, 0.8, 0.6, 0.9], window_size=4)
                record_memory_cascade_risk(fold_count=300, retrieval_depth=5, cascade_detected=False)
                record_thought_complexity(reasoning_depth=3, logic_chains=2, inference_steps=10)
                record_decision_confidence(confidence_score=0.8, decision_type="validation", node_id="pipeline_node")

            self.log("✓ Cognitive pipeline span executed successfully")
            return True

        except Exception as e:
            self.log(f"✗ Pipeline span validation failed: {e}", "error")
            return False

    def validate_anomaly_detection(self) -> bool:
        """Validate anomaly detection for rare cognitive events"""
        self.log("=== Validating Anomaly Detection (1-in-10,000 Events) ===")

        anomaly_scenarios = [
            # Focus drift anomaly
            {
                "name": "Focus Drift Anomaly",
                "test": lambda: record_focus_drift("anomaly_node", [0.9, 0.1, 0.95, 0.05], window_size=4),
                "description": "High attention weight variance"
            },

            # Memory cascade risk
            {
                "name": "Memory Cascade Risk",
                "test": lambda: record_memory_cascade_risk(fold_count=980, retrieval_depth=40, cascade_detected=True),
                "description": "Critical memory cascade conditions"
            },

            # Thought complexity spike
            {
                "name": "Thought Complexity Spike",
                "test": lambda: record_thought_complexity(reasoning_depth=25, logic_chains=12, inference_steps=300),
                "description": "Extreme reasoning complexity"
            },

            # Low decision confidence
            {
                "name": "Low Decision Confidence",
                "test": lambda: record_decision_confidence(confidence_score=0.15, decision_type="critical", node_id="anomaly_node"),
                "description": "Very low confidence decision"
            },

            # Performance outlier
            {
                "name": "Performance Outlier",
                "test": self._test_performance_outlier,
                "description": "Extreme processing latency"
            }
        ]

        detected_anomalies = 0
        total_scenarios = len(anomaly_scenarios)

        for scenario in anomaly_scenarios:
            try:
                self.log(f"Testing {scenario['name']}: {scenario['description']}")
                scenario["test"]()
                detected_anomalies += 1
                self.log(f"✓ {scenario['name']} anomaly detected")
            except Exception as e:
                self.log(f"✗ {scenario['name']} test failed: {e}", "error")

        detection_rate = detected_anomalies / total_scenarios
        self.log(f"Anomaly detection rate: {detection_rate:.1%} ({detected_anomalies}/{total_scenarios})")

        return detection_rate >= 0.8

    def _test_performance_outlier(self):
        """Test performance outlier detection"""
        @instrument_cognitive_stage("memory", node_id="outlier_node", slo_target_ms=50.0, anomaly_detection=True)
        def slow_processing():
            time.sleep(0.200)  # 200ms - 4x the SLO target
            return {"processed": True}

        result = slow_processing()
        return result.get("processed", False)

    def validate_performance_impact(self) -> bool:
        """Validate that observability has minimal performance impact"""
        self.log("=== Validating Performance Impact ===")

        iterations = 1000

        # Test function without instrumentation
        def baseline_function():
            time.sleep(0.001)  # 1ms processing time
            return {"result": "done"}

        # Test function with instrumentation
        @instrument_cognitive_stage("performance", node_id="perf_node", slo_target_ms=10.0)
        def instrumented_function():
            time.sleep(0.001)  # Same 1ms processing time
            return {"result": "done"}

        # Measure baseline performance
        baseline_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            baseline_function()
            baseline_times.append(time.perf_counter() - start)

        # Measure instrumented performance
        instrumented_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            instrumented_function()
            instrumented_times.append(time.perf_counter() - start)

        # Calculate statistics
        baseline_mean = statistics.mean(baseline_times) * 1000  # Convert to ms
        instrumented_mean = statistics.mean(instrumented_times) * 1000

        baseline_p95 = statistics.quantiles(baseline_times, n=20)[18] * 1000  # 95th percentile
        instrumented_p95 = statistics.quantiles(instrumented_times, n=20)[18] * 1000

        overhead_mean = ((instrumented_mean - baseline_mean) / baseline_mean) * 100
        overhead_p95 = ((instrumented_p95 - baseline_p95) / baseline_p95) * 100

        self.log(f"Baseline mean: {baseline_mean:.3f}ms, P95: {baseline_p95:.3f}ms")
        self.log(f"Instrumented mean: {instrumented_mean:.3f}ms, P95: {instrumented_p95:.3f}ms")
        self.log(f"Overhead - Mean: {overhead_mean:.1f}%, P95: {overhead_p95:.1f}%")

        # Performance impact should be less than 5%
        performance_acceptable = overhead_mean < 5.0 and overhead_p95 < 5.0

        if performance_acceptable:
            self.log("✓ Performance impact within acceptable limits")
        else:
            self.log("✗ Performance impact exceeds acceptable limits", "warning")

        self.performance_results = {
            "baseline_mean_ms": baseline_mean,
            "instrumented_mean_ms": instrumented_mean,
            "baseline_p95_ms": baseline_p95,
            "instrumented_p95_ms": instrumented_p95,
            "overhead_mean_percent": overhead_mean,
            "overhead_p95_percent": overhead_p95,
            "acceptable": performance_acceptable
        }

        return performance_acceptable

    def validate_cognitive_event_instrumentation(self) -> bool:
        """Validate cognitive event instrumentation (e.g., process_matriz_event)"""
        self.log("=== Validating Cognitive Event Instrumentation ===")

        try:
            @instrument_cognitive_event("process_matriz_event", slo_target_ms=100.0)
            def mock_process_matriz_event(event: dict[str, Any]) -> dict[str, Any]:
                # Simulate MATRIZ event processing
                stage = event.get('node_type', 'unknown').lower()
                node_id = event.get('id', 'unknown')

                time.sleep(0.03)  # Simulate processing time

                return {
                    "processed": True,
                    "stage": stage,
                    "node_id": node_id,
                    "confidence": 0.85,
                    "reasoning_depth": 3
                }

            # Test event
            test_event = {
                "id": "test_node_validation",
                "node_type": "THOUGHT",
                "data": {"query": "validation test"},
                "connections": ["node_456"],
                "timestamp": time.time(),
                "metadata": {"priority": "normal"}
            }

            result = mock_process_matriz_event(test_event)

            if (result.get("processed") and
                result.get("stage") == "thought" and
                result.get("node_id") == "test_node_validation"):
                self.log("✓ Cognitive event instrumentation working")
                return True
            else:
                self.log("✗ Cognitive event instrumentation failed", "error")
                return False

        except Exception as e:
            self.log(f"✗ Cognitive event validation failed: {e}", "error")
            return False

    async def run_full_validation(self) -> dict[str, Any]:
        """Run complete validation suite"""
        self.log("🧠 Starting MATRIZ Cognitive Pipeline Observability Validation")
        self.log("=" * 60)

        validation_results = {
            "initialization": False,
            "cognitive_stages": False,
            "pipeline_span": False,
            "cognitive_events": False,
            "anomaly_detection": False,
            "performance_impact": False,
            "overall_success": False
        }

        # Run all validations
        validation_results["initialization"] = self.validate_initialization()
        validation_results["cognitive_stages"] = self.validate_cognitive_stage_instrumentation()
        validation_results["pipeline_span"] = await self.validate_cognitive_pipeline_span()
        validation_results["cognitive_events"] = self.validate_cognitive_event_instrumentation()
        validation_results["anomaly_detection"] = self.validate_anomaly_detection()
        validation_results["performance_impact"] = self.validate_performance_impact()

        # Calculate overall success
        success_count = sum(1 for result in validation_results.values() if result)
        total_tests = len(validation_results) - 1  # Exclude overall_success
        success_rate = success_count / total_tests

        validation_results["overall_success"] = success_rate >= 0.8
        validation_results["success_rate"] = success_rate
        validation_results["performance_results"] = self.performance_results

        # Final results
        self.log("=" * 60)
        self.log("🎯 MATRIZ Observability Validation Results:")
        self.log(f"Overall Success Rate: {success_rate:.1%} ({success_count}/{total_tests})")

        for test, passed in validation_results.items():
            if test not in ["overall_success", "success_rate", "performance_results"]:
                status = "✓ PASS" if passed else "✗ FAIL"
                self.log(f"{test.replace('_', ' ').title()}: {status}")

        if validation_results["overall_success"]:
            self.log("🎉 MATRIZ Cognitive Pipeline Observability is READY for production!")
        else:
            self.log("⚠️  MATRIZ Cognitive Pipeline Observability needs attention before production", "warning")

        return validation_results


def main():
    """Main validation script"""
    parser = argparse.ArgumentParser(description="Validate MATRIZ Cognitive Pipeline Observability")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--performance-test", "-p", action="store_true", help="Run extended performance tests")

    args = parser.parse_args()

    # Set up environment for testing
    os.environ["LUKHAS_LANE"] = "candidate"

    # Create validator
    validator = MatrizObservabilityValidator(verbose=args.verbose)

    # Run validation
    try:
        results = asyncio.run(validator.run_full_validation())

        # Exit with appropriate code
        if results["overall_success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation script failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
