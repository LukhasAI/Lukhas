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
from typing import Optional

# Observability integrations
try:
    from datadog import DogStatsd, initialize
    from datadog.api.metrics import Metric

    DATADOG_AVAILABLE = True
except ImportError:
    DATADOG_AVAILABLE = False

try:
    from opentelemetry import metrics, trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

try:
    import prometheus_client

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# LUKHAS integrations
try:
    from lukhas.consciousness import ConsciousnessCore
    from lukhas.guardian import GuardianSystem
    from lukhas.memory import MemoryFoldSystem
    from lukhas.trinity import TrinityFramework

    LUKHAS_AVAILABLE = True
except ImportError:
    try:
        from candidate.consciousness import ConsciousnessCore
        from candidate.memory import MemoryFoldSystem

        LUKHAS_AVAILABLE = True
    except ImportError:
        LUKHAS_AVAILABLE = False

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

    # TODO: Implement real metric collection from LUKHAS components.
    # The following methods are placeholders for where you would integrate
    # with the actual application code to collect and submit metrics.
    #
    # Example:
    #
    # async def collect_trinity_metrics(self, trinity_app: TrinityFramework):
    #     metrics = await trinity_app.get_performance_metrics()
    #     self.submit_metric('gauge', 'lukhas.trinity.coherence', metrics.coherence_score)
    #     self.submit_metric('gauge', 'lukhas.trinity.active_sessions', metrics.active_sessions)
    #
    # This would be called from a background task or a periodic job within the
    # main application.
