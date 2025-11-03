#!/usr/bin/env python3
"""
LUKHAS Core Reliability Module

Enterprise-grade reliability patterns for 0.01% systems.
This module provides the subtle but critical patterns that distinguish
top-tier systems from merely good ones.

Components:
- Circuit Breaker: Adaptive failure handling with intelligent thresholds
- Performance Regression Detection: Proactive monitoring of system degradation
- Error Context: Rich error correlation and intelligent classification
- Adaptive Timeouts: Learning timeout and backoff strategies
"""

from .adaptive_timeouts import (
    AdaptiveTimeoutManager,
    BackoffConfig,
    BackoffStrategy,
    IntelligentBackoff,
    TimeoutConfig,
    adaptive_timeout,
    execute_with_adaptive_timeout,
    execute_with_backoff,
    get_default_backoff,
    get_timeout_manager,
    intelligent_backoff,
    resilient_operation,
)
from .circuit_breaker import (
    AdaptiveCircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerRegistry,
    circuit_breaker,
    get_circuit_health,
    get_degraded_services,
)
from .error_context import (
    ErrorCategory,
    ErrorContext,
    ErrorContextManager,
    ErrorSeverity,
    capture_error_context,
    enhanced_error_handler,
    error_context,
    find_related_errors,
    get_error_context_from_exception,
    get_error_manager,
    get_error_summary,
)
from .performance_regression import (
    AlertSeverity,
    PerformanceBaseline,
    PerformanceRegressionDetector,
    RegressionAlert,
    get_performance_health,
    get_regression_detector,
    performance_monitor,
    record_operation_performance,
)

__all__ = [
    # Circuit Breaker
    "AdaptiveCircuitBreaker",
    # Adaptive Timeouts
    "AdaptiveTimeoutManager",
    "AlertSeverity",
    "BackoffConfig",
    "BackoffStrategy",
    "CircuitBreakerOpenError",
    "CircuitBreakerRegistry",
    "ErrorCategory",
    "ErrorContext",
    # Error Context
    "ErrorContextManager",
    "ErrorSeverity",
    "IntelligentBackoff",
    "PerformanceBaseline",
    # Performance Regression
    "PerformanceRegressionDetector",
    "RegressionAlert",
    "TimeoutConfig",
    "adaptive_timeout",
    "capture_error_context",
    "circuit_breaker",
    "enhanced_error_handler",
    "error_context",
    "execute_with_adaptive_timeout",
    "execute_with_backoff",
    "find_related_errors",
    "get_circuit_health",
    "get_default_backoff",
    "get_degraded_services",
    "get_error_context_from_exception",
    "get_error_manager",
    "get_error_summary",
    "get_performance_health",
    "get_regression_detector",
    "get_timeout_manager",
    "intelligent_backoff",
    "performance_monitor",
    "record_operation_performance",
    "resilient_operation"
]


def get_reliability_health_status() -> dict:
    """Get comprehensive reliability system health status."""
    from .circuit_breaker import get_circuit_health
    from .error_context import get_error_summary
    from .performance_regression import get_performance_health

    return {
        "circuit_breakers": get_circuit_health(),
        "performance_monitoring": get_performance_health(),
        "error_tracking": get_error_summary(hours=1),  # Last hour
        "timestamp": __import__("time").time(),
        "reliability_systems_operational": True
    }
