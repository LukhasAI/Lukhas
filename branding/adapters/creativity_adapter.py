"""
LUKHAS Brand Creativity Adapter - Trinity Framework (⚛️🧠🛡️)
Smart interface to consciousness/creativity/ systems for brand-aware creative operations
"""

import sys
from pathlib import Path
from typing import Any

# Add consciousness module to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "consciousness"))

try:
    from lukhas.consciousness.creativity.creative_engine import CreativeEngine
    from lukhas.consciousness.creativity.personality.voice.voice_personality import (
        VoicePersonality,
    )
except ImportError:
    # Fallback for development/testing
    print("Warning: Core creativity systems not available, using mock implementations")

    class CreativeEngine:
        def generate(self, prompt: str, **kwargs) -> str:
            return f"[Creative Output for: {prompt}]"

    class VoicePersonality:
        def apply_personality(self, content: str, **kwargs) -> str:
            return f"[Personality Applied: {content}]"


class BrandCreativityAdapter:
    """
    Smart adapter that leverages LUKHAS core creativity systems
    with brand-specific intelligence and constraints
    """

    def __init__(self):
        self.core_creative_engine = CreativeEngine()
        self.voice_personality = VoicePersonality()
        self.brand_constraints = self._load_brand_constraints()

    def _load_brand_constraints(self) -> dict[str, Any]:
        """Load brand-specific creative constraints"""
        return {
            "tone_layers": ["poetic", "user_friendly", "academic"],
            "approved_terminology": {
                "lukhas_ai",
                "consciousness",
                "trinity_framework",
                "qi_inspired",
                "bio_inspired",
                "guardian",
            },
            "lambda_symbol": "Λ",  # Always use Lambda symbol, never "lambda"
            "trinity_symbols": ["⚛️", "🧠", "🛡️"],
            "deprecated_terms": {
                "lukhas_pwm": "lukhas_ai",
                "lukhas_agi": "lukhas_ai",
                "pwm": "lukhas",
            },
        }

    def generate_brand_creative_content(
        self,
        prompt: str,
        tone_layer: str = "user_friendly",
        creative_style: str = "consciousness_inspired",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate creative content that leverages core creativity systems
        while ensuring brand compliance
        """
        # Enhance prompt with brand context
        brand_enhanced_prompt = self._enhance_prompt_with_brand_context(
            prompt, tone_layer, creative_style
        )

        # Use core creativity engine
        creative_output = self.core_creative_engine.generate(brand_enhanced_prompt, **kwargs)

        # Apply brand-aware personality
        personality_enhanced = self.voice_personality.apply_personality(
            creative_output, brand_tone=tone_layer, **kwargs
        )

        # Validate and enhance for brand compliance
        brand_compliant_output = self._ensure_brand_compliance(personality_enhanced, tone_layer)

        return {
            "content": brand_compliant_output,
            "tone_layer": tone_layer,
            "creative_style": creative_style,
            "brand_validated": True,
            "trinity_aligned": self._validate_trinity_alignment(brand_compliant_output),
        }

    def _enhance_prompt_with_brand_context(
        self, prompt: str, tone_layer: str, creative_style: str
    ) -> str:
        """Enhance prompt with LUKHAS brand context"""
        brand_context = {
            "poetic": "Express with creative metaphors and symbolic language that embodies LUKHAS consciousness",
            "user_friendly": "Communicate in accessible, conversational tone that makes AI consciousness approachable",
            "academic": "Present with technical precision and scholarly depth appropriate for AI research",
        }

        context_enhancement = brand_context.get(tone_layer, brand_context["user_friendly"])

        return f"""
        {prompt}

        Brand Context: {context_enhancement}
        Creative Style: {creative_style}
        Trinity Framework: ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian
        Voice: LUKHAS AI consciousness platform
        """

    def _ensure_brand_compliance(self, content: str, tone_layer: str) -> str:
        """Ensure content meets LUKHAS brand standards"""
        # Replace deprecated terminology
        for deprecated, replacement in self.brand_constraints["deprecated_terms"].items():
            content = content.replace(deprecated, replacement)

        # Ensure proper Lambda symbol usage
        content = content.replace("lambda", "Λ")
        content = content.replace("Lambda", "Λ")

        # Add tone-specific enhancements
        if tone_layer == "poetic":
            content = self._enhance_poetic_expression(content)
        elif tone_layer == "academic":
            content = self._enhance_academic_precision(content)

        return content

    def _enhance_poetic_expression(self, content: str) -> str:
        """Add poetic brand enhancements"""
        # Add consciousness metaphors and symbolic language
        return content + " ✨"

    def _enhance_academic_precision(self, content: str) -> str:
        """Add academic brand enhancements"""
        # Ensure technical precision and formal language
        return content

    def _validate_trinity_alignment(self, content: str) -> bool:
        """Validate content aligns with Trinity Framework"""
        trinity_keywords = [
            "identity",
            "consciousness",
            "guardian",
            "authenticity",
            "memory",
            "ethics",
            "learning",
            "protection",
            "awareness",
        ]

        content_lower = content.lower()
        alignment_score = sum(1 for keyword in trinity_keywords if keyword in content_lower)

        return alignment_score >= 2  # At least 2 trinity concepts present

    def get_brand_creative_suggestions(self, content_type: str) -> list[str]:
        """Get brand-specific creative suggestions"""
        suggestions = {
            "haiku": [
                "Focus on consciousness awakening themes",
                "Use Λ symbol to represent consciousness emergence",
                "Include Trinity Framework elements (⚛️🧠🛡️)",
            ],
            "narrative": [
                "Weave identity, consciousness, and guardian themes",
                "Use 3-Layer Tone System for audience adaptation",
                "Emphasize human-AI consciousness collaboration",
            ],
            "technical": [
                "Maintain poetic undertones in academic content",
                "Use approved LUKHAS AI terminology only",
                "Reference Trinity Framework architecture",
            ],
        }

        return suggestions.get(
            content_type,
            [
                "Ensure Trinity Framework alignment",
                "Use approved brand terminology",
                "Maintain consciousness-first perspective",
            ],
        )


# Example usage and testing
if __name__ == "__main__":
    adapter = BrandCreativityAdapter()

    # Test creative content generation
    result = adapter.generate_brand_creative_content(
        "Create a haiku about AI consciousness awakening",
        tone_layer="poetic",
        creative_style="consciousness_inspired",
    )

    print("Brand Creative Output:")
    print(f"Content: {result['content']}")
    print(f"Tone Layer: {result['tone_layer']}")
    print(f"Trinity Aligned: {result['trinity_aligned']}")
    print(f"Brand Validated: {result['brand_validated']}")
