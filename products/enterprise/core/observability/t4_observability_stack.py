#!/usr/bin/env python3
"""
T4 Enterprise Observability Stack
================================
Enterprise Leadership Level: "Complete visibility into every system component"

Comprehensive observability for LUKHAS AI Trinity Framework
Designed for Jules Agent #4: Enterprise Observability Specialist
"""

import inspect
import json
import logging
import os
import socket
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional


# ΛTAG: optional_dependency_loader
def _load_optional(module_path: str, attribute: Optional[str] = None) -> Optional[Any]:
    """Attempt to import an optional dependency without raising."""

    try:
        module = __import__(module_path, fromlist=[attribute] if attribute else [])
        return getattr(module, attribute) if attribute else module
    except (ImportError, AttributeError):
        return None

# Observability integrations
if TYPE_CHECKING:
    from opentelemetry import metrics as otel_metrics
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    from candidate.consciousness import ConsciousnessCore
    from candidate.memory import MemoryFoldSystem
    from lukhas.guardian import GuardianSystem
    from lukhas.trinity import TrinityFramework


datadog_module = _load_optional("datadog")
DogStatsd = None if datadog_module is None else getattr(datadog_module, "DogStatsd", None)
initialize = None if datadog_module is None else getattr(datadog_module, "initialize", None)
DATADOG_AVAILABLE = DogStatsd is not None and initialize is not None

trace = _load_optional("opentelemetry.trace")
otel_metrics = _load_optional("opentelemetry.metrics")
TracerProvider = _load_optional("opentelemetry.sdk.trace", "TracerProvider")
BatchSpanProcessor = _load_optional("opentelemetry.sdk.trace.export", "BatchSpanProcessor")
OPENTELEMETRY_AVAILABLE = bool(trace and TracerProvider)

prometheus_client = _load_optional("prometheus_client")
PROMETHEUS_AVAILABLE = prometheus_client is not None

ConsciousnessCore = _load_optional("lukhas.consciousness", "ConsciousnessCore") or _load_optional(
    "candidate.consciousness", "ConsciousnessCore"
)
MemoryFoldSystem = _load_optional("lukhas.memory", "MemoryFoldSystem") or _load_optional(
    "candidate.memory", "MemoryFoldSystem"
)
GuardianSystem = _load_optional("lukhas.guardian", "GuardianSystem") or _load_optional(
    "candidate.governance", "GuardianSystem"
)
TrinityFramework = _load_optional("lukhas.trinity", "TrinityFramework")
LUKHAS_AVAILABLE = bool(ConsciousnessCore or MemoryFoldSystem or GuardianSystem or TrinityFramework)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """
    Formats log records as a JSON string for Datadog.
    """

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "dd.service": os.getenv("DATADOG_SERVICE", "lukhas-ai"),
            "dd.env": os.getenv("DATADOG_ENV", "production"),
            "dd.version": os.getenv("DATADOG_VERSION", "1.0.0"),
        }

        # Add trace and span IDs for log correlation (if OpenTelemetry is available)
        try:
            if trace:
                span = trace.get_current_span()
                if span and span.get_span_context().is_valid:
                    log_record["dd.trace_id"] = str(span.get_span_context().trace_id)
                    log_record["dd.span_id"] = str(span.get_span_context().span_id)
        except Exception:
            # If tracing is not available or raises, skip correlation fields
            pass

        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record)


class DatadogLogHandler(logging.Handler):
    """
    A logging handler that sends logs to Datadog via TCP.
    """

    def __init__(self, host="127.0.0.1", port=10514):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except Exception:
            self.socket.close()
            self.socket = None  # Connection failed
            logger.error("Could not connect to Datadog log collection agent.")

    def emit(self, record):
        log_entry = self.format(record)
        if not self.socket:
            return

        try:
            self.socket.sendall((log_entry + "\n").encode("utf-8"))
        except Exception:
            # Try to reconnect
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.sendall((log_entry + "\n").encode("utf-8"))
            except Exception:
                logger.error("Failed to send log to Datadog agent.")

    def close(self):
        if self.socket:
            self.socket.close()
        super().close()


class T4ObservabilityStack:
    """Enterprise-grade observability for LUKHAS AI"""

    def __init__(
        self,
        datadog_enabled: bool = True,
        prometheus_enabled: bool = True,
        opentelemetry_enabled: bool = True,
    ):
        self.datadog_enabled = datadog_enabled and DATADOG_AVAILABLE
        self.prometheus_enabled = prometheus_enabled and PROMETHEUS_AVAILABLE
        self.opentelemetry_enabled = opentelemetry_enabled and OPENTELEMETRY_AVAILABLE

        self.datadog_client = None
        self.tracer = None
        self.meter = None

        self._initialize_observability_stack()

    def _initialize_observability_stack(self):
        """Initialize all observability components"""
        logger.info("🚀 Initializing T4 Enterprise Observability Stack")

        # Initialize Datadog
        if self.datadog_enabled:
            self._initialize_datadog()

        # Initialize Logging
        if self.datadog_enabled:
            self._initialize_logging()

        # Initialize OpenTelemetry
        if self.opentelemetry_enabled:
            self._initialize_opentelemetry()

        # Initialize Prometheus
        if self.prometheus_enabled:
            self._initialize_prometheus()

        logger.info("✅ T4 Observability Stack initialized")

    def _initialize_datadog(self):
        """Initialize Datadog monitoring"""
        try:
            # Initialize Datadog API
            initialize(
                api_key=os.getenv("DATADOG_API_KEY"),
                app_key=os.getenv("DATADOG_APP_KEY"),
                host_name="lukhas-ai-enterprise",
            )

            # Create StatsD client
            self.datadog_client = DogStatsd(host="localhost", port=8125)
            logger.info("✅ Datadog initialized")

        except Exception as e:
            logger.error(f"❌ Datadog initialization failed: {e}")
            self.datadog_enabled = False

    def _initialize_logging(self):
        """Initialize Datadog logging handler."""
        try:
            handler = DatadogLogHandler()
            handler.setFormatter(JSONFormatter())
            logging.getLogger().addHandler(handler)
            logging.getLogger().setLevel(logging.INFO)
            logger.info("✅ Datadog logging handler initialized")
        except Exception as e:
            logger.error(f"❌ Datadog logging initialization failed: {e}")

    def _initialize_opentelemetry(self):
        """Initialize OpenTelemetry tracing and metrics"""
        try:
            # Set up tracing
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)

            # In a real scenario, you would configure an exporter here.
            # Example for Datadog:
            # if self.datadog_enabled:
            #     from opentelemetry.exporter.datadog import DatadogSpanExporter
            #     datadog_exporter = DatadogSpanExporter(agent_url="http://localhost:8126")
            #     span_processor = BatchSpanProcessor(datadog_exporter)
            #     trace.get_tracer_provider().add_span_processor(span_processor)

            self.tracer = tracer
            logger.info("✅ OpenTelemetry initialized")

        except Exception as e:
            logger.error(f"❌ OpenTelemetry initialization failed: {e}")
            self.opentelemetry_enabled = False

    def _initialize_prometheus(self):
        """Initialize Prometheus metrics"""
        # Note: In a real application, you would expose metrics via an endpoint
        # that Prometheus scrapes. This initialization is for a standalone Prometheus
        # client, which is not needed if you are using the Datadog agent to scrape
        # a Prometheus endpoint.
        #
        # Example of exposing a metric with prometheus_client:
        #
        # from prometheus_client import Counter
        # c = Counter('my_failures', 'Description of counter')
        # c.inc()
        #
        # start_http_server(8000) # Expose metrics on port 8000
        logger.info("✅ Prometheus integration ready.")

    def trace(self, name: Optional[str] = None):
        """
        A decorator to trace a function with OpenTelemetry.

        Args:
            name (str, optional): The name of the span. Defaults to the function name.
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                span_name = name or func.__name__
                if not self.opentelemetry_enabled or not self.tracer:
                    return await func(*args, **kwargs)

                with self.tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("function.name", func.__name__)
                    try:
                        result = await func(*args, **kwargs)
                        status_cls = getattr(trace, "Status", None)
                        status_code = getattr(trace, "StatusCode", None)
                        if status_cls and status_code:
                            span.set_status(status_cls(status_code.OK))
                        return result
                    except Exception as e:
                        status_cls = getattr(trace, "Status", None)
                        status_code = getattr(trace, "StatusCode", None)
                        if status_cls and status_code:
                            span.set_status(status_cls(status_code.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            return wrapper

        return decorator

    def submit_metric(self, metric_type: str, metric_name: str, value: float, tags: Optional[list[str]] = None):
        """
        Submit a custom metric to Datadog.

        Args:
            metric_type (str): The type of metric (e.g., 'gauge', 'count', 'histogram').
            metric_name (str): The name of the metric (e.g., 'lukhas.business.revenue').
            value (float): The value of the metric.
            tags (list, optional): A list of tags to associate with the metric.
        """
        if not self.datadog_enabled or not self.datadog_client:
            return

        try:
            metric_func = getattr(self.datadog_client, metric_type)
            metric_func(metric_name, value, tags=tags)
        except AttributeError:
            logger.error(f"Invalid metric type: {metric_type}")
        except Exception as e:
            logger.error(f"Failed to submit metric {metric_name}: {e}")

    def _normalise_metric_value(self, value: Any) -> Optional[float]:
        """Convert arbitrary values into floats suitable for metric emission."""

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return None

    def _submit_bulk_metrics(self, prefix: str, metrics: dict[str, Any], tags: Optional[list[str]] = None):
        """Submit a collection of metrics using a common prefix."""

        for key, raw_value in metrics.items():
            value = self._normalise_metric_value(raw_value)
            if value is None:
                continue
            metric_name = f"lukhas.{prefix}.{key}".replace("..", ".")
            self.submit_metric("gauge", metric_name, value, tags=tags)

    async def _maybe_await(self, candidate: Any) -> Any:
        """Await coroutine values produced by metric providers."""

        if inspect.isawaitable(candidate):
            return await candidate
        return candidate

    async def collect_triad_metrics(self, triad_app: Any) -> dict[str, Any]:
        """Collect coherence and throughput metrics from the Trinity framework."""

        if not triad_app:
            return {}

        metrics: dict[str, Any] = {}

        collector = getattr(triad_app, "get_performance_metrics", None)
        if callable(collector):
            try:
                result = await self._maybe_await(collector())
                if isinstance(result, dict):
                    metrics.update(result)
            except Exception as error:  # pragma: no cover - defensive logging
                logger.warning("Trinity metrics collection failed: %s", error)

        coherence = getattr(triad_app, "coherence", None)
        if coherence is not None:
            metrics.setdefault("coherence", coherence)

        self._submit_bulk_metrics("trinity", metrics)
        return metrics

    async def collect_consciousness_metrics(self, consciousness_core: Any) -> dict[str, Any]:
        """Collect consciousness engine metrics for observability."""

        if not consciousness_core:
            return {}

        metrics: dict[str, Any] = {}

        runtime_state = getattr(consciousness_core, "runtime_state", None)
        if isinstance(runtime_state, dict):
            metrics.update({f"runtime.{k}": v for k, v in runtime_state.items()})

        drift_score = getattr(consciousness_core, "drift_score", None)
        if drift_score is not None:
            metrics["drift_score"] = drift_score

        self._submit_bulk_metrics("consciousness", metrics)
        return metrics

    async def collect_memory_metrics(self, memory_system: Any) -> dict[str, Any]:
        """Collect metrics from the Memory Fold system."""

        if not memory_system:
            return {}

        metrics: dict[str, Any] = {}

        fold_stats = getattr(memory_system, "get_statistics", None)
        if callable(fold_stats):
            try:
                result = await self._maybe_await(fold_stats())
                if isinstance(result, dict):
                    metrics.update(result)
            except Exception as error:  # pragma: no cover - defensive logging
                logger.warning("Memory metrics collection failed: %s", error)

        active_folds = getattr(memory_system, "active_folds", None)
        if active_folds is not None:
            metrics.setdefault("active_folds", active_folds)

        self._submit_bulk_metrics("memory", metrics)
        return metrics

    async def collect_guardian_metrics(self, guardian_system: Any) -> dict[str, Any]:
        """Collect Guardian/ethics metrics if available."""

        if not guardian_system:
            return {}

        metrics: dict[str, Any] = {}

        incident_count = getattr(guardian_system, "open_incidents", None)
        if incident_count is not None:
            metrics["open_incidents"] = incident_count

        affect_delta = getattr(guardian_system, "affect_delta", None)
        if affect_delta is not None:
            metrics["affect_delta"] = affect_delta

        self._submit_bulk_metrics("guardian", metrics)
        return metrics

    async def harvest_component_metrics(
        self,
        *,
        trinity: Any = None,
        consciousness: Any = None,
        memory: Any = None,
        guardian: Any = None,
        output_path: Optional[Path] = None,
    ) -> dict[str, Any]:
        """Collect and optionally persist observability metrics from core systems."""

        metrics: dict[str, Any] = {}

        if trinity:
            metrics["trinity"] = await self.collect_triad_metrics(trinity)
        if consciousness:
            metrics["consciousness"] = await self.collect_consciousness_metrics(consciousness)
        if memory:
            metrics["memory"] = await self.collect_memory_metrics(memory)
        if guardian:
            metrics["guardian"] = await self.collect_guardian_metrics(guardian)

        metrics["timestamp"] = datetime.now(timezone.utc).isoformat()

        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as handle:
                    json.dump(metrics, handle, indent=2)
            except Exception as error:  # pragma: no cover - defensive logging
                logger.warning("Unable to persist observability metrics: %s", error)

        return metrics
