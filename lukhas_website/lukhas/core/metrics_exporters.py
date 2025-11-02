"""
lukhas/core/metrics_exporters.py

Prometheus + OTEL exporters with opt-in, safe defaults.
Prometheus is fully optional; OTEL is noop if not configured.

Usage:
  from core.metrics_exporters import enable_runtime_exporters
  enable_runtime_exporters()  # Call once at app boot
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# ---- Prometheus HTTP exporter (pull-based) -----------------------------------
_PROM_SERVER = None


def start_prometheus_exporter() -> None:
    """Start Prometheus /metrics if LUKHAS_PROM_PORT is set; idempotent."""
    global _PROM_SERVER
    if _PROM_SERVER is not None:
        return
    port = os.getenv("LUKHAS_PROM_PORT")
    if not port:
        logger.info("Prometheus exporter disabled (LUKHAS_PROM_PORT unset)")
        return
    try:
        from prometheus_client import start_http_server

        start_http_server(int(port))
        _PROM_SERVER = True
        logger.info("✅ Prometheus exporter started on :%s", port)
    except Exception as e:
        logger.warning("Prometheus exporter not started: %s", e)


# ---- OpenTelemetry (push-based) ----------------------------------------------
_otel_inited = False


def init_opentelemetry() -> None:
    """Init OTEL metrics/traces if LUKHAS_OTEL_ENDPOINT is set; idempotent."""
    global _otel_inited
    if _otel_inited:
        return
    endpoint = os.getenv("LUKHAS_OTEL_ENDPOINT")
    if not endpoint:
        logger.info("OTEL disabled (LUKHAS_OTEL_ENDPOINT unset)")
        return
    try:
        # Minimal, metrics only (safe defaults). Traces can be added later.
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource

        # Configure
        res = Resource.create({"service.name": os.getenv("LUKHAS_SERVICE", "lukhas-core")})
        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint, timeout=5.0))
        provider = MeterProvider(resource=res, metric_readers=[reader])

        from opentelemetry import metrics

        metrics.set_meter_provider(provider)
        _otel_inited = True
        logger.info("✅ OTEL metrics initialized (endpoint=%s)", endpoint)
    except Exception as e:
        logger.warning("OTEL not initialized: %s", e)


def enable_runtime_exporters() -> None:
    """Single entry point used by apps/CLI/tests that want exporters."""
    start_prometheus_exporter()
    init_opentelemetry()


# CLI for testing
if __name__ == "__main__":
    import sys
    import time

    print("Metrics Exporters CLI")
    print("Set LUKHAS_PROM_PORT=9095 to start Prometheus exporter")
    print("Set LUKHAS_OTEL_ENDPOINT=http://localhost:4318/v1/metrics for OTEL")

    enable_runtime_exporters()

    if os.getenv("LUKHAS_PROM_PORT"):
        print(f"Prometheus metrics available at http://localhost:{os.getenv('LUKHAS_PROM_PORT')}/metrics")
        print("Press Ctrl+C to exit...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    else:
        print("No exporters configured. Exiting.")
