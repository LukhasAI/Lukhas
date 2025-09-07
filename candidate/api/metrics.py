"""Metrics API Endpoint ⚛️📊
Prometheus-compatible metrics endpoint for monitoring.
"""
from fastapi import APIRouter
from fastapi.responses import Response

from lukhas.metrics import get_metrics_collector

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics():
    """Prometheus-compatible metrics endpoint"""
    collector = get_metrics_collector()
    metrics_output = collector.get_metrics()

    return Response(
        content=metrics_output,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get("/health/alerts")
def get_alerts():
    """Check for active alert conditions"""
    collector = get_metrics_collector()
    alerts = collector.check_alert_conditions()

    status = "healthy" if not alerts else "warning"

    return {"status": status, "alerts": alerts, "alert_count": len(alerts)}
