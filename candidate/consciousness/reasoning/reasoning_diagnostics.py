"""
Reasoning Diagnostics
Comprehensive diagnostics and health checks for the reasoning system
"""

import asyncio
import traceback
import unittest
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger
from reasoning.adaptive_reasoning_loop import AdaptiveReasoningLoop, ReasoningContext
from reasoning.reasoning_engine import SymbolicEngine
from reasoning.reasoning_metrics import get_metrics_calculator
from reasoning.trace_summary_builder import TraceSummaryBuilder

logger = get_logger(__name__)


class DiagnosticLevel(Enum):
    """Diagnostic severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DiagnosticResult:
    """Result of a diagnostic check"""

    def __init__(
        self,
        check_name: str,
        level: DiagnosticLevel,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ):
        self.check_name = check_name
        self.level = level
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_name": self.check_name,
            "level": self.level.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class ReasoningDiagnostics:
    """
    Comprehensive diagnostics for the reasoning system
    """

    def __init__(self):
        self.diagnostic_history = []
        self.health_status = "unknown"
        self.last_check_time = None
        self.check_interval = timedelta(minutes=5)
        self.diagnostic_thresholds = {
            "logic_drift": 0.3,
            "recall_efficiency": 0.5,
            "coherence_score": 0.6,
            "confidence_calibration": 0.5,
            "error_rate": 0.1,
            "response_time": 5.0,  # seconds
        }

    async def run_full_diagnostics(self) -> dict[str, Any]:
        """
        Run comprehensive diagnostics on the reasoning system
        """
        logger.info("Starting full reasoning diagnostics")

        results = []
        start_time = datetime.now()

        # Component health checks
        results.extend(await self._check_component_health())

        # Performance diagnostics
        results.extend(await self._check_performance_metrics())

        # Logic consistency checks
        results.extend(await self._check_logic_consistency())

        # Memory integration checks
        results.extend(await self._check_memory_integration())

        # Stability checks
        results.extend(await self._check_system_stability())

        # Update health status
        self._update_health_status(results)

        # Create summary
        summary = {
            "status": self.health_status,
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - start_time).total_seconds(),
            "total_checks": len(results),
            "results_by_level": self._summarize_by_level(results),
            "critical_issues": [r for r in results if r.level == DiagnosticLevel.CRITICAL],
            "recommendations": self._generate_recommendations(results),
        }

        # Store results
        self.diagnostic_history.append({"timestamp": datetime.now(), "results": results, "summary": summary})

        self.last_check_time = datetime.now()

        return summary

    async def _check_component_health(self) -> list[DiagnosticResult]:
        """Check health of individual reasoning components"""
        results = []

        # Check Adaptive Reasoning Loop
        try:
            loop = AdaptiveReasoningLoop()
            test_context = ReasoningContext("test query", "general")

            # Quick test
            result = await asyncio.wait_for(loop.start_reasoning(test_context), timeout=5.0)

            if result.get("status") in ["completed", "max_iterations_reached"]:
                results.append(
                    DiagnosticResult(
                        "adaptive_reasoning_loop",
                        DiagnosticLevel.INFO,
                        "Adaptive reasoning loop is functional",
                        {"test_result": result},
                    )
                )
            else:
                results.append(
                    DiagnosticResult(
                        "adaptive_reasoning_loop",
                        DiagnosticLevel.WARNING,
                        "Adaptive reasoning loop returned unexpected status",
                        {"status": result.get("status")},
                    )
                )

        except asyncio.TimeoutError:
            results.append(
                DiagnosticResult(
                    "adaptive_reasoning_loop",
                    DiagnosticLevel.ERROR,
                    "Adaptive reasoning loop timeout",
                    {"timeout": 5.0},
                )
            )
        except Exception as e:
            results.append(
                DiagnosticResult(
                    "adaptive_reasoning_loop",
                    DiagnosticLevel.ERROR,
                    f"Adaptive reasoning loop error: {e!s}",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )
            )

        # Check Symbolic Engine
        try:
            engine = SymbolicEngine()
            test_input = {
                "text": "Test diagnostic input",
                "context": {"diagnostic": True},
            }

            # Test reasoning
            engine.reason(test_input)

            results.append(
                DiagnosticResult(
                    "symbolic_engine",
                    DiagnosticLevel.INFO,
                    "Symbolic engine is functional",
                )
            )

        except Exception as e:
            results.append(
                DiagnosticResult(
                    "symbolic_engine",
                    DiagnosticLevel.ERROR,
                    f"Symbolic engine error: {e!s}",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )
            )

        # Check Trace Summary Builder
        try:
            builder = TraceSummaryBuilder()
            test_trace = {"type": "diagnostic", "content": "test", "confidence": 0.8}

            summary = await builder.build_summary(test_trace, "technical")

            if "error" not in summary:
                results.append(
                    DiagnosticResult(
                        "trace_summary_builder",
                        DiagnosticLevel.INFO,
                        "Trace summary builder is functional",
                    )
                )
            else:
                results.append(
                    DiagnosticResult(
                        "trace_summary_builder",
                        DiagnosticLevel.WARNING,
                        f"Trace summary builder error: {summary['error']}",
                    )
                )

        except Exception as e:
            results.append(
                DiagnosticResult(
                    "trace_summary_builder",
                    DiagnosticLevel.ERROR,
                    f"Trace summary builder error: {e!s}",
                    {"error": str(e), "traceback": traceback.format_exc()},
                )
            )

        return results

    async def _check_performance_metrics(self) -> list[DiagnosticResult]:
        """Check system performance metrics"""
        results = []

        calculator = get_metrics_calculator()

        # Check metric trends
        trends = calculator.get_metric_trends()

        if not trends:
            results.append(
                DiagnosticResult(
                    "performance_metrics",
                    DiagnosticLevel.WARNING,
                    "No performance metric history available",
                )
            )
            return results

        # Analyze each metric
        for metric_name, values in trends.items():
            if not values:
                continue

            avg_value = sum(values) / len(values)

            # Check against thresholds
            if metric_name in self.diagnostic_thresholds:
                threshold = self.diagnostic_thresholds[metric_name]

                if metric_name == "logic_drift":
                    # For drift, lower is better
                    if avg_value > threshold:
                        results.append(
                            DiagnosticResult(
                                f"metric_{metric_name}",
                                DiagnosticLevel.WARNING,
                                f"High {metric_name}: {avg_value:.3f} (threshold: {threshold})",
                                {"average": avg_value, "recent_values": values[-5:]},
                            )
                        )
                else:
                    # For other metrics, higher is better
                    if avg_value < threshold:
                        results.append(
                            DiagnosticResult(
                                f"metric_{metric_name}",
                                DiagnosticLevel.WARNING,
                                f"Low {metric_name}: {avg_value:.3f} (threshold: {threshold})",
                                {"average": avg_value, "recent_values": values[-5:]},
                            )
                        )

        # Check for metric degradation
        if "overall_score" in trends and len(trends["overall_score"]) >= 5:
            recent_scores = trends["overall_score"][-5:]
            if all(recent_scores[i] < recent_scores[i - 1] for i in range(1, len(recent_scores))):
                results.append(
                    DiagnosticResult(
                        "metric_degradation",
                        DiagnosticLevel.WARNING,
                        "Consistent performance degradation detected",
                        {"recent_scores": recent_scores},
                    )
                )

        return results

    async def _check_logic_consistency(self) -> list[DiagnosticResult]:
        """Check logical consistency of reasoning"""
        results = []

        # Test logic fallbacks
        try:
            engine = SymbolicEngine()

            # Test various edge cases
            test_cases = [
                {"text": "", "context": {}},  # Empty input
                {"text": "A and not A", "context": {}},  # Contradiction
                {"text": "If P then Q, P", "context": {}},  # Simple deduction
            ]

            for i, test_case in enumerate(test_cases):
                try:
                    result = engine.reason(test_case)
                    # Check for logical inconsistencies
                    if "contradiction" in str(result).lower():
                        results.append(
                            DiagnosticResult(
                                f"logic_consistency_test_{i}",
                                DiagnosticLevel.INFO,
                                "Contradiction detected correctly",
                            )
                        )
                except Exception as e:
                    results.append(
                        DiagnosticResult(
                            f"logic_consistency_test_{i}",
                            DiagnosticLevel.WARNING,
                            f"Logic test {i} failed: {e!s}",
                            {"test_case": test_case},
                        )
                    )

        except Exception as e:
            results.append(
                DiagnosticResult(
                    "logic_consistency",
                    DiagnosticLevel.ERROR,
                    f"Logic consistency check failed: {e!s}",
                )
            )

        # Test unstable inference detection
        # #ΛDIAGNOSE: reasoning_drift
        try:
            loop = AdaptiveReasoningLoop()

            # Run same query multiple times
            query = "What is the meaning of life?"
            results_list = []

            for _ in range(3):
                context = ReasoningContext(query, "philosophical")
                result = await loop.start_reasoning(context)
                results_list.append(result)

            # Check for consistency
            conclusions = [r.get("conclusion") for r in results_list]
            unique_conclusions = len({str(c) for c in conclusions})

            if unique_conclusions > 2:
                results.append(
                    DiagnosticResult(
                        "inference_stability",
                        DiagnosticLevel.WARNING,
                        "Unstable inference detected - different conclusions for same query",
                        {
                            "unique_conclusions": unique_conclusions,
                            "conclusions": conclusions,
                        },
                    )
                )
            else:
                results.append(
                    DiagnosticResult(
                        "inference_stability",
                        DiagnosticLevel.INFO,
                        "Inference is stable",
                    )
                )

        except Exception as e:
            results.append(
                DiagnosticResult(
                    "inference_stability",
                    DiagnosticLevel.ERROR,
                    f"Inference stability check failed: {e!s}",
                )
            )

        return results

    async def _check_memory_integration(self) -> list[DiagnosticResult]:
        """Check integration with memory system"""
        results = []

        try:
            # Test memory recall efficiency
            test_memories = [
                {"key": "test1", "content": "Test memory 1"},
                {"key": "test2", "content": "Test memory 2"},
            ]

            calculator = get_metrics_calculator()

            # Test perfect recall
            efficiency = calculator._calculate_recall_efficiency(test_memories, test_memories)

            if efficiency >= 0.9:
                results.append(
                    DiagnosticResult(
                        "memory_recall_perfect",
                        DiagnosticLevel.INFO,
                        "Perfect memory recall functioning correctly",
                        {"efficiency": efficiency},
                    )
                )

            # Test partial recall
            partial_recall = [test_memories[0]]
            efficiency = calculator._calculate_recall_efficiency(partial_recall, test_memories)

            if 0.4 <= efficiency <= 0.6:
                results.append(
                    DiagnosticResult(
                        "memory_recall_partial",
                        DiagnosticLevel.INFO,
                        "Partial memory recall functioning correctly",
                        {"efficiency": efficiency},
                    )
                )
            else:
                results.append(
                    DiagnosticResult(
                        "memory_recall_partial",
                        DiagnosticLevel.WARNING,
                        f"Unexpected partial recall efficiency: {efficiency}",
                    )
                )

        except Exception as e:
            results.append(
                DiagnosticResult(
                    "memory_integration",
                    DiagnosticLevel.ERROR,
                    f"Memory integration check failed: {e!s}",
                )
            )

        return results

    async def _check_system_stability(self) -> list[DiagnosticResult]:
        """Check overall system stability"""
        results = []

        # Check diagnostic history for recurring issues
        if len(self.diagnostic_history) >= 5:
            recent_diagnostics = self.diagnostic_history[-5:]

            # Count errors and warnings
            error_counts = defaultdict(int)
            warning_counts = defaultdict(int)

            for diagnostic in recent_diagnostics:
                for result in diagnostic["results"]:
                    if result.level == DiagnosticLevel.ERROR:
                        error_counts[result.check_name] += 1
                    elif result.level == DiagnosticLevel.WARNING:
                        warning_counts[result.check_name] += 1

            # Check for recurring errors
            for check_name, count in error_counts.items():
                if count >= 3:
                    results.append(
                        DiagnosticResult(
                            "recurring_error",
                            DiagnosticLevel.CRITICAL,
                            f"Recurring error in {check_name}: {count} times in last 5 checks",
                            {"check_name": check_name, "count": count},
                        )
                    )

            # Check for persistent warnings
            for check_name, count in warning_counts.items():
                if count >= 4:
                    results.append(
                        DiagnosticResult(
                            "persistent_warning",
                            DiagnosticLevel.WARNING,
                            f"Persistent warning in {check_name}: {count} times in last 5 checks",
                            {"check_name": check_name, "count": count},
                        )
                    )

        return results

    def _update_health_status(self, results: list[DiagnosticResult]):
        """Update overall health status based on diagnostic results"""
        critical_count = sum(1 for r in results if r.level == DiagnosticLevel.CRITICAL)
        error_count = sum(1 for r in results if r.level == DiagnosticLevel.ERROR)
        warning_count = sum(1 for r in results if r.level == DiagnosticLevel.WARNING)

        if critical_count > 0:
            self.health_status = "critical"
        elif error_count > 2:
            self.health_status = "unhealthy"
        elif warning_count > 5:
            self.health_status = "degraded"
        else:
            self.health_status = "healthy"

    def _summarize_by_level(self, results: list[DiagnosticResult]) -> dict[str, int]:
        """Summarize results by diagnostic level"""
        summary = defaultdict(int)
        for result in results:
            summary[result.level.value] += 1
        return dict(summary)

    def _generate_recommendations(self, results: list[DiagnosticResult]) -> list[str]:
        """Generate actionable recommendations based on diagnostic results"""
        recommendations = []

        # Check for critical issues
        critical_issues = [r for r in results if r.level == DiagnosticLevel.CRITICAL]
        if critical_issues:
            recommendations.append("URGENT: Address critical issues immediately. System stability at risk.")

        # Check for performance issues
        perf_issues = [
            r
            for r in results
            if "metric_" in r.check_name and r.level in [DiagnosticLevel.WARNING, DiagnosticLevel.ERROR]
        ]
        if perf_issues:
            recommendations.append("Review and optimize reasoning strategies. Performance metrics below threshold.")

        # Check for logic issues
        logic_issues = [r for r in results if "logic" in r.check_name.lower() and r.level != DiagnosticLevel.INFO]
        if logic_issues:
            recommendations.append("Investigate logical consistency issues. Consider adjusting inference parameters.")

        # Check for stability issues
        stability_issues = [
            r for r in results if "stability" in r.check_name.lower() or "drift" in r.check_name.lower()
        ]
        if stability_issues:
            recommendations.append("System showing signs of instability. Implement drift correction mechanisms.")

        if not recommendations:
            recommendations.append("System operating within normal parameters. Continue monitoring.")

        return recommendations

    async def quick_health_check(self) -> dict[str, Any]:
        """Perform a quick health check"""
        if self.last_check_time and datetime.now() - self.last_check_time < self.check_interval:
            # Return cached status
            return {
                "status": self.health_status,
                "last_check": self.last_check_time.isoformat(),
                "cached": True,
            }

        # Run minimal checks
        results = []

        # Quick component check
        try:
            loop = AdaptiveReasoningLoop()
            status = loop.get_status()
            if status:
                results.append(DiagnosticResult("quick_check", DiagnosticLevel.INFO, "Components responsive"))
        except Exception as e:
            results.append(DiagnosticResult("quick_check", DiagnosticLevel.ERROR, f"Component error: {e!s}"))

        self._update_health_status(results)

        return {
            "status": self.health_status,
            "timestamp": datetime.now().isoformat(),
            "cached": False,
        }


# Test classes for backward compatibility
class TestReasoningDiagnostics(unittest.TestCase):
    """Unit tests for reasoning diagnostics"""

    def test_logic_fallbacks(self):
        """
        Tests that the reasoning engine's logic fallbacks are working correctly.
        """
        engine = SymbolicEngine()
        input_data = {
            "text": "This is a test of the logic fallbacks.",
            "context": {"user_id": "test_user"},
        }
        # This should not raise an exception
        engine.reason(input_data)

    def test_unstable_inference(self):
        """
        Tests that the reasoning engine can handle unstable inference.
        """
        # #ΛDIAGNOSE: reasoning_drift
        engine = SymbolicEngine()
        input_data = {
            "text": "This is a test of unstable inference.",
            "context": {"user_id": "test_user"},
        }
        # This should not raise an exception
        engine.reason(input_data)


if __name__ == "__main__":
    # Run unit tests if executed directly
    unittest.main()
