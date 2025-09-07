#!/usr/bin/env python3
"""
LUKHΛS Multilingual Glyph Engine
Cross-cultural symbolic translation system
Trinity Framework: ⚛️🧠🛡️
"""
from typing import List
import streamlit as st

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CulturalGlyph:
    """Represents a glyph with cultural context"""

    universal: str  # Universal Unicode glyph
    meaning: str  # Core meaning
    cultural_variants: dict[str, str]  # Locale-specific variants
    context: str  # Usage context
    weight: float  # Semantic weight (0.0-1.0)
    trinity_mapping: Optional[str] = None  # Maps to ⚛️, 🧠, or 🛡️


class MultilingualGlyphEngine:
    """
    Translates symbolic glyphs across cultures and languages,
    maintaining semantic meaning while respecting cultural contexts.
    """

    def __init__(self, glyph_map_path: str = "glyph_translation_map.json"):
        """
        Initialize the multilingual engine.

        Args:
            glyph_map_path: Path to glyph translation mappings
        """
        self.glyph_map_path = Path(glyph_map_path)
        self.supported_locales = [
            "en",
            "es",
            "fr",
            "de",
            "zh",
            "ja",
            "pt",
            "ar",
            "hi",
            "ru",
        ]
        self.glyph_database = {}
        self.cultural_mappings = {}

        # Trinity core mappings
        self.trinity_core = {
            "⚛️": "quantum/potential",
            "🧠": "consciousness/wisdom",
            "🛡️": "protection/ethics",
        }

        # Initialize database
        self._initialize_glyph_database()

        # Load or create translation map
        self._load_or_create_map()

        logger.info("🌍 Multilingual Glyph Engine initialized")
        logger.info(f"   Supported locales: {', '.join(self.supported_locales}")
        logger.info(f"   Glyphs loaded: {len(self.glyph_database}")

    def _initialize_glyph_database(self):
        """Initialize the core glyph database with cultural variants"""

        # Wisdom/Consciousness glyphs
        self.glyph_database["wisdom"] = [
            CulturalGlyph(
                universal="🧠",
                meaning="consciousness/wisdom",
                cultural_variants={
                    "en": "🧠",
                    "es": "🧠",
                    "fr": "🧠",
                    "de": "🧠",
                    "zh": "智",
                    "ja": "知",
                    "pt": "🧠",
                    "ar": "حكمة",
                    "hi": "ज्ञान",
                    "ru": "мудрость",
                },
                context="intellectual/spiritual wisdom",
                weight=1.0,
                trinity_mapping="🧠",
            ),
            CulturalGlyph(
                universal="📚",
                meaning="knowledge/learning",
                cultural_variants={
                    "en": "📚",
                    "es": "📚",
                    "fr": "📚",
                    "de": "📚",
                    "zh": "書",
                    "ja": "本",
                    "pt": "📚",
                    "ar": "كتب",
                    "hi": "पुस्तक",
                    "ru": "книги",
                },
                context="education/study",
                weight=0.8,
                trinity_mapping="🧠",
            ),
            CulturalGlyph(
                universal="🧘",
                meaning="meditation/mindfulness",
                cultural_variants={
                    "en": "🧘",
                    "es": "🧘",
                    "fr": "🧘",
                    "de": "🧘",
                    "zh": "禅",
                    "ja": "瞑想",
                    "pt": "🧘",
                    "ar": "تأمل",
                    "hi": "ध्यान",
                    "ru": "медитация",
                },
                context="spiritual practice",
                weight=0.9,
                trinity_mapping="🧠",
            ),
        ]

        # Protection/Ethics glyphs
        self.glyph_database["protection"] = [
            CulturalGlyph(
                universal="🛡️",
                meaning="protection/defense",
                cultural_variants={
                    "en": "🛡️",
                    "es": "🛡️",
                    "fr": "🛡️",
                    "de": "🛡️",
                    "zh": "盾",
                    "ja": "盾",
                    "pt": "🛡️",
                    "ar": "درع",
                    "hi": "ढाल",
                    "ru": "щит",
                },
                context="safety/security",
                weight=1.0,
                trinity_mapping="🛡️",
            ),
            CulturalGlyph(
                universal="⚖️",
                meaning="justice/balance",
                cultural_variants={
                    "en": "⚖️",
                    "es": "⚖️",
                    "fr": "⚖️",
                    "de": "⚖️",
                    "zh": "正义",
                    "ja": "正義",
                    "pt": "⚖️",
                    "ar": "عدالة",
                    "hi": "न्याय",
                    "ru": "правосудие",
                },
                context="ethical balance",
                weight=0.9,
                trinity_mapping="🛡️",
            ),
        ]

        # Quantum/Potential glyphs
        self.glyph_database["quantum"] = [
            CulturalGlyph(
                universal="⚛️",
                meaning="quantum/atomic",
                cultural_variants={
                    "en": "⚛️",
                    "es": "⚛️",
                    "fr": "⚛️",
                    "de": "⚛️",
                    "zh": "原子",
                    "ja": "原子",
                    "pt": "⚛️",
                    "ar": "ذرة",
                    "hi": "परमाणु",
                    "ru": "атом",
                },
                context="fundamental reality",
                weight=1.0,
                trinity_mapping="⚛️",
            ),
            CulturalGlyph(
                universal="∞",
                meaning="infinity/potential",
                cultural_variants={
                    "en": "∞",
                    "es": "∞",
                    "fr": "∞",
                    "de": "∞",
                    "zh": "無限",
                    "ja": "無限",
                    "pt": "∞",
                    "ar": "لانهاية",
                    "hi": "अनंत",
                    "ru": "бесконечность",
                },
                context="unlimited potential",
                weight=0.9,
                trinity_mapping="⚛️",
            ),
        ]

        # Harmony/Balance glyphs (culturally specific)
        self.glyph_database["harmony"] = [
            CulturalGlyph(
                universal="☯️",
                meaning="yin-yang/balance",
                cultural_variants={
                    "en": "☯️",
                    "es": "☯️",
                    "fr": "☯️",
                    "de": "☯️",
                    "zh": "☯️",
                    "ja": "☯️",
                    "pt": "☯️",
                    "ar": "☯️",
                    "hi": "☯️",
                    "ru": "☯️",
                },
                context="Eastern philosophy balance",
                weight=0.95,
                trinity_mapping="🧠",
            ),
            CulturalGlyph(
                universal="🕉️",
                meaning="om/unity",
                cultural_variants={
                    "en": "🕉️",
                    "es": "🕉️",
                    "fr": "🕉️",
                    "de": "🕉️",
                    "zh": "唵",
                    "ja": "オーム",
                    "pt": "🕉️",
                    "ar": "أوم",
                    "hi": "ॐ",
                    "ru": "Ом",
                },
                context="Hindu/Buddhist unity",
                weight=0.9,
                trinity_mapping="⚛️",
            ),
        ]

        # Nature/Growth glyphs
        self.glyph_database["nature"] = [
            CulturalGlyph(
                universal="🌿",
                meaning="growth/nature",
                cultural_variants={
                    "en": "🌿",
                    "es": "🌿",
                    "fr": "🌿",
                    "de": "🌿",
                    "zh": "叶",
                    "ja": "葉",
                    "pt": "🌿",
                    "ar": "ورقة",
                    "hi": "पत्ती",
                    "ru": "лист",
                },
                context="natural growth",
                weight=0.7,
                trinity_mapping="🧠",
            ),
            CulturalGlyph(
                universal="🌸",
                meaning="cherry blossom/transience",
                cultural_variants={
                    "en": "🌸",
                    "es": "🌸",
                    "fr": "🌸",
                    "de": "🌸",
                    "zh": "櫻",
                    "ja": "桜",
                    "pt": "🌸",
                    "ar": "زهرة",
                    "hi": "फूल",
                    "ru": "сакура",
                },
                context="beauty and impermanence",
                weight=0.8,
                trinity_mapping="🧠",
            ),
        ]

    def _load_or_create_map(self):
        """Load existing translation map or create new one"""
        if self.glyph_map_path.exists():
            try:
                with open(self.glyph_map_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self.cultural_mappings = data.get("mappings", {})
                    logger.info(f"   Loaded translation map from {self.glyph_map_path}")
            except Exception as e:
                logger.error(f"Failed to load translation map: {e}")
                self._create_default_map()
        else:
            self._create_default_map()

    def _create_default_map(self):
        """Create default translation mappings"""
        self.cultural_mappings = {
            "universal_to_cultural": {},
            "cultural_to_universal": {},
            "context_rules": {
                "zh": {
                    "prefer_characters": True,
                    "philosophy": "taoism/confucianism",
                },
                "ja": {"prefer_kanji": True, "philosophy": "zen/shinto"},
                "hi": {"prefer_devanagari": True, "philosophy": "vedic"},
                "ar": {"rtl": True, "philosophy": "islamic"},
            },
        }

        # Build mappings from database
        for glyphs in self.glyph_database.values():
            for glyph in glyphs:
                self.cultural_mappings["universal_to_cultural"][glyph.universal] = glyph.cultural_variants

                # Reverse mappings
                for locale, variant in glyph.cultural_variants.items():
                    if locale not in self.cultural_mappings["cultural_to_universal"]:
                        self.cultural_mappings["cultural_to_universal"][locale] = {}
                    self.cultural_mappings["cultural_to_universal"][locale][variant] = glyph.universal

        self._save_map()

    def _save_map(self):
        """Save translation map to file"""
        try:
            self.glyph_map_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare export data
            export_data = {
                "version": "1.0.0",
                "trinity_framework": ["⚛️", "🧠", "🛡️"],
                "supported_locales": self.supported_locales,
                "mappings": self.cultural_mappings,
                "glyph_categories": {},
            }

            # Export glyph database
            for category, glyphs in self.glyph_database.items():
                export_data["glyph_categories"][category] = [
                    {
                        "universal": g.universal,
                        "meaning": g.meaning,
                        "cultural_variants": g.cultural_variants,
                        "context": g.context,
                        "weight": g.weight,
                        "trinity_mapping": g.trinity_mapping,
                    }
                    for g in glyphs
                ]

            with open(self.glyph_map_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"   Saved translation map to {self.glyph_map_path}")

        except Exception as e:
            logger.error(f"Failed to save translation map: {e}")

    def translate_glyph(self, glyph: str, target_locale: str, context: Optional[str] = None) -> str:
        """
        Translate a single glyph to target locale.

        Args:
            glyph: Universal glyph to translate
            target_locale: Target locale code
            context: Optional context for translation

        Returns:
            Translated glyph or original if no translation
        """
        if target_locale not in self.supported_locales:
            logger.warning(f"Unsupported locale: {target_locale}")
            return glyph

        # Check direct mapping
        if glyph in self.cultural_mappings["universal_to_cultural"]:
            variants = self.cultural_mappings["universal_to_cultural"][glyph]
            if target_locale in variants:
                return variants[target_locale]

        # Return original if no translation
        return glyph

    def translate_sequence(
        self,
        glyphs: list[str],
        target_locale: str,
        preserve_trinity: bool = True,
    ) -> list[str]:
        """
        Translate a sequence of glyphs to target locale.

        Args:
            glyphs: List of glyphs to translate
            target_locale: Target locale code
            preserve_trinity: Keep Trinity glyphs universal

        Returns:
            List of translated glyphs
        """
        translated = []

        for glyph in glyphs:
            # Preserve Trinity core if requested
            if preserve_trinity and glyph in self.trinity_core:
                translated.append(glyph)
            else:
                translated.append(self.translate_glyph(glyph, target_locale))

        return translated

    def detect_cultural_context(self, text: str, glyphs: list[str]) -> dict[str, Any]:
        """
        Detect cultural context from text and glyphs.

        Args:
            text: Input text
            glyphs: Detected glyphs

        Returns:
            Cultural context analysis
        """
        context = {
            "detected_scripts": [],
            "likely_locales": [],
            "cultural_themes": [],
        }

        # Analyze glyphs
        for glyph in glyphs:
            if glyph == "☯️":
                context["cultural_themes"].append("eastern_philosophy")
                context["likely_locales"].extend(["zh", "ja"])
            elif glyph == "🕉️":
                context["cultural_themes"].append("hindu_buddhist")
                context["likely_locales"].extend(["hi", "th"])
            elif glyph in ["🌸", "櫻", "桜"]:
                context["cultural_themes"].append("japanese_aesthetics")
                context["likely_locales"].append("ja")

        # Detect scripts in text
        if any("\u4e00" <= c <= "\u9fff" for c in text):
            context["detected_scripts"].append("chinese")
            context["likely_locales"].append("zh")

        if any("\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" for c in text):
            context["detected_scripts"].append("japanese")
            context["likely_locales"].append("ja")

        if any("\u0600" <= c <= "\u06ff" for c in text):
            context["detected_scripts"].append("arabic")
            context["likely_locales"].append("ar")

        # Remove duplicates
        context["likely_locales"] = list(set(context["likely_locales"]))

        return context

    def get_locale_preferences(self, locale: str) -> dict[str, Any]:
        """
        Get cultural preferences for a locale.

        Args:
            locale: Locale code

        Returns:
            Cultural preferences
        """
        if locale not in self.supported_locales:
            return {}

        preferences = {
            "locale": locale,
            "preferred_glyphs": [],
            "avoided_glyphs": [],
            "philosophical_context": "",
        }

        # Locale-specific preferences
        if locale == "zh":
            preferences["preferred_glyphs"] = ["☯️", "道", "和", "智"]
            preferences["philosophical_context"] = "Taoist/Confucian harmony"

        elif locale == "ja":
            preferences["preferred_glyphs"] = ["🌸", "禅", "和", "侘寂"]
            preferences["philosophical_context"] = "Zen aesthetics and impermanence"

        elif locale == "hi":
            preferences["preferred_glyphs"] = ["🕉️", "ॐ", "चक्र", "कर्म"]
            preferences["philosophical_context"] = "Vedic wisdom and dharma"

        elif locale == "ar":
            preferences["preferred_glyphs"] = ["☪️", "🌙", "⭐", "🕌"]
            preferences["philosophical_context"] = "Islamic wisdom and submission"
            preferences["avoided_glyphs"] = ["🕉️"]  # Cultural sensitivity

        elif locale in ["en", "es", "fr", "de", "pt"]:
            preferences["preferred_glyphs"] = ["⚛️", "🧠", "🛡️", "⚖️"]
            preferences["philosophical_context"] = "Western rational/ethical framework"

        return preferences

    def harmonize_glyphs(self, glyphs: list[str], target_locale: str) -> list[str]:
        """
        Harmonize glyphs for cultural appropriateness.

        Args:
            glyphs: Original glyphs
            target_locale: Target locale

        Returns:
            Culturally harmonized glyphs
        """
        preferences = self.get_locale_preferences(target_locale)
        avoided = set(preferences.get("avoided_glyphs", []))

        harmonized = []
        for glyph in glyphs:
            if glyph in avoided:
                # Replace with culturally appropriate alternative
                if glyph == "🕉️" and target_locale == "ar":
                    harmonized.append("☪️")  # Islamic alternative
                else:
                    # Skip problematic glyph
                    continue
            else:
                harmonized.append(self.translate_glyph(glyph, target_locale))

        return harmonized

    def get_trinity_translations(self, locale: str) -> dict[str, str]:
        """
        Get Trinity Framework translations for a locale.

        Args:
            locale: Target locale

        Returns:
            Trinity translations
        """
        trinity_translations = {
            "en": {"⚛️": "Quantum", "🧠": "Consciousness", "🛡️": "Protection"},
            "es": {"⚛️": "Cuántico", "🧠": "Conciencia", "🛡️": "Protección"},
            "fr": {"⚛️": "Quantique", "🧠": "Conscience", "🛡️": "Protection"},
            "de": {"⚛️": "Quantum", "🧠": "Bewusstsein", "🛡️": "Schutz"},
            "zh": {"⚛️": "量子", "🧠": "意识", "🛡️": "保护"},
            "ja": {"⚛️": "量子", "🧠": "意識", "🛡️": "保護"},
            "pt": {"⚛️": "Quântico", "🧠": "Consciência", "🛡️": "Proteção"},
            "ar": {"⚛️": "كمي", "🧠": "وعي", "🛡️": "حماية"},
            "hi": {"⚛️": "क्वांटम", "🧠": "चेतना", "🛡️": "सुरक्षा"},
            "ru": {"⚛️": "Квантовый", "🧠": "Сознание", "🛡️": "Защита"},
        }

        return trinity_translations.get(locale, trinity_translations["en"])

    def generate_cultural_report(self) -> dict[str, Any]:
        """Generate report on cultural glyph coverage"""
        report = {
            "total_glyphs": sum(len(glyphs) for glyphs in self.glyph_database.values()),
            "supported_locales": len(self.supported_locales),
            "coverage_by_locale": {},
            "trinity_support": {},
        }

        # Calculate coverage
        for locale in self.supported_locales:
            translated_count = 0
            total_count = 0

            for glyphs in self.glyph_database.values():
                for glyph in glyphs:
                    total_count += 1
                    if locale in glyph.cultural_variants:
                        if glyph.cultural_variants[locale] != glyph.universal:
                            translated_count += 1

            report["coverage_by_locale"][locale] = {
                "translated": translated_count,
                "total": total_count,
                "percentage": ((translated_count / total_count * 100) if total_count > 0 else 0),
            }

            # Trinity support
            trinity_trans = self.get_trinity_translations(locale)
            report["trinity_support"][locale] = trinity_trans

        return report


# Example usage


def main():
    """Test the multilingual glyph engine"""
    engine = MultilingualGlyphEngine()

    # Test translations
    test_glyphs = ["🧠", "🛡️", "⚛️", "☯️", "🕉️", "🌸"]

    print("🌍 Multilingual Glyph Engine Test")
    print("=" * 60)

    for locale in ["en", "zh", "ja", "hi", "ar"]:
        print(f"\n{locale.upper(} Translations:")
        translated = engine.translate_sequence(test_glyphs, locale)

        for orig, trans in zip(test_glyphs, translated):
            print(f"  {orig} → {trans}")

        # Get preferences
        prefs = engine.get_locale_preferences(locale)
        print(f"  Philosophy: {prefs.get('philosophical_context', 'Universal'}")

    # Generate report
    print("\n" + "=" * 60)
    print("CULTURAL COVERAGE REPORT")
    print("=" * 60)

    report = engine.generate_cultural_report()
    print(f"Total glyphs: {report['total_glyphs']}")
    print(f"Supported locales: {report['supported_locales']}")

    print("\nCoverage by locale:")
    for locale, coverage in report["coverage_by_locale"].items():
        print(
            f"  {locale}: {coverage['translated']}/{coverage['total']} "
            f"({coverage['percentage']:.1f}% culturally adapted)"
        )

    print("\n✅ Multilingual Glyph Engine ready!")


if __name__ == "__main__":
    main()
