#!/usr/bin/env python3
"""
T4 Enterprise Observability Stack
================================
Enterprise Leadership Level: "Complete visibility into every system component"

Comprehensive observability for LUKHAS AI Trinity Framework
Designed for Jules Agent #4: Enterprise Observability Specialist
"""

import json
import logging
import os
import socket
from functools import wraps
from typing import Any, Dict, Optional

# Observability integrations
try:
    from datadog import DogStatsd, initialize

    DATADOG_AVAILABLE = True
except ImportError:
    DATADOG_AVAILABLE = False

try:
    from opentelemetry import metrics, trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

try:
    import prometheus_client
    from prometheus_client import CollectorRegistry, Gauge

    PROMETHEUS_AVAILABLE = True
except ImportError:
    CollectorRegistry = None  # type: ignore[assignment]
    Gauge = None  # type: ignore[assignment]
    PROMETHEUS_AVAILABLE = False

# LUKHAS integrations
try:
    from lukhas.consciousness import ConsciousnessCore
    from lukhas.consciousness.trinity_integration import TrinityFramework, TrinityFrameworkIntegrator
    from lukhas.governance import GuardianSystem
    from lukhas.memory import MemoryFoldSystem

    LUKHAS_AVAILABLE = True
except ImportError:
    try:
        from candidate.consciousness import ConsciousnessCore
        from candidate.consciousness.trinity.framework_integration import (  # type: ignore
            TrinityFrameworkIntegration as TrinityFramework,
        )
        from candidate.governance import GuardianSystem
        from candidate.memory import MemoryFoldSystem

        LUKHAS_AVAILABLE = True
    except ImportError:
        LUKHAS_AVAILABLE = False
        ConsciousnessCore = None  # type: ignore[assignment]
        GuardianSystem = None  # type: ignore[assignment]
        MemoryFoldSystem = None  # type: ignore[assignment]
        TrinityFramework = None  # type: ignore[assignment]
        TrinityFrameworkIntegrator = None  # type: ignore[assignment]

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
            if "trace" in globals():
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
        self._span_processor = None
        self.prometheus_registry = None
        self.prometheus_metrics: Dict[str, Any] = {}

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
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)

            exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            self.tracer = tracer
            self._span_processor = span_processor

            # ΛTAG: otel_meter
            meter_provider = getattr(metrics, "get_meter_provider", None)
            if callable(meter_provider):
                provider = meter_provider()
                if provider:
                    self.meter = provider.get_meter(__name__)
            elif hasattr(metrics, "get_meter"):
                self.meter = metrics.get_meter(__name__)  # type: ignore[attr-defined]

            logger.info("✅ OpenTelemetry initialized")

        except Exception as e:
            logger.error(f"❌ OpenTelemetry initialization failed: {e}")
            self.opentelemetry_enabled = False

    def _initialize_prometheus(self):
        """Initialize Prometheus metrics"""
        if not self.prometheus_enabled:
            logger.info("Prometheus integration disabled by configuration")
            return

        if not PROMETHEUS_AVAILABLE or Gauge is None or CollectorRegistry is None:
            logger.info("Prometheus client not available; skipping metrics registry initialization")
            self.prometheus_enabled = False
            return

        # ΛTAG: prometheus_bridge
        registry = CollectorRegistry()
        self.prometheus_registry = registry
        self.prometheus_metrics = {
            "triad_coherence": Gauge(
                "lukhas_triad_coherence",
                "Estimated coherence score across consciousness, memory, and guardian systems",
                registry=registry,
            ),
            "observability_heartbeat": Gauge(
                "lukhas_observability_heartbeat",
                "Heartbeat indicator for the enterprise observability stack",
                registry=registry,
            ),
        }

        # Initialize default readings to keep dashboards warm
        self.prometheus_metrics["observability_heartbeat"].set(1.0)

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
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
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
    async def collect_triad_metrics(self) -> Dict[str, Any]:
        """Collect synthetic health metrics from Trinity/Constellation components."""

        # ΛTAG: triad_metrics
        metrics_payload: Dict[str, Any] = {
            "consciousness_active": 1.0 if ConsciousnessCore else 0.0,
            "memory_active": 1.0 if MemoryFoldSystem else 0.0,
            "guardian_active": 1.0 if GuardianSystem else 0.0,
        }

        active_components = sum(value for value in metrics_payload.values())
        coherence = 0.55 + 0.15 * active_components
        if TrinityFrameworkIntegrator:
            coherence += 0.05
        if TrinityFramework and hasattr(TrinityFramework, "IDENTITY"):
            coherence += 0.05

        metrics_payload["triad_coherence"] = round(min(coherence, 0.99), 3)
        metrics_payload["origin"] = "lukhas" if LUKHAS_AVAILABLE else "candidate"

        self.submit_metric("gauge", "lukhas.triad.coherence", metrics_payload["triad_coherence"])

        if self.prometheus_enabled and self.prometheus_metrics:
            gauge = self.prometheus_metrics.get("triad_coherence")
            if gauge is not None:
                gauge.set(metrics_payload["triad_coherence"])

        return metrics_payload
