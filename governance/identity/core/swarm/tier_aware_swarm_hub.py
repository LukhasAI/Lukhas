"""
Tier-Aware Swarm Hub

Orchestrates identity verification colonies based on user tier levels,
manages resource allocation, and coordinates cross-tier identity migration.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from core.enhanced_swarm import EnhancedSwarmHub

# Import swarm infrastructure
from core.swarm import SwarmTask, TaskPriority
from identity.core.colonies import (
    BiometricVerificationColony,
    ConsciousnessVerificationColony,
    DreamVerificationColony,
)

# Import identity components
from identity.core.events import (
    IdentityEventPublisher,
    IdentityEventType,
    get_identity_event_publisher,
)

logger = logging.getLogger("LUKHAS_TIER_SWARM_HUB")


class VerificationDepth(Enum):
    """Verification depth levels based on tier."""

    MINIMAL = 1  # Tier 0: Basic checks
    STANDARD = 2  # Tier 1: Standard verification
    ENHANCED = 3  # Tier 2: Enhanced with multi-factor
    DEEP = 4  # Tier 3: Deep verification with behavior
    QUANTUM = 5  # Tier 4: Quantum-enhanced verification
    TRANSCENDENT = 6  # Tier 5: Full consciousness verification


@dataclass
class TierResourceAllocation:
    """Resource allocation profile for each tier."""

    tier_level: int
    max_agents: int
    priority_boost: float
    timeout_seconds: float
    parallel_colonies: int
    verification_depth: VerificationDepth
    healing_enabled: bool
    quantum_resources: bool = False
    consciousness_resources: bool = False
    dream_resources: bool = False


@dataclass
class IdentitySwarmTask(SwarmTask):
    """Extended swarm task for identity verification."""

    lambda_id: str
    tier_level: int
    verification_type: str
    required_colonies: list[str]
    verification_depth: VerificationDepth
    session_id: Optional[str] = None
    auth_context: Optional[dict[str, Any]] = None
    biometric_data: Optional[dict[str, Any]] = None
    consciousness_data: Optional[dict[str, Any]] = None
    dream_data: Optional[dict[str, Any]] = None
    tier_migration_target: Optional[int] = None


@dataclass
class ColonyOrchestration:
    """Orchestration plan for colony coordination."""

    task_id: str
    colonies: list[str]
    execution_order: list[str]
    parallel_groups: list[list[str]]
    consensus_requirements: dict[str, float]
    timeout_config: dict[str, float]
    resource_allocation: TierResourceAllocation


class TierAwareSwarmHub(EnhancedSwarmHub):
    """
    Swarm hub that orchestrates identity verification based on user tiers.
    Manages colony allocation, resource prioritization, and cross-tier migrations.
    """

    def __init__(self, hub_id: str = "identity_tier_hub"):
        super().__init__(hub_id=hub_id)

        # Colony registry
        self.colonies: dict[str, Any] = {}
        self.colony_health: dict[str, dict[str, Any]] = {}

        # Tier resource profiles
        self.tier_profiles: dict[int, TierResourceAllocation] = (
            self._initialize_tier_profiles()
        )

        # Active orchestrations
        self.active_orchestrations: dict[str, ColonyOrchestration] = {}
        self.tier_task_queues: dict[int, list[IdentitySwarmTask]] = {
            i: [] for i in range(6)
        }

        # Performance tracking
        self.tier_metrics: dict[int, dict[str, Any]] = {
            i: {"total_tasks": 0, "successful": 0, "failed": 0, "avg_duration": 0.0}
            for i in range(6)
        }

        # Event publisher
        self.event_publisher: Optional[IdentityEventPublisher] = None

        # Cross-tier migration tracking
        self.migration_requests: dict[str, dict[str, Any]] = {}
        self.migration_history: list[dict[str, Any]] = []

        logger.info(f"Tier-Aware Swarm Hub {hub_id} initialized")

    def _initialize_tier_profiles(self) -> dict[int, TierResourceAllocation]:
        """Initialize resource allocation profiles for each tier."""
        return {
            0: TierResourceAllocation(  # Guest
                tier_level=0,
                max_agents=5,
                priority_boost=1.0,
                timeout_seconds=30.0,
                parallel_colonies=1,
                verification_depth=VerificationDepth.MINIMAL,
                healing_enabled=False,
            ),
            1: TierResourceAllocation(  # Basic
                tier_level=1,
                max_agents=10,
                priority_boost=1.2,
                timeout_seconds=45.0,
                parallel_colonies=2,
                verification_depth=VerificationDepth.STANDARD,
                healing_enabled=True,
            ),
            2: TierResourceAllocation(  # Standard
                tier_level=2,
                max_agents=20,
                priority_boost=1.5,
                timeout_seconds=60.0,
                parallel_colonies=3,
                verification_depth=VerificationDepth.ENHANCED,
                healing_enabled=True,
            ),
            3: TierResourceAllocation(  # Professional
                tier_level=3,
                max_agents=50,
                priority_boost=2.0,
                timeout_seconds=90.0,
                parallel_colonies=5,
                verification_depth=VerificationDepth.DEEP,
                healing_enabled=True,
                consciousness_resources=True,
            ),
            4: TierResourceAllocation(  # Premium
                tier_level=4,
                max_agents=100,
                priority_boost=3.0,
                timeout_seconds=120.0,
                parallel_colonies=8,
                verification_depth=VerificationDepth.QUANTUM,
                healing_enabled=True,
                quantum_resources=True,
                consciousness_resources=True,
            ),
            5: TierResourceAllocation(  # Transcendent
                tier_level=5,
                max_agents=200,
                priority_boost=5.0,
                timeout_seconds=300.0,
                parallel_colonies=10,
                verification_depth=VerificationDepth.TRANSCENDENT,
                healing_enabled=True,
                quantum_resources=True,
                consciousness_resources=True,
                dream_resources=True,
            ),
        }

    async def initialize(self):
        """Initialize the hub and register colonies."""
        await super().initialize()

        # Get event publisher
        self.event_publisher = await get_identity_event_publisher()

        # Initialize and register colonies
        await self._initialize_colonies()

        # Start tier-based task scheduler
        asyncio.create_task(self._tier_task_scheduler())

        # Start colony health monitor
        asyncio.create_task(self._colony_health_monitor())

        logger.info("Tier-Aware Swarm Hub fully initialized")

    async def _initialize_colonies(self):
        """Initialize all verification colonies."""

        # Biometric verification colony (all tiers)
        bio_colony = BiometricVerificationColony("biometric_main")
        await bio_colony.initialize()
        self.colonies["biometric"] = bio_colony

        # Consciousness verification colony (tier 3+)
        consciousness_colony = ConsciousnessVerificationColony("consciousness_main")
        await consciousness_colony.initialize()
        self.colonies["consciousness"] = consciousness_colony

        # Dream verification colony (tier 5)
        dream_colony = DreamVerificationColony("dream_main")
        await dream_colony.initialize()
        self.colonies["dream"] = dream_colony

        # Initialize health tracking
        for colony_name in self.colonies:
            self.colony_health[colony_name] = {
                "status": "healthy",
                "last_check": datetime.utcnow(),
                "success_rate": 1.0,
                "active_tasks": 0,
            }

        logger.info(f"Initialized {len(self.colonies)} verification colonies")

    async def submit_identity_verification_task(
        self,
        lambda_id: str,
        tier_level: int,
        verification_type: str,
        session_id: Optional[str] = None,
        auth_data: Optional[dict[str, Any]] = None,
        priority_override: Optional[TaskPriority] = None,
    ) -> str:
        """
        Submit an identity verification task with tier-aware orchestration.
        """
        # Validate tier level
        if tier_level not in self.tier_profiles:
            raise ValueError(f"Invalid tier level: {tier_level}")

        # Get tier profile
        tier_profile = self.tier_profiles[tier_level]

        # Determine required colonies based on tier and verification type
        required_colonies = self._determine_required_colonies(
            tier_level, verification_type
        )

        # Calculate priority based on tier
        base_priority = priority_override or TaskPriority.NORMAL
        adjusted_priority = self._calculate_tier_priority(
            base_priority, tier_profile.priority_boost
        )

        # Create identity swarm task
        task = IdentitySwarmTask(
            task_id=f"id_verify_{lambda_id}_{int(datetime.utcnow().timestamp())}",
            task_type=f"identity_{verification_type}",
            priority=adjusted_priority,
            lambda_id=lambda_id,
            tier_level=tier_level,
            verification_type=verification_type,
            required_colonies=required_colonies,
            verification_depth=tier_profile.verification_depth,
            session_id=session_id,
            auth_context=auth_data,
        )

        # Add biometric/consciousness/dream data if provided
        if auth_data:
            task.biometric_data = auth_data.get("biometric_data")
            task.consciousness_data = auth_data.get("consciousness_data")
            task.dream_data = auth_data.get("dream_data")

        # Create orchestration plan
        orchestration = self._create_orchestration_plan(task, tier_profile)
        self.active_orchestrations[task.task_id] = orchestration

        # Add to tier queue
        self.tier_task_queues[tier_level].append(task)

        # Publish task submission event
        await self.event_publisher.publish_colony_event(
            IdentityEventType.SWARM_TASK_SUBMITTED,
            lambda_id=lambda_id,
            tier_level=tier_level,
            colony_id=self.hub_id,
            swarm_task_id=task.task_id,
            consensus_data={
                "verification_type": verification_type,
                "required_colonies": required_colonies,
                "verification_depth": tier_profile.verification_depth.name,
            },
        )

        # Update metrics
        self.tier_metrics[tier_level]["total_tasks"] += 1

        return task.task_id

    async def submit_tier_migration_request(
        self,
        lambda_id: str,
        current_tier: int,
        target_tier: int,
        migration_reason: str,
        verification_data: dict[str, Any],
    ) -> str:
        """
        Submit a cross-tier identity migration request.
        """
        if target_tier <= current_tier:
            raise ValueError("Target tier must be higher than current tier")

        migration_id = f"migrate_{lambda_id}_{current_tier}_to_{target_tier}_{int(datetime.utcnow().timestamp())}"

        # Create migration request
        migration_request = {
            "migration_id": migration_id,
            "lambda_id": lambda_id,
            "current_tier": current_tier,
            "target_tier": target_tier,
            "reason": migration_reason,
            "requested_at": datetime.utcnow(),
            "verification_data": verification_data,
            "status": "pending",
            "verification_tasks": [],
        }

        self.migration_requests[migration_id] = migration_request

        # Determine verification requirements for tier upgrade
        verification_tasks = []

        # Each tier upgrade requires additional verification
        for tier in range(current_tier + 1, target_tier + 1):
            self.tier_profiles[tier]

            # Create verification task for this tier level
            task_id = await self.submit_identity_verification_task(
                lambda_id=lambda_id,
                tier_level=tier,
                verification_type="tier_upgrade",
                session_id=migration_id,
                auth_data={
                    "migration_context": {
                        "from_tier": current_tier,
                        "to_tier": target_tier,
                        "current_step": tier,
                    },
                    **verification_data,
                },
                priority_override=TaskPriority.HIGH,
            )

            verification_tasks.append(
                {"tier": tier, "task_id": task_id, "status": "pending"}
            )

        migration_request["verification_tasks"] = verification_tasks

        # Publish migration event
        await self.event_publisher.publish_colony_event(
            IdentityEventType.TIER_MIGRATION_REQUESTED,
            lambda_id=lambda_id,
            tier_level=current_tier,
            colony_id=self.hub_id,
            consensus_data={
                "target_tier": target_tier,
                "migration_id": migration_id,
                "verification_steps": len(verification_tasks),
            },
        )

        return migration_id

    def _determine_required_colonies(
        self, tier_level: int, verification_type: str
    ) -> list[str]:
        """Determine which colonies are required based on tier and type."""
        required = []

        # All tiers use biometric verification
        required.append("biometric")

        # Tier 3+ adds consciousness verification
        if tier_level >= 3:
            required.append("consciousness")

        # Tier 5 adds dream verification
        if tier_level >= 5:
            required.append("dream")

        # Special cases for verification types
        if verification_type == "high_security":
            # High security always uses all available colonies for the tier
            if tier_level >= 3 and "consciousness" not in required:
                required.append("consciousness")

        return required

    def _calculate_tier_priority(
        self, base_priority: TaskPriority, priority_boost: float
    ) -> TaskPriority:
        """Calculate adjusted priority based on tier boost."""
        priority_values = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.CRITICAL: 4,
            TaskPriority.EMERGENCY: 5,
        }

        base_value = priority_values[base_priority]
        boosted_value = min(5, int(base_value * priority_boost))

        # Map back to priority enum
        for priority, value in priority_values.items():
            if value == boosted_value:
                return priority

        return base_priority

    def _create_orchestration_plan(
        self, task: IdentitySwarmTask, tier_profile: TierResourceAllocation
    ) -> ColonyOrchestration:
        """Create orchestration plan for task execution."""

        # Determine execution order based on verification depth
        if tier_profile.verification_depth == VerificationDepth.MINIMAL:
            # Simple sequential execution
            execution_order = task.required_colonies
            parallel_groups = [[colony] for colony in task.required_colonies]

        elif tier_profile.verification_depth in [
            VerificationDepth.STANDARD,
            VerificationDepth.ENHANCED,
        ]:
            # Parallel biometric, then others
            execution_order = task.required_colonies
            parallel_groups = [["biometric"]]
            if len(task.required_colonies) > 1:
                parallel_groups.append(task.required_colonies[1:])

        else:  # DEEP, QUANTUM, TRANSCENDENT
            # Full parallel execution for higher tiers
            execution_order = task.required_colonies
            parallel_groups = [task.required_colonies]

        # Set consensus requirements based on tier
        consensus_requirements = {}
        for colony in task.required_colonies:
            if task.tier_level <= 2:
                consensus_requirements[colony] = 0.51  # Simple majority
            elif task.tier_level <= 4:
                consensus_requirements[colony] = 0.67  # Two-thirds
            else:
                consensus_requirements[colony] = 0.8  # 80% for Tier 5

        # Set timeouts
        timeout_config = {
            colony: tier_profile.timeout_seconds / len(task.required_colonies)
            for colony in task.required_colonies
        }

        return ColonyOrchestration(
            task_id=task.task_id,
            colonies=task.required_colonies,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            consensus_requirements=consensus_requirements,
            timeout_config=timeout_config,
            resource_allocation=tier_profile,
        )

    async def _tier_task_scheduler(self):
        """Background task scheduler that processes tier queues."""
        while self.running:
            try:
                # Process tasks in priority order (higher tiers first)
                for tier in range(5, -1, -1):
                    queue = self.tier_task_queues[tier]
                    if queue:
                        # Get tier profile
                        tier_profile = self.tier_profiles[tier]

                        # Check resource availability
                        if self._can_allocate_resources(tier_profile):
                            task = queue.pop(0)

                            # Execute task with orchestration
                            asyncio.create_task(self._execute_orchestrated_task(task))

                await asyncio.sleep(0.1)  # Small delay between scheduling cycles

            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(1)

    async def _execute_orchestrated_task(self, task: IdentitySwarmTask):
        """Execute a task with colony orchestration."""
        orchestration = self.active_orchestrations.get(task.task_id)
        if not orchestration:
            logger.error(f"No orchestration found for task {task.task_id}")
            return

        start_time = datetime.utcnow()
        results = {}
        success = True

        try:
            # Publish execution start
            await self.event_publisher.publish_colony_event(
                IdentityEventType.SWARM_TASK_EXECUTING,
                lambda_id=task.lambda_id,
                tier_level=task.tier_level,
                colony_id=self.hub_id,
                swarm_task_id=task.task_id,
            )

            # Execute colony groups in order
            for group in orchestration.parallel_groups:
                group_tasks = []

                for colony_name in group:
                    colony = self.colonies.get(colony_name)
                    if not colony:
                        logger.error(f"Colony {colony_name} not found")
                        continue

                    # Update colony health tracking
                    self.colony_health[colony_name]["active_tasks"] += 1

                    # Execute colony-specific verification
                    if colony_name == "biometric" and task.biometric_data:
                        colony_task = colony.verify_biometric_identity(
                            lambda_id=task.lambda_id,
                            biometric_samples=task.biometric_data.get("samples", []),
                            reference_template=task.biometric_data.get("template", b""),
                            tier_level=task.tier_level,
                            session_id=task.session_id,
                        )
                    elif colony_name == "consciousness" and task.consciousness_data:
                        colony_task = colony.verify_consciousness_state(
                            lambda_id=task.lambda_id,
                            consciousness_data=task.consciousness_data,
                            tier_level=task.tier_level,
                            session_id=task.session_id,
                        )
                    elif colony_name == "dream" and task.dream_data:
                        colony_task = colony.verify_dream_authentication(
                            lambda_id=task.lambda_id,
                            dream_sequence=task.dream_data.get("sequence", []),
                            multiverse_branches=task.dream_data.get("branches", 7),
                            session_id=task.session_id,
                        )
                    else:
                        logger.warning(f"No data for colony {colony_name}")
                        continue

                    group_tasks.append(colony_task)

                # Wait for group completion with timeout
                group_timeout = max(orchestration.timeout_config.values())
                group_results = await asyncio.wait_for(
                    asyncio.gather(*group_tasks, return_exceptions=True),
                    timeout=group_timeout,
                )

                # Process results
                for i, result in enumerate(group_results):
                    colony_name = group[i] if i < len(group) else "unknown"

                    if isinstance(result, Exception):
                        logger.error(f"Colony {colony_name} error: {result}")
                        results[colony_name] = {"error": str(result)}
                        success = False
                    else:
                        results[colony_name] = result
                        if not result.verified:
                            success = False

                    # Update colony health
                    self.colony_health[colony_name]["active_tasks"] -= 1

            # Calculate overall verification result
            overall_confidence = 0.0
            if results:
                confidences = [
                    r.confidence_score
                    for r in results.values()
                    if hasattr(r, "confidence_score")
                ]
                if confidences:
                    overall_confidence = sum(confidences) / len(confidences)

            # Update tier metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._update_tier_metrics(task.tier_level, success, duration)

            # Publish completion event
            await self.event_publisher.publish_colony_event(
                IdentityEventType.SWARM_TASK_COMPLETED,
                lambda_id=task.lambda_id,
                tier_level=task.tier_level,
                colony_id=self.hub_id,
                swarm_task_id=task.task_id,
                consensus_data={
                    "success": success,
                    "overall_confidence": overall_confidence,
                    "colony_results": len(results),
                    "duration_seconds": duration,
                },
            )

            # Handle tier migration if applicable
            if task.tier_migration_target:
                await self._handle_migration_result(
                    task.task_id, success, overall_confidence
                )

        except asyncio.TimeoutError:
            logger.error(f"Task {task.task_id} timeout")
            success = False

            # Trigger healing for timeout
            await self._trigger_orchestration_healing(task.task_id, "timeout")

        except Exception as e:
            logger.error(f"Task execution error: {e}")
            success = False

        finally:
            # Cleanup orchestration
            self.active_orchestrations.pop(task.task_id, None)

    def _can_allocate_resources(self, tier_profile: TierResourceAllocation) -> bool:
        """Check if resources can be allocated for tier profile."""
        # Count active agents across all colonies
        total_active = sum(
            health["active_tasks"] for health in self.colony_health.values()
        )

        # Simple resource check - can be made more sophisticated
        return total_active < tier_profile.max_agents

    def _update_tier_metrics(self, tier_level: int, success: bool, duration: float):
        """Update metrics for a tier."""
        metrics = self.tier_metrics[tier_level]

        if success:
            metrics["successful"] += 1
        else:
            metrics["failed"] += 1

        # Update average duration
        total = metrics["successful"] + metrics["failed"]
        current_avg = metrics["avg_duration"]
        metrics["avg_duration"] = (current_avg * (total - 1) + duration) / total

    async def _handle_migration_result(
        self, task_id: str, success: bool, confidence: float
    ):
        """Handle result of a migration verification task."""
        # Find migration request containing this task
        migration_request = None
        for req in self.migration_requests.values():
            for task in req["verification_tasks"]:
                if task["task_id"] == task_id:
                    migration_request = req
                    task["status"] = "completed" if success else "failed"
                    task["confidence"] = confidence
                    break

        if not migration_request:
            return

        # Check if all tasks are complete
        all_complete = all(
            task["status"] != "pending"
            for task in migration_request["verification_tasks"]
        )

        if all_complete:
            # Determine if migration is approved
            all_successful = all(
                task["status"] == "completed"
                for task in migration_request["verification_tasks"]
            )

            avg_confidence = sum(
                task.get("confidence", 0)
                for task in migration_request["verification_tasks"]
            ) / len(migration_request["verification_tasks"])

            migration_approved = all_successful and avg_confidence >= 0.7

            # Update migration status
            migration_request["status"] = "approved" if migration_approved else "denied"
            migration_request["completed_at"] = datetime.utcnow()
            migration_request["avg_confidence"] = avg_confidence

            # Move to history
            self.migration_history.append(migration_request)
            del self.migration_requests[migration_request["migration_id"]]

            # Publish migration result
            from identity.core.events import TierChangeContext

            tier_context = TierChangeContext(
                previous_tier=migration_request["current_tier"],
                new_tier=migration_request["target_tier"],
                change_reason=migration_request["reason"],
                approval_required=True,
                approver_id="tier_aware_swarm_hub",
                benefits_delta={},
                cooldown_period=timedelta(days=30),
            )

            await self.event_publisher.publish_tier_change_event(
                lambda_id=migration_request["lambda_id"],
                tier_context=tier_context,
                approved=migration_approved,
                session_id=migration_request["migration_id"],
            )

    async def _trigger_orchestration_healing(self, task_id: str, reason: str):
        """Trigger healing for orchestration failures."""
        orchestration = self.active_orchestrations.get(task_id)
        if not orchestration:
            return

        # Publish healing event
        await self.event_publisher.publish_healing_event(
            lambda_id="system",
            tier_level=0,
            healing_reason=f"orchestration_{reason}",
            correlation_id=task_id,
            healing_strategy="COLONY_RESTART",
        )

        # Mark affected colonies for healing
        for colony_name in orchestration.colonies:
            self.colony_health[colony_name]["status"] = "healing"
            self.colony_health[colony_name]["last_failure"] = datetime.utcnow()

    async def _colony_health_monitor(self):
        """Monitor colony health and trigger healing when needed."""
        while self.running:
            try:
                for colony_name, health in self.colony_health.items():
                    colony = self.colonies.get(colony_name)
                    if not colony:
                        continue

                    # Get colony health status
                    colony_status = colony.get_colony_health_status()

                    # Update health tracking
                    health["last_check"] = datetime.utcnow()
                    health["success_rate"] = colony_status.get(
                        "performance_metrics", {}
                    ).get("success_rate", 1.0)

                    # Check if healing is needed
                    if colony_status["health_score"] < 0.6:
                        if health["status"] != "healing":
                            health["status"] = "degraded"

                            # Trigger healing
                            await self.event_publisher.publish_healing_event(
                                lambda_id="system",
                                tier_level=0,
                                healing_reason="colony_health_degraded",
                                correlation_id=colony_name,
                                healing_strategy="GRADUAL_RECOVERY",
                            )

                    elif (
                        health["status"] == "healing"
                        and colony_status["health_score"] > 0.8
                    ):
                        # Colony has recovered
                        health["status"] = "healthy"
                        logger.info(f"Colony {colony_name} recovered to healthy state")

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(5)

    def get_hub_statistics(self) -> dict[str, Any]:
        """Get comprehensive hub statistics."""
        return {
            "hub_id": self.hub_id,
            "active_orchestrations": len(self.active_orchestrations),
            "colony_health": self.colony_health,
            "tier_metrics": self.tier_metrics,
            "tier_queues": {
                tier: len(queue) for tier, queue in self.tier_task_queues.items()
            },
            "active_migrations": len(self.migration_requests),
            "migration_history_count": len(self.migration_history),
            "total_tasks_processed": sum(
                m["successful"] + m["failed"] for m in self.tier_metrics.values()
            ),
        }

    def get_tier_performance_report(self) -> dict[str, Any]:
        """Generate performance report by tier."""
        report = {}

        for tier, metrics in self.tier_metrics.items():
            total = metrics["successful"] + metrics["failed"]
            if total > 0:
                report[f"tier_{tier}"] = {
                    "total_tasks": total,
                    "success_rate": metrics["successful"] / total,
                    "avg_duration_seconds": metrics["avg_duration"],
                    "resource_allocation": {
                        "max_agents": self.tier_profiles[tier].max_agents,
                        "verification_depth": self.tier_profiles[
                            tier
                        ].verification_depth.name,
                        "parallel_colonies": self.tier_profiles[tier].parallel_colonies,
                    },
                }

        return report
