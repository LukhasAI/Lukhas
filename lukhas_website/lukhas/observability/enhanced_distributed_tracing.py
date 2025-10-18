#!/usr/bin/env python3
"""
LUKHAS Enhanced Distributed Tracing
Comprehensive distributed tracing integration across all LUKHAS components.

Features:
- Cross-component correlation and tracing
- Evidence collection tracing integration
- Performance regression detection tracing
- Compliance dashboard operation tracing
- Advanced metrics and alerting tracing
- Custom LUKHAS semantic conventions
- Intelligent trace sampling and filtering
- Trace-based performance analysis
"""

import asyncio
import functools
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

try:
    from opentelemetry import baggage, context, propagate, trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
    from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.propagators.b3 import B3MultiFormat, B3SingleFormat
    from opentelemetry.propagators.jaeger import JaegerPropagator
    from opentelemetry.sdk.trace import Span, TracerProvider  # noqa: F401  # TODO: opentelemetry.sdk.trace.Span; ...
    from opentelemetry.sdk.trace.export import (  # noqa: F401  # TODO: opentelemetry.sdk.trace.export...
        BatchSpanProcessor,
        SpanExporter,
    )
    from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
    from opentelemetry.semconv.trace import SpanAttributes  # noqa: F401  # TODO: opentelemetry.semconv.trace.Sp...
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.trace.status import Status, StatusCode
    from opentelemetry.util.http import get_excluded_urls  # noqa: F401  # TODO: opentelemetry.util.http.get_ex...

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Mock implementations for when OpenTelemetry is not available
    trace = None


# LUKHAS-specific semantic conventions
class LUKHASSemanticConventions:
    """Semantic conventions for LUKHAS distributed tracing"""

    # Component attributes
    LUKHAS_COMPONENT = "component"
    LUKHAS_COMPONENT_VERSION = "component.version"
    LUKHAS_OPERATION = "operation"
    LUKHAS_OPERATION_TYPE = "operation.type"

    # Evidence collection attributes
    LUKHAS_EVIDENCE_ID = "evidence.id"
    LUKHAS_EVIDENCE_TYPE = "evidence.type"
    LUKHAS_EVIDENCE_SIZE = "evidence.size"
    LUKHAS_EVIDENCE_INTEGRITY = "evidence.integrity"

    # Performance attributes
    LUKHAS_PERFORMANCE_BASELINE = "performance.baseline"
    LUKHAS_PERFORMANCE_CURRENT = "performance.current"
    LUKHAS_PERFORMANCE_DEGRADATION = "performance.degradation"
    LUKHAS_PERFORMANCE_REGRESSION_ID = "performance.regression_id"

    # Compliance attributes
    LUKHAS_COMPLIANCE_REGIME = "compliance.regime"
    LUKHAS_COMPLIANCE_SCORE = "compliance.score"
    LUKHAS_COMPLIANCE_VIOLATION = "compliance.violation"

    # Memory system attributes
    LUKHAS_MEMORY_OPERATION = "memory.operation"
    LUKHAS_MEMORY_ITEM_COUNT = "memory.item_count"
    LUKHAS_MEMORY_SIZE_BYTES = "memory.size_bytes"
    LUKHAS_MEMORY_COMPRESSION_RATIO = "memory.compression_ratio"

    # Identity system attributes
    LUKHAS_IDENTITY_USER_ID = "identity.user_id"
    LUKHAS_IDENTITY_SESSION_ID = "identity.session_id"
    LUKHAS_IDENTITY_AUTH_TIER = "identity.auth_tier"
    LUKHAS_IDENTITY_TOKEN_ID = "identity.token_id"

    # Orchestrator attributes
    LUKHAS_ORCHESTRATOR_PIPELINE_ID = "orchestrator.pipeline_id"
    LUKHAS_ORCHESTRATOR_STAGE = "orchestrator.stage"
    LUKHAS_ORCHESTRATOR_WITHIN_BUDGET = "orchestrator.within_budget"

    # Alerting attributes
    LUKHAS_ALERT_ID = "alert.id"
    LUKHAS_ALERT_RULE_ID = "alert.rule_id"
    LUKHAS_ALERT_SEVERITY = "alert.severity"
    LUKHAS_ALERT_ESCALATION_LEVEL = "alert.escalation_level"


@dataclass
class TraceConfig:
    """Configuration for enhanced distributed tracing"""
    service_name: str = "lukhas-ai"
    service_version: str = "1.0.0"
    jaeger_endpoint: Optional[str] = None
    otlp_endpoint: Optional[str] = None
    sampling_ratio: float = 1.0
    enable_auto_instrumentation: bool = True
    enable_baggage_propagation: bool = True
    custom_propagators: List[str] = field(default_factory=lambda: ["tracecontext", "baggage"])
    span_batch_size: int = 512
    span_export_timeout_ms: int = 30000
    enable_performance_tracing: bool = True
    enable_evidence_tracing: bool = True
    enable_compliance_tracing: bool = True


class EnhancedLUKHASTracer:
    """
    Enhanced distributed tracing system for LUKHAS components.
    Provides comprehensive tracing with custom semantic conventions.
    """

    def __init__(self, config: TraceConfig):
        """
        Initialize enhanced LUKHAS tracer.

        Args:
            config: Trace configuration
        """
        self.config = config
        self.enabled = OTEL_AVAILABLE

        if not OTEL_AVAILABLE:
            print("Warning: OpenTelemetry not available. Tracing disabled.")
            return

        # Initialize tracing
        self._setup_tracing()
        self._setup_propagation()
        self._setup_auto_instrumentation()

        # Get tracer
        self._tracer = trace.get_tracer(
            instrumenting_module_name=__name__,
            instrumenting_library_version=config.service_version,
        )

        # Trace correlation tracking
        self._correlation_map: Dict[str, str] = {}

    def _setup_tracing(self):
        """Setup OpenTelemetry tracing with custom configuration"""
        # Configure sampling
        if self.config.sampling_ratio < 1.0:
            sampler = ParentBased(root=TraceIdRatioBased(self.config.sampling_ratio))
        else:
            sampler = ParentBased()

        # Create tracer provider
        provider = TracerProvider(
            resource=self._create_resource(),
            sampler=sampler,
        )
        trace.set_tracer_provider(provider)

        # Setup exporters
        exporters = []

        # Jaeger exporter
        if self.config.jaeger_endpoint:
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.config.jaeger_endpoint.split(':')[0],
                agent_port=int(self.config.jaeger_endpoint.split(':')[1])
                if ':' in self.config.jaeger_endpoint else 14268,
            )
            exporters.append(jaeger_exporter)

        # OTLP exporter
        if self.config.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config.otlp_endpoint,
                timeout=self.config.span_export_timeout_ms // 1000,
            )
            exporters.append(otlp_exporter)

        # Console exporter for development
        if not exporters:
            from opentelemetry.exporter.console import ConsoleSpanExporter
            exporters.append(ConsoleSpanExporter())

        # Add span processors
        for exporter in exporters:
            processor = BatchSpanProcessor(
                exporter,
                max_queue_size=2048,
                max_export_batch_size=self.config.span_batch_size,
                export_timeout_millis=self.config.span_export_timeout_ms,
            )
            provider.add_span_processor(processor)

    def _create_resource(self):
        """Create OpenTelemetry resource with LUKHAS-specific attributes"""
        from opentelemetry.sdk.resources import Resource

        return Resource.create({
            "service.name": self.config.service_name,
            "service.version": self.config.service_version,
            "service.namespace": "lukhas",
            "deployment.environment": os.getenv("LUKHAS_ENV", "development"),
            "phase": "5",  # Phase 5 implementation
            "features": "enhanced_observability,evidence_collection,compliance_dashboard",
        })

    def _setup_propagation(self):
        """Setup trace context propagation"""
        propagators = []

        for prop_name in self.config.custom_propagators:
            if prop_name == "tracecontext":
                propagators.append(TraceContextTextMapPropagator())
            elif prop_name == "baggage":
                from opentelemetry.propagators.baggage import BaggagePropagator
                propagators.append(BaggagePropagator())
            elif prop_name == "jaeger":
                propagators.append(JaegerPropagator())
            elif prop_name == "b3":
                propagators.append(B3MultiFormat())
            elif prop_name == "b3single":
                propagators.append(B3SingleFormat())

        if propagators:
            from opentelemetry.propagators.composite import CompositePropagator
            propagate.set_global_textmap(CompositePropagator(propagators))

    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries"""
        if not self.config.enable_auto_instrumentation:
            return

        try:
            # HTTP clients and servers
            RequestsInstrumentor().instrument()

            if OTEL_AVAILABLE:
                AioHttpClientInstrumentor().instrument()
                AsyncioInstrumentor().instrument()

            # Database instrumentation (when available)
            try:
                SQLAlchemyInstrumentor().instrument()
            except Exception:
                pass  # SQLAlchemy not available

        except Exception as e:
            print(f"Warning: Auto-instrumentation setup failed: {e}")

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        component: str,
        operation_type: str = "generic",
        attributes: Optional[Dict[str, Any]] = None,
        baggage_items: Optional[Dict[str, str]] = None,
    ):
        """
        Context manager for tracing LUKHAS operations.

        Args:
            operation_name: Name of the operation
            component: LUKHAS component name
            operation_type: Type of operation
            attributes: Additional span attributes
            baggage_items: Baggage items to propagate
        """
        if not self.enabled:
            yield None
            return

        # Set baggage items
        if baggage_items and self.config.enable_baggage_propagation:
            ctx = context.get_current()
            for key, value in baggage_items.items():
                ctx = baggage.set_baggage(key, value, context=ctx)
            token = context.attach(ctx)
        else:
            token = None

        try:
            with self._tracer.start_as_current_span(operation_name) as span:
                # Set standard LUKHAS attributes
                span.set_attribute(LUKHASSemanticConventions.LUKHAS_COMPONENT, component)
                span.set_attribute(LUKHASSemanticConventions.LUKHAS_OPERATION, operation_name)
                span.set_attribute(LUKHASSemanticConventions.LUKHAS_OPERATION_TYPE, operation_type)
                span.set_attribute(LUKHASSemanticConventions.LUKHAS_COMPONENT_VERSION, self.config.service_version)

                # Set additional attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    yield span
                    span.set_status(Status(StatusCode.OK))
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        finally:
            if token:
                context.detach(token)

    def trace_evidence_operation(
        self,
        operation_name: str,
        evidence_id: str,
        evidence_type: str,
        evidence_size: Optional[int] = None,
        integrity_verified: Optional[bool] = None,
        correlation_id: Optional[str] = None,
    ):
        """Context manager for tracing evidence collection operations"""
        attributes = {
            LUKHASSemanticConventions.LUKHAS_EVIDENCE_ID: evidence_id,
            LUKHASSemanticConventions.LUKHAS_EVIDENCE_TYPE: evidence_type,
        }

        if evidence_size is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_EVIDENCE_SIZE] = evidence_size

        if integrity_verified is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_EVIDENCE_INTEGRITY] = str(integrity_verified)

        baggage_items = {}
        if correlation_id:
            baggage_items["correlation_id"] = correlation_id

        return self.trace_operation(
            operation_name=operation_name,
            component="evidence_collection",
            operation_type="evidence",
            attributes=attributes,
            baggage_items=baggage_items,
        )

    def trace_performance_operation(
        self,
        operation_name: str,
        metric_name: str,
        current_value: float,
        baseline_value: Optional[float] = None,
        degradation_percentage: Optional[float] = None,
        regression_id: Optional[str] = None,
    ):
        """Context manager for tracing performance operations"""
        attributes = {
            "metric.name": metric_name,
            LUKHASSemanticConventions.LUKHAS_PERFORMANCE_CURRENT: current_value,
        }

        if baseline_value is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_PERFORMANCE_BASELINE] = baseline_value

        if degradation_percentage is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_PERFORMANCE_DEGRADATION] = degradation_percentage

        if regression_id:
            attributes[LUKHASSemanticConventions.LUKHAS_PERFORMANCE_REGRESSION_ID] = regression_id

        return self.trace_operation(
            operation_name=operation_name,
            component="performance_regression",
            operation_type="performance",
            attributes=attributes,
        )

    def trace_compliance_operation(
        self,
        operation_name: str,
        compliance_regime: str,
        compliance_score: Optional[float] = None,
        violation_detected: bool = False,
    ):
        """Context manager for tracing compliance operations"""
        attributes = {
            LUKHASSemanticConventions.LUKHAS_COMPLIANCE_REGIME: compliance_regime,
            LUKHASSemanticConventions.LUKHAS_COMPLIANCE_VIOLATION: str(violation_detected),
        }

        if compliance_score is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_COMPLIANCE_SCORE] = compliance_score

        return self.trace_operation(
            operation_name=operation_name,
            component="compliance_dashboard",
            operation_type="compliance",
            attributes=attributes,
        )

    def trace_memory_operation(
        self,
        operation_name: str,
        operation_type: str,
        item_count: Optional[int] = None,
        size_bytes: Optional[int] = None,
        compression_ratio: Optional[float] = None,
    ):
        """Context manager for tracing memory system operations"""
        attributes = {
            LUKHASSemanticConventions.LUKHAS_MEMORY_OPERATION: operation_type,
        }

        if item_count is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_MEMORY_ITEM_COUNT] = item_count

        if size_bytes is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_MEMORY_SIZE_BYTES] = size_bytes

        if compression_ratio is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_MEMORY_COMPRESSION_RATIO] = compression_ratio

        return self.trace_operation(
            operation_name=operation_name,
            component="memory",
            operation_type="memory",
            attributes=attributes,
        )

    def trace_identity_operation(
        self,
        operation_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        auth_tier: Optional[str] = None,
        token_id: Optional[str] = None,
    ):
        """Context manager for tracing identity system operations"""
        attributes = {}

        if user_id:
            attributes[LUKHASSemanticConventions.LUKHAS_IDENTITY_USER_ID] = user_id

        if session_id:
            attributes[LUKHASSemanticConventions.LUKHAS_IDENTITY_SESSION_ID] = session_id

        if auth_tier:
            attributes[LUKHASSemanticConventions.LUKHAS_IDENTITY_AUTH_TIER] = auth_tier

        if token_id:
            attributes[LUKHASSemanticConventions.LUKHAS_IDENTITY_TOKEN_ID] = token_id

        return self.trace_operation(
            operation_name=operation_name,
            component="identity",
            operation_type="identity",
            attributes=attributes,
        )

    def trace_orchestrator_operation(
        self,
        operation_name: str,
        pipeline_id: Optional[str] = None,
        stage: Optional[str] = None,
        within_budget: Optional[bool] = None,
    ):
        """Context manager for tracing orchestrator operations"""
        attributes = {}

        if pipeline_id:
            attributes[LUKHASSemanticConventions.LUKHAS_ORCHESTRATOR_PIPELINE_ID] = pipeline_id

        if stage:
            attributes[LUKHASSemanticConventions.LUKHAS_ORCHESTRATOR_STAGE] = stage

        if within_budget is not None:
            attributes[LUKHASSemanticConventions.LUKHAS_ORCHESTRATOR_WITHIN_BUDGET] = str(within_budget)

        return self.trace_operation(
            operation_name=operation_name,
            component="orchestrator",
            operation_type="orchestrator",
            attributes=attributes,
        )

    def trace_alert_operation(
        self,
        operation_name: str,
        alert_id: str,
        rule_id: Optional[str] = None,
        severity: Optional[str] = None,
        escalation_level: Optional[str] = None,
    ):
        """Context manager for tracing alerting operations"""
        attributes = {
            LUKHASSemanticConventions.LUKHAS_ALERT_ID: alert_id,
        }

        if rule_id:
            attributes[LUKHASSemanticConventions.LUKHAS_ALERT_RULE_ID] = rule_id

        if severity:
            attributes[LUKHASSemanticConventions.LUKHAS_ALERT_SEVERITY] = severity

        if escalation_level:
            attributes[LUKHASSemanticConventions.LUKHAS_ALERT_ESCALATION_LEVEL] = escalation_level

        return self.trace_operation(
            operation_name=operation_name,
            component="intelligent_alerting",
            operation_type="alert",
            attributes=attributes,
        )

    def create_correlation_id(self, correlation_type: str = "request") -> str:
        """Create a new correlation ID for trace correlation"""
        correlation_id = f"{correlation_type}_{uuid4()}"

        # Store in correlation map
        if self.enabled:
            span = trace.get_current_span()
            if span.is_recording():
                trace_id = format(span.get_span_context().trace_id, '032x')
                self._correlation_map[correlation_id] = trace_id

        return correlation_id

    def get_current_trace_context(self) -> Dict[str, str]:
        """Get current trace context for propagation"""
        if not self.enabled:
            return {}

        carrier = {}
        propagate.inject(carrier)
        return carrier

    def set_trace_context(self, carrier: Dict[str, str]):
        """Set trace context from propagation carrier"""
        if not self.enabled or not carrier:
            return None

        ctx = propagate.extract(carrier)
        return context.attach(ctx)

    def add_span_event(
        self,
        event_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ):
        """Add an event to the current span"""
        if not self.enabled:
            return

        span = trace.get_current_span()
        if span.is_recording():
            event_attributes = attributes or {}
            event_timestamp = timestamp or datetime.now(timezone.utc)

            span.add_event(
                event_name,
                attributes=event_attributes,
                timestamp=int(event_timestamp.timestamp() * 1_000_000_000),  # nanoseconds
            )

    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get tracing statistics"""
        return {
            "enabled": self.enabled,
            "service_name": self.config.service_name,
            "service_version": self.config.service_version,
            "sampling_ratio": self.config.sampling_ratio,
            "correlation_count": len(self._correlation_map),
            "auto_instrumentation_enabled": self.config.enable_auto_instrumentation,
            "propagators": self.config.custom_propagators,
        }


def trace_lukhas_operation(
    operation_name: str,
    component: str,
    operation_type: str = "generic",
    **trace_kwargs
):
    """
    Decorator for tracing LUKHAS operations.

    Args:
        operation_name: Name of the operation
        component: LUKHAS component name
        operation_type: Type of operation
        **trace_kwargs: Additional trace arguments

    Example:
        @trace_lukhas_operation("memory_recall", "memory", "recall")
        def recall_memory(query):
            return memory_system.recall(query)
    """
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_enhanced_tracer()
            with tracer.trace_operation(
                operation_name=operation_name,
                component=component,
                operation_type=operation_type,
                **trace_kwargs
            ):
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_enhanced_tracer()
            with tracer.trace_operation(
                operation_name=operation_name,
                component=component,
                operation_type=operation_type,
                **trace_kwargs
            ):
                return await func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def trace_evidence_collection(evidence_type: str, **trace_kwargs):
    """Decorator for tracing evidence collection operations"""
    def decorator(func):
        operation_name = f"collect_{evidence_type}_evidence"
        return trace_lukhas_operation(
            operation_name=operation_name,
            component="evidence_collection",
            operation_type="evidence",
            **trace_kwargs
        )(func)
    return decorator


def trace_performance_check(metric_name: str, **trace_kwargs):
    """Decorator for tracing performance check operations"""
    def decorator(func):
        operation_name = f"check_{metric_name}_performance"
        return trace_lukhas_operation(
            operation_name=operation_name,
            component="performance_regression",
            operation_type="performance",
            **trace_kwargs
        )(func)
    return decorator


# Global tracer instance
_enhanced_tracer: Optional[EnhancedLUKHASTracer] = None


def initialize_enhanced_tracing(
    config: Optional[TraceConfig] = None,
    **config_kwargs
) -> EnhancedLUKHASTracer:
    """Initialize enhanced distributed tracing"""
    global _enhanced_tracer

    if not config:
        # Load from environment or use defaults
        config = TraceConfig(
            jaeger_endpoint=os.getenv("LUKHAS_JAEGER_ENDPOINT"),
            otlp_endpoint=os.getenv("LUKHAS_OTLP_ENDPOINT"),
            sampling_ratio=float(os.getenv("LUKHAS_TRACE_SAMPLING_RATIO", "1.0")),
            **config_kwargs
        )

    _enhanced_tracer = EnhancedLUKHASTracer(config)
    return _enhanced_tracer


def get_enhanced_tracer() -> EnhancedLUKHASTracer:
    """Get or create enhanced tracer instance"""
    global _enhanced_tracer
    if _enhanced_tracer is None:
        _enhanced_tracer = initialize_enhanced_tracing()
    return _enhanced_tracer


def create_correlation_id(correlation_type: str = "request") -> str:
    """Create correlation ID for cross-component tracing"""
    tracer = get_enhanced_tracer()
    return tracer.create_correlation_id(correlation_type)


def propagate_trace_context() -> Dict[str, str]:
    """Get current trace context for HTTP header propagation"""
    tracer = get_enhanced_tracer()
    return tracer.get_current_trace_context()


def extract_trace_context(carrier: Dict[str, str]):
    """Extract and set trace context from HTTP headers"""
    tracer = get_enhanced_tracer()
    return tracer.set_trace_context(carrier)


def add_trace_event(event_name: str, **event_kwargs):
    """Add event to current trace span"""
    tracer = get_enhanced_tracer()
    tracer.add_span_event(event_name, **event_kwargs)


def shutdown_enhanced_tracing():
    """Shutdown enhanced tracing"""
    if OTEL_AVAILABLE:
        try:
            # Flush and shutdown trace provider
            provider = trace.get_tracer_provider()
            if hasattr(provider, 'shutdown'):
                provider.shutdown()
        except Exception as e:
            print(f"Warning: Error during enhanced tracing shutdown: {e}")


# Integration with existing observability components
@contextmanager
def trace_with_evidence_collection(
    operation_name: str,
    evidence_type: str,
    evidence_payload: Dict[str, Any],
    correlation_id: Optional[str] = None,
):
    """
    Context manager that combines tracing with evidence collection.

    Args:
        operation_name: Name of the operation
        evidence_type: Type of evidence to collect
        evidence_payload: Evidence payload
        correlation_id: Optional correlation ID
    """
    tracer = get_enhanced_tracer()

    # Create correlation ID if not provided
    if not correlation_id:
        correlation_id = tracer.create_correlation_id("evidence")

    with tracer.trace_evidence_operation(
        operation_name=operation_name,
        evidence_id=str(uuid4()),
        evidence_type=evidence_type,
        correlation_id=correlation_id,
    ) as span:
        try:
            yield span, correlation_id

            # Add evidence collection event
            tracer.add_span_event(
                "evidence_collected",
                attributes={
                    "evidence_type": evidence_type,
                    "evidence_payload_size": len(str(evidence_payload)),
                    "correlation_id": correlation_id,
                }
            )

        except Exception as e:
            # Record evidence collection failure
            tracer.add_span_event(
                "evidence_collection_failed",
                attributes={
                    "error": str(e),
                    "evidence_type": evidence_type,
                }
            )
            raise
