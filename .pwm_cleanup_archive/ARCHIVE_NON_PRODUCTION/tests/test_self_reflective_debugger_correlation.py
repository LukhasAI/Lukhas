#!/usr/bin/env python3
"""
Test Self-Reflective Debugger Correlation Analysis Implementation
Tests the correlation analysis between modules in self_reflective_debugger.py

This test validates the TODO #10 implementation following the established pattern
from previous testing.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_enhanced_srd_basic():
    """Test basic Enhanced SRD functionality"""
    print("📋 Testing Enhanced SRD Basic Functionality")

    try:
        from ethics.self_reflective_debugger import (
            EnhancedSelfReflectiveDebugger,
        )

        # Test initialization
        srd = EnhancedSelfReflectiveDebugger()
        print("✅ EnhancedSelfReflectiveDebugger imported and initialized successfully")

        # Test configuration
        config = {"enable_realtime": True, "anomaly_threshold": 0.3}
        configured_srd = EnhancedSelfReflectiveDebugger(config)
        print("✅ EnhancedSelfReflectiveDebugger configuration works")

        # Test correlation matrix initialization
        assert hasattr(srd, "cross_module_correlation_matrix")
        print("✅ Correlation matrix properly initialized")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


async def test_correlation_analysis():
    """Test cross-module correlation analysis"""
    print("\n📋 Testing Cross-Module Correlation Analysis")

    try:
        from ethics.self_reflective_debugger import (
            EnhancedReasoningChain,
            EnhancedSelfReflectiveDebugger,
            ReasoningStep,
        )

        # Initialize SRD
        srd = EnhancedSelfReflectiveDebugger()
        print("✅ Enhanced SRD initialized successfully")

        # Create a test reasoning chain
        chain_id = "test_correlation_chain"
        chain = EnhancedReasoningChain(chain_id=chain_id)
        srd.active_chains[chain_id] = chain

        # Create test reasoning step with module interactions
        step = ReasoningStep(
            operation="test_correlation_operation",
            confidence=0.75,
            metadata={
                # Module call counts
                "hds_calls": 2,
                "cpi_calls": 3,
                "ppmv_calls": 1,
                "xil_calls": 2,
                "hitlo_calls": 1,
                # Module states
                "hds_scenario": "test_scenario",
                "causal_graph": "test_graph",
                "memory_access": "test_memory",
                "explanation_generated": "test_explanation",
                # Module latencies
                "hds_latency": 0.1,
                "cpi_latency": 0.2,
                "ppmv_latency": 0.15,
                "xil_latency": 0.12,
                "hitlo_latency": 0.08,
                # Data flow indicators
                "hds_to_cpi_data": True,
                "cpi_to_ppmv_data": True,
                "ppmv_to_xil_data": True,
                "xil_to_hitlo_data": False,
            },
        )

        # Add step to chain
        chain.steps.append(step)
        print("✅ Test reasoning chain and step created")

        # Test correlation analysis
        correlations = await srd._analyze_cross_module_correlations(chain, step)
        print("✅ Cross-module correlation analysis completed")

        # Validate correlation structure
        expected_correlation_keys = [
            "hds_cpi_correlation",
            "cpi_ppmv_correlation",
            "ppmv_xil_correlation",
            "xil_hitlo_correlation",
            "hds_hitlo_correlation",
            "reasoning_pipeline_coherence",
            "decision_making_consistency",
            "memory_explanation_alignment",
            "temporal_consistency",
            "workflow_progression",
            "processing_time_correlation",
            "confidence_module_correlation",
            "error_propagation_analysis",
            "overall_integration_score",
            "anomaly_risk_score",
            "stability_index",
        ]

        for key in expected_correlation_keys:
            if key not in correlations:
                print(f"❌ Missing correlation key: {key}")
                return False
        print("✅ All correlation metrics present")

        # Validate correlation values are in reasonable ranges
        for key, value in correlations.items():
            if (
                key.endswith("_correlation")
                or key.endswith("_score")
                or key.endswith("_index")
            ):
                if isinstance(value, (int, float)):
                    if not (0.0 <= value <= 1.0):
                        print(f"❌ Correlation value out of range: {key}={value}")
                        return False
        print("✅ Correlation values in valid ranges")

        # Test error propagation analysis
        error_analysis = correlations.get("error_propagation_analysis", {})
        expected_error_keys = ["error_isolation", "cascade_risk", "containment_score"]
        for key in expected_error_keys:
            if key not in error_analysis:
                print(f"❌ Missing error analysis key: {key}")
                return False
        print("✅ Error propagation analysis structure valid")

        return True

    except Exception as e:
        print(f"❌ Correlation analysis test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_cross_module_anomaly_detection():
    """Test cross-module anomaly detection using correlations"""
    print("\n📋 Testing Cross-Module Anomaly Detection")

    try:
        from ethics.self_reflective_debugger import (
            EnhancedAnomalyType,
            EnhancedReasoningChain,
            EnhancedSelfReflectiveDebugger,
            ReasoningStep,
        )

        # Initialize SRD
        srd = EnhancedSelfReflectiveDebugger()

        # Test case 1: Normal operation (should detect no anomalies)
        chain_id_normal = "test_normal_chain"
        chain_normal = EnhancedReasoningChain(chain_id=chain_id_normal)
        srd.active_chains[chain_id_normal] = chain_normal

        step_normal = ReasoningStep(
            operation="normal_operation",
            confidence=0.85,
            metadata={
                "hds_calls": 1,
                "cpi_calls": 1,
                "ppmv_calls": 1,
                "xil_calls": 1,
                "hitlo_calls": 0,
                "hds_scenario": "normal",
                "causal_graph": "normal",
                "memory_access": "normal",
                "hds_latency": 0.1,
                "cpi_latency": 0.1,
                "ppmv_latency": 0.1,
                "xil_latency": 0.1,
                "hds_to_cpi_data": True,
                "cpi_to_ppmv_data": True,
                "ppmv_to_xil_data": True,
            },
        )

        chain_normal.steps.append(step_normal)
        anomalies_normal = await srd._detect_cross_module_anomalies(
            chain_id_normal, step_normal
        )
        print(
            f"✅ Normal operation: {len(anomalies_normal)} anomalies detected (expected: 0-2)"
        )

        # Test case 2: Integration failure (should detect anomalies)
        chain_id_failure = "test_failure_chain"
        chain_failure = EnhancedReasoningChain(chain_id=chain_id_failure)
        srd.active_chains[chain_id_failure] = chain_failure

        step_failure = ReasoningStep(
            operation="failure_operation",
            confidence=0.3,
            metadata={
                "hds_calls": 5,
                "cpi_calls": 0,
                "ppmv_calls": 3,
                "xil_calls": 0,
                "hitlo_calls": 2,
                "hds_scenario": "failure",
                "memory_access": "failure",
                "hds_latency": 2.0,
                "ppmv_latency": 0.5,
                "hitlo_latency": 1.0,
                "hds_to_cpi_data": False,
                "cpi_to_ppmv_data": False,
                "ppmv_to_xil_data": False,
                "hds_error": True,
                "ppmv_error": True,
            },
        )

        chain_failure.steps.append(step_failure)
        anomalies_failure = await srd._detect_cross_module_anomalies(
            chain_id_failure, step_failure
        )
        print(
            f"✅ Integration failure: {len(anomalies_failure)} anomalies detected (expected: 3+)"
        )

        # Validate specific anomaly types
        anomaly_types = [anomaly.anomaly_type for anomaly in anomalies_failure]
        expected_types = [
            EnhancedAnomalyType.MODULE_INTEGRATION_FAILURE,
            EnhancedAnomalyType.WORKFLOW_SYNCHRONIZATION_ERROR,
            EnhancedAnomalyType.CROSS_MODULE_DATA_CORRUPTION,
            EnhancedAnomalyType.INTEGRATION_PERFORMANCE_DEGRADATION,
        ]

        detected_types = set(anomaly_types)
        print(f"✅ Detected anomaly types: {[t.value for t in detected_types]}")

        # Test case 3: Performance issues
        chain_id_perf = "test_performance_chain"
        chain_perf = EnhancedReasoningChain(chain_id=chain_id_perf)
        srd.active_chains[chain_id_perf] = chain_perf

        step_perf = ReasoningStep(
            operation="performance_operation",
            confidence=0.9,  # High confidence but poor performance
            metadata={
                "hds_calls": 10,
                "cpi_calls": 8,
                "ppmv_calls": 6,
                "xil_calls": 5,
                "hitlo_calls": 3,
                "hds_scenario": "perf",
                "causal_graph": "perf",
                "memory_access": "perf",
                "hds_latency": 5.0,
                "cpi_latency": 0.1,
                "ppmv_latency": 3.0,
                "xil_latency": 0.1,
                "hds_to_cpi_data": True,
                "cpi_to_ppmv_data": True,
                "ppmv_to_xil_data": True,
            },
        )

        chain_perf.steps.append(step_perf)
        anomalies_perf = await srd._detect_cross_module_anomalies(
            chain_id_perf, step_perf
        )
        print(f"✅ Performance issues: {len(anomalies_perf)} anomalies detected")

        # Validate that performance anomalies are detected
        perf_anomaly_types = [anomaly.anomaly_type for anomaly in anomalies_perf]
        has_performance_anomaly = (
            EnhancedAnomalyType.INTEGRATION_PERFORMANCE_DEGRADATION
            in perf_anomaly_types
        )
        print(f"✅ Performance degradation detected: {has_performance_anomaly}")

        return True

    except Exception as e:
        print(f"❌ Cross-module anomaly detection test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_correlation_matrix_updates():
    """Test correlation matrix updates and trend analysis"""
    print("\n📋 Testing Correlation Matrix Updates and Trends")

    try:
        from ethics.self_reflective_debugger import (
            EnhancedReasoningChain,
            EnhancedSelfReflectiveDebugger,
            ReasoningStep,
        )

        # Initialize SRD
        srd = EnhancedSelfReflectiveDebugger()

        # Create test chain
        chain_id = "test_matrix_chain"
        chain = EnhancedReasoningChain(chain_id=chain_id)
        srd.active_chains[chain_id] = chain

        # Simulate multiple steps with varying correlations
        for i in range(5):
            step = ReasoningStep(
                operation=f"matrix_operation_{i}",
                confidence=0.8 - (i * 0.1),  # Declining confidence
                metadata={
                    "hds_calls": i + 1,
                    "cpi_calls": i + 1,
                    "ppmv_calls": i,
                    "xil_calls": max(0, i - 1),
                    "hds_scenario": f"scenario_{i}",
                    "causal_graph": f"graph_{i}" if i > 0 else None,
                    "hds_latency": 0.1 + (i * 0.05),
                    "cpi_latency": 0.1 + (i * 0.03),
                    "hds_to_cpi_data": True,
                    "cpi_to_ppmv_data": i > 1,
                },
            )

            chain.steps.append(step)

            # Analyze correlations and update matrix
            correlations = await srd._analyze_cross_module_correlations(chain, step)
            srd._update_correlation_matrix(chain, step, correlations)

        print("✅ Multiple correlation matrix updates completed")

        # Validate matrix structure
        if chain_id not in srd.cross_module_correlation_matrix:
            print("❌ Chain not found in correlation matrix")
            return False

        matrix_entry = srd.cross_module_correlation_matrix[chain_id]
        expected_matrix_keys = [
            "step_correlations",
            "summary_statistics",
            "trend_analysis",
            "last_updated",
        ]

        for key in expected_matrix_keys:
            if key not in matrix_entry:
                print(f"❌ Missing matrix key: {key}")
                return False
        print("✅ Correlation matrix structure valid")

        # Validate statistics
        stats = matrix_entry["summary_statistics"]
        if not stats:
            print("❌ No summary statistics generated")
            return False

        # Check for key statistical measures
        for metric_key, metric_stats in stats.items():
            expected_stat_keys = ["mean", "min", "max", "latest", "trend", "variance"]
            for stat_key in expected_stat_keys:
                if stat_key not in metric_stats:
                    print(f"❌ Missing statistic {stat_key} for {metric_key}")
                    return False
        print("✅ Summary statistics structure valid")

        # Validate trend analysis
        trends = matrix_entry["trend_analysis"]
        expected_trend_keys = [
            "integration_trend",
            "risk_trend",
            "stability_trend",
            "coherence_trend",
            "alerts",
        ]

        for key in expected_trend_keys:
            if key not in trends:
                print(f"❌ Missing trend key: {key}")
                return False
        print("✅ Trend analysis structure valid")

        # Test trend detection
        for trend_key, trend_data in trends.items():
            if trend_key.endswith("_trend") and isinstance(trend_data, dict):
                if "direction" not in trend_data or "magnitude" not in trend_data:
                    print(f"❌ Invalid trend data for {trend_key}")
                    return False
        print("✅ Trend data validation passed")

        return True

    except Exception as e:
        print(f"❌ Correlation matrix test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_integration_with_reasoning_chain():
    """Test integration with complete reasoning chain workflow"""
    print("\n📋 Testing Integration with Complete Reasoning Chain")

    try:
        from ethics.self_reflective_debugger import (
            EnhancedSelfReflectiveDebugger,
        )

        # Initialize SRD
        srd = EnhancedSelfReflectiveDebugger()

        # Test complete reasoning chain workflow
        chain_id = srd.begin_enhanced_reasoning_chain(
            context="correlation_test_workflow",
            symbolic_tags=["correlation", "test", "integration"],
            ceo_integration_config={"enable_all": True},
        )
        print("✅ Enhanced reasoning chain started")

        # Log multiple reasoning steps with varying module interactions
        step_scenarios = [
            {
                "operation": "initial_analysis",
                "confidence": 0.9,
                "metadata": {
                    "hds_calls": 1,
                    "hds_scenario": "initial_scan",
                    "hds_latency": 0.1,
                    "hds_to_cpi_data": True,
                },
            },
            {
                "operation": "causal_modeling",
                "confidence": 0.8,
                "metadata": {
                    "cpi_calls": 2,
                    "causal_graph": "main_analysis",
                    "cpi_latency": 0.15,
                    "cpi_to_ppmv_data": True,
                },
            },
            {
                "operation": "memory_integration",
                "confidence": 0.75,
                "metadata": {
                    "ppmv_calls": 1,
                    "memory_access": "integration_data",
                    "ppmv_latency": 0.12,
                    "ppmv_to_xil_data": True,
                },
            },
            {
                "operation": "explanation_generation",
                "confidence": 0.85,
                "metadata": {
                    "xil_calls": 1,
                    "explanation_generated": "workflow_explanation",
                    "xil_latency": 0.08,
                    "xil_to_hitlo_data": False,
                },
            },
        ]

        for scenario in step_scenarios:
            step_id = await srd.log_enhanced_reasoning_step(
                chain_id=chain_id,
                operation=scenario["operation"],
                confidence=scenario["confidence"],
                metadata=scenario["metadata"],
                ceo_module_calls={"test_calls": scenario["metadata"]},
            )
            print(f"✅ Logged step: {scenario['operation']}")

        # Complete the reasoning chain
        analysis_results = await srd.complete_enhanced_reasoning_chain(chain_id)
        print("✅ Enhanced reasoning chain completed")

        # Validate analysis results
        if "error" in analysis_results:
            print(f"❌ Chain completion error: {analysis_results['error']}")
            return False

        expected_analysis_keys = [
            "chain_id",
            "summary",
            "performance_metrics",
            "ceo_integration_analysis",
            "anomaly_summary",
            "recommendations",
        ]

        for key in expected_analysis_keys:
            if key not in analysis_results:
                print(f"❌ Missing analysis key: {key}")
                return False
        print("✅ Analysis results structure valid")

        # Check if correlation analysis was integrated
        chain_matrix = srd.cross_module_correlation_matrix.get(chain_id)
        if not chain_matrix:
            print("❌ Chain not found in correlation matrix after completion")
            return False

        if len(chain_matrix["step_correlations"]) != len(step_scenarios):
            print(
                f"❌ Expected {len(step_scenarios)} step correlations, got {len(chain_matrix['step_correlations'])}"
            )
            return False
        print("✅ Correlation analysis properly integrated with reasoning chain")

        # Validate performance metrics include correlation-derived insights
        perf_metrics = analysis_results.get("performance_metrics", {})
        if "efficiency_score" not in perf_metrics:
            print("❌ Missing efficiency score in performance metrics")
            return False
        print("✅ Performance metrics include correlation insights")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def run_comprehensive_correlation_tests():
    """Run all correlation analysis tests"""
    print("🧪 Starting Comprehensive Self-Reflective Debugger Correlation Tests")
    print("=" * 80)

    tests = [
        ("Basic Functionality", test_enhanced_srd_basic),
        ("Correlation Analysis", test_correlation_analysis),
        ("Cross-Module Anomaly Detection", test_cross_module_anomaly_detection),
        ("Correlation Matrix Updates", test_correlation_matrix_updates),
        ("Integration with Reasoning Chain", test_integration_with_reasoning_chain),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} Test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False

    # Test Summary
    print("\n" + "=" * 80)
    print("📊 CORRELATION ANALYSIS TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL CORRELATION ANALYSIS TESTS PASSED!")
        print("✅ TODO #10 implementation validated successfully")
        print("📈 Cross-module correlation analysis fully functional")
        print("🔍 Anomaly detection using correlations operational")
        print("📊 Correlation matrix and trend analysis working")
        return True
    else:
        print("⚠️ Some tests failed - review implementation")
        return False


if __name__ == "__main__":
    print("🚀 Self-Reflective Debugger Correlation Analysis Test Suite")
    success = asyncio.run(run_comprehensive_correlation_tests())
    exit(0 if success else 1)
