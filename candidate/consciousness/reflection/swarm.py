"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


Enhanced Swarm System with Real Agent Behaviors
Integrated with Colony Coherence Upgrade
Fixes the current implementation gaps and aligns with BaseColony infrastructure
"""

import asyncio
import logging
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Union

import numpy as np

from candidate.core.actor_system import Actor
from candidate.core.common import get_logger
from candidate.core.distributed_tracing import AIAgentTracer, get_global_tracer

# Import BaseColony infrastructure for coherence
try:
    from candidate.core.colonies.base_colony import BaseColony

    BASE_COLONY_AVAILABLE = True
except ImportError:
    BASE_COLONY_AVAILABLE = False
    BaseColony = object

logger = get_logger(__name__)


class AgentState(Enum):
    """Agent lifecycle states."""

    IDLE = "idle"
    WORKING = "working"
    COLLABORATING = "collaborating"
    LEARNING = "learning"
    FATIGUED = "fatigued"
    FAILED = "failed"


class MessageType(Enum):
    """Types of messages agents can exchange."""

    TASK = "task"
    REQUEST_HELP = "request_help"
    OFFER_HELP = "offer_help"
    SHARE_KNOWLEDGE = "share_knowledge"
    SYNC_STATE = "sync_state"
    HEARTBEAT = "heartbeat"
    VOTE = "vote"
    CONSENSUS = "consensus"


@dataclass
class AgentCapability:
    """Represents an agent's capability."""

    name: str
    proficiency: float = 0.5  # 0.0 to 1.0
    experience: int = 0
    success_rate: float = 0.5


@dataclass
class AgentMemory:
    """Local memory for an agent."""

    short_term: deque = field(default_factory=lambda: deque(maxlen=100))
    long_term: dict[str, Any] = field(default_factory=dict)
    shared_knowledge: dict[str, Any] = field(default_factory=dict)

    def remember(self, key: str, value: Any, term: str = "short"):
        """Store a memory."""
        if term == "short":
            self.short_term.append((key, value, time.time()))
        else:
            self.long_term[key] = value

    def recall(self, key: str) -> Optional[Any]:
        """Recall a memory."""
        # Check short term first
        for k, v, _ in reversed(self.short_term):
            if k == key:
                return v
        # Then long term
        return self.long_term.get(key)


class EnhancedSwarmAgent(Actor):
    """
    Enhanced SwarmAgent with real behaviors and capabilities.
    """

    def __init__(self, agent_id: str, colony: "EnhancedColony", capabilities: list[str] = None):
        super().__init__(agent_id)
        self.agent_id = agent_id
        self.colony = colony
        self.state = AgentState.IDLE
        self.energy = 1.0  # 0.0 to 1.0
        self.memory = AgentMemory()

        # Initialize capabilities
        self.capabilities: dict[str, AgentCapability] = {}
        for cap in capabilities or ["general"]:
            self.capabilities[cap] = AgentCapability(name=cap)

        # Communication
        self.neighbors: set[str] = set()  # Direct connections
        self.trust_scores: dict[str, float] = {}  # Trust in other agents

        # Learning
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.3

        # Metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.collaborations = 0

        self.tracer = AIAgentTracer(f"agent-{self.agent_id}", get_global_tracer().collector)

    def receive(self, message: dict[str, Any]):
        """Handle incoming messages."""
        with self.tracer.trace_agent_operation(self.agent_id, "receive_message"):
            asyncio.create_task(self._handle_message(message))

    async def _handle_message(self, message: dict[str, Any]):
        """Process different message types."""
        msg_type = message.get("type", MessageType.TASK.value)
        sender = message.get("sender", "unknown")

        try:
            if msg_type == MessageType.TASK.value:
                await self._handle_task(message)
            elif msg_type == MessageType.REQUEST_HELP.value:
                await self._handle_help_request(message)
            elif msg_type == MessageType.OFFER_HELP.value:
                await self._handle_help_offer(message)
            elif msg_type == MessageType.SHARE_KNOWLEDGE.value:
                await self._handle_knowledge_share(message)
            elif msg_type == MessageType.VOTE.value:
                await self._handle_vote_request(message)
            elif msg_type == MessageType.HEARTBEAT.value:
                await self._handle_heartbeat(message)

            # Update trust based on interaction
            self._update_trust(sender, success=True)

        except Exception as e:
            logger.error(f"Agent {self.agent_id} error handling message: {e}")
            self._update_trust(sender, success=False)

    async def _handle_task(self, message: dict[str, Any]):
        """Handle task assignment."""
        task = message.get("task", {})
        task_type = task.get("type", "unknown")

        # Check if we can handle this task
        can_handle, capability = self._can_handle_task(task_type)

        if not can_handle:
            # Request help from neighbors
            await self._request_help(task)
            return

        # Check energy level
        if self.energy < 0.2:
            self.state = AgentState.FATIGUED
            await self._delegate_task(task)
            return

        # Execute task
        self.state = AgentState.WORKING
        success = await self._execute_task(task, capability)

        # Update metrics
        if success:
            self.tasks_completed += 1
            capability.experience += 1
            capability.success_rate = capability.success_rate * 0.9 + 1.0 * 0.1  # EMA
        else:
            self.tasks_failed += 1
            capability.success_rate = capability.success_rate * 0.9 + 0.0 * 0.1

        # Learn from experience
        await self._learn_from_task(task, success)

        # Update energy
        self.energy = max(0, self.energy - 0.1)

        self.state = AgentState.IDLE

    def _can_handle_task(self, task_type: str) -> tuple[bool, Optional[AgentCapability]]:
        """Check if agent can handle a task type."""
        # Direct capability match
        if task_type in self.capabilities:
            cap = self.capabilities[task_type]
            return cap.proficiency > self.adaptation_threshold, cap

        # Check for related capabilities
        for cap_name, cap in self.capabilities.items():
            if self._are_capabilities_related(cap_name, task_type):
                return (
                    cap.proficiency > self.adaptation_threshold * 1.5,
                    cap,
                )  # Higher threshold

        return False, None

    def _are_capabilities_related(self, cap1: str, cap2: str) -> bool:
        """Check if two capabilities are related."""
        # Simple heuristic - can be made more sophisticated
        related_pairs = [
            ("reasoning", "analysis"),
            ("memory", "storage"),
            ("creativity", "generation"),
            ("ethics", "governance"),
        ]

        for pair in related_pairs:
            if (
                (cap1 in pair and cap2 in pair)
                or (cap1.startswith(pair[0]) and cap2.startswith(pair[1]))
                or (cap1.startswith(pair[1]) and cap2.startswith(pair[0]))
            ):
                return True

        return False

    async def _execute_task(self, task: dict[str, Any], capability: AgentCapability) -> bool:
        """Execute a task using the given capability."""
        # Simulate task execution with success probability based on capability
        execution_time = random.uniform(0.1, 0.5)
        await asyncio.sleep(execution_time)

        # Success probability based on proficiency and energy
        success_prob = capability.proficiency * self.energy
        success = random.random() < success_prob

        # Store result in memory
        self.memory.remember(
            f"task_{task.get('id', 'unknown')}",
            {
                "task": task,
                "success": success,
                "capability_used": capability.name,
                "execution_time": execution_time,
            },
        )

        return success

    async def _request_help(self, task: dict[str, Any]):
        """Request help from neighbors."""
        self.state = AgentState.COLLABORATING

        help_request = {
            "type": MessageType.REQUEST_HELP.value,
            "sender": self.agent_id,
            "task": task,
            "required_capability": task.get("type"),
            "urgency": task.get("priority", 0.5),
        }

        # Broadcast to neighbors
        for neighbor in self.neighbors:
            await self.colony.send_agent_message(neighbor, help_request)

        self.collaborations += 1

    async def _handle_help_request(self, message: dict[str, Any]):
        """Handle help request from another agent."""
        sender = message.get("sender")
        task = message.get("task", {})
        required_cap = message.get("required_capability")

        # Check if we can help
        can_help, capability = self._can_handle_task(required_cap)

        if can_help and self.energy > 0.3 and self.state == AgentState.IDLE:
            # Offer help
            offer = {
                "type": MessageType.OFFER_HELP.value,
                "sender": self.agent_id,
                "task_id": task.get("id"),
                "capability": capability.name,
                "proficiency": capability.proficiency,
                "availability": self.energy,
            }

            await self.colony.send_agent_message(sender, offer)

    async def _learn_from_task(self, task: dict[str, Any], success: bool):
        """Learn from task execution."""
        self.state = AgentState.LEARNING

        task_type = task.get("type", "unknown")

        # Update or create capability
        if task_type not in self.capabilities:
            # Learn new capability
            self.capabilities[task_type] = AgentCapability(name=task_type, proficiency=0.1 if success else 0.05)
        else:
            # Improve existing capability
            cap = self.capabilities[task_type]
            if success:
                cap.proficiency = min(1.0, cap.proficiency + self.learning_rate)
            else:
                cap.proficiency = max(0.0, cap.proficiency - self.learning_rate * 0.5)

        self.state = AgentState.IDLE

    def _update_trust(self, agent_id: str, success: bool):
        """Update trust score for another agent."""
        if agent_id not in self.trust_scores:
            self.trust_scores[agent_id] = 0.5

        if success:
            self.trust_scores[agent_id] = min(1.0, self.trust_scores[agent_id] + 0.05)
        else:
            self.trust_scores[agent_id] = max(0.0, self.trust_scores[agent_id] - 0.1)

    async def share_knowledge(self, knowledge_type: str, knowledge: Any):
        """Share knowledge with neighbors."""
        message = {
            "type": MessageType.SHARE_KNOWLEDGE.value,
            "sender": self.agent_id,
            "knowledge_type": knowledge_type,
            "knowledge": knowledge,
            "timestamp": time.time(),
        }

        # Share with trusted neighbors
        for neighbor in self.neighbors:
            if self.trust_scores.get(neighbor, 0) > 0.6:
                await self.colony.send_agent_message(neighbor, message)

    async def _handle_knowledge_share(self, message: dict[str, Any]):
        """Handle shared knowledge from another agent."""
        sender = message.get("sender")
        knowledge_type = message.get("knowledge_type")
        knowledge = message.get("knowledge")

        # Store in shared knowledge if from trusted source
        if self.trust_scores.get(sender, 0) > 0.5:
            self.memory.shared_knowledge[knowledge_type] = knowledge

    async def participate_in_consensus(self, topic: str, options: list[Any]) -> Any:
        """Participate in colony-wide consensus."""
        # Make decision based on knowledge and experience
        if topic in self.memory.shared_knowledge:
            # Informed decision
            return self._make_informed_decision(topic, options)
        else:
            # Random or capability-based decision
            return random.choice(options)

    def _make_informed_decision(self, topic: str, options: list[Any]) -> Any:
        """Make decision based on available information."""
        knowledge = self.memory.shared_knowledge.get(topic, {})

        # Simple scoring based on knowledge
        scores = []
        for option in options:
            score = random.random()  # Base random score

            # Adjust based on knowledge
            if isinstance(knowledge, dict):
                for _key, value in knowledge.items():
                    if str(option) in str(value):
                        score += 0.2

            scores.append(score)

        # Return option with highest score
        best_idx = np.argmax(scores)
        return options[best_idx]

    async def rest_and_recover(self):
        """Rest to recover energy."""
        if self.state == AgentState.IDLE:
            self.energy = min(1.0, self.energy + 0.05)

    def get_status(self) -> dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "energy": self.energy,
            "capabilities": {
                name: {
                    "proficiency": cap.proficiency,
                    "experience": cap.experience,
                    "success_rate": cap.success_rate,
                }
                for name, cap in self.capabilities.items()
            },
            "neighbors": len(self.neighbors),
            "trust_network": len(self.trust_scores),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "collaborations": self.collaborations,
        }


class EnhancedColony(BaseColony if BASE_COLONY_AVAILABLE else object):
    """
    Enhanced Colony with real agent management and emergent behaviors.
    Integrated with BaseColony infrastructure for coherence.
    """

    def __init__(self, colony_id: str, colony_type: str, agent_count: int = 10):
        # Map colony_type to capabilities for BaseColony compatibility
        capabilities = self._get_capabilities_for_type(colony_type)

        if BASE_COLONY_AVAILABLE:
            super().__init__(colony_id, capabilities)

        self.colony_id = colony_id
        self.colony_type = colony_type
        self.agents: dict[str, EnhancedSwarmAgent] = {}
        self.agent_graph: dict[str, set[str]] = defaultdict(set)  # Neighbor relationships

        # Colony-level metrics
        self.collective_knowledge: dict[str, Any] = {}
        self.consensus_history: list[dict[str, Any]] = []
        self.emergence_patterns: list[dict[str, Any]] = []

        self.logger = logging.getLogger(f"{__name__}.{colony_id}")

        # Initialize agents
        self._initialize_agents(agent_count)

    def _get_capabilities_for_type(self, colony_type: str) -> list[str]:
        """Map colony type to capabilities for BaseColony compatibility."""
        capability_mapping = {
            "reasoning": [
                "logical_reasoning",
                "pattern_recognition",
                "inference",
                "analysis",
            ],
            "memory": [
                "storage",
                "retrieval",
                "indexing",
                "compression",
                "episodic_memory",
            ],
            "creativity": [
                "idea_generation",
                "synthesis",
                "innovation",
                "divergent_thinking",
            ],
            "governance": [
                "ethics",
                "policy",
                "consensus",
                "arbitration",
                "deontological_ethics",
            ],
            "temporal": [
                "time_analysis",
                "prediction",
                "scheduling",
                "temporal_reasoning",
            ],
            "quantum": [
                "superposition",
                "entanglement",
                "interference",
                "qi_algorithms",
            ],
            "general": ["general_processing", "coordination", "communication"],
        }
        return capability_mapping.get(colony_type, ["general_processing"])

    async def process_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Process a task using colony agents with consensus."""
        task_id = task.get("task_id", f"task_{int(time.time())}")
        task_type = task.get("type", "general")
        required_consensus = task.get("required_consensus", 0.6)

        self.logger.info(f"Processing task {task_id} of type {task_type}")

        # Integrate with BaseColony event sourcing if available
        if BASE_COLONY_AVAILABLE and hasattr(self, "aggregate") and hasattr(self.aggregate, "start_task"):
            try:
                self.aggregate.start_task(
                    task_id,
                    {
                        "task_type": task_type,
                        "colony_id": self.colony_id,
                        "agent_count": len(self.agents),
                    },
                )
            except Exception as e:
                self.logger.warning(f"Failed to log task start: {e}")

        # Find capable agents
        capable_agents = self._find_capable_agents(task_type)
        if not capable_agents:
            result = {
                "task_id": task_id,
                "status": "failed",
                "error": "No capable agents available",
                "timestamp": time.time(),
            }

            # Log failure event
            if BASE_COLONY_AVAILABLE and hasattr(self, "aggregate") and hasattr(self.aggregate, "complete_task"):
                try:
                    self.aggregate.complete_task(task_id, result)
                except Exception as e:
                    self.logger.warning(f"Failed to log task completion: {e}")

            return result

        # Distribute task to agents
        agent_results = []
        for agent_id in capable_agents[: min(3, len(capable_agents))]:  # Use max 3 agents
            agent = self.agents[agent_id]
            result = await agent.process_task_request(task)
            if result:
                agent_results.append(
                    {
                        "agent_id": agent_id,
                        "result": result,
                        "confidence": result.get("confidence", 0.5),
                    }
                )

        # Achieve consensus
        consensus_result = self._achieve_consensus(agent_results, required_consensus)

        # Record task completion
        task_record = {
            "task_id": task_id,
            "task_type": task_type,
            "agents_involved": [r["agent_id"] for r in agent_results],
            "consensus_achieved": consensus_result["consensus_achieved"],
            "final_confidence": consensus_result["confidence"],
            "timestamp": time.time(),
        }

        self.consensus_history.append(task_record)

        final_result = {
            "task_id": task_id,
            "status": ("completed" if consensus_result["consensus_achieved"] else "partial"),
            "result": consensus_result["result"],
            "confidence": consensus_result["confidence"],
            "agents_involved": len(agent_results),
            "consensus_achieved": consensus_result["consensus_achieved"],
            "timestamp": time.time(),
        }

        # Integrate with BaseColony event sourcing
        if BASE_COLONY_AVAILABLE and hasattr(self, "aggregate") and hasattr(self.aggregate, "complete_task"):
            try:
                self.aggregate.complete_task(task_id, final_result)
            except Exception as e:
                self.logger.warning(f"Failed to log task completion: {e}")

        return final_result

    def _find_capable_agents(self, task_type: str) -> list[str]:
        """Find agents capable of handling the task type."""
        capable_agents = []
        for agent_id, agent in self.agents.items():
            if agent.can_handle_task_type(task_type):
                capable_agents.append(agent_id)
        return capable_agents

    def _achieve_consensus(self, agent_results: list[dict], required_consensus: float) -> dict[str, Any]:
        """Achieve consensus from agent results."""
        if not agent_results:
            return {"consensus_achieved": False, "result": None, "confidence": 0.0}

        # Simple consensus: average confidence and majority vote
        total_confidence = sum(r["confidence"] for r in agent_results)
        avg_confidence = total_confidence / len(agent_results)

        # Majority result (simplified)
        results = [r["result"] for r in agent_results]
        consensus_result = results[0] if results else None

        consensus_achieved = avg_confidence >= required_consensus

        return {
            "consensus_achieved": consensus_achieved,
            "result": consensus_result,
            "confidence": avg_confidence,
        }

    async def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute task - BaseColony abstract method implementation."""
        return await self.process_task(task)

    def _initialize_agents(self, count: int):
        """Initialize colony with agents."""
        # Define capability distribution based on colony type
        capability_pools = {
            "reasoning": ["analysis", "logic", "inference", "pattern_recognition"],
            "memory": ["storage", "retrieval", "indexing", "compression"],
            "creativity": ["generation", "synthesis", "innovation", "combination"],
            "governance": ["ethics", "policy", "consensus", "arbitration"],
            "temporal": ["time_analysis", "prediction", "history", "scheduling"],
            "quantum": ["superposition", "entanglement", "interference", "measurement"],
        }

        base_capabilities = capability_pools.get(self.colony_type, ["general"])

        for i in range(count):
            agent_id = f"{self.colony_id}-agent-{i}"

            # Give each agent a mix of capabilities
            agent_capabilities = [base_capabilities[i % len(base_capabilities)]]

            # Add some diversity
            if random.random() > 0.5 and len(base_capabilities) > 1:
                extra_cap = random.choice(base_capabilities)
                if extra_cap not in agent_capabilities:
                    agent_capabilities.append(extra_cap)

            agent = EnhancedSwarmAgent(agent_id, self, agent_capabilities)
            self.agents[agent_id] = agent

        # Create agent network (small-world topology)
        self._create_agent_network()

        self.logger.info(f"Initialized {count} agents in {self.colony_id}")

    def _create_agent_network(self):
        """Create small-world network topology for agents."""
        agent_ids = list(self.agents.keys())
        n = len(agent_ids)

        if n < 2:
            return

        # Create ring lattice (each connected to k nearest neighbors)
        k = min(4, n - 1)  # Each agent connected to k neighbors
        for i in range(n):
            for j in range(1, k // 2 + 1):
                neighbor1 = agent_ids[(i + j) % n]
                neighbor2 = agent_ids[(i - j) % n]

                self.agent_graph[agent_ids[i]].add(neighbor1)
                self.agent_graph[agent_ids[i]].add(neighbor2)
                self.agent_graph[neighbor1].add(agent_ids[i])
                self.agent_graph[neighbor2].add(agent_ids[i])

        # Add random shortcuts (small-world property)
        num_shortcuts = max(1, n // 10)
        for _ in range(num_shortcuts):
            a1, a2 = random.sample(agent_ids, 2)
            self.agent_graph[a1].add(a2)
            self.agent_graph[a2].add(a1)

        # Update agent neighbors
        for agent_id, neighbors in self.agent_graph.items():
            if agent_id in self.agents:
                self.agents[agent_id].neighbors = neighbors.copy()

    async def send_agent_message(self, recipient: str, message: dict[str, Any]):
        """Send message between agents."""
        if recipient in self.agents:
            self.agents[recipient].receive(message)

    async def broadcast_to_agents(self, message: dict[str, Any], criteria: Optional[Callable] = None):
        """Broadcast message to all agents or those matching criteria."""
        for _agent_id, agent in self.agents.items():
            if criteria is None or criteria(agent):
                agent.receive(message)

    async def execute_colony_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute task using colony's collective intelligence."""
        task_id = task.get("id", f"task-{time.time()}")
        task_type = task.get("type", "unknown")

        self.logger.info(f"Colony {self.colony_id} executing task {task_id}")

        # Find capable agents
        capable_agents = []
        for agent in self.agents.values():
            can_handle, capability = agent._can_handle_task(task_type)
            if can_handle:
                capable_agents.append((agent, capability))

        if not capable_agents:
            # No single agent can handle - try collaborative approach
            return await self._collaborative_task_execution(task)

        # Sort by proficiency and energy
        capable_agents.sort(key=lambda x: x[1].proficiency * x[0].energy, reverse=True)

        # Assign to best agent
        best_agent, _ = capable_agents[0]
        message = {"type": MessageType.TASK.value, "sender": "colony", "task": task}

        best_agent.receive(message)

        # Wait for completion (simplified - in real system would use futures)
        await asyncio.sleep(1.0)

        return {
            "task_id": task_id,
            "status": "assigned",
            "assigned_to": best_agent.agent_id,
            "colony": self.colony_id,
        }

    async def _collaborative_task_execution(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute task through agent collaboration."""
        self.logger.info(f"Initiating collaborative execution for task {task.get('id')}")

        # Broadcast task to all agents
        await self.broadcast_to_agents(
            {
                "type": MessageType.TASK.value,
                "sender": "colony",
                "task": task,
                "collaborative": True,
            }
        )

        # Agents will self-organize through help requests

        return {
            "task_id": task.get("id"),
            "status": "collaborative_execution",
            "colony": self.colony_id,
        }

    async def achieve_consensus(self, topic: str, options: list[Any]) -> Any:
        """Achieve consensus among agents."""
        self.logger.info(f"Colony {self.colony_id} seeking consensus on {topic}")

        # Collect votes from all agents
        votes = {}
        for agent in self.agents.values():
            vote = await agent.participate_in_consensus(topic, options)
            votes[agent.agent_id] = vote

        # Count votes
        vote_counts = defaultdict(int)
        for vote in votes.values():
            vote_counts[vote] += 1

        # Find consensus (simple majority)
        consensus = max(vote_counts.items(), key=lambda x: x[1])[0]

        # Record consensus
        self.consensus_history.append(
            {
                "topic": topic,
                "options": options,
                "consensus": consensus,
                "votes": votes,
                "timestamp": time.time(),
                "participation": len(votes) / len(self.agents),
            }
        )

        return consensus

    async def share_collective_knowledge(self, knowledge_type: str, knowledge: Any):
        """Share knowledge across all agents."""
        self.collective_knowledge[knowledge_type] = knowledge

        # Propagate to all agents
        await self.broadcast_to_agents(
            {
                "type": MessageType.SHARE_KNOWLEDGE.value,
                "sender": "colony",
                "knowledge_type": knowledge_type,
                "knowledge": knowledge,
            }
        )

    async def maintain_colony_health(self):
        """Maintain health of all agents."""
        for agent in self.agents.values():
            await agent.rest_and_recover()

            # Check for failed agents
            if agent.state == AgentState.FAILED:
                await self._revive_agent(agent)

    async def _revive_agent(self, agent: EnhancedSwarmAgent):
        """Revive a failed agent."""
        self.logger.info(f"Reviving agent {agent.agent_id}")

        # Reset agent state
        agent.state = AgentState.IDLE
        agent.energy = 0.5

        # Share knowledge from neighbors to help recovery
        for neighbor_id in agent.neighbors:
            if neighbor_id in self.agents:
                neighbor = self.agents[neighbor_id]
                if neighbor.memory.shared_knowledge:
                    await neighbor.share_knowledge("recovery_knowledge", neighbor.memory.shared_knowledge)

    def detect_emergent_patterns(self) -> list[dict[str, Any]]:
        """Detect emergent patterns in colony behavior."""
        patterns = []

        # Pattern 1: Specialization emergence
        capability_clusters = defaultdict(list)
        for agent in self.agents.values():
            primary_cap = max(agent.capabilities.items(), key=lambda x: x[1].proficiency)[0]
            capability_clusters[primary_cap].append(agent.agent_id)

        if len(capability_clusters) > 1:
            patterns.append(
                {
                    "type": "specialization",
                    "clusters": dict(capability_clusters),
                    "diversity": len(capability_clusters) / len(self.agents),
                }
            )

        # Pattern 2: Trust networks
        trust_clusters = defaultdict(set)
        for agent in self.agents.values():
            high_trust = [other for other, trust in agent.trust_scores.items() if trust > 0.7]
            if high_trust:
                cluster_id = min(high_trust)  # Use lowest ID as cluster identifier
                trust_clusters[cluster_id].add(agent.agent_id)
                trust_clusters[cluster_id].update(high_trust)

        if trust_clusters:
            patterns.append(
                {
                    "type": "trust_networks",
                    "clusters": {k: list(v) for k, v in trust_clusters.items()},
                    "num_clusters": len(trust_clusters),
                }
            )

        # Pattern 3: Knowledge distribution
        knowledge_spread = defaultdict(int)
        for agent in self.agents.values():
            for k_type in agent.memory.shared_knowledge:
                knowledge_spread[k_type] += 1

        if knowledge_spread:
            patterns.append(
                {
                    "type": "knowledge_distribution",
                    "spread": dict(knowledge_spread),
                    "coverage": sum(knowledge_spread.values()) / (len(self.agents) * len(knowledge_spread)),
                }
            )

        self.emergence_patterns = patterns
        return patterns

    def get_colony_status(self) -> dict[str, Any]:
        """Get comprehensive colony status."""
        agent_states = defaultdict(int)
        total_energy = 0
        total_capabilities = defaultdict(float)

        for agent in self.agents.values():
            agent_states[agent.state.value] += 1
            total_energy += agent.energy

            for cap_name, cap in agent.capabilities.items():
                total_capabilities[cap_name] += cap.proficiency

        return {
            "colony_id": self.colony_id,
            "colony_type": self.colony_type,
            "agent_count": len(self.agents),
            "agent_states": dict(agent_states),
            "average_energy": total_energy / len(self.agents) if self.agents else 0,
            "capabilities": {name: prof / len(self.agents) for name, prof in total_capabilities.items()},
            "collective_knowledge_items": len(self.collective_knowledge),
            "consensus_history": len(self.consensus_history),
            "emergence_patterns": len(self.emergence_patterns),
            "network_density": sum(len(n) for n in self.agent_graph.values()) / (2 * len(self.agents)),
        }


class EnhancedSwarmHub:
    """
    Enhanced Swarm Hub with real colony coordination and emergent behaviors.
    """

    def __init__(self):
        self.colonies: dict[str, EnhancedColony] = {}
        self.inter_colony_links: dict[str, set[str]] = defaultdict(set)
        self.global_knowledge: dict[str, Any] = {}
        self.swarm_patterns: list[dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.SwarmHub")

    def create_colony(
        self, colony_id: str, colony_type: Union[str, list[str]], agent_count: int = 10
    ) -> "EnhancedColony":
        """Create a new colony."""
        if colony_id in self.colonies:
            raise ValueError(f"Colony {colony_id} already exists")

        # Handle both string and list inputs for colony_type
        if isinstance(colony_type, list):
            # If list of capabilities is provided, infer colony type from colony_id
            if any(
                t in colony_id.lower()
                for t in [
                    "reasoning",
                    "memory",
                    "creativity",
                    "governance",
                    "temporal",
                    "quantum",
                ]
            ):
                inferred_type = next(
                    t
                    for t in [
                        "reasoning",
                        "memory",
                        "creativity",
                        "governance",
                        "temporal",
                        "quantum",
                    ]
                    if t in colony_id.lower()
                )
                colony = EnhancedColony(colony_id, inferred_type, agent_count)
            else:
                colony = EnhancedColony(colony_id, "general", agent_count)
        else:
            colony = EnhancedColony(colony_id, colony_type, agent_count)

        self.colonies[colony_id] = colony

        # Link to related colonies
        self._establish_colony_links(colony_id, colony_type)

        self.logger.info(f"Created {colony_type} colony: {colony_id}")
        return colony

    def _establish_colony_links(self, new_colony_id: str, colony_type: Union[str, list[str]]):
        """Establish links between related colonies."""
        # Define colony relationships
        relationships = {
            "reasoning": ["memory", "creativity"],
            "memory": ["reasoning", "temporal"],
            "creativity": ["reasoning", "memory"],
            "governance": ["reasoning", "memory", "temporal"],
            "temporal": ["memory", "reasoning"],
            "quantum": ["reasoning", "creativity"],
        }

        # Handle both string and list inputs
        if isinstance(colony_type, list):
            # If list of capabilities, infer colony type from colony_id
            if any(t in new_colony_id.lower() for t in relationships):
                inferred_type = next(t for t in relationships if t in new_colony_id.lower())
                related_types = relationships.get(inferred_type, [])
            else:
                related_types = []
        else:
            related_types = relationships.get(colony_type, [])

        for colony_id, colony in self.colonies.items():
            if colony_id != new_colony_id and colony.colony_type in related_types:
                self.inter_colony_links[new_colony_id].add(colony_id)
                self.inter_colony_links[colony_id].add(new_colony_id)

    async def execute_swarm_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute task using the entire swarm."""
        task_id = task.get("id", f"swarm-task-{time.time()}")
        required_capabilities = task.get("required_capabilities", [])

        self.logger.info(f"Swarm executing task {task_id}")

        # Find suitable colonies
        suitable_colonies = []
        for colony in self.colonies.values():
            colony_caps = set()
            for agent in colony.agents.values():
                colony_caps.update(agent.capabilities.keys())

            if any(req in colony_caps for req in required_capabilities):
                suitable_colonies.append(colony)

        if not suitable_colonies:
            return {
                "task_id": task_id,
                "status": "no_suitable_colonies",
                "error": f"No colonies found for capabilities: {required_capabilities}",
            }

        # Distribute task to colonies
        colony_results = []
        for colony in suitable_colonies:
            result = await colony.execute_colony_task(task)
            colony_results.append(result)

        return {
            "task_id": task_id,
            "status": "distributed",
            "colonies_involved": [c.colony_id for c in suitable_colonies],
            "colony_results": colony_results,
        }

    async def achieve_swarm_consensus(self, topic: str, options: list[Any]) -> Any:
        """Achieve consensus across the entire swarm."""
        self.logger.info(f"Swarm seeking consensus on {topic}")

        # Get consensus from each colony
        colony_decisions = {}
        for colony_id, colony in self.colonies.items():
            decision = await colony.achieve_consensus(topic, options)
            colony_decisions[colony_id] = decision

        # Weight by colony size and health
        weighted_votes = defaultdict(float)
        for colony_id, decision in colony_decisions.items():
            colony = self.colonies[colony_id]
            status = colony.get_colony_status()

            # Weight by agent count and average energy
            weight = status["agent_count"] * status["average_energy"]
            weighted_votes[decision] += weight

        # Find swarm consensus
        swarm_consensus = max(weighted_votes.items(), key=lambda x: x[1])[0]

        self.logger.info(f"Swarm consensus on {topic}: {swarm_consensus}")
        return swarm_consensus

    async def propagate_knowledge(self, knowledge_type: str, knowledge: Any, source_colony: str):
        """Propagate knowledge across the swarm."""
        self.global_knowledge[knowledge_type] = knowledge

        # First propagate to linked colonies
        for linked_colony_id in self.inter_colony_links.get(source_colony, []):
            if linked_colony_id in self.colonies:
                await self.colonies[linked_colony_id].share_collective_knowledge(knowledge_type, knowledge)

        # Then propagate to all colonies with delay
        await asyncio.sleep(0.1)  # Simulate propagation delay

        for colony_id, colony in self.colonies.items():
            if colony_id != source_colony:
                await colony.share_collective_knowledge(knowledge_type, knowledge)

    async def maintain_swarm_health(self):
        """Maintain health of the entire swarm."""
        maintenance_tasks = []

        for colony in self.colonies.values():
            maintenance_tasks.append(colony.maintain_colony_health())

        await asyncio.gather(*maintenance_tasks)

        # Detect swarm-level patterns
        self._detect_swarm_patterns()

    def _detect_swarm_patterns(self):
        """Detect emergent patterns at swarm level."""
        patterns = []

        # Pattern 1: Inter-colony collaboration
        defaultdict(int)
        # This would track actual collaborations in a real system

        # Pattern 2: Knowledge convergence
        knowledge_overlap = defaultdict(set)
        for colony_id, colony in self.colonies.items():
            for k_type in colony.collective_knowledge:
                knowledge_overlap[k_type].add(colony_id)

        if knowledge_overlap:
            patterns.append(
                {
                    "type": "knowledge_convergence",
                    "shared_knowledge": {k: list(colonies) for k, colonies in knowledge_overlap.items()},
                    "convergence_rate": sum(len(colonies) for colonies in knowledge_overlap.values())
                    / (len(self.colonies) * len(knowledge_overlap)),
                }
            )

        # Pattern 3: Specialization distribution
        specializations = defaultdict(list)
        for colony in self.colonies.values():
            status = colony.get_colony_status()
            primary_cap = (
                max(status["capabilities"].items(), key=lambda x: x[1])[0] if status["capabilities"] else "none"
            )
            specializations[primary_cap].append(colony.colony_id)

        patterns.append(
            {
                "type": "swarm_specialization",
                "distribution": dict(specializations),
                "diversity": len(specializations),
            }
        )

        self.swarm_patterns = patterns

    def get_swarm_status(self) -> dict[str, Any]:
        """Get comprehensive swarm status."""
        total_agents = 0
        total_energy = 0
        total_tasks = 0

        colony_statuses = {}
        for colony_id, colony in self.colonies.items():
            status = colony.get_colony_status()
            colony_statuses[colony_id] = status

            total_agents += status["agent_count"]
            total_energy += status["average_energy"] * status["agent_count"]

            # Sum tasks from all agents
            for agent in colony.agents.values():
                total_tasks += agent.tasks_completed

        return {
            "swarm_id": "enhanced-swarm",
            "colony_count": len(self.colonies),
            "total_agents": total_agents,
            "average_energy": total_energy / total_agents if total_agents > 0 else 0,
            "total_tasks_completed": total_tasks,
            "inter_colony_connections": sum(len(links) for links in self.inter_colony_links.values()) // 2,
            "global_knowledge_items": len(self.global_knowledge),
            "swarm_patterns": self.swarm_patterns,
            "colony_statuses": colony_statuses,
        }


# Example demonstration
async def demonstrate_enhanced_swarm():
    """Demonstrate the enhanced swarm system."""

    # Create swarm hub
    swarm = EnhancedSwarmHub()

    # Create diverse colonies
    colonies = [
        ("reasoning-alpha", "reasoning", 8),
        ("memory-beta", "memory", 10),
        ("creativity-gamma", "creativity", 6),
        ("governance-delta", "governance", 4),
    ]

    for colony_id, colony_type, agent_count in colonies:
        swarm.create_colony(colony_id, colony_type, agent_count)

    print("=== Enhanced Swarm System Created ===")
    print(f"Colonies: {len(swarm.colonies)}")
    print(f"Total Agents: {sum(len(c.agents) for c in swarm.colonies.values())}")

    # Execute some tasks
    tasks = [
        {
            "id": "task-1",
            "type": "analysis",
            "required_capabilities": ["reasoning", "memory"],
            "priority": 0.8,
        },
        {
            "id": "task-2",
            "type": "generation",
            "required_capabilities": ["creativity"],
            "priority": 0.6,
        },
        {
            "id": "task-3",
            "type": "policy_review",
            "required_capabilities": ["governance", "reasoning"],
            "priority": 0.9,
        },
    ]

    print("\n=== Executing Swarm Tasks ===")
    for task in tasks:
        result = await swarm.execute_swarm_task(task)
        print(f"Task {task['id']}: {result['status']}")

    # Achieve consensus
    print("\n=== Achieving Swarm Consensus ===")
    consensus = await swarm.achieve_swarm_consensus("optimization_strategy", ["parallel", "sequential", "hybrid"])
    print(f"Consensus reached: {consensus}")

    # Share knowledge
    print("\n=== Propagating Knowledge ===")
    await swarm.propagate_knowledge(
        "best_practices",
        {
            "efficiency": "Use parallel processing",
            "collaboration": "Share early and often",
        },
        "reasoning-alpha",
    )

    # Maintain health
    print("\n=== Maintaining Swarm Health ===")
    await swarm.maintain_swarm_health()

    # Detect patterns
    for colony in swarm.colonies.values():
        patterns = colony.detect_emergent_patterns()
        if patterns:
            print(f"\nEmergent patterns in {colony.colony_id}:")
            for pattern in patterns:
                print(f"  - {pattern['type']}: {pattern.get('num_clusters', pattern.get('diversity', 'detected'))}")

    # Get final status
    print("\n=== Final Swarm Status ===")
    status = swarm.get_swarm_status()
    print(f"Total Agents: {status['total_agents']}")
    print(f"Average Energy: {status['average_energy']:.2f}")
    print(f"Tasks Completed: {status['total_tasks_completed']}")
    print(f"Inter-colony Connections: {status['inter_colony_connections']}")
    print(f"Swarm Patterns Detected: {len(status['swarm_patterns'])}")

    # Show some agent details
    print("\n=== Sample Agent Status ===")
    sample_colony = swarm.colonies["reasoning-alpha"]
    sample_agent = list(sample_colony.agents.values())[0]
    agent_status = sample_agent.get_status()
    print(f"Agent: {agent_status['agent_id']}")
    print(f"State: {agent_status['state']}")
    print(f"Energy: {agent_status['energy']:.2f}")
    print(f"Capabilities: {list(agent_status['capabilities'].keys())}")
    print(f"Tasks Completed: {agent_status['tasks_completed']}")


if __name__ == "__main__":
    asyncio.run(demonstrate_enhanced_swarm())
