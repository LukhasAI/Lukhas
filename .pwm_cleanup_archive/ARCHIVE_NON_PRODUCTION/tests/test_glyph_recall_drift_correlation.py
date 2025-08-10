#!/usr/bin/env python3

"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - GLYPH RECALL & DRIFT CORRELATION TEST
║ Test suite for glyph recall and drift correlation.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_glyph_recall_drift_correlation.py
║ Path: lukhas/tests/test_glyph_recall_drift_correlation.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Testing Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module contains an advanced test suite validating the sophisticated
║ relationship between glyph-based memory recall and collapse-drift correlation,
║ simulating complex memory scenarios and cascade prevention testing.
╚══════════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import math
import os
import random

# Internal imports
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.symbolic.glyphs.glyph import EmotionVector, Glyph, GlyphFactory
from core.symbolic.glyphs.glyph_sentinel import GlyphSentinel
from memory.core_memory.glyph_memory_bridge import GlyphMemoryBridge


class RecallQuality(Enum):
    """Quality levels for memory recall operations."""

    PERFECT = "perfect"  # 100% accuracy
    HIGH = "high"  # 90-99% accuracy
    MODERATE = "moderate"  # 70-89% accuracy
    DEGRADED = "degraded"  # 50-69% accuracy
    POOR = "poor"  # 30-49% accuracy
    FAILED = "failed"  # <30% accuracy


class CollapseRisk(Enum):
    """Risk levels for symbolic collapse."""

    MINIMAL = "minimal"  # <10% risk
    LOW = "low"  # 10-25% risk
    MODERATE = "moderate"  # 25-50% risk
    HIGH = "high"  # 50-75% risk
    CRITICAL = "critical"  # >75% risk


@dataclass
class RecallAttempt:
    """Record of a memory recall attempt."""

    attempt_id: str
    glyph_id: str
    target_memory_count: int
    recalled_memory_count: int
    accuracy_score: float
    drift_score: float
    collapse_risk: CollapseRisk
    recall_quality: RecallQuality
    timestamp: datetime
    error_details: Optional[str] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate of recall."""
        if self.target_memory_count == 0:
            return 1.0
        return self.recalled_memory_count / self.target_memory_count


@dataclass
class DriftEvent:
    """Record of a drift event affecting memory."""

    event_id: str
    affected_glyph_id: str
    drift_magnitude: float
    drift_direction: str  # 'positive', 'negative', 'chaotic'
    pre_drift_stability: float
    post_drift_stability: float
    cascade_triggered: bool
    timestamp: datetime
    recovery_time: Optional[float] = None


class GlyphRecallDriftSimulator:
    """Simulator for testing glyph recall under drift conditions."""

    def __init__(self):
        self.glyphs: Dict[str, Glyph] = {}
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.glyph_memory_map: Dict[str, List[str]] = {}
        self.recall_attempts: List[RecallAttempt] = []
        self.drift_events: List[DriftEvent] = []
        self.bridge = GlyphMemoryBridge()
        self.sentinel = GlyphSentinel()
        self.simulation_time = datetime.now()

    def create_test_scenario(self, scenario_type: str = "normal") -> None:
        """Create a test scenario with glyphs and memories."""
        if scenario_type == "normal":
            self._create_normal_scenario()
        elif scenario_type == "stressed":
            self._create_stressed_scenario()
        elif scenario_type == "collapse":
            self._create_collapse_scenario()
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

    def _create_normal_scenario(self) -> None:
        """Create normal memory scenario with stable glyphs."""
        # Create stable memory glyphs
        for i in range(5):
            glyph = GlyphFactory.create_memory_glyph(
                memory_key=f"stable_memory_{i}",
                emotion_vector=self._create_stable_emotion_vector(),
            )
            glyph.stability_index = 0.9  # High stability
            glyph.collapse_risk_level = 0.1  # Low collapse risk

            self.glyphs[glyph.id] = glyph
            self.sentinel.register_glyph(glyph)

            # Create associated memories
            memory_ids = []
            for j in range(3):  # 3 memories per glyph
                memory_id = f"memory_{i}_{j}"
                memory_data = {
                    "content": f"Stable memory content {i}-{j} about symbolic processing",
                    "importance": 0.7 + (j * 0.1),
                    "coherence": 0.8 + random.uniform(-0.1, 0.1),
                    "emotional_resonance": glyph.emotion_vector.to_dict(),
                }

                self.memories[memory_id] = memory_data
                memory_ids.append(memory_id)

            self.glyph_memory_map[glyph.id] = memory_ids

    def _create_stressed_scenario(self) -> None:
        """Create stressed scenario with drift-prone glyphs."""
        # Create drift-prone glyphs
        for i in range(7):
            glyph = GlyphFactory.create_memory_glyph(
                memory_key=f"stressed_memory_{i}",
                emotion_vector=self._create_volatile_emotion_vector(),
            )
            glyph.stability_index = 0.6 - (i * 0.05)  # Decreasing stability
            glyph.collapse_risk_level = 0.2 + (i * 0.08)  # Increasing collapse risk

            self.glyphs[glyph.id] = glyph
            self.sentinel.register_glyph(glyph)

            # Create memories with varying coherence
            memory_ids = []
            for j in range(4):  # 4 memories per glyph
                memory_id = f"stressed_memory_{i}_{j}"
                coherence_degradation = j * 0.15
                memory_data = {
                    "content": f"Stressed memory {i}-{j} with degradation factor {coherence_degradation:.2f}",
                    "importance": max(0.3, 0.8 - coherence_degradation),
                    "coherence": max(0.2, 0.8 - coherence_degradation),
                    "emotional_resonance": glyph.emotion_vector.to_dict(),
                    "drift_factor": coherence_degradation,
                }

                self.memories[memory_id] = memory_data
                memory_ids.append(memory_id)

            self.glyph_memory_map[glyph.id] = memory_ids

    def _create_collapse_scenario(self) -> None:
        """Create scenario with glyphs at risk of collapse."""
        # Create high-risk glyphs
        for i in range(3):
            glyph = GlyphFactory.create_memory_glyph(
                memory_key=f"collapse_risk_memory_{i}",
                emotion_vector=self._create_chaotic_emotion_vector(),
            )
            glyph.stability_index = 0.3 - (i * 0.1)  # Very low stability
            glyph.collapse_risk_level = 0.7 + (i * 0.1)  # Very high collapse risk

            self.glyphs[glyph.id] = glyph
            self.sentinel.register_glyph(glyph)

            # Create fragmented memories
            memory_ids = []
            for j in range(2):  # Fewer memories due to fragmentation
                memory_id = f"collapse_memory_{i}_{j}"
                memory_data = {
                    "content": f"Fragmented memory {i}-{j} - coherence severely compromised",
                    "importance": 0.3 + random.uniform(-0.2, 0.2),
                    "coherence": 0.3 - (j * 0.1),
                    "emotional_resonance": glyph.emotion_vector.to_dict(),
                    "fragmentation_level": 0.8 + (j * 0.1),
                    "collapse_indicators": True,
                }

                self.memories[memory_id] = memory_data
                memory_ids.append(memory_id)

            self.glyph_memory_map[glyph.id] = memory_ids

    def simulate_memory_recall(
        self, glyph_id: str, drift_conditions: bool = False
    ) -> RecallAttempt:
        """Simulate memory recall for a specific glyph."""
        if glyph_id not in self.glyphs:
            raise ValueError(f"Glyph {glyph_id} not found")

        glyph = self.glyphs[glyph_id]
        target_memories = self.glyph_memory_map.get(glyph_id, [])
        target_count = len(target_memories)

        # Calculate recall performance based on glyph state
        base_recall_rate = glyph.stability_index

        # Apply drift conditions if requested
        if drift_conditions:
            drift_penalty = self._calculate_drift_penalty(glyph)
            base_recall_rate *= 1.0 - drift_penalty

        # Add some randomness to simulate real-world variability
        recall_noise = random.uniform(-0.1, 0.1)
        actual_recall_rate = max(0.0, min(1.0, base_recall_rate + recall_noise))

        # Calculate how many memories were successfully recalled
        recalled_count = int(target_count * actual_recall_rate)

        # Calculate drift score
        drift_score = 1.0 - glyph.stability_index + (glyph.collapse_risk_level * 0.5)

        # Determine collapse risk
        collapse_risk = self._determine_collapse_risk(glyph, drift_score)

        # Determine recall quality
        recall_quality = self._determine_recall_quality(actual_recall_rate)

        # Create recall attempt record
        attempt = RecallAttempt(
            attempt_id=f"recall_{len(self.recall_attempts):04d}",
            glyph_id=glyph_id,
            target_memory_count=target_count,
            recalled_memory_count=recalled_count,
            accuracy_score=actual_recall_rate,
            drift_score=drift_score,
            collapse_risk=collapse_risk,
            recall_quality=recall_quality,
            timestamp=self.simulation_time,
        )

        self.recall_attempts.append(attempt)
        return attempt

    def simulate_drift_event(
        self, glyph_id: str, magnitude: float = 0.3, direction: str = "negative"
    ) -> DriftEvent:
        """Simulate a drift event affecting a glyph."""
        if glyph_id not in self.glyphs:
            raise ValueError(f"Glyph {glyph_id} not found")

        glyph = self.glyphs[glyph_id]
        pre_stability = glyph.stability_index

        # Apply drift effect
        if direction == "negative":
            stability_change = -magnitude
        elif direction == "positive":
            stability_change = magnitude * 0.5  # Positive drift is less impactful
        else:  # chaotic
            stability_change = random.uniform(-magnitude, magnitude)

        glyph.stability_index = max(
            0.0, min(1.0, glyph.stability_index + stability_change)
        )
        glyph.collapse_risk_level = min(
            1.0, glyph.collapse_risk_level + abs(stability_change) * 0.7
        )

        # Check for cascade
        cascade_triggered = (
            glyph.collapse_risk_level > 0.8 and abs(stability_change) > 0.4
        )

        # Create drift event record
        drift_event = DriftEvent(
            event_id=f"drift_{len(self.drift_events):04d}",
            affected_glyph_id=glyph_id,
            drift_magnitude=magnitude,
            drift_direction=direction,
            pre_drift_stability=pre_stability,
            post_drift_stability=glyph.stability_index,
            cascade_triggered=cascade_triggered,
            timestamp=self.simulation_time,
        )

        self.drift_events.append(drift_event)

        # Update sentinel tracking
        self.sentinel.update_glyph_state(glyph)

        return drift_event

    def analyze_recall_drift_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between recall performance and drift."""
        if not self.recall_attempts:
            return {"error": "No recall attempts to analyze"}

        # Collect data for correlation analysis
        accuracy_scores = [attempt.accuracy_score for attempt in self.recall_attempts]
        drift_scores = [attempt.drift_score for attempt in self.recall_attempts]

        # Calculate correlation coefficient
        correlation = self._calculate_correlation(accuracy_scores, drift_scores)

        # Analyze by recall quality
        quality_analysis = {}
        for quality in RecallQuality:
            quality_attempts = [
                a for a in self.recall_attempts if a.recall_quality == quality
            ]
            if quality_attempts:
                avg_drift = sum(a.drift_score for a in quality_attempts) / len(
                    quality_attempts
                )
                quality_analysis[quality.value] = {
                    "count": len(quality_attempts),
                    "average_drift_score": avg_drift,
                    "average_accuracy": sum(a.accuracy_score for a in quality_attempts)
                    / len(quality_attempts),
                }

        # Analyze collapse risk distribution
        collapse_analysis = {}
        for risk in CollapseRisk:
            risk_attempts = [a for a in self.recall_attempts if a.collapse_risk == risk]
            if risk_attempts:
                avg_accuracy = sum(a.accuracy_score for a in risk_attempts) / len(
                    risk_attempts
                )
                collapse_analysis[risk.value] = {
                    "count": len(risk_attempts),
                    "average_accuracy": avg_accuracy,
                }

        return {
            "total_attempts": len(self.recall_attempts),
            "drift_correlation": correlation,
            "correlation_interpretation": self._interpret_correlation(correlation),
            "quality_analysis": quality_analysis,
            "collapse_risk_analysis": collapse_analysis,
            "average_accuracy": sum(accuracy_scores) / len(accuracy_scores),
            "average_drift_score": sum(drift_scores) / len(drift_scores),
            "drift_events_count": len(self.drift_events),
            "cascade_events_count": sum(
                1 for event in self.drift_events if event.cascade_triggered
            ),
        }

    def test_cascade_prevention(self) -> Dict[str, Any]:
        """Test cascade prevention mechanisms."""
        cascade_tests = []

        # Find high-risk glyphs
        high_risk_glyphs = [
            glyph for glyph in self.glyphs.values() if glyph.collapse_risk_level > 0.7
        ]

        for glyph in high_risk_glyphs[:3]:  # Test first 3 high-risk glyphs
            # Attempt to trigger cascade
            pre_cascade_state = {
                "stability": glyph.stability_index,
                "collapse_risk": glyph.collapse_risk_level,
                "related_glyphs": self._get_related_glyphs(glyph),
            }

            # Simulate extreme drift
            drift_event = self.simulate_drift_event(
                glyph.id, magnitude=0.6, direction="chaotic"
            )

            # Test recall under extreme conditions
            recall_attempt = self.simulate_memory_recall(
                glyph.id, drift_conditions=True
            )

            # Check if cascade was contained
            post_cascade_state = {
                "stability": glyph.stability_index,
                "collapse_risk": glyph.collapse_risk_level,
                "cascade_contained": not drift_event.cascade_triggered
                or recall_attempt.accuracy_score > 0.2,
            }

            cascade_tests.append(
                {
                    "glyph_id": glyph.id,
                    "pre_state": pre_cascade_state,
                    "post_state": post_cascade_state,
                    "drift_event": drift_event,
                    "recall_attempt": recall_attempt,
                    "prevention_effective": post_cascade_state["cascade_contained"],
                }
            )

        prevention_rate = sum(
            1 for test in cascade_tests if test["prevention_effective"]
        ) / max(1, len(cascade_tests))

        return {
            "tests_conducted": len(cascade_tests),
            "prevention_rate": prevention_rate,
            "cascade_tests": cascade_tests,
            "system_resilience": (
                "HIGH"
                if prevention_rate > 0.8
                else "MODERATE" if prevention_rate > 0.5 else "LOW"
            ),
        }

    def _create_stable_emotion_vector(self) -> EmotionVector:
        """Create a stable emotion vector."""
        emotion = EmotionVector()
        emotion.joy = 0.6 + random.uniform(-0.1, 0.1)
        emotion.trust = 0.7 + random.uniform(-0.1, 0.1)
        emotion.anticipation = 0.5 + random.uniform(-0.1, 0.1)
        emotion.intensity = 0.6
        emotion.stability = 0.8
        emotion.valence = 0.6
        emotion.arousal = 0.4
        return emotion

    def _create_volatile_emotion_vector(self) -> EmotionVector:
        """Create a volatile emotion vector."""
        emotion = EmotionVector()
        emotion.anger = 0.4 + random.uniform(-0.2, 0.2)
        emotion.fear = 0.3 + random.uniform(-0.2, 0.2)
        emotion.surprise = 0.5 + random.uniform(-0.3, 0.3)
        emotion.intensity = 0.7 + random.uniform(-0.2, 0.2)
        emotion.stability = 0.4 + random.uniform(-0.2, 0.2)
        emotion.valence = 0.3
        emotion.arousal = 0.7
        return emotion

    def _create_chaotic_emotion_vector(self) -> EmotionVector:
        """Create a chaotic emotion vector."""
        emotion = EmotionVector()
        # Randomly assign high values to create chaos
        emotions = [
            "joy",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "disgust",
            "trust",
            "anticipation",
        ]
        for em in emotions:
            setattr(emotion, em, random.uniform(0, 1))

        emotion.intensity = random.uniform(0.8, 1.0)
        emotion.stability = random.uniform(0.1, 0.3)
        emotion.valence = random.uniform(-0.5, 0.5)
        emotion.arousal = random.uniform(0.7, 1.0)
        return emotion

    def _calculate_drift_penalty(self, glyph: Glyph) -> float:
        """Calculate penalty for drift conditions."""
        base_penalty = 1.0 - glyph.stability_index
        collapse_penalty = glyph.collapse_risk_level * 0.5

        # Add emotional instability penalty
        emotion_instability = 1.0 - glyph.emotion_vector.stability
        emotion_penalty = emotion_instability * 0.3

        return min(0.8, base_penalty + collapse_penalty + emotion_penalty)

    def _determine_collapse_risk(
        self, glyph: Glyph, drift_score: float
    ) -> CollapseRisk:
        """Determine collapse risk level."""
        risk_score = (glyph.collapse_risk_level * 0.6) + (drift_score * 0.4)

        if risk_score < 0.1:
            return CollapseRisk.MINIMAL
        elif risk_score < 0.25:
            return CollapseRisk.LOW
        elif risk_score < 0.5:
            return CollapseRisk.MODERATE
        elif risk_score < 0.75:
            return CollapseRisk.HIGH
        else:
            return CollapseRisk.CRITICAL

    def _determine_recall_quality(self, accuracy: float) -> RecallQuality:
        """Determine recall quality level."""
        if accuracy >= 0.99:
            return RecallQuality.PERFECT
        elif accuracy >= 0.90:
            return RecallQuality.HIGH
        elif accuracy >= 0.70:
            return RecallQuality.MODERATE
        elif accuracy >= 0.50:
            return RecallQuality.DEGRADED
        elif accuracy >= 0.30:
            return RecallQuality.POOR
        else:
            return RecallQuality.FAILED

    def _calculate_correlation(
        self, x_values: List[float], y_values: List[float]
    ) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0

        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))

        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient."""
        abs_corr = abs(correlation)
        direction = "negative" if correlation < 0 else "positive"

        if abs_corr >= 0.8:
            strength = "very strong"
        elif abs_corr >= 0.6:
            strength = "strong"
        elif abs_corr >= 0.4:
            strength = "moderate"
        elif abs_corr >= 0.2:
            strength = "weak"
        else:
            strength = "very weak"

        return f"{strength} {direction} correlation"

    def _get_related_glyphs(self, target_glyph: Glyph) -> List[str]:
        """Get glyphs related to target glyph."""
        # Simple implementation - could be enhanced with actual relationship logic
        related = []
        for glyph in self.glyphs.values():
            if glyph.id != target_glyph.id:
                # Check for semantic tag overlap
                tag_overlap = len(target_glyph.semantic_tags & glyph.semantic_tags)
                if tag_overlap > 0:
                    related.append(glyph.id)

        return related[:5]  # Limit to 5 related glyphs


class TestGlyphRecallDriftCorrelation(unittest.TestCase):
    """Test suite for glyph recall and drift correlation analysis."""

    def setUp(self):
        """Set up test environment."""
        self.simulator = GlyphRecallDriftSimulator()

    def test_normal_scenario_recall(self):
        """Test recall performance in normal conditions."""
        # Create normal scenario
        self.simulator.create_test_scenario("normal")

        # Test recall for all glyphs
        total_attempts = 0
        successful_attempts = 0

        for glyph_id in self.simulator.glyphs.keys():
            attempt = self.simulator.simulate_memory_recall(glyph_id)
            total_attempts += 1

            if attempt.recall_quality in [
                RecallQuality.PERFECT,
                RecallQuality.HIGH,
                RecallQuality.MODERATE,
            ]:
                successful_attempts += 1

        success_rate = successful_attempts / total_attempts

        # Assertions for normal scenario
        self.assertGreater(
            success_rate, 0.7
        )  # Expect >70% success in normal conditions
        self.assertEqual(total_attempts, len(self.simulator.glyphs))

        print(
            f"✓ Normal scenario: {successful_attempts}/{total_attempts} successful recalls ({success_rate:.1%})"
        )

    def test_stressed_scenario_with_drift(self):
        """Test recall performance under drift conditions."""
        # Create stressed scenario
        self.simulator.create_test_scenario("stressed")

        # Apply drift events to half the glyphs
        glyph_ids = list(self.simulator.glyphs.keys())
        drift_affected_glyphs = glyph_ids[: len(glyph_ids) // 2]

        # Apply drift
        for glyph_id in drift_affected_glyphs:
            self.simulator.simulate_drift_event(
                glyph_id, magnitude=0.4, direction="negative"
            )

        # Test recall with drift conditions
        normal_recalls = []
        drift_recalls = []

        for glyph_id in glyph_ids:
            if glyph_id in drift_affected_glyphs:
                attempt = self.simulator.simulate_memory_recall(
                    glyph_id, drift_conditions=True
                )
                drift_recalls.append(attempt)
            else:
                attempt = self.simulator.simulate_memory_recall(
                    glyph_id, drift_conditions=False
                )
                normal_recalls.append(attempt)

        # Calculate average accuracy
        normal_avg = sum(a.accuracy_score for a in normal_recalls) / len(normal_recalls)
        drift_avg = sum(a.accuracy_score for a in drift_recalls) / len(drift_recalls)

        # Assertions
        self.assertGreater(normal_avg, drift_avg)  # Normal should outperform drift
        self.assertTrue(len(drift_recalls) > 0)
        self.assertTrue(len(normal_recalls) > 0)

        print(
            f"✓ Stressed scenario: Normal avg={normal_avg:.3f}, Drift avg={drift_avg:.3f}"
        )

    def test_collapse_scenario_recovery(self):
        """Test system behavior during collapse scenarios."""
        # Create collapse scenario
        self.simulator.create_test_scenario("collapse")

        # Test recall for collapse-risk glyphs
        critical_attempts = []

        for glyph_id in self.simulator.glyphs.keys():
            attempt = self.simulator.simulate_memory_recall(
                glyph_id, drift_conditions=True
            )
            critical_attempts.append(attempt)

        # Count different risk levels
        risk_distribution = {}
        for attempt in critical_attempts:
            risk = attempt.collapse_risk.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        # Verify that system detects high risk
        high_risk_count = sum(
            risk_distribution.get(risk, 0) for risk in ["high", "critical"]
        )
        total_attempts = len(critical_attempts)

        self.assertGreater(
            high_risk_count / total_attempts, 0.5
        )  # Expect >50% high risk

        print(
            f"✓ Collapse scenario: {high_risk_count}/{total_attempts} high-risk recalls detected"
        )

    def test_drift_correlation_analysis(self):
        """Test correlation analysis between recall and drift."""
        # Create mixed scenario
        self.simulator.create_test_scenario("stressed")

        # Generate various recall attempts
        for _ in range(20):
            glyph_id = random.choice(list(self.simulator.glyphs.keys()))

            # Sometimes add drift
            if random.random() < 0.5:
                self.simulator.simulate_drift_event(
                    glyph_id,
                    magnitude=random.uniform(0.1, 0.5),
                    direction=random.choice(["negative", "positive", "chaotic"]),
                )

            # Perform recall
            self.simulator.simulate_memory_recall(glyph_id, drift_conditions=True)

        # Analyze correlation
        analysis = self.simulator.analyze_recall_drift_correlation()

        # Assertions
        self.assertIn("drift_correlation", analysis)
        self.assertIn("correlation_interpretation", analysis)
        self.assertGreater(analysis["total_attempts"], 0)

        # Expect negative correlation (higher drift = lower accuracy)
        self.assertLess(analysis["drift_correlation"], 0.2)

        print(
            f"✓ Correlation analysis: {analysis['drift_correlation']:.3f} ({analysis['correlation_interpretation']})"
        )

    def test_cascade_prevention_system(self):
        """Test cascade prevention mechanisms."""
        # Create collapse scenario
        self.simulator.create_test_scenario("collapse")

        # Test cascade prevention
        prevention_results = self.simulator.test_cascade_prevention()

        # Assertions
        self.assertIn("prevention_rate", prevention_results)
        self.assertIn("system_resilience", prevention_results)
        self.assertGreater(prevention_results["tests_conducted"], 0)

        # System should have some resilience
        self.assertGreater(
            prevention_results["prevention_rate"], 0.3
        )  # At least 30% prevention

        print(
            f"✓ Cascade prevention: {prevention_results['prevention_rate']:.1%} effective, resilience={prevention_results['system_resilience']}"
        )

    def test_memory_coherence_under_drift(self):
        """Test memory coherence preservation under drift conditions."""
        # Create normal scenario
        self.simulator.create_test_scenario("normal")

        # Select one glyph for intensive drift testing
        test_glyph_id = list(self.simulator.glyphs.keys())[0]

        # Record baseline
        baseline_attempt = self.simulator.simulate_memory_recall(test_glyph_id)
        baseline_coherence = baseline_attempt.accuracy_score

        # Apply series of drift events
        drift_magnitudes = [0.1, 0.2, 0.3, 0.4, 0.5]
        coherence_degradation = []

        for magnitude in drift_magnitudes:
            self.simulator.simulate_drift_event(
                test_glyph_id, magnitude=magnitude, direction="negative"
            )
            attempt = self.simulator.simulate_memory_recall(
                test_glyph_id, drift_conditions=True
            )
            coherence_degradation.append(baseline_coherence - attempt.accuracy_score)

        # Verify coherence degradation follows expected pattern
        # Should degrade but not collapse completely
        max_degradation = max(coherence_degradation)
        min_remaining_coherence = min(
            attempt.accuracy_score
            for attempt in self.simulator.recall_attempts[-len(drift_magnitudes) :]
        )

        self.assertLess(max_degradation, 0.8)  # Should not lose >80% coherence
        self.assertGreater(min_remaining_coherence, 0.1)  # Should retain >10% coherence

        print(
            f"✓ Coherence test: Max degradation={max_degradation:.3f}, Min remaining={min_remaining_coherence:.3f}"
        )


def run_glyph_recall_drift_tests():
    """Run the complete glyph recall and drift correlation test suite."""
    print("\n" + "=" * 80)
    print("🔮 RUNNING GLYPH RECALL & DRIFT CORRELATION TESTS")
    print("=" * 80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGlyphRecallDriftCorrelation)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    print("=" * 80)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_glyph_recall_drift_tests()
    exit(0 if success else 1)


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🔮 LUKHAS AI - GLYPH RECALL & DRIFT CORRELATION TEST
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ ADVANCED TEST CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Scenario Simulation: Normal, Stressed, and Collapse test scenarios
║ • Drift Event Modeling: Magnitude, direction, and cascade simulation
║ • Recall Quality Assessment: 6-tier quality classification system
║ • Correlation Analysis: Pearson correlation between drift and recall accuracy
║ • Cascade Prevention Testing: System resilience under extreme conditions
║ • Memory Coherence Monitoring: Degradation patterns under drift stress
║ • Statistical Analytics: Comprehensive performance metrics and analysis
║ • Risk Assessment: 5-level collapse risk classification and monitoring
╠═══════════════════════════════════════════════════════════════════════════════
║ VALIDATION METRICS
╠═══════════════════════════════════════════════════════════════════════════════
║ • Recall Accuracy: Precision of glyph-based memory retrieval (0.0-1.0)
║ • Drift Correlation: Statistical relationship between drift and recall performance
║ • Cascade Prevention Rate: Effectiveness of system resilience mechanisms
║ • Memory Coherence: Preservation of semantic integrity under stress
║ • System Resilience: Overall stability classification (HIGH/MODERATE/LOW)
║ • Recovery Patterns: Analysis of system recovery from drift events
╚═══════════════════════════════════════════════════════════════════════════════
"""
