#!/usr/bin/env python3
"""
LUKHAS Advanced Health Monitoring & Auto-Healing System

Enterprise-grade health monitoring with predictive failure detection,
automated recovery, and comprehensive system diagnostics.

# ΛTAG: health_monitoring, auto_healing, predictive_analytics, system_diagnostics
"""

import asyncio
import json
import logging
import statistics
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of system components."""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    API = "api"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    MEMORY = "memory"
    CPU = "cpu"
    CUSTOM = "custom"


@dataclass
class HealthMetric:
    """Individual health metric."""

    name: str
    value: float
    unit: str
    timestamp: float
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    is_higher_better: bool = True  # True if higher values are better

    def get_status(self) -> HealthStatus:
        """Determine status based on thresholds."""

        if self.threshold_critical is None and self.threshold_warning is None:
            return HealthStatus.HEALTHY

        if self.is_higher_better:
            # Higher is better (e.g., CPU idle, memory available)
            if self.threshold_critical is not None and self.value <= self.threshold_critical:
                return HealthStatus.CRITICAL
            elif self.threshold_warning is not None and self.value <= self.threshold_warning:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
        else:
            # Lower is better (e.g., response time, error rate)
            if self.threshold_critical is not None and self.value >= self.threshold_critical:
                return HealthStatus.CRITICAL
            elif self.threshold_warning is not None and self.value >= self.threshold_warning:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY


@dataclass
class ComponentHealth:
    """Health status of a system component."""

    component_name: str
    component_type: ComponentType
    status: HealthStatus
    metrics: Dict[str, HealthMetric]
    last_check: float
    error_message: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_name": self.component_name,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp,
                    "status": metric.get_status().value
                }
                for name, metric in self.metrics.items()
            },
            "last_check": self.last_check,
            "error_message": self.error_message,
            "recovery_suggestions": self.recovery_suggestions,
            "dependencies": self.dependencies
        }


class HealthChecker(ABC):
    """Abstract base class for health checkers."""

    @abstractmethod
    async def check_health(self) -> ComponentHealth:
        """Perform health check and return component health."""
        pass


class SystemResourceChecker(HealthChecker):
    """Health checker for system resources (CPU, memory, disk)."""

    def __init__(self, component_name: str = "system_resources"):
        self.component_name = component_name

    async def check_health(self) -> ComponentHealth:
        """Check system resource health."""

        metrics = {}
        current_time = time.time()

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage"] = HealthMetric(
                name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=current_time,
                threshold_warning=80.0,
                threshold_critical=95.0,
                is_higher_better=False
            )

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = HealthMetric(
                name="memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=current_time,
                threshold_warning=80.0,
                threshold_critical=95.0,
                is_higher_better=False
            )

            metrics["memory_available"] = HealthMetric(
                name="memory_available",
                value=memory.available / (1024**3),  # GB
                unit="GB",
                timestamp=current_time,
                threshold_warning=2.0,
                threshold_critical=0.5,
                is_higher_better=True
            )

            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics["disk_usage"] = HealthMetric(
                name="disk_usage",
                value=disk.percent,
                unit="percent",
                timestamp=current_time,
                threshold_warning=85.0,
                threshold_critical=95.0,
                is_higher_better=False
            )

            # Load average (Unix-like systems)
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()[0]  # 1-minute load average
                cpu_count = psutil.cpu_count()
                load_percent = (load_avg / cpu_count) * 100

                metrics["load_average"] = HealthMetric(
                    name="load_average",
                    value=load_percent,
                    unit="percent",
                    timestamp=current_time,
                    threshold_warning=80.0,
                    threshold_critical=100.0,
                    is_higher_better=False
                )

            # Determine overall status
            statuses = [metric.get_status() for metric in metrics.values()]
            if HealthStatus.CRITICAL in statuses:
                overall_status = HealthStatus.CRITICAL
            elif HealthStatus.DEGRADED in statuses:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY

            # Generate recovery suggestions
            recovery_suggestions = []
            if metrics["cpu_usage"].get_status() != HealthStatus.HEALTHY:
                recovery_suggestions.append("Consider scaling CPU resources or optimizing CPU-intensive processes")
            if metrics["memory_usage"].get_status() != HealthStatus.HEALTHY:
                recovery_suggestions.append("Consider increasing memory or optimizing memory usage")
            if metrics["disk_usage"].get_status() != HealthStatus.HEALTHY:
                recovery_suggestions.append("Clean up disk space or add additional storage")

            return ComponentHealth(
                component_name=self.component_name,
                component_type=ComponentType.CPU,
                status=overall_status,
                metrics=metrics,
                last_check=current_time,
                recovery_suggestions=recovery_suggestions
            )

        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                component_type=ComponentType.CPU,
                status=HealthStatus.UNKNOWN,
                metrics={},
                last_check=current_time,
                error_message=str(e),
                recovery_suggestions=["Check system resource monitoring configuration"]
            )


class ServiceHealthChecker(HealthChecker):
    """Health checker for services/applications."""

    def __init__(self,
                 component_name: str,
                 health_check_func: Callable[[], Any],
                 component_type: ComponentType = ComponentType.SERVICE):
        self.component_name = component_name
        self.health_check_func = health_check_func
        self.component_type = component_type
        self.response_times = deque(maxlen=100)

    async def check_health(self) -> ComponentHealth:
        """Check service health."""

        current_time = time.time()
        start_time = current_time

        try:
            # Call health check function
            if asyncio.iscoroutinefunction(self.health_check_func):
                result = await self.health_check_func()
            else:
                result = self.health_check_func()

            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # ms
            self.response_times.append(response_time)

            # Create metrics
            metrics = {
                "response_time": HealthMetric(
                    name="response_time",
                    value=response_time,
                    unit="ms",
                    timestamp=current_time,
                    threshold_warning=1000.0,  # 1 second
                    threshold_critical=5000.0,  # 5 seconds
                    is_higher_better=False
                ),
                "availability": HealthMetric(
                    name="availability",
                    value=1.0,  # Available since check succeeded
                    unit="ratio",
                    timestamp=current_time,
                    is_higher_better=True
                )
            }

            # Add average response time if we have history
            if len(self.response_times) > 1:
                avg_response_time = statistics.mean(self.response_times)
                metrics["avg_response_time"] = HealthMetric(
                    name="avg_response_time",
                    value=avg_response_time,
                    unit="ms",
                    timestamp=current_time,
                    threshold_warning=500.0,
                    threshold_critical=2000.0,
                    is_higher_better=False
                )

            # Determine status
            statuses = [metric.get_status() for metric in metrics.values()]
            if HealthStatus.CRITICAL in statuses:
                overall_status = HealthStatus.CRITICAL
            elif HealthStatus.DEGRADED in statuses:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY

            return ComponentHealth(
                component_name=self.component_name,
                component_type=self.component_type,
                status=overall_status,
                metrics=metrics,
                last_check=current_time
            )

        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                component_type=self.component_type,
                status=HealthStatus.UNHEALTHY,
                metrics={
                    "availability": HealthMetric(
                        name="availability",
                        value=0.0,
                        unit="ratio",
                        timestamp=current_time,
                        is_higher_better=True
                    )
                },
                last_check=current_time,
                error_message=str(e),
                recovery_suggestions=[
                    "Check service configuration",
                    "Verify service dependencies",
                    "Review service logs for errors"
                ]
            )


class PredictiveAnalyzer:
    """Analyzes health trends for predictive failure detection."""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metric_history: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=history_size))
        )

    def add_health_data(self, component_health: ComponentHealth) -> None:
        """Add health data to history for analysis."""

        component_key = f"{component_health.component_name}.{component_health.component_type.value}"

        for metric_name, metric in component_health.metrics.items():
            self.metric_history[component_key][metric_name].append({
                "timestamp": metric.timestamp,
                "value": metric.value,
                "status": metric.get_status().value
            })

    def predict_failure_risk(self,
                           component_name: str,
                           component_type: ComponentType,
                           metric_name: str,
                           prediction_window_minutes: float = 30.0) -> Tuple[float, List[str]]:
        """
        Predict failure risk for a specific metric.
        
        Returns:
            Tuple of (risk_score, risk_factors) where risk_score is 0-1
        """

        component_key = f"{component_name}.{component_type.value}"

        if (component_key not in self.metric_history or
            metric_name not in self.metric_history[component_key]):
            return 0.0, ["Insufficient historical data"]

        history = list(self.metric_history[component_key][metric_name])

        if len(history) < 10:
            return 0.0, ["Insufficient historical data"]

        # Analyze trends
        risk_factors = []
        risk_score = 0.0

        # Get recent values (last 10 data points)
        recent_values = [point["value"] for point in history[-10:]]
        older_values = [point["value"] for point in history[-20:-10]] if len(history) >= 20 else []

        # Trend analysis
        if len(recent_values) >= 5:
            # Calculate trend (slope)
            x = list(range(len(recent_values)))
            y = recent_values

            # Simple linear regression
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))

            if n * sum_x2 - sum_x ** 2 != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

                # Analyze slope based on metric type
                # For metrics where higher is better, negative slope is bad
                # For metrics where lower is better, positive slope is bad
                latest_point = history[-1]
                if latest_point["status"] in ["degraded", "critical"]:
                    risk_score += 0.3
                    risk_factors.append(f"Current {metric_name} status is {latest_point['status']}")

                # Trend analysis
                if abs(slope) > statistics.stdev(recent_values) * 0.1:  # Significant trend
                    if slope > 0:
                        risk_factors.append(f"{metric_name} is trending upward")
                        risk_score += 0.2
                    else:
                        risk_factors.append(f"{metric_name} is trending downward")
                        risk_score += 0.2

        # Volatility analysis
        if len(recent_values) >= 5:
            recent_std = statistics.stdev(recent_values)
            recent_mean = statistics.mean(recent_values)

            if recent_mean > 0:
                coefficient_of_variation = recent_std / recent_mean

                if coefficient_of_variation > 0.3:  # High volatility
                    risk_score += 0.2
                    risk_factors.append(f"{metric_name} showing high volatility")

        # Compare recent vs older performance
        if older_values:
            recent_mean = statistics.mean(recent_values)
            older_mean = statistics.mean(older_values)

            if older_mean > 0:
                performance_change = (recent_mean - older_mean) / older_mean

                if abs(performance_change) > 0.2:  # 20% change
                    risk_score += 0.15
                    direction = "degraded" if performance_change > 0 else "improved"
                    risk_factors.append(f"{metric_name} performance has {direction} by {abs(performance_change):.1%}")

        # Threshold proximity analysis
        latest_point = history[-1]
        if "threshold_warning" in latest_point or "threshold_critical" in latest_point:
            # This would require passing threshold information to history
            # For now, we'll use status as a proxy
            status_scores = {
                "healthy": 0.0,
                "degraded": 0.4,
                "unhealthy": 0.7,
                "critical": 0.9
            }

            status_risk = status_scores.get(latest_point["status"], 0.0)
            risk_score += status_risk

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        if not risk_factors:
            risk_factors = ["No significant risk factors detected"]

        return risk_score, risk_factors


class AutoHealingAction(ABC):
    """Abstract base class for auto-healing actions."""

    @abstractmethod
    async def execute(self, component_health: ComponentHealth) -> bool:
        """
        Execute healing action.
        
        Returns:
            True if action was successful, False otherwise
        """
        pass

    @abstractmethod
    def can_handle(self, component_health: ComponentHealth) -> bool:
        """
        Check if this action can handle the given component health issue.
        
        Returns:
            True if this action can help with the issue
        """
        pass


class RestartServiceAction(AutoHealingAction):
    """Auto-healing action to restart a service."""

    def __init__(self,
                 service_name: str,
                 restart_command: str,
                 max_restarts_per_hour: int = 3):
        self.service_name = service_name
        self.restart_command = restart_command
        self.max_restarts_per_hour = max_restarts_per_hour
        self.restart_history = deque(maxlen=max_restarts_per_hour)

    def can_handle(self, component_health: ComponentHealth) -> bool:
        """Check if can restart this service."""

        # Check if this is the right service
        if component_health.component_name != self.service_name:
            return False

        # Check if service is unhealthy
        if component_health.status not in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            return False

        # Check restart rate limits
        current_time = time.time()
        recent_restarts = [
            t for t in self.restart_history
            if current_time - t < 3600  # Last hour
        ]

        return len(recent_restarts) < self.max_restarts_per_hour

    async def execute(self, component_health: ComponentHealth) -> bool:
        """Execute service restart."""

        try:
            logger.info(f"Attempting to restart service: {self.service_name}")

            # Execute restart command
            process = await asyncio.create_subprocess_shell(
                self.restart_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Successfully restarted service: {self.service_name}")
                self.restart_history.append(time.time())
                return True
            else:
                logger.error(f"Failed to restart service {self.service_name}: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error restarting service {self.service_name}: {e}")
            return False


class HealthMonitoringSystem:
    """Comprehensive health monitoring system."""

    def __init__(self,
                 check_interval_sec: float = 30.0,
                 enable_predictive_analysis: bool = True,
                 enable_auto_healing: bool = True):
        """
        Initialize health monitoring system.
        
        Args:
            check_interval_sec: Interval between health checks
            enable_predictive_analysis: Enable predictive failure detection
            enable_auto_healing: Enable automatic healing actions
        """

        self.check_interval_sec = check_interval_sec
        self.enable_predictive_analysis = enable_predictive_analysis
        self.enable_auto_healing = enable_auto_healing

        # Component management
        self.health_checkers: Dict[str, HealthChecker] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        self.health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Predictive analysis
        if enable_predictive_analysis:
            self.predictive_analyzer = PredictiveAnalyzer()
        else:
            self.predictive_analyzer = None

        # Auto-healing
        self.healing_actions: List[AutoHealingAction] = []
        self.healing_history: deque = deque(maxlen=100)

        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.predictive_task: Optional[asyncio.Task] = None

        # Telemetry integration
        try:
            from observability.telemetry_system import get_telemetry
            self.telemetry = get_telemetry()
        except ImportError:
            self.telemetry = None

    def register_health_checker(self, name: str, checker: HealthChecker) -> None:
        """Register a health checker."""
        self.health_checkers[name] = checker

    def register_healing_action(self, action: AutoHealingAction) -> None:
        """Register an auto-healing action."""
        self.healing_actions.append(action)

    async def check_all_health(self) -> Dict[str, ComponentHealth]:
        """Check health of all registered components."""

        health_results = {}

        # Run all health checks concurrently
        tasks = {
            name: checker.check_health()
            for name, checker in self.health_checkers.items()
        }

        if tasks:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            for name, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Health check failed for {name}: {result}")
                    # Create error health status
                    health_results[name] = ComponentHealth(
                        component_name=name,
                        component_type=ComponentType.CUSTOM,
                        status=HealthStatus.UNKNOWN,
                        metrics={},
                        last_check=time.time(),
                        error_message=str(result)
                    )
                else:
                    health_results[name] = result

        # Update stored health data
        self.component_health.update(health_results)

        # Add to history
        for name, health in health_results.items():
            self.health_history[name].append({
                "timestamp": health.last_check,
                "status": health.status.value,
                "health_data": health.to_dict()
            })

        # Update predictive analyzer
        if self.predictive_analyzer:
            for health in health_results.values():
                self.predictive_analyzer.add_health_data(health)

        # Emit telemetry
        if self.telemetry:
            for name, health in health_results.items():
                self.telemetry.emit_event(
                    component="health_monitor",
                    event_type="health_check",
                    message=f"Health check completed for {name}",
                    data={
                        "component": name,
                        "status": health.status.value,
                        "metric_count": len(health.metrics)
                    }
                )

                # Emit metrics
                for metric_name, metric in health.metrics.items():
                    self.telemetry.emit_metric(
                        component=f"health.{name}",
                        metric_name=metric_name,
                        value=metric.value
                    )

        return health_results

    async def trigger_auto_healing(self, component_health: ComponentHealth) -> bool:
        """Trigger auto-healing for a component if needed."""

        if not self.enable_auto_healing:
            return False

        if component_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
            return False  # No healing needed

        # Find applicable healing actions
        applicable_actions = [
            action for action in self.healing_actions
            if action.can_handle(component_health)
        ]

        if not applicable_actions:
            logger.warning(f"No healing actions available for {component_health.component_name}")
            return False

        # Try healing actions
        for action in applicable_actions:
            try:
                logger.info(f"Attempting healing action for {component_health.component_name}")

                success = await action.execute(component_health)

                # Record healing attempt
                healing_record = {
                    "timestamp": time.time(),
                    "component": component_health.component_name,
                    "action": action.__class__.__name__,
                    "success": success,
                    "component_status": component_health.status.value
                }
                self.healing_history.append(healing_record)

                if self.telemetry:
                    self.telemetry.emit_event(
                        component="auto_healing",
                        event_type="healing_attempt",
                        message=f"Auto-healing attempted for {component_health.component_name}",
                        data=healing_record
                    )

                if success:
                    logger.info(f"Auto-healing successful for {component_health.component_name}")
                    return True

            except Exception as e:
                logger.error(f"Auto-healing action failed for {component_health.component_name}: {e}")

        return False

    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system health overview."""

        # Get current health status
        current_health = await self.check_all_health()

        # Calculate overall system health
        if current_health:
            status_scores = {
                HealthStatus.HEALTHY: 1.0,
                HealthStatus.DEGRADED: 0.7,
                HealthStatus.UNHEALTHY: 0.3,
                HealthStatus.CRITICAL: 0.0,
                HealthStatus.UNKNOWN: 0.5
            }

            total_score = sum(status_scores[health.status] for health in current_health.values())
            overall_health_score = total_score / len(current_health)

            if overall_health_score >= 0.9:
                overall_status = HealthStatus.HEALTHY
            elif overall_health_score >= 0.7:
                overall_status = HealthStatus.DEGRADED
            elif overall_health_score >= 0.3:
                overall_status = HealthStatus.UNHEALTHY
            else:
                overall_status = HealthStatus.CRITICAL
        else:
            overall_health_score = 0.0
            overall_status = HealthStatus.UNKNOWN

        # Component summary
        component_summary = {
            name: health.to_dict()
            for name, health in current_health.items()
        }

        # Predictive analysis
        risk_analysis = {}
        if self.predictive_analyzer:
            for name, health in current_health.items():
                component_risks = {}
                for metric_name in health.metrics:
                    risk_score, risk_factors = self.predictive_analyzer.predict_failure_risk(
                        health.component_name,
                        health.component_type,
                        metric_name
                    )
                    component_risks[metric_name] = {
                        "risk_score": risk_score,
                        "risk_factors": risk_factors
                    }
                risk_analysis[name] = component_risks

        # Recent healing activity
        recent_healing = list(self.healing_history)[-10:]  # Last 10 healing attempts

        return {
            "timestamp": time.time(),
            "overall_health_score": overall_health_score,
            "overall_status": overall_status.value,
            "component_count": len(current_health),
            "healthy_components": sum(1 for h in current_health.values() if h.status == HealthStatus.HEALTHY),
            "degraded_components": sum(1 for h in current_health.values() if h.status == HealthStatus.DEGRADED),
            "unhealthy_components": sum(1 for h in current_health.values() if h.status == HealthStatus.UNHEALTHY),
            "critical_components": sum(1 for h in current_health.values() if h.status == HealthStatus.CRITICAL),
            "components": component_summary,
            "risk_analysis": risk_analysis,
            "recent_healing": recent_healing,
            "monitoring_config": {
                "check_interval_sec": self.check_interval_sec,
                "predictive_analysis_enabled": self.enable_predictive_analysis,
                "auto_healing_enabled": self.enable_auto_healing,
                "registered_checkers": len(self.health_checkers),
                "registered_healing_actions": len(self.healing_actions)
            }
        }

    async def start_monitoring(self) -> None:
        """Start background health monitoring."""

        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        if self.enable_predictive_analysis and self.predictive_task is None:
            self.predictive_task = asyncio.create_task(self._predictive_monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop background health monitoring."""

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

        if self.predictive_task:
            self.predictive_task.cancel()
            try:
                await self.predictive_task
            except asyncio.CancelledError:
                pass
            self.predictive_task = None

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""

        while True:
            try:
                # Check all component health
                health_results = await self.check_all_health()

                # Trigger auto-healing for unhealthy components
                if self.enable_auto_healing:
                    healing_tasks = [
                        self.trigger_auto_healing(health)
                        for health in health_results.values()
                        if health.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]
                    ]

                    if healing_tasks:
                        await asyncio.gather(*healing_tasks, return_exceptions=True)

                await asyncio.sleep(self.check_interval_sec)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(10)  # Brief pause on error

    async def _predictive_monitoring_loop(self) -> None:
        """Background predictive monitoring loop."""

        while True:
            try:
                # Run predictive analysis every 5 minutes
                await asyncio.sleep(300)

                if not self.predictive_analyzer or not self.component_health:
                    continue

                # Analyze each component for failure risk
                high_risk_components = []

                for name, health in self.component_health.items():
                    for metric_name in health.metrics:
                        risk_score, risk_factors = self.predictive_analyzer.predict_failure_risk(
                            health.component_name,
                            health.component_type,
                            metric_name
                        )

                        if risk_score > 0.7:  # High risk threshold
                            high_risk_components.append({
                                "component": name,
                                "metric": metric_name,
                                "risk_score": risk_score,
                                "risk_factors": risk_factors
                            })

                # Emit alerts for high-risk components
                if high_risk_components and self.telemetry:
                    for risk_info in high_risk_components:
                        self.telemetry.emit_event(
                            component="predictive_analysis",
                            event_type="high_failure_risk",
                            message=f"High failure risk detected for {risk_info['component']}.{risk_info['metric']}",
                            data=risk_info,
                            severity=self.telemetry.SeverityLevel.WARNING if hasattr(self.telemetry, 'SeverityLevel') else None
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Predictive monitoring loop error: {e}")


if __name__ == "__main__":
    # Example usage
    async def demo_health_monitoring():

        # Create health monitoring system
        health_monitor = HealthMonitoringSystem(
            check_interval_sec=10.0,
            enable_predictive_analysis=True,
            enable_auto_healing=True
        )

        # Register system resource checker
        system_checker = SystemResourceChecker()
        health_monitor.register_health_checker("system", system_checker)

        # Register a dummy service checker
        async def dummy_service_check():
            # Simulate service check
            await asyncio.sleep(0.1)
            if time.time() % 30 < 5:  # Fail every 30 seconds for 5 seconds
                raise Exception("Service temporarily unavailable")
            return {"status": "ok"}

        service_checker = ServiceHealthChecker("demo_service", dummy_service_check)
        health_monitor.register_health_checker("demo_service", service_checker)

        # Start monitoring
        await health_monitor.start_monitoring()

        # Let it run for a while
        await asyncio.sleep(60)

        # Get final overview
        overview = await health_monitor.get_system_overview()
        print(json.dumps(overview, indent=2, default=str))

        # Stop monitoring
        await health_monitor.stop_monitoring()

    asyncio.run(demo_health_monitoring())
