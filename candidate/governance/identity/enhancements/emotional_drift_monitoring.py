#!/usr/bin/env python3
"""
LUKHAS Emotional Drift Monitoring System
=======================================
Advanced mood slope detection and emotional pattern analysis for recurring logins.
Tracks consciousness evolution and emotional states over time.

🧠 FEATURES:
- Emotional slope detection across sessions
- Mood pattern recognition
- Consciousness evolution tracking
- Anomaly detection in emotional patterns
- Proactive mental health indicators

Author: LUKHAS AI Systems & Claude Code
Version: 1.0.0 - Emotional Intelligence
Created: 2025-08-03
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class EmotionalTrend(Enum):
    """Emotional trend classifications"""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class MoodSlope(Enum):
    """Mood slope indicators"""

    STEEP_POSITIVE = "steep_positive"  # Rapid improvement
    GRADUAL_POSITIVE = "gradual_positive"
    STABLE_POSITIVE = "stable_positive"
    NEUTRAL = "neutral"
    STABLE_NEGATIVE = "stable_negative"
    GRADUAL_NEGATIVE = "gradual_negative"
    STEEP_NEGATIVE = "steep_negative"  # Concerning decline


@dataclass
class EmotionalDataPoint:
    """Single emotional measurement"""

    timestamp: datetime
    consciousness_state: str
    attention_level: float
    creativity_index: float
    coherence_score: float
    stress_indicators: float
    mood_valence: float  # -1.0 (negative) to +1.0 (positive)
    energy_level: float
    session_quality: float


@dataclass
class EmotionalPattern:
    """Detected emotional pattern"""

    pattern_type: str
    confidence: float
    duration_days: int
    trend_direction: EmotionalTrend
    mood_slope: MoodSlope
    key_indicators: list[str]
    recommendations: list[str]


@dataclass
class DriftAnalysisResult:
    """Complete drift analysis result"""

    user_id: str
    analysis_period: str
    overall_trend: EmotionalTrend
    mood_slope: MoodSlope
    slope_value: float
    stability_score: float
    patterns: list[EmotionalPattern]
    risk_factors: list[str]
    positive_indicators: list[str]
    recommendations: list[str]
    intervention_suggested: bool


class EmotionalDriftMonitor:
    """
    Monitors emotional patterns and mood slopes across authentication sessions
    """

    def __init__(self):
        self.consciousness_weights = {
            "focused": {"valence": 0.6, "energy": 0.8, "stability": 0.9},
            "creative": {"valence": 0.8, "energy": 0.7, "stability": 0.6},
            "meditative": {"valence": 0.7, "energy": 0.4, "stability": 0.95},
            "analytical": {"valence": 0.6, "energy": 0.9, "stability": 0.8},
            "dreaming": {"valence": 0.5, "energy": 0.3, "stability": 0.4},
            "flow_state": {"valence": 0.9, "energy": 0.95, "stability": 0.8},
        }

        self.emotional_baselines = {
            "attention_baseline": 0.7,
            "creativity_baseline": 0.6,
            "coherence_baseline": 0.75,
            "mood_baseline": 0.5,
            "energy_baseline": 0.6,
        }

        logger.info("🧠 Emotional Drift Monitor initialized")

    async def analyze_emotional_drift(
        self,
        user_id: str,
        session_history: list[dict[str, Any]],
        analysis_days: int = 30,
    ) -> DriftAnalysisResult:
        """
        Analyze emotional drift patterns over specified period
        """
        logger.info(f"🧠 Analyzing emotional drift for {user_id} over {analysis_days} days")

        try:
            # Convert session data to emotional data points
            emotional_data = self._extract_emotional_data(session_history, analysis_days)

            if len(emotional_data) < 3:
                return self._create_insufficient_data_result(user_id, analysis_days)

            # Calculate mood slope
            mood_slope, slope_value = self._calculate_mood_slope(emotional_data)

            # Determine overall trend
            overall_trend = self._determine_overall_trend(emotional_data, slope_value)

            # Calculate stability score
            stability_score = self._calculate_stability_score(emotional_data)

            # Detect patterns
            patterns = await self._detect_emotional_patterns(emotional_data)

            # Identify risk factors and positive indicators
            risk_factors = self._identify_risk_factors(emotional_data, patterns)
            positive_indicators = self._identify_positive_indicators(emotional_data, patterns)

            # Generate recommendations
            recommendations = self._generate_recommendations(mood_slope, patterns, stability_score)

            # Determine if intervention is suggested
            intervention_suggested = self._should_suggest_intervention(
                mood_slope, risk_factors, stability_score
            )

            return DriftAnalysisResult(
                user_id=user_id,
                analysis_period=f"{analysis_days} days",
                overall_trend=overall_trend,
                mood_slope=mood_slope,
                slope_value=slope_value,
                stability_score=stability_score,
                patterns=patterns,
                risk_factors=risk_factors,
                positive_indicators=positive_indicators,
                recommendations=recommendations,
                intervention_suggested=intervention_suggested,
            )

        except Exception as e:
            logger.error(f"❌ Emotional drift analysis failed: {e}")
            return self._create_error_result(user_id, analysis_days, str(e))

    def _extract_emotional_data(
        self, session_history: list[dict[str, Any]], days: int
    ) -> list[EmotionalDataPoint]:
        """Extract emotional data points from session history"""

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        emotional_data = []

        for session in session_history:
            session_time = datetime.fromisoformat(
                session.get("timestamp", datetime.utcnow().isoformat())
            )

            if session_time < cutoff_date:
                continue

            consciousness_state = session.get("consciousness_state", "unknown")
            attention_metrics = session.get("attention_metrics", {})

            # Calculate mood valence from consciousness state and metrics
            mood_valence = self._calculate_mood_valence(consciousness_state, attention_metrics)

            # Calculate stress indicators
            stress_indicators = self._calculate_stress_indicators(session)

            # Calculate session quality
            session_quality = self._calculate_session_quality(session)

            data_point = EmotionalDataPoint(
                timestamp=session_time,
                consciousness_state=consciousness_state,
                attention_level=attention_metrics.get("attention", 0.5),
                creativity_index=attention_metrics.get("creativity", 0.5),
                coherence_score=attention_metrics.get("coherence", 0.5),
                stress_indicators=stress_indicators,
                mood_valence=mood_valence,
                energy_level=self._estimate_energy_level(consciousness_state, attention_metrics),
                session_quality=session_quality,
            )

            emotional_data.append(data_point)

        # Sort by timestamp
        emotional_data.sort(key=lambda x: x.timestamp)
        return emotional_data

    def _calculate_mood_valence(
        self, consciousness_state: str, attention_metrics: dict[str, float]
    ) -> float:
        """Calculate mood valence from consciousness and metrics"""

        state_weights = self.consciousness_weights.get(consciousness_state, {"valence": 0.5})
        base_valence = state_weights["valence"]

        # Adjust based on attention metrics
        attention = attention_metrics.get("attention", 0.5)
        creativity = attention_metrics.get("creativity", 0.5)
        coherence = attention_metrics.get("coherence", 0.5)

        # Weighted combination
        calculated_valence = (
            base_valence * 0.4 + attention * 0.2 + creativity * 0.2 + coherence * 0.2
        )

        # Normalize to -1.0 to +1.0 range
        return (calculated_valence * 2.0) - 1.0

    def _calculate_stress_indicators(self, session: dict[str, Any]) -> float:
        """Calculate stress indicators from session data"""

        stress_score = 0.0

        # Authentication failures increase stress
        if not session.get("authentication_success", True):
            stress_score += 0.3

        # Multiple retry attempts indicate stress
        retry_count = session.get("retry_attempts", 0)
        stress_score += min(retry_count * 0.1, 0.4)

        # Time of day can indicate stress patterns
        hour = session.get("hour_of_day", 12)
        if hour < 6 or hour > 22:  # Very early or late
            stress_score += 0.2

        # Consciousness state can indicate stress
        consciousness = session.get("consciousness_state", "unknown")
        if consciousness in ["volatile", "fragmented"]:
            stress_score += 0.3

        return min(stress_score, 1.0)

    def _calculate_session_quality(self, session: dict[str, Any]) -> float:
        """Calculate overall session quality score"""

        quality_score = 0.7  # Base quality

        # Authentication success
        if session.get("authentication_success", True):
            quality_score += 0.2
        else:
            quality_score -= 0.3

        # Consciousness score
        consciousness_score = session.get("consciousness_score", 0.5)
        quality_score += (consciousness_score - 0.5) * 0.3

        # Cultural compatibility
        cultural_score = session.get("cultural_compatibility", 0.5)
        quality_score += (cultural_score - 0.5) * 0.2

        return max(0.0, min(1.0, quality_score))

    def _estimate_energy_level(
        self, consciousness_state: str, attention_metrics: dict[str, float]
    ) -> float:
        """Estimate energy level from consciousness and metrics"""

        state_weights = self.consciousness_weights.get(consciousness_state, {"energy": 0.5})
        base_energy = state_weights["energy"]

        attention = attention_metrics.get("attention", 0.5)
        creativity = attention_metrics.get("creativity", 0.5)

        # Energy estimation
        estimated_energy = base_energy * 0.6 + attention * 0.3 + creativity * 0.1

        return max(0.0, min(1.0, estimated_energy))

    def _calculate_mood_slope(
        self, emotional_data: list[EmotionalDataPoint]
    ) -> tuple[MoodSlope, float]:
        """Calculate mood slope using linear regression"""

        if len(emotional_data) < 2:
            return MoodSlope.UNKNOWN, 0.0

        # Prepare data for regression
        x_values = [
            (dp.timestamp - emotional_data[0].timestamp).total_seconds() / 86400
            for dp in emotional_data
        ]  # Days
        y_values = [dp.mood_valence for dp in emotional_data]

        # Calculate slope using numpy
        try:
            slope, _ = np.polyfit(x_values, y_values, 1)
        except BaseException:
            # Fallback calculation
            slope = (
                (y_values[-1] - y_values[0]) / (x_values[-1] - x_values[0])
                if x_values[-1] != x_values[0]
                else 0.0
            )

        # Classify slope
        if slope > 0.05:
            mood_slope = MoodSlope.STEEP_POSITIVE
        elif slope > 0.02:
            mood_slope = MoodSlope.GRADUAL_POSITIVE
        elif slope > 0.01:
            mood_slope = MoodSlope.STABLE_POSITIVE
        elif slope > -0.01:
            mood_slope = MoodSlope.NEUTRAL
        elif slope > -0.02:
            mood_slope = MoodSlope.STABLE_NEGATIVE
        elif slope > -0.05:
            mood_slope = MoodSlope.GRADUAL_NEGATIVE
        else:
            mood_slope = MoodSlope.STEEP_NEGATIVE

        return mood_slope, slope

    def _determine_overall_trend(
        self, emotional_data: list[EmotionalDataPoint], slope_value: float
    ) -> EmotionalTrend:
        """Determine overall emotional trend"""

        if len(emotional_data) < 3:
            return EmotionalTrend.UNKNOWN

        # Calculate variance to detect volatility
        mood_values = [dp.mood_valence for dp in emotional_data]
        variance = statistics.variance(mood_values) if len(mood_values) > 1 else 0

        if variance > 0.3:
            return EmotionalTrend.VOLATILE
        elif slope_value > 0.02:
            return EmotionalTrend.IMPROVING
        elif slope_value < -0.02:
            return EmotionalTrend.DECLINING
        else:
            return EmotionalTrend.STABLE

    def _calculate_stability_score(self, emotional_data: list[EmotionalDataPoint]) -> float:
        """Calculate emotional stability score"""

        if len(emotional_data) < 2:
            return 0.5

        # Calculate coefficient of variation for key metrics
        mood_values = [dp.mood_valence for dp in emotional_data]
        attention_values = [dp.attention_level for dp in emotional_data]
        energy_values = [dp.energy_level for dp in emotional_data]

        stability_factors = []

        for values in [mood_values, attention_values, energy_values]:
            if len(values) > 1:
                mean_val = statistics.mean(values)
                if mean_val != 0:
                    cv = statistics.stdev(values) / abs(mean_val)
                    # Lower CV = higher stability
                    stability_factors.append(1.0 - min(cv, 1.0))

        return statistics.mean(stability_factors) if stability_factors else 0.5

    async def _detect_emotional_patterns(
        self, emotional_data: list[EmotionalDataPoint]
    ) -> list[EmotionalPattern]:
        """Detect emotional patterns in the data"""

        patterns = []

        if len(emotional_data) < 7:  # Need at least a week of data
            return patterns

        # Pattern 1: Consistent consciousness state preference
        consciousness_states = [dp.consciousness_state for dp in emotional_data]
        most_common_state = max(set(consciousness_states), key=consciousness_states.count)
        state_frequency = consciousness_states.count(most_common_state) / len(consciousness_states)

        if state_frequency > 0.7:
            patterns.append(
                EmotionalPattern(
                    pattern_type="consciousness_preference",
                    confidence=state_frequency,
                    duration_days=len(emotional_data),
                    trend_direction=EmotionalTrend.STABLE,
                    mood_slope=MoodSlope.NEUTRAL,
                    key_indicators=[f"Prefers {most_common_state} consciousness state"],
                    recommendations=[f"Optimize authentication flow for {most_common_state} state"],
                )
            )

        # Pattern 2: Weekly cycle detection
        weekday_moods = {}
        for dp in emotional_data:
            weekday = dp.timestamp.weekday()
            if weekday not in weekday_moods:
                weekday_moods[weekday] = []
            weekday_moods[weekday].append(dp.mood_valence)

        if len(weekday_moods) >= 5:  # Have data for most weekdays
            weekday_averages = {day: statistics.mean(moods) for day, moods in weekday_moods.items()}
            max_day = max(weekday_averages, key=weekday_averages.get)
            min_day = min(weekday_averages, key=weekday_averages.get)

            if weekday_averages[max_day] - weekday_averages[min_day] > 0.3:
                patterns.append(
                    EmotionalPattern(
                        pattern_type="weekly_cycle",
                        confidence=0.8,
                        duration_days=len(emotional_data),
                        trend_direction=EmotionalTrend.VOLATILE,
                        mood_slope=MoodSlope.NEUTRAL,
                        key_indicators=[
                            f"Higher mood on day {max_day}",
                            f"Lower mood on day {min_day}",
                        ],
                        recommendations=["Consider workload adjustment based on weekly patterns"],
                    )
                )

        return patterns

    def _identify_risk_factors(
        self, emotional_data: list[EmotionalDataPoint], patterns: list[EmotionalPattern]
    ) -> list[str]:
        """Identify emotional risk factors"""

        risk_factors = []

        # Check for declining trends
        recent_data = emotional_data[-7:] if len(emotional_data) >= 7 else emotional_data
        if recent_data:
            recent_mood_avg = statistics.mean([dp.mood_valence for dp in recent_data])
            if recent_mood_avg < -0.3:
                risk_factors.append("Sustained negative mood pattern")

        # Check stress indicators
        stress_levels = [dp.stress_indicators for dp in emotional_data]
        if stress_levels:
            avg_stress = statistics.mean(stress_levels)
            if avg_stress > 0.6:
                risk_factors.append("Elevated stress indicators")

        # Check session quality
        quality_scores = [dp.session_quality for dp in emotional_data]
        if quality_scores:
            avg_quality = statistics.mean(quality_scores)
            if avg_quality < 0.4:
                risk_factors.append("Declining session quality")

        # Check for volatile patterns
        volatile_patterns = [p for p in patterns if p.trend_direction == EmotionalTrend.VOLATILE]
        if volatile_patterns:
            risk_factors.append("Emotional volatility detected")

        return risk_factors

    def _identify_positive_indicators(
        self, emotional_data: list[EmotionalDataPoint], patterns: list[EmotionalPattern]
    ) -> list[str]:
        """Identify positive emotional indicators"""

        positive_indicators = []

        # Check for improving trends
        recent_data = emotional_data[-7:] if len(emotional_data) >= 7 else emotional_data
        if len(recent_data) >= 2:
            recent_improvement = recent_data[-1].mood_valence - recent_data[0].mood_valence
            if recent_improvement > 0.2:
                positive_indicators.append("Recent mood improvement")

        # Check creativity levels
        creativity_levels = [dp.creativity_index for dp in emotional_data]
        if creativity_levels:
            avg_creativity = statistics.mean(creativity_levels)
            if avg_creativity > 0.7:
                positive_indicators.append("High creative engagement")

        # Check coherence scores
        coherence_scores = [dp.coherence_score for dp in emotional_data]
        if coherence_scores:
            avg_coherence = statistics.mean(coherence_scores)
            if avg_coherence > 0.8:
                positive_indicators.append("Strong mental coherence")

        # Check consciousness state diversity
        consciousness_states = {dp.consciousness_state for dp in emotional_data}
        if len(consciousness_states) >= 4:
            positive_indicators.append("Diverse consciousness state exploration")

        return positive_indicators

    def _generate_recommendations(
        self,
        mood_slope: MoodSlope,
        patterns: list[EmotionalPattern],
        stability_score: float,
    ) -> list[str]:
        """Generate personalized recommendations"""

        recommendations = []

        # Mood slope based recommendations
        if mood_slope == MoodSlope.STEEP_NEGATIVE:
            recommendations.extend(
                [
                    "Consider professional mental health support",
                    "Implement stress reduction techniques",
                    "Review recent life changes or stressors",
                ]
            )
        elif mood_slope == MoodSlope.GRADUAL_NEGATIVE:
            recommendations.extend(
                [
                    "Focus on self-care and stress management",
                    "Consider mindfulness or meditation practices",
                ]
            )
        elif mood_slope == MoodSlope.STEEP_POSITIVE:
            recommendations.append("Maintain current positive practices")

        # Stability based recommendations
        if stability_score < 0.4:
            recommendations.extend(
                [
                    "Work on establishing consistent daily routines",
                    "Consider emotional regulation techniques",
                ]
            )
        elif stability_score > 0.8:
            recommendations.append("Excellent emotional stability - continue current practices")

        # Pattern based recommendations
        for pattern in patterns:
            recommendations.extend(pattern.recommendations)

        return list(set(recommendations))  # Remove duplicates

    def _should_suggest_intervention(
        self, mood_slope: MoodSlope, risk_factors: list[str], stability_score: float
    ) -> bool:
        """Determine if intervention should be suggested"""

        high_risk_slopes = [MoodSlope.STEEP_NEGATIVE, MoodSlope.GRADUAL_NEGATIVE]

        return (
            mood_slope in high_risk_slopes
            or len(risk_factors) >= 3
            or stability_score < 0.3
            or "Sustained negative mood pattern" in risk_factors
        )

    def _create_insufficient_data_result(self, user_id: str, days: int) -> DriftAnalysisResult:
        """Create result for insufficient data"""

        return DriftAnalysisResult(
            user_id=user_id,
            analysis_period=f"{days} days",
            overall_trend=EmotionalTrend.UNKNOWN,
            mood_slope=MoodSlope.NEUTRAL,
            slope_value=0.0,
            stability_score=0.5,
            patterns=[],
            risk_factors=["Insufficient data for analysis"],
            positive_indicators=[],
            recommendations=["Continue using the system to enable emotional pattern analysis"],
            intervention_suggested=False,
        )

    def _create_error_result(self, user_id: str, days: int, error: str) -> DriftAnalysisResult:
        """Create error result"""

        return DriftAnalysisResult(
            user_id=user_id,
            analysis_period=f"{days} days",
            overall_trend=EmotionalTrend.UNKNOWN,
            mood_slope=MoodSlope.NEUTRAL,
            slope_value=0.0,
            stability_score=0.0,
            patterns=[],
            risk_factors=[f"Analysis error: {error}"],
            positive_indicators=[],
            recommendations=["Contact support for emotional drift analysis issues"],
            intervention_suggested=False,
        )


async def main():
    """Demo emotional drift monitoring"""
    print("🧠 LUKHAS Emotional Drift Monitoring System")
    print("=" * 55)

    monitor = EmotionalDriftMonitor()

    # Mock session history
    session_history = []
    base_time = datetime.utcnow() - timedelta(days=30)

    consciousness_cycle = [
        "focused",
        "creative",
        "meditative",
        "analytical",
        "flow_state",
    ]

    for i in range(30):
        session_time = base_time + timedelta(days=i)
        consciousness = consciousness_cycle[i % len(consciousness_cycle)]

        # Simulate gradual mood improvement
        mood_trend = 0.5 + (i * 0.01)  # Gradual improvement

        session = {
            "timestamp": session_time.isoformat(),
            "consciousness_state": consciousness,
            "attention_metrics": {
                "attention": 0.6 + (i * 0.005),
                "creativity": 0.5 + (i * 0.008),
                "coherence": 0.7 + (i * 0.003),
            },
            "authentication_success": True,
            "consciousness_score": mood_trend,
            "cultural_compatibility": 0.8,
            "hour_of_day": (9 + (i % 12)) % 24,
        }

        session_history.append(session)

    # Analyze emotional drift
    result = await monitor.analyze_emotional_drift("demo_user", session_history, 30)

    print(f"\n📊 Emotional Drift Analysis for {result.user_id}")
    print(f"📅 Period: {result.analysis_period}")
    print(f"📈 Overall Trend: {result.overall_trend.value}")
    print(f"📉 Mood Slope: {result.mood_slope.value} (value: {result.slope_value:.4f})")
    print(f"⚖️ Stability Score: {result.stability_score:.2f}")

    if result.patterns:
        print("\n🔍 Detected Patterns:")
        for pattern in result.patterns:
            print(f"  • {pattern.pattern_type}: {pattern.confidence:.2f} confidence")
            for indicator in pattern.key_indicators:
                print(f"    - {indicator}")

    if result.positive_indicators:
        print("\n✅ Positive Indicators:")
        for indicator in result.positive_indicators:
            print(f"  • {indicator}")

    if result.risk_factors:
        print("\n⚠️ Risk Factors:")
        for risk in result.risk_factors:
            print(f"  • {risk}")

    print("\n💡 Recommendations:")
    for rec in result.recommendations:
        print(f"  • {rec}")

    if result.intervention_suggested:
        print("\n🚨 Intervention Suggested: Professional support recommended")
    else:
        print("\n✅ No Intervention Needed: Emotional patterns within healthy range")


if __name__ == "__main__":
    asyncio.run(main())
