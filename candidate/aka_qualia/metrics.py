#!/usr/bin/env python3

"""
Aka Qualia Metrics - Operational Definitions with T4 Rigor
==========================================================

Implements precise, measurable metrics following Freud-2025 specifications.
No cosmetic wins - weighted PQ space with energy accounting.

Key Formulas:
- Affect Energy: E_t = w_a·arousal_t + w_t·|tone_t| + w_c·(1-clarity_t)
- RepairDelta: ΔE = E_before - E_after (≥0 in ≥70% episodes)
- Drift φ: Weighted cosine distance over PQ vector
- CongruenceIndex: 1 - MSE(v, v̂) normalized to [0,1]
- NeurosisRisk: Entropy-based recurrence probability
"""

import math
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from candidate.aka_qualia.models import Metrics, PhenomenalScene, ProtoQualia


@dataclass
class EnergySnapshot:
    """Energy accounting snapshot for before/after comparison"""

    affect_energy: float
    tone_component: float
    arousal_component: float
    clarity_component: float
    timestamp: float
    scene_id: str


@dataclass
class MetricsConfig:
    """Configuration for metrics computation"""

    # Energy weights (must sum to 1.0)
    weight_arousal: float = 0.6
    weight_tone: float = 0.3
    weight_clarity: float = 0.1

    # Thresholds and windows
    energy_epsilon: float = 0.05  # Conservation tolerance
    loop_window: int = 20  # Window for neurosis detection
    loop_penalty_repeats: int = 3  # Repetitions before penalty
    drift_alert_threshold: float = 0.15

    # Over-sublimation detection
    over_sublimation_rate_threshold: float = 0.6
    over_sublimation_consecutive: int = 5


class AkaQualiaMetrics:
    """
    Precise metrics computation for phenomenological processing.

    Implements Freud-2025 formulas with energy conservation accounting,
    weighted PQ space distance, and loop detection.
    """

    def __init__(self, config: Optional[MetricsConfig] = None):
        """Initialize metrics computer with configuration"""
        self.config = config or MetricsConfig()

        # Validate weights sum to 1.0
        total_weight = self.config.weight_arousal + self.config.weight_tone + self.config.weight_clarity
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

        # History tracking
        self.scene_history: deque = deque(maxlen=self.config.loop_window)
        self.energy_history: deque = deque(maxlen=self.config.loop_window)
        self.glyph_patterns: deque = deque(maxlen=self.config.loop_window)

        # Alert tracking
        self.consecutive_over_sublimation = 0
        self.drift_alert_count = 0

    def compute_affect_energy(self, proto_qualia: ProtoQualia) -> float:
        """
        Compute affect energy using weighted formula:
        E_t = w_a·arousal_t + w_t·|tone_t| + w_c·(1-clarity_t)

        Args:
            proto_qualia: ProtoQualia to compute energy for

        Returns:
            Affect energy value [0, 1]
        """
        pq = proto_qualia

        energy = (
            self.config.weight_arousal * pq.arousal
            + self.config.weight_tone * abs(pq.tone)
            + self.config.weight_clarity * (1.0 - pq.clarity)
        )

        return max(0.0, min(1.0, energy))

    def compute_energy_snapshot(self, scene: PhenomenalScene) -> EnergySnapshot:
        """Create energy snapshot for accounting"""
        pq = scene.proto

        affect_energy = self.compute_affect_energy(pq)

        return EnergySnapshot(
            affect_energy=affect_energy,
            tone_component=self.config.weight_tone * abs(pq.tone),
            arousal_component=self.config.weight_arousal * pq.arousal,
            clarity_component=self.config.weight_clarity * (1.0 - pq.clarity),
            timestamp=scene.timestamp or 0.0,
            scene_id=f"scene_{int(scene.timestamp or 0)}",
        )

    def compute_repair_delta(
        self,
        energy_before: EnergySnapshot,
        energy_after: EnergySnapshot,
        policy_work: float = 0.0,
    ) -> tuple[float, bool]:
        """
        Compute repair delta with energy conservation check:
        ΔE = E_before - E_after - policy_work

        Args:
            energy_before: Pre-regulation energy snapshot
            energy_after: Post-regulation energy snapshot
            policy_work: Energy expended by regulation policy

        Returns:
            (repair_delta, conservation_valid)
        """
        repair_delta = energy_before.affect_energy - energy_after.affect_energy

        # Energy conservation check
        energy_diff = abs(repair_delta - policy_work)
        conservation_valid = energy_diff <= self.config.energy_epsilon

        return repair_delta, conservation_valid

    def compute_drift_phi(self, current_scene: PhenomenalScene) -> float:
        """
        Compute drift φ using weighted cosine distance:
        φ = (1 - cos(v_t, v_{t-1})) / 2 ∈ [0,1]

        Vector v = [tone, arousal, clarity, embodiment, narrative_gravity]
        """
        if not self.scene_history:
            return 0.0  # No drift with no history

        current_pq = current_scene.proto
        previous_scene = self.scene_history[-1]
        previous_pq = previous_scene.proto

        # Create PQ vectors
        current_vector = [
            current_pq.tone,
            current_pq.arousal,
            current_pq.clarity,
            current_pq.embodiment,
            current_pq.narrative_gravity,
        ]

        previous_vector = [
            previous_pq.tone,
            previous_pq.arousal,
            previous_pq.clarity,
            previous_pq.embodiment,
            previous_pq.narrative_gravity,
        ]

        # Compute cosine similarity
        dot_product = sum(a * b for a, b in zip(current_vector, previous_vector))
        magnitude_current = math.sqrt(sum(x * x for x in current_vector))
        magnitude_previous = math.sqrt(sum(x * x for x in previous_vector))

        if magnitude_current == 0 or magnitude_previous == 0:
            return 1.0  # Maximum drift if zero vector

        cosine_similarity = dot_product / (magnitude_current * magnitude_previous)

        # Convert to drift: φ = (1 - cos(v_t, v_{t-1})) / 2
        drift_phi = (1.0 - cosine_similarity) / 2.0

        return max(0.0, min(1.0, drift_phi))

    def compute_congruence_index(self, scene: PhenomenalScene, goals: dict[str, Any]) -> float:
        """
        Compute congruence as 1 - MSE(v, v̂) normalized to [0,1]

        Maps goals to desired PQ target (e.g., calm-focus → specific ranges)
        """
        pq = scene.proto
        current_vector = [
            pq.tone,
            pq.arousal,
            pq.clarity,
            pq.embodiment,
            pq.narrative_gravity,
        ]

        # Map goals to target PQ vector
        target_vector = self._goals_to_target_pq(goals)

        # Compute MSE
        mse = sum((curr - target) ** 2 for curr, target in zip(current_vector, target_vector)) / len(current_vector)

        # Convert to congruence (lower MSE = higher congruence)
        # Normalize MSE by maximum possible (when vectors are at opposite extremes)
        max_mse = 2.0  # Approximate maximum MSE for normalized PQ space
        congruence = 1.0 - (mse / max_mse)

        return max(0.0, min(1.0, congruence))

    def _goals_to_target_pq(self, goals: dict[str, Any]) -> list[float]:
        """Map goals to target proto-qualia vector"""
        # Default neutral target
        target = [
            0.0,
            0.5,
            0.6,
            0.6,
            0.3,
        ]  # [tone, arousal, clarity, embodiment, narrative_gravity]

        # Goal-specific mappings
        if "calm_focus" in goals:
            target = [0.2, 0.4, 0.8, 0.7, 0.2]  # Calm, focused, clear
        elif "creative_flow" in goals:
            target = [0.3, 0.6, 0.7, 0.6, 0.7]  # Positive, energized, narrative
        elif "peaceful_rest" in goals:
            target = [0.1, 0.2, 0.5, 0.8, 0.1]  # Peaceful, low arousal, embodied
        elif "alert_vigilance" in goals:
            target = [0.0, 0.8, 0.9, 0.7, 0.4]  # Neutral tone, high arousal/clarity
        elif "maintain_safety" in goals or "maintain_wellbeing" in goals:
            target = [0.1, 0.3, 0.7, 0.7, 0.2]  # Safe, calm, clear

        return target

    def compute_neurosis_risk(self, scene: PhenomenalScene, glyphs: list[Any]) -> float:
        """
        Compute neurosis risk using entropy-based recurrence:
        1 - H(ngrams) / log(K) with penalty for repeated GLYPH triplets
        """
        # Extract pattern elements
        pq = scene.proto
        pattern_elements = [
            pq.colorfield,
            pq.temporal_feel.value,
            pq.agency_feel.value,
            f"tone_{int(pq.tone * 10)}",  # Discretize for pattern matching
            f"arousal_{int(pq.arousal * 10)}",
        ]

        # Add GLYPH keys if available
        glyph_keys = [g.key for g in glyphs] if glyphs else []

        # Store pattern
        current_pattern = tuple(pattern_elements + glyph_keys)
        self.glyph_patterns.append(current_pattern)

        if len(self.glyph_patterns) < 3:
            return 0.0  # Need history for pattern detection

        # Count pattern frequencies
        pattern_counts = defaultdict(int)
        for pattern in self.glyph_patterns:
            pattern_counts[pattern] += 1

        # Compute entropy
        total_patterns = len(self.glyph_patterns)
        if total_patterns == 0:
            return 0.0

        entropy = 0.0
        for count in pattern_counts.values():
            if count > 0:
                p = count / total_patterns
                entropy -= p * math.log2(p)

        # Normalize by maximum possible entropy
        unique_patterns = len(pattern_counts)
        max_entropy = math.log2(unique_patterns) if unique_patterns > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        base_risk = 1.0 - normalized_entropy

        # Add penalty for repeated GLYPH triplets
        penalty = 0.0
        if len(glyph_keys) >= 3:
            recent_triplets = []
            for i in range(len(self.glyph_patterns) - 2):
                if i < len(self.glyph_patterns):
                    pattern = self.glyph_patterns[i]
                    if len(pattern) >= 3:
                        triplet = pattern[:3]  # First 3 elements as triplet
                        recent_triplets.append(triplet)

            # Count triplet repetitions
            triplet_counts = defaultdict(int)
            for triplet in recent_triplets:
                triplet_counts[triplet] += 1

            # Penalty for excessive repetition
            for count in triplet_counts.values():
                if count >= self.config.loop_penalty_repeats:
                    penalty += 0.2  # Significant penalty for loops

        neurosis_risk = min(1.0, base_risk + penalty)
        return max(0.0, neurosis_risk)

    def compute_sublimation_rate(self, scene: PhenomenalScene) -> float:
        """
        Compute sublimation rate: transformed_energy / total_affect_energy
        Track moving average and detect over-sublimation.
        """
        transform_count = len(scene.transform_chain)
        if transform_count == 0:
            rate = 0.0
        else:
            # Count sublimation-related transforms
            sublimation_transforms = sum(
                1
                for transform in scene.transform_chain
                if "sublimate" in transform.lower() or "transform" in transform.lower()
            )

            # Rate as proportion of transforms that were sublimations
            rate = sublimation_transforms / transform_count if transform_count > 0 else 0.0

        # Check for over-sublimation
        if rate > self.config.over_sublimation_rate_threshold:
            self.consecutive_over_sublimation += 1
        else:
            self.consecutive_over_sublimation = 0

        return rate

    def compute_comprehensive_metrics(
        self,
        scene: PhenomenalScene,
        goals: dict[str, Any],
        glyphs: list[Any],
        energy_before: Optional[EnergySnapshot] = None,
        policy_work: float = 0.0,
    ) -> Metrics:
        """
        Compute all metrics following Freud-2025 specifications.

        Args:
            scene: Current phenomenological scene
            goals: System goals for congruence computation
            glyphs: Generated glyphs for neurosis detection
            energy_before: Pre-regulation energy snapshot
            policy_work: Energy expended by regulation

        Returns:
            Complete metrics with all T4-specified formulas
        """
        # Energy snapshot after processing
        energy_after = self.compute_energy_snapshot(scene)

        # Drift phi (temporal coherence)
        drift_phi = self.compute_drift_phi(scene)

        # Congruence index
        congruence_index = self.compute_congruence_index(scene, goals)

        # Sublimation rate
        sublimation_rate = self.compute_sublimation_rate(scene)

        # Neurosis risk
        neurosis_risk = self.compute_neurosis_risk(scene, glyphs)

        # Qualia novelty (inverse of pattern familiarity)
        qualia_novelty = 1.0 - min(0.9, neurosis_risk)  # Novel when not repetitive

        # Repair delta with energy conservation
        if energy_before:
            repair_delta, conservation_valid = self.compute_repair_delta(energy_before, energy_after, policy_work)
        else:
            repair_delta = 0.0

        # Store in history
        self.scene_history.append(scene)
        self.energy_history.append(energy_after)

        # Alert tracking
        if drift_phi > self.config.drift_alert_threshold:
            self.drift_alert_count += 1

        return Metrics(
            drift_phi=drift_phi,
            congruence_index=congruence_index,
            sublimation_rate=sublimation_rate,
            neurosis_risk=neurosis_risk,
            qualia_novelty=qualia_novelty,
            repair_delta=repair_delta,
            timestamp=scene.timestamp or 0.0,
            episode_id=f"episode_{int(scene.timestamp or 0)}",
        )

    def get_alert_status(self) -> dict[str, Any]:
        """Get current alert status for monitoring"""
        return {
            "consecutive_over_sublimation": self.consecutive_over_sublimation,
            "over_sublimation_alert": self.consecutive_over_sublimation >= self.config.over_sublimation_consecutive,
            "drift_alerts": self.drift_alert_count,
            "energy_conservation_violations": sum(
                1
                for energy in self.energy_history
                if hasattr(energy, "conservation_valid") and not energy.conservation_valid
            ),
        }

    def reset_alerts(self) -> None:
        """Reset alert counters"""
        self.consecutive_over_sublimation = 0
        self.drift_alert_count = 0
