#!/usr/bin/env python3
"""
LUKHAS Advanced Monitoring & Resilience Integration Hub

Central integration point for telemetry, circuit breakers, health monitoring,
and auto-healing systems across the LUKHAS platform.

# ΛTAG: monitoring_integration, resilience_hub, observability_orchestration
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Optional

from resilience.circuit_breaker import (
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
)

from resilience.circuit_breaker import (
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
)

from resilience.circuit_breaker import (
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
)

from monitoring.health_system import (
    HealthMonitoringSystem,
    RestartServiceAction,
    ServiceHealthChecker,
    SystemResourceChecker,
)

# Import monitoring components
from observability.telemetry_system import SeverityLevel, TelemetryCollector

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for integrated monitoring system."""

    # Telemetry settings
    telemetry_flush_interval: float = 30.0
    max_events: int = 10000
    max_metrics: int = 50000

    # Circuit breaker settings
    default_failure_threshold: int = 5
    default_recovery_timeout: float = 30.0
    enable_adaptive_thresholds: bool = True

    # Health monitoring settings
    health_check_interval: float = 30.0
    enable_predictive_analysis: bool = True
    enable_auto_healing: bool = True

    # Integration settings
    cross_system_correlation: bool = True
    dashboard_update_interval: float = 5.0


class LUKHASMonitoringHub:
    """
    Central hub for LUKHAS monitoring and resilience systems.

    Integrates telemetry, circuit breakers, health monitoring, and auto-healing
    into a unified observability platform.
    """

    def __init__(self, config: Optional[MonitoringConfig] = None):
        """
        Initialize monitoring hub.

        Args:
            config: Monitoring configuration
        """

        self.config = config or MonitoringConfig()

        # Initialize core systems
        self.telemetry = TelemetryCollector(
            max_events=self.config.max_events,
            max_metrics=self.config.max_metrics,
            flush_interval_sec=self.config.telemetry_flush_interval
        )

        self.circuit_breaker_registry = CircuitBreakerRegistry()

        self.health_monitor = HealthMonitoringSystem(
            check_interval_sec=self.config.health_check_interval,
            enable_predictive_analysis=self.config.enable_predictive_analysis,
            enable_auto_healing=self.config.enable_auto_healing
        )

        # State tracking
        self.is_running = False
        self.background_tasks: list[asyncio.Task] = []

        # Integration components
        self.component_correlations: dict[str, set[str]] = {}
        self.cross_system_events: list[dict[str, Any]] = []

        # Dashboard state
        self.dashboard_state: dict[str, Any] = {}
        self.last_dashboard_update = 0.0

        # Setup initial integrations
        self._setup_integrations()

    def _setup_integrations(self) -> None:
        """Setup cross-system integrations."""

        # Register system resource health checker
        system_checker = SystemResourceChecker("lukhas_system")
        self.health_monitor.register_health_checker("system_resources", system_checker)

        # Setup telemetry event subscribers for correlation
        self.telemetry.event_subscribers.append(self._correlate_telemetry_event)
        self.telemetry.metric_subscribers.append(self._correlate_telemetry_metric)

        logger.info("LUKHAS monitoring integrations initialized")

    def register_service_monitoring(self,
                                  service_name: str,
                                  health_check_func: callable,
                                  circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
                                  restart_command: Optional[str] = None) -> None:
        """
        Register comprehensive monitoring for a service.

        Args:
            service_name: Name of the service
            health_check_func: Function to check service health
            circuit_breaker_config: Circuit breaker configuration
            restart_command: Command to restart service for auto-healing
        """

        # Register health checker
        health_checker = ServiceHealthChecker(service_name, health_check_func)
        self.health_monitor.register_health_checker(service_name, health_checker)

        # Register circuit breaker
        cb_config = circuit_breaker_config or CircuitBreakerConfig(
            failure_threshold=self.config.default_failure_threshold,
            recovery_timeout_sec=self.config.default_recovery_timeout,
            adaptive_thresholds=self.config.enable_adaptive_thresholds
        )
        self.circuit_breaker_registry.register(service_name, cb_config)

        # Register auto-healing action if restart command provided
        if restart_command and self.config.enable_auto_healing:
            restart_action = RestartServiceAction(service_name, restart_command)
            self.health_monitor.register_healing_action(restart_action)

        # Setup correlation
        self.component_correlations[service_name] = {
            "health_monitor", "circuit_breaker", "telemetry"
        }

        self.telemetry.emit_event(
            component="monitoring_hub",
            event_type="service_registered",
            message=f"Comprehensive monitoring registered for {service_name}",
            data={
                "service_name": service_name,
                "has_circuit_breaker": True,
                "has_health_check": True,
                "has_auto_healing": restart_command is not None
            }
        )

        logger.info(f"Registered comprehensive monitoring for service: {service_name}")

    def _correlate_telemetry_event(self, event) -> None:
        """Correlate telemetry events across systems."""

        if not self.config.cross_system_correlation:
            return

        # Check for patterns that indicate system-wide issues
        if event.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL]:
            # Cross-system error correlation
            correlation_event = {
                "timestamp": event.timestamp,
                "type": "error_correlation",
                "component": event.component,
                "event": event.to_dict(),
                "correlated_systems": []
            }

            # Check circuit breaker states for this component
            cb = self.circuit_breaker_registry.get(event.component)
            if cb:
                correlation_event["correlated_systems"].append({
                    "system": "circuit_breaker",
                    "component": event.component,
                    "state": cb.state.value,
                    "failure_rate": cb.stats.current_failure_rate
                })

            # Check health status
            if event.component in self.health_monitor.component_health:
                health = self.health_monitor.component_health[event.component]
                correlation_event["correlated_systems"].append({
                    "system": "health_monitor",
                    "component": event.component,
                    "status": health.status.value,
                    "last_check": health.last_check
                })

            self.cross_system_events.append(correlation_event)

            # Limit correlation history
            if len(self.cross_system_events) > 1000:
                self.cross_system_events = self.cross_system_events[-500:]

    def _correlate_telemetry_metric(self, metric) -> None:
        """Correlate telemetry metrics across systems."""

        if not self.config.cross_system_correlation:
            return

        # Track metrics that might indicate system stress
        stress_metrics = ["cpu_usage", "memory_usage", "response_time", "error_rate"]

        if any(stress_metric in metric.metric_name.lower() for stress_metric in stress_metrics):  # TODO[T4-ISSUE]: {"code":"SIM102","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Nested if statements - can be collapsed with 'and' operator","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_monitoring_integration_hub_py_L223"}
            # Check if this metric indicates potential issues
            if ((metric.metric_name in ["cpu_usage", "memory_usage"] and metric.value > 80) or
                (metric.metric_name == "response_time" and metric.value > 1000) or
                (metric.metric_name == "error_rate" and metric.value > 0.1)):

                # Emit correlation warning
                self.telemetry.emit_event(
                    component="monitoring_hub",
                    event_type="performance_correlation",
                    message=f"Performance degradation detected: {metric.metric_name}={metric.value}",
                    severity=SeverityLevel.WARNING,
                    data={
                        "metric": metric.to_dict(),
                        "threshold_exceeded": True
                    }
                )

    @asynccontextmanager
    async def monitor_operation(self,
                               operation_name: str,
                               component: str,
                               use_circuit_breaker: bool = True):
        """
        Context manager for comprehensive operation monitoring.

        Args:
            operation_name: Name of the operation
            component: Component performing the operation
            use_circuit_breaker: Whether to use circuit breaker protection
        """

        # Start telemetry trace
        async with self.telemetry.trace_operation(operation_name, component) as span:
            try:
                # Add circuit breaker protection if requested
                if use_circuit_breaker:
                    cb = self.circuit_breaker_registry.get(component)
                    if cb:
                        async with cb.protect(operation_name):
                            yield span
                    else:
                        # No circuit breaker registered, just trace
                        yield span
                else:
                    yield span

                # Record success metric
                self.telemetry.emit_metric(
                    component=component,
                    metric_name=f"{operation_name}_success",
                    value=1.0
                )

            except Exception as e:
                # Record failure
                span.set_error(str(e))

                self.telemetry.emit_event(
                    component=component,
                    event_type="operation_failed",
                    message=f"Operation {operation_name} failed: {e}",
                    severity=SeverityLevel.ERROR,
                    data={
                        "operation": operation_name,
                        "error": str(e),
                        "error_type": type(e).__name__
                    },
                    trace_id=span.trace_id,
                    span_id=span.span_id
                )

                self.telemetry.emit_metric(
                    component=component,
                    metric_name=f"{operation_name}_failure",
                    value=1.0
                )

                raise

    async def get_unified_dashboard_data(self) -> dict[str, Any]:
        """Get unified dashboard data from all monitoring systems."""

        current_time = time.time()

        # Update dashboard cache if needed
        if (current_time - self.last_dashboard_update) > self.config.dashboard_update_interval:
            await self._update_dashboard_cache()
            self.last_dashboard_update = current_time

        return self.dashboard_state

    async def _update_dashboard_cache(self) -> None:
        """Update dashboard data cache."""

        try:
            # Get data from all systems
            telemetry_overview = self.telemetry.get_system_overview()
            health_overview = await self.health_monitor.get_system_overview()
            circuit_breaker_stats = self.circuit_breaker_registry.get_all_stats()

            # Combine into unified dashboard
            self.dashboard_state = {
                "timestamp": time.time(),
                "overall_status": self._calculate_overall_status(
                    telemetry_overview, health_overview, circuit_breaker_stats
                ),
                "telemetry": telemetry_overview,
                "health": health_overview,
                "circuit_breakers": circuit_breaker_stats,
                "correlations": {
                    "cross_system_events": self.cross_system_events[-50:],  # Last 50 events
                    "component_correlations": dict(self.component_correlations)
                },
                "performance_summary": self._generate_performance_summary()
            }

        except Exception as e:
            logger.error(f"Error updating dashboard cache: {e}")
            self.dashboard_state["error"] = str(e)

    def _calculate_overall_status(self,
                                telemetry_overview: dict[str, Any],
                                health_overview: dict[str, Any],
                                circuit_breaker_stats: dict[str, Any]) -> str:
        """Calculate overall system status from all monitoring data."""

        # Health system status weights the most
        health_status = health_overview.get("overall_status", "unknown")
        health_score = health_overview.get("overall_health_score", 0.5)

        # Circuit breaker status
        open_circuits = sum(
            1 for stats in circuit_breaker_stats.values()
            if stats["state"] == "open"
        )

        # Telemetry system health
        telemetry_health = telemetry_overview.get("overall_health", 0.5)

        # Calculate combined score
        combined_score = (health_score * 0.6) + (telemetry_health * 0.3) + ((1.0 - min(open_circuits / max(len(circuit_breaker_stats), 1), 1.0)) * 0.1)

        # Determine status
        if combined_score >= 0.9 and health_status == "healthy":
            return "healthy"
        elif combined_score >= 0.7:
            return "degraded"
        elif combined_score >= 0.4:
            return "unhealthy"
        else:
            return "critical"

    def _generate_performance_summary(self) -> dict[str, Any]:
        """Generate performance summary across all systems."""

        # Get recent metrics from telemetry
        recent_metrics = list(self.telemetry.metrics)[-100:]  # Last 100 metrics

        if not recent_metrics:
            return {"status": "no_data"}

        # Analyze response times
        response_times = [
            m.value for m in recent_metrics
            if "response_time" in m.metric_name.lower()
        ]

        # Analyze error rates
        error_metrics = [
            m.value for m in recent_metrics
            if "error" in m.metric_name.lower() or "failure" in m.metric_name.lower()
        ]

        summary = {
            "total_metrics": len(recent_metrics),
            "response_time_analysis": {},
            "error_analysis": {},
            "resource_utilization": {}
        }

        if response_times:
            import statistics
            summary["response_time_analysis"] = {
                "count": len(response_times),
                "average": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "max": max(response_times),
                "min": min(response_times)
            }

        if error_metrics:
            summary["error_analysis"] = {
                "count": len(error_metrics),
                "total_errors": sum(error_metrics),
                "average_error_rate": sum(error_metrics) / len(error_metrics) if error_metrics else 0
            }

        return summary

    async def start(self) -> None:
        """Start all monitoring systems."""

        if self.is_running:
            logger.warning("Monitoring hub already running")
            return

        try:
            # Start telemetry system
            await self.telemetry.start_background_processing()

            # Start health monitoring
            await self.health_monitor.start_monitoring()

            # Start circuit breaker health monitoring
            await self.circuit_breaker_registry.start_health_monitoring()

            # Start dashboard update task
            dashboard_task = asyncio.create_task(self._dashboard_update_loop())
            self.background_tasks.append(dashboard_task)

            self.is_running = True

            self.telemetry.emit_event(
                component="monitoring_hub",
                event_type="system_started",
                message="LUKHAS monitoring hub started successfully",
                severity=SeverityLevel.INFO
            )

            logger.info("LUKHAS monitoring hub started successfully")

        except Exception as e:
            logger.error(f"Error starting monitoring hub: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop all monitoring systems."""

        if not self.is_running:
            return

        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()

            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)

            self.background_tasks.clear()

            # Stop monitoring systems
            await self.telemetry.stop_background_processing()
            await self.health_monitor.stop_monitoring()
            await self.circuit_breaker_registry.stop_health_monitoring()

            self.is_running = False

            logger.info("LUKHAS monitoring hub stopped")

        except Exception as e:
            logger.error(f"Error stopping monitoring hub: {e}")

    async def _dashboard_update_loop(self) -> None:
        """Background loop for updating dashboard data."""

        while True:
            try:
                await asyncio.sleep(self.config.dashboard_update_interval)
                await self._update_dashboard_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dashboard update loop error: {e}")
                await asyncio.sleep(10)


# Global monitoring hub instance
_global_monitoring_hub: Optional[LUKHASMonitoringHub] = None


def get_monitoring_hub() -> LUKHASMonitoringHub:
    """Get global monitoring hub instance."""
    global _global_monitoring_hub

    if _global_monitoring_hub is None:
        _global_monitoring_hub = LUKHASMonitoringHub()

    return _global_monitoring_hub


# Convenience functions
async def monitor_operation(operation_name: str,
                          component: str,
                          use_circuit_breaker: bool = True):
    """Convenience function for operation monitoring."""
    return get_monitoring_hub().monitor_operation(
        operation_name, component, use_circuit_breaker
    )


def register_service(service_name: str,
                    health_check_func: callable,
                    circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
                    restart_command: Optional[str] = None) -> None:
    """Convenience function for service registration."""
    get_monitoring_hub().register_service_monitoring(
        service_name, health_check_func, circuit_breaker_config, restart_command
    )


if __name__ == "__main__":
    # Example usage
    async def demo_monitoring_hub():

        # Create monitoring hub
        hub = LUKHASMonitoringHub()

        # Register a demo service
        async def demo_health_check():
            return {"status": "ok", "uptime": time.time()}

        hub.register_service_monitoring(
            service_name="demo_service",
            health_check_func=demo_health_check,
            restart_command="echo 'Restarting demo service'"
        )

        # Start monitoring
        await hub.start()

        try:
            # Simulate some operations
            for i in range(5):
                async with hub.monitor_operation("demo_operation", "demo_service"):
                    await asyncio.sleep(0.1)
                    if i == 3:
                        # Simulate an error
                        raise Exception("Simulated error")
        except Exception:
            pass  # Expected

        # Get dashboard data
        dashboard = await hub.get_unified_dashboard_data()
        print(f"Overall status: {dashboard['overall_status']}")
        print(f"Components monitored: {len(dashboard['telemetry']['components'])}")

        # Stop monitoring
        await hub.stop()

    asyncio.run(demo_monitoring_hub())
