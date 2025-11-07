#!/usr/bin/env python3
"""
LUKHAS Phase 4 - Health Monitoring Service
==========================================

Real-time health monitoring for external AI providers with intelligent
degradation detection, performance tracking, and proactive failover.

Key Features:
- Continuous health checks for all AI providers
- Performance metric collection (latency, success rate, error rate)
- Intelligent degradation detection
- Predictive failure analysis
- Health status broadcasting to routing engine
- Integration with circuit breakers
- SLA monitoring and alerting

Performance Requirements:
- Health checks every 30 seconds
- <50ms health check overhead
- 99.9% monitoring uptime
- Real-time status updates

Constellation Framework: Flow Star (🌊) coordination hub
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from opentelemetry import trace

from observability import counter, gauge, histogram

from .providers import AIProvider, create_provider_client
from .routing_config import HealthStatus, ProviderHealth

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics for health monitoring
health_check_total = counter(
    'lukhas_health_check_total',
    'Total health checks performed',
    ['provider', 'result']
)

health_check_duration = histogram(
    'lukhas_health_check_duration_seconds',
    'Health check duration',
    ['provider'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

provider_health_score = gauge(
    'lukhas_provider_health_score',
    'Provider health score (0-100)',
    ['provider']
)

provider_latency_ms = gauge(
    'lukhas_provider_latency_ms',
    'Provider average latency in milliseconds',
    ['provider']
)

provider_success_rate = gauge(
    'lukhas_provider_success_rate',
    'Provider success rate (0-1)',
    ['provider']
)

provider_error_rate = gauge(
    'lukhas_provider_error_rate',
    'Provider error rate (0-1)',
    ['provider']
)

health_status_changes = counter(
    'lukhas_health_status_changes_total',
    'Health status changes',
    ['provider', 'from_status', 'to_status']
)

sla_violations = counter(
    'lukhas_sla_violations_total',
    'SLA violations detected',
    ['provider', 'violation_type']
)


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    provider: str
    success: bool
    latency_ms: float
    error: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a provider"""
    provider: str
    total_requests: int = 0
    successful_requests: int = 0
    total_latency_ms: float = 0.0
    error_count: int = 0
    last_error: str | None = None
    uptime_percentage: float = 100.0


@dataclass
class SLAThresholds:
    """SLA thresholds for monitoring"""
    max_latency_ms: float = 2000.0
    min_success_rate: float = 0.99
    max_error_rate: float = 0.01
    uptime_percentage: float = 99.9


class HealthMonitor:
    """Health monitoring service for AI providers"""

    def __init__(self, check_interval: float = 30.0, history_size: int = 100):
        self.check_interval = check_interval
        self.history_size = history_size

        # Health state
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}

        # SLA configuration
        self.sla_thresholds = SLAThresholds()

        # Monitoring state
        self.running = False
        self.monitor_task: asyncio.Task | None = None
        self.health_change_callbacks: List[Callable] = []

        # Provider clients for health checks
        self.provider_clients: Dict[str, Any] = {}

        logger.info("Health monitor initialized")

    async def start(self) -> None:
        """Start health monitoring"""
        if self.running:
            return

        logger.info("🏥 Starting health monitor...")

        # Initialize provider clients
        await self._initialize_provider_clients()

        # Initialize health state
        await self._initialize_health_state()

        # Start monitoring loop
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())

        logger.info("✅ Health monitor started")

    async def stop(self) -> None:
        """Stop health monitoring"""
        if not self.running:
            return

        logger.info("🛑 Stopping health monitor...")

        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.monitor_task

        logger.info("✅ Health monitor stopped")

    def add_health_change_callback(self, callback: Callable) -> None:
        """Add callback for health status changes"""
        self.health_change_callbacks.append(callback)

    async def get_provider_health(self, provider: str) -> ProviderHealth | None:
        """Get current health status for a provider"""
        return self.provider_health.get(provider)

    async def get_all_provider_health(self) -> Dict[str, ProviderHealth]:
        """Get health status for all providers"""
        return self.provider_health.copy()

    async def perform_health_check(self, provider: str) -> HealthCheckResult:
        """Perform health check for a specific provider"""
        start_time = time.time()

        with tracer.start_span("health_monitor.check") as span:
            span.set_attribute("provider", provider)

            try:
                client = self.provider_clients.get(provider)
                if not client:
                    raise ValueError(f"No client for provider: {provider}")

                # Perform lightweight health check
                test_prompt = "Hello, this is a health check. Please respond with 'OK'."

                check_start = time.time()
                response = await client.generate(
                    prompt=test_prompt,
                    model=self._get_default_model_for_provider(provider),
                    max_tokens=10,
                    temperature=0.0
                )
                check_end = time.time()

                latency_ms = (check_end - check_start) * 1000
                success = bool(response and response.content)

                # Record metrics
                health_check_total.labels(
                    provider=provider,
                    result="success" if success else "failure"
                ).inc()

                health_check_duration.labels(provider=provider).observe(check_end - start_time)

                span.set_attribute("success", success)
                span.set_attribute("latency_ms", latency_ms)

                return HealthCheckResult(
                    provider=provider,
                    success=success,
                    latency_ms=latency_ms,
                    metadata={
                        "response_length": len(response.content) if response and response.content else 0,
                        "model_used": self._get_default_model_for_provider(provider)
                    }
                )

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000

                health_check_total.labels(
                    provider=provider,
                    result="error"
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                logger.warning(f"Health check failed for {provider}: {e}")

                return HealthCheckResult(
                    provider=provider,
                    success=False,
                    latency_ms=latency_ms,
                    error=str(e)
                )

    async def update_provider_health(self, provider: str, result: HealthCheckResult) -> None:
        """Update provider health based on check result"""

        # Get or create health record
        if provider not in self.provider_health:
            self.provider_health[provider] = ProviderHealth(provider=provider)

        health = self.provider_health[provider]
        old_status = health.status

        # Update basic metrics
        health.last_check = result.timestamp

        # Update latency (exponential moving average)
        alpha = 0.2
        if health.avg_latency_ms == 0:
            health.avg_latency_ms = result.latency_ms
        else:
            health.avg_latency_ms = alpha * result.latency_ms + (1 - alpha) * health.avg_latency_ms

        # Update success rate based on recent history
        history = self.health_history[provider]
        history.append(result)

        recent_checks = list(history)[-20:]  # Last 20 checks
        if recent_checks:
            successful_checks = sum(1 for check in recent_checks if check.success)
            health.success_rate = successful_checks / len(recent_checks)

        # Update consecutive failures
        if result.success:
            health.consecutive_failures = 0
            health.last_error = None
        else:
            health.consecutive_failures += 1
            health.last_error = result.error

        # Determine health status
        new_status = self._calculate_health_status(health)
        health.status = new_status

        # Update Prometheus metrics
        provider_health_score.labels(provider=provider).set(self._calculate_health_score(health))
        provider_latency_ms.labels(provider=provider).set(health.avg_latency_ms)
        provider_success_rate.labels(provider=provider).set(health.success_rate)
        provider_error_rate.labels(provider=provider).set(1.0 - health.success_rate)

        # Check for status changes
        if old_status != new_status:
            logger.info(f"🔄 Provider {provider} status changed: {old_status.value} -> {new_status.value}")

            health_status_changes.labels(
                provider=provider,
                from_status=old_status.value,
                to_status=new_status.value
            ).inc()

            # Notify callbacks
            await self._notify_health_change_callbacks(provider, old_status, new_status)

        # Check SLA violations
        await self._check_sla_violations(provider, health)

    async def _initialize_provider_clients(self) -> None:
        """Initialize clients for all providers"""
        logger.info("Initializing provider clients for health checks...")

        for provider_enum in AIProvider:
            try:
                client = create_provider_client(provider_enum)
                self.provider_clients[provider_enum.value] = client
                logger.info(f"✅ Health check client ready for {provider_enum.value}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize client for {provider_enum.value}: {e}")

    async def _initialize_health_state(self) -> None:
        """Initialize health state for all providers"""
        logger.info("Initializing provider health state...")

        for provider in self.provider_clients:
            self.provider_health[provider] = ProviderHealth(
                provider=provider,
                status=HealthStatus.UNKNOWN
            )
            self.performance_metrics[provider] = PerformanceMetrics(provider=provider)

        logger.info(f"✅ Health state initialized for {len(self.provider_clients)} providers")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        logger.info(f"🔄 Health monitoring loop started (interval: {self.check_interval}s)")

        while self.running:
            try:
                # Perform health checks for all providers
                check_tasks = []
                for provider in self.provider_clients:
                    task = asyncio.create_task(self._check_and_update_provider(provider))
                    check_tasks.append(task)

                # Wait for all checks to complete
                if check_tasks:
                    await asyncio.gather(*check_tasks, return_exceptions=True)

                # Wait for next check interval
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying

        logger.info("🛑 Health monitoring loop stopped")

    async def _check_and_update_provider(self, provider: str) -> None:
        """Check and update health for a single provider"""
        try:
            result = await self.perform_health_check(provider)
            await self.update_provider_health(provider, result)

        except Exception as e:
            logger.error(f"Error checking health for {provider}: {e}")

            # Create failure result
            result = HealthCheckResult(
                provider=provider,
                success=False,
                latency_ms=0.0,
                error=str(e)
            )
            await self.update_provider_health(provider, result)

    def _calculate_health_status(self, health: ProviderHealth) -> HealthStatus:
        """Calculate health status based on metrics"""

        # Unhealthy conditions
        if (health.consecutive_failures >= 3 or
            health.success_rate < 0.80 or
            health.avg_latency_ms > 5000):
            return HealthStatus.UNHEALTHY

        # Degraded conditions
        if (health.consecutive_failures >= 1 or
            health.success_rate < 0.95 or
            health.avg_latency_ms > 2000):
            return HealthStatus.DEGRADED

        # Healthy conditions
        if (health.success_rate >= 0.95 and
            health.avg_latency_ms <= 2000 and
            health.consecutive_failures == 0):
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN

    def _calculate_health_score(self, health: ProviderHealth) -> float:
        """Calculate health score (0-100)"""
        score = 0.0

        # Success rate component (0-50 points)
        score += health.success_rate * 50

        # Latency component (0-30 points)
        if health.avg_latency_ms <= 100:
            score += 30
        elif health.avg_latency_ms <= 500:
            score += 20
        elif health.avg_latency_ms <= 1000:
            score += 10

        # Failure streak penalty (0-20 points)
        if health.consecutive_failures == 0:
            score += 20
        elif health.consecutive_failures <= 2:
            score += 10

        return min(100.0, max(0.0, score))

    def _get_default_model_for_provider(self, provider: str) -> str:
        """Get default model for provider health checks"""
        model_map = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-haiku-20240307",
            "google": "gemini-pro",
            "local": "llama2"
        }
        return model_map.get(provider, "default")

    async def _notify_health_change_callbacks(
        self,
        provider: str,
        old_status: HealthStatus,
        new_status: HealthStatus
    ) -> None:
        """Notify registered callbacks of health status changes"""

        for callback in self.health_change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(provider, old_status, new_status)
                else:
                    callback(provider, old_status, new_status)
            except Exception as e:
                logger.error(f"Error in health change callback: {e}")

    async def _check_sla_violations(self, provider: str, health: ProviderHealth) -> None:
        """Check for SLA violations and record metrics"""

        # Check latency SLA
        if health.avg_latency_ms > self.sla_thresholds.max_latency_ms:
            sla_violations.labels(
                provider=provider,
                violation_type="latency"
            ).inc()

        # Check success rate SLA
        if health.success_rate < self.sla_thresholds.min_success_rate:
            sla_violations.labels(
                provider=provider,
                violation_type="success_rate"
            ).inc()

        # Check error rate SLA
        error_rate = 1.0 - health.success_rate
        if error_rate > self.sla_thresholds.max_error_rate:
            sla_violations.labels(
                provider=provider,
                violation_type="error_rate"
            ).inc()

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all providers"""
        summary = {
            "timestamp": time.time(),
            "providers": {},
            "overall_status": "healthy"
        }

        healthy_count = 0
        total_count = len(self.provider_health)

        for provider, health in self.provider_health.items():
            provider_summary = {
                "status": health.status.value,
                "success_rate": health.success_rate,
                "avg_latency_ms": health.avg_latency_ms,
                "consecutive_failures": health.consecutive_failures,
                "last_check": health.last_check,
                "health_score": self._calculate_health_score(health)
            }
            summary["providers"][provider] = provider_summary

            if health.status == HealthStatus.HEALTHY:
                healthy_count += 1

        # Determine overall status
        if healthy_count == total_count:
            summary["overall_status"] = "healthy"
        elif healthy_count >= total_count * 0.5:
            summary["overall_status"] = "degraded"
        else:
            summary["overall_status"] = "unhealthy"

        summary["healthy_providers"] = healthy_count
        summary["total_providers"] = total_count

        return summary


# Global health monitor instance
_health_monitor: HealthMonitor | None = None


async def get_health_monitor() -> HealthMonitor:
    """Get or create global health monitor"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
        await _health_monitor.start()
    return _health_monitor


async def get_provider_health_status() -> Dict[str, ProviderHealth]:
    """Get current health status for all providers"""
    monitor = await get_health_monitor()
    return await monitor.get_all_provider_health()
