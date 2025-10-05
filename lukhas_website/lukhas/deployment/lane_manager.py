"""
Lane Manager - Central lane assignment and coordination system for LUKHAS deployment
====================================================================================

Manages the candidate → lukhas → MATRIZ lane progression system with health-based
automatic lane switching and Constellation Framework coordination.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from ..constellation_framework import ConstellationFramework
from ..governance.guardian_integration import GuardianValidator
from ..observability.metrics import MetricsCollector


class Lane(Enum):
    """Deployment lane definitions"""
    CANDIDATE = "candidate"  # Development/Integration testing
    LUKHAS = "lukhas"       # Staging/Pre-production
    MATRIZ = "MATRIZ"       # Production with full traffic


class LaneState(Enum):
    """Lane operational states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


@dataclass
class LaneConfig:
    """Configuration for a deployment lane"""
    name: str
    max_traffic_percentage: float
    health_check_interval: int
    failover_threshold: float
    rollback_threshold: float
    feature_flags: Dict[str, bool]
    resource_limits: Dict[str, Any]
    constellation_enabled: bool = True


@dataclass
class LaneMetrics:
    """Lane performance and health metrics"""
    lane: Lane
    state: LaneState
    traffic_percentage: float
    latency_p95: float
    latency_p99: float
    error_rate: float
    throughput_rps: float
    health_score: float
    last_updated: datetime
    active_deployments: int


class LaneManager:
    """Central lane assignment and coordination system"""

    def __init__(
        self,
        constellation: ConstellationFramework,
        metrics_collector: MetricsCollector,
        guardian: GuardianValidator,
        config_path: Optional[str] = None
    ):
        self.constellation = constellation
        self.metrics_collector = metrics_collector
        self.guardian = guardian
        self.logger = logging.getLogger(f"{__name__}.LaneManager")

        # Lane state management
        self._lanes: Dict[Lane, LaneConfig] = {}
        self._lane_metrics: Dict[Lane, LaneMetrics] = {}
        self._lane_assignments: Dict[str, Lane] = {}  # service_id -> lane
        self._traffic_distribution: Dict[Lane, float] = {}

        # Control flags
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._last_health_check = {}

        # Performance tracking
        self._lane_switch_latencies = []
        self._assignment_cache: Dict[str, Tuple[Lane, float]] = {}  # service_id -> (lane, timestamp)

        # Load default configuration
        self._load_default_config()

        # Initialize metrics
        self._init_metrics()

    def _load_default_config(self):
        """Load default lane configurations"""
        self._lanes = {
            Lane.CANDIDATE: LaneConfig(
                name="candidate",
                max_traffic_percentage=10.0,
                health_check_interval=30,
                failover_threshold=0.05,  # 5% error rate
                rollback_threshold=0.10,  # 10% error rate
                feature_flags={"canary_enabled": True, "experimental_features": True},
                resource_limits={"cpu": "2", "memory": "4Gi"},
                constellation_enabled=True
            ),
            Lane.LUKHAS: LaneConfig(
                name="lukhas",
                max_traffic_percentage=50.0,
                health_check_interval=20,
                failover_threshold=0.03,  # 3% error rate
                rollback_threshold=0.05,  # 5% error rate
                feature_flags={"canary_enabled": True, "experimental_features": False},
                resource_limits={"cpu": "4", "memory": "8Gi"},
                constellation_enabled=True
            ),
            Lane.MATRIZ: LaneConfig(
                name="MATRIZ",
                max_traffic_percentage=100.0,
                health_check_interval=10,
                failover_threshold=0.01,  # 1% error rate
                rollback_threshold=0.02,  # 2% error rate
                feature_flags={"canary_enabled": False, "experimental_features": False},
                resource_limits={"cpu": "8", "memory": "16Gi"},
                constellation_enabled=True
            )
        }

        # Initialize traffic distribution
        self._traffic_distribution = {
            Lane.CANDIDATE: 0.0,
            Lane.LUKHAS: 0.0,
            Lane.MATRIZ: 100.0
        }

    def _init_metrics(self):
        """Initialize metrics collection"""
        self.metrics_collector.register_histogram(
            "lane_assignment_latency_seconds",
            "Lane assignment operation latency",
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )

        self.metrics_collector.register_counter(
            "lane_assignments_total",
            "Total lane assignments performed",
            labels=["lane", "service_type"]
        )

        self.metrics_collector.register_gauge(
            "lane_health_score",
            "Current health score for each lane",
            labels=["lane"]
        )

        self.metrics_collector.register_gauge(
            "lane_traffic_percentage",
            "Current traffic percentage for each lane",
            labels=["lane"]
        )

        self.metrics_collector.register_counter(
            "lane_switches_total",
            "Total lane switches performed",
            labels=["from_lane", "to_lane", "reason"]
        )

    async def start(self):
        """Start the lane manager"""
        if self._running:
            return

        self.logger.info("Starting Lane Manager")
        self._running = True

        # Initialize lane metrics
        for lane in Lane:
            self._lane_metrics[lane] = LaneMetrics(
                lane=lane,
                state=LaneState.HEALTHY,
                traffic_percentage=self._traffic_distribution[lane],
                latency_p95=0.0,
                latency_p99=0.0,
                error_rate=0.0,
                throughput_rps=0.0,
                health_score=1.0,
                last_updated=datetime.now(),
                active_deployments=0
            )

        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        # Register with Constellation Framework
        if self.constellation:
            await self.constellation.register_component(
                "lane_manager",
                self,
                health_check=self._health_check
            )

        self.logger.info("Lane Manager started successfully")

    async def stop(self):
        """Stop the lane manager"""
        if not self._running:
            return

        self.logger.info("Stopping Lane Manager")
        self._running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Lane Manager stopped")

    async def assign_service_to_lane(
        self,
        service_id: str,
        service_type: str,
        preferred_lane: Optional[Lane] = None,
        force: bool = False
    ) -> Lane:
        """
        Assign a service to the most appropriate lane

        Args:
            service_id: Unique service identifier
            service_type: Type of service (identity, memory, consciousness, etc.)
            preferred_lane: Preferred lane if available
            force: Force assignment even if lane is unhealthy

        Returns:
            Assigned lane
        """
        start_time = time.time()

        try:
            # Check cache first for performance
            if service_id in self._assignment_cache and not force:
                lane, timestamp = self._assignment_cache[service_id]
                if time.time() - timestamp < 60:  # 1 minute cache
                    return lane

            # Validate with Guardian
            assignment_context = {
                "service_id": service_id,
                "service_type": service_type,
                "preferred_lane": preferred_lane.value if preferred_lane else None,
                "current_metrics": {lane.value: asdict(metrics)
                                 for lane, metrics in self._lane_metrics.items()}
            }

            guardian_result = await self.guardian.validate_action_async(
                "lane_assignment",
                assignment_context,
                timeout=5.0
            )

            if not guardian_result.allowed:
                self.logger.warning(f"Guardian blocked lane assignment: {guardian_result.reason}")
                # Fall back to MATRIZ as safest option
                assigned_lane = Lane.MATRIZ
            else:
                # Determine best lane
                assigned_lane = await self._determine_optimal_lane(
                    service_type, preferred_lane, force
                )

            # Update assignment
            self._lane_assignments[service_id] = assigned_lane
            self._assignment_cache[service_id] = (assigned_lane, time.time())

            # Record metrics
            latency = time.time() - start_time
            self._lane_switch_latencies.append(latency)

            self.metrics_collector.record_histogram(
                "lane_assignment_latency_seconds", latency
            )
            self.metrics_collector.increment_counter(
                "lane_assignments_total",
                labels={"lane": assigned_lane.value, "service_type": service_type}
            )

            # Constellation Framework integration
            if self.constellation:
                await self.constellation.coordinate_assignment(
                    service_id, assigned_lane.value, service_type
                )

            self.logger.info(
                f"Assigned service {service_id} ({service_type}) to lane {assigned_lane.value}"
            )

            return assigned_lane

        except Exception as e:
            self.logger.error(f"Error assigning service to lane: {e}")
            self.metrics_collector.increment_counter("lane_assignment_errors_total")
            # Default to MATRIZ for safety
            return Lane.MATRIZ

    async def _determine_optimal_lane(
        self,
        service_type: str,
        preferred_lane: Optional[Lane],
        force: bool
    ) -> Lane:
        """Determine the optimal lane for a service"""

        # If preferred lane is specified and healthy, use it
        if preferred_lane and (force or self._is_lane_healthy(preferred_lane)):
            return preferred_lane

        # Service type specific logic
        if service_type in ["identity", "auth", "session"]:
            # Identity services prefer stability
            if self._is_lane_healthy(Lane.MATRIZ):
                return Lane.MATRIZ
            elif self._is_lane_healthy(Lane.LUKHAS):
                return Lane.LUKHAS

        elif service_type in ["memory", "consciousness"]:
            # Memory/consciousness can use staging
            if self._is_lane_healthy(Lane.LUKHAS):
                return Lane.LUKHAS
            elif self._is_lane_healthy(Lane.MATRIZ):
                return Lane.MATRIZ

        elif service_type in ["experimental", "canary"]:
            # Experimental features use candidate lane
            if self._is_lane_healthy(Lane.CANDIDATE):
                return Lane.CANDIDATE

        # Fallback to healthiest lane
        return self._get_healthiest_lane()

    def _is_lane_healthy(self, lane: Lane) -> bool:
        """Check if a lane is healthy"""
        if lane not in self._lane_metrics:
            return False

        metrics = self._lane_metrics[lane]
        config = self._lanes[lane]

        # Check various health indicators
        return (
            metrics.state in [LaneState.HEALTHY, LaneState.DEGRADED] and
            metrics.error_rate < config.failover_threshold and
            metrics.health_score > 0.7
        )

    def _get_healthiest_lane(self) -> Lane:
        """Get the lane with the best health score"""
        healthiest_lane = Lane.MATRIZ
        best_score = 0.0

        for lane, metrics in self._lane_metrics.items():
            if metrics.health_score > best_score and self._is_lane_healthy(lane):
                best_score = metrics.health_score
                healthiest_lane = lane

        return healthiest_lane

    async def get_lane_assignment(self, service_id: str) -> Optional[Lane]:
        """Get current lane assignment for a service"""
        return self._lane_assignments.get(service_id)

    async def update_traffic_distribution(self, distribution: Dict[Lane, float]):
        """Update traffic distribution across lanes"""
        total = sum(distribution.values())
        if abs(total - 100.0) > 0.1:
            raise ValueError(f"Traffic distribution must sum to 100%, got {total}")

        old_distribution = self._traffic_distribution.copy()
        self._traffic_distribution = distribution.copy()

        # Update metrics
        for lane, percentage in distribution.items():
            self.metrics_collector.set_gauge(
                "lane_traffic_percentage",
                percentage,
                labels={"lane": lane.value}
            )

            if lane in self._lane_metrics:
                self._lane_metrics[lane].traffic_percentage = percentage

        # Log changes
        changes = []
        for lane in Lane:
            old = old_distribution.get(lane, 0.0)
            new = distribution.get(lane, 0.0)
            if abs(old - new) > 0.1:
                changes.append(f"{lane.value}: {old:.1f}% -> {new:.1f}%")

        if changes:
            self.logger.info(f"Traffic distribution updated: {', '.join(changes)}")

    async def force_lane_switch(
        self,
        from_lane: Lane,
        to_lane: Lane,
        reason: str = "manual"
    ) -> bool:
        """Force traffic switch from one lane to another"""
        try:
            # Validate lanes exist and target is healthy
            if not self._is_lane_healthy(to_lane) and reason != "emergency":
                self.logger.warning(f"Cannot switch to unhealthy lane {to_lane.value}")
                return False

            # Get services currently assigned to from_lane
            services_to_switch = [
                service_id for service_id, lane in self._lane_assignments.items()
                if lane == from_lane
            ]

            # Reassign services
            switched_count = 0
            for service_id in services_to_switch:
                old_assignment = self._lane_assignments.get(service_id)
                if old_assignment == from_lane:
                    self._lane_assignments[service_id] = to_lane
                    # Clear cache
                    if service_id in self._assignment_cache:
                        del self._assignment_cache[service_id]
                    switched_count += 1

            # Update metrics
            self.metrics_collector.increment_counter(
                "lane_switches_total",
                labels={
                    "from_lane": from_lane.value,
                    "to_lane": to_lane.value,
                    "reason": reason
                }
            )

            self.logger.info(
                f"Switched {switched_count} services from {from_lane.value} "
                f"to {to_lane.value} (reason: {reason})"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error during lane switch: {e}")
            return False

    async def _monitoring_loop(self):
        """Main monitoring loop for lane health"""
        while self._running:
            try:
                await self._update_lane_metrics()
                await self._check_lane_health()
                await self._perform_automatic_switching()
                await asyncio.sleep(10)  # Check every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Back off on errors

    async def _update_lane_metrics(self):
        """Update metrics for all lanes"""
        for lane in Lane:
            try:
                # Collect metrics from various sources
                latency_p95 = await self._get_lane_latency(lane, 95)
                latency_p99 = await self._get_lane_latency(lane, 99)
                error_rate = await self._get_lane_error_rate(lane)
                throughput = await self._get_lane_throughput(lane)

                # Calculate health score
                health_score = self._calculate_health_score(lane, error_rate, latency_p95)

                # Determine state
                state = self._determine_lane_state(error_rate, health_score, lane)

                # Update metrics
                if lane in self._lane_metrics:
                    metrics = self._lane_metrics[lane]
                    metrics.latency_p95 = latency_p95
                    metrics.latency_p99 = latency_p99
                    metrics.error_rate = error_rate
                    metrics.throughput_rps = throughput
                    metrics.health_score = health_score
                    metrics.state = state
                    metrics.last_updated = datetime.now()

                # Update Prometheus metrics
                self.metrics_collector.set_gauge(
                    "lane_health_score",
                    health_score,
                    labels={"lane": lane.value}
                )

            except Exception as e:
                self.logger.error(f"Error updating metrics for lane {lane.value}: {e}")

    async def _get_lane_latency(self, lane: Lane, percentile: int) -> float:
        """Get latency percentile for a lane"""
        # This would integrate with actual metrics collection
        # For now, return simulated values based on lane type
        base_latency = {
            Lane.CANDIDATE: 0.05,  # Higher latency in dev
            Lane.LUKHAS: 0.03,     # Medium latency in staging
            Lane.MATRIZ: 0.02      # Lower latency in production
        }.get(lane, 0.05)

        multiplier = 1.2 if percentile == 95 else 1.5
        return base_latency * multiplier

    async def _get_lane_error_rate(self, lane: Lane) -> float:
        """Get error rate for a lane"""
        # Simulated error rates - would integrate with real metrics
        return {
            Lane.CANDIDATE: 0.02,  # 2% error rate in dev
            Lane.LUKHAS: 0.01,     # 1% error rate in staging
            Lane.MATRIZ: 0.005     # 0.5% error rate in production
        }.get(lane, 0.01)

    async def _get_lane_throughput(self, lane: Lane) -> float:
        """Get throughput for a lane"""
        # Simulated throughput - would integrate with real metrics
        return {
            Lane.CANDIDATE: 10.0,   # 10 RPS
            Lane.LUKHAS: 50.0,      # 50 RPS
            Lane.MATRIZ: 100.0      # 100 RPS
        }.get(lane, 10.0)

    def _calculate_health_score(self, lane: Lane, error_rate: float, latency: float) -> float:
        """Calculate overall health score for a lane"""
        config = self._lanes[lane]

        # Error rate component (0-1, higher is better)
        error_score = max(0.0, 1.0 - (error_rate / config.rollback_threshold))

        # Latency component (0-1, higher is better)
        target_latency = 0.05  # 50ms target
        latency_score = max(0.0, 1.0 - (latency - target_latency) / target_latency)

        # Weighted combination
        health_score = (error_score * 0.7 + latency_score * 0.3)
        return max(0.0, min(1.0, health_score))

    def _determine_lane_state(self, error_rate: float, health_score: float, lane: Lane) -> LaneState:
        """Determine lane state based on metrics"""
        config = self._lanes[lane]

        if error_rate > config.rollback_threshold:
            return LaneState.UNHEALTHY
        elif error_rate > config.failover_threshold or health_score < 0.7:
            return LaneState.DEGRADED
        else:
            return LaneState.HEALTHY

    async def _check_lane_health(self):
        """Check lane health and log issues"""
        for lane, metrics in self._lane_metrics.items():
            if metrics.state == LaneState.UNHEALTHY:
                self.logger.error(
                    f"Lane {lane.value} is UNHEALTHY: "
                    f"error_rate={metrics.error_rate:.3f}, "
                    f"health_score={metrics.health_score:.3f}"
                )
            elif metrics.state == LaneState.DEGRADED:
                self.logger.warning(
                    f"Lane {lane.value} is DEGRADED: "
                    f"error_rate={metrics.error_rate:.3f}, "
                    f"health_score={metrics.health_score:.3f}"
                )

    async def _perform_automatic_switching(self):
        """Perform automatic lane switching based on health"""
        for lane in [Lane.CANDIDATE, Lane.LUKHAS]:  # Don't auto-switch MATRIZ
            metrics = self._lane_metrics[lane]

            if metrics.state == LaneState.UNHEALTHY:
                # Find services in unhealthy lane
                affected_services = [
                    service_id for service_id, assigned_lane in self._lane_assignments.items()
                    if assigned_lane == lane
                ]

                if affected_services:
                    # Find target lane
                    target_lane = self._get_healthiest_lane()
                    if target_lane != lane:
                        await self.force_lane_switch(
                            lane, target_lane, "automatic_health_failover"
                        )

    async def _health_check(self) -> Dict[str, Any]:
        """Health check for Constellation Framework"""
        return {
            "status": "healthy" if self._running else "stopped",
            "lanes": len(self._lanes),
            "active_assignments": len(self._lane_assignments),
            "avg_assignment_latency": (
                sum(self._lane_switch_latencies[-100:]) / len(self._lane_switch_latencies[-100:])
                if self._lane_switch_latencies else 0.0
            ),
            "lane_states": {
                lane.value: metrics.state.value
                for lane, metrics in self._lane_metrics.items()
            }
        }

    async def get_deployment_status(self) -> Dict[str, Any]:
        """Get comprehensive deployment status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "lanes": {
                lane.value: {
                    "config": asdict(config),
                    "metrics": asdict(metrics) if lane in self._lane_metrics else None,
                    "assignments": len([
                        s for s, l in self._lane_assignments.items() if l == lane
                    ])
                }
                for lane, config in self._lanes.items()
            },
            "traffic_distribution": self._traffic_distribution,
            "total_services": len(self._lane_assignments),
            "performance": {
                "avg_assignment_latency": (
                    sum(self._lane_switch_latencies[-100:]) / len(self._lane_switch_latencies[-100:])
                    if self._lane_switch_latencies else 0.0
                )
            }
        }

    @asynccontextmanager
    async def lane_assignment_context(self, service_id: str, service_type: str):
        """Context manager for temporary lane assignments"""
        original_lane = await self.get_lane_assignment(service_id)
        temp_lane = await self.assign_service_to_lane(service_id, service_type)

        try:
            yield temp_lane
        finally:
            if original_lane:
                self._lane_assignments[service_id] = original_lane
            elif service_id in self._lane_assignments:
                del self._lane_assignments[service_id]
