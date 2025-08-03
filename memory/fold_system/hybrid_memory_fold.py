#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: hybrid_memory_fold.py
║ Path: memory/systems/hybrid_memory_fold.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🧬 LUKHAS AI - HYBRID MEMORY FOLD SYSTEM                                   ║
║ ║ Neural-Symbolic Memory with Vector Embeddings & Attention                  ║
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.                         ║
║ ╠══════════════════════════════════════════════════════════════════════════════╣
║ ║ Module: hybrid_memory_fold.py                                               ║
║ ║ Path: memory/systems/hybrid_memory_fold.py                                  ║
║ ║ Version: 2.0.0 | Created: 2025-07-29                                       ║
║ ║ Authors: LUKHAS AI Architecture Team                                        ║
║ ╠══════════════════════════════════════════════════════════════════════════════╣
║ ║                         🌀 HARMONIOUS CONFLUENCE OF MEMORY                  ║
║ ║                A CHOREOGRAPHY OF SYNAPSES AND SYMBOLS IN THE DIGITAL AGE   ║
║ ╠══════════════════════════════════════════════════════════════════════════════╣
║ ║ In the realm where silicon dreams intertwine with the tapestry of thought,   ║
║ ║ the Hybrid Memory Fold emerges as a luminary beacon, illuminating the       ║
║ ║ labyrinthine pathways of cognition. Here, within the sacred halls of        ║
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
import numpy as np
import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict
import structlog

# Base memory fold system
from .memory_fold_system import MemoryFoldSystem, MemoryItem, TagInfo

# Neural components (stubbed for now - would use PyTorch/TensorFlow in production)
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Stub implementations for demo
    class nn:
        class Module: pass
        class Linear:
            def __init__(self, *args): pass
        class MultiheadAttention:
            def __init__(self, *args, **kwargs): pass

from core.common import get_logger


@dataclass
class HybridMemoryItem(MemoryItem):
    """Extended memory item with vector embeddings"""
    # Vector representations
    text_embedding: Optional[np.ndarray] = None
    image_embedding: Optional[np.ndarray] = None
    audio_embedding: Optional[np.ndarray] = None
    unified_embedding: Optional[np.ndarray] = None

    # Attention weights
    importance_score: float = 1.0
    attention_weights: Dict[str, float] = field(default_factory=dict)

    # Learning metadata
    usage_count: int = 0
    last_used: Optional[datetime] = None
    td_error: Optional[float] = None  # For prioritized replay

    # Causal relationships
    causes: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    causal_strength: Dict[str, float] = field(default_factory=dict)


class VectorStorageLayer:
    """High-performance vector storage with multiple index types"""

    def __init__(self, dimension: int = 1024):
        self.dimension = dimension
        self.vectors = {}  # memory_id -> vector

        # In production, would use Faiss, Annoy, or similar
        # For now, simple numpy arrays
        self.vector_matrix = None
        self.id_to_index = {}
        self.index_to_id = {}
        self.next_index = 0

    def add_vector(self, memory_id: str, vector: np.ndarray):
        """Add vector to storage"""
        if memory_id in self.vectors:
            # Update existing
            idx = self.id_to_index[memory_id]
            if self.vector_matrix is not None:
                self.vector_matrix[idx] = vector
        else:
            # Add new
            self.vectors[memory_id] = vector
            self.id_to_index[memory_id] = self.next_index
            self.index_to_id[self.next_index] = memory_id
            self.next_index += 1

            # Rebuild matrix
            self._rebuild_matrix()

    def search_similar(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """Find similar vectors using cosine similarity"""
        if self.vector_matrix is None or len(self.vectors) == 0:
            return []

        # Normalize query
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)

        # Compute similarities
        similarities = np.dot(self.vector_matrix, query_norm)

        # Get top-k
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            sim = similarities[idx]
            if sim >= threshold:
                memory_id = self.index_to_id[idx]
                results.append((memory_id, float(sim)))

        return results

    def _rebuild_matrix(self):
        """Rebuild vector matrix for efficient search"""
        if not self.vectors:
            self.vector_matrix = None
            return

        # Stack vectors into matrix
        vectors = []
        for i in range(self.next_index):
            if i in self.index_to_id:
                memory_id = self.index_to_id[i]
                vector = self.vectors[memory_id]
                # Normalize for cosine similarity
                norm = np.linalg.norm(vector) + 1e-8
                vectors.append(vector / norm)

        self.vector_matrix = np.array(vectors)


class MemoryAttentionLayer:
    """Attention mechanisms for memory relevance scoring"""

    def __init__(self, hidden_dim: int = 1024, num_heads: int = 8):
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads

        if TORCH_AVAILABLE:
            self.attention = nn.MultiheadAttention(
                embed_dim=hidden_dim,
                num_heads=num_heads,
                dropout=0.1
            )

    def compute_attention_scores(
        self,
        query_embedding: np.ndarray,
        memory_embeddings: List[np.ndarray],
        context: Dict[str, Any]
    ) -> List[float]:
        """Compute attention scores for memories given query"""

        if not memory_embeddings:
            return []

        # Simple dot-product attention for demo
        # In production, would use full transformer attention
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)

        scores = []
        for mem_emb in memory_embeddings:
            # Semantic similarity
            mem_norm = mem_emb / (np.linalg.norm(mem_emb) + 1e-8)
            semantic_score = np.dot(query_norm, mem_norm)

            # Context modulation (simplified)
            context_boost = 1.0
            if "temporal_weight" in context:
                context_boost *= context["temporal_weight"]
            if "emotional_weight" in context:
                context_boost *= context["emotional_weight"]

            # Final score
            final_score = semantic_score * context_boost
            scores.append(float(final_score))

        # Softmax normalization
        if scores:
            max_score = max(scores)
            exp_scores = [math.exp(s - max_score) for s in scores]
            sum_exp = sum(exp_scores)
            scores = [e / sum_exp for e in exp_scores]

        return scores


class ContinuousLearningEngine:
    """Adaptive learning for memory importance and tag weights"""

    def __init__(self, learning_rate: float = 0.001):
        self.learning_rate = learning_rate
        self.tag_weights = defaultdict(lambda: 1.0)
        self.tag_usage_stats = defaultdict(lambda: {"success": 0, "total": 0})

        # Decay parameters
        self.base_decay = 0.99
        self.usage_boost = 1.1
        self.min_weight = 0.1
        self.max_weight = 10.0

    def update_tag_importance(
        self,
        tag: str,
        feedback: float,  # -1 to 1
        context: Dict[str, Any]
    ):
        """Update tag weight based on feedback"""
        current_weight = self.tag_weights[tag]

        # Update statistics
        self.tag_usage_stats[tag]["total"] += 1
        if feedback > 0:
            self.tag_usage_stats[tag]["success"] += 1

        # Calculate update
        if feedback > 0:
            # Positive reinforcement
            delta = self.usage_boost ** feedback
            new_weight = current_weight * delta
        else:
            # Negative feedback or decay
            delta = self.base_decay + (0.1 * feedback)
            new_weight = current_weight * delta

        # Clamp weight
        self.tag_weights[tag] = max(self.min_weight, min(new_weight, self.max_weight))

        logger.debug(
            "Updated tag weight",
            tag=tag,
            old_weight=current_weight,
            new_weight=self.tag_weights[tag],
            feedback=feedback
        )

    def get_tag_importance(self, tag: str) -> float:
        """Get current importance weight for tag"""
        return self.tag_weights[tag]

    def decay_all_weights(self, decay_factor: float = 0.99):
        """Apply temporal decay to all tag weights"""
        for tag in list(self.tag_weights.keys()):
            self.tag_weights[tag] *= decay_factor
            if self.tag_weights[tag] < self.min_weight:
                del self.tag_weights[tag]


class HybridMemoryFold(MemoryFoldSystem):
    """
    Enhanced memory fold system with neural-symbolic integration.

    Combines the efficiency of symbolic tags with the semantic
    richness of vector embeddings for AGI-ready memory.
    """

    def __init__(
        self,
        embedding_dim: int = 1024,
        enable_attention: bool = True,
        enable_continuous_learning: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Vector storage
        self.vector_store = VectorStorageLayer(dimension=embedding_dim)
        self.embedding_dim = embedding_dim

        # Attention layer
        self.enable_attention = enable_attention
        if enable_attention:
            self.attention_layer = MemoryAttentionLayer(hidden_dim=embedding_dim)

        # Continuous learning
        self.enable_continuous_learning = enable_continuous_learning
        if enable_continuous_learning:
            self.learning_engine = ContinuousLearningEngine()

        # Embedding cache
        self.embedding_cache = {}

        # Causal graph
        self.causal_graph = defaultdict(lambda: {"causes": [], "effects": []})

        logger.info(
            "Hybrid Memory Fold initialized",
            embedding_dim=embedding_dim,
            attention_enabled=enable_attention,
            learning_enabled=enable_continuous_learning
        )

    async def fold_in_with_embedding(
        self,
        data: Any,
        tags: List[str],
        embedding: Optional[np.ndarray] = None,
        text_content: Optional[str] = None,
        image_content: Optional[np.ndarray] = None,
        audio_content: Optional[np.ndarray] = None,
        **kwargs
    ) -> str:
        """
        Enhanced fold-in with vector embeddings.

        Args:
            data: Memory content
            tags: Symbolic tags
            embedding: Pre-computed unified embedding
            text_content: Text for embedding generation
            image_content: Image data for embedding
            audio_content: Audio data for embedding
            **kwargs: Additional arguments for base fold_in

        Returns:
            Memory ID
        """
        # Generate embeddings if not provided
        if embedding is None:
            embedding = await self._generate_embedding(
                data, text_content, image_content, audio_content
            )

        # Create hybrid memory item
        memory_id = await super().fold_in(data, tags, **kwargs)

        # Store vector
        if embedding is not None:
            self.vector_store.add_vector(memory_id, embedding)
            self.embedding_cache[memory_id] = embedding

        # Update tag weights if learning enabled
        if self.enable_continuous_learning:
            for tag in tags:
                # Initial positive feedback for new memories
                self.learning_engine.update_tag_importance(tag, 0.1, {})

        logger.info(
            "Hybrid memory folded in",
            memory_id=memory_id,
            has_embedding=embedding is not None,
            num_tags=len(tags)
        )

        return memory_id

    async def fold_out_semantic(
        self,
        query: Union[str, np.ndarray],
        top_k: int = 10,
        use_attention: bool = True,
        combine_with_tags: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[MemoryItem, float]]:
        """
        Semantic search using vector embeddings.

        Args:
            query: Query text or embedding vector
            top_k: Number of results
            use_attention: Apply attention scoring
            combine_with_tags: Also consider tag matches
            context: Additional context for attention

        Returns:
            List of (memory, score) tuples
        """
        # Get query embedding
        if isinstance(query, str):
            query_embedding = await self._generate_text_embedding(query)
        else:
            query_embedding = query

        # Vector search
        vector_results = self.vector_store.search_similar(
            query_embedding, top_k=top_k * 2 if combine_with_tags else top_k
        )

        results = []

        for memory_id, similarity in vector_results:
            if memory_id not in self.items:
                continue

            memory = self.items[memory_id]
            score = similarity

            # Apply attention if enabled
            if use_attention and self.enable_attention:
                memory_embedding = self.embedding_cache.get(memory_id)
                if memory_embedding is not None:
                    attention_scores = self.attention_layer.compute_attention_scores(
                        query_embedding,
                        [memory_embedding],
                        context or {}
                    )
                    if attention_scores:
                        score *= attention_scores[0]

            # Boost score based on tag importance
            if self.enable_continuous_learning:
                tag_boost = 1.0
                item_tags = self.item_tags.get(memory_id, set())
                for tag_id in item_tags:
                    tag_name = self.tag_registry.get(tag_id, {}).tag_name
                    if tag_name:
                        importance = self.learning_engine.get_tag_importance(tag_name)
                        tag_boost = max(tag_boost, importance)
                score *= tag_boost

            results.append((memory, score))

        # Combine with tag-based results if requested
        if combine_with_tags and isinstance(query, str):
            # Extract potential tags from query
            query_tags = query.lower().split()
            for tag in query_tags:
                if tag in self.tag_name_index:
                    tag_results = await self.fold_out_by_tag(
                        tag, max_items=top_k
                    )
                    for tag_memory, _ in tag_results:
                        # Check if already in results
                        if not any(m[0].item_id == tag_memory.item_id for m in results):
                            results.append((tag_memory, 0.5))  # Lower score for tag-only match

        # Sort by score and return top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    async def add_causal_link(
        self,
        cause_id: str,
        effect_id: str,
        strength: float = 1.0,
        evidence: Optional[List[str]] = None
    ):
        """Add causal relationship between memories"""
        if cause_id not in self.items or effect_id not in self.items:
            raise ValueError("Both memories must exist")

        # Validate temporal constraint
        cause_time = self.items[cause_id].timestamp
        effect_time = self.items[effect_id].timestamp

        if cause_time >= effect_time:
            raise ValueError("Cause must precede effect temporally")

        # Add to causal graph
        self.causal_graph[cause_id]["effects"].append({
            "id": effect_id,
            "strength": strength,
            "evidence": evidence or []
        })

        self.causal_graph[effect_id]["causes"].append({
            "id": cause_id,
            "strength": strength,
            "evidence": evidence or []
        })

        logger.info(
            "Causal link added",
            cause=cause_id,
            effect=effect_id,
            strength=strength
        )

    async def trace_causal_chain(
        self,
        memory_id: str,
        direction: str = "backward",
        max_depth: int = 5
    ) -> List[List[Tuple[str, float]]]:
        """
        Trace causal chains from a memory.

        Args:
            memory_id: Starting memory
            direction: "backward" (causes) or "forward" (effects)
            max_depth: Maximum chain depth

        Returns:
            List of causal paths, each path is list of (memory_id, strength) tuples
        """
        paths = []

        def trace_recursive(current_id, path, cumulative_strength, depth):
            if depth >= max_depth:
                return

            # Get connections
            connections = self.causal_graph[current_id]
            links = connections["causes"] if direction == "backward" else connections["effects"]

            if not links:
                # Reached end of chain
                if len(path) > 1:
                    paths.append(path.copy())
            else:
                # Continue tracing
                for link in links:
                    next_id = link["id"]
                    strength = link["strength"]

                    # Avoid cycles
                    if any(p[0] == next_id for p in path):
                        continue

                    new_path = path + [(next_id, cumulative_strength * strength)]
                    trace_recursive(
                        next_id,
                        new_path,
                        cumulative_strength * strength,
                        depth + 1
                    )

        # Start tracing
        trace_recursive(memory_id, [(memory_id, 1.0)], 1.0, 0)

        # Sort paths by cumulative strength
        paths.sort(key=lambda p: p[-1][1], reverse=True)

        return paths

    async def update_memory_importance(
        self,
        memory_id: str,
        feedback: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Update memory importance based on usage feedback"""
        if memory_id not in self.items:
            return

        memory = self.items[memory_id]

        # Update access statistics
        memory.access_count += 1
        memory.last_accessed = datetime.now(timezone.utc)

        # Update tag weights
        if self.enable_continuous_learning:
            item_tags = self.item_tags.get(memory_id, set())
            for tag_id in item_tags:
                tag_info = self.tag_registry.get(tag_id)
                if tag_info:
                    self.learning_engine.update_tag_importance(
                        tag_info.tag_name,
                        feedback,
                        context or {}
                    )

        logger.debug(
            "Updated memory importance",
            memory_id=memory_id,
            feedback=feedback,
            access_count=memory.access_count
        )

    async def _generate_embedding(
        self,
        data: Any,
        text: Optional[str] = None,
        image: Optional[np.ndarray] = None,
        audio: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Generate unified embedding from multi-modal inputs"""
        embeddings = []

        # Text embedding
        if text or isinstance(data, str):
            text_content = text or str(data)
            text_emb = await self._generate_text_embedding(text_content)
            embeddings.append(text_emb)

        # Image embedding (stub)
        if image is not None:
            image_emb = await self._generate_image_embedding(image)
            embeddings.append(image_emb)

        # Audio embedding (stub)
        if audio is not None:
            audio_emb = await self._generate_audio_embedding(audio)
            embeddings.append(audio_emb)

        # Combine embeddings
        if not embeddings:
            # Random embedding if no content
            return np.random.randn(self.embedding_dim).astype(np.float32)
        elif len(embeddings) == 1:
            return embeddings[0]
        else:
            # Average pool multiple embeddings
            return np.mean(embeddings, axis=0)

    async def _generate_text_embedding(self, text: str) -> np.ndarray:
        """Generate text embedding (stub - would use sentence-transformers)"""
        # Simplified embedding generation
        # In production, would use: model.encode(text)

        # Create deterministic pseudo-embedding from text
        text_hash = hashlib.sha256(text.encode()).digest()

        # Convert hash to float array
        embedding = np.frombuffer(text_hash, dtype=np.uint8).astype(np.float32)

        # Expand to full dimension
        if len(embedding) < self.embedding_dim:
            # Repeat pattern
            repeats = self.embedding_dim // len(embedding) + 1
            embedding = np.tile(embedding, repeats)[:self.embedding_dim]
        else:
            embedding = embedding[:self.embedding_dim]

        # Normalize
        embedding = embedding / 255.0 - 0.5
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    async def _generate_image_embedding(self, image: np.ndarray) -> np.ndarray:
        """Generate image embedding (stub - would use CLIP/ViT)"""
        # Placeholder - in production would use vision model
        return np.random.randn(self.embedding_dim).astype(np.float32)

    async def _generate_audio_embedding(self, audio: np.ndarray) -> np.ndarray:
        """Generate audio embedding (stub - would use wav2vec2)"""
        # Placeholder - in production would use audio model
        return np.random.randn(self.embedding_dim).astype(np.float32)

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get statistics including vector and learning metrics"""
        base_stats = super().get_statistics()

        # Add vector statistics
        base_stats["vector_stats"] = {
            "total_vectors": len(self.vector_store.vectors),
            "embedding_dim": self.embedding_dim,
            "cache_size": len(self.embedding_cache)
        }

        # Add learning statistics
        if self.enable_continuous_learning:
            base_stats["learning_stats"] = {
                "total_tag_weights": len(self.learning_engine.tag_weights),
                "avg_tag_weight": np.mean(list(self.learning_engine.tag_weights.values())) if self.learning_engine.tag_weights else 0,
                "most_important_tags": sorted(
                    self.learning_engine.tag_weights.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }

        # Add causal statistics
        base_stats["causal_stats"] = {
            "memories_with_causes": sum(1 for m in self.causal_graph.values() if m["causes"]),
            "memories_with_effects": sum(1 for m in self.causal_graph.values() if m["effects"]),
            "total_causal_links": sum(len(m["causes"]) + len(m["effects"]) for m in self.causal_graph.values()) // 2
        }

        return base_stats


# Factory function
def create_hybrid_memory_fold(
    embedding_dim: int = 1024,
    enable_attention: bool = True,
    enable_continuous_learning: bool = True,
    enable_conscience: bool = True,
    **kwargs
) -> HybridMemoryFold:
    """
    Create an AGI-ready hybrid memory fold system.

    Args:
        embedding_dim: Dimension of vector embeddings
        enable_attention: Enable attention mechanisms
        enable_continuous_learning: Enable adaptive learning
        enable_conscience: Enable structural conscience
        **kwargs: Additional arguments for base system

    Returns:
        Configured HybridMemoryFold instance
    """
    # Create structural conscience if requested
    if enable_conscience:
        from memory.structural_conscience import create_structural_conscience
        conscience = create_structural_conscience()
        kwargs["structural_conscience"] = conscience

    return HybridMemoryFold(
        embedding_dim=embedding_dim,
        enable_attention=enable_attention,
        enable_continuous_learning=enable_continuous_learning,
        **kwargs
    )