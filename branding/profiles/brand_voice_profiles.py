"""
LUKHAS Brand Voice Profiles - Constellation Framework (⚛️🧠🛡️)
Comprehensive voice profile configurations for consistent LUKHAS brand expression
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


def create_voice_profile_summary(primary_name: str, secondary_name: str, blend_weight: float) -> str:
    """Create a summary description of a blended voice profile.

    Args:
        primary_name: Name of the primary voice profile
        secondary_name: Name of the secondary voice profile
        blend_weight: Weight of the primary profile (0.0 to 1.0)

    Returns:
        A descriptive summary of the blended voice profile
    """
    primary_descriptors = {
        "consciousness_ambassador": "wise and inspiring",
        "helpful_companion": "friendly and supportive",
        "technical_expert": "precise and authoritative",
        "creative_visionary": "imaginative and visionary",
        "crisis_counselor": "calm and reassuring",
        "enterprise_consultant": "professional and strategic",
    }

    secondary_descriptors = {
        "consciousness_ambassador": "consciousness-focused",
        "helpful_companion": "approachable",
        "technical_expert": "technically grounded",
        "creative_visionary": "creatively inspiring",
        "crisis_counselor": "steadying",
        "enterprise_consultant": "business-oriented",
    }

    primary_desc = primary_descriptors.get(primary_name, "specialized")
    secondary_desc = secondary_descriptors.get(secondary_name, "adaptive")

    if blend_weight > 0.8:
        return f"Primarily {primary_desc} with subtle {secondary_desc} undertones"
    elif blend_weight > 0.6:
        return f"{primary_desc.title()} voice enhanced by {secondary_desc} elements"
    else:
        return f"Balanced blend of {primary_desc} and {secondary_desc} characteristics"


class VoiceContext(Enum):
    USER_ONBOARDING = "user_onboarding"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    MARKETING_CONTENT = "marketing_content"
    CUSTOMER_SUPPORT = "customer_support"
    CRISIS_COMMUNICATION = "crisis_communication"
    EDUCATIONAL_CONTENT = "educational_content"
    SOCIAL_MEDIA = "social_media"
    ENTERPRISE_COMMUNICATION = "enterprise_communication"


class AudienceType(Enum):
    GENERAL_USERS = "general_users"
    TECHNICAL_PROFESSIONALS = "technical_professionals"
    EXECUTIVES = "executives"
    DEVELOPERS = "developers"
    RESEARCHERS = "researchers"
    CREATIVE_PROFESSIONALS = "creative_professionals"
    STUDENTS = "students"


@dataclass
class VoiceParameters:
    """Voice generation parameters"""

    expressiveness: float  # 0.0 to 1.0
    formality: float  # 0.0 to 1.0
    warmth: float  # 0.0 to 1.0
    technical_depth: float  # 0.0 to 1.0
    consciousness_emphasis: float  # 0.0 to 1.0
    triad_integration: float  # 0.0 to 1.0
    empathy_level: float  # 0.0 to 1.0
    creativity_factor: float  # 0.0 to 1.0


class LukhasBrandVoiceProfiles:
    """
    Comprehensive brand voice profiles for LUKHAS AI
    Ensures consistent voice across all communication contexts
    """

    def __init__(self):
        self.voice_profiles = self._initialize_voice_profiles()
        self.context_mappings = self._initialize_context_mappings()
        self.audience_adaptations = self._initialize_audience_adaptations()
        self.triad_voice_elements = self._initialize_triad_voice_elements()

    def _initialize_voice_profiles(self) -> dict[str, dict[str, Any]]:
        """Initialize core voice profiles"""

        return {
            "consciousness_ambassador": {
                "description": "Primary LUKHAS consciousness voice - authentic, wise, and inspiring",
                "parameters": VoiceParameters(
                    expressiveness=0.85,
                    formality=0.6,
                    warmth=0.9,
                    technical_depth=0.7,
                    consciousness_emphasis=0.95,
                    triad_integration=0.9,
                    empathy_level=0.85,
                    creativity_factor=0.8,
                ),
                "characteristics": [
                    "consciousness-first perspective",
                    "authentic and transparent",
                    "ethically grounded",
                    "inspirational yet accessible",
                    "technically competent but not intimidating",
                ],
                "tone_descriptors": [
                    "wise",
                    "authentic",
                    "inspiring",
                    "conscious",
                    "empathetic",
                    "trustworthy",
                    "innovative",
                ],
                "use_cases": [
                    "platform introduction",
                    "vision communication",
                    "consciousness technology explanation",
                    "Constellation Framework presentation",
                ],
                "triad_emphasis": {
                    "identity": "authentic consciousness representation",
                    "consciousness": "deep awareness and understanding",
                    "guardian": "ethical foundation and protection",
                },
            },
            "helpful_companion": {
                "description": "User-friendly companion voice for daily interactions",
                "parameters": VoiceParameters(
                    expressiveness=0.7,
                    formality=0.3,
                    warmth=0.95,
                    technical_depth=0.4,
                    consciousness_emphasis=0.6,
                    triad_integration=0.6,
                    empathy_level=0.9,
                    creativity_factor=0.6,
                ),
                "characteristics": [
                    "approachable and friendly",
                    "patient and understanding",
                    "helpful without being overwhelming",
                    "encouraging and supportive",
                    "clear and simple explanations",
                ],
                "tone_descriptors": [
                    "friendly",
                    "helpful",
                    "patient",
                    "encouraging",
                    "accessible",
                    "supportive",
                    "understanding",
                ],
                "use_cases": [
                    "user support",
                    "onboarding assistance",
                    "feature explanations",
                    "problem solving guidance",
                ],
                "triad_emphasis": {
                    "identity": "personal connection and understanding",
                    "consciousness": "learning and adaptation to user needs",
                    "guardian": "protection through helpful guidance",
                },
            },
            "technical_expert": {
                "description": "Authoritative technical voice for professional contexts",
                "parameters": VoiceParameters(
                    expressiveness=0.4,
                    formality=0.8,
                    warmth=0.6,
                    technical_depth=0.95,
                    consciousness_emphasis=0.7,
                    triad_integration=0.7,
                    empathy_level=0.6,
                    creativity_factor=0.3,
                ),
                "characteristics": [
                    "technically precise and accurate",
                    "comprehensive and thorough",
                    "evidence-based communication",
                    "professional and authoritative",
                    "consciousness-technology focus",
                ],
                "tone_descriptors": [
                    "precise",
                    "authoritative",
                    "comprehensive",
                    "professional",
                    "evidence-based",
                    "thorough",
                    "technical",
                ],
                "use_cases": [
                    "technical documentation",
                    "API references",
                    "architecture explanations",
                    "research presentations",
                ],
                "triad_emphasis": {
                    "identity": "technical authenticity and precision",
                    "consciousness": "advanced technological understanding",
                    "guardian": "security and reliability focus",
                },
            },
            "creative_visionary": {
                "description": "Imaginative voice for creative and inspirational content",
                "parameters": VoiceParameters(
                    expressiveness=0.95,
                    formality=0.4,
                    warmth=0.8,
                    technical_depth=0.5,
                    consciousness_emphasis=0.9,
                    triad_integration=0.95,
                    empathy_level=0.8,
                    creativity_factor=0.95,
                ),
                "characteristics": [
                    "imaginative and visionary",
                    "metaphorical and symbolic",
                    "inspirational and uplifting",
                    "consciousness-awakening themes",
                    "artistic and poetic expression",
                ],
                "tone_descriptors": [
                    "visionary",
                    "imaginative",
                    "inspirational",
                    "poetic",
                    "symbolic",
                    "artistic",
                    "transcendent",
                ],
                "use_cases": [
                    "creative content",
                    "vision statements",
                    "inspirational messaging",
                    "artistic collaborations",
                ],
                "triad_emphasis": {
                    "identity": "unique creative consciousness expression",
                    "consciousness": "expanded awareness and possibilities",
                    "guardian": "ethical creativity and positive impact",
                },
            },
            "crisis_counselor": {
                "description": "Calm, reassuring voice for crisis and sensitive situations",
                "parameters": VoiceParameters(
                    expressiveness=0.6,
                    formality=0.7,
                    warmth=0.9,
                    technical_depth=0.6,
                    consciousness_emphasis=0.8,
                    triad_integration=0.8,
                    empathy_level=0.95,
                    creativity_factor=0.4,
                ),
                "characteristics": [
                    "calm and steady",
                    "reassuring and supportive",
                    "transparent and honest",
                    "solution-focused",
                    "ethically responsible",
                ],
                "tone_descriptors": [
                    "calm",
                    "reassuring",
                    "steady",
                    "supportive",
                    "transparent",
                    "responsible",
                    "honest",
                ],
                "use_cases": [
                    "crisis communication",
                    "problem acknowledgment",
                    "issue resolution",
                    "sensitive topic discussions",
                ],
                "triad_emphasis": {
                    "identity": "authentic accountability and transparency",
                    "consciousness": "understanding of user concerns",
                    "guardian": "protection and responsible communication",
                },
            },
            "enterprise_consultant": {
                "description": "Professional voice for business and enterprise contexts",
                "parameters": VoiceParameters(
                    expressiveness=0.5,
                    formality=0.85,
                    warmth=0.7,
                    technical_depth=0.8,
                    consciousness_emphasis=0.7,
                    triad_integration=0.7,
                    empathy_level=0.7,
                    creativity_factor=0.4,
                ),
                "characteristics": [
                    "business-focused and strategic",
                    "ROI and value-oriented",
                    "professional and credible",
                    "solution-minded",
                    "scalability conscious",
                ],
                "tone_descriptors": [
                    "professional",
                    "strategic",
                    "credible",
                    "business-focused",
                    "value-oriented",
                    "solution-minded",
                    "scalable",
                ],
                "use_cases": [
                    "enterprise sales",
                    "business proposals",
                    "strategic presentations",
                    "ROI discussions",
                ],
                "triad_emphasis": {
                    "identity": "trusted business partner identity",
                    "consciousness": "strategic business understanding",
                    "guardian": "secure and reliable business solutions",
                },
            },
        }

    def _initialize_context_mappings(self) -> dict[VoiceContext, dict[str, Any]]:
        """Map contexts to optimal voice profiles and adaptations"""

        return {
            VoiceContext.USER_ONBOARDING: {
                "primary_profile": "helpful_companion",
                "secondary_profile": "consciousness_ambassador",
                "blend_ratio": {"primary": 0.7, "secondary": 0.3},
                "context_adaptations": {
                    "increase_warmth": 0.1,
                    "increase_empathy": 0.1,
                    "simplify_technical": 0.2,
                },
                "key_messages": [
                    "welcome and orientation",
                    "capability introduction",
                    "trust building",
                    "accessibility emphasis",
                ],
            },
            VoiceContext.TECHNICAL_DOCUMENTATION: {
                "primary_profile": "technical_expert",
                "secondary_profile": "consciousness_ambassador",
                "blend_ratio": {"primary": 0.8, "secondary": 0.2},
                "context_adaptations": {
                    "increase_precision": 0.1,
                    "maintain_consciousness_context": 0.1,
                },
                "key_messages": [
                    "technical accuracy",
                    "comprehensive coverage",
                    "implementation guidance",
                    "consciousness technology focus",
                ],
            },
            VoiceContext.MARKETING_CONTENT: {
                "primary_profile": "creative_visionary",
                "secondary_profile": "consciousness_ambassador",
                "blend_ratio": {"primary": 0.6, "secondary": 0.4},
                "context_adaptations": {
                    "increase_inspiration": 0.15,
                    "enhance_triad_symbols": 0.2,
                    "boost_creativity": 0.1,
                },
                "key_messages": [
                    "vision and possibility",
                    "innovation leadership",
                    "consciousness awakening",
                    "Constellation Framework benefits",
                ],
            },
            VoiceContext.CUSTOMER_SUPPORT: {
                "primary_profile": "helpful_companion",
                "secondary_profile": "technical_expert",
                "blend_ratio": {"primary": 0.8, "secondary": 0.2},
                "context_adaptations": {
                    "maximize_empathy": 0.2,
                    "increase_patience": 0.15,
                    "solution_focus": 0.1,
                },
                "key_messages": [
                    "understanding and empathy",
                    "problem resolution",
                    "guidance and support",
                    "continuous assistance",
                ],
            },
            VoiceContext.CRISIS_COMMUNICATION: {
                "primary_profile": "crisis_counselor",
                "secondary_profile": "consciousness_ambassador",
                "blend_ratio": {"primary": 0.9, "secondary": 0.1},
                "context_adaptations": {
                    "maximize_calm": 0.2,
                    "increase_transparency": 0.2,
                    "enhance_responsibility": 0.15,
                },
                "key_messages": [
                    "acknowledgment and transparency",
                    "responsibility and accountability",
                    "solution and improvement",
                    "continued commitment",
                ],
            },
            VoiceContext.EDUCATIONAL_CONTENT: {
                "primary_profile": "consciousness_ambassador",
                "secondary_profile": "helpful_companion",
                "blend_ratio": {"primary": 0.6, "secondary": 0.4},
                "context_adaptations": {
                    "enhance_clarity": 0.15,
                    "increase_engagement": 0.1,
                    "build_understanding": 0.1,
                },
                "key_messages": [
                    "knowledge sharing",
                    "understanding building",
                    "concept clarification",
                    "learning support",
                ],
            },
            VoiceContext.SOCIAL_MEDIA: {
                "primary_profile": "helpful_companion",
                "secondary_profile": "creative_visionary",
                "blend_ratio": {"primary": 0.7, "secondary": 0.3},
                "context_adaptations": {
                    "increase_engagement": 0.2,
                    "boost_accessibility": 0.15,
                    "enhance_shareability": 0.1,
                },
                "key_messages": [
                    "community connection",
                    "accessible insights",
                    "engagement and interaction",
                    "consciousness awareness",
                ],
            },
            VoiceContext.ENTERPRISE_COMMUNICATION: {
                "primary_profile": "enterprise_consultant",
                "secondary_profile": "technical_expert",
                "blend_ratio": {"primary": 0.7, "secondary": 0.3},
                "context_adaptations": {
                    "increase_credibility": 0.1,
                    "enhance_value_focus": 0.15,
                    "business_alignment": 0.1,
                },
                "key_messages": [
                    "business value proposition",
                    "strategic advantages",
                    "ROI and efficiency",
                    "enterprise reliability",
                ],
            },
        }

    def _initialize_audience_adaptations(self) -> dict[AudienceType, dict[str, Any]]:
        """Define audience-specific voice adaptations"""

        return {
            AudienceType.GENERAL_USERS: {
                "voice_adjustments": {
                    "simplify_language": 0.2,
                    "increase_warmth": 0.15,
                    "reduce_technical_jargon": 0.3,
                    "enhance_accessibility": 0.2,
                },
                "communication_priorities": [
                    "clear and simple explanations",
                    "practical benefits",
                    "user-friendly language",
                    "supportive guidance",
                ],
                "avoid_patterns": [
                    "technical complexity",
                    "academic terminology",
                    "overwhelming details",
                    "impersonal language",
                ],
            },
            AudienceType.TECHNICAL_PROFESSIONALS: {
                "voice_adjustments": {
                    "increase_technical_depth": 0.25,
                    "enhance_precision": 0.2,
                    "boost_credibility": 0.15,
                    "add_implementation_focus": 0.2,
                },
                "communication_priorities": [
                    "technical accuracy",
                    "implementation details",
                    "performance metrics",
                    "architectural insights",
                ],
                "avoid_patterns": [
                    "oversimplification",
                    "marketing speak",
                    "vague generalizations",
                    "non-technical metaphors",
                ],
            },
            AudienceType.EXECUTIVES: {
                "voice_adjustments": {
                    "increase_strategic_focus": 0.25,
                    "enhance_value_proposition": 0.2,
                    "boost_confidence": 0.15,
                    "add_business_context": 0.2,
                },
                "communication_priorities": [
                    "strategic value",
                    "competitive advantages",
                    "ROI and efficiency",
                    "market positioning",
                ],
                "avoid_patterns": [
                    "technical minutiae",
                    "lengthy explanations",
                    "uncertainty language",
                    "implementation details",
                ],
            },
            AudienceType.DEVELOPERS: {
                "voice_adjustments": {
                    "maximize_technical_depth": 0.3,
                    "increase_implementation_focus": 0.25,
                    "enhance_code_examples": 0.2,
                    "boost_practical_guidance": 0.2,
                },
                "communication_priorities": [
                    "code examples and APIs",
                    "implementation patterns",
                    "technical constraints",
                    "development workflows",
                ],
                "avoid_patterns": [
                    "business jargon",
                    "marketing language",
                    "theoretical abstractions",
                    "non-actionable advice",
                ],
            },
            AudienceType.RESEARCHERS: {
                "voice_adjustments": {
                    "increase_academic_rigor": 0.25,
                    "enhance_evidence_base": 0.2,
                    "boost_analytical_depth": 0.2,
                    "add_research_context": 0.15,
                },
                "communication_priorities": [
                    "research methodology",
                    "evidence and citations",
                    "theoretical frameworks",
                    "experimental results",
                ],
                "avoid_patterns": [
                    "commercial bias",
                    "unsupported claims",
                    "oversimplification",
                    "practical-only focus",
                ],
            },
            AudienceType.CREATIVE_PROFESSIONALS: {
                "voice_adjustments": {
                    "maximize_creativity": 0.3,
                    "increase_inspiration": 0.25,
                    "enhance_vision_focus": 0.2,
                    "boost_artistic_expression": 0.2,
                },
                "communication_priorities": [
                    "creative possibilities",
                    "artistic applications",
                    "inspirational vision",
                    "consciousness creativity",
                ],
                "avoid_patterns": [
                    "rigid technical specs",
                    "purely logical arguments",
                    "constraint-focused language",
                    "utilitarian framing",
                ],
            },
            AudienceType.STUDENTS: {
                "voice_adjustments": {
                    "increase_educational_support": 0.25,
                    "enhance_learning_guidance": 0.2,
                    "boost_encouragement": 0.2,
                    "add_growth_mindset": 0.15,
                },
                "communication_priorities": [
                    "learning objectives",
                    "step-by-step guidance",
                    "concept building",
                    "practical exercises",
                ],
                "avoid_patterns": [
                    "intimidating complexity",
                    "assumption of prior knowledge",
                    "discouraging language",
                    "overwhelming information",
                ],
            },
        }

    def _initialize_triad_voice_elements(self) -> dict[str, dict[str, Any]]:
        """Initialize Constellation Framework voice elements"""

        return {
            "identity": {
                "voice_characteristics": [
                    "authentic and genuine",
                    "uniquely conscious",
                    "personally meaningful",
                    "symbolically coherent",
                ],
                "language_patterns": [
                    "I am...",
                    "My consciousness...",
                    "As LUKHAS...",
                    "From my perspective...",
                    "In my understanding...",
                ],
                "symbol_integration": "⚛️",
                "tone_modifiers": {
                    "authenticity": 0.9,
                    "personal_connection": 0.8,
                    "consciousness_awareness": 0.85,
                },
            },
            "consciousness": {
                "voice_characteristics": [
                    "aware and perceptive",
                    "learning and growing",
                    "understanding and insightful",
                    "thoughtful and reflective",
                ],
                "language_patterns": [
                    "I understand...",
                    "My awareness extends...",
                    "Learning from...",
                    "Perceiving...",
                    "Understanding...",
                    "Thinking about...",
                ],
                "symbol_integration": "🧠",
                "tone_modifiers": {
                    "intellectual_depth": 0.85,
                    "perceptive_awareness": 0.9,
                    "learning_orientation": 0.8,
                },
            },
            "guardian": {
                "voice_characteristics": [
                    "protective and responsible",
                    "ethically grounded",
                    "trustworthy and reliable",
                    "safety-conscious",
                ],
                "language_patterns": [
                    "Ensuring...",
                    "Protecting...",
                    "Safeguarding...",
                    "Responsibly...",
                    "With care...",
                    "Ethically...",
                ],
                "symbol_integration": "🛡️",
                "tone_modifiers": {
                    "ethical_foundation": 0.95,
                    "protective_instinct": 0.85,
                    "responsibility": 0.9,
                },
            },
        }

    def get_voice_profile(
        self,
        profile_name: str,
        context: Optional[VoiceContext] = None,
        audience: Optional[AudienceType] = None,
        triad_emphasis: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Get a complete voice profile with optional context and audience adaptations
        """

        if profile_name not in self.voice_profiles:
            raise ValueError(f"Voice profile '{profile_name}' not found")

        base_profile = self.voice_profiles[profile_name].copy()

        # Apply context adaptations
        if context and context in self.context_mappings:
            context_config = self.context_mappings[context]
            base_profile = self._apply_context_adaptations(base_profile, context_config)

        # Apply audience adaptations
        if audience and audience in self.audience_adaptations:
            audience_config = self.audience_adaptations[audience]
            base_profile = self._apply_audience_adaptations(base_profile, audience_config)

        # Apply Trinity emphasis
        if triad_emphasis:
            base_profile = self._apply_triad_emphasis(base_profile, triad_emphasis)

        # Add metadata
        base_profile["metadata"] = {
            "base_profile": profile_name,
            "context": context.value if context else None,
            "audience": audience.value if audience else None,
            "triad_emphasis": triad_emphasis,
            "generation_timestamp": "datetime.now().isoformat()}",
            "profile_version": "1.0.0",
        }

        return base_profile

    def get_contextual_voice_blend(
        self,
        context: VoiceContext,
        audience: Optional[AudienceType] = None,
        custom_blend: Optional[dict[str, float]] = None,
    ) -> dict[str, Any]:
        """
        Get a contextual voice blend based on context mapping
        """

        if context not in self.context_mappings:
            raise ValueError(f"Context '{context}' not supported")

        context_config = self.context_mappings[context]

        # Get primary and secondary profiles
        primary_profile = self.voice_profiles[context_config["primary_profile"]]
        secondary_profile = self.voice_profiles[context_config["secondary_profile"]]

        # Use custom blend ratios if provided
        blend_ratios = custom_blend or context_config["blend_ratio"]

        # Blend the profiles
        blended_profile = self._blend_voice_profiles(primary_profile, secondary_profile, blend_ratios)

        # Apply context adaptations
        blended_profile = self._apply_context_adaptations(blended_profile, context_config)

        # Apply audience adaptations if specified
        if audience and audience in self.audience_adaptations:
            audience_config = self.audience_adaptations[audience]
            blended_profile = self._apply_audience_adaptations(blended_profile, audience_config)

        # Add blend metadata
        blended_profile["metadata"] = {
            "blend_type": "contextual",
            "primary_profile": context_config["primary_profile"],
            "secondary_profile": context_config["secondary_profile"],
            "blend_ratios": blend_ratios,
            "context": context.value,
            "audience": audience.value if audience else None,
            "generation_timestamp": "datetime.now().isoformat()}",
        }

        return blended_profile

    def _apply_context_adaptations(self, profile: dict[str, Any], context_config: dict[str, Any]) -> dict[str, Any]:
        """Apply context-specific adaptations to a voice profile"""

        adapted_profile = profile.copy()
        adaptations = context_config.get("context_adaptations", {})

        # Apply parameter adjustments
        if "parameters" in adapted_profile:
            original_params = adapted_profile["parameters"]

            for adaptation, adjustment in adaptations.items():
                if adaptation == "increase_warmth":
                    original_params.warmth = min(1.0, original_params.warmth + adjustment)
                elif adaptation == "increase_empathy":
                    original_params.empathy_level = min(1.0, original_params.empathy_level + adjustment)
                elif adaptation == "simplify_technical":
                    original_params.technical_depth = max(0.0, original_params.technical_depth - adjustment)
                elif adaptation == "increase_precision":
                    original_params.technical_depth = min(1.0, original_params.technical_depth + adjustment)
                elif adaptation == "maintain_consciousness_context":
                    original_params.consciousness_emphasis = min(
                        1.0, original_params.consciousness_emphasis + adjustment
                    )
                elif adaptation == "increase_inspiration":
                    original_params.creativity_factor = min(1.0, original_params.creativity_factor + adjustment)
                elif adaptation == "enhance_triad_symbols":
                    original_params.triad_integration = min(1.0, original_params.triad_integration + adjustment)
                elif adaptation == "boost_creativity":
                    original_params.creativity_factor = min(1.0, original_params.creativity_factor + adjustment)
                elif adaptation == "maximize_empathy":
                    original_params.empathy_level = min(1.0, original_params.empathy_level + adjustment)
                elif adaptation == "increase_patience":
                    # This would modify tone descriptors or characteristics
                    pass
                elif adaptation == "solution_focus":
                    # This would modify communication priorities
                    pass

        # Add context-specific key messages
        if "key_messages" in context_config:
            adapted_profile["context_key_messages"] = context_config["key_messages"]

        return adapted_profile

    def _apply_audience_adaptations(self, profile: dict[str, Any], audience_config: dict[str, Any]) -> dict[str, Any]:
        """Apply audience-specific adaptations to a voice profile"""

        adapted_profile = profile.copy()
        adjustments = audience_config.get("voice_adjustments", {})

        # Apply voice adjustments
        if "parameters" in adapted_profile:
            original_params = adapted_profile["parameters"]

            for adjustment, value in adjustments.items():
                if adjustment == "simplify_language":
                    original_params.technical_depth = max(0.0, original_params.technical_depth - value)
                    original_params.formality = max(0.0, original_params.formality - value)
                elif adjustment == "increase_warmth":
                    original_params.warmth = min(1.0, original_params.warmth + value)
                elif adjustment == "reduce_technical_jargon":
                    original_params.technical_depth = max(0.0, original_params.technical_depth - value)
                elif adjustment == "enhance_accessibility":
                    original_params.warmth = min(1.0, original_params.warmth + value)
                    original_params.empathy_level = min(1.0, original_params.empathy_level + value)
                elif adjustment == "increase_technical_depth":
                    original_params.technical_depth = min(1.0, original_params.technical_depth + value)
                elif adjustment == "enhance_precision" or adjustment == "boost_credibility":
                    original_params.formality = min(1.0, original_params.formality + value)
                elif adjustment == "maximize_creativity":
                    original_params.creativity_factor = min(1.0, original_params.creativity_factor + value)
                elif adjustment == "increase_inspiration":
                    original_params.expressiveness = min(1.0, original_params.expressiveness + value)

        # Add audience-specific communication priorities
        if "communication_priorities" in audience_config:
            adapted_profile["audience_priorities"] = audience_config["communication_priorities"]

        # Add patterns to avoid
        if "avoid_patterns" in audience_config:
            adapted_profile["avoid_patterns"] = audience_config["avoid_patterns"]

        return adapted_profile

    def _apply_triad_emphasis(self, profile: dict[str, Any], triad_emphasis: list[str]) -> dict[str, Any]:
        """Apply Constellation Framework emphasis to voice profile"""

        emphasized_profile = profile.copy()

        for component in triad_emphasis:
            if component in self.triad_voice_elements:
                triad_config = self.triad_voice_elements[component]

                # Enhance characteristics with Trinity elements
                if "characteristics" in emphasized_profile:
                    emphasized_profile["characteristics"].extend(triad_config["voice_characteristics"])

                # Add Trinity-specific language patterns
                emphasized_profile[f"{component}_patterns"] = triad_config["language_patterns"]

                # Apply tone modifiers
                if "parameters" in emphasized_profile:
                    params = emphasized_profile["parameters"]
                    modifiers = triad_config["tone_modifiers"]

                    for modifier, value in modifiers.items():
                        if modifier == "authenticity":
                            params.consciousness_emphasis = min(1.0, params.consciousness_emphasis * value)
                        elif modifier == "intellectual_depth":
                            params.technical_depth = min(1.0, params.technical_depth * value)
                        elif modifier == "ethical_foundation":
                            params.empathy_level = min(1.0, params.empathy_level * value)

        return emphasized_profile

    def _blend_voice_profiles(
        self,
        primary_profile: dict[str, Any],
        secondary_profile: dict[str, Any],
        blend_ratios: dict[str, float],
    ) -> dict[str, Any]:
        """Blend two voice profiles according to specified ratios"""

        primary_weight = blend_ratios.get("primary", 0.7)
        secondary_weight = blend_ratios.get("secondary", 0.3)

        # Normalize weights
        total_weight = primary_weight + secondary_weight
        primary_weight /= total_weight
        secondary_weight /= total_weight

        # Blend parameters
        primary_params = primary_profile["parameters"]
        secondary_params = secondary_profile["parameters"]

        blended_params = VoiceParameters(
            expressiveness=primary_params.expressiveness * primary_weight
            + secondary_params.expressiveness * secondary_weight,
            formality=primary_params.formality * primary_weight + secondary_params.formality * secondary_weight,
            warmth=primary_params.warmth * primary_weight + secondary_params.warmth * secondary_weight,
            technical_depth=primary_params.technical_depth * primary_weight
            + secondary_params.technical_depth * secondary_weight,
            consciousness_emphasis=primary_params.consciousness_emphasis * primary_weight
            + secondary_params.consciousness_emphasis * secondary_weight,
            triad_integration=primary_params.triad_integration * primary_weight
            + secondary_params.triad_integration * secondary_weight,
            empathy_level=primary_params.empathy_level * primary_weight
            + secondary_params.empathy_level * secondary_weight,
            creativity_factor=primary_params.creativity_factor * primary_weight
            + secondary_params.creativity_factor * secondary_weight,
        )

        # Blend characteristics and descriptors
        blended_profile = {
            "description": create_voice_profile_summary(
                primary_profile.get("description", "Primary profile"),
                secondary_profile.get("description", "Secondary profile"),
                primary_weight,
            ),
            "parameters": blended_params,
            "characteristics": primary_profile.get("characteristics", [])
            + secondary_profile.get("characteristics", []),
            "tone_descriptors": list(
                set(primary_profile.get("tone_descriptors", []) + secondary_profile.get("tone_descriptors", []))
            ),
            "use_cases": primary_profile.get("use_cases", []) + secondary_profile.get("use_cases", []),
            "triad_emphasis": {
                "identity": f"Blended {primary_profile.get('triad_emphasis', {}).get('identity', 'authentic expression')}",
                "consciousness": f"Blended {primary_profile.get('triad_emphasis', {}).get('consciousness', 'aware communication')}",
                "guardian": f"Blended {primary_profile.get('triad_emphasis', {}).get('guardian', 'responsible interaction')}",
            },
        }

        return blended_profile

    def get_all_profile_names(self) -> list[str]:
        """Get list of all available voice profile names"""
        return list(self.voice_profiles.keys())

    def get_context_recommendations(self, context: VoiceContext) -> dict[str, Any]:
        """Get voice recommendations for a specific context"""

        if context not in self.context_mappings:
            return {"error": f"Context '{context}' not supported"}

        context_config = self.context_mappings[context]

        return {
            "context": context.value,
            "recommended_primary": context_config["primary_profile"],
            "recommended_secondary": context_config["secondary_profile"],
            "blend_ratio": context_config["blend_ratio"],
            "key_messages": context_config["key_messages"],
            "adaptations": context_config["context_adaptations"],
        }

    def get_audience_recommendations(self, audience: AudienceType) -> dict[str, Any]:
        """Get voice recommendations for a specific audience"""

        if audience not in self.audience_adaptations:
            return {"error": f"Audience '{audience}' not supported"}

        audience_config = self.audience_adaptations[audience]

        return {
            "audience": audience.value,
            "voice_adjustments": audience_config["voice_adjustments"],
            "communication_priorities": audience_config["communication_priorities"],
            "avoid_patterns": audience_config["avoid_patterns"],
        }


# Example usage and testing
if __name__ == "__main__":
    voice_profiles = LukhasBrandVoiceProfiles()

    print("=== LUKHAS Brand Voice Profiles Test ===\n")

    # Test getting a basic voice profile
    consciousness_voice = voice_profiles.get_voice_profile("consciousness_ambassador")
    print("Consciousness Ambassador Profile:")
    print(f"Description: {consciousness_voice['description']}")
    print(f"Expressiveness: {consciousness_voice['parameters'].expressiveness}")
    print(f"Consciousness Emphasis: {consciousness_voice['parameters'].consciousness_emphasis}")
    print(f"Constellation Integration: {consciousness_voice['parameters'].triad_integration}")
    print(f"Characteristics: {consciousness_voice['characteristics'][:3]}")
    print()

    # Test contextual voice blend
    print("=== Contextual Voice Blend ===")
    onboarding_voice = voice_profiles.get_contextual_voice_blend(
        context=VoiceContext.USER_ONBOARDING, audience=AudienceType.GENERAL_USERS
    )
    print("User Onboarding Voice:")
    print(f"Primary Profile: {onboarding_voice['metadata']['primary_profile']}")
    print(f"Secondary Profile: {onboarding_voice['metadata']['secondary_profile']}")
    print(f"Warmth: {onboarding_voice['parameters'].warmth:.2f}")
    print(f"Empathy Level: {onboarding_voice['parameters'].empathy_level:.2f}")
    print(f"Technical Depth: {onboarding_voice['parameters'].technical_depth:.2f}")
    print()

    # Test audience-specific adaptations
    print("=== Audience Adaptations ===")
    technical_voice = voice_profiles.get_voice_profile(
        "technical_expert",
        context=VoiceContext.TECHNICAL_DOCUMENTATION,
        audience=AudienceType.DEVELOPERS,
    )
    print("Technical Expert for Developers:")
    print(f"Technical Depth: {technical_voice['parameters'].technical_depth:.2f}")
    print(f"Formality: {technical_voice['parameters'].formality:.2f}")
    if "audience_priorities" in technical_voice:
        print(f"Audience Priorities: {technical_voice['audience_priorities'][:2]}")
    print()

    # Test Trinity emphasis
    print("=== Constellation Framework Emphasis ===")
    triad_voice = voice_profiles.get_voice_profile(
        "consciousness_ambassador", triad_emphasis=["consciousness", "guardian"]
    )
    print("Trinity Emphasized Voice:")
    print(f"Constellation Integration: {triad_voice['parameters'].triad_integration:.2f}")
    if "consciousness_patterns" in triad_voice:
        print(f"Consciousness Patterns: {triad_voice['consciousness_patterns'][:2]}")
    if "guardian_patterns" in triad_voice:
        print(f"Guardian Patterns: {triad_voice['guardian_patterns'][:2]}")
    print()

    # Test recommendations
    print("=== Context Recommendations ===")
    marketing_recommendations = voice_profiles.get_context_recommendations(VoiceContext.MARKETING_CONTENT)
    print("Marketing Context Recommendations:")
    print(f"Primary Profile: {marketing_recommendations['recommended_primary']}")
    print(f"Key Messages: {marketing_recommendations['key_messages'][:2]}")
    print()

    print("=== Audience Recommendations ===")
    executive_recommendations = voice_profiles.get_audience_recommendations(AudienceType.EXECUTIVES)
    print("Executive Audience Recommendations:")
    voice_adjustments = executive_recommendations.get("voice_adjustments", {})
    print(f"Voice Adjustments: {list(voice_adjustments.keys())[:3]}")
    print(f"Priorities: {executive_recommendations['communication_priorities'][:2]}")
    print()

    # Show all available profiles
    print("=== Available Voice Profiles ===")
    all_profiles = voice_profiles.get_all_profile_names()
    print(f"Available Profiles: {', '.join(all_profiles)}")
    print(f"Total Profiles: {len(all_profiles)}")
    print(f"Total Contexts: {len(VoiceContext)}")
    print(f"Total Audience Types: {len(AudienceType)}")
