import logging
from datetime import timezone

import streamlit as st

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


LUKHAS Cognitive Load Estimator - User State Inference Logic

This module implements cognitive load estimation for adaptive authentication
interfaces that respond to user mental state and capacity.

Author: LUKHAS Team
Date: June 2025
Purpose: Estimate user cognitive load for adaptive UI optimization
"""

import statistics
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class CognitiveLoadLevel(Enum):
    """Cognitive load intensity levels"""

    VERY_LOW = "very_low"  # 0.0-0.2 - User is relaxed, minimal mental effort
    LOW = "low"  # 0.2-0.4 - Light cognitive engagement
    MODERATE = "moderate"  # 0.4-0.6 - Normal working memory usage
    HIGH = "high"  # 0.6-0.8 - Approaching cognitive limits
    OVERLOAD = "overload"  # 0.8-1.0 - Cognitive overload detected


class CognitiveTask(Enum):
    """Types of cognitive tasks for load assessment"""

    ATTENTION = "attention"  # Focused attention tasks
    MEMORY = "memory"  # Working memory tasks
    PROCESSING = "processing"  # Information processing
    DECISION = "decision"  # Decision-making tasks
    MOTOR = "motor"  # Motor coordination
    MULTITASK = "multitask"  # Multiple concurrent tasks


@dataclass
class CognitiveIndicators:
    """Physiological and behavioral indicators of cognitive load"""

    reaction_time_ms: float  # Response time to stimuli
    error_rate: float  # Percentage of errors made
    task_completion_time: float  # Time to complete tasks
    input_variability: float  # Variability in input timing
    attention_focus: float  # Attention focus score 0.0-1.0
    stress_level: float  # Estimated stress level 0.0-1.0
    fatigue_level: float  # Estimated fatigue level 0.0-1.0


@dataclass
class CognitiveLoadAssessment:
    """Complete cognitive load assessment result"""

    load_level: CognitiveLoadLevel
    load_score: float  # Numerical load score 0.0-1.0
    primary_factors: list[str]  # Main contributing factors
    indicators: CognitiveIndicators
    confidence: float  # Assessment confidence 0.0-1.0
    recommendations: list[str]  # UI adaptation recommendations
    timestamp: datetime


class CognitiveLoadEstimator:
    """
    Cognitive load estimation system for LUKHAS authentication.

    Features:
    - Multi-modal cognitive load assessment
    - Real-time adaptation recommendations
    - Task-specific load modeling
    - Individual baseline learning
    - Fatigue and stress detection
    - Performance degradation prediction
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or self._get_default_config()

        # Baseline measurements for this user
        self.baseline_metrics = None
        self.personal_thresholds = {}
        self.learning_data = []

        # Current assessment state
        self.current_load = CognitiveLoadLevel.MODERATE
        self.load_history = []
        self.indicators_history = []

        # Task-specific models
        self.task_models = {}
        self.active_tasks = set()

        # Performance tracking
        self.performance_metrics = {"accuracy": [], "speed": [], "consistency": []}

        # Adaptation recommendations
        self.adaptation_rules = self._initialize_adaptation_rules()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for cognitive load estimation."""
        return {
            "baseline_learning_enabled": True,
            "adaptive_thresholds": True,
            "task_specific_modeling": True,
            "fatigue_detection": True,
            "stress_detection": True,
            "prediction_horizon_minutes": 5,
            "assessment_interval_seconds": 2,
            "smoothing_window_size": 10,
            "confidence_threshold": 0.7,
        }

    def _initialize_adaptation_rules(self) -> dict[str, Any]:
        """Initialize UI adaptation rules based on cognitive load."""
        return {
            CognitiveLoadLevel.VERY_LOW: {
                "grid_size_multiplier": 1.2,  # Can handle slightly larger grids
                "timeout_multiplier": 0.8,  # Can work with shorter timeouts
                "animation_speed": 1.0,  # Normal animation speed
                "feedback_level": "minimal",  # Less feedback needed
                "help_prompts": False,  # No help prompts needed
            },
            CognitiveLoadLevel.LOW: {
                "grid_size_multiplier": 1.0,
                "timeout_multiplier": 1.0,
                "animation_speed": 1.0,
                "feedback_level": "standard",
                "help_prompts": False,
            },
            CognitiveLoadLevel.MODERATE: {
                "grid_size_multiplier": 1.0,
                "timeout_multiplier": 1.0,
                "animation_speed": 0.9,
                "feedback_level": "standard",
                "help_prompts": True,
            },
            CognitiveLoadLevel.HIGH: {
                "grid_size_multiplier": 0.8,  # Smaller grids to reduce choice overload
                "timeout_multiplier": 1.3,  # More time needed
                "animation_speed": 0.7,  # Slower animations
                "feedback_level": "enhanced",  # More feedback
                "help_prompts": True,
            },
            CognitiveLoadLevel.OVERLOAD: {
                "grid_size_multiplier": 0.6,  # Much smaller grids
                "timeout_multiplier": 1.5,  # Much more time
                "animation_speed": 0.5,  # Very slow animations
                "feedback_level": "maximum",  # Maximum feedback
                "help_prompts": True,
                "break_suggestion": True,  # Suggest taking a break
            },
        }

    async def initialize_baseline(self, calibration_data: Optional[dict[str, Any]] = None) -> bool:
        """
        Initialize baseline cognitive metrics for this user.

        Args:
            calibration_data: Optional pre-existing calibration data

        Returns:
            True if baseline initialization successful
        """
        try:
            if calibration_data:
                self.baseline_metrics = self._parse_calibration_data(calibration_data)
            else:
                # Use standard baseline values
                self.baseline_metrics = CognitiveIndicators(
                    reaction_time_ms=750,  # Average reaction time
                    error_rate=0.1,  # 10% error rate baseline
                    task_completion_time=5.0,  # 5 seconds average
                    input_variability=0.2,  # 20% timing variability
                    attention_focus=0.7,  # 70% attention focus
                    stress_level=0.3,  # 30% stress level
                    fatigue_level=0.2,  # 20% fatigue level
                )

            # Initialize personal thresholds based on baseline
            self._calculate_personal_thresholds()

            logger.info("Cognitive load baseline initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize baseline: {e}")
            return False

    def _parse_calibration_data(self, data: dict[str, Any]) -> CognitiveIndicators:
        """Parse calibration data into baseline metrics."""
        return CognitiveIndicators(
            reaction_time_ms=data.get("avg_reaction_time", 750),
            error_rate=data.get("avg_error_rate", 0.1),
            task_completion_time=data.get("avg_completion_time", 5.0),
            input_variability=data.get("input_variability", 0.2),
            attention_focus=data.get("attention_focus", 0.7),
            stress_level=data.get("stress_level", 0.3),
            fatigue_level=data.get("fatigue_level", 0.2),
        )

    def _calculate_personal_thresholds(self):
        """Calculate personalized thresholds based on baseline."""
        if not self.baseline_metrics:
            return

        base = self.baseline_metrics

        self.personal_thresholds = {
            "high_reaction_time": base.reaction_time_ms * 1.5,
            "high_error_rate": base.error_rate * 2.0,
            "high_completion_time": base.task_completion_time * 1.8,
            "high_variability": base.input_variability * 2.0,
            "low_attention": base.attention_focus * 0.6,
            "high_stress": base.stress_level * 2.0,
            "high_fatigue": base.fatigue_level * 2.5,
        }

    def assess_cognitive_load(
        self, performance_data: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> CognitiveLoadAssessment:
        """
        Assess current cognitive load based on performance data.

        Args:
            performance_data: Current performance metrics
            context: Optional context information (time of day, task type, etc.)

        Returns:
            Complete cognitive load assessment
        """
        # Extract indicators from performance data
        indicators = self._extract_cognitive_indicators(performance_data)

        # Calculate load score
        load_score = self._calculate_load_score(indicators)

        # Determine load level
        load_level = self._classify_load_level(load_score)

        # Identify primary contributing factors
        primary_factors = self._identify_load_factors(indicators, load_score)

        # Calculate assessment confidence
        confidence = self._calculate_confidence(indicators, context)

        # Generate adaptation recommendations
        recommendations = self._generate_recommendations(load_level, indicators, context)

        # Create assessment
        assessment = CognitiveLoadAssessment(
            load_level=load_level,
            load_score=load_score,
            primary_factors=primary_factors,
            indicators=indicators,
            confidence=confidence,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc),
        )

        # Update history
        self.load_history.append(assessment)
        self.indicators_history.append(indicators)

        # Limit history size
        if len(self.load_history) > 100:
            self.load_history = self.load_history[-50:]
            self.indicators_history = self.indicators_history[-50:]

        self.current_load = load_level

        return assessment

    def _extract_cognitive_indicators(self, performance_data: dict[str, Any]) -> CognitiveIndicators:
        """
        Extract cognitive indicators from performance data.

        Args:
            performance_data: Raw performance metrics

        Returns:
            Structured cognitive indicators
        """
        # Extract reaction time
        reaction_time = performance_data.get("reaction_time_ms", 0)
        if reaction_time == 0 and "response_times" in performance_data:
            reaction_time = statistics.mean(performance_data["response_times"])

        # Extract error rate
        error_rate = performance_data.get("error_rate", 0)
        if error_rate == 0 and "errors" in performance_data and "total_attempts" in performance_data:
            error_rate = performance_data["errors"] / max(performance_data["total_attempts"], 1)

        # Extract task completion time
        completion_time = performance_data.get("completion_time", 0)
        if completion_time == 0 and "task_duration" in performance_data:
            completion_time = performance_data["task_duration"]

        # Calculate input variability
        input_variability = 0
        if "input_times" in performance_data and len(performance_data["input_times"]) > 1:
            times = performance_data["input_times"]
            intervals = [times[i + 1] - times[i] for i in range(len(times) - 1)]
            if intervals:
                mean_interval = statistics.mean(intervals)
                if mean_interval > 0:
                    variability = statistics.stdev(intervals) if len(intervals) > 1 else 0
                    input_variability = variability / mean_interval

        # Extract attention focus (from attention monitor if available)
        attention_focus = performance_data.get("attention_focus", 0.5)

        # Estimate stress level from performance degradation
        stress_level = self._estimate_stress_level(performance_data)

        # Estimate fatigue level
        fatigue_level = self._estimate_fatigue_level(performance_data)

        return CognitiveIndicators(
            reaction_time_ms=reaction_time,
            error_rate=error_rate,
            task_completion_time=completion_time,
            input_variability=input_variability,
            attention_focus=attention_focus,
            stress_level=stress_level,
            fatigue_level=fatigue_level,
        )

    def _estimate_stress_level(self, performance_data: dict[str, Any]) -> float:
        """Estimate stress level from performance indicators."""
        stress_indicators = []

        # High error rate indicates stress
        error_rate = performance_data.get("error_rate", 0)
        if self.baseline_metrics and error_rate > self.baseline_metrics.error_rate * 1.5:
            stress_indicators.append(0.7)

        # Erratic input timing indicates stress
        if "input_variability" in performance_data and performance_data["input_variability"] > 0.3:
            stress_indicators.append(0.6)

        # Fast but inaccurate responses indicate stress
        reaction_time = performance_data.get("reaction_time_ms", 0)
        if (
            self.baseline_metrics
            and reaction_time < self.baseline_metrics.reaction_time_ms * 0.7
            and error_rate > self.baseline_metrics.error_rate
        ):
            stress_indicators.append(0.8)

        # Calculate overall stress level
        if stress_indicators:
            return min(1.0, statistics.mean(stress_indicators))
        else:
            return 0.3  # Baseline stress level

    def _estimate_fatigue_level(self, performance_data: dict[str, Any]) -> float:
        """Estimate fatigue level from performance degradation patterns."""
        fatigue_indicators = []

        # Slow reaction times indicate fatigue
        reaction_time = performance_data.get("reaction_time_ms", 0)
        if self.baseline_metrics and reaction_time > self.baseline_metrics.reaction_time_ms * 1.3:
            fatigue_indicators.append(0.6)

        # Declining performance over time indicates fatigue
        if len(self.performance_metrics["accuracy"]) > 10:
            recent_accuracy = statistics.mean(self.performance_metrics["accuracy"][-5:])
            earlier_accuracy = statistics.mean(self.performance_metrics["accuracy"][-10:-5])
            if recent_accuracy < earlier_accuracy * 0.9:
                fatigue_indicators.append(0.7)

        # Long completion times indicate fatigue
        completion_time = performance_data.get("completion_time", 0)
        if self.baseline_metrics and completion_time > self.baseline_metrics.task_completion_time * 1.5:
            fatigue_indicators.append(0.5)

        # Calculate overall fatigue level
        if fatigue_indicators:
            return min(1.0, statistics.mean(fatigue_indicators))
        else:
            return 0.2  # Baseline fatigue level

    def _calculate_load_score(self, indicators: CognitiveIndicators) -> float:
        """
        Calculate overall cognitive load score from indicators.

        Args:
            indicators: Cognitive indicators

        Returns:
            Load score between 0.0 and 1.0
        """
        if not self.baseline_metrics:
            # Use relative scoring without baseline
            score_components = [
                min(indicators.reaction_time_ms / 2000, 1.0) * 0.2,  # Normalize to 2000ms max
                indicators.error_rate * 0.25,  # Error rate component
                min(indicators.task_completion_time / 20, 1.0) * 0.15,  # Completion time
                indicators.input_variability * 0.15,  # Input variability
                (1.0 - indicators.attention_focus) * 0.1,  # Inverted attention
                indicators.stress_level * 0.1,  # Stress level
                indicators.fatigue_level * 0.05,  # Fatigue level
            ]
        else:
            # Use baseline-relative scoring
            base = self.baseline_metrics
            score_components = [
                min(indicators.reaction_time_ms / (base.reaction_time_ms * 2), 1.0) * 0.2,
                min(indicators.error_rate / (base.error_rate * 3), 1.0) * 0.25,
                min(
                    indicators.task_completion_time / (base.task_completion_time * 2),
                    1.0,
                )
                * 0.15,
                min(indicators.input_variability / (base.input_variability * 2), 1.0) * 0.15,
                max(
                    0,
                    (base.attention_focus - indicators.attention_focus) / base.attention_focus,
                )
                * 0.1,
                (indicators.stress_level / 1.0) * 0.1,
                (indicators.fatigue_level / 1.0) * 0.05,
            ]

        # Calculate weighted average
        load_score = sum(score_components)

        # Apply smoothing if we have history
        if len(self.load_history) > 0:
            recent_scores = [assessment.load_score for assessment in self.load_history[-5:]]
            recent_scores.append(load_score)
            load_score = statistics.mean(recent_scores)

        return min(1.0, max(0.0, load_score))

    def _classify_load_level(self, load_score: float) -> CognitiveLoadLevel:
        """Classify load score into discrete load level."""
        if load_score < 0.2:
            return CognitiveLoadLevel.VERY_LOW
        elif load_score < 0.4:
            return CognitiveLoadLevel.LOW
        elif load_score < 0.6:
            return CognitiveLoadLevel.MODERATE
        elif load_score < 0.8:
            return CognitiveLoadLevel.HIGH
        else:
            return CognitiveLoadLevel.OVERLOAD

    def _identify_load_factors(self, indicators: CognitiveIndicators, load_score: float) -> list[str]:
        """Identify primary factors contributing to cognitive load."""
        factors = []

        # Check each indicator against thresholds
        if self.baseline_metrics:
            base = self.baseline_metrics

            if indicators.reaction_time_ms > base.reaction_time_ms * 1.3:
                factors.append("slow_responses")
            if indicators.error_rate > base.error_rate * 1.5:
                factors.append("high_error_rate")
            if indicators.task_completion_time > base.task_completion_time * 1.4:
                factors.append("slow_completion")
            if indicators.input_variability > base.input_variability * 1.5:
                factors.append("inconsistent_input")
            if indicators.attention_focus < base.attention_focus * 0.7:
                factors.append("poor_attention")

        # Check absolute thresholds
        if indicators.stress_level > 0.6:
            factors.append("high_stress")
        if indicators.fatigue_level > 0.6:
            factors.append("fatigue")

        # If no specific factors, use general classification
        if not factors:
            if load_score > 0.7:
                factors.append("general_overload")
            elif load_score < 0.3:
                factors.append("low_engagement")

        return factors

    def _calculate_confidence(self, indicators: CognitiveIndicators, context: Optional[dict[str, Any]]) -> float:
        """Calculate confidence in the cognitive load assessment."""
        confidence_factors = []

        # Data quality factors
        if indicators.reaction_time_ms > 0:
            confidence_factors.append(0.8)
        if indicators.error_rate >= 0:
            confidence_factors.append(0.7)
        if indicators.attention_focus > 0:
            confidence_factors.append(0.9)

        # Baseline availability
        if self.baseline_metrics:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)

        # History length
        if len(self.load_history) > 10:
            confidence_factors.append(0.8)
        elif len(self.load_history) > 5:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)

        # Context information
        if context:
            confidence_factors.append(0.7)

        return statistics.mean(confidence_factors) if confidence_factors else 0.5

    def _generate_recommendations(
        self,
        load_level: CognitiveLoadLevel,
        indicators: CognitiveIndicators,
        context: Optional[dict[str, Any]],
    ) -> list[str]:
        """Generate UI adaptation recommendations based on cognitive load."""
        recommendations = []

        # Get base recommendations for load level
        if load_level in self.adaptation_rules:
            rules = self.adaptation_rules[load_level]

            if rules.get("grid_size_multiplier", 1.0) != 1.0:
                if rules["grid_size_multiplier"] < 1.0:
                    recommendations.append("reduce_grid_size")
                else:
                    recommendations.append("increase_grid_size")

            if rules.get("timeout_multiplier", 1.0) > 1.0:
                recommendations.append("increase_timeout")

            if rules.get("animation_speed", 1.0) < 1.0:
                recommendations.append("slow_animations")

            if rules.get("feedback_level") == "enhanced":
                recommendations.append("increase_feedback")
            elif rules.get("feedback_level") == "maximum":
                recommendations.append("maximum_feedback")

            if rules.get("help_prompts"):
                recommendations.append("show_help_prompts")

            if rules.get("break_suggestion"):
                recommendations.append("suggest_break")

        # Specific indicator-based recommendations
        if indicators.stress_level > 0.7:
            recommendations.append("stress_reduction_mode")

        if indicators.fatigue_level > 0.7:
            recommendations.append("fatigue_management")

        if indicators.attention_focus < 0.4:
            recommendations.append("attention_enhancement")

        return list(set(recommendations))  # Remove duplicates

    def get_ui_adaptations(self, load_level: Optional[CognitiveLoadLevel] = None) -> dict[str, Any]:
        """
        Get specific UI adaptation parameters for current or specified load level.

        Args:
            load_level: Optional specific load level, uses current if None

        Returns:
            UI adaptation parameters
        """
        level = load_level or self.current_load

        if level in self.adaptation_rules:
            return self.adaptation_rules[level].copy()
        else:
            return self.adaptation_rules[CognitiveLoadLevel.MODERATE].copy()

    def update_performance_tracking(self, performance_metrics: dict[str, float]):
        """Update performance tracking for trend analysis."""
        if "accuracy" in performance_metrics:
            self.performance_metrics["accuracy"].append(performance_metrics["accuracy"])
        if "speed" in performance_metrics:
            self.performance_metrics["speed"].append(performance_metrics["speed"])
        if "consistency" in performance_metrics:
            self.performance_metrics["consistency"].append(performance_metrics["consistency"])

        # Limit history size
        for key in self.performance_metrics:
            if len(self.performance_metrics[key]) > 50:
                self.performance_metrics[key] = self.performance_metrics[key][-25:]

    def get_cognitive_status(self) -> dict[str, Any]:
        """Get comprehensive cognitive load estimation status."""
        latest_assessment = self.load_history[-1] if self.load_history else None

        return {
            "current_load_level": self.current_load.value,
            "current_load_score": (latest_assessment.load_score if latest_assessment else 0.5),
            "assessment_confidence": (latest_assessment.confidence if latest_assessment else 0.5),
            "baseline_available": self.baseline_metrics is not None,
            "assessments_count": len(self.load_history),
            "primary_factors": (latest_assessment.primary_factors if latest_assessment else []),
            "recommendations": (latest_assessment.recommendations if latest_assessment else []),
            "performance_trends": {
                "accuracy_trend": len(self.performance_metrics["accuracy"]),
                "speed_trend": len(self.performance_metrics["speed"]),
                "consistency_trend": len(self.performance_metrics["consistency"]),
            },
            "thresholds": self.personal_thresholds.copy(),
            "adaptation_rules": {level.value: rules for level, rules in self.adaptation_rules.items()},
        }


# Export the main classes
__all__ = [
    "CognitiveIndicators",
    "CognitiveLoadAssessment",
    "CognitiveLoadEstimator",
    "CognitiveLoadLevel",
    "CognitiveTask",
]
