#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ══════════════════════════════════════════════════════════════════════════════════
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: causal_memory_chains.py
║ Path: memory/systems/causal_memory_chains.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🚀 LUKHAS AI - CAUSAL MEMORY CHAINS: WEAVING THE TAPESTRY OF REASONING
║ ║ Illuminating the labyrinth of cause-and-effect for the nascent AGI mind
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: causal_memory_chains.py
║ ║ Path: memory/systems/causal_memory_chains.py
║ ║ Version: 1.0.0 | Created: 2025-07-29
║ ║ Author: LUKHAS AI Development Team
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the intricate dance of intellect and intuition, where shadows play upon the
║ ║ canvas of cognition, this module emerges as a beacon of clarity. It encapsulates
║ ║ the essence of causality, weaving together the threads of memory and inference,
║ ║ crafting a rich tapestry for Artificial General Intelligence. Herein lies a system
║ ║ that transcends mere data storage, aspiring instead to harness the profound
║ ║ symphony of relationships that govern the universe of thought.
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
import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import networkx as nx
import numpy as np


class CausalRelationType(Enum):
    """Types of causal relationships between memories"""

    DIRECT_CAUSE = "direct_cause"  # A directly causes B
    INDIRECT_CAUSE = "indirect_cause"  # A causes B through intermediates
    NECESSARY_CONDITION = "necessary_condition"  # A is necessary for B
    SUFFICIENT_CONDITION = "sufficient_condition"  # A is sufficient for B
    CONTRIBUTORY_CAUSE = "contributory_cause"  # A contributes to B
    PREVENTIVE_CAUSE = "preventive_cause"  # A prevents B
    ENABLING_CONDITION = "enabling_condition"  # A enables B to occur
    TRIGGERING_EVENT = "triggering_event"  # A triggers B
    CORRELATION = "correlation"  # A and B are correlated
    SPURIOUS_CORRELATION = "spurious_correlation"  # False causal relationship


class CausalStrength(Enum):
    """Strength of causal relationships"""

    VERY_STRONG = 0.9
    STRONG = 0.75
    MODERATE = 0.6
    WEAK = 0.4
    VERY_WEAK = 0.2
    UNCERTAIN = 0.1


@dataclass
class CausalEvidence:
    """Evidence supporting a causal relationship"""

    evidence_type: str  # temporal, statistical, experimental, logical
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    source_memories: List[str]  # Memory IDs that provide this evidence
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_type": self.evidence_type,
            "strength": self.strength,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "source_memories": self.source_memories,
            "description": self.description,
        }


@dataclass
class CausalRelation:
    """Represents a causal relationship between two memories"""

    cause_memory_id: str
    effect_memory_id: str
    relation_type: CausalRelationType
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    temporal_delay: Optional[timedelta] = None  # Time between cause and effect
    evidence: List[CausalEvidence] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    validated: bool = False
    validation_count: int = 0

    def add_evidence(self, evidence: CausalEvidence):
        """Add supporting evidence to this causal relation"""
        self.evidence.append(evidence)
        self.last_updated = datetime.now()

        # Update strength based on accumulated evidence
        self._update_strength()

    def _update_strength(self):
        """Update causal strength based on accumulated evidence"""
        if not self.evidence:
            return

        # Weight evidence by confidence and recency
        total_weight = 0.0
        weighted_strength = 0.0

        for evidence in self.evidence:
            # Recency weighting (newer evidence gets more weight)
            days_old = (datetime.now() - evidence.timestamp).days
            recency_weight = max(0.1, 1.0 - (days_old * 0.01))  # Decay over time

            weight = evidence.confidence * recency_weight
            total_weight += weight
            weighted_strength += evidence.strength * weight

        if total_weight > 0:
            self.strength = min(0.99, weighted_strength / total_weight)
            self.confidence = min(0.99, total_weight / len(self.evidence))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cause_memory_id": self.cause_memory_id,
            "effect_memory_id": self.effect_memory_id,
            "relation_type": self.relation_type.value,
            "strength": self.strength,
            "confidence": self.confidence,
            "temporal_delay": (
                self.temporal_delay.total_seconds() if self.temporal_delay else None
            ),
            "evidence": [e.to_dict() for e in self.evidence],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "validated": self.validated,
            "validation_count": self.validation_count,
        }


@dataclass
class CausalChain:
    """Represents a sequence of causally connected memories"""

    chain_id: str
    memory_sequence: List[str]  # Ordered list of memory IDs
    causal_relations: List[CausalRelation]
    chain_strength: float  # Overall strength of the causal chain
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    chain_type: str = "sequential"  # sequential, branching, converging

    def get_chain_length(self) -> int:
        """Get the length of the causal chain"""
        return len(self.memory_sequence)

    def get_total_delay(self) -> Optional[timedelta]:
        """Get total temporal delay across the chain"""
        total_delay = timedelta(0)
        for relation in self.causal_relations:
            if relation.temporal_delay:
                total_delay += relation.temporal_delay
        return total_delay if total_delay.total_seconds() > 0 else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "memory_sequence": self.memory_sequence,
            "causal_relations": [r.to_dict() for r in self.causal_relations],
            "chain_strength": self.chain_strength,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "chain_type": self.chain_type,
            "chain_length": self.get_chain_length(),
            "total_delay": (
                self.get_total_delay().total_seconds()
                if self.get_total_delay()
                else None
            ),
        }


class TemporalCausalAnalyzer:
    """
    Analyzes temporal patterns to infer causal relationships.

    Uses time-series analysis and pattern recognition to identify
    potential cause-and-effect relationships in memory sequences.
    """

    def __init__(
        self,
        min_temporal_gap: timedelta = timedelta(seconds=1),
        max_temporal_gap: timedelta = timedelta(hours=24),
        min_confidence_threshold: float = 0.3,
    ):
        self.min_temporal_gap = min_temporal_gap
        self.max_temporal_gap = max_temporal_gap
        self.min_confidence_threshold = min_confidence_threshold

        logger.info(
            "Temporal causal analyzer initialized",
            min_gap=min_temporal_gap,
            max_gap=max_temporal_gap,
            min_confidence=min_confidence_threshold,
        )

    async def analyze_temporal_sequence(
        self, memories: List[Dict[str, Any]]
    ) -> List[CausalRelation]:
        """
        Analyze a sequence of memories for temporal causal patterns.

        Args:
            memories: List of memory dictionaries with timestamps

        Returns:
            List of inferred causal relations
        """

        if len(memories) < 2:
            return []

        # Sort memories by timestamp
        sorted_memories = sorted(
            memories, key=lambda m: m.get("timestamp", datetime.min)
        )

        causal_relations = []

        # Analyze pairs of memories for causal relationships
        for i in range(len(sorted_memories)):
            for j in range(i + 1, len(sorted_memories)):
                memory_a = sorted_memories[i]
                memory_b = sorted_memories[j]

                # Check temporal constraints
                time_diff = memory_b["timestamp"] - memory_a["timestamp"]

                if self.min_temporal_gap <= time_diff <= self.max_temporal_gap:
                    relation = await self._analyze_memory_pair(
                        memory_a, memory_b, time_diff
                    )
                    if relation:
                        causal_relations.append(relation)

        return causal_relations

    async def _analyze_memory_pair(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any], time_diff: timedelta
    ) -> Optional[CausalRelation]:
        """Analyze a pair of memories for causal relationship"""

        # Extract features for causal analysis
        content_similarity = await self._calculate_content_similarity(
            memory_a, memory_b
        )
        semantic_connection = await self._calculate_semantic_connection(
            memory_a, memory_b
        )
        tag_overlap = self._calculate_tag_overlap(memory_a, memory_b)

        # Causal strength indicators
        temporal_strength = self._calculate_temporal_strength(time_diff)
        content_strength = content_similarity * 0.3 + semantic_connection * 0.7
        tag_strength = tag_overlap

        # Overall causal strength
        causal_strength = (
            temporal_strength * 0.4 + content_strength * 0.4 + tag_strength * 0.2
        )

        # Determine if relationship is strong enough
        if causal_strength < self.min_confidence_threshold:
            return None

        # Determine relation type based on analysis
        relation_type = self._determine_relation_type(
            memory_a, memory_b, causal_strength
        )

        # Create evidence
        evidence = CausalEvidence(
            evidence_type="temporal",
            strength=causal_strength,
            confidence=min(0.9, causal_strength + 0.2),
            timestamp=datetime.now(),
            source_memories=[memory_a["id"], memory_b["id"]],
            description=f"Temporal sequence analysis: {time_diff.total_seconds():.1f}s gap",
        )

        # Create causal relation
        relation = CausalRelation(
            cause_memory_id=memory_a["id"],
            effect_memory_id=memory_b["id"],
            relation_type=relation_type,
            strength=causal_strength,
            confidence=evidence.confidence,
            temporal_delay=time_diff,
            evidence=[evidence],
        )

        logger.debug(
            "Causal relation inferred",
            cause=memory_a["id"][:8],
            effect=memory_b["id"][:8],
            type=relation_type.value,
            strength=causal_strength,
            delay=time_diff.total_seconds(),
        )

        return relation

    async def _calculate_content_similarity(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any]
    ) -> float:
        """Calculate content similarity between two memories"""

        content_a = memory_a.get("content", "")
        content_b = memory_b.get("content", "")

        if not content_a or not content_b:
            return 0.0

        # Simple word overlap similarity (placeholder for more sophisticated NLP)
        words_a = set(content_a.lower().split())
        words_b = set(content_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a.intersection(words_b))
        union = len(words_a.union(words_b))

        return intersection / union if union > 0 else 0.0

    async def _calculate_semantic_connection(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any]
    ) -> float:
        """Calculate semantic connection between memories"""

        # Use embeddings if available
        embedding_a = memory_a.get("embedding")
        embedding_b = memory_b.get("embedding")

        if embedding_a is not None and embedding_b is not None:
            embedding_a = np.array(embedding_a)
            embedding_b = np.array(embedding_b)

            # Cosine similarity
            similarity = np.dot(embedding_a, embedding_b) / (
                np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b)
            )
            return max(0.0, float(similarity))

        # Fallback to content analysis
        return await self._calculate_content_similarity(memory_a, memory_b)

    def _calculate_tag_overlap(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any]
    ) -> float:
        """Calculate tag overlap between memories"""

        tags_a = set(memory_a.get("tags", []))
        tags_b = set(memory_b.get("tags", []))

        if not tags_a or not tags_b:
            return 0.0

        intersection = len(tags_a.intersection(tags_b))
        union = len(tags_a.union(tags_b))

        return intersection / union if union > 0 else 0.0

    def _calculate_temporal_strength(self, time_diff: timedelta) -> float:
        """Calculate temporal strength based on time difference"""

        seconds = time_diff.total_seconds()
        max_seconds = self.max_temporal_gap.total_seconds()

        # Stronger causal inference for shorter time gaps
        # Using exponential decay
        return max(0.1, np.exp(-seconds / (max_seconds * 0.3)))

    def _determine_relation_type(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any], strength: float
    ) -> CausalRelationType:
        """Determine the type of causal relation"""

        # Analyze content for causal keywords and patterns
        content_a = memory_a.get("content", "").lower()
        content_b = memory_b.get("content", "").lower()

        # Look for causal language patterns
        causal_keywords = {
            "direct_cause": ["caused", "resulted in", "led to", "triggered"],
            "preventive_cause": ["prevented", "stopped", "blocked", "avoided"],
            "enabling_condition": [
                "enabled",
                "allowed",
                "facilitated",
                "made possible",
            ],
            "necessary_condition": ["required", "needed", "necessary", "essential"],
        }

        # Check for causal language
        for relation_type, keywords in causal_keywords.items():
            if any(word in content_a or word in content_b for word in keywords):
                return CausalRelationType(relation_type)

        # Default classification based on strength
        if strength > 0.7:
            return CausalRelationType.DIRECT_CAUSE
        elif strength > 0.5:
            return CausalRelationType.CONTRIBUTORY_CAUSE
        else:
            return CausalRelationType.CORRELATION


class CausalGraphBuilder:
    """
    Builds and maintains causal graphs from memory relationships.

    Creates directed graphs representing causal structures in the
    AGI's memory for advanced reasoning and prediction.
    """

    def __init__(self):
        self.causal_graph = nx.DiGraph()
        self.memory_metadata: Dict[str, Dict[str, Any]] = {}
        self.causal_relations: Dict[str, CausalRelation] = {}

        logger.info("Causal graph builder initialized")

    def add_memory(self, memory_id: str, memory_data: Dict[str, Any]):
        """Add a memory node to the causal graph"""

        self.causal_graph.add_node(memory_id)
        self.memory_metadata[memory_id] = memory_data

        logger.debug("Memory added to causal graph", memory_id=memory_id[:8])

    def add_causal_relation(self, relation: CausalRelation):
        """Add a causal relation to the graph"""

        # Add nodes if they don't exist
        if relation.cause_memory_id not in self.causal_graph:
            self.causal_graph.add_node(relation.cause_memory_id)

        if relation.effect_memory_id not in self.causal_graph:
            self.causal_graph.add_node(relation.effect_memory_id)

        # Add or update edge
        relation_id = f"{relation.cause_memory_id}->{relation.effect_memory_id}"
        self.causal_relations[relation_id] = relation

        self.causal_graph.add_edge(
            relation.cause_memory_id,
            relation.effect_memory_id,
            relation_type=relation.relation_type.value,
            strength=relation.strength,
            confidence=relation.confidence,
            temporal_delay=(
                relation.temporal_delay.total_seconds()
                if relation.temporal_delay
                else None
            ),
        )

        logger.debug(
            "Causal relation added to graph",
            cause=relation.cause_memory_id[:8],
            effect=relation.effect_memory_id[:8],
            type=relation.relation_type.value,
            strength=relation.strength,
        )

    def find_causal_paths(
        self, source_memory_id: str, target_memory_id: str, max_path_length: int = 5
    ) -> List[List[str]]:
        """Find all causal paths between two memories"""

        try:
            paths = list(
                nx.all_simple_paths(
                    self.causal_graph,
                    source_memory_id,
                    target_memory_id,
                    cutoff=max_path_length,
                )
            )
            return paths
        except nx.NetworkXNoPath:
            return []

    def get_causal_ancestors(self, memory_id: str, max_depth: int = 3) -> List[str]:
        """Get all memories that causally influence the given memory"""

        ancestors = set()
        queue = deque([(memory_id, 0)])

        while queue:
            current_id, depth = queue.popleft()

            if depth >= max_depth:
                continue

            # Get all predecessors (causes)
            predecessors = list(self.causal_graph.predecessors(current_id))

            for pred in predecessors:
                if pred not in ancestors:
                    ancestors.add(pred)
                    queue.append((pred, depth + 1))

        return list(ancestors)

    def get_causal_descendants(self, memory_id: str, max_depth: int = 3) -> List[str]:
        """Get all memories that are causally influenced by the given memory"""

        descendants = set()
        queue = deque([(memory_id, 0)])

        while queue:
            current_id, depth = queue.popleft()

            if depth >= max_depth:
                continue

            # Get all successors (effects)
            successors = list(self.causal_graph.successors(current_id))

            for succ in successors:
                if succ not in descendants:
                    descendants.add(succ)
                    queue.append((succ, depth + 1))

        return list(descendants)

    def identify_causal_chains(self, min_chain_length: int = 3) -> List[CausalChain]:
        """Identify significant causal chains in the graph"""

        chains = []

        # Find all simple paths above minimum length
        for start_node in self.causal_graph.nodes():
            for end_node in self.causal_graph.nodes():
                if start_node != end_node:
                    paths = self.find_causal_paths(
                        start_node, end_node, min_chain_length + 2
                    )

                    for path in paths:
                        if len(path) >= min_chain_length:
                            chain = self._create_causal_chain(path)
                            if chain:
                                chains.append(chain)

        # Sort by chain strength
        chains.sort(key=lambda c: c.chain_strength, reverse=True)

        return chains

    def _create_causal_chain(self, memory_path: List[str]) -> Optional[CausalChain]:
        """Create a CausalChain from a path of memories"""

        if len(memory_path) < 2:
            return None

        # Collect causal relations along the path
        causal_relations = []
        total_strength = 0.0
        total_confidence = 0.0

        for i in range(len(memory_path) - 1):
            cause_id = memory_path[i]
            effect_id = memory_path[i + 1]
            relation_id = f"{cause_id}->{effect_id}"

            if relation_id in self.causal_relations:
                relation = self.causal_relations[relation_id]
                causal_relations.append(relation)
                total_strength += relation.strength
                total_confidence += relation.confidence

        if not causal_relations:
            return None

        # Calculate chain metrics
        chain_strength = total_strength / len(causal_relations)
        confidence = total_confidence / len(causal_relations)

        # Generate chain ID
        chain_id = hashlib.sha256(
            f"{'->'.join(memory_path)}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        return CausalChain(
            chain_id=chain_id,
            memory_sequence=memory_path,
            causal_relations=causal_relations,
            chain_strength=chain_strength,
            confidence=confidence,
        )

    def analyze_causal_structure(self) -> Dict[str, Any]:
        """Analyze the overall causal structure of the graph"""

        if not self.causal_graph.nodes():
            return {"error": "Empty causal graph"}

        # Basic graph metrics
        num_nodes = self.causal_graph.number_of_nodes()
        num_edges = self.causal_graph.number_of_edges()

        # Centrality measures
        in_degree_centrality = nx.in_degree_centrality(self.causal_graph)
        out_degree_centrality = nx.out_degree_centrality(self.causal_graph)

        # Find most influential memories
        most_influential_causes = sorted(
            out_degree_centrality.items(), key=lambda x: x[1], reverse=True
        )[:5]

        most_influenced_effects = sorted(
            in_degree_centrality.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Detect cycles (circular causality)
        cycles = list(nx.simple_cycles(self.causal_graph))

        # Calculate average path length
        try:
            if nx.is_weakly_connected(self.causal_graph):
                avg_path_length = nx.average_shortest_path_length(
                    self.causal_graph.to_undirected()
                )
            else:
                avg_path_length = None
        except:
            avg_path_length = None

        return {
            "total_memories": num_nodes,
            "total_relations": num_edges,
            "density": nx.density(self.causal_graph),
            "most_influential_causes": most_influential_causes,
            "most_influenced_effects": most_influenced_effects,
            "circular_causality_detected": len(cycles) > 0,
            "circular_chains": len(cycles),
            "average_path_length": avg_path_length,
            "weakly_connected": nx.is_weakly_connected(self.causal_graph),
            "strongly_connected_components": nx.number_strongly_connected_components(
                self.causal_graph
            ),
        }


class CausalReasoningEngine:
    """
    Main engine for causal reasoning in AGI memory systems.

    Integrates temporal analysis, graph building, and reasoning
    capabilities for advanced AGI decision-making.
    """

    def __init__(
        self,
        enable_temporal_analysis: bool = True,
        enable_graph_analysis: bool = True,
        min_confidence_threshold: float = 0.3,
    ):
        self.enable_temporal_analysis = enable_temporal_analysis
        self.enable_graph_analysis = enable_graph_analysis
        self.min_confidence_threshold = min_confidence_threshold

        # Initialize components
        self.temporal_analyzer = (
            TemporalCausalAnalyzer(min_confidence_threshold=min_confidence_threshold)
            if enable_temporal_analysis
            else None
        )

        self.graph_builder = CausalGraphBuilder() if enable_graph_analysis else None

        # Memory storage for causal reasoning
        self.causal_memory_store: Dict[str, Dict[str, Any]] = {}
        self.causal_chains: Dict[str, CausalChain] = {}

        logger.info(
            "Causal reasoning engine initialized",
            temporal_analysis=enable_temporal_analysis,
            graph_analysis=enable_graph_analysis,
            min_confidence=min_confidence_threshold,
        )

    async def add_memory_for_causal_analysis(
        self,
        memory_id: str,
        content: str,
        tags: List[str] = None,
        embedding: np.ndarray = None,
        timestamp: datetime = None,
        metadata: Dict[str, Any] = None,
    ):
        """Add a memory to the causal reasoning system"""

        memory_data = {
            "id": memory_id,
            "content": content,
            "tags": tags or [],
            "embedding": embedding.tolist() if embedding is not None else None,
            "timestamp": timestamp or datetime.now(),
            "metadata": metadata or {},
        }

        self.causal_memory_store[memory_id] = memory_data

        # Add to graph builder
        if self.graph_builder:
            self.graph_builder.add_memory(memory_id, memory_data)

        logger.debug("Memory added for causal analysis", memory_id=memory_id[:8])

    async def analyze_causal_relationships(
        self, memory_ids: List[str] = None, time_window: timedelta = None
    ) -> List[CausalRelation]:
        """Analyze causal relationships in memories"""

        if memory_ids:
            memories = [
                self.causal_memory_store[mid]
                for mid in memory_ids
                if mid in self.causal_memory_store
            ]
        else:
            memories = list(self.causal_memory_store.values())

        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            memories = [m for m in memories if m["timestamp"] >= cutoff_time]

        if not memories:
            return []

        # Temporal analysis
        causal_relations = []
        if self.temporal_analyzer:
            temporal_relations = await self.temporal_analyzer.analyze_temporal_sequence(
                memories
            )
            causal_relations.extend(temporal_relations)

        # Add relations to graph
        if self.graph_builder:
            for relation in causal_relations:
                self.graph_builder.add_causal_relation(relation)

        logger.info(
            "Causal relationship analysis completed",
            memories_analyzed=len(memories),
            relations_found=len(causal_relations),
        )

        return causal_relations

    async def find_causal_explanation(
        self, target_memory_id: str, max_depth: int = 3
    ) -> Dict[str, Any]:
        """Find causal explanation for a specific memory/event"""

        if not self.graph_builder or target_memory_id not in self.causal_memory_store:
            return {"error": "Memory not found or graph analysis disabled"}

        # Find causal ancestors
        causal_ancestors = self.graph_builder.get_causal_ancestors(
            target_memory_id, max_depth
        )

        # Build explanation
        explanation = {
            "target_memory": self.causal_memory_store[target_memory_id],
            "causal_factors": [],
            "explanation_confidence": 0.0,
            "explanation_depth": len(causal_ancestors),
        }

        total_confidence = 0.0
        for ancestor_id in causal_ancestors:
            if ancestor_id in self.causal_memory_store:
                # Find direct causal path
                paths = self.graph_builder.find_causal_paths(
                    ancestor_id, target_memory_id, max_depth
                )

                if paths:
                    shortest_path = min(paths, key=len)

                    # Calculate path strength
                    path_strength = 1.0
                    for i in range(len(shortest_path) - 1):
                        relation_id = f"{shortest_path[i]}->{shortest_path[i+1]}"
                        if relation_id in self.graph_builder.causal_relations:
                            path_strength *= self.graph_builder.causal_relations[
                                relation_id
                            ].strength

                    explanation["causal_factors"].append(
                        {
                            "memory": self.causal_memory_store[ancestor_id],
                            "causal_path": shortest_path,
                            "path_length": len(shortest_path) - 1,
                            "path_strength": path_strength,
                        }
                    )

                    total_confidence += path_strength

        if explanation["causal_factors"]:
            explanation["explanation_confidence"] = total_confidence / len(
                explanation["causal_factors"]
            )

        return explanation

    async def predict_causal_outcomes(
        self, source_memory_id: str, max_depth: int = 3
    ) -> Dict[str, Any]:
        """Predict potential causal outcomes from a memory/event"""

        if not self.graph_builder or source_memory_id not in self.causal_memory_store:
            return {"error": "Memory not found or graph analysis disabled"}

        # Find causal descendants
        causal_descendants = self.graph_builder.get_causal_descendants(
            source_memory_id, max_depth
        )

        # Build prediction
        prediction = {
            "source_memory": self.causal_memory_store[source_memory_id],
            "predicted_outcomes": [],
            "prediction_confidence": 0.0,
            "prediction_depth": len(causal_descendants),
        }

        total_confidence = 0.0
        for descendant_id in causal_descendants:
            if descendant_id in self.causal_memory_store:
                # Find direct causal path
                paths = self.graph_builder.find_causal_paths(
                    source_memory_id, descendant_id, max_depth
                )

                if paths:
                    shortest_path = min(paths, key=len)

                    # Calculate path strength
                    path_strength = 1.0
                    for i in range(len(shortest_path) - 1):
                        relation_id = f"{shortest_path[i]}->{shortest_path[i+1]}"
                        if relation_id in self.graph_builder.causal_relations:
                            path_strength *= self.graph_builder.causal_relations[
                                relation_id
                            ].strength

                    prediction["predicted_outcomes"].append(
                        {
                            "memory": self.causal_memory_store[descendant_id],
                            "causal_path": shortest_path,
                            "path_length": len(shortest_path) - 1,
                            "prediction_strength": path_strength,
                        }
                    )

                    total_confidence += path_strength

        if prediction["predicted_outcomes"]:
            prediction["prediction_confidence"] = total_confidence / len(
                prediction["predicted_outcomes"]
            )

        return prediction

    async def identify_significant_causal_chains(
        self, min_chain_length: int = 3, min_strength: float = 0.5
    ) -> List[CausalChain]:
        """Identify significant causal chains for AGI reasoning"""

        if not self.graph_builder:
            return []

        # Find all causal chains
        all_chains = self.graph_builder.identify_causal_chains(min_chain_length)

        # Filter by strength
        significant_chains = [
            chain for chain in all_chains if chain.chain_strength >= min_strength
        ]

        # Store for future reference
        for chain in significant_chains:
            self.causal_chains[chain.chain_id] = chain

        logger.info(
            "Significant causal chains identified",
            total_chains=len(all_chains),
            significant_chains=len(significant_chains),
            min_length=min_chain_length,
            min_strength=min_strength,
        )

        return significant_chains

    def get_causal_reasoning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about causal reasoning"""

        stats = {
            "total_memories": len(self.causal_memory_store),
            "causal_chains": len(self.causal_chains),
            "temporal_analysis_enabled": self.temporal_analyzer is not None,
            "graph_analysis_enabled": self.graph_builder is not None,
        }

        if self.graph_builder:
            graph_stats = self.graph_builder.analyze_causal_structure()
            stats.update(graph_stats)

        return stats


# Integration with existing memory systems
class CausalMemoryWrapper:
    """
    Wrapper that adds causal reasoning to existing memory systems.

    Integrates with OptimizedHybridMemoryFold to provide causal
    analysis capabilities.
    """

    def __init__(self, base_memory_system, enable_causal_reasoning: bool = True):
        self.base_memory_system = base_memory_system
        self.enable_causal_reasoning = enable_causal_reasoning

        if enable_causal_reasoning:
            self.causal_engine = CausalReasoningEngine()
        else:
            self.causal_engine = None

        logger.info(
            "Causal memory wrapper initialized",
            causal_reasoning_enabled=enable_causal_reasoning,
        )

    async def fold_in_with_causal_analysis(
        self,
        data: str,
        tags: List[str] = None,
        embedding: np.ndarray = None,
        timestamp: datetime = None,
        **kwargs,
    ) -> str:
        """Store memory with causal analysis"""

        # Store in base system
        memory_id = await self.base_memory_system.fold_in_with_embedding(
            data=data, tags=tags, embedding=embedding, **kwargs
        )

        # Add to causal analysis
        if self.causal_engine:
            await self.causal_engine.add_memory_for_causal_analysis(
                memory_id=memory_id,
                content=data,
                tags=tags,
                embedding=embedding,
                timestamp=timestamp or datetime.now(),
            )

            # Analyze causal relationships periodically
            if len(self.causal_engine.causal_memory_store) % 10 == 0:
                await self.causal_engine.analyze_causal_relationships()

        return memory_id

    async def fold_out_with_causal_context(
        self,
        query: str,
        top_k: int = 10,
        include_causal_explanation: bool = True,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Retrieve memories with causal context"""

        # Get base results
        base_results = await self.base_memory_system.fold_out_semantic(
            query=query, top_k=top_k, **kwargs
        )

        enhanced_results = []
        for memory, score in base_results:
            result = {"memory": memory, "score": score, "causal_context": {}}

            # Add causal context if enabled
            if (
                self.causal_engine
                and include_causal_explanation
                and hasattr(memory, "id")
            ):
                memory_id = (
                    memory.id if hasattr(memory, "id") else str(hash(memory.data))
                )

                # Get causal explanation
                explanation = await self.causal_engine.find_causal_explanation(
                    memory_id
                )
                result["causal_context"]["explanation"] = explanation

                # Get causal predictions
                prediction = await self.causal_engine.predict_causal_outcomes(memory_id)
                result["causal_context"]["predictions"] = prediction

            enhanced_results.append(result)

        return enhanced_results


# Factory functions for easy integration
async def create_causal_memory_system(
    base_memory_system=None,
    enable_temporal_analysis: bool = True,
    enable_graph_analysis: bool = True,
    min_confidence_threshold: float = 0.3,
):
    """
    Create a causal reasoning-enabled memory system.

    Args:
        base_memory_system: Existing memory system to enhance
        enable_temporal_analysis: Enable temporal causal analysis
        enable_graph_analysis: Enable causal graph construction
        min_confidence_threshold: Minimum confidence for causal relations

    Returns:
        CausalMemoryWrapper or CausalReasoningEngine
    """

    if base_memory_system:
        return CausalMemoryWrapper(
            base_memory_system=base_memory_system, enable_causal_reasoning=True
        )
    else:
        return CausalReasoningEngine(
            enable_temporal_analysis=enable_temporal_analysis,
            enable_graph_analysis=enable_graph_analysis,
            min_confidence_threshold=min_confidence_threshold,
        )


# Example usage and testing
async def example_causal_reasoning():
    """Example of causal reasoning in AGI memory"""

    print("🚀 Causal Memory Chains for AGI Reasoning Demo")
    print("=" * 60)

    # Create causal reasoning engine
    causal_engine = await create_causal_memory_system()

    # Add sequence of causally related memories
    memories = [
        {
            "id": "mem_1",
            "content": "I decided to study machine learning to improve my AI capabilities",
            "tags": ["decision", "learning", "ai"],
            "timestamp": datetime.now() - timedelta(days=10),
        },
        {
            "id": "mem_2",
            "content": "I started reading research papers on neural networks and deep learning",
            "tags": ["study", "research", "neural_networks"],
            "timestamp": datetime.now() - timedelta(days=9),
        },
        {
            "id": "mem_3",
            "content": "My understanding of artificial intelligence concepts significantly improved",
            "tags": ["improvement", "understanding", "ai"],
            "timestamp": datetime.now() - timedelta(days=7),
        },
        {
            "id": "mem_4",
            "content": "I was able to implement a neural network from scratch successfully",
            "tags": ["implementation", "success", "neural_networks"],
            "timestamp": datetime.now() - timedelta(days=5),
        },
    ]

    # Add memories to causal engine
    print("Adding memories for causal analysis...")
    for memory in memories:
        await causal_engine.add_memory_for_causal_analysis(
            memory_id=memory["id"],
            content=memory["content"],
            tags=memory["tags"],
            timestamp=memory["timestamp"],
            embedding=np.random.randn(512).astype(np.float32),
        )

    # Analyze causal relationships
    print("Analyzing causal relationships...")
    causal_relations = await causal_engine.analyze_causal_relationships()

    print(f"✅ Found {len(causal_relations)} causal relationships")

    # Show causal relations
    for relation in causal_relations:
        print(f"  {relation.cause_memory_id} → {relation.effect_memory_id}")
        print(f"    Type: {relation.relation_type.value}")
        print(f"    Strength: {relation.strength:.3f}")
        print(f"    Confidence: {relation.confidence:.3f}")
        if relation.temporal_delay:
            print(f"    Delay: {relation.temporal_delay.total_seconds():.0f}s")
        print()

    # Find causal explanation for final memory
    print("Finding causal explanation for successful implementation...")
    explanation = await causal_engine.find_causal_explanation("mem_4")

    if "error" not in explanation:
        print(f"📊 Explanation confidence: {explanation['explanation_confidence']:.3f}")
        print(f"📈 Causal factors found: {len(explanation['causal_factors'])}")

        for factor in explanation["causal_factors"]:
            print(f"  Cause: {factor['memory']['content'][:50]}...")
            print(f"  Path length: {factor['path_length']}")
            print(f"  Strength: {factor['path_strength']:.3f}")
            print()

    # Identify causal chains
    print("Identifying significant causal chains...")
    causal_chains = await causal_engine.identify_significant_causal_chains(
        min_chain_length=3, min_strength=0.4
    )

    print(f"🔗 Found {len(causal_chains)} significant causal chains")

    for chain in causal_chains:
        print(f"  Chain: {' → '.join(chain.memory_sequence)}")
        print(f"  Length: {chain.get_chain_length()}")
        print(f"  Strength: {chain.chain_strength:.3f}")
        print(f"  Confidence: {chain.confidence:.3f}")
        print()

    # Get reasoning statistics
    stats = causal_engine.get_causal_reasoning_statistics()
    print("📊 Causal reasoning statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("✅ Causal reasoning demo completed!")

    return causal_engine


if __name__ == "__main__":
    asyncio.run(example_causal_reasoning())
