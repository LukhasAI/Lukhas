"""
Voice Module Symbolic Vocabulary

This module defines the symbolic vocabulary for the LUKHAS Voice Module,
providing the symbolic language elements used for voice synthesis,
emotional expression, and vocal communication.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from ..core import VoiceEmotion, VoiceProvider


@dataclass
class Voicesymbol:
    """Represents a voice-related symbolic element."""

    symbol: str
    meaning: str
    emotional_weight: float
    vocal_properties: Dict[str, Any]
    usage_contexts: List[str]


class Voicesymbolicvocabulary:
    """Symbolic vocabulary for voice synthesis and expression."""

    def __init__(self):
        self.synthesis_symbols = self._init_synthesis_symbols()
        self.emotion_symbols = self._init_emotion_symbols()
        self.provider_symbols = self._init_provider_symbols()
        self.quality_symbols = self._init_quality_symbols()
        self.expression_symbols = self._init_expression_symbols()

    def _init_synthesis_symbols(self) -> Dict[str, VoiceSymbol]:
        """Initialize voice synthesis symbolic elements."""
        return {
            "🎤": VoiceSymbol(
                symbol="🎤",
                meaning="Voice synthesis initiation",
                emotional_weight=0.0,
                vocal_properties={"activation": True, "clarity": "high"},
                usage_contexts=["synthesis_start", "recording", "vocal_activation"],
            ),
            "🗣️": VoiceSymbol(
                symbol="🗣️",
                meaning="Active speech generation",
                emotional_weight=0.2,
                vocal_properties={"articulation": "clear", "pace": "normal"},
                usage_contexts=["speaking", "narration", "communication"],
            ),
            "🎵": VoiceSymbol(
                symbol="🎵",
                meaning="Melodic vocal expression",
                emotional_weight=0.6,
                vocal_properties={"melody": "present", "rhythm": "flowing"},
                usage_contexts=["singing", "musical_speech", "emotional_expression"],
            ),
            "📢": VoiceSymbol(
                symbol="📢",
                meaning="Amplified vocal communication",
                emotional_weight=0.4,
                vocal_properties={"volume": "high", "projection": "strong"},
                usage_contexts=["announcements", "emphasis", "public_speaking"],
            ),
            "🔇": VoiceSymbol(
                symbol="🔇",
                meaning="Voice synthesis disabled",
                emotional_weight=-0.1,
                vocal_properties={"silence": True, "muted": True},
                usage_contexts=["muting", "pause", "silence"],
            ),
            "🎙️": VoiceSymbol(
                symbol="🎙️",
                meaning="Professional voice recording",
                emotional_weight=0.1,
                vocal_properties={"quality": "studio", "clarity": "pristine"},
                usage_contexts=["recording", "broadcast", "professional"],
            ),
        }

    def _init_emotion_symbols(self) -> Dict[str, VoiceSymbol]:
        """Initialize emotional voice symbolic elements."""
        return {
            "😊": VoiceSymbol(
                symbol="😊",
                meaning="Joyful vocal expression",
                emotional_weight=0.8,
                vocal_properties={
                    "tone": "bright",
                    "pitch": "elevated",
                    "warmth": "high",
                },
                usage_contexts=["happiness", "celebration", "positive_news"],
            ),
            "😢": VoiceSymbol(
                symbol="😢",
                meaning="Sorrowful vocal expression",
                emotional_weight=-0.6,
                vocal_properties={
                    "tone": "somber",
                    "pitch": "lowered",
                    "tremor": "slight",
                },
                usage_contexts=["sadness", "grief", "empathy"],
            ),
            "😡": VoiceSymbol(
                symbol="😡",
                meaning="Angry vocal expression",
                emotional_weight=-0.7,
                vocal_properties={
                    "intensity": "high",
                    "sharpness": "pronounced",
                    "speed": "rapid",
                },
                usage_contexts=["anger", "frustration", "confrontation"],
            ),
            "😴": VoiceSymbol(
                symbol="😴",
                meaning="Calm, sleepy vocal expression",
                emotional_weight=-0.2,
                vocal_properties={
                    "pace": "slow",
                    "softness": "high",
                    "rhythm": "gentle",
                },
                usage_contexts=["relaxation", "bedtime", "meditation"],
            ),
            "🤖": VoiceSymbol(
                symbol="🤖",
                meaning="Neutral, robotic vocal expression",
                emotional_weight=0.0,
                vocal_properties={
                    "monotone": True,
                    "precision": "high",
                    "emotion": "minimal",
                },
                usage_contexts=["technical", "formal", "system_messages"],
            ),
            "💫": VoiceSymbol(
                symbol="💫",
                meaning="Dreamy, ethereal vocal expression",
                emotional_weight=0.3,
                vocal_properties={
                    "reverb": "slight",
                    "softness": "high",
                    "mystery": "present",
                },
                usage_contexts=["dreams", "fantasy", "mystical"],
            ),
            "❤️": VoiceSymbol(
                symbol="❤️",
                meaning="Loving, warm vocal expression",
                emotional_weight=0.9,
                vocal_properties={
                    "warmth": "maximum",
                    "gentleness": "high",
                    "intimacy": "present",
                },
                usage_contexts=["love", "care", "intimacy"],
            ),
            "⚡": VoiceSymbol(
                symbol="⚡",
                meaning="Excited, energetic vocal expression",
                emotional_weight=0.7,
                vocal_properties={
                    "energy": "high",
                    "speed": "fast",
                    "dynamism": "pronounced",
                },
                usage_contexts=["excitement", "energy", "motivation"],
            ),
        }

    def _init_provider_symbols(self) -> Dict[str, VoiceSymbol]:
        """Initialize voice provider symbolic elements."""
        return {
            "🎭": VoiceSymbol(
                symbol="🎭",
                meaning="ElevenLabs professional voice",
                emotional_weight=0.3,
                vocal_properties={
                    "quality": "premium",
                    "realism": "high",
                    "flexibility": "maximum",
                },
                usage_contexts=["professional", "high_quality", "character_voices"],
            ),
            "🌐": VoiceSymbol(
                symbol="🌐",
                meaning="Edge TTS system voice",
                emotional_weight=0.1,
                vocal_properties={
                    "reliability": "high",
                    "availability": "universal",
                    "latency": "low",
                },
                usage_contexts=["system", "fallback", "reliable"],
            ),
            "🧠": VoiceSymbol(
                symbol="🧠",
                meaning="OpenAI voice synthesis",
                emotional_weight=0.2,
                vocal_properties={
                    "intelligence": "high",
                    "naturalness": "good",
                    "consistency": "stable",
                },
                usage_contexts=["ai_generated", "conversational", "intelligent"],
            ),
            "🔧": VoiceSymbol(
                symbol="🔧",
                meaning="Mock voice for testing",
                emotional_weight=0.0,
                vocal_properties={
                    "testing": True,
                    "simulation": True,
                    "development": True,
                },
                usage_contexts=["testing", "development", "debugging"],
            ),
        }

    def _init_quality_symbols(self) -> Dict[str, VoiceSymbol]:
        """Initialize voice quality symbolic elements."""
        return {
            "💎": VoiceSymbol(
                symbol="💎",
                meaning="Premium voice quality",
                emotional_weight=0.4,
                vocal_properties={
                    "clarity": "crystal",
                    "depth": "rich",
                    "fidelity": "maximum",
                },
                usage_contexts=["premium", "high_fidelity", "professional"],
            ),
            "⚡": VoiceSymbol(
                symbol="⚡",
                meaning="Fast synthesis speed",
                emotional_weight=0.2,
                vocal_properties={
                    "latency": "minimal",
                    "responsiveness": "instant",
                    "efficiency": "high",
                },
                usage_contexts=["real_time", "interactive", "responsive"],
            ),
            "🎯": VoiceSymbol(
                symbol="🎯",
                meaning="Precise articulation",
                emotional_weight=0.1,
                vocal_properties={
                    "precision": "exact",
                    "clarity": "perfect",
                    "accuracy": "high",
                },
                usage_contexts=["technical", "precise", "clear"],
            ),
            "🌊": VoiceSymbol(
                symbol="🌊",
                meaning="Flowing, natural speech",
                emotional_weight=0.3,
                vocal_properties={
                    "fluency": "natural",
                    "rhythm": "organic",
                    "flow": "seamless",
                },
                usage_contexts=["natural", "conversational", "flowing"],
            ),
        }

    def _init_expression_symbols(self) -> Dict[str, VoiceSymbol]:
        """Initialize vocal expression symbolic elements."""
        return {
            "📚": VoiceSymbol(
                symbol="📚",
                meaning="Educational, instructional voice",
                emotional_weight=0.1,
                vocal_properties={
                    "clarity": "educational",
                    "pace": "measured",
                    "authority": "gentle",
                },
                usage_contexts=["teaching", "explanation", "instruction"],
            ),
            "🎭": VoiceSymbol(
                symbol="🎭",
                meaning="Dramatic, theatrical expression",
                emotional_weight=0.6,
                vocal_properties={
                    "drama": "high",
                    "expression": "theatrical",
                    "range": "wide",
                },
                usage_contexts=["storytelling", "drama", "performance"],
            ),
            "🌟": VoiceSymbol(
                symbol="🌟",
                meaning="Inspiring, motivational voice",
                emotional_weight=0.7,
                vocal_properties={
                    "inspiration": "high",
                    "energy": "positive",
                    "uplift": "strong",
                },
                usage_contexts=["motivation", "inspiration", "encouragement"],
            ),
            "🧘": VoiceSymbol(
                symbol="🧘",
                meaning="Meditative, calming voice",
                emotional_weight=-0.1,
                vocal_properties={
                    "tranquility": "high",
                    "pace": "slow",
                    "soothing": "maximum",
                },
                usage_contexts=["meditation", "relaxation", "calm"],
            ),
            "🎪": VoiceSymbol(
                symbol="🎪",
                meaning="Playful, entertaining voice",
                emotional_weight=0.5,
                vocal_properties={
                    "playfulness": "high",
                    "variation": "dynamic",
                    "fun": "maximum",
                },
                usage_contexts=["entertainment", "games", "fun"],
            ),
        }

    def get_symbol_for_emotion(self, emotion: VoiceEmotion) -> str:
        """Get the appropriate symbol for a voice emotion."""
        emotion_map = {
            VoiceEmotion.HAPPY: "😊",
            VoiceEmotion.SAD: "😢",
            VoiceEmotion.ANGRY: "😡",
            VoiceEmotion.EXCITED: "⚡",
            VoiceEmotion.CALM: "😴",
            VoiceEmotion.ANXIOUS: "😰",
            VoiceEmotion.CONFIDENT: "🌟",
            VoiceEmotion.NEUTRAL: "🤖",
        }
        return emotion_map.get(emotion, "🗣️")

    def get_symbol_for_provider(self, provider: VoiceProvider) -> str:
        """Get the appropriate symbol for a voice provider."""
        provider_map = {
            VoiceProvider.ELEVENLABS: "🎭",
            VoiceProvider.EDGE_TTS: "🌐",
            VoiceProvider.OPENAI: "🧠",
            VoiceProvider.MOCK: "🔧",
        }
        return provider_map.get(provider, "🎤")

    def create_synthesis_phrase(
        self, emotion: VoiceEmotion, provider: VoiceProvider, text: str
    ) -> str:
        """Create a symbolic phrase for voice synthesis."""
        emotion_symbol = self.get_symbol_for_emotion(emotion)
        provider_symbol = self.get_symbol_for_provider(provider)

        return f"{emotion_symbol} {provider_symbol} 🎤 {text[:30]}{'...' if len(text) > 30 else ''}"

    def get_quality_indicators(self, success: bool, processing_time: float) -> str:
        """Get quality indicator symbols based on synthesis results."""
        symbols = []

        if success:
            symbols.append("✅")
        else:
            symbols.append("❌")

        if processing_time < 1.0:
            symbols.append("⚡")  # Fast
        elif processing_time < 3.0:
            symbols.append("🎯")  # Normal
        else:
            symbols.append("🐌")  # Slow

        return " ".join(symbols)

    def get_all_symbols(self) -> Dict[str, VoiceSymbol]:
        """Get all voice symbolic elements."""
        all_symbols = {}
        all_symbols.update(self.synthesis_symbols)
        all_symbols.update(self.emotion_symbols)
        all_symbols.update(self.provider_symbols)
        all_symbols.update(self.quality_symbols)
        all_symbols.update(self.expression_symbols)
        return all_symbols

    def get_context_symbols(self, context: str) -> List[str]:
        """Get symbols relevant to a specific context."""
        relevant_symbols = []
        all_symbols = self.get_all_symbols()

        for symbol, data in all_symbols.items():
            if context in data.usage_contexts:
                relevant_symbols.append(symbol)

        return relevant_symbols

    def analyze_emotional_weight(self, text: str) -> float:
        """Analyze the emotional weight of text based on contained symbols."""
        total_weight = 0.0
        symbol_count = 0
        all_symbols = self.get_all_symbols()

        for symbol in text:
            if symbol in all_symbols:
                total_weight += all_symbols[symbol].emotional_weight
                symbol_count += 1

        return total_weight / symbol_count if symbol_count > 0 else 0.0


# Global vocabulary instance
voice_vocabulary = VoiceSymbolicVocabulary()


# Export main classes
__all__ = ["VoiceSymbol", "VoiceSymbolicVocabulary", "voice_vocabulary"]
