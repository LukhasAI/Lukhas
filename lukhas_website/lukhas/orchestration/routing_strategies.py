#!/usr/bin/env python3
"""
LUKHAS Phase 4 - Routing Strategies Engine
==========================================

Implements intelligent routing strategies with health-based selection,
load balancing, A/B testing, and circuit breaker patterns.

Key Features:
- Round-robin load balancing
- Weighted routing based on provider capabilities
- Health-based routing with real-time monitoring
- Latency-optimized routing
- Cost-optimized routing
- A/B testing framework
- Circuit breaker patterns
- Hybrid routing strategies

Performance Targets:
- <100ms routing decision latency
- <250ms context handoff
- >99.9% availability through fallbacks

Constellation Framework: Flow Star (🌊) coordination hub
"""

from __future__ import annotations

import random
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from opentelemetry import trace

from observability import counter, gauge

from .routing_config import (
    HealthStatus,
    ProviderHealth,
    RoutingRule,
    RoutingStrategy,
    routing_decisions_total,
    routing_latency_seconds,
)

tracer = trace.get_tracer(__name__)

# Additional metrics for strategies
strategy_selections = counter(
    "lukhas_strategy_selections_total", "Strategy selection counts", ["strategy", "rule_name"]
)

provider_selections = counter(
    "lukhas_provider_selections_total", "Provider selection counts", ["provider", "strategy", "reason"]
)

circuit_breaker_state = gauge(
    "lukhas_circuit_breaker_state", "Circuit breaker state (0=closed, 1=open, 2=half_open)", ["provider"]
)

routing_fallback_triggered = counter(
    "lukhas_routing_fallback_triggered_total",
    "Fallback routing triggers",
    ["original_provider", "fallback_provider", "reason"],
)


@dataclass
class RoutingContext:
    """Context for routing decisions"""

    session_id: str
    request_type: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    previous_providers: List[str] = field(default_factory=list)


@dataclass
class RoutingResult:
    """Result of routing decision"""

    provider: str
    strategy_used: RoutingStrategy
    reason: str
    confidence: float
    fallback_available: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2


@dataclass
class CircuitBreaker:
    """Circuit breaker for provider resilience"""

    provider: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    timeout_duration: float = 60.0
    last_failure_time: float = 0.0
    half_open_max_calls: int = 3
    half_open_calls: int = 0


class BaseRoutingStrategy(ABC):
    """Abstract base class for routing strategies"""

    def __init__(self, name: str):
        self.name = name
        self.metrics = {"total_decisions": 0, "successful_decisions": 0, "avg_latency_ms": 0.0}

    @abstractmethod
    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:
        """Select provider based on strategy"""
        pass

    def update_metrics(self, latency_ms: float, success: bool):
        """Update strategy metrics"""
        self.metrics["total_decisions"] += 1
        if success:
            self.metrics["successful_decisions"] += 1

        # Update average latency with exponential moving average
        alpha = 0.1
        current_avg = self.metrics["avg_latency_ms"]
        self.metrics["avg_latency_ms"] = alpha * latency_ms + (1 - alpha) * current_avg


class RoundRobinStrategy(BaseRoutingStrategy):
    """Round-robin routing strategy"""

    def __init__(self):
        super().__init__("round_robin")
        self.provider_counters: Dict[str, int] = defaultdict(int)

    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:

        start_time = time.time()

        # Filter healthy and available providers
        available_providers = []
        for provider in rule.providers:
            health = provider_health.get(provider)
            breaker = circuit_breakers.get(provider)

            if (
                health
                and health.status == HealthStatus.HEALTHY
                and breaker
                and breaker.state == CircuitBreakerState.CLOSED
            ):
                available_providers.append(provider)

        if not available_providers:
            return None

        # Generate cache key for this rule
        rule_key = rule.name

        # Select next provider in round-robin fashion
        current_count = self.provider_counters[rule_key]
        selected_provider = available_providers[current_count % len(available_providers)]
        self.provider_counters[rule_key] += 1

        latency_ms = (time.time() - start_time) * 1000
        self.update_metrics(latency_ms, True)

        provider_selections.labels(
            provider=selected_provider, strategy="round_robin", reason="round_robin_selection"
        ).inc()

        return RoutingResult(
            provider=selected_provider,
            strategy_used=RoutingStrategy.ROUND_ROBIN,
            reason=f"Round-robin selection ({current_count % len(available_providers)})",
            confidence=0.8,
            fallback_available=len(available_providers) > 1,
            metadata={"position": current_count % len(available_providers)},
        )


class WeightedStrategy(BaseRoutingStrategy):
    """Weighted routing based on provider capabilities"""

    def __init__(self):
        super().__init__("weighted")

    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:

        start_time = time.time()

        if not rule.weights:
            # Fall back to round-robin if no weights specified
            fallback_strategy = RoundRobinStrategy()
            return await fallback_strategy.select_provider(rule, context, provider_health, circuit_breakers)

        # Calculate weighted selection
        available_weights = []
        available_providers = []

        for provider in rule.providers:
            health = provider_health.get(provider)
            breaker = circuit_breakers.get(provider)

            if (
                health
                and health.status == HealthStatus.HEALTHY
                and breaker
                and breaker.state == CircuitBreakerState.CLOSED
            ):

                weight = rule.weights.get(provider, 1.0)

                # Adjust weight based on health metrics
                if health.success_rate < rule.health_threshold:
                    weight *= health.success_rate

                if health.avg_latency_ms > rule.latency_threshold_ms:
                    weight *= 0.5  # Reduce weight for slow providers

                available_weights.append(weight)
                available_providers.append(provider)

        if not available_providers:
            return None

        # Weighted random selection
        total_weight = sum(available_weights)
        if total_weight == 0:
            return None

        random_value = random.uniform(0, total_weight)
        cumulative_weight = 0

        for i, weight in enumerate(available_weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                selected_provider = available_providers[i]
                break
        else:
            selected_provider = available_providers[-1]

        latency_ms = (time.time() - start_time) * 1000
        self.update_metrics(latency_ms, True)

        provider_selections.labels(provider=selected_provider, strategy="weighted", reason="weighted_selection").inc()

        return RoutingResult(
            provider=selected_provider,
            strategy_used=RoutingStrategy.WEIGHTED,
            reason=f"Weighted selection (weight: {rule.weights.get(selected_provider, 1.0)})",
            confidence=0.9,
            fallback_available=len(available_providers) > 1,
            metadata={"weight": rule.weights.get(selected_provider, 1.0)},
        )


class HealthBasedStrategy(BaseRoutingStrategy):
    """Health-based routing prioritizing healthy providers"""

    def __init__(self):
        super().__init__("health_based")

    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:

        start_time = time.time()

        # Score providers based on health metrics
        provider_scores = []

        for provider in rule.providers:
            health = provider_health.get(provider)
            breaker = circuit_breakers.get(provider)

            if not health or not breaker:
                continue

            if breaker.state != CircuitBreakerState.CLOSED:
                continue

            # Calculate health score
            score = 0.0

            # Success rate component (0-40 points)
            score += health.success_rate * 40

            # Latency component (0-30 points, inverse relationship)
            if health.avg_latency_ms > 0:
                latency_score = max(0, 30 * (1 - health.avg_latency_ms / 1000))
                score += latency_score

            # Health status component (0-30 points)
            if health.status == HealthStatus.HEALTHY:
                score += 30
            elif health.status == HealthStatus.DEGRADED:
                score += 15

            # Penalize recent failures
            if health.consecutive_failures > 0:
                score -= health.consecutive_failures * 5

            provider_scores.append((score, provider, health))

        if not provider_scores:
            return None

        # Sort by score (highest first)
        provider_scores.sort(key=lambda x: x[0], reverse=True)

        # Select best provider, but add some randomness to avoid always picking the same one
        if len(provider_scores) > 1 and provider_scores[0][0] - provider_scores[1][0] < 10:
            # Scores are close, randomly pick from top 2
            selected_idx = random.randint(0, 1)
        else:
            selected_idx = 0

        score, selected_provider, health = provider_scores[selected_idx]

        latency_ms = (time.time() - start_time) * 1000
        self.update_metrics(latency_ms, True)

        provider_selections.labels(
            provider=selected_provider, strategy="health_based", reason="health_score_selection"
        ).inc()

        return RoutingResult(
            provider=selected_provider,
            strategy_used=RoutingStrategy.HEALTH_BASED,
            reason=f"Health-based selection (score: {score:.1f})",
            confidence=min(1.0, score / 100),
            fallback_available=len(provider_scores) > 1,
            metadata={
                "health_score": score,
                "success_rate": health.success_rate,
                "avg_latency_ms": health.avg_latency_ms,
            },
        )


class LatencyBasedStrategy(BaseRoutingStrategy):
    """Latency-optimized routing"""

    def __init__(self):
        super().__init__("latency_based")

    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:

        start_time = time.time()

        # Find provider with lowest latency
        best_provider = None
        best_latency = float("inf")
        available_providers = []

        for provider in rule.providers:
            health = provider_health.get(provider)
            breaker = circuit_breakers.get(provider)

            if (
                health
                and health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
                and breaker
                and breaker.state == CircuitBreakerState.CLOSED
                and health.success_rate >= rule.health_threshold * 0.8
            ):  # Slightly lower threshold

                available_providers.append((provider, health))

                if health.avg_latency_ms < best_latency:
                    best_latency = health.avg_latency_ms
                    best_provider = provider

        if not best_provider:
            return None

        latency_ms = (time.time() - start_time) * 1000
        self.update_metrics(latency_ms, True)

        provider_selections.labels(provider=best_provider, strategy="latency_based", reason="lowest_latency").inc()

        return RoutingResult(
            provider=best_provider,
            strategy_used=RoutingStrategy.LATENCY_BASED,
            reason=f"Latency-optimized selection ({best_latency:.1f}ms)",
            confidence=0.9,
            fallback_available=len(available_providers) > 1,
            metadata={"selected_latency_ms": best_latency},
        )


class CostOptimizedStrategy(BaseRoutingStrategy):
    """Cost-optimized routing"""

    def __init__(self):
        super().__init__("cost_optimized")
        # Cost per token estimates (can be externalized to config)
        self.provider_costs = {"openai": 0.00003, "anthropic": 0.000015, "google": 0.000001, "local": 0.0}

    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:

        start_time = time.time()

        # Score providers based on cost-effectiveness
        provider_scores = []

        for provider in rule.providers:
            health = provider_health.get(provider)
            breaker = circuit_breakers.get(provider)

            if (
                health
                and health.status == HealthStatus.HEALTHY
                and breaker
                and breaker.state == CircuitBreakerState.CLOSED
                and health.success_rate >= rule.health_threshold
            ):

                cost = self.provider_costs.get(provider, 0.00002)

                # Calculate cost-effectiveness score (lower cost = higher score)
                if cost == 0:
                    cost_score = 100  # Free providers get max score
                else:
                    cost_score = min(100, 1.0 / cost * 10000)

                # Adjust for quality (success rate and latency)
                quality_factor = health.success_rate
                if health.avg_latency_ms < rule.latency_threshold_ms:
                    quality_factor *= 1.2

                final_score = cost_score * quality_factor
                provider_scores.append((final_score, provider, health, cost))

        if not provider_scores:
            return None

        # Select best cost-effectiveness
        provider_scores.sort(key=lambda x: x[0], reverse=True)
        score, selected_provider, health, cost = provider_scores[0]

        latency_ms = (time.time() - start_time) * 1000
        self.update_metrics(latency_ms, True)

        provider_selections.labels(
            provider=selected_provider, strategy="cost_optimized", reason="cost_effectiveness"
        ).inc()

        return RoutingResult(
            provider=selected_provider,
            strategy_used=RoutingStrategy.COST_OPTIMIZED,
            reason=f"Cost-optimized selection (${cost:.6f}/token)",
            confidence=0.8,
            fallback_available=len(provider_scores) > 1,
            metadata={"cost_per_token": cost, "cost_effectiveness_score": score},
        )


class HybridStrategy(BaseRoutingStrategy):
    """Hybrid strategy combining multiple approaches"""

    def __init__(self):
        super().__init__("hybrid")
        self.sub_strategies = {
            "health": HealthBasedStrategy(),
            "latency": LatencyBasedStrategy(),
            "weighted": WeightedStrategy(),
        }

    async def select_provider(
        self,
        rule: RoutingRule,
        context: RoutingContext,
        provider_health: Dict[str, ProviderHealth],
        circuit_breakers: Dict[str, CircuitBreaker],
    ) -> Optional[RoutingResult]:

        start_time = time.time()

        # Get results from multiple strategies
        results = {}
        for strategy_name, strategy in self.sub_strategies.items():
            try:
                result = await strategy.select_provider(rule, context, provider_health, circuit_breakers)
                if result:
                    results[strategy_name] = result
            except Exception:
                continue

        if not results:
            return None

        # Weighted combination of strategies
        strategy_weights = {"health": 0.5, "latency": 0.3, "weighted": 0.2}

        provider_votes = defaultdict(float)
        for strategy_name, result in results.items():
            weight = strategy_weights.get(strategy_name, 0.1)
            provider_votes[result.provider] += weight * result.confidence

        if not provider_votes:
            return None

        # Select provider with highest combined score
        selected_provider = max(provider_votes.items(), key=lambda x: x[1])[0]
        combined_confidence = provider_votes[selected_provider]

        latency_ms = (time.time() - start_time) * 1000
        self.update_metrics(latency_ms, True)

        provider_selections.labels(provider=selected_provider, strategy="hybrid", reason="hybrid_combination").inc()

        return RoutingResult(
            provider=selected_provider,
            strategy_used=RoutingStrategy.HYBRID,
            reason=f"Hybrid selection (confidence: {combined_confidence:.2f})",
            confidence=min(1.0, combined_confidence),
            fallback_available=len(provider_votes) > 1,
            metadata={"strategy_votes": dict(provider_votes), "contributing_strategies": list(results.keys())},
        )


class RoutingEngine:
    """Main routing engine orchestrating all strategies"""

    def __init__(self):
        self.strategies: Dict[RoutingStrategy, BaseRoutingStrategy] = {
            RoutingStrategy.ROUND_ROBIN: RoundRobinStrategy(),
            RoutingStrategy.WEIGHTED: WeightedStrategy(),
            RoutingStrategy.HEALTH_BASED: HealthBasedStrategy(),
            RoutingStrategy.LATENCY_BASED: LatencyBasedStrategy(),
            RoutingStrategy.COST_OPTIMIZED: CostOptimizedStrategy(),
            RoutingStrategy.HYBRID: HybridStrategy(),
        }

        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.provider_health: Dict[str, ProviderHealth] = {}

    async def route_request(
        self, rule: RoutingRule, context: RoutingContext, provider_health: Optional[Dict[str, ProviderHealth]] = None
    ) -> Optional[RoutingResult]:
        """Route request using specified strategy"""

        start_time = time.time()

        with tracer.start_span("routing_engine.route_request") as span:
            span.set_attribute("rule_name", rule.name)
            span.set_attribute("strategy", rule.strategy.value)
            span.set_attribute("session_id", context.session_id)

            try:
                # Use provided health data or internal state
                health_data = provider_health or self.provider_health

                # Get strategy
                strategy = self.strategies.get(rule.strategy)
                if not strategy:
                    raise ValueError(f"Unknown strategy: {rule.strategy}")

                # Record strategy selection
                strategy_selections.labels(strategy=rule.strategy.value, rule_name=rule.name).inc()

                # Execute strategy
                result = await strategy.select_provider(rule, context, health_data, self.circuit_breakers)

                if result:
                    # Record successful routing decision
                    routing_decisions_total.labels(
                        strategy=rule.strategy.value, provider=result.provider, success="true"
                    ).inc()

                    span.set_attribute("selected_provider", result.provider)
                    span.set_attribute("confidence", result.confidence)

                else:
                    # Try fallback providers if available
                    if rule.fallback_providers:
                        result = await self._try_fallback_providers(rule, context, health_data)

                    if not result:
                        routing_decisions_total.labels(
                            strategy=rule.strategy.value, provider="none", success="false"
                        ).inc()

                # Record latency
                latency = time.time() - start_time
                routing_latency_seconds.labels(strategy=rule.strategy.value).observe(latency)

                span.set_attribute("routing_latency_ms", latency * 1000)

                return result

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                routing_decisions_total.labels(strategy=rule.strategy.value, provider="error", success="false").inc()

                raise

    async def _try_fallback_providers(
        self, rule: RoutingRule, context: RoutingContext, provider_health: Dict[str, ProviderHealth]
    ) -> Optional[RoutingResult]:
        """Try fallback providers when primary strategy fails"""

        if not rule.fallback_providers:
            return None

        # Create fallback rule with health-based strategy
        fallback_rule = RoutingRule(
            name=f"{rule.name}_fallback",
            pattern=rule.pattern,
            strategy=RoutingStrategy.HEALTH_BASED,
            providers=rule.fallback_providers,
            health_threshold=max(0.8, rule.health_threshold - 0.1),  # Lower threshold
        )

        health_strategy = self.strategies[RoutingStrategy.HEALTH_BASED]
        result = await health_strategy.select_provider(fallback_rule, context, provider_health, self.circuit_breakers)

        if result:
            # Record fallback trigger
            routing_fallback_triggered.labels(
                original_provider="unavailable", fallback_provider=result.provider, reason="primary_strategy_failed"
            ).inc()

            result.reason = f"Fallback: {result.reason}"

        return result

    def update_circuit_breaker(self, provider: str, success: bool) -> None:
        """Update circuit breaker state based on request result"""

        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreaker(provider=provider)

        breaker = self.circuit_breakers[provider]

        if success:
            if breaker.state == CircuitBreakerState.HALF_OPEN:
                breaker.half_open_calls += 1
                if breaker.half_open_calls >= breaker.half_open_max_calls:
                    # Close circuit breaker
                    breaker.state = CircuitBreakerState.CLOSED
                    breaker.failure_count = 0
                    breaker.half_open_calls = 0
            elif breaker.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                breaker.failure_count = 0

        else:
            breaker.failure_count += 1
            breaker.last_failure_time = time.time()

            if breaker.state == CircuitBreakerState.CLOSED:
                if breaker.failure_count >= breaker.failure_threshold:
                    breaker.state = CircuitBreakerState.OPEN

            elif breaker.state == CircuitBreakerState.HALF_OPEN:
                breaker.state = CircuitBreakerState.OPEN
                breaker.half_open_calls = 0

        # Check if open circuit should move to half-open
        if (
            breaker.state == CircuitBreakerState.OPEN
            and time.time() - breaker.last_failure_time > breaker.timeout_duration
        ):
            breaker.state = CircuitBreakerState.HALF_OPEN
            breaker.half_open_calls = 0

        # Update metric
        circuit_breaker_state.labels(provider=provider).set(breaker.state.value)

    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        status = {}
        for provider, breaker in self.circuit_breakers.items():
            status[provider] = {
                "state": breaker.state.name,
                "failure_count": breaker.failure_count,
                "last_failure_time": breaker.last_failure_time,
            }
        return status


# Global routing engine instance
_routing_engine: Optional[RoutingEngine] = None


def get_routing_engine() -> RoutingEngine:
    """Get or create global routing engine"""
    global _routing_engine
    if _routing_engine is None:
        _routing_engine = RoutingEngine()
    return _routing_engine
