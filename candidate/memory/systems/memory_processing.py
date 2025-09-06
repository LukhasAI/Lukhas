"""
lukhas AI System - Function Library
Path: lukhas/core/memory/processing/memory_processing.py
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

"""
Memory Processing System for LUKHAS.
Memory Processing System for LUKHAS.

This module provides memory management, emotional tagging, and adaptive interaction storage.
It implements the MATADA node structure and integrates with the core memory helix.
"""

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class EmotionalState(Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CURIOUS = "curious"
    EMPATHETIC = "empathetic"


@dataclass
class MemoryNode:
    """MATADA memory node structure"""

    content: str
    context: dict[str, Any]
    timestamp: datetime.datetime
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    importance: float = 0.0
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryProcessor:
    """Main memory processing system implementing MATADA architecture"""

    def __init__(self, max_memories: int = 1000):
        self.memories = {}  # User ID -> list of MemoryNode
        self.max_memories = max_memories
        self.interaction_count = 0

    def store_interaction(
        self,
        user_id: str,
        content: str,
        context: dict[str, Any],
        emotional_state: EmotionalState = EmotionalState.NEUTRAL,
    ) -> None:
        """Store an interaction in memory using MATADA node structure"""
        if user_id not in self.memories:
            self.memories[user_id] = []

        # Create memory node
        memory = MemoryNode(
            content=content,
            context=context,
            timestamp=datetime.datetime.now(timezone.utc),
            emotional_state=emotional_state,
            importance=self._calculate_importance(context),
            metadata={"interaction_id": self.interaction_count},
        )

        self.interaction_count += 1

        # Add to user's memories
        self.memories[user_id].append(memory)

        # Trim if needed, removing least important memories first
        if len(self.memories[user_id]) > self.max_memories:
            self.memories[user_id] = sorted(self.memories[user_id], key=lambda x: x.importance, reverse=True)[
                : self.max_memories
            ]

        logger.info(f"Stored memory for user {user_id} with importance {memory.importance:.2f}")

    def get_relevant_memories(self, user_id: str, context: dict[str, Any], limit: int = 5) -> list[MemoryNode]:
        """Retrieve relevant memories based on context similarity"""
        if user_id not in self.memories:
            return []

        def calculate_relevance(memory: MemoryNode) -> float:
            # Context matching score (0-1)
            context_score = sum(1 for k, v in context.items() if k in memory.context and memory.context[k] == v)
            context_score = context_score / max(len(context), len(memory.context))

            # Time decay factor (1.0 -> 0.0)
            time_diff = (datetime.datetime.now(timezone.utc) - memory.timestamp).total_seconds()
            time_factor = 1.0 / (1.0 + time_diff / (24 * 3600))  # 24hr half-life

            return context_score * time_factor * memory.importance

        # Sort memories by relevance
        memories = sorted(self.memories[user_id], key=calculate_relevance, reverse=True)

        return memories[:limit]

    def _calculate_importance(self, context: dict[str, Any]) -> float:
        """Calculate importance score for memory retention"""
        importance = 0.0

        # Base importance from context
        if "priority" in context:
            importance += float(context["priority"])

        # Emotional impact
        if "emotional_intensity" in context:
            importance += float(context["emotional_intensity"]) * 0.5

        # Cultural significance
        if "cultural_relevance" in context:
            importance += float(context["cultural_relevance"]) * 0.3

        # Normalize to 0-1 range
        importance = max(0.0, min(1.0, importance))

        return importance

    def update_memory_references(self, user_id: str, memory_id: str, referenced_ids: list[str]) -> None:
        """Update memory node references to build connections"""
        if user_id not in self.memories:
            return

        for memory in self.memories[user_id]:
            if memory.metadata.get("interaction_id") == memory_id:
                memory.references.extend(referenced_ids)
                memory.references = list(set(memory.references))  # Remove duplicates
                break

    def get_emotional_summary(
        self, user_id: str, timeframe: Optional[datetime.timedelta] = None
    ) -> dict[EmotionalState, int]:
        """Get summary of emotional states from recent interactions"""
        if user_id not in self.memories:
            return dict.fromkeys(EmotionalState, 0)

        if timeframe:
            cutoff = datetime.datetime.now(timezone.utc) - timeframe
            relevant_memories = [m for m in self.memories[user_id] if m.timestamp >= cutoff]
        else:
            relevant_memories = self.memories[user_id]

        summary = dict.fromkeys(EmotionalState, 0)
        for memory in relevant_memories:
            summary[memory.emotional_state] += 1

        return summary

    def export_memories(self, user_id: str, format: str = "json") -> dict[str, Any]:
        """Export user memories in specified format"""
        if user_id not in self.memories:
            return {"memories": []}

        memory_data = []
        for memory in self.memories[user_id]:
            memory_dict = {
                "content": memory.content,
                "context": memory.context,
                "timestamp": memory.timestamp.isoformat(),
                "emotional_state": memory.emotional_state.value,
                "importance": memory.importance,
                "references": memory.references,
                "metadata": memory.metadata,
            }
            memory_data.append(memory_dict)

        return {
            "user_id": user_id,
            "export_timestamp": datetime.datetime.now(timezone.utc).isoformat(),
            "memory_count": len(memory_data),
            "memories": memory_data,
        }

    def import_memories(self, data: dict[str, Any]) -> int:
        """Import memories from exported data"""
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("Missing user_id in import data")

        imported_count = 0
        for memory_dict in data.get("memories", []):
            try:
                memory = MemoryNode(
                    content=memory_dict["content"],
                    context=memory_dict["context"],
                    timestamp=datetime.datetime.fromisoformat(memory_dict["timestamp"]),
                    emotional_state=EmotionalState(memory_dict["emotional_state"]),
                    importance=memory_dict["importance"],
                    references=memory_dict["references"],
                    metadata=memory_dict["metadata"],
                )

                if user_id not in self.memories:
                    self.memories[user_id] = []
                self.memories[user_id].append(memory)
                imported_count += 1

            except (KeyError, ValueError) as e:
                logger.error(f"Error importing memory: {e!s}")
                continue

        return imported_count

    def cluster_memories(
        self,
        user_id: str,
        cluster_key: str = "emotional_state",
        min_cluster_size: int = 2,
    ) -> dict[Any, list[MemoryNode]]:
        """Cluster memories based on specified attribute"""
        if user_id not in self.memories:
            return {}

        clusters = {}
        for memory in self.memories[user_id]:
            if cluster_key == "emotional_state":
                key = memory.emotional_state
            elif cluster_key in memory.context:
                key = memory.context[cluster_key]
            else:
                continue

            if key not in clusters:
                clusters[key] = []
            clusters[key].append(memory)

        # Filter out small clusters
        return {k: v for k, v in clusters.items() if len(v) >= min_cluster_size}

    def get_memory_timeline(
        self,
        user_id: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> list[MemoryNode]:
        """Get chronological timeline of memories within timeframe"""
        if user_id not in self.memories:
            return []

        memories = self.memories[user_id]

        if start_time:
            memories = [m for m in memories if m.timestamp >= start_time]
        if end_time:
            memories = [m for m in memories if m.timestamp <= end_time]

        return sorted(memories, key=lambda x: x.timestamp)


# Last Updated: 2025-06-05 09:37:28
