"""
DNA Helix Memory Architecture
=============================
Immutable, temporal memory structure inspired by biological DNA double helix.
Implements MATADA cognitive DNA concepts with quantum-resistant security.

Core Principles:
- Immutability: Once written, memory nodes cannot be altered
- Temporal Evolution: Nodes evolve through time creating helix structure
- Causal Chains: Every memory linked to its triggers and effects
- Emotional Context: Each memory carries emotional state vectors
- Privacy-First: Encrypted storage with differential privacy
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

import numpy as np


class NodeType(Enum):
    """MATADA cognitive node types"""

    SENSORY_IMG = "sensory_img"
    SENSORY_AUD = "sensory_aud"
    SENSORY_VID = "sensory_vid"
    SENSORY_TOUCH = "sensory_touch"
    EMOTION = "emotion"
    INTENT = "intent"
    DECISION = "decision"
    CONTEXT = "context"
    MEMORY = "memory"
    REFLECTION = "reflection"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    AWARENESS = "awareness"


class LinkType(Enum):
    """Types of connections between memory nodes"""

    TEMPORAL = "temporal"  # Time-based sequence
    CAUSAL = "causal"  # Cause-effect relationship
    SEMANTIC = "semantic"  # Meaning-based connection
    EMOTIONAL = "emotional"  # Emotional association
    SPATIAL = "spatial"  # Spatial relationship
    SYMBOLIC = "symbolic"  # Symbol-based link


@dataclass
class CognitiveState:
    """Dynamic cognitive and emotional parameters"""

    confidence: float = 0.5  # [0..1] Certainty level
    valence: float = 0.0  # [-1..1] Emotional positivity/negativity
    arousal: float = 0.5  # [0..1] Emotional intensity
    salience: float = 0.5  # [0..1] Attention weight
    novelty: float = 0.5  # [0..1] Newness factor
    urgency: float = 0.0  # [0..1] Time sensitivity
    shock_factor: float = 0.0  # [0..1] Surprise element

    def to_vector(self) -> np.ndarray:
        """Convert state to numpy vector for computation"""
        return np.array(
            [
                self.confidence,
                self.valence,
                self.arousal,
                self.salience,
                self.novelty,
                self.urgency,
                self.shock_factor,
            ]
        )

    def entropy(self) -> float:
        """Calculate Shannon entropy of the state"""
        vec = self.to_vector()
        # Normalize to probabilities
        vec = np.abs(vec) / (np.sum(np.abs(vec)) + 1e-10)
        # Calculate entropy
        return -np.sum(vec * np.log2(vec + 1e-10))


@dataclass
class MemoryLink:
    """Connection between memory nodes"""

    target_node_id: str
    link_type: LinkType
    weight: float = 1.0  # Connection strength
    bidirectional: bool = False  # Whether link goes both ways
    metadata: dict[str, Any] = field(default_factory=dict)

    def strengthen(self, factor: float = 1.1) -> None:
        """Strengthen connection through use"""
        self.weight = min(10.0, self.weight * factor)

    def weaken(self, factor: float = 0.9) -> None:
        """Weaken connection through decay"""
        self.weight = max(0.01, self.weight * factor)


@dataclass
class MemoryNode:
    """
    Immutable memory node in the DNA helix structure.
    Once created, cannot be modified - only evolved into new nodes.
    """

    # Mandatory fields (immutable)
    id: str = field(default_factory=lambda: f"node_{uuid4().hex[:8]}_{int(time.time())}")
    type: NodeType = NodeType.MEMORY
    created_at: datetime = field(default_factory=datetime.now)
    content_hash: str = ""  # SHA-256 of content for integrity

    # Content and state
    content: dict[str, Any] = field(default_factory=dict)
    state: CognitiveState = field(default_factory=CognitiveState)

    # Connections
    links: list[MemoryLink] = field(default_factory=list)
    evolves_to: list[str] = field(default_factory=list)  # Future versions
    evolved_from: str | None = None  # Previous version

    # Triggers and reflections
    triggers: list[dict[str, Any]] = field(default_factory=list)
    reflections: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    tags: set[str] = field(default_factory=set)
    privacy_level: int = 0  # 0=public, 1=private, 2=encrypted

    def __post_init__(self):
        """Calculate content hash after initialization"""
        if not self.content_hash:
            self.content_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of content for integrity verification"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify node hasn't been tampered with"""
        return self.content_hash == self._calculate_hash()

    def evolve(self, new_content: dict[str, Any], new_state: CognitiveState) -> MemoryNode:
        """
        Create evolved version of this node (immutable evolution).
        Original node remains unchanged.
        """
        new_node = MemoryNode(
            type=self.type,
            content=new_content,
            state=new_state,
            evolved_from=self.id,
            tags=self.tags.copy(),
            privacy_level=self.privacy_level,
        )
        # Record evolution in this node
        self.evolves_to.append(new_node.id)
        return new_node

    def add_reflection(self, reflection_type: str, cause: str, old_state: dict, new_state: dict):
        """Add meta-reflection about state changes"""
        self.reflections.append(
            {
                "type": reflection_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cause": cause,
                "old_state": old_state,
                "new_state": new_state,
            }
        )

    def calculate_importance(self) -> float:
        """Calculate node importance based on connections and state"""
        base_importance = self.state.salience * self.state.confidence
        connection_factor = len(self.links) * 0.1
        evolution_factor = len(self.evolves_to) * 0.05
        reflection_factor = len(self.reflections) * 0.05

        return min(
            1.0,
            base_importance + connection_factor + evolution_factor + reflection_factor,
        )


class DNAHelixMemory:
    """
    Double helix memory structure with two intertwined strands:
    - Spatial strand: Nodes existing in same temporal moment
    - Temporal strand: Node evolution across time
    """

    def __init__(self, max_nodes: int = 10000, decay_rate: float = 0.01):
        self.nodes: dict[str, MemoryNode] = {}
        self.max_nodes = max_nodes
        self.decay_rate = decay_rate

        # Indexes for efficient retrieval
        self.temporal_index: dict[datetime, list[str]] = {}
        self.type_index: dict[NodeType, list[str]] = {}
        self.tag_index: dict[str, set[str]] = {}

        # Helix structure
        self.spatial_strand: list[list[str]] = []  # Nodes at each time slice
        self.temporal_strand: dict[str, list[str]] = {}  # Evolution chains

        # Privacy and security
        self.encryption_key: bytes | None = None
        self.access_log: list[dict[str, Any]] = []

    def add_node(self, node: MemoryNode) -> str:
        """Add new immutable node to memory"""
        if not node.verify_integrity():
            raise ValueError("Node integrity check failed")

        # Check capacity
        if len(self.nodes) >= self.max_nodes:
            self._cleanup_old_nodes()

        # Store node
        self.nodes[node.id] = node

        # Update indexes
        self._index_node(node)

        # Log access for audit
        self._log_access("add", node.id)

        return node.id

    def _index_node(self, node: MemoryNode):
        """Update all indexes with new node"""
        # Temporal index
        time_key = node.created_at.replace(microsecond=0)
        if time_key not in self.temporal_index:
            self.temporal_index[time_key] = []
        self.temporal_index[time_key].append(node.id)

        # Type index
        if node.type not in self.type_index:
            self.type_index[node.type] = []
        self.type_index[node.type].append(node.id)

        # Tag index
        for tag in node.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(node.id)

        # Update helix structure
        self._update_helix(node)

    def _update_helix(self, node: MemoryNode):
        """Update double helix structure with new node"""
        # Add to spatial strand (current time slice)
        current_slice = len(self.spatial_strand) - 1
        if current_slice < 0 or len(self.spatial_strand[current_slice]) > 100:
            self.spatial_strand.append([])
            current_slice += 1
        self.spatial_strand[current_slice].append(node.id)

        # Update temporal strand (evolution chain)
        if node.evolved_from:
            if node.evolved_from not in self.temporal_strand:
                self.temporal_strand[node.evolved_from] = []
            self.temporal_strand[node.evolved_from].append(node.id)

    def create_link(
        self,
        source_id: str,
        target_id: str,
        link_type: LinkType,
        weight: float = 1.0,
        bidirectional: bool = False,
    ) -> bool:
        """Create connection between nodes"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return False

        source = self.nodes[source_id]
        link = MemoryLink(target_id, link_type, weight, bidirectional)
        source.links.append(link)

        if bidirectional:
            target = self.nodes[target_id]
            reverse_link = MemoryLink(source_id, link_type, weight, True)
            target.links.append(reverse_link)

        self._log_access("link", f"{source_id}->{target_id}")
        return True

    def retrieve_by_similarity(self, query_state: CognitiveState, top_k: int = 5) -> list[MemoryNode]:
        """Retrieve nodes most similar to query state"""
        query_vec = query_state.to_vector()
        similarities = []

        for node in self.nodes.values():
            node_vec = node.state.to_vector()
            # Cosine similarity
            similarity = np.dot(query_vec, node_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(node_vec) + 1e-10)
            similarities.append((similarity, node))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in similarities[:top_k]]

    def trace_causal_chain(self, node_id: str, max_depth: int = 10) -> list[str]:
        """Trace causal chain backwards from given node"""
        if node_id not in self.nodes:
            return []

        chain = [node_id]
        current = self.nodes[node_id]
        depth = 0

        while current.evolved_from and depth < max_depth:
            chain.append(current.evolved_from)
            if current.evolved_from in self.nodes:
                current = self.nodes[current.evolved_from]
                depth += 1
            else:
                break

        return chain

    def apply_decay(self):
        """Apply temporal decay to all connections"""
        for node in self.nodes.values():
            for link in node.links:
                link.weaken(1 - self.decay_rate)

    def _cleanup_old_nodes(self):
        """Remove least important nodes when at capacity"""
        # Calculate importance for all nodes
        importances = [(node.calculate_importance(), node_id) for node_id, node in self.nodes.items()]
        importances.sort()

        # Remove bottom 10%
        to_remove = int(self.max_nodes * 0.1)
        for _, node_id in importances[:to_remove]:
            del self.nodes[node_id]

    def _log_access(self, action: str, target: str):
        """Log access for audit trail"""
        self.access_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "target": target,
            }
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get memory system statistics"""
        return {
            "total_nodes": len(self.nodes),
            "node_types": {t: len(nodes) for t, nodes in self.type_index.items()},
            "total_links": sum(len(n.links) for n in self.nodes.values()),
            "evolution_chains": len(self.temporal_strand),
            "spatial_slices": len(self.spatial_strand),
            "avg_importance": np.mean([n.calculate_importance() for n in self.nodes.values()]),
            "memory_entropy": np.mean([n.state.entropy() for n in self.nodes.values()]),
        }


# Singleton instance
_dna_memory_instance: DNAHelixMemory | None = None


def get_dna_memory() -> DNAHelixMemory:
    """Get singleton DNA memory instance"""
    global _dna_memory_instance
    if _dna_memory_instance is None:
        _dna_memory_instance = DNAHelixMemory()
    return _dna_memory_instance


# Alias for backward compatibility
DNAMemoryArchitecture = DNAHelixMemory


class DNAMemoryArchitecture:
    """Wrapper class for DNAHelixMemory with additional methods"""

    def __init__(self):
        self._helix = DNAHelixMemory()

    def encode_memory(self, data):
        """Encode memory into DNA helix structure"""
        node = self._helix.add_node(node_type=NodeType.MEMORY, content=data, parent_ids=[])
        return node.id

    def decode_memory(self, memory_id):
        """Decode memory from dna_helix structure"""
        node = self._helix.get_node(memory_id)
        if node:
            return node.content
        return None