#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```MARKDOWN
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: glyph_memory_bridge.py
║ Path: memory/systems/glyph_memory_bridge.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │                           LUKHAS AI DOCUMENTATION HEADER                       │
║ ├───────────────────────────────────────────────────────────────────────────────┤
║ │                           MODULE: GLYPH-MEMORY BRIDGE                          │
║ │                  A bridge of cognition, where memories intertwine.             │
║ ├───────────────────────────────────────────────────────────────────────────────┤
║ │                                   ESSENCE                                        │
║ │                                                                               │
║ │ In the vast expanse of the cognitive cosmos, where the ethereal threads of     │
║ │ memory and meaning coalesce, the Glyph-Memory Bridge emerges as a beacon of    │
║ │ enlightenment. It stands resolute, a bridge spanning the chasm between the    │
║ │ ephemeral and the eternal, where the whispers of forgotten knowledge are       │
║ │ woven into the tapestry of conscious thought. Each glyph, a symbol of         │
║ │ understanding, carries the weight of history and the breath of possibility,    │
║ │ inviting the seeker to traverse the labyrinthine corridors of their own mind.  │
║ │                                                                               │
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛSTANDARD, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

from candidate.core.common import get_logger

# Internal imports
from symbolic.glyphs.glyph import EmotionVector, Glyph, GlyphFactory

from .memory_fold import MemoryFoldSystem

# Configure logger
logger = get_logger(__name__)


@dataclass
class GlyphMemoryIndex:
    """Index structure linking glyphs to memory fold keys."""

    glyph_to_memory: dict[str, set[str]]  # glyph_id -> set of memory_fold_keys
    memory_to_glyph: dict[str, set[str]]  # memory_fold_key -> set of glyph_ids
    binding_strength: dict[tuple[str, str], float]  # (glyph_id, memory_key) -> strength
    last_updated: datetime

    def __post_init__(self):
        if not hasattr(self, "last_updated"):
            self.last_updated = datetime.now()


class GlyphMemoryBridge:
    """
    Core bridge between GLYPH subsystem and Memory Fold System.

    Provides glyph-based indexing, retrieval, and drift anchoring for memory operations.
    """

    def __init__(self, memory_system: MemoryFoldSystem):
        """Initialize the glyph-memory bridge."""
        self.memory_system = memory_system
        self.glyph_index = GlyphMemoryIndex(
            glyph_to_memory=defaultdict(set),
            memory_to_glyph=defaultdict(set),
            binding_strength={},
            last_updated=datetime.now(),
        )
        self.active_glyphs: dict[str, Glyph] = {}
        self.drift_anchors: dict[str, float] = {}  # memory_key -> drift_anchor_score

        logger.info("Glyph-Memory Bridge initialized")

    def create_glyph_indexed_memory(
        self,
        content: str,
        emotion: str,
        context: str,
        glyphs: Optional[list[Union[str, Glyph]]] = None,
        user_id: Optional[str] = None,
        drift_anchor_strength: float = 0.5,
    ) -> dict[str, Any]:
        """
        Create a memory fold with glyph indexing integration.

        Args:
            content: Memory content
            emotion: Primary emotion
            context: Memory context
            glyphs: List of glyph symbols or Glyph objects to associate
            user_id: User identifier
            drift_anchor_strength: Strength of drift anchoring (0.0-1.0)

        Returns:
            Memory fold dictionary with glyph associations
        """
        # Create the base memory fold
        memory_fold = self.memory_system.create_memory_fold(
            emotion=emotion, context=context, user_id=user_id
        )

        memory_key = memory_fold["fold_hash"]

        # Process glyphs and create associations
        if glyphs:
            glyph_objects = []
            for glyph_item in glyphs:
                if isinstance(glyph_item, str):
                    # Create memory glyph from symbol
                    emotion_vector = self._emotion_to_vector(emotion)
                    glyph = GlyphFactory.create_memory_glyph(memory_key, emotion_vector)
                    glyph.symbol = glyph_item
                    glyph.add_semantic_tag(f"emotion_{emotion}")
                    glyph.add_semantic_tag("memory_indexed")
                elif isinstance(glyph_item, Glyph):
                    glyph = glyph_item
                    glyph.add_memory_key(memory_key)
                else:
                    continue

                # Set drift anchor strength
                glyph.update_drift_anchor(drift_anchor_strength)

                glyph_objects.append(glyph)
                self._link_glyph_to_memory(glyph, memory_key)

        # Set drift anchor for memory
        self.drift_anchors[memory_key] = drift_anchor_strength

        # Update memory fold with glyph metadata
        memory_fold["glyph_associations"] = (
            [g.id for g in glyph_objects] if glyph_objects else []
        )
        memory_fold["drift_anchor_score"] = drift_anchor_strength
        memory_fold["symbolic_tags"] = (
            list(set().union(*[g.semantic_tags for g in glyph_objects]))
            if glyph_objects
            else []
        )

        logger.info(
            f"Created glyph-indexed memory: {memory_key[:10]}... with {len(glyph_objects)} glyphs"
        )
        return memory_fold

    def recall_by_glyph(
        self,
        glyph_filters: dict[str, Any],
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Recall memories using glyph-based filtering.

        Args:
            glyph_filters: Dictionary of glyph filter criteria
                - 'symbols': List of glyph symbols to match
                - 'emotion_similarity': EmotionVector for similarity search
                - 'semantic_tags': Set of required semantic tags
                - 'glyph_type': GlyphType to filter by
                - 'min_drift_anchor': Minimum drift anchor score
            user_id: User identifier for filtering
            limit: Maximum memories to return

        Returns:
            List of memory folds matching glyph criteria
        """
        matching_memories = []

        # Find glyphs matching the filters
        matching_glyph_ids = self._find_glyphs_by_filters(glyph_filters)

        # Get associated memory keys
        memory_keys = set()
        for glyph_id in matching_glyph_ids:
            memory_keys.update(self.glyph_index.glyph_to_memory.get(glyph_id, set()))

        # Retrieve memories and apply additional filtering
        for memory_key in memory_keys:
            # Check drift anchor requirements
            min_drift_anchor = glyph_filters.get("min_drift_anchor", 0.0)
            if self.drift_anchors.get(memory_key, 0.0) < min_drift_anchor:
                continue

            # Get memory fold from storage
            memory_folds = self.memory_system.recall_memory_folds(
                user_id=user_id, limit=1000  # Get all, we'll filter
            )

            # Find matching memory fold
            matching_fold = None
            for fold in memory_folds:
                if fold.get("fold_hash") == memory_key:
                    matching_fold = fold
                    break

            if matching_fold:
                # Enhance with glyph metadata
                glyph_ids = self.glyph_index.memory_to_glyph.get(memory_key, set())
                matching_fold["associated_glyphs"] = list(glyph_ids)
                matching_fold["drift_anchor_score"] = self.drift_anchors.get(
                    memory_key, 0.0
                )
                matching_memories.append(matching_fold)

            if len(matching_memories) >= limit:
                break

        logger.info(f"Recalled {len(matching_memories)} memories using glyph filters")
        return matching_memories

    def create_drift_anchor(
        self,
        memory_key: str,
        anchor_strength: float = 1.0,
        anchor_type: str = "stability",
    ) -> Glyph:
        """
        Create a drift detection anchor for a memory.

        Args:
            memory_key: Memory fold key to anchor
            anchor_strength: Strength of the anchor (0.0-1.0)
            anchor_type: Type of anchor ("stability", "reference", "baseline")

        Returns:
            Drift anchor glyph
        """
        # Create drift anchor glyph
        anchor_glyph = GlyphFactory.create_drift_anchor(anchor_strength)
        anchor_glyph.add_memory_key(memory_key)
        anchor_glyph.add_semantic_tag(f"anchor_{anchor_type}")
        anchor_glyph.add_semantic_tag("drift_detection")

        # Link to memory
        self._link_glyph_to_memory(anchor_glyph, memory_key)

        # Update drift anchor tracking
        self.drift_anchors[memory_key] = max(
            self.drift_anchors.get(memory_key, 0.0), anchor_strength
        )

        logger.info(
            f"Created drift anchor for memory {memory_key[:10]}... strength: {anchor_strength:.3f}"
        )
        return anchor_glyph

    def assess_memory_drift(self, memory_key: str) -> dict[str, float]:
        """
        Assess drift for a specific memory using its glyph anchors.

        Args:
            memory_key: Memory fold key to assess

        Returns:
            Dictionary containing drift assessment metrics
        """
        assessment = {
            "drift_score": 0.0,
            "anchor_strength": 0.0,
            "stability_index": 1.0,
            "glyph_count": 0,
            "average_glyph_stability": 1.0,
        }

        # Get associated glyphs
        glyph_ids = self.glyph_index.memory_to_glyph.get(memory_key, set())
        if not glyph_ids:
            assessment["drift_score"] = 0.5  # No anchors = moderate drift risk
            return assessment

        assessment["glyph_count"] = len(glyph_ids)

        # Assess glyph-based drift indicators
        glyph_stabilities = []
        anchor_strengths = []

        for glyph_id in glyph_ids:
            glyph = self.active_glyphs.get(glyph_id)
            if glyph:
                glyph_stabilities.append(glyph.stability_index)
                anchor_strengths.append(glyph.drift_anchor_score)

        if glyph_stabilities:
            assessment["average_glyph_stability"] = sum(glyph_stabilities) / len(
                glyph_stabilities
            )
            assessment["anchor_strength"] = (
                max(anchor_strengths) if anchor_strengths else 0.0
            )

            # Calculate drift score (inverse of stability)
            assessment["drift_score"] = 1.0 - assessment["average_glyph_stability"]
            assessment["stability_index"] = assessment["average_glyph_stability"]

        logger.debug(f"Memory drift assessment for {memory_key[:10]}...: {assessment}")
        return assessment

    def get_memory_by_causal_link(
        self, causal_origin_id: str, max_depth: int = 5
    ) -> list[dict[str, Any]]:
        """
        Retrieve memories connected through causal glyph linkages.

        Args:
            causal_origin_id: Starting point for causal chain
            max_depth: Maximum depth to traverse

        Returns:
            List of causally linked memories
        """
        visited = set()
        causal_memories = []

        def traverse_causal_chain(glyph_id: str, depth: int):
            if depth >= max_depth or glyph_id in visited:
                return

            visited.add(glyph_id)
            glyph = self.active_glyphs.get(glyph_id)

            if glyph and glyph.memory_keys:
                # Get memories associated with this glyph
                for memory_key in glyph.memory_keys:
                    memory_folds = self.memory_system.recall_memory_folds(limit=1000)
                    for fold in memory_folds:
                        if fold.get("fold_hash") == memory_key:
                            fold["causal_depth"] = depth
                            fold["causal_glyph_id"] = glyph_id
                            causal_memories.append(fold)
                            break

                # Follow causal links
                for child_id in glyph.causal_link.child_glyph_ids:
                    traverse_causal_chain(child_id, depth + 1)

        # Start traversal
        traverse_causal_chain(causal_origin_id, 0)

        logger.info(
            f"Found {len(causal_memories)} causally linked memories from origin {causal_origin_id}"
        )
        return causal_memories

    def create_retrieval_filter(
        self, filter_name: str, glyph_criteria: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a reusable retrieval filter based on glyph criteria.

        Args:
            filter_name: Name for the filter
            glyph_criteria: Glyph-based filter criteria

        Returns:
            Filter configuration dictionary
        """
        filter_config = {
            "name": filter_name,
            "created_at": datetime.now().isoformat(),
            "criteria": glyph_criteria,
            "usage_count": 0,
            "last_used": None,
        }

        # Validate criteria
        valid_keys = {
            "symbols",
            "emotion_similarity",
            "semantic_tags",
            "glyph_type",
            "min_drift_anchor",
        }
        if not set(glyph_criteria.keys()).issubset(valid_keys):
            raise ValueError(f"Invalid filter criteria. Valid keys: {valid_keys}")

        logger.info(f"Created retrieval filter: {filter_name}")
        return filter_config

    def _emotion_to_vector(self, emotion: str) -> EmotionVector:
        """Convert emotion string to EmotionVector."""
        # Basic emotion mapping - can be enhanced with more sophisticated mapping
        emotion_mapping = {
            "joy": EmotionVector(joy=0.8, valence=0.7, arousal=0.6),
            "sadness": EmotionVector(sadness=0.8, valence=-0.7, arousal=0.3),
            "anger": EmotionVector(anger=0.8, valence=-0.6, arousal=0.8),
            "fear": EmotionVector(fear=0.8, valence=-0.5, arousal=0.7),
            "surprise": EmotionVector(surprise=0.8, valence=0.2, arousal=0.8),
            "trust": EmotionVector(trust=0.8, valence=0.6, arousal=0.4),
            "disgust": EmotionVector(disgust=0.8, valence=-0.8, arousal=0.5),
            "anticipation": EmotionVector(anticipation=0.8, valence=0.5, arousal=0.6),
        }

        return emotion_mapping.get(emotion.lower(), EmotionVector())

    def _link_glyph_to_memory(
        self, glyph: Glyph, memory_key: str, strength: float = 1.0
    ):
        """Create bidirectional link between glyph and memory."""
        glyph_id = glyph.id

        # Update indices
        self.glyph_index.glyph_to_memory[glyph_id].add(memory_key)
        self.glyph_index.memory_to_glyph[memory_key].add(glyph_id)
        self.glyph_index.binding_strength[(glyph_id, memory_key)] = strength
        self.glyph_index.last_updated = datetime.now()

        # Store active glyph
        self.active_glyphs[glyph_id] = glyph

        logger.debug(
            f"Linked glyph {glyph_id} to memory {memory_key[:10]}... strength: {strength}"
        )

    def _find_glyphs_by_filters(self, filters: dict[str, Any]) -> set[str]:
        """Find glyph IDs matching the specified filters."""
        matching_glyphs = set()

        for glyph_id, glyph in self.active_glyphs.items():
            # Check symbol filter
            if "symbols" in filters and glyph.symbol not in filters["symbols"]:
                continue

            # Check glyph type filter
            if "glyph_type" in filters and glyph.glyph_type != filters["glyph_type"]:
                continue

            # Check semantic tags filter
            if "semantic_tags" in filters:
                required_tags = set(filters["semantic_tags"])
                if not required_tags.issubset(glyph.semantic_tags):
                    continue

            # Check emotion similarity filter
            if "emotion_similarity" in filters:
                target_emotion = filters["emotion_similarity"]
                if isinstance(target_emotion, EmotionVector):
                    similarity_threshold = filters.get("emotion_threshold", 0.5)
                    distance = glyph.emotion_vector.distance_to(target_emotion)
                    if distance > similarity_threshold:
                        continue

            # Check minimum drift anchor filter
            if "min_drift_anchor" in filters:
                if glyph.drift_anchor_score < filters["min_drift_anchor"]:
                    continue

            matching_glyphs.add(glyph_id)

        return matching_glyphs

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about glyph-memory integration."""
        stats = {
            "total_glyphs": len(self.active_glyphs),
            "total_memory_associations": len(self.glyph_index.memory_to_glyph),
            "average_glyphs_per_memory": 0.0,
            "drift_anchored_memories": len(self.drift_anchors),
            "glyph_types": defaultdict(int),
            "last_index_update": self.glyph_index.last_updated.isoformat(),
            "binding_strength_distribution": {"min": 0.0, "max": 1.0, "avg": 0.0},
        }

        # Calculate averages
        if self.glyph_index.memory_to_glyph:
            total_associations = sum(
                len(glyphs) for glyphs in self.glyph_index.memory_to_glyph.values()
            )
            stats["average_glyphs_per_memory"] = total_associations / len(
                self.glyph_index.memory_to_glyph
            )

        # Glyph type distribution
        for glyph in self.active_glyphs.values():
            stats["glyph_types"][glyph.glyph_type.value] += 1

        # Binding strength distribution
        if self.glyph_index.binding_strength:
            strengths = list(self.glyph_index.binding_strength.values())
            stats["binding_strength_distribution"] = {
                "min": min(strengths),
                "max": max(strengths),
                "avg": sum(strengths) / len(strengths),
            }

        return dict(stats)


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🔗 LUKHAS AI - GLYPH-MEMORY BRIDGE
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Glyph-Based Memory Indexing: Symbolic keys for memory organization
║ • Advanced Retrieval Filtering: Multi-criteria glyph-based memory queries
║ • Drift Detection Anchoring: Stability tracking through glyph associations
║ • Causal Chain Traversal: Memory lineage following through glyph links
║ • Emotional Context Preservation: EmotionVector integration with memory
║ • Bidirectional Association Management: Glyph-memory relationship tracking
║ • Statistics and Analytics: Comprehensive integration metrics
║ • Filter Configuration: Reusable query pattern management
╠═══════════════════════════════════════════════════════════════════════════════
║ INTEGRATION POINTS
╠═══════════════════════════════════════════════════════════════════════════════
║ • Memory Fold System: Direct integration with core memory storage
║ • GLYPH Subsystem: Full utilization of glyph schema and factory patterns
║ • Drift Detection: Anchor-based stability monitoring
║ • Causal Tracking: Lineage management through glyph relationships
║ • Emotion Engine: EmotionVector compatibility and processing
║ • Semantic Tagging: Rich metadata association and filtering
╚═══════════════════════════════════════════════════════════════════════════════
"""
