#!/usr/bin/env python3
import logging
import streamlit as st
import random
import time
logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - PATTERN SEPARATOR
║ Dentate gyrus-inspired pattern separation for distinct memory encoding
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: pattern_separator.py
║ Path: memory/hippocampal/pattern_separator.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╚══════════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
from typing import Any

import numpy as np


class PatternSeparator:
    """
    Implements pattern separation inspired by dentate gyrus granule cells.
    Creates highly sparse, orthogonal representations from similar inputs.
    """

    def __init__(
        self,
        input_dimension: int = 512,
        output_dimension: int = 2048,
        sparsity: float = 0.02,  # 2% active neurons
        separation_threshold: float = 0.5,
        use_competitive_learning: bool = True,
    ):
        self.input_dimension = input_dimension
        self.output_dimension = output_dimension
        self.sparsity = sparsity
        self.separation_threshold = separation_threshold
        self.use_competitive_learning = use_competitive_learning

        # Initialize random projection matrix (input -> expanded representation)
        self.projection_matrix = np.random.randn(input_dimension, output_dimension) * np.sqrt(2.0 / input_dimension)

        # Competitive learning weights
        if use_competitive_learning:
            self.competitive_weights = np.ones(output_dimension)

        # Statistics
        self.patterns_separated = 0
        self.average_sparsity = 0.0

        logger.info(
            "PatternSeparator initialized",
            input_dim=input_dimension,
            output_dim=output_dimension,
            sparsity=sparsity,
        )

    def separate(self, input_pattern: np.ndarray) -> np.ndarray:
        """
        Perform pattern separation on input.
        Returns sparse, high-dimensional representation.
        """

        # Ensure input is correct dimension
        if input_pattern.shape[0] != self.input_dimension:
            raise ValueError(f"Input dimension mismatch: expected {self.input_dimension}, got {input_pattern.shape[0]}")

        # Project to high-dimensional space
        expanded = np.dot(input_pattern, self.projection_matrix)

        # Apply non-linearity (ReLU)
        expanded = np.maximum(0, expanded)

        # Competitive inhibition
        if self.use_competitive_learning:
            expanded *= self.competitive_weights

        # k-winner-take-all to enforce sparsity
        k = int(self.output_dimension * self.sparsity)

        if k > 0:
            # Find top-k activations
            threshold = np.partition(expanded, -k)[-k]
            sparse_pattern = np.where(expanded >= threshold, expanded, 0)

            # Normalize to maintain stable activation levels
            if np.sum(sparse_pattern) > 0:
                sparse_pattern = sparse_pattern / np.sum(sparse_pattern) * k
        else:
            sparse_pattern = np.zeros_like(expanded)

        # Update competitive weights (hebbian learning)
        if self.use_competitive_learning:
            active_indices = np.where(sparse_pattern > 0)[0]
            self.competitive_weights[active_indices] *= 1.01  # Strengthen winners
            self.competitive_weights /= np.mean(self.competitive_weights)  # Normalize

        # Update statistics
        self.patterns_separated += 1
        current_sparsity = np.count_nonzero(sparse_pattern) / self.output_dimension
        self.average_sparsity = (
            self.average_sparsity * (self.patterns_separated - 1) + current_sparsity
        ) / self.patterns_separated

        return sparse_pattern

    def separate_batch(self, input_patterns: list[np.ndarray]) -> list[np.ndarray]:
        """Separate multiple patterns in batch"""
        return [self.separate(pattern) for pattern in input_patterns]

    def compute_separation_quality(self, pattern1: np.ndarray, pattern2: np.ndarray) -> dict[str, float]:
        """
        Compute metrics for pattern separation quality.
        Returns overlap, correlation, and orthogonality measures.
        """

        # Separate both patterns
        separated1 = self.separate(pattern1)
        separated2 = self.separate(pattern2)

        # Compute overlap (Jaccard index of active neurons)
        active1 = separated1 > 0
        active2 = separated2 > 0
        intersection = np.sum(active1 & active2)
        union = np.sum(active1 | active2)
        overlap = intersection / max(union, 1)

        # Compute correlation
        if np.std(separated1) > 0 and np.std(separated2) > 0:
            correlation = np.corrcoef(separated1, separated2)[0, 1]
        else:
            correlation = 0.0

        # Compute normalized dot product (orthogonality)
        norm1 = np.linalg.norm(separated1)
        norm2 = np.linalg.norm(separated2)
        orthogonality = 1.0 - abs(np.dot(separated1, separated2) / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 1.0

        return {
            "overlap": overlap,
            "correlation": correlation,
            "orthogonality": orthogonality,
            "separation_score": (1 - overlap) * orthogonality,
        }

    def create_content_vector(self, content: Any) -> np.ndarray:
        """
        Convert arbitrary content to input vector for pattern separation.
        Uses feature hashing for consistent dimensionality.
        """

        # Convert to string representation
        content_str = json.dumps(content, sort_keys=True) if isinstance(content, (dict, list)) else str(content)

        # Create feature vector using hashing trick
        vector = np.zeros(self.input_dimension)

        # Hash different n-grams
        for n in range(1, 4):  # 1-grams, 2-grams, 3-grams
            for i in range(len(content_str) - n + 1):
                ngram = content_str[i : i + n]

                # Hash to get index and value
                hash_obj = hashlib.md5(ngram.encode())
                hash_bytes = hash_obj.digest()

                # Use first 4 bytes for index
                index = int.from_bytes(hash_bytes[:4], "big") % self.input_dimension

                # Use next 4 bytes for value (normalized)
                value = int.from_bytes(hash_bytes[4:8], "big") / (2**32)

                vector[index] += value

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def reset_competitive_weights(self):
        """Reset competitive learning weights"""
        if self.use_competitive_learning:
            self.competitive_weights = np.ones(self.output_dimension)

    def get_metrics(self) -> dict[str, Any]:
        """Get pattern separator metrics"""
        return {
            "patterns_separated": self.patterns_separated,
            "average_sparsity": self.average_sparsity,
            "target_sparsity": self.sparsity,
            "expansion_factor": self.output_dimension / self.input_dimension,
            "competitive_weight_variance": (np.var(self.competitive_weights) if self.use_competitive_learning else 0.0),
        }


# Example usage
if __name__ == "__main__":
    # Create pattern separator
    separator = PatternSeparator(input_dimension=256, output_dimension=1024, sparsity=0.05)

    # Test with similar inputs
    content1 = {"type": "learning", "subject": "math", "topic": "calculus"}
    content2 = {"type": "learning", "subject": "math", "topic": "algebra"}
    content3 = {"type": "eating", "food": "pizza", "time": "lunch"}

    # Convert to vectors
    vec1 = separator.create_content_vector(content1)
    vec2 = separator.create_content_vector(content2)
    vec3 = separator.create_content_vector(content3)

    # Test separation quality
    print("=== Pattern Separation Test ===\n")

    # Similar contents (math topics)
    quality_12 = separator.compute_separation_quality(vec1, vec2)
    print("Similar contents (math topics):")
    print(f"  Overlap: {quality_12['overlap']:.3f}")
    print(f"  Correlation: {quality_12['correlation']:.3f}")
    print(f"  Orthogonality: {quality_12['orthogonality']:.3f}")
    print(f"  Separation score: {quality_12['separation_score']:.3f}\n")

    # Different contents
    quality_13 = separator.compute_separation_quality(vec1, vec3)
    print("Different contents (learning vs eating):")
    print(f"  Overlap: {quality_13['overlap']:.3f}")
    print(f"  Correlation: {quality_13['correlation']:.3f}")
    print(f"  Orthogonality: {quality_13['orthogonality']:.3f}")
    print(f"  Separation score: {quality_13['separation_score']:.3f}\n")

    # Metrics
    print("Separator metrics:")
    for key, value in separator.get_metrics().items():
        print(f"  {key}: {value}")