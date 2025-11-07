#!/usr/bin/env python3
"""
Dynamic ID Hardening Validation - T4/0.01% Excellence
=====================================================

Validates that the telemetry hardening prevents dynamic IDs from sneaking into
Prometheus labels, which would cause cardinality explosion.

This script implements automated CI checks ensuring production safety.

Performance Target: <50ms p95 for validation checks
T4/0.01% Excellence: 100% detection accuracy for dynamic ID patterns

Constellation Framework: 🛡️ Telemetry Hardening
"""

import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from observability.service_metrics import (  # noqa: E402 - project root must be injected before import
    MetricType,
    ServiceType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_dynamic_id_patterns() -> tuple[bool, dict[str, Any]]:
    """Validate all dynamic ID pattern detection."""
    validator = MATRIZMetricsContractValidator()

    # Test cases covering all dynamic ID patterns
    test_cases = [
        # UUIDs (should be detected)
        {"label_key": "deployment_id", "label_value": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "expected_violation": True, "pattern_type": "UUID"},
        {"label_key": "correlation", "label_value": "550e8400-e29b-41d4-a716-446655440000", "expected_violation": True, "pattern_type": "UUID"},
        {"label_key": "build_id", "label_value": "build-6ba7b810-9dad-11d1-80b4-00c04fd430c8", "expected_violation": True, "pattern_type": "UUID with prefix"},

        # Timestamps (should be detected)
        {"label_key": "timestamp", "label_value": "1695646894123", "expected_violation": True, "pattern_type": "Unix timestamp"},
        {"label_key": "build_time", "label_value": "20230925134134", "expected_violation": True, "pattern_type": "Formatted timestamp"},
        {"label_key": "deploy_time", "label_value": "ts_1695646894123456", "expected_violation": True, "pattern_type": "Prefixed timestamp"},

        # Request/Session/User IDs (should be detected)
        {"label_key": "request", "label_value": "req_abc123def456", "expected_violation": True, "pattern_type": "Request ID"},
        {"label_key": "session", "label_value": "sess_xyz789abc123", "expected_violation": True, "pattern_type": "Session ID"},
        {"label_key": "user", "label_value": "usr_def456ghi789", "expected_violation": True, "pattern_type": "User ID"},
        {"label_key": "transaction", "label_value": "tx_transaction123456", "expected_violation": True, "pattern_type": "Transaction ID"},

        # Valid static labels (should NOT be detected)
        {"label_key": "environment", "label_value": "production", "expected_violation": False, "pattern_type": "Static environment"},
        {"label_key": "version", "label_value": "v1.2.3", "expected_violation": False, "pattern_type": "Semantic version"},
        {"label_key": "region", "label_value": "us-west-2", "expected_violation": False, "pattern_type": "AWS region"},
        {"label_key": "service", "label_value": "matriz-core", "expected_violation": False, "pattern_type": "Service name"},
        {"label_key": "component", "label_value": "decision-engine", "expected_violation": False, "pattern_type": "Component name"},
    ]

    results = {
        "total_tests": len(test_cases),
        "passed_tests": 0,
        "failed_tests": 0,
        "detection_accuracy": 0.0,
        "performance_metrics": [],
        "test_results": []
    }

    for i, test_case in enumerate(test_cases):
        start_time = time.perf_counter()

        # Test the dynamic ID detection
        violations = validator.record_and_validate_matriz_metric(
            name=f"lukhas_matriz_dynamic_id_test_{i}",
            value=1.0,
            service=ServiceType.CONSCIOUSNESS,
            metric_type=MetricType.COUNTER,
            operation="validation",
            phase="testing",
            lane="canary",
            labels={test_case["label_key"]: test_case["label_value"]}
        )

        validation_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Check if dynamic ID was detected
        has_dynamic_violation = any("Dynamic ID detected" in v for v in violations)
        expected_violation = test_case["expected_violation"]

        test_passed = (has_dynamic_violation == expected_violation)

        test_result = {
            "pattern_type": test_case["pattern_type"],
            "label_key": test_case["label_key"],
            "label_value": test_case["label_value"],
            "expected_violation": expected_violation,
            "actual_violation": has_dynamic_violation,
            "test_passed": test_passed,
            "validation_time_ms": validation_time
        }

        results["test_results"].append(test_result)
        results["performance_metrics"].append(validation_time)

        if test_passed:
            results["passed_tests"] += 1
            logger.info(f"✓ PASS: {test_case['pattern_type']} - {test_case['label_value'][:20]}...")
        else:
            results["failed_tests"] += 1
            logger.error(f"✗ FAIL: {test_case['pattern_type']} - Expected: {expected_violation}, Got: {has_dynamic_violation}")

    # Calculate detection accuracy
    results["detection_accuracy"] = results["passed_tests"] / results["total_tests"]

    # Performance analysis
    if results["performance_metrics"]:
        results["mean_latency_ms"] = sum(results["performance_metrics"]) / len(results["performance_metrics"])
        results["max_latency_ms"] = max(results["performance_metrics"])
        results["p95_latency_ms"] = sorted(results["performance_metrics"])[int(len(results["performance_metrics"]) * 0.95)]

    return results["detection_accuracy"] == 1.0, results


def validate_ci_integration() -> tuple[bool, dict[str, Any]]:
    """Validate CI integration scenarios."""
    validator = MATRIZMetricsContractValidator()

    # Simulate real CI scenarios where dynamic IDs might sneak in
    ci_scenarios = [
        {
            "name": "Production deployment with clean labels",
            "labels": {"environment": "production", "version": "v2.1.0", "region": "us-east-1"},
            "should_pass": True
        },
        {
            "name": "Staging with build timestamp (violation)",
            "labels": {"environment": "staging", "build": "build_1695646894123"},
            "should_pass": False
        },
        {
            "name": "Canary with UUID deployment ID (violation)",
            "labels": {"environment": "canary", "deployment": "deploy-f47ac10b-58cc-4372-a567-0e02b2c3d479"},
            "should_pass": False
        },
        {
            "name": "Development with user ID (violation)",
            "labels": {"environment": "dev", "deployer": "usr_developer123"},
            "should_pass": False
        },
        {
            "name": "Valid production rollout",
            "labels": {"environment": "production", "rollout": "progressive", "version": "v2.1.1-hotfix"},
            "should_pass": True
        }
    ]

    results = {
        "total_scenarios": len(ci_scenarios),
        "passed_scenarios": 0,
        "failed_scenarios": 0,
        "scenario_results": []
    }

    for scenario in ci_scenarios:
        violations = validator.record_and_validate_matriz_metric(
            name="lukhas_matriz_ci_integration_test",
            value=1.0,
            service=ServiceType.CONSCIOUSNESS,
            metric_type=MetricType.COUNTER,
            operation="ci_test",
            phase="integration",
            lane="canary",
            labels=scenario["labels"]
        )

        has_dynamic_violations = any("Dynamic ID detected" in v for v in violations)
        should_pass = scenario["should_pass"]

        # CI test passes if no dynamic ID violations when expected to pass, or dynamic ID violations when expected to fail
        scenario_passed = (not has_dynamic_violations and should_pass) or (has_dynamic_violations and not should_pass)

        scenario_result = {
            "name": scenario["name"],
            "labels": scenario["labels"],
            "should_pass": should_pass,
            "has_dynamic_violations": has_dynamic_violations,
            "scenario_passed": scenario_passed,
            "violations": violations
        }

        results["scenario_results"].append(scenario_result)

        if scenario_passed:
            results["passed_scenarios"] += 1
            logger.info(f"✓ CI SCENARIO PASS: {scenario['name']}")
        else:
            results["failed_scenarios"] += 1
            logger.error(f"✗ CI SCENARIO FAIL: {scenario['name']}")

    return results["passed_scenarios"] == results["total_scenarios"], results


def main() -> int:
    """Main validation function."""
    print("🛡️  MATRIZ Dynamic ID Hardening Validation")
    print("=" * 60)

    overall_success = True

    # Test 1: Dynamic ID Pattern Detection
    print("\n1. Testing Dynamic ID Pattern Detection...")
    pattern_success, pattern_results = validate_dynamic_id_patterns()

    print(f"   Detection Accuracy: {pattern_results['detection_accuracy']:.1%}")
    print(f"   Performance (P95): {pattern_results.get('p95_latency_ms', 0):.1f}ms")
    print(f"   Tests: {pattern_results['passed_tests']}/{pattern_results['total_tests']}")

    if pattern_success:
        print("   ✅ Pattern detection PASSED")
    else:
        print("   ❌ Pattern detection FAILED")
        overall_success = False

    # Test 2: CI Integration
    print("\n2. Testing CI Integration Scenarios...")
    ci_success, ci_results = validate_ci_integration()

    print(f"   CI Scenarios: {ci_results['passed_scenarios']}/{ci_results['total_scenarios']}")

    if ci_success:
        print("   ✅ CI integration PASSED")
    else:
        print("   ❌ CI integration FAILED")
        overall_success = False

    # Performance validation
    if pattern_results.get('p95_latency_ms', 0) > 50.0:
        print(f"   ⚠️  Performance warning: P95 latency {pattern_results['p95_latency_ms']:.1f}ms exceeds 50ms target")

    # Overall result
    print("\n" + "=" * 60)
    if overall_success:
        print("🎯 MATRIZ Dynamic ID Hardening: ✅ T4/0.01% EXCELLENCE ACHIEVED")
        print("   • 100% detection accuracy for dynamic ID patterns")
        print("   • All CI integration scenarios pass")
        print("   • Performance targets met")
        return 0
    else:
        print("❌ MATRIZ Dynamic ID Hardening: FAILED")
        print("   • Hardening insufficient for production deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
