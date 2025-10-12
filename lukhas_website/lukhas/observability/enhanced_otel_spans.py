"""
Enhanced OpenTelemetry Span Coverage
====================================

P0-3 OBS-BURN: Advanced OpenTelemetry integration with >95% span coverage
for comprehensive distributed tracing across all LUKHAS services.

Features:
- Automatic span creation and management
- Context propagation across service boundaries
- Custom attributes for LUKHAS-specific operations
- Performance and error tracking
- Integration with T4/0.01% excellence monitoring
- Distributed tracing correlation
"""

import asyncio
import functools
import inspect
import logging
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

# Try to import OpenTelemetry components
try:
    from opentelemetry import baggage, context, trace  # noqa: F401  # TODO: opentelemetry.baggage; conside...
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.auto_instrumentation import (
        sitecustomize,  # noqa: F401  # TODO: opentelemetry.instrumentation....
    )
    from opentelemetry.propagators.composite import CompositePropagator
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.semconv.trace import SpanAttributes  # noqa: F401  # TODO: opentelemetry.semconv.trace.Sp...
    from opentelemetry.trace import Span, Status, StatusCode, Tracer
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Mock classes for when OpenTelemetry is not available
    class Span:
        def set_attribute(self, key, value): pass
        def set_status(self, status): pass
        def record_exception(self, exception): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass

    class Tracer:
        def start_as_current_span(self, name, **kwargs): return MockSpan()

logger = logging.getLogger(__name__)


class SpanType(Enum):
    """Types of spans for LUKHAS operations"""
    HTTP_REQUEST = "http.request"
    DATABASE_QUERY = "db.query"
    MEMORY_OPERATION = "memory.operation"
    CONSCIOUSNESS_PROCESS = "consciousness.process"
    IDENTITY_AUTH = "identity.auth"
    REGISTRY_LOOKUP = "registry.lookup"
    GOVERNANCE_CHECK = "governance.check"
    LEDGER_APPEND = "ledger.append"
    AI_INFERENCE = "ai.inference"
    VECTOR_SEARCH = "vector.search"


@dataclass
class SpanContext:
    """Enhanced span context with LUKHAS-specific attributes"""
    service_name: str
    operation_name: str
    span_type: SpanType
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    performance_target_ms: Optional[float] = None

    # Required T4/0.01% observability attributes
    correlation_id: Optional[str] = None
    lane: Optional[str] = None
    provider: Optional[str] = None
    rule_name: Optional[str] = None
    component: Optional[str] = None


@dataclass
class SpanMetrics:
    """Metrics collected during span execution"""
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    custom_metrics: Dict[str, float] = field(default_factory=dict)


# Context variables for span correlation
current_span_context: ContextVar[Optional[SpanContext]] = ContextVar('current_span_context', default=None)
current_trace_id: ContextVar[Optional[str]] = ContextVar('current_trace_id', default=None)


class MockSpan:
    """Mock span for when OpenTelemetry is not available"""
    def set_attribute(self, key: str, value: Any): pass
    def set_status(self, status: Any): pass
    def record_exception(self, exception: Exception): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass


class EnhancedTracer:
    """
    Enhanced OpenTelemetry tracer with LUKHAS-specific instrumentation
    and comprehensive span coverage for distributed tracing.
    """

    def __init__(self, service_name: str = "lukhas"):
        self.service_name = service_name
        self.tracer: Optional[Tracer] = None
        self.span_coverage_stats = {
            'total_spans': 0,
            'successful_spans': 0,
            'failed_spans': 0,
            'span_types': {},
            'services': {}
        }

        if OTEL_AVAILABLE:
            self.tracer = trace.get_tracer(__name__)
        else:
            logger.warning("OpenTelemetry not available, using mock tracer")

        logger.info(f"EnhancedTracer initialized for service: {service_name}")

    def create_span(self,
                   operation_name: str,
                   span_type: SpanType = SpanType.HTTP_REQUEST,
                   span_context: Optional[SpanContext] = None,
                   **attributes) -> Union[Span, MockSpan]:
        """Create a new span with enhanced context"""

        if not self.tracer:
            return MockSpan()

        # Create span context if not provided
        if not span_context:
            span_context = SpanContext(
                service_name=self.service_name,
                operation_name=operation_name,
                span_type=span_type
            )

        # Set current context
        current_span_context.set(span_context)

        # Create OpenTelemetry span
        span = self.tracer.start_as_current_span(operation_name)

        # Set standard attributes
        span.set_attribute("service.name", span_context.service_name)
        span.set_attribute("operation.name", span_context.operation_name)
        span.set_attribute("span.type", span_context.span_type.value)

        # Set LUKHAS-specific attributes
        if span_context.user_id:
            span.set_attribute("user.id", span_context.user_id)
        if span_context.session_id:
            span.set_attribute("session.id", span_context.session_id)
        if span_context.request_id:
            span.set_attribute("request.id", span_context.request_id)
        if span_context.performance_target_ms:
            span.set_attribute("performance.target_ms", span_context.performance_target_ms)

        # Set T4/0.01% required observability attributes
        if span_context.correlation_id:
            span.set_attribute("lukhas.correlation_id", span_context.correlation_id)
        if span_context.lane:
            span.set_attribute("lukhas.lane", span_context.lane)
        if span_context.provider:
            span.set_attribute("lukhas.provider", span_context.provider)
        if span_context.rule_name:
            span.set_attribute("lukhas.rule_name", span_context.rule_name)
        if span_context.component:
            span.set_attribute("lukhas.component", span_context.component)

        # Set custom attributes
        for key, value in span_context.custom_attributes.items():
            span.set_attribute(f"custom.{key}", value)

        # Set additional attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)

        # Update coverage stats
        self.span_coverage_stats['total_spans'] += 1
        span_type_key = span_type.value
        self.span_coverage_stats['span_types'][span_type_key] = \
            self.span_coverage_stats['span_types'].get(span_type_key, 0) + 1

        service_key = span_context.service_name
        self.span_coverage_stats['services'][service_key] = \
            self.span_coverage_stats['services'].get(service_key, 0) + 1

        return span

    def trace_operation(self,
                       operation_name: str,
                       span_type: SpanType = SpanType.HTTP_REQUEST,
                       performance_target_ms: Optional[float] = None,
                       capture_args: bool = False,
                       capture_result: bool = False):
        """Decorator for automatic span creation and management"""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_with_span(
                    func, operation_name, span_type, performance_target_ms,
                    capture_args, capture_result, args, kwargs
                )

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(self._execute_with_span(
                    func, operation_name, span_type, performance_target_ms,
                    capture_args, capture_result, args, kwargs
                ))

            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    async def _execute_with_span(self,
                               func: Callable,
                               operation_name: str,
                               span_type: SpanType,
                               performance_target_ms: Optional[float],
                               capture_args: bool,
                               capture_result: bool,
                               args: tuple,
                               kwargs: dict) -> Any:
        """Execute function with span tracing"""

        span_context = SpanContext(
            service_name=self.service_name,
            operation_name=operation_name,
            span_type=span_type,
            performance_target_ms=performance_target_ms
        )

        with self.create_span(operation_name, span_type, span_context) as span:
            start_time = time.perf_counter()
            result = None
            success = True
            error_type = None

            try:
                # Capture function arguments if requested
                if capture_args:
                    span.set_attribute("function.args_count", len(args))
                    span.set_attribute("function.kwargs_count", len(kwargs))

                    # Capture specific argument values (be careful with sensitive data)
                    if args:
                        span.set_attribute("function.first_arg_type", type(args[0]).__name__)

                # Execute the function
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Capture result if requested
                if capture_result and result is not None:
                    span.set_attribute("function.result_type", type(result).__name__)
                    if hasattr(result, '__len__'):
                        try:
                            span.set_attribute("function.result_length", len(result))
                        except:
                            pass

            except Exception as e:
                success = False
                error_type = type(e).__name__

                # Record exception in span
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("error.type", error_type)
                span.set_attribute("error.message", str(e))

                # Re-raise the exception
                raise

            finally:
                # Record execution metrics
                duration_ms = (time.perf_counter() - start_time) * 1000

                span.set_attribute("execution.duration_ms", duration_ms)
                span.set_attribute("execution.success", success)

                if error_type:
                    span.set_attribute("execution.error_type", error_type)

                # Check performance target
                if performance_target_ms and duration_ms > performance_target_ms:
                    span.set_attribute("performance.target_exceeded", True)
                    span.set_attribute("performance.target_violation_ms",
                                     duration_ms - performance_target_ms)

                # Update coverage stats
                if success:
                    self.span_coverage_stats['successful_spans'] += 1
                else:
                    self.span_coverage_stats['failed_spans'] += 1

                # Set span status
                if success:
                    span.set_status(Status(StatusCode.OK))

            return result

    def trace_memory_operation(self,
                             operation: str,
                             fold_id: Optional[str] = None,
                             performance_target_ms: float = 100.0):
        """Specific tracer for memory operations"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                span_context = SpanContext(
                    service_name="memory",
                    operation_name=f"memory.{operation}",
                    span_type=SpanType.MEMORY_OPERATION,
                    performance_target_ms=performance_target_ms,
                    custom_attributes={"fold_id": fold_id} if fold_id else {}
                )

                with self.create_span(f"memory.{operation}", SpanType.MEMORY_OPERATION, span_context) as span:
                    # Set memory-specific attributes
                    if fold_id:
                        span.set_attribute("memory.fold_id", fold_id)

                    span.set_attribute("memory.operation", operation)

                    # Execute with timing
                    start_time = time.perf_counter()
                    try:
                        if inspect.iscoroutinefunction(func):
                            result = await func(*args, **kwargs)
                        else:
                            result = func(*args, **kwargs)

                        duration_ms = (time.perf_counter() - start_time) * 1000

                        # Set result attributes
                        if hasattr(result, '__len__'):
                            span.set_attribute("memory.result_count", len(result))

                        # Check T4 compliance
                        if duration_ms <= performance_target_ms:
                            span.set_attribute("memory.t4_compliant", True)
                        else:
                            span.set_attribute("memory.t4_compliant", False)
                            span.set_attribute("memory.t4_violation_ms", duration_ms - performance_target_ms)

                        span.set_status(Status(StatusCode.OK))
                        return result

                    except Exception as e:
                        duration_ms = (time.perf_counter() - start_time) * 1000
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.set_attribute("memory.error", True)
                        raise

                    finally:
                        duration_ms = (time.perf_counter() - start_time) * 1000
                        span.set_attribute("memory.duration_ms", duration_ms)

            return wrapper
        return decorator

    def trace_identity_operation(self,
                               operation: str,
                               user_id: Optional[str] = None,
                               performance_target_ms: float = 100.0):
        """Specific tracer for identity operations"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                span_context = SpanContext(
                    service_name="identity",
                    operation_name=f"identity.{operation}",
                    span_type=SpanType.IDENTITY_AUTH,
                    user_id=user_id,
                    performance_target_ms=performance_target_ms
                )

                with self.create_span(f"identity.{operation}", SpanType.IDENTITY_AUTH, span_context) as span:
                    # Set identity-specific attributes
                    if user_id:
                        span.set_attribute("identity.user_id", user_id)

                    span.set_attribute("identity.operation", operation)

                    # Execute and track
                    start_time = time.perf_counter()
                    try:
                        if inspect.iscoroutinefunction(func):
                            result = await func(*args, **kwargs)
                        else:
                            result = func(*args, **kwargs)

                        # Set success attributes
                        span.set_attribute("identity.success", True)
                        if hasattr(result, 'get'):
                            # For auth results
                            if 'authenticated' in str(result):
                                span.set_attribute("identity.authenticated", True)

                        span.set_status(Status(StatusCode.OK))
                        return result

                    except Exception as e:
                        span.set_attribute("identity.success", False)
                        span.set_attribute("identity.error_type", type(e).__name__)
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise

                    finally:
                        duration_ms = (time.perf_counter() - start_time) * 1000
                        span.set_attribute("identity.duration_ms", duration_ms)

                        # Check performance target
                        if duration_ms > performance_target_ms:
                            span.set_attribute("identity.slow_operation", True)

            return wrapper
        return decorator

    def trace_consciousness_process(self,
                                  process: str,
                                  performance_target_ms: float = 500.0):
        """Specific tracer for consciousness processes"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                span_context = SpanContext(
                    service_name="consciousness",
                    operation_name=f"consciousness.{process}",
                    span_type=SpanType.CONSCIOUSNESS_PROCESS,
                    performance_target_ms=performance_target_ms
                )

                with self.create_span(f"consciousness.{process}", SpanType.CONSCIOUSNESS_PROCESS, span_context) as span:
                    # Set consciousness-specific attributes
                    span.set_attribute("consciousness.process", process)

                    start_time = time.perf_counter()
                    try:
                        if inspect.iscoroutinefunction(func):
                            result = await func(*args, **kwargs)
                        else:
                            result = func(*args, **kwargs)

                        # Analyze consciousness result
                        if hasattr(result, 'get'):
                            if 'awareness_level' in str(result):
                                span.set_attribute("consciousness.awareness_detected", True)
                            if 'drift' in str(result):
                                span.set_attribute("consciousness.drift_detected", True)

                        span.set_status(Status(StatusCode.OK))
                        return result

                    except Exception as e:
                        span.set_attribute("consciousness.process_failed", True)
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise

                    finally:
                        duration_ms = (time.perf_counter() - start_time) * 1000
                        span.set_attribute("consciousness.processing_time_ms", duration_ms)

            return wrapper
        return decorator

    def get_coverage_metrics(self) -> Dict[str, Any]:
        """Get span coverage metrics"""
        total_spans = self.span_coverage_stats['total_spans']
        successful_spans = self.span_coverage_stats['successful_spans']

        coverage_rate = successful_spans / total_spans if total_spans > 0 else 0
        error_rate = (total_spans - successful_spans) / total_spans if total_spans > 0 else 0

        return {
            'total_spans': total_spans,
            'successful_spans': successful_spans,
            'failed_spans': self.span_coverage_stats['failed_spans'],
            'coverage_rate': coverage_rate,
            'error_rate': error_rate,
            'span_types': dict(self.span_coverage_stats['span_types']),
            'services': dict(self.span_coverage_stats['services']),
            'coverage_target': 0.95,  # 95% target
            'coverage_compliant': coverage_rate >= 0.95
        }

    def inject_trace_context(self, carrier: Dict[str, str]) -> Dict[str, str]:
        """Inject trace context into carrier for cross-service calls"""
        if not OTEL_AVAILABLE:
            return carrier

        propagator = TraceContextTextMapPropagator()
        propagator.inject(carrier)
        return carrier

    def extract_trace_context(self, carrier: Dict[str, str]) -> Optional[context.Context]:
        """Extract trace context from carrier"""
        if not OTEL_AVAILABLE:
            return None

        propagator = TraceContextTextMapPropagator()
        return propagator.extract(carrier)

    def create_child_span(self,
                         operation_name: str,
                         parent_context: Optional[context.Context] = None) -> Union[Span, MockSpan]:
        """Create a child span with proper parent context"""
        if not self.tracer:
            return MockSpan()

        if parent_context:
            # Use provided parent context
            with context.use_context(parent_context):
                return self.tracer.start_as_current_span(operation_name)
        else:
            # Use current context
            return self.tracer.start_as_current_span(operation_name)


# Global enhanced tracer instance
_global_enhanced_tracer: Optional[EnhancedTracer] = None


def get_enhanced_tracer(service_name: str = "lukhas") -> EnhancedTracer:
    """Get global enhanced tracer instance"""
    global _global_enhanced_tracer
    if _global_enhanced_tracer is None:
        _global_enhanced_tracer = EnhancedTracer(service_name)
    return _global_enhanced_tracer


def initialize_enhanced_tracing(service_name: str = "lukhas",
                              jaeger_endpoint: Optional[str] = None,
                              console_export: bool = False) -> EnhancedTracer:
    """Initialize enhanced OpenTelemetry tracing"""
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available")
        return EnhancedTracer(service_name)

    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()

    # Set up exporters
    if jaeger_endpoint:
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)

    if console_export:
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(console_processor)

    # Set up propagators
    propagators = [
        TraceContextTextMapPropagator(),
        W3CBaggagePropagator()
    ]
    composite_propagator = CompositePropagator(propagators)
    trace.set_global_textmap(composite_propagator)

    logger.info(f"Enhanced OpenTelemetry tracing initialized for {service_name}")
    return get_enhanced_tracer(service_name)


# Convenience decorators
def trace_memory(operation: str, performance_target_ms: float = 100.0):
    """Convenience decorator for memory operations"""
    tracer = get_enhanced_tracer("memory")
    return tracer.trace_memory_operation(operation, performance_target_ms=performance_target_ms)


def trace_identity(operation: str, performance_target_ms: float = 100.0):
    """Convenience decorator for identity operations"""
    tracer = get_enhanced_tracer("identity")
    return tracer.trace_identity_operation(operation, performance_target_ms=performance_target_ms)


def trace_consciousness(process: str, performance_target_ms: float = 500.0):
    """Convenience decorator for consciousness processes"""
    tracer = get_enhanced_tracer("consciousness")
    return tracer.trace_consciousness_process(process, performance_target_ms=performance_target_ms)


def trace_operation(operation_name: str,
                   span_type: SpanType = SpanType.HTTP_REQUEST,
                   performance_target_ms: Optional[float] = None,
                   service_name: str = "lukhas"):
    """General operation tracing decorator"""
    tracer = get_enhanced_tracer(service_name)
    return tracer.trace_operation(
        operation_name,
        span_type,
        performance_target_ms
    )
