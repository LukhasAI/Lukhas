"""
Health Check System for LUKHAS Orchestrators
Provides comprehensive health monitoring and status reporting
"""
import asyncio
import contextlib
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional, Union

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status for a component"""

    component_name: str
    status: HealthStatus
    message: str = ""
    last_check: datetime = field(default_factory=datetime.now)
    response_time_ms: float = 0.0
    error_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "response_time_ms": self.response_time_ms,
            "error_count": self.error_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComponentHealth":
        """Create from dictionary"""
        return cls(
            component_name=data["component_name"],
            status=HealthStatus(data["status"]),
            message=data.get("message", ""),
            last_check=datetime.fromisoformat(data["last_check"]),
            response_time_ms=data.get("response_time_ms", 0.0),
            error_count=data.get("error_count", 0),
            metadata=data.get("metadata", {}),
        )


class HealthCheck:
    """Individual health check definition"""

    def __init__(
        self,
        name: str,
        check_function: Callable[[], Union[bool, dict[str, Any]]],
        interval_seconds: int = 30,
        timeout_seconds: int = 10,
        critical: bool = False,
    ):
        self.name = name
        self.check_function = check_function
        self.interval_seconds = interval_seconds
        self.timeout_seconds = timeout_seconds
        self.critical = critical
        self.last_run = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3

    async def run_check(self) -> ComponentHealth:
        """Run the health check and return status"""
        start_time = time.time()

        try:
            # Run check with timeout
            result = await asyncio.wait_for(self._run_check_async(), timeout=self.timeout_seconds)

            response_time_ms = (time.time() - start_time) * 1000

            if isinstance(result, bool):
                if result:
                    status = HealthStatus.HEALTHY
                    message = f"{self.name} check passed"
                    self.consecutive_failures = 0
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"{self.name} check failed"
                    self.consecutive_failures += 1
                metadata = {}

            elif isinstance(result, dict):
                # Detailed result
                status_value = result.get("status", "healthy")
                status = HealthStatus(status_value.lower())
                message = result.get("message", f"{self.name} check completed")
                metadata = result.get("metadata", {})

                if status == HealthStatus.HEALTHY:
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1

            else:
                # Unexpected result type
                status = HealthStatus.UNKNOWN
                message = f"{self.name} returned unexpected result type: {type(result)}"
                metadata = {"result": str(result)}
                self.consecutive_failures += 1

            # Escalate status based on consecutive failures
            if self.consecutive_failures >= self.max_consecutive_failures:
                if self.critical:
                    status = HealthStatus.CRITICAL
                    message += f" (critical component failed {self.consecutive_failures} times)"
                elif status == HealthStatus.UNHEALTHY:
                    message += f" (failed {self.consecutive_failures} consecutive times)"

            self.last_run = datetime.now(timezone.utc)

            return ComponentHealth(
                component_name=self.name,
                status=status,
                message=message,
                last_check=self.last_run,
                response_time_ms=response_time_ms,
                error_count=self.consecutive_failures,
                metadata=metadata,
            )

        except asyncio.TimeoutError:
            response_time_ms = self.timeout_seconds * 1000
            self.consecutive_failures += 1

            return ComponentHealth(
                component_name=self.name,
                status=(HealthStatus.CRITICAL if self.critical else HealthStatus.UNHEALTHY),
                message=f"{self.name} check timed out after {self.timeout_seconds}s",
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time_ms,
                error_count=self.consecutive_failures,
                metadata={"timeout": True},
            )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self.consecutive_failures += 1

            return ComponentHealth(
                component_name=self.name,
                status=(HealthStatus.CRITICAL if self.critical else HealthStatus.UNHEALTHY),
                message=f"{self.name} check failed: {e!s}",
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time_ms,
                error_count=self.consecutive_failures,
                metadata={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc(),
                },
            )

    async def _run_check_async(self):
        """Run the check function asynchronously"""
        if asyncio.iscoroutinefunction(self.check_function):
            return await self.check_function()
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.check_function)

    def should_run(self) -> bool:
        """Check if this health check should run now"""
        if self.last_run is None:
            return True

        next_run = self.last_run + timedelta(seconds=self.interval_seconds)
        return datetime.now(timezone.utc) >= next_run


class HealthChecker:
    """Main health checker that manages multiple health checks"""

    def __init__(self):
        self.health_checks: dict[str, HealthCheck] = {}
        self.health_status: dict[str, ComponentHealth] = {}
        self.running = False
        self.check_task: Optional[asyncio.Task] = None
        self.check_interval = 10  # How often to check if individual checks should run

    def register_check(
        self,
        name: str,
        check_function: Callable[[], Union[bool, dict[str, Any]]],
        interval_seconds: int = 30,
        timeout_seconds: int = 10,
        critical: bool = False,
    ) -> None:
        """Register a new health check"""
        self.health_checks[name] = HealthCheck(
            name=name,
            check_function=check_function,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            critical=critical,
        )
        logger.info(f"Registered health check: {name}")

    def unregister_check(self, name: str) -> None:
        """Remove a health check"""
        if name in self.health_checks:
            del self.health_checks[name]
            if name in self.health_status:
                del self.health_status[name]
            logger.info(f"Unregistered health check: {name}")

    async def run_check(self, name: str) -> Optional[ComponentHealth]:
        """Run a specific health check"""
        if name not in self.health_checks:
            logger.warning(f"Health check '{name}' not found")
            return None

        health_check = self.health_checks[name]
        result = await health_check.run_check()
        self.health_status[name] = result
        return result

    async def run_all_checks(self) -> dict[str, ComponentHealth]:
        """Run all health checks"""
        results = {}

        # Run checks concurrently
        tasks = []
        for name, health_check in self.health_checks.items():
            task = asyncio.create_task(health_check.run_check())
            tasks.append((name, task))

        # Wait for all checks to complete
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
                self.health_status[name] = result
            except Exception as e:
                logger.error(f"Health check '{name}' failed with exception: {e}")
                error_result = ComponentHealth(
                    component_name=name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check execution failed: {e!s}",
                    last_check=datetime.now(timezone.utc),
                    error_count=1,
                    metadata={"error": str(e)},
                )
                results[name] = error_result
                self.health_status[name] = error_result

        return results

    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self.running:
            logger.warning("Health monitoring is already running")
            return

        self.running = True
        self.check_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started health monitoring")

    async def stop_monitoring(self) -> None:
        """Stop continuous health monitoring"""
        if not self.running:
            return

        self.running = False
        if self.check_task:
            self.check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.check_task

        logger.info("Stopped health monitoring")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                # Check which health checks should run
                checks_to_run = []
                for name, health_check in self.health_checks.items():
                    if health_check.should_run():
                        checks_to_run.append(name)

                # Run due checks concurrently
                if checks_to_run:
                    tasks = []
                    for name in checks_to_run:
                        task = asyncio.create_task(self.run_check(name))
                        tasks.append(task)

                    # Wait for all to complete
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Sleep until next check cycle
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    def get_overall_health(self) -> dict[str, Any]:
        """Get overall system health status"""
        if not self.health_status:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks have been run",
                "component_count": 0,
                "healthy_count": 0,
                "degraded_count": 0,
                "unhealthy_count": 0,
                "critical_count": 0,
                "unknown_count": 0,
                "last_check": None,
            }

        # Count statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0,
            HealthStatus.UNKNOWN: 0,
        }

        latest_check = None
        total_response_time = 0.0

        for health in self.health_status.values():
            status_counts[health.status] += 1
            total_response_time += health.response_time_ms

            if latest_check is None or health.last_check > latest_check:
                latest_check = health.last_check

        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_status = HealthStatus.CRITICAL
            message = f"{status_counts[HealthStatus.CRITICAL]} critical component(s)"
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
            message = f"{status_counts[HealthStatus.UNHEALTHY]} unhealthy component(s)"
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
            message = f"{status_counts[HealthStatus.DEGRADED]} degraded component(s)"
        elif status_counts[HealthStatus.UNKNOWN] > 0:
            overall_status = HealthStatus.UNKNOWN
            message = f"{status_counts[HealthStatus.UNKNOWN]} unknown component(s)"
        else:
            overall_status = HealthStatus.HEALTHY
            message = "All components healthy"

        avg_response_time = total_response_time / len(self.health_status) if self.health_status else 0.0

        return {
            "status": overall_status.value,
            "message": message,
            "component_count": len(self.health_status),
            "healthy_count": status_counts[HealthStatus.HEALTHY],
            "degraded_count": status_counts[HealthStatus.DEGRADED],
            "unhealthy_count": status_counts[HealthStatus.UNHEALTHY],
            "critical_count": status_counts[HealthStatus.CRITICAL],
            "unknown_count": status_counts[HealthStatus.UNKNOWN],
            "avg_response_time_ms": avg_response_time,
            "last_check": latest_check.isoformat() if latest_check else None,
        }

    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Get health status for a specific component"""
        return self.health_status.get(component_name)

    def get_all_health_status(self) -> dict[str, ComponentHealth]:
        """Get health status for all components"""
        return self.health_status.copy()

    def export_health_report(self) -> dict[str, Any]:
        """Export complete health report"""
        return {
            "overall_health": self.get_overall_health(),
            "components": {name: health.to_dict() for name, health in self.health_status.items()},
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "monitoring_active": self.running,
        }


# Pre-defined health checks for orchestrators


def create_orchestrator_health_checks(health_checker: HealthChecker) -> None:
    """Create standard health checks for orchestrators"""

    # Basic system health

    def memory_check() -> dict[str, Any]:
        """Check memory usage"""
        import psutil

        memory = psutil.virtual_memory()
        percent_used = memory.percent

        if percent_used > 90:
            return {
                "status": "critical",
                "message": f"Memory usage critical: {percent_used:.1f}%",
                "metadata": {"memory_percent": percent_used},
            }
        elif percent_used > 80:
            return {
                "status": "degraded",
                "message": f"Memory usage high: {percent_used:.1f}%",
                "metadata": {"memory_percent": percent_used},
            }
        else:
            return {
                "status": "healthy",
                "message": f"Memory usage normal: {percent_used:.1f}%",
                "metadata": {"memory_percent": percent_used},
            }

    def cpu_check() -> dict[str, Any]:
        """Check CPU usage"""
        import psutil

        cpu_percent = psutil.cpu_percent(interval=1)

        if cpu_percent > 95:
            return {
                "status": "critical",
                "message": f"CPU usage critical: {cpu_percent:.1f}%",
                "metadata": {"cpu_percent": cpu_percent},
            }
        elif cpu_percent > 85:
            return {
                "status": "degraded",
                "message": f"CPU usage high: {cpu_percent:.1f}%",
                "metadata": {"cpu_percent": cpu_percent},
            }
        else:
            return {
                "status": "healthy",
                "message": f"CPU usage normal: {cpu_percent:.1f}%",
                "metadata": {"cpu_percent": cpu_percent},
            }

    def disk_check() -> dict[str, Any]:
        """Check disk usage"""
        import psutil

        disk = psutil.disk_usage("/")
        percent_used = (disk.used / disk.total) * 100

        if percent_used > 95:
            return {
                "status": "critical",
                "message": f"Disk usage critical: {percent_used:.1f}%",
                "metadata": {"disk_percent": percent_used},
            }
        elif percent_used > 85:
            return {
                "status": "degraded",
                "message": f"Disk usage high: {percent_used:.1f}%",
                "metadata": {"disk_percent": percent_used},
            }
        else:
            return {
                "status": "healthy",
                "message": f"Disk usage normal: {percent_used:.1f}%",
                "metadata": {"disk_percent": percent_used},
            }

    # Register health checks
    try:
        health_checker.register_check("memory", memory_check, interval_seconds=30, critical=True)
        health_checker.register_check("cpu", cpu_check, interval_seconds=30, critical=False)
        health_checker.register_check("disk", disk_check, interval_seconds=60, critical=True)
    except ImportError:
        logger.warning("psutil not available, skipping system health checks")


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    global _health_checker

    if _health_checker is None:
        _health_checker = HealthChecker()
        # Set up default health checks
        create_orchestrator_health_checks(_health_checker)

    return _health_checker