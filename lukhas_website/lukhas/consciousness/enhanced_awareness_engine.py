#!/usr/bin/env python3
"""
LUKHAS Enhanced AwarenessEngine with Meta-Cognitive Integration
==============================================================

Enhanced awareness engine that integrates meta-cognitive self-assessment
with the existing real-time awareness monitoring. Provides comprehensive
cognitive state tracking and self-correction mechanisms.

Features:
- Real-time awareness monitoring (existing functionality)
- Meta-cognitive self-assessment integration
- Cognitive load management and optimization
- Self-correction trigger detection
- Performance analytics and trend tracking

Constellation Framework: 🌊 Flow Star Integration
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from ..cognitive_core.reasoning.deep_inference_engine import InferenceResult
from .awareness_engine import AwarenessEngine
from .meta_cognitive_assessor import (
    CognitiveLoadLevel,
    MetaCognitiveAssessment,
    MetaCognitiveAssessor,
    MetaCognitiveContext,
    MetaCognitiveInsight,
)
from .types import AwarenessSnapshot, ConsciousnessState

logger = logging.getLogger(__name__)


@dataclass
class EnhancedAwarenessSnapshot:
    """Enhanced awareness snapshot with meta-cognitive data"""
    # Base awareness data
    base_snapshot: AwarenessSnapshot

    # Meta-cognitive assessment
    meta_assessment: Optional[MetaCognitiveAssessment]

    # Enhanced cognitive state
    cognitive_load_level: CognitiveLoadLevel
    self_awareness_score: float
    meta_reasoning_quality: float

    # Actionable insights
    actionable_insights: list[MetaCognitiveInsight]
    cognitive_adjustments: list[str]

    # Performance metrics
    reasoning_accuracy: float
    confidence_calibration: float
    processing_efficiency: float

    # System state
    self_correction_active: bool
    performance_trend: str

    timestamp: float = field(default_factory=time.time)


class EnhancedAwarenessEngine:
    """
    Enhanced awareness engine with integrated meta-cognitive assessment.

    Combines real-time awareness monitoring with deep cognitive self-assessment
    to provide comprehensive consciousness state tracking and optimization.
    """

    def __init__(
        self,
        awareness_config: Optional[dict[str, Any]] = None,
        metacognitive_config: Optional[dict[str, Any]] = None,
        enable_auto_adjustment: bool = True,
        assessment_frequency_ratio: float = 0.2  # Meta-assessment every 5th update
    ):
        """Initialize enhanced awareness engine."""
        self.enable_auto_adjustment = enable_auto_adjustment
        self.assessment_frequency_ratio = assessment_frequency_ratio

        # Initialize core components
        self.base_awareness = AwarenessEngine(config=awareness_config)
        self.meta_assessor = MetaCognitiveAssessor(
            assessment_frequency_hz=5.0,
            cognitive_load_window_size=10,
            performance_history_size=100,
            adaptation_learning_rate=0.1,
            enable_self_correction=True,
            **(metacognitive_config or {})
        )

        # Enhanced state tracking
        self.recent_inferences: list[InferenceResult] = []
        self.recent_thoughts: list[dict[str, Any]] = []
        self.processing_history: list[dict[str, float]] = []
        self.session_id = f"awareness_session_{int(time.time())}"

        # Auto-adjustment parameters
        self.auto_adjustment_counters = {
            'cognitive_load_adjustments': 0,
            'performance_optimizations': 0,
            'self_corrections_applied': 0
        }

        # Update tracking
        self.update_counter = 0
        self.last_meta_assessment_time = 0.0

        logger.info(
            f"EnhancedAwarenessEngine initialized: auto_adjustment={enable_auto_adjustment}, "
            f"assessment_ratio={assessment_frequency_ratio}"
        )

    async def enhanced_update(
        self,
        state: ConsciousnessState,
        signals: dict[str, Any],
        recent_inference: Optional[InferenceResult] = None,
        recent_thought: Optional[dict[str, Any]] = None
    ) -> EnhancedAwarenessSnapshot:
        """
        Enhanced awareness update with meta-cognitive assessment.

        Args:
            state: Current consciousness state
            signals: Signal data for processing
            recent_inference: Optional recent inference result
            recent_thought: Optional recent thought synthesis result

        Returns:
            EnhancedAwarenessSnapshot with comprehensive cognitive assessment
        """
        start_time = time.time()

        try:
            # Update tracking data
            if recent_inference:
                self._track_inference(recent_inference)
            if recent_thought:
                self._track_thought(recent_thought)

            # Record processing history
            processing_entry = {
                'processing_time_ms': 0.0,  # Will be updated
                'quality_score': recent_thought.get('quality_score', 0.5) if recent_thought else 0.5,
                'timestamp': start_time
            }
            self._track_processing_history(processing_entry)

            # Get base awareness snapshot
            base_snapshot = await self.base_awareness.update(state, signals)

            # Determine if we should perform meta-cognitive assessment
            should_assess = self._should_perform_meta_assessment()

            meta_assessment = None
            if should_assess:
                meta_assessment = await self._perform_meta_assessment(state)

            # Create enhanced snapshot
            enhanced_snapshot = await self._create_enhanced_snapshot(
                base_snapshot, meta_assessment, state
            )

            # Apply auto-adjustments if enabled
            if self.enable_auto_adjustment and meta_assessment:
                await self._apply_auto_adjustments(enhanced_snapshot, meta_assessment)

            # Update processing time
            processing_time = (time.time() - start_time) * 1000
            processing_entry['processing_time_ms'] = processing_time

            self.update_counter += 1

            return enhanced_snapshot

        except Exception as e:
            logger.error(f"Enhanced awareness update failed: {e}")

            # Return minimal snapshot on error
            base_snapshot = AwarenessSnapshot(
                drift_ema=0.0,
                load_factor=1.0,  # High load due to error
                signal_strength=0.0,
                signal_noise_ratio=0.0,
                processing_time_ms=(time.time() - start_time) * 1000
            )

            return EnhancedAwarenessSnapshot(
                base_snapshot=base_snapshot,
                meta_assessment=None,
                cognitive_load_level=CognitiveLoadLevel.EXCESSIVE,
                self_awareness_score=0.0,
                meta_reasoning_quality=0.0,
                actionable_insights=[],
                cognitive_adjustments=[f"Error in awareness update: {e!s}"],
                reasoning_accuracy=0.0,
                confidence_calibration=0.0,
                processing_efficiency=0.0,
                self_correction_active=True,
                performance_trend="error"
            )

    async def _perform_meta_assessment(self, state: ConsciousnessState) -> MetaCognitiveAssessment:
        """Perform meta-cognitive assessment of current state."""

        context = MetaCognitiveContext(
            reasoning_session_id=self.session_id,
            consciousness_state=state,
            recent_inferences=self.recent_inferences[-10:],  # Last 10 inferences
            recent_thoughts=self.recent_thoughts[-10:],  # Last 10 thoughts
            processing_history=self.processing_history[-20:],  # Last 20 entries
            time_budget_ms=50.0,  # Quick assessment budget
            assessment_depth="standard",
            metadata={'enhanced_awareness': True}
        )

        assessment = await self.meta_assessor.assess_cognitive_state(context)
        self.last_meta_assessment_time = time.time()

        return assessment

    async def _create_enhanced_snapshot(
        self,
        base_snapshot: AwarenessSnapshot,
        meta_assessment: Optional[MetaCognitiveAssessment],
        state: ConsciousnessState
    ) -> EnhancedAwarenessSnapshot:
        """Create enhanced awareness snapshot."""

        if meta_assessment:
            # Use meta-assessment data
            cognitive_load_level = meta_assessment.cognitive_load_assessment
            self_awareness_score = meta_assessment.self_awareness_score
            meta_reasoning_quality = meta_assessment.meta_reasoning_quality
            actionable_insights = [
                insight for insight in meta_assessment.insights
                if insight.actionable_recommendation
            ]
            cognitive_adjustments = meta_assessment.recommended_adjustments
            reasoning_accuracy = meta_assessment.performance_metrics.reasoning_accuracy
            confidence_calibration = meta_assessment.performance_metrics.confidence_calibration
            processing_efficiency = meta_assessment.performance_metrics.processing_efficiency
            self_correction_active = self.meta_assessor.self_correction_active
            performance_trend = self.meta_assessor.assessment_stats.get("performance_trend", "stable")

        else:
            # Use fallback values from base awareness and heuristics
            cognitive_load_level = self._estimate_cognitive_load(base_snapshot)
            self_awareness_score = self._estimate_self_awareness(base_snapshot)
            meta_reasoning_quality = self._estimate_reasoning_quality(base_snapshot)
            actionable_insights = []
            cognitive_adjustments = self._generate_basic_adjustments(base_snapshot)
            reasoning_accuracy = self._estimate_reasoning_accuracy()
            confidence_calibration = self._estimate_confidence_calibration()
            processing_efficiency = self._estimate_processing_efficiency(base_snapshot)
            self_correction_active = False
            performance_trend = "stable"

        return EnhancedAwarenessSnapshot(
            base_snapshot=base_snapshot,
            meta_assessment=meta_assessment,
            cognitive_load_level=cognitive_load_level,
            self_awareness_score=self_awareness_score,
            meta_reasoning_quality=meta_reasoning_quality,
            actionable_insights=actionable_insights,
            cognitive_adjustments=cognitive_adjustments,
            reasoning_accuracy=reasoning_accuracy,
            confidence_calibration=confidence_calibration,
            processing_efficiency=processing_efficiency,
            self_correction_active=self_correction_active,
            performance_trend=performance_trend
        )

    async def _apply_auto_adjustments(
        self,
        snapshot: EnhancedAwarenessSnapshot,
        meta_assessment: MetaCognitiveAssessment
    ) -> None:
        """Apply automatic cognitive adjustments based on assessment."""

        # Apply cognitive load adjustments
        if snapshot.cognitive_load_level == CognitiveLoadLevel.EXCESSIVE:
            await self._adjust_cognitive_load()
            self.auto_adjustment_counters['cognitive_load_adjustments'] += 1

        # Apply performance optimizations
        if snapshot.reasoning_accuracy < 0.7 or snapshot.processing_efficiency < 0.6:
            await self._optimize_performance(meta_assessment.performance_metrics)
            self.auto_adjustment_counters['performance_optimizations'] += 1

        # Apply self-corrections
        if snapshot.self_correction_active:
            await self._apply_self_correction(snapshot.actionable_insights)
            self.auto_adjustment_counters['self_corrections_applied'] += 1

    async def _adjust_cognitive_load(self) -> None:
        """Adjust system parameters to reduce cognitive load."""
        logger.info("Applying cognitive load adjustment")

        # Reduce inference depth for future operations
        # This would be communicated to the inference engine
        # For now, we log the recommendation
        logger.info("Recommendation: Reduce inference depth to manage cognitive load")

    async def _optimize_performance(self, performance_metrics) -> None:
        """Optimize system performance based on metrics."""
        logger.info("Applying performance optimization")

        if performance_metrics.reasoning_accuracy < 0.7:
            logger.info("Recommendation: Improve reasoning accuracy through better validation")

        if performance_metrics.processing_efficiency < 0.6:
            logger.info("Recommendation: Optimize processing pipelines for better efficiency")

    async def _apply_self_correction(self, insights: list[MetaCognitiveInsight]) -> None:
        """Apply self-correction based on meta-cognitive insights."""
        logger.info(f"Applying self-correction based on {len(insights)} insights")

        for insight in insights:
            if insight.priority == "high" and insight.actionable_recommendation:
                logger.info(f"Self-correction: {insight.actionable_recommendation}")

    def _should_perform_meta_assessment(self) -> bool:
        """Determine if meta-cognitive assessment should be performed."""

        # Perform assessment based on frequency ratio
        if self.update_counter % max(1, int(1 / self.assessment_frequency_ratio)) == 0:
            return True

        # Force assessment if significant time has passed
        return (time.time() - self.last_meta_assessment_time) > 30.0  # 30 seconds

        # Force assessment if anomalies detected in base awareness
        # (This would be determined by the base snapshot)

    def _track_inference(self, inference_result: InferenceResult) -> None:
        """Track inference result for meta-cognitive assessment."""
        self.recent_inferences.append(inference_result)

        # Keep only recent inferences
        if len(self.recent_inferences) > 20:
            self.recent_inferences.pop(0)

    def _track_thought(self, thought_result: dict[str, Any]) -> None:
        """Track thought result for meta-cognitive assessment."""
        self.recent_thoughts.append(thought_result)

        # Keep only recent thoughts
        if len(self.recent_thoughts) > 20:
            self.recent_thoughts.pop(0)

    def _track_processing_history(self, processing_entry: dict[str, float]) -> None:
        """Track processing history for performance analysis."""
        self.processing_history.append(processing_entry)

        # Keep only recent history
        if len(self.processing_history) > 50:
            self.processing_history.pop(0)

    def _estimate_cognitive_load(self, base_snapshot: AwarenessSnapshot) -> CognitiveLoadLevel:
        """Estimate cognitive load from base awareness snapshot."""
        load_factor = base_snapshot.load_factor

        if load_factor < 0.2:
            return CognitiveLoadLevel.MINIMAL
        elif load_factor < 0.4:
            return CognitiveLoadLevel.LOW
        elif load_factor < 0.6:
            return CognitiveLoadLevel.MODERATE
        elif load_factor < 0.8:
            return CognitiveLoadLevel.HIGH
        else:
            return CognitiveLoadLevel.EXCESSIVE

    def _estimate_self_awareness(self, base_snapshot: AwarenessSnapshot) -> float:
        """Estimate self-awareness score from base snapshot."""
        # Simple heuristic based on signal quality and processing efficiency
        signal_quality = base_snapshot.signal_noise_ratio
        processing_quality = 1.0 - min(1.0, base_snapshot.processing_time_ms / 100.0)

        return (signal_quality * 0.6 + processing_quality * 0.4)

    def _estimate_reasoning_quality(self, base_snapshot: AwarenessSnapshot) -> float:
        """Estimate reasoning quality from base snapshot."""
        # Heuristic based on drift and signal strength
        stability = max(0.0, 1.0 - base_snapshot.drift_ema)
        signal_strength = base_snapshot.signal_strength

        return (stability * 0.6 + signal_strength * 0.4)

    def _generate_basic_adjustments(self, base_snapshot: AwarenessSnapshot) -> list[str]:
        """Generate basic cognitive adjustments without full meta-assessment."""
        adjustments = []

        if base_snapshot.load_factor > 0.8:
            adjustments.append("High system load detected - consider reducing processing complexity")

        if base_snapshot.drift_ema > 0.7:
            adjustments.append("High state drift detected - review consciousness state stability")

        if base_snapshot.signal_noise_ratio < 0.5:
            adjustments.append("Low signal quality detected - improve signal processing")

        if not adjustments:
            adjustments.append("System operating within normal parameters")

        return adjustments

    def _estimate_reasoning_accuracy(self) -> float:
        """Estimate reasoning accuracy from recent inferences."""
        if not self.recent_inferences:
            return 0.5  # Neutral default

        successful_inferences = sum(1 for inf in self.recent_inferences if inf.success)
        return successful_inferences / len(self.recent_inferences)

    def _estimate_confidence_calibration(self) -> float:
        """Estimate confidence calibration from recent inferences."""
        if not self.recent_inferences:
            return 0.5  # Neutral default

        # Simple heuristic: higher confidence with successful results indicates good calibration
        calibrated_inferences = sum(
            1 for inf in self.recent_inferences
            if (inf.success and inf.confidence_score > 0.7) or
               (not inf.success and inf.confidence_score <= 0.7)
        )
        return calibrated_inferences / len(self.recent_inferences)

    def _estimate_processing_efficiency(self, base_snapshot: AwarenessSnapshot) -> float:
        """Estimate processing efficiency from snapshot and history."""
        # Base efficiency on processing time
        base_efficiency = max(0.0, 1.0 - base_snapshot.processing_time_ms / 100.0)  # Normalize by 100ms

        # Consider load factor
        load_penalty = base_snapshot.load_factor * 0.3

        return max(0.0, min(1.0, base_efficiency - load_penalty))

    def get_enhanced_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics."""
        base_stats = self.base_awareness.get_performance_stats()
        meta_stats = self.meta_assessor.get_performance_analytics()

        return {
            'base_awareness': base_stats,
            'meta_cognitive': meta_stats,
            'enhanced_awareness': {
                'total_updates': self.update_counter,
                'recent_inferences': len(self.recent_inferences),
                'recent_thoughts': len(self.recent_thoughts),
                'processing_history_size': len(self.processing_history),
                'auto_adjustments': dict(self.auto_adjustment_counters),
                'last_meta_assessment': self.last_meta_assessment_time
            },
            'integration_status': 'operational'
        }

    def reset_enhanced_state(self) -> None:
        """Reset enhanced state for testing or reconfiguration."""
        self.base_awareness.reset_state()
        self.recent_inferences.clear()
        self.recent_thoughts.clear()
        self.processing_history.clear()
        self.update_counter = 0
        self.last_meta_assessment_time = 0.0
        self.auto_adjustment_counters = {
            'cognitive_load_adjustments': 0,
            'performance_optimizations': 0,
            'self_corrections_applied': 0
        }


# Export for public API
__all__ = [
    "EnhancedAwarenessEngine",
    "EnhancedAwarenessSnapshot"
]
