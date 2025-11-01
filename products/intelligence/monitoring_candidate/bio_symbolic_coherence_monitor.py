#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Bio-Symbolic Coherence Monitor
==============================
Monitors and tracks the coherence between biological-inspired systems
(endocrine, hormone, homeostasis) and symbolic processing systems (GLYPHs,
consciousness, reasoning) to ensure system integration and harmony.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import structlog

from orchestration.signals.signal_bus import (
    Signal,
    SignalBus,
    SignalType,
    get_signal_bus,
)

# Support both package and direct module execution import styles for EndocrineSnapshot
try:
    from .endocrine_observability_engine import EndocrineSnapshot
except Exception:
    try:
        from monitoring.endocrine_observability_engine import EndocrineSnapshot
    except Exception:
        from endocrine_observability_engine import EndocrineSnapshot

logger = structlog.get_logger(__name__)


class CoherenceLevel(Enum):
    """Levels of bio-symbolic coherence"""

    CRITICAL = 0  # Severe misalignment, system instability
    POOR = 1  # Significant misalignment, reduced functionality
    FAIR = 2  # Some misalignment, minor issues
    GOOD = 3  # Well aligned, optimal functioning
    EXCELLENT = 4  # Perfect alignment, peak performance


class CoherenceMetric(Enum):
    """Types of coherence metrics to track"""

    HORMONE_GLYPH_ALIGNMENT = "hormone_glyph_alignment"
    STRESS_RESPONSE_COHERENCE = "stress_response_coherence"
    LEARNING_INTEGRATION = "learning_integration"
    EMOTIONAL_SYMBOLIC_SYNC = "emotional_symbolic_sync"
    DECISION_BIOMARKER_MATCH = "decision_biomarker_match"
    HOMEOSTASIS_CONSCIOUSNESS = "homeostasis_consciousness"
    PLASTICITY_SYMBOLIC_FLOW = "plasticity_symbolic_flow"
    CIRCADIAN_PROCESSING_RHYTHM = "circadian_processing_rhythm"


@dataclass
class CoherenceMeasurement:
    """Single measurement of bio-symbolic coherence"""

    metric_type: CoherenceMetric
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    coherence_score: float = 0.0  # 0.0 to 1.0
    bio_component_state: dict[str, Any] = field(default_factory=dict)
    symbolic_component_state: dict[str, Any] = field(default_factory=dict)
    alignment_factors: list[str] = field(default_factory=list)
    misalignment_factors: list[str] = field(default_factory=list)
    confidence: float = 0.8

    def get_coherence_level(self) -> CoherenceLevel:
        """Convert score to coherence level"""
        if self.coherence_score >= 0.9:
            return CoherenceLevel.EXCELLENT
        elif self.coherence_score >= 0.7:
            return CoherenceLevel.GOOD
        elif self.coherence_score >= 0.5:
            return CoherenceLevel.FAIR
        elif self.coherence_score >= 0.3:
            return CoherenceLevel.POOR
        else:
            return CoherenceLevel.CRITICAL

    # Backwards/forwards compatibility property expected by tests
    @property
    def metric_name(self) -> str:
        try:
            return self.metric_type.value
        except Exception:
            return str(self.metric_type)


@dataclass
class CoherenceReport:
    """Comprehensive coherence assessment report"""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    overall_coherence: float = 0.0
    overall_level: CoherenceLevel = CoherenceLevel.FAIR
    individual_metrics: dict[CoherenceMetric, CoherenceMeasurement] = field(default_factory=dict)
    trend_analysis: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    critical_issues: list[str] = field(default_factory=list)
    stability_index: float = 0.0


class BioSymbolicCoherenceMonitor:
    """
    Advanced monitor for bio-symbolic coherence that ensures biological-inspired
    systems and symbolic processing systems remain aligned and mutually supportive.
    """

    def __init__(
        self,
        signal_bus: Optional[SignalBus] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        # Allow optional bus for tests and fall back to global bus when available
        self.signal_bus = signal_bus or get_signal_bus()
        self.config = config or {}

        # Monitoring configuration
        self.monitoring_interval = self.config.get("coherence_monitoring_interval", 10.0)  # seconds
        self.measurement_retention = self.config.get("measurement_retention", 500)
        self.trend_window_minutes = self.config.get("trend_window_minutes", 60)

        # Data storage
        self.measurements: dict[CoherenceMetric, deque] = {
            metric: deque(maxlen=self.measurement_retention) for metric in CoherenceMetric
        }
        self.coherence_history: deque = deque(maxlen=1000)
        self.reports: deque = deque(maxlen=100)

        # State tracking for bio and symbolic systems
        self.bio_system_state: dict[str, Any] = {}
        self.symbolic_system_state: dict[str, Any] = {}
        self.last_endocrine_snapshot: Optional[EndocrineSnapshot] = None

        # Coherence thresholds and weights
        self.coherence_thresholds = {
            CoherenceMetric.HORMONE_GLYPH_ALIGNMENT: 0.6,
            CoherenceMetric.STRESS_RESPONSE_COHERENCE: 0.7,
            CoherenceMetric.LEARNING_INTEGRATION: 0.5,
            CoherenceMetric.EMOTIONAL_SYMBOLIC_SYNC: 0.6,
            CoherenceMetric.DECISION_BIOMARKER_MATCH: 0.65,
            CoherenceMetric.HOMEOSTASIS_CONSCIOUSNESS: 0.75,
            CoherenceMetric.PLASTICITY_SYMBOLIC_FLOW: 0.55,
            CoherenceMetric.CIRCADIAN_PROCESSING_RHYTHM: 0.5,
        }

        # Metric weights for overall coherence calculation
        self.metric_weights = {
            CoherenceMetric.HORMONE_GLYPH_ALIGNMENT: 0.15,
            CoherenceMetric.STRESS_RESPONSE_COHERENCE: 0.20,
            CoherenceMetric.LEARNING_INTEGRATION: 0.10,
            CoherenceMetric.EMOTIONAL_SYMBOLIC_SYNC: 0.15,
            CoherenceMetric.DECISION_BIOMARKER_MATCH: 0.15,
            CoherenceMetric.HOMEOSTASIS_CONSCIOUSNESS: 0.10,
            CoherenceMetric.PLASTICITY_SYMBOLIC_FLOW: 0.10,
            CoherenceMetric.CIRCADIAN_PROCESSING_RHYTHM: 0.05,
        }

        # Pattern detection
        self.coherence_patterns: dict[str, Any] = {}
        self.anomaly_detector = CoherenceAnomalyDetector()

        # Integration tracking
        self.integration_events: deque = deque(maxlen=200)

        logger.info(
            "BioSymbolicCoherenceMonitor initialized",
            monitoring_interval=self.monitoring_interval,
            metrics_tracked=len(CoherenceMetric),
        )

    async def initialize(self) -> bool:
        """Initialize monitor (compatibility stub for tests)."""
        return True

    async def update_bio_system_state(self, endocrine_snapshot: EndocrineSnapshot):
        """Update biological system state information"""
        self.last_endocrine_snapshot = endocrine_snapshot

        # Extract biological system state
        self.bio_system_state = {
            "hormone_levels": endocrine_snapshot.hormone_levels,
            "homeostasis_state": endocrine_snapshot.homeostasis_state,
            "system_metrics": endocrine_snapshot.system_metrics,
            "coherence_score": endocrine_snapshot.coherence_score,
            "timestamp": endocrine_snapshot.timestamp,
        }

        # Trigger coherence assessment
        await self._assess_coherence()

    async def update_symbolic_system_state(self, symbolic_data: dict[str, Any]):
        """Update symbolic system state information"""
        self.symbolic_system_state.update(
            {
                "glyph_processing_rate": symbolic_data.get("glyph_processing_rate", 0.0),
                "consciousness_level": symbolic_data.get("consciousness_level", 0.0),
                "decision_making_active": symbolic_data.get("decision_making_active", False),
                "memory_operations": symbolic_data.get("memory_operations", 0),
                "reasoning_depth": symbolic_data.get("reasoning_depth", 0.0),
                "symbolic_complexity": symbolic_data.get("symbolic_complexity", 0.0),
                "processing_load": symbolic_data.get("processing_load", 0.0),
                "timestamp": datetime.now(timezone.utc),
            }
        )

        # Trigger coherence assessment
        await self._assess_coherence()

    async def _assess_coherence(self):
        """Perform comprehensive coherence assessment"""
        if not self.bio_system_state or not self.symbolic_system_state:
            return  # Need both systems to assess coherence

        # Measure each coherence metric
        measurements = {}

        for metric in CoherenceMetric:
            measurement = await self._measure_coherence_metric(metric)
            if measurement:
                measurements[metric] = measurement
                self.measurements[metric].append(measurement)

        # Generate overall coherence report
        if measurements:
            report = await self._generate_coherence_report(measurements)
            self.reports.append(report)
            self.coherence_history.append(
                {
                    # Store ISO string for robust handling
                    "timestamp": report.timestamp.isoformat(),
                    "overall_coherence": report.overall_coherence,
                    "level": report.overall_level.value,
                }
            )

            # Check for coherence issues
            await self._check_coherence_issues(report)

            # Emit coherence signal
            await self._emit_coherence_signal(report)

    # --- Public compatibility APIs used by tests ---
    async def measure_coherence(
        self,
        bio_state: dict[str, Any],
        symbolic_state: dict[str, Any],
    ) -> list[CoherenceMeasurement]:
        """Measure coherence given raw bio/symbolic states and return measurements.

        Tests expect a list of CoherenceMeasurement items with metric_name and score.
        """
        # Update internal state directly from provided dicts
        self.bio_system_state = {
            "hormone_levels": bio_state.get("hormone_levels", {}),
            "homeostasis_state": bio_state.get("homeostasis_state", "balanced"),
            "system_metrics": bio_state.get("system_metrics", {}),
        }
        self.symbolic_system_state = dict(symbolic_state)

        results: list[CoherenceMeasurement] = []
        for metric in CoherenceMetric:
            m = await self._measure_coherence_metric(metric)
            if m:
                results.append(m)
        return results

    async def analyze_coherence_trends(self, trend_data: list[float]) -> dict[str, Any]:
        """Analyze a list of coherence values and return trend direction/strength."""
        if not trend_data:
            return {"trend_direction": "unknown", "trend_strength": 0.0}
        n = len(trend_data)
        if n < 3:
            avg = sum(trend_data) / n
            return {"trend_direction": "stable", "trend_strength": 0.0, "average": avg}
        # Compare first and last thirds
        k = max(1, n // 3)
        first_avg = sum(trend_data[:k]) / k
        last_avg = sum(trend_data[-k:]) / k
        delta = last_avg - first_avg
        if delta > 0.05:
            direction = "improving"
        elif delta < -0.05:
            direction = "declining"
        else:
            direction = "stable"
        strength = min(1.0, max(0.0, abs(delta)))
        return {
            "trend_direction": direction,
            "trend_strength": strength,
            "first_avg": first_avg,
            "last_avg": last_avg,
        }

    async def detect_alignment_issues(
        self,
        bio_state: dict[str, Any],
        symbolic_state: dict[str, Any],
    ) -> list[str]:
        """Detect alignment issues based on measured coherence metrics."""
        measurements = await self.measure_coherence(bio_state, symbolic_state)
        issues: list[str] = []
        for m in measurements:
            if m.coherence_score < 0.5:
                issues.append(f"Low coherence: {m.metric_type.value} ({m.coherence_score:.2f})")
                # Include a representative misalignment factor if available
                if m.misalignment_factors:
                    issues.append(f" - {m.misalignment_factors[0]}")
        return issues

    async def _measure_coherence_metric(self, metric: CoherenceMetric) -> Optional[CoherenceMeasurement]:
        """Measure a specific coherence metric"""

        try:
            if metric == CoherenceMetric.HORMONE_GLYPH_ALIGNMENT:
                return await self._measure_hormone_glyph_alignment()

            elif metric == CoherenceMetric.STRESS_RESPONSE_COHERENCE:
                return await self._measure_stress_response_coherence()

            elif metric == CoherenceMetric.LEARNING_INTEGRATION:
                return await self._measure_learning_integration()

            elif metric == CoherenceMetric.EMOTIONAL_SYMBOLIC_SYNC:
                return await self._measure_emotional_symbolic_sync()

            elif metric == CoherenceMetric.DECISION_BIOMARKER_MATCH:
                return await self._measure_decision_biomarker_match()

            elif metric == CoherenceMetric.HOMEOSTASIS_CONSCIOUSNESS:
                return await self._measure_homeostasis_consciousness()

            elif metric == CoherenceMetric.PLASTICITY_SYMBOLIC_FLOW:
                return await self._measure_plasticity_symbolic_flow()

            elif metric == CoherenceMetric.CIRCADIAN_PROCESSING_RHYTHM:
                return await self._measure_circadian_processing_rhythm()

        except Exception as e:
            logger.error(
                "Error measuring coherence metric",
                metric=metric.value,
                error=str(e),
            )

        return None

    async def _measure_hormone_glyph_alignment(self) -> CoherenceMeasurement:
        """Measure alignment between hormone levels and GLYPH processing patterns"""

        hormone_levels = self.bio_system_state.get("hormone_levels", {})
        glyph_rate = self.symbolic_system_state.get("glyph_processing_rate", 0.0)
        processing_load = self.symbolic_system_state.get("processing_load", 0.0)

        # Calculate expected GLYPH processing rate based on hormone state
        dopamine = hormone_levels.get("dopamine", 0.5)
        serotonin = hormone_levels.get("serotonin", 0.5)
        cortisol = hormone_levels.get("cortisol", 0.5)

        # Expected processing rate based on hormone balance
        expected_rate = (dopamine * 0.4 + serotonin * 0.3 - cortisol * 0.3) * 0.5 + 0.5
        expected_rate = max(0.1, min(1.0, expected_rate))

        # Compare with actual processing patterns
        rate_alignment = 1.0 - abs(glyph_rate - expected_rate)

        # Factor in processing load coherence
        load_coherence = 1.0 - abs(processing_load - (cortisol * 0.7 + 0.3))

        # Overall alignment score
        coherence_score = (rate_alignment * 0.7) + (load_coherence * 0.3)

        alignment_factors = []
        misalignment_factors = []

        if rate_alignment > 0.7:
            alignment_factors.append("GLYPH processing rate matches hormone state")
        else:
            misalignment_factors.append("GLYPH processing rate misaligned with hormones")

        if load_coherence > 0.7:
            alignment_factors.append("Processing load coherent with stress hormones")
        else:
            misalignment_factors.append("Processing load doesn't match stress indicators")

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.HORMONE_GLYPH_ALIGNMENT,
            coherence_score=coherence_score,
            bio_component_state={"hormones": hormone_levels},
            symbolic_component_state={
                "glyph_rate": glyph_rate,
                "load": processing_load,
            },
            alignment_factors=alignment_factors,
            misalignment_factors=misalignment_factors,
        )

    async def _measure_stress_response_coherence(self) -> CoherenceMeasurement:
        """Measure coherence between biological stress response and symbolic processing"""

        hormone_levels = self.bio_system_state.get("hormone_levels", {})
        homeostasis_state = self.bio_system_state.get("homeostasis_state", "balanced")

        consciousness_level = self.symbolic_system_state.get("consciousness_level", 0.5)
        decision_making_active = self.symbolic_system_state.get("decision_making_active", False)
        reasoning_depth = self.symbolic_system_state.get("reasoning_depth", 0.5)

        # Calculate biological stress level
        cortisol = hormone_levels.get("cortisol", 0.5)
        adrenaline = hormone_levels.get("adrenaline", 0.5)
        gaba = hormone_levels.get("gaba", 0.5)

        bio_stress = (cortisol + adrenaline - gaba) / 2
        bio_stress = max(0.0, min(1.0, bio_stress))

        # Calculate symbolic system stress response
        # High consciousness + active decision making should correlate with stress
        expected_consciousness = 0.5 + (bio_stress * 0.4)  # Stress increases awareness
        expected_reasoning = 0.5 + (bio_stress * 0.3)  # Stress increases reasoning depth

        consciousness_alignment = 1.0 - abs(consciousness_level - expected_consciousness)
        reasoning_alignment = 1.0 - abs(reasoning_depth - expected_reasoning)

        # Check if decision making is appropriately activated during stress
        decision_coherence = 1.0
        if bio_stress > 0.6 and not decision_making_active:
            decision_coherence = 0.3  # Should be making decisions under stress
        elif bio_stress < 0.3 and decision_making_active:
            decision_coherence = 0.7  # Shouldn't be overly active when relaxed

        coherence_score = consciousness_alignment * 0.4 + reasoning_alignment * 0.4 + decision_coherence * 0.2

        alignment_factors = []
        misalignment_factors = []

        if consciousness_alignment > 0.7:
            alignment_factors.append("Consciousness level matches stress state")
        else:
            misalignment_factors.append("Consciousness not aligned with biological stress")

        if reasoning_alignment > 0.7:
            alignment_factors.append("Reasoning depth appropriate for stress level")
        else:
            misalignment_factors.append("Reasoning depth misaligned with stress")

        if decision_coherence > 0.8:
            alignment_factors.append("Decision making coherent with stress response")
        else:
            misalignment_factors.append("Decision making not matching stress state")

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.STRESS_RESPONSE_COHERENCE,
            coherence_score=coherence_score,
            bio_component_state={
                "stress_level": bio_stress,
                "homeostasis": homeostasis_state,
            },
            symbolic_component_state={
                "consciousness": consciousness_level,
                "reasoning": reasoning_depth,
                "decision_active": decision_making_active,
            },
            alignment_factors=alignment_factors,
            misalignment_factors=misalignment_factors,
        )

    async def _measure_learning_integration(self) -> CoherenceMeasurement:
        """Measure integration between biological plasticity and symbolic learning"""

        # This would measure how well biological adaptation triggers
        # are integrated with symbolic learning processes

        hormone_levels = self.bio_system_state.get("hormone_levels", {})
        memory_operations = self.symbolic_system_state.get("memory_operations", 0)

        # Learning-related hormones
        dopamine = hormone_levels.get("dopamine", 0.5)  # Reward/learning
        serotonin = hormone_levels.get("serotonin", 0.5)  # Mood/learning state

        # Expected memory activity based on learning hormones
        expected_memory_ops = (dopamine * 0.6 + serotonin * 0.4) * 10  # Scale to ops count

        # Compare with actual memory operations
        memory_alignment = min(1.0, memory_operations / expected_memory_ops) if expected_memory_ops > 0 else 0.5

        # Base coherence on memory alignment
        coherence_score = memory_alignment

        alignment_factors: list[str] = []
        misalignment_factors: list[str] = []

        if memory_alignment > 0.7:
            alignment_factors.append("Memory operations aligned with learning hormones")
        else:
            misalignment_factors.append("Memory activity not matching learning state")

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.LEARNING_INTEGRATION,
            coherence_score=coherence_score,
            bio_component_state={"learning_hormones": {"dopamine": dopamine, "serotonin": serotonin}},
            symbolic_component_state={"memory_ops": memory_operations},
            alignment_factors=alignment_factors,
            misalignment_factors=misalignment_factors,
            confidence=0.6,  # Lower confidence as this is complex to measure
        )

    async def _measure_emotional_symbolic_sync(self) -> CoherenceMeasurement:
        """Measure synchronization between emotional state and symbolic processing"""

        hormone_levels = self.bio_system_state.get("hormone_levels", {})
        symbolic_complexity = self.symbolic_system_state.get("symbolic_complexity", 0.5)

        # Emotional state from hormones
        serotonin = hormone_levels.get("serotonin", 0.5)  # Mood stabilizer
        dopamine = hormone_levels.get("dopamine", 0.5)  # Motivation/reward
        oxytocin = hormone_levels.get("oxytocin", 0.5)  # Social bonding
        cortisol = hormone_levels.get("cortisol", 0.5)  # Stress

        # Calculate emotional valence
        positive_emotions = (serotonin + dopamine + oxytocin) / 3
        negative_emotions = cortisol
        emotional_valence = positive_emotions - negative_emotions + 0.5  # Normalize to 0-1
        emotional_valence = max(0.0, min(1.0, emotional_valence))

        # Expected symbolic complexity based on emotional state
        # Positive emotions might increase creative/complex processing
        # Negative emotions might reduce complexity (focus on immediate concerns)
        expected_complexity = 0.3 + (emotional_valence * 0.4)  # Range: 0.3-0.7

        complexity_alignment = 1.0 - abs(symbolic_complexity - expected_complexity)

        coherence_score = complexity_alignment

        alignment_factors = []
        misalignment_factors = []

        if complexity_alignment > 0.7:
            alignment_factors.append("Symbolic processing complexity matches emotional state")
        else:
            misalignment_factors.append("Processing complexity not aligned with emotions")

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.EMOTIONAL_SYMBOLIC_SYNC,
            coherence_score=coherence_score,
            bio_component_state={
                "emotional_valence": emotional_valence,
                "hormones": hormone_levels,
            },
            symbolic_component_state={"complexity": symbolic_complexity},
            alignment_factors=alignment_factors,
            misalignment_factors=misalignment_factors,
        )

    async def _measure_decision_biomarker_match(self) -> CoherenceMeasurement:
        """Measure match between decision-making activity and biological markers"""

        hormone_levels = self.bio_system_state.get("hormone_levels", {})
        decision_making_active = self.symbolic_system_state.get("decision_making_active", False)
        reasoning_depth = self.symbolic_system_state.get("reasoning_depth", 0.5)

        # Decision-relevant hormones
        dopamine = hormone_levels.get("dopamine", 0.5)  # Motivation for decisions
        cortisol = hormone_levels.get("cortisol", 0.5)  # Stress driving decisions
        serotonin = hormone_levels.get("serotonin", 0.5)  # Confidence in decisions

        # Calculate expected decision activity
        decision_drive = dopamine * 0.4 + cortisol * 0.3 + serotonin * 0.3

        # Expected reasoning depth
        expected_reasoning = 0.3 + (decision_drive * 0.4)

        # Calculate coherence
        decision_coherence = 1.0
        if decision_drive > 0.6 and not decision_making_active:
            decision_coherence = 0.4
        elif decision_drive < 0.4 and decision_making_active:
            decision_coherence = 0.6

        reasoning_coherence = 1.0 - abs(reasoning_depth - expected_reasoning)

        coherence_score = (decision_coherence * 0.6) + (reasoning_coherence * 0.4)

        alignment_factors = []
        misalignment_factors = []

        if decision_coherence > 0.7:
            alignment_factors.append("Decision activity matches biological drive")
        else:
            misalignment_factors.append("Decision activity misaligned with bio markers")

        if reasoning_coherence > 0.7:
            alignment_factors.append("Reasoning depth appropriate for hormone state")
        else:
            misalignment_factors.append("Reasoning depth not matching biological state")

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.DECISION_BIOMARKER_MATCH,
            coherence_score=coherence_score,
            bio_component_state={
                "decision_drive": decision_drive,
                "hormones": hormone_levels,
            },
            symbolic_component_state={
                "decision_active": decision_making_active,
                "reasoning": reasoning_depth,
            },
            alignment_factors=alignment_factors,
            misalignment_factors=misalignment_factors,
        )

    # Simplified implementations for remaining metrics
    async def _measure_homeostasis_consciousness(self) -> CoherenceMeasurement:
        """Measure coherence between homeostasis state and consciousness level"""
        homeostasis_state = self.bio_system_state.get("homeostasis_state", "balanced")
        consciousness_level = self.symbolic_system_state.get("consciousness_level", 0.5)

        # Map homeostasis states to expected consciousness levels
        homeostasis_consciousness_map = {
            "balanced": 0.7,
            "stressed": 0.9,
            "overloaded": 0.8,
            "underutilized": 0.4,
            "recovering": 0.5,
            "critical": 1.0,
        }

        expected_consciousness = homeostasis_consciousness_map.get(homeostasis_state, 0.5)
        coherence_score = 1.0 - abs(consciousness_level - expected_consciousness)

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.HOMEOSTASIS_CONSCIOUSNESS,
            coherence_score=coherence_score,
            bio_component_state={"homeostasis": homeostasis_state},
            symbolic_component_state={"consciousness": consciousness_level},
        )

    async def _measure_plasticity_symbolic_flow(self) -> CoherenceMeasurement:
        """Measure flow between plasticity adaptations and symbolic processing"""
        # Simplified measurement
        coherence_score = 0.7  # Mock value

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.PLASTICITY_SYMBOLIC_FLOW,
            coherence_score=coherence_score,
            bio_component_state={},
            symbolic_component_state={},
        )

    async def _measure_circadian_processing_rhythm(self) -> CoherenceMeasurement:
        """Measure alignment between circadian rhythms and processing patterns"""
        hormone_levels = self.bio_system_state.get("hormone_levels", {})
        processing_load = self.symbolic_system_state.get("processing_load", 0.5)

        # Use melatonin as circadian indicator
        melatonin = hormone_levels.get("melatonin", 0.5)

        # Expected processing load based on circadian state
        # High melatonin = should have lower processing (rest time)
        expected_load = 1.0 - melatonin

        coherence_score = 1.0 - abs(processing_load - expected_load)

        return CoherenceMeasurement(
            metric_type=CoherenceMetric.CIRCADIAN_PROCESSING_RHYTHM,
            coherence_score=coherence_score,
            bio_component_state={"melatonin": melatonin},
            symbolic_component_state={"processing_load": processing_load},
        )

    async def _generate_coherence_report(
        self, measurements: dict[CoherenceMetric, CoherenceMeasurement]
    ) -> CoherenceReport:
        """Generate comprehensive coherence report"""

        # Calculate overall coherence as weighted average
        total_weighted_score = 0.0
        total_weight = 0.0

        for metric, measurement in measurements.items():
            weight = self.metric_weights.get(metric, 0.1)
            total_weighted_score += measurement.coherence_score * weight
            total_weight += weight

        overall_coherence = total_weighted_score / total_weight if total_weight > 0 else 0.5

        # Determine overall level
        overall_level = CoherenceLevel.FAIR
        if overall_coherence >= 0.9:
            overall_level = CoherenceLevel.EXCELLENT
        elif overall_coherence >= 0.7:
            overall_level = CoherenceLevel.GOOD
        elif overall_coherence >= 0.5:
            overall_level = CoherenceLevel.FAIR
        elif overall_coherence >= 0.3:
            overall_level = CoherenceLevel.POOR
        else:
            overall_level = CoherenceLevel.CRITICAL

        # Generate trend analysis
        trend_analysis = await self._analyze_coherence_trends()

        # Generate recommendations
        recommendations = await self._generate_recommendations(measurements, overall_level)

        # Identify critical issues
        critical_issues = []
        for metric, measurement in measurements.items():
            if measurement.coherence_score < 0.3:
                critical_issues.append(f"{metric.value} critically low: {measurement.coherence_score:.2f}")

        # Calculate stability index
        stability_index = await self._calculate_stability_index()

        return CoherenceReport(
            overall_coherence=overall_coherence,
            overall_level=overall_level,
            individual_metrics=measurements,
            trend_analysis=trend_analysis,
            recommendations=recommendations,
            critical_issues=critical_issues,
            stability_index=stability_index,
        )

    async def _analyze_coherence_trends(self) -> dict[str, Any]:
        """Analyze coherence trends over time"""
        if len(self.coherence_history) < 5:
            return {"trend": "insufficient_data", "direction": "stable"}

        recent_scores = [entry["overall_coherence"] for entry in list(self.coherence_history)[-10:]]

        # Simple trend analysis
        if len(recent_scores) >= 3:
            first_third = sum(recent_scores[: len(recent_scores) // 3])
            last_third = sum(recent_scores[-len(recent_scores) // 3 :])

            if last_third > first_third * 1.1:
                trend = "improving"
            elif last_third < first_third * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "direction": trend,
            "recent_average": sum(recent_scores) / len(recent_scores),
            "variance": sum((x - sum(recent_scores) / len(recent_scores)) ** 2 for x in recent_scores)
            / len(recent_scores),
        }

    async def _generate_recommendations(
        self,
        measurements: dict[CoherenceMetric, CoherenceMeasurement],
        overall_level: CoherenceLevel,
    ) -> list[str]:
        """Generate recommendations for improving coherence"""
        recommendations = []

        # Overall level recommendations
        if overall_level in [CoherenceLevel.CRITICAL, CoherenceLevel.POOR]:
            recommendations.append("System requires immediate attention to restore bio-symbolic alignment")
            recommendations.append("Consider reducing system load and focusing on core functions")

        # Metric-specific recommendations
        for metric, measurement in measurements.items():
            if measurement.coherence_score < 0.5:
                if metric == CoherenceMetric.HORMONE_GLYPH_ALIGNMENT:
                    recommendations.append("Adjust GLYPH processing rate to match current hormone state")
                elif metric == CoherenceMetric.STRESS_RESPONSE_COHERENCE:
                    recommendations.append("Calibrate consciousness and decision systems to stress levels")
                elif metric == CoherenceMetric.EMOTIONAL_SYMBOLIC_SYNC:
                    recommendations.append("Balance symbolic processing complexity with emotional state")

        return recommendations

    async def _calculate_stability_index(self) -> float:
        """Calculate stability index based on coherence variance"""
        if len(self.coherence_history) < 5:
            return 0.5

        recent_scores = [entry["overall_coherence"] for entry in list(self.coherence_history)[-20:]]

        if not recent_scores:
            return 0.5

        mean_score = sum(recent_scores) / len(recent_scores)
        variance = sum((x - mean_score) ** 2 for x in recent_scores) / len(recent_scores)

        # Stability is inverse of variance (lower variance = higher stability)
        stability = 1.0 - min(1.0, variance * 4)  # Scale variance

        return max(0.0, min(1.0, stability))

    async def _check_coherence_issues(self, report: CoherenceReport):
        """Check for coherence issues and trigger alerts if needed"""

        if report.overall_level == CoherenceLevel.CRITICAL:
            logger.critical(
                "Critical bio-symbolic coherence detected",
                overall_coherence=report.overall_coherence,
                critical_issues=report.critical_issues,
            )

            # Emit critical alert signal
            signal = Signal(
                name=SignalType.ALERT,
                source="bio_symbolic_coherence_monitor",
                level=1.0,
                metadata={
                    "alert_type": "critical_coherence",
                    "coherence_level": report.overall_coherence,
                    "issues": report.critical_issues,
                },
            )
            self.signal_bus.publish(signal)

        elif report.overall_level == CoherenceLevel.POOR:
            logger.warning(
                "Poor bio-symbolic coherence detected",
                overall_coherence=report.overall_coherence,
                recommendations=report.recommendations,
            )

    async def _emit_coherence_signal(self, report: CoherenceReport):
        """Emit coherence status signal for other systems"""

        signal = Signal(
            name=SignalType.COHERENCE,
            source="bio_symbolic_coherence_monitor",
            level=report.overall_coherence,
            metadata={
                "coherence_level": report.overall_level.value,
                "stability_index": report.stability_index,
                "critical_issues": len(report.critical_issues),
                "timestamp": report.timestamp.isoformat(),
            },
        )

        self.signal_bus.publish(signal)

    # Public API methods
    def get_current_coherence(self) -> Optional[CoherenceReport]:
        """Get the most recent coherence report"""
        return self.reports[-1] if self.reports else None

    def get_coherence_trend(self, lookback_minutes: int = 60) -> list[dict[str, Any]]:
        """Get coherence trend data"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes)

        return [
            entry
            for entry in self.coherence_history
            if (
                datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                if isinstance(entry.get("timestamp"), str)
                else entry.get("timestamp", datetime.now(timezone.utc))
            )
            > cutoff_time
        ]

    def get_metric_history(self, metric: CoherenceMetric, lookback_points: int = 50) -> list[CoherenceMeasurement]:
        """Get history for a specific coherence metric"""
        measurements = self.measurements[metric]
        return list(measurements)[-lookback_points:]

    def get_coherence_statistics(self) -> dict[str, Any]:
        """Get coherence monitoring statistics"""
        current_report = self.get_current_coherence()

        return {
            "current_coherence": (current_report.overall_coherence if current_report else 0.0),
            "current_level": (current_report.overall_level.name if current_report else "UNKNOWN"),
            "stability_index": (current_report.stability_index if current_report else 0.0),
            "total_measurements": sum(len(measurements) for measurements in self.measurements.values()),
            "critical_issues_count": (len(current_report.critical_issues) if current_report else 0),
            "metrics_tracked": len(CoherenceMetric),
            "monitoring_duration_hours": (
                (datetime.now(timezone.utc) - self.coherence_history[0]["timestamp"]).total_seconds() / 3600
                if self.coherence_history
                else 0
            ),
        }


class CoherenceAnomalyDetector:
    """Detects anomalies in bio-symbolic coherence patterns"""

    def __init__(self):
        self.baseline_patterns = {}
        self.anomaly_threshold = 0.3

    def detect_anomalies(self, measurements: dict[CoherenceMetric, CoherenceMeasurement]) -> list[str]:
        """Detect coherence anomalies"""
        anomalies = []

        for metric, measurement in measurements.items():
            if measurement.coherence_score < self.anomaly_threshold:
                anomalies.append(f"Anomaly detected in {metric.value}: score {measurement.coherence_score:.2f}")

        return anomalies


# Factory function
def create_bio_symbolic_coherence_monitor(
    signal_bus: SignalBus, config: Optional[dict[str, Any]] = None
) -> BioSymbolicCoherenceMonitor:
    """Create and return a BioSymbolicCoherenceMonitor instance"""
    return BioSymbolicCoherenceMonitor(signal_bus, config)


# --- Compatibility/public API methods expected by tests ---

# Note: The following methods are appended at the end of the file to avoid
# disrupting existing logic. They delegate to internal measurement helpers.
