#!/usr/bin/env python3
"""
OpenTelemetry Instrumentation for MATRIZ Stages

Provides comprehensive OTel spans, histograms, and counters for:
- Per-stage execution tracing
- Pipeline performance monitoring
- Error rate tracking
- SLO compliance validation

Usage:
    from observability.otel_instrumentation import instrument_matriz_stage, instrument_cognitive_event

    @instrument_matriz_stage("memory_recall")
    async def recall_memories(query: str):
        # Your stage implementation
        return result

    # For MATRIZ cognitive pipeline events:
    @instrument_cognitive_event("process_matriz_event")
    async def process_matriz_event(event: Dict) -> MatrizResult:
        # MATRIZ processing logic
        return result
"""

import functools
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

# Optional OpenTelemetry imports
try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.metrics import get_meter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global tracer and meter
_tracer = None
_meter = None
_metrics_initialized = False

# Stage-specific metrics
_stage_duration_histogram = None
_stage_counter = None
_pipeline_duration_histogram = None
_error_counter = None

def initialize_otel_instrumentation(
    service_name: str = "lukhas-matriz",
    enable_prometheus: bool = True,
    enable_logging: bool = True
) -> bool:
    """
    Initialize OpenTelemetry instrumentation for MATRIZ.

    Args:
        service_name: Service name for tracing
        enable_prometheus: Enable Prometheus metrics export
        enable_logging: Enable structured logging instrumentation

    Returns:
        True if successfully initialized, False otherwise
    """
    global _tracer, _meter, _metrics_initialized
    global _stage_duration_histogram, _stage_counter, _pipeline_duration_histogram, _error_counter

    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available - instrumentation disabled")
        return False

    try:
        # Initialize tracing
        trace.set_tracer_provider(TracerProvider())
        _tracer = trace.get_tracer(__name__)

        # Initialize metrics
        if enable_prometheus:
            metric_reader = PrometheusMetricReader()
            metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
        else:
            metrics.set_meter_provider(MeterProvider())

        _meter = get_meter(__name__)

        # Create stage-specific metrics
        _stage_duration_histogram = _meter.create_histogram(
            name="lukhas_matriz_stage_duration_seconds",
            description="Duration of MATRIZ stage execution",
            unit="s"
        )

        _stage_counter = _meter.create_counter(
            name="lukhas_matriz_stage_total",
            description="Total MATRIZ stage executions",
            unit="1"
        )

        _pipeline_duration_histogram = _meter.create_histogram(
            name="lukhas_matriz_pipeline_duration_seconds",
            description="Duration of complete MATRIZ pipeline",
            unit="s"
        )

        _error_counter = _meter.create_counter(
            name="lukhas_matriz_errors_total",
            description="Total MATRIZ errors by stage and type",
            unit="1"
        )

        # Initialize logging instrumentation
        if enable_logging:
            LoggingInstrumentor().instrument(set_logging_format=True)

        _metrics_initialized = True
        logger.info(f"OTel instrumentation initialized for {service_name}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize OTel instrumentation: {e}")
        return False


def instrument_matriz_stage(
    stage_name: str,
    stage_type: str = "processing",
    critical: bool = True,
    slo_target_ms: Optional[float] = None
):
    """
    Decorator to instrument MATRIZ stages with OTel spans and metrics.

    Args:
        stage_name: Name of the stage (e.g., "memory_recall", "attention_focus")
        stage_type: Type of stage (memory, attention, reasoning, output)
        critical: Whether stage failure should fail the pipeline
        slo_target_ms: SLO target in milliseconds for alerting

    Usage:
        @instrument_matriz_stage("memory_recall", "memory", slo_target_ms=100.0)
        async def recall_memories(query: str):
            return memories
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await _execute_instrumented_stage(
                func, stage_name, stage_type, critical, slo_target_ms, args, kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            import asyncio
            # Convert sync function to async for consistent instrumentation
            async def _async_func():
                return func(*args, **kwargs)
            return asyncio.run(_execute_instrumented_stage(
                _async_func, stage_name, stage_type, critical, slo_target_ms, (), {}
            ))

        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_ITERABLE_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def _execute_instrumented_stage(
    func: Callable,
    stage_name: str,
    stage_type: str,
    critical: bool,
    slo_target_ms: Optional[float],
    args: tuple,
    kwargs: dict
) -> Any:
    """Execute function with full OTel instrumentation"""

    if not _metrics_initialized or not OTEL_AVAILABLE:
        # Fall back to direct execution without instrumentation
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    lane = os.getenv("LUKHAS_LANE", "experimental")
    start_time = time.perf_counter()

    # Create span for tracing
    with _tracer.start_as_current_span(
        f"matriz.stage.{stage_name}",
        attributes={
            "matriz.stage.name": stage_name,
            "matriz.stage.type": stage_type,
            "matriz.stage.critical": critical,
            "matriz.lane": lane,
            "matriz.slo_target_ms": slo_target_ms or 0.0,
        }
    ) as span:

        try:
            # Execute the function
            if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # async
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Calculate duration
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            # Record success metrics
            _record_stage_success(stage_name, stage_type, lane, duration_s, slo_target_ms)

            # Add span attributes
            span.set_attributes({
                "matriz.stage.duration_ms": duration_ms,
                "matriz.stage.success": True,
                "matriz.stage.within_slo": slo_target_ms is None or duration_ms <= slo_target_ms,
            })

            span.set_status(Status(StatusCode.OK))

            logger.debug(
                f"MATRIZ stage {stage_name} completed successfully in {duration_ms:.2f}ms",
                extra={
                    "matriz_stage": stage_name,
                    "matriz_type": stage_type,
                    "duration_ms": duration_ms,
                    "within_slo": slo_target_ms is None or duration_ms <= slo_target_ms,
                }
            )

            return result

        except Exception as e:
            # Calculate duration for failed execution
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            # Record error metrics
            _record_stage_error(stage_name, stage_type, lane, duration_s, str(type(e).__name__))

            # Add error info to span
            span.set_attributes({
                "matriz.stage.duration_ms": duration_ms,
                "matriz.stage.success": False,
                "matriz.stage.error_type": type(e).__name__,
                "matriz.stage.error_message": str(e),
            })

            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                f"MATRIZ stage {stage_name} failed after {duration_ms:.2f}ms: {e}",
                extra={
                    "matriz_stage": stage_name,
                    "matriz_type": stage_type,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "critical": critical,
                },
                exc_info=True
            )

            raise


@contextmanager
def matriz_pipeline_span(
    pipeline_name: str,
    user_query: str,
    target_slo_ms: float = 250.0
):
    """
    Context manager for instrumenting complete MATRIZ pipelines.

    Args:
        pipeline_name: Name of the pipeline (e.g., "cognitive_processing")
        user_query: User's input query
        target_slo_ms: Target SLO for complete pipeline

    Usage:
        with matriz_pipeline_span("cognitive_processing", user_input):
            # Execute pipeline stages
            result = await process_pipeline(user_input)
    """
    if not _metrics_initialized or not OTEL_AVAILABLE:
        yield
        return

    lane = os.getenv("LUKHAS_LANE", "experimental")
    start_time = time.perf_counter()

    with _tracer.start_as_current_span(
        f"matriz.pipeline.{pipeline_name}",
        attributes={
            "matriz.pipeline.name": pipeline_name,
            "matriz.pipeline.user_query": user_query[:100],  # Truncate for privacy
            "matriz.pipeline.target_slo_ms": target_slo_ms,
            "matriz.lane": lane,
        }
    ) as span:

        try:
            yield span

            # Record successful pipeline completion
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000
            within_slo = duration_ms <= target_slo_ms

            _pipeline_duration_histogram.record(
                duration_s,
                attributes={
                    "pipeline": pipeline_name,
                    "lane": lane,
                    "status": "success",
                    "within_slo": str(within_slo).lower()
                }
            )

            span.set_attributes({
                "matriz.pipeline.duration_ms": duration_ms,
                "matriz.pipeline.success": True,
                "matriz.pipeline.within_slo": within_slo,
            })

            span.set_status(Status(StatusCode.OK))

            logger.info(
                f"MATRIZ pipeline {pipeline_name} completed in {duration_ms:.2f}ms",
                extra={
                    "matriz_pipeline": pipeline_name,
                    "duration_ms": duration_ms,
                    "within_slo": within_slo,
                    "target_slo_ms": target_slo_ms,
                }
            )

        except Exception as e:
            # Record failed pipeline
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            _pipeline_duration_histogram.record(
                duration_s,
                attributes={
                    "pipeline": pipeline_name,
                    "lane": lane,
                    "status": "error",
                    "within_slo": "false"
                }
            )

            _error_counter.add(
                1,
                attributes={
                    "stage": pipeline_name,
                    "stage_type": "pipeline",
                    "error_type": type(e).__name__,
                    "lane": lane
                }
            )

            span.set_attributes({
                "matriz.pipeline.duration_ms": duration_ms,
                "matriz.pipeline.success": False,
                "matriz.pipeline.error_type": type(e).__name__,
                "matriz.pipeline.error_message": str(e),
            })

            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                f"MATRIZ pipeline {pipeline_name} failed after {duration_ms:.2f}ms: {e}",
                extra={
                    "matriz_pipeline": pipeline_name,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True
            )

            raise


def _record_stage_success(
    stage_name: str,
    stage_type: str,
    lane: str,
    duration_s: float,
    slo_target_ms: Optional[float]
):
    """Record successful stage execution metrics"""
    if not _metrics_initialized:
        return

    within_slo = slo_target_ms is None or (duration_s * 1000) <= slo_target_ms

    _stage_duration_histogram.record(
        duration_s,
        attributes={
            "stage": stage_name,
            "stage_type": stage_type,
            "lane": lane,
            "outcome": "success",
            "within_slo": str(within_slo).lower()
        }
    )

    _stage_counter.add(
        1,
        attributes={
            "stage": stage_name,
            "stage_type": stage_type,
            "lane": lane,
            "outcome": "success"
        }
    )


def _record_stage_error(
    stage_name: str,
    stage_type: str,
    lane: str,
    duration_s: float,
    error_type: str
):
    """Record failed stage execution metrics"""
    if not _metrics_initialized:
        return

    _stage_duration_histogram.record(
        duration_s,
        attributes={
            "stage": stage_name,
            "stage_type": stage_type,
            "lane": lane,
            "outcome": "error",
            "within_slo": "false"
        }
    )

    _stage_counter.add(
        1,
        attributes={
            "stage": stage_name,
            "stage_type": stage_type,
            "lane": lane,
            "outcome": "error"
        }
    )

    _error_counter.add(
        1,
        attributes={
            "stage": stage_name,
            "stage_type": stage_type,
            "error_type": error_type,
            "lane": lane
        }
    )


@contextmanager
def stage_span(stage: str, attrs: Optional[dict[str, Any]] = None):
    """
    Simple stage span helper for basic tracing.

    Args:
        stage: Stage name (e.g., "intent", "decision")
        attrs: Optional attributes dict

    Usage:
        with stage_span("INTENT", {"lane": lane, "node_count": len(nodes)}):
            # intent work...
    """
    if not OTEL_AVAILABLE or not _tracer:
        yield
        return

    with _tracer.start_as_current_span(f"matriz.{stage.lower()}") as sp:
        if attrs:
            for k, v in attrs.items():
                try:  # TODO[T4-ISSUE]: {"code":"SIM105","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"try-except-pass pattern - consider contextlib.suppress for clarity","estimate":"10m","priority":"low","dependencies":"contextlib","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_observability_otel_instrumentation_py_L498"}
                    sp.set_attribute(f"matriz.{k}", v)
                except Exception:
                    # Ignore attribute setting errors
                    pass
        yield sp


def get_instrumentation_status() -> dict[str, Any]:
    """Get current instrumentation status and configuration"""
    return {
        "otel_available": OTEL_AVAILABLE,
        "metrics_initialized": _metrics_initialized,
        "tracer_active": _tracer is not None,
        "meter_active": _meter is not None,
        "service_name": "lukhas-matriz",
        "metrics": {
            "stage_duration_histogram": _stage_duration_histogram is not None,
            "stage_counter": _stage_counter is not None,
            "pipeline_duration_histogram": _pipeline_duration_histogram is not None,
            "error_counter": _error_counter is not None,
        }
    }


def instrument_cognitive_event(
    event_name: str,
    cognitive_stage: Optional[str] = None,
    node_id_extractor: Optional[Callable[[Dict], str]] = None,
    slo_target_ms: float = 250.0
):
    """
    Decorator to instrument MATRIZ cognitive pipeline events like process_matriz_event.

    This decorator provides comprehensive observability for cognitive events with:
    - Automatic stage detection from event data
    - Node ID extraction and tracking
    - Processing time metrics per cognitive stage
    - Anomaly detection for cognitive patterns
    - Full span tracing with cognitive context

    Args:
        event_name: Name of the cognitive event (e.g., "process_matriz_event")
        cognitive_stage: Override cognitive stage detection
        node_id_extractor: Function to extract node ID from event data
        slo_target_ms: SLO target for the cognitive event processing

    Usage:
        @instrument_cognitive_event("process_matriz_event", slo_target_ms=100.0)
        def process_matriz_event(event: Dict) -> MatrizResult:
            # Extract cognitive stage from event
            stage = event.get('node_type', 'unknown').lower()
            node_id = event.get('id', 'unknown')

            # Your MATRIZ processing logic here
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await _execute_cognitive_event_instrumented(
                func, event_name, cognitive_stage, node_id_extractor, slo_target_ms, args, kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            import asyncio
            # Convert sync function to async for consistent instrumentation
            async def _async_func():
                return func(*args, **kwargs)
            return asyncio.run(_execute_cognitive_event_instrumented(
                _async_func, event_name, cognitive_stage, node_id_extractor, slo_target_ms, (), {}
            ))

        # Return appropriate wrapper
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def _execute_cognitive_event_instrumented(
    func: Callable,
    event_name: str,
    cognitive_stage: Optional[str],
    node_id_extractor: Optional[Callable[[Dict], str]],
    slo_target_ms: float,
    args: tuple,
    kwargs: dict
) -> Any:
    """Execute cognitive event function with comprehensive instrumentation"""

    if not _metrics_initialized or not OTEL_AVAILABLE:
        # Fall back to direct execution without instrumentation
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    start_time = time.perf_counter()

    # Extract event data for context (assume first argument is event dict)
    event_data = args[0] if args and isinstance(args[0], dict) else {}

    # Determine cognitive stage and node ID
    detected_stage = cognitive_stage or event_data.get('node_type', 'unknown').lower()
    if node_id_extractor:
        node_id = node_id_extractor(event_data)
    else:
        node_id = event_data.get('id', event_data.get('node_id', f"node_{int(time.time() * 1000)}"))

    lane = os.getenv("LUKHAS_LANE", "experimental")

    # Create comprehensive span for cognitive event
    with _tracer.start_as_current_span(
        f"matriz.cognitive_event.{event_name}",
        attributes={
            "matriz.event.name": event_name,
            "matriz.event.cognitive_stage": detected_stage,
            "matriz.event.node_id": node_id,
            "matriz.event.slo_target_ms": slo_target_ms,
            "matriz.lane": lane,
            "matriz.event.data_keys": ",".join(event_data.keys()) if event_data else "",
        }
    ) as span:

        try:
            # Execute the function
            if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Calculate duration
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000
            within_slo = duration_ms <= slo_target_ms

            # Record cognitive event metrics
            _record_cognitive_event_success(
                event_name, detected_stage, node_id, lane, duration_s, slo_target_ms
            )

            # Update span attributes
            span.set_attributes({
                "matriz.event.duration_ms": duration_ms,
                "matriz.event.success": True,
                "matriz.event.within_slo": within_slo,
                "matriz.event.result_type": type(result).__name__,
            })

            # Add cognitive-specific attributes if result has cognitive data
            if hasattr(result, '__dict__') or isinstance(result, dict):
                result_dict = result.__dict__ if hasattr(result, '__dict__') else result
                if isinstance(result_dict, dict):
                    if 'confidence' in result_dict:
                        span.set_attribute("matriz.cognitive.confidence", result_dict['confidence'])
                    if 'reasoning_depth' in result_dict:
                        span.set_attribute("matriz.cognitive.reasoning_depth", result_dict['reasoning_depth'])

            span.set_status(Status(StatusCode.OK))

            logger.debug(
                f"Cognitive event {event_name} completed successfully",
                extra={
                    "cognitive_event": event_name,
                    "cognitive_stage": detected_stage,
                    "node_id": node_id,
                    "duration_ms": duration_ms,
                    "within_slo": within_slo,
                    "lane": lane,
                }
            )

            return result

        except Exception as e:
            # Calculate duration for failed execution
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            # Record error metrics
            _record_cognitive_event_error(
                event_name, detected_stage, node_id, lane, duration_s, str(type(e).__name__)
            )

            # Add error info to span
            span.set_attributes({
                "matriz.event.duration_ms": duration_ms,
                "matriz.event.success": False,
                "matriz.event.error_type": type(e).__name__,
                "matriz.event.error_message": str(e)[:500],  # Truncate for span limits
            })

            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                f"Cognitive event {event_name} failed after {duration_ms:.2f}ms: {e}",
                extra={
                    "cognitive_event": event_name,
                    "cognitive_stage": detected_stage,
                    "node_id": node_id,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "lane": lane,
                },
                exc_info=True
            )

            raise


def _record_cognitive_event_success(
    event_name: str,
    stage: str,
    node_id: str,
    lane: str,
    duration_s: float,
    slo_target_ms: float
):
    """Record successful cognitive event execution metrics"""
    if not _metrics_initialized:
        return

    within_slo = (duration_s * 1000) <= slo_target_ms

    _stage_duration_histogram.record(
        duration_s,
        attributes={
            "event_name": event_name,
            "cognitive_stage": stage,
            "node_id": node_id,
            "lane": lane,
            "outcome": "success",
            "within_slo": str(within_slo).lower()
        }
    )

    _stage_counter.add(
        1,
        attributes={
            "event_name": event_name,
            "cognitive_stage": stage,
            "node_id": node_id,
            "lane": lane,
            "outcome": "success"
        }
    )


def _record_cognitive_event_error(
    event_name: str,
    stage: str,
    node_id: str,
    lane: str,
    duration_s: float,
    error_type: str
):
    """Record failed cognitive event execution metrics"""
    if not _metrics_initialized:
        return

    _stage_duration_histogram.record(
        duration_s,
        attributes={
            "event_name": event_name,
            "cognitive_stage": stage,
            "node_id": node_id,
            "lane": lane,
            "outcome": "error",
            "within_slo": "false"
        }
    )

    _stage_counter.add(
        1,
        attributes={
            "event_name": event_name,
            "cognitive_stage": stage,
            "node_id": node_id,
            "lane": lane,
            "outcome": "error"
        }
    )

    _error_counter.add(
        1,
        attributes={
            "event_name": event_name,
            "cognitive_stage": stage,
            "error_type": error_type,
            "node_id": node_id,
            "lane": lane
        }
    )


# Auto-initialize if running in production environment
if os.getenv("LUKHAS_LANE") in ["production", "candidate"] and OTEL_AVAILABLE:
    initialize_otel_instrumentation()
