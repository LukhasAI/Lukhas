#!/usr/bin/env python3
"""
LUKHAS Enterprise Health Check System
Comprehensive health monitoring with subsystem checks and alerts
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

import aiohttp
import psutil

# from prometheus_client import Counter, Gauge, Histogram, generate_latest
import redis.asyncio as redis
import structlog

# import asyncpg  # External dependency

# Configure structured logging
logger = structlog.get_logger()


class HealthStatus(str, Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """Types of components to check"""

    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    QUEUE = "queue"
    STORAGE = "storage"
    SERVICE = "service"
    LUKHAS_MODULE = "lukhas_module"


@dataclass
class HealthCheckResult:
    """Result of a health check"""

    component: str
    component_type: ComponentType
    status: HealthStatus
    latency_ms: float
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "component": self.component,
            "type": self.component_type.value,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 2),
            "message": self.message,
            "metadata": self.metadata,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class HealthThresholds:
    """Configurable health thresholds"""

    response_time_warn_ms: float = 1000.0
    response_time_critical_ms: float = 5000.0
    cpu_usage_warn_percent: float = 80.0
    cpu_usage_critical_percent: float = 95.0
    memory_usage_warn_percent: float = 85.0
    memory_usage_critical_percent: float = 95.0
    disk_usage_warn_percent: float = 80.0
    disk_usage_critical_percent: float = 90.0
    error_rate_warn_percent: float = 5.0
    error_rate_critical_percent: float = 10.0


class HealthCheckSystem:
    """
    Comprehensive health check system with:
    - Multiple component type support
    - Async health checks
    - Prometheus metrics
    - Alerting capabilities
    - Historical tracking
    - Dependency mapping
    """

    def __init__(
        self,
        config: Optional[dict[str, Any]] = None,
        thresholds: Optional[HealthThresholds] = None,
    ):
        self.config = config or {}
        self.thresholds = thresholds or HealthThresholds()

        # Component checks registry
        self.checks: dict[str, Callable] = {}
        self.check_metadata: dict[str, dict[str, Any]] = {}

        # Results cache
        self.latest_results: dict[str, HealthCheckResult] = {}
        self.check_history: list[dict[str, Any]] = []
        self.max_history = 1000

        # Metrics
        self._init_metrics()

        # Register default checks
        self._register_default_checks()

        # Alert callbacks
        self.alert_callbacks: list[Callable] = []

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.health_check_duration = Histogram(
            "health_check_duration_seconds",
            "Health check duration",
            ["component", "type"],
        )

        self.health_status_gauge = Gauge(
            "health_status",
            "Health status (1=healthy, 0.5=degraded, 0=unhealthy)",
            ["component", "type"],
        )

        self.health_check_total = Counter(
            "health_check_total",
            "Total health checks performed",
            ["component", "type", "status"],
        )

    def _register_default_checks(self):
        """Register default health checks"""
        # System checks
        self.register_check(
            "system_cpu",
            ComponentType.SERVICE,
            self._check_cpu_usage,
            {"threshold_warn": self.thresholds.cpu_usage_warn_percent},
        )

        self.register_check(
            "system_memory",
            ComponentType.SERVICE,
            self._check_memory_usage,
            {"threshold_warn": self.thresholds.memory_usage_warn_percent},
        )

        self.register_check(
            "system_disk",
            ComponentType.SERVICE,
            self._check_disk_usage,
            {"threshold_warn": self.thresholds.disk_usage_warn_percent},
        )

    def register_check(
        self,
        name: str,
        component_type: ComponentType,
        check_func: Callable,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Register a health check"""
        self.checks[name] = check_func
        self.check_metadata[name] = {"type": component_type, "metadata": metadata or {}

    async def check_all(self) -> dict[str, Any]:
        """Run all registered health checks"""
        start_time = datetime.now(timezone.utc)
        results = []

        # Run all checks concurrently
        check_tasks = []
        for name, check_func in self.checks.items():
            check_tasks.append(self._run_check(name, check_func))

        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)

        # Process results
        overall_status = HealthStatus.HEALTHY
        component_statuses = {}

        for i, (name, _) in enumerate(self.checks.items()):
            result = check_results[i]

            if isinstance(result, Exception):
                # Check failed
                result = HealthCheckResult(
                    component=name,
                    component_type=self.check_metadata[name]["type"],
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=0,
                    message=f"Check failed: {result!s}",
                )

            results.append(result)
            self.latest_results[name] = result

            # Update metrics
            self._update_metrics(result)

            # Update overall status
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED

            # Group by component type
            comp_type = result.component_type.value
            if comp_type not in component_statuses:
                component_statuses[comp_type] = []
            component_statuses[comp_type].append(result.to_dict())

        # Check for alerts
        await self._check_alerts(results)

        # Build response
        response = {
            "status": overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
            "checks_total": len(results),
            "checks_healthy": sum(1 for r in results if r.status == HealthStatus.HEALTHY),
            "checks_degraded": sum(1 for r in results if r.status == HealthStatus.DEGRADED),
            "checks_unhealthy": sum(1 for r in results if r.status == HealthStatus.UNHEALTHY),
            "components": component_statuses,
            "system_info": await self._get_system_info(),
        }

        # Add to history
        self._add_to_history(response)

        return response

    async def _run_check(self, name: str, check_func: Callable) -> HealthCheckResult:
        """Run individual health check"""
        start = datetime.now(timezone.utc)

        try:
            # Run the check
            result = await check_func()

            # Ensure it's a HealthCheckResult
            if not isinstance(result, HealthCheckResult):
                result = HealthCheckResult(
                    component=name,
                    component_type=self.check_metadata[name]["type"],
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    latency_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                )
            else:
                # Update latency if not set
                if result.latency_ms == 0:
                    result.latency_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return result

        except Exception as e:
            logger.error("health_check_failed", component=name, error=str(e))
            return HealthCheckResult(
                component=name,
                component_type=self.check_metadata[name]["type"],
                status=HealthStatus.UNHEALTHY,
                latency_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                message=f"Exception: {e!s}",
            )

    def _update_metrics(self, result: HealthCheckResult):
        """Update Prometheus metrics"""
        # Duration
        self.health_check_duration.labels(component=result.component, type=result.component_type.value).observe(
            result.latency_ms / 1000.0
        )

        # Status
        status_value = {
            HealthStatus.HEALTHY: 1.0,
            HealthStatus.DEGRADED: 0.5,
            HealthStatus.UNHEALTHY: 0.0,
            HealthStatus.UNKNOWN: 0.0,
        }[result.status]

        self.health_status_gauge.labels(component=result.component, type=result.component_type.value).set(status_value)

        # Counter
        self.health_check_total.labels(
            component=result.component,
            type=result.component_type.value,
            status=result.status.value,
        ).inc()

    async def _check_alerts(self, results: list[HealthCheckResult]):
        """Check if any alerts should be triggered"""
        for result in results:
            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                # Check if this is a new issue
                previous = self.latest_results.get(result.component)
                if not previous or previous.status == HealthStatus.HEALTHY:
                    # Trigger alerts
                    await self._trigger_alerts(result)

    async def _trigger_alerts(self, result: HealthCheckResult):
        """Trigger registered alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                await callback(result)
            except Exception as e:
                logger.error("alert_callback_failed", error=str(e))

    def _add_to_history(self, response: dict[str, Any]):
        """Add response to history"""
        self.check_history.append(response)

        # Trim history
        if len(self.check_history) > self.max_history:
            self.check_history = self.check_history[-self.max_history :]

    async def _get_system_info(self) -> dict[str, Any]:
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "free": psutil.disk_usage("/").free,
                "percent": psutil.disk_usage("/").percent,
            },
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        }

    # Default health checks
    async def _check_cpu_usage(self) -> HealthCheckResult:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=0.1)

        if cpu_percent >= self.thresholds.cpu_usage_critical_percent:
            status = HealthStatus.UNHEALTHY
        elif cpu_percent >= self.thresholds.cpu_usage_warn_percent:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthCheckResult(
            component="system_cpu",
            component_type=ComponentType.SERVICE,
            status=status,
            latency_ms=0,
            message=f"CPU usage: {cpu_percent}%",
            metadata={"cpu_percent": cpu_percent},
        )

    async def _check_memory_usage(self) -> HealthCheckResult:
        """Check memory usage"""
        memory = psutil.virtual_memory()

        if memory.percent >= self.thresholds.memory_usage_critical_percent:
            status = HealthStatus.UNHEALTHY
        elif memory.percent >= self.thresholds.memory_usage_warn_percent:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthCheckResult(
            component="system_memory",
            component_type=ComponentType.SERVICE,
            status=status,
            latency_ms=0,
            message=f"Memory usage: {memory.percent}%",
            metadata={
                "memory_percent": memory.percent,
                "available_mb": memory.available / 1024 / 1024,
            },
        )

    async def _check_disk_usage(self) -> HealthCheckResult:
        """Check disk usage"""
        disk = psutil.disk_usage("/")

        if disk.percent >= self.thresholds.disk_usage_critical_percent:
            status = HealthStatus.UNHEALTHY
        elif disk.percent >= self.thresholds.disk_usage_warn_percent:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthCheckResult(
            component="system_disk",
            component_type=ComponentType.SERVICE,
            status=status,
            latency_ms=0,
            message=f"Disk usage: {disk.percent}%",
            metadata={
                "disk_percent": disk.percent,
                "free_gb": disk.free / 1024 / 1024 / 1024,
            },
        )

    def register_alert_callback(self, callback: Callable):
        """Register an alert callback"""
        self.alert_callbacks.append(callback)

    def get_metrics(self) -> bytes:
        """Get Prometheus metrics"""
        return generate_latest()

    async def get_history(self, minutes: int = 60, component: Optional[str] = None) -> list[dict[str, Any]]:
        """Get health check history"""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        filtered_history = []
        for entry in self.check_history:
            entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if entry_time >= cutoff:
                if component:
                    # Filter by component
                    component_data = {}
                    for comp_type, checks in entry["components"].items():
                        filtered_checks = [c for c in checks if c["component"] == component]
                        if filtered_checks:
                            component_data[comp_type] = filtered_checks

                    if component_data:
                        filtered_entry = entry.copy()
                        filtered_entry["components"] = component_data
                        filtered_history.append(filtered_entry)
                else:
                    filtered_history.append(entry)

        return filtered_history


# Specialized health checks for common services


class DatabaseHealthCheck:
    """PostgreSQL health check"""

    def __init__(self, connection_string: str, timeout: float = 5.0):
        self.connection_string = connection_string
        self.timeout = timeout

    async def __call__(self) -> HealthCheckResult:
        start = datetime.now(timezone.utc)

        try:
            # Connect with timeout
            conn = await asyncio.wait_for(asyncpg.connect(self.connection_string), timeout=self.timeout)

            # Run simple query
            await conn.fetchval("SELECT 1")
            await conn.close()

            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return HealthCheckResult(
                component="postgresql",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                message="Database connection successful",
            )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                component="postgresql",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                latency_ms=self.timeout * 1000,
                message="Connection timeout",
            )
        except Exception as e:
            return HealthCheckResult(
                component="postgresql",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                latency_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                message=f"Connection failed: {e!s}",
            )


class RedisHealthCheck:
    """Redis health check"""

    def __init__(self, redis_url: str, timeout: float = 5.0):
        self.redis_url = redis_url
        self.timeout = timeout

    async def __call__(self) -> HealthCheckResult:
        start = datetime.now(timezone.utc)

        try:
            # Connect to Redis
            client = redis.from_url(self.redis_url)

            # Ping
            await asyncio.wait_for(client.ping(), timeout=self.timeout)

            # Get info
            info = await client.info()

            await client.close()

            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            return HealthCheckResult(
                component="redis",
                component_type=ComponentType.CACHE,
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                message="Redis connection successful",
                metadata={
                    "version": info.get("redis_version"),
                    "connected_clients": info.get("connected_clients"),
                    "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                component="redis",
                component_type=ComponentType.CACHE,
                status=HealthStatus.UNHEALTHY,
                latency_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                message=f"Connection failed: {e!s}",
            )


class HTTPHealthCheck:
    """HTTP endpoint health check"""

    def __init__(
        self,
        url: str,
        expected_status: int = 200,
        timeout: float = 5.0,
        headers: Optional[dict[str, str]] = None,
    ):
        self.url = url
        self.expected_status = expected_status
        self.timeout = timeout
        self.headers = headers or {}

    async def __call__(self) -> HealthCheckResult:
        start = datetime.now(timezone.utc)

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(
                    self.url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response,
            ):
                latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000

                if response.status == self.expected_status:
                    return HealthCheckResult(
                        component=self.url,
                        component_type=ComponentType.API,
                        status=HealthStatus.HEALTHY,
                        latency_ms=latency,
                        message=f"HTTP {response.status}",
                        metadata={"status_code": response.status},
                    )
                else:
                    return HealthCheckResult(
                        component=self.url,
                        component_type=ComponentType.API,
                        status=HealthStatus.UNHEALTHY,
                        latency_ms=latency,
                        message=f"Unexpected status: {response.status}",
                        metadata={"status_code": response.status},
                    )

        except Exception as e:
            return HealthCheckResult(
                component=self.url,
                component_type=ComponentType.API,
                status=HealthStatus.UNHEALTHY,
                latency_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                message=f"Request failed: {e!s}",
            )


# LUKHAS-specific health checks


class LukhasMemoryHealthCheck:
    """Check LUKHAS memory system health"""

    def __init__(self, memory_service):
        self.memory_service = memory_service

    async def __call__(self) -> HealthCheckResult:
        try:
            # Check memory fold capability
            test_result = await self.memory_service.test_fold_capability()

            if test_result["success"]:
                return HealthCheckResult(
                    component="lukhas_memory",
                    component_type=ComponentType.LUKHAS_MODULE,
                    status=HealthStatus.HEALTHY,
                    latency_ms=test_result["latency_ms"],
                    message="Memory system operational",
                    metadata={
                        "memory_count": test_result["memory_count"],
                        "fold_capacity": test_result["fold_capacity"],
                    },
                )
            else:
                return HealthCheckResult(
                    component="lukhas_memory",
                    component_type=ComponentType.LUKHAS_MODULE,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=0,
                    message=test_result["error"],
                )

        except Exception as e:
            return HealthCheckResult(
                component="lukhas_memory",
                component_type=ComponentType.LUKHAS_MODULE,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Check failed: {e!s}",
            )


async def main():
    """Example usage"""
    # Initialize health check system
    health_system = HealthCheckSystem()

    # Register custom checks
    health_system.register_check(
        "database",
        ComponentType.DATABASE,
        DatabaseHealthCheck("postgresql://localhost/lukhas"),
    )

    health_system.register_check("redis", ComponentType.CACHE, RedisHealthCheck("redis://localhost:6379"))

    health_system.register_check("api", ComponentType.API, HTTPHealthCheck("http://localhost:8000/health"))

    # Register alert callback
    async def alert_callback(result: HealthCheckResult):
        if result.status == HealthStatus.UNHEALTHY:
            print(f"⚠️  ALERT: {result.component} is {result.status.value}")
            print(f"   Message: {result.message}")

    health_system.register_alert_callback(alert_callback)

    # Run health checks
    results = await health_system.check_all()

    print("\n🏥 Health Check Results")
    print(f"   Overall Status: {results['status']}")
    print(f"   Total Checks: {results['checks_total']}")
    print(f"   Healthy: {results['checks_healthy']}")
    print(f"   Degraded: {results['checks_degraded']}")
    print(f"   Unhealthy: {results['checks_unhealthy']}")

    # Get metrics
    metrics = health_system.get_metrics()
    print(f"\n📊 Prometheus Metrics Available: {len(metrics}} bytes")


if __name__ == "__main__":
    asyncio.run(main())
