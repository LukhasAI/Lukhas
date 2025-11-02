#!/usr/bin/env python3
"""
MATRIZ Cognitive Pipeline Observability Instrumentation

Comprehensive observability for MATRIZ Memory→Attention→Thought→Action→Decision→Awareness pipeline.
Enables detection of 1-in-10,000 cognitive anomalies through detailed metrics, tracing, and alerting.

Key Features:
- Stage-specific instrumentation for each cognitive phase
- Node-level tracking with processing time metrics
- Focus drift and attention weight monitoring
- Memory cascade risk assessment
- Thought complexity scoring
- Decision confidence tracking
- Anomaly detection for rare cognitive patterns

Usage:
    from observability.matriz_instrumentation import instrument_cognitive_stage, cognitive_pipeline_span

    @instrument_cognitive_stage("memory", node_id="memory_node_1")
    async def memory_recall_process(query):
        # Memory processing logic
        return recalled_memories

    with cognitive_pipeline_span("full_cognition", user_query):
        # Execute complete MATRIZ pipeline
        result = await process_cognitive_pipeline(user_query)
"""

import functools
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# Import existing OTel infrastructure
from observability.otel_instrumentation import OTEL_AVAILABLE, _metrics_initialized, _tracer

if OTEL_AVAILABLE:
    from opentelemetry.metrics import get_meter
    from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)


# Cognitive stage definitions matching MATRIZ pipeline
class CognitiveStage(Enum):
    """MATRIZ cognitive pipeline stages"""

    MEMORY = "memory"
    ATTENTION = "attention"
    THOUGHT = "thought"
    ACTION = "action"
    DECISION = "decision"
    AWARENESS = "awareness"


# Cognitive-specific metrics
_cognitive_metrics = {}
_cognitive_initialized = False


@dataclass
class CognitiveMetrics:
    """Container for cognitive-specific metrics"""

    stage_duration_histogram: Any = None
    stage_events_counter: Any = None
    focus_drift_gauge: Any = None
    memory_cascade_risk_gauge: Any = None
    thought_complexity_gauge: Any = None
    decision_confidence_gauge: Any = None
    attention_weight_histogram: Any = None
    reasoning_depth_histogram: Any = None
    cognitive_load_gauge: Any = None
    anomaly_detection_counter: Any = None


def initialize_cognitive_instrumentation(enable_metrics: bool = True) -> bool:
    """
    Initialize cognitive-specific metrics and instrumentation.

    Args:
        enable_metrics: Enable cognitive metrics collection

    Returns:
        True if successfully initialized, False otherwise
    """
    global _cognitive_metrics, _cognitive_initialized

    if not OTEL_AVAILABLE or not _metrics_initialized:
        logger.warning("Base OTel instrumentation not available - cognitive instrumentation disabled")
        return False

    try:
        meter = get_meter("matriz.cognitive")

        # Initialize cognitive-specific metrics
        _cognitive_metrics = CognitiveMetrics(
            # Stage execution metrics
            stage_duration_histogram=meter.create_histogram(
                name="matriz_cognitive_stage_duration_seconds",
                description="Duration of MATRIZ cognitive stage execution",
                unit="s",
            ),
            stage_events_counter=meter.create_counter(
                name="matriz_cognitive_stage_events_total",
                description="Total cognitive stage events by outcome",
                unit="1",
            ),
            # Attention and focus metrics
            focus_drift_gauge=meter.create_up_down_counter(
                name="matriz_focus_drift_score",
                description="Attention focus drift score (higher = more drift)",
                unit="1",
            ),
            attention_weight_histogram=meter.create_histogram(
                name="matriz_attention_weight_distribution",
                description="Distribution of attention weights across nodes",
                unit="1",
            ),
            # Memory system metrics
            memory_cascade_risk_gauge=meter.create_up_down_counter(
                name="matriz_memory_cascade_risk",
                description="Memory cascade risk score (0-1, higher = more risk)",
                unit="1",
            ),
            # Thought processing metrics
            thought_complexity_gauge=meter.create_up_down_counter(
                name="matriz_thought_complexity_score",
                description="Complexity score for thought processing (reasoning depth, logic chains)",
                unit="1",
            ),
            reasoning_depth_histogram=meter.create_histogram(
                name="matriz_reasoning_depth_levels",
                description="Distribution of reasoning depth in thought processing",
                unit="1",
            ),
            # Decision making metrics
            decision_confidence_gauge=meter.create_up_down_counter(
                name="matriz_decision_confidence_score",
                description="Confidence score for decision making (0-1)",
                unit="1",
            ),
            # Overall cognitive load
            cognitive_load_gauge=meter.create_up_down_counter(
                name="matriz_cognitive_load", description="Overall cognitive load across pipeline stages", unit="1"
            ),
            # Anomaly detection
            anomaly_detection_counter=meter.create_counter(
                name="matriz_cognitive_anomalies_total",
                description="Detected cognitive anomalies by type and stage",
                unit="1",
            ),
        )

        _cognitive_initialized = True
        logger.info("Cognitive instrumentation initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize cognitive instrumentation: {e}")
        return False


def instrument_cognitive_stage(
    stage: Union[str, CognitiveStage],
    node_id: Optional[str] = None,
    intent_type: Optional[str] = None,
    slo_target_ms: Optional[float] = None,
    anomaly_detection: bool = True,
):
    """
    Decorator to instrument MATRIZ cognitive stages with comprehensive observability.

    Args:
        stage: Cognitive stage name (memory, attention, thought, action, decision, awareness)
        node_id: Unique identifier for the processing node
        intent_type: Type of intent being processed (mathematical, question, general, etc.)
        slo_target_ms: SLO target in milliseconds for latency alerting
        anomaly_detection: Enable anomaly detection for this stage

    Usage:
        @instrument_cognitive_stage("memory", node_id="mem_fold_1", slo_target_ms=50.0)
        async def process_memory_recall(query: str):
            return recalled_memories
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await _execute_instrumented_cognitive_stage(
                func, stage, node_id, intent_type, slo_target_ms, anomaly_detection, args, kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            import asyncio

            # Convert sync to async for consistent instrumentation
            async def _async_func():
                return func(*args, **kwargs)

            return asyncio.run(
                _execute_instrumented_cognitive_stage(
                    _async_func, stage, node_id, intent_type, slo_target_ms, anomaly_detection, (), {}
                )
            )

        # Return appropriate wrapper based on function type
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def _execute_instrumented_cognitive_stage(
    func: Callable,
    stage: Union[str, CognitiveStage],
    node_id: Optional[str],
    intent_type: Optional[str],
    slo_target_ms: Optional[float],
    anomaly_detection: bool,
    args: tuple,
    kwargs: dict,
) -> Any:
    """Execute cognitive stage function with full instrumentation"""

    if not _cognitive_initialized or not OTEL_AVAILABLE:
        # Fall back to direct execution without instrumentation
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    # Normalize stage name
    stage_name = stage.value if isinstance(stage, CognitiveStage) else str(stage)
    node_id = node_id or f"node_{int(time.time() * 1000)}"

    start_time = time.perf_counter()

    # Create comprehensive span for cognitive stage
    span_name = f"matriz.cognitive.{stage_name}"
    with _tracer.start_as_current_span(
        span_name,
        attributes={
            "matriz.cognitive.stage": stage_name,
            "matriz.cognitive.node_id": node_id,
            "matriz.cognitive.intent_type": intent_type or "unknown",
            "matriz.cognitive.slo_target_ms": slo_target_ms or 0.0,
            "matriz.cognitive.anomaly_detection": anomaly_detection,
            "matriz.cognitive.function": func.__name__,
        },
    ) as span:

        try:
            # Execute the function
            if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Calculate metrics
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            # Record success metrics
            _record_cognitive_success(
                stage_name, node_id, intent_type, duration_s, duration_ms, slo_target_ms, result, anomaly_detection
            )

            # Update span with success info
            span.set_attributes(
                {
                    "matriz.cognitive.duration_ms": duration_ms,
                    "matriz.cognitive.success": True,
                    "matriz.cognitive.within_slo": slo_target_ms is None or duration_ms <= slo_target_ms,
                    "matriz.cognitive.result_type": type(result).__name__,
                }
            )

            span.set_status(Status(StatusCode.OK))

            logger.debug(
                f"Cognitive stage {stage_name} completed successfully",
                extra={
                    "cognitive_stage": stage_name,
                    "node_id": node_id,
                    "duration_ms": duration_ms,
                    "within_slo": slo_target_ms is None or duration_ms <= slo_target_ms,
                    "intent_type": intent_type,
                },
            )

            return result

        except Exception as e:
            # Handle failure case
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            # Record error metrics
            _record_cognitive_error(stage_name, node_id, intent_type, duration_s, str(type(e).__name__))

            # Update span with error info
            span.set_attributes(
                {
                    "matriz.cognitive.duration_ms": duration_ms,
                    "matriz.cognitive.success": False,
                    "matriz.cognitive.error_type": type(e).__name__,
                    "matriz.cognitive.error_message": str(e)[:500],  # Truncate for span limits
                }
            )

            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                f"Cognitive stage {stage_name} failed",
                extra={
                    "cognitive_stage": stage_name,
                    "node_id": node_id,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                    "intent_type": intent_type,
                },
                exc_info=True,
            )

            raise


@contextmanager
def cognitive_pipeline_span(
    pipeline_name: str, user_query: str, expected_stages: Optional[List[str]] = None, target_slo_ms: float = 250.0
):
    """
    Context manager for instrumenting complete MATRIZ cognitive pipelines.

    Args:
        pipeline_name: Name of the cognitive pipeline (e.g., "full_cognition", "memory_only")
        user_query: User's input query for context
        expected_stages: List of expected cognitive stages
        target_slo_ms: Target SLO for complete pipeline

    Usage:
        with cognitive_pipeline_span("full_cognition", user_input,
                                   expected_stages=["memory", "attention", "thought", "decision"]):
            result = await process_cognitive_pipeline(user_input)
    """
    if not _cognitive_initialized or not OTEL_AVAILABLE:
        yield
        return

    start_time = time.perf_counter()
    pipeline_id = f"pipeline_{int(time.time() * 1000)}"

    with _tracer.start_as_current_span(
        f"matriz.cognitive.pipeline.{pipeline_name}",
        attributes={
            "matriz.cognitive.pipeline.name": pipeline_name,
            "matriz.cognitive.pipeline.id": pipeline_id,
            "matriz.cognitive.pipeline.user_query": user_query[:100],  # Truncate for privacy
            "matriz.cognitive.pipeline.expected_stages": ",".join(expected_stages or []),
            "matriz.cognitive.pipeline.target_slo_ms": target_slo_ms,
        },
    ) as span:

        try:
            yield span

            # Record successful pipeline completion
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000
            within_slo = duration_ms <= target_slo_ms

            # Update cognitive load based on pipeline complexity
            if _cognitive_metrics.cognitive_load_gauge:
                complexity_score = _calculate_pipeline_complexity(expected_stages, duration_ms)
                _cognitive_metrics.cognitive_load_gauge.add(
                    complexity_score,
                    attributes={
                        "pipeline": pipeline_name,
                        "query_type": _classify_query_type(user_query),
                        "within_slo": str(within_slo).lower(),
                    },
                )

            span.set_attributes(
                {
                    "matriz.cognitive.pipeline.duration_ms": duration_ms,
                    "matriz.cognitive.pipeline.success": True,
                    "matriz.cognitive.pipeline.within_slo": within_slo,
                    "matriz.cognitive.pipeline.complexity_score": _calculate_pipeline_complexity(
                        expected_stages, duration_ms
                    ),
                }
            )

            span.set_status(Status(StatusCode.OK))

            logger.info(
                f"Cognitive pipeline {pipeline_name} completed",
                extra={
                    "pipeline_name": pipeline_name,
                    "pipeline_id": pipeline_id,
                    "duration_ms": duration_ms,
                    "within_slo": within_slo,
                    "target_slo_ms": target_slo_ms,
                },
            )

        except Exception as e:
            # Record failed pipeline
            duration_s = time.perf_counter() - start_time
            duration_ms = duration_s * 1000

            span.set_attributes(
                {
                    "matriz.cognitive.pipeline.duration_ms": duration_ms,
                    "matriz.cognitive.pipeline.success": False,
                    "matriz.cognitive.pipeline.error_type": type(e).__name__,
                    "matriz.cognitive.pipeline.error_message": str(e)[:500],
                }
            )

            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                f"Cognitive pipeline {pipeline_name} failed",
                extra={
                    "pipeline_name": pipeline_name,
                    "pipeline_id": pipeline_id,
                    "duration_ms": duration_ms,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )

            raise


def record_focus_drift(node_id: str, attention_weights: List[float], window_size: int = 10):
    """
    Record focus drift metrics for attention monitoring.

    Args:
        node_id: Node processing the attention
        attention_weights: List of attention weight values
        window_size: Size of the sliding window for drift calculation
    """
    if not _cognitive_initialized or not _cognitive_metrics.focus_drift_gauge:
        return

    if len(attention_weights) < 2:
        return

    # Calculate focus drift as variance in attention weights
    mean_weight = sum(attention_weights) / len(attention_weights)
    variance = sum((w - mean_weight) ** 2 for w in attention_weights) / len(attention_weights)
    drift_score = variance**0.5  # Standard deviation as drift score

    _cognitive_metrics.focus_drift_gauge.add(
        int(drift_score * 1000),  # Scale for better granularity
        attributes={
            "node_id": node_id,
            "window_size": window_size,
            "attention_range": _classify_attention_range(min(attention_weights), max(attention_weights)),
        },
    )

    # Check for anomaly (drift > 2 standard deviations from normal)
    if drift_score > 0.5:  # Configurable threshold
        _record_cognitive_anomaly("focus_drift", node_id, {"drift_score": drift_score})


def record_memory_cascade_risk(fold_count: int, retrieval_depth: int, cascade_detected: bool = False):
    """
    Record memory cascade risk metrics.

    Args:
        fold_count: Current number of active memory folds
        retrieval_depth: Depth of memory retrieval
        cascade_detected: Whether a cascade was detected
    """
    if not _cognitive_initialized or not _cognitive_metrics.memory_cascade_risk_gauge:
        return

    # Calculate risk score based on fold count and retrieval depth
    max_folds = 1000  # From MATRIZ specifications
    risk_score = (fold_count / max_folds) + (retrieval_depth / 50.0)  # Normalize depth
    risk_score = min(1.0, risk_score)  # Cap at 1.0

    _cognitive_metrics.memory_cascade_risk_gauge.add(
        int(risk_score * 100),  # Scale to 0-100
        attributes={
            "fold_count_range": _classify_fold_count_range(fold_count),
            "retrieval_depth_range": _classify_retrieval_depth_range(retrieval_depth),
            "cascade_detected": str(cascade_detected).lower(),
        },
    )

    # Check for anomaly (approaching cascade conditions)
    if fold_count > 900 or cascade_detected:  # 90% of limit or detected cascade
        _record_cognitive_anomaly(
            "memory_cascade_risk",
            "fold_system",
            {"fold_count": fold_count, "risk_score": risk_score, "cascade_detected": cascade_detected},
        )


def record_thought_complexity(reasoning_depth: int, logic_chains: int, inference_steps: int):
    """
    Record thought complexity metrics for thought processing analysis.

    Args:
        reasoning_depth: Depth of reasoning layers
        logic_chains: Number of logical chains
        inference_steps: Number of inference steps taken
    """
    if not _cognitive_initialized:
        return

    # Calculate complexity score
    complexity_score = (reasoning_depth * 2) + logic_chains + (inference_steps / 10)

    if _cognitive_metrics.thought_complexity_gauge:
        _cognitive_metrics.thought_complexity_gauge.add(
            int(complexity_score),
            attributes={
                "reasoning_depth_range": _classify_reasoning_depth_range(reasoning_depth),
                "logic_chains_range": _classify_logic_chains_range(logic_chains),
                "inference_complexity": _classify_inference_complexity(inference_steps),
            },
        )

    if _cognitive_metrics.reasoning_depth_histogram:
        _cognitive_metrics.reasoning_depth_histogram.record(
            reasoning_depth, attributes={"thought_type": "logical_reasoning"}
        )

    # Check for anomaly (extremely high complexity)
    if complexity_score > 100:  # Configurable threshold
        _record_cognitive_anomaly(
            "thought_complexity",
            "thought_processor",
            {
                "complexity_score": complexity_score,
                "reasoning_depth": reasoning_depth,
                "logic_chains": logic_chains,
                "inference_steps": inference_steps,
            },
        )


def record_decision_confidence(confidence_score: float, decision_type: str, node_id: str):
    """
    Record decision confidence metrics.

    Args:
        confidence_score: Confidence score for the decision (0-1)
        decision_type: Type of decision made
        node_id: Node that made the decision
    """
    if not _cognitive_initialized or not _cognitive_metrics.decision_confidence_gauge:
        return

    _cognitive_metrics.decision_confidence_gauge.add(
        int(confidence_score * 100),  # Scale to 0-100
        attributes={
            "decision_type": decision_type,
            "node_id": node_id,
            "confidence_range": _classify_confidence_range(confidence_score),
        },
    )

    # Check for anomaly (very low confidence with high frequency)
    if confidence_score < 0.3:  # Low confidence threshold
        _record_cognitive_anomaly(
            "low_decision_confidence", node_id, {"confidence_score": confidence_score, "decision_type": decision_type}
        )


def _record_cognitive_success(
    stage_name: str,
    node_id: str,
    intent_type: Optional[str],
    duration_s: float,
    duration_ms: float,
    slo_target_ms: Optional[float],
    result: Any,
    anomaly_detection: bool,
):
    """Record successful cognitive stage execution metrics"""
    if not _cognitive_initialized:
        return

    within_slo = slo_target_ms is None or duration_ms <= slo_target_ms

    # Record stage duration
    if _cognitive_metrics.stage_duration_histogram:
        _cognitive_metrics.stage_duration_histogram.record(
            duration_s,
            attributes={
                "stage": stage_name,
                "node_id": node_id,
                "intent_type": intent_type or "unknown",
                "outcome": "success",
                "within_slo": str(within_slo).lower(),
            },
        )

    # Record stage events
    if _cognitive_metrics.stage_events_counter:
        _cognitive_metrics.stage_events_counter.add(
            1,
            attributes={
                "stage": stage_name,
                "node_id": node_id,
                "intent_type": intent_type or "unknown",
                "outcome": "success",
            },
        )

    # Anomaly detection for performance outliers
    if anomaly_detection and slo_target_ms and duration_ms > (slo_target_ms * 2):
        _record_cognitive_anomaly(
            "performance_outlier",
            node_id,
            {
                "stage": stage_name,
                "duration_ms": duration_ms,
                "slo_target_ms": slo_target_ms,
                "outlier_ratio": duration_ms / slo_target_ms,
            },
        )


def _record_cognitive_error(
    stage_name: str, node_id: str, intent_type: Optional[str], duration_s: float, error_type: str
):
    """Record failed cognitive stage execution metrics"""
    if not _cognitive_initialized:
        return

    # Record stage duration even for errors
    if _cognitive_metrics.stage_duration_histogram:
        _cognitive_metrics.stage_duration_histogram.record(
            duration_s,
            attributes={
                "stage": stage_name,
                "node_id": node_id,
                "intent_type": intent_type or "unknown",
                "outcome": "error",
                "within_slo": "false",
            },
        )

    # Record stage events
    if _cognitive_metrics.stage_events_counter:
        _cognitive_metrics.stage_events_counter.add(
            1,
            attributes={
                "stage": stage_name,
                "node_id": node_id,
                "intent_type": intent_type or "unknown",
                "outcome": "error",
            },
        )

    # Always record errors as anomalies
    _record_cognitive_anomaly(
        "stage_error", node_id, {"stage": stage_name, "error_type": error_type, "intent_type": intent_type}
    )


def _record_cognitive_anomaly(anomaly_type: str, node_id: str, context: Dict[str, Any]):
    """Record detected cognitive anomalies"""
    if not _cognitive_initialized or not _cognitive_metrics.anomaly_detection_counter:
        return

    _cognitive_metrics.anomaly_detection_counter.add(
        1,
        attributes={
            "anomaly_type": anomaly_type,
            "node_id": node_id,
            "severity": _classify_anomaly_severity(anomaly_type, context),
        },
    )

    logger.warning(
        f"Cognitive anomaly detected: {anomaly_type}",
        extra={"anomaly_type": anomaly_type, "node_id": node_id, "context": context},
    )


# Classification helper functions
def _classify_query_type(user_query: str) -> str:
    """Classify user query type for metrics"""
    query_lower = user_query.lower()
    if any(op in query_lower for op in ["+", "-", "*", "/", "=", "calculate", "math"]):
        return "mathematical"
    elif "?" in query_lower:
        return "question"
    elif any(word in query_lower for word in ["remember", "recall", "memory"]):
        return "memory"
    else:
        return "general"


def _calculate_pipeline_complexity(expected_stages: Optional[List[str]], duration_ms: float) -> float:
    """Calculate pipeline complexity score"""
    base_complexity = len(expected_stages) if expected_stages else 1
    time_factor = min(duration_ms / 100, 10)  # Cap time factor at 10
    return base_complexity * (1 + time_factor / 10)


def _classify_attention_range(min_weight: float, max_weight: float) -> str:
    """Classify attention weight range"""
    range_span = max_weight - min_weight
    if range_span < 0.1:
        return "narrow"
    elif range_span < 0.5:
        return "medium"
    else:
        return "wide"


def _classify_fold_count_range(fold_count: int) -> str:
    """Classify fold count range"""
    if fold_count < 100:
        return "low"
    elif fold_count < 500:
        return "medium"
    elif fold_count < 800:
        return "high"
    else:
        return "critical"


def _classify_retrieval_depth_range(depth: int) -> str:
    """Classify retrieval depth range"""
    if depth < 5:
        return "shallow"
    elif depth < 20:
        return "medium"
    else:
        return "deep"


def _classify_reasoning_depth_range(depth: int) -> str:
    """Classify reasoning depth range"""
    if depth < 3:
        return "simple"
    elif depth < 10:
        return "moderate"
    else:
        return "complex"


def _classify_logic_chains_range(chains: int) -> str:
    """Classify logic chains range"""
    if chains < 2:
        return "linear"
    elif chains < 5:
        return "branched"
    else:
        return "complex"


def _classify_inference_complexity(steps: int) -> str:
    """Classify inference complexity"""
    if steps < 10:
        return "simple"
    elif steps < 50:
        return "moderate"
    else:
        return "complex"


def _classify_confidence_range(confidence: float) -> str:
    """Classify confidence score range"""
    if confidence < 0.3:
        return "low"
    elif confidence < 0.7:
        return "medium"
    else:
        return "high"


def _classify_anomaly_severity(anomaly_type: str, context: Dict[str, Any]) -> str:
    """Classify anomaly severity for alerting"""
    critical_types = ["memory_cascade_risk", "stage_error"]
    warning_types = ["performance_outlier", "low_decision_confidence"]

    if anomaly_type in critical_types:
        return "critical"
    elif anomaly_type in warning_types:
        return "warning"
    else:
        return "info"


def get_cognitive_instrumentation_status() -> Dict[str, Any]:
    """Get current cognitive instrumentation status and configuration"""
    return {
        "cognitive_initialized": _cognitive_initialized,
        "base_otel_available": OTEL_AVAILABLE,
        "base_metrics_initialized": _metrics_initialized,
        "cognitive_metrics": {
            "stage_duration_histogram": (
                _cognitive_metrics.stage_duration_histogram is not None if _cognitive_metrics else False
            ),
            "stage_events_counter": (
                _cognitive_metrics.stage_events_counter is not None if _cognitive_metrics else False
            ),
            "focus_drift_gauge": _cognitive_metrics.focus_drift_gauge is not None if _cognitive_metrics else False,
            "memory_cascade_risk_gauge": (
                _cognitive_metrics.memory_cascade_risk_gauge is not None if _cognitive_metrics else False
            ),
            "thought_complexity_gauge": (
                _cognitive_metrics.thought_complexity_gauge is not None if _cognitive_metrics else False
            ),
            "decision_confidence_gauge": (
                _cognitive_metrics.decision_confidence_gauge is not None if _cognitive_metrics else False
            ),
            "anomaly_detection_counter": (
                _cognitive_metrics.anomaly_detection_counter is not None if _cognitive_metrics else False
            ),
        },
    }


# Auto-initialize if base instrumentation is available
if OTEL_AVAILABLE and _metrics_initialized:
    initialize_cognitive_instrumentation()
