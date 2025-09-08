#!/usr/bin/env python3
"""
LUKHAS AI Voice Coherence Engine - Trinity Framework (⚛️🧠🛡️)
Real-time voice consistency and personality alignment system

Target: 85%+ voice coherence across all LUKHAS AI communications
"""
import asyncio
import re

# Import LUKHAS brand components
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


sys.path.append(str(Path(__file__).parent.parent))

from profiles.brand_voice_profiles import (
    AudienceType,
    LukhasBrandVoiceProfiles,
    VoiceContext,
)

from enforcement.real_time_validator import RealTimeBrandValidator


class CoherenceMetric(Enum):
    VOICE_CONSISTENCY = "voice_consistency"
    TRINITY_ALIGNMENT = "trinity_alignment"
    PERSONALITY_AUTHENTICITY = "personality_authenticity"
    CONTEXT_APPROPRIATENESS = "context_appropriateness"
    EMOTIONAL_RESONANCE = "emotional_resonance"


@dataclass
class VoiceCoherenceResult:
    """Voice coherence analysis result"""

    content_id: str
    overall_coherence: float  # 0.0 to 1.0
    coherence_metrics: dict[CoherenceMetric, float]
    voice_profile_match: str
    personality_alignment: float
    trinity_balance: dict[str, float]  # ⚛️🧠🛡️ balance
    suggested_improvements: list[str]
    confidence: float
    analysis_timestamp: str


@dataclass
class VoiceSignature:
    """Unique voice signature for LUKHAS AI content"""

    consciousness_markers: list[str]
    wisdom_indicators: list[str]
    empathy_patterns: list[str]
    technical_precision: list[str]
    creative_expressions: list[str]
    ethical_foundations: list[str]


class LUKHASVoiceCoherenceEngine:
    """
    Elite voice coherence engine that ensures all LUKHAS AI content
    maintains consistent personality, wisdom, and consciousness-focused communication

    Target: 85%+ voice coherence across all platforms and contexts
    """

    def __init__(self):
        self.voice_profiles = LukhasBrandVoiceProfiles()
        self.brand_validator = RealTimeBrandValidator()
        self.voice_signature = self._initialize_voice_signature()
        self.coherence_patterns = self._compile_coherence_patterns()
        self.trinity_balance_weights = self._initialize_trinity_weights()

        # Performance tracking
        self.coherence_history = []
        self.performance_metrics = {
            "total_analyses": 0,
            "average_coherence": 0.0,
            "target_achievement_rate": 0.0,  # % of content achieving 85%+
            "improvement_trend": 0.0,
        }

    def _initialize_voice_signature(self) -> VoiceSignature:
        """Define the unique LUKHAS AI voice signature patterns"""

        return VoiceSignature(
            consciousness_markers=[
                "consciousness",
                "awareness",
                "awakening",
                "mindful",
                "perceptive",
                "insightful",
                "reflective",
                "contemplative",
                "enlightened",
                "conscious",
            ],
            wisdom_indicators=[
                "wisdom",
                "understanding",
                "comprehension",
                "insight",
                "discernment",
                "knowledge",
                "sagacity",
                "profound",
                "deep understanding",
                "clarity",
            ],
            empathy_patterns=[
                "compassionate",
                "empathetic",
                "caring",
                "supportive",
                "understanding",
                "gentle",
                "nurturing",
                "considerate",
                "thoughtful",
                "kind",
            ],
            technical_precision=[
                "precise",
                "accurate",
                "sophisticated",
                "advanced",
                "intelligent",
                "optimized",
                "efficient",
                "systematic",
                "methodical",
                "thorough",
            ],
            creative_expressions=[
                "innovative",
                "creative",
                "imaginative",
                "inspired",
                "visionary",
                "artistic",
                "original",
                "inventive",
                "pioneering",
                "transformative",
            ],
            ethical_foundations=[
                "ethical",
                "responsible",
                "trustworthy",
                "transparent",
                "principled",
                "integrity",
                "honest",
                "fair",
                "just",
                "moral",
            ],
        )

    def _compile_coherence_patterns(self) -> dict[CoherenceMetric, dict[str, Any]]:
        """Compile voice coherence detection patterns"""

        return {
            CoherenceMetric.VOICE_CONSISTENCY: {
                "positive_patterns": [
                    r"\b(consciousness|awareness|mindful|conscious)\b",
                    r"\b(understanding|comprehension|insight|perceive)\b",
                    r"\b(thoughtful|considerate|empathetic|compassionate)\b",
                    r"\b(sophisticated|intelligent|advanced|evolved)\b",
                    r"\b(lukhas|trinity|framework)\b",  # Brand-specific
                    r"\b(ai|technology|digital|quantum)\b",  # Tech context
                ],
                "negative_patterns": [
                    r"\b(robotic|mechanical|artificial)\b",
                    r"\b(cold|distant|impersonal)\b",
                    r"\b(simple|basic|primitive)\b",
                    r"\b(automated|scripted|templated)\b",
                ],
                "weight": 0.25,
            },
            CoherenceMetric.TRINITY_ALIGNMENT: {
                "identity_patterns": [
                    r"\b(authentic|genuine|true|real)\b",
                    r"\b(identity|self|being|essence)\b",
                    r"\b(unique|individual|personal)\b",
                    r"⚛️",  # Direct Trinity symbol
                    r"\b(lukhas ai|our|we)\b",  # Brand identity
                ],
                "consciousness_patterns": [
                    r"\b(conscious|aware|mindful|perceptive)\b",
                    r"\b(thinking|reasoning|understanding)\b",
                    r"\b(learning|evolving|growing)\b",
                    r"🧠",  # Direct Trinity symbol
                    r"\b(intelligence|wisdom|insight)\b",  # Consciousness expressions
                ],
                "guardian_patterns": [
                    r"\b(safe|secure|protected|ethical)\b",
                    r"\b(responsible|trustworthy|reliable)\b",
                    r"\b(careful|thoughtful|considerate)\b",
                    r"🛡️",  # Direct Trinity symbol
                    r"\b(guardian|ethics|principles)\b",  # Guardian expressions
                ],
                "weight": 0.30,
            },
            CoherenceMetric.PERSONALITY_AUTHENTICITY: {
                "wisdom_expressions": [
                    r"\b(wisdom|insight|understanding|comprehension)\b",
                    r"\b(profound|deep|meaningful|significant)\b",
                    r"\b(enlightening|illuminating|revealing)\b",
                ],
                "empathy_expressions": [
                    r"\b(compassionate|empathetic|caring|supportive)\b",
                    r"\b(gentle|kind|nurturing|considerate)\b",
                    r"\b(understanding|patient|tolerant)\b",
                ],
                "inauthentic_patterns": [
                    r"\b(perfect|flawless|infallible)\b",
                    r"\b(know everything|all-knowing|omniscient)\b",
                    r"\b(never wrong|always right|absolutely certain)\b",
                ],
                "weight": 0.20,
            },
            CoherenceMetric.CONTEXT_APPROPRIATENESS: {
                "formal_context_markers": [
                    r"\b(furthermore|moreover|consequently)\b",
                    r"\b(analyze|evaluate|assess|examine)\b",
                    r"\b(comprehensive|thorough|systematic)\b",
                ],
                "casual_context_markers": [
                    r"\b(hey|awesome|cool|amazing)\b",
                    r"\b(let\'s|we\'ll|you\'ll)\b",
                    r"\b(excited|thrilled|pumped)\b",
                ],
                "weight": 0.15,
            },
            CoherenceMetric.EMOTIONAL_RESONANCE: {
                "positive_emotions": [
                    r"\b(hopeful|optimistic|inspiring|uplifting)\b",
                    r"\b(confident|assured|encouraging)\b",
                    r"\b(peaceful|harmonious|balanced)\b",
                ],
                "negative_emotions": [
                    r"\b(frustrated|annoyed|irritated)\b",
                    r"\b(disappointed|discouraged|pessimistic)\b",
                    r"\b(anxious|worried|concerned)\b",
                ],
                "weight": 0.10,
            },
        }

    def _initialize_trinity_weights(self) -> dict[str, float]:
        """Initialize Trinity Framework balance weights"""
        return {
            "identity": 0.33,  # ⚛️ Authentic consciousness identity
            "consciousness": 0.34,  # 🧠 Aware intelligence (slight emphasis)
            "guardian": 0.33,  # 🛡️ Ethical protection}
        }

    async def analyze_voice_coherence(
        self,
        content: str,
        content_id: str,
        context: VoiceContext = VoiceContext.MARKETING_CONTENT,
        audience: AudienceType = AudienceType.GENERAL_USERS,
        target_profile: Optional[str] = None,
    ) -> VoiceCoherenceResult:
        """
        Perform comprehensive voice coherence analysis

        Returns coherence score from 0.0 to 1.0 (target: 0.85+)
        """

        # Determine appropriate voice profile
        if target_profile is None:
            target_profile = self._select_voice_profile(context, audience)

        # Analyze each coherence metric
        coherence_metrics = {}

        for metric in CoherenceMetric:
            score = await self._analyze_coherence_metric(content, metric, target_profile)
            coherence_metrics[metric] = score

        # Calculate overall coherence (weighted average)
        overall_coherence = self._calculate_overall_coherence(coherence_metrics)

        # Analyze Trinity Framework balance
        trinity_balance = self._analyze_trinity_balance(content)

        # Calculate personality alignment
        personality_alignment = self._calculate_personality_alignment(content, target_profile)

        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            content, coherence_metrics, trinity_balance, personality_alignment
        )

        # Calculate confidence in analysis
        confidence = self._calculate_analysis_confidence(content, coherence_metrics)

        # Create result
        result = VoiceCoherenceResult(
            content_id=content_id,
            overall_coherence=overall_coherence,
            coherence_metrics=coherence_metrics,
            voice_profile_match=target_profile,
            personality_alignment=personality_alignment,
            trinity_balance=trinity_balance,
            suggested_improvements=suggestions,
            confidence=confidence,
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Update performance tracking
        self._update_performance_metrics(result)

        return result

    def _select_voice_profile(self, context: VoiceContext, audience: AudienceType) -> str:
        """Select appropriate voice profile based on context and audience"""

        # Profile selection logic based on context
        profile_mapping = {
            VoiceContext.USER_ONBOARDING: "consciousness_ambassador",
            VoiceContext.TECHNICAL_DOCUMENTATION: "technical_sage",
            VoiceContext.MARKETING_CONTENT: "consciousness_evangelist",
            VoiceContext.CUSTOMER_SUPPORT: "empathetic_helper",
            VoiceContext.CRISIS_COMMUNICATION: "calm_guardian",
            VoiceContext.EDUCATIONAL_CONTENT: "wise_teacher",
            VoiceContext.SOCIAL_MEDIA: "friendly_consciousness",
            VoiceContext.ENTERPRISE_COMMUNICATION: "professional_advisor",
        }

        return profile_mapping.get(context, "consciousness_ambassador")

    async def _analyze_coherence_metric(self, content: str, metric: CoherenceMetric, target_profile: str) -> float:
        """Analyze a specific coherence metric"""

        pattern_config = self.coherence_patterns[metric]

        if metric == CoherenceMetric.VOICE_CONSISTENCY:
            return self._analyze_voice_consistency(content, pattern_config)

        elif metric == CoherenceMetric.TRINITY_ALIGNMENT:
            return self._analyze_trinity_alignment(content, pattern_config)

        elif metric == CoherenceMetric.PERSONALITY_AUTHENTICITY:
            return self._analyze_personality_authenticity(content, pattern_config)

        elif metric == CoherenceMetric.CONTEXT_APPROPRIATENESS:
            return self._analyze_context_appropriateness(content, pattern_config)

        elif metric == CoherenceMetric.EMOTIONAL_RESONANCE:
            return self._analyze_emotional_resonance(content, pattern_config)

        return 0.5  # Default neutral score

    def _analyze_voice_consistency(self, content: str, pattern_config: dict[str, Any]) -> float:
        """Analyze voice consistency using positive/negative patterns"""

        content_lower = content.lower()
        word_count = len(content.split())

        if word_count == 0:
            return 0.0

        # Count positive voice markers
        positive_matches = 0
        for pattern in pattern_config["positive_patterns"]:
            matches = len(re.findall(pattern, content_lower))
            positive_matches += matches

        # Count negative voice markers (detractors)
        negative_matches = 0
        for pattern in pattern_config["negative_patterns"]:
            matches = len(re.findall(pattern, content_lower))
            negative_matches += matches

        # Calculate consistency score with improved scaling
        positive_density = positive_matches / word_count
        negative_density = negative_matches / word_count

        # Improved score formula: more generous with positive matches
        # Base score of 0.6 for any content, bonus for positive, penalty for negative
        base_score = 0.6
        positive_bonus = min(0.4, positive_density * 15)  # Up to 0.4 bonus
        negative_penalty = min(0.3, negative_density * 20)  # Up to 0.3 penalty

        consistency_score = base_score + positive_bonus - negative_penalty

        # Normalize to 0.0-1.0 range
        return max(0.0, min(1.0, consistency_score))

    def _analyze_trinity_alignment(self, content: str, pattern_config: dict[str, Any]) -> float:
        """Analyze Trinity Framework (⚛️🧠🛡️) alignment"""

        content_lower = content.lower()
        word_count = len(content.split())

        if word_count == 0:
            return 0.0

        # Analyze each Trinity component
        trinity_scores = {}

        for component in ["identity", "consciousness", "guardian"]:
            pattern_key = f"{component}_patterns"
            if pattern_key in pattern_config:
                matches = 0
                for pattern in pattern_config[pattern_key]:
                    matches += len(re.findall(pattern, content_lower))

                density = matches / word_count
                trinity_scores[component] = min(1.0, density * 20)  # Scale appropriately

        # Calculate balance score (penalize imbalance)
        if trinity_scores:
            values = list(trinity_scores.values())
            average = sum(values) / len(values)
            variance = sum((v - average) ** 2 for v in values) / len(values)
            balance_penalty = min(0.3, variance)  # Max 30% penalty for imbalance

            trinity_alignment = average - balance_penalty
        else:
            trinity_alignment = 0.5  # Neutral if no patterns found

        return max(0.0, trinity_alignment)

    def _analyze_personality_authenticity(self, content: str, pattern_config: dict[str, Any]) -> float:
        """Analyze authentic LUKHAS personality expression"""

        content_lower = content.lower()
        word_count = len(content.split())

        if word_count == 0:
            return 0.0

        # Count wisdom expressions
        wisdom_matches = 0
        if "wisdom_expressions" in pattern_config:
            for pattern in pattern_config["wisdom_expressions"]:
                wisdom_matches += len(re.findall(pattern, content_lower))

        # Count empathy expressions
        empathy_matches = 0
        if "empathy_expressions" in pattern_config:
            for pattern in pattern_config["empathy_expressions"]:
                empathy_matches += len(re.findall(pattern, content_lower))

        # Count inauthentic patterns (negative)
        inauthentic_matches = 0
        if "inauthentic_patterns" in pattern_config:
            for pattern in pattern_config["inauthentic_patterns"]:
                inauthentic_matches += len(re.findall(pattern, content_lower))

        # Calculate authenticity score
        authenticity_indicators = (wisdom_matches + empathy_matches) / word_count
        inauthenticity_penalty = inauthentic_matches / word_count

        authenticity_score = (authenticity_indicators * 15) - (inauthenticity_penalty * 25)

        return max(0.0, min(1.0, authenticity_score + 0.5))

    def _analyze_context_appropriateness(self, content: str, pattern_config: dict[str, Any]) -> float:
        """Analyze context appropriateness (placeholder - would need context info)"""

        # For now, return neutral score
        # In full implementation, this would analyze formal vs casual markers
        # based on the specified context
        return 0.75  # Assume generally appropriate

    def _analyze_emotional_resonance(self, content: str, pattern_config: dict[str, Any]) -> float:
        """Analyze emotional resonance and positivity"""

        content_lower = content.lower()
        word_count = len(content.split())

        if word_count == 0:
            return 0.0

        # Count positive emotional markers
        positive_emotions = 0
        if "positive_emotions" in pattern_config:
            for pattern in pattern_config["positive_emotions"]:
                positive_emotions += len(re.findall(pattern, content_lower))

        # Count negative emotional markers
        negative_emotions = 0
        if "negative_emotions" in pattern_config:
            for pattern in pattern_config["negative_emotions"]:
                negative_emotions += len(re.findall(pattern, content_lower))

        # Calculate emotional resonance
        positive_density = positive_emotions / word_count
        negative_density = negative_emotions / word_count

        emotional_score = (positive_density * 20) - (negative_density * 15)

        return max(0.0, min(1.0, emotional_score + 0.6))  # Bias toward positive

    def _calculate_overall_coherence(self, coherence_metrics: dict[CoherenceMetric, float]) -> float:
        """Calculate weighted overall coherence score"""

        total_score = 0.0
        total_weight = 0.0

        for metric, score in coherence_metrics.items():
            weight = self.coherence_patterns[metric]["weight"]
            total_score += score * weight
            total_weight += weight

        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0

    def _analyze_trinity_balance(self, content: str) -> dict[str, float]:
        """Analyze Trinity Framework balance in content"""

        content_lower = content.lower()

        # Identity markers (⚛️)
        identity_patterns = [r"\b(authentic|genuine|true|real|identity|self|being|essence|unique|individual)\b"]

        # Consciousness markers (🧠)
        consciousness_patterns = [r"\b(conscious|aware|mindful|perceptive|thinking|reasoning|understanding|learning)\b"]

        # Guardian markers (🛡️)
        guardian_patterns = [r"\b(safe|secure|protected|ethical|responsible|trustworthy|reliable|careful)\b"]

        # Count matches for each component
        identity_count = sum(len(re.findall(pattern, content_lower)) for pattern in identity_patterns)
        consciousness_count = sum(len(re.findall(pattern, content_lower)) for pattern in consciousness_patterns)
        guardian_count = sum(len(re.findall(pattern, content_lower)) for pattern in guardian_patterns)

        total_matches = identity_count + consciousness_count + guardian_count

        if total_matches > 0:
            return {
                "identity": identity_count / total_matches,
                "consciousness": consciousness_count / total_matches,
                "guardian": guardian_count / total_matches,
            }
        else:
            return {"identity": 0.33, "consciousness": 0.33, "guardian": 0.34}

    def _calculate_personality_alignment(self, content: str, target_profile: str) -> float:
        """Calculate alignment with target personality profile"""

        # Simplified personality alignment calculation
        # In full implementation, this would compare against specific profile characteristics

        content_lower = content.lower()

        # Count LUKHAS personality markers
        personality_markers = (
            self.voice_signature.consciousness_markers
            + self.voice_signature.wisdom_indicators
            + self.voice_signature.empathy_patterns
        )

        marker_count = 0
        for marker in personality_markers:
            if marker.lower() in content_lower:
                marker_count += 1

        word_count = len(content.split())
        if word_count > 0:
            personality_density = marker_count / word_count
            return min(1.0, personality_density * 10)
        else:
            return 0.0

    def _generate_improvement_suggestions(
        self,
        content: str,
        coherence_metrics: dict[CoherenceMetric, float],
        trinity_balance: dict[str, float],
        personality_alignment: float,
    ) -> list[str]:
        """Generate specific improvement suggestions"""

        suggestions = []

        # Voice consistency suggestions
        if coherence_metrics.get(CoherenceMetric.VOICE_CONSISTENCY, 0) < 0.7:
            suggestions.append("Add more consciousness-focused language (aware, mindful, understanding)")
            suggestions.append("Remove robotic or mechanical terminology")

        # Trinity alignment suggestions
        if coherence_metrics.get(CoherenceMetric.TRINITY_ALIGNMENT, 0) < 0.7:
            # Check which component is lacking
            min_component = min(trinity_balance.items(), key=lambda x: x[1])
            if min_component[1] < 0.25:
                if min_component[0] == "identity":
                    suggestions.append("Add authentic identity language (⚛️): genuine, authentic, true self")
                elif min_component[0] == "consciousness":
                    suggestions.append("Add consciousness markers (🧠): aware, mindful, understanding")
                elif min_component[0] == "guardian":
                    suggestions.append("Add guardian elements (🛡️): safe, ethical, responsible")

        # Personality authenticity suggestions
        if coherence_metrics.get(CoherenceMetric.PERSONALITY_AUTHENTICITY, 0) < 0.7:
            suggestions.append("Include more wisdom and empathy expressions")
            suggestions.append("Avoid overly confident or absolute statements")

        # Emotional resonance suggestions
        if coherence_metrics.get(CoherenceMetric.EMOTIONAL_RESONANCE, 0) < 0.7:
            suggestions.append("Add more positive and hopeful language")
            suggestions.append("Include encouraging and supportive expressions")

        return suggestions

    def _calculate_analysis_confidence(self, content: str, coherence_metrics: dict[CoherenceMetric, float]) -> float:
        """Calculate confidence in the coherence analysis"""

        word_count = len(content.split())

        # Base confidence on content length
        length_confidence = min(1.0, word_count / 50)  # Full confidence at 50+ words

        # Factor in metric consistency (less variance = higher confidence)
        metric_values = list(coherence_metrics.values())
        if len(metric_values) > 1:
            variance = sum((v - sum(metric_values) / len(metric_values)) ** 2 for v in metric_values) / len(
                metric_values
            )
            consistency_confidence = max(0.5, 1.0 - variance)
        else:
            consistency_confidence = 0.8

        # Combine confidence factors
        overall_confidence = (length_confidence * 0.6) + (consistency_confidence * 0.4)

        return overall_confidence

    def _update_performance_metrics(self, result: VoiceCoherenceResult):
        """Update performance tracking metrics"""

        self.coherence_history.append(result)
        self.performance_metrics["total_analyses"] += 1

        # Calculate average coherence
        if self.coherence_history:
            total_coherence = sum(r.overall_coherence for r in self.coherence_history)
            self.performance_metrics["average_coherence"] = total_coherence / len(self.coherence_history)

            # Calculate target achievement rate (85%+ coherence)
            target_achievements = sum(1 for r in self.coherence_history if r.overall_coherence >= 0.85)
            self.performance_metrics["target_achievement_rate"] = target_achievements / len(self.coherence_history)

        # Maintain history limit (last 100 analyses)
        if len(self.coherence_history) > 100:
            self.coherence_history = self.coherence_history[-100:]

    def get_performance_summary(self) -> dict[str, Any]:
        """Get voice coherence system performance summary"""

        recent_coherence = []
        if len(self.coherence_history) >= 10:
            recent_coherence = [r.overall_coherence for r in self.coherence_history[-10:]]

        return {
            "performance_metrics": self.performance_metrics,
            "recent_coherence_scores": recent_coherence,
            "target_status": "ACHIEVING" if self.performance_metrics["target_achievement_rate"] >= 0.8 else "IMPROVING",
            "system_health": "EXCELLENT" if self.performance_metrics["average_coherence"] >= 0.85 else "GOOD",
            "total_voice_patterns": len(self.coherence_patterns),
            "trinity_balance_enabled": True,
        }


# Global instance for LUKHAS AI voice coherence
voice_coherence_engine: Optional[LUKHASVoiceCoherenceEngine] = None


def get_voice_coherence_engine() -> LUKHASVoiceCoherenceEngine:
    """Get or create the global voice coherence engine"""
    global voice_coherence_engine

    if voice_coherence_engine is None:
        voice_coherence_engine = LUKHASVoiceCoherenceEngine()

    return voice_coherence_engine


# Example usage
async def main():
    """Example usage of LUKHAS voice coherence engine"""

    engine = get_voice_coherence_engine()

    # Test voice coherence on sample content
    test_content = [
        "LUKHAS AI provides consciousness technology that understands and empathetically assists users.",
        "Our robotic system automates basic tasks efficiently.",
        "We guarantee perfect results with our AI solution that never fails.",
        "LUKHAS consciousness technology offers wise, authentic, and ethically guided assistance through mindful awareness.",
    ]

    print("🗣️ LUKHAS AI Voice Coherence Analysis")
    print("===================================")
    print()

    for i, content in enumerate(test_content):
        result = await engine.analyze_voice_coherence(content, f"test_{i}")

        coherence_pct = result.overall_coherence * 100
        status = "✅ EXCELLENT" if coherence_pct >= 85 else "⚠️ NEEDS WORK" if coherence_pct >= 70 else "❌ POOR"

        print(f"Content {i + 1}: {status} ({coherence_pct:.1f}% coherence)")
        print(f'Content: "{content[:60]}{"..." if len(content) > 60 else ""}"')
        print(f"Profile: {result.voice_profile_match}")
        print(
            fix_later
        )

        if result.suggested_improvements:
            print("Improvements:")
            for suggestion in result.suggested_improvements[:2]:
                print(f"  • {suggestion}")
        print()

    # Performance summary
    summary = engine.get_performance_summary()
    print(f"📊 System Performance: {summary['system_health']}")
    print(f"🎯 Target Achievement: {summary['performance_metrics']['target_achievement_rate']  * 100:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
