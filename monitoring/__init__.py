"""
LUKHAS AI Monitoring Module
System monitoring, metrics collection, and health tracking
Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

logger = logging.getLogger(__name__, timezone)

# Monitoring domains
MONITORING_DOMAINS = {
    "system": "System resource monitoring (CPU, memory, disk)",
    "consciousness": "Consciousness module health and performance",
    "agents": "Agent system monitoring and coordination",
    "api": "API endpoint performance and availability",
    "security": "Security event monitoring and threat detection",
    "business": "Business metrics and KPI tracking",
}


class SystemMetrics:
    """System resource metrics collector"""

    @staticmethod
    def get_cpu_metrics() -> Dict[str, Any]:
        """Get CPU usage metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else [0, 0, 0],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def get_memory_metrics() -> Dict[str, Any]:
        """Get memory usage metrics"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent_used": memory.percent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def get_disk_metrics() -> Dict[str, Any]:
        """Get disk usage metrics"""
        disk = psutil.disk_usage("/")
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": round((disk.used / disk.total) * 100, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class ConsciousnessMonitor:
    """Monitor consciousness module health"""

    @staticmethod
    def check_memory_system() -> Dict[str, Any]:
        """Check memory system health"""
        try:
            from lukhas.memory import MEMORY_AVAILABLE, create_fold

            # Test memory functionality
            test_fold = create_fold("monitor_test", ["system", "health"])

            return {
                "status": "healthy",
                "memory_available": MEMORY_AVAILABLE,
                "test_fold_created": test_fold is not None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

    @staticmethod
    def check_agent_system() -> Dict[str, Any]:
        """Check agent system health"""
        try:
            from agent import get_agent_system_status

            status = get_agent_system_status()

            return {
                "status": "healthy" if status.get("operational_status") == "READY" else "degraded",
                "agent_status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}


def get_monitoring_status() -> Dict[str, Any]:
    """Get comprehensive monitoring system status"""
    return {
        "version": __version__,
        "domains": MONITORING_DOMAINS,
        "total_domains": len(MONITORING_DOMAINS),
        "operational_status": "READY",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "monitoring_active": True,
    }


def collect_system_metrics() -> Dict[str, Any]:
    """Collect comprehensive system metrics"""
    try:
        metrics = SystemMetrics()

        return {
            "cpu": metrics.get_cpu_metrics(),
            "memory": metrics.get_memory_metrics(),
            "disk": metrics.get_disk_metrics(),
            "collection_time": datetime.now(timezone.utc).isoformat(),
            "status": "collected",
        }
    except Exception as e:
        logger.error(f"System metrics collection failed: {e}")
        return {"status": "error", "error": str(e), "collection_time": datetime.now(timezone.utc).isoformat()}


def monitor_consciousness_health() -> Dict[str, Any]:
    """Monitor consciousness system health"""
    try:
        monitor = ConsciousnessMonitor()

        return {
            "memory_system": monitor.check_memory_system(),
            "agent_system": monitor.check_agent_system(),
            "overall_health": "healthy",
            "check_time": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }
    except Exception as e:
        logger.error(f"Consciousness health monitoring failed: {e}")
        return {"status": "error", "error": str(e), "check_time": datetime.now(timezone.utc).isoformat()}


def create_alert(severity: str, message: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create monitoring alert"""
    try:
        alert = {
            "alert_id": f"alert_{int(time.time())}_{hash(message)}",
            "severity": severity,
            "message": message,
            "source": source,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }

        logger.warning(f"Alert created: {severity} - {message} from {source}")
        return alert
    except Exception as e:
        logger.error(f"Alert creation failed: {e}")
        return {"status": "error", "error": str(e)}


def get_health_dashboard() -> Dict[str, Any]:
    """Get comprehensive health dashboard"""
    try:
        system_metrics = collect_system_metrics()
        consciousness_health = monitor_consciousness_health()

        # Calculate overall health score
        health_score = 100
        if system_metrics.get("status") != "collected":
            health_score -= 30
        if consciousness_health.get("status") != "completed":
            health_score -= 40
        if system_metrics.get("memory", {}).get("percent_used", 0) > 90:
            health_score -= 20
        if system_metrics.get("cpu", {}).get("cpu_percent", 0) > 90:
            health_score -= 10

        return {
            "health_score": max(0, health_score),
            "system_metrics": system_metrics,
            "consciousness_health": consciousness_health,
            "dashboard_generated": datetime.now(timezone.utc).isoformat(),
            "status": "ready",
        }
    except Exception as e:
        logger.error(f"Health dashboard generation failed: {e}")
        return {"status": "error", "error": str(e), "dashboard_generated": datetime.now(timezone.utc).isoformat()}


__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Constants
    "MONITORING_DOMAINS",
    # Classes
    "SystemMetrics",
    "ConsciousnessMonitor",
    # Core functions
    "get_monitoring_status",
    "collect_system_metrics",
    "monitor_consciousness_health",
    "create_alert",
    "get_health_dashboard",
]
