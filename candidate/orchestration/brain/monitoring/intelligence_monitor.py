"""
LUKHAS AI Intelligence Monitoring System
======================================
Comprehensive monitoring and logging system for intelligence operations.
Provides real-time performance tracking, agent coordination metrics,
and Trinity Framework compliance monitoring.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import psutil

logger = logging.getLogger("LUKHAS.Orchestration.Monitoring.Intelligence")


class MetricType(Enum):
    """Types of metrics collected"""

    PERFORMANCE = "performance"
    SAFETY = "safety"
    AGENT_COORDINATION = "agent_coordination"
    INTELLIGENCE_ENGINE = "intelligence_engine"
    TRINITY_COMPLIANCE = "trinity_compliance"
    SYSTEM_HEALTH = "system_health"


class AlertLevel(Enum):
    """Alert levels for monitoring"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""

    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    agent_id: Optional[str] = None
    intelligence_engine: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


@dataclass
class AlertEvent:
    """Alert event data structure"""

    alert_id: str
    level: AlertLevel
    message: str
    metric_type: MetricType
    source: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: Optional[datetime] = None
    resolved: bool = False
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "metric_type": self.metric_type.value,
        }


class LukhasIntelligenceMonitor:
    """
    Comprehensive monitoring system for intelligence operations.
    Tracks performance, safety, agent coordination, and Trinity compliance.
    """

    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size

        # Metric storage
        self.metrics_history = defaultdict(lambda: deque(maxlen=max_history_size))
        self.real_time_metrics = {}
        self.aggregated_metrics = {}

        # Alert system
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.alert_thresholds = self._initialize_alert_thresholds()

        # Agent tracking
        self.agent_metrics = defaultdict(dict)
        self.agent_coordination_stats = defaultdict(list)

        # Intelligence engine tracking
        self.engine_metrics = defaultdict(dict)
        self.engine_performance_stats = defaultdict(list)

        # Trinity Framework compliance
        self.trinity_metrics = {
            "identity": deque(maxlen=100),
            "consciousness": deque(maxlen=100),
            "guardian": deque(maxlen=100),
        }

        # System health
        self.system_health_metrics = {}

        # Background tasks
        self.monitoring_tasks = []
        self._monitoring_active = False
        self._lock = threading.Lock()

    def _initialize_alert_thresholds(self) -> dict[str, dict[str, float]]:
        """Initialize alert thresholds for different metrics"""
        return {
            "response_time": {
                "warning": 5.0,  # 5 seconds
                "error": 10.0,  # 10 seconds
                "critical": 30.0,  # 30 seconds
            },
            "error_rate": {
                "warning": 0.05,  # 5%
                "error": 0.10,  # 10%
                "critical": 0.20,  # 20%
            },
            "safety_score": {
                "warning": 0.8,  # Below 80%
                "error": 0.7,  # Below 70%
                "critical": 0.6,  # Below 60%
            },
            "memory_usage": {
                "warning": 0.8,  # 80%
                "error": 0.9,  # 90%
                "critical": 0.95,  # 95%
            },
            "cpu_usage": {
                "warning": 0.8,  # 80%
                "error": 0.9,  # 90%
                "critical": 0.95,  # 95%
            },
            "trinity_compliance": {
                "warning": 0.9,  # Below 90%
                "error": 0.8,  # Below 80%
                "critical": 0.7,  # Below 70%
            },
        }

    async def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("📊 Starting Intelligence Monitoring System")

        self._monitoring_active = True

        # Start background monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_system_health()),
            asyncio.create_task(self._monitor_performance_trends()),
            asyncio.create_task(self._monitor_trinity_compliance()),
            asyncio.create_task(self._process_alerts()),
            asyncio.create_task(self._cleanup_old_data()),
        ]

        logger.info("✅ Intelligence Monitoring System started")

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        logger.info("⏹️ Stopping Intelligence Monitoring System")

        self._monitoring_active = False

        # Cancel background tasks
        for task in self.monitoring_tasks:
            task.cancel()

        # Wait for tasks to finish
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)

        logger.info("✅ Intelligence Monitoring System stopped")

    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        metric_type: MetricType = MetricType.PERFORMANCE,
        agent_id: Optional[str] = None,
        intelligence_engine: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Record a metric value"""
        with self._lock:
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                agent_id=agent_id,
                intelligence_engine=intelligence_engine,
                metadata=metadata or {},
            )

            # Store in history
            self.metrics_history[metric_name].append(metric)

            # Update real-time metrics
            self.real_time_metrics[metric_name] = metric

            # Update agent-specific metrics
            if agent_id:
                self.agent_metrics[agent_id][metric_name] = metric

            # Update engine-specific metrics
            if intelligence_engine:
                self.engine_metrics[intelligence_engine][metric_name] = metric

            # Check for alert conditions
            self._check_alert_conditions(metric_name, value, metric_type)

    def record_operation_start(
        self, operation_id: str, agent_id: str, intelligence_engine: str
    ) -> float:
        """Record the start of an intelligence operation"""
        start_time = time.time()

        operation_data = {
            "operation_id": operation_id,
            "agent_id": agent_id,
            "intelligence_engine": intelligence_engine,
            "start_time": start_time,
            "timestamp": datetime.now(),
        }

        # Store operation start
        with self._lock:
            if not hasattr(self, "active_operations"):
                self.active_operations = {}
            self.active_operations[operation_id] = operation_data

        return start_time

    def record_operation_complete(
        self,
        operation_id: str,
        start_time: float,
        success: bool,
        confidence: float = 0.0,
        safety_score: float = 0.0,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Record the completion of an intelligence operation"""
        end_time = time.time()
        processing_time = end_time - start_time

        with self._lock:
            # Get operation data
            operation_data = getattr(self, "active_operations", {}).get(
                operation_id, {}
            )
            agent_id = operation_data.get("agent_id", "unknown")
            intelligence_engine = operation_data.get("intelligence_engine", "unknown")

            # Record metrics
            self.record_metric(
                "operation_processing_time",
                processing_time,
                "seconds",
                MetricType.PERFORMANCE,
                agent_id,
                intelligence_engine,
                metadata,
            )

            self.record_metric(
                "operation_success",
                1.0 if success else 0.0,
                "boolean",
                MetricType.PERFORMANCE,
                agent_id,
                intelligence_engine,
            )

            if confidence > 0:
                self.record_metric(
                    "operation_confidence",
                    confidence,
                    "score",
                    MetricType.PERFORMANCE,
                    agent_id,
                    intelligence_engine,
                )

            if safety_score > 0:
                self.record_metric(
                    "operation_safety_score",
                    safety_score,
                    "score",
                    MetricType.SAFETY,
                    agent_id,
                    intelligence_engine,
                )

            # Update agent coordination stats
            self.agent_coordination_stats[agent_id].append(
                {
                    "operation_id": operation_id,
                    "processing_time": processing_time,
                    "success": success,
                    "confidence": confidence,
                    "timestamp": datetime.now(),
                }
            )

            # Update engine performance stats
            self.engine_performance_stats[intelligence_engine].append(
                {
                    "operation_id": operation_id,
                    "processing_time": processing_time,
                    "success": success,
                    "confidence": confidence,
                    "timestamp": datetime.now(),
                }
            )

            # Clean up active operation
            if hasattr(self, "active_operations"):
                self.active_operations.pop(operation_id, None)

    def record_trinity_compliance(
        self,
        identity_score: float,
        consciousness_score: float,
        guardian_score: float,
        agent_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Record Trinity Framework compliance scores"""
        timestamp = datetime.now()

        trinity_data = {
            "identity": identity_score,
            "consciousness": consciousness_score,
            "guardian": guardian_score,
            "overall": (identity_score + consciousness_score + guardian_score) / 3,
            "timestamp": timestamp,
            "agent_id": agent_id,
            "metadata": metadata or {},
        }

        # Store in Trinity metrics
        for component, score in trinity_data.items():
            if component in self.trinity_metrics and isinstance(score, float):
                self.trinity_metrics[component].append(
                    {
                        "score": score,
                        "timestamp": timestamp,
                        "agent_id": agent_id,
                    }
                )

        # Record as metrics
        self.record_metric(
            "trinity_identity",
            identity_score,
            "score",
            MetricType.TRINITY_COMPLIANCE,
            agent_id,
        )
        self.record_metric(
            "trinity_consciousness",
            consciousness_score,
            "score",
            MetricType.TRINITY_COMPLIANCE,
            agent_id,
        )
        self.record_metric(
            "trinity_guardian",
            guardian_score,
            "score",
            MetricType.TRINITY_COMPLIANCE,
            agent_id,
        )
        self.record_metric(
            "trinity_overall",
            trinity_data["overall"],
            "score",
            MetricType.TRINITY_COMPLIANCE,
            agent_id,
        )

    def _check_alert_conditions(
        self, metric_name: str, value: float, metric_type: MetricType
    ):
        """Check if metric value triggers any alerts"""
        # Get alert thresholds for this metric
        thresholds = self.alert_thresholds.get(metric_name, {})

        if not thresholds:
            return

        # Check thresholds
        alert_level = None
        threshold_value = None

        if value >= thresholds.get("critical", float("inf")):
            alert_level = AlertLevel.CRITICAL
            threshold_value = thresholds["critical"]
        elif value >= thresholds.get("error", float("inf")):
            alert_level = AlertLevel.ERROR
            threshold_value = thresholds["error"]
        elif value >= thresholds.get("warning", float("inf")):
            alert_level = AlertLevel.WARNING
            threshold_value = thresholds["warning"]

        # For metrics where lower is worse (like safety_score)
        if metric_name in ["safety_score", "trinity_compliance"]:
            if value <= thresholds.get("critical", 0):
                alert_level = AlertLevel.CRITICAL
                threshold_value = thresholds["critical"]
            elif value <= thresholds.get("error", 0):
                alert_level = AlertLevel.ERROR
                threshold_value = thresholds["error"]
            elif value <= thresholds.get("warning", 0):
                alert_level = AlertLevel.WARNING
                threshold_value = thresholds["warning"]

        # Create alert if threshold exceeded
        if alert_level:
            alert_id = f"{metric_name}_{alert_level.value}_{int(time.time())}"

            alert = AlertEvent(
                alert_id=alert_id,
                level=alert_level,
                message=f"{metric_name} threshold exceeded: {value} (threshold: {threshold_value})",
                metric_type=metric_type,
                source="intelligence_monitor",
                value=value,
                threshold=threshold_value,
            )

            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

            logger.warning(f"🚨 Alert: {alert.message}")

    async def _monitor_system_health(self):
        """Monitor system health metrics"""
        while self._monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_metric(
                    "cpu_usage",
                    cpu_percent / 100,
                    "percentage",
                    MetricType.SYSTEM_HEALTH,
                )

                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.record_metric(
                    "memory_usage",
                    memory_percent / 100,
                    "percentage",
                    MetricType.SYSTEM_HEALTH,
                )

                # Disk usage
                disk = psutil.disk_usage("/")
                disk_percent = disk.percent
                self.record_metric(
                    "disk_usage",
                    disk_percent / 100,
                    "percentage",
                    MetricType.SYSTEM_HEALTH,
                )

                # Active operations count
                active_ops = len(getattr(self, "active_operations", {}))
                self.record_metric(
                    "active_operations", active_ops, "count", MetricType.SYSTEM_HEALTH
                )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error monitoring system health: {e}")
                await asyncio.sleep(30)

    async def _monitor_performance_trends(self):
        """Monitor performance trends and detect anomalies"""
        while self._monitoring_active:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Analyze response time trends
                await self._analyze_response_time_trends()

                # Analyze error rate trends
                await self._analyze_error_rate_trends()

                # Analyze agent performance trends
                await self._analyze_agent_performance_trends()

            except Exception as e:
                logger.error(f"Error monitoring performance trends: {e}")

    async def _analyze_response_time_trends(self):
        """Analyze response time trends"""
        response_times = self.metrics_history.get("operation_processing_time", deque())

        if len(response_times) < 10:
            return

        recent_times = [
            m.value for m in list(response_times)[-50:]
        ]  # Last 50 operations
        avg_response_time = sum(recent_times) / len(recent_times)

        self.record_metric(
            "avg_response_time", avg_response_time, "seconds", MetricType.PERFORMANCE
        )

        # Check for degradation
        if len(response_times) >= 100:
            older_times = [
                m.value for m in list(response_times)[-100:-50]
            ]  # Previous 50 operations
            older_avg = sum(older_times) / len(older_times)

            if avg_response_time > older_avg * 1.5:  # 50% increase
                logger.warning(
                    f"📈 Response time degradation detected: {avg_response_time:.2f}s vs {older_avg:.2f}s"
                )

    async def _analyze_error_rate_trends(self):
        """Analyze error rate trends"""
        success_metrics = self.metrics_history.get("operation_success", deque())

        if len(success_metrics) < 10:
            return

        recent_success = [
            m.value for m in list(success_metrics)[-50:]
        ]  # Last 50 operations
        success_rate = sum(recent_success) / len(recent_success)
        error_rate = 1.0 - success_rate

        self.record_metric(
            "error_rate", error_rate, "percentage", MetricType.PERFORMANCE
        )

    async def _analyze_agent_performance_trends(self):
        """Analyze agent performance trends"""
        for agent_id, stats in self.agent_coordination_stats.items():
            if len(stats) < 5:
                continue

            recent_stats = stats[-20:]  # Last 20 operations

            # Calculate agent-specific metrics
            avg_processing_time = sum(s["processing_time"] for s in recent_stats) / len(
                recent_stats
            )
            success_rate = sum(1 for s in recent_stats if s["success"]) / len(
                recent_stats
            )
            avg_confidence = sum(
                s["confidence"] for s in recent_stats if s["confidence"] > 0
            ) / max(1, len([s for s in recent_stats if s["confidence"] > 0]))

            # Record agent-specific metrics
            self.record_metric(
                "agent_avg_processing_time",
                avg_processing_time,
                "seconds",
                MetricType.AGENT_COORDINATION,
                agent_id,
            )
            self.record_metric(
                "agent_success_rate",
                success_rate,
                "percentage",
                MetricType.AGENT_COORDINATION,
                agent_id,
            )
            self.record_metric(
                "agent_avg_confidence",
                avg_confidence,
                "score",
                MetricType.AGENT_COORDINATION,
                agent_id,
            )

    async def _monitor_trinity_compliance(self):
        """Monitor Trinity Framework compliance trends"""
        while self._monitoring_active:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes

                # Calculate overall Trinity compliance
                trinity_scores = []
                for _component, metrics in self.trinity_metrics.items():
                    if metrics and isinstance(metrics, deque):
                        recent_scores = [
                            m["score"]
                            for m in list(metrics)[-10:]
                            if isinstance(m, dict) and "score" in m
                        ]
                        if recent_scores:
                            avg_score = sum(recent_scores) / len(recent_scores)
                            trinity_scores.append(avg_score)

                if trinity_scores:
                    overall_compliance = sum(trinity_scores) / len(trinity_scores)
                    self.record_metric(
                        "trinity_overall_compliance",
                        overall_compliance,
                        "score",
                        MetricType.TRINITY_COMPLIANCE,
                    )

            except Exception as e:
                logger.error(f"Error monitoring Trinity compliance: {e}")

    async def _process_alerts(self):
        """Process and manage alerts"""
        while self._monitoring_active:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Auto-resolve alerts that are no longer triggered
                current_time = datetime.now()
                alerts_to_resolve = []

                for alert_id, alert in self.active_alerts.items():
                    # Auto-resolve alerts older than 1 hour if conditions have improved
                    if (current_time - alert.timestamp).total_seconds() > 3600:
                        alerts_to_resolve.append(alert_id)

                for alert_id in alerts_to_resolve:
                    self.resolve_alert(alert_id)

            except Exception as e:
                logger.error(f"Error processing alerts: {e}")

    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        while self._monitoring_active:
            try:
                await asyncio.sleep(3600)  # Clean up every hour

                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=24)

                # Clean up metrics history
                for metric_name, history in self.metrics_history.items():
                    # Convert to list, filter, and convert back to deque
                    filtered_metrics = [m for m in history if m.timestamp > cutoff_time]
                    self.metrics_history[metric_name] = deque(
                        filtered_metrics, maxlen=self.max_history_size
                    )

                # Clean up agent coordination stats
                for agent_id, stats in self.agent_coordination_stats.items():
                    self.agent_coordination_stats[agent_id] = [
                        s for s in stats if s["timestamp"] > cutoff_time
                    ]

                # Clean up engine performance stats
                for engine, stats in self.engine_performance_stats.items():
                    self.engine_performance_stats[engine] = [
                        s for s in stats if s["timestamp"] > cutoff_time
                    ]

                logger.info("🧹 Cleaned up old monitoring data")

            except Exception as e:
                logger.error(f"Error cleaning up old data: {e}")

    def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            del self.active_alerts[alert_id]
            logger.info(f"✅ Resolved alert: {alert_id}")

    def get_real_time_metrics(self) -> dict[str, Any]:
        """Get current real-time metrics"""
        with self._lock:
            return {
                name: metric.to_dict()
                for name, metric in self.real_time_metrics.items()
            }

    def get_agent_metrics(self, agent_id: Optional[str] = None) -> dict[str, Any]:
        """Get agent-specific metrics"""
        with self._lock:
            if agent_id:
                return {
                    name: metric.to_dict()
                    for name, metric in self.agent_metrics.get(agent_id, {}).items()
                }
            return {
                agent: {name: metric.to_dict() for name, metric in metrics.items()}
                for agent, metrics in self.agent_metrics.items()
            }

    def get_engine_metrics(self, engine: Optional[str] = None) -> dict[str, Any]:
        """Get intelligence engine specific metrics"""
        with self._lock:
            if engine:
                return {
                    name: metric.to_dict()
                    for name, metric in self.engine_metrics.get(engine, {}).items()
                }
            return {
                eng: {name: metric.to_dict() for name, metric in metrics.items()}
                for eng, metrics in self.engine_metrics.items()
            }

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get current active alerts"""
        return [alert.to_dict() for alert in self.active_alerts.values()]

    def get_trinity_compliance_summary(self) -> dict[str, Any]:
        """Get Trinity Framework compliance summary"""
        summary = {}

        for component, metrics in self.trinity_metrics.items():
            if metrics and isinstance(metrics, deque):
                recent_scores = [
                    m["score"]
                    for m in list(metrics)[-10:]
                    if isinstance(m, dict) and "score" in m
                ]
                if recent_scores:
                    summary[component] = {
                        "current_score": recent_scores[-1],
                        "average_score": sum(recent_scores) / len(recent_scores),
                        "min_score": min(recent_scores),
                        "max_score": max(recent_scores),
                        "trend": "stable",  # Could be enhanced with trend analysis
                    }

        return summary

    def get_system_health_summary(self) -> dict[str, Any]:
        """Get system health summary"""
        health_metrics = [
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "active_operations",
        ]

        summary = {}
        for metric_name in health_metrics:
            if metric_name in self.real_time_metrics:
                metric = self.real_time_metrics[metric_name]
                summary[metric_name] = {
                    "current_value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "status": self._get_health_status(metric_name, metric.value),
                }

        return summary

    def _get_health_status(self, metric_name: str, value: float) -> str:
        """Get health status for a metric value"""
        thresholds = self.alert_thresholds.get(metric_name, {})

        if value >= thresholds.get("critical", float("inf")):
            return "critical"
        elif value >= thresholds.get("error", float("inf")):
            return "error"
        elif value >= thresholds.get("warning", float("inf")):
            return "warning"
        else:
            return "healthy"

    def export_metrics(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> dict[str, Any]:
        """Export metrics for external analysis"""
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=1)
        if end_time is None:
            end_time = datetime.now()

        exported_data = {
            "export_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "exported_at": datetime.now().isoformat(),
            },
            "metrics": {},
            "alerts": [],
            "agent_stats": {},
            "engine_stats": {},
            "trinity_compliance": self.get_trinity_compliance_summary(),
        }

        # Export metrics in time range
        for metric_name, history in self.metrics_history.items():
            filtered_metrics = [
                m.to_dict() for m in history if start_time <= m.timestamp <= end_time
            ]
            if filtered_metrics:
                exported_data["metrics"][metric_name] = filtered_metrics

        # Export alerts in time range
        exported_data["alerts"] = [
            alert.to_dict()
            for alert in self.alert_history
            if start_time <= alert.timestamp <= end_time
        ]

        return exported_data


# Global monitor instance
_monitor_instance = None


def get_monitor() -> LukhasIntelligenceMonitor:
    """Get the global monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = LukhasIntelligenceMonitor()
    return _monitor_instance


# Convenience functions for monitoring
def record_operation_metric(
    metric_name: str,
    value: float,
    unit: str = "",
    agent_id: Optional[str] = None,
    intelligence_engine: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
):
    """Convenience function to record a metric"""
    monitor = get_monitor()
    monitor.record_metric(
        metric_name,
        value,
        unit,
        MetricType.PERFORMANCE,
        agent_id,
        intelligence_engine,
        metadata,
    )


def start_operation_tracking(
    operation_id: str, agent_id: str, intelligence_engine: str
) -> float:
    """Convenience function to start operation tracking"""
    monitor = get_monitor()
    return monitor.record_operation_start(operation_id, agent_id, intelligence_engine)


def complete_operation_tracking(
    operation_id: str,
    start_time: float,
    success: bool,
    confidence: float = 0.0,
    safety_score: float = 0.0,
    metadata: Optional[dict[str, Any]] = None,
):
    """Convenience function to complete operation tracking"""
    monitor = get_monitor()
    monitor.record_operation_complete(
        operation_id, start_time, success, confidence, safety_score, metadata
    )


if __name__ == "__main__":
    # Example usage and testing
    async def example_monitoring():
        """Example of monitoring system usage"""

        # Get monitor instance
        monitor = get_monitor()

        # Start monitoring
        await monitor.start_monitoring()

        # Simulate some operations
        for i in range(5):
            operation_id = f"test_op_{i}"
            start_time = start_operation_tracking(
                operation_id, "consciousness_architect_001", "meta_cognitive"
            )

            # Simulate processing
            await asyncio.sleep(0.1)

            # Record completion
            complete_operation_tracking(
                operation_id,
                start_time,
                True,
                confidence=0.85 + (i * 0.02),
                safety_score=0.9 + (i * 0.01),
            )

            # Record Trinity compliance
            monitor.record_trinity_compliance(
                0.95, 0.92, 0.88, "consciousness_architect_001"
            )

        # Wait for metrics to be processed
        await asyncio.sleep(2)

        # Get metrics summary
        real_time = monitor.get_real_time_metrics()
        agent_metrics = monitor.get_agent_metrics("consciousness_architect_001")
        trinity_summary = monitor.get_trinity_compliance_summary()
        health_summary = monitor.get_system_health_summary()

        print("📊 Monitoring Results:")
        print(f"Real-time metrics: {len(real_time)} metrics")
        print(f"Agent metrics: {len(agent_metrics)} metrics")
        print(f"Trinity compliance: {trinity_summary}")
        print(f"System health: {health_summary}")
        print(f"Active alerts: {len(monitor.get_active_alerts())}")

        # Stop monitoring
        await monitor.stop_monitoring()

    # Run example
    asyncio.run(example_monitoring())
