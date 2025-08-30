"""
Real-Time Service Switching for DAST
Dynamic failover and service selection for resilient operations
"""

import asyncio
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ServiceType(Enum):
    """Types of services that can be switched"""

    LLM = "llm"  # Language models
    IMAGE_PROCESSING = "image_processing"
    TRANSLATION = "translation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    SEARCH = "search"
    DATABASE = "database"
    CACHE = "cache"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"


class ServiceStatus(Enum):
    """Current status of a service"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"


class FailoverStrategy(Enum):
    """Strategy for failover"""

    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    PERFORMANCE_BASED = "performance_based"
    COST_OPTIMIZED = "cost_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    LOAD_BALANCED = "load_balanced"


@dataclass
class ServiceProvider:
    """Individual service provider configuration"""

    provider_id: str
    name: str
    service_type: ServiceType
    endpoint: str
    api_key: Optional[str] = None
    priority: int = 1  # Lower is higher priority
    cost_per_request: float = 0.0
    max_requests_per_second: int = 100
    timeout: float = 30.0
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """Health metrics for a service"""

    provider_id: str
    status: ServiceStatus
    response_time_ms: float
    success_rate: float  # 0-1
    error_count: int
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    health_score: float = 1.0  # 0-1 score


@dataclass
class ServiceRequest:
    """Request to be routed to a service"""

    request_id: str
    service_type: ServiceType
    payload: dict[str, Any]
    requirements: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    timeout_override: Optional[float] = None


@dataclass
class ServiceResponse:
    """Response from a service"""

    request_id: str
    provider_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    response_time_ms: float = 0.0
    retry_count: int = 0


class RealTimeServiceSwitcher:
    """
    Manages real-time service switching and failover
    Ensures resilience through automatic backup service selection
    """

    def __init__(self):
        self.service_providers: dict[str, list[ServiceProvider]] = {}
        self.service_health: dict[str, ServiceHealth] = {}
        self.failover_strategy = FailoverStrategy.PERFORMANCE_BASED
        self.request_history: list[ServiceRequest] = []
        self.response_history: list[ServiceResponse] = []

        # Health check configuration
        self.health_check_interval = 30.0  # seconds
        self.health_check_timeout = 5.0
        self.failure_threshold = 3  # consecutive failures before marking unhealthy
        self.recovery_threshold = 2  # consecutive successes to mark recovered

        # Performance tracking
        self.performance_window = 100  # Last N requests for performance calculation
        self.performance_metrics: dict[str, list[float]] = {}

        # Circuit breaker configuration
        self.circuit_breaker_enabled = True
        self.circuit_breaker_threshold = 5  # failures before opening
        self.circuit_breaker_timeout = 60.0  # seconds before attempting recovery
        self.circuit_breakers: dict[str, datetime] = {}

        # Executor for async operations
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Initialize default providers
        self._initialize_default_providers()

    def register_provider(self, provider: ServiceProvider) -> None:
        """Register a new service provider"""
        if provider.service_type not in self.service_providers:
            self.service_providers[provider.service_type] = []

        self.service_providers[provider.service_type].append(provider)

        # Initialize health tracking
        self.service_health[provider.provider_id] = ServiceHealth(
            provider_id=provider.provider_id,
            status=ServiceStatus.UNKNOWN,
            response_time_ms=0.0,
            success_rate=1.0,
            error_count=0,
        )

        # Initialize performance metrics
        self.performance_metrics[provider.provider_id] = []

    async def execute_request(self, request: ServiceRequest) -> ServiceResponse:
        """
        Execute a request with automatic failover
        """
        # Select primary provider
        primary_provider = self._select_provider(request)

        if not primary_provider:
            return ServiceResponse(
                request_id=request.request_id,
                provider_id="none",
                success=False,
                error="No available providers for service type",
            )

        # Try primary provider
        response = await self._try_provider(primary_provider, request)

        if response.success:
            return response

        # Primary failed, try failover
        backup_providers = self._get_backup_providers(
            request.service_type, exclude=[primary_provider.provider_id]
        )

        for backup in backup_providers[: request.max_retries]:
            response = await self._try_provider(backup, request)
            if response.success:
                # Log successful failover
                self._record_failover_success(primary_provider, backup)
                return response

        # All providers failed
        return ServiceResponse(
            request_id=request.request_id,
            provider_id="all_failed",
            success=False,
            error="All providers failed after retries",
            retry_count=request.max_retries,
        )

    def get_service_status(self, service_type: Optional[ServiceType] = None) -> dict[str, Any]:
        """Get current status of services"""
        status = {
            "overall_health": self._calculate_overall_health(),
            "providers": {},
            "failover_ready": {},
            "recommendations": [],
        }

        # Filter by service type if specified
        providers_to_check = []
        if service_type:
            providers_to_check = self.service_providers.get(service_type, [])
        else:
            for providers in self.service_providers.values():
                providers_to_check.extend(providers)

        # Check each provider
        for provider in providers_to_check:
            health = self.service_health.get(provider.provider_id)
            if health:
                status["providers"][provider.provider_id] = {
                    "name": provider.name,
                    "type": provider.service_type.value,
                    "status": health.status.value,
                    "health_score": health.health_score,
                    "response_time_ms": health.response_time_ms,
                    "success_rate": health.success_rate,
                    "circuit_breaker": self._is_circuit_open(provider.provider_id),
                }

        # Check failover readiness
        for svc_type in ServiceType:
            available_count = self._count_available_providers(svc_type)
            status["failover_ready"][svc_type.value] = available_count >= 2

        # Generate recommendations
        status["recommendations"] = self._generate_recommendations()

        return status

    async def perform_health_checks(self) -> dict[str, ServiceHealth]:
        """Perform health checks on all providers"""
        health_results = {}

        tasks = []
        for providers in self.service_providers.values():
            for provider in providers:
                if not self._is_circuit_open(provider.provider_id):
                    tasks.append(self._health_check_provider(provider))

        # Run health checks concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, ServiceHealth):
                    health_results[result.provider_id] = result
                    self.service_health[result.provider_id] = result

        return health_results

    def configure_failover_strategy(
        self, strategy: FailoverStrategy, config: Optional[dict[str, Any]] = None
    ) -> None:
        """Configure the failover strategy"""
        self.failover_strategy = strategy

        if config:
            if "health_check_interval" in config:
                self.health_check_interval = config["health_check_interval"]
            if "failure_threshold" in config:
                self.failure_threshold = config["failure_threshold"]
            if "circuit_breaker_enabled" in config:
                self.circuit_breaker_enabled = config["circuit_breaker_enabled"]

    def get_performance_report(self) -> dict[str, Any]:
        """Get performance report for all services"""
        report = {
            "summary": {},
            "providers": {},
            "failover_events": [],
            "optimization_opportunities": [],
        }

        # Calculate summary metrics
        total_requests = len(self.response_history)
        successful_requests = sum(1 for r in self.response_history if r.success)

        report["summary"] = {
            "total_requests": total_requests,
            "success_rate": (successful_requests / total_requests if total_requests > 0 else 0),
            "avg_response_time_ms": self._calculate_avg_response_time(),
            "failover_count": sum(1 for r in self.response_history if r.retry_count > 0),
        }

        # Provider-specific metrics
        for provider_id, metrics in self.performance_metrics.items():
            if metrics:
                provider = self._get_provider_by_id(provider_id)
                report["providers"][provider_id] = {
                    "name": provider.name if provider else "Unknown",
                    "avg_response_time_ms": statistics.mean(metrics[-100:]),
                    "p95_response_time_ms": self._calculate_percentile(metrics[-100:], 95),
                    "p99_response_time_ms": self._calculate_percentile(metrics[-100:], 99),
                    "requests_handled": len(
                        [r for r in self.response_history if r.provider_id == provider_id]
                    ),
                    "cost_incurred": self._calculate_provider_cost(provider_id),
                }

        # Failover events
        report["failover_events"] = self._get_recent_failover_events()

        # Optimization opportunities
        report["optimization_opportunities"] = self._identify_optimizations()

        return report

    def _initialize_default_providers(self) -> None:
        """Initialize default service providers"""
        # LLM providers
        default_llms = [
            ServiceProvider(
                provider_id="openai_gpt4",
                name="OpenAI GPT-4",
                service_type=ServiceType.LLM,
                endpoint="https://api.openai.com/v1/chat/completions",
                priority=1,
                cost_per_request=0.03,
                timeout=60.0,
                capabilities=["chat", "completion", "analysis"],
            ),
            ServiceProvider(
                provider_id="anthropic_claude",
                name="Anthropic Claude",
                service_type=ServiceType.LLM,
                endpoint="https://api.anthropic.com/v1/messages",
                priority=2,
                cost_per_request=0.025,
                timeout=60.0,
                capabilities=["chat", "completion", "coding"],
            ),
            ServiceProvider(
                provider_id="local_llm",
                name="Local LLM",
                service_type=ServiceType.LLM,
                endpoint="http://localhost:8080/v1/completions",
                priority=3,
                cost_per_request=0.0,
                timeout=30.0,
                capabilities=["chat", "completion"],
            ),
        ]

        for provider in default_llms:
            self.register_provider(provider)

    def _select_provider(self, request: ServiceRequest) -> Optional[ServiceProvider]:
        """Select best provider based on strategy"""
        available_providers = self._get_available_providers(request.service_type)

        if not available_providers:
            return None

        if self.failover_strategy == FailoverStrategy.PRIORITY:
            return self._select_by_priority(available_providers)
        elif self.failover_strategy == FailoverStrategy.PERFORMANCE_BASED:
            return self._select_by_performance(available_providers)
        elif self.failover_strategy == FailoverStrategy.COST_OPTIMIZED:
            return self._select_by_cost(available_providers)
        elif self.failover_strategy == FailoverStrategy.LATENCY_OPTIMIZED:
            return self._select_by_latency(available_providers)
        elif self.failover_strategy == FailoverStrategy.LOAD_BALANCED:
            return self._select_by_load_balance(available_providers)
        else:  # ROUND_ROBIN
            return self._select_round_robin(available_providers)

    def _get_available_providers(self, service_type: ServiceType) -> list[ServiceProvider]:
        """Get available providers for service type"""
        if service_type not in self.service_providers:
            return []

        available = []
        for provider in self.service_providers[service_type]:
            # Check circuit breaker
            if self._is_circuit_open(provider.provider_id):
                continue

            # Check health status
            health = self.service_health.get(provider.provider_id)
            if health and health.status in [
                ServiceStatus.UNAVAILABLE,
                ServiceStatus.FAILING,
            ]:
                continue

            available.append(provider)

        return available

    def _get_backup_providers(
        self, service_type: ServiceType, exclude: list[str]
    ) -> list[ServiceProvider]:
        """Get backup providers excluding specific ones"""
        available = self._get_available_providers(service_type)
        return [p for p in available if p.provider_id not in exclude]

    async def _try_provider(
        self, provider: ServiceProvider, request: ServiceRequest
    ) -> ServiceResponse:
        """Try to execute request with specific provider"""
        start_time = time.time()

        try:
            # Simulate provider call (would be actual API call)
            timeout = request.timeout_override or provider.timeout

            # This would be the actual service call
            result = await self._call_provider_api(provider, request, timeout)

            response_time = (time.time() - start_time) * 1000

            # Update metrics
            self._update_provider_metrics(provider.provider_id, True, response_time)

            return ServiceResponse(
                request_id=request.request_id,
                provider_id=provider.provider_id,
                success=True,
                data=result,
                response_time_ms=response_time,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Update metrics
            self._update_provider_metrics(provider.provider_id, False, response_time)

            return ServiceResponse(
                request_id=request.request_id,
                provider_id=provider.provider_id,
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _call_provider_api(
        self, provider: ServiceProvider, request: ServiceRequest, timeout: float
    ) -> Any:
        """Make actual API call to provider"""
        # This is a simulation - would implement actual API calls
        import random

        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate for testing
            raise Exception("Simulated provider failure")

        return {"result": "success", "provider": provider.name}

    async def _health_check_provider(self, provider: ServiceProvider) -> ServiceHealth:
        """Perform health check on a provider"""
        start_time = time.time()

        try:
            # Simple health check - would be actual ping/health endpoint
            await self._call_provider_api(
                provider,
                ServiceRequest(
                    request_id="health_check",
                    service_type=provider.service_type,
                    payload={"test": True},
                ),
                self.health_check_timeout,
            )

            response_time = (time.time() - start_time) * 1000

            # Update health
            health = self.service_health[provider.provider_id]
            health.status = ServiceStatus.HEALTHY
            health.response_time_ms = response_time
            health.last_success = datetime.now()
            health.consecutive_failures = 0
            health.health_score = 1.0

            return health

        except Exception:
            response_time = (time.time() - start_time) * 1000

            # Update health
            health = self.service_health[provider.provider_id]
            health.consecutive_failures += 1
            health.last_failure = datetime.now()
            health.error_count += 1

            # Update status based on failures
            if health.consecutive_failures >= self.failure_threshold:
                health.status = ServiceStatus.FAILING
                health.health_score = 0.2
            else:
                health.status = ServiceStatus.DEGRADED
                health.health_score = 0.6

            return health

    def _update_provider_metrics(
        self, provider_id: str, success: bool, response_time: float
    ) -> None:
        """Update provider performance metrics"""
        # Update performance history
        if provider_id not in self.performance_metrics:
            self.performance_metrics[provider_id] = []

        self.performance_metrics[provider_id].append(response_time)

        # Keep only recent metrics
        if len(self.performance_metrics[provider_id]) > self.performance_window:
            self.performance_metrics[provider_id] = self.performance_metrics[provider_id][
                -self.performance_window :
            ]

        # Update health
        if provider_id in self.service_health:
            health = self.service_health[provider_id]

            if success:
                health.last_success = datetime.now()
                health.consecutive_failures = 0

                # Check for recovery
                if health.status == ServiceStatus.RECOVERING:
                    health.status = ServiceStatus.HEALTHY
                    self._close_circuit_breaker(provider_id)
            else:
                health.last_failure = datetime.now()
                health.consecutive_failures += 1
                health.error_count += 1

                # Check for circuit breaker
                if health.consecutive_failures >= self.circuit_breaker_threshold:
                    self._open_circuit_breaker(provider_id)
                    health.status = ServiceStatus.UNAVAILABLE

            # Update success rate
            recent_responses = [
                r for r in self.response_history[-100:] if r.provider_id == provider_id
            ]
            if recent_responses:
                health.success_rate = sum(1 for r in recent_responses if r.success) / len(
                    recent_responses
                )

            # Update health score
            health.health_score = self._calculate_health_score(health)

    def _is_circuit_open(self, provider_id: str) -> bool:
        """Check if circuit breaker is open for provider"""
        if not self.circuit_breaker_enabled:
            return False

        if provider_id not in self.circuit_breakers:
            return False

        # Check if timeout has passed
        open_time = self.circuit_breakers[provider_id]
        if (datetime.now() - open_time).total_seconds() > self.circuit_breaker_timeout:
            # Try to close circuit
            self._close_circuit_breaker(provider_id)
            return False

        return True

    def _open_circuit_breaker(self, provider_id: str) -> None:
        """Open circuit breaker for provider"""
        if self.circuit_breaker_enabled:
            self.circuit_breakers[provider_id] = datetime.now()

    def _close_circuit_breaker(self, provider_id: str) -> None:
        """Close circuit breaker for provider"""
        if provider_id in self.circuit_breakers:
            del self.circuit_breakers[provider_id]

            # Set to recovering state
            if provider_id in self.service_health:
                self.service_health[provider_id].status = ServiceStatus.RECOVERING

    def _select_by_priority(self, providers: list[ServiceProvider]) -> ServiceProvider:
        """Select provider by priority"""
        return min(providers, key=lambda p: p.priority)

    def _select_by_performance(self, providers: list[ServiceProvider]) -> ServiceProvider:
        """Select provider by performance"""
        best_score = -1
        best_provider = providers[0]

        for provider in providers:
            health = self.service_health.get(provider.provider_id)
            if health and health.health_score > best_score:
                best_score = health.health_score
                best_provider = provider

        return best_provider

    def _select_by_cost(self, providers: list[ServiceProvider]) -> ServiceProvider:
        """Select provider by cost"""
        return min(providers, key=lambda p: p.cost_per_request)

    def _select_by_latency(self, providers: list[ServiceProvider]) -> ServiceProvider:
        """Select provider by latency"""
        best_latency = float("inf")
        best_provider = providers[0]

        for provider in providers:
            health = self.service_health.get(provider.provider_id)
            if health and health.response_time_ms < best_latency:
                best_latency = health.response_time_ms
                best_provider = provider

        return best_provider

    def _select_by_load_balance(self, providers: list[ServiceProvider]) -> ServiceProvider:
        """Select provider using load balancing"""
        # Count recent requests per provider
        request_counts = {}
        for provider in providers:
            count = sum(
                1 for r in self.response_history[-100:] if r.provider_id == provider.provider_id
            )
            request_counts[provider.provider_id] = count

        # Select provider with least recent requests
        return min(providers, key=lambda p: request_counts.get(p.provider_id, 0))

    def _select_round_robin(self, providers: list[ServiceProvider]) -> ServiceProvider:
        """Select provider using round robin"""
        # Simple round robin based on request count
        import random

        return random.choice(providers)

    def _calculate_health_score(self, health: ServiceHealth) -> float:
        """Calculate overall health score for provider"""
        score = 0.0

        # Success rate component (40%)
        score += health.success_rate * 0.4

        # Response time component (30%)
        if health.response_time_ms < 100:
            score += 0.3
        elif health.response_time_ms < 500:
            score += 0.2
        elif health.response_time_ms < 1000:
            score += 0.1

        # Availability component (30%)
        if health.status == ServiceStatus.HEALTHY:
            score += 0.3
        elif health.status == ServiceStatus.DEGRADED:
            score += 0.15
        elif health.status == ServiceStatus.RECOVERING:
            score += 0.1

        return min(1.0, max(0.0, score))

    def _calculate_overall_health(self) -> str:
        """Calculate overall system health"""
        if not self.service_health:
            return "unknown"

        avg_health_score = statistics.mean(h.health_score for h in self.service_health.values())

        if avg_health_score > 0.8:
            return "healthy"
        elif avg_health_score > 0.6:
            return "degraded"
        elif avg_health_score > 0.4:
            return "poor"
        else:
            return "critical"

    def _count_available_providers(self, service_type: ServiceType) -> int:
        """Count available providers for a service type"""
        return len(self._get_available_providers(service_type))

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on current state"""
        recommendations = []

        # Check for single points of failure
        for service_type in ServiceType:
            if self._count_available_providers(service_type) < 2:
                recommendations.append(
                    f"Add backup provider for {service_type.value} to enable failover"
                )

        # Check for poor performing providers
        for provider_id, health in self.service_health.items():
            if health.health_score < 0.5:
                provider = self._get_provider_by_id(provider_id)
                if provider:
                    recommendations.append(
                        f"Investigate issues with {provider.name} (health score: {health.health_score:.2f})"
                    )

        # Check for high costs
        high_cost_providers = [
            p
            for providers in self.service_providers.values()
            for p in providers
            if p.cost_per_request > 0.05
        ]
        if high_cost_providers:
            recommendations.append("Consider adding lower-cost alternatives for cost optimization")

        return recommendations

    def _get_provider_by_id(self, provider_id: str) -> Optional[ServiceProvider]:
        """Get provider by ID"""
        for providers in self.service_providers.values():
            for provider in providers:
                if provider.provider_id == provider_id:
                    return provider
        return None

    def _record_failover_success(self, primary: ServiceProvider, backup: ServiceProvider) -> None:
        """Record successful failover event"""
        # Would log this for analysis

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.response_history:
            return 0.0

        recent_responses = self.response_history[-100:]
        return statistics.mean(r.response_time_ms for r in recent_responses)

    def _calculate_percentile(self, values: list[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _calculate_provider_cost(self, provider_id: str) -> float:
        """Calculate total cost for provider"""
        provider = self._get_provider_by_id(provider_id)
        if not provider:
            return 0.0

        request_count = sum(
            1 for r in self.response_history if r.provider_id == provider_id and r.success
        )

        return request_count * provider.cost_per_request

    def _get_recent_failover_events(self) -> list[dict]:
        """Get recent failover events"""
        events = []

        for response in self.response_history[-50:]:
            if response.retry_count > 0:
                events.append(
                    {
                        "request_id": response.request_id,
                        "final_provider": response.provider_id,
                        "retry_count": response.retry_count,
                        "success": response.success,
                    }
                )

        return events[-10:]  # Last 10 events

    def _identify_optimizations(self) -> list[str]:
        """Identify optimization opportunities"""
        optimizations = []

        # Check for providers that are consistently faster
        fastest_providers = {}
        for service_type in ServiceType:
            providers = self.service_providers.get(service_type, [])
            if len(providers) > 1:
                best_latency = float("inf")
                best_provider = None

                for provider in providers:
                    health = self.service_health.get(provider.provider_id)
                    if health and health.response_time_ms < best_latency:
                        best_latency = health.response_time_ms
                        best_provider = provider

                if best_provider:
                    fastest_providers[service_type] = best_provider

        if fastest_providers:
            optimizations.append("Consider prioritizing fastest providers for latency optimization")

        # Check for cost optimization opportunities
        if self.failover_strategy != FailoverStrategy.COST_OPTIMIZED:
            total_cost = sum(
                self._calculate_provider_cost(p.provider_id)
                for providers in self.service_providers.values()
                for p in providers
            )
            if total_cost > 100:  # Arbitrary threshold
                optimizations.append("Consider COST_OPTIMIZED strategy to reduce expenses")

        return optimizations


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        switcher = RealTimeServiceSwitcher()

        # Configure failover strategy
        switcher.configure_failover_strategy(
            FailoverStrategy.PERFORMANCE_BASED, {"health_check_interval": 10.0}
        )

        # Simulate some requests
        for i in range(5):
            request = ServiceRequest(
                request_id=f"req_{i}",
                service_type=ServiceType.LLM,
                payload={"prompt": "Hello, world!"},
                max_retries=2,
            )

            response = await switcher.execute_request(request)
            print(
                f"Request {i}: Success={response.success}, Provider={response.provider_id}, "
                f"Time={response.response_time_ms:.2f}ms"
            )

        # Perform health checks
        health_results = await switcher.perform_health_checks()
        print("\nHealth Check Results:")
        for provider_id, health in health_results.items():
            print(f"- {provider_id}: {health.status.value} (score: {health.health_score:.2f})")

        # Get service status
        status = switcher.get_service_status()
        print("\nService Status:")
        print(f"Overall Health: {status['overall_health']}")
        print(f"Failover Ready: {status['failover_ready']}")

        # Get performance report
        report = switcher.get_performance_report()
        print("\nPerformance Report:")
        print(f"Success Rate: {report['summary']['success_rate']:.2%}")
        print(f"Avg Response Time: {report['summary']['avg_response_time_ms']:.2f}ms")
        print(f"Failover Count: {report['summary']['failover_count']}")

        if report["optimization_opportunities"]:
            print("\nOptimization Opportunities:")
            for opt in report["optimization_opportunities"]:
                print(f"- {opt}")

    asyncio.run(main())
