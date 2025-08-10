#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - REPLAY BUFFER
║ Experience replay for reinforcement learning and memory consolidation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: replay_buffer.py
║ Path: memory/replay/replay_buffer.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the theater of mind, experiences replay like echoes of thunder—some     │
║ │ loud and immediate, others soft and distant, yet all contributing to the   │
║ │ symphony of learning. The Replay Buffer is the stage where past moments    │
║ │ perform again, teaching through repetition, refining through practice.     │
║ │                                                                               │
║ │ Like a master storyteller who knows which tales bear retelling, it         │
║ │ selects experiences not by age but by wisdom—those that surprised,         │
║ │ those that taught, those that transformed understanding. In this           │
║ │ selective recollection, the rare becomes common, the difficult becomes     │
║ │ familiar, the novel becomes natural.                                        │
║ │                                                                               │
║ │ Each replay is not mere repetition but resurrection—bringing the dead       │
║ │ past into the living present, where it can dance again with current        │
║ │ knowledge, creating new partnerships between what was and what is.          │
║ │                                                                               │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Prioritized experience replay (PER)
║ • Temporal difference error sampling
║ • Multi-scale temporal replay
║ • Episodic vs semantic replay modes
║ • Adaptive buffer sizing
║ • Colony-distributed storage
║ • Integration with consolidation systems
║ • Real-time priority updates
║
║ ΛTAG: ΛREPLAY, ΛEXPERIENCE, ΛLEARNING, ΛPRIORITY, ΛBUFFER
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import heapq
import math
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

import numpy as np

# Import LUKHAS components
try:
    from memory.hippocampal.hippocampal_buffer import EpisodicMemory
    from memory.neocortical.neocortical_network import SemanticMemory

    LUKHAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some LUKHAS modules not available: {e}")
    LUKHAS_AVAILABLE = False

    # Minimal stubs
    class EpisodicMemory:
        pass

    class SemanticMemory:
        pass


class ReplayMode(Enum):
    """Replay sampling modes"""

    UNIFORM = "uniform"  # Random uniform sampling
    PRIORITIZED = "prioritized"  # Priority-based sampling
    TEMPORAL = "temporal"  # Recent experiences favored
    CURIOSITY = "curiosity"  # High surprise/error experiences
    SEMANTIC = "semantic"  # Semantic similarity based


class ExperienceType(Enum):
    """Types of experiences in replay buffer"""

    EPISODIC = "episodic"  # Episodic memories
    SEMANTIC = "semantic"  # Semantic memories
    TRANSITION = "transition"  # State transitions
    REWARD = "reward"  # Reward experiences
    ERROR = "error"  # Prediction errors


@dataclass
class Experience:
    """Single experience in replay buffer"""

    experience_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)

    # Experience content
    state: Any = None
    action: Any = None
    reward: float = 0.0
    next_state: Any = None
    done: bool = False

    # Experience metadata
    experience_type: ExperienceType = ExperienceType.EPISODIC
    source_id: Optional[str] = None  # Original memory ID

    # Priority and sampling
    priority: float = 1.0
    td_error: float = 0.0  # Temporal difference error
    surprise: float = 0.0  # Prediction surprise
    importance: float = 0.5

    # Replay statistics
    replay_count: int = 0
    last_replay: Optional[float] = None
    success_rate: float = 0.0  # Learning success rate

    # Associations
    similar_experiences: set[str] = field(default_factory=set)

    def calculate_sampling_weight(self, alpha: float = 0.6) -> float:
        """Calculate sampling weight based on priority"""
        return self.priority**alpha

    def update_priority(self, td_error: float, surprise: float = 0.0):
        """Update experience priority based on learning metrics"""
        self.td_error = abs(td_error)
        self.surprise = surprise

        # Combine TD error and surprise
        self.priority = (
            self.td_error + 0.1 * self.surprise + 1e-6
        )  # Small constant for stability

        # Boost recent experiences
        age = time.time() - self.timestamp
        recency_factor = math.exp(-age / 3600)  # Decay over hours
        self.priority *= 1 + 0.5 * recency_factor


@dataclass
class ReplayBatch:
    """Batch of experiences for replay"""

    batch_id: str = field(default_factory=lambda: str(uuid4()))
    experiences: list[Experience] = field(default_factory=list)

    # Batch metadata
    sampling_mode: ReplayMode = ReplayMode.UNIFORM
    importance_weights: Optional[np.ndarray] = None

    # Batch statistics
    avg_priority: float = 0.0
    avg_age: float = 0.0
    diversity_score: float = 0.0

    def calculate_metrics(self):
        """Calculate batch statistics"""
        if not self.experiences:
            return

        priorities = [exp.priority for exp in self.experiences]
        ages = [time.time() - exp.timestamp for exp in self.experiences]

        self.avg_priority = np.mean(priorities)
        self.avg_age = np.mean(ages)

        # Diversity based on experience types
        types = [exp.experience_type for exp in self.experiences]
        unique_types = len(set(types))
        self.diversity_score = unique_types / len(ExperienceType)


class ReplayBuffer:
    """
    Experience replay buffer for memory consolidation and learning.
    Supports prioritized sampling and multi-modal experience storage.
    """

    def __init__(
        self,
        capacity: int = 100000,
        alpha: float = 0.6,  # Priority exponent
        beta: float = 0.4,  # Importance sampling exponent
        beta_increment: float = 0.001,
        enable_prioritized: bool = True,
        enable_clustering: bool = True,
        min_buffer_size: int = 1000,
        scaffold: Optional[Any] = None,
    ):
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.enable_prioritized = enable_prioritized
        self.enable_clustering = enable_clustering
        self.min_buffer_size = min_buffer_size
        self.scaffold = scaffold

        # Experience storage
        self.experiences: dict[str, Experience] = {}
        self.experience_queue: deque = deque(maxlen=capacity)

        # Priority management
        self.priority_tree = []  # Min-heap for priorities
        self.max_priority = 1.0

        # Clustering for semantic similarity
        self.experience_clusters: dict[str, set[str]] = {}
        self.cluster_centers: dict[str, np.ndarray] = {}

        # Sampling statistics
        self.total_samples = 0
        self.sampling_history: deque = deque(maxlen=10000)

        # Buffer metrics
        self.eviction_count = 0
        self.priority_updates = 0

        # Background tasks
        self._running = False
        self._maintenance_task = None
        self._clustering_task = None

        logger.info(
            "ReplayBuffer initialized",
            capacity=capacity,
            prioritized=enable_prioritized,
            clustering=enable_clustering,
        )

    async def start(self):
        """Start replay buffer"""
        self._running = True

        # Start background tasks
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())
        if self.enable_clustering:
            self._clustering_task = asyncio.create_task(self._clustering_loop())

        logger.info("ReplayBuffer started")

    async def stop(self):
        """Stop replay buffer"""
        self._running = False

        # Cancel tasks
        for task in [self._maintenance_task, self._clustering_task]:
            if task:
                task.cancel()

        logger.info(
            "ReplayBuffer stopped",
            total_experiences=len(self.experiences),
            total_samples=self.total_samples,
        )

    def add_experience(
        self,
        state: Any,
        action: Any = None,
        reward: float = 0.0,
        next_state: Any = None,
        done: bool = False,
        experience_type: ExperienceType = ExperienceType.EPISODIC,
        source_id: Optional[str] = None,
        priority: Optional[float] = None,
    ) -> str:
        """Add new experience to buffer"""

        # Create experience
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            experience_type=experience_type,
            source_id=source_id,
            priority=priority or self.max_priority,
        )

        # Add to buffer
        if len(self.experiences) >= self.capacity:
            self._evict_oldest()

        self.experiences[experience.experience_id] = experience
        self.experience_queue.append(experience.experience_id)

        # Update priority tracking
        if self.enable_prioritized:
            heapq.heappush(
                self.priority_tree, (-experience.priority, experience.experience_id)
            )
            self.max_priority = max(self.max_priority, experience.priority)

        logger.debug(
            "Experience added",
            experience_id=experience.experience_id[:8],
            type=experience_type.value,
            priority=experience.priority,
        )

        return experience.experience_id

    def add_episodic_memory(self, memory: EpisodicMemory) -> str:
        """Add episodic memory as experience"""

        return self.add_experience(
            state=memory.content,
            experience_type=ExperienceType.EPISODIC,
            source_id=memory.memory_id if hasattr(memory, "memory_id") else None,
            priority=getattr(memory, "encoding_strength", 1.0),
        )

    def add_semantic_memory(self, memory: SemanticMemory) -> str:
        """Add semantic memory as experience"""

        return self.add_experience(
            state=memory.concept if hasattr(memory, "concept") else memory,
            experience_type=ExperienceType.SEMANTIC,
            source_id=memory.memory_id if hasattr(memory, "memory_id") else None,
            priority=getattr(memory, "stability", 1.0),
        )

    def sample_batch(
        self, batch_size: int, mode: ReplayMode = ReplayMode.PRIORITIZED
    ) -> ReplayBatch:
        """Sample batch of experiences for replay"""

        if len(self.experiences) < self.min_buffer_size:
            return ReplayBatch()  # Empty batch

        # Sample based on mode
        if mode == ReplayMode.PRIORITIZED and self.enable_prioritized:
            sampled_experiences = self._sample_prioritized(batch_size)
        elif mode == ReplayMode.TEMPORAL:
            sampled_experiences = self._sample_temporal(batch_size)
        elif mode == ReplayMode.CURIOSITY:
            sampled_experiences = self._sample_curiosity(batch_size)
        elif mode == ReplayMode.SEMANTIC:
            sampled_experiences = self._sample_semantic(batch_size)
        else:
            sampled_experiences = self._sample_uniform(batch_size)

        # Create batch
        batch = ReplayBatch(experiences=sampled_experiences, sampling_mode=mode)

        # Calculate importance weights if prioritized
        if mode == ReplayMode.PRIORITIZED and self.enable_prioritized:
            batch.importance_weights = self._calculate_importance_weights(
                sampled_experiences
            )

        batch.calculate_metrics()

        # Update statistics
        self.total_samples += len(sampled_experiences)
        self.sampling_history.append(
            {
                "timestamp": time.time(),
                "mode": mode.value,
                "batch_size": len(sampled_experiences),
                "avg_priority": batch.avg_priority,
            }
        )

        # Update beta for importance sampling
        self.beta = min(1.0, self.beta + self.beta_increment)

        logger.debug(
            "Batch sampled",
            batch_id=batch.batch_id[:8],
            size=len(sampled_experiences),
            mode=mode.value,
        )

        return batch

    def update_priorities(self, experience_ids: list[str], td_errors: list[float]):
        """Update priorities based on TD errors"""

        for exp_id, td_error in zip(experience_ids, td_errors):
            if exp_id in self.experiences:
                experience = self.experiences[exp_id]
                experience.update_priority(td_error)
                self.max_priority = max(self.max_priority, experience.priority)
                self.priority_updates += 1

        # Rebuild priority tree periodically
        if self.priority_updates % 1000 == 0:
            self._rebuild_priority_tree()

    def get_experience(self, experience_id: str) -> Optional[Experience]:
        """Get specific experience by ID"""
        return self.experiences.get(experience_id)

    def find_similar_experiences(
        self,
        target_experience: Experience,
        similarity_threshold: float = 0.7,
        max_results: int = 10,
    ) -> list[Experience]:
        """Find experiences similar to target"""

        similar = []
        target_features = self._extract_features(target_experience.state)

        for exp in self.experiences.values():
            if exp.experience_id == target_experience.experience_id:
                continue

            exp_features = self._extract_features(exp.state)
            similarity = self._calculate_similarity(target_features, exp_features)

            if similarity > similarity_threshold:
                similar.append((similarity, exp))

        # Sort by similarity and return top results
        similar.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in similar[:max_results]]

    def _sample_prioritized(self, batch_size: int) -> list[Experience]:
        """Sample based on priorities"""

        if not self.priority_tree:
            return self._sample_uniform(batch_size)

        sampled = []

        # Sample proportional to priority
        total_priority = sum(exp.priority for exp in self.experiences.values())

        for _ in range(min(batch_size, len(self.experiences))):
            # Weighted random selection
            threshold = np.random.random() * total_priority
            current_sum = 0.0

            for exp in self.experiences.values():
                current_sum += exp.priority
                if current_sum >= threshold:
                    sampled.append(exp)
                    exp.replay_count += 1
                    exp.last_replay = time.time()
                    break

        return sampled

    def _sample_uniform(self, batch_size: int) -> list[Experience]:
        """Sample uniformly at random"""

        available = list(self.experiences.values())
        sample_size = min(batch_size, len(available))

        sampled = np.random.choice(available, size=sample_size, replace=False)

        for exp in sampled:
            exp.replay_count += 1
            exp.last_replay = time.time()

        return sampled.tolist()

    def _sample_temporal(self, batch_size: int) -> list[Experience]:
        """Sample recent experiences with higher probability"""

        # Calculate temporal weights
        current_time = time.time()
        experiences = list(self.experiences.values())

        weights = []
        for exp in experiences:
            age = current_time - exp.timestamp
            weight = math.exp(-age / 3600)  # Exponential decay over hours
            weights.append(weight)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return self._sample_uniform(batch_size)

        weights = [w / total_weight for w in weights]

        # Sample based on weights
        sample_size = min(batch_size, len(experiences))
        indices = np.random.choice(
            len(experiences), size=sample_size, replace=False, p=weights
        )

        sampled = [experiences[i] for i in indices]

        for exp in sampled:
            exp.replay_count += 1
            exp.last_replay = time.time()

        return sampled

    def _sample_curiosity(self, batch_size: int) -> list[Experience]:
        """Sample experiences with high surprise/error"""

        experiences = list(self.experiences.values())

        # Sort by surprise and TD error
        experiences.sort(key=lambda x: x.surprise + x.td_error, reverse=True)

        # Take top experiences
        sample_size = min(batch_size, len(experiences))
        sampled = experiences[:sample_size]

        for exp in sampled:
            exp.replay_count += 1
            exp.last_replay = time.time()

        return sampled

    def _sample_semantic(self, batch_size: int) -> list[Experience]:
        """Sample diverse experiences based on semantic clustering"""

        if not self.experience_clusters:
            return self._sample_uniform(batch_size)

        sampled = []

        # Sample from each cluster
        clusters = list(self.experience_clusters.keys())
        samples_per_cluster = max(1, batch_size // len(clusters))

        for cluster_id in clusters:
            cluster_exp_ids = self.experience_clusters[cluster_id]
            cluster_experiences = [
                self.experiences[exp_id]
                for exp_id in cluster_exp_ids
                if exp_id in self.experiences
            ]

            if cluster_experiences:
                cluster_sample_size = min(samples_per_cluster, len(cluster_experiences))
                cluster_sample = np.random.choice(
                    cluster_experiences, size=cluster_sample_size, replace=False
                )
                sampled.extend(cluster_sample)

        # Fill remaining slots if needed
        while len(sampled) < batch_size and len(sampled) < len(self.experiences):
            remaining = [exp for exp in self.experiences.values() if exp not in sampled]
            if remaining:
                sampled.append(np.random.choice(remaining))

        for exp in sampled:
            exp.replay_count += 1
            exp.last_replay = time.time()

        return sampled[:batch_size]

    def _calculate_importance_weights(
        self, experiences: list[Experience]
    ) -> np.ndarray:
        """Calculate importance sampling weights"""

        if not self.enable_prioritized:
            return np.ones(len(experiences))

        # Calculate weights: (1/N * 1/P(i))^beta
        N = len(self.experiences)
        weights = []

        for exp in experiences:
            prob = exp.calculate_sampling_weight(self.alpha) / sum(
                e.calculate_sampling_weight(self.alpha)
                for e in self.experiences.values()
            )
            weight = (1.0 / (N * prob)) ** self.beta
            weights.append(weight)

        # Normalize by max weight for stability
        weights = np.array(weights)
        return weights / np.max(weights)

    def _extract_features(self, state: Any) -> np.ndarray:
        """Extract feature vector from state"""

        # Simple feature extraction - in practice would use embeddings
        if isinstance(state, dict):
            features = []
            for key, value in sorted(state.items()):
                features.append(hash(key) % 1000)
                features.append(hash(str(value)) % 1000)
        else:
            features = [hash(str(state)) % 1000]

        # Pad to fixed size
        feature_size = 128
        if len(features) < feature_size:
            features.extend([0] * (feature_size - len(features)))
        else:
            features = features[:feature_size]

        return np.array(features, dtype=float)

    def _calculate_similarity(
        self, features1: np.ndarray, features2: np.ndarray
    ) -> float:
        """Calculate cosine similarity between feature vectors"""

        dot_product = np.dot(features1, features2)
        norm_product = np.linalg.norm(features1) * np.linalg.norm(features2)

        if norm_product == 0:
            return 0.0

        return dot_product / norm_product

    def _evict_oldest(self):
        """Evict oldest experience to make room"""

        if self.experience_queue:
            oldest_id = self.experience_queue.popleft()
            if oldest_id in self.experiences:
                del self.experiences[oldest_id]
                self.eviction_count += 1

    def _rebuild_priority_tree(self):
        """Rebuild priority tree for efficient sampling"""

        self.priority_tree = []
        for exp in self.experiences.values():
            heapq.heappush(self.priority_tree, (-exp.priority, exp.experience_id))

    async def _maintenance_loop(self):
        """Background maintenance tasks"""

        while self._running:
            # Update priority tree
            if len(self.priority_tree) != len(self.experiences):
                self._rebuild_priority_tree()

            # Decay old priorities
            current_time = time.time()
            for exp in self.experiences.values():
                age = current_time - exp.timestamp
                if age > 86400:  # Older than 1 day
                    exp.priority *= 0.99  # Slight decay

            await asyncio.sleep(60)  # Every minute

    async def _clustering_loop(self):
        """Background clustering for semantic similarity"""

        while self._running:
            if len(self.experiences) > 100:  # Minimum for clustering
                # Simple k-means clustering
                experiences = list(self.experiences.values())
                [self._extract_features(exp.state) for exp in experiences]

                # Create clusters (simplified)
                num_clusters = min(10, len(experiences) // 10)

                # Random cluster assignment for now
                for i, exp in enumerate(experiences):
                    cluster_id = f"cluster_{i % num_clusters}"
                    if cluster_id not in self.experience_clusters:
                        self.experience_clusters[cluster_id] = set()
                    self.experience_clusters[cluster_id].add(exp.experience_id)

            await asyncio.sleep(300)  # Every 5 minutes

    def get_metrics(self) -> dict[str, Any]:
        """Get replay buffer metrics"""

        metrics = {
            "total_experiences": len(self.experiences),
            "capacity_utilization": len(self.experiences) / self.capacity,
            "total_samples": self.total_samples,
            "eviction_count": self.eviction_count,
            "priority_updates": self.priority_updates,
            "max_priority": self.max_priority,
            "current_beta": self.beta,
        }

        # Experience type distribution
        type_counts = {}
        for exp in self.experiences.values():
            type_counts[exp.experience_type.value] = (
                type_counts.get(exp.experience_type.value, 0) + 1
            )
        metrics["experience_types"] = type_counts

        # Priority statistics
        if self.experiences:
            priorities = [exp.priority for exp in self.experiences.values()]
            metrics["avg_priority"] = np.mean(priorities)
            metrics["priority_std"] = np.std(priorities)

        # Replay statistics
        replay_counts = [exp.replay_count for exp in self.experiences.values()]
        if replay_counts:
            metrics["avg_replay_count"] = np.mean(replay_counts)
            metrics["max_replay_count"] = max(replay_counts)

        # Clustering metrics
        if self.experience_clusters:
            metrics["num_clusters"] = len(self.experience_clusters)
            cluster_sizes = [
                len(cluster) for cluster in self.experience_clusters.values()
            ]
            metrics["avg_cluster_size"] = np.mean(cluster_sizes)

        return metrics


# Example usage
async def demonstrate_replay_buffer():
    """Demonstrate replay buffer functionality"""

    buffer = ReplayBuffer(
        capacity=1000, enable_prioritized=True, enable_clustering=True
    )

    await buffer.start()

    print("=== Replay Buffer Demonstration ===\n")

    # Add some experiences
    print("--- Adding Experiences ---")

    for i in range(50):
        # Simulate different types of experiences
        if i % 5 == 0:
            exp_type = ExperienceType.SEMANTIC
            state = {"concept": f"concept_{i}", "category": "learning"}
            reward = np.random.uniform(0.5, 1.0)
        else:
            exp_type = ExperienceType.EPISODIC
            state = {"event": f"event_{i}", "context": f"context_{i % 10}"}
            reward = np.random.uniform(-0.5, 0.5)

        exp_id = buffer.add_experience(
            state=state,
            action=f"action_{i}",
            reward=reward,
            experience_type=exp_type,
            priority=np.random.uniform(0.1, 2.0),
        )

        if i < 5:
            print(f"Added: {exp_id[:8]}... ({exp_type.value})")

    # Sample different batches
    print("\n--- Sampling Batches ---")

    modes = [
        ReplayMode.UNIFORM,
        ReplayMode.PRIORITIZED,
        ReplayMode.TEMPORAL,
        ReplayMode.CURIOSITY,
    ]

    for mode in modes:
        batch = buffer.sample_batch(10, mode=mode)
        print(
            f"{mode.value}: {len(batch.experiences)} experiences, avg_priority={batch.avg_priority:.2f}"
        )

    # Update priorities
    print("\n--- Updating Priorities ---")

    batch = buffer.sample_batch(5)
    exp_ids = [exp.experience_id for exp in batch.experiences]
    td_errors = np.random.uniform(0.1, 2.0, len(exp_ids))

    buffer.update_priorities(exp_ids, td_errors)
    print(f"Updated priorities for {len(exp_ids)} experiences")

    # Show metrics
    print("\n--- Buffer Metrics ---")
    metrics = buffer.get_metrics()

    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")

    await buffer.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_replay_buffer())
