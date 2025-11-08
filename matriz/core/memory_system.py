#!/usr/bin/env python3
"""
MATRIZ Memory System

A comprehensive memory system for the MATRIZ-AGI architecture that provides:
- Context buffer for recent interactions and short-term memory
- Episodic memory for query-response pairs and experiences
- Semantic memory for knowledge graph and long-term concepts
- Working memory management with capacity limits
- Memory decay and consolidation mechanisms
- Full integration with MATRIZ nodes and provenance tracking
- Production-ready implementation with comprehensive error handling

This memory system follows the MATRIZ principles:
- Every memory operation creates traceable MATRIZ nodes
- Complete provenance tracking for governance
- Deterministic behavior for reproducibility
- Confidence and salience scoring for memory importance
"""

import hashlib
import json
import threading
import time
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import lz4.frame
from matriz.core.node_interface import (
    CognitiveNode,
    NodeState,
    NodeTrigger,
)


class MemoryType(Enum):
    """Types of memory supported by the system"""

    CONTEXT = "context"  # Short-term context buffer
    EPISODIC = "episodic"  # Query-response experiences
    SEMANTIC = "semantic"  # Knowledge and concepts
    WORKING = "working"  # Active processing memory
    CONSOLIDATED = "consolidated"  # Long-term consolidated memory


class MemoryPriority(Enum):
    """Priority levels for memory items"""

    CRITICAL = "critical"  # Must not be forgotten (confidence > 0.9)
    HIGH = "high"  # Important (confidence > 0.7)
    MEDIUM = "medium"  # Standard (confidence > 0.5)
    LOW = "low"  # Can be forgotten easily (confidence <= 0.5)


@dataclass
class MemoryItem:
    """Individual memory item with metadata"""

    id: str
    memory_type: MemoryType
    content: Any  # Can be dict (uncompressed) or bytes (compressed)
    confidence: float
    salience: float
    priority: MemoryPriority
    created_timestamp: int
    last_accessed: int
    access_count: int = 0
    decay_rate: float = 0.01
    associated_node_ids: list[str] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    context: dict[str, Any] = field(default_factory=dict)
    compressed: bool = False


@dataclass
class ConsolidationRule:
    """Rules for memory consolidation"""

    min_access_count: int = 3
    min_confidence: float = 0.6
    time_window_hours: int = 24
    similarity_threshold: float = 0.8
    priority_boost: float = 0.1


@dataclass
class MemoryQuery:
    """Query structure for memory retrieval"""

    query_text: Optional[str] = None
    memory_types: Optional[list[MemoryType]] = None
    tags: Optional[set[str]] = None
    time_range: Optional[tuple[int, int]] = None
    min_confidence: float = 0.0
    min_salience: float = 0.0
    limit: int = 10
    similarity_search: bool = True


class MemorySystem(CognitiveNode):
    """
    Production-ready memory system for MATRIZ-AGI.

    Features:
    - Multiple memory types (context, episodic, semantic, working)
    - Automatic memory decay and consolidation
    - Similarity-based retrieval with semantic search
    - Capacity management with intelligent eviction
    - MATRIZ node integration for full traceability
    - Thread-safe operations for concurrent access
    - Configurable parameters for different use cases

    Memory Architecture:
    - Context Buffer: Recent interactions (sliding window)
    - Episodic Memory: Query-response pairs with experiences
    - Semantic Memory: Knowledge graph and concepts
    - Working Memory: Active processing items (limited capacity)
    - Consolidated Memory: Important long-term memories
    """

    def __init__(
        self,
        tenant: str = "default",
        context_buffer_size: int = 100,
        working_memory_size: int = 20,
        episodic_memory_size: int = 1000,
        semantic_memory_size: int = 5000,
        decay_enabled: bool = True,
        consolidation_enabled: bool = True,
        persistence_path: Optional[str] = None,
    ):
        """
        Initialize the memory system.

        Args:
            tenant: Tenant identifier for multi-tenancy
            context_buffer_size: Maximum items in context buffer
            working_memory_size: Maximum items in working memory
            episodic_memory_size: Maximum items in episodic memory
            semantic_memory_size: Maximum items in semantic memory
            decay_enabled: Whether to enable automatic memory decay
            consolidation_enabled: Whether to enable memory consolidation
            persistence_path: Optional path for memory persistence
        """
        super().__init__(
            node_name="matriz_memory_system",
            capabilities=[
                "context_buffering",
                "episodic_memory",
                "semantic_memory",
                "working_memory",
                "memory_consolidation",
                "memory_retrieval",
                "similarity_search",
                "memory_decay",
                "provenance_tracking",
            ],
            tenant=tenant,
        )

        # Memory storage by type
        self.context_buffer: deque = deque(maxlen=context_buffer_size)
        self.working_memory: dict[str, MemoryItem] = {}
        self.episodic_memory: dict[str, MemoryItem] = {}
        self.semantic_memory: dict[str, MemoryItem] = {}
        self.consolidated_memory: dict[str, MemoryItem] = {}

        # Configuration
        self.context_buffer_size = context_buffer_size
        self.working_memory_size = working_memory_size
        self.episodic_memory_size = episodic_memory_size
        self.semantic_memory_size = semantic_memory_size
        self.decay_enabled = decay_enabled
        self.consolidation_enabled = consolidation_enabled
        self.persistence_path = persistence_path

        # Memory management
        self.consolidation_rules = ConsolidationRule()
        self.last_consolidation = time.time()
        self.last_decay = time.time()
        self._lock = threading.RLock()  # Thread safety

        # Statistics and metrics
        self.stats = {
            "total_stores": 0,
            "total_retrievals": 0,
            "cache_hits": 0,
            "consolidations": 0,
            "decays": 0,
            "evictions": 0,
        }

        # Load persisted memories if path provided
        if self.persistence_path:
            self._load_memories()

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process memory operations (store, retrieve, consolidate, etc.).

        Args:
            input_data: Dict containing:
                - 'operation': Memory operation ('store', 'retrieve', 'consolidate', 'decay')
                - 'memory_type': Type of memory to operate on
                - 'content': Content to store (for store operations)
                - 'query': Query for retrieval operations
                - 'trace_id': Optional execution trace ID

        Returns:
            Dict containing:
                - 'result': Operation result
                - 'confidence': Confidence in the operation
                - 'matriz_node': Complete MATRIZ format node
                - 'processing_time': Processing duration in seconds
        """
        start_time = time.time()

        operation = input_data.get("operation", "").strip().lower()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        # Create initial trigger
        trigger = NodeTrigger(
            event_type=f"memory_{operation}_request",
            timestamp=int(time.time() * 1000),
            effect="memory_system_operation",
        )

        if not operation:
            return self._create_error_response(
                "No memory operation specified",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

        try:
            # Route to appropriate operation
            if operation == "store":
                result = self._handle_store_operation(input_data, trace_id, [trigger])
            elif operation == "retrieve":
                result = self._handle_retrieve_operation(input_data, trace_id, [trigger])
            elif operation == "consolidate":
                result = self._handle_consolidate_operation(input_data, trace_id, [trigger])
            elif operation == "decay":
                result = self._handle_decay_operation(input_data, trace_id, [trigger])
            elif operation == "stats":
                result = self._handle_stats_operation(input_data, trace_id, [trigger])
            else:
                return self._create_error_response(
                    f"Unknown memory operation: {operation}",
                    input_data,
                    trace_id,
                    start_time,
                    [trigger],
                )

            processing_time = time.time() - start_time
            result["processing_time"] = processing_time

            return result

        except Exception as e:
            return self._create_error_response(
                f"Memory operation failed: {e!s}",
                input_data,
                trace_id,
                start_time,
                [trigger],
            )

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate memory system output.

        Args:
            output: Output from process() method

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ["result", "confidence", "matriz_node", "processing_time"]
            for name in required_fields:
                if name not in output:
                    return False

            # Validate types
            if not isinstance(output["confidence"], (int, float)):
                return False
            if not isinstance(output["processing_time"], (int, float)):
                return False

            # Validate confidence range
            confidence = output["confidence"]
            if not (0 <= confidence <= 1):
                return False

            # Validate MATRIZ node
            matriz_node = output["matriz_node"]
            if not self.validate_matriz_node(matriz_node):
                return False

            # Check node type is MEMORY
            return matriz_node.get("type") == "MEMORY"

        except Exception:
            return False

    def store_memory(
        self,
        content: dict[str, Any],
        memory_type: MemoryType,
        confidence: float = 0.8,
        salience: float = 0.7,
        tags: Optional[set[str]] = None,
        context: Optional[dict[str, Any]] = None,
        compress: bool = True,
    ) -> str:
        """
        Store a memory item.

        Args:
            content: Memory content to store
            memory_type: Type of memory
            confidence: Confidence in this memory (0.0-1.0)
            salience: Importance/salience of this memory (0.0-1.0)
            tags: Optional tags for categorization
            context: Optional additional context

        Returns:
            Memory item ID
        """
        with self._lock:
            memory_id = str(uuid.uuid4())
            current_time = int(time.time() * 1000)

            # Determine priority based on confidence
            if confidence > 0.9:
                priority = MemoryPriority.CRITICAL
            elif confidence > 0.7:
                priority = MemoryPriority.HIGH
            elif confidence > 0.5:
                priority = MemoryPriority.MEDIUM
            else:
                priority = MemoryPriority.LOW

            # Compress content if specified
            is_compressed = False
            if compress:
                try:
                    content_bytes = json.dumps(content).encode("utf-8")
                    content = lz4.frame.compress(content_bytes)
                    is_compressed = True
                except Exception:
                    # If compression fails, store uncompressed
                    pass

            memory_item = MemoryItem(
                id=memory_id,
                memory_type=memory_type,
                content=content,
                confidence=confidence,
                salience=salience,
                compressed=is_compressed,
                priority=priority,
                created_timestamp=current_time,
                last_accessed=current_time,
                tags=tags or set(),
                context=context or {},
            )

            # Store in appropriate memory store
            if memory_type == MemoryType.CONTEXT:
                self.context_buffer.append(memory_item)
            elif memory_type == MemoryType.WORKING:
                self._store_in_working_memory(memory_item)
            elif memory_type == MemoryType.EPISODIC:
                self._store_in_episodic_memory(memory_item)
            elif memory_type == MemoryType.SEMANTIC:
                self._store_in_semantic_memory(memory_item)
            elif memory_type == MemoryType.CONSOLIDATED:
                self.consolidated_memory[memory_id] = memory_item

            self.stats["total_stores"] += 1

            # Trigger automatic maintenance if needed
            if self.decay_enabled:
                self._maybe_trigger_decay()
            if self.consolidation_enabled:
                self._maybe_trigger_consolidation()

            return memory_id

    def retrieve_memories(self, query: MemoryQuery) -> list[MemoryItem]:
        """
        Retrieve memories based on query criteria.

        Args:
            query: Memory query with search criteria

        Returns:
            List of matching memory items, sorted by relevance
        """
        with self._lock:
            all_memories = []

            # Collect memories from requested types
            memory_types = query.memory_types or list(MemoryType)

            for memory_type in memory_types:
                if memory_type == MemoryType.CONTEXT:
                    all_memories.extend(self.context_buffer)
                elif memory_type == MemoryType.WORKING:
                    all_memories.extend(self.working_memory.values())
                elif memory_type == MemoryType.EPISODIC:
                    all_memories.extend(self.episodic_memory.values())
                elif memory_type == MemoryType.SEMANTIC:
                    all_memories.extend(self.semantic_memory.values())
                elif memory_type == MemoryType.CONSOLIDATED:
                    all_memories.extend(self.consolidated_memory.values())

            # Apply filters
            filtered_memories = self._filter_memories(all_memories, query)

        # Decompress content before returning
        for memory in filtered_memories:
            memory.content = self.decompress_content(memory)

        # Update access statistics
            for memory in filtered_memories:
                memory.last_accessed = int(time.time() * 1000)
                memory.access_count += 1

            self.stats["total_retrievals"] += 1
            if filtered_memories:
                self.stats["cache_hits"] += 1

            return filtered_memories[: query.limit]

    def decompress_content(self, memory_item: MemoryItem) -> dict[str, Any]:
        """Decompress memory content if it is compressed."""
        if not memory_item.compressed:
            return memory_item.content

        try:
            decompressed_bytes = lz4.frame.decompress(memory_item.content)
            return json.loads(decompressed_bytes.decode("utf-8"))
        except Exception:
            # Return raw content if decompression fails
            return {"error": "decompression_failed", "raw_content": memory_item.content}

    def consolidate_memories(self) -> int:
        """
        Consolidate memories based on consolidation rules.

        Returns:
            Number of memories consolidated
        """
        with self._lock:
            consolidation_count = 0
            current_time = int(time.time() * 1000)
            time_window = self.consolidation_rules.time_window_hours * 3600 * 1000

            # Find candidates for consolidation from episodic and working memory
            candidates = []

            for memory in list(self.episodic_memory.values()) + list(self.working_memory.values()):
                if (
                    memory.access_count >= self.consolidation_rules.min_access_count
                    and memory.confidence >= self.consolidation_rules.min_confidence
                    and current_time - memory.created_timestamp >= time_window
                ):
                    candidates.append(memory)

            # Consolidate candidates
            for memory in candidates:
                # Boost priority and confidence for consolidation
                memory.confidence = min(
                    1.0, memory.confidence + self.consolidation_rules.priority_boost
                )
                memory.salience = min(
                    1.0, memory.salience + self.consolidation_rules.priority_boost
                )

                # Move to consolidated memory
                self.consolidated_memory[memory.id] = memory

                # Remove from original location
                if memory.id in self.working_memory:
                    del self.working_memory[memory.id]
                if memory.id in self.episodic_memory:
                    del self.episodic_memory[memory.id]

                consolidation_count += 1

            self.stats["consolidations"] += consolidation_count
            self.last_consolidation = time.time()

            return consolidation_count

    def decay_memories(self) -> int:
        """
        Apply decay to memories based on time and access patterns.

        Returns:
            Number of memories that were decayed or removed
        """
        with self._lock:
            decay_count = 0
            current_time = int(time.time() * 1000)

            # Decay memories in all stores except consolidated
            memory_stores = [
                (self.working_memory, "working"),
                (self.episodic_memory, "episodic"),
                (self.semantic_memory, "semantic"),
            ]

            for store, _store_name in memory_stores:
                to_remove = []

                for memory_id, memory in store.items():
                    # Calculate time-based decay
                    time_since_access = current_time - memory.last_accessed
                    hours_since_access = time_since_access / (1000 * 3600)

                    # Apply decay based on time and access pattern
                    decay_factor = memory.decay_rate * hours_since_access

                    # Reduce confidence and salience
                    memory.confidence = max(0.0, memory.confidence - decay_factor)
                    memory.salience = max(0.0, memory.salience - decay_factor * 0.5)

                    # Remove if confidence drops too low (unless critical priority)
                    if memory.confidence < 0.1 and memory.priority != MemoryPriority.CRITICAL:
                        to_remove.append(memory_id)

                # Remove decayed memories
                for memory_id in to_remove:
                    del store[memory_id]
                    decay_count += 1

            self.stats["decays"] += decay_count
            self.last_decay = time.time()

            return decay_count

    def get_memory_stats(self) -> dict[str, Any]:
        """
        Get comprehensive memory system statistics.

        Returns:
            Dictionary with memory statistics
        """
        with self._lock:
            return {
                "memory_counts": {
                    "context": len(self.context_buffer),
                    "working": len(self.working_memory),
                    "episodic": len(self.episodic_memory),
                    "semantic": len(self.semantic_memory),
                    "consolidated": len(self.consolidated_memory),
                },
                "capacity_limits": {
                    "context": self.context_buffer_size,
                    "working": self.working_memory_size,
                    "episodic": self.episodic_memory_size,
                    "semantic": self.semantic_memory_size,
                },
                "utilization": {
                    "context": len(self.context_buffer) / self.context_buffer_size,
                    "working": len(self.working_memory) / self.working_memory_size,
                    "episodic": len(self.episodic_memory) / self.episodic_memory_size,
                    "semantic": len(self.semantic_memory) / self.semantic_memory_size,
                },
                "operations": self.stats.copy(),
                "last_maintenance": {
                    "consolidation": self.last_consolidation,
                    "decay": self.last_decay,
                },
            }

    def clear_memory_type(self, memory_type: MemoryType) -> int:
        """
        Clear all memories of a specific type.

        Args:
            memory_type: Type of memory to clear

        Returns:
            Number of memories cleared
        """
        with self._lock:
            count = 0

            if memory_type == MemoryType.CONTEXT:
                count = len(self.context_buffer)
                self.context_buffer.clear()
            elif memory_type == MemoryType.WORKING:
                count = len(self.working_memory)
                self.working_memory.clear()
            elif memory_type == MemoryType.EPISODIC:
                count = len(self.episodic_memory)
                self.episodic_memory.clear()
            elif memory_type == MemoryType.SEMANTIC:
                count = len(self.semantic_memory)
                self.semantic_memory.clear()
            elif memory_type == MemoryType.CONSOLIDATED:
                count = len(self.consolidated_memory)
                self.consolidated_memory.clear()

            return count

    def _store_in_working_memory(self, memory_item: MemoryItem) -> None:
        """Store item in working memory with capacity management."""
        if len(self.working_memory) >= self.working_memory_size:
            self._evict_from_working_memory()

        self.working_memory[memory_item.id] = memory_item

    def _store_in_episodic_memory(self, memory_item: MemoryItem) -> None:
        """Store item in episodic memory with capacity management."""
        if len(self.episodic_memory) >= self.episodic_memory_size:
            self._evict_from_episodic_memory()

        self.episodic_memory[memory_item.id] = memory_item

    def _store_in_semantic_memory(self, memory_item: MemoryItem) -> None:
        """Store item in semantic memory with capacity management."""
        if len(self.semantic_memory) >= self.semantic_memory_size:
            self._evict_from_semantic_memory()

        self.semantic_memory[memory_item.id] = memory_item

    def _evict_from_working_memory(self) -> None:
        """Evict least important items from working memory."""
        if not self.working_memory:
            return

        # Sort by importance (confidence * salience) and recency
        items = list(self.working_memory.values())
        items.sort(key=lambda m: (m.confidence * m.salience, m.last_accessed, m.priority.value))

        # Remove the least important item
        least_important = items[0]
        del self.working_memory[least_important.id]
        self.stats["evictions"] += 1

    def _evict_from_episodic_memory(self) -> None:
        """Evict least important items from episodic memory."""
        if not self.episodic_memory:
            return

        items = list(self.episodic_memory.values())
        items.sort(key=lambda m: (m.confidence * m.salience, m.access_count, m.last_accessed))

        least_important = items[0]
        del self.episodic_memory[least_important.id]
        self.stats["evictions"] += 1

    def _evict_from_semantic_memory(self) -> None:
        """Evict least important items from semantic memory."""
        if not self.semantic_memory:
            return

        items = list(self.semantic_memory.values())
        items.sort(
            key=lambda m: (
                m.confidence * m.salience * (1 + m.access_count),
                m.last_accessed,
            )
        )

        least_important = items[0]
        del self.semantic_memory[least_important.id]
        self.stats["evictions"] += 1

    def _filter_memories(self, memories: list[MemoryItem], query: MemoryQuery) -> list[MemoryItem]:
        """Filter memories based on query criteria."""
        filtered = []

        for memory in memories:
            # Apply filters
            if memory.confidence < query.min_confidence:
                continue
            if memory.salience < query.min_salience:
                continue

            # Time range filter
            if query.time_range:
                start_time, end_time = query.time_range
                if not (start_time <= memory.created_timestamp <= end_time):
                    continue

            # Tag filter
            if query.tags and not query.tags.intersection(memory.tags):
                continue

            # Text similarity filter
            if query.query_text and query.similarity_search:
                content = self.decompress_content(memory)
                similarity = self._calculate_similarity(query.query_text, content)
                if similarity < 0.3:  # Minimum similarity threshold
                    continue

            filtered.append(memory)

        # Sort by relevance (combination of confidence, salience, recency, and similarity)
        filtered.sort(
            key=lambda m: (m.confidence * m.salience, m.last_accessed, m.access_count),
            reverse=True,
        )

        return filtered

    def _calculate_similarity(self, query_text: str, content: dict[str, Any]) -> float:
        """Calculate similarity between query text and memory content."""
        # Simple similarity based on text overlap
        # In production, this could use embeddings or more sophisticated methods

        content_text = str(content).lower()
        query_text = query_text.lower()

        # Word overlap similarity
        query_words = set(query_text.split())
        content_words = set(content_text.split())

        if not query_words:
            return 0.0

        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)

        if not union:
            return 0.0

        jaccard_similarity = len(intersection) / len(union)

        # Boost similarity if query text is substring of content
        if query_text in content_text:
            jaccard_similarity += 0.3

        return min(1.0, jaccard_similarity)

    def _maybe_trigger_decay(self) -> None:
        """Trigger decay if enough time has passed."""
        if time.time() - self.last_decay > 3600:  # Every hour
            self.decay_memories()

    def _maybe_trigger_consolidation(self) -> None:
        """Trigger consolidation if enough time has passed."""
        if time.time() - self.last_consolidation > 86400:  # Every day
            self.consolidate_memories()

    def _handle_store_operation(
        self, input_data: dict[str, Any], trace_id: str, triggers: list[NodeTrigger]
    ) -> dict[str, Any]:
        """Handle memory store operations."""
        content = input_data.get("content", {})
        memory_type_str = input_data.get("memory_type", "episodic")
        confidence = input_data.get("confidence", 0.8)
        salience = input_data.get("salience", 0.7)
        tags = set(input_data.get("tags", []))
        context = input_data.get("context", {})

        try:
            memory_type = MemoryType(memory_type_str)
        except ValueError:
            memory_type = MemoryType.EPISODIC

        memory_id = self.store_memory(content, memory_type, confidence, salience, tags, context)

        # Create success state
        state = NodeState(confidence=0.95, salience=0.8, valence=0.7, utility=0.9)

        reflection = self.create_reflection(
            reflection_type="affirmation",
            cause=f"Successfully stored {memory_type.value} memory",
            new_state={"memory_id": memory_id, "memory_type": memory_type.value},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "operation": "store",
                "memory_id": memory_id,
                "memory_type": memory_type.value,
                "content_hash": hashlib.sha256(str(content).encode()).hexdigest()[:16],
            },
        )

        return {
            "result": {"memory_id": memory_id, "status": "stored"},
            "confidence": 0.95,
            "matriz_node": matriz_node,
        }

    def _handle_retrieve_operation(
        self, input_data: dict[str, Any], trace_id: str, triggers: list[NodeTrigger]
    ) -> dict[str, Any]:
        """Handle memory retrieval operations."""
        query_dict = input_data.get("query", {})

        # Build memory query
        memory_query = MemoryQuery(
            query_text=query_dict.get("text"),
            memory_types=[
                MemoryType(t) for t in query_dict.get("types", [MemoryType.EPISODIC.value])
            ],
            tags=set(query_dict.get("tags", [])),
            min_confidence=query_dict.get("min_confidence", 0.0),
            min_salience=query_dict.get("min_salience", 0.0),
            limit=query_dict.get("limit", 10),
        )

        memories = self.retrieve_memories(memory_query)

        # Convert memories to serializable format
        result_memories = []
        for memory in memories:
            result_memories.append(
                {
                    "id": memory.id,
                    "content": self.decompress_content(memory),
                    "confidence": memory.confidence,
                    "salience": memory.salience,
                    "memory_type": memory.memory_type.value,
                    "created_timestamp": memory.created_timestamp,
                    "access_count": memory.access_count,
                    "tags": list(memory.tags),
                }
            )

        confidence = 0.9 if memories else 0.3

        state = NodeState(
            confidence=confidence,
            salience=0.8,
            valence=0.5 if memories else -0.2,
            utility=0.8 if memories else 0.2,
        )

        reflection = self.create_reflection(
            reflection_type="affirmation" if memories else "regret",
            cause=f"Retrieved {len(memories)} memories",
            new_state={"memory_count": len(memories)},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "operation": "retrieve",
                "query": query_dict,
                "results_count": len(memories),
            },
        )

        return {
            "result": {"memories": result_memories, "count": len(memories)},
            "confidence": confidence,
            "matriz_node": matriz_node,
        }

    def _handle_consolidate_operation(
        self, input_data: dict[str, Any], trace_id: str, triggers: list[NodeTrigger]
    ) -> dict[str, Any]:
        """Handle memory consolidation operations."""
        consolidated_count = self.consolidate_memories()

        state = NodeState(confidence=0.9, salience=0.7, valence=0.6, utility=0.8)

        reflection = self.create_reflection(
            reflection_type="affirmation",
            cause=f"Consolidated {consolidated_count} memories",
            new_state={"consolidated_count": consolidated_count},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "operation": "consolidate",
                "consolidated_count": consolidated_count,
            },
        )

        return {
            "result": {"consolidated_count": consolidated_count},
            "confidence": 0.9,
            "matriz_node": matriz_node,
        }

    def _handle_decay_operation(
        self, input_data: dict[str, Any], trace_id: str, triggers: list[NodeTrigger]
    ) -> dict[str, Any]:
        """Handle memory decay operations."""
        decayed_count = self.decay_memories()

        state = NodeState(confidence=0.9, salience=0.6, valence=0.4, utility=0.7)

        reflection = self.create_reflection(
            reflection_type="affirmation",
            cause=f"Applied decay to {decayed_count} memories",
            new_state={"decayed_count": decayed_count},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={"operation": "decay", "decayed_count": decayed_count},
        )

        return {
            "result": {"decayed_count": decayed_count},
            "confidence": 0.9,
            "matriz_node": matriz_node,
        }

    def _handle_stats_operation(
        self, input_data: dict[str, Any], trace_id: str, triggers: list[NodeTrigger]
    ) -> dict[str, Any]:
        """Handle memory statistics operations."""
        stats = self.get_memory_stats()

        state = NodeState(confidence=1.0, salience=0.6, valence=0.5, utility=0.8)

        reflection = self.create_reflection(
            reflection_type="affirmation",
            cause="Retrieved memory system statistics",
            new_state={"total_memories": sum(stats["memory_counts"].values())},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={"operation": "stats", "stats": stats},
        )

        return {"result": stats, "confidence": 1.0, "matriz_node": matriz_node}

    def _create_error_response(
        self,
        error_message: str,
        input_data: dict[str, Any],
        trace_id: str,
        start_time: float,
        triggers: list[NodeTrigger],
    ) -> dict[str, Any]:
        """Create standardized error response with MATRIZ node."""
        confidence = 0.1

        state = NodeState(confidence=confidence, salience=0.3, valence=-0.6, risk=0.8, utility=0.1)

        reflection = self.create_reflection(
            reflection_type="regret",
            cause=f"Memory operation failed: {error_message}",
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "operation": "error",
                "error": error_message,
                "input_data": input_data,
            },
        )

        processing_time = time.time() - start_time

        return {
            "result": {"error": error_message},
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def _load_memories(self) -> None:
        """Load persisted memories from file."""
        if not self.persistence_path:
            return

        try:
            persistence_file = Path(self.persistence_path)
            if persistence_file.exists():
                with open(persistence_file) as f:
                    data = json.load(f)

                # Load memories into appropriate stores
                for memory_data in data.get("memories", []):
                    # Convert string representations back to enums before creating the MemoryItem
                    if "memory_type" in memory_data and isinstance(memory_data["memory_type"], str):
                        memory_data["memory_type"] = MemoryType(memory_data["memory_type"])
                    if "priority" in memory_data and isinstance(memory_data["priority"], str):
                        memory_data["priority"] = MemoryPriority(memory_data["priority"])

                    memory_item = MemoryItem(**memory_data)
                    memory_type = memory_item.memory_type

                    if memory_type == MemoryType.WORKING:
                        self.working_memory[memory_item.id] = memory_item
                    elif memory_type == MemoryType.EPISODIC:
                        self.episodic_memory[memory_item.id] = memory_item
                    elif memory_type == MemoryType.SEMANTIC:
                        self.semantic_memory[memory_item.id] = memory_item
                    elif memory_type == MemoryType.CONSOLIDATED:
                        self.consolidated_memory[memory_item.id] = memory_item

                # Load statistics
                self.stats.update(data.get("stats", {}))

        except Exception as e:
            print(f"Warning: Failed to load memories from {self.persistence_path}: {e}")

    def _save_memories(self) -> None:
        """Save memories to persistence file."""
        if not self.persistence_path:
            return

        try:
            all_memories = []

            # Collect all memories
            for memory in self.working_memory.values():
                all_memories.append(asdict(memory))
            for memory in self.episodic_memory.values():
                all_memories.append(asdict(memory))
            for memory in self.semantic_memory.values():
                all_memories.append(asdict(memory))
            for memory in self.consolidated_memory.values():
                all_memories.append(asdict(memory))

            # Convert sets to lists for JSON serialization
            for memory_data in all_memories:
                if isinstance(memory_data.get("tags"), set):
                    memory_data["tags"] = list(memory_data["tags"])
                if isinstance(memory_data.get("memory_type"), MemoryType):
                    memory_data["memory_type"] = memory_data["memory_type"].value
                if isinstance(memory_data.get("priority"), MemoryPriority):
                    memory_data["priority"] = memory_data["priority"].value

            data = {
                "memories": all_memories,
                "stats": self.stats,
                "timestamp": int(time.time() * 1000),
            }

            persistence_file = Path(self.persistence_path)
            persistence_file.parent.mkdir(parents=True, exist_ok=True)

            with open(persistence_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save memories to {self.persistence_path}: {e}")

    def __del__(self):
        """Save memories on destruction if persistence is enabled."""
        if hasattr(self, "persistence_path") and self.persistence_path:
            self._save_memories()
