"""
Bio Adaptation Engine for ABAS (ΛBAS) System
Provides biological adaptation and biometric processing capabilities
"""
import streamlit as st
from datetime import timezone

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class BiometricType(Enum, timezone):
    """Types of biometric data"""

    HEART_RATE = "heart_rate"
    STRESS_LEVEL = "stress_level"
    AROUSAL = "arousal"
    ATTENTION = "attention"
    TEMPERATURE = "temperature"
    SLEEP_QUALITY = "sleep_quality"


@dataclass
class BiometricProfile:
    """User biometric profile"""

    user_id: str
    baseline_heart_rate: float
    stress_tolerance: float
    arousal_sensitivity: float
    attention_span: float
    temperature_norm: float
    sleep_pattern: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class AdaptationRecommendation:
    """Bio adaptation recommendation"""

    recommendation_type: str
    priority: str  # high, medium, low
    description: str
    parameters: dict[str, Any]
    confidence: float


class BioAdaptationEngine:
    """Main bio adaptation engine for ABAS system"""

    def __init__(self):
        self.user_profiles = {}
        self.adaptation_patterns = {}
        self.biometric_thresholds = {
            BiometricType.HEART_RATE: {"min": 60, "max": 120, "optimal": 70},
            BiometricType.STRESS_LEVEL: {"min": 0.0, "max": 1.0, "optimal": 0.3},
            BiometricType.AROUSAL: {"min": 0.0, "max": 1.0, "optimal": 0.6},
            BiometricType.ATTENTION: {"min": 0.0, "max": 1.0, "optimal": 0.8},
            BiometricType.TEMPERATURE: {"min": 36.0, "max": 39.0, "optimal": 37.0},
            BiometricType.SLEEP_QUALITY: {"min": 0.0, "max": 1.0, "optimal": 0.8},
        }

    async def analyze_biometric_patterns(self, biometric_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze biometric data patterns"""
        user_id = biometric_data.get("user_id", "unknown")

        # Extract biometric values
        heart_rate = biometric_data.get("heart_rate", 70)
        stress_level = biometric_data.get("stress_level", 0.3)
        biometric_data.get("arousal", 0.5)
        attention = biometric_data.get("attention", 0.7)
        biometric_data.get("temperature", 37.0)
        sleep_quality = biometric_data.get("sleep_quality", 0.8)

        # Analyze patterns
        patterns = {}

        # Heart rate analysis
        hr_threshold = self.biometric_thresholds[BiometricType.HEART_RATE]
        if heart_rate > hr_threshold["optimal"] * 1.3:
            patterns["heart_rate"] = {
                "status": "elevated",
                "deviation": (heart_rate - hr_threshold["optimal"]) / hr_threshold["optimal"],
                "recommendation": "relaxation_techniques",
            }
        elif heart_rate < hr_threshold["optimal"] * 0.7:
            patterns["heart_rate"] = {
                "status": "low",
                "deviation": (hr_threshold["optimal"] - heart_rate) / hr_threshold["optimal"],
                "recommendation": "mild_stimulation",
            }
        else:
            patterns["heart_rate"] = {
                "status": "normal",
                "deviation": 0.0,
                "recommendation": "maintain_current",
            }

        # Stress analysis
        if stress_level > 0.7:
            patterns["stress"] = {
                "status": "high",
                "level": stress_level,
                "recommendation": "stress_reduction",
            }
        elif stress_level < 0.2:
            patterns["stress"] = {
                "status": "low",
                "level": stress_level,
                "recommendation": "engagement_increase",
            }
        else:
            patterns["stress"] = {
                "status": "optimal",
                "level": stress_level,
                "recommendation": "maintain_current",
            }

        # Attention analysis
        patterns["attention"] = {
            "focus_level": attention,
            "status": ("high" if attention > 0.8 else "medium" if attention > 0.5 else "low"),
            "recommendation": ("focus_enhancement" if attention < 0.6 else "maintain_focus"),
        }

        # Sleep quality analysis
        patterns["sleep"] = {
            "quality_score": sleep_quality,
            "status": ("excellent" if sleep_quality > 0.8 else "good" if sleep_quality > 0.6 else "poor"),
            "recommendation": ("sleep_optimization" if sleep_quality < 0.7 else "maintain_routine"),
        }

        # Overall assessment
        overall_score = (
            (1.0 - abs(patterns["heart_rate"]["deviation"])) * 0.3
            + (1.0 - patterns["stress"]["level"]) * 0.3
            + patterns["attention"]["focus_level"] * 0.2
            + patterns["sleep"]["quality_score"] * 0.2
        )

        return {
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "patterns": patterns,
            "overall_score": overall_score,
            "adaptation_needed": overall_score < 0.7,
            "priority_areas": [
                key
                for key, value in patterns.items()
                if "status" in value and value["status"] in ["high", "low", "poor"]
            ],
        }

    async def adapt_dream_parameters(
        self, biometric_data: dict[str, Any], dream_params: dict[str, Any]
    ) -> dict[str, Any]:
        """Adapt dream parameters based on biometric data"""

        # Get current biometric analysis
        analysis = await self.analyze_biometric_patterns(biometric_data)
        patterns = analysis["patterns"]

        # Start with original parameters
        adapted_params = dream_params.copy()

        # Adapt intensity based on stress and arousal
        stress_level = patterns["stress"]["level"]
        if stress_level > 0.7:
            # High stress - reduce intensity
            adapted_params["intensity"] = min(adapted_params.get("intensity", 0.5) * 0.7, 1.0)
        elif stress_level < 0.3:
            # Low stress - can increase intensity
            adapted_params["intensity"] = min(adapted_params.get("intensity", 0.5) * 1.3, 1.0)

        # Adapt duration based on attention and sleep quality
        attention = patterns["attention"]["focus_level"]
        sleep_quality = patterns["sleep"]["quality_score"]

        base_duration = adapted_params.get("duration", 30)
        if attention < 0.5 or sleep_quality < 0.6:
            # Poor attention or sleep - shorter sessions
            adapted_params["duration"] = max(base_duration * 0.8, 10)
        elif attention > 0.8 and sleep_quality > 0.8:
            # Good attention and sleep - can extend
            adapted_params["duration"] = min(base_duration * 1.2, 120)

        # Adapt type based on overall state
        adapted_params.get("type", "free")
        if stress_level > 0.8:
            adapted_params["type"] = "guided"  # More structure for high stress
        elif attention > 0.9 and stress_level < 0.3:
            adapted_params["type"] = "lucid"  # Allow more control for optimal state

        # Add adaptation metadata
        adapted_params["adaptation_info"] = {
            "original_params": dream_params,
            "biometric_influence": {
                "stress_adjustment": patterns["stress"]["status"],
                "attention_adjustment": patterns["attention"]["status"],
                "sleep_adjustment": patterns["sleep"]["status"],
            },
            "adaptation_confidence": analysis["overall_score"],
            "adapted_at": datetime.now(timezone.utc).isoformat(),
        }

        return adapted_params

    async def generate_bio_feedback(self, biometric_data: dict[str, Any]) -> list[AdaptationRecommendation]:
        """Generate biometric feedback recommendations"""

        analysis = await self.analyze_biometric_patterns(biometric_data)
        patterns = analysis["patterns"]
        recommendations = []

        # Heart rate recommendations
        hr_pattern = patterns["heart_rate"]
        if hr_pattern["status"] == "elevated":
            recommendations.append(
                AdaptationRecommendation(
                    recommendation_type="heart_rate_reduction",
                    priority="high",
                    description="Heart rate is elevated. Consider breathing exercises and relaxation.",
                    parameters={
                        "technique": "deep_breathing",
                        "duration": 5,
                        "repetitions": 3,
                    },
                    confidence=0.9,
                )
            )
        elif hr_pattern["status"] == "low":
            recommendations.append(
                AdaptationRecommendation(
                    recommendation_type="heart_rate_stimulation",
                    priority="medium",
                    description="Heart rate is low. Light physical activity may help.",
                    parameters={
                        "activity": "light_movement",
                        "duration": 3,
                        "intensity": "low",
                    },
                    confidence=0.7,
                )
            )

        # Stress recommendations
        stress_pattern = patterns["stress"]
        if stress_pattern["status"] == "high":
            recommendations.append(
                AdaptationRecommendation(
                    recommendation_type="stress_reduction",
                    priority="high",
                    description="Stress levels are high. Relaxation techniques recommended.",
                    parameters={
                        "techniques": ["meditation", "progressive_relaxation"],
                        "duration": 10,
                        "frequency": "immediate",
                    },
                    confidence=0.95,
                )
            )

        # Attention recommendations
        attention_pattern = patterns["attention"]
        if attention_pattern["status"] == "low":
            recommendations.append(
                AdaptationRecommendation(
                    recommendation_type="focus_enhancement",
                    priority="medium",
                    description="Attention levels are low. Focus exercises may help.",
                    parameters={
                        "exercises": ["mindfulness", "attention_training"],
                        "duration": 7,
                        "difficulty": "easy",
                    },
                    confidence=0.8,
                )
            )

        # Sleep recommendations
        sleep_pattern = patterns["sleep"]
        if sleep_pattern["status"] == "poor":
            recommendations.append(
                AdaptationRecommendation(
                    recommendation_type="sleep_optimization",
                    priority="high",
                    description="Sleep quality is poor. Sleep hygiene improvements needed.",
                    parameters={
                        "improvements": ["sleep_schedule", "environment_optimization"],
                        "timeline": "gradual",
                        "monitoring_period": "14_days",
                    },
                    confidence=0.85,
                )
            )

        return recommendations

    async def update_bio_profile(self, user_id: str, biometric_data: dict[str, Any]) -> dict[str, Any]:
        """Update user biometric profile"""

        if user_id not in self.user_profiles:
            # Create new profile
            self.user_profiles[user_id] = BiometricProfile(
                user_id=user_id,
                baseline_heart_rate=biometric_data.get("heart_rate", 70),
                stress_tolerance=1.0 - biometric_data.get("stress_level", 0.3),
                arousal_sensitivity=biometric_data.get("arousal", 0.5),
                attention_span=biometric_data.get("attention", 0.7),
                temperature_norm=biometric_data.get("temperature", 37.0),
                sleep_pattern={"quality": biometric_data.get("sleep_quality", 0.8)},
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        else:
            # Update existing profile with moving averages
            profile = self.user_profiles[user_id]
            alpha = 0.1  # Learning rate for exponential moving average

            profile.baseline_heart_rate = (
                alpha * biometric_data.get("heart_rate", profile.baseline_heart_rate)
                + (1 - alpha) * profile.baseline_heart_rate
            )

            current_stress = biometric_data.get("stress_level", 1.0 - profile.stress_tolerance)
            profile.stress_tolerance = alpha * (1.0 - current_stress) + (1 - alpha) * profile.stress_tolerance

            profile.arousal_sensitivity = (
                alpha * biometric_data.get("arousal", profile.arousal_sensitivity)
                + (1 - alpha) * profile.arousal_sensitivity
            )

            profile.attention_span = (
                alpha * biometric_data.get("attention", profile.attention_span) + (1 - alpha) * profile.attention_span
            )

            profile.temperature_norm = (
                alpha * biometric_data.get("temperature", profile.temperature_norm)
                + (1 - alpha) * profile.temperature_norm
            )

            current_sleep = biometric_data.get("sleep_quality", profile.sleep_pattern["quality"])
            profile.sleep_pattern["quality"] = alpha * current_sleep + (1 - alpha) * profile.sleep_pattern["quality"]

            profile.updated_at = datetime.now(timezone.utc)

        # Return profile summary
        profile = self.user_profiles[user_id]
        return {
            "user_id": user_id,
            "profile_updated": True,
            "baseline_metrics": {
                "heart_rate": profile.baseline_heart_rate,
                "stress_tolerance": profile.stress_tolerance,
                "arousal_sensitivity": profile.arousal_sensitivity,
                "attention_span": profile.attention_span,
                "temperature_norm": profile.temperature_norm,
                "sleep_quality": profile.sleep_pattern["quality"],
            },
            "profile_age_days": (datetime.now(timezone.utc) - profile.created_at).days,
            "last_updated": profile.updated_at.isoformat(),
        }
