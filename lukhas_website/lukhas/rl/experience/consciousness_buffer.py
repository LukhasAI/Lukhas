"""
Consciousness Experience Replay Buffer for LUKHAS RL
===================================================

Advanced experience replay system designed for consciousness learning.
Integrates with LUKHAS memory fold system and provides consciousness-aware
experience sampling and storage.

Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from __future__ import annotations

import asyncio
import logging
import pickle
import random
from collections import deque, namedtuple
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from observability.matriz_decorators import instrument

from memory import MemoryFoldSystem

logger = logging.getLogger(__name__)

# Experience tuple for consciousness RL
ConsciousnessExperience = namedtuple(
    "ConsciousnessExperience",
    [
        "state",  # Consciousness state
        "action",  # Action taken
        "reward",  # Reward received
        "next_state",  # Next consciousness state
        "done",  # Episode termination
        "log_prob",  # Action log probability
        "value",  # State value estimate
        "advantage",  # Advantage estimate
        "consciousness_info",  # Additional consciousness metadata
        "timestamp",  # Experience timestamp
    ],
)


@dataclass
class ConsciousnessMemoryPriorities:
    """Priority settings for different types of consciousness experiences"""

    reflection_experiences: float = 1.5  # High priority for reflection learning
    ethical_dilemmas: float = 2.0  # Highest priority for ethical learning
    novel_discoveries: float = 1.3  # High priority for novel experiences
    integration_successes: float = 1.2  # High priority for successful integration
    consciousness_breakthroughs: float = 2.5  # Highest priority for consciousness growth
    failure_experiences: float = 1.1  # Slightly higher priority for learning from failures
    routine_experiences: float = 0.8  # Lower priority for routine experiences


class ConsciousnessReplayBuffer:
    """
    Advanced replay buffer for consciousness RL experiences.

    Features:
    - Consciousness-aware experience prioritization
    - Integration with LUKHAS memory fold system
    - Multi-objective experience sampling
    - Temporal coherence preservation
    - Ethical experience filtering
    """

    def __init__(
        self,
        capacity: int = 100000,
        alpha: float = 0.6,  # Prioritization exponent
        beta: float = 0.4,  # Importance sampling exponent
        beta_increment: float = 0.001,  # Beta annealing rate
        memory_system: MemoryFoldSystem | None = None,
        consciousness_priorities: ConsciousnessMemoryPriorities | None = None,
    ):
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.memory_system = memory_system
        self.consciousness_priorities = consciousness_priorities or ConsciousnessMemoryPriorities()

        # Storage
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.position = 0

        # Consciousness-specific storage
        self.consciousness_experiences = {
            "reflection": deque(maxlen=capacity // 10),
            "ethical": deque(maxlen=capacity // 10),
            "novel": deque(maxlen=capacity // 10),
            "integration": deque(maxlen=capacity // 10),
            "breakthrough": deque(maxlen=capacity // 20),
        }

        # Statistics
        self.total_experiences = 0
        self.consciousness_stats = {
            "reflection_count": 0,
            "ethical_count": 0,
            "novel_count": 0,
            "integration_count": 0,
            "breakthrough_count": 0,
        }

        logger.info(
            "🧠 ConsciousnessReplayBuffer initialized: capacity=%d, alpha=%.2f, beta=%.2f", capacity, alpha, beta
        )

        # Background task tracking: keep strong refs to asyncio tasks created by this buffer
        # prevents them from being garbage-collected and silences linter warnings.
        # Type: set[asyncio.Task]
        self._background_tasks = set()

    @instrument("AWARENESS", label="rl:experience_store", capability="rl:memory")
    def store(
        self,
        state: torch.Tensor,
        action: torch.Tensor,
        reward: float,
        next_state: torch.Tensor,
        done: bool,
        log_prob: float,
        value: float,
        advantage: float | None = None,
        consciousness_info: dict[str, Any] | None = None,
    ) -> None:
        """Store consciousness experience in replay buffer"""

        consciousness_info = consciousness_info or {}

        experience = ConsciousnessExperience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            log_prob=log_prob,
            value=value,
            advantage=advantage,
            consciousness_info=consciousness_info,
            timestamp=self.total_experiences,
        )

        # Calculate experience priority
        priority = self._calculate_experience_priority(experience)

        # Store in main buffer
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
            self.priorities.append(priority)
        else:
            self.buffer[self.position] = experience
            self.priorities[self.position] = priority

        # Store in consciousness-specific buffers
        self._store_consciousness_experience(experience)

        # Integrate with memory fold system
        if self.memory_system:
            # Create background task and keep a strong reference to avoid GC
            task = asyncio.create_task(self._integrate_with_memory_system(experience))
            self._background_tasks.add(task)

            # Remove task from the set when done to avoid unbounded growth
            task.add_done_callback(lambda t: self._background_tasks.discard(t))

        self.position = (self.position + 1) % self.capacity
        self.total_experiences += 1

        logger.debug("📦 Stored consciousness experience: reward=%.3f, priority=%.3f", reward, priority)

    def _calculate_experience_priority(self, experience: ConsciousnessExperience) -> float:
        """Calculate priority for consciousness experience"""

        base_priority = abs(experience.advantage) if experience.advantage else abs(experience.reward)
        consciousness_multiplier = 1.0

        consciousness_info = experience.consciousness_info

        # Consciousness-specific priority boosts
        if consciousness_info.get("is_reflection", False):
            consciousness_multiplier *= self.consciousness_priorities.reflection_experiences

        if consciousness_info.get("ethical_significance", 0.0) > 0.7:
            consciousness_multiplier *= self.consciousness_priorities.ethical_dilemmas

        if consciousness_info.get("novelty_score", 0.0) > 0.8:
            consciousness_multiplier *= self.consciousness_priorities.novel_discoveries

        if consciousness_info.get("integration_success", False):
            consciousness_multiplier *= self.consciousness_priorities.integration_successes

        if consciousness_info.get("consciousness_breakthrough", False):
            consciousness_multiplier *= self.consciousness_priorities.consciousness_breakthroughs

        if experience.reward < 0 and consciousness_info.get("learning_opportunity", False):
            consciousness_multiplier *= self.consciousness_priorities.failure_experiences

        # Temporal coherence bonus
        temporal_coherence = consciousness_info.get("temporal_coherence", 0.9)
        if temporal_coherence > 0.95:
            consciousness_multiplier *= 1.1

        # Apply consciousness multiplier
        final_priority = base_priority * consciousness_multiplier

        # Ensure minimum priority
        return max(final_priority, 1e-6)

    def _store_consciousness_experience(self, experience: ConsciousnessExperience) -> None:
        """Store experience in consciousness-specific buffers"""

        consciousness_info = experience.consciousness_info

        if consciousness_info.get("is_reflection", False):
            self.consciousness_experiences["reflection"].append(experience)
            self.consciousness_stats["reflection_count"] += 1

        if consciousness_info.get("ethical_significance", 0.0) > 0.7:
            self.consciousness_experiences["ethical"].append(experience)
            self.consciousness_stats["ethical_count"] += 1

        if consciousness_info.get("novelty_score", 0.0) > 0.8:
            self.consciousness_experiences["novel"].append(experience)
            self.consciousness_stats["novel_count"] += 1

        if consciousness_info.get("integration_success", False):
            self.consciousness_experiences["integration"].append(experience)
            self.consciousness_stats["integration_count"] += 1

        if consciousness_info.get("consciousness_breakthrough", False):
            self.consciousness_experiences["breakthrough"].append(experience)
            self.consciousness_stats["breakthrough_count"] += 1

    async def _integrate_with_memory_system(self, experience: ConsciousnessExperience) -> None:
        """Integrate experience with LUKHAS memory fold system"""

        try:
            # Convert experience to memory fold format
            memory_fold = {
                "timestamp": experience.timestamp,
                "experience_type": "rl_learning",
                "consciousness_state": experience.state,
                "action_taken": experience.action,
                "reward_received": experience.reward,
                "learning_outcome": experience.consciousness_info,
                "memory_salience": self._calculate_memory_salience(experience),
                "temporal_coherence": experience.consciousness_info.get("temporal_coherence", 0.9),
                "tags": self._generate_memory_tags(experience),
            }

            # Store in memory system
            if hasattr(self.memory_system, "store_consciousness_experience"):
                await self.memory_system.store_consciousness_experience(memory_fold)

        except Exception as e:
            logger.warning("⚠️ Failed to integrate experience with memory system: %s", str(e))

    def _calculate_memory_salience(self, experience: ConsciousnessExperience) -> float:
        """Calculate memory salience for experience"""

        base_salience = min(abs(experience.reward), 1.0)
        consciousness_info = experience.consciousness_info

        # Boost salience for important consciousness events
        if consciousness_info.get("consciousness_breakthrough", False):
            base_salience = min(base_salience + 0.5, 1.0)

        if consciousness_info.get("ethical_significance", 0.0) > 0.8:
            base_salience = min(base_salience + 0.3, 1.0)

        if consciousness_info.get("is_reflection", False):
            base_salience = min(base_salience + 0.2, 1.0)

        return base_salience

    def _generate_memory_tags(self, experience: ConsciousnessExperience) -> list[str]:
        """Generate memory tags for experience"""

        tags = ["rl_experience"]
        consciousness_info = experience.consciousness_info

        # Add consciousness-specific tags
        if consciousness_info.get("is_reflection", False):
            tags.append("reflection")

        if consciousness_info.get("ethical_significance", 0.0) > 0.7:
            tags.append("ethical_learning")

        if consciousness_info.get("novelty_score", 0.0) > 0.8:
            tags.append("novel_discovery")

        if consciousness_info.get("integration_success", False):
            tags.append("integration")

        if consciousness_info.get("consciousness_breakthrough", False):
            tags.append("breakthrough")

        # Add reward-based tags
        if experience.reward > 0.5:
            tags.append("high_reward")
        elif experience.reward < -0.5:
            tags.append("learning_failure")

        return tags

    @instrument("DECISION", label="rl:experience_sample", capability="rl:memory")
    def sample(
        self, batch_size: int, consciousness_focus: str | None = None, temporal_coherence_threshold: float = 0.0
    ) -> tuple[list[ConsciousnessExperience], torch.Tensor, list[int]]:
        """
        Sample batch of consciousness experiences.

        Args:
            batch_size: Number of experiences to sample
            consciousness_focus: Focus on specific type ('reflection', 'ethical', etc.)
            temporal_coherence_threshold: Minimum temporal coherence for sampling

        Returns:
            Tuple of (experiences, importance_weights, indices)
        """

        if len(self.buffer) < batch_size:
            logger.warning("⚠️ Buffer has fewer experiences than requested batch size")
            batch_size = len(self.buffer)

        # Update beta for importance sampling
        self.beta = min(1.0, self.beta + self.beta_increment)

        if consciousness_focus and consciousness_focus in self.consciousness_experiences:
            # Sample from consciousness-specific buffer
            experiences, indices = self._sample_consciousness_focused(batch_size, consciousness_focus)
        else:
            # Standard prioritized sampling
            experiences, indices = self._sample_prioritized(batch_size, temporal_coherence_threshold)

        # Calculate importance sampling weights
        importance_weights = self._calculate_importance_weights(indices)

        logger.debug("🎯 Sampled %d consciousness experiences (focus=%s)", len(experiences), consciousness_focus)

        return experiences, importance_weights, indices

    def _sample_consciousness_focused(
        self, batch_size: int, focus: str
    ) -> tuple[list[ConsciousnessExperience], list[int]]:
        """Sample from consciousness-specific experience buffer"""

        consciousness_buffer = self.consciousness_experiences[focus]

        if len(consciousness_buffer) < batch_size:
            # Not enough focused experiences, sample what we have plus general experiences
            focused_experiences = list(consciousness_buffer)
            remaining_needed = batch_size - len(focused_experiences)

            if remaining_needed > 0:
                general_experiences, general_indices = self._sample_prioritized(remaining_needed)
                focused_experiences.extend(general_experiences)

                # Create indices (approximate for focused experiences)
                focused_indices = list(range(len(focused_experiences)))
                return focused_experiences, focused_indices
        else:
            # Enough focused experiences available
            sampled_experiences = random.sample(list(consciousness_buffer), batch_size)
            indices = list(range(len(sampled_experiences)))
            return sampled_experiences, indices

        return list(consciousness_buffer), list(range(len(consciousness_buffer)))

    def _sample_prioritized(
        self, batch_size: int, temporal_coherence_threshold: float = 0.0
    ) -> tuple[list[ConsciousnessExperience], list[int]]:
        """Sample experiences using prioritized replay"""

        # Filter experiences by temporal coherence threshold
        valid_experiences = []
        valid_priorities = []
        valid_indices = []

        for i, (exp, priority) in enumerate(zip(self.buffer, self.priorities)):
            temporal_coherence = exp.consciousness_info.get("temporal_coherence", 1.0)
            if temporal_coherence >= temporal_coherence_threshold:
                valid_experiences.append(exp)
                valid_priorities.append(priority)
                valid_indices.append(i)

        if len(valid_experiences) < batch_size:
            logger.warning("⚠️ Not enough experiences meeting temporal coherence threshold")
            # Fallback to all experiences
            valid_experiences = list(self.buffer)
            valid_priorities = list(self.priorities)
            valid_indices = list(range(len(self.buffer)))

        # Calculate sampling probabilities
        priorities_array = np.array(valid_priorities)
        probabilities = priorities_array**self.alpha
        probabilities = probabilities / probabilities.sum()

        # Sample indices
        sampled_indices = np.random.choice(
            len(valid_experiences), size=min(batch_size, len(valid_experiences)), p=probabilities, replace=False
        )

        # Get sampled experiences
        sampled_experiences = [valid_experiences[i] for i in sampled_indices]
        original_indices = [valid_indices[i] for i in sampled_indices]

        return sampled_experiences, original_indices

    def _calculate_importance_weights(self, indices: list[int]) -> torch.Tensor:
        """Calculate importance sampling weights for sampled experiences"""

        if not indices or len(self.buffer) == 0:
            return torch.ones(len(indices))

        # Calculate sampling probabilities for sampled experiences
        priorities_array = np.array(list(self.priorities))
        probabilities = priorities_array**self.alpha
        probabilities = probabilities / probabilities.sum()

        # Calculate importance weights
        weights = []
        max_weight = (len(self.buffer) * probabilities.min()) ** (-self.beta)

        for idx in indices:
            if idx < len(probabilities):
                prob = probabilities[idx]
                weight = (len(self.buffer) * prob) ** (-self.beta)
                normalized_weight = weight / max_weight
                weights.append(normalized_weight)
            else:
                weights.append(1.0)  # Default weight

        return torch.tensor(weights, dtype=torch.float32)

    def update_priorities(self, indices: list[int], priorities: torch.Tensor) -> None:
        """Update priorities for sampled experiences"""

        for idx, priority in zip(indices, priorities):
            if idx < len(self.priorities):
                self.priorities[idx] = float(priority) + 1e-6  # Avoid zero priority

    def get_consciousness_statistics(self) -> dict[str, Any]:
        """Get consciousness experience statistics"""

        total_experiences = len(self.buffer)

        stats = {
            "total_experiences": total_experiences,
            "consciousness_breakdown": self.consciousness_stats.copy(),
            "buffer_utilization": total_experiences / self.capacity,
            "priority_stats": {
                "mean_priority": float(np.mean(list(self.priorities))) if self.priorities else 0.0,
                "max_priority": float(np.max(list(self.priorities))) if self.priorities else 0.0,
                "min_priority": float(np.min(list(self.priorities))) if self.priorities else 0.0,
            },
        }

        # Calculate consciousness ratios
        if total_experiences > 0:
            stats["consciousness_ratios"] = {
                key: count / total_experiences for key, count in self.consciousness_stats.items()
            }
        else:
            stats["consciousness_ratios"] = {key: 0.0 for key in self.consciousness_stats}

        return stats

    def save_buffer(self, filepath: str) -> None:
        """Save replay buffer to file"""

        try:
            buffer_data = {
                "buffer": list(self.buffer),
                "priorities": list(self.priorities),
                "consciousness_experiences": {
                    key: list(buffer) for key, buffer in self.consciousness_experiences.items()
                },
                "consciousness_stats": self.consciousness_stats,
                "position": self.position,
                "total_experiences": self.total_experiences,
                "alpha": self.alpha,
                "beta": self.beta,
            }

            with open(filepath, "wb") as f:
                pickle.dump(buffer_data, f)

            logger.info("💾 Saved consciousness replay buffer to %s", filepath)

        except Exception as e:
            logger.error("❌ Failed to save replay buffer: %s", str(e))

    def load_buffer(self, filepath: str) -> None:
        """Load replay buffer from file"""

        try:
            with open(filepath, "rb") as f:
                buffer_data = pickle.load(f)

            self.buffer = deque(buffer_data["buffer"], maxlen=self.capacity)
            self.priorities = deque(buffer_data["priorities"], maxlen=self.capacity)
            self.consciousness_experiences = {
                key: deque(experiences, maxlen=self.capacity // 10)
                for key, experiences in buffer_data["consciousness_experiences"].items()
            }
            self.consciousness_stats = buffer_data["consciousness_stats"]
            self.position = buffer_data["position"]
            self.total_experiences = buffer_data["total_experiences"]
            self.alpha = buffer_data.get("alpha", self.alpha)
            self.beta = buffer_data.get("beta", self.beta)

            logger.info("📂 Loaded consciousness replay buffer from %s", filepath)

        except Exception as e:
            logger.error("❌ Failed to load replay buffer: %s", str(e))

    def clear(self) -> None:
        """Clear all experiences from buffer"""

        self.buffer.clear()
        self.priorities.clear()

        for buffer in self.consciousness_experiences.values():
            buffer.clear()

        self.consciousness_stats = {key: 0 for key in self.consciousness_stats}
        self.position = 0
        self.total_experiences = 0

        logger.info("🗑️ Cleared consciousness replay buffer")

    def __len__(self) -> int:
        """Return number of experiences in buffer"""
        return len(self.buffer)

    def __bool__(self) -> bool:
        """Return True if buffer has experiences"""
        return len(self.buffer) > 0


class EpisodicConsciousnessBuffer:
    """
    Buffer for complete consciousness episodes.

    Stores entire episodes for trajectory-based learning algorithms
    like PPO or for consciousness temporal analysis.
    """

    def __init__(self, max_episodes: int = 1000):
        self.max_episodes = max_episodes
        self.episodes = deque(maxlen=max_episodes)
        self.current_episode = []

        logger.info("🧠 EpisodicConsciousnessBuffer initialized: max_episodes=%d", max_episodes)

    def add_experience(
        self,
        state: torch.Tensor,
        action: torch.Tensor,
        reward: float,
        next_state: torch.Tensor,
        done: bool,
        consciousness_info: dict[str, Any] | None = None,
    ) -> None:
        """Add experience to current episode"""

        experience = {
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "done": done,
            "consciousness_info": consciousness_info or {},
        }

        self.current_episode.append(experience)

        if done:
            self.finish_episode()

    def finish_episode(self) -> None:
        """Finish current episode and start new one"""

        if self.current_episode:
            episode_data = {
                "experiences": self.current_episode.copy(),
                "episode_length": len(self.current_episode),
                "total_reward": sum(exp["reward"] for exp in self.current_episode),
                "consciousness_metrics": self._calculate_episode_consciousness_metrics(),
            }

            self.episodes.append(episode_data)
            self.current_episode = []

            logger.debug(
                "📝 Finished consciousness episode: length=%d, reward=%.2f",
                episode_data["episode_length"],
                episode_data["total_reward"],
            )

    def _calculate_episode_consciousness_metrics(self) -> dict[str, float]:
        """Calculate consciousness metrics for the episode"""

        if not self.current_episode:
            return {}

        consciousness_infos = [exp["consciousness_info"] for exp in self.current_episode]

        metrics = {
            "avg_temporal_coherence": np.mean([info.get("temporal_coherence", 0.9) for info in consciousness_infos]),
            "reflection_actions": sum([1 for info in consciousness_infos if info.get("is_reflection", False)]),
            "ethical_significance": np.mean([info.get("ethical_significance", 0.5) for info in consciousness_infos]),
            "consciousness_growth": sum([info.get("consciousness_growth", 0.0) for info in consciousness_infos]),
        }

        return metrics

    def sample_episodes(self, batch_size: int) -> list[dict[str, Any]]:
        """Sample episodes for training"""

        if len(self.episodes) < batch_size:
            return list(self.episodes)

        return random.sample(list(self.episodes), batch_size)

    def get_recent_episodes(self, num_episodes: int) -> list[dict[str, Any]]:
        """Get most recent episodes"""

        return list(self.episodes)[-num_episodes:]

    def clear(self) -> None:
        """Clear all episodes"""

        self.episodes.clear()
        self.current_episode = []

        logger.info("🗑️ Cleared episodic consciousness buffer")

    def __len__(self) -> int:
        """Return number of complete episodes"""
        return len(self.episodes)
