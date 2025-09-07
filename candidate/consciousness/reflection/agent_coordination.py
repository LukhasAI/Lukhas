import logging
import streamlit as st
logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


Decentralized Agent Coordination System
Addresses TODO 24: Dynamic Working Group Formation

This module implements a decentralized coordination system where agents can:
1. Broadcast their needs to the network
2. Discover agents with requisite skills
3. Form temporary working groups
4. Coordinate without hard-coded dependencies

The system is inherently flexible, scalable, and resilient.
"""

import asyncio
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

from .actor_system import ActorMessage, ActorRef
from .mailbox import MailboxActor, MailboxType, MessagePriority


# Extension methods for ActorRef serialization
def actorref_to_dict(self):
    """Convert ActorRef to dictionary for serialization"""
    return {"actor_id": self.actor_id, "_type": "ActorRef"}


def actorref_from_dict(data, actor_system):
    """Create ActorRef from dictionary"""
    if data.get("_type") == "ActorRef":
        return ActorRef(data["actor_id"], actor_system)
    return None


# Monkey patch ActorRef if needed
if not hasattr(ActorRef, "to_dict"):
    ActorRef.to_dict = actorref_to_dict
if not hasattr(ActorRef, "from_dict"):
    ActorRef.from_dict = staticmethod(actorref_from_dict)

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Status of a broadcasted task"""

    ANNOUNCED = "announced"
    NEGOTIATING = "negotiating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SkillLevel(Enum):
    """Proficiency level for skills"""

    NOVICE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


@dataclass
class Skill:
    """Represents an agent's capability"""

    name: str
    level: SkillLevel
    success_rate: float = 1.0
    avg_completion_time: float = 0.0
    total_tasks: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_metrics(self, success: bool, completion_time: float):
        """Update skill metrics after task completion"""
        self.total_tasks += 1
        if success:
            # Update success rate
            self.success_rate = ((self.success_rate * (self.total_tasks - 1)) + 1) / self.total_tasks
        else:
            self.success_rate = (self.success_rate * (self.total_tasks - 1)) / self.total_tasks

        # Update average completion time
        self.avg_completion_time = (
            (self.avg_completion_time * (self.total_tasks - 1)) + completion_time
        ) / self.total_tasks


@dataclass
class TaskAnnouncement:
    """Broadcast message for task needs"""

    task_id: str
    description: str
    required_skills: list[tuple[str, SkillLevel]]  # (skill_name, min_level)
    initiator: ActorRef
    deadline: Optional[float] = None
    priority: MessagePriority = MessagePriority.NORMAL
    max_group_size: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)
    announced_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if announcement has expired"""
        if self.deadline:
            return time.time() > self.deadline
        # Default 5 minute expiry
        return time.time() - self.announced_at > 300


@dataclass
class SkillOffer:
    """Response to task announcement"""

    agent_ref: ActorRef
    agent_id: str
    offered_skills: list[Skill]
    availability: float  # 0.0 to 1.0
    estimated_time: float
    cost_estimate: Optional[float] = None
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkingGroup:
    """Temporary group formed for a task"""

    group_id: str
    task: TaskAnnouncement
    leader: ActorRef
    members: dict[str, ActorRef]  # agent_id -> ref
    skills_covered: dict[str, list[str]]  # skill -> [agent_ids]
    status: TaskStatus = TaskStatus.NEGOTIATING
    formed_at: float = field(default_factory=time.time)

    def add_member(self, agent_id: str, agent_ref: ActorRef, skills: list[Skill]):
        """Add member to working group"""
        self.members[agent_id] = agent_ref
        for skill in skills:
            if skill.name in [s for s, _ in self.task.required_skills]:
                if skill.name not in self.skills_covered:
                    self.skills_covered[skill.name] = []
                self.skills_covered[skill.name].append(agent_id)

    def all_skills_covered(self) -> bool:
        """Check if all required skills are covered"""
        required = {s for s, _ in self.task.required_skills}
        covered = set(self.skills_covered.keys())
        return required.issubset(covered)


class CoordinationProtocol:
    """Protocol for agent coordination messages"""

    # Task announcements
    TASK_ANNOUNCE = "coord:task_announce"
    TASK_CANCEL = "coord:task_cancel"

    # Skill discovery
    SKILL_QUERY = "coord:skill_query"
    SKILL_OFFER = "coord:skill_offer"

    # Group formation
    GROUP_INVITE = "coord:group_invite"
    GROUP_ACCEPT = "coord:group_accept"
    GROUP_REJECT = "coord:group_reject"
    GROUP_FORMED = "coord:group_formed"

    # Task execution
    TASK_START = "coord:task_start"
    TASK_UPDATE = "coord:task_update"
    TASK_COMPLETE = "coord:task_complete"
    TASK_FAILED = "coord:task_failed"

    # Coordination
    COORD_PING = "coord:ping"
    COORD_PONG = "coord:pong"


class SkillRegistry:
    """Central registry for agent skills (could be distributed)"""

    def __init__(self):
        self._skills_by_agent: dict[str, list[Skill]] = {}
        self._agents_by_skill: dict[str, set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def register_skill(self, agent_id: str, skill: Skill):
        """Register an agent's skill"""
        async with self._lock:
            if agent_id not in self._skills_by_agent:
                self._skills_by_agent[agent_id] = []

            # Update or add skill
            existing = next(
                (s for s in self._skills_by_agent[agent_id] if s.name == skill.name),
                None,
            )
            if existing:
                self._skills_by_agent[agent_id].remove(existing)

            self._skills_by_agent[agent_id].append(skill)
            self._agents_by_skill[skill.name].add(agent_id)

    async def unregister_agent(self, agent_id: str):
        """Remove all skills for an agent"""
        async with self._lock:
            if agent_id in self._skills_by_agent:
                for skill in self._skills_by_agent[agent_id]:
                    self._agents_by_skill[skill.name].discard(agent_id)
                del self._skills_by_agent[agent_id]

    async def find_agents_with_skill(
        self, skill_name: str, min_level: SkillLevel = SkillLevel.NOVICE
    ) -> list[tuple[str, Skill]]:
        """Find agents with a specific skill"""
        async with self._lock:
            results = []
            for agent_id in self._agents_by_skill.get(skill_name, []):
                skills = self._skills_by_agent.get(agent_id, [])
                for skill in skills:
                    if skill.name == skill_name and skill.level.value >= min_level.value:
                        results.append((agent_id, skill))

            # Sort by skill level and success rate
            results.sort(key=lambda x: (x[1].level.value, x[1].success_rate), reverse=True)
            return results


class CoordinationHub(MailboxActor):
    """Central hub for coordination (can be made distributed)"""

    def __init__(self, actor_id: str = "coordination_hub"):
        super().__init__(
            actor_id,
            mailbox_type=MailboxType.PRIORITY,
            mailbox_config={"max_size": 10000},
        )

        self.skill_registry = SkillRegistry()
        self.active_announcements: dict[str, TaskAnnouncement] = {}
        self.working_groups: dict[str, WorkingGroup] = {}
        self.agent_groups: dict[str, set[str]] = defaultdict(set)  # agent_id -> group_ids

        # Register protocol handlers
        self._register_handlers()

        # Start maintenance task
        self._maintenance_task = None

    def _register_handlers(self):
        """Register message handlers"""
        self.register_handler(CoordinationProtocol.TASK_ANNOUNCE, self._handle_task_announce)
        self.register_handler(CoordinationProtocol.TASK_CANCEL, self._handle_task_cancel)
        self.register_handler(CoordinationProtocol.SKILL_OFFER, self._handle_skill_offer)
        self.register_handler(CoordinationProtocol.GROUP_INVITE, self._handle_group_invite)
        self.register_handler(CoordinationProtocol.GROUP_ACCEPT, self._handle_group_accept)
        self.register_handler(CoordinationProtocol.GROUP_REJECT, self._handle_group_reject)
        self.register_handler(CoordinationProtocol.TASK_COMPLETE, self._handle_task_complete)
        self.register_handler(CoordinationProtocol.TASK_FAILED, self._handle_task_failed)

    async def start(self, actor_system=None):
        """Start the coordination hub"""
        await super().start(actor_system)
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())

    async def stop(self):
        """Stop the coordination hub"""
        if self._maintenance_task:
            self._maintenance_task.cancel()
        await super().stop()

    async def _maintenance_loop(self):
        """Periodic maintenance tasks"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Every 30 seconds

                # Clean up expired announcements
                expired = []
                for task_id, announcement in self.active_announcements.items():
                    if announcement.is_expired():
                        expired.append(task_id)

                for task_id in expired:
                    await self._cleanup_announcement(task_id)

                # Log stats
                logger.info(
                    f"Coordination Hub Stats: "
                    f"Active announcements: {len(self.active_announcements}, "
                    f"Working groups: {len(self.working_groups}"
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance loop error: {e}")

    async def _handle_task_announce(self, msg: ActorMessage):
        """Handle task announcement"""
        try:
            # Handle ActorRef deserialization
            payload = msg.payload.copy()
            if "initiator" in payload and isinstance(payload["initiator"], dict):
                payload["initiator"] = ActorRef.from_dict(payload["initiator"], self.actor_system)

            announcement = TaskAnnouncement(**payload)

            # Store announcement
            self.active_announcements[announcement.task_id] = announcement

            # Find suitable agents
            candidates = []
            for skill_name, min_level in announcement.required_skills:
                agents = await self.skill_registry.find_agents_with_skill(skill_name, min_level)
                candidates.extend(agents)

            # Send skill queries to candidates
            contacted = set()
            for agent_id, _skill in candidates:
                if agent_id not in contacted:
                    contacted.add(agent_id)
                    agent_ref = self.actor_system.get_actor_ref(agent_id)
                    if agent_ref:
                        await agent_ref.tell(CoordinationProtocol.SKILL_QUERY, announcement.__dict__)

            # Start group formation timer
            asyncio.create_task(self._form_group_timeout(announcement.task_id))

            return {"status": "announced", "candidates": len(contacted)}

        except Exception as e:
            logger.error(f"Error handling task announcement: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_skill_offer(self, msg: ActorMessage):
        """Handle skill offer from agent"""
        try:
            # Handle ActorRef deserialization
            payload = msg.payload.copy()
            if "agent_ref" in payload and isinstance(payload["agent_ref"], dict):
                payload["agent_ref"] = ActorRef.from_dict(payload["agent_ref"], self.actor_system)

            offer = SkillOffer(**payload)
            task_id = msg.correlation_id

            if task_id not in self.active_announcements:
                return {"status": "expired"}

            announcement = self.active_announcements[task_id]

            # Check if we have a group for this task
            group = self.working_groups.get(task_id)
            if not group:
                # Create new group
                group = WorkingGroup(
                    group_id=str(uuid.uuid4()),
                    task=announcement,
                    leader=announcement.initiator,
                    members={},
                    skills_covered={},
                )
                self.working_groups[task_id] = group

            # Add to group if suitable
            if len(group.members) < announcement.max_group_size:
                group.add_member(offer.agent_id, offer.agent_ref, offer.offered_skills)

                # Send group invite
                await offer.agent_ref.tell(
                    CoordinationProtocol.GROUP_INVITE,
                    {
                        "group_id": group.group_id,
                        "task": announcement.__dict__,
                        "role": "member",
                    },
                )

                # Check if all skills covered
                if group.all_skills_covered():
                    await self._finalize_group(task_id)

            return {"status": "processed"}

        except Exception as e:
            logger.error(f"Error handling skill offer: {e}")
            return {"status": "error", "error": str(e)}

    async def _form_group_timeout(self, task_id: str, timeout: float = 30.0):
        """Timeout for group formation"""
        await asyncio.sleep(timeout)

        if task_id in self.working_groups:
            group = self.working_groups[task_id]
            if group.status == TaskStatus.NEGOTIATING:
                # Force group formation with available members
                await self._finalize_group(task_id)

    async def _finalize_group(self, task_id: str):
        """Finalize working group formation"""
        if task_id not in self.working_groups:
            return

        group = self.working_groups[task_id]
        group.status = TaskStatus.IN_PROGRESS

        # Notify all members
        for agent_id, agent_ref in group.members.items():
            self.agent_groups[agent_id].add(group.group_id)

            await agent_ref.tell(
                CoordinationProtocol.GROUP_FORMED,
                {
                    "group_id": group.group_id,
                    "members": list(group.members.keys()),
                    "leader": group.leader.actor_id,
                    "task": group.task.__dict__,
                },
            )

        # Notify initiator
        await group.leader.tell(
            CoordinationProtocol.GROUP_FORMED,
            {
                "group_id": group.group_id,
                "task_id": task_id,
                "members": list(group.members.keys()),
                "skills_covered": group.skills_covered,
            },
        )

        # Clean up announcement
        if task_id in self.active_announcements:
            del self.active_announcements[task_id]

        logger.info(f"Working group {group.group_id} formed for task {task_id} with {len(group.members} members")

    async def _handle_task_complete(self, msg: ActorMessage):
        """Handle task completion"""
        group_id = msg.payload.get("group_id")

        for task_id, group in self.working_groups.items():
            if group.group_id == group_id:
                group.status = TaskStatus.COMPLETED

                # Update skill metrics
                for agent_id in group.members:
                    if agent_id in self.agent_groups:
                        self.agent_groups[agent_id].discard(group_id)

                # Notify all members
                for agent_ref in group.members.values():
                    await agent_ref.tell(
                        CoordinationProtocol.TASK_COMPLETE,
                        {
                            "group_id": group_id,
                            "results": msg.payload.get("results", {}),
                        },
                    )

                logger.info(f"Task {task_id} completed by group {group_id}")

                # Clean up after delay
                asyncio.create_task(self._delayed_cleanup(task_id, 60))

                return {"status": "acknowledged"}

        return {"status": "group_not_found"}

    async def _handle_task_failed(self, msg: ActorMessage):
        """Handle task failure"""
        group_id = msg.payload.get("group_id")

        for task_id, group in self.working_groups.items():
            if group.group_id == group_id:
                group.status = TaskStatus.FAILED

                # Could implement retry logic here
                logger.warning(f"Task {task_id} failed in group {group_id}: {msg.payload.get('reason', 'Unknown'}")

                # Clean up
                await self._cleanup_group(task_id)

                return {"status": "acknowledged"}

        return {"status": "group_not_found"}

    async def _handle_task_cancel(self, msg: ActorMessage):
        """Handle task cancellation"""
        task_id = msg.payload.get("task_id")

        if task_id in self.active_announcements:
            await self._cleanup_announcement(task_id)

        if task_id in self.working_groups:
            await self._cleanup_group(task_id)

        return {"status": "cancelled"}

    async def _handle_group_invite(self, msg: ActorMessage):
        """Handle group invitation"""
        try:
            agent_ref = ActorRef.from_dict(msg.payload["agent_ref"], self.actor_system)
            if agent_ref:
                response = await agent_ref.ask(CoordinationProtocol.GROUP_INVITE, msg.payload)
                return response
            return {"status": "error", "reason": "agent_not_found"}
        except Exception as e:
            logger.error(f"Error handling group invite: {e}")
            return {"status": "error", "error": str(e)}

    async def _handle_group_accept(self, msg: ActorMessage):
        """Handle group acceptance from agent"""
        # Implementation depends on specific coordination needs
        return {"status": "acknowledged"}

    async def _handle_group_reject(self, msg: ActorMessage):
        """Handle group rejection from agent"""
        # Remove agent from group and find replacement
        return {"status": "acknowledged"}

    async def _cleanup_announcement(self, task_id: str):
        """Clean up expired announcement"""
        if task_id in self.active_announcements:
            announcement = self.active_announcements[task_id]

            # Notify initiator
            await announcement.initiator.tell("task_expired", {"task_id": task_id})

            del self.active_announcements[task_id]

    async def _cleanup_group(self, task_id: str):
        """Clean up working group"""
        if task_id in self.working_groups:
            group = self.working_groups[task_id]

            # Remove from agent groups
            for agent_id in group.members:
                if agent_id in self.agent_groups:
                    self.agent_groups[agent_id].discard(group.group_id)

            del self.working_groups[task_id]

    async def _delayed_cleanup(self, task_id: str, delay: float):
        """Clean up after delay"""
        await asyncio.sleep(delay)
        await self._cleanup_group(task_id)


class AutonomousAgent(MailboxActor):
    """Base class for agents that participate in coordination"""

    def __init__(self, agent_id: str, skills: Optional[list[Skill]] = None):
        super().__init__(
            agent_id,
            mailbox_type=MailboxType.PRIORITY,
            mailbox_config={"max_size": 1000},
        )

        self.skills = skills or []
        self.current_groups: dict[str, WorkingGroup] = {}
        self.task_queue: list[TaskAnnouncement] = []
        self.availability = 1.0  # Full availability

        # Coordination hub reference (would be discovered in real system)
        self.coord_hub: Optional[ActorRef] = None

        self._register_coordination_handlers()

    def _register_coordination_handlers(self):
        """Register coordination protocol handlers"""
        self.register_handler(CoordinationProtocol.SKILL_QUERY, self._handle_skill_query)
        self.register_handler(CoordinationProtocol.GROUP_INVITE, self._handle_group_invite)
        self.register_handler(CoordinationProtocol.GROUP_FORMED, self._handle_group_formed)
        self.register_handler(CoordinationProtocol.TASK_START, self._handle_task_start)
        self.register_handler(CoordinationProtocol.TASK_UPDATE, self._handle_task_update)
        self.register_handler(CoordinationProtocol.TASK_COMPLETE, self._handle_task_complete)

    def get_ref(self) -> ActorRef:
        """Get reference to this actor"""
        if hasattr(self, "actor_system") and self.actor_system:
            return ActorRef(self.actor_id, self.actor_system)
        # Fallback for testing
        return ActorRef(self.actor_id, None)

    async def announce_task(self, description: str, required_skills: list[tuple[str, SkillLevel]], **kwargs) -> str:
        """Broadcast a task need to the network"""
        task_id = str(uuid.uuid4())

        announcement = TaskAnnouncement(
            task_id=task_id,
            description=description,
            required_skills=required_skills,
            initiator=self.get_ref(),
            **kwargs,
        )

        if self.coord_hub:
            result = await self.coord_hub.ask(CoordinationProtocol.TASK_ANNOUNCE, announcement.__dict__)
            logger.info(f"Task {task_id} announced: {result}")

        return task_id

    async def register_skills(self):
        """Register agent's skills with coordination hub"""
        if not self.coord_hub:
            return

        for skill in self.skills:
            await self.coord_hub.tell("register_skill", {"agent_id": self.actor_id, "skill": skill.__dict__})

    async def _handle_skill_query(self, msg: ActorMessage):
        """Respond to skill query"""
        task_announcement = TaskAnnouncement(**msg.payload)

        # Check if we have required skills and availability
        matching_skills = []
        for required_skill, min_level in task_announcement.required_skills:
            for skill in self.skills:
                if skill.name == required_skill and skill.level.value >= min_level.value:
                    matching_skills.append(skill)

        if matching_skills and self.availability > 0.2:  # At least 20% available
            # Make offer
            offer = SkillOffer(
                agent_ref=self.get_ref(),
                agent_id=self.actor_id,
                offered_skills=matching_skills,
                availability=self.availability,
                estimated_time=self._estimate_task_time(task_announcement),
            )

            sender_ref = self.actor_system.get_actor_ref(msg.sender)
            if sender_ref:
                await sender_ref.tell(
                    CoordinationProtocol.SKILL_OFFER,
                    offer.__dict__,
                    correlation_id=task_announcement.task_id,
                )

            return {"status": "offered"}

        return {"status": "no_match"}

    async def _handle_group_invite(self, msg: ActorMessage):
        """Handle invitation to join working group"""
        group_id = msg.payload["group_id"]
        task_dict = msg.payload["task"]

        sender_ref = self.actor_system.get_actor_ref(msg.sender)
        if not sender_ref:
            return {"status": "error", "reason": "sender_not_found"}

        # Decide whether to accept (can be overridden)
        if await self._should_join_group(task_dict):
            await sender_ref.tell(
                CoordinationProtocol.GROUP_ACCEPT,
                {"group_id": group_id, "agent_id": self.actor_id},
            )
            return {"status": "accepted"}
        else:
            await sender_ref.tell(
                CoordinationProtocol.GROUP_REJECT,
                {"group_id": group_id, "agent_id": self.actor_id, "reason": "busy"},
            )
            return {"status": "rejected"}

    async def _handle_group_formed(self, msg: ActorMessage):
        """Handle notification that group is formed"""
        group_id = msg.payload["group_id"]

        # Create local group representation
        # In real implementation, would store more details
        logger.info(f"Agent {self.actor_id} joined group {group_id}")

        # Update availability
        self.availability *= 0.7  # Reduce by 30%

        return {"status": "ready"}

    async def _handle_task_start(self, msg: ActorMessage):
        """Handle task start signal"""
        # Override in subclass
        return {"status": "started"}

    async def _handle_task_update(self, msg: ActorMessage):
        """Handle task progress update"""
        # Override in subclass
        return {"status": "acknowledged"}

    async def _handle_task_complete(self, msg: ActorMessage):
        """Handle task completion"""
        msg.payload.get("group_id")

        # Update availability
        self.availability = min(1.0, self.availability * 1.3)

        # Update skill metrics based on results
        # In real implementation

        return {"status": "acknowledged"}

    async def _should_join_group(self, task_dict: dict[str, Any]) -> bool:
        """Decide whether to join a working group"""
        # Default implementation - override in subclass
        return self.availability > 0.3

    def _estimate_task_time(self, task: TaskAnnouncement) -> float:
        """Estimate time to complete task"""
        # Simple estimate based on skill metrics
        total_time = 0.0
        count = 0

        for required_skill, _ in task.required_skills:
            for skill in self.skills:
                if skill.name == required_skill and skill.avg_completion_time > 0:
                    total_time += skill.avg_completion_time
                    count += 1

        if count > 0:
            return total_time / count

        return 60.0  # Default 1 minute


# Example specialized agents


class DataProcessorAgent(AutonomousAgent):
    """Agent specialized in data processing tasks"""

    def __init__(self, agent_id: str):
        skills = [
            Skill("data_cleaning", SkillLevel.EXPERT, success_rate=0.95),
            Skill("data_transformation", SkillLevel.ADVANCED, success_rate=0.92),
            Skill("data_validation", SkillLevel.EXPERT, success_rate=0.98),
            Skill("etl_pipeline", SkillLevel.INTERMEDIATE, success_rate=0.88),
        ]
        super().__init__(agent_id, skills)

    async def _handle_task_start(self, msg: ActorMessage):
        """Handle data processing task"""
        task_type = msg.payload.get("task_type")
        data = msg.payload.get("data")

        if task_type == "clean":
            result = await self._clean_data(data)
        elif task_type == "transform":
            result = await self._transform_data(data)
        elif task_type == "validate":
            result = await self._validate_data(data)
        else:
            result = {"error": "Unknown task type"}

        # Report completion
        group_id = msg.payload.get("group_id")
        await self.coord_hub.tell(
            CoordinationProtocol.TASK_COMPLETE,
            {"group_id": group_id, "results": result},
        )

        return {"status": "completed", "result": result}

    async def _clean_data(self, data: Any) -> dict[str, Any]:
        """Clean data (placeholder)"""
        await asyncio.sleep(0.1)  # Simulate work
        return {"cleaned": True, "records": len(data) if data else 0}

    async def _transform_data(self, data: Any) -> dict[str, Any]:
        """Transform data (placeholder)"""
        await asyncio.sleep(0.2)
        return {"transformed": True}

    async def _validate_data(self, data: Any) -> dict[str, Any]:
        """Validate data (placeholder)"""
        await asyncio.sleep(0.05)
        return {"valid": True, "errors": []}


class AnalyticsAgent(AutonomousAgent):
    """Agent specialized in analytics tasks"""

    def __init__(self, agent_id: str):
        skills = [
            Skill("statistical_analysis", SkillLevel.EXPERT, success_rate=0.96),
            Skill("predictive_modeling", SkillLevel.ADVANCED, success_rate=0.89),
            Skill("anomaly_detection", SkillLevel.EXPERT, success_rate=0.94),
            Skill("report_generation", SkillLevel.INTERMEDIATE, success_rate=0.98),
        ]
        super().__init__(agent_id, skills)


class MLModelAgent(AutonomousAgent):
    """Agent specialized in ML model operations"""

    def __init__(self, agent_id: str):
        skills = [
            Skill("model_training", SkillLevel.ADVANCED, success_rate=0.91),
            Skill("model_evaluation", SkillLevel.EXPERT, success_rate=0.95),
            Skill("hyperparameter_tuning", SkillLevel.INTERMEDIATE, success_rate=0.87),
            Skill("model_deployment", SkillLevel.ADVANCED, success_rate=0.93),
        ]
        super().__init__(agent_id, skills)


# Demo function
async def demo_decentralized_coordination():
    """Demonstrate decentralized agent coordination"""
    from .actor_system import ActorSystem

    # Create actor system
    system = ActorSystem()
    await system.start()

    # Create coordination hub
    hub = await system.create_actor(CoordinationHub, "coord_hub")

    # Create specialized agents
    agents = []
    agent_types = [
        (DataProcessorAgent, "data_agent_1"),
        (DataProcessorAgent, "data_agent_2"),
        (AnalyticsAgent, "analytics_agent_1"),
        (MLModelAgent, "ml_agent_1"),
    ]

    for agent_class, agent_id in agent_types:
        agent = await system.create_actor(agent_class, agent_id)
        agents.append(agent)

        # Set coordination hub reference
        actor = system.get_actor(agent_id)
        actor.coord_hub = hub

        # Register skills
        await actor.register_skills()

    # Simulate a complex task requiring multiple skills
    agents[0]  # First agent initiates

    task_id = await system.get_actor("data_agent_1").announce_task(
        description="Process and analyze customer data for ML model training",
        required_skills=[
            ("data_cleaning", SkillLevel.INTERMEDIATE),
            ("data_validation", SkillLevel.INTERMEDIATE),
            ("statistical_analysis", SkillLevel.ADVANCED),
            ("model_training", SkillLevel.INTERMEDIATE),
        ],
        priority=MessagePriority.HIGH,
        deadline=time.time() + 300,  # 5 minutes
    )

    print(f"Task announced: {task_id}")

    # Wait for coordination
    await asyncio.sleep(5)

    # Check hub stats
    hub_actor = system.get_actor("coord_hub")
    print(f"Active announcements: {len(hub_actor.active_announcements}")
    print(f"Working groups: {len(hub_actor.working_groups}")

    # Clean up
    await system.stop()


if __name__ == "__main__":
    asyncio.run(demo_decentralized_coordination())