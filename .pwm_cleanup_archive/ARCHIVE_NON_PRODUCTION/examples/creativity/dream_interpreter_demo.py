#!/usr/bin/env python3
"""
Dream Interpreter - Core Logic Demo
A simplified version focusing on the core logic without external dependencies
"""

import json
import locale
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DreamSymbol:
    symbol: str
    meaning: str


@dataclass
class DreamInterpretation:
    main_themes: List[str]
    emotional_tone: str
    symbols: List[DreamSymbol]
    personal_insight: str
    guidance: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "main_themes": self.main_themes,
            "emotional_tone": self.emotional_tone,
            "symbols": [
                {"symbol": s.symbol, "meaning": s.meaning} for s in self.symbols
            ],
            "personal_insight": self.personal_insight,
            "guidance": self.guidance,
        }


@dataclass
class DreamEntry:
    """Represents a dream entry with metadata"""

    id: str
    dream_text: str
    interpretation: Optional[DreamInterpretation]
    timestamp: datetime
    locale: str
    llm_provider: str


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""

    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7


@dataclass
class MediaInput:
    """Represents multimedia input for dream enhancement"""

    type: str  # 'audio', 'image', 'text', 'url', 'emoji'
    content: str  # base64 for audio/image, text for others
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VoiceInput:
    """Voice input configuration and processing"""

    audio_data: Optional[str] = None  # base64 encoded
    transcription: Optional[str] = None
    language: str = "en-US"
    confidence: float = 0.0
    processing_time: float = 0.0


@dataclass
class DreamEnrichment:
    """Enhanced dream content with multimedia"""

    original_text: str
    enriched_text: str
    media_inputs: List[MediaInput] = field(default_factory=list)
    emojis_added: List[str] = field(default_factory=list)
    generated_content: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIGeneratedDream:
    """AI-generated dream from multimedia inputs"""

    narrative: str
    dream_themes: List[str]
    generated_media: Dict[str, str] = field(default_factory=dict)
    inspiration_sources: List[str] = field(default_factory=list)
    creativity_level: float = 0.7


class QuickAccessRecorder:
    """iPhone-style quick access voice recording for dreams"""

    def __init__(self, dream_interpreter: "DreamInterpreter"):
        self.dream_interpreter = dream_interpreter
        self.is_recording = False
        self.current_session = None
        self.auto_enhance = True
        self.wake_up_mode = True

    def quick_dream_capture(self) -> Optional[str]:
        """Complete quick capture workflow for sleepy users"""
        print("\n🌙 Quick Dream Capture Mode")
        print("📝 Type your dream (voice recording simulation):")

        dream_text = input("> ").strip()

        if not dream_text:
            return None

        if self.auto_enhance:
            enhancement = self.dream_interpreter.enrich_dream_text(dream_text)
            return enhancement.enriched_text
        return dream_text


class DreamEnhancer:
    """Advanced dream text enhancement"""

    @staticmethod
    def smart_emoji_enhancement(text: str, context: str = "dream") -> DreamEnrichment:
        """Intelligently add emojis based on dream context"""

        # Simple emoji mapping for demo
        emoji_map = {
            "flying": "🕊️",
            "fly": "✈️",
            "bird": "🐦",
            "sky": "☁️",
            "water": "💧",
            "ocean": "🌊",
            "sea": "🌊",
            "river": "🏞️",
            "fire": "🔥",
            "sun": "☀️",
            "moon": "🌙",
            "star": "⭐",
            "forest": "🌲",
            "tree": "🌳",
            "flower": "🌸",
            "garden": "🌻",
            "house": "🏠",
            "home": "🏡",
            "door": "🚪",
            "window": "🪟",
            "car": "🚗",
            "road": "🛣️",
            "path": "🛤️",
            "bridge": "🌉",
            "animal": "🦋",
            "cat": "🐱",
            "dog": "🐶",
            "fish": "🐠",
            "happy": "😊",
            "sad": "😢",
            "fear": "😨",
            "love": "❤️",
            "dream": "💭",
            "sleep": "😴",
            "wake": "⏰",
            "night": "🌃",
            "dark": "🌑",
            "light": "💡",
            "beautiful": "✨",
            "scary": "👻",
        }

        enriched_text = text
        emojis_added = []

        words = text.lower().split()
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word)
            if clean_word in emoji_map:
                emoji_char = emoji_map[clean_word]
                if emoji_char not in emojis_added:
                    emojis_added.append(emoji_char)
                    # Add emoji after the word
                    enriched_text = enriched_text.replace(
                        word, f"{word} {emoji_char}", 1
                    )

        return DreamEnrichment(
            original_text=text, enriched_text=enriched_text, emojis_added=emojis_added
        )


class MultimediaInputProcessor:
    """Simplified multimedia processing"""

    def process_multiple_inputs(self, inputs: List[Dict[str, Any]]) -> List[MediaInput]:
        """Process multiple multimedia inputs"""
        processed_inputs = []

        for input_data in inputs:
            input_type = input_data.get("type")
            content = input_data.get("content")

            media_input = MediaInput(
                type=input_type,
                content=content,
                metadata={"processed": True, "source": "demo"},
            )
            processed_inputs.append(media_input)

        return processed_inputs


class DreamInterpreter:
    """Enhanced Dream interpreter with multi-language support"""

    TRANSLATIONS = {
        "en-US": {
            "dreamInterpreterTitle": "Dream interpreter",
            "dreamInterpreterSubtitle": "Share your dream, discover its meaning ✨",
            "dreamInputLabel": "Tell me about your dream...",
            "dreamInputPlaceholder": "Describe your dream in as much detail as you can remember... ☁️",
            "interpretingDream": "Interpreting your dream...",
            "interpretDreamButton": "Interpret dream",
            "interpretationError": "Unable to interpret your dream. Please try again.",
            "mainThemesTitle": "Main themes",
            "emotionalAtmosphereTitle": "Emotional atmosphere",
            "dreamSymbolsTitle": "Dream symbols",
            "personalInsightTitle": "Personal insight",
            "guidanceTitle": "Guidance for reflection",
        },
        "es-ES": {
            "dreamInterpreterTitle": "Intérprete de sueños",
            "dreamInterpreterSubtitle": "Comparte tu sueño, descubre su significado ✨",
            "dreamInputLabel": "Cuéntame sobre tu sueño...",
            "dreamInputPlaceholder": "Describe tu sueño con tanto detalle como puedas recordar... ☁️",
            "interpretingDream": "Interpretando tu sueño...",
            "interpretDreamButton": "Interpretar sueño",
            "interpretationError": "No se pudo interpretar tu sueño. Por favor, inténtalo de nuevo.",
            "mainThemesTitle": "Temas principales",
            "emotionalAtmosphereTitle": "Atmósfera emocional",
            "dreamSymbolsTitle": "Símbolos del sueño",
            "personalInsightTitle": "Perspectiva personal",
            "guidanceTitle": "Guía para la reflexión",
        },
    }

    def __init__(
        self, app_locale: Optional[str] = None, llm_config: Optional[LLMConfig] = None
    ):
        """Initialize the dream interpreter"""
        self.app_locale = app_locale
        self.locale = self._determine_locale()
        self.dream_text = ""
        self.interpretation = None
        self.error = None
        self.dream_entries = []

        # Enhanced components
        self.quick_recorder = QuickAccessRecorder(self)
        self.dream_enhancer = DreamEnhancer()
        self.multimedia_input_processor = MultimediaInputProcessor()

        if llm_config:
            self.llm_config = llm_config
        else:
            self.llm_config = None

    def _determine_locale(self) -> str:
        """Determine the appropriate locale to use"""
        if self.app_locale and self.app_locale != "{{APP_LOCALE}}":
            return self._find_matching_locale(self.app_locale)

        try:
            system_locale = locale.getdefaultlocale()[0] or "en-US"
        except:
            system_locale = "en-US"

        return self._find_matching_locale(system_locale)

    def _find_matching_locale(self, target_locale: str) -> str:
        """Find the best matching locale"""
        if target_locale in self.TRANSLATIONS:
            return target_locale

        lang = target_locale.split("-")[0] if "-" in target_locale else target_locale
        for available_locale in self.TRANSLATIONS.keys():
            if available_locale.startswith(lang + "-"):
                return available_locale

        return "en-US"

    def t(self, key: str) -> str:
        """Translate a key to the current locale"""
        return self.TRANSLATIONS.get(self.locale, {}).get(key) or self.TRANSLATIONS[
            "en-US"
        ].get(key, key)

    def set_dream_text(self, dream_text: str) -> None:
        """Set the dream text to be interpreted"""
        self.dream_text = dream_text.strip()

    def enrich_dream_text(
        self, dream_text: str, enhancement_level: str = "moderate"
    ) -> DreamEnrichment:
        """Enrich dream text with emojis and symbols"""
        return self.dream_enhancer.smart_emoji_enhancement(dream_text)

    def parse_interpretation_response(self, response: str) -> DreamInterpretation:
        """Parse the AI response into a DreamInterpretation object"""
        try:
            data = json.loads(response)

            symbols = [
                DreamSymbol(symbol=s["symbol"], meaning=s["meaning"])
                for s in data.get("symbols", [])
            ]

            return DreamInterpretation(
                main_themes=data.get("mainThemes", []),
                emotional_tone=data.get("emotionalTone", ""),
                symbols=symbols,
                personal_insight=data.get("personalInsight", ""),
                guidance=data.get("guidance", ""),
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid interpretation response: {e}")

    def interpret_dream_with_ai(
        self, ai_complete_function
    ) -> Optional[DreamInterpretation]:
        """Interpret the dream using an AI completion function"""
        if not self.dream_text:
            self.error = "No dream text provided"
            return None

        try:
            self.error = None
            print(f"🌙 {self.t('interpretingDream')}")

            # Create a simple prompt for demo
            prompt = f"Interpret this dream: {self.dream_text}"
            response = ai_complete_function(prompt)

            self.interpretation = self.parse_interpretation_response(response)

            # Save dream entry
            dream_id = str(uuid.uuid4())
            entry = DreamEntry(
                id=dream_id,
                dream_text=self.dream_text,
                interpretation=self.interpretation,
                timestamp=datetime.now(),
                locale=self.locale,
                llm_provider=self.llm_config.provider if self.llm_config else "mock",
            )
            self.dream_entries.append(entry)

            return self.interpretation

        except Exception as e:
            self.error = self.t("interpretationError")
            print(f"Error interpreting dream: {e}")
            return None

    def display_interpretation(self) -> None:
        """Display the dream interpretation"""
        if not self.interpretation:
            if self.error:
                print(f"❌ {self.error}")
            else:
                print("No interpretation available")
            return

        print(f"\n✨ {self.t('dreamInterpreterTitle')}")
        print("=" * 50)

        print(f"\n🎯 {self.t('mainThemesTitle')}:")
        for theme in self.interpretation.main_themes:
            print(f"  • {theme}")

        print(f"\n💭 {self.t('emotionalAtmosphereTitle')}:")
        print(f"  {self.interpretation.emotional_tone}")

        print(f"\n🔮 {self.t('dreamSymbolsTitle')}:")
        for symbol in self.interpretation.symbols:
            print(f"  • {symbol.symbol}: {symbol.meaning}")

        print(f"\n🌟 {self.t('personalInsightTitle')}:")
        print(f"  {self.interpretation.personal_insight}")

        print(f"\n🧭 {self.t('guidanceTitle')}:")
        print(f"  {self.interpretation.guidance}")

        print("\n" + "=" * 50)

    def get_dream_history(self) -> List[DreamEntry]:
        """Get all saved dream entries"""
        return self.dream_entries


def mock_ai_complete(prompt: str) -> str:
    """Mock AI completion function for testing"""
    return json.dumps(
        {
            "mainThemes": ["Transformation", "Adventure", "Growth"],
            "emotionalTone": "The dream carries a sense of excitement mixed with anticipation, suggesting you're ready for positive changes in your life.",
            "symbols": [
                {
                    "symbol": "Flying",
                    "meaning": "Freedom and liberation from constraints",
                },
                {"symbol": "Water", "meaning": "Emotional cleansing and renewal"},
            ],
            "personalInsight": "This dream suggests you're entering a period of personal transformation where you're ready to embrace new possibilities and break free from limiting beliefs.",
            "guidance": "Trust in your ability to navigate change. Consider what areas of your life are calling for growth and be open to new opportunities.",
        }
    )


def mock_generate_ai_dream(media_inputs: List[MediaInput]) -> AIGeneratedDream:
    """Mock AI dream generation for testing"""
    themes = []
    narrative_parts = []

    for media in media_inputs:
        if media.type == "text":
            narrative_parts.append(
                f"Elements from your thoughts: {media.content[:50]}..."
            )
            themes.append("personal_reflection")
        elif media.type == "emoji_sequence":
            themes.append("symbolic_imagery")
            narrative_parts.append("Symbolic imagery dances through the dreamscape...")
        elif media.type == "voice_note":
            themes.append("emotional_resonance")
            narrative_parts.append("Echoes of spoken words weave through the dream...")
        elif media.type == "url":
            themes.append("external_inspiration")
            narrative_parts.append(
                "Knowledge from the world beyond merges with your subconscious..."
            )

    narrative = f"""
In the twilight realm between sleep and waking, your dream unfolds like a tapestry woven from multiple threads of experience...

{' '.join(narrative_parts)}

The dream shifts and transforms, carrying you through landscapes both familiar and strange, where {', '.join(set(themes))} blend into a meaningful narrative that speaks to your deepest self.

As you move through this ethereal world, each element—every image, sound, and emotion—contributes to a greater understanding of your inner journey.
    """

    return AIGeneratedDream(
        narrative=narrative.strip(),
        dream_themes=list(set(themes))
        or ["transformation", "creativity", "integration"],
        inspiration_sources=[media.type for media in media_inputs],
        creativity_level=0.85,
    )


def main():
    """Enhanced main function demonstrating all features"""
    print("🌙 Dream Interpreter - Enhanced Edition (Demo)")
    print("=" * 50)

    interpreter = DreamInterpreter()

    while True:
        print(f"\n{interpreter.t('dreamInterpreterSubtitle')}")
        print("\nChoose an option:")
        print("1. 🎙️  Quick voice dream capture (simulation)")
        print("2. 📝  Type your dream")
        print("3. 🎨  Create AI dream from multimedia")
        print("4. 📚  View dream history")
        print("5. ⚙️  Test emoji enhancement")
        print("6. 🚪  Exit")

        choice = input("\nSelect (1-6): ").strip()

        if choice == "1":
            # Quick voice capture simulation
            dream_text = interpreter.quick_recorder.quick_dream_capture()
            if dream_text:
                interpreter.set_dream_text(dream_text)
                print(f"\n✨ Enhanced dream text:\n{dream_text}")

                interpretation = interpreter.interpret_dream_with_ai(mock_ai_complete)
                if interpretation:
                    interpreter.display_interpretation()

        elif choice == "2":
            # Manual text input
            print(f"\n{interpreter.t('dreamInputLabel')}")
            dream_text = input("> ").strip()

            if dream_text:
                enhancement = interpreter.dream_enhancer.smart_emoji_enhancement(
                    dream_text
                )
                print(f"\n✨ Enhanced with emojis: {enhancement.enriched_text}")

                interpreter.set_dream_text(enhancement.enriched_text)
                interpretation = interpreter.interpret_dream_with_ai(mock_ai_complete)

                if interpretation:
                    interpreter.display_interpretation()

        elif choice == "3":
            # AI dream generation simulation
            print("\n🎨 AI Dream Generation (Demo)")
            print("Simulating multimedia inputs...")

            media_inputs = [
                {"type": "text", "content": "I saw a beautiful sunset over mountains"},
                {"type": "emoji_sequence", "content": "🌅⛰️🦋✨🌙"},
                {"type": "voice_note", "content": "peaceful nature sounds"},
                {"type": "url", "content": "https://example.com/nature-article"},
            ]

            processed_inputs = (
                interpreter.multimedia_input_processor.process_multiple_inputs(
                    media_inputs
                )
            )

            print(f"📝 Processed {len(processed_inputs)} inputs:")
            for i, media_input in enumerate(processed_inputs, 1):
                print(f"  {i}. {media_input.type}: {media_input.content[:50]}...")

            ai_dream = mock_generate_ai_dream(processed_inputs)
            print(f"\n🌟 AI Generated Dream:\n{ai_dream.narrative}")
            print(f"\n🎯 Themes: {', '.join(ai_dream.dream_themes)}")

        elif choice == "4":
            # Dream history
            history = interpreter.get_dream_history()
            if history:
                print(f"\n📚 Dream History ({len(history)} entries):")
                for i, entry in enumerate(history[-5:], 1):
                    print(
                        f"  {i}. {entry.timestamp.strftime('%Y-%m-%d %H:%M')} - {entry.dream_text[:50]}..."
                    )
            else:
                print("\n📚 No dream history yet")

        elif choice == "5":
            # Test emoji enhancement
            print("\n🧪 Testing Emoji Enhancement")
            test_text = "I was flying through a dark forest and saw a mysterious glowing door with water flowing underneath"

            enhancement = interpreter.dream_enhancer.smart_emoji_enhancement(test_text)
            print(f"📝 Original: {test_text}")
            print(f"✨ Enhanced: {enhancement.enriched_text}")
            print(f"😊 Emojis added: {', '.join(enhancement.emojis_added)}")

        elif choice == "6":
            print("🌙 Sweet dreams! ✨")
            break

        else:
            print("❌ Invalid choice, please try again")


if __name__ == "__main__":
    main()
