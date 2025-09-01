"""
Performance Monitoring and Optimization System for Tool Execution
===============================================================
Real-time monitoring, alerting, and optimization for the LUKHAS AI tool execution ecosystem.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import psutil

logger = logging.getLogger("ΛTRACE.tools.performance")


@dataclass
class PerformanceMetric:
    """Single performance metric measurement"""

    timestamp: float
    metric_name: str
    value: float
    unit: str
    component: str
    context: dict[str, Any] = None


@dataclass
class PerformanceAlert:
    """Performance alert definition"""

    alert_id: str
    severity: str  # "critical", "warning", "info"
    message: str
    metric_name: str
    threshold_value: float
    current_value: float
    component: str
    timestamp: float
    resolved: bool = False


class PerformanceCollector:
    """Collects performance metrics from various system components"""

    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.collecting = False
        self.metrics_buffer = deque(maxlen=10000)  # Keep last 10k metrics

        # Component-specific collectors
        self.system_collector = SystemMetricsCollector()
        self.tool_collector = ToolExecutionMetricsCollector()

    async def start_collection(self):
        """Start continuous metric collection"""
        self.collecting = True
        logger.info("Performance collection started")

        while self.collecting:
            try:
                # Collect system metrics
                system_metrics = await self.system_collector.collect()
                for metric in system_metrics:
                    self.metrics_buffer.append(metric)

                # Collect tool execution metrics
                tool_metrics = await self.tool_collector.collect()
                for metric in tool_metrics:
                    self.metrics_buffer.append(metric)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"Performance collection error: {e}")
                await asyncio.sleep(5)  # Wait before retry

    def stop_collection(self):
        """Stop metric collection"""
        self.collecting = False
        logger.info("Performance collection stopped")

    def get_recent_metrics(
        self,
        component: Optional[str] = None,
        metric_name: Optional[str] = None,
        time_window: int = 300,
    ) -> list[PerformanceMetric]:
        """Get recent metrics within time window"""
        current_time = time.time()
        cutoff_time = current_time - time_window

        filtered_metrics = []
        for metric in self.metrics_buffer:
            if metric.timestamp < cutoff_time:
                continue

            if component and metric.component != component:
                continue

            if metric_name and metric.metric_name != metric_name:
                continue

            filtered_metrics.append(metric)

        return filtered_metrics


class SystemMetricsCollector:
    """Collects system-level performance metrics"""

    async def collect(self) -> list[PerformanceMetric]:
        """Collect system metrics"""
        timestamp = time.time()
        metrics = []

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics.append(
                PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="cpu_usage",
                    value=cpu_percent,
                    unit="percent",
                    component="system",
                )
            )

            # Memory usage
            memory = psutil.virtual_memory()
            metrics.append(
                PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="memory_usage",
                    value=memory.percent,
                    unit="percent",
                    component="system",
                    context={"available_mb": memory.available // (1024 * 1024)},
                )
            )

            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.extend(
                    [
                        PerformanceMetric(
                            timestamp=timestamp,
                            metric_name="disk_read_mb_per_sec",
                            value=disk_io.read_bytes / (1024 * 1024),
                            unit="mb/s",
                            component="system",
                        ),
                        PerformanceMetric(
                            timestamp=timestamp,
                            metric_name="disk_write_mb_per_sec",
                            value=disk_io.write_bytes / (1024 * 1024),
                            unit="mb/s",
                            component="system",
                        ),
                    ]
                )

            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                metrics.extend(
                    [
                        PerformanceMetric(
                            timestamp=timestamp,
                            metric_name="network_bytes_sent",
                            value=network_io.bytes_sent,
                            unit="bytes",
                            component="system",
                        ),
                        PerformanceMetric(
                            timestamp=timestamp,
                            metric_name="network_bytes_recv",
                            value=network_io.bytes_recv,
                            unit="bytes",
                            component="system",
                        ),
                    ]
                )

            # Process count
            process_count = len(psutil.pids())
            metrics.append(
                PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="process_count",
                    value=process_count,
                    unit="count",
                    component="system",
                )
            )

        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")

        return metrics


class ToolExecutionMetricsCollector:
    """Collects tool execution specific metrics"""

    def __init__(self):
        self.execution_times = defaultdict(list)
        self.execution_counts = defaultdict(int)
        self.error_counts = defaultdict(int)

    def record_execution(
        self,
        tool_name: str,
        execution_time: float,
        success: bool,
        context: Optional[dict[str, Any]] = None,
    ):
        """Record tool execution metrics"""
        self.execution_times[tool_name].append(execution_time)
        self.execution_counts[tool_name] += 1

        if not success:
            self.error_counts[tool_name] += 1

    async def collect(self) -> list[PerformanceMetric]:
        """Collect tool execution metrics"""
        timestamp = time.time()
        metrics = []

        for tool_name in self.execution_times:
            times = self.execution_times[tool_name]
            if not times:
                continue

            # Calculate statistics
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min(times)

            # Add metrics
            metrics.extend(
                [
                    PerformanceMetric(
                        timestamp=timestamp,
                        metric_name="avg_execution_time",
                        value=avg_time,
                        unit="seconds",
                        component=f"tool_{tool_name}",
                        context={"sample_size": len(times)},
                    ),
                    PerformanceMetric(
                        timestamp=timestamp,
                        metric_name="max_execution_time",
                        value=max_time,
                        unit="seconds",
                        component=f"tool_{tool_name}",
                    ),
                    PerformanceMetric(
                        timestamp=timestamp,
                        metric_name="execution_count",
                        value=self.execution_counts[tool_name],
                        unit="count",
                        component=f"tool_{tool_name}",
                    ),
                    PerformanceMetric(
                        timestamp=timestamp,
                        metric_name="error_count",
                        value=self.error_counts[tool_name],
                        unit="count",
                        component=f"tool_{tool_name}",
                    ),
                ]
            )

            # Calculate error rate
            error_rate = self.error_counts[tool_name] / self.execution_counts[tool_name]
            metrics.append(
                PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="error_rate",
                    value=error_rate,
                    unit="ratio",
                    component=f"tool_{tool_name}",
                )
            )

        return metrics


class PerformanceAnalyzer:
    """Analyzes performance metrics and identifies issues"""

    def __init__(self, alert_thresholds: Optional[dict[str, dict[str, float]]] = None):
        self.alert_thresholds = alert_thresholds or self._default_thresholds()
        self.active_alerts = {}

    def _default_thresholds(self) -> dict[str, dict[str, float]]:
        """Default performance alert thresholds"""
        return {
            "system": {
                "cpu_usage": {"warning": 80.0, "critical": 95.0},
                "memory_usage": {"warning": 85.0, "critical": 95.0},
                "disk_read_mb_per_sec": {"warning": 100.0, "critical": 500.0},
                "disk_write_mb_per_sec": {"warning": 100.0, "critical": 500.0},
            },
            "tool_execution": {
                "avg_execution_time": {"warning": 5.0, "critical": 10.0},
                "max_execution_time": {"warning": 30.0, "critical": 60.0},
                "error_rate": {"warning": 0.1, "critical": 0.25},
            },
        }

    def analyze_metrics(self, metrics: list[PerformanceMetric]) -> list[PerformanceAlert]:
        """Analyze metrics and generate alerts"""
        alerts = []

        for metric in metrics:
            alert = self._check_thresholds(metric)
            if alert:
                alerts.append(alert)
                self.active_alerts[alert.alert_id] = alert

        return alerts

    def _check_thresholds(self, metric: PerformanceMetric) -> Optional[PerformanceAlert]:
        """Check if metric exceeds thresholds"""
        component_thresholds = None

        if metric.component == "system":
            component_thresholds = self.alert_thresholds.get("system", {})
        elif metric.component.startswith("tool_"):
            component_thresholds = self.alert_thresholds.get("tool_execution", {})

        if not component_thresholds or metric.metric_name not in component_thresholds:
            return None

        thresholds = component_thresholds[metric.metric_name]

        # Check critical threshold
        if metric.value >= thresholds.get("critical", float("inf")):
            return PerformanceAlert(
                alert_id=f"{metric.component}_{metric.metric_name}_{int(metric.timestamp)}",
                severity="critical",
                message=f"Critical threshold exceeded for {metric.metric_name}",
                metric_name=metric.metric_name,
                threshold_value=thresholds["critical"],
                current_value=metric.value,
                component=metric.component,
                timestamp=metric.timestamp,
            )

        # Check warning threshold
        if metric.value >= thresholds.get("warning", float("inf")):
            return PerformanceAlert(
                alert_id=f"{metric.component}_{metric.metric_name}_{int(metric.timestamp)}",
                severity="warning",
                message=f"Warning threshold exceeded for {metric.metric_name}",
                metric_name=metric.metric_name,
                threshold_value=thresholds["warning"],
                current_value=metric.value,
                component=metric.component,
                timestamp=metric.timestamp,
            )

        return None

    def get_performance_summary(self, metrics: list[PerformanceMetric]) -> dict[str, Any]:
        """Generate performance summary from metrics"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(metrics),
            "components": set(m.component for m in metrics),
            "time_range": {},
            "component_summaries": {},
        }

        if metrics:
            timestamps = [m.timestamp for m in metrics]
            summary["time_range"] = {
                "start": datetime.fromtimestamp(min(timestamps)).isoformat(),
                "end": datetime.fromtimestamp(max(timestamps)).isoformat(),
                "duration_seconds": max(timestamps) - min(timestamps),
            }

        # Component-specific summaries
        by_component = defaultdict(list)
        for metric in metrics:
            by_component[metric.component].append(metric)

        for component, component_metrics in by_component.items():
            component_summary = {
                "metrics_count": len(component_metrics),
                "metric_types": list(set(m.metric_name for m in component_metrics)),
            }

            # Calculate averages for numeric metrics
            by_metric_name = defaultdict(list)
            for metric in component_metrics:
                by_metric_name[metric.metric_name].append(metric.value)

            averages = {}
            for metric_name, values in by_metric_name.items():
                if values:
                    averages[f"avg_{metric_name}"] = sum(values) / len(values)
                    averages[f"max_{metric_name}"] = max(values)
                    averages[f"min_{metric_name}"] = min(values)

            component_summary["averages"] = averages
            summary["component_summaries"][component] = component_summary

        return summary


class PerformanceOptimizer:
    """Provides performance optimization recommendations"""

    def __init__(self):
        self.optimization_rules = self._load_optimization_rules()

    def _load_optimization_rules(self) -> list[dict[str, Any]]:
        """Load performance optimization rules"""
        return [
            {
                "name": "high_cpu_usage",
                "condition": lambda metrics: any(m.metric_name == "cpu_usage" and m.value > 80 for m in metrics),
                "recommendation": "Consider reducing concurrent operations or optimizing CPU-intensive tasks",
                "priority": "high",
            },
            {
                "name": "high_memory_usage",
                "condition": lambda metrics: any(m.metric_name == "memory_usage" and m.value > 85 for m in metrics),
                "recommendation": "Implement memory management strategies, clear caches, or increase available memory",
                "priority": "high",
            },
            {
                "name": "slow_tool_execution",
                "condition": lambda metrics: any(
                    m.metric_name == "avg_execution_time" and m.value > 5.0 for m in metrics
                ),
                "recommendation": "Optimize slow tool implementations, consider caching, or implement parallel execution",
                "priority": "medium",
            },
            {
                "name": "high_error_rate",
                "condition": lambda metrics: any(m.metric_name == "error_rate" and m.value > 0.15 for m in metrics),
                "recommendation": "Investigate error causes, improve error handling, and enhance validation",
                "priority": "high",
            },
            {
                "name": "excessive_disk_io",
                "condition": lambda metrics: any(
                    m.metric_name in ["disk_read_mb_per_sec", "disk_write_mb_per_sec"] and m.value > 100
                    for m in metrics
                ),
                "recommendation": "Optimize file operations, implement caching, or consider using faster storage",
                "priority": "medium",
            },
        ]

    def generate_recommendations(self, metrics: list[PerformanceMetric]) -> list[dict[str, Any]]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []

        for rule in self.optimization_rules:
            try:
                if rule["condition"](metrics):
                    recommendations.append(
                        {
                            "name": rule["name"],
                            "recommendation": rule["recommendation"],
                            "priority": rule["priority"],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except Exception as e:
                logger.error(f"Error evaluating optimization rule {rule['name']}: {e}")

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

        return recommendations


class PerformanceMonitor:
    """
    🔍 Main Performance Monitor

    Coordinates performance collection, analysis, and optimization
    for the LUKHAS AI tool execution system.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Components
        self.collector = PerformanceCollector(collection_interval=self.config.get("collection_interval", 1.0))
        self.analyzer = PerformanceAnalyzer(alert_thresholds=self.config.get("alert_thresholds"))
        self.optimizer = PerformanceOptimizer()

        # State
        self.monitoring = False
        self.last_analysis = None
        self.performance_history = deque(maxlen=1000)

        # Export configuration
        self.export_directory = Path(self.config.get("export_directory", "data/performance"))
        self.export_directory.mkdir(parents=True, exist_ok=True)

        logger.info("Performance Monitor initialized")

    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring:
            logger.warning("Performance monitoring already active")
            return

        self.monitoring = True
        logger.info("Performance monitoring started")

        # Start collection task
        collection_task = asyncio.create_task(self.collector.start_collection())

        # Start analysis task
        analysis_task = asyncio.create_task(self._analysis_loop())

        try:
            await asyncio.gather(collection_task, analysis_task)
        except asyncio.CancelledError:
            logger.info("Performance monitoring cancelled")
        finally:
            self.monitoring = False

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        self.collector.stop_collection()
        logger.info("Performance monitoring stopped")

    async def _analysis_loop(self):
        """Continuous performance analysis loop"""
        analysis_interval = self.config.get("analysis_interval", 30)  # 30 seconds

        while self.monitoring:
            try:
                # Get recent metrics
                metrics = self.collector.get_recent_metrics(time_window=300)  # 5 minutes

                if metrics:
                    # Analyze metrics
                    alerts = self.analyzer.analyze_metrics(metrics)

                    # Generate summary
                    summary = self.analyzer.get_performance_summary(metrics)

                    # Generate recommendations
                    recommendations = self.optimizer.generate_recommendations(metrics)

                    # Create analysis result
                    analysis_result = {
                        "timestamp": datetime.now().isoformat(),
                        "metrics_analyzed": len(metrics),
                        "alerts": [asdict(alert) for alert in alerts],
                        "summary": summary,
                        "recommendations": recommendations,
                        "health_score": self._calculate_health_score(metrics, alerts),
                    }

                    self.last_analysis = analysis_result
                    self.performance_history.append(analysis_result)

                    # Log significant alerts
                    critical_alerts = [a for a in alerts if a.severity == "critical"]
                    if critical_alerts:
                        logger.critical(f"Performance critical alerts: {len(critical_alerts)}")

                    warning_alerts = [a for a in alerts if a.severity == "warning"]
                    if warning_alerts:
                        logger.warning(f"Performance warning alerts: {len(warning_alerts)}")

                await asyncio.sleep(analysis_interval)

            except Exception as e:
                logger.error(f"Performance analysis error: {e}")
                await asyncio.sleep(10)

    def _calculate_health_score(self, metrics: list[PerformanceMetric], alerts: list[PerformanceAlert]) -> float:
        """Calculate overall system health score (0.0 to 1.0)"""
        if not metrics:
            return 0.5  # Neutral score with no data

        base_score = 1.0

        # Penalize based on alerts
        for alert in alerts:
            if alert.severity == "critical":
                base_score -= 0.3
            elif alert.severity == "warning":
                base_score -= 0.1

        # Penalize based on high resource usage
        cpu_metrics = [m for m in metrics if m.metric_name == "cpu_usage"]
        if cpu_metrics:
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 90:
                base_score -= 0.2
            elif avg_cpu > 80:
                base_score -= 0.1

        memory_metrics = [m for m in metrics if m.metric_name == "memory_usage"]
        if memory_metrics:
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
            if avg_memory > 90:
                base_score -= 0.2
            elif avg_memory > 80:
                base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def get_current_status(self) -> dict[str, Any]:
        """Get current monitoring status"""
        status = {
            "monitoring_active": self.monitoring,
            "last_analysis": self.last_analysis,
            "metrics_buffer_size": len(self.collector.metrics_buffer),
            "active_alerts": len(self.analyzer.active_alerts),
            "history_size": len(self.performance_history),
        }

        if self.last_analysis:
            status["health_score"] = self.last_analysis.get("health_score", 0.5)
            status["critical_alerts"] = len(
                [a for a in self.last_analysis.get("alerts", []) if a.get("severity") == "critical"]
            )
            status["recommendations_count"] = len(self.last_analysis.get("recommendations", []))

        return status

    async def export_performance_report(self, time_range: Optional[int] = None) -> str:
        """Export comprehensive performance report"""
        time_range = time_range or 3600  # Default 1 hour

        # Get metrics for time range
        metrics = self.collector.get_recent_metrics(time_window=time_range)

        # Generate comprehensive report
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "time_range_seconds": time_range,
            "metrics_count": len(metrics),
            "summary": self.analyzer.get_performance_summary(metrics),
            "alerts": [asdict(a) for a in self.analyzer.analyze_metrics(metrics)],
            "recommendations": self.optimizer.generate_recommendations(metrics),
            "health_score": self._calculate_health_score(metrics, self.analyzer.analyze_metrics(metrics)),
            "monitoring_config": self.config,
            "raw_metrics": [asdict(m) for m in metrics[-1000:]],  # Last 1000 metrics
        }

        # Export to file
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.export_directory / f"performance_report_{timestamp_str}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Performance report exported to {report_file}")
        return str(report_file)


# Global monitor instance
_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor(config: Optional[dict[str, Any]] = None) -> PerformanceMonitor:
    """Get or create the global performance monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor(config)
    return _monitor


# Integration function for tool executors
def record_tool_execution(
    tool_name: str, execution_time: float, success: bool, context: Optional[dict[str, Any]] = None
):
    """Record tool execution metrics (convenience function)"""
    monitor = get_performance_monitor()
    monitor.collector.tool_collector.record_execution(tool_name, execution_time, success, context)
