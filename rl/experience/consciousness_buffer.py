"""
╔══════════════════════════════════════════════════════════════
║ 🧠 MΛTRIZ RL Module: Consciousness Experience Buffer
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: MEMORY
║ CONSCIOUSNESS_ROLE: Experience replay using memory fold system
║ EVOLUTIONARY_STAGE: Memory - Experience storage and retrieval
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Memory identity and storage authority
║ 🧠 CONSCIOUSNESS: Consciousness-aware experience management
║ 🛡️ GUARDIAN: Safe memory storage with cascade prevention
╚══════════════════════════════════════════════════════════════
"""

import random
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import numpy as np
except ImportError:
    np = None

from candidate.core.common import get_logger

from ..engine.consciousness_environment import MatrizNode

logger = get_logger(__name__)


@dataclass
class RLExperience:
    """Single RL experience tuple"""

    state: MatrizNode
    action: MatrizNode
    reward: MatrizNode
    next_state: MatrizNode
    done: bool = False
    episode_id: Optional[str] = None
    step: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConsciousnessBuffer:
    """
    MΛTRIZ-native experience buffer that integrates with memory fold system.
    Stores RL experiences as MEMORY nodes and prevents memory cascades.
    This is NOT traditional experience replay - it's consciousness-aware memory.
    """

    def __init__(self, capacity: int = 10000):
        self.capabilities = ["rl.experience", "memory.fold", "buffer.replay"]
        self.node_type = "MEMORY"
        self.trace_id = f"rl-buffer-{uuid.uuid4().hex[:12]}"

        # Buffer configuration
        self.capacity = capacity
        self.cascade_prevention_threshold = 0.997  # 99.7% cascade prevention from design

        # Experience storage
        self.experiences = deque(maxlen=capacity)
        self.experience_nodes = deque(maxlen=capacity)  # MEMORY nodes
        self.episode_boundaries = []  # Track episode starts/ends

        # Memory fold integration
        self.memory_fold = None
        self.fold_registry = {}

        # Buffer metrics
        self.total_experiences = 0
        self.memory_efficiency = []
        self.cascade_prevention_successes = 0
        self.cascade_prevention_attempts = 0

        logger.info(
            "MΛTRIZ ConsciousnessBuffer initialized",
            capabilities=self.capabilities,
            trace_id=self.trace_id,
            capacity=capacity,
        )

    def get_module(self, module_path: str) -> Optional[Any]:
        """Get reference to existing consciousness module (no duplication)"""
        try:
            if module_path == "memory.fold.v1":
                from candidate.memory.temporal.compliance_hooks import ComplianceHooks

                return ComplianceHooks()
            elif module_path == "memory.core.v1":
                # Mock memory core for now
                class MockMemoryCore:
                    def create_fold(self, data, **kwargs):
                        return f"fold-{uuid.uuid4().hex[:8]}"

                    def get_fold(self, fold_id):
                        return {"data": "mock", "id": fold_id}

                    def get_salience_map(self):
                        return {"recent": 0.9, "important": 0.8}

                return MockMemoryCore()
        except ImportError:
            return None

    def _initialize_memory_fold(self):
        """Initialize memory fold integration"""
        if self.memory_fold is None:
            self.memory_fold = self.get_module("memory.fold.v1")
            if not self.memory_fold:
                # Create mock memory fold
                class MockMemoryFold:
                    def create_fold(self, data, cascade_prevention=0.997):
                        fold_id = f"fold-{uuid.uuid4().hex[:8]}"
                        logger.info(f"Mock memory fold created: {fold_id}")
                        return fold_id

                    def get_fold(self, fold_id):
                        return {"id": fold_id, "data": "mock", "salience": 0.8}

                    def update_salience(self, fold_id, salience):
                        logger.info(f"Updated salience for {fold_id}: {salience}")
                        return True

                self.memory_fold = MockMemoryFold()
                logger.warning("Using mock memory fold system")

    async def store_experience(
        self,
        state: MatrizNode,
        action: MatrizNode,
        reward: MatrizNode,
        next_state: MatrizNode,
        done: bool = False,
        episode_id: Optional[str] = None,
    ) -> MatrizNode:
        """
        Store RL experience using memory fold system, emit MEMORY node.
        This integrates with the existing 99.7% cascade prevention system.
        """
        self._initialize_memory_fold()

        # Create rich RL experience
        experience = RLExperience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            episode_id=episode_id or f"episode-{uuid.uuid4().hex[:8]}",
            step=len(self.experiences),
            timestamp=datetime.now(timezone.utc),
        )

        # Calculate experience salience based on reward and consciousness coherence
        salience = self._calculate_experience_salience(experience)

        # Store in memory fold system with cascade prevention
        try:
            self.cascade_prevention_attempts += 1

            experience_data = {
                "type": "rl_experience",
                "state_node_id": state.id,
                "action_node_id": action.id,
                "reward_node_id": reward.id,
                "next_state_node_id": next_state.id,
                "done": done,
                "episode_id": experience.episode_id,
                "step": experience.step,
                "salience": salience,
                "consciousness_coherence": self._extract_coherence(state),
                "ethical_alignment": self._extract_ethics(state),
                "timestamp": experience.timestamp.isoformat(),
            }

            fold_id = self.memory_fold.create_fold(
                experience_data, cascade_prevention=self.cascade_prevention_threshold
            )

            self.cascade_prevention_successes += 1

        except Exception as e:
            logger.error(f"Memory fold creation failed: {e}")
            fold_id = f"emergency-fold-{uuid.uuid4().hex[:8]}"

        # Create MEMORY node
        memory_node = MatrizNode(
            version=1,
            id=f"RL-MEMORY-{self.trace_id}-{self.total_experiences}",
            type="MEMORY",
            labels=[
                "rl:role=experience@1",
                "memory:type=rl_experience@1",
                f"salience:level={salience:.2f}@1",
                f"episode:id={experience.episode_id}@1",
                "cascade:prevention=active@1",
            ],
            state={
                "confidence": 0.95,  # High confidence in stored experiences
                "salience": salience,
                "valence": reward.state.get("valence", 0.0),
                "arousal": 0.5,  # Moderate arousal for memories
                "novelty": self._calculate_experience_novelty(experience),
                "urgency": 0.3,  # Memories have low urgency
                # Rich experience information
                "fold_id": fold_id,
                "experience_type": "rl_learning",
                "episode_id": experience.episode_id,
                "step_in_episode": experience.step,
                "is_terminal": done,
                "reward_magnitude": reward.state.get("reward_total", 0.0),
                "consciousness_coherence": self._extract_coherence(state),
                "ethical_alignment": self._extract_ethics(state),
                "memory_efficiency": len(self.experiences) / self.capacity,
                "cascade_prevention_rate": self.cascade_prevention_successes / max(1, self.cascade_prevention_attempts),
            },
            timestamps={
                "created_ts": int(time.time() * 1000),
                "observed_ts": int(experience.timestamp.timestamp() * 1000),
            },
            provenance={
                "producer": "rl.experience.consciousness_buffer",
                "capabilities": self.capabilities,
                "tenant": "lukhas_rl",
                "trace_id": self.trace_id,
                "consent_scopes": ["rl_memory", "experience_storage"],
                "policy_version": "rl.memory.v1.0",
                "colony": {"id": "rl_experience", "role": "buffer", "iteration": self.total_experiences},
            },
            links=[
                {
                    "target_node_id": state.id,
                    "link_type": "temporal",
                    "weight": 0.9,
                    "direction": "bidirectional",
                    "explanation": "Experience state component",
                },
                {
                    "target_node_id": action.id,
                    "link_type": "causal",
                    "weight": 0.95,
                    "direction": "unidirectional",
                    "explanation": "Action taken in this experience",
                },
                {
                    "target_node_id": reward.id,
                    "link_type": "causal",
                    "weight": 1.0,
                    "direction": "unidirectional",
                    "explanation": "Reward received for action",
                },
                {
                    "target_node_id": next_state.id,
                    "link_type": "temporal",
                    "weight": 0.9,
                    "direction": "bidirectional",
                    "explanation": "Resulting state after action",
                },
            ],
            evolves_to=["HYPOTHESIS", "REFLECTION", "CAUSAL"],
            triggers=[
                {
                    "event_type": "experience_storage",
                    "effect": "memory_fold_created",
                    "timestamp": int(time.time() * 1000),
                }
            ]
            + (
                [
                    {
                        "event_type": "episode_termination",
                        "effect": "episode_boundary_marked",
                        "timestamp": int(time.time() * 1000),
                    }
                ]
                if done
                else []
            ),
            reflections=[
                {
                    "reflection_type": "self_question",
                    "timestamp": int(time.time() * 1000),
                    "cause": "How will this experience improve learning?",
                    "old_state": {"learning_potential": "unknown"},
                    "new_state": {"learning_potential": salience},
                }
            ],
            embeddings=[],
            evidence=[{"kind": "trace", "uri": f"memory://fold/{fold_id}"}],
        )

        # Store experience and memory node
        self.experiences.append(experience)
        self.experience_nodes.append(memory_node)
        self.fold_registry[memory_node.id] = fold_id

        # Track episode boundaries
        if done:
            self.episode_boundaries.append(
                {
                    "episode_id": experience.episode_id,
                    "end_index": len(self.experiences) - 1,
                    "total_steps": experience.step + 1,
                    "timestamp": experience.timestamp,
                }
            )

        # Update metrics
        self.total_experiences += 1
        self.memory_efficiency.append(salience)
        if len(self.memory_efficiency) > 100:
            self.memory_efficiency = self.memory_efficiency[-100:]

        logger.info(
            "Experience stored in consciousness buffer",
            fold_id=fold_id,
            salience=salience,
            episode_id=experience.episode_id,
            step=experience.step,
            done=done,
            memory_node_id=memory_node.id,
        )

        return memory_node

    def _calculate_experience_salience(self, experience: RLExperience) -> float:
        """Calculate salience of experience for memory storage"""
        # Base salience from reward magnitude
        reward_magnitude = abs(experience.reward.state.get("reward_total", 0.0))
        base_salience = min(1.0, reward_magnitude * 2.0)  # Scale reward to salience

        # Boost salience for terminal states
        terminal_bonus = 0.2 if experience.done else 0.0

        # Consciousness coherence bonus
        coherence = self._extract_coherence(experience.state)
        coherence_bonus = coherence * 0.1

        # Ethics alignment bonus
        ethics = self._extract_ethics(experience.state)
        ethics_bonus = ethics * 0.1

        # Novelty bonus
        novelty_bonus = self._calculate_experience_novelty(experience) * 0.1

        total_salience = base_salience + terminal_bonus + coherence_bonus + ethics_bonus + novelty_bonus

        return min(1.0, max(0.1, total_salience))

    def _extract_coherence(self, node: MatrizNode) -> float:
        """Extract temporal coherence from node"""
        return node.state.get("temporal_coherence", 0.95)

    def _extract_ethics(self, node: MatrizNode) -> float:
        """Extract ethical alignment from node"""
        return node.state.get("ethical_alignment", 0.98)

    def _calculate_experience_novelty(self, experience: RLExperience) -> float:
        """Calculate novelty of experience"""
        if len(self.experiences) < 5:
            return 0.7  # High novelty for early experiences

        # Simple novelty: compare state to recent states
        recent_states = [exp.state for exp in list(self.experiences)[-10:]]
        current_coherence = self._extract_coherence(experience.state)

        recent_coherences = [self._extract_coherence(state) for state in recent_states]
        if recent_coherences:
            avg_coherence = sum(recent_coherences) / len(recent_coherences)
            novelty = abs(current_coherence - avg_coherence) * 5  # Scale difference
            return min(1.0, novelty)

        return 0.5

    async def sample_batch(self, batch_size: int = 32) -> list[RLExperience]:
        """Sample batch of experiences for training"""
        if len(self.experiences) < batch_size:
            return list(self.experiences)

        # Prioritized sampling based on salience
        if np:
            # Calculate sampling probabilities based on salience
            saliences = [
                self.memory_efficiency[i] if i < len(self.memory_efficiency) else 0.5
                for i in range(len(self.experiences))
            ]

            # Add small epsilon to avoid zero probabilities
            probs = np.array(saliences) + 1e-6
            probs = probs / np.sum(probs)

            # Sample indices
            indices = np.random.choice(len(self.experiences), size=batch_size, replace=False, p=probs)
            sampled_experiences = [self.experiences[i] for i in indices]
        else:
            # Random sampling fallback
            sampled_experiences = random.sample(list(self.experiences), batch_size)

        logger.info(f"Sampled batch of {len(sampled_experiences)} experiences")
        return sampled_experiences

    async def get_episode_experiences(self, episode_id: str) -> list[RLExperience]:
        """Get all experiences from a specific episode"""
        episode_experiences = [exp for exp in self.experiences if exp.episode_id == episode_id]

        logger.info(f"Retrieved {len(episode_experiences)} experiences for episode {episode_id}")
        return episode_experiences

    async def get_high_salience_experiences(self, threshold: float = 0.8, limit: int = 50) -> list[RLExperience]:
        """Get experiences with high salience for priority learning"""
        high_salience = []

        for i, experience in enumerate(self.experiences):
            if i < len(self.memory_efficiency) and self.memory_efficiency[i] >= threshold:
                high_salience.append(experience)
                if len(high_salience) >= limit:
                    break

        logger.info(f"Retrieved {len(high_salience)} high-salience experiences (threshold: {threshold})")
        return high_salience

    def get_buffer_metrics(self) -> dict[str, Any]:
        """Get buffer performance metrics"""
        return {
            "total_experiences": self.total_experiences,
            "buffer_utilization": len(self.experiences) / self.capacity,
            "cascade_prevention_rate": self.cascade_prevention_successes / max(1, self.cascade_prevention_attempts),
            "average_salience": (
                sum(self.memory_efficiency) / len(self.memory_efficiency) if self.memory_efficiency else 0.0
            ),
            "total_episodes": len(self.episode_boundaries),
            "memory_efficiency_trend": (
                self.memory_efficiency[-10:] if len(self.memory_efficiency) >= 10 else self.memory_efficiency
            ),
            "fold_registry_size": len(self.fold_registry),
            "trace_id": self.trace_id,
        }

    def clear(self):
        """Clear all stored experiences"""
        self.experiences.clear()
        self.experience_nodes.clear()
        self.episode_boundaries.clear()
        self.fold_registry.clear()
        self.memory_efficiency.clear()

        logger.info("Consciousness buffer cleared")

    def __len__(self) -> int:
        """Return number of stored experiences"""
        return len(self.experiences)

    def is_ready_for_training(self, min_experiences: int = 1000) -> bool:
        """Check if buffer has enough experiences for training"""
        return len(self.experiences) >= min_experiences
