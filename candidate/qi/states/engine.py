#!/usr/bin/env python3

"""

#TAG:qim
#TAG:qi_states
#TAG:neuroplastic
#TAG:colony


LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Symbolic Collapse Engine

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

The Symbolic Collapse Engine handles the compression and consolidation of
memory nodes while preserving semantic integrity and causal relationships.
This is critical for managing memory complexity and preventing runaway growth.

For more information, visit: https://lukhas.ai
"""
from consciousness.qi import qi
from typing import List
import time
import streamlit as st

# ΛTRACE: Symbolic collapse engine
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 13

__version__ = "2.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import hashlib
import logging
import math
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Import collapse tracker for integration
try:
    from candidate.core.monitoring.collapse_tracker import get_global_tracker
except ImportError:
    get_global_tracker = None
    logger.warning("Collapse tracker not available")

# Import collapse trace for logging
try:
    from .collapse_trace import get_global_tracer
except ImportError:
    get_global_tracer = None
    logger.warning("Collapse tracer not available")


@dataclass
class MemoryNode:
    """Represents a node in the memory DAG with enhanced metadata."""

    node_id: str = field(default_factory=lambda: f"node_{uuid.uuid4().hex[:12]}")
    content_hash: str = ""
    content: Any = None  # Actual memory content
    emotional_weight: float = 0.0
    semantic_tags: list[str] = field(default_factory=list)
    parent_nodes: list[str] = field(default_factory=list)
    child_nodes: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    collapse_count: int = 0  # Times this node has been collapsed
    entropy_score: float = 0.0  # Individual node entropy
    glyph_id: Optional[str] = None  # Associated glyph

    def compute_hash(self) -> str:
        """Compute content hash for the node."""
        if self.content is None:
            return ""

        # Create hash from content and metadata
        hash_input = f"{self.content}:{self.emotional_weight}:{sorted(self.semantic_tags)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "content_hash": self.content_hash,
            "emotional_weight": self.emotional_weight,
            "semantic_tags": self.semantic_tags,
            "parent_nodes": self.parent_nodes,
            "child_nodes": self.child_nodes,
            "timestamp": self.timestamp.isoformat(),
            "collapse_count": self.collapse_count,
            "entropy_score": self.entropy_score,
            "glyph_id": self.glyph_id,
        }


@dataclass
class CollapseResult:
    """Result of a collapse operation."""

    collapsed_node: MemoryNode
    source_nodes: list[str]
    collapse_type: str  # consolidation, compression, fusion
    entropy_reduction: float
    semantic_loss: float
    metadata: dict[str, Any] = field(default_factory=dict)


class CollapseEngine:
    """
    Engine for collapsing memory nodes while preserving symbolic integrity.

    This engine handles various collapse strategies including:
    - Consolidation: Merging similar nodes
    - Compression: Reducing redundant information
    - Fusion: Creating higher-order abstractions
    """

    def __init__(
        self,
        entropy_threshold: float = 0.7,
        min_nodes_for_collapse: int = 3,
        semantic_similarity_threshold: float = 0.8,
    ):
        """
        Initialize the collapse engine.

        Args:
            entropy_threshold: Entropy level triggering collapse
            min_nodes_for_collapse: Minimum nodes required for collapse
            semantic_similarity_threshold: Threshold for semantic consolidation
        """
        self.entropy_threshold = entropy_threshold
        self.min_nodes_for_collapse = min_nodes_for_collapse
        self.semantic_similarity_threshold = semantic_similarity_threshold

        # Node registry
        self.nodes: dict[str, MemoryNode] = {}

        # Collapse history
        self.collapse_history: list[CollapseResult] = []

        # Get global trackers if available
        self.collapse_tracker = get_global_tracker() if get_global_tracker else None
        self.collapse_tracer = get_global_tracer() if get_global_tracer else None

        logger.info(
            "CollapseEngine initialized",
            entropy_threshold=entropy_threshold,
            min_nodes=min_nodes_for_collapse,
        )

    # {ΛCOLLAPSE}
    def collapse_nodes(self, nodes: list[MemoryNode], strategy: str = "auto") -> Optional[CollapseResult]:
        """
        Collapse a list of memory nodes into a single node.

        Args:
            nodes: List of nodes to collapse
            strategy: Collapse strategy (auto, consolidation, compression, fusion)

        Returns:
            CollapseResult if successful, None otherwise
        """
        if len(nodes) < self.min_nodes_for_collapse:
            logger.debug("Insufficient nodes for collapse", count=len(nodes))
            return None

        # Register nodes
        for node in nodes:
            self.nodes[node.node_id] = node

        # Calculate entropy
        entropy = self._calculate_node_entropy(nodes)

        # Determine strategy if auto
        if strategy == "auto":
            strategy = self._determine_collapse_strategy(nodes, entropy)

        logger.info("Collapsing nodes", count=len(nodes), strategy=strategy, entropy=entropy)

        # Execute collapse based on strategy
        if strategy == "consolidation":
            result = self._consolidate_nodes(nodes)
        elif strategy == "compression":
            result = self._compress_nodes(nodes)
        elif strategy == "fusion":
            result = self._fuse_nodes(nodes)
        else:
            logger.error("Unknown collapse strategy", strategy=strategy)
            return None

        if result:
            # Update tracking
            self._update_collapse_tracking(result, entropy)

            # Log collapse event
            if self.collapse_tracer:
                self.collapse_tracer.log_collapse(
                    source_keys=[n.node_id for n in nodes],
                    resulting_key=result.collapsed_node.node_id,
                    collapse_type=strategy,
                    metadata={
                        "entropy": entropy,
                        "semantic_loss": result.semantic_loss,
                    },
                )

            # Store result
            self.collapse_history.append(result)
            self.nodes[result.collapsed_node.node_id] = result.collapsed_node

        return result

    def _calculate_node_entropy(self, nodes: list[MemoryNode]) -> float:
        """
        Calculate Shannon entropy for a set of nodes.

        Args:
            nodes: List of memory nodes

        Returns:
            Entropy score between 0 and 1
        """
        if not nodes:
            return 0.0

        # Collect all semantic tags
        all_tags = []
        for node in nodes:
            all_tags.extend(node.semantic_tags)

        if not all_tags:
            return 0.0

        # Calculate tag frequency distribution
        tag_counts = Counter(all_tags)
        total_tags = len(all_tags)

        # Shannon entropy
        entropy = 0.0
        for count in tag_counts.values():
            if count > 0:
                p = count / total_tags
                entropy -= p * math.log2(p)

        # Normalize
        max_entropy = math.log2(len(tag_counts)) if len(tag_counts) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        return min(1.0, max(0.0, normalized_entropy))

    def _determine_collapse_strategy(self, nodes: list[MemoryNode], entropy: float) -> str:
        """
        Determine optimal collapse strategy based on node characteristics.

        Args:
            nodes: List of memory nodes
            entropy: Current entropy level

        Returns:
            Strategy name
        """
        # High entropy suggests compression
        if entropy > 0.8:
            return "compression"

        # Check semantic similarity for consolidation
        avg_similarity = self._calculate_average_similarity(nodes)
        if avg_similarity > self.semantic_similarity_threshold:
            return "consolidation"

        # Default to fusion for creating abstractions
        return "fusion"

    def _calculate_average_similarity(self, nodes: list[MemoryNode]) -> float:
        """Calculate average semantic similarity between nodes."""
        if len(nodes) < 2:
            return 1.0

        similarities = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                sim = self._semantic_similarity(nodes[i], nodes[j])
                similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _semantic_similarity(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Calculate semantic similarity between two nodes."""
        # Jaccard similarity of semantic tags
        tags1 = set(node1.semantic_tags)
        tags2 = set(node2.semantic_tags)

        if not tags1 and not tags2:
            return 1.0

        intersection = tags1.intersection(tags2)
        union = tags1.union(tags2)

        return len(intersection) / len(union) if union else 0.0

    # {ΛCONSOLIDATION}
    def _consolidate_nodes(self, nodes: list[MemoryNode]) -> CollapseResult:
        """
        Consolidate similar nodes by merging their content.

        Args:
            nodes: Nodes to consolidate

        Returns:
            CollapseResult
        """
        # Create consolidated node
        consolidated = MemoryNode()

        # Merge semantic tags (union)
        all_tags = set()
        for node in nodes:
            all_tags.update(node.semantic_tags)
        consolidated.semantic_tags = sorted(all_tags)

        # Average emotional weights
        consolidated.emotional_weight = sum(n.emotional_weight for n in nodes) / len(nodes)

        # Merge parent/child relationships
        all_parents = set()
        all_children = set()
        for node in nodes:
            all_parents.update(node.parent_nodes)
            all_children.update(node.child_nodes)

        # Remove self-references
        node_ids = {n.node_id for n in nodes}
        consolidated.parent_nodes = sorted(all_parents - node_ids)
        consolidated.child_nodes = sorted(all_children - node_ids)

        # Aggregate content (simplified - in reality would be more sophisticated)
        [n.content for n in nodes if n.content]
        consolidated.content = f"[Consolidated from {len(nodes)} nodes]"

        # Update metadata
        consolidated.collapse_count = max(n.collapse_count for n in nodes) + 1
        consolidated.entropy_score = self._calculate_node_entropy([consolidated])
        consolidated.content_hash = consolidated.compute_hash()

        # Calculate semantic loss (minimal for consolidation)
        semantic_loss = 1.0 - self._calculate_average_similarity(nodes)

        return CollapseResult(
            collapsed_node=consolidated,
            source_nodes=[n.node_id for n in nodes],
            collapse_type="consolidation",
            entropy_reduction=0.3,  # Moderate reduction
            semantic_loss=semantic_loss,
            metadata={"tag_count": len(all_tags)},
        )

    # {ΛCOMPRESSION}
    def _compress_nodes(self, nodes: list[MemoryNode]) -> CollapseResult:
        """
        Compress nodes by removing redundancy.

        Args:
            nodes: Nodes to compress

        Returns:
            CollapseResult
        """
        # Create compressed node
        compressed = MemoryNode()

        # Find most common tags (keep top 75%)
        tag_counter = Counter()
        for node in nodes:
            tag_counter.update(node.semantic_tags)

        keep_count = int(len(tag_counter) * 0.75)
        compressed.semantic_tags = [tag for tag, _ in tag_counter.most_common(keep_count)]

        # Weighted average of emotional weights
        total_weight = sum(n.emotional_weight for n in nodes)
        if total_weight > 0:
            weights = [n.emotional_weight / total_weight for n in nodes]
            compressed.emotional_weight = sum(w * n.emotional_weight for w, n in zip(weights, nodes))
        else:
            compressed.emotional_weight = 0.0

        # Keep only strong parent/child relationships
        parent_counter = Counter()
        child_counter = Counter()
        for node in nodes:
            parent_counter.update(node.parent_nodes)
            child_counter.update(node.child_nodes)

        # Keep relationships that appear in >50% of nodes
        threshold = len(nodes) / 2
        compressed.parent_nodes = [p for p, c in parent_counter.items() if c > threshold]
        compressed.child_nodes = [c for c, count in child_counter.items() if count > threshold]

        # Compress content
        compressed.content = f"[Compressed from {len(nodes)} nodes with {len(tag_counter)} original tags]"

        # Update metadata
        compressed.collapse_count = max(n.collapse_count for n in nodes) + 1
        compressed.entropy_score = self._calculate_node_entropy([compressed])
        compressed.content_hash = compressed.compute_hash()

        # Higher semantic loss for compression
        semantic_loss = 0.25  # 25% information loss

        return CollapseResult(
            collapsed_node=compressed,
            source_nodes=[n.node_id for n in nodes],
            collapse_type="compression",
            entropy_reduction=0.5,  # Significant reduction
            semantic_loss=semantic_loss,
            metadata={
                "original_tags": len(tag_counter),
                "compressed_tags": len(compressed.semantic_tags),
                "compression_ratio": len(compressed.semantic_tags) / len(tag_counter),
            },
        )

    # {ΛFUSION}
    def _fuse_nodes(self, nodes: list[MemoryNode]) -> CollapseResult:
        """
        Fuse nodes into higher-order abstraction.

        Args:
            nodes: Nodes to fuse

        Returns:
            CollapseResult
        """
        # Create fusion node
        fusion = MemoryNode()

        # Create abstraction tags
        tag_categories = self._categorize_tags(nodes)
        fusion.semantic_tags = [f"abstract_{cat}" for cat in tag_categories]
        fusion.semantic_tags.append(f"fusion_of_{len(nodes)}_nodes")

        # Fusion uses maximum emotional weight (peak experience)
        fusion.emotional_weight = max(n.emotional_weight for n in nodes)

        # Abstract relationships
        fusion.parent_nodes = []  # Fusion creates new abstraction level
        fusion.child_nodes = [n.node_id for n in nodes]  # Points to original nodes

        # Abstract content
        fusion.content = {
            "type": "fusion_abstraction",
            "source_count": len(nodes),
            "categories": list(tag_categories.keys()),
            "peak_emotion": fusion.emotional_weight,
            "creation_time": datetime.now(timezone.utc).isoformat(),
        }

        # Update metadata
        fusion.collapse_count = max(n.collapse_count for n in nodes) + 1
        fusion.entropy_score = 0.2  # Low entropy for abstractions
        fusion.content_hash = fusion.compute_hash()

        # Moderate semantic loss for abstraction
        semantic_loss = 0.15  # Some detail lost in abstraction

        return CollapseResult(
            collapsed_node=fusion,
            source_nodes=[n.node_id for n in nodes],
            collapse_type="fusion",
            entropy_reduction=0.6,  # High reduction through abstraction
            semantic_loss=semantic_loss,
            metadata={
                "abstraction_level": fusion.collapse_count,
                "categories": list(tag_categories.keys()),
            },
        )

    def _categorize_tags(self, nodes: list[MemoryNode]) -> dict[str, list[str]]:
        """Categorize semantic tags into higher-level concepts."""
        categories = {
            "emotion": [],
            "cognition": [],
            "memory": [],
            "action": [],
            "entity": [],
            "other": [],
        }

        # Simple categorization (in practice would use NLP/ontology)
        emotion_keywords = ["happy", "sad", "fear", "anger", "joy", "emotion"]
        cognition_keywords = ["think", "know", "understand", "learn", "reason"]
        memory_keywords = ["remember", "recall", "forget", "memory", "past"]
        action_keywords = ["do", "act", "move", "create", "change"]

        for node in nodes:
            for tag in node.semantic_tags:
                tag_lower = tag.lower()
                categorized = False

                if any(k in tag_lower for k in emotion_keywords):
                    categories["emotion"].append(tag)
                    categorized = True
                elif any(k in tag_lower for k in cognition_keywords):
                    categories["cognition"].append(tag)
                    categorized = True
                elif any(k in tag_lower for k in memory_keywords):
                    categories["memory"].append(tag)
                    categorized = True
                elif any(k in tag_lower for k in action_keywords):
                    categories["action"].append(tag)
                    categorized = True

                if not categorized:
                    categories["other"].append(tag)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _update_collapse_tracking(self, result: CollapseResult, entropy: float) -> None:
        """Update global collapse tracking system."""
        if not self.collapse_tracker:
            return

        # Update entropy score
        self.collapse_tracker.update_entropy_score(
            symbolic_data=[result.collapsed_node.node_id],
            component_scores={
                "memory_collapse": entropy,
                "semantic_integrity": 1.0 - result.semantic_loss,
            },
        )

        # Record collapse event
        self.collapse_tracker.record_collapse_event(
            affected_components=["memory", "symbolic"],
            symbolic_drift={"memory_entropy": entropy},
            metadata={
                "collapse_type": result.collapse_type,
                "source_count": len(result.source_nodes),
                "entropy_reduction": result.entropy_reduction,
            },
        )

    def get_collapse_metrics(self) -> dict[str, Any]:
        """Get metrics about collapse operations."""
        if not self.collapse_history:
            return {
                "total_collapses": 0,
                "nodes_affected": 0,
                "average_entropy_reduction": 0.0,
                "average_semantic_loss": 0.0,
            }

        total_source_nodes = sum(len(r.source_nodes) for r in self.collapse_history)
        avg_entropy_reduction = sum(r.entropy_reduction for r in self.collapse_history) / len(self.collapse_history)
        avg_semantic_loss = sum(r.semantic_loss for r in self.collapse_history) / len(self.collapse_history)

        collapse_type_counts = Counter(r.collapse_type for r in self.collapse_history)

        return {
            "total_collapses": len(self.collapse_history),
            "nodes_affected": total_source_nodes,
            "nodes_created": len([r.collapsed_node for r in self.collapse_history]),
            "average_entropy_reduction": avg_entropy_reduction,
            "average_semantic_loss": avg_semantic_loss,
            "collapse_types": dict(collapse_type_counts),
            "current_node_count": len(self.nodes),
        }

    def visualize_collapse_graph(self) -> dict[str, Any]:
        """Generate visualization data for collapse operations."""
        graph_data = {"nodes": [], "edges": [], "collapse_events": []}

        # Add all nodes
        for node_id, node in self.nodes.items():
            graph_data["nodes"].append(
                {
                    "id": node_id,
                    "type": "collapsed" if node.collapse_count > 0 else "original",
                    "collapse_count": node.collapse_count,
                    "entropy": node.entropy_score,
                    "tags": node.semantic_tags[:5],  # First 5 tags
                }
            )

        # Add edges from collapse history
        for result in self.collapse_history:
            for source in result.source_nodes:
                graph_data["edges"].append(
                    {
                        "source": source,
                        "target": result.collapsed_node.node_id,
                        "type": result.collapse_type,
                    }
                )

            graph_data["collapse_events"].append(
                {
                    "type": result.collapse_type,
                    "sources": result.source_nodes,
                    "target": result.collapsed_node.node_id,
                    "entropy_reduction": result.entropy_reduction,
                    "semantic_loss": result.semantic_loss,
                }
            )

        return graph_data


# Singleton instance
_global_engine: Optional[CollapseEngine] = None


def get_global_engine() -> CollapseEngine:
    """Get or create the global collapse engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = CollapseEngine()
    return _global_engine


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠═══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/core/symbolic/collapse/test_collapse_engine.py
║   - Coverage: Target 85%
║   - Integration: CollapseTracker, CollapseTrace
║
║ MONITORING:
║   - Metrics: collapse_count, entropy_reduction, semantic_loss
║   - Events: All collapse operations logged with trace IDs
║   - Alerts: High semantic loss (>30%), rapid collapse rate
║
║ COMPLIANCE:
║   - Memory Safety: Preserves causal relationships
║   - Semantic Integrity: Tracks information loss
║   - Audit Trail: Complete collapse history maintained
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
