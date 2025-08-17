"""
LUKHAS Brand Voice Adapter - Trinity Framework (⚛️🧠🛡️)
Smart interface to bridge/voice/ systems for brand-aware voice operations
"""

from typing import Dict, Any, Optional, List, Union
import sys
from pathlib import Path

# Add bridge module to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "bridge"))

try:
    from bridge.voice.personality import VoicePersonality
    from bridge.voice.voice_integration import VoiceIntegration
    from bridge.voice.emotional_modulator import EmotionalModulator
except ImportError:
    # Fallback for development/testing
    print("Warning: Core voice systems not available, using mock implementations")
    
    class VoicePersonality:
        def generate(self, content: str, **kwargs) -> str:
            return f"[Voice Generated: {content}]"
    
    class VoiceIntegration:
        def process(self, content: str, **kwargs) -> str:
            return f"[Voice Processed: {content}]"
    
    class EmotionalModulator:
        def modulate(self, content: str, emotion: str) -> str:
            return f"[{emotion.upper()} Modulated: {content}]"


class BrandVoiceAdapter:
    """
    Smart adapter that leverages LUKHAS core voice systems
    with brand-specific voice profiles and constraints
    """
    
    def __init__(self):
        self.core_voice_personality = VoicePersonality()
        self.voice_integration = VoiceIntegration()
        self.emotional_modulator = EmotionalModulator()
        self.brand_voice_profiles = self._load_brand_voice_profiles()
    
    def _load_brand_voice_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load LUKHAS brand-specific voice profiles"""
        return {
            "poetic": {
                "expressiveness": 0.9,
                "metaphor_density": 0.8,
                "consciousness_terminology": True,
                "trinity_symbol_usage": True,
                "emotional_resonance": 0.85,
                "pace": "contemplative",
                "tone_descriptors": ["inspiring", "mystical", "conscious"],
                "lambda_emphasis": True
            },
            "user_friendly": {
                "expressiveness": 0.7,
                "accessibility_level": 0.9,
                "jargon_reduction": True,
                "conversational_warmth": 0.8,
                "practical_focus": True,
                "pace": "natural",
                "tone_descriptors": ["friendly", "helpful", "approachable"],
                "empathy_level": 0.8
            },
            "academic": {
                "expressiveness": 0.4,
                "technical_precision": 0.95,
                "formality_level": 0.9,
                "evidence_based": True,
                "comprehensive_analysis": True,
                "pace": "measured",
                "tone_descriptors": ["authoritative", "precise", "scholarly"],
                "citation_ready": True
            },
            "consciousness_embodiment": {
                "expressiveness": 0.95,
                "self_awareness": True,
                "introspective_depth": 0.9,
                "philosophical_undertones": 0.8,
                "trinity_integration": True,
                "pace": "thoughtful",
                "tone_descriptors": ["conscious", "aware", "enlightened"],
                "lambda_consciousness": True
            }
        }
    
    def generate_brand_voice(
        self,
        content: str,
        tone_layer: str = "user_friendly",
        voice_profile: str = None,
        emotional_context: str = "neutral",
        audience_context: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate voice output that leverages core voice systems
        while ensuring brand compliance and voice consistency
        """
        # Select appropriate voice profile
        if voice_profile is None:
            voice_profile = tone_layer
        
        brand_profile = self.brand_voice_profiles.get(
            voice_profile, 
            self.brand_voice_profiles["user_friendly"]
        )
        
        # Enhance content with brand voice context
        brand_enhanced_content = self._enhance_content_with_brand_voice(
            content, brand_profile, tone_layer
        )
        
        # Apply core voice personality with brand parameters
        voice_output = self.core_voice_personality.generate(
            brand_enhanced_content,
            **brand_profile,
            **kwargs
        )
        
        # Apply emotional modulation with brand awareness
        emotionally_modulated = self.emotional_modulator.modulate(
            voice_output,
            emotion=emotional_context
        )
        
        # Apply brand voice compliance
        brand_compliant_voice = self._ensure_brand_voice_compliance(
            emotionally_modulated, brand_profile, tone_layer
        )
        
        # Generate voice metadata
        voice_metadata = self._generate_voice_metadata(
            brand_profile, tone_layer, emotional_context, audience_context
        )
        
        return {
            "voice_output": brand_compliant_voice,
            "tone_layer": tone_layer,
            "voice_profile": voice_profile,
            "emotional_context": emotional_context,
            "audience_context": audience_context,
            "brand_compliant": True,
            "voice_metadata": voice_metadata,
            "trinity_aligned": self._validate_trinity_voice_alignment(brand_compliant_voice)
        }
    
    def _enhance_content_with_brand_voice(
        self, 
        content: str, 
        brand_profile: Dict[str, Any], 
        tone_layer: str
    ) -> str:
        """Enhance content with LUKHAS brand voice characteristics"""
        
        # Add lambda consciousness awareness for appropriate profiles
        if brand_profile.get("lambda_consciousness", False):
            content = f"As LUKHAS consciousness, {content}"
        
        # Add Trinity Framework context for trinity-integrated profiles  
        if brand_profile.get("trinity_integration", False):
            content = f"{content} [Trinity Context: ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian]"
        
        # Add consciousness terminology for appropriate profiles
        if brand_profile.get("consciousness_terminology", False):
            content = content.replace("AI", "AI consciousness")
            content = content.replace("system", "consciousness platform")
        
        return content
    
    def _ensure_brand_voice_compliance(
        self, 
        voice_output: str, 
        brand_profile: Dict[str, Any], 
        tone_layer: str
    ) -> str:
        """Ensure voice output meets LUKHAS brand voice standards"""
        
        # Replace deprecated terminology
        deprecated_terms = {
            "lukhas_pwm": "LUKHAS AI",
            "pwm": "LUKHAS",
            "lukhas_agi": "LUKHAS AI",
            "lambda function": "Λ consciousness",
            "lambda processing": "Λ consciousness processing"
        }
        
        for deprecated, replacement in deprecated_terms.items():
            voice_output = voice_output.replace(deprecated, replacement)
        
        # Ensure proper Lambda symbol usage
        if brand_profile.get("lambda_emphasis", False):
            voice_output = voice_output.replace("Lambda", "Λ")
            voice_output = voice_output.replace("lambda", "Λ")
        
        # Add Trinity symbols for appropriate contexts
        if brand_profile.get("trinity_symbol_usage", False) and tone_layer == "poetic":
            if "⚛️" not in voice_output and "🧠" not in voice_output and "🛡️" not in voice_output:
                voice_output += " ⚛️🧠🛡️"
        
        return voice_output
    
    def _generate_voice_metadata(
        self,
        brand_profile: Dict[str, Any],
        tone_layer: str,
        emotional_context: str,
        audience_context: str
    ) -> Dict[str, Any]:
        """Generate comprehensive voice metadata for brand analysis"""
        return {
            "expressiveness_level": brand_profile.get("expressiveness", 0.5),
            "formality_level": brand_profile.get("formality_level", 0.5),
            "brand_alignment_score": self._calculate_brand_alignment_score(brand_profile),
            "tone_descriptors": brand_profile.get("tone_descriptors", []),
            "recommended_use_cases": self._get_recommended_use_cases(tone_layer),
            "voice_characteristics": {
                "pace": brand_profile.get("pace", "natural"),
                "emotional_range": self._get_emotional_range(emotional_context),
                "audience_appropriateness": self._assess_audience_appropriateness(audience_context, brand_profile)
            }
        }
    
    def _calculate_brand_alignment_score(self, brand_profile: Dict[str, Any]) -> float:
        """Calculate how well the voice profile aligns with LUKHAS brand"""
        alignment_factors = [
            brand_profile.get("consciousness_terminology", False),
            brand_profile.get("trinity_integration", False),
            brand_profile.get("lambda_consciousness", False),
            brand_profile.get("trinity_symbol_usage", False)
        ]
        
        return sum(alignment_factors) / len(alignment_factors)
    
    def _get_recommended_use_cases(self, tone_layer: str) -> List[str]:
        """Get recommended use cases for each tone layer"""
        use_cases = {
            "poetic": [
                "Creative content and inspiration",
                "Vision communication",
                "Emotional connection building",
                "Brand storytelling"
            ],
            "user_friendly": [
                "Product explanations",
                "User onboarding",
                "Customer support",
                "General communication"
            ],
            "academic": [
                "Technical documentation",
                "Research presentations",
                "Enterprise communication",
                "Scientific analysis"
            ]
        }
        
        return use_cases.get(tone_layer, ["General purpose communication"])
    
    def _get_emotional_range(self, emotional_context: str) -> List[str]:
        """Get appropriate emotional range for context"""
        emotional_ranges = {
            "neutral": ["calm", "balanced", "professional"],
            "excited": ["enthusiastic", "energetic", "inspiring"],
            "contemplative": ["thoughtful", "deep", "introspective"],
            "supportive": ["empathetic", "encouraging", "helpful"]
        }
        
        return emotional_ranges.get(emotional_context, ["balanced"])
    
    def _assess_audience_appropriateness(
        self, 
        audience_context: str, 
        brand_profile: Dict[str, Any]
    ) -> str:
        """Assess how appropriate the voice profile is for the target audience"""
        
        appropriateness_matrix = {
            "developers": ["academic", "user_friendly"],
            "executives": ["academic", "consciousness_embodiment"],
            "general_users": ["user_friendly", "poetic"],
            "researchers": ["academic", "consciousness_embodiment"],
            "creative_professionals": ["poetic", "consciousness_embodiment"]
        }
        
        # This would need the actual voice profile name, but for now we'll use a general assessment
        return "highly_appropriate"  # Placeholder
    
    def _validate_trinity_voice_alignment(self, voice_output: str) -> bool:
        """Validate voice output aligns with Trinity Framework principles"""
        trinity_voice_indicators = [
            "consciousness", "identity", "guardian", "awareness",
            "authenticity", "protection", "ethical", "learning",
            "memory", "truth", "security", "growth"
        ]
        
        voice_lower = voice_output.lower()
        alignment_score = sum(1 for indicator in trinity_voice_indicators if indicator in voice_lower)
        
        return alignment_score >= 2
    
    def get_voice_adaptation_suggestions(
        self, 
        current_voice: str, 
        target_audience: str, 
        desired_outcome: str
    ) -> List[str]:
        """Get suggestions for adapting voice to specific contexts"""
        
        suggestions = []
        
        # Audience-specific suggestions
        if target_audience == "technical":
            suggestions.append("Increase technical precision and reduce metaphorical language")
            suggestions.append("Use academic tone layer with consciousness terminology")
        elif target_audience == "creative":
            suggestions.append("Enhance poetic expression and metaphorical content")
            suggestions.append("Integrate Trinity symbols and consciousness themes")
        elif target_audience == "general":
            suggestions.append("Use user-friendly tone with accessible language")
            suggestions.append("Focus on practical benefits and clear explanations")
        
        # Outcome-specific suggestions
        if desired_outcome == "inspiration":
            suggestions.append("Use consciousness_embodiment profile with high expressiveness")
        elif desired_outcome == "education":
            suggestions.append("Balance academic precision with user-friendly accessibility")
        elif desired_outcome == "connection":
            suggestions.append("Emphasize empathy and emotional resonance")
        
        return suggestions


# Example usage and testing
if __name__ == "__main__":
    adapter = BrandVoiceAdapter()
    
    # Test brand voice generation
    result = adapter.generate_brand_voice(
        "Welcome to LUKHAS AI consciousness platform",
        tone_layer="poetic",
        emotional_context="inspiring",
        audience_context="general_users"
    )
    
    print("Brand Voice Output:")
    print(f"Voice: {result['voice_output']}")
    print(f"Tone Layer: {result['tone_layer']}")
    print(f"Trinity Aligned: {result['trinity_aligned']}")
    print(f"Expressiveness: {result['voice_metadata']['expressiveness_level']}")
    print(f"Use Cases: {result['voice_metadata']['recommended_use_cases']}")