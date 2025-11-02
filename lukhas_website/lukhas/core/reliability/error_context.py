#!/usr/bin/env python3
"""
Enhanced Error Context and Correlation for 0.01% Reliability

Rich error context with correlation IDs, causal chains, and intelligent
error classification - the kind of debugging visibility that transforms
incident response from hours to minutes.
"""

import time
import traceback
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from observability.opentelemetry_tracing import LUKHASTracer
from observability.prometheus_metrics import LUKHASMetrics


class ErrorCategory(Enum):
    SYSTEM = "system"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RESOURCE = "resource"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Rich error context with correlation and causality."""

    error_id: str
    correlation_id: str
    timestamp: float
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception_type: str
    stack_trace: List[str]
    operation: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    causal_chain: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    related_errors: List[str] = field(default_factory=list)


# Context variables for correlation
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
_causal_chain: ContextVar[List[str]] = ContextVar("causal_chain", default=[])
_operation_context: ContextVar[Dict[str, Any]] = ContextVar("operation_context", default={})


class ErrorContextManager:
    """
    Central error context manager with intelligent classification.

    0.01% Features:
    - Automatic error categorization using heuristics
    - Causal chain tracking across operation boundaries
    - System state capture at error time
    - Error pattern detection and clustering
    """

    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.error_patterns: Dict[str, int] = {}
        self.correlation_map: Dict[str, List[str]] = {}

        self.metrics = LUKHASMetrics()
        self.tracer = LUKHASTracer()

        # Configuration
        self.max_history_size = 10000
        self.pattern_threshold = 3  # Minimum occurrences to identify pattern

    def capture_error(
        self,
        exception: Exception,
        operation: str,
        additional_context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ErrorContext:
        """Capture comprehensive error context."""

        # Generate error ID
        error_id = str(uuid.uuid4())

        # Get correlation context
        correlation_id = _correlation_id.get() or f"err_{int(time.time() * 1000)}"
        causal_chain = _causal_chain.get().copy()
        causal_chain.append(error_id)

        # Classify error
        category = self._classify_error(exception)
        severity = self._assess_severity(exception, category)

        # Capture stack trace
        stack_trace = traceback.format_exception(type(exception), exception, exception.__traceback__)

        # Gather system state
        system_state = self._capture_system_state()

        # Combine context data
        context_data = {}
        context_data.update(_operation_context.get())
        if additional_context:
            context_data.update(additional_context)

        # Create error context
        error_context = ErrorContext(
            error_id=error_id,
            correlation_id=correlation_id,
            timestamp=time.time(),
            category=category,
            severity=severity,
            message=str(exception),
            exception_type=type(exception).__name__,
            stack_trace=stack_trace,
            operation=operation,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            causal_chain=causal_chain,
            context_data=context_data,
            system_state=system_state,
        )

        # Store and analyze
        self._store_error(error_context)
        self._analyze_patterns(error_context)

        # Record metrics
        self.metrics.record_error_context(
            category=category.value, severity=severity.value, operation=operation, correlation_id=correlation_id
        )

        # Add to trace
        with self.tracer.trace_operation("error_capture") as span:
            span.set_attribute("error_id", error_id)
            span.set_attribute("correlation_id", correlation_id)
            span.set_attribute("category", category.value)
            span.set_attribute("severity", severity.value)
            span.set_attribute("operation", operation)

        return error_context

    def _classify_error(self, exception: Exception) -> ErrorCategory:
        """Automatically classify error using intelligent heuristics."""
        exception_name = type(exception).__name__.lower()
        message = str(exception).lower()

        # Network-related errors
        if any(term in exception_name for term in ["connection", "timeout", "network", "socket"]):
            return ErrorCategory.NETWORK
        if any(term in message for term in ["connection refused", "timeout", "network unreachable"]):
            return ErrorCategory.NETWORK

        # Authentication errors
        if any(term in exception_name for term in ["auth", "login", "credential"]):
            return ErrorCategory.AUTHENTICATION
        if any(term in message for term in ["unauthorized", "invalid credentials", "authentication"]):
            return ErrorCategory.AUTHENTICATION

        # Authorization errors
        if any(term in exception_name for term in ["permission", "access", "forbidden"]):
            return ErrorCategory.AUTHORIZATION
        if any(term in message for term in ["forbidden", "access denied", "permission"]):
            return ErrorCategory.AUTHORIZATION

        # Validation errors
        if any(term in exception_name for term in ["validation", "value", "type", "attribute"]):
            return ErrorCategory.VALIDATION
        if any(term in message for term in ["invalid", "required", "validation", "format"]):
            return ErrorCategory.VALIDATION

        # Resource errors
        if any(term in exception_name for term in ["memory", "resource", "disk", "file"]):
            return ErrorCategory.RESOURCE
        if any(term in message for term in ["out of memory", "disk full", "resource", "file not found"]):
            return ErrorCategory.RESOURCE

        # External service errors
        if any(term in exception_name for term in ["http", "api", "service", "external"]):
            return ErrorCategory.EXTERNAL
        if any(term in message for term in ["service unavailable", "api error", "external"]):
            return ErrorCategory.EXTERNAL

        # System errors
        if any(term in exception_name for term in ["system", "os", "runtime"]):
            return ErrorCategory.SYSTEM

        return ErrorCategory.UNKNOWN

    def _assess_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Assess error severity based on type and category."""
        exception_name = type(exception).__name__.lower()
        message = str(exception).lower()

        # Critical severity indicators
        if any(term in exception_name for term in ["critical", "fatal", "system"]):
            return ErrorSeverity.CRITICAL
        if any(term in message for term in ["critical", "fatal", "system failure"]):
            return ErrorSeverity.CRITICAL
        if category == ErrorCategory.SYSTEM:
            return ErrorSeverity.CRITICAL

        # High severity indicators
        if any(term in exception_name for term in ["security", "auth", "permission"]):
            return ErrorSeverity.HIGH
        if any(term in message for term in ["security", "unauthorized", "forbidden"]):
            return ErrorSeverity.HIGH
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.HIGH

        # Medium severity indicators
        if category in [ErrorCategory.NETWORK, ErrorCategory.EXTERNAL, ErrorCategory.RESOURCE]:
            return ErrorSeverity.MEDIUM

        # Default to low
        return ErrorSeverity.LOW

    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture relevant system state at error time."""
        try:
            import os

            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "process_id": os.getpid(),
                "thread_count": psutil.Process().num_threads(),
                "open_files": len(psutil.Process().open_files()),
                "timestamp": time.time(),
            }
        except ImportError:
            # Fallback to basic system info
            import os

            return {"process_id": os.getpid(), "timestamp": time.time()}
        except Exception:
            return {"timestamp": time.time()}

    def _store_error(self, error_context: ErrorContext) -> None:
        """Store error context with intelligent cleanup."""
        self.error_history.append(error_context)

        # Maintain correlation mapping
        if error_context.correlation_id not in self.correlation_map:
            self.correlation_map[error_context.correlation_id] = []
        self.correlation_map[error_context.correlation_id].append(error_context.error_id)

        # Cleanup old entries
        if len(self.error_history) > self.max_history_size:
            old_error = self.error_history.pop(0)
            # Clean up correlation map
            if old_error.correlation_id in self.correlation_map:
                try:
                    self.correlation_map[old_error.correlation_id].remove(old_error.error_id)
                    if not self.correlation_map[old_error.correlation_id]:
                        del self.correlation_map[old_error.correlation_id]
                except ValueError:
                    pass

    def _analyze_patterns(self, error_context: ErrorContext) -> None:
        """Analyze error patterns for proactive insights."""
        # Create pattern key
        pattern_key = f"{error_context.category.value}:{error_context.exception_type}:{error_context.operation}"

        # Update pattern count
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1

        # Check for concerning patterns
        if self.error_patterns[pattern_key] >= self.pattern_threshold:
            print(f"🔍 Error pattern detected: {pattern_key} (occurred {self.error_patterns[pattern_key]} times)")

    def get_related_errors(self, correlation_id: str) -> List[ErrorContext]:
        """Get all errors related to a correlation ID."""
        if correlation_id not in self.correlation_map:
            return []

        error_ids = self.correlation_map[correlation_id]
        return [error for error in self.error_history if error.error_id in error_ids]

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the specified time window."""
        cutoff_time = time.time() - (hours * 3600)
        recent_errors = [error for error in self.error_history if error.timestamp >= cutoff_time]

        # Count by category
        category_counts = {}
        severity_counts = {}
        operation_counts = {}

        for error in recent_errors:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            operation_counts[error.operation] = operation_counts.get(error.operation, 0) + 1

        # Find top patterns
        top_patterns = sorted(
            [(pattern, count) for pattern, count in self.error_patterns.items() if count >= self.pattern_threshold],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        return {
            "time_window_hours": hours,
            "total_errors": len(recent_errors),
            "unique_correlations": len(set(error.correlation_id for error in recent_errors)),
            "categories": category_counts,
            "severities": severity_counts,
            "top_operations": dict(sorted(operation_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "recurring_patterns": dict(top_patterns),
            "error_rate_per_hour": len(recent_errors) / max(hours, 1),
        }


# Global error context manager
_error_manager: Optional[ErrorContextManager] = None


def get_error_manager() -> ErrorContextManager:
    """Get or create the global error context manager."""
    global _error_manager
    if _error_manager is None:
        _error_manager = ErrorContextManager()
    return _error_manager


@contextmanager
def error_context(
    operation: str,
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **context_data,
):
    """Context manager for enhanced error tracking."""
    # Set correlation context
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    correlation_token = _correlation_id.set(correlation_id)
    context_token = _operation_context.set(context_data)

    try:
        yield correlation_id
    except Exception as e:
        # Capture error context
        manager = get_error_manager()
        error_ctx = manager.capture_error(
            exception=e, operation=operation, user_id=user_id, session_id=session_id, request_id=request_id
        )

        # Add error context to exception
        if not hasattr(e, "_lukhas_error_context"):
            e._lukhas_error_context = error_ctx

        raise
    finally:
        _correlation_id.reset(correlation_token)
        _operation_context.reset(context_token)


def capture_error_context(exception: Exception, operation: str, **kwargs) -> ErrorContext:
    """Capture error context for an exception."""
    manager = get_error_manager()
    return manager.capture_error(exception, operation, **kwargs)


def get_error_context_from_exception(exception: Exception) -> Optional[ErrorContext]:
    """Get error context from an exception if available."""
    return getattr(exception, "_lukhas_error_context", None)


def enhanced_error_handler(operation_name: str):
    """Decorator for automatic error context capture."""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with error_context(operation_name, **kwargs):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            with error_context(operation_name, **kwargs):
                return func(*args, **kwargs)

        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def get_error_summary(hours: int = 24) -> Dict[str, Any]:
    """Get comprehensive error summary."""
    manager = get_error_manager()
    return manager.get_error_summary(hours)


def find_related_errors(correlation_id: str) -> List[ErrorContext]:
    """Find all errors related to a correlation ID."""
    manager = get_error_manager()
    return manager.get_related_errors(correlation_id)
