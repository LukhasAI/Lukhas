"""
Identity Health Monitor with Self-Healing

Monitors the health of all identity system components and orchestrates
self-healing procedures based on tier-specific strategies.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable

import numpy as np
import psutil

# Import self-healing components
from core.self_healing import HealingStrategy, HealthStatus, SelfHealingSystem

# Import identity components
from governance.identity.core.events import (
    IdentityEventPriority,
    IdentityEventPublisher,
    get_identity_event_publisher,
)

logger = logging.getLogger("LUKHAS_IDENTITY_HEALTH")


class ComponentType(Enum):
    """Types of identity system components."""

    COLONY = "colony"
    SWARM_HUB = "swarm_hub"
    EVENT_SYSTEM = "event_system"
    AUTH_SERVICE = "auth_service"
    TAG_RESOLVER = "tag_resolver"
    CRYPTO_ENGINE = "crypto_engine"
    STORAGE = "storage"
    NETWORK = "network"


class HealthMetric(Enum):
    """Health metrics to monitor."""

    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    RESOURCE_USAGE = "resource_usage"
    QUEUE_DEPTH = "queue_depth"
    CONNECTION_COUNT = "connection_count"
    CONSENSUS_STRENGTH = "consensus_strength"
    AGENT_HEALTH = "agent_health"


@dataclass
class ComponentHealth:
    """Health status of a system component."""

    component_id: str
    component_type: ComponentType
    status: HealthStatus
    health_score: float  # 0.0 to 1.0
    last_check: datetime
    metrics: dict[HealthMetric, float]
    error_history: deque = field(default_factory=lambda: deque(maxlen=100))
    healing_attempts: int = 0
    last_healing: datetime | None = None
    tier_specific_data: dict[int, dict[str, Any]] = field(default_factory=dict)

    def add_error(self, error: str):
        """Add error to history."""
        self.error_history.append({"timestamp": datetime.now(timezone.utc), "error": error})

    def calculate_health_score(self) -> float:
        """Calculate overall health score from metrics."""
        weights = {
            HealthMetric.ERROR_RATE: -0.3,
            HealthMetric.SUCCESS_RATE: 0.3,
            HealthMetric.RESPONSE_TIME: -0.2,
            HealthMetric.RESOURCE_USAGE: -0.1,
            HealthMetric.CONSENSUS_STRENGTH: 0.1,
        }

        score = 0.5  # Base score

        for metric, weight in weights.items():
            if metric in self.metrics:
                value = self.metrics[metric]

                # Normalize metrics to 0-1 range
                if metric == HealthMetric.ERROR_RATE:
                    normalized = min(1.0, value)  # Higher is worse
                elif metric == HealthMetric.SUCCESS_RATE:
                    normalized = value  # Already 0-1
                elif metric == HealthMetric.RESPONSE_TIME:
                    normalized = min(1.0, value / 1000)  # Convert ms, cap at 1s
                elif metric == HealthMetric.RESOURCE_USAGE or metric == HealthMetric.CONSENSUS_STRENGTH:
                    normalized = value  # Already 0-1
                else:
                    normalized = 0.5  # Default

                score += weight * normalized

        # Consider error history
        recent_errors = sum(
            1 for error in self.error_history if error["timestamp"] > datetime.now(timezone.utc) - timedelta(minutes=5)
        )
        if recent_errors > 10:
            score *= 0.8
        elif recent_errors > 5:
            score *= 0.9

        return max(0.0, min(1.0, score))


@dataclass
class HealingPlan:
    """Plan for healing a component."""

    plan_id: str
    component_id: str
    component_type: ComponentType
    strategy: HealingStrategy
    tier_level: int
    steps: list[dict[str, Any]]
    priority: IdentityEventPriority
    deadline: datetime
    dependencies: list[str] = field(default_factory=list)

    def add_step(self, action: str, params: dict[str, Any], order: int):
        """Add a healing step."""
        self.steps.append(
            {
                "order": order,
                "action": action,
                "params": params,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "result": None,
            }
        )
        self.steps.sort(key=lambda x: x["order"])


class IdentityHealthMonitor:
    """
    Comprehensive health monitoring and self-healing for identity system.
    """

    def __init__(self, monitor_id: str = "identity_health_monitor"):
        self.monitor_id = monitor_id
        self.self_healing_system = SelfHealingSystem()

        # Component health tracking
        self.component_health: dict[str, ComponentHealth] = {}
        self.health_history: list[dict[str, Any]] = []

        # Active healing plans
        self.active_healing_plans: dict[str, HealingPlan] = {}
        self.healing_history: list[HealingPlan] = []

        # Health thresholds by tier
        self.tier_thresholds = {
            0: {"critical": 0.3, "warning": 0.5, "healthy": 0.7},
            1: {"critical": 0.35, "warning": 0.55, "healthy": 0.75},
            2: {"critical": 0.4, "warning": 0.6, "healthy": 0.8},
            3: {"critical": 0.45, "warning": 0.65, "healthy": 0.85},
            4: {"critical": 0.5, "warning": 0.7, "healthy": 0.9},
            5: {"critical": 0.55, "warning": 0.75, "healthy": 0.95},
        }

        # Healing strategies by component type
        self.healing_strategies: dict[ComponentType, list[Callable]] = {
            ComponentType.COLONY: [
                self._heal_colony_restart,
                self._heal_colony_agent_replacement,
                self._heal_colony_consensus_adjustment,
            ],
            ComponentType.SWARM_HUB: [
                self._heal_swarm_task_redistribution,
                self._heal_swarm_resource_reallocation,
            ],
            ComponentType.AUTH_SERVICE: [
                self._heal_auth_cache_clear,
                self._heal_auth_session_cleanup,
            ],
        }

        # System metrics
        self.system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_latency": 0.0,
        }

        # Event publisher
        self.event_publisher: IdentityEventPublisher | None = None

        logger.info(f"Identity Health Monitor {monitor_id} initialized")

    async def initialize(self):
        """Initialize the health monitor."""
        # Get event publisher
        self.event_publisher = await get_identity_event_publisher()

        # Initialize self-healing system
        await self.self_healing_system.initialize()

        # Start monitoring tasks
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._monitor_system_health())
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._monitor_component_health())
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._execute_healing_plans())
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._analyze_health_trends())

        logger.info("Identity Health Monitor initialized")

    async def register_component(
        self,
        component_id: str,
        component_type: ComponentType,
        health_check_callback: Callable | None = None,
        tier_level: int = 0,
    ):
        """Register a component for health monitoring."""

        if component_id not in self.component_health:
            self.component_health[component_id] = ComponentHealth(
                component_id=component_id,
                component_type=component_type,
                status=HealthStatus.HEALTHY,
                health_score=1.0,
                last_check=datetime.now(timezone.utc),
                metrics={},
            )

        # Store health check callback if provided
        if health_check_callback:
            self.component_health[component_id].health_check = health_check_callback

        # Initialize tier-specific data
        self.component_health[component_id].tier_specific_data[tier_level] = {
            "registered_at": datetime.now(timezone.utc),
            "performance_baseline": {},
        }

        logger.info(f"Registered component {component_id} of type {component_type.value}")

    async def report_component_metrics(
        self, component_id: str, metrics: dict[HealthMetric, float], tier_level: int = 0
    ):
        """Report metrics for a component."""

        if component_id not in self.component_health:
            logger.warning(f"Unknown component {component_id}")
            return

        component = self.component_health[component_id]
        component.metrics.update(metrics)
        component.last_check = datetime.now(timezone.utc)

        # Update tier-specific metrics
        if tier_level not in component.tier_specific_data:
            component.tier_specific_data[tier_level] = {}

        component.tier_specific_data[tier_level]["last_metrics"] = metrics
        component.tier_specific_data[tier_level]["last_update"] = datetime.now(timezone.utc)

        # Calculate new health score
        old_score = component.health_score
        component.health_score = component.calculate_health_score()

        # Update status based on tier thresholds
        thresholds = self.tier_thresholds[min(tier_level, 5)]

        if component.health_score >= thresholds["healthy"]:
            component.status = HealthStatus.HEALTHY
        elif component.health_score >= thresholds["warning"]:
            component.status = HealthStatus.DEGRADED
        else:
            component.status = HealthStatus.CRITICAL

        # Trigger healing if needed
        if component.status == HealthStatus.CRITICAL:
            await self._trigger_component_healing(component_id, tier_level)

        # Record in history
        self.health_history.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "component_id": component_id,
                "health_score": component.health_score,
                "status": component.status.value,
                "tier_level": tier_level,
            }
        )

        # Publish health update event if significant change
        if abs(old_score - component.health_score) > 0.1:
            await self.event_publisher.publish_healing_event(
                lambda_id="system",
                tier_level=tier_level,
                healing_reason=f"health_score_change_{component_id}",
                healing_strategy=component.status.value,
            )

    async def report_component_error(
        self,
        component_id: str,
        error: str,
        severity: str = "error",
        tier_level: int = 0,
    ):
        """Report an error for a component."""

        if component_id not in self.component_health:
            logger.warning(f"Unknown component {component_id}")
            return

        component = self.component_health[component_id]
        component.add_error(f"{severity}: {error}")

        # Update error rate metric
        error_count = len(
            [e for e in component.error_history if e["timestamp"] > datetime.now(timezone.utc) - timedelta(minutes=5)]
        )
        # Errors per second over 5 minutes
        component.metrics[HealthMetric.ERROR_RATE] = error_count / 300

        # Recalculate health
        component.health_score = component.calculate_health_score()

        # Immediate healing for critical errors
        if severity == "critical" or error_count > 20:
            await self._trigger_component_healing(component_id, tier_level, priority=IdentityEventPriority.CRITICAL)

    async def _trigger_component_healing(
        self,
        component_id: str,
        tier_level: int,
        priority: IdentityEventPriority = IdentityEventPriority.HIGH,
    ):
        """Trigger healing for a component."""

        component = self.component_health.get(component_id)
        if not component:
            return

        # Check if already healing
        if component_id in self.active_healing_plans:
            logger.info(f"Component {component_id} already has active healing plan")
            return

        # Check healing cooldown
        if component.last_healing and datetime.now(timezone.utc) - component.last_healing < timedelta(minutes=5):
            logger.info(f"Component {component_id} in healing cooldown")
            return

        # Create healing plan
        plan = HealingPlan(
            plan_id=f"heal_{component_id}_{int(datetime.now(timezone.utc).timestamp())}",
            component_id=component_id,
            component_type=component.component_type,
            strategy=self._determine_healing_strategy(component, tier_level),
            tier_level=tier_level,
            steps=[],
            priority=priority,
            deadline=datetime.now(timezone.utc) + timedelta(minutes=30),
        )

        # Add healing steps based on component type
        if component.component_type in self.healing_strategies:
            for i, strategy_func in enumerate(self.healing_strategies[component.component_type]):
                steps = await strategy_func(component, tier_level)
                for step in steps:
                    plan.add_step(step["action"], step["params"], i * 10 + step.get("order", 0))

        # Add to active plans
        self.active_healing_plans[plan.plan_id] = plan
        component.healing_attempts += 1
        component.last_healing = datetime.now(timezone.utc)

        # Publish healing event
        await self.event_publisher.publish_healing_event(
            lambda_id="system",
            tier_level=tier_level,
            healing_reason="component_health_critical",
            correlation_id=plan.plan_id,
            healing_strategy=plan.strategy.value,
        )

        logger.info(f"Created healing plan {plan.plan_id} for {component_id}")

    def _determine_healing_strategy(self, component: ComponentHealth, tier_level: int) -> HealingStrategy:
        """Determine appropriate healing strategy."""

        # Tier-based strategy selection
        if tier_level <= 1:
            # Lower tiers: Simple restart
            return HealingStrategy.RESTART
        elif tier_level <= 3:
            # Mid tiers: Gradual recovery
            if component.healing_attempts < 3:
                return HealingStrategy.GRADUAL_RECOVERY
            else:
                return HealingStrategy.REDISTRIBUTE_LOAD
        else:
            # High tiers: Advanced strategies
            if component.component_type == ComponentType.COLONY:
                return HealingStrategy.REDUNDANCY_SWITCHOVER
            else:
                return HealingStrategy.SELF_REPAIR

    # Healing strategy implementations

    async def _heal_colony_restart(self, component: ComponentHealth, tier_level: int) -> list[dict[str, Any]]:
        """Restart colony healing strategy."""
        return [
            {
                "action": "stop_colony",
                "params": {"colony_id": component.component_id},
                "order": 1,
            },
            {
                "action": "clear_colony_state",
                "params": {"colony_id": component.component_id},
                "order": 2,
            },
            {
                "action": "start_colony",
                "params": {
                    "colony_id": component.component_id,
                    "tier_level": tier_level,
                },
                "order": 3,
            },
        ]

    async def _heal_colony_agent_replacement(self, component: ComponentHealth, tier_level: int) -> list[dict[str, Any]]:
        """Replace unhealthy agents in colony."""
        return [
            {
                "action": "identify_unhealthy_agents",
                "params": {"colony_id": component.component_id},
                "order": 1,
            },
            {
                "action": "spawn_replacement_agents",
                "params": {"colony_id": component.component_id, "count": 5},
                "order": 2,
            },
            {
                "action": "migrate_agent_state",
                "params": {"colony_id": component.component_id},
                "order": 3,
            },
            {
                "action": "terminate_unhealthy_agents",
                "params": {"colony_id": component.component_id},
                "order": 4,
            },
        ]

    async def _heal_colony_consensus_adjustment(
        self, component: ComponentHealth, tier_level: int
    ) -> list[dict[str, Any]]:
        """Adjust consensus parameters for better performance."""

        # Lower consensus requirements temporarily
        new_threshold = max(0.51, component.metrics.get(HealthMetric.CONSENSUS_STRENGTH, 0.67) - 0.1)

        return [
            {
                "action": "adjust_consensus_threshold",
                "params": {
                    "colony_id": component.component_id,
                    "new_threshold": new_threshold,
                    "duration_minutes": 30,
                },
                "order": 1,
            },
            {
                "action": "increase_voting_timeout",
                "params": {"colony_id": component.component_id, "multiplier": 1.5},
                "order": 2,
            },
        ]

    async def _heal_swarm_task_redistribution(
        self, component: ComponentHealth, tier_level: int
    ) -> list[dict[str, Any]]:
        """Redistribute tasks in swarm hub."""
        return [
            {
                "action": "pause_task_acceptance",
                "params": {"hub_id": component.component_id},
                "order": 1,
            },
            {
                "action": "redistribute_pending_tasks",
                "params": {
                    "hub_id": component.component_id,
                    "strategy": "load_balanced",
                },
                "order": 2,
            },
            {
                "action": "resume_task_acceptance",
                "params": {"hub_id": component.component_id},
                "order": 3,
            },
        ]

    async def _heal_swarm_resource_reallocation(
        self, component: ComponentHealth, tier_level: int
    ) -> list[dict[str, Any]]:
        """Reallocate resources in swarm hub."""
        return [
            {
                "action": "analyze_resource_usage",
                "params": {"hub_id": component.component_id},
                "order": 1,
            },
            {
                "action": "scale_agent_pool",
                "params": {
                    "hub_id": component.component_id,
                    "scale_factor": 1.2 if tier_level >= 3 else 1.1,
                },
                "order": 2,
            },
            {
                "action": "optimize_task_scheduling",
                "params": {"hub_id": component.component_id},
                "order": 3,
            },
        ]

    async def _heal_auth_cache_clear(self, component: ComponentHealth, tier_level: int) -> list[dict[str, Any]]:
        """Clear authentication caches."""
        return [
            {
                "action": "clear_session_cache",
                "params": {"service_id": component.component_id},
                "order": 1,
            },
            {
                "action": "clear_permission_cache",
                "params": {"service_id": component.component_id},
                "order": 2,
            },
            {
                "action": "rebuild_cache_indices",
                "params": {"service_id": component.component_id},
                "order": 3,
            },
        ]

    async def _heal_auth_session_cleanup(self, component: ComponentHealth, tier_level: int) -> list[dict[str, Any]]:
        """Clean up stale auth sessions."""
        return [
            {
                "action": "identify_stale_sessions",
                "params": {
                    "service_id": component.component_id,
                    "max_age_hours": 24 if tier_level <= 2 else 48,
                },
                "order": 1,
            },
            {
                "action": "terminate_stale_sessions",
                "params": {"service_id": component.component_id},
                "order": 2,
            },
            {
                "action": "compact_session_storage",
                "params": {"service_id": component.component_id},
                "order": 3,
            },
        ]

    async def _execute_healing_plans(self):
        """Execute active healing plans."""
        while True:
            try:
                completed_plans = []

                for plan_id, plan in self.active_healing_plans.items():
                    # Check deadline
                    if datetime.now(timezone.utc) > plan.deadline:
                        logger.error(f"Healing plan {plan_id} exceeded deadline")
                        completed_plans.append(plan_id)
                        continue

                    # Find next pending step
                    next_step = None
                    for step in plan.steps:
                        if step["status"] == "pending":
                            next_step = step
                            break

                    if not next_step:
                        # All steps completed
                        completed_plans.append(plan_id)
                        continue

                    # Execute step
                    try:
                        next_step["status"] = "executing"
                        next_step["started_at"] = datetime.now(timezone.utc)

                        # Execute healing action
                        result = await self._execute_healing_action(
                            next_step["action"],
                            next_step["params"],
                            plan.component_type,
                        )

                        next_step["status"] = "completed"
                        next_step["completed_at"] = datetime.now(timezone.utc)
                        next_step["result"] = result

                    except Exception as e:
                        logger.error(f"Healing step failed: {e}")
                        next_step["status"] = "failed"
                        next_step["result"] = str(e)

                        # Mark plan as failed
                        completed_plans.append(plan_id)

                # Move completed plans to history
                for plan_id in completed_plans:
                    plan = self.active_healing_plans.pop(plan_id)
                    self.healing_history.append(plan)

                    # Update component status
                    component = self.component_health.get(plan.component_id)
                    if component:
                        # Re-evaluate health after healing
                        await self._evaluate_component_health(component.component_id)

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Healing executor error: {e}")
                await asyncio.sleep(5)

    async def _execute_healing_action(self, action: str, params: dict[str, Any], component_type: ComponentType) -> Any:
        """Execute a specific healing action."""

        # This would integrate with actual component APIs
        logger.info(f"Executing healing action: {action} with params: {params}")

        # Simulate action execution
        await asyncio.sleep(0.5)

        return {"success": True, "action": action}

    async def _monitor_system_health(self):
        """Monitor overall system health metrics."""
        while True:
            try:
                # Get system metrics
                self.system_metrics["cpu_usage"] = psutil.cpu_percent() / 100
                self.system_metrics["memory_usage"] = psutil.virtual_memory().percent / 100
                self.system_metrics["disk_usage"] = psutil.disk_usage("/").percent / 100

                # Calculate network latency (simulated)
                self.system_metrics["network_latency"] = np.random.normal(50, 10)  # ms

                # Check for system-wide issues
                if self.system_metrics["cpu_usage"] > 0.9:
                    await self._trigger_system_healing("high_cpu_usage")
                elif self.system_metrics["memory_usage"] > 0.9:
                    await self._trigger_system_healing("high_memory_usage")

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"System health monitor error: {e}")
                await asyncio.sleep(10)

    async def _monitor_component_health(self):
        """Monitor individual component health."""
        while True:
            try:
                for component_id, component in self.component_health.items():
                    # Check if component has custom health check
                    if hasattr(component, "health_check"):
                        try:
                            health_data = await component.health_check()
                            if health_data:
                                await self.report_component_metrics(
                                    component_id,
                                    health_data.get("metrics", {}),
                                    health_data.get("tier_level", 0),
                                )
                        except Exception as e:
                            await self.report_component_error(component_id, f"Health check failed: {e}", "error")

                    # Check for stale components
                    if datetime.now(timezone.utc) - component.last_check > timedelta(minutes=5):
                        component.status = HealthStatus.UNKNOWN
                        logger.warning(f"Component {component_id} health check stale")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Component health monitor error: {e}")
                await asyncio.sleep(30)

    async def _analyze_health_trends(self):
        """Analyze health trends for predictive healing."""
        while True:
            try:
                # Analyze recent health history
                recent_history = [
                    h for h in self.health_history if h["timestamp"] > datetime.now(timezone.utc) - timedelta(hours=1)
                ]

                if len(recent_history) > 10:
                    # Group by component
                    component_trends = defaultdict(list)
                    for entry in recent_history:
                        component_trends[entry["component_id"]].append(entry["health_score"])

                    # Detect declining trends
                    for component_id, scores in component_trends.items():
                        if len(scores) > 5:
                            # Calculate trend
                            trend = np.polyfit(range(len(scores)), scores, 1)[0]

                            # Negative trend indicates declining health
                            if trend < -0.01:  # 1% decline per measurement
                                logger.warning(f"Declining health trend for {component_id}: {trend}")

                                # Preemptive healing for critical components
                                component = self.component_health.get(component_id)
                                if component and component.component_type in [
                                    ComponentType.COLONY,
                                    ComponentType.AUTH_SERVICE,
                                ]:
                                    await self._trigger_component_healing(
                                        component_id,
                                        0,  # Default tier
                                        IdentityEventPriority.NORMAL,
                                    )

                await asyncio.sleep(300)  # Analyze every 5 minutes

            except Exception as e:
                logger.error(f"Health trend analysis error: {e}")
                await asyncio.sleep(300)

    async def _trigger_system_healing(self, reason: str):
        """Trigger system-wide healing."""
        await self.event_publisher.publish_healing_event(
            lambda_id="system",
            tier_level=0,
            healing_reason=f"system_{reason}",
            healing_strategy="SYSTEM_OPTIMIZATION",
        )

    async def _evaluate_component_health(self, component_id: str):
        """Re-evaluate component health after healing."""
        component = self.component_health.get(component_id)
        if not component:
            return

        # Request fresh metrics
        if hasattr(component, "health_check"):
            try:
                health_data = await component.health_check()
                if health_data:
                    component.metrics.update(health_data.get("metrics", {}))
            except BaseException:
                pass

        # Recalculate health score
        component.health_score = component.calculate_health_score()

        # Update status
        if component.health_score >= 0.7:
            component.status = HealthStatus.HEALTHY
            logger.info(f"Component {component_id} recovered to healthy state")

    def get_system_health_report(self) -> dict[str, Any]:
        """Get comprehensive system health report."""

        # Calculate overall system health
        component_scores = [c.health_score for c in self.component_health.values()]
        overall_health = sum(component_scores) / len(component_scores) if component_scores else 0

        # Count components by status
        status_counts = defaultdict(int)
        for component in self.component_health.values():
            status_counts[component.status.value] += 1

        # Get active healing
        active_healing = [
            {
                "plan_id": plan.plan_id,
                "component": plan.component_id,
                "strategy": plan.strategy.value,
                "progress": (
                    sum(1 for s in plan.steps if s["status"] == "completed") / len(plan.steps) if plan.steps else 0
                ),
            }
            for plan in self.active_healing_plans.values()
        ]

        return {
            "overall_health": overall_health,
            "system_metrics": self.system_metrics,
            "component_count": len(self.component_health),
            "status_distribution": dict(status_counts),
            "active_healing_plans": len(self.active_healing_plans),
            "healing_details": active_healing,
            "total_healing_attempts": sum(c.healing_attempts for c in self.component_health.values()),
            "recent_errors": sum(len(c.error_history) for c in self.component_health.values()),
        }

    def get_component_health_details(self, component_id: str) -> dict[str, Any] | None:
        """Get detailed health information for a component."""
        component = self.component_health.get(component_id)
        if not component:
            return None

        return {
            "component_id": component.component_id,
            "component_type": component.component_type.value,
            "status": component.status.value,
            "health_score": component.health_score,
            "last_check": component.last_check.isoformat(),
            "metrics": {k.value: v for k, v in component.metrics.items()},
            "recent_errors": len(
                [e for e in component.error_history if e["timestamp"] > datetime.now(timezone.utc) - timedelta(hours=1)]
            ),
            "healing_attempts": component.healing_attempts,
            "last_healing": (component.last_healing.isoformat() if component.last_healing else None),
            "tier_data": component.tier_specific_data,
        }
