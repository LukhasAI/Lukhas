"""
T4/0.01% Excellence Traffic Router for Lane-Based Distribution

Intelligent traffic routing with A/B testing, gradual rollout, and health-aware distribution
for the LUKHAS deployment system.

Performance targets:
- Routing decision: <5ms p95
- Cache hit rate: >95%
- Zero allocation for hot paths
"""

import hashlib
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from core.logging import get_logger
from observability.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class RoutingStrategy(Enum):
    """Traffic routing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    LATENCY_BASED = "latency_based"
    HASH_BASED = "hash_based"
    CANARY = "canary"
    AB_TEST = "ab_test"


@dataclass
class RoutingTarget:
    """Target for traffic routing"""
    target_id: str
    lane: str
    weight: float = 1.0
    health_score: float = 1.0
    active_connections: int = 0
    avg_latency_ms: float = 0.0
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def effective_weight(self) -> float:
        """Calculate effective weight based on health and configuration"""
        if not self.enabled:
            return 0.0
        return self.weight * self.health_score


@dataclass
class ABTestConfig:
    """A/B test configuration"""
    test_id: str
    control_targets: list[str]
    treatment_targets: list[str]
    traffic_split: float = 0.5  # Percentage to treatment
    hash_seed: str = ""
    enabled: bool = True
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if A/B test is currently active"""
        if not self.enabled:
            return False
        now = datetime.now(timezone.utc)
        return not (self.end_time and now > self.end_time)


class TrafficRouter:
    """
    High-performance traffic router for lane-based distribution.

    Supports multiple routing strategies, A/B testing, and health-aware routing.
    """

    def __init__(
        self,
        default_strategy: RoutingStrategy = RoutingStrategy.WEIGHTED,
        enable_caching: bool = True,
        cache_ttl_seconds: int = 60
    ):
        self.default_strategy = default_strategy
        self.enable_caching = enable_caching
        self.cache_ttl_seconds = cache_ttl_seconds

        # Routing targets
        self.targets: dict[str, RoutingTarget] = {}
        self.lane_targets: dict[str, set[str]] = defaultdict(set)

        # A/B tests
        self.ab_tests: dict[str, ABTestConfig] = {}

        # Routing state
        self.round_robin_indices: dict[str, int] = defaultdict(int)
        self.routing_cache: dict[str, tuple[str, datetime]] = {}

        # Statistics
        self.routing_stats = defaultdict(lambda: {
            "requests": 0,
            "cache_hits": 0,
            "errors": 0,
            "total_latency_ms": 0.0
        })

        logger.info(
            "Traffic router initialized",
            default_strategy=default_strategy.value,
            caching_enabled=enable_caching
        )

    def add_target(self, target: RoutingTarget):
        """Add routing target"""
        self.targets[target.target_id] = target
        self.lane_targets[target.lane].add(target.target_id)

        logger.debug(
            "Routing target added",
            target_id=target.target_id,
            lane=target.lane,
            weight=target.weight
        )

    def remove_target(self, target_id: str):
        """Remove routing target"""
        if target_id in self.targets:
            target = self.targets[target_id]
            self.lane_targets[target.lane].discard(target_id)
            del self.targets[target_id]

            logger.debug("Routing target removed", target_id=target_id)

    def update_target_health(
        self,
        target_id: str,
        health_score: float,
        active_connections: Optional[int] = None,
        avg_latency_ms: Optional[float] = None
    ):
        """Update target health metrics"""
        if target_id not in self.targets:
            return

        target = self.targets[target_id]
        target.health_score = max(0.0, min(1.0, health_score))

        if active_connections is not None:
            target.active_connections = active_connections

        if avg_latency_ms is not None:
            target.avg_latency_ms = avg_latency_ms

    async def route(
        self,
        request_id: str,
        lane: Optional[str] = None,
        strategy: Optional[RoutingStrategy] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Route request to appropriate target.

        Args:
            request_id: Unique request identifier
            lane: Target lane (optional, uses all if not specified)
            strategy: Routing strategy (uses default if not specified)
            session_id: Session ID for sticky routing
            metadata: Additional routing metadata

        Returns:
            Target ID to route to, or None if no targets available
        """
        start_time = time.perf_counter()

        try:
            # Check cache if enabled
            if self.enable_caching and session_id:
                cache_key = f"{session_id}:{lane or 'all'}"
                if cache_key in self.routing_cache:
                    cached_target, cached_time = self.routing_cache[cache_key]
                    if (datetime.now(timezone.utc) - cached_time).seconds < self.cache_ttl_seconds and (cached_target in self.targets and self.targets[cached_target].enabled):
                        # Validate target still exists and is healthy
                        self.routing_stats[lane or "all"]["cache_hits"] += 1
                        return cached_target

            # Check for active A/B tests
            for ab_test in self.ab_tests.values():
                if ab_test.is_active():
                    ab_target = self._route_ab_test(request_id, ab_test)
                    if ab_target:
                        self._update_cache(session_id, lane, ab_target)
                        self._record_routing_stats(lane, start_time)
                        return ab_target

            # Get available targets
            if lane:
                available_targets = [
                    self.targets[tid] for tid in self.lane_targets.get(lane, set())
                    if self.targets[tid].enabled and self.targets[tid].effective_weight > 0
                ]
            else:
                available_targets = [
                    target for target in self.targets.values()
                    if target.enabled and target.effective_weight > 0
                ]

            if not available_targets:
                logger.warning("No available targets for routing", lane=lane)
                return None

            # Apply routing strategy
            strategy = strategy or self.default_strategy
            target = self._apply_strategy(strategy, available_targets, request_id)

            if target:
                self._update_cache(session_id, lane, target.target_id)
                self._record_routing_stats(lane, start_time)
                return target.target_id

            return None

        except Exception as e:
            logger.error("Routing error", error=str(e), request_id=request_id)
            self.routing_stats[lane or "all"]["errors"] += 1
            return None

    def _route_ab_test(
        self,
        request_id: str,
        ab_test: ABTestConfig
    ) -> Optional[str]:
        """Route request based on A/B test configuration"""
        # Generate consistent hash for request
        hash_input = f"{request_id}:{ab_test.hash_seed}".encode()
        hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)

        # Determine treatment vs control
        if (hash_value % 100) < (ab_test.traffic_split * 100):
            # Route to treatment
            targets = ab_test.treatment_targets
        else:
            # Route to control
            targets = ab_test.control_targets

        # Select from available targets
        available = [
            tid for tid in targets
            if tid in self.targets and self.targets[tid].enabled
        ]

        if available:
            return random.choice(available)

        return None

    def _apply_strategy(
        self,
        strategy: RoutingStrategy,
        targets: list[RoutingTarget],
        request_id: str
    ) -> Optional[RoutingTarget]:
        """Apply routing strategy to select target"""
        if not targets:
            return None

        if strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin(targets)
        elif strategy == RoutingStrategy.WEIGHTED:
            return self._weighted_random(targets)
        elif strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(targets)
        elif strategy == RoutingStrategy.LATENCY_BASED:
            return self._latency_based(targets)
        elif strategy == RoutingStrategy.HASH_BASED:
            return self._hash_based(targets, request_id)
        else:
            # Default to weighted random
            return self._weighted_random(targets)

    def _round_robin(self, targets: list[RoutingTarget]) -> RoutingTarget:
        """Round-robin selection"""
        key = ",".join(sorted(t.target_id for t in targets))
        index = self.round_robin_indices[key] % len(targets)
        self.round_robin_indices[key] = index + 1
        return targets[index]

    def _weighted_random(self, targets: list[RoutingTarget]) -> RoutingTarget:
        """Weighted random selection"""
        weights = [t.effective_weight for t in targets]
        total_weight = sum(weights)

        if total_weight == 0:
            return random.choice(targets)

        r = random.uniform(0, total_weight)
        cumulative = 0

        for target, weight in zip(targets, weights):
            cumulative += weight
            if r <= cumulative:
                return target

        return targets[-1]

    def _least_connections(self, targets: list[RoutingTarget]) -> RoutingTarget:
        """Select target with least active connections"""
        return min(targets, key=lambda t: t.active_connections)

    def _latency_based(self, targets: list[RoutingTarget]) -> RoutingTarget:
        """Select target with lowest latency"""
        # Filter out targets with no latency data
        with_latency = [t for t in targets if t.avg_latency_ms > 0]

        if not with_latency:
            return random.choice(targets)

        return min(with_latency, key=lambda t: t.avg_latency_ms)

    def _hash_based(
        self,
        targets: list[RoutingTarget],
        request_id: str
    ) -> RoutingTarget:
        """Consistent hash-based selection"""
        hash_value = int(hashlib.sha256(request_id.encode()).hexdigest(), 16)
        index = hash_value % len(targets)
        return targets[index]

    def _update_cache(
        self,
        session_id: Optional[str],
        lane: Optional[str],
        target_id: str
    ):
        """Update routing cache"""
        if self.enable_caching and session_id:
            cache_key = f"{session_id}:{lane or 'all'}"
            self.routing_cache[cache_key] = (target_id, datetime.now(timezone.utc))

    def _record_routing_stats(self, lane: Optional[str], start_time: float):
        """Record routing statistics"""
        duration_ms = (time.perf_counter() - start_time) * 1000
        lane_key = lane or "all"

        self.routing_stats[lane_key]["requests"] += 1
        self.routing_stats[lane_key]["total_latency_ms"] += duration_ms

        metrics.record_histogram(
            "traffic_routing_duration_ms",
            duration_ms,
            tags={"lane": lane_key}
        )

    def add_ab_test(self, ab_test: ABTestConfig):
        """Add A/B test configuration"""
        self.ab_tests[ab_test.test_id] = ab_test

        logger.info(
            "A/B test configured",
            test_id=ab_test.test_id,
            traffic_split=ab_test.traffic_split
        )

    def remove_ab_test(self, test_id: str):
        """Remove A/B test"""
        if test_id in self.ab_tests:
            del self.ab_tests[test_id]
            logger.info("A/B test removed", test_id=test_id)

    async def get_routing_metrics(self) -> dict[str, Any]:
        """Get comprehensive routing metrics"""
        metrics_data = {}

        for lane, stats in self.routing_stats.items():
            total_requests = stats["requests"]
            if total_requests > 0:
                metrics_data[lane] = {
                    "total_requests": total_requests,
                    "cache_hits": stats["cache_hits"],
                    "cache_hit_rate": stats["cache_hits"] / total_requests,
                    "errors": stats["errors"],
                    "error_rate": stats["errors"] / total_requests,
                    "avg_latency_ms": stats["total_latency_ms"] / total_requests
                }

        return {
            "lanes": metrics_data,
            "total_targets": len(self.targets),
            "healthy_targets": sum(1 for t in self.targets.values() if t.enabled),
            "active_ab_tests": sum(1 for t in self.ab_tests.values() if t.is_active()),
            "cache_size": len(self.routing_cache)
        }

    def clear_cache(self):
        """Clear routing cache"""
        self.routing_cache.clear()
        logger.debug("Routing cache cleared")
