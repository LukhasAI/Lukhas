#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: episodic_replay_buffer.py
║ Path: memory/systems/episodic_replay_buffer.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🚀 LUKHAS AI - EPISODIC REPLAY BUFFER FOR REINFORCEMENT LEARNING
║ ║ Bio-inspired memory replay for AGI learning and decision optimization
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: EPISODIC REPLAY BUFFER
║ ║ Path: memory/systems/episodic_replay_buffer.py
║ ║ Version: 1.0.0 | Created: 2025-10-20
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Description: A sophisticated memory system poised to enhance the learning
║ ║              capabilities of autonomous agents through the art of episodic
║ ║              memory recall.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the grand theater of intelligence, where the dance of neurons paints the
║ ║ tapestry of cognition, lies a reservoir of experiences, a sacred vault of
║ ║ memories—the Episodic Replay Buffer. This module stands as the sentinel
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛADVANCED, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import heapq
import random
import threading
from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

import numpy as np

# Experience tuple for storing RL experiences
Experience = namedtuple(
    "Experience",
    [
        "state",
        "action",
        "reward",
        "next_state",
        "done",
        "timestamp",
        "priority",
        "memory_id",
        "consciousness_level",
    ])


class ReplayStrategy(Enum):
    """Strategies for memory replay"""

    UNIFORM_RANDOM = "uniform_random"
    PRIORITY_BASED = "priority_based"
    TEMPORAL_DIFFERENCE = "temporal_difference"
    CONSCIOUSNESS_WEIGHTED = "consciousness_weighted"
    RECENCY_WEIGHTED = "recency_weighted"
    SURPRISE_BASED = "surprise_based"
    MIXED_STRATEGY = "mixed_strategy"


class ConsolidationPhase(Enum):
    """Phases of memory consolidation during replay"""

    ACQUISITION = "acquisition"  # Initial experience storage
    CONSOLIDATION = "consolidation"  # Memory strengthening
    RECONSOLIDATION = "reconsolidation"  # Memory updating
    INTEGRATION = "integration"  # Cross-memory integration
    GENERALIZATION = "generalization"  # Pattern extraction


@dataclass
class EpisodicMemory:
    """Container for episodic memory experiences"""

    memory_id: str
    experience: Experience
    replay_count: int = 0
    last_replayed: Optional[datetime] = None
    consolidation_strength: float = 0.0
    surprise_value: float = 0.0
    consciousness_impact: float = 0.0
    learning_value: float = 0.0

    # Temporal context
    episode_id: Optional[str] = None
    sequence_position: int = 0

    # Relationships
    related_memories: list[str] = field(default_factory=list)
    causal_predecessors: list[str] = field(default_factory=list)
    causal_successors: list[str] = field(default_factory=list)

    def update_priority(self, td_error: float, consciousness_level: float):
        """Update memory priority based on learning signals"""

        # Combine TD error with consciousness impact
        base_priority = abs(td_error) + 1e-6  # Small epsilon to avoid zero priority
        consciousness_boost = 1.0 + (consciousness_level * 0.5)

        # Update experience priority
        new_experience = self.experience._replace(priority=base_priority * consciousness_boost)
        self.experience = new_experience

        # Update consciousness impact
        self.consciousness_impact = consciousness_level

        # Update learning value based on replay frequency and recency
        recency_factor = 1.0
        if self.last_replayed:
            days_since_replay = (datetime.now(timezone.utc) - self.last_replayed).days
            recency_factor = max(0.1, 1.0 - (days_since_replay * 0.1))

        # Diminishing returns on replay count
        replay_factor = 1.0 / (1.0 + self.replay_count * 0.1)

        self.learning_value = base_priority * consciousness_boost * recency_factor * replay_factor

    def mark_replayed(self):
        """Mark this memory as having been replayed"""
        self.replay_count += 1
        self.last_replayed = datetime.now(timezone.utc)

        # Strengthen consolidation
        self.consolidation_strength = min(1.0, self.consolidation_strength + 0.1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "experience": {
                "state": (
                    self.experience.state.tolist()
                    if isinstance(self.experience.state, np.ndarray)
                    else self.experience.state
                ),
                "action": (
                    self.experience.action.tolist()
                    if isinstance(self.experience.action, np.ndarray)
                    else self.experience.action
                ),
                "reward": float(self.experience.reward),
                "next_state": (
                    self.experience.next_state.tolist()
                    if isinstance(self.experience.next_state, np.ndarray)
                    else self.experience.next_state
                ),
                "done": bool(self.experience.done),
                "timestamp": self.experience.timestamp.isoformat(),
                "priority": float(self.experience.priority),
                "consciousness_level": float(self.experience.consciousness_level),
            },
            "replay_count": self.replay_count,
            "last_replayed": (self.last_replayed.isoformat() if self.last_replayed else None),
            "consolidation_strength": self.consolidation_strength,
            "surprise_value": self.surprise_value,
            "consciousness_impact": self.consciousness_impact,
            "learning_value": self.learning_value,
            "episode_id": self.episode_id,
            "sequence_position": self.sequence_position,
            "related_memories": self.related_memories,
            "causal_predecessors": self.causal_predecessors,
            "causal_successors": self.causal_successors,
        }


class PrioritizedReplayBuffer:
    """
    Priority-based episodic replay buffer with consciousness-aware sampling.

    Implements biologically-inspired memory replay similar to hippocampal
    replay during sleep, with priority sampling based on learning value.
    """

    def __init__(
        self,
        capacity: int = 100000,
        alpha: float = 0.6,  # Priority exponent
        beta: float = 0.4,  # Importance sampling exponent
        consciousness_weight: float = 0.3,
        surprise_weight: float = 0.2,
    ):
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.consciousness_weight = consciousness_weight
        self.surprise_weight = surprise_weight

        # Storage
        self.memories: dict[str, EpisodicMemory] = {}
        self.priority_tree = []  # Min-heap for priority sampling

        # Statistics
        self.total_samples = 0
        self.total_replays = 0
        self.consolidation_stats = {phase.value: 0 for phase in ConsolidationPhase}

        # Threading for background consolidation
        self._consolidation_lock = threading.Lock()

        logger.info(
            "Prioritized replay buffer initialized",
            capacity=capacity,
            alpha=alpha,
            beta=beta,
            consciousness_weight=consciousness_weight,
        )

    def add_experience(
        self,
        state: np.ndarray,
        action: Union[int, np.ndarray],
        reward: float,
        next_state: np.ndarray,
        done: bool,
        consciousness_level: float = 0.5,
        episode_id: Optional[str] = None,
        sequence_position: int = 0,
    ) -> str:
        """Add a new experience to the replay buffer"""

        # Generate memory ID
        memory_id = f"exp_{self.total_samples}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Create experience
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            timestamp=datetime.now(timezone.utc),
            priority=1.0,  # Initial priority
            memory_id=memory_id,
            consciousness_level=consciousness_level,
        )

        # Create episodic memory
        episodic_memory = EpisodicMemory(
            memory_id=memory_id,
            experience=experience,
            episode_id=episode_id,
            sequence_position=sequence_position,
        )

        # Calculate initial surprise value
        episodic_memory.surprise_value = self._calculate_surprise_value(experience)

        # Update priority based on surprise and consciousness
        td_error = abs(reward)  # Simple initial TD error estimate
        episodic_memory.update_priority(td_error, consciousness_level)

        # Store memory
        with self._consolidation_lock:
            # Remove oldest memories if at capacity
            if len(self.memories) >= self.capacity:
                self._evict_oldest_memory()

            self.memories[memory_id] = episodic_memory

            # Update priority tree
            heapq.heappush(self.priority_tree, (-episodic_memory.learning_value, memory_id))

        self.total_samples += 1
        self.consolidation_stats[ConsolidationPhase.ACQUISITION.value] += 1

        logger.debug(
            "Experience added to replay buffer",
            memory_id=memory_id[:8],
            reward=reward,
            consciousness_level=consciousness_level,
            surprise_value=episodic_memory.surprise_value,
        )

        return memory_id

    def sample_batch(
        self,
        batch_size: int,
        strategy: ReplayStrategy = ReplayStrategy.PRIORITY_BASED,
        beta: Optional[float] = None,
    ) -> tuple[list[EpisodicMemory], np.ndarray]:
        """
        Sample a batch of experiences for replay.

        Args:
            batch_size: Number of experiences to sample
            strategy: Replay strategy to use
            beta: Importance sampling exponent (overrides default)

        Returns:
            Tuple of (sampled_memories, importance_weights)
        """

        if not self.memories:
            return [], np.array([])

        beta = beta or self.beta

        with self._consolidation_lock:
            if strategy == ReplayStrategy.UNIFORM_RANDOM:
                sampled_memories = self._sample_uniform_random(batch_size)
            elif strategy == ReplayStrategy.PRIORITY_BASED:
                sampled_memories = self._sample_priority_based(batch_size)
            elif strategy == ReplayStrategy.CONSCIOUSNESS_WEIGHTED:
                sampled_memories = self._sample_consciousness_weighted(batch_size)
            elif strategy == ReplayStrategy.SURPRISE_BASED:
                sampled_memories = self._sample_surprise_based(batch_size)
            elif strategy == ReplayStrategy.MIXED_STRATEGY:
                sampled_memories = self._sample_mixed_strategy(batch_size)
            else:
                sampled_memories = self._sample_priority_based(batch_size)

        # Calculate importance sampling weights
        importance_weights = self._calculate_importance_weights(sampled_memories, beta)

        # Mark memories as replayed
        for memory in sampled_memories:
            memory.mark_replayed()

        self.total_replays += len(sampled_memories)
        self.consolidation_stats[ConsolidationPhase.CONSOLIDATION.value] += len(sampled_memories)

        logger.debug(
            "Batch sampled for replay",
            batch_size=len(sampled_memories),
            strategy=strategy.value,
            avg_priority=np.mean([m.learning_value for m in sampled_memories]),
        )

        return sampled_memories, importance_weights

    def _sample_uniform_random(self, batch_size: int) -> list[EpisodicMemory]:
        """Sample experiences uniformly at random"""
        memory_ids = list(self.memories.keys())
        sampled_ids = random.sample(memory_ids, min(batch_size, len(memory_ids)))
        return [self.memories[mid] for mid in sampled_ids]

    def _sample_priority_based(self, batch_size: int) -> list[EpisodicMemory]:
        """Sample experiences based on priority/learning value"""

        # Get all memories sorted by learning value
        sorted_memories = sorted(self.memories.values(), key=lambda m: m.learning_value, reverse=True)

        # Prioritized sampling with alpha scaling
        priorities = np.array([m.learning_value**self.alpha for m in sorted_memories])

        if np.sum(priorities) == 0:
            return self._sample_uniform_random(batch_size)

        probabilities = priorities / np.sum(priorities)

        # Sample with replacement
        sampled_indices = np.random.choice(
            len(sorted_memories),
            size=min(batch_size, len(sorted_memories)),
            p=probabilities,
            replace=True,
        )

        return [sorted_memories[i] for i in sampled_indices]

    def _sample_consciousness_weighted(self, batch_size: int) -> list[EpisodicMemory]:
        """Sample experiences weighted by consciousness impact"""

        consciousness_weights = np.array([m.consciousness_impact + 1e-6 for m in self.memories.values()])

        probabilities = consciousness_weights / np.sum(consciousness_weights)

        memory_list = list(self.memories.values())
        sampled_indices = np.random.choice(
            len(memory_list),
            size=min(batch_size, len(memory_list)),
            p=probabilities,
            replace=True,
        )

        return [memory_list[i] for i in sampled_indices]

    def _sample_surprise_based(self, batch_size: int) -> list[EpisodicMemory]:
        """Sample experiences based on surprise value"""

        surprise_weights = np.array([m.surprise_value + 1e-6 for m in self.memories.values()])

        probabilities = surprise_weights / np.sum(surprise_weights)

        memory_list = list(self.memories.values())
        sampled_indices = np.random.choice(
            len(memory_list),
            size=min(batch_size, len(memory_list)),
            p=probabilities,
            replace=True,
        )

        return [memory_list[i] for i in sampled_indices]

    def _sample_mixed_strategy(self, batch_size: int) -> list[EpisodicMemory]:
        """Sample using a mixture of strategies"""

        # Allocate batch among different strategies
        priority_count = int(batch_size * 0.4)
        consciousness_count = int(batch_size * 0.3)
        surprise_count = int(batch_size * 0.2)
        random_count = batch_size - priority_count - consciousness_count - surprise_count

        sampled_memories = []

        if priority_count > 0:
            sampled_memories.extend(self._sample_priority_based(priority_count))

        if consciousness_count > 0:
            sampled_memories.extend(self._sample_consciousness_weighted(consciousness_count))

        if surprise_count > 0:
            sampled_memories.extend(self._sample_surprise_based(surprise_count))

        if random_count > 0:
            sampled_memories.extend(self._sample_uniform_random(random_count))

        return sampled_memories

    def _calculate_importance_weights(self, sampled_memories: list[EpisodicMemory], beta: float) -> np.ndarray:
        """Calculate importance sampling weights for bias correction"""

        if not sampled_memories:
            return np.array([])

        # Get sampling probabilities
        all_priorities = np.array([m.learning_value for m in self.memories.values()])
        total_priority = np.sum(all_priorities**self.alpha)

        weights = []
        for memory in sampled_memories:
            prob = (memory.learning_value**self.alpha) / total_priority
            weight = (len(self.memories) * prob) ** (-beta)
            weights.append(weight)

        weights = np.array(weights)

        # Normalize weights
        if np.max(weights) > 0:
            weights = weights / np.max(weights)

        return weights

    def _calculate_surprise_value(self, experience: Experience) -> float:
        """Calculate surprise value for a new experience"""

        # Simple surprise calculation based on reward magnitude
        # In a more sophisticated system, this would compare against
        # expected rewards from a learned model

        reward_surprise = abs(experience.reward)

        # Add temporal surprise (unusual timing)
        temporal_surprise = 0.0
        if self.memories:
            recent_memories = [
                m
                for m in self.memories.values()
                if (datetime.now(timezone.utc) - m.experience.timestamp).total_seconds() < 300  # 5 minutes
            ]

            if recent_memories:
                avg_recent_reward = np.mean([m.experience.reward for m in recent_memories])
                temporal_surprise = abs(experience.reward - avg_recent_reward)

        # Combine surprise components
        total_surprise = reward_surprise * 0.7 + temporal_surprise * 0.3

        # Normalize to [0, 1]
        return min(1.0, total_surprise / 10.0)  # Assuming max surprise of 10

    def _evict_oldest_memory(self):
        """Evict the oldest memory to make room for new ones"""

        if not self.memories:
            return

        # Find oldest memory
        oldest_memory_id = min(
            self.memories.keys(),
            key=lambda mid: self.memories[mid].experience.timestamp,
        )

        # Remove from storage
        del self.memories[oldest_memory_id]

        # Rebuild priority tree (simple approach for now)
        self.priority_tree = [(-m.learning_value, mid) for mid, m in self.memories.items()]
        heapq.heapify(self.priority_tree)

    def update_priorities(self, memory_ids: list[str], td_errors: np.ndarray):
        """Update priorities for specific memories based on TD errors"""

        with self._consolidation_lock:
            for memory_id, td_error in zip(memory_ids, td_errors):
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    memory.update_priority(td_error, memory.consciousness_impact)

        # Rebuild priority tree
        self.priority_tree = [(-m.learning_value, mid) for mid, m in self.memories.items()]
        heapq.heapify(self.priority_tree)

        self.consolidation_stats[ConsolidationPhase.RECONSOLIDATION.value] += len(memory_ids)

    def get_episode_trajectory(self, episode_id: str) -> list[EpisodicMemory]:
        """Get all memories from a specific episode in sequence"""

        episode_memories = [memory for memory in self.memories.values() if memory.episode_id == episode_id]

        # Sort by sequence position
        episode_memories.sort(key=lambda m: m.sequence_position)

        return episode_memories

    def consolidate_memories(self, consolidation_phase: ConsolidationPhase = ConsolidationPhase.CONSOLIDATION):
        """Perform memory consolidation similar to sleep replay"""

        with self._consolidation_lock:
            if consolidation_phase == ConsolidationPhase.CONSOLIDATION:
                self._strengthen_important_memories()
            elif consolidation_phase == ConsolidationPhase.INTEGRATION:
                self._integrate_related_memories()
            elif consolidation_phase == ConsolidationPhase.GENERALIZATION:
                self._extract_patterns()

        self.consolidation_stats[consolidation_phase.value] += 1

        logger.info(
            "Memory consolidation completed",
            phase=consolidation_phase.value,
            total_memories=len(self.memories),
        )

    def _strengthen_important_memories(self):
        """Strengthen memories with high learning value"""

        # Identify top memories for strengthening
        top_memories = sorted(self.memories.values(), key=lambda m: m.learning_value, reverse=True)[
            : int(len(self.memories) * 0.1)
        ]  # Top 10%

        for memory in top_memories:
            memory.consolidation_strength = min(1.0, memory.consolidation_strength + 0.2)

    def _integrate_related_memories(self):
        """Find and link related memories for integration"""

        memory_list = list(self.memories.values())

        for i, memory_a in enumerate(memory_list):
            for _j, memory_b in enumerate(memory_list[i + 1 :], i + 1):
                # Calculate similarity
                similarity = self._calculate_memory_similarity(memory_a, memory_b)

                if similarity > 0.7:  # Threshold for relatedness
                    # Link memories
                    if memory_b.memory_id not in memory_a.related_memories:
                        memory_a.related_memories.append(memory_b.memory_id)

                    if memory_a.memory_id not in memory_b.related_memories:
                        memory_b.related_memories.append(memory_a.memory_id)

    def _calculate_memory_similarity(self, memory_a: EpisodicMemory, memory_b: EpisodicMemory) -> float:
        """Calculate similarity between two memories"""

        # State similarity
        state_a = memory_a.experience.state
        state_b = memory_b.experience.state

        if isinstance(state_a, np.ndarray) and isinstance(state_b, np.ndarray):
            if state_a.shape == state_b.shape:
                state_similarity = np.corrcoef(state_a.flatten(), state_b.flatten())[0, 1]
                state_similarity = max(0, state_similarity)  # Handle NaN
            else:
                state_similarity = 0.0
        else:
            state_similarity = 1.0 if state_a == state_b else 0.0

        # Action similarity
        action_similarity = 1.0 if np.array_equal(memory_a.experience.action, memory_b.experience.action) else 0.0

        # Reward similarity
        reward_diff = abs(memory_a.experience.reward - memory_b.experience.reward)
        reward_similarity = max(0, 1.0 - reward_diff / 10.0)  # Normalize by max expected reward

        # Temporal similarity
        time_diff = abs((memory_a.experience.timestamp - memory_b.experience.timestamp).total_seconds())
        temporal_similarity = max(0, 1.0 - time_diff / 3600.0)  # 1 hour window

        # Combined similarity
        return state_similarity * 0.4 + action_similarity * 0.2 + reward_similarity * 0.2 + temporal_similarity * 0.2

    def _extract_patterns(self):
        """Extract common patterns across memories for generalization"""

        # Group memories by similar states/actions
        pattern_groups = {}

        for memory in self.memories.values():
            # Create a simple pattern key (this could be more sophisticated)
            pattern_key = f"action_{memory.experience.action}"

            if pattern_key not in pattern_groups:
                pattern_groups[pattern_key] = []

            pattern_groups[pattern_key].append(memory)

        # Identify significant patterns
        for memories in pattern_groups.values():
            if len(memories) >= 5:  # Pattern must appear multiple times
                avg_reward = np.mean([m.experience.reward for m in memories])

                # Update learning values based on pattern strength
                for memory in memories:
                    pattern_bonus = abs(avg_reward) * 0.1
                    memory.learning_value += pattern_bonus

    def get_replay_statistics(self) -> dict[str, Any]:
        """Get comprehensive replay buffer statistics"""

        if not self.memories:
            return {"total_memories": 0}

        # Basic statistics
        total_memories = len(self.memories)
        avg_priority = np.mean([m.learning_value for m in self.memories.values()])
        avg_consolidation = np.mean([m.consolidation_strength for m in self.memories.values()])
        avg_replay_count = np.mean([m.replay_count for m in self.memories.values()])

        # Reward statistics
        rewards = [m.experience.reward for m in self.memories.values()]
        reward_stats = {
            "mean": np.mean(rewards),
            "std": np.std(rewards),
            "min": np.min(rewards),
            "max": np.max(rewards),
        }

        # Consciousness statistics
        consciousness_levels = [m.consciousness_impact for m in self.memories.values()]
        consciousness_stats = {
            "mean": np.mean(consciousness_levels),
            "std": np.std(consciousness_levels),
            "high_consciousness_memories": sum(1 for c in consciousness_levels if c > 0.7),
        }

        # Episode statistics
        episodes = {m.episode_id for m in self.memories.values() if m.episode_id}

        return {
            "total_memories": total_memories,
            "total_samples": self.total_samples,
            "total_replays": self.total_replays,
            "avg_priority": avg_priority,
            "avg_consolidation_strength": avg_consolidation,
            "avg_replay_count": avg_replay_count,
            "reward_statistics": reward_stats,
            "consciousness_statistics": consciousness_stats,
            "unique_episodes": len(episodes),
            "consolidation_statistics": self.consolidation_stats.copy(),
            "buffer_utilization": total_memories / self.capacity,
        }


class DreamStateReplay:
    """
    Dream-state memory replay system for offline learning.

    Simulates REM sleep-like replay patterns for memory consolidation
    and creative insight generation.
    """

    def __init__(
        self,
        replay_buffer: PrioritizedReplayBuffer,
        dream_cycles_per_session: int = 5,
        memories_per_cycle: int = 20,
    ):
        self.replay_buffer = replay_buffer
        self.dream_cycles_per_session = dream_cycles_per_session
        self.memories_per_cycle = memories_per_cycle

        # Dream statistics
        self.dream_sessions = 0
        self.insights_generated = 0
        self.novel_combinations = 0

        logger.info(
            "Dream-state replay system initialized",
            cycles_per_session=dream_cycles_per_session,
            memories_per_cycle=memories_per_cycle,
        )

    async def enter_dream_state(self) -> dict[str, Any]:
        """Enter dream state and perform memory replay for consolidation"""

        logger.info("Entering dream state for memory consolidation")

        dream_results = {
            "session_id": f"dream_{self.dream_sessions}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "cycles_completed": 0,
            "memories_replayed": 0,
            "insights_generated": 0,
            "novel_combinations": 0,
            "consolidation_improvements": [],
        }

        for cycle in range(self.dream_cycles_per_session):
            cycle_results = await self._perform_dream_cycle(cycle)

            dream_results["cycles_completed"] += 1
            dream_results["memories_replayed"] += cycle_results["memories_replayed"]
            dream_results["insights_generated"] += cycle_results["insights_generated"]
            dream_results["novel_combinations"] += cycle_results["novel_combinations"]
            dream_results["consolidation_improvements"].extend(cycle_results["improvements"])

            # Brief pause between cycles (simulating sleep stages)
            await asyncio.sleep(0.1)

        self.dream_sessions += 1
        self.insights_generated += dream_results["insights_generated"]
        self.novel_combinations += dream_results["novel_combinations"]

        logger.info(
            "Dream state completed",
            session_id=dream_results["session_id"],
            cycles=dream_results["cycles_completed"],
            memories_replayed=dream_results["memories_replayed"],
            insights=dream_results["insights_generated"],
        )

        return dream_results

    async def _perform_dream_cycle(self, cycle_number: int) -> dict[str, Any]:
        """Perform a single dream cycle"""

        # Sample memories with different strategies based on cycle
        if cycle_number % 2 == 0:
            # Even cycles: focus on high-priority memories
            strategy = ReplayStrategy.PRIORITY_BASED
        else:
            # Odd cycles: explore surprising or novel combinations
            strategy = ReplayStrategy.SURPRISE_BASED

        sampled_memories, _ = self.replay_buffer.sample_batch(batch_size=self.memories_per_cycle, strategy=strategy)

        cycle_results = {
            "memories_replayed": len(sampled_memories),
            "insights_generated": 0,
            "novel_combinations": 0,
            "improvements": [],
        }

        # Analyze memory combinations for insights
        insights = self._analyze_memory_combinations(sampled_memories)
        cycle_results["insights_generated"] = len(insights)

        # Find novel combinations
        novel_combinations = self._find_novel_combinations(sampled_memories)
        cycle_results["novel_combinations"] = len(novel_combinations)

        # Perform consolidation improvements
        improvements = self._improve_memory_consolidation(sampled_memories)
        cycle_results["improvements"] = improvements

        return cycle_results

    def _analyze_memory_combinations(self, memories: list[EpisodicMemory]) -> list[dict[str, Any]]:
        """Analyze combinations of memories for potential insights"""

        insights = []

        # Look for patterns across memories
        for i, memory_a in enumerate(memories):
            for memory_b in memories[i + 1 :]:
                # Check for interesting combinations
                if self._is_insightful_combination(memory_a, memory_b):
                    insight = {
                        "type": "memory_combination",
                        "memory_a": memory_a.memory_id,
                        "memory_b": memory_b.memory_id,
                        "insight_value": self._calculate_insight_value(memory_a, memory_b),
                        "description": f"Novel combination of {memory_a.memory_id[:8]} and {memory_b.memory_id[:8]}",
                    }
                    insights.append(insight)

        return insights

    def _is_insightful_combination(self, memory_a: EpisodicMemory, memory_b: EpisodicMemory) -> bool:
        """Check if two memories form an insightful combination"""

        # Different actions but similar states might reveal strategy insights
        state_similar = self._calculate_state_similarity(memory_a, memory_b) > 0.8
        action_different = not np.array_equal(memory_a.experience.action, memory_b.experience.action)
        reward_different = abs(memory_a.experience.reward - memory_b.experience.reward) > 1.0

        return state_similar and action_different and reward_different

    def _calculate_state_similarity(self, memory_a: EpisodicMemory, memory_b: EpisodicMemory) -> float:
        """Calculate state similarity between two memories"""

        state_a = memory_a.experience.state
        state_b = memory_b.experience.state

        if isinstance(state_a, np.ndarray) and isinstance(state_b, np.ndarray):
            if state_a.shape == state_b.shape:
                return np.corrcoef(state_a.flatten(), state_b.flatten())[0, 1]

        return 1.0 if np.array_equal(state_a, state_b) else 0.0

    def _calculate_insight_value(self, memory_a: EpisodicMemory, memory_b: EpisodicMemory) -> float:
        """Calculate the value of an insight from memory combination"""

        # Higher value for memories with different outcomes
        reward_diff = abs(memory_a.experience.reward - memory_b.experience.reward)

        # Higher value for high-consciousness memories
        consciousness_avg = (memory_a.consciousness_impact + memory_b.consciousness_impact) / 2

        # Higher value for well-consolidated memories
        consolidation_avg = (memory_a.consolidation_strength + memory_b.consolidation_strength) / 2

        return reward_diff * 0.5 + consciousness_avg * 0.3 + consolidation_avg * 0.2

    def _find_novel_combinations(self, memories: list[EpisodicMemory]) -> list[dict[str, Any]]:
        """Find novel combinations of memories that haven't been explored"""

        novel_combinations = []

        # Group memories by episode
        episode_groups = {}
        for memory in memories:
            if memory.episode_id:
                if memory.episode_id not in episode_groups:
                    episode_groups[memory.episode_id] = []
                episode_groups[memory.episode_id].append(memory)

        # Find cross-episode combinations
        episode_ids = list(episode_groups.keys())
        for i, episode_a in enumerate(episode_ids):
            for episode_b in episode_ids[i + 1 :]:
                # Check if this combination has been explored
                memories_a = episode_groups[episode_a]
                memories_b = episode_groups[episode_b]

                if self._is_novel_episode_combination(memories_a, memories_b):
                    novel_combinations.append(
                        {
                            "type": "cross_episode",
                            "episode_a": episode_a,
                            "episode_b": episode_b,
                            "novelty_score": self._calculate_novelty_score(memories_a, memories_b),
                        }
                    )

        return novel_combinations

    def _is_novel_episode_combination(self, memories_a: list[EpisodicMemory], memories_b: list[EpisodicMemory]) -> bool:
        """Check if combination of episodes is novel"""

        # Simple novelty check: episodes with different reward patterns
        rewards_a = [m.experience.reward for m in memories_a]
        rewards_b = [m.experience.reward for m in memories_b]

        mean_a = np.mean(rewards_a)
        mean_b = np.mean(rewards_b)

        return abs(mean_a - mean_b) > 0.5  # Significant difference in outcomes

    def _calculate_novelty_score(self, memories_a: list[EpisodicMemory], memories_b: list[EpisodicMemory]) -> float:
        """Calculate novelty score for memory combination"""

        # Reward difference component
        rewards_a = [m.experience.reward for m in memories_a]
        rewards_b = [m.experience.reward for m in memories_b]

        reward_novelty = abs(np.mean(rewards_a) - np.mean(rewards_b))

        # Consciousness difference component
        consciousness_a = [m.consciousness_impact for m in memories_a]
        consciousness_b = [m.consciousness_impact for m in memories_b]

        consciousness_novelty = abs(np.mean(consciousness_a) - np.mean(consciousness_b))

        return reward_novelty * 0.7 + consciousness_novelty * 0.3

    def _improve_memory_consolidation(self, memories: list[EpisodicMemory]) -> list[str]:
        """Improve memory consolidation based on dream replay"""

        improvements = []

        for memory in memories:
            original_strength = memory.consolidation_strength

            # Strengthen memories replayed during dreams
            memory.consolidation_strength = min(1.0, memory.consolidation_strength + 0.1)

            # Strengthen memories with high consciousness impact
            if memory.consciousness_impact > 0.7:
                memory.consolidation_strength = min(1.0, memory.consolidation_strength + 0.05)

            if memory.consolidation_strength > original_strength:
                improvements.append(
                    f"Strengthened {memory.memory_id[:8]} from {original_strength:.2f} to {memory.consolidation_strength:.2f}"
                )

        return improvements


# Integration with existing memory systems
class EpisodicReplayMemoryWrapper:
    """
    Wrapper that adds episodic replay capabilities to existing memory systems.

    Integrates with OptimizedHybridMemoryFold to provide reinforcement
    learning and replay capabilities.
    """

    def __init__(
        self,
        base_memory_system,
        replay_buffer_capacity: int = 50000,
        enable_dream_replay: bool = True,
    ):
        self.base_memory_system = base_memory_system
        self.enable_dream_replay = enable_dream_replay

        # Initialize replay buffer
        self.replay_buffer = PrioritizedReplayBuffer(capacity=replay_buffer_capacity)

        # Initialize dream replay if enabled
        if enable_dream_replay:
            self.dream_replay = DreamStateReplay(self.replay_buffer)
        else:
            self.dream_replay = None

        logger.info(
            "Episodic replay memory wrapper initialized",
            buffer_capacity=replay_buffer_capacity,
            dream_replay_enabled=enable_dream_replay,
        )

    async def store_experience(
        self,
        state: np.ndarray,
        action: Union[int, np.ndarray],
        reward: float,
        next_state: np.ndarray,
        done: bool,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        consciousness_level: float = 0.5,
        episode_id: Optional[str] = None,
        sequence_position: int = 0,
    ) -> tuple[str, str]:
        """
        Store experience in both base memory system and replay buffer.

        Returns:
            Tuple of (base_memory_id, replay_memory_id)
        """

        # Store in base memory system
        base_memory_id = None
        if content:
            base_memory_id = await self.base_memory_system.fold_in_with_embedding(
                data=content,
                tags=tags or [],
                embedding=state if isinstance(state, np.ndarray) else None,
                importance=consciousness_level,
                reward=reward,
                action=action.tolist() if isinstance(action, np.ndarray) else action,
            )

        # Store in replay buffer
        replay_memory_id = self.replay_buffer.add_experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            consciousness_level=consciousness_level,
            episode_id=episode_id,
            sequence_position=sequence_position,
        )

        return base_memory_id, replay_memory_id

    async def replay_and_learn(
        self,
        batch_size: int = 32,
        strategy: ReplayStrategy = ReplayStrategy.PRIORITY_BASED,
        learning_callback: Optional[callable] = None,
    ) -> dict[str, Any]:
        """
        Sample experiences for replay and perform learning.

        Args:
            batch_size: Number of experiences to replay
            strategy: Replay sampling strategy
            learning_callback: Optional callback for learning from replayed experiences

        Returns:
            Dictionary with replay results
        """

        # Sample batch for replay
        sampled_memories, importance_weights = self.replay_buffer.sample_batch(batch_size=batch_size, strategy=strategy)

        replay_results = {
            "memories_replayed": len(sampled_memories),
            "avg_importance_weight": (np.mean(importance_weights) if len(importance_weights) > 0 else 0.0),
            "avg_priority": (np.mean([m.learning_value for m in sampled_memories]) if sampled_memories else 0.0),
            "learning_applied": False,
        }

        # Apply learning if callback provided
        if learning_callback and sampled_memories:
            try:
                # Extract experiences for learning
                experiences = [m.experience for m in sampled_memories]

                # Apply learning callback
                learning_results = await learning_callback(experiences, importance_weights)

                replay_results["learning_applied"] = True
                replay_results["learning_results"] = learning_results

                # Update priorities based on learning results if TD errors provided
                if "td_errors" in learning_results:
                    memory_ids = [m.memory_id for m in sampled_memories]
                    self.replay_buffer.update_priorities(memory_ids, learning_results["td_errors"])

            except Exception as e:
                logger.error("Learning callback failed", error=str(e))
                replay_results["learning_error"] = str(e)

        return replay_results

    async def enter_dream_state(self) -> dict[str, Any]:
        """Enter dream state for memory consolidation"""

        if not self.dream_replay:
            return {"error": "Dream replay not enabled"}

        return await self.dream_replay.enter_dream_state()

    def get_replay_statistics(self) -> dict[str, Any]:
        """Get comprehensive replay statistics"""

        stats = self.replay_buffer.get_replay_statistics()

        if self.dream_replay:
            stats["dream_sessions"] = self.dream_replay.dream_sessions
            stats["insights_generated"] = self.dream_replay.insights_generated
            stats["novel_combinations"] = self.dream_replay.novel_combinations

        return stats


# Factory functions for easy integration
async def create_episodic_replay_memory(
    base_memory_system=None,
    buffer_capacity: int = 50000,
    enable_dream_replay: bool = True,
    **kwargs,
):
    """
    Create an episodic replay-enabled memory system.

    Args:
        base_memory_system: Existing memory system to enhance
        buffer_capacity: Capacity of the replay buffer
        enable_dream_replay: Enable dream-state replay
        **kwargs: Additional arguments for replay buffer

    Returns:
        EpisodicReplayMemoryWrapper or PrioritizedReplayBuffer
    """

    if base_memory_system:
        return EpisodicReplayMemoryWrapper(
            base_memory_system=base_memory_system,
            replay_buffer_capacity=buffer_capacity,
            enable_dream_replay=enable_dream_replay,
        )
    else:
        return PrioritizedReplayBuffer(capacity=buffer_capacity, **kwargs)


# Example usage and testing
async def example_episodic_replay():
    """Example of episodic replay buffer usage"""

    print("🚀 Episodic Replay Buffer for Reinforcement Learning Demo")
    print("=" * 70)

    # Create replay buffer
    replay_buffer = await create_episodic_replay_memory(buffer_capacity=1000)

    print("✅ Created episodic replay buffer")

    # Simulate adding experiences from an episode
    episode_id = "episode_001"

    experiences = [
        # State, Action, Reward, Next_state, Done, Consciousness
        (np.random.randn(4), 0, 1.0, np.random.randn(4), False, 0.8),
        (np.random.randn(4), 1, 0.5, np.random.randn(4), False, 0.6),
        (
            np.random.randn(4),
            0,
            -1.0,
            np.random.randn(4),
            False,
            0.9,
        ),  # High consciousness negative reward
        (
            np.random.randn(4),
            2,
            2.0,
            np.random.randn(4),
            True,
            0.7,
        ),  # Episode end with high reward
    ]

    print(f"📥 Adding {len(experiences)} experiences to replay buffer...")

    for i, (state, action, reward, next_state, done, consciousness) in enumerate(experiences):
        memory_id = replay_buffer.add_experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            consciousness_level=consciousness,
            episode_id=episode_id,
            sequence_position=i,
        )

        print(f"  Added experience {i + 1}: reward={reward}, consciousness={consciousness}")

    # Sample experiences with different strategies
    print("\n🎯 Testing different replay strategies...")

    strategies = [
        ReplayStrategy.PRIORITY_BASED,
        ReplayStrategy.CONSCIOUSNESS_WEIGHTED,
        ReplayStrategy.SURPRISE_BASED,
        ReplayStrategy.MIXED_STRATEGY,
    ]

    for strategy in strategies:
        sampled_memories, weights = replay_buffer.sample_batch(batch_size=3, strategy=strategy)

        print(f"\n{strategy.value}:")
        print(f"  Sampled {len(sampled_memories)} memories")
        if len(weights) > 0:
            print(f"  Avg importance weight: {np.mean(weights)}:.3f}")

        for i, memory in enumerate(sampled_memories):
            print(f"    Memory {i + 1}: reward={memory.experience.reward}, priority={memory.learning_value:.3f}")

    # Simulate learning and priority updates
    print("\n📚 Simulating learning with TD error updates...")

    # Sample for learning
    sampled_memories, _ = replay_buffer.sample_batch(batch_size=2, strategy=ReplayStrategy.PRIORITY_BASED)

    if sampled_memories:
        # Simulate TD errors (larger errors for more surprising experiences)
        td_errors = np.array([abs(m.experience.reward) + np.random.normal(0, 0.1) for m in sampled_memories])
        memory_ids = [m.memory_id for m in sampled_memories]

        print(f"  Updating priorities for {len(memory_ids)} memories")
        print(f"  TD errors: {td_errors}")

        replay_buffer.update_priorities(memory_ids, td_errors)

        # Show updated priorities
        for i, memory_id in enumerate(memory_ids):
            updated_memory = replay_buffer.memories[memory_id]
            print(f"    {memory_id[:8]}: new priority = {updated_memory.learning_value:.3f}")

    # Perform memory consolidation
    print("\n🧠 Performing memory consolidation...")

    for phase in [ConsolidationPhase.CONSOLIDATION, ConsolidationPhase.INTEGRATION]:
        replay_buffer.consolidate_memories(phase)
        print(f"  Completed {phase.value}")

    # Enter dream state (if enabled)
    if hasattr(replay_buffer, "dream_replay") and replay_buffer.dream_replay:
        print("\n💭 Entering dream state for memory replay...")

        dream_results = await replay_buffer.enter_dream_state()

        print(f"  Dream session: {dream_results['session_id']}")
        print(f"  Cycles completed: {dream_results['cycles_completed']}")
        print(f"  Memories replayed: {dream_results['memories_replayed']}")
        print(f"  Insights generated: {dream_results['insights_generated']}")
        print(f"  Novel combinations: {dream_results['novel_combinations']}")

    # Get comprehensive statistics
    print("\n📊 Replay buffer statistics:")
    stats = replay_buffer.get_replay_statistics()

    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")

    print("\n✅ Episodic replay buffer demo completed!")

    return replay_buffer


if __name__ == "__main__":
    asyncio.run(example_episodic_replay())
