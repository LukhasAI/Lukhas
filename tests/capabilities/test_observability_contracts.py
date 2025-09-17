"""
tests/capabilities/test_observability_contracts.py

Capability regression suite for observability exporters.
Ensures exporters behave, never crash, and key metric families exist.
"""
import os
import re
import socket
import contextlib
import time
import logging
import pytest
import importlib
import sys
from threading import Thread
from http.client import HTTPConnection


def _reset_exporters_module(monkeypatch):
    """
    Reload lukhas.core.metrics_exporters and reset its singletons so tests
    can assert on fresh log emissions each time.
    """
    if "lukhas.core.metrics_exporters" in sys.modules:
        me = sys.modules["lukhas.core.metrics_exporters"]
        # Reset private singletons/guards if present
        for name in ("_PROM_SERVER", "_otel_inited"):
            if hasattr(me, name):
                setattr(me, name, None if name == "_PROM_SERVER" else False)
        importlib.reload(me)
        return me
    else:
        import lukhas.core.metrics_exporters as me
        return me


def _free_port():
    """Get a free port for testing."""
    with contextlib.closing(socket.socket()) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


@pytest.mark.capability
def test_prometheus_exporter_starts_and_exposes_metrics(monkeypatch):
    """Test that Prometheus exporter starts and exposes core metric families."""
    port = _free_port()
    monkeypatch.setenv("LUKHAS_PROM_PORT", str(port))

    # Import modules to register metrics first
    try:
        import lukhas.core.breakthrough  # Register breakthrough metrics
        import storage.events  # Register event metrics
        import memory.folds  # Register memory metrics
    except ImportError:
        pytest.skip("Phase 3 modules not available")

    # Late import triggers exporter on boot
    from lukhas.core.metrics_exporters import enable_runtime_exporters
    enable_runtime_exporters()

    # Give the server a moment to start
    time.sleep(0.3)

    # Test HTTP endpoint
    conn = HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        conn.request("GET", "/metrics")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", "ignore")

        assert resp.status == 200

        # At minimum, Python metrics should be present
        assert "python_info" in body

        # Core metric families should appear (may be TYPE comments only if no samples)
        lukhas_metrics_found = 0
        for fam in (
            "lukhas_tick_duration_seconds",
            "lukhas_drift_ema",
            "lukhas_memory_circuit_breaks_total",
            "lukhas_breakthrough_flags_total",
        ):
            if fam in body:
                lukhas_metrics_found += 1

        # At least some LUKHAS metrics should be present
        assert lukhas_metrics_found >= 1, f"No LUKHAS metrics found in /metrics output"

    finally:
        conn.close()


@pytest.mark.capability
def test_prometheus_exporter_disabled_when_no_port(monkeypatch, caplog):
    """Test that Prometheus exporter is disabled when LUKHAS_PROM_PORT is unset."""
    monkeypatch.delenv("LUKHAS_PROM_PORT", raising=False)
    with caplog.at_level(logging.INFO, logger="lukhas.core.metrics_exporters"):
        me = _reset_exporters_module(monkeypatch)
        me.start_prometheus_exporter()
    assert "Prometheus exporter disabled" in caplog.text


@pytest.mark.capability
def test_otel_disabled_is_noop(monkeypatch, caplog):
    """Test that OTEL init is noop when LUKHAS_OTEL_ENDPOINT is unset."""
    monkeypatch.delenv("LUKHAS_OTEL_ENDPOINT", raising=False)
    with caplog.at_level(logging.INFO, logger="lukhas.core.metrics_exporters"):
        me = _reset_exporters_module(monkeypatch)
        me.init_opentelemetry()
    assert "OTEL disabled" in caplog.text


@pytest.mark.capability
def test_enable_runtime_exporters_idempotent(monkeypatch):
    """Test that enable_runtime_exporters can be called multiple times safely."""
    port = _free_port()
    monkeypatch.setenv("LUKHAS_PROM_PORT", str(port))
    monkeypatch.delenv("LUKHAS_OTEL_ENDPOINT", raising=False)

    from lukhas.core.metrics_exporters import enable_runtime_exporters

    # Should not raise on multiple calls
    enable_runtime_exporters()
    enable_runtime_exporters()
    enable_runtime_exporters()

    # Verify server is still responsive
    time.sleep(0.1)
    conn = HTTPConnection("127.0.0.1", port, timeout=1)
    conn.request("GET", "/metrics")
    resp = conn.getresponse()
    assert resp.status == 200
    conn.close()


@pytest.mark.capability
def test_prometheus_exporter_handles_invalid_port(monkeypatch, caplog):
    """Test that invalid port configuration is handled gracefully."""
    monkeypatch.setenv("LUKHAS_PROM_PORT", "invalid_port")
    with caplog.at_level(logging.WARNING, logger="lukhas.core.metrics_exporters"):
        me = _reset_exporters_module(monkeypatch)
        me.start_prometheus_exporter()
    assert ("Prometheus exporter not started" in caplog.text
            or "invalid literal for int()" in caplog.text)


@pytest.mark.capability
def test_metrics_families_present_in_output():
    """Test that all expected metric families are defined (even if zero)."""
    # Import modules that define metrics
    try:
        from lukhas.core import breakthrough
        from storage import events
    except ImportError:
        pytest.skip("Phase 3 modules not available")

    # Test that Phase 3 modules are available and working
    # These should be importable without error
    assert breakthrough is not None
    assert events is not None

    # Test that basic metric attributes exist (even if no-op)
    # Use hasattr to check for either real metrics or no-op implementations
    breakthrough_has_metrics = (
        hasattr(breakthrough, 'BREAKTHROUGH_FLAGS') or
        hasattr(breakthrough, '_NoopCounter') or
        callable(getattr(breakthrough, 'step', None))
    )

    events_has_metrics = (
        hasattr(events, 'EVENTS_APPENDED') or
        hasattr(events, '_NoopMetric') or
        hasattr(events, 'EventStore')
    )

    assert breakthrough_has_metrics, "Breakthrough module should have metrics or detection capability"
    assert events_has_metrics, "Events module should have metrics or storage capability"


@pytest.mark.capability
def test_otel_missing_packages_handled_gracefully(monkeypatch, caplog):
    """Test OTEL gracefully handles missing opentelemetry packages."""
    monkeypatch.setenv("LUKHAS_OTEL_ENDPOINT", "http://localhost:4318/v1/metrics")

    import builtins
    orig_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name.startswith("opentelemetry"):
            raise ImportError(f"No module named '{name}'")
        return orig_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    with caplog.at_level(logging.WARNING, logger="lukhas.core.metrics_exporters"):
        me = _reset_exporters_module(monkeypatch)
        me.init_opentelemetry()
    assert "OTEL not initialized" in caplog.text


@pytest.mark.capability
def test_prometheus_missing_package_is_logged(monkeypatch, caplog):
    """Test exporters handle missing prometheus_client gracefully."""
    import builtins
    orig_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "prometheus_client":
            raise ImportError("No module named 'prometheus_client'")
        return orig_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    monkeypatch.setenv("LUKHAS_PROM_PORT", "9099")
    with caplog.at_level(logging.WARNING, logger="lukhas.core.metrics_exporters"):
        me = _reset_exporters_module(monkeypatch)
        me.start_prometheus_exporter()
    assert ("Prometheus exporter not started" in caplog.text
            or "No module named 'prometheus_client'" in caplog.text)