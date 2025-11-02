"""
T4/0.01% Excellence Multi-Dimensional Health Monitoring

Comprehensive health checking for LUKHAS deployment system with
multi-factor analysis and predictive failure detection.

Performance targets:
- Health check: <10ms overhead
- Detection latency: <30s for failures
- False positive rate: <1%
"""

import asyncio
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional

from core.logging import get_logger
from observability.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class HealthDimension(Enum):
    """Health check dimensions"""

    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"
    DEPENDENCIES = "dependencies"
    BUSINESS_METRICS = "business_metrics"


@dataclass
class HealthMetric:
    """Individual health metric"""

    name: str
    dimension: HealthDimension
    value: float
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Get metric status based on thresholds"""
        if self.dimension in [HealthDimension.ERROR_RATE, HealthDimension.LATENCY]:
            # Higher is worse
            if self.value >= self.threshold_critical:
                return "critical"
            elif self.value >= self.threshold_warning:
                return "warning"
            else:
                return "healthy"
        else:
            # Lower is worse
            if self.value <= self.threshold_critical:
                return "critical"
            elif self.value <= self.threshold_warning:
                return "warning"
            else:
                return "healthy"

    @property
    def health_score(self) -> float:
        """Calculate health score (0-1) based on thresholds"""
        if self.dimension in [HealthDimension.ERROR_RATE, HealthDimension.LATENCY]:
            # Inverse scoring
            if self.value >= self.threshold_critical:
                return 0.0
            elif self.value >= self.threshold_warning:
                # Linear interpolation between warning and critical
                range_size = self.threshold_critical - self.threshold_warning
                if range_size == 0:
                    return 0.5
                position = (self.value - self.threshold_warning) / range_size
                return 0.5 * (1 - position)
            else:
                # Linear interpolation up to warning
                if self.threshold_warning == 0:
                    return 1.0
                return 1.0 - (self.value / self.threshold_warning) * 0.5
        else:
            # Normal scoring
            if self.value <= self.threshold_critical:
                return 0.0
            elif self.value <= self.threshold_warning:
                range_size = self.threshold_warning - self.threshold_critical
                if range_size == 0:
                    return 0.5
                position = (self.value - self.threshold_critical) / range_size
                return 0.5 * position
            else:
                return 1.0


@dataclass
class HealthCheck:
    """Health check configuration"""

    check_id: str
    name: str
    check_function: Callable
    dimension: HealthDimension
    interval_seconds: int = 30
    timeout_seconds: int = 10
    enabled: bool = True
    critical_for_deployment: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentHealth:
    """Overall component health status"""

    component_id: str
    overall_status: str  # healthy, degraded, unhealthy
    overall_score: float  # 0-1
    metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    consecutive_failures: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_metric(self, metric: HealthMetric):
        """Update individual metric and recalculate overall health"""
        self.metrics[metric.name] = metric
        self._recalculate_health()

    def _recalculate_health(self):
        """Recalculate overall health based on all metrics"""
        if not self.metrics:
            self.overall_status = "unknown"
            self.overall_score = 0.5
            return

        # Calculate weighted average score
        total_score = 0.0
        critical_count = 0
        warning_count = 0

        for metric in self.metrics.values():
            total_score += metric.health_score
            if metric.status == "critical":
                critical_count += 1
            elif metric.status == "warning":
                warning_count += 1

        avg_score = total_score / len(self.metrics)

        # Determine overall status
        if critical_count > 0:
            self.overall_status = "unhealthy"
            # Penalize score for critical metrics
            self.overall_score = min(0.3, avg_score)
        elif warning_count > len(self.metrics) / 2:
            self.overall_status = "degraded"
            self.overall_score = min(0.7, avg_score)
        else:
            self.overall_status = "healthy"
            self.overall_score = avg_score

        self.last_check = datetime.now(timezone.utc)


class HealthMonitor:
    """
    Multi-dimensional health monitoring system for LUKHAS deployment.

    Provides comprehensive health checking with predictive failure detection
    and automated alerting.
    """

    def __init__(self, enable_predictive: bool = True, history_window_size: int = 100):
        self.enable_predictive = enable_predictive
        self.history_window_size = history_window_size

        # Health checks registry
        self.health_checks: Dict[str, HealthCheck] = {}
        self.component_health: Dict[str, ComponentHealth] = {}

        # Metric history for trend analysis
        self.metric_history: Dict[str, Deque[HealthMetric]] = defaultdict(lambda: deque(maxlen=history_window_size))

        # Check scheduling
        self.check_tasks: Dict[str, asyncio.Task] = {}

        # Alerting
        self.alert_handlers: List[Callable] = []
        self.alert_history: Deque[Dict[str, Any]] = deque(maxlen=1000)

        # Statistics
        self.stats = {"total_checks": 0, "failed_checks": 0, "alerts_triggered": 0, "predictions_made": 0}

        logger.info(
            "Health monitor initialized", predictive_enabled=enable_predictive, history_window=history_window_size
        )

    def register_health_check(self, health_check: HealthCheck):
        """Register a health check"""
        self.health_checks[health_check.check_id] = health_check

        logger.debug("Health check registered", check_id=health_check.check_id, dimension=health_check.dimension.value)

    def unregister_health_check(self, check_id: str):
        """Unregister a health check"""
        if check_id in self.health_checks:
            # Cancel running task
            if check_id in self.check_tasks:
                self.check_tasks[check_id].cancel()
                del self.check_tasks[check_id]

            del self.health_checks[check_id]
            logger.debug("Health check unregistered", check_id=check_id)

    async def start_monitoring(self, component_id: str):
        """Start health monitoring for a component"""
        if component_id not in self.component_health:
            self.component_health[component_id] = ComponentHealth(
                component_id=component_id, overall_status="unknown", overall_score=0.5
            )

        # Start check tasks
        for check_id, health_check in self.health_checks.items():
            if check_id not in self.check_tasks:
                task = asyncio.create_task(self._run_health_check_loop(component_id, health_check))
                self.check_tasks[check_id] = task

        logger.info("Health monitoring started", component_id=component_id)

    async def stop_monitoring(self, component_id: str):
        """Stop health monitoring for a component"""
        # Cancel all check tasks
        for task in self.check_tasks.values():
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.check_tasks.values(), return_exceptions=True)

        self.check_tasks.clear()

        logger.info("Health monitoring stopped", component_id=component_id)

    async def _run_health_check_loop(self, component_id: str, health_check: HealthCheck):
        """Run health check loop for a specific check"""
        while True:
            try:
                await asyncio.sleep(health_check.interval_seconds)

                if not health_check.enabled:
                    continue

                # Execute health check
                start_time = time.perf_counter()

                try:
                    result = await asyncio.wait_for(
                        health_check.check_function(component_id), timeout=health_check.timeout_seconds
                    )

                    duration_ms = (time.perf_counter() - start_time) * 1000

                    # Parse result
                    if isinstance(result, dict):
                        value = result.get("value", 0.0)
                        metadata = result.get("metadata", {})
                    else:
                        value = float(result)
                        metadata = {}

                    # Create metric
                    metric = HealthMetric(
                        name=health_check.name,
                        dimension=health_check.dimension,
                        value=value,
                        threshold_warning=metadata.get(
                            "threshold_warning", self._get_default_threshold(health_check.dimension, "warning")
                        ),
                        threshold_critical=metadata.get(
                            "threshold_critical", self._get_default_threshold(health_check.dimension, "critical")
                        ),
                        metadata=metadata,
                    )

                    # Update component health
                    self.component_health[component_id].update_metric(metric)
                    self.component_health[component_id].consecutive_failures = 0

                    # Store in history
                    history_key = f"{component_id}:{health_check.name}"
                    self.metric_history[history_key].append(metric)

                    # Check for alerts
                    await self._check_alerts(component_id, metric)

                    # Predictive analysis
                    if self.enable_predictive:
                        await self._analyze_trends(component_id, health_check.name)

                    # Update statistics
                    self.stats["total_checks"] += 1

                    # Record metrics
                    metrics.record_histogram(
                        "health_check_duration_ms",
                        duration_ms,
                        tags={"component": component_id, "dimension": health_check.dimension.value},
                    )

                except asyncio.TimeoutError:
                    logger.warning("Health check timeout", component_id=component_id, check_id=health_check.check_id)
                    self.component_health[component_id].consecutive_failures += 1
                    self.stats["failed_checks"] += 1

                except Exception as e:
                    logger.error(
                        "Health check error", component_id=component_id, check_id=health_check.check_id, error=str(e)
                    )
                    self.component_health[component_id].consecutive_failures += 1
                    self.stats["failed_checks"] += 1

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check loop error", component_id=component_id, error=str(e))
                await asyncio.sleep(10)

    def _get_default_threshold(self, dimension: HealthDimension, level: str) -> float:
        """Get default threshold for dimension"""
        defaults = {
            HealthDimension.AVAILABILITY: {"warning": 0.95, "critical": 0.90},
            HealthDimension.LATENCY: {"warning": 500, "critical": 1000},  # ms
            HealthDimension.ERROR_RATE: {"warning": 0.01, "critical": 0.05},
            HealthDimension.THROUGHPUT: {"warning": 100, "critical": 50},  # requests/s
            HealthDimension.RESOURCE_USAGE: {"warning": 0.80, "critical": 0.95},
        }

        return defaults.get(dimension, {}).get(level, 0.5)

    async def _check_alerts(self, component_id: str, metric: HealthMetric):
        """Check if metric should trigger alert"""
        if metric.status in ["critical", "warning"]:
            alert = {
                "timestamp": datetime.now(timezone.utc),
                "component_id": component_id,
                "metric_name": metric.name,
                "dimension": metric.dimension.value,
                "status": metric.status,
                "value": metric.value,
                "threshold": metric.threshold_critical if metric.status == "critical" else metric.threshold_warning,
            }

            self.alert_history.append(alert)
            self.stats["alerts_triggered"] += 1

            # Notify handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error("Alert handler error", handler=handler.__name__, error=str(e))

            logger.warning(
                "Health alert triggered",
                component_id=component_id,
                metric=metric.name,
                status=metric.status,
                value=metric.value,
            )

    async def _analyze_trends(self, component_id: str, metric_name: str):
        """Analyze metric trends for predictive failure detection"""
        history_key = f"{component_id}:{metric_name}"
        history = list(self.metric_history[history_key])

        if len(history) < 10:
            return  # Not enough data

        # Extract values
        values = [m.value for m in history]
        timestamps = [(m.timestamp - history[0].timestamp).total_seconds() for m in history]

        # Calculate trend using linear regression
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)

        # Slope calculation
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Predict future value
        prediction_horizon = 300  # 5 minutes ahead
        timestamps[-1]
        predicted_value = values[-1] + slope * prediction_horizon

        # Check if prediction crosses threshold
        latest_metric = history[-1]
        dimension = latest_metric.dimension

        if dimension in [HealthDimension.ERROR_RATE, HealthDimension.LATENCY]:
            # Higher is worse
            if predicted_value > latest_metric.threshold_critical * 0.9:
                logger.warning(
                    "Predictive alert: metric trending toward critical",
                    component_id=component_id,
                    metric=metric_name,
                    current_value=values[-1],
                    predicted_value=predicted_value,
                    threshold=latest_metric.threshold_critical,
                )
                self.stats["predictions_made"] += 1
        else:
            # Lower is worse
            if predicted_value < latest_metric.threshold_critical * 1.1:
                logger.warning(
                    "Predictive alert: metric trending toward critical",
                    component_id=component_id,
                    metric=metric_name,
                    current_value=values[-1],
                    predicted_value=predicted_value,
                    threshold=latest_metric.threshold_critical,
                )
                self.stats["predictions_made"] += 1

    def register_alert_handler(self, handler: Callable):
        """Register alert notification handler"""
        self.alert_handlers.append(handler)

    async def get_component_health(self, component_id: str) -> Optional[ComponentHealth]:
        """Get current health status for component"""
        return self.component_health.get(component_id)

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        healthy_count = sum(1 for h in self.component_health.values() if h.overall_status == "healthy")
        degraded_count = sum(1 for h in self.component_health.values() if h.overall_status == "degraded")
        unhealthy_count = sum(1 for h in self.component_health.values() if h.overall_status == "unhealthy")

        return {
            "total_components": len(self.component_health),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "average_health_score": (
                statistics.mean([h.overall_score for h in self.component_health.values()])
                if self.component_health
                else 0.0
            ),
            "recent_alerts": len(
                [a for a in self.alert_history if (datetime.now(timezone.utc) - a["timestamp"]).seconds < 3600]
            ),
            "statistics": self.stats,
        }

    def get_metric_history(self, component_id: str, metric_name: str) -> List[HealthMetric]:
        """Get historical metrics for analysis"""
        history_key = f"{component_id}:{metric_name}"
        return list(self.metric_history[history_key])
