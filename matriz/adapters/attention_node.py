"""
MATRIZ Attention Node
=====================

Implements selective attention mechanism for consciousness stream.
Focuses cognitive resources on salient features using bio-inspired
salience mapping and quantum-inspired superposition collapse.

Performance Target: <50ms p95 latency
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

try:
    from prometheus_client import Histogram
    ATTENTION_LATENCY = Histogram(
        "matriz_attention_latency_ms",
        "Attention node processing latency",
        ["lane"],
        buckets=[10, 25, 50, 100, 250]
    )
    PROM = True
except Exception:
    class _N:
        def labels(self, *_, **__): return self
        def observe(self, *_): pass
    ATTENTION_LATENCY = _N()
    PROM = False


@dataclass
class AttentionMap:
    """Salience map for attention focus"""
    features: np.ndarray  # Feature vector (normalized)
    salience_scores: np.ndarray  # [0, 1] salience per feature
    focus_window: List[int]  # Top-k salient feature indices
    attention_score: float  # Overall attention quality [0, 1]


class AttentionNode:
    """
    Selective attention mechanism for consciousness stream.

    Implements:
    - Salience mapping (bottom-up attention)
    - Task-driven focus (top-down attention)
    - Attention bandwidth management (bounded focus)
    - Quantum-inspired superposition collapse

    Algorithm:
    1. Compute salience scores for all input features
    2. Apply task-driven modulation (goals boost salience)
    3. Select top-k features within attention bandwidth
    4. Return focused feature subset + attention quality score
    """

    def __init__(
        self,
        attention_bandwidth: int = 7,  # Miller's law: 7±2 items
        salience_threshold: float = 0.3,
        lane: str = "experimental"
    ):
        self.bandwidth = attention_bandwidth
        self.threshold = salience_threshold
        self.lane = lane

    def process(
        self,
        memory_context: Dict,
        current_input: Dict,
        task_goals: Optional[List[str]] = None
    ) -> AttentionMap:
        """
        Apply attention mechanism to input.

        Args:
            memory_context: Retrieved memory fold
            current_input: Current sensory/input data
            task_goals: Optional task-driven attention hints

        Returns:
            AttentionMap with focused features
        """
        import time
        t0 = time.perf_counter()

        try:
            # Extract features
            features = self._extract_features(memory_context, current_input)

            # Compute bottom-up salience
            salience = self._compute_salience(features)

            # Apply top-down modulation
            if task_goals:
                salience = self._modulate_by_goals(salience, features, task_goals)

            # Select focus window (top-k)
            focus_indices = self._select_focus(salience)

            # Compute attention quality
            attention_score = self._compute_attention_quality(salience, focus_indices)

            return AttentionMap(
                features=features,
                salience_scores=salience,
                focus_window=focus_indices,
                attention_score=attention_score
            )

        finally:
            latency_ms = (time.perf_counter() - t0) * 1000
            if PROM:
                ATTENTION_LATENCY.labels(lane=self.lane).observe(latency_ms)

    def _extract_features(
        self,
        memory: Dict,
        input_data: Dict
    ) -> np.ndarray:
        """Extract and normalize feature vector"""
        # Simplified: combine memory + input embeddings
        # In production: use learned feature extractor

        mem_features = memory.get("embedding", np.zeros(128))
        input_features = input_data.get("embedding", np.zeros(128))

        # Concatenate and normalize
        combined = np.concatenate([mem_features, input_features])
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm

        return combined

    def _compute_salience(self, features: np.ndarray) -> np.ndarray:
        """
        Compute bottom-up salience scores.

        Salience = novelty + intensity + contrast
        """
        # Novelty: deviation from mean
        mean = np.mean(features)
        novelty = np.abs(features - mean)

        # Intensity: absolute magnitude
        intensity = np.abs(features)

        # Contrast: local variance
        window = 5
        contrast = np.array([
            np.std(features[max(0, i-window):min(len(features), i+window)])
            for i in range(len(features))
        ])

        # Combine (weighted sum)
        salience = 0.4 * novelty + 0.3 * intensity + 0.3 * contrast

        # Normalize to [0, 1]
        if np.max(salience) > 0:
            salience = salience / np.max(salience)

        return salience

    def _modulate_by_goals(
        self,
        salience: np.ndarray,
        features: np.ndarray,
        goals: List[str]
    ) -> np.ndarray:
        """Apply top-down task-driven modulation"""
        # Simplified: boost salience for goal-relevant features
        # In production: use goal embeddings and similarity

        # For now, boost high-magnitude features (proxy for goal relevance)
        goal_boost = np.abs(features) > 0.5
        salience[goal_boost] *= 1.5

        # Renormalize
        if np.max(salience) > 0:
            salience = salience / np.max(salience)

        return salience

    def _select_focus(self, salience: np.ndarray) -> List[int]:
        """
        Select top-k salient features within attention bandwidth.

        Respects Miller's law: 7±2 items in working attention.
        """
        # Get indices sorted by salience (descending)
        sorted_indices = np.argsort(salience)[::-1]

        # Take top-k within bandwidth, above threshold
        focus = []
        for idx in sorted_indices:
            if len(focus) >= self.bandwidth:
                break
            if salience[idx] >= self.threshold:
                focus.append(int(idx))

        return focus

    def _compute_attention_quality(
        self,
        salience: np.ndarray,
        focus_indices: List[int]
    ) -> float:
        """
        Compute overall attention quality score [0, 1].

        Quality = (average focus salience) * (coverage ratio)
        """
        if not focus_indices:
            return 0.0

        # Average salience of focused features
        avg_focus_salience = np.mean([salience[i] for i in focus_indices])

        # Coverage: what fraction of total salience is captured?
        total_salience = np.sum(salience)
        captured_salience = np.sum([salience[i] for i in focus_indices])
        coverage = captured_salience / total_salience if total_salience > 0 else 0

        # Quality = salience * coverage
        quality = avg_focus_salience * coverage

        return float(quality)
