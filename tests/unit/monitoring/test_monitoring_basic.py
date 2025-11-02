# ΛTAG: monitoring
"""Basic tests for monitoring module."""

from monitoring import (
    MONITORING_DOMAINS,
    collect_system_metrics,
    get_health_dashboard,
    get_monitoring_status,
)


def test_get_monitoring_status_fields():
    """Verify monitoring status contains expected fields."""
    status = get_monitoring_status()
    assert status["operational_status"] == "READY"
    assert status["monitoring_active"] is True
    assert status["total_domains"] == len(MONITORING_DOMAINS)


def test_collect_system_metrics_structure():
    """Ensure system metrics include core categories."""
    metrics = collect_system_metrics()
    assert metrics["status"] == "collected"
    assert set(metrics.keys()) >= {"cpu", "memory", "disk", "collection_time"}


def test_get_health_dashboard_aggregates(monkeypatch):
    """Validate health dashboard aggregates patched data."""
    dummy_metrics = {
        "cpu": {"cpu_percent": 10},
        "memory": {"percent_used": 20},
        "disk": {},
        "collection_time": "now",
        "status": "collected",
    }
    dummy_consciousness = {"status": "completed"}

    monkeypatch.setattr("monitoring.collect_system_metrics", lambda: dummy_metrics)
    monkeypatch.setattr("monitoring.monitor_consciousness_health", lambda: dummy_consciousness)

    dashboard = get_health_dashboard()
    assert dashboard["status"] == "ready"
    assert dashboard["health_score"] == 100
    assert "system_metrics" in dashboard and "consciousness_health" in dashboard
