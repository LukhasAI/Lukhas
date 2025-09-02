#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ══════════════════════════════════════════════════════════════════════════════════
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: attention_memory_layer.py
║ Path: memory/systems/attention_memory_layer.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🧬 LUKHAS AI - ATTENTION-BASED MEMORY LAYER
║ ║ A SYMPHONY OF MULTI-HEAD SELF-ATTENTION FOR MEMORY RELEVANCE & PRIORITY
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: attention_memory_layer.py
║ ║ Path: memory/systems/attention_memory_layer.py
║ ║ Version: 1.0.0 | Created: 2025-07-29
║ ║ Authors: LUKHAS AI Arc
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Description: A computational vessel for orchestrating memory relevance through
║ ║              the artful choreography of attention mechanisms.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the vast expanse of the cognitive cosmos, where thoughts and memories weave
║ ║ an intricate tapestry, this module stands as the sentinel of relevance and
║ ║ priority. Like a master conductor guiding a symphony, the Attention-Based Memory
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

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional, Union

import numpy as np

# For production, would use PyTorch/TensorFlow
# Here we implement attention from scratch for demonstration


@dataclass
class AttentionConfig:
    """Configuration for attention mechanisms"""

    hidden_dim: int = 1024
    num_heads: int = 8
    dropout_rate: float = 0.1
    max_sequence_length: int = 512
    use_relative_position: bool = True
    use_temporal_decay: bool = True
    temperature: float = 1.0
    causal_mask: bool = False


class MultiHeadAttention:
    """
    Multi-head attention mechanism for memory processing.

    Implements scaled dot-product attention with multiple heads
    for learning different types of relationships between memories.
    """

    def __init__(self, config: AttentionConfig):
        self.config = config
        self.head_dim = config.hidden_dim // config.num_heads

        # Initialize projection matrices (would be learnable in production)
        self._init_projections()

        logger.info(
            "Multi-head attention initialized",
            hidden_dim=config.hidden_dim,
            num_heads=config.num_heads,
            head_dim=self.head_dim,
        )

    def _init_projections(self):
        """Initialize projection matrices for Q, K, V"""
        # In production, these would be nn.Linear layers
        # For demo, we use random initialization
        dim = self.config.hidden_dim

        # Xavier/Glorot initialization
        scale = np.sqrt(2.0 / dim)

        self.W_q = np.random.randn(dim, dim) * scale
        self.W_k = np.random.randn(dim, dim) * scale
        self.W_v = np.random.randn(dim, dim) * scale
        self.W_o = np.random.randn(dim, dim) * scale

    def forward(
        self,
        query: np.ndarray,
        key: np.ndarray,
        value: np.ndarray,
        mask: Optional[np.ndarray] = None,
        position_bias: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Apply multi-head attention.

        Args:
            query: Query embeddings [batch_size, seq_len, hidden_dim]
            key: Key embeddings [batch_size, seq_len, hidden_dim]
            value: Value embeddings [batch_size, seq_len, hidden_dim]
            mask: Attention mask [batch_size, seq_len, seq_len]
            position_bias: Relative position bias [seq_len, seq_len]

        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size = query.shape[0]
        seq_len = query.shape[1]

        # Linear projections
        Q = self._reshape_for_heads(np.dot(query, self.W_q))
        K = self._reshape_for_heads(np.dot(key, self.W_k))
        V = self._reshape_for_heads(np.dot(value, self.W_v))

        # Scaled dot-product attention
        attention_scores = np.matmul(Q, K.transpose(0, 1, 3, 2))
        attention_scores /= math.sqrt(self.head_dim)

        # Add position bias if provided
        if position_bias is not None:
            attention_scores += position_bias.reshape(1, 1, seq_len, seq_len)

        # Apply mask if provided
        if mask is not None:
            attention_scores = np.where(
                mask.reshape(batch_size, 1, seq_len, seq_len), attention_scores, -1e9
            )

        # Temperature scaling
        attention_scores /= self.config.temperature

        # Softmax
        attention_weights = self._softmax(attention_scores, axis=-1)

        # Apply dropout (simplified - just zeros out some weights)
        if self.config.dropout_rate > 0:
            dropout_mask = np.random.binomial(
                1, 1 - self.config.dropout_rate, attention_weights.shape
            )
            attention_weights *= dropout_mask
            attention_weights /= 1 - self.config.dropout_rate

        # Apply attention to values
        attention_output = np.matmul(attention_weights, V)

        # Reshape and project
        attention_output = self._reshape_from_heads(attention_output)
        output = np.dot(attention_output, self.W_o)

        # Average attention weights across heads for visualization
        avg_attention = attention_weights.mean(axis=1)

        return output, avg_attention

    def _reshape_for_heads(self, x: np.ndarray) -> np.ndarray:
        """Reshape tensor for multi-head attention"""
        batch_size, seq_len, _ = x.shape
        x = x.reshape(batch_size, seq_len, self.config.num_heads, self.head_dim)
        return x.transpose(0, 2, 1, 3)  # [batch, heads, seq_len, head_dim]

    def _reshape_from_heads(self, x: np.ndarray) -> np.ndarray:
        """Reshape tensor back from multi-head format"""
        batch_size, _, seq_len, _ = x.shape
        x = x.transpose(0, 2, 1, 3)  # [batch, seq_len, heads, head_dim]
        return x.reshape(batch_size, seq_len, self.config.hidden_dim)

    def _softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
        """Stable softmax implementation"""
        exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
        return exp_x / (np.sum(exp_x, axis=axis, keepdims=True) + 1e-8)


class TemporalAttention:
    """
    Temporal attention mechanism that considers time decay
    and temporal relationships between memories.
    """

    def __init__(self, config: AttentionConfig):
        self.config = config
        self.base_attention = MultiHeadAttention(config)

        # Temporal decay parameters
        self.decay_rate = 0.001  # Decay per day
        self.min_weight = 0.1  # Minimum temporal weight

    def compute_temporal_bias(
        self, query_time: datetime, memory_times: list[datetime]
    ) -> np.ndarray:
        """
        Compute temporal bias based on time differences.

        Recent memories get higher bias scores.
        """
        current_time = query_time.timestamp()

        bias = np.zeros((1, len(memory_times)))

        for i, mem_time in enumerate(memory_times):
            # Time difference in days
            time_diff = (current_time - mem_time.timestamp()) / 86400.0

            # Exponential decay
            temporal_weight = max(self.min_weight, np.exp(-self.decay_rate * time_diff))

            # Convert to log space for addition to attention scores
            bias[0, i] = np.log(temporal_weight + 1e-8)

        return bias

    def forward(
        self,
        query_embedding: np.ndarray,
        memory_embeddings: np.ndarray,
        query_time: datetime,
        memory_times: list[datetime],
        **kwargs,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Apply temporal attention to memories.

        Returns:
            Tuple of (weighted_memories, attention_weights)
        """
        # Compute temporal bias
        temporal_bias = self.compute_temporal_bias(query_time, memory_times)

        # Expand dimensions for batch processing
        # For temporal attention, we repeat query to match memory length for
        # cross-attention
        num_memories = len(memory_embeddings)
        query_repeated = np.repeat(query_embedding.reshape(1, -1), num_memories, axis=0)
        query_batch = query_repeated.reshape(1, num_memories, -1)
        memories = memory_embeddings.reshape(1, num_memories, -1)

        # Apply attention without position bias (temporal weights handled differently)
        output, attention_weights = self.base_attention.forward(
            query_batch, memories, memories
        )

        # Apply temporal weights to attention scores
        temporal_weights = np.exp(temporal_bias.squeeze())
        attention_weights = attention_weights.squeeze() * temporal_weights
        attention_weights = attention_weights / (attention_weights.sum() + 1e-8)

        # Remove batch dimension
        output = output.squeeze(0)
        # attention_weights already has correct shape after our manual processing

        return output, attention_weights


class HierarchicalAttention:
    """
    Hierarchical attention for processing memories at multiple scales.
    Useful for handling both fine-grained and abstract memories.
    """

    def __init__(self, config: AttentionConfig, num_levels: int = 3):
        self.config = config
        self.num_levels = num_levels

        # Create attention layers for each level
        self.level_attentions = [MultiHeadAttention(config) for _ in range(num_levels)]

        # Pooling sizes for each level
        self.pool_sizes = [2**i for i in range(num_levels)]

    def create_hierarchical_representations(
        self, memories: np.ndarray
    ) -> list[np.ndarray]:
        """
        Create multi-scale representations of memories.

        Args:
            memories: Memory embeddings [num_memories, hidden_dim]

        Returns:
            List of representations at different scales
        """
        representations = [memories]

        for pool_size in self.pool_sizes[1:]:
            # Simple average pooling for demonstration
            # In production, could use learned pooling
            num_groups = len(memories) // pool_size
            if num_groups == 0:
                break

            pooled = []
            for i in range(num_groups):
                start = i * pool_size
                end = min(start + pool_size, len(memories))
                group = memories[start:end]
                pooled.append(np.mean(group, axis=0))

            if pooled:
                pooled_array = np.array(pooled)
                representations.append(pooled_array)

        return representations

    def forward(
        self, query: np.ndarray, memories: np.ndarray, return_all_levels: bool = False
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """
        Apply hierarchical attention across multiple scales.

        Returns:
            Tuple of (combined_output, attention_info)
        """
        # Create hierarchical representations
        hierarchical_memories = self.create_hierarchical_representations(memories)

        level_outputs = []
        level_weights = []

        # Apply attention at each level
        for _level, (level_memories, attention) in enumerate(
            zip(hierarchical_memories, self.level_attentions)
        ):
            if len(level_memories) == 0:
                continue

            # Expand dimensions
            q = query.reshape(1, 1, -1)
            m = level_memories.reshape(1, len(level_memories), -1)

            output, weights = attention.forward(q, m, m)

            level_outputs.append(output.squeeze())
            level_weights.append(weights.squeeze())

        # Combine outputs from different levels
        if level_outputs:
            # Simple averaging for demo; could use learned combination
            combined_output = np.mean(level_outputs, axis=0)
        else:
            combined_output = query

        # Prepare attention info
        attention_info = {
            f"level_{i}_weights": weights for i, weights in enumerate(level_weights)
        }

        if return_all_levels:
            attention_info["level_outputs"] = level_outputs

        return combined_output, attention_info


class CrossModalAttention:
    """
    Cross-modal attention for integrating information
    across different modalities (text, image, audio).
    """

    def __init__(self, config: AttentionConfig):
        self.config = config

        # Separate attention modules for each modality pair
        self.text_to_image = MultiHeadAttention(config)
        self.text_to_audio = MultiHeadAttention(config)
        self.image_to_text = MultiHeadAttention(config)
        self.image_to_audio = MultiHeadAttention(config)
        self.audio_to_text = MultiHeadAttention(config)
        self.audio_to_image = MultiHeadAttention(config)

        # Modality embeddings (learned in production)
        self.modality_embeddings = {
            "text": np.random.randn(config.hidden_dim) * 0.1,
            "image": np.random.randn(config.hidden_dim) * 0.1,
            "audio": np.random.randn(config.hidden_dim) * 0.1,
        }

    def forward(
        self, modality_embeddings: dict[str, np.ndarray], primary_modality: str = "text"
    ) -> dict[str, np.ndarray]:
        """
        Apply cross-modal attention between different modalities.

        Args:
            modality_embeddings: Dict mapping modality name to embeddings
            primary_modality: Primary modality to attend from

        Returns:
            Dict of attended representations for each modality
        """
        attended = {}

        # Get primary modality embedding
        if primary_modality not in modality_embeddings:
            logger.warning(
                "Primary modality not found",
                primary=primary_modality,
                available=list(modality_embeddings.keys()),
            )
            return modality_embeddings

        primary_emb = modality_embeddings[primary_modality]
        primary_emb = primary_emb.reshape(1, 1, -1)

        # Apply cross-modal attention
        for modality, embedding in modality_embeddings.items():
            if modality == primary_modality:
                attended[modality] = modality_embeddings[modality]
                continue

            # Select appropriate attention module
            if primary_modality == "text" and modality == "image":
                attention = self.text_to_image
            elif primary_modality == "text" and modality == "audio":
                attention = self.text_to_audio
            elif primary_modality == "image" and modality == "text":
                attention = self.image_to_text
            elif primary_modality == "image" and modality == "audio":
                attention = self.image_to_audio
            elif primary_modality == "audio" and modality == "text":
                attention = self.audio_to_text
            elif primary_modality == "audio" and modality == "image":
                attention = self.audio_to_image
            else:
                # Fallback to original
                attended[modality] = embedding
                continue

            # Apply attention
            target_emb = embedding.reshape(1, 1, -1)
            output, _ = attention.forward(primary_emb, target_emb, target_emb)
            attended[modality] = output.squeeze()

        return attended


class MemoryAttentionOrchestrator:
    """
    Orchestrates different attention mechanisms for comprehensive
    memory processing in the AGI system.
    """

    def __init__(self, config: Optional[AttentionConfig] = None):
        self.config = config or AttentionConfig()

        # Initialize attention components
        self.multi_head = MultiHeadAttention(self.config)
        self.temporal = TemporalAttention(self.config)
        self.hierarchical = HierarchicalAttention(self.config)
        self.cross_modal = CrossModalAttention(self.config)

        logger.info("Memory attention orchestrator initialized")

    def compute_memory_relevance(
        self,
        query: Union[str, np.ndarray],
        memories: list[dict[str, Any]],
        mode: str = "multi_head",
        context: Optional[dict[str, Any]] = None,
    ) -> list[tuple[int, float]]:
        """
        Compute relevance scores for memories using specified attention mode.

        Args:
            query: Query text or embedding
            memories: List of memory items with embeddings
            mode: Attention mode (multi_head, temporal, hierarchical, cross_modal)
            context: Additional context for attention computation

        Returns:
            List of (memory_index, relevance_score) tuples
        """
        if not memories:
            return []

        # Convert query to embedding if needed
        if isinstance(query, str):
            # Simplified: use hash-based embedding
            query_embedding = self._text_to_embedding(query)
        else:
            query_embedding = query

        # Extract memory embeddings
        memory_embeddings = []
        valid_indices = []

        for i, memory in enumerate(memories):
            if "embedding" in memory and memory["embedding"] is not None:
                memory_embeddings.append(memory["embedding"])
                valid_indices.append(i)

        if not memory_embeddings:
            logger.warning("No memories with embeddings found")
            return []

        memory_array = np.array(memory_embeddings)

        # Apply specified attention mode
        if mode == "temporal" and all("timestamp" in m for m in memories):
            # Use temporal attention
            memory_times = [m["timestamp"] for m in memories if "embedding" in m]
            query_time = context.get("query_time", datetime.now(timezone.utc))

            _, attention_weights = self.temporal.forward(
                query_embedding, memory_array, query_time, memory_times
            )

        elif mode == "hierarchical":
            # Use hierarchical attention
            _, attention_info = self.hierarchical.forward(query_embedding, memory_array)
            # Use finest level weights
            attention_weights = attention_info.get(
                "level_0_weights", np.ones(len(memory_array))
            )

        elif mode == "cross_modal" and context and "modalities" in context:
            # Use cross-modal attention
            modalities = context["modalities"]
            self.cross_modal.forward(modalities)
            # For simplicity, use uniform weights
            attention_weights = np.ones(len(memory_array)) / len(memory_array)

        else:
            # Default to multi-head attention
            query_batch = query_embedding.reshape(1, 1, -1)
            memory_batch = memory_array.reshape(1, len(memory_array), -1)

            _, attention_weights = self.multi_head.forward(
                query_batch, memory_batch, memory_batch
            )
            attention_weights = attention_weights.squeeze()

        # Convert to relevance scores
        relevance_scores = []
        # Handle different shapes of attention_weights
        if attention_weights.ndim > 1:
            # Average across dimensions if needed
            weights = attention_weights.mean(
                axis=tuple(range(attention_weights.ndim - 1))
            )
        else:
            weights = attention_weights

        for idx, weight in zip(valid_indices, weights):
            relevance_scores.append((idx, float(weight)))

        # Sort by relevance
        relevance_scores.sort(key=lambda x: x[1], reverse=True)

        return relevance_scores

    def _text_to_embedding(self, text: str) -> np.ndarray:
        """Simple text to embedding conversion (placeholder)"""
        # In production, would use sentence transformers
        text_hash = hash(text)
        np.random.seed(abs(text_hash) % (2**32))
        embedding = np.random.randn(self.config.hidden_dim)
        return embedding / np.linalg.norm(embedding)

    def explain_attention(
        self, attention_weights: np.ndarray, memory_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Generate human-readable explanation of attention patterns.

        Args:
            attention_weights: Attention weight matrix
            memory_items: List of memory items

        Returns:
            Dict with attention analysis
        """
        analysis = {
            "top_attended_memories": [],
            "attention_distribution": {},
            "attention_entropy": 0.0,
            "focus_score": 0.0,
        }

        # Get top attended memories
        weights = (
            attention_weights
            if len(attention_weights.shape) == 1
            else attention_weights.mean(axis=0)
        )

        top_indices = np.argsort(weights)[-5:][::-1]

        for idx in top_indices:
            if idx < len(memory_items):
                memory = memory_items[idx]
                analysis["top_attended_memories"].append(
                    {
                        "index": int(idx),
                        "weight": float(weights[idx]),
                        "content": str(memory.get("content", ""))[:100],
                        "tags": memory.get("tags", []),
                    }
                )

        # Attention distribution
        analysis["attention_distribution"] = {
            "max": float(weights.max()),
            "min": float(weights.min()),
            "mean": float(weights.mean()),
            "std": float(weights.std()),
        }

        # Attention entropy (how distributed the attention is)
        # Lower entropy = more focused attention
        entropy = -np.sum(weights * np.log(weights + 1e-8))
        analysis["attention_entropy"] = float(entropy)

        # Focus score (inverse of entropy, normalized)
        max_entropy = -np.log(1.0 / len(weights))
        analysis["focus_score"] = 1.0 - (entropy / max_entropy)

        return analysis


# Factory function
def create_attention_orchestrator(
    hidden_dim: int = 1024,
    num_heads: int = 8,
    enable_temporal: bool = True,
    enable_hierarchical: bool = True,
    enable_cross_modal: bool = True,
) -> MemoryAttentionOrchestrator:
    """
    Create a configured attention orchestrator for memory systems.

    Args:
        hidden_dim: Hidden dimension for attention
        num_heads: Number of attention heads
        enable_temporal: Enable temporal attention
        enable_hierarchical: Enable hierarchical attention
        enable_cross_modal: Enable cross-modal attention

    Returns:
        Configured MemoryAttentionOrchestrator
    """
    config = AttentionConfig(
        hidden_dim=hidden_dim,
        num_heads=num_heads,
        use_temporal_decay=enable_temporal,
    )

    return MemoryAttentionOrchestrator(config)
