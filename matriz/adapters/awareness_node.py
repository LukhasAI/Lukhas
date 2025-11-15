"""
MATRIZ Awareness Node
=====================

Meta-cognitive monitoring and self-awareness.
Implements consciousness of consciousness - awareness of internal states,
processing quality, and cognitive coherence.

Performance Target: <50ms p95 latency
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AwarenessState:
    """Meta-cognitive awareness state"""
    self_model: Dict  # Current self-representation
    processing_quality: float  # [0, 1] overall quality
    coherence: float  # [0, 1] internal consistency
    attention_drift: float  # [0, 1] focus stability
    meta_thoughts: List[str]  # Self-reflective observations


class AwarenessNode:
    """
    Meta-cognitive awareness and self-monitoring.

    Monitors:
    - Processing quality across all nodes
    - Internal coherence (consistency checks)
    - Attention stability (drift detection)
    - Self-model accuracy

    Implements consciousness of consciousness.
    """

    def __init__(self, lane: str = "experimental"):
        self.lane = lane
        self._processing_history = []  # Last 10 cycles

    def process(
        self,
        attention_map,
        thought: "Thought",
        decision_pending: bool = False
    ) -> AwarenessState:
        """
        Monitor and analyze current cognitive state.

        Returns meta-cognitive awareness including:
        - Self-model (what am I thinking about?)
        - Processing quality (how well am I thinking?)
        - Coherence (am I thinking consistently?)
        """
        # Build self-model
        self_model = self._build_self_model(attention_map, thought)

        # Assess processing quality
        quality = self._assess_quality(attention_map, thought)

        # Check coherence
        coherence = self._check_coherence(thought)

        # Monitor attention drift
        drift = self._measure_drift(attention_map)

        # Generate meta-thoughts
        meta_thoughts = self._generate_meta_thoughts(
            quality, coherence, drift, decision_pending
        )

        # Record state
        self._processing_history.append({
            "quality": quality,
            "coherence": coherence,
            "drift": drift
        })
        if len(self._processing_history) > 10:
            self._processing_history.pop(0)

        return AwarenessState(
            self_model=self_model,
            processing_quality=quality,
            coherence=coherence,
            attention_drift=drift,
            meta_thoughts=meta_thoughts
        )

    def _build_self_model(self, attention_map, thought) -> Dict:
        """Build current self-representation"""
        return {
            "currently_attending_to": len(attention_map.focus_window),
            "current_thought": thought.content[:50] + "...",
            "thought_confidence": thought.confidence,
            "thought_novelty": thought.novelty,
            "lane": self.lane
        }

    def _assess_quality(self, attention_map, thought) -> float:
        """Assess overall processing quality [0, 1]"""
        # Combine attention quality + thought confidence
        quality = 0.5 * attention_map.attention_score + 0.5 * thought.confidence
        return quality

    def _check_coherence(self, thought) -> float:
        """Check internal thought coherence [0, 1]"""
        # Simplified: check reasoning chain consistency
        # In production: use semantic coherence models

        if len(thought.reasoning_chain) < 2:
            return 1.0  # Trivially coherent

        # Check if reasoning steps are non-contradictory
        # (Simplified heuristic)
        coherence = 0.8  # Default high coherence

        return coherence

    def _measure_drift(self, attention_map) -> float:
        """Measure attention drift [0, 1]"""
        if len(self._processing_history) < 2:
            return 0.0  # No drift yet

        # Compare current attention quality to recent average
        recent_quality = sum(
            h["quality"] for h in self._processing_history[-5:]
        ) / min(5, len(self._processing_history))

        current_quality = attention_map.attention_score

        drift = abs(current_quality - recent_quality)
        return min(1.0, drift)

    def _generate_meta_thoughts(
        self,
        quality: float,
        coherence: float,
        drift: float,
        decision_pending: bool
    ) -> List[str]:
        """Generate self-reflective meta-thoughts"""
        meta = []

        if quality < 0.5:
            meta.append("Processing quality degraded - attention may be overloaded")

        if coherence < 0.7:
            meta.append("Thought coherence low - internal contradiction detected")

        if drift > 0.3:
            meta.append("Attention drift elevated - focus instability")

        if decision_pending and quality > 0.7:
            meta.append("Cognitive state suitable for decision-making")

        if not meta:
            meta.append("Cognitive processing nominal")

        return meta
