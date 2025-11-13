#!/usr/bin/env python3
"""
LUKHAS Meta-Cognitive Self-Assessment Engine
===========================================

Advanced meta-cognitive assessment system for self-reflection on reasoning
processes, thought quality, and cognitive performance. Integrates with the
AwarenessEngine to provide comprehensive cognitive monitoring.

Features:
- Real-time reasoning quality assessment
- Cognitive load monitoring and management
- Self-correction mechanism detection
- Reasoning strategy effectiveness evaluation
- Performance feedback loops
- Meta-reasoning about reasoning processes

Performance Target: T4/0.01% compliance with sub-50ms assessment cycles
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ..cognitive_core.reasoning.deep_inference_engine import InferenceResult
from .types import ConsciousnessState

logger = logging.getLogger(__name__)


class MetaCognitiveAspect(Enum):
    """Aspects of meta-cognitive assessment"""
    REASONING_QUALITY = "reasoning_quality"
    LOGICAL_COHERENCE = "logical_coherence"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    COGNITIVE_EFFICIENCY = "cognitive_efficiency"
    ERROR_DETECTION = "error_detection"
    STRATEGY_EFFECTIVENESS = "strategy_effectiveness"
    LEARNING_ADAPTATION = "learning_adaptation"
    SELF_AWARENESS = "self_awareness"


class CognitiveLoadLevel(Enum):
    """Levels of cognitive load"""
    MINIMAL = "minimal"      # < 20% capacity
    LOW = "low"             # 20-40% capacity
    MODERATE = "moderate"   # 40-60% capacity
    HIGH = "high"          # 60-80% capacity
    EXCESSIVE = "excessive" # > 80% capacity


@dataclass
class MetaCognitiveContext:
    """Context for meta-cognitive assessment"""
    reasoning_session_id: str
    consciousness_state: Optional[ConsciousnessState]
    recent_inferences: list[InferenceResult]
    recent_thoughts: list[dict[str, Any]]
    processing_history: list[dict[str, float]]
    time_budget_ms: float
    assessment_depth: str = "standard"  # standard, deep, minimal
    focus_aspects: Optional[list[MetaCognitiveAspect]] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitivePerformanceMetrics:
    """Metrics for cognitive performance assessment"""
    reasoning_accuracy: float
    reasoning_depth_adequacy: float
    confidence_calibration: float
    processing_efficiency: float
    error_detection_rate: float
    strategy_success_rate: float
    cognitive_load: float
    adaptation_score: float
    overall_performance: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class MetaCognitiveInsight:
    """Insight generated through meta-cognitive reflection"""
    insight_id: str
    aspect: MetaCognitiveAspect
    observation: str
    confidence: float
    actionable_recommendation: Optional[str]
    evidence: dict[str, Any]
    priority: str  # high, medium, low
    timestamp: float = field(default_factory=time.time)


@dataclass
class MetaCognitiveAssessment:
    """Complete meta-cognitive assessment result"""
    session_id: str
    performance_metrics: CognitivePerformanceMetrics
    insights: list[MetaCognitiveInsight]
    cognitive_load_assessment: CognitiveLoadLevel
    recommended_adjustments: list[str]
    self_awareness_score: float
    meta_reasoning_quality: float
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class MetaCognitiveAssessor:
    """
    Meta-cognitive self-assessment engine for advanced cognitive monitoring.

    Provides real-time assessment of reasoning processes, cognitive load
    monitoring, and adaptive feedback for cognitive system optimization.
    """

    def __init__(
        self,
        assessment_frequency_hz: float = 5.0,  # 5 assessments per second
        cognitive_load_window_size: int = 10,
        performance_history_size: int = 100,
        adaptation_learning_rate: float = 0.1,
        enable_self_correction: bool = True
    ):
        """Initialize meta-cognitive assessor."""
        self.assessment_frequency_hz = assessment_frequency_hz
        self.cognitive_load_window_size = cognitive_load_window_size
        self.performance_history_size = performance_history_size
        self.adaptation_learning_rate = adaptation_learning_rate
        self.enable_self_correction = enable_self_correction

        # Performance tracking
        self.performance_history: list[CognitivePerformanceMetrics] = []
        self.cognitive_load_window: list[float] = []
        self.strategy_effectiveness_tracker: dict[str, list[float]] = {}

        # Meta-cognitive state
        self.current_cognitive_load = CognitiveLoadLevel.LOW
        self.meta_awareness_level = 0.8
        self.self_correction_active = False

        # Assessment statistics
        self.assessment_stats = {
            "total_assessments": 0,
            "successful_assessments": 0,
            "insights_generated": 0,
            "self_corrections_triggered": 0,
            "avg_assessment_time_ms": 0.0,
            "performance_trend": "stable"  # improving, stable, declining
        }

        logger.info(
            f"MetaCognitiveAssessor initialized: frequency={assessment_frequency_hz}Hz, "
            f"self_correction={enable_self_correction}"
        )

    async def assess_cognitive_state(self, context: MetaCognitiveContext) -> MetaCognitiveAssessment:
        """
        Perform comprehensive meta-cognitive assessment of current cognitive state.

        Args:
            context: Meta-cognitive context with reasoning history and state

        Returns:
            MetaCognitiveAssessment with insights and recommendations
        """
        start_time = time.time()

        try:
            # Calculate cognitive performance metrics
            performance_metrics = await self._calculate_performance_metrics(context)

            # Assess cognitive load
            cognitive_load = await self._assess_cognitive_load(context)

            # Generate meta-cognitive insights
            insights = await self._generate_meta_insights(context, performance_metrics)

            # Calculate self-awareness score
            self_awareness_score = await self._calculate_self_awareness(context, insights)

            # Assess meta-reasoning quality
            meta_reasoning_quality = await self._assess_meta_reasoning_quality(
                context, performance_metrics, insights
            )

            # Generate recommendations
            recommendations = await self._generate_cognitive_adjustments(
                performance_metrics, cognitive_load, insights
            )

            # Build final assessment
            processing_time = (time.time() - start_time) * 1000

            assessment = MetaCognitiveAssessment(
                session_id=context.reasoning_session_id,
                performance_metrics=performance_metrics,
                insights=insights,
                cognitive_load_assessment=cognitive_load,
                recommended_adjustments=recommendations,
                self_awareness_score=self_awareness_score,
                meta_reasoning_quality=meta_reasoning_quality,
                processing_time_ms=processing_time,
                success=True
            )

            # Update tracking and statistics
            self._update_performance_tracking(performance_metrics, cognitive_load)
            self._update_assessment_stats(assessment, success=True)

            # Trigger self-correction if needed
            if self.enable_self_correction:
                await self._check_self_correction_triggers(assessment)

            return assessment

        except Exception as e:
            logger.error(f"Meta-cognitive assessment failed: {e}")
            processing_time = (time.time() - start_time) * 1000

            error_assessment = MetaCognitiveAssessment(
                session_id=context.reasoning_session_id,
                performance_metrics=CognitivePerformanceMetrics(
                    reasoning_accuracy=0.0,
                    reasoning_depth_adequacy=0.0,
                    confidence_calibration=0.0,
                    processing_efficiency=0.0,
                    error_detection_rate=0.0,
                    strategy_success_rate=0.0,
                    cognitive_load=1.0,
                    adaptation_score=0.0,
                    overall_performance=0.0
                ),
                insights=[],
                cognitive_load_assessment=CognitiveLoadLevel.EXCESSIVE,
                recommended_adjustments=[f"Error in assessment: {e!s}"],
                self_awareness_score=0.0,
                meta_reasoning_quality=0.0,
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )

            self._update_assessment_stats(error_assessment, success=False)
            return error_assessment

    async def _calculate_performance_metrics(
        self, context: MetaCognitiveContext
    ) -> CognitivePerformanceMetrics:
        """Calculate comprehensive cognitive performance metrics."""

        # Reasoning accuracy from recent inferences
        reasoning_accuracy = await self._assess_reasoning_accuracy(context.recent_inferences)

        # Reasoning depth adequacy
        depth_adequacy = await self._assess_depth_adequacy(context.recent_inferences)

        # Confidence calibration
        confidence_calibration = await self._assess_confidence_calibration(context.recent_inferences)

        # Processing efficiency
        processing_efficiency = await self._assess_processing_efficiency(context.processing_history)

        # Error detection rate
        error_detection_rate = await self._assess_error_detection(context.recent_inferences)

        # Strategy effectiveness
        strategy_success_rate = await self._assess_strategy_effectiveness(
            context.recent_inferences, context.recent_thoughts
        )

        # Cognitive load
        cognitive_load = await self._calculate_current_cognitive_load(context)

        # Adaptation score
        adaptation_score = await self._assess_learning_adaptation(context)

        # Overall performance (weighted combination)
        overall_performance = (
            reasoning_accuracy * 0.25 +
            confidence_calibration * 0.2 +
            processing_efficiency * 0.15 +
            error_detection_rate * 0.15 +
            strategy_success_rate * 0.15 +
            (1.0 - cognitive_load) * 0.1  # Lower load is better
        )

        return CognitivePerformanceMetrics(
            reasoning_accuracy=reasoning_accuracy,
            reasoning_depth_adequacy=depth_adequacy,
            confidence_calibration=confidence_calibration,
            processing_efficiency=processing_efficiency,
            error_detection_rate=error_detection_rate,
            strategy_success_rate=strategy_success_rate,
            cognitive_load=cognitive_load,
            adaptation_score=adaptation_score,
            overall_performance=overall_performance
        )

    async def _assess_reasoning_accuracy(self, recent_inferences: list[InferenceResult]) -> float:
        """Assess accuracy of recent reasoning processes."""
        if not recent_inferences:
            return 0.5  # Neutral when no data

        accuracy_scores = []
        for inference in recent_inferences:
            # Base accuracy on success rate and contradiction detection
            base_score = 1.0 if inference.success else 0.0

            # Adjust for contradiction detection (good detection improves score)
            if inference.contradictions_detected > 0:
                # If contradictions detected and resolved successfully
                if inference.success:
                    base_score += 0.1  # Bonus for good error detection
                else:
                    base_score -= 0.2  # Penalty for unresolved contradictions

            # Consider reasoning quality
            if hasattr(inference, 'reasoning_quality'):
                base_score = (base_score + inference.reasoning_quality) / 2

            accuracy_scores.append(max(0.0, min(1.0, base_score)))

        return statistics.mean(accuracy_scores)

    async def _assess_depth_adequacy(self, recent_inferences: list[InferenceResult]) -> float:
        """Assess if reasoning depth is adequate for the problems tackled."""
        if not recent_inferences:
            return 0.5

        depth_scores = []
        for inference in recent_inferences:
            max_depth = inference.max_depth_explored
            total_steps = inference.total_steps

            # Simple heuristic: adequate depth based on problem complexity
            if total_steps == 0:
                depth_score = 0.0
            elif max_depth < 3:
                depth_score = 0.4  # Shallow reasoning
            elif max_depth < 7:
                depth_score = 0.7  # Moderate depth
            elif max_depth < 12:
                depth_score = 0.9  # Good depth
            else:
                depth_score = 1.0  # Excellent depth

            # Adjust for efficiency (depth vs steps ratio)
            if total_steps > 0:
                efficiency_factor = min(1.0, max_depth / (total_steps * 0.5))
                depth_score *= efficiency_factor

            depth_scores.append(depth_score)

        return statistics.mean(depth_scores)

    async def _assess_confidence_calibration(self, recent_inferences: list[InferenceResult]) -> float:
        """Assess how well confidence scores match actual performance."""
        if not recent_inferences:
            return 0.5

        calibration_scores = []
        for inference in recent_inferences:
            confidence = inference.confidence_score
            actual_quality = inference.reasoning_quality if hasattr(inference, 'reasoning_quality') else 0.5

            # Good calibration means confidence matches quality
            calibration_diff = abs(confidence - actual_quality)
            calibration_score = max(0.0, 1.0 - calibration_diff)

            calibration_scores.append(calibration_score)

        return statistics.mean(calibration_scores)

    async def _assess_processing_efficiency(self, processing_history: list[dict[str, float]]) -> float:
        """Assess efficiency of cognitive processing."""
        if not processing_history:
            return 0.5

        efficiency_scores = []
        for session in processing_history[-10:]:  # Last 10 sessions
            processing_time = session.get("processing_time_ms", 100)
            quality_achieved = session.get("quality_score", 0.5)

            # Efficiency = quality per unit time
            if processing_time > 0:
                efficiency = min(1.0, quality_achieved / (processing_time / 100))  # Normalize by 100ms
            else:
                efficiency = quality_achieved

            efficiency_scores.append(efficiency)

        return statistics.mean(efficiency_scores)

    async def _assess_error_detection(self, recent_inferences: list[InferenceResult]) -> float:
        """Assess ability to detect and handle errors/contradictions."""
        if not recent_inferences:
            return 0.5

        detection_scores = []
        for inference in recent_inferences:
            # Score based on contradiction detection and circular logic detection
            contradictions = inference.contradictions_detected
            circular_logic = inference.circular_logic_detected

            total_issues = contradictions + circular_logic
            if total_issues == 0:
                # No issues detected - could be good (no issues) or bad (missed issues)
                # Assume good if reasoning was successful
                detection_score = 0.8 if inference.success else 0.6
            else:
                # Issues detected - good if resolved successfully
                detection_score = 0.9 if inference.success else 0.4

            detection_scores.append(detection_score)

        return statistics.mean(detection_scores)

    async def _assess_strategy_effectiveness(
        self,
        recent_inferences: list[InferenceResult],
        recent_thoughts: list[dict[str, Any]]
    ) -> float:
        """Assess effectiveness of reasoning strategies used."""
        if not recent_inferences and not recent_thoughts:
            return 0.5

        strategy_scores = []

        # Assess inference strategies
        for inference in recent_inferences:
            strategy_score = inference.reasoning_quality if hasattr(inference, 'reasoning_quality') else 0.5

            # Bonus for successful complex reasoning
            if inference.max_depth_explored > 8 and inference.success:
                strategy_score += 0.1

            strategy_scores.append(min(1.0, strategy_score))

        # Assess thought synthesis strategies
        for thought in recent_thoughts:
            quality_score = thought.get("quality_score", 0.5)
            strategy_scores.append(quality_score)

        return statistics.mean(strategy_scores) if strategy_scores else 0.5

    async def _calculate_current_cognitive_load(self, context: MetaCognitiveContext) -> float:
        """Calculate current cognitive load level."""

        load_factors = []

        # Processing time factor
        if context.processing_history:
            recent_times = [h.get("processing_time_ms", 0) for h in context.processing_history[-5:]]
            avg_time = statistics.mean(recent_times)
            time_factor = min(1.0, avg_time / 200)  # Normalize by 200ms expected
            load_factors.append(time_factor)

        # Inference complexity factor
        if context.recent_inferences:
            complexity_scores = []
            for inference in context.recent_inferences:
                complexity = min(1.0, (inference.max_depth_explored + inference.total_steps) / 20)
                complexity_scores.append(complexity)
            load_factors.append(statistics.mean(complexity_scores))

        # Consciousness state factor
        if context.consciousness_state:
            arousal = context.consciousness_state.arousal
            load_factors.append(arousal)

        # Calculate overall load
        cognitive_load = statistics.mean(load_factors) if load_factors else 0.3  # Default moderate-low load

        return min(1.0, cognitive_load)

    async def _assess_learning_adaptation(self, context: MetaCognitiveContext) -> float:
        """Assess ability to learn and adapt from experience."""

        if len(self.performance_history) < 5:
            return 0.5  # Insufficient data

        # Look at performance trend over time
        recent_performances = [p.overall_performance for p in self.performance_history[-10:]]

        if len(recent_performances) < 2:
            return 0.5

        # Calculate trend
        x_values = list(range(len(recent_performances)))
        y_values = recent_performances

        # Simple linear regression slope
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0

        # Positive slope indicates learning/adaptation
        adaptation_score = max(0.0, min(1.0, 0.5 + slope))

        return adaptation_score

    async def _assess_cognitive_load(self, context: MetaCognitiveContext) -> CognitiveLoadLevel:
        """Assess current cognitive load level."""

        load_value = await self._calculate_current_cognitive_load(context)

        if load_value < 0.2:
            return CognitiveLoadLevel.MINIMAL
        elif load_value < 0.4:
            return CognitiveLoadLevel.LOW
        elif load_value < 0.6:
            return CognitiveLoadLevel.MODERATE
        elif load_value < 0.8:
            return CognitiveLoadLevel.HIGH
        else:
            return CognitiveLoadLevel.EXCESSIVE

    async def _generate_meta_insights(
        self,
        context: MetaCognitiveContext,
        performance_metrics: CognitivePerformanceMetrics
    ) -> list[MetaCognitiveInsight]:
        """Generate meta-cognitive insights from performance analysis."""

        insights = []

        # Reasoning quality insight
        if performance_metrics.reasoning_accuracy < 0.7:
            insights.append(MetaCognitiveInsight(
                insight_id=f"reasoning_accuracy_{int(time.time())}",
                aspect=MetaCognitiveAspect.REASONING_QUALITY,
                observation=f"Reasoning accuracy is {performance_metrics.reasoning_accuracy:.1%}, below optimal threshold",
                confidence=0.8,
                actionable_recommendation="Consider reducing reasoning depth or improving contradiction detection",
                evidence={"accuracy_score": performance_metrics.reasoning_accuracy},
                priority="high"
            ))

        # Confidence calibration insight
        if performance_metrics.confidence_calibration < 0.6:
            insights.append(MetaCognitiveInsight(
                insight_id=f"confidence_cal_{int(time.time())}",
                aspect=MetaCognitiveAspect.CONFIDENCE_CALIBRATION,
                observation=f"Confidence calibration is poor ({performance_metrics.confidence_calibration:.1%})",
                confidence=0.7,
                actionable_recommendation="Recalibrate confidence scoring based on actual performance outcomes",
                evidence={"calibration_score": performance_metrics.confidence_calibration},
                priority="medium"
            ))

        # Cognitive load insight
        if performance_metrics.cognitive_load > 0.8:
            insights.append(MetaCognitiveInsight(
                insight_id=f"cognitive_load_{int(time.time())}",
                aspect=MetaCognitiveAspect.COGNITIVE_EFFICIENCY,
                observation=f"Cognitive load is excessive ({performance_metrics.cognitive_load:.1%})",
                confidence=0.9,
                actionable_recommendation="Reduce reasoning complexity or increase processing time budget",
                evidence={"cognitive_load": performance_metrics.cognitive_load},
                priority="high"
            ))

        # Strategy effectiveness insight
        if performance_metrics.strategy_success_rate < 0.6:
            insights.append(MetaCognitiveInsight(
                insight_id=f"strategy_eff_{int(time.time())}",
                aspect=MetaCognitiveAspect.STRATEGY_EFFECTIVENESS,
                observation=f"Current reasoning strategies are underperforming ({performance_metrics.strategy_success_rate:.1%})",
                confidence=0.6,
                actionable_recommendation="Experiment with alternative reasoning approaches or simplify problem decomposition",
                evidence={"strategy_success": performance_metrics.strategy_success_rate},
                priority="medium"
            ))

        # Adaptation insight
        if performance_metrics.adaptation_score < 0.4:
            insights.append(MetaCognitiveInsight(
                insight_id=f"adaptation_{int(time.time())}",
                aspect=MetaCognitiveAspect.LEARNING_ADAPTATION,
                observation=f"Learning adaptation appears limited ({performance_metrics.adaptation_score:.1%})",
                confidence=0.5,
                actionable_recommendation="Increase variation in reasoning approaches to promote adaptation",
                evidence={"adaptation_score": performance_metrics.adaptation_score},
                priority="low"
            ))

        return insights

    async def _calculate_self_awareness(
        self,
        context: MetaCognitiveContext,
        insights: list[MetaCognitiveInsight]
    ) -> float:
        """Calculate self-awareness score based on insight generation and accuracy."""

        base_awareness = self.meta_awareness_level

        # Boost for generating insights
        insight_bonus = min(0.2, len(insights) * 0.05)

        # Bonus for high-confidence insights
        high_confidence_insights = [i for i in insights if i.confidence > 0.8]
        confidence_bonus = min(0.1, len(high_confidence_insights) * 0.02)

        # Penalty for excessive insights (might indicate poor filtering)
        insight_penalty = 0.1 if len(insights) > 10 else 0.0

        self_awareness_score = min(1.0, max(0.0,
            base_awareness + insight_bonus + confidence_bonus - insight_penalty
        ))

        return self_awareness_score

    async def _assess_meta_reasoning_quality(
        self,
        context: MetaCognitiveContext,
        performance_metrics: CognitivePerformanceMetrics,
        insights: list[MetaCognitiveInsight]
    ) -> float:
        """Assess quality of meta-reasoning (reasoning about reasoning)."""

        quality_factors = []

        # Quality of performance assessment
        if performance_metrics.overall_performance > 0:
            assessment_quality = min(1.0, performance_metrics.overall_performance)
            quality_factors.append(assessment_quality)

        # Quality of insight generation
        if insights:
            avg_insight_confidence = statistics.mean([i.confidence for i in insights])
            quality_factors.append(avg_insight_confidence)

            # Diversity of insights (covering different aspects)
            unique_aspects = len({i.aspect for i in insights})
            aspect_diversity = min(1.0, unique_aspects / len(MetaCognitiveAspect))
            quality_factors.append(aspect_diversity)

        # Consistency with historical performance
        if self.performance_history:
            recent_trend = statistics.mean([p.overall_performance for p in self.performance_history[-5:]])
            consistency_score = 1.0 - abs(performance_metrics.overall_performance - recent_trend)
            quality_factors.append(max(0.0, consistency_score))

        meta_reasoning_quality = statistics.mean(quality_factors) if quality_factors else 0.5

        return meta_reasoning_quality

    async def _generate_cognitive_adjustments(
        self,
        performance_metrics: CognitivePerformanceMetrics,
        cognitive_load: CognitiveLoadLevel,
        insights: list[MetaCognitiveInsight]
    ) -> list[str]:
        """Generate recommended cognitive adjustments."""

        recommendations = []

        # Cognitive load adjustments
        if cognitive_load == CognitiveLoadLevel.EXCESSIVE:
            recommendations.append("Reduce reasoning complexity to manage cognitive load")
            recommendations.append("Increase processing time budget for current tasks")

        elif cognitive_load == CognitiveLoadLevel.MINIMAL:
            recommendations.append("Consider tackling more complex reasoning challenges")

        # Performance-based adjustments
        if performance_metrics.reasoning_accuracy < 0.7:
            recommendations.append("Focus on improving reasoning accuracy through better validation")

        if performance_metrics.processing_efficiency < 0.6:
            recommendations.append("Optimize processing pipelines for better time-to-quality ratio")

        # Insight-based adjustments
        high_priority_insights = [i for i in insights if i.priority == "high" and i.actionable_recommendation]
        for insight in high_priority_insights:
            if insight.actionable_recommendation not in recommendations:
                recommendations.append(insight.actionable_recommendation)

        # Default recommendation
        if not recommendations:
            recommendations.append("Continue current cognitive approach - performance is satisfactory")

        return recommendations

    async def _check_self_correction_triggers(self, assessment: MetaCognitiveAssessment) -> None:
        """Check if self-correction mechanisms should be triggered."""

        if not self.enable_self_correction:
            return

        # Trigger self-correction for poor performance
        if assessment.performance_metrics.overall_performance < 0.4:
            self.self_correction_active = True
            self.assessment_stats["self_corrections_triggered"] += 1
            logger.info("Self-correction triggered due to poor performance")

        # Trigger for excessive cognitive load
        if assessment.cognitive_load_assessment == CognitiveLoadLevel.EXCESSIVE:
            self.self_correction_active = True
            logger.info("Self-correction triggered due to excessive cognitive load")

        # Reset self-correction if performance improves
        if (assessment.performance_metrics.overall_performance > 0.7 and
            assessment.cognitive_load_assessment in [CognitiveLoadLevel.LOW, CognitiveLoadLevel.MODERATE]):
            self.self_correction_active = False

    def _update_performance_tracking(
        self,
        performance_metrics: CognitivePerformanceMetrics,
        cognitive_load: CognitiveLoadLevel
    ) -> None:
        """Update performance tracking and cognitive load monitoring."""

        # Add to performance history
        self.performance_history.append(performance_metrics)
        if len(self.performance_history) > self.performance_history_size:
            self.performance_history.pop(0)

        # Update cognitive load window
        load_value = performance_metrics.cognitive_load
        self.cognitive_load_window.append(load_value)
        if len(self.cognitive_load_window) > self.cognitive_load_window_size:
            self.cognitive_load_window.pop(0)

        # Update current states
        self.current_cognitive_load = cognitive_load

        # Update performance trend
        if len(self.performance_history) >= 5:
            recent_performances = [p.overall_performance for p in self.performance_history[-5:]]
            older_performances = [p.overall_performance for p in self.performance_history[-10:-5]]

            if older_performances:
                recent_avg = statistics.mean(recent_performances)
                older_avg = statistics.mean(older_performances)

                if recent_avg > older_avg + 0.05:
                    self.assessment_stats["performance_trend"] = "improving"
                elif recent_avg < older_avg - 0.05:
                    self.assessment_stats["performance_trend"] = "declining"
                else:
                    self.assessment_stats["performance_trend"] = "stable"

    def _update_assessment_stats(self, assessment: MetaCognitiveAssessment, success: bool) -> None:
        """Update assessment statistics."""
        self.assessment_stats["total_assessments"] += 1

        if success:
            self.assessment_stats["successful_assessments"] += 1
            self.assessment_stats["insights_generated"] += len(assessment.insights)

            # Update average assessment time
            total = self.assessment_stats["total_assessments"]
            current_avg = self.assessment_stats["avg_assessment_time_ms"]
            self.assessment_stats["avg_assessment_time_ms"] = (
                (current_avg * (total - 1) + assessment.processing_time_ms) / total
            )

    def get_current_cognitive_state(self) -> dict[str, Any]:
        """Get current cognitive state summary."""

        return {
            "cognitive_load": self.current_cognitive_load.value,
            "meta_awareness_level": self.meta_awareness_level,
            "self_correction_active": self.self_correction_active,
            "performance_trend": self.assessment_stats["performance_trend"],
            "recent_performance": self.performance_history[-1].overall_performance if self.performance_history else 0.5,
            "assessment_stats": dict(self.assessment_stats)
        }

    def get_performance_analytics(self) -> dict[str, Any]:
        """Get detailed performance analytics."""

        if not self.performance_history:
            return {"status": "insufficient_data"}

        recent_metrics = self.performance_history[-10:]

        analytics = {
            "performance_summary": {
                "current_performance": recent_metrics[-1].overall_performance,
                "avg_performance": statistics.mean([m.overall_performance for m in recent_metrics]),
                "performance_trend": self.assessment_stats["performance_trend"],
                "stability": statistics.stdev([m.overall_performance for m in recent_metrics]) if len(recent_metrics) > 1 else 0.0
            },
            "cognitive_load_analysis": {
                "current_load": self.current_cognitive_load.value,
                "avg_load": statistics.mean(self.cognitive_load_window) if self.cognitive_load_window else 0.3,
                "load_stability": statistics.stdev(self.cognitive_load_window) if len(self.cognitive_load_window) > 1 else 0.0
            },
            "assessment_efficiency": {
                "success_rate": (self.assessment_stats["successful_assessments"] / max(1, self.assessment_stats["total_assessments"])) * 100,
                "avg_assessment_time_ms": self.assessment_stats["avg_assessment_time_ms"],
                "insights_per_assessment": self.assessment_stats["insights_generated"] / max(1, self.assessment_stats["successful_assessments"])
            },
            "self_awareness_metrics": {
                "meta_awareness_level": self.meta_awareness_level,
                "self_correction_rate": self.assessment_stats["self_corrections_triggered"] / max(1, self.assessment_stats["total_assessments"]),
                "adaptation_capability": recent_metrics[-1].adaptation_score if recent_metrics else 0.5
            }
        }

        return analytics


# Export main classes
__all__ = [
    "CognitiveLoadLevel",
    "CognitivePerformanceMetrics",
    "MetaCognitiveAspect",
    "MetaCognitiveAssessment",
    "MetaCognitiveAssessor",
    "MetaCognitiveContext",
    "MetaCognitiveInsight"
]
