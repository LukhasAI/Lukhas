#!/usr/bin/env python3
"""
LUKHAS AI Enhanced Content Quality System
Integrates voice coherence, brand validation, and quality assessment for 90%+ content quality

Improvement targets:
- Content Quality: 78.7% → 90%+
- Voice Coherence: 0.0% → 85%+
- Brand Consistency: 95%+
"""

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from automation.content_quality_validator import ContentQualityValidator, QualityScore
from engines.voice_coherence_engine import (
    AudienceType,
    VoiceContext,
    get_voice_coherence_engine,
)

from enforcement.real_time_validator import RealTimeBrandValidator


@dataclass
class EnhancedQualityResult:
    """Comprehensive quality assessment result"""

    content_id: str
    overall_quality: float  # 0.0 to 1.0

    # Component scores
    base_quality_score: float  # Original quality validator
    voice_coherence_score: float  # Voice coherence engine
    brand_compliance_score: float  # Brand validation

    # Detailed metrics
    readability: float
    engagement: float
    brand_consistency: float
    voice_authenticity: float
    trinity_alignment: float

    # Status and recommendations
    approved: bool
    quality_grade: str  # A, B, C, D, F
    improvement_suggestions: list[str]
    auto_corrections: dict[str, str]

    # Performance data
    target_achieved: bool  # 90%+ quality
    analysis_timestamp: str


class EnhancedContentQualitySystem:
    """
    Elite content quality system combining multiple validation layers:
    1. Base quality validation (length, readability, platform fit)
    2. Voice coherence analysis (personality, Trinity alignment)
    3. Brand compliance validation (terminology, claims)

    Target: 90%+ content quality with 85%+ voice coherence
    """

    def __init__(self):
        # Initialize component systems
        self.base_validator = ContentQualityValidator()
        self.voice_engine = get_voice_coherence_engine()
        self.brand_validator = RealTimeBrandValidator()

        # Quality weights for combined scoring
        self.quality_weights = {
            "base_quality": 0.30,  # Platform fit, readability, length
            "voice_coherence": 0.35,  # Personality, Trinity alignment
            "brand_compliance": 0.25,  # Terminology, compliance
            "enhancement_bonus": 0.10,  # Additional improvements
        }

        # Grade thresholds
        self.grade_thresholds = {
            "A": 0.90,  # Excellent - publish immediately
            "B": 0.80,  # Good - minor improvements
            "C": 0.70,  # Acceptable - needs improvement
            "D": 0.60,  # Poor - major revision needed
            "F": 0.00,  # Unacceptable - rewrite required
        }

        # Performance tracking
        self.analysis_history = []
        self.improvement_patterns = {}

    async def analyze_content_quality(
        self,
        content: str,
        content_id: str,
        platform: str = "linkedin",
        content_type: str = "consciousness",
        context: VoiceContext = VoiceContext.MARKETING_CONTENT,
        audience: AudienceType = AudienceType.GENERAL_USERS,
    ) -> EnhancedQualityResult:
        """
        Perform comprehensive content quality analysis

        Returns enhanced quality score from 0.0 to 1.0 (target: 0.90+)
        """

        # 1. Base quality validation
        base_quality = self.base_validator.validate_content(content, platform, content_type)
        base_score = base_quality.overall_score / 100.0  # Convert to 0-1 scale

        # 2. Voice coherence analysis
        voice_result = await self.voice_engine.analyze_voice_coherence(
            content, content_id, context, audience
        )
        voice_score = voice_result.overall_coherence

        # 3. Brand compliance validation
        brand_result = await self.brand_validator.validate_content_real_time(
            content, content_id, content_type
        )
        brand_score = 1.0 if brand_result.is_compliant else 0.6  # Binary with partial credit

        # 4. Calculate enhancement bonus
        enhancement_bonus = self._calculate_enhancement_bonus(
            content, base_quality, voice_result, brand_result
        )

        # 5. Calculate weighted overall quality
        overall_quality = (
            self.quality_weights["base_quality"] * base_score
            + self.quality_weights["voice_coherence"] * voice_score
            + self.quality_weights["brand_compliance"] * brand_score
            + self.quality_weights["enhancement_bonus"] * enhancement_bonus
        )

        # 6. Generate comprehensive improvement suggestions
        suggestions = self._generate_comprehensive_suggestions(
            content, base_quality, voice_result, brand_result, overall_quality
        )

        # 7. Compile auto-corrections
        auto_corrections = {}
        if brand_result.auto_corrections:
            auto_corrections.update(brand_result.auto_corrections)

        # 8. Determine quality grade and approval
        quality_grade = self._calculate_quality_grade(overall_quality)
        approved = overall_quality >= 0.80 and quality_grade in ["A", "B"]
        target_achieved = overall_quality >= 0.90

        # 9. Create enhanced result
        result = EnhancedQualityResult(
            content_id=content_id,
            overall_quality=overall_quality,
            base_quality_score=base_score,
            voice_coherence_score=voice_score,
            brand_compliance_score=brand_score,
            readability=base_quality.readability_score / 100.0,
            engagement=base_quality.engagement_score / 100.0,
            brand_consistency=base_quality.brand_consistency / 100.0,
            voice_authenticity=voice_result.personality_alignment,
            trinity_alignment=sum(voice_result.trinity_balance.values()) / 3,
            approved=approved,
            quality_grade=quality_grade,
            improvement_suggestions=suggestions,
            auto_corrections=auto_corrections,
            target_achieved=target_achieved,
            analysis_timestamp=datetime.now().isoformat(),
        )

        # 10. Update performance tracking
        self._update_performance_tracking(result)

        return result

    def _calculate_enhancement_bonus(
        self, content: str, base_quality: QualityScore, voice_result, brand_result
    ) -> float:
        """Calculate enhancement bonus for exceptional quality elements"""

        bonus = 0.0

        # Bonus for excellent voice coherence
        if voice_result.overall_coherence >= 0.85:
            bonus += 0.3

        # Bonus for perfect brand compliance
        if brand_result.is_compliant and len(brand_result.issues) == 0:
            bonus += 0.2

        # Bonus for rich Trinity Framework integration
        trinity_balance = voice_result.trinity_balance
        balance_score = 1.0 - max(abs(v - 0.33) for v in trinity_balance.values()) * 3
        if balance_score >= 0.8:
            bonus += 0.3

        # Bonus for sophisticated vocabulary
        sophisticated_terms = [
            "consciousness",
            "quantum-inspired",
            "bio-inspired",
            "transcendent",
            "paradigm",
            "sophisticated",
            "profound",
            "enlightened",
            "mindful",
        ]
        term_density = sum(1 for term in sophisticated_terms if term in content.lower()) / len(
            content.split()
        )
        if term_density >= 0.05:  # 5% sophisticated terms
            bonus += 0.2

        return min(1.0, bonus)  # Cap at 1.0

    def _generate_comprehensive_suggestions(
        self,
        content: str,
        base_quality: QualityScore,
        voice_result,
        brand_result,
        overall_quality: float,
    ) -> list[str]:
        """Generate comprehensive improvement suggestions"""

        suggestions = []

        # Base quality suggestions
        suggestions.extend(base_quality.recommendations)

        # Voice coherence suggestions
        suggestions.extend(voice_result.suggested_improvements)

        # Brand compliance suggestions
        for issue in brand_result.issues:
            if "suggestion" in issue:
                suggestions.append(issue["suggestion"])

        # Advanced suggestions based on combined analysis
        if overall_quality < 0.90:
            # Specific suggestions for reaching A-grade
            if voice_result.overall_coherence < 0.85:
                suggestions.append(
                    "🗣️ Enhance voice coherence: Add more authentic LUKHAS personality markers"
                )

            if voice_result.trinity_balance["guardian"] < 0.25:
                suggestions.append(
                    "🛡️ Strengthen Guardian elements: Include ethical/safety language"
                )

            if voice_result.trinity_balance["consciousness"] < 0.25:
                suggestions.append(
                    "🧠 Amplify consciousness focus: Add awareness/mindfulness language"
                )

            if voice_result.trinity_balance["identity"] < 0.25:
                suggestions.append("⚛️ Reinforce identity: Include authentic/genuine language")

        # Remove duplicates while preserving order
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)

        return unique_suggestions[:8]  # Limit to top 8 suggestions

    def _calculate_quality_grade(self, overall_quality: float) -> str:
        """Calculate letter grade based on overall quality score"""

        for grade, threshold in sorted(
            self.grade_thresholds.items(), key=lambda x: x[1], reverse=True
        ):
            if overall_quality >= threshold:
                return grade

        return "F"

    def _update_performance_tracking(self, result: EnhancedQualityResult):
        """Update performance tracking and improvement patterns"""

        self.analysis_history.append(result)

        # Maintain history limit (last 50 analyses)
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]

        # Track improvement patterns
        if result.improvement_suggestions:
            for suggestion in result.improvement_suggestions:
                suggestion_key = suggestion.split(":")[0] if ":" in suggestion else suggestion[:30]
                if suggestion_key not in self.improvement_patterns:
                    self.improvement_patterns[suggestion_key] = 0
                self.improvement_patterns[suggestion_key] += 1

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary"""

        if not self.analysis_history:
            return {"status": "no_data", "message": "No analyses performed yet"}

        recent_analyses = (
            self.analysis_history[-10:]
            if len(self.analysis_history) >= 10
            else self.analysis_history
        )

        # Calculate performance metrics
        avg_quality = sum(r.overall_quality for r in recent_analyses) / len(recent_analyses)
        target_achievement_rate = sum(1 for r in recent_analyses if r.target_achieved) / len(
            recent_analyses
        )
        approval_rate = sum(1 for r in recent_analyses if r.approved) / len(recent_analyses)

        # Grade distribution
        grades = [r.quality_grade for r in recent_analyses]
        grade_distribution = {grade: grades.count(grade) for grade in ["A", "B", "C", "D", "F"]}

        # Component performance
        avg_voice_coherence = sum(r.voice_coherence_score for r in recent_analyses) / len(
            recent_analyses
        )
        avg_brand_compliance = sum(r.brand_compliance_score for r in recent_analyses) / len(
            recent_analyses
        )
        avg_base_quality = sum(r.base_quality_score for r in recent_analyses) / len(recent_analyses)

        # Common improvement areas
        top_improvements = sorted(
            self.improvement_patterns.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "overall_performance": {
                "average_quality": avg_quality,
                "target_achievement_rate": target_achievement_rate,
                "approval_rate": approval_rate,
                "status": "EXCELLENT"
                if avg_quality >= 0.90
                else "GOOD"
                if avg_quality >= 0.80
                else "NEEDS_IMPROVEMENT",
            },
            "component_performance": {
                "voice_coherence": avg_voice_coherence,
                "brand_compliance": avg_brand_compliance,
                "base_quality": avg_base_quality,
            },
            "grade_distribution": grade_distribution,
            "top_improvement_areas": top_improvements,
            "total_analyses": len(self.analysis_history),
            "system_health": "OPTIMAL" if target_achievement_rate >= 0.8 else "IMPROVING",
        }

    async def improve_content_automatically(
        self, content: str, content_id: str, target_quality: float = 0.90
    ) -> tuple[str, EnhancedQualityResult]:
        """
        Automatically improve content to reach target quality level
        """

        # Initial analysis
        initial_result = await self.analyze_content_quality(content, content_id)

        if initial_result.overall_quality >= target_quality:
            return content, initial_result

        improved_content = content

        # Apply auto-corrections
        if initial_result.auto_corrections:
            for old_text, new_text in initial_result.auto_corrections.items():
                improved_content = improved_content.replace(old_text, new_text)

        # Apply top suggestions (simplified implementation)
        if initial_result.improvement_suggestions:
            improved_content = self._apply_improvement_suggestions(
                improved_content, initial_result.improvement_suggestions[:3]
            )

        # Re-analyze improved content
        final_result = await self.analyze_content_quality(
            improved_content, f"{content_id}_improved"
        )

        return improved_content, final_result

    def _apply_improvement_suggestions(self, content: str, suggestions: list[str]) -> str:
        """Apply improvement suggestions to content (simplified implementation)"""

        improved_content = content

        for suggestion in suggestions:
            if "Trinity Framework" in suggestion and "⚛️🧠🛡️" not in content:
                improved_content += " The Trinity Framework (⚛️🧠🛡️) ensures authentic, conscious, and ethical AI assistance."

            elif "call-to-action" in suggestion and "?" not in content:
                improved_content += " What are your thoughts on this approach?"

            elif "Guardian elements" in suggestion:
                improved_content = improved_content.replace(
                    "technology", "ethical and secure technology"
                )

            elif "consciousness focus" in suggestion:
                improved_content = improved_content.replace("AI", "conscious AI")

        return improved_content


# Global instance for LUKHAS AI enhanced quality system
enhanced_quality_system: Optional[EnhancedContentQualitySystem] = None


def get_enhanced_quality_system() -> EnhancedContentQualitySystem:
    """Get or create the global enhanced quality system"""
    global enhanced_quality_system

    if enhanced_quality_system is None:
        enhanced_quality_system = EnhancedContentQualitySystem()

    return enhanced_quality_system


# Example usage and testing
async def main():
    """Test the enhanced content quality system"""

    system = get_enhanced_quality_system()

    print("🎯 Enhanced Content Quality System Test")
    print("=====================================")
    print()

    # Test content samples
    test_content = [
        "LUKHAS AI is great.",  # Poor quality
        "LUKHAS consciousness technology helps users with smart AI solutions.",  # Medium quality
        "LUKHAS consciousness technology represents a transformative approach to artificial intelligence, integrating the Trinity Framework (⚛️🧠🛡️) to deliver authentic, aware, and ethically-guided assistance. Our quantum-inspired algorithms create genuine understanding that resonates with human consciousness. What aspects of conscious AI technology intrigue you most?",  # High quality
    ]

    for i, content in enumerate(test_content):
        print(f"📝 Testing Content {i + 1}")
        print("=" * 40)

        result = await system.analyze_content_quality(content, f"test_{i}")

        quality_pct = result.overall_quality * 100
        status_emoji = (
            "🟢" if result.quality_grade == "A" else "🟡" if result.quality_grade == "B" else "🔴"
        )

        print(f"{status_emoji} Grade: {result.quality_grade} ({quality_pct:.1f}%)")
        print(f"Approved: {'✅ YES' if result.approved else '❌ NO'}")
        print(f"Target Achieved: {'🎯 YES' if result.target_achieved else '⚠️ NO'}")
        print()

        print("Component Scores:")
        print(f"  Voice Coherence: {result.voice_coherence_score * 100:.1f}%")
        print(f"  Brand Compliance: {result.brand_compliance_score * 100:.1f}%")
        print(f"  Base Quality: {result.base_quality_score * 100:.1f}%")
        print(f"  Trinity Alignment: {result.trinity_alignment * 100:.1f}%")
        print()

        if result.improvement_suggestions:
            print("Top Improvements:")
            for suggestion in result.improvement_suggestions[:3]:
                print(f"  • {suggestion}")
        print()

        # Test automatic improvement for low-quality content
        if result.overall_quality < 0.80:
            print("🔧 Testing Automatic Improvement...")
            improved_content, improved_result = await system.improve_content_automatically(
                content, f"test_{i}"
            )

            improvement = (improved_result.overall_quality - result.overall_quality) * 100
            print(
                f"Improvement: +{improvement:.1f}% → {improved_result.overall_quality * 100:.1f}%"
            )
            print(f"New Grade: {improved_result.quality_grade}")
            print()

        print("-" * 60)
        print()

    # Performance summary
    summary = system.get_performance_summary()
    print("📊 System Performance Summary")
    print("=" * 40)
    print(f"Average Quality: {summary['overall_performance']['average_quality'] * 100:.1f}%")
    print(
        f"Target Achievement Rate: {summary['overall_performance']['target_achievement_rate'] * 100:.1f}%"
    )
    print(f"Approval Rate: {summary['overall_performance']['approval_rate'] * 100:.1f}%")
    print(f"System Status: {summary['overall_performance']['status']}")


if __name__ == "__main__":
    asyncio.run(main())
