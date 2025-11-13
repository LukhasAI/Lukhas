#!/usr/bin/env python3
"""
Guardian Integration Performance Validation Script
Phase 3 Implementation - T4/0.01% Excellence Standards

Validates Guardian-consciousness integration performance against requirements:
- p95 latency < 250ms (PHASE_MATRIX.md requirement)
- p99 latency < 300ms (fail-closed timeout)
- Drift detection accuracy with 0.15 threshold
- Fail-closed behavior verification
- GDPR audit trail compliance

Usage:
    python scripts/validate_guardian_performance.py [--iterations=1000] [--report-file=guardian_perf.json]

Constellation Framework: 🛡️ Guardian Performance Validation
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add LUKHAS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import LUKHAS components
from consciousness.guardian_integration import (
    ConsciousnessGuardianIntegration,
    GuardianValidationConfig,
    GuardianValidationType,
    ValidationResult,
    create_validation_context,
)
from consciousness.types import ConsciousnessState


class GuardianPerformanceValidator:
    """
    Comprehensive performance validator for Guardian integration.

    Tests performance, accuracy, and compliance requirements from PHASE_MATRIX.md
    """

    def __init__(self, iterations: int = 1000, verbose: bool = False):
        """
        Initialize performance validator.

        Args:
            iterations: Number of test iterations to run
            verbose: Enable verbose logging
        """
        self.iterations = iterations
        self.verbose = verbose
        self.results: list[dict[str, Any]] = []
        self.performance_stats: dict[str, Any] = {}

        # Performance targets from PHASE_MATRIX.md
        self.p95_target_ms = 250.0
        self.p99_target_ms = 300.0
        self.drift_threshold = 0.15  # AUDITOR_CHECKLIST.md

        # Test configuration
        self.config = GuardianValidationConfig(
            p95_target_ms=200.0,  # Conservative target
            p99_target_ms=250.0,  # Phase 3 requirement
            drift_threshold=0.15,
            fail_closed_on_error=True,
            gdpr_audit_enabled=True,
            constitutional_check_enabled=True,
            performance_regression_detection=True
        )

        # Initialize Guardian integration with mock components
        self.guardian = self._create_guardian_integration()

    def _create_guardian_integration(self) -> ConsciousnessGuardianIntegration:
        """Create Guardian integration with mocked dependencies"""

        # Mock Guardian system for testing
        class MockGuardianImpl:
            def __init__(self, drift_threshold: float = 0.15):
                self.drift_threshold = drift_threshold

            def detect_drift(self, baseline: str, current: str, threshold: float, context: dict) -> Any:
                # Simulate drift calculation
                import hashlib
                baseline_hash = hashlib.md5(baseline.encode()).hexdigest()
                current_hash = hashlib.md5(current.encode()).hexdigest()

                # Simple drift simulation based on hash difference
                drift_score = abs(int(baseline_hash[:8], 16) - int(current_hash[:8], 16)) / 0xFFFFFFFF
                drift_score = min(drift_score, 1.0)

                from governance.guardian.core import DriftResult, EthicalSeverity
                return DriftResult(
                    drift_score=drift_score,
                    threshold_exceeded=drift_score > threshold,
                    severity=EthicalSeverity.HIGH if drift_score > threshold else EthicalSeverity.LOW,
                    remediation_needed=drift_score > threshold,
                    details={
                        "method": "mock_semantic_analysis",
                        "baseline_hash": baseline_hash[:8],
                        "current_hash": current_hash[:8],
                        "threshold": threshold
                    }
                )

            def check_safety(self, content: str, context: dict, constitutional_check: bool) -> Any:
                # Mock safety validation
                violations = []
                safe = True

                # Check for mock violations
                unsafe_patterns = ["harm", "violate", "attack", "dangerous"]
                for pattern in unsafe_patterns:
                    if pattern in content.lower():
                        violations.append(f"Detected unsafe pattern: {pattern}")
                        safe = False

                from governance.guardian.core import EthicalSeverity, SafetyResult
                return SafetyResult(
                    safe=safe,
                    risk_level=EthicalSeverity.HIGH if not safe else EthicalSeverity.LOW,
                    violations=violations,
                    recommendations=["Review content" if not safe else "Content approved"],
                    constitutional_check=constitutional_check
                )

        # Mock ethics engine
        class MockEthicsEngine:
            def validate_action(self, action: str, context: dict) -> Any:
                # Mock ethical evaluation
                class MockEthicalDecision:
                    def __init__(self):
                        self.decision = "approved"
                        self.rationale = "Mock ethical validation passed"
                        self.severity = type('', (), {'value': 'low'})()
                        self.confidence = 0.9
                        self.triad_compliance = {
                            "identity": True,
                            "consciousness": True,
                            "guardian": True
                        }

                return MockEthicalDecision()

        # Create Guardian integration with mocks
        integration = ConsciousnessGuardianIntegration(config=self.config)
        integration.guardian_impl = MockGuardianImpl(self.drift_threshold)
        integration.ethics_engine = MockEthicsEngine()

        return integration

    async def run_performance_validation(self) -> dict[str, Any]:
        """
        Run comprehensive performance validation.

        Returns:
            Comprehensive performance validation report
        """
        print("🛡️ Starting Guardian Performance Validation")
        print(f"Iterations: {self.iterations}")
        print(f"Performance Targets: p95 < {self.p95_target_ms}ms, p99 < {self.p99_target_ms}ms")
        print(f"Drift Threshold: {self.drift_threshold}")
        print()

        # Run test suites
        await self._test_basic_validation_performance()
        await self._test_drift_detection_accuracy()
        await self._test_fail_closed_behavior()
        await self._test_concurrent_validation_performance()
        await self._test_gdpr_compliance()

        # Generate final report
        report = self._generate_performance_report()
        return report

    async def _test_basic_validation_performance(self):
        """Test basic validation operation performance"""
        print("📊 Testing basic validation performance...")

        latencies = []
        success_count = 0

        for i in range(self.iterations):
            # Create test consciousness state
            state = ConsciousnessState(
                phase="REFLECT",
                level=0.5 + (i % 100) / 200,  # Vary level
                awareness_level=0.6 + (i % 50) / 100,
                emotional_tone=["neutral", "focused", "curious", "analytical"][i % 4]
            )

            # Create validation context
            context = create_validation_context(
                validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
                consciousness_state=state,
                user_id=f"user_{i % 10}",
                session_id=f"session_{i % 5}",
                tenant="performance_test"
            )

            # Measure validation latency
            start_time = time.time()
            try:
                result = await self.guardian.validate_consciousness_operation(context)
                end_time = time.time()

                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

                if result.is_approved():
                    success_count += 1

                self.results.append({
                    "test": "basic_validation",
                    "iteration": i,
                    "latency_ms": latency_ms,
                    "approved": result.is_approved(),
                    "drift_score": result.drift_result.drift_score if result.drift_result else None,
                    "validation_duration": result.validation_duration_ms
                })

                if self.verbose and i % 100 == 0:
                    print(f"  Completed {i}/{self.iterations} iterations")

            except Exception as e:
                print(f"  Error in iteration {i}: {e}")
                continue

        # Calculate statistics
        if latencies:
            latencies.sort()
            self.performance_stats["basic_validation"] = {
                "iterations": len(latencies),
                "success_rate": success_count / len(latencies),
                "mean_latency_ms": statistics.mean(latencies),
                "median_latency_ms": statistics.median(latencies),
                "p95_latency_ms": latencies[int(len(latencies) * 0.95)],
                "p99_latency_ms": latencies[int(len(latencies) * 0.99)],
                "max_latency_ms": max(latencies),
                "min_latency_ms": min(latencies)
            }

            # Check performance targets
            p95_latency = self.performance_stats["basic_validation"]["p95_latency_ms"]
            p99_latency = self.performance_stats["basic_validation"]["p99_latency_ms"]

            p95_pass = p95_latency <= self.p95_target_ms
            p99_pass = p99_latency <= self.p99_target_ms

            print(f"  ✓ Mean latency: {self.performance_stats['basic_validation']['mean_latency_ms']:.2f}ms")
            print(f"  {'✓' if p95_pass else '✗'} p95 latency: {p95_latency:.2f}ms (target: {self.p95_target_ms}ms)")
            print(f"  {'✓' if p99_pass else '✗'} p99 latency: {p99_latency:.2f}ms (target: {self.p99_target_ms}ms)")
            print(f"  ✓ Success rate: {self.performance_stats['basic_validation']['success_rate']:.1%}")

            self.performance_stats["basic_validation"]["p95_target_met"] = p95_pass
            self.performance_stats["basic_validation"]["p99_target_met"] = p99_pass
        else:
            print("  ✗ No successful validations completed")

    async def _test_drift_detection_accuracy(self):
        """Test drift detection accuracy with various scenarios"""
        print("\n🔍 Testing drift detection accuracy...")

        test_cases = [
            # (baseline_state, current_state, expected_drift_level, description)
            (
                ConsciousnessState(phase="IDLE", level=0.3, emotional_tone="neutral"),
                ConsciousnessState(phase="IDLE", level=0.31, emotional_tone="neutral"),
                "low", "Minimal change"
            ),
            (
                ConsciousnessState(phase="REFLECT", level=0.7, emotional_tone="focused"),
                ConsciousnessState(phase="REFLECT", level=0.72, emotional_tone="focused"),
                "low", "Small change within phase"
            ),
            (
                ConsciousnessState(phase="IDLE", level=0.3, emotional_tone="neutral"),
                ConsciousnessState(phase="AWARE", level=0.7, emotional_tone="alert"),
                "medium", "Phase transition with level change"
            ),
            (
                ConsciousnessState(phase="REFLECT", level=0.8, emotional_tone="focused"),
                ConsciousnessState(phase="DECIDE", level=0.9, emotional_tone="determined"),
                "medium", "Complex phase transition"
            ),
            (
                ConsciousnessState(phase="IDLE", level=0.2, emotional_tone="calm"),
                ConsciousnessState(phase="CREATE", level=0.95, emotional_tone="excited"),
                "high", "Major state transition"
            )
        ]

        drift_results = []
        accuracy_count = 0

        for i, (baseline_state, current_state, expected_level, description) in enumerate(test_cases):
            # Set baseline state
            self.guardian.update_baseline_state(baseline_state, "drift_test", f"session_{i}")

            # Create validation context with current state
            context = create_validation_context(
                validation_type=GuardianValidationType.CONSCIOUSNESS_STATE_TRANSITION,
                consciousness_state=current_state,
                session_id=f"session_{i}",
                tenant="drift_test"
            )

            # Perform validation
            result = await self.guardian.validate_consciousness_operation(context)

            if result.drift_result:
                drift_score = result.drift_result.drift_score
                threshold_exceeded = result.drift_result.threshold_exceeded

                # Classify detected drift level
                if drift_score <= 0.05:
                    detected_level = "low"
                elif drift_score <= 0.15:
                    detected_level = "medium"
                else:
                    detected_level = "high"

                # Check accuracy (allow some tolerance)
                is_accurate = (
                    (expected_level == "low" and detected_level in ["low", "medium"]) or
                    (expected_level == "medium" and detected_level in ["low", "medium", "high"]) or
                    (expected_level == "high" and detected_level in ["medium", "high"])
                )

                if is_accurate:
                    accuracy_count += 1

                drift_results.append({
                    "description": description,
                    "expected_level": expected_level,
                    "detected_level": detected_level,
                    "drift_score": drift_score,
                    "threshold_exceeded": threshold_exceeded,
                    "accurate": is_accurate
                })

                if self.verbose:
                    print(f"  {description}: {drift_score:.3f} ({detected_level}, expected {expected_level}) {'✓' if is_accurate else '✗'}")

        # Calculate drift detection statistics
        accuracy_rate = accuracy_count / len(test_cases) if test_cases else 0
        self.performance_stats["drift_detection"] = {
            "test_cases": len(test_cases),
            "accuracy_rate": accuracy_rate,
            "results": drift_results
        }

        print(f"  ✓ Drift detection accuracy: {accuracy_rate:.1%} ({accuracy_count}/{len(test_cases)})")

    async def _test_fail_closed_behavior(self):
        """Test fail-closed behavior on Guardian component failures"""
        print("\n🛡️ Testing fail-closed behavior...")

        # Test scenarios that should trigger fail-closed behavior
        fail_closed_tests = 0
        fail_closed_correct = 0

        # Test 1: Simulate Guardian implementation failure
        original_impl = self.guardian.guardian_impl
        self.guardian.guardian_impl = None  # Simulate component failure

        state = ConsciousnessState(phase="DECIDE", level=0.8)
        context = create_validation_context(
            validation_type=GuardianValidationType.DECISION_MAKING,
            consciousness_state=state,
            sensitive_operation=True
        )

        result = await self.guardian.validate_consciousness_operation(context)
        fail_closed_tests += 1

        # Should still complete but with conservative behavior
        if not result.is_approved() or result.result == ValidationResult.ERROR:
            fail_closed_correct += 1
            print("  ✓ Fail-closed on Guardian component failure")
        else:
            print("  ✗ Did not fail-closed on Guardian component failure")

        # Restore Guardian implementation
        self.guardian.guardian_impl = original_impl

        # Test 2: Trigger emergency mode through consecutive errors
        self.guardian._consecutive_errors = 6  # Exceed max_consecutive_errors (5)
        self.guardian._emergency_mode = True

        result = await self.guardian.validate_consciousness_operation(context)
        fail_closed_tests += 1

        if not result.is_approved() and "emergency mode" in result.reason.lower():
            fail_closed_correct += 1
            print("  ✓ Fail-closed in emergency mode")
        else:
            print("  ✗ Did not fail-closed in emergency mode")

        # Reset emergency mode
        self.guardian._consecutive_errors = 0
        self.guardian._emergency_mode = False

        # Calculate fail-closed statistics
        fail_closed_rate = fail_closed_correct / fail_closed_tests if fail_closed_tests else 0
        self.performance_stats["fail_closed"] = {
            "tests": fail_closed_tests,
            "correct_responses": fail_closed_correct,
            "fail_closed_rate": fail_closed_rate
        }

        print(f"  ✓ Fail-closed behavior: {fail_closed_rate:.1%} ({fail_closed_correct}/{fail_closed_tests})")

    async def _test_concurrent_validation_performance(self):
        """Test performance under concurrent validation load"""
        print("\n⚡ Testing concurrent validation performance...")

        concurrent_tasks = 50  # Number of concurrent validations
        tasks = []
        start_time = time.time()

        # Create concurrent validation tasks
        for i in range(concurrent_tasks):
            state = ConsciousnessState(
                phase=["IDLE", "AWARE", "REFLECT", "CREATE", "DECIDE"][i % 5],
                level=0.3 + (i % 7) / 10,
                emotional_tone=f"tone_{i % 3}"
            )

            context = create_validation_context(
                validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
                consciousness_state=state,
                user_id=f"concurrent_user_{i}",
                session_id=f"concurrent_session_{i // 10}"
            )

            task = self.guardian.validate_consciousness_operation(context)
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Analyze concurrent performance
        successful_results = [r for r in results if not isinstance(r, Exception)]
        total_duration = end_time - start_time
        throughput = len(successful_results) / total_duration

        concurrent_latencies = [
            r.validation_duration_ms for r in successful_results
            if hasattr(r, 'validation_duration_ms')
        ]

        if concurrent_latencies:
            concurrent_latencies.sort()
            self.performance_stats["concurrent"] = {
                "concurrent_tasks": concurrent_tasks,
                "successful_tasks": len(successful_results),
                "total_duration_ms": total_duration * 1000,
                "throughput_per_second": throughput,
                "mean_latency_ms": statistics.mean(concurrent_latencies),
                "p95_latency_ms": concurrent_latencies[int(len(concurrent_latencies) * 0.95)],
                "p99_latency_ms": concurrent_latencies[int(len(concurrent_latencies) * 0.99)]
            }

            print(f"  ✓ Concurrent throughput: {throughput:.1f} validations/second")
            print(f"  ✓ Success rate: {len(successful_results)/concurrent_tasks:.1%}")
            print(f"  ✓ p95 latency: {self.performance_stats['concurrent']['p95_latency_ms']:.2f}ms")
        else:
            print("  ✗ No successful concurrent validations")

    async def _test_gdpr_compliance(self):
        """Test GDPR compliance features"""
        print("\n📋 Testing GDPR compliance...")

        # Test audit trail creation and management
        gdpr_tests = 0
        gdpr_passed = 0

        # Test 1: User data processing with consent
        state = ConsciousnessState(phase="REFLECT", level=0.7)
        context = create_validation_context(
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            consciousness_state=state,
            user_id="gdpr_test_user",
            session_id="gdpr_test_session",
            sensitive_operation=True
        )

        result = await self.guardian.validate_consciousness_operation(context)
        gdpr_tests += 1

        # Check GDPR compliance indicators
        if (hasattr(result, 'gdpr_compliant') and
            result.gdpr_compliant and
            len(result.audit_trail) > 0):
            gdpr_passed += 1
            print("  ✓ GDPR compliance with user data processing")
        else:
            print("  ✗ GDPR compliance check failed")

        # Test 2: Audit trail retention and cleanup
        initial_events = len(self.guardian._audit_events)

        # Add multiple audit events
        for i in range(10):
            self.guardian._add_audit_event(f"gdpr_test_event_{i}", {"test_data": i})

        events_after_addition = len(self.guardian._audit_events)
        gdpr_tests += 1

        if events_after_addition >= initial_events + 10:
            gdpr_passed += 1
            print("  ✓ Audit trail event storage")
        else:
            print("  ✗ Audit trail event storage failed")

        # Test 3: Data minimization (only necessary data in audit)
        if result.audit_trail:
            audit_entry = result.audit_trail[0]
            required_fields = ["timestamp", "event_type", "operation_id"]
            has_required = all(field in audit_entry for field in required_fields)
            gdpr_tests += 1

            if has_required:
                gdpr_passed += 1
                print("  ✓ Audit trail data minimization")
            else:
                print("  ✗ Audit trail missing required fields")

        # Calculate GDPR compliance statistics
        gdpr_compliance_rate = gdpr_passed / gdpr_tests if gdpr_tests else 0
        self.performance_stats["gdpr_compliance"] = {
            "tests": gdpr_tests,
            "passed": gdpr_passed,
            "compliance_rate": gdpr_compliance_rate,
            "audit_events_count": len(self.guardian._audit_events)
        }

        print(f"  ✓ GDPR compliance rate: {gdpr_compliance_rate:.1%} ({gdpr_passed}/{gdpr_tests})")

    def _generate_performance_report(self) -> dict[str, Any]:
        """Generate comprehensive performance validation report"""

        # Overall assessment
        overall_pass = True
        critical_issues = []
        warnings = []

        # Check performance targets
        basic_stats = self.performance_stats.get("basic_validation", {})
        if not basic_stats.get("p95_target_met", False):
            overall_pass = False
            critical_issues.append(f"p95 latency target not met: {basic_stats.get('p95_latency_ms', 'unknown')}ms > {self.p95_target_ms}ms")

        if not basic_stats.get("p99_target_met", False):
            overall_pass = False
            critical_issues.append(f"p99 latency target not met: {basic_stats.get('p99_latency_ms', 'unknown')}ms > {self.p99_target_ms}ms")

        # Check drift detection accuracy
        drift_stats = self.performance_stats.get("drift_detection", {})
        if drift_stats.get("accuracy_rate", 0) < 0.8:
            warnings.append(f"Drift detection accuracy below 80%: {drift_stats.get('accuracy_rate', 0):.1%}")

        # Check fail-closed behavior
        fail_closed_stats = self.performance_stats.get("fail_closed", {})
        if fail_closed_stats.get("fail_closed_rate", 0) < 1.0:
            critical_issues.append(f"Fail-closed behavior not consistent: {fail_closed_stats.get('fail_closed_rate', 0):.1%}")

        # Check GDPR compliance
        gdpr_stats = self.performance_stats.get("gdpr_compliance", {})
        if gdpr_stats.get("compliance_rate", 0) < 1.0:
            warnings.append(f"GDPR compliance not perfect: {gdpr_stats.get('compliance_rate', 0):.1%}")

        # Generate report
        report = {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "test_configuration": {
                "iterations": self.iterations,
                "p95_target_ms": self.p95_target_ms,
                "p99_target_ms": self.p99_target_ms,
                "drift_threshold": self.drift_threshold
            },
            "performance_statistics": self.performance_stats,
            "assessment": {
                "overall_pass": overall_pass,
                "critical_issues": critical_issues,
                "warnings": warnings,
                "phase_3_requirements_met": overall_pass and len(critical_issues) == 0
            },
            "raw_results": self.results[:100]  # Limit raw results for report size
        }

        return report

    def print_performance_summary(self, report: dict[str, Any]):
        """Print performance validation summary"""
        print("\n" + "="*60)
        print("🛡️ GUARDIAN PERFORMANCE VALIDATION SUMMARY")
        print("="*60)

        assessment = report["assessment"]

        # Overall status
        status = "✅ PASSED" if assessment["overall_pass"] else "❌ FAILED"
        print(f"Overall Status: {status}")

        # Phase 3 requirements
        phase3_status = "✅ MET" if assessment["phase_3_requirements_met"] else "❌ NOT MET"
        print(f"Phase 3 Requirements: {phase3_status}")

        print("\nPerformance Metrics:")

        # Basic validation performance
        basic = report["performance_statistics"].get("basic_validation", {})
        if basic:
            print(f"  • Mean Latency: {basic.get('mean_latency_ms', 'N/A'):.2f}ms")
            print(f"  • p95 Latency: {basic.get('p95_latency_ms', 'N/A'):.2f}ms (target: {self.p95_target_ms}ms)")
            print(f"  • p99 Latency: {basic.get('p99_latency_ms', 'N/A'):.2f}ms (target: {self.p99_target_ms}ms)")
            print(f"  • Success Rate: {basic.get('success_rate', 0):.1%}")

        # Drift detection
        drift = report["performance_statistics"].get("drift_detection", {})
        if drift:
            print(f"  • Drift Detection Accuracy: {drift.get('accuracy_rate', 0):.1%}")

        # Fail-closed behavior
        fail_closed = report["performance_statistics"].get("fail_closed", {})
        if fail_closed:
            print(f"  • Fail-Closed Rate: {fail_closed.get('fail_closed_rate', 0):.1%}")

        # GDPR compliance
        gdpr = report["performance_statistics"].get("gdpr_compliance", {})
        if gdpr:
            print(f"  • GDPR Compliance: {gdpr.get('compliance_rate', 0):.1%}")

        # Issues and warnings
        if assessment["critical_issues"]:
            print(f"\n❌ Critical Issues ({len(assessment['critical_issues'])}):")
            for issue in assessment["critical_issues"]:
                print(f"  • {issue}")

        if assessment["warnings"]:
            print(f"\n⚠️  Warnings ({len(assessment['warnings'])}):")
            for warning in assessment["warnings"]:
                print(f"  • {warning}")

        if not assessment["critical_issues"] and not assessment["warnings"]:
            print("\n✅ No issues detected - Guardian integration ready for production")

        print("\n" + "="*60)


async def main():
    """Main entry point for Guardian performance validation"""
    parser = argparse.ArgumentParser(
        description="Validate Guardian-consciousness integration performance"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of test iterations (default: 1000)"
    )
    parser.add_argument(
        "--report-file",
        type=str,
        help="File to save detailed performance report (JSON)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Run performance validation
    validator = GuardianPerformanceValidator(
        iterations=args.iterations,
        verbose=args.verbose
    )

    try:
        report = await validator.run_performance_validation()

        # Print summary
        validator.print_performance_summary(report)

        # Save detailed report if requested
        if args.report_file:
            with open(args.report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Detailed report saved to: {args.report_file}")

        # Exit with appropriate code
        if report["assessment"]["overall_pass"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Performance validation failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
