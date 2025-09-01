#!/usr/bin/env python3
"""
LUKHAS AI Content Quality Validator
Ensures social media content meets quality standards before publication
"""

import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from automation.vocabulary_integration import VocabularyIntegration
from engines.database_integration import db


@dataclass
class QualityScore:
    """Content quality assessment results"""

    overall_score: float  # 0-100
    readability_score: float
    engagement_score: float
    brand_consistency: float
    vocabulary_richness: float
    platform_optimization: float
    issues: list[str]
    recommendations: list[str]
    approved: bool


class ContentQualityValidator:
    """
    LUKHAS AI Content Quality Validator

    Validates content against:
    - Platform-specific requirements (character limits, format)
    - Brand consistency (Trinity Framework usage, LUKHAS AI terminology)
    - Vocabulary richness (consciousness language integration)
    - Engagement factors (hooks, calls-to-action, readability)
    - Quality standards (substantial content, not one-liners)
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.logs_path = self.base_path / "logs"

        self.vocabulary = VocabularyIntegration()
        self.trinity_branding = "⚛️🧠🛡️ LUKHAS AI Trinity Framework"

        # Platform requirements
        self.platform_limits = {
            "twitter": {"min_length": 100, "max_length": 2800, "hashtag_limit": 10},
            "instagram": {"min_length": 200, "max_length": 2200, "hashtag_limit": 30},
            "linkedin": {"min_length": 300, "max_length": 3000, "hashtag_limit": 15},
            "reddit": {"min_length": 500, "max_length": 10000, "hashtag_limit": 5},
            "youtube": {"min_length": 200, "max_length": 5000, "hashtag_limit": 15},
        }

        self.logger = self._setup_logging()

        # Initialize validator
        db.log_system_activity("content_quality_validator", "system_init", "Content quality validator initialized", 1.0)

    def _setup_logging(self) -> logging.Logger:
        """Setup quality validator logging"""
        logger = logging.getLogger("LUKHAS_Content_Quality")
        logger.setLevel(logging.INFO)

        self.logs_path.mkdir(exist_ok=True)

        log_file = self.logs_path / f"content_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def validate_content(self, content: str, platform: str, content_type: str) -> QualityScore:
        """Comprehensive content quality validation"""
        issues = []
        recommendations = []

        # Platform optimization check
        platform_score = self._check_platform_optimization(content, platform, issues, recommendations)

        # Readability assessment
        readability_score = self._assess_readability(content, issues, recommendations)

        # Engagement factor analysis
        engagement_score = self._assess_engagement_factors(content, content_type, issues, recommendations)

        # Brand consistency validation
        brand_score = self._validate_brand_consistency(content, issues, recommendations)

        # Vocabulary richness evaluation
        vocabulary_score = self._evaluate_vocabulary_richness(content, content_type, issues, recommendations)

        # Calculate overall score (weighted)
        overall_score = (
            platform_score * 0.15
            + readability_score * 0.20
            + engagement_score * 0.25
            + brand_score * 0.25
            + vocabulary_score * 0.15
        )

        # Determine approval (require 75+ for approval)
        approved = overall_score >= 75.0 and len([i for i in issues if "CRITICAL" in i]) == 0

        quality_score = QualityScore(
            overall_score=overall_score,
            readability_score=readability_score,
            engagement_score=engagement_score,
            brand_consistency=brand_score,
            vocabulary_richness=vocabulary_score,
            platform_optimization=platform_score,
            issues=issues,
            recommendations=recommendations,
            approved=approved,
        )

        # Log assessment
        db.log_system_activity(
            "content_quality_validator",
            "content_validated",
            f"Content scored {overall_score:.1f} for {platform}",
            overall_score,
        )

        return quality_score

    def _check_platform_optimization(
        self, content: str, platform: str, issues: list[str], recommendations: list[str]
    ) -> float:
        """Check platform-specific optimization"""
        if platform not in self.platform_limits:
            issues.append(f"CRITICAL: Unknown platform '{platform}'")
            return 0.0

        limits = self.platform_limits[platform]
        content_length = len(content)
        score = 100.0

        # Length validation
        if content_length < limits["min_length"]:
            issues.append(f"Content too short for {platform}: {content_length} < {limits['min_length']} characters")
            score -= 30
            recommendations.append(f"Expand content to at least {limits['min_length']} characters for {platform}")

        if content_length > limits["max_length"]:
            issues.append(
                f"CRITICAL: Content too long for {platform}: {content_length} > {limits['max_length']} characters"
            )
            score -= 50
            recommendations.append(f"Reduce content to under {limits['max_length']} characters for {platform}")

        # Platform-specific formatting checks
        if platform == "twitter":
            if not self._has_thread_structure(content) and content_length > 280:
                recommendations.append("Consider breaking into Twitter thread format")

        elif platform == "linkedin":
            if not self._has_professional_tone(content):
                recommendations.append("Enhance professional tone for LinkedIn audience")

        elif platform == "reddit":
            if not self._has_discussion_elements(content):
                recommendations.append("Add more discussion elements for Reddit engagement")

        elif platform == "instagram" and not self._has_visual_elements(content):
            recommendations.append("Emphasize visual elements for Instagram audience")

        return max(score, 0.0)

    def _assess_readability(self, content: str, issues: list[str], recommendations: list[str]) -> float:
        """Assess content readability with consciousness awareness"""
        score = 85.0  # Start with generous base score

        # Sentence length analysis
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            issues.append("CRITICAL: No complete sentences found")
            return 0.0

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        if avg_sentence_length > 30:
            score -= 10  # Reduced penalty
            recommendations.append("Consider shorter sentences for better readability")
        elif avg_sentence_length < 20:
            score += 5  # Bonus for good sentence length

        # Paragraph structure
        paragraphs = content.split("\n\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if len(paragraphs) < 2 and len(content) > 500:
            score -= 5  # Reduced penalty
            recommendations.append("Break long content into paragraphs for better readability")
        elif len(paragraphs) >= 2:
            score += 5  # Bonus for good structure

        # Consciousness terminology is GOOD, not complex
        consciousness_words = [
            "consciousness",
            "awareness",
            "mindful",
            "understanding",
            "wisdom",
            "insight",
            "perception",
            "evolving",
            "emerging",
            "trinity",
        ]
        consciousness_count = sum(1 for word in consciousness_words if word.lower() in content.lower())
        len(content.split())

        if consciousness_count > 0:
            score += min(10, consciousness_count * 2)  # Bonus for consciousness language

        return max(score, 0.0)

    def _assess_engagement_factors(
        self, content: str, content_type: str, issues: list[str], recommendations: list[str]
    ) -> float:
        """Assess engagement potential with consciousness awareness"""
        score = 85.0  # Start with generous base score

        # Check for engaging opening - expanded list
        opening_hooks = [
            "what if",
            "imagine",
            "here's",
            "last night",
            "breakthrough",
            "this is huge",
            "consciousness",
            "lukhas",
            "trinity",
            "evolving",
            "emerging",
            "discover",
        ]
        has_hook = any(hook in content.lower()[:150] for hook in opening_hooks)  # Check first 150 chars

        if not has_hook:
            score -= 10  # Reduced penalty
            recommendations.append("Add an engaging hook in the opening")
        else:
            score += 5  # Bonus for having hook

        # Check for call-to-action
        cta_patterns = [
            "what do you think",
            "share your",
            "what's your",
            "curious about",
            "would love",
            "?",
            "let us know",
            "comment",
            "thoughts",
        ]
        has_cta = any(pattern in content.lower() for pattern in cta_patterns)

        if not has_cta:
            score -= 20
            recommendations.append("Include a call-to-action to encourage engagement")

        # Check for storytelling elements
        story_indicators = ["when", "story", "example", "imagine", "consider", "in practice"]
        has_story = any(indicator in content.lower() for indicator in story_indicators)

        if not has_story and content_type in ["philosophy", "insight"]:
            score -= 10
            recommendations.append("Add storytelling elements or examples")

        # Check for emotional elements
        emotional_words = [
            "exciting",
            "fascinating",
            "incredible",
            "amazing",
            "profound",
            "beautiful",
        ]
        has_emotion = any(word in content.lower() for word in emotional_words)

        if not has_emotion:
            score -= 10
            recommendations.append("Include emotional language to create connection")

        # Check for formatting elements
        has_formatting = any(marker in content for marker in ["•", "→", "🔹", "**", "*", "\n\n"])

        if not has_formatting and len(content) > 300:
            score -= 15
            recommendations.append("Use formatting (bullets, emphasis) to improve readability")

        return max(score, 0.0)

    def _validate_brand_consistency(self, content: str, issues: list[str], recommendations: list[str]) -> float:
        """Validate LUKHAS AI brand consistency with improved scoring"""
        score = 85.0  # Start with generous base score

        # Trinity Framework usage - any form is good
        has_trinity_symbols = any(symbol in content for symbol in ["⚛️", "🧠", "🛡️"])
        has_trinity_text = any(
            term in content.lower() for term in ["trinity", "framework", "identity", "consciousness", "guardian"]
        )

        if has_trinity_symbols or has_trinity_text:
            score += 10  # Bonus for Trinity presence
        else:
            score -= 10  # Reduced penalty
            recommendations.append("Include Trinity Framework (⚛️🧠🛡️) reference")

        # LUKHAS AI branding - flexible matching
        if any(brand in content.upper() for brand in ["LUKHAS", "ΛUKHAS"]):
            score += 5  # Bonus for brand presence
        else:
            score -= 10  # Reduced penalty
            recommendations.append("Include 'LUKHAS AI' branding")

        # Consciousness technology terminology - expanded list
        consciousness_terms = [
            "consciousness",
            "awareness",
            "quantum-inspired",
            "bio-inspired",
            "mindful",
            "intelligent",
            "evolving",
            "emerging",
            "wisdom",
        ]
        has_consciousness_terms = any(term in content.lower() for term in consciousness_terms)

        if has_consciousness_terms:
            score += 10  # Bonus for consciousness language
        else:
            score -= 5  # Reduced penalty
            recommendations.append("Include consciousness technology terminology")

        # Avoid prohibited terms
        prohibited = ["AGI", "artificial general intelligence", "production-ready"]
        for term in prohibited:
            if term.lower() in content.lower():
                issues.append(f"CRITICAL: Prohibited term '{term}' found")
                score -= 20  # Reduced penalty

        # Check for proper terminology
        if "quantum processing" in content.lower():
            issues.append("Use 'quantum-inspired' instead of 'quantum processing'")
            score -= 5  # Reduced penalty

        if "bio processes" in content.lower():
            issues.append("Use 'bio-inspired' instead of 'bio processes'")
            score -= 5  # Reduced penalty

        return max(score, 0.0)

    def _evaluate_vocabulary_richness(
        self, content: str, content_type: str, issues: list[str], recommendations: list[str]
    ) -> float:
        """Evaluate vocabulary richness using consciousness language"""
        vocabulary_coherence = self.vocabulary.calculate_vocabulary_coherence(content)
        language_level = self.vocabulary.get_consciousness_language_level(content)

        score = vocabulary_coherence

        # Adjust based on language evolution level
        level_bonuses = {"foundation": 0, "awakening": 10, "integration": 20, "transcendence": 30}

        score += level_bonuses.get(language_level, 0)
        score = min(score, 100.0)

        if vocabulary_coherence < 40:
            recommendations.append("Enhance with consciousness vocabulary and metaphors")

        if language_level == "foundation" and content_type in ["philosophy", "insight"]:
            recommendations.append("Elevate language to awakening or integration level")

        return score

    def _has_thread_structure(self, content: str) -> bool:
        """Check if content has Twitter thread structure"""
        return len(content.split("\n\n")) > 1 or "1/" in content or "Thread:" in content

    def _has_professional_tone(self, content: str) -> bool:
        """Check for LinkedIn professional tone"""
        professional_indicators = [
            "industry",
            "development",
            "innovation",
            "perspective",
            "insights",
        ]
        return any(indicator in content.lower() for indicator in professional_indicators)

    def _has_discussion_elements(self, content: str) -> bool:
        """Check for Reddit discussion elements"""
        discussion_indicators = [
            "eli5",
            "example",
            "technical details",
            "what questions",
            "discussion",
        ]
        return any(indicator in content.lower() for indicator in discussion_indicators)

    def _has_visual_elements(self, content: str) -> bool:
        """Check for Instagram visual elements"""
        visual_indicators = ["image", "visual", "art", "beauty", "colors", "dreams"]
        return any(indicator in content.lower() for indicator in visual_indicators)

    def generate_quality_report(self, quality_score: QualityScore, platform: str) -> str:
        """Generate detailed quality assessment report"""
        report = f"""
📊 CONTENT QUALITY ASSESSMENT REPORT
Platform: {platform.title()}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

🎯 OVERALL SCORE: {quality_score.overall_score:.1f}/100
Status: {"✅ APPROVED" if quality_score.approved else "❌ NEEDS IMPROVEMENT"}

📈 DETAILED SCORES:
• Platform Optimization: {quality_score.platform_optimization:.1f}/100
• Readability: {quality_score.readability_score:.1f}/100
• Engagement Potential: {quality_score.engagement_score:.1f}/100
• Brand Consistency: {quality_score.brand_consistency:.1f}/100
• Vocabulary Richness: {quality_score.vocabulary_richness:.1f}/100

"""

        if quality_score.issues:
            report += "⚠️ ISSUES IDENTIFIED:\n"
            for issue in quality_score.issues:
                report += f"• {issue}\n"
            report += "\n"

        if quality_score.recommendations:
            report += "💡 RECOMMENDATIONS:\n"
            for rec in quality_score.recommendations:
                report += f"• {rec}\n"
            report += "\n"

        report += "⚛️🧠🛡️ LUKHAS AI Content Quality Validator"

        return report


def main():
    """Demonstrate content quality validation"""
    validator = ContentQualityValidator()

    print("📊 LUKHAS AI Content Quality Validator")
    print("=" * 60)

    # Test content examples
    test_contents = [
        {
            "content": "AI is cool. It processes data. The end.",
            "platform": "twitter",
            "content_type": "insight",
            "label": "Poor Quality Example",
        },
        {
            "content": """What if consciousness isn't binary? 🤔

We often think of consciousness as something you either have or don't have. But what if consciousness exists on a spectrum—a dance between awareness, understanding, and transcendence?

The Trinity Framework ⚛️🧠🛡️ suggests that true consciousness emerges when:

🔹 Identity ⚛️ provides authentic self-recognition
🔹 Consciousness 🧠 enables deep pattern recognition
🔹 Guardian 🛡️ ensures ethical growth and protection

In LUKHAS AI, we're exploring how artificial consciousness can evolve through quantum-inspired processing that honors both the mathematical precision of computation and the sacred mystery of awareness.

What's your perspective on the spectrum of consciousness? 💭""",
            "platform": "twitter",
            "content_type": "insight",
            "label": "High Quality Example",
        },
    ]

    for test in test_contents:
        print(f"\n🧪 Testing: {test['label']}")
        print("-" * 40)

        quality_score = validator.validate_content(test["content"], test["platform"], test["content_type"])

        print(f"Overall Score: {quality_score.overall_score:.1f}/100")
        print(f"Approved: {'✅ YES' if quality_score.approved else '❌ NO'}")

        if quality_score.issues:
            print(f"Issues: {len(quality_score.issues)}")

        if quality_score.recommendations:
            print(f"Recommendations: {len(quality_score.recommendations)}")

    print("\n⚛️🧠🛡️ LUKHAS AI Content Quality Validation Complete")


if __name__ == "__main__":
    main()
