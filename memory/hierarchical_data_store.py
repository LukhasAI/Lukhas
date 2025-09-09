#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: hierarchical_data_store.py
║ Path: memory/systems/hierarchical_data_store.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║                             ESSENCE OF THE MODULE                            ║
║ ║                                                                             ║
║ ║ In the grand tapestry of existence, where the threads of thought intertwine,  ║
║ ║ the Hierarchical Data Store emerges as a sanctuary of wisdom, a boundless    ║
║ ║ library where the echoes of experience resound. This architectural marvel,   ║
║ ║ like the roots of an ancient tree, delves deep into the fertile soil of       ║
║ ║ memory, branching out to embrace the vast expanse of knowledge. Each layer,  ║
║ ║ an intricate stratum of understanding, whispers tales of raw sensory data,    ║
║ ║ evolving into the ethereal realms of abstraction and meta-cognition.         ║
║ ║                                                                             ║
║ ║ Here, the HDS stands as a sentinel, guarding the sanctity of memories,       ║
║ ║ allowing them to flourish in their rightful place within the grand scheme     ║
║ ║ of artificial general intelligence. It is a symphony of organization,        ║
║ ║ where the dissonance of information is harmonized into a melodious cascade    ║
║ ║ of retrieval and reflection. The intricate dance of indexing and access      ║
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
import json
import logging
import zlib
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

# Initialize structured logger
logger = logging.getLogger(__name__)


class MemoryTier(Enum):
    """Hierarchical memory storage tiers"""

    SENSORY = "sensory"  # Raw perceptual data
    EPISODIC = "episodic"  # Event sequences
    SEMANTIC = "semantic"  # Facts and concepts
    PROCEDURAL = "procedural"  # Skills and procedures
    META = "meta"  # Self-knowledge and beliefs


class CompressionLevel(Enum):
    """Compression strategies for different storage levels"""

    NONE = 0  # No compression
    LOSSLESS = 1  # Full fidelity compression
    SEMANTIC = 2  # Meaning-preserving compression
    CONCEPTUAL = 3  # Abstract concept extraction
    SYMBOLIC = 4  # Symbolic representation only


@dataclass
class MemoryNode:
    """Individual memory node in the hierarchical structure"""

    node_id: str = field(default_factory=lambda: str(uuid4()))
    tier: MemoryTier = MemoryTier.SENSORY
    content: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    children_ids: list[str] = field(default_factory=list)
    cross_refs: set[str] = field(default_factory=set)
    compression_level: CompressionLevel = CompressionLevel.NONE
    importance_score: float = 1.0
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decay_rate: float = 0.1
    is_compressed: bool = False
    checksum: Optional[str] = None
    # Collapse state tracking fields (Task 6 - Claude Code)
    collapse_trace_id: Optional[str] = None  # Links to collapse events
    collapse_score_history: list[tuple[datetime, float]] = field(default_factory=list)  # History of collapse scores
    collapse_alert_level: Optional[str] = None  # Current alert level (GREEN/YELLOW/ORANGE/RED)
    collapse_metadata: dict[str, Any] = field(default_factory=dict)  # Additional collapse-related data


@dataclass
class RetrievalContext:
    """Context for memory retrieval operations"""

    query: str
    tier_filter: Optional[MemoryTier] = None
    max_depth: int = 3
    time_range: Optional[tuple[datetime, datetime]] = None
    importance_threshold: float = 0.5
    include_cross_refs: bool = True
    max_results: int = 10


class HierarchicalDataStore:
    """Main HDS implementation for hierarchical memory storage"""

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_memory_mb: int = 1024,
        compression_threshold: float = 0.7,
        prune_interval_seconds: int = 3600,
    ):
        """
        Initialize the Hierarchical Data Store

        # Notes:
        - Storage path is optional; defaults to in-memory storage
        - Compression threshold determines when nodes get compressed
        - Pruning runs periodically to remove low-importance memories
        """
        self.storage_path = storage_path
        self.max_memory_mb = max_memory_mb
        self.compression_threshold = compression_threshold
        self.prune_interval = prune_interval_seconds

        # Core storage structures
        self.nodes: dict[str, MemoryNode] = {}
        self.tier_indices: dict[MemoryTier, set[str]] = defaultdict(set)
        self.parent_child_map: dict[str, set[str]] = defaultdict(set)
        self.importance_queue = deque(maxlen=10000)

        # Caching layers
        self.access_cache: dict[str, Any] = {}
        self.compression_cache: dict[str, bytes] = {}

        # Metrics and monitoring
        self.metrics = {
            "total_nodes": 0,
            "compressed_nodes": 0,
            "total_accesses": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "pruned_nodes": 0,
            "compression_ratio": 0.0,
        }

        # Background tasks
        self._pruning_task = None
        self._compression_task = None
        self._running = False

        logger.info(
            "ΛHDS: Hierarchical Data Store initialized",
            storage_path=str(storage_path) if storage_path else "memory",
            max_memory_mb=max_memory_mb,
        )

    async def start(self):
        """Start background maintenance tasks"""
        self._running = True
        self._pruning_task = asyncio.create_task(self._prune_loop())
        self._compression_task = asyncio.create_task(self._compression_loop())
        logger.info("ΛHDS: Background tasks started")

    async def stop(self):
        """Stop background tasks gracefully"""
        self._running = False
        if self._pruning_task:
            self._pruning_task.cancel()
        if self._compression_task:
            self._compression_task.cancel()
        await self.flush_to_disk()
        logger.info("ΛHDS: Stopped and flushed to disk")

    async def store(
        self,
        content: Any,
        tier: MemoryTier,
        parent_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        importance: float = 1.0,
    ) -> str:
        """
        Store a new memory in the hierarchical structure

        # Notes:
        - Content can be any serializable data
        - Parent_id creates hierarchical relationships
        - Importance affects pruning and compression decisions
        """
        node = MemoryNode(
            tier=tier,
            content=content,
            metadata=metadata or {},
            parent_id=parent_id,
            importance_score=importance,
        )

        # Calculate checksum for integrity
        node.checksum = self._calculate_checksum(content)

        # Add to storage
        self.nodes[node.node_id] = node
        self.tier_indices[tier].add(node.node_id)

        # Update parent-child relationships
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children_ids.append(node.node_id)
            self.parent_child_map[parent_id].add(node.node_id)

        # Update metrics
        self.metrics["total_nodes"] += 1

        # Check if compression needed
        if await self._should_compress(node):
            await self._compress_node(node)

        logger.info(
            "ΛHDS: Memory stored",
            node_id=node.node_id,
            tier=tier.value,
            parent_id=parent_id,
            importance=importance,
        )

        return node.node_id

    async def retrieve(self, context: RetrievalContext) -> list[MemoryNode]:
        """
        Retrieve memories based on context

        # Notes:
        - Uses hierarchical search with configurable depth
        - Applies importance and time filters
        - Includes cross-references if requested
        """
        results = []
        visited = set()

        # Start with tier-filtered nodes or all nodes
        start_nodes = self.tier_indices[context.tier_filter] if context.tier_filter else set(self.nodes.keys())

        # Apply filters and search
        for node_id in start_nodes:
            if node_id in visited:
                continue

            node = await self._get_node(node_id)
            if not node:
                continue

            # Apply filters
            if not self._matches_context(node, context):
                continue

            # Depth-first search with depth limit
            await self._dfs_collect(node, context, results, visited, 0)

            if len(results) >= context.max_results:
                break

        # Sort by relevance (importance * recency)
        results.sort(key=lambda n: n.importance_score * self._recency_factor(n), reverse=True)

        return results[: context.max_results]

    async def update_importance(self, node_id: str, delta: float):
        """Update the importance score of a memory"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]
        old_importance = node.importance_score
        node.importance_score = max(0.0, min(10.0, node.importance_score + delta))

        logger.debug(
            "ΛHDS: Importance updated",
            node_id=node_id,
            old=old_importance,
            new=node.importance_score,
        )

    async def add_cross_reference(self, node_id1: str, node_id2: str):
        """Create a cross-reference between two memory nodes"""
        if node_id1 in self.nodes and node_id2 in self.nodes:
            self.nodes[node_id1].cross_refs.add(node_id2)
            self.nodes[node_id2].cross_refs.add(node_id1)
            logger.debug("ΛHDS: Cross-reference added", node1=node_id1, node2=node_id2)

    async def get_hierarchy(self, root_id: str, max_depth: int = 3) -> dict[str, Any]:
        """Get hierarchical structure starting from a root node"""
        if root_id not in self.nodes:
            return {}

        def build_tree(node_id: str, depth: int) -> dict[str, Any]:
            if depth > max_depth or node_id not in self.nodes:
                return {}

            node = self.nodes[node_id]
            return {
                "id": node_id,
                "tier": node.tier.value,
                "importance": node.importance_score,
                "children": [build_tree(child_id, depth + 1) for child_id in node.children_ids],
            }

        return build_tree(root_id, 0)

    async def _get_node(self, node_id: str) -> Optional[MemoryNode]:
        """Get a node with caching and decompression"""
        if node_id not in self.nodes:
            return None

        node = self.nodes[node_id]

        # Update access metrics
        node.access_count += 1
        node.last_accessed = datetime.now(timezone.utc)
        self.metrics["total_accesses"] += 1

        # Check cache
        if node_id in self.access_cache:
            self.metrics["cache_hits"] += 1
            return self.access_cache[node_id]

        self.metrics["cache_misses"] += 1

        # Decompress if needed
        if node.is_compressed:
            await self._decompress_node(node)

        # Add to cache
        self.access_cache[node_id] = node

        return node

    async def _should_compress(self, node: MemoryNode) -> bool:
        """Determine if a node should be compressed"""
        # Don't compress recently accessed or high-importance nodes
        if node.importance_score > 5.0:
            return False

        age = (datetime.now(timezone.utc) - node.created_at).days
        recency = (datetime.now(timezone.utc) - node.last_accessed).days

        # Compress based on age and access patterns
        return (age > 7 and recency > 3) or (age > 30)

    async def _compress_node(self, node: MemoryNode):
        """Compress a memory node based on its tier"""
        if node.is_compressed:
            return

        original_size = len(str(node.content).encode())

        # Apply tier-specific compression
        if node.tier == MemoryTier.SENSORY:
            # Lossless compression for sensory data
            compressed = zlib.compress(json.dumps(node.content).encode(), level=9)
            node.compression_level = CompressionLevel.LOSSLESS

        elif node.tier == MemoryTier.EPISODIC:
            # Semantic compression - extract key events
            compressed = await self._semantic_compress(node.content)
            node.compression_level = CompressionLevel.SEMANTIC

        elif node.tier in [MemoryTier.SEMANTIC, MemoryTier.PROCEDURAL]:
            # Conceptual compression - abstract representation
            compressed = await self._conceptual_compress(node.content)
            node.compression_level = CompressionLevel.CONCEPTUAL

        else:  # META
            # Symbolic compression - highest abstraction
            compressed = await self._symbolic_compress(node.content)
            node.compression_level = CompressionLevel.SYMBOLIC

        # Store compressed data
        self.compression_cache[node.node_id] = compressed
        node.is_compressed = True
        node.content = None  # Clear original content

        # Update metrics
        self.metrics["compressed_nodes"] += 1
        compressed_size = len(compressed)
        ratio = compressed_size / original_size if original_size > 0 else 1.0
        self.metrics["compression_ratio"] = (
            self.metrics["compression_ratio"] * (self.metrics["compressed_nodes"] - 1) + ratio
        ) / self.metrics["compressed_nodes"]

        logger.debug(
            "ΛHDS: Node compressed",
            node_id=node.node_id,
            original_size=original_size,
            compressed_size=compressed_size,
            ratio=f"{ratio:.2%}",
        )

    async def _decompress_node(self, node: MemoryNode):
        """Decompress a memory node"""
        if not node.is_compressed or node.node_id not in self.compression_cache:
            return

        compressed_data = self.compression_cache[node.node_id]

        # Apply tier-specific decompression
        if node.compression_level == CompressionLevel.LOSSLESS:
            node.content = json.loads(zlib.decompress(compressed_data).decode())
        else:
            # For lossy compression, reconstruct from compressed form
            node.content = await self._reconstruct_from_compressed(compressed_data, node.compression_level)

        node.is_compressed = False

    async def _semantic_compress(self, content: Any) -> bytes:
        """Extract semantic meaning from content"""
        # Placeholder for semantic compression
        # In production, would use NLP models to extract key concepts
        summary = {
            "type": "semantic_summary",
            "key_concepts": str(content)[:100],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return json.dumps(summary).encode()

    async def _conceptual_compress(self, content: Any) -> bytes:
        """Extract conceptual abstractions"""
        # Placeholder for conceptual compression
        abstract = {
            "type": "conceptual_abstract",
            "concept": str(content)[:50],
            "relations": [],
        }
        return json.dumps(abstract).encode()

    async def _symbolic_compress(self, content: Any) -> bytes:
        """Create symbolic representation"""
        # Placeholder for symbolic compression
        symbol = {
            "type": "symbol",
            "id": hashlib.sha256(str(content).encode()).hexdigest()[:8],  # Changed from MD5 for security
        }
        return json.dumps(symbol).encode()

    async def _reconstruct_from_compressed(self, data: bytes, level: CompressionLevel) -> Any:
        """Reconstruct content from compressed form"""
        # Placeholder for reconstruction
        # In production, would use appropriate models/algorithms
        return json.loads(data.decode())

    def _matches_context(self, node: MemoryNode, context: RetrievalContext) -> bool:
        """Check if node matches retrieval context"""
        # Importance filter
        if node.importance_score < context.importance_threshold:
            return False

        # Time range filter
        if context.time_range:
            start, end = context.time_range
            if not (start <= node.created_at <= end):
                return False

        # Query matching (simple substring for now)
        if context.query:
            node_str = str(node.content).lower() + str(node.metadata).lower()
            if context.query.lower() not in node_str:
                return False

        return True

    async def _dfs_collect(
        self,
        node: MemoryNode,
        context: RetrievalContext,
        results: list[MemoryNode],
        visited: set[str],
        depth: int,
    ):
        """Depth-first search collection with context filtering"""
        if depth > context.max_depth or node.node_id in visited:
            return

        visited.add(node.node_id)

        if self._matches_context(node, context):
            results.append(node)

        # Explore children
        for child_id in node.children_ids:
            if child_id in self.nodes:
                child = await self._get_node(child_id)
                if child:
                    await self._dfs_collect(child, context, results, visited, depth + 1)

        # Explore cross-references if requested
        if context.include_cross_refs:
            for ref_id in node.cross_refs:
                if ref_id in self.nodes and ref_id not in visited:
                    ref_node = await self._get_node(ref_id)
                    if ref_node:
                        await self._dfs_collect(ref_node, context, results, visited, depth + 1)

    def _recency_factor(self, node: MemoryNode) -> float:
        """Calculate recency factor for ranking"""
        age_days = (datetime.now(timezone.utc) - node.last_accessed).days
        return 1.0 / (1.0 + age_days * node.decay_rate)

    def _calculate_checksum(self, content: Any) -> str:
        """Calculate content checksum for integrity verification"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def _prune_loop(self):
        """Background task for pruning low-importance memories"""
        while self._running:
            try:
                await asyncio.sleep(self.prune_interval)
                pruned = await self._prune_memories()
                if pruned > 0:
                    logger.info("ΛHDS: Pruned memories", count=pruned)
            except Exception as e:
                logger.error("ΛHDS: Pruning error", error=str(e))

    async def _prune_memories(self) -> int:
        """Prune low-importance, old memories"""
        pruned = 0
        current_time = datetime.now(timezone.utc)

        # Collect candidates for pruning
        candidates = []
        for node_id, node in self.nodes.items():
            # Skip important or recently accessed nodes
            if node.importance_score > 3.0 or node.access_count > 5:
                continue

            # Calculate pruning score
            age_days = (current_time - node.created_at).days
            access_days = (current_time - node.last_accessed).days
            prune_score = (age_days * access_days) / (node.importance_score * (node.access_count + 1))

            if prune_score > 1000:  # Threshold for pruning
                candidates.append((prune_score, node_id))

        # Sort by prune score and remove highest scoring (least valuable)
        candidates.sort(reverse=True)
        for _, node_id in candidates[:100]:  # Limit pruning per cycle
            await self._remove_node(node_id)
            pruned += 1

        self.metrics["pruned_nodes"] += pruned
        return pruned

    async def _remove_node(self, node_id: str):
        """Remove a node and clean up references"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

        # Remove from tier index
        self.tier_indices[node.tier].discard(node_id)

        # Update parent's children list
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            parent.children_ids.remove(node_id)
            self.parent_child_map[node.parent_id].discard(node_id)

        # Remove cross-references
        for ref_id in node.cross_refs:
            if ref_id in self.nodes:
                self.nodes[ref_id].cross_refs.discard(node_id)

        # Clean up caches
        self.access_cache.pop(node_id, None)
        self.compression_cache.pop(node_id, None)

        # Remove node
        del self.nodes[node_id]
        self.metrics["total_nodes"] -= 1

    async def _compression_loop(self):
        """Background task for compressing eligible memories"""
        while self._running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                compressed = await self._compress_eligible()
                if compressed > 0:
                    logger.info("ΛHDS: Compressed memories", count=compressed)
            except Exception as e:
                logger.error("ΛHDS: Compression error", error=str(e))

    async def _compress_eligible(self) -> int:
        """Compress eligible memories based on access patterns"""
        compressed = 0

        for node in self.nodes.values():
            if node.is_compressed:
                continue

            if await self._should_compress(node):
                await self._compress_node(node)
                compressed += 1

                if compressed >= 50:  # Limit per cycle
                    break

        return compressed

    async def flush_to_disk(self):
        """Persist current state to disk if storage path configured"""
        if not self.storage_path:
            return

        try:
            state = {
                "nodes": {
                    node_id: {
                        "tier": node.tier.value,
                        "metadata": node.metadata,
                        "parent_id": node.parent_id,
                        "children_ids": node.children_ids,
                        "cross_refs": list(node.cross_refs),
                        "importance_score": node.importance_score,
                        "access_count": node.access_count,
                        "compression_level": node.compression_level.value,
                        "is_compressed": node.is_compressed,
                        "checksum": node.checksum,
                        "created_at": node.created_at.isoformat(),
                        "last_accessed": node.last_accessed.isoformat(),
                    }
                    for node_id, node in self.nodes.items()
                },
                "compression_cache": {node_id: data.hex() for node_id, data in self.compression_cache.items()},
                "metrics": self.metrics,
            }

            # Write to temporary file first for atomicity
            temp_path = self.storage_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(state, f, indent=2)

            # Atomic rename
            temp_path.rename(self.storage_path)

            logger.info(
                "ΛHDS: State persisted to disk",
                path=str(self.storage_path),
                nodes=len(self.nodes),
            )

        except Exception as e:
            logger.error("ΛHDS: Failed to persist state", error=str(e))

    async def load_from_disk(self):
        """Load state from disk if available"""
        if not self.storage_path or not self.storage_path.exists():
            return

        try:
            with open(self.storage_path) as f:
                state = json.load(f)

            # Reconstruct nodes
            for node_id, node_data in state["nodes"].items():
                node = MemoryNode(
                    node_id=node_id,
                    tier=MemoryTier(node_data["tier"]),
                    metadata=node_data["metadata"],
                    parent_id=node_data["parent_id"],
                    children_ids=node_data["children_ids"],
                    cross_refs=set(node_data["cross_refs"]),
                    importance_score=node_data["importance_score"],
                    access_count=node_data["access_count"],
                    compression_level=CompressionLevel(node_data["compression_level"]),
                    is_compressed=node_data["is_compressed"],
                    checksum=node_data["checksum"],
                    created_at=datetime.fromisoformat(node_data["created_at"]),
                    last_accessed=datetime.fromisoformat(node_data["last_accessed"]),
                )
                self.nodes[node_id] = node
                self.tier_indices[node.tier].add(node_id)

                if node.parent_id:
                    self.parent_child_map[node.parent_id].add(node_id)

            # Restore compression cache
            self.compression_cache = {
                node_id: bytes.fromhex(data) for node_id, data in state["compression_cache"].items()
            }

            # Restore metrics
            self.metrics.update(state["metrics"])

            logger.info(
                "ΛHDS: State loaded from disk",
                path=str(self.storage_path),
                nodes=len(self.nodes),
            )

        except Exception as e:
            logger.error("ΛHDS: Failed to load state", error=str(e))

    # Collapse state management methods (Task 6 - Claude Code)
    async def update_collapse_state(
        self,
        node_id: str,
        collapse_trace_id: str,
        collapse_score: float,
        alert_level: str,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Update collapse state for a memory node

        Args:
            node_id: ID of the memory node
            collapse_trace_id: Trace ID from collapse tracker
            collapse_score: Current collapse/entropy score
            alert_level: Alert level (GREEN/YELLOW/ORANGE/RED)
            metadata: Additional collapse metadata
        """
        if node_id not in self.nodes:
            logger.warning("ΛHDS: Node not found for collapse update", node_id=node_id)
            return

        node = self.nodes[node_id]
        node.collapse_trace_id = collapse_trace_id
        node.collapse_alert_level = alert_level

        # Add to collapse score history
        node.collapse_score_history.append((datetime.now(timezone.utc), collapse_score))

        # Limit history size to prevent memory bloat
        if len(node.collapse_score_history) > 100:
            node.collapse_score_history = node.collapse_score_history[-100:]

        # Update metadata
        if metadata:
            node.collapse_metadata.update(metadata)

        logger.info(
            "ΛHDS: Collapse state updated",
            node_id=node_id,
            trace_id=collapse_trace_id,
            score=collapse_score,
            alert_level=alert_level,
        )

    async def get_collapse_affected_nodes(self, collapse_trace_id: str) -> list[MemoryNode]:
        """
        Get all nodes affected by a specific collapse event

        Args:
            collapse_trace_id: Collapse trace ID to search for

        Returns:
            List of affected memory nodes
        """
        affected_nodes = []

        for node in self.nodes.values():
            if node.collapse_trace_id == collapse_trace_id:
                affected_nodes.append(node)

        return affected_nodes

    async def get_high_risk_nodes(self, alert_threshold: str = "ORANGE") -> list[MemoryNode]:
        """
        Get nodes with high collapse risk

        Args:
            alert_threshold: Minimum alert level to include (YELLOW/ORANGE/RED)

        Returns:
            List of high-risk memory nodes
        """
        alert_levels = ["GREEN", "YELLOW", "ORANGE", "RED"]
        threshold_index = alert_levels.index(alert_threshold)

        high_risk_nodes = []

        for node in self.nodes.values():
            if node.collapse_alert_level:
                try:
                    node_level_index = alert_levels.index(node.collapse_alert_level)
                    if node_level_index >= threshold_index:
                        high_risk_nodes.append(node)
                except ValueError:
                    continue

        return high_risk_nodes

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive HDS status"""
        memory_usage_mb = (
            sum(len(str(node.content).encode()) for node in self.nodes.values() if node.content)
            + sum(len(data) for data in self.compression_cache.values())
        ) / (1024 * 1024)

        # Count collapse-affected nodes
        collapse_affected = sum(1 for node in self.nodes.values() if node.collapse_trace_id is not None)
        high_risk_count = len([n for n in self.nodes.values() if n.collapse_alert_level in ["ORANGE", "RED"]])

        return {
            "total_nodes": self.metrics["total_nodes"],
            "compressed_nodes": self.metrics["compressed_nodes"],
            "memory_usage_mb": round(memory_usage_mb, 2),
            "compression_ratio": f"{self.metrics['compression_ratio']:.2%}",
            "cache_hit_rate": f"{self.metrics['cache_hits'] / max(1, self.metrics['total_accesses']):.2%}",
            "tier_distribution": {tier.value: len(nodes) for tier, nodes in self.tier_indices.items()},
            "pruned_total": self.metrics["pruned_nodes"],
            # Collapse state metrics
            "collapse_affected_nodes": collapse_affected,
            "high_risk_nodes": high_risk_count,
        }


# Global HDS instance
_hds_instance: Optional[HierarchicalDataStore] = None


async def get_hds() -> HierarchicalDataStore:
    """Get the global Hierarchical Data Store instance"""
    global _hds_instance
    if _hds_instance is None:
        _hds_instance = HierarchicalDataStore()
        await _hds_instance.start()
    return _hds_instance


# ═══════════════════════════════════════════════════════════════════════════
# 📚 USER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# BASIC USAGE:
# -----------
# 1. Store a memory:
#    hds = await get_hds()
#    node_id = await hds.store(
#        content={"event": "User logged in", "user_id": "123"},
#        tier=MemoryTier.EPISODIC,
#        importance=2.5
#    )
#
# 2. Retrieve memories:
#    context = RetrievalContext(
#        query="user login",
#        tier_filter=MemoryTier.EPISODIC,
#        max_results=5
#    )
#    memories = await hds.retrieve(context)
#
# 3. Create hierarchies:
#    parent_id = await hds.store({"concept": "Animals"}, MemoryTier.SEMANTIC)
#    child_id = await hds.store(
#        {"concept": "Dogs"},
#        MemoryTier.SEMANTIC,
#        parent_id=parent_id
#    )
#
# 4. Cross-reference memories:
#    await hds.add_cross_reference(node_id1, node_id2)
#
# ═══════════════════════════════════════════════════════════════════════════
# 👨‍💻 DEVELOPER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# ARCHITECTURE:
# ------------
# - Tree-based hierarchy with parent-child relationships
# - Cross-references for non-hierarchical associations
# - Tiered storage with different compression strategies
# - Background tasks for maintenance (pruning, compression)
#
# EXTENSION POINTS:
# ----------------
# 1. Custom compression algorithms:
#    - Override _semantic_compress, _conceptual_compress methods
#    - Implement domain-specific compression strategies
#
# 2. Custom retrieval strategies:
#    - Extend RetrievalContext with new filters
#    - Override _matches_context for custom matching logic
#
# 3. Storage backends:
#    - Current implementation uses JSON file storage
#    - Can be extended to use databases, cloud storage, etc.
#
# PERFORMANCE TUNING:
# ------------------
# - Adjust compression_threshold based on memory/CPU tradeoff
# - Tune prune_interval for memory pressure
# - Configure max_memory_mb based on system resources
# - Use tier-specific caching strategies
#
# ═══════════════════════════════════════════════════════════════════════════
# 🎯 FINE-TUNING INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════
#
# FOR HIGH-THROUGHPUT SYSTEMS:
# ---------------------------
# - Increase cache sizes in access_cache
# - Reduce compression_threshold to 0.5
# - Use parallel retrieval with asyncio.gather
# - Implement sharding for nodes > 1M
#
# FOR MEMORY-CONSTRAINED SYSTEMS:
# ------------------------------
# - Reduce max_memory_mb to available RAM/4
# - Increase compression_threshold to 0.9
# - Reduce prune_interval to 600 seconds
# - Enable aggressive pruning (lower thresholds)
#
# FOR LONG-TERM STORAGE:
# ---------------------
# - Enable disk persistence with storage_path
# - Implement archival tiers beyond META
# - Use time-based partitioning for old memories
# - Integrate with external storage services
#
# ═══════════════════════════════════════════════════════════════════════════
# ❓ COMMON QUESTIONS & PROBLEMS
# ═══════════════════════════════════════════════════════════════════════════
#
# Q: Why are my memories being pruned too aggressively?
# A: Check importance scores - ensure critical memories have score > 3.0
#    Adjust pruning thresholds in _prune_memories method
#
# Q: How do I implement custom memory types?
# A: Add new MemoryTier enum values and corresponding compression strategies
#    Override _compress_node to handle new tiers appropriately
#
# Q: Can I use this with distributed systems?
# A: Yes, but requires:
#    - Distributed locking for write operations
#    - Consistent hashing for node distribution
#    - Replication for fault tolerance
#
# Q: How do I debug memory retrieval issues?
# A: Enable debug logging: logger.setLevel(logging.DEBUG)
#    Check tier_indices for proper categorization
#    Verify parent_child_map for hierarchy integrity
#
# Q: What's the maximum recommended hierarchy depth?
# A: Typically 5-7 levels for optimal performance
#    Deeper hierarchies increase retrieval time
#    Consider flattening or using cross-references
#
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: memory/core_memory/hierarchical_data_store.py
# VERSION: v1.0.0
# SYMBOLIC TAGS: ΛHDS, ΛMEMORY, ΛHIERARCHY, ΛSTORAGE, ΛCOMPRESSION
# CLASSES: HierarchicalDataStore, MemoryNode, RetrievalContext
# FUNCTIONS: get_hds, store, retrieve, add_cross_reference
# LOGGER: structlog (UTC)
# INTEGRATION: Fold Memory, MEG, SRD
# ═══════════════════════════════════════════════════════════════════════════