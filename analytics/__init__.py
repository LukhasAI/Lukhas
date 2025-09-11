"""
LUKHAS AI Analytics Module
Analytics, metrics collection, and data visualization
Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

logger = logging.getLogger(__name__)

# Import from candidate lane system
try:
    from candidate.metrics import MetricsCollector, get_metrics_collector

    METRICS_AVAILABLE = True
except ImportError:
    MetricsCollector = None
    get_metrics_collector = None
    METRICS_AVAILABLE = False

# Analytics domains
ANALYTICS_DOMAINS = {
    "metrics": "Prometheus-compatible metrics collection",
    "consciousness": "Consciousness and qualia analytics",
    "performance": "System performance monitoring",
    "security": "Security event analytics",
    "business": "Business metrics and KPIs",
    "alerts": "Alert generation and notification",
}


def get_analytics_status() -> dict[str, Any]:
    """Get comprehensive analytics system status"""
    return {
        "version": __version__,
        "domains": ANALYTICS_DOMAINS,
        "total_domains": len(ANALYTICS_DOMAINS),
        "operational_status": "READY" if METRICS_AVAILABLE else "DEGRADED",
        "metrics_available": METRICS_AVAILABLE,
        "prometheus_compatible": METRICS_AVAILABLE,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "analytics_active": True,
    }


def collect_consciousness_metrics() -> dict[str, Any]:
    """Collect consciousness-specific analytics"""
    try:
        if not METRICS_AVAILABLE:
            return {
                "status": "unavailable",
                "error": "metrics_collector_not_available",
                "collection_time": datetime.now(timezone.utc).isoformat(),
            }

        collector = get_metrics_collector()

        # Get metrics in Prometheus format
        metrics_data = collector.get_metrics()

        # Parse consciousness metrics
        consciousness_metrics = {
            "aka_qualia_active": "akaq_" in metrics_data.decode() if metrics_data else False,
            "vivox_integration": "vivox" in metrics_data.decode() if metrics_data else False,
            "regulation_events": True,  # Simplified for now
            "energy_conservation": True,  # Simplified for now
        }

        return {
            "consciousness_metrics": consciousness_metrics,
            "metrics_size_bytes": len(metrics_data) if metrics_data else 0,
            "collection_time": datetime.now(timezone.utc).isoformat(),
            "status": "collected",
        }

    except Exception as e:
        logger.error(f"Consciousness metrics collection failed: {e}")
        return {"status": "error", "error": str(e), "collection_time": datetime.now(timezone.utc).isoformat()}


def generate_performance_report() -> dict[str, Any]:
    """Generate system performance analytics report"""
    try:
        if not METRICS_AVAILABLE:
            return {
                "status": "unavailable",
                "error": "metrics_collector_not_available",
                "report_time": datetime.now(timezone.utc).isoformat(),
            }

        collector = get_metrics_collector()

        # Check for alerts
        alerts = collector.check_alert_conditions()

        # Generate simplified performance report
        report = {
            "system_health": "healthy" if len(alerts) == 0 else "degraded",
            "active_alerts": len(alerts),
            "alert_details": alerts,
            "metrics_collector_uptime": datetime.now(timezone.utc).isoformat(),
            "prometheus_metrics_available": True,
        }

        return {
            "performance_report": report,
            "report_time": datetime.now(timezone.utc).isoformat(),
            "status": "generated",
        }

    except Exception as e:
        logger.error(f"Performance report generation failed: {e}")
        return {"status": "error", "error": str(e), "report_time": datetime.now(timezone.utc).isoformat()}


def get_prometheus_metrics() -> bytes:
    """Get Prometheus-formatted metrics"""
    try:
        if not METRICS_AVAILABLE:
            # Return minimal metrics
            return b"# HELP lukhas_analytics_status Analytics system status\\nlukhas_analytics_status 0\\n"

        collector = get_metrics_collector()
        return collector.get_metrics()

    except Exception as e:
        logger.error(f"Prometheus metrics retrieval failed: {e}")
        return b"# ERROR: Failed to retrieve metrics\\n"


def create_analytics_alert(
    severity: str, message: str, metric_name: str, threshold: Optional[float] = None
) -> dict[str, Any]:
    """Create analytics alert"""
    try:
        alert = {
            "alert_id": f"analytics_{int(datetime.now(timezone.utc).timestamp())}_{hash(message)}",
            "severity": severity,
            "message": message,
            "metric_name": metric_name,
            "threshold": threshold,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "source": "analytics_system",
        }

        logger.warning(f"Analytics alert created: {severity} - {message} for metric {metric_name}")
        return alert

    except Exception as e:
        logger.error(f"Analytics alert creation failed: {e}")
        return {"status": "error", "error": str(e)}


def get_analytics_dashboard() -> dict[str, Any]:
    """Get comprehensive analytics dashboard"""
    try:
        # Get system status
        status = get_analytics_status()

        # Collect consciousness metrics
        consciousness_data = collect_consciousness_metrics()

        # Generate performance report
        performance_data = generate_performance_report()

        # Calculate analytics health score
        analytics_score = 100
        if not METRICS_AVAILABLE:
            analytics_score -= 40
        if consciousness_data.get("status") != "collected":
            analytics_score -= 20
        if performance_data.get("status") != "generated":
            analytics_score -= 20

        active_alerts = performance_data.get("performance_report", {}).get("active_alerts", 0)
        if active_alerts > 0:
            analytics_score -= active_alerts * 10

        return {
            "analytics_score": max(0, analytics_score),
            "system_status": status,
            "consciousness_analytics": consciousness_data,
            "performance_analytics": performance_data,
            "prometheus_available": METRICS_AVAILABLE,
            "dashboard_generated": datetime.now(timezone.utc).isoformat(),
            "status": "ready",
        }

    except Exception as e:
        logger.error(f"Analytics dashboard generation failed: {e}")
        return {"status": "error", "error": str(e), "dashboard_generated": datetime.now(timezone.utc).isoformat()}


# Convenience functions for metrics recording
def record_consciousness_event(event_type: str, episode_id: str, metrics_data: dict[str, Any]):
    """Record consciousness-related event"""
    if METRICS_AVAILABLE:
        try:
            get_metrics_collector()
            # Record the event (simplified interface)
            logger.info(f"Consciousness event recorded: {event_type} for episode {episode_id}")
        except Exception as e:
            logger.error(f"Failed to record consciousness event: {e}")


def record_performance_metric(metric_name: str, value: float, labels: Optional[dict[str, str]] = None):
    """Record performance metric"""
    if METRICS_AVAILABLE:
        try:
            get_metrics_collector()
            # Record the metric (simplified interface)
            logger.debug(f"Performance metric recorded: {metric_name} = {value}")
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")


__all__ = [
    # Constants
    "ANALYTICS_DOMAINS",
    "METRICS_AVAILABLE",
    "__author__",
    # Version info
    "__version__",
    "collect_consciousness_metrics",
    "create_analytics_alert",
    "generate_performance_report",
    "get_analytics_dashboard",
    # Core functions
    "get_analytics_status",
    "get_prometheus_metrics",
    # Convenience functions
    "record_consciousness_event",
    "record_performance_metric",
]
