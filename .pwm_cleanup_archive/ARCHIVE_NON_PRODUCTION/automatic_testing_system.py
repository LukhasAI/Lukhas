# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: automatic_testing_system.py
# MODULE: core.automatic_testing_system
# DESCRIPTION: Provides an enhanced automatic testing and logging system for LUKHAS AGI,
#              featuring AI-powered analysis, performance monitoring, and streamlined operations.
# DEPENDENCIES: asyncio, json, logging, subprocess, time, psutil, threading, datetime,
#               pathlib, typing, dataclasses, contextlib, sys, os, traceback, hashlib, tempfile,
#               numpy, pandas (optional), .test_framework (optional)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import asyncio
import hashlib
import json
import os
import shlex  # For secure command parsing
import subprocess

# from contextlib import asynccontextmanager # Not used
import sys
import threading
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import (  # Union, asynccontextmanager, tempfile not directly used here
    Any,
    Callable,
    Dict,
    List,
    Optional,
)

import psutil
import structlog  # Changed from logging

# import tempfile # Not used

# Initialize ΛTRACE logger for this module using structlog
# Assumes structlog is configured in a higher-level __init__.py (e.g., core/__init__.py)
logger = structlog.get_logger("ΛTRACE.core.automatic_testing_system")
logger.info("ΛTRACE: Initializing automatic_testing_system module.")

# AI and ML imports (optional, with fallbacks)
# ΛNOTE: numpy and pandas are optional dependencies. If not found, AI-powered analysis features relying on them will be limited or disabled. The system uses fallbacks (None) for these packages.
try:
    import numpy as np
    import pandas as pd

    logger.info("ΛTRACE: Successfully imported numpy and pandas.")
except ImportError:
    logger.warning(
        "ΛTRACE: numpy or pandas not found. Some AI analysis features might be limited. Using None fallbacks."
    )
    np = None
    pd = None

# Import existing LUKHAS test framework (optional, with fallback)
# ΛNOTE: Integration with 'LucasTestFramework' (assumed to be at '.test_framework') is optional. If the framework is not found, its specific functionalities will be skipped, and a None fallback is used.
try:
    from .test_framework import (
        LucasTestFramework,  # Assuming it's in the same package or discoverable
    )

    logger.info("ΛTRACE: Successfully imported LucasTestFramework.")
except ImportError:
    logger.warning(
        "ΛTRACE: LucasTestFramework not found. Integration will be skipped. Using None fallback."
    )
    LucasTestFramework = None  # type: ignore


# Dataclass for a single test operation
# Represents a single recorded test operation, including its execution details,
# performance metrics, and any AI-driven analysis results.
@dataclass
class TestOperation:
    """
    Represents a single recorded test operation, including its execution details,
    performance metrics, and any AI-driven analysis results.
    """

    operation_id: str
    operation_type: str  # e.g., 'terminal_command', 'api_call', 'ui_interaction', 'benchmark_run', 'validation_check'
    command: str  # Or a description of the operation
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    status: str = (
        "pending"  # 'pending', 'running', 'completed', 'failed', 'skipped', 'timeout'
    )
    output: str = ""  # Standard output from the operation
    error: str = ""  # Standard error or exception message
    exit_code: Optional[int] = None  # Relevant for command-line operations
    performance_metrics: Dict[str, Any] = field(
        default_factory=dict
    )  # e.g., CPU, memory usage during op
    ai_analysis: Dict[str, Any] = field(
        default_factory=dict
    )  # Stores insights from AITestAnalyzer
    context: Dict[str, Any] = field(
        default_factory=dict
    )  # Additional contextual information
    logger.debug("ΛTRACE: TestOperation Dataclass defined.")


# Dataclass for a test session
# Represents a complete testing session, encapsulating multiple TestOperations,
# summary statistics, performance data, and overall AI insights.
@dataclass
class TestSession:
    """
    Represents a complete testing session, encapsulating multiple TestOperations,
    summary statistics, performance data, and overall AI insights.
    """

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    operations: List[TestOperation] = field(default_factory=list)
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    performance_summary: Dict[str, Any] = field(
        default_factory=dict
    )  # Aggregated from PerformanceMonitor
    ai_insights: Dict[str, Any] = field(
        default_factory=dict
    )  # Aggregated from AITestAnalyzer
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )  # e.g., environment, test suite version
    logger.debug("ΛTRACE: TestSession Dataclass defined.")


# Class for real-time performance monitoring
# Monitors system and application performance metrics in real-time during test execution.
# It captures metrics, checks against predefined thresholds, and generates alerts.
class PerformanceMonitor:
    """
    Monitors system and application performance metrics in real-time during test execution.
    It captures metrics, checks against predefined thresholds, and generates alerts.
    """

    # Initialization
    def __init__(self):
        """Initializes the PerformanceMonitor with empty history and default thresholds."""
        self.metrics_history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        # Thresholds for generating alerts (can be made configurable)
        self.thresholds: Dict[str, float] = {
            "cpu_percent": 80.0,  # Overall CPU usage percentage
            "memory_percent": 85.0,  # Overall memory usage percentage
            "response_time_ms": 1000.0,  # Placeholder for specific operation response times
            "error_rate_percent": 5.0,  # Placeholder for application-level error rates
        }
        self.logger = logger.getChild("PerformanceMonitor")  # Instance-specific logger
        self.logger.info("ΛTRACE: PerformanceMonitor initialized.")

    # Method to capture current performance metrics
    def capture_metrics(self) -> Dict[str, Any]:
        """
        Captures current system-level (CPU, memory, disk) and process-level metrics.
        Stores metrics in history and checks for performance alerts.
        Returns:
            Dict[str, Any]: A dictionary of captured metrics or an error dictionary.
        """
        self.logger.debug("ΛTRACE: Capturing current performance metrics.")
        try:
            current_process = psutil.Process(os.getpid())  # Get current Python process

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent_system": psutil.cpu_percent(
                    interval=0.1
                ),  # System-wide CPU
                "memory_percent_system": psutil.virtual_memory().percent,  # System-wide memory
                "disk_usage_percent_root": psutil.disk_usage(
                    "/"
                ).percent,  # Root disk usage
                "process_memory_mb": current_process.memory_info().rss
                / (1024 * 1024),  # Process RSS memory
                "process_cpu_percent": current_process.cpu_percent(
                    interval=0.1
                ),  # Process CPU usage
                "process_open_files": (
                    len(current_process.open_files())
                    if hasattr(current_process, "open_files")
                    else 0
                ),
                "process_threads": current_process.num_threads(),
                "system_load_average": (
                    os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
                ),  # 1, 5, 15 min load avg
            }
            self.logger.debug(f"ΛTRACE: Metrics captured: {metrics}")

            self.metrics_history.append(metrics)
            # Limit history size to prevent excessive memory usage
            if len(self.metrics_history) > 1000:  # Configurable limit
                self.metrics_history = self.metrics_history[-1000:]

            self._check_performance_alerts(
                metrics
            )  # Check new metrics against thresholds
            return metrics

        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Error capturing performance metrics: {e}", exc_info=True
            )
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    # Private method to check for performance alerts
    def _check_performance_alerts(self, current_metrics: Dict[str, Any]) -> None:
        """Checks current metrics against predefined thresholds and logs alerts if exceeded."""
        self.logger.debug(
            f"ΛTRACE: Checking performance alerts against thresholds. Current CPU: {current_metrics.get('cpu_percent_system', 'N/A')}, Memory: {current_metrics.get('memory_percent_system', 'N/A')}"
        )
        for metric_key, threshold_value in self.thresholds.items():
            # Adapt metric keys to match those in capture_metrics (e.g., 'cpu_percent' -> 'cpu_percent_system')
            actual_metric_key = (
                metric_key
                if metric_key not in ["cpu_percent", "memory_percent"]
                else f"{metric_key}_system"
            )

            if (
                actual_metric_key in current_metrics
                and current_metrics[actual_metric_key] > threshold_value
            ):
                severity = (
                    "critical"
                    if current_metrics[actual_metric_key] > threshold_value * 1.2
                    else "warning"
                )
                alert_details = {
                    "timestamp": datetime.now().isoformat(),
                    "metric": actual_metric_key,
                    "value": current_metrics[actual_metric_key],
                    "threshold": threshold_value,
                    "severity": severity,
                }
                self.alerts.append(alert_details)
                self.logger.warning(
                    f"ΛTRACE: Performance Alert! Metric: '{actual_metric_key}', Value: {current_metrics[actual_metric_key]}, Threshold: {threshold_value}, Severity: {severity}"
                )

                # Limit alerts history size
                if len(self.alerts) > 100:  # Configurable limit
                    self.alerts = self.alerts[-100:]

    # Method to get a summary of performance
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Generates a summary of performance based on recently captured metrics.
        Includes averages, peak values, active alerts, and a calculated health score.
        Returns:
            Dict[str, Any]: A dictionary containing the performance summary.
        """
        self.logger.debug("ΛTRACE: Generating performance summary.")
        if not self.metrics_history:
            self.logger.info(
                "ΛTRACE: No performance metrics history available for summary."
            )
            return {"status": "no_data_captured"}

        # Analyze the last N metrics (e.g., last 10 or up to 100)
        recent_metrics_sample = self.metrics_history[
            -min(len(self.metrics_history), 100) :
        ]

        summary = {
            "avg_cpu_percent_system": (
                np.mean([m.get("cpu_percent_system", 0) for m in recent_metrics_sample])
                if recent_metrics_sample and np
                else 0.0
            ),
            "avg_memory_percent_system": (
                np.mean(
                    [m.get("memory_percent_system", 0) for m in recent_metrics_sample]
                )
                if recent_metrics_sample and np
                else 0.0
            ),
            "peak_process_memory_mb": (
                max(m.get("process_memory_mb", 0) for m in recent_metrics_sample)
                if recent_metrics_sample
                else 0.0
            ),
            "active_alerts_last_5_min": len(
                [
                    a
                    for a in self.alerts
                    if datetime.fromisoformat(a["timestamp"])
                    > datetime.now() - timedelta(minutes=5)
                ]
            ),
            "total_metrics_measurements": len(self.metrics_history),
            "current_health_score": self._calculate_health_score(
                recent_metrics_sample
            ),  # Use a sample for health score
        }
        self.logger.info(f"ΛTRACE: Performance summary generated: {summary}")
        return summary

    # Private method to calculate health score
    def _calculate_health_score(self, metrics_sample: List[Dict[str, Any]]) -> float:
        """Calculates an overall system health score (0-100) based on a sample of metrics."""
        self.logger.debug(
            f"ΛTRACE: Calculating health score based on {len(metrics_sample)} metrics samples."
        )
        if not metrics_sample:
            self.logger.debug(
                "ΛTRACE: No metrics for health score calculation; returning 0.0."
            )
            return 0.0

        avg_cpu_system = (
            np.mean([m.get("cpu_percent_system", 0) for m in metrics_sample])
            if np
            else 0.0
        )
        avg_memory_system = (
            np.mean([m.get("memory_percent_system", 0) for m in metrics_sample])
            if np
            else 0.0
        )

        # Health scoring logic (can be refined)
        # Score starts at 100, penalties applied
        health_score = 100.0
        # CPU penalty: for each 10% over 50% usage, deduct 5 points (max 25 points deduction)
        health_score -= (
            max(0, min(25, ((avg_cpu_system - 50) / 10) * 5))
            if avg_cpu_system > 50
            else 0
        )
        # Memory penalty: for each 10% over 60% usage, deduct 5 points (max 25 points deduction)
        health_score -= (
            max(0, min(25, ((avg_memory_system - 60) / 10) * 5))
            if avg_memory_system > 60
            else 0
        )

        # Penalty for active alerts
        active_alerts_count = len(
            [
                a
                for a in self.alerts
                if datetime.fromisoformat(a["timestamp"])
                > datetime.now() - timedelta(minutes=5)
            ]
        )
        health_score -= active_alerts_count * 10  # Deduct 10 points per recent alert

        final_health_score = max(
            0.0, min(100.0, health_score)
        )  # Clamp score between 0 and 100
        self.logger.debug(
            f"ΛTRACE: Health score calculated: {final_health_score:.2f} (CPU avg: {avg_cpu_system:.1f}%, Mem avg: {avg_memory_system:.1f}%, Alerts: {active_alerts_count})"
        )
        return final_health_score


# Class for AI-powered test analysis
# Provides AI-powered analysis of test operations and sessions.
# It categorizes performance, predicts success, suggests optimizations,
# assesses risks, and identifies patterns.
class AITestAnalyzer:
    """
    Provides AI-powered analysis of test operations and sessions.
    It categorizes performance, predicts success, suggests optimizations,
    assesses risks, and identifies patterns.
    """

    # Initialization
    def __init__(self):
        """Initializes the AITestAnalyzer with an empty cache and pattern list."""
        self.analysis_cache: Dict[str, Dict[str, Any]] = (
            {}
        )  # Cache for operation analysis
        self.known_patterns: List[Dict[str, Any]] = (
            []
        )  # For storing learned issue/optimization patterns
        self.recommendation_rules: List[Callable[[TestOperation], Optional[str]]] = (
            []
        )  # Rule-based recommendations
        self.logger = logger.getChild("AITestAnalyzer")  # Instance-specific logger
        self.logger.info("ΛTRACE: AITestAnalyzer initialized.")
        self._load_default_rules_and_patterns()

    # Private method to load default rules/patterns
    def _load_default_rules_and_patterns(self) -> None:
        """Loads a predefined set of analysis rules and issue patterns."""
        # Example recommendation rules (can be expanded significantly)
        self.recommendation_rules.append(
            lambda op: (
                "Optimize for sub-100ms if duration > 100ms and 'critical_path' in op.context"
                if op.duration_ms > 100 and op.context.get("critical_path")
                else None
            )
        )
        self.recommendation_rules.append(
            lambda op: (
                "Investigate high error count if status is 'failed' and exit_code != 0"
                if op.status == "failed" and op.exit_code != 0
                else None
            )
        )
        self.logger.debug(
            f"ΛTRACE: Loaded {len(self.recommendation_rules)} default recommendation rules."
        )
        # Example known patterns (can be loaded from a config file or database)
        self.known_patterns.append(
            {
                "name": "timeout_error",
                "condition": lambda op: "timeout" in op.error.lower(),
                "implication": "Potential network latency or inefficient algorithm.",
            }
        )
        self.known_patterns.append({"name": "memory_leak_symptom", "condition": lambda op: "memory allocation failed" in op.error.lower() or (op.performance_metrics.get("final", {}).get("process_memory_mb", 0) > op.performance_metrics.get("initial", {}).get("process_memory_mb", 0) * 1.5 and op.performance_metrics.get("initial", {}).get("process_memory_mb", 0) > 100), "implication": "Possible memory leak detected during operation."})  # type: ignore
        self.logger.debug(
            f"ΛTRACE: Loaded {len(self.known_patterns)} default known issue patterns."
        )

    # Method to analyze a single test operation
    def analyze_operation(self, operation: TestOperation) -> Dict[str, Any]:
        """
        Analyzes a single TestOperation, providing insights on performance,
        success probability, optimization suggestions, risk, and pattern matches.
        Results are cached.
        Args:
            operation (TestOperation): The test operation to analyze.
        Returns:
            Dict[str, Any]: A dictionary containing the analysis results.
        """
        self.logger.debug(
            f"ΛTRACE: Analyzing operation ID '{operation.operation_id}' (Type: {operation.operation_type}, Command: {operation.command[:50]}...)."
        )
        operation_hash = self._hash_operation(operation)
        if operation_hash in self.analysis_cache:
            self.logger.debug(
                f"ΛTRACE: Returning cached analysis for operation hash '{operation_hash}'."
            )
            return self.analysis_cache[operation_hash]

        analysis = {
            "performance_category": self._categorize_performance(
                operation.duration_ms
            ),  # Already logs
            "predicted_success_probability": self._predict_success_probability(
                operation
            ),  # Already logs
            "optimization_suggestions": self._generate_optimization_suggestions(
                operation
            ),  # Already logs
            "risk_assessment_score": self._assess_risk_score(operation),  # Already logs
            "matched_known_patterns": self._find_known_pattern_matches(
                operation
            ),  # Already logs
        }
        self.logger.info(
            f"ΛTRACE: Analysis for operation '{operation.operation_id}' complete: {analysis}"
        )
        self.analysis_cache[operation_hash] = analysis  # Cache the result
        return analysis

    # Method to analyze a complete test session
    def analyze_session(self, session: TestSession) -> Dict[str, Any]:
        """
        Analyzes a complete TestSession, providing aggregated insights,
        performance grades, recommendations, risk factors, and optimization opportunities.
        Args:
            session (TestSession): The test session to analyze.
        Returns:
            Dict[str, Any]: A dictionary containing the session analysis results.
        """
        self.logger.info(
            f"ΛTRACE: Analyzing session ID '{session.session_id}'. Operations count: {len(session.operations)}."
        )
        if not session.operations:
            self.logger.warning("ΛTRACE: No operations in session to analyze.")
            return {"status": "no_operations_in_session"}

        # Aggregate performance data
        op_durations = [
            op.duration_ms
            for op in session.operations
            if op.status == "completed" and op.duration_ms is not None
        ]
        success_rate = (
            (session.successful_operations / session.total_operations)
            if session.total_operations > 0
            else 0.0
        )
        self.logger.debug(
            f"ΛTRACE: Session success rate: {success_rate:.2%}, Durations count: {len(op_durations)}."
        )

        session_analysis = {
            "overall_session_summary": {
                "total_operations": session.total_operations,
                "success_rate": success_rate,
                "average_operation_duration_ms": (
                    np.mean(op_durations) if op_durations and np else 0.0
                ),
                "median_operation_duration_ms": (
                    np.median(op_durations) if op_durations and np else 0.0
                ),
                "p95_operation_duration_ms": (
                    np.percentile(op_durations, 95) if op_durations and np else 0.0
                ),
                "peak_operation_duration_ms": (
                    max(op_durations) if op_durations else 0.0
                ),
                "operation_duration_trend": self._analyze_duration_trend(
                    op_durations
                ),  # Already logs
            },
            "session_performance_insights": {
                "count_sub_100ms_ops": len([d for d in op_durations if d < 100]),
                "count_slow_ops_over_1s": len([d for d in op_durations if d > 1000]),
                "overall_performance_grade": self._calculate_performance_grade(
                    op_durations, success_rate
                ),  # Already logs
            },
            "actionable_session_recommendations": self._generate_session_recommendations(
                session
            ),  # Already logs
            "identified_session_risk_factors": self._identify_session_risks(
                session
            ),  # Already logs
            "potential_optimization_opportunities": self._find_optimization_opportunities(
                session
            ),  # Already logs
        }
        self.logger.info(
            f"ΛTRACE: Session '{session.session_id}' analysis complete: {session_analysis['overall_session_summary']}"
        )
        return session_analysis

    # Private method to categorize performance
    def _categorize_performance(self, duration_ms: float) -> str:
        """Categorizes operation performance based on its duration."""
        # Thresholds can be made configurable
        if duration_ms < 50:
            cat = "excellent"
        elif duration_ms < 100:
            cat = "good"
        elif duration_ms < 500:
            cat = "acceptable"
        elif duration_ms < 2000:
            cat = "slow"  # Adjusted threshold
        else:
            cat = "critically_slow"
        self.logger.debug(
            f"ΛTRACE: Performance categorized for duration {duration_ms:.2f}ms as '{cat}'."
        )
        return cat

    # Private method to predict success probability (heuristic)
    def _predict_success_probability(self, operation: TestOperation) -> float:
        """Estimates success probability based on operation type and past performance (heuristic)."""
        # This is a placeholder for a more sophisticated ML model if available
        base_prob = 0.95
        if operation.operation_type == "terminal_command":
            base_prob = 0.90
        elif operation.operation_type == "api_call":
            base_prob = 0.98

        if operation.duration_ms > 2000:
            base_prob -= 0.10  # Penalty for slowness
        if operation.context.get("retries_attempted", 0) > 0:
            base_prob -= 0.05 * operation.context["retries_attempted"]

        final_prob = max(0.50, min(0.99, base_prob))  # Clamp probability
        self.logger.debug(
            f"ΛTRACE: Predicted success probability for op '{operation.operation_id}': {final_prob:.2f}"
        )
        return final_prob

    # Private method to generate optimization suggestions
    def _generate_optimization_suggestions(self, operation: TestOperation) -> List[str]:
        """Generates context-specific optimization suggestions for an operation."""
        suggestions: List[str] = []
        for rule in self.recommendation_rules:
            suggestion = rule(operation)
            if suggestion:
                suggestions.append(suggestion)

        # Generic suggestions based on status/duration
        if (
            operation.status == "failed"
            and "Consider adding more specific error handling" not in suggestions
        ):
            suggestions.append(
                "Consider adding more specific error handling or retry logic for this operation type."
            )
        if (
            operation.duration_ms > 5000
            and "Operation is critically slow, investigate performance bottlenecks"
            not in suggestions
        ):
            suggestions.append(
                "Operation is critically slow, investigate performance bottlenecks (e.g., I/O, CPU, network)."
            )

        self.logger.debug(
            f"ΛTRACE: Generated {len(suggestions)} optimization suggestions for op '{operation.operation_id}'."
        )
        return suggestions

    # Private method to assess risk score (heuristic)
    def _assess_risk_score(self, operation: TestOperation) -> float:
        """Assesses a risk score (0-1) for an operation based on its outcome and characteristics."""
        risk = 0.0
        if operation.status == "failed":
            risk += 0.5
        if operation.status == "timeout":
            risk += 0.7
        if operation.duration_ms > 5000:
            risk += 0.2  # Penalty for very slow ops
        if operation.exit_code is not None and operation.exit_code != 0:
            risk += 0.1 * abs(
                operation.exit_code
            )  # Small penalty for non-zero exit codes

        final_risk = max(0.0, min(1.0, risk))  # Clamp risk score
        self.logger.debug(
            f"ΛTRACE: Risk score for op '{operation.operation_id}': {final_risk:.2f}"
        )
        return final_risk

    # Private method to find matches with known patterns
    def _find_known_pattern_matches(
        self, operation: TestOperation
    ) -> List[Dict[str, str]]:
        """Matches operation details against a list of known issue/optimization patterns."""
        matched_patterns: List[Dict[str, str]] = []
        for pattern in self.known_patterns:
            if pattern["condition"](operation):
                matched_patterns.append(
                    {
                        "pattern_name": pattern["name"],
                        "implication": pattern["implication"],
                    }
                )
        self.logger.debug(
            f"ΛTRACE: Found {len(matched_patterns)} known pattern matches for op '{operation.operation_id}'."
        )
        return matched_patterns

    # Private method to hash an operation for caching
    def _hash_operation(self, operation: TestOperation) -> str:
        """Creates a hash string from key operation details for caching analysis results."""
        # Using a subset of fields that define the operation's nature for hashing
        op_string_for_hash = (
            f"{operation.operation_type}:{operation.command}:{operation.status}"
        )
        # Security fix: Use SHA-256 instead of MD5 for better security
        return hashlib.sha256(op_string_for_hash.encode()).hexdigest()[
            :16
        ]  # Truncate to 16 chars for brevity

    # Private method to analyze duration trend in a list of durations
    def _analyze_duration_trend(self, durations: List[float]) -> str:
        """Analyzes if a list of durations shows an improving, degrading, or stable trend."""
        self.logger.debug(
            f"ΛTRACE: Analyzing duration trend for {len(durations)} data points."
        )
        if len(durations) < 5:  # Need enough data points for a meaningful trend
            self.logger.debug("ΛTRACE: Insufficient data for duration trend analysis.")
            return "insufficient_data"

        # Simplified trend analysis: compare average of first half vs. second half
        mid_point = len(durations) // 2
        avg_first_half = np.mean(durations[:mid_point]) if np else 0.0
        avg_second_half = np.mean(durations[mid_point:]) if np else 0.0

        trend = "stable"
        if avg_second_half > avg_first_half * 1.15:  # Degradation if 15% worse
            trend = "degrading"
        elif avg_second_half < avg_first_half * 0.85:  # Improvement if 15% better
            trend = "improving"
        self.logger.debug(
            f"ΛTRACE: Duration trend: {trend} (First half avg: {avg_first_half:.2f}ms, Second half avg: {avg_second_half:.2f}ms)."
        )
        return trend

    # Private method to calculate performance grade
    def _calculate_performance_grade(
        self, durations: List[float], success_rate: float
    ) -> str:
        """Calculates an overall performance grade (A-F) based on durations and success rate."""
        self.logger.debug(
            f"ΛTRACE: Calculating performance grade. Durations count: {len(durations)}, Success rate: {success_rate:.2%}."
        )
        if not durations and success_rate == 0:  # No data or all failed
            self.logger.debug(
                "ΛTRACE: No duration data or 0% success rate, performance grade 'F'."
            )
            return "F"

        # Score based on average duration (lower is better)
        avg_duration = (
            np.mean(durations) if durations and np else 10000.0
        )  # Penalize if no durations but some success
        duration_score = 0
        if avg_duration < 100:
            duration_score = 40
        elif avg_duration < 500:
            duration_score = 30
        elif avg_duration < 2000:
            duration_score = 20
        elif avg_duration < 5000:
            duration_score = 10

        # Score based on success rate (higher is better)
        success_score = success_rate * 60
        total_score = duration_score + success_score

        grade = "F"
        if total_score >= 90:
            grade = "A"
        elif total_score >= 80:
            grade = "B"
        elif total_score >= 70:
            grade = "C"
        elif total_score >= 60:
            grade = "D"
        self.logger.debug(
            f"ΛTRACE: Performance grade: {grade} (Total score: {total_score:.2f}, Avg duration: {avg_duration:.2f}ms)."
        )
        return grade

    # Private method to generate session-level recommendations
    def _generate_session_recommendations(self, session: TestSession) -> List[str]:
        """Generates actionable recommendations based on overall session performance."""
        self.logger.debug(
            f"ΛTRACE: Generating session-level recommendations for session '{session.session_id}'."
        )
        recs: List[str] = []
        success_rate = (
            (session.successful_operations / session.total_operations)
            if session.total_operations > 0
            else 0.0
        )
        if (
            success_rate < 0.90 and session.total_operations > 5
        ):  # If many ops and low success
            recs.append(
                f"Improve overall test reliability; current success rate is low ({success_rate:.1%}). Focus on failing operations."
            )

        slow_ops_count = len(
            [
                op
                for op in session.operations
                if op.duration_ms is not None and op.duration_ms > 2000
            ]
        )  # Ops > 2s
        if (
            slow_ops_count > session.total_operations * 0.1 and slow_ops_count > 2
        ):  # If >10% are slow and at least 2 slow ops
            recs.append(
                f"Address {slow_ops_count} significantly slow operations (>{2000}ms) to improve overall test suite speed."
            )

        if not recs:
            recs.append(
                "Session performance appears stable. Continue monitoring key metrics."
            )
        self.logger.debug(f"ΛTRACE: Generated {len(recs)} session recommendations.")
        return recs

    # Private method to identify session-level risks
    def _identify_session_risks(self, session: TestSession) -> List[str]:
        """Identifies potential risks based on aggregated session data."""
        self.logger.debug(
            f"ΛTRACE: Identifying session-level risks for session '{session.session_id}'."
        )
        risks_found: List[str] = []
        if (
            session.failed_operations > session.total_operations * 0.2
            and session.total_operations > 5
        ):  # >20% failure rate
            risks_found.append(
                f"High failure rate: {session.failed_operations}/{session.total_operations} operations failed. Indicates potential instability."
            )

        timeout_ops_count = len(
            [op for op in session.operations if op.status == "timeout"]
        )
        if timeout_ops_count > 0:
            risks_found.append(
                f"Timeout issues detected in {timeout_ops_count} operation(s). Investigate underlying causes."
            )

        # Add more risk identification logic here (e.g., based on performance degradation over time)
        if not risks_found:
            risks_found.append(
                "No immediate high-priority risks identified in this session."
            )
        self.logger.debug(f"ΛTRACE: Identified {len(risks_found)} session risks.")
        return risks_found

    # Private method to find session-level optimization opportunities
    def _find_optimization_opportunities(self, session: TestSession) -> List[str]:
        """Scans session data for potential optimization opportunities."""
        self.logger.debug(
            f"ΛTRACE: Finding session-level optimization opportunities for session '{session.session_id}'."
        )
        opportunities_found: List[str] = []
        # Example: Look for frequently repeated commands that could be batched or whose results cached
        command_counts = {}
        if np:  # Only if numpy is available for Counter-like behavior easily
            from collections import Counter

            command_counts = Counter([op.command for op in session.operations])
            repeated_commands = [
                cmd
                for cmd, count in command_counts.items()
                if count > 3 and len(cmd) > 10
            ]  # Repeated >3 times, non-trivial
            if repeated_commands:
                opportunities_found.append(
                    f"Consider batching or caching results for frequently repeated commands: {repeated_commands[:2]}{'...' if len(repeated_commands)>2 else ''}."
                )

        # Example: If many tests are short but run sequentially
        short_test_runs = [
            op
            for op in session.operations
            if op.operation_type == "test_run"
            and op.duration_ms is not None
            and op.duration_ms < 500
        ]
        if (
            len(short_test_runs) > 10
            and session.metadata.get("execution_mode", "sequential") == "sequential"
        ):  # Assuming metadata field
            opportunities_found.append(
                "Multiple short test runs detected; consider parallel execution to reduce total test time."
            )

        if not opportunities_found:
            opportunities_found.append(
                "No obvious high-impact optimization opportunities detected from this session's structure."
            )
        self.logger.debug(
            f"ΛTRACE: Found {len(opportunities_found)} optimization opportunities."
        )
        return opportunities_found


# Main class for the Automatic Testing System
# Manages the entire automatic testing lifecycle for LUKHAS AGI.
# Provides one-line operations for running tests, continuous monitoring, and reporting,
# integrating performance monitoring and AI-powered analysis.
class AutomaticTestingSystem:
    """
    Manages the entire automatic testing lifecycle for LUKHAS AGI.
    Provides one-line operations for running tests, continuous monitoring, and reporting,
    integrating performance monitoring and AI-powered analysis.
    """

    # Initialization
    def __init__(
        self,
        workspace_path: Optional[Path] = None,
        enable_ai_analysis: bool = True,
        enable_performance_monitoring: bool = True,
    ):
        """
        Initializes the AutomaticTestingSystem.
        Args:
            workspace_path (Optional[Path]): The root workspace path for tests. Defaults to CWD.
            enable_ai_analysis (bool): Flag to enable/disable AI-powered test analysis.
            enable_performance_monitoring (bool): Flag to enable/disable performance monitoring.
        """
        self.logger = logger.getChild(
            "AutomaticTestingSystemMain"
        )  # Instance-specific logger
        self.logger.info(
            f"ΛTRACE: Initializing AutomaticTestingSystem. Workspace: {workspace_path}, AI Analysis: {enable_ai_analysis}, Perf Mon: {enable_performance_monitoring}"
        )

        self.workspace_path: Path = workspace_path or Path.cwd()
        self.enable_ai_analysis: bool = enable_ai_analysis
        self.enable_performance_monitoring: bool = enable_performance_monitoring

        # Initialize core components
        self.performance_monitor: Optional[PerformanceMonitor] = (
            PerformanceMonitor() if self.enable_performance_monitoring else None
        )
        self.ai_analyzer: Optional[AITestAnalyzer] = (
            AITestAnalyzer() if self.enable_ai_analysis else None
        )

        # Attempt to initialize LucasTestFramework if available
        self.lukhas_framework: Optional[LucasTestFramework] = None
        if LucasTestFramework:
            try:
                self.lukhas_framework = (
                    LucasTestFramework()
                )  # Assuming it has a default constructor
                self.logger.info(
                    "ΛTRACE: LucasTestFramework component initialized successfully."
                )
            except Exception as ltf_e:
                self.logger.error(
                    f"ΛTRACE: Failed to initialize LucasTestFramework: {ltf_e}",
                    exc_info=True,
                )
        else:
            self.logger.info(
                "ΛTRACE: LucasTestFramework component not available or not imported."
            )

        # Storage for test sessions and results
        self.sessions: Dict[str, TestSession] = {}
        self.current_session: Optional[TestSession] = None
        self.results_dir: Path = (
            self.workspace_path / "test_results_lukhas" / "automatic_v2"
        )  # Changed dir name
        try:
            self.results_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(
                f"ΛTRACE: Results directory ensured at: {self.results_dir}"
            )
        except OSError as e:
            self.logger.error(
                f"ΛTRACE: Failed to create results directory {self.results_dir}: {e}",
                exc_info=True,
            )
            # Potentially raise or handle this more gracefully if dir creation is critical

        # State for continuous monitoring
        self.is_watching: bool = False
        self.watch_thread: Optional[threading.Thread] = None

        # Logging setup (distinct from ΛTRACE, for system's own operational logs if needed, or could merge)
        # The original _setup_logging created self.logger. If we use module-level ΛTRACE logger,
        # this specific setup might be redundant or need integration.
        # For now, assuming self.logger refers to the ΛTRACE child logger.
        # self._setup_logging() # This was creating a new logger. We'll use the ΛTRACE one.

        self.logger.info(
            f"ΛTRACE: AutomaticTestingSystem fully initialized. Workspace: {self.workspace_path}, AI Analysis: {self.enable_ai_analysis}, Perf Mon: {self.enable_performance_monitoring}"
        )

    # Original _setup_logging is removed as ΛTRACE logger is used.
    # If separate operational logging is needed, it can be added back carefully.

    # =========================================================================
    # ONE-LINE API - Targeted by JULES for Header/Footer/ΛTRACE
    # =========================================================================
    # Human-readable comment: One-line API method to run tests.
    async def run(
        self,
        test_type: str = "comprehensive",  # e.g., "smoke", "full", "performance", "integration"
        timeout_seconds: int = 3600,
    ) -> Dict[str, Any]:  # Increased default timeout
        """
        Runs a specified type of test suite automatically. This is a primary
        one-line API operation for the testing system.
        Args:
            test_type (str): The type of test suite to run.
            timeout_seconds (int): Overall timeout for the test run.
        Returns:
            Dict[str, Any]: A summary of the test run including session ID and status.
        """
        self.logger.info(
            f"ΛTRACE: autotest.run() called. Test Type: '{test_type}', Timeout: {timeout_seconds}s."
        )
        session_id = f"autorun_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"  # Added microseconds for uniqueness
        session = await self._start_session(session_id)  # _start_session logs
        self.logger.info(
            f"ΛTRACE: Test session '{session_id}' started for run type '{test_type}'."
        )

        run_results: Dict[str, Any] = {}
        try:
            # Test execution logic based on test_type
            if test_type == "comprehensive":
                run_results = await self._run_comprehensive_tests(
                    session
                )  # This method should log internally
            elif test_type == "performance":
                run_results = await self._run_performance_tests(
                    session
                )  # Logs internally
            # ... other test types
            else:  # Default or basic
                run_results = await self._run_basic_tests(session)  # Logs internally
            self.logger.info(
                f"ΛTRACE: Test execution for type '{test_type}' completed for session '{session_id}'."
            )

            # Finalize session with analysis and summaries
            if self.ai_analyzer and session:  # Ensure session is not None
                ai_session_insights = self.ai_analyzer.analyze_session(
                    session
                )  # Logs internally
                run_results["ai_session_insights"] = ai_session_insights
                self.logger.info(
                    f"ΛTRACE: AI session analysis complete for '{session_id}'."
                )

            if self.performance_monitor and session:  # Ensure session is not None
                perf_session_summary = (
                    self.performance_monitor.get_performance_summary()
                )  # Logs internally
                run_results["performance_session_summary"] = perf_session_summary
                self.logger.info(
                    f"ΛTRACE: Performance summary generated for '{session_id}'."
                )

            await self._end_session(session)  # _end_session logs
            await self._save_session_results(
                session, run_results
            )  # _save_session_results logs

            success_rate_final = (
                (session.successful_operations / session.total_operations * 100)
                if session.total_operations > 0
                else 0
            )
            self.logger.info(
                f"ΛTRACE: Automatic test run '{test_type}' completed successfully for session '{session_id}'. Total Ops: {session.total_operations}, Success: {success_rate_final:.1f}%."
            )
            return {
                "session_id": session_id,
                "status": "completed",
                "summary_results": run_results,
                "session_data_path": str(self.results_dir / f"{session_id}.json"),
            }

        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Critical error during test run '{test_type}' for session '{session_id}': {e}",
                exc_info=True,
            )
            if session:  # Ensure session exists before trying to end it
                await self._end_session(
                    session, status="critical_failure", error_message=str(e)
                )
            return {
                "session_id": session_id,
                "status": "critical_failure",
                "error_details": str(e),
                "traceback_info": traceback.format_exc(),
            }

    # Human-readable comment: One-line API method to start continuous monitoring.
    async def watch(
        self,
        interval_seconds: int = 30,  # How often to check for changes/run monitoring tasks
        auto_test_on_change: bool = True,
    ) -> Dict[str, Any]:
        """
        Starts continuous background monitoring of the system and optionally
        triggers tests on detected changes. This is a one-line API operation.
        Args:
            interval_seconds (int): The interval for monitoring checks.
            auto_test_on_change (bool): Whether to automatically run tests on changes.
        Returns:
            Dict[str, Any]: Status of the watch operation.
        """
        self.logger.info(
            f"ΛTRACE: autotest.watch() called. Interval: {interval_seconds}s, Auto-test on change: {auto_test_on_change}."
        )
        if self.is_watching:
            self.logger.warning("ΛTRACE: Watch mode is already active.")
            return {
                "status": "already_watching",
                "message": "Continuous monitoring is already active.",
            }

        self.is_watching = True
        # self.capture_enabled = True # This seems related to terminal capture, ensure its scope is clear.

        # Initialize and start the monitoring thread
        self.watch_thread = threading.Thread(
            target=self._watch_loop_entry,  # Renamed to avoid async confusion with thread target
            args=(interval_seconds, auto_test_on_change),
            daemon=True,  # Daemon thread will exit when main program exits
        )
        self.watch_thread.start()
        self.logger.info(
            f"ΛTRACE: Continuous monitoring watch_thread started. Interval: {interval_seconds}s, Auto-test: {auto_test_on_change}."
        )
        return {
            "status": "monitoring_started",
            "interval_seconds": interval_seconds,
            "auto_test_on_change_enabled": auto_test_on_change,
            "message": "Continuous background monitoring has been initiated.",
        }

    # Entry point for the thread, which then runs the async loop
    def _watch_loop_entry(
        self, interval_seconds: int, auto_test_on_change: bool
    ) -> None:
        """Synchronous entry point for the watch thread that sets up and runs the async watch loop."""
        self.logger.info(
            "ΛTRACE: Watch loop thread started. Setting up async event loop for watch tasks."
        )
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self._watch_loop_async(interval_seconds, auto_test_on_change)
            )
        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Exception in _watch_loop_entry's async runner: {e}",
                exc_info=True,
            )
        finally:
            loop.close()
            self.logger.info("ΛTRACE: Watch loop thread's async event loop closed.")

    # Human-readable comment: One-line API method to generate a test report.
    async def report(
        self,
        session_id_to_report: Optional[str] = None,  # Renamed for clarity
        report_format: str = "comprehensive_json",
    ) -> Dict[str, Any]:  # Added report_format
        """
        Generates a comprehensive report for a specific test session or the most recent one.
        This is a one-line API operation.
        Args:
            session_id_to_report (Optional[str]): The ID of the session to report on. Defaults to the most recent.
            report_format (str): The desired format of the report (e.g., "json", "html_summary").
        Returns:
            Dict[str, Any]: The generated report content or status of report generation.
        """
        self.logger.info(
            f"ΛTRACE: autotest.report() called. Session ID: '{session_id_to_report if session_id_to_report else 'most_recent'}', Format: '{report_format}'."
        )

        target_session: Optional[TestSession] = None
        if session_id_to_report:
            target_session = self.sessions.get(session_id_to_report)
            if not target_session:  # Try loading from file if not in memory
                try:
                    session_file_path = (
                        self.results_dir / f"{session_id_to_report}.json"
                    )
                    if session_file_path.exists():
                        with open(session_file_path) as f_in:
                            loaded_session_data = json.load(f_in)
                        target_session = self._deserialize_session(
                            loaded_session_data["session"]
                        )  # Assuming structure
                        self.logger.info(
                            f"ΛTRACE: Loaded session '{session_id_to_report}' from file for reporting."
                        )
                    else:
                        self.logger.error(
                            f"ΛTRACE: Session ID '{session_id_to_report}' not found in memory or disk for reporting."
                        )
                        return {
                            "error": f"Session '{session_id_to_report}' not found.",
                            "status": "session_not_found",
                        }
                except Exception as e:
                    self.logger.error(
                        f"ΛTRACE: Error loading session '{session_id_to_report}' from file: {e}",
                        exc_info=True,
                    )
                    return {
                        "error": f"Error loading session '{session_id_to_report}': {e}",
                        "status": "load_error",
                    }
        else:  # Get most recent if no ID specified
            target_session = (
                self.current_session or self._get_most_recent_session()
            )  # _get_most_recent_session logs

        if not target_session:
            self.logger.warning(
                "ΛTRACE: No session available (neither specified nor recent) for reporting."
            )
            return {
                "error": "No test sessions available to generate a report.",
                "status": "no_sessions_available",
            }

        # Generate the report data structure
        self.logger.debug(
            f"ΛTRACE: Generating report data for session '{target_session.session_id}'."
        )
        report_content = {
            "report_metadata": {
                "report_generated_at": datetime.now().isoformat(),
                "report_format_requested": report_format,
                "reporting_system_version": "ATS_vJULES_1.1.0",  # Example version
            },
            "session_details": self._serialize_session(
                target_session
            ),  # Use existing serialization
            # Include AI insights and performance if available and enabled during the session
            "ai_driven_insights": (
                target_session.ai_insights
                if self.enable_ai_analysis
                else "AI analysis was disabled for this session."
            ),
            "performance_data_summary": (
                target_session.performance_summary
                if self.enable_performance_monitoring
                else "Performance monitoring was disabled for this session."
            ),
        }

        # Save the report to a file (e.g., JSON format)
        report_file_name = f"report_{target_session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file_path = self.results_dir / report_file_name
        try:
            with open(report_file_path, "w") as f_out:
                json.dump(
                    report_content, f_out, indent=2, default=str
                )  # default=str for datetime etc.
            self.logger.info(
                f"ΛTRACE: Comprehensive report for session '{target_session.session_id}' generated and saved to: {report_file_path}"
            )
            return {
                "status": "report_generated_successfully",
                "report_content_summary": {
                    k: (type(v).__name__ if k != "report_metadata" else v)
                    for k, v in report_content.items()
                },  # Summary of content
                "report_file_location": str(report_file_path),
            }
        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Failed to save report for session '{target_session.session_id}' to file: {e}",
                exc_info=True,
            )
            return {
                "status": "report_generation_failed_on_save",
                "error_details": str(e),
            }

    # =========================================================================
    # TERMINAL OPERATION CAPTURE
    # =========================================================================
    # Human-readable comment: Method to capture and analyze a single terminal operation.
    async def capture_terminal_operation(
        self,
        command_str: str,  # Renamed for clarity
        operation_type_str: str = "terminal_command",  # Renamed
        timeout_val_seconds: int = 60,  # Renamed
        capture_perf_metrics: bool = True,
    ) -> TestOperation:  # Renamed
        """
        Captures the execution of a terminal command, including its output, errors,
        duration, and optionally, performance metrics and AI analysis.
        Args:
            command_str (str): The terminal command to execute.
            operation_type_str (str): The type of operation being performed.
            timeout_val_seconds (int): Timeout for the command execution.
            capture_perf_metrics (bool): Whether to capture performance metrics during this operation.
        Returns:
            TestOperation: An object containing all details of the executed operation.
        """
        op_id = (
            f"op_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"  # Unique operation ID
        )
        op_start_time = datetime.now()
        self.logger.info(
            f"ΛTRACE: Capturing terminal operation ID '{op_id}'. Command: '{command_str}', Type: '{operation_type_str}', Timeout: {timeout_val_seconds}s."
        )

        current_op = TestOperation(
            operation_id=op_id,
            operation_type=operation_type_str,
            command=command_str,
            start_time=op_start_time,
            context={
                "workspace_path": str(self.workspace_path),
                "capture_performance": capture_perf_metrics,
            },
        )

        initial_perf_metrics: Optional[Dict[str, Any]] = None
        if capture_perf_metrics and self.performance_monitor:
            initial_perf_metrics = (
                self.performance_monitor.capture_metrics()
            )  # Logs internally
            current_op.context["initial_performance_metrics"] = initial_perf_metrics
            self.logger.debug(
                f"ΛTRACE: Initial performance metrics captured for op '{op_id}'."
            )

        try:
            self.logger.info(
                f"ΛTRACE: Executing command for op '{op_id}': {command_str}"
            )
            # Using subprocess.run for synchronous execution, suitable for most test commands.
            # For truly non-blocking async subprocesses, asyncio.create_subprocess_shell might be used.

            # Security fix: Use shlex.split to avoid shell injection vulnerabilities
            command_args = shlex.split(command_str)
            process_result = subprocess.run(
                command_args,
                shell=False,
                capture_output=True,
                text=True,  # Ensure text=True for string output
                timeout=timeout_val_seconds,
                cwd=self.workspace_path,
                check=False,  # check=False to not raise on non-zero exit
            )
            op_end_time = datetime.now()
            current_op.end_time = op_end_time
            current_op.duration_ms = (
                op_end_time - op_start_time
            ).total_seconds() * 1000
            current_op.exit_code = process_result.returncode
            current_op.output = (
                process_result.stdout.strip() if process_result.stdout else ""
            )
            current_op.error = (
                process_result.stderr.strip() if process_result.stderr else ""
            )
            current_op.status = (
                "completed" if process_result.returncode == 0 else "failed"
            )

            log_status_emoji = "✅" if current_op.status == "completed" else "❌"
            self.logger.info(
                f"ΛTRACE: {log_status_emoji} Command for op '{op_id}' completed. Duration: {current_op.duration_ms:.2f}ms, ExitCode: {current_op.exit_code}."
            )
            if current_op.output:
                self.logger.debug(
                    f"ΛTRACE: Op '{op_id}' STDOUT: {current_op.output[:200]}{'...' if len(current_op.output) > 200 else ''}"
                )
            if current_op.error:
                self.logger.warning(
                    f"ΛTRACE: Op '{op_id}' STDERR: {current_op.error[:200]}{'...' if len(current_op.error) > 200 else ''}"
                )

        except subprocess.TimeoutExpired:
            op_end_time = datetime.now()
            current_op.end_time = op_end_time
            current_op.duration_ms = (
                timeout_val_seconds * 1000
            )  # Reflect timeout duration
            current_op.status = "timeout"
            current_op.error = f"Command '{command_str}' timed out after {timeout_val_seconds} seconds."
            self.logger.warning(
                f"ΛTRACE: ⏰ Command for op '{op_id}' timed out: {command_str}"
            )

        except Exception as e:  # Catch other potential errors during subprocess.run
            op_end_time = datetime.now()
            current_op.end_time = op_end_time
            current_op.duration_ms = (
                op_end_time - op_start_time
            ).total_seconds() * 1000
            current_op.status = "execution_error"
            current_op.error = f"Exception during command execution: {str(e)}. Traceback: {traceback.format_exc()}"
            self.logger.error(
                f"ΛTRACE: 💥 Exception during execution of op '{op_id}' command '{command_str}': {e}",
                exc_info=True,
            )

        final_perf_metrics: Optional[Dict[str, Any]] = None
        if capture_perf_metrics and self.performance_monitor:
            final_perf_metrics = (
                self.performance_monitor.capture_metrics()
            )  # Logs internally
            current_op.performance_metrics = {
                "initial_snapshot": initial_perf_metrics,  # Store initial metrics for delta if needed
                "final_snapshot": final_perf_metrics,
                "operation_duration_ms": current_op.duration_ms,  # Redundant but explicit
            }
            self.logger.debug(
                f"ΛTRACE: Final performance metrics captured for op '{op_id}'."
            )

        if self.ai_analyzer:
            current_op.ai_analysis = self.ai_analyzer.analyze_operation(
                current_op
            )  # Logs internally
            self.logger.debug(f"ΛTRACE: AI analysis performed for op '{op_id}'.")

        # Add to current session if one is active
        if self.current_session:
            self.current_session.operations.append(current_op)
            self.current_session.total_operations += 1
            if current_op.status == "completed":
                self.current_session.successful_operations += 1
            else:
                self.current_session.failed_operations += 1
            self.logger.debug(
                f"ΛTRACE: Op '{op_id}' added to current session '{self.current_session.session_id}'. Session ops: {self.current_session.total_operations}."
            )

        return current_op

    # =========================================================================
    # SESSION MANAGEMENT (Private Helpers)
    # =========================================================================
    # Human-readable comment: Private helper to start a new test session.
    async def _start_session(self, session_id_str: str) -> TestSession:  # Renamed
        """Initializes and starts a new TestSession, making it the current session."""
        self.logger.info(f"ΛTRACE: Starting new test session: '{session_id_str}'.")
        new_session = TestSession(
            session_id=session_id_str,
            start_time=datetime.now(),
            metadata={  # Example metadata
                "workspace_path": str(self.workspace_path),
                "python_version_info": sys.version,
                "system_platform": sys.platform,
                "os_name": os.name,
                "user": os.getlogin() if hasattr(os, "getlogin") else "unknown",
            },
        )
        self.sessions[session_id_str] = new_session
        self.current_session = new_session
        self.logger.debug(
            f"ΛTRACE: Session '{session_id_str}' object created and set as current. Metadata: {new_session.metadata}"
        )
        return new_session

    # Human-readable comment: Private helper to end the current test session.
    async def _end_session(
        self,
        session_obj: TestSession,
        status_str: str = "completed",
        error_message: Optional[str] = None,
    ) -> None:  # Renamed
        """Finalizes a TestSession, calculating summaries and recording end time."""
        self.logger.info(
            f"ΛTRACE: Ending test session '{session_obj.session_id}'. Status: {status_str}."
        )
        session_obj.end_time = datetime.now()
        session_obj.metadata["final_status_recorded"] = status_str
        if error_message:
            session_obj.metadata["session_error_message"] = error_message
            self.logger.error(
                f"ΛTRACE: Session '{session_obj.session_id}' ended with error: {error_message}"
            )

        # Aggregate performance and AI insights if components are enabled
        if self.performance_monitor:
            session_obj.performance_summary = (
                self.performance_monitor.get_performance_summary()
            )  # Logs internally
            self.logger.debug(
                f"ΛTRACE: Performance summary captured for session '{session_obj.session_id}'."
            )
        if self.ai_analyzer:
            session_obj.ai_insights = self.ai_analyzer.analyze_session(
                session_obj
            )  # Logs internally
            self.logger.debug(
                f"ΛTRACE: AI insights generated for session '{session_obj.session_id}'."
            )

        # If this was the current session, clear it (or set to None)
        if (
            self.current_session
            and self.current_session.session_id == session_obj.session_id
        ):
            self.current_session = None
            self.logger.debug(
                f"ΛTRACE: Current session cleared after ending session '{session_obj.session_id}'."
            )
        self.logger.info(
            f"ΛTRACE: Session '{session_obj.session_id}' officially ended at {session_obj.end_time.isoformat()}."
        )

    # Human-readable comment: Private helper to get the most recent test session.
    def _get_most_recent_session(self) -> Optional[TestSession]:
        """Retrieves the most recently started TestSession from memory."""
        self.logger.debug("ΛTRACE: Getting most recent session.")
        if not self.sessions:
            self.logger.info("ΛTRACE: No sessions found in memory.")
            return None
        # Sort sessions by start_time in descending order and pick the first one
        most_recent = sorted(
            self.sessions.values(), key=lambda s: s.start_time, reverse=True
        )[0]
        self.logger.info(
            f"ΛTRACE: Most recent session found: '{most_recent.session_id}' (Started: {most_recent.start_time.isoformat()})."
        )
        return most_recent

    # Human-readable comment: Private helper to save session results to a file.
    async def _save_session_results(
        self, session_obj: TestSession, run_exec_results: Dict[str, Any]
    ) -> None:  # Renamed
        """Saves the completed TestSession data and execution results to a JSON file."""
        self.logger.info(
            f"ΛTRACE: Saving results for session '{session_obj.session_id}'."
        )
        session_file_path = self.results_dir / f"{session_obj.session_id}.json"

        # Data structure to be saved
        session_data_to_save = {
            "session_details": self._serialize_session(
                session_obj
            ),  # Serialize TestSession object
            "execution_run_results": run_exec_results,  # Results from specific run type (e.g. comprehensive)
            "save_timestamp": datetime.now().isoformat(),
        }
        try:
            with open(session_file_path, "w") as f_out:
                json.dump(
                    session_data_to_save, f_out, indent=2, default=str
                )  # default=str for datetime
            self.logger.info(
                f"ΛTRACE: Session results for '{session_obj.session_id}' saved successfully to {session_file_path}."
            )
        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Failed to save session results for '{session_obj.session_id}' to {session_file_path}: {e}",
                exc_info=True,
            )

    # Human-readable comment: Private helper to serialize a TestSession object.
    def _serialize_session(self, session_obj: TestSession) -> Dict[str, Any]:  # Renamed
        """Serializes a TestSession object into a JSON-compatible dictionary."""
        self.logger.debug(f"ΛTRACE: Serializing session '{session_obj.session_id}'.")
        return {
            "session_id": session_obj.session_id,
            "start_time": session_obj.start_time.isoformat(),
            "end_time": (
                session_obj.end_time.isoformat() if session_obj.end_time else None
            ),
            "total_operations": session_obj.total_operations,
            "successful_operations": session_obj.successful_operations,
            "failed_operations": session_obj.failed_operations,
            "operations_data": [
                self._serialize_operation(op) for op in session_obj.operations
            ],  # Serialize each op
            "final_performance_summary": session_obj.performance_summary,
            "final_ai_insights": session_obj.ai_insights,
            "session_metadata": session_obj.metadata,
        }

    # Human-readable comment: Private helper to serialize a TestOperation object.
    def _serialize_operation(self, op_obj: TestOperation) -> Dict[str, Any]:  # Renamed
        """Serializes a TestOperation object into a JSON-compatible dictionary."""
        # self.logger.debug(f"ΛTRACE: Serializing operation '{op_obj.operation_id}'.") # Can be too verbose
        return {
            "operation_id": op_obj.operation_id,
            "type": op_obj.operation_type,
            "command_or_description": op_obj.command,
            "start_time": op_obj.start_time.isoformat(),
            "end_time": op_obj.end_time.isoformat() if op_obj.end_time else None,
            "duration_milliseconds": op_obj.duration_ms,
            "status": op_obj.status,
            "standard_output": op_obj.output,
            "standard_error": op_obj.error,
            "exit_code": op_obj.exit_code,
            "captured_performance_metrics": op_obj.performance_metrics,
            "ai_driven_analysis": op_obj.ai_analysis,
            "operation_context": op_obj.context,
        }

    # Human-readable comment: Private helper to deserialize TestSession data.
    def _deserialize_session(
        self, session_json_data: Dict[str, Any]
    ) -> TestSession:  # Renamed
        """Deserializes JSON data back into a TestSession object."""
        self.logger.debug(
            f"ΛTRACE: Deserializing session data for ID '{session_json_data.get('session_id', 'Unknown')}'."
        )
        deserialized_session = TestSession(
            session_id=session_json_data["session_id"],
            start_time=datetime.fromisoformat(session_json_data["start_time"]),
            end_time=(
                datetime.fromisoformat(session_json_data["end_time"])
                if session_json_data.get("end_time")
                else None
            ),
            total_operations=session_json_data.get("total_operations", 0),
            successful_operations=session_json_data.get("successful_operations", 0),
            failed_operations=session_json_data.get("failed_operations", 0),
            operations=[
                self._deserialize_operation(op_data)
                for op_data in session_json_data.get("operations_data", [])
            ],
            performance_summary=session_json_data.get("final_performance_summary", {}),
            ai_insights=session_json_data.get("final_ai_insights", {}),
            metadata=session_json_data.get("session_metadata", {}),
        )
        self.logger.debug(
            f"ΛTRACE: Session '{deserialized_session.session_id}' deserialized."
        )
        return deserialized_session

    # Human-readable comment: Private helper to deserialize TestOperation data.
    def _deserialize_operation(
        self, op_json_data: Dict[str, Any]
    ) -> TestOperation:  # Renamed
        """Deserializes JSON data back into a TestOperation object."""
        # self.logger.debug(f"ΛTRACE: Deserializing operation data for ID '{op_json_data.get('operation_id', 'Unknown')}'.") # Too verbose
        return TestOperation(
            operation_id=op_json_data["operation_id"],
            operation_type=op_json_data["type"],
            command=op_json_data["command_or_description"],
            start_time=datetime.fromisoformat(op_json_data["start_time"]),
            end_time=(
                datetime.fromisoformat(op_json_data["end_time"])
                if op_json_data.get("end_time")
                else None
            ),
            duration_ms=op_json_data["duration_milliseconds"],
            status=op_json_data["status"],
            output=op_json_data.get("standard_output", ""),
            error=op_json_data.get("standard_error", ""),
            exit_code=op_json_data.get("exit_code"),
            performance_metrics=op_json_data.get("captured_performance_metrics", {}),
            ai_analysis=op_json_data.get("ai_driven_analysis", {}),
            context=op_json_data.get("operation_context", {}),
        )

    # Human-readable comment: Private helper to format operations for reporting.
    def _format_operations_for_report(
        self, operations_list: List[TestOperation]
    ) -> List[Dict[str, Any]]:  # Renamed
        """Formats a list of TestOperation objects into a simplified list of dicts for reports."""
        self.logger.debug(
            f"ΛTRACE: Formatting {len(operations_list)} operations for report."
        )
        formatted_ops = []
        for op_obj in operations_list:
            formatted_ops.append(
                {
                    "command_summary": op_obj.command[:100]
                    + ("..." if len(op_obj.command) > 100 else ""),
                    "duration_ms": op_obj.duration_ms,
                    "status": op_obj.status,
                    "performance_category_ai": (
                        op_obj.ai_analysis.get("performance_category", "N/A")
                        if op_obj.ai_analysis
                        else "N/A"
                    ),
                    "error_present": bool(op_obj.error),
                }
            )
        return formatted_ops

    # =========================================================================
    # CONTINUOUS MONITORING (Private Helpers)
    # =========================================================================
    # Human-readable comment: Asynchronous core loop for continuous monitoring.
    async def _watch_loop_async(
        self, interval_seconds: int, auto_test_on_change: bool
    ) -> None:
        """The asynchronous core loop for continuous monitoring tasks."""
        self.logger.info(
            f"ΛTRACE: Async watch loop started. Interval: {interval_seconds}s, Auto-Test: {auto_test_on_change}."
        )
        last_fs_check_time = datetime.now()  # For filesystem change detection

        while self.is_watching:
            self.logger.debug(
                f"ΛTRACE: Watch loop iteration. Current time: {datetime.now().isoformat()}"
            )
            try:
                # Task 1: Capture performance metrics if enabled
                if self.performance_monitor:
                    current_perf_metrics = (
                        self.performance_monitor.capture_metrics()
                    )  # Logs internally
                    # Example: Log significant changes or specific metrics
                    if (
                        current_perf_metrics.get("cpu_percent_system", 0) > 75
                    ):  # Example threshold
                        self.logger.warning(
                            f"ΛTRACE: High system CPU usage detected: {current_perf_metrics['cpu_percent_system']:.1f}%"
                        )

                # Task 2: Check for file changes if auto_test_on_change is enabled
                if auto_test_on_change:
                    # This is a simplified check. A more robust solution might use watchdog library.
                    # For demonstration, checking a specific directory for *.py file modifications.
                    # Path needs to be configured appropriately.
                    # ΛNOTE: The watch_dir_path for change detection is hardcoded to 'self.workspace_path / "CORE" / "lukhas_dast"'. This should be made configurable (e.g., via constructor or a settings file) for broader applicability and easier maintenance.
                    watch_dir_path = (
                        self.workspace_path / "CORE" / "lukhas_dast"
                    )  # Example path
                    if watch_dir_path.exists():
                        for py_file in watch_dir_path.glob("*.py"):
                            try:
                                if (
                                    py_file.stat().st_mtime
                                    > last_fs_check_time.timestamp()
                                ):
                                    self.logger.info(
                                        f"ΛTRACE: File change detected: '{py_file.name}'. Triggering change-based test."
                                    )
                                    await self._run_change_triggered_test()  # Run specific tests
                                    last_fs_check_time = (
                                        datetime.now()
                                    )  # Update check time after test
                                    break  # Process one change per interval to avoid overwhelming system
                            except (
                                FileNotFoundError
                            ):  # File might be deleted during glob
                                self.logger.debug(
                                    f"ΛTRACE: File '{py_file.name}' not found during mtime check, possibly deleted."
                                )
                                continue  # Skip to next file
                            except Exception as fs_err:
                                self.logger.error(
                                    f"ΛTRACE: Error checking file '{py_file.name}' for changes: {fs_err}",
                                    exc_info=False,
                                )  # No need for full exc_info here
                    last_fs_check_time = (
                        datetime.now()
                    )  # Update check time even if no changes found in this iteration

                await asyncio.sleep(interval_seconds)  # Asynchronous sleep

            except asyncio.CancelledError:
                self.logger.info("ΛTRACE: Async watch loop was cancelled.")
                break
            except Exception as e:
                self.logger.error(
                    f"ΛTRACE: Error in async watch loop: {e}", exc_info=True
                )
                await asyncio.sleep(
                    interval_seconds
                )  # Wait before retrying after an error

    # Human-readable comment: Runs tests triggered by file changes during watch mode.
    async def _run_change_triggered_test(self) -> None:
        """Runs a quick suite of validation tests when a file change is detected."""
        self.logger.info("ΛTRACE: Running change-triggered validation tests...")
        change_session_id = (
            f"auto_change_test_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        )
        test_session = await self._start_session(change_session_id)
        self.logger.debug(
            f"ΛTRACE: Session '{change_session_id}' started for change-triggered test."
        )

        try:
            # Example: Run a small, specific set of validation tests or smoke tests
            # Path needs to be robust for the command.
            # ΛNOTE: The command path for change-triggered tests is hardcoded to 'self.workspace_path / 'CORE' / 'lukhas_dast''. This should be configurable or determined more dynamically.
            validation_commands = [
                f"cd {self.workspace_path / 'CORE' / 'lukhas_dast'} && python simple_test.py"
            ]
            await self._run_test_category(
                test_session, "Change_Validation_Suite", validation_commands
            )
            await self._end_session(
                test_session, status_str="completed_change_validation"
            )
            self.logger.info(
                f"ΛTRACE: Change-triggered tests completed for session '{change_session_id}'."
            )
        except Exception as e:
            self.logger.error(
                f"ΛTRACE: Error during change-triggered tests for session '{change_session_id}': {e}",
                exc_info=True,
            )
            await self._end_session(
                test_session,
                status_str="failed_change_validation",
                error_message=str(e),
            )

    # Human-readable comment: Stops the continuous monitoring mode.
    def stop_watching(self) -> Dict[str, Any]:
        """Stops the continuous monitoring watch loop if it is active."""
        self.logger.info("ΛTRACE: autotest.stop_watching() called.")
        if not self.is_watching:
            self.logger.info("ΛTRACE: Watch mode is not currently active.")
            return {
                "status": "not_monitoring",
                "message": "Continuous monitoring was not active.",
            }

        self.is_watching = False  # Signal the loop to stop
        # self.capture_enabled = False # If this flag is used by the loop

        if self.watch_thread and self.watch_thread.is_alive():
            self.logger.debug("ΛTRACE: Attempting to join watch_thread...")
            self.watch_thread.join(timeout=5.0)  # Wait for the thread to finish
            if self.watch_thread.is_alive():
                self.logger.warning(
                    "ΛTRACE: Watch thread did not terminate cleanly after 5s."
                )
            else:
                self.logger.info("ΛTRACE: Watch thread terminated successfully.")
        self.watch_thread = None

        self.logger.info("ΛTRACE: Continuous monitoring stopped successfully.")
        return {
            "status": "monitoring_stopped",
            "message": "Continuous monitoring has been stopped.",
        }


# =============================================================================
# MODULE-LEVEL ONE-LINE API FUNCTIONS (Public Interface)
# =============================================================================
# Human-readable comment: Module-level functions providing the one-line API.

_autotest_global_instance: Optional[AutomaticTestingSystem] = None


# Function to get or initialize the global instance
def _get_global_autotest_instance() -> AutomaticTestingSystem:
    """Ensures a single global instance of AutomaticTestingSystem is used for one-line API calls."""
    global _autotest_global_instance
    if _autotest_global_instance is None:
        logger.info(
            "ΛTRACE: Creating global AutomaticTestingSystem instance for one-line API."
        )
        # Default workspace path, can be made configurable if needed
        # For example, from an environment variable or a config file
        # ΛNOTE: The default_workspace path for the global AutomaticTestingSystem instance is hardcoded (with an environment variable fallback). Consider making this more configurable or discoverable, especially if the system needs to run in diverse environments or on different projects.
        default_workspace = Path(
            os.getenv(
                "LUKHAS_TEST_WORKSPACE",
                "/Users/A_G_I/LUKHAS_REBIRTH_Workspace/Lukhas_Private/Lukhas-Flagship-Prototype-Pre-Modularitation/prot2",
            )
        )
        _autotest_global_instance = AutomaticTestingSystem(
            workspace_path=default_workspace,
            enable_ai_analysis=True,  # Default to enabled
            enable_performance_monitoring=True,  # Default to enabled
        )
        logger.info(
            f"ΛTRACE: Global AutomaticTestingSystem instance created. Workspace: {default_workspace}"
        )
    return _autotest_global_instance


# One-line API function: autotest.run()
# ΛEXPOSE
async def run(test_type_str: str = "comprehensive") -> Dict[str, Any]:  # Renamed arg
    """One-line API: Runs a specified test suite (e.g., 'comprehensive', 'smoke')."""
    logger.info(f"ΛTRACE: Global autotest.run() invoked. Test type: '{test_type_str}'.")
    instance = _get_global_autotest_instance()
    return await instance.run(test_type=test_type_str)


# One-line API function: autotest.watch()
# ΛEXPOSE
async def watch(check_interval_seconds: int = 30) -> Dict[str, Any]:  # Renamed arg
    """One-line API: Starts continuous background monitoring."""
    logger.info(
        f"ΛTRACE: Global autotest.watch() invoked. Interval: {check_interval_seconds}s."
    )
    instance = _get_global_autotest_instance()
    return await instance.watch(interval_seconds=check_interval_seconds)


# One-line API function: autotest.report()
# ΛEXPOSE
async def report(session_id_str: Optional[str] = None) -> Dict[str, Any]:  # Renamed arg
    """One-line API: Generates a report for a session or the most recent one."""
    logger.info(
        f"ΛTRACE: Global autotest.report() invoked. Session ID: '{session_id_str if session_id_str else 'most_recent'}'."
    )
    instance = _get_global_autotest_instance()
    return await instance.report(session_id_to_report=session_id_str)


# One-line API function: autotest.stop()
# ΛEXPOSE
def stop() -> Dict[str, Any]:
    """One-line API: Stops continuous monitoring if active."""
    logger.info("ΛTRACE: Global autotest.stop() invoked.")
    instance = _get_global_autotest_instance()
    return instance.stop_watching()


# One-line API function: autotest.capture()
# ΛEXPOSE
async def capture(
    command_to_run: str, timeout_duration_seconds: int = 60
) -> TestOperation:  # Renamed args
    """One-line API: Captures and analyzes a single terminal command."""
    logger.info(
        f"ΛTRACE: Global autotest.capture() invoked. Command: '{command_to_run}', Timeout: {timeout_duration_seconds}s."
    )
    instance = _get_global_autotest_instance()
    return await instance.capture_terminal_operation(
        command_str=command_to_run, timeout_val_seconds=timeout_duration_seconds
    )


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: automatic_testing_system.py
# VERSION: 1.2.0 # Incremented due to JULES enhancements
# TIER SYSTEM: Tier 1-3 (Core testing infrastructure, advanced features like AI analysis might be higher tier)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Automated test execution (various types), Terminal command capture,
#               Performance monitoring & alerting, AI-powered test analysis & insights,
#               Session management & reporting, Continuous background monitoring.
# FUNCTIONS: run, watch, report, stop, capture (module-level one-line API).
# CLASSES: TestOperation, TestSession, PerformanceMonitor, AITestAnalyzer, AutomaticTestingSystem.
# DECORATORS: @dataclass.
# DEPENDENCIES: asyncio, json, logging, subprocess, time, psutil, threading, datetime,
#               pathlib, typing, hashlib. Optional: numpy, pandas, .test_framework.
# INTERFACES: Public module functions (run, watch, etc.) and AutomaticTestingSystem class.
# ERROR HANDLING: Exceptions during command execution, timeouts, and internal operations are caught and logged.
#                 Provides status and error details in return values.
# LOGGING: ΛTRACE_ENABLED via Python's logging module for detailed operational tracing.
#          Uses hierarchical loggers (e.g., ΛTRACE.core.automatic_testing_system.PerformanceMonitor).
# AUTHENTICATION: Not applicable directly; operates on the local system based on execution permissions.
# HOW TO USE:
#   import core.automatic_testing_system as autotest
#   async def my_tests():
#       results = await autotest.run(test_type="smoke")
#       print(results)
#       op_details = await autotest.capture("my_script.py --arg")
#       print(op_details.status)
# INTEGRATION NOTES: Uses secure command execution (shlex.split) for terminal operations.
#                    Falls back to shell=True with warning if parsing fails.
#                    Workspace path needs to be correctly configured.
#                    Optional dependencies (numpy, pandas) enhance AI analysis; system functions without them.
#                    The `lukhas_dast` path in example tests is hardcoded; make configurable for robustness.
# MAINTENANCE: Regularly update AI analysis rules and patterns.
#              Monitor performance of the testing system itself, especially the watch loop.
#              Ensure paths and commands in predefined test suites are current.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
