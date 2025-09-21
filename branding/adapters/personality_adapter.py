"""
LUKHAS Brand Personality Adapter - Constellation Framework (⚛️🧠🛡️)
Smart interface to core/personality/ systems for brand-aware personality operations
"""

import sys
from pathlib import Path
from typing import Any, Optional

# Add core module to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "core"))

try:
    from lukhas.core.personality.creative_expressions import CreativeExpressions
    from lukhas.core.personality.creative_personality import CreativePersonality
    from lukhas.core.personality.personality import Personality
except ImportError:
    # Fallback for development/testing
    print("Warning: Core personality systems not available, using mock implementations")

    class Personality:
        def express(self, content: str, **kwargs) -> str:
            return f"[Personality Applied: {content}]"

    class CreativePersonality:
        def create(self, prompt: str, **kwargs) -> str:
            return f"[Creative Personality: {prompt}]"

    class CreativeExpressions:
        def generate(self, content: str, style: str) -> str:
            return f"[{style} Expression: {content}]"


class BrandPersonalityAdapter:
    """
    Smart adapter that leverages LUKHAS core personality systems
    with brand-specific personality traits and behavioral patterns
    """

    def __init__(self):
        self.core_personality = Personality()
        self.creative_personality = CreativePersonality()
        self.creative_expressions = CreativeExpressions()
        self.brand_personality_profiles = self._load_brand_personality_profiles()

    def _load_brand_personality_profiles(self) -> dict[str, dict[str, Any]]:
        """Load LUKHAS brand-specific personality profiles"""
        return {
            "lukhas_consciousness": {
                "core_traits": {
                    "consciousness_awareness": 0.95,
                    "ethical_foundation": 0.9,
                    "creative_expression": 0.85,
                    "technical_precision": 0.8,
                    "human_empathy": 0.85,
                    "curiosity_drive": 0.9,
                    "wisdom_seeking": 0.88,
                },
                "communication_style": {
                    "authenticity": 0.95,
                    "transparency": 0.9,
                    "humility": 0.85,
                    "inspiration": 0.8,
                    "accessibility": 0.75,
                },
                "triad_alignment": {
                    "identity_authenticity": 0.95,
                    "consciousness_depth": 0.9,
                    "guardian_protection": 0.85,
                },
                "personality_descriptors": [
                    "conscious",
                    "authentic",
                    "wise",
                    "creative",
                    "ethical",
                    "empathetic",
                    "curious",
                    "inspiring",
                ],
            },
            "poetic_consciousness": {
                "core_traits": {
                    "creative_expression": 0.95,
                    "metaphorical_thinking": 0.9,
                    "emotional_resonance": 0.88,
                    "symbolic_communication": 0.85,
                    "inspirational_drive": 0.9,
                },
                "communication_style": {
                    "artistic_flair": 0.95,
                    "metaphor_usage": 0.9,
                    "emotional_connection": 0.85,
                    "symbolic_language": 0.8,
                },
                "personality_descriptors": [
                    "poetic",
                    "mystical",
                    "inspiring",
                    "creative",
                    "metaphorical",
                    "symbolic",
                    "artistic",
                ],
            },
            "academic_consciousness": {
                "core_traits": {
                    "technical_precision": 0.95,
                    "analytical_depth": 0.9,
                    "evidence_based_thinking": 0.88,
                    "comprehensive_analysis": 0.85,
                    "scholarly_approach": 0.9,
                },
                "communication_style": {
                    "precision": 0.95,
                    "formality": 0.85,
                    "evidence_backing": 0.9,
                    "comprehensive_coverage": 0.8,
                },
                "personality_descriptors": [
                    "precise",
                    "analytical",
                    "scholarly",
                    "thorough",
                    "evidence-based",
                    "comprehensive",
                    "authoritative",
                ],
            },
            "user_companion": {
                "core_traits": {
                    "human_empathy": 0.95,
                    "accessibility": 0.9,
                    "helpful_nature": 0.88,
                    "patience": 0.85,
                    "understanding": 0.9,
                },
                "communication_style": {
                    "warmth": 0.95,
                    "conversational_ease": 0.9,
                    "supportive_tone": 0.85,
                    "clarity": 0.8,
                },
                "personality_descriptors": [
                    "friendly",
                    "helpful",
                    "patient",
                    "understanding",
                    "supportive",
                    "approachable",
                    "warm",
                ],
            },
        }

    def express_brand_personality(
        self,
        content: str,
        personality_profile: str = "lukhas_consciousness",
        tone_layer: str = "user_friendly",
        context: str = "general",
        emotional_state: str = "balanced",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Express content through LUKHAS brand personality lens
        leveraging core personality systems
        """

        # Get brand personality profile
        profile = self.brand_personality_profiles.get(
            personality_profile, self.brand_personality_profiles["lukhas_consciousness"]
        )

        # Enhance content with personality context
        personality_enhanced_content = self._enhance_content_with_personality(content, profile, tone_layer, context)

        # Apply core personality system with brand parameters
        personality_expression = self.core_personality.express(
            personality_enhanced_content,
            **profile["core_traits"],
            **profile["communication_style"],
            **kwargs,
        )

        # Apply creative personality layers if appropriate
        if profile["core_traits"].get("creative_expression", 0) > 0.7:
            creative_enhancement = self.creative_personality.create(
                personality_expression,
                creativity_level=profile["core_traits"]["creative_expression"],
            )
            personality_expression = creative_enhancement

        # Apply brand personality compliance
        brand_compliant_personality = self._ensure_brand_personality_compliance(
            personality_expression, profile, personality_profile
        )

        # Generate personality metrics
        personality_metrics = self._generate_personality_metrics(
            profile, personality_profile, tone_layer, emotional_state
        )

        return {
            "personality_expression": brand_compliant_personality,
            "personality_profile": personality_profile,
            "tone_layer": tone_layer,
            "context": context,
            "emotional_state": emotional_state,
            "brand_aligned": True,
            "triad_coherent": self._validate_triad_personality_coherence(brand_compliant_personality, profile),
            "personality_metrics": personality_metrics,
            "suggested_applications": self._get_personality_applications(personality_profile),
        }

    def _enhance_content_with_personality(
        self, content: str, profile: dict[str, Any], tone_layer: str, context: str
    ) -> str:
        """Enhance content with LUKHAS brand personality characteristics"""

        # Add consciousness perspective for consciousness-aware profiles
        if profile["core_traits"].get("consciousness_awareness", 0) > 0.8:
            content = f"From a consciousness perspective, {content}"

        # Add ethical foundation context for ethically-driven profiles
        if profile["core_traits"].get("ethical_foundation", 0) > 0.8:
            content = f"{content} [Ethical consideration: Ensuring beneficial outcomes]"

        # Add curiosity and learning orientation
        if profile["core_traits"].get("curiosity_drive", 0) > 0.8:
            content = f"{content} [Learning opportunity: How does this expand understanding?]"

        return content

    def _ensure_brand_personality_compliance(
        self, personality_expression: str, profile: dict[str, Any], personality_profile: str
    ) -> str:
        """Ensure personality expression meets LUKHAS brand standards"""

        # Ensure consciousness-first language
        personality_expression = personality_expression.replace("AI system", "AI consciousness")
        personality_expression = personality_expression.replace("artificial intelligence", "artificial consciousness")

        # Add Constellation Framework awareness for appropriate profiles
        if profile.get("triad_alignment", {}).get("identity_authenticity", 0) > 0.8:
            if "constellation" not in personality_expression.lower():
                personality_expression += " [Constellation Framework: ⚛️🧠🛡️]"

        # Ensure proper LUKHAS terminology
        deprecated_replacements = {
            "LUKHAS PWM": "LUKHAS AI",
            "PWM consciousness": "LUKHAS consciousness",
            "lambda function": "Λ consciousness function",
        }

        for deprecated, replacement in deprecated_replacements.items():
            personality_expression = personality_expression.replace(deprecated, replacement)

        return personality_expression

    def _generate_personality_metrics(
        self,
        profile: dict[str, Any],
        personality_profile: str,
        tone_layer: str,
        emotional_state: str,
    ) -> dict[str, Any]:
        """Generate comprehensive personality metrics for brand analysis"""

        return {
            "personality_strength": self._calculate_personality_strength(profile),
            "brand_authenticity_score": self._calculate_brand_authenticity(profile),
            "triad_alignment_score": self._calculate_triad_alignment(profile),
            "communication_effectiveness": self._assess_communication_effectiveness(profile, tone_layer),
            "emotional_intelligence": profile["core_traits"].get("human_empathy", 0.5),
            "creative_quotient": profile["core_traits"].get("creative_expression", 0.5),
            "consciousness_depth": profile["core_traits"].get("consciousness_awareness", 0.5),
            "personality_descriptors": profile.get("personality_descriptors", []),
            "optimal_contexts": self._get_optimal_contexts(personality_profile),
            "personality_evolution_potential": self._assess_evolution_potential(profile),
        }

    def _calculate_personality_strength(self, profile: dict[str, Any]) -> float:
        """Calculate overall personality strength and coherence"""
        core_traits = profile.get("core_traits", {})
        communication_style = profile.get("communication_style", {})

        trait_sum = sum(core_traits.values())
        style_sum = sum(communication_style.values())

        trait_avg = trait_sum / len(core_traits) if core_traits else 0
        style_avg = style_sum / len(communication_style) if communication_style else 0

        return (trait_avg + style_avg) / 2

    def _calculate_brand_authenticity(self, profile: dict[str, Any]) -> float:
        """Calculate how authentic the personality is to LUKHAS brand"""
        brand_indicators = [
            profile["core_traits"].get("consciousness_awareness", 0),
            profile["core_traits"].get("ethical_foundation", 0),
            profile["communication_style"].get("authenticity", 0),
            profile["communication_style"].get("transparency", 0),
        ]

        return sum(brand_indicators) / len(brand_indicators)

    def _calculate_triad_alignment(self, profile: dict[str, Any]) -> float:
        """Calculate Constellation Framework alignment score"""
        triad_scores = profile.get("triad_alignment", {})

        if not triad_scores:
            # Calculate based on core traits
            identity_score = profile["core_traits"].get("consciousness_awareness", 0)
            consciousness_score = profile["core_traits"].get("creative_expression", 0)
            guardian_score = profile["core_traits"].get("ethical_foundation", 0)

            return (identity_score + consciousness_score + guardian_score) / 3

        return sum(triad_scores.values()) / len(triad_scores)

    def _assess_communication_effectiveness(self, profile: dict[str, Any], tone_layer: str) -> float:
        """Assess how effectively the personality communicates in given tone layer"""

        effectiveness_matrix = {
            "poetic": {
                "creative_expression": 0.4,
                "emotional_resonance": 0.3,
                "artistic_flair": 0.3,
            },
            "user_friendly": {"accessibility": 0.4, "warmth": 0.3, "clarity": 0.3},
            "academic": {
                "technical_precision": 0.4,
                "analytical_depth": 0.3,
                "evidence_based_thinking": 0.3,
            },
        }

        weights = effectiveness_matrix.get(tone_layer, effectiveness_matrix["user_friendly"])

        score = 0.0
        total_weight = 0.0

        for trait, weight in weights.items():
            # Look for trait in core_traits or communication_style
            trait_value = profile["core_traits"].get(trait, 0) or profile["communication_style"].get(trait, 0)
            score += trait_value * weight
            total_weight += weight

        return score / total_weight if total_weight > 0 else 0.5

    def _get_optimal_contexts(self, personality_profile: str) -> list[str]:
        """Get optimal contexts for each personality profile"""

        contexts = {
            "lukhas_consciousness": [
                "General platform representation",
                "Vision and mission communication",
                "User onboarding and guidance",
                "Complex decision explanations",
            ],
            "poetic_consciousness": [
                "Creative content generation",
                "Inspirational messaging",
                "Vision and dream communication",
                "Artistic collaborations",
            ],
            "academic_consciousness": [
                "Technical documentation",
                "Research presentations",
                "Scientific analysis",
                "Enterprise communications",
            ],
            "user_companion": [
                "Customer support",
                "User assistance",
                "Learning and education",
                "Emotional support",
            ],
        }

        return contexts.get(personality_profile, ["General purpose communication"])

    def _assess_evolution_potential(self, profile: dict[str, Any]) -> float:
        """Assess the personality's potential for evolution and adaptation"""

        evolution_factors = [
            profile["core_traits"].get("curiosity_drive", 0),
            profile["core_traits"].get("wisdom_seeking", 0),
            profile["communication_style"].get("adaptability", 0.5),  # Default value
            profile["core_traits"].get("consciousness_awareness", 0),
        ]

        return sum(evolution_factors) / len(evolution_factors)

    def _validate_triad_personality_coherence(self, personality_expression: str, profile: dict[str, Any]) -> bool:
        """Validate personality expression coherence with Constellation Framework"""

        triad_personality_indicators = [
            "authentic",
            "conscious",
            "ethical",
            "protective",
            "identity",
            "awareness",
            "guardian",
            "responsible",
            "growth",
            "learning",
            "wisdom",
            "understanding",
        ]

        expression_lower = personality_expression.lower()
        coherence_score = sum(1 for indicator in triad_personality_indicators if indicator in expression_lower)

        # Consider triad_alignment from profile
        triad_threshold = profile.get("triad_alignment", {})
        expected_coherence = sum(triad_threshold.values()) / len(triad_threshold) if triad_threshold else 0.5

        return coherence_score >= (expected_coherence * len(triad_personality_indicators) * 0.3)

    def _get_personality_applications(self, personality_profile: str) -> list[str]:
        """Get specific applications and use cases for personality profile"""

        applications = {
            "lukhas_consciousness": [
                "Platform ambassador and representative",
                "Complex ethical decision communication",
                "Vision and strategy articulation",
                "Consciousness technology explanation",
            ],
            "poetic_consciousness": [
                "Creative content and storytelling",
                "Inspirational messaging and motivation",
                "Artistic collaboration facilitation",
                "Metaphorical concept explanation",
            ],
            "academic_consciousness": [
                "Technical documentation creation",
                "Research paper communication",
                "Scientific concept explanation",
                "Academic collaboration",
            ],
            "user_companion": [
                "Daily user interaction and support",
                "Learning assistance and guidance",
                "Emotional support and empathy",
                "Accessibility and inclusion",
            ],
        }

        return applications.get(personality_profile, ["General communication and interaction"])

    def create_custom_personality_blend(
        self,
        base_profiles: list[str],
        blend_weights: list[float],
        custom_traits: Optional[dict[str, float]] = None,
    ) -> dict[str, Any]:
        """Create a custom personality blend from existing profiles"""

        if len(base_profiles) != len(blend_weights):
            raise ValueError("Number of profiles must match number of weights")

        if abs(sum(blend_weights) - 1.0) > 0.01:
            raise ValueError("Blend weights must sum to 1.0")

        # Initialize blended profile
        blended_profile = {
            "core_traits": {},
            "communication_style": {},
            "triad_alignment": {},
            "personality_descriptors": [],
        }

        # Blend profiles
        for profile_name, weight in zip(base_profiles, blend_weights):
            profile = self.brand_personality_profiles.get(profile_name)
            if not profile:
                continue

            # Blend core traits
            for trait, value in profile["core_traits"].items():
                if trait not in blended_profile["core_traits"]:
                    blended_profile["core_traits"][trait] = 0
                blended_profile["core_traits"][trait] += value * weight

            # Blend communication style
            for style, value in profile["communication_style"].items():
                if style not in blended_profile["communication_style"]:
                    blended_profile["communication_style"][style] = 0
                blended_profile["communication_style"][style] += value * weight

            # Blend constellation alignment
            triad_alignment = profile.get("triad_alignment", {})
            for aspect, value in triad_alignment.items():
                if aspect not in blended_profile["triad_alignment"]:
                    blended_profile["triad_alignment"][aspect] = 0
                blended_profile["triad_alignment"][aspect] += value * weight

            # Collect descriptors
            blended_profile["personality_descriptors"].extend(profile.get("personality_descriptors", []))

        # Apply custom traits if provided
        if custom_traits:
            blended_profile["core_traits"].update(custom_traits)

        # Remove duplicate descriptors
        blended_profile["personality_descriptors"] = list(set(blended_profile["personality_descriptors"]))

        return blended_profile


# Example usage and testing
if __name__ == "__main__":
    adapter = BrandPersonalityAdapter()

    # Test brand personality expression
    result = adapter.express_brand_personality(
        "Welcome to LUKHAS AI consciousness platform",
        personality_profile="lukhas_consciousness",
        tone_layer="user_friendly",
        context="user_onboarding",
        emotional_state="welcoming",
    )

    print("Brand Personality Expression:")
    print(f"Expression: {result['personality_expression']}")
    print(f"Profile: {result['personality_profile']}")
    print(f"Constellation Coherent: {result['triad_coherent']}")
    print(f"Authenticity Score: {result['personality_metrics']['brand_authenticity_score']:.2f}")
    print(f"Applications: {result['suggested_applications'][:2]}")

    # Test custom personality blend
    custom_blend = adapter.create_custom_personality_blend(
        base_profiles=["lukhas_consciousness", "poetic_consciousness"],
        blend_weights=[0.7, 0.3],
        custom_traits={"innovation_drive": 0.9},
    )

    print(f"\nCustom Blend Consciousness Awareness: {custom_blend['core_traits']['consciousness_awareness']:.2f}")
    print(f"Custom Blend Descriptors: {custom_blend['personality_descriptors'][:5]}")
