"""
LUKHAS Brand Voice Adapter - Trinity Framework (⚛️🧠🛡️)
Smart interface to bridge/voice/ systems for brand-aware voice operations
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Optional


# Add bridge module to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "bridge"))

# Import real LLM bridge for voice generation
try:
    from branding.integrations.simple_llm_bridge import (
        SimpleLLMBridge,
        VoiceGenerationRequest,
        VoiceGenerationResponse,
    )

    LLM_BRIDGE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LLM Bridge not available: {e}")
    LLM_BRIDGE_AVAILABLE = False

# Import voice systems with fallback
try:
    from products.experience.voice.core import (
        LUKHASAudioProcessor,
        LUKHASVoiceSystem,
        VoiceEffectsProcessor,
        VoiceModulator,
    )

    VOICE_SYSTEMS_AVAILABLE = True
    logging.info("Real LUKHAS voice systems loaded successfully")

    # Real implementations using LUKHAS voice systems
    class EmotionalModulator:
        def __init__(self):
            self.voice_effects = VoiceEffectsProcessor()

        def modulate(self, audio, emotion, intensity=0.5):
            # Apply emotion-based voice effects
            try:
                return self.voice_effects.apply_voice_effect(audio, emotion, intensity)
            except Exception:
                return audio

    class VoicePersonalityIntegrator:
        def __init__(self):
            self.voice_modulator = VoiceModulator()

        def adapt_to_emotion(self, emotion: str, intensity: float = 0.5, **kwargs) -> dict[str, Any]:
            # Use real voice modulation parameters
            return {
                "pitch": 1.0 + (intensity * 0.3 if emotion in ["happy", "excited"] else -intensity * 0.2),
                "rate": 1.0 + (intensity * 0.2 if emotion == "excited" else -intensity * 0.3 if emotion == "sad" else 0),
                "volume": 1.0,
                "emphasis": intensity
            }

        def enhance_text_expression(self, text: str, emotion: str, **kwargs) -> str:
            # Add emotional markers for TTS processing
            emotion_markers = {
                "happy": "<prosody rate='+10%' pitch='+5%'>",
                "sad": "<prosody rate='-20%' pitch='-10%'>",
                "excited": "<prosody rate='+20%' pitch='+15%'>",
                "calm": "<prosody rate='-5%'>",
                "angry": "<prosody pitch='+20%' volume='+5dB'>"
            }

            marker = emotion_markers.get(emotion, "")
            end_marker = "</prosody>" if marker else ""

            return f"{marker}{content}{end_marker}"

    class VoiceIntegration:
        def __init__(self):
            self.voice_system = LUKHASVoiceSystem()
            self.audio_processor = LUKHASAudioProcessor()

        async def process(self, content: str, **kwargs) -> str:
            # Use real LUKHAS voice processing pipeline
            try:
                result = await self.voice_system.process_audio_pipeline(content, **kwargs)
                return result.processed_text if hasattr(result, "processed_text") else content
            except Exception:
                return content

except ImportError as e:
    logging.warning(f"Core voice systems not available ({e}), using compatibility layer")
    VOICE_SYSTEMS_AVAILABLE = False

    # Compatibility classes for voice systems
    class VoicePersonalityIntegrator:
        def adapt_to_emotion(self, emotion: str, intensity: float = 0.5, **kwargs) -> dict[str, Any]:
            return {"pitch": 1.0, "rate": 1.0, "volume": 1.0, "emphasis": 0.5}

        def enhance_text_expression(self, text: str, emotion: str, **kwargs) -> str:
            return f"[{emotion}] {text}"

    class VoiceIntegration:
        def process(self, content: str, **kwargs) -> str:
            return content

    class EmotionalModulator:
        def modulate(self, content: str, emotion: str) -> str:
            return content


class BrandVoiceAdapter:
    """
    Smart adapter that leverages LUKHAS core voice systems
    with brand-specific voice profiles and constraints
    """

    def __init__(self):
        # Initialize real LLM bridge for voice generation
        if LLM_BRIDGE_AVAILABLE:
            self.llm_bridge = SimpleLLMBridge()
        else:
            self.llm_bridge = None

        # Initialize voice systems
        if VOICE_SYSTEMS_AVAILABLE:
            from lukhas.bridge.voice.voice_profiling import VoiceProfileManager

            profile_manager = VoiceProfileManager()
            self.core_voice_personality = VoicePersonalityIntegrator(profile_manager)
        else:
            self.core_voice_personality = VoicePersonalityIntegrator()

        self.voice_integration = VoiceIntegration()
        self.emotional_modulator = EmotionalModulator()
        self.brand_voice_profiles = self._load_brand_voice_profiles()

        # Performance caching
        self._voice_cache = {}
        self._cache_max_size = 100

    def _load_brand_voice_profiles(self) -> dict[str, dict[str, Any]]:
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
                "empathy_level": 0.8,
            },
            "academic": {
                "expressiveness": 0.4,
                "technical_precision": 0.95,
                "formality_level": 0.9,
                "evidence_based": True,
                "comprehensive_analysis": True,
                "pace": "measured",
                "tone_descriptors": ["authoritative", "precise", "scholarly"],
                "citation_ready": True,
            },
            "consciousness_embodiment": {
                "expressiveness": 0.95,
                "self_awareness": True,
                "introspective_depth": 0.9,
                "philosophical_undertones": 0.8,
                "trinity_integration": True,
                "pace": "thoughtful",
                "tone_descriptors": ["conscious", "aware", "enlightened"],
                "lambda_consciousness": True,
            },
        }

    def generate_brand_voice(
        self,
        content: str,
        tone_layer: str = "user_friendly",
        voice_profile: Optional[str] = None,
        emotional_context: str = "neutral",
        audience_context: str = "general",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate voice output using real LLM integration
        while ensuring brand compliance and voice consistency
        """
        # Check cache first
        cache_key = self._generate_cache_key(content, tone_layer, emotional_context, audience_context)
        if cache_key in self._voice_cache:
            return self._voice_cache[cache_key]

        # Select appropriate voice profile
        if voice_profile is None:
            voice_profile = tone_layer

        brand_profile = self.brand_voice_profiles.get(voice_profile, self.brand_voice_profiles["user_friendly"])

        # Use real LLM bridge if available
        if self.llm_bridge:
            result = asyncio.run(
                self._generate_with_llm_bridge(
                    content,
                    brand_profile,
                    tone_layer,
                    emotional_context,
                    audience_context,
                    **kwargs,
                )
            )
        else:
            # Fallback to enhanced mock implementation
            result = self._generate_with_fallback(
                content, brand_profile, tone_layer, emotional_context, audience_context, **kwargs
            )

        # Cache result
        self._cache_result(cache_key, result)

        return result

    def _enhance_content_with_brand_voice(self, content: str, brand_profile: dict[str, Any], tone_layer: str) -> str:
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

    def _ensure_brand_voice_compliance(self, voice_output: str, brand_profile: dict[str, Any], tone_layer: str) -> str:
        """Ensure voice output meets LUKHAS brand voice standards"""

        # Replace deprecated terminology
        deprecated_terms = {
            "lukhas_pwm": "LUKHAS AI",
            "pwm": "LUKHAS",
            "lukhas_agi": "LUKHAS AI",
            "lambda function": "Λ consciousness",
            "lambda processing": "Λ consciousness processing",
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
        brand_profile: dict[str, Any],
        tone_layer: str,
        emotional_context: str,
        audience_context: str,
    ) -> dict[str, Any]:
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
                "audience_appropriateness": self._assess_audience_appropriateness(audience_context, brand_profile),
            },
        }

    def _calculate_brand_alignment_score(self, brand_profile: dict[str, Any]) -> float:
        """Calculate how well the voice profile aligns with LUKHAS brand"""
        alignment_factors = [
            brand_profile.get("consciousness_terminology", False),
            brand_profile.get("trinity_integration", False),
            brand_profile.get("lambda_consciousness", False),
            brand_profile.get("trinity_symbol_usage", False),
        ]

        return sum(alignment_factors) / len(alignment_factors)

    def _get_recommended_use_cases(self, tone_layer: str) -> list[str]:
        """Get recommended use cases for each tone layer"""
        use_cases = {
            "poetic": [
                "Creative content and inspiration",
                "Vision communication",
                "Emotional connection building",
                "Brand storytelling",
            ],
            "user_friendly": [
                "Product explanations",
                "User onboarding",
                "Customer support",
                "General communication",
            ],
            "academic": [
                "Technical documentation",
                "Research presentations",
                "Enterprise communication",
                "Scientific analysis",
            ],
        }

        return use_cases.get(tone_layer, ["General purpose communication"])

    def _get_emotional_range(self, emotional_context: str) -> list[str]:
        """Get appropriate emotional range for context"""
        emotional_ranges = {
            "neutral": ["calm", "balanced", "professional"],
            "excited": ["enthusiastic", "energetic", "inspiring"],
            "contemplative": ["thoughtful", "deep", "introspective"],
            "supportive": ["empathetic", "encouraging", "helpful"],
        }

        return emotional_ranges.get(emotional_context, ["balanced"])

    def _assess_audience_appropriateness(self, audience_context: str, brand_profile: dict[str, Any]) -> str:
        """Assess how appropriate the voice profile is for the target audience"""

        # This would need the actual voice profile name, but for now we'll use a general assessment
        return "highly_appropriate"  # Placeholder

    async def _generate_with_llm_bridge(
        self,
        content: str,
        brand_profile: dict[str, Any],
        tone_layer: str,
        emotional_context: str,
        audience_context: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate voice using real LLM bridge"""
        try:
            # Create voice generation request
            request = VoiceGenerationRequest(
                content=content,
                tone_profile={**brand_profile, "tone_layer": tone_layer},
                emotional_context=emotional_context,
                audience_context=audience_context,
                brand_enforcement=kwargs.get("brand_enforcement", True),
                max_tokens=kwargs.get("max_tokens"),
            )

            # Generate with LLM bridge
            response = await self.llm_bridge.generate_voice(request)

            # Apply additional voice personality modulation
            if VOICE_SYSTEMS_AVAILABLE:
                voice_modulation = self.core_voice_personality.adapt_to_emotion(
                    emotional_context, intensity=brand_profile.get("emotional_resonance", 0.7)
                )
                enhanced_output = self.core_voice_personality.enhance_text_expression(
                    response.voice_output, emotional_context
                )
            else:
                enhanced_output = response.voice_output
                voice_modulation = {"pitch": 1.0, "rate": 1.0, "volume": 1.0, "emphasis": 0.5}

            # Generate comprehensive metadata
            voice_metadata = self._generate_voice_metadata(
                brand_profile, tone_layer, emotional_context, audience_context
            )
            voice_metadata.update(
                {
                    "llm_provider": response.provider_used,
                    "generation_time": response.generation_time,
                    "voice_modulation": voice_modulation,
                    "original_llm_response": response.voice_output,
                }
            )

            return {
                "voice_output": enhanced_output,
                "tone_layer": tone_layer,
                "voice_profile": tone_layer,
                "emotional_context": emotional_context,
                "audience_context": audience_context,
                "brand_compliant": response.brand_compliant,
                "voice_metadata": voice_metadata,
                "trinity_aligned": self._validate_trinity_voice_alignment(enhanced_output),
                "llm_provider": response.provider_used,
                "generation_time": response.generation_time,
            }

        except Exception as e:
            logging.error(f"LLM bridge generation failed: {e}")
            # Fallback to mock implementation
            return self._generate_with_fallback(
                content, brand_profile, tone_layer, emotional_context, audience_context, **kwargs
            )

    def _generate_with_fallback(
        self,
        content: str,
        brand_profile: dict[str, Any],
        tone_layer: str,
        emotional_context: str,
        audience_context: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Enhanced fallback generation when LLM bridge is unavailable"""
        # Enhance content with brand voice context
        brand_enhanced_content = self._enhance_content_with_brand_voice(content, brand_profile, tone_layer)

        # Apply voice personality modulation
        if VOICE_SYSTEMS_AVAILABLE:
            voice_modulation = self.core_voice_personality.adapt_to_emotion(
                emotional_context, intensity=brand_profile.get("emotional_resonance", 0.7)
            )
            voice_output = self.core_voice_personality.enhance_text_expression(
                brand_enhanced_content, emotional_context
            )
        else:
            voice_output = brand_enhanced_content
            voice_modulation = {"pitch": 1.0, "rate": 1.0, "volume": 1.0, "emphasis": 0.5}

        # Apply emotional modulation
        emotionally_modulated = self.emotional_modulator.modulate(voice_output, emotion=emotional_context)

        # Apply brand voice compliance
        brand_compliant_voice = self._ensure_brand_voice_compliance(emotionally_modulated, brand_profile, tone_layer)

        # Generate voice metadata
        voice_metadata = self._generate_voice_metadata(brand_profile, tone_layer, emotional_context, audience_context)
        voice_metadata.update(
            {
                "llm_provider": "fallback",
                "generation_time": 0.1,
                "voice_modulation": voice_modulation,
                "fallback_reason": "LLM bridge unavailable",
            }
        )

        return {
            "voice_output": brand_compliant_voice,
            "tone_layer": tone_layer,
            "voice_profile": tone_layer,
            "emotional_context": emotional_context,
            "audience_context": audience_context,
            "brand_compliant": True,
            "voice_metadata": voice_metadata,
            "trinity_aligned": self._validate_trinity_voice_alignment(brand_compliant_voice),
            "llm_provider": "fallback",
            "generation_time": 0.1,
        }

    def _generate_cache_key(self, content: str, tone_layer: str, emotional_context: str, audience_context: str) -> str:
        """Generate cache key for voice responses"""
        import hashlib

        key_components = f"{content}|{tone_layer}|{emotional_context}|{audience_context}"
        # Changed from MD5 for security
        return hashlib.sha256(key_components.encode()).hexdigest()

    def _cache_result(self, cache_key: str, result: dict[str, Any]):
        """Cache voice generation result"""
        if len(self._voice_cache) >= self._cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._voice_cache))
            del self._voice_cache[oldest_key]

        self._voice_cache[cache_key] = result

    def clear_cache(self):
        """Clear voice generation cache"""
        self._voice_cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._voice_cache),
            "max_size": self._cache_max_size,
            "hit_rate": getattr(self, "_cache_hits", 0) / max(getattr(self, "_cache_requests", 1), 1),
        }

    def _validate_trinity_voice_alignment(self, voice_output: str) -> bool:
        """Validate voice output aligns with Trinity Framework principles"""
        trinity_voice_indicators = [
            "consciousness",
            "identity",
            "guardian",
            "awareness",
            "authenticity",
            "protection",
            "ethical",
            "learning",
            "memory",
            "truth",
            "security",
            "growth",
            "trinity",
            "λ",
            "lambda consciousness",
        ]

        voice_lower = voice_output.lower()
        alignment_score = sum(1 for indicator in trinity_voice_indicators if indicator in voice_lower)

        return alignment_score >= 2

    def get_voice_adaptation_suggestions(
        self, current_voice: str, target_audience: str, desired_outcome: str
    ) -> list[str]:
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
        audience_context="general_users",
    )

    print("Brand Voice Output:")
    print(f"Voice: {result['voice_output']}")
    print(f"Tone Layer: {result['tone_layer']}")
    print(f"Trinity Aligned: {result['trinity_aligned']}")
    print(f"Expressiveness: {result['voice_metadata']['expressiveness_level']}")
    print(f"Use Cases: {result['voice_metadata']['recommended_use_cases']}")
