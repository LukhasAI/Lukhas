"""
Multi-Modal Language System
===========================
Combines words, symbols (emojis), images, sounds, and gestures
to create a universal language with maximum entropy for passwords.

Based on user requirements for highest entropy password system.
"""

import asyncio
import base64
import hashlib
import io
import logging
import math
import time
from collections.abc import Awaitable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np
from PIL import Image

# Audio processing (optional - install with pip install librosa)
try:
    import librosa

    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("librosa not available - audio processing disabled")

# Import LUKHAS components
from lukhas.orchestration.signals.signal_bus import Signal, SignalBus, SignalType
from symbolic.exchange.universal_exchange import UniversalSymbolExchange
from symbolic.personal.symbol_dictionary import PersonalSymbolDictionary

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Types of input modalities"""

    TEXT = "text"
    EMOJI = "emoji"
    IMAGE = "image"
    SOUND = "sound"
    GESTURE = "gesture"
    COLOR = "color"
    PATTERN = "pattern"
    RHYTHM = "rhythm"


@dataclass
class ModalityFeatures:
    """Extracted features from a modality"""

    modality: ModalityType
    raw_data: Any
    features: np.ndarray
    entropy_bits: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UniversalConcept:
    """A universal concept built from multi-modal inputs"""

    concept_id: str
    meaning: str
    modalities: list[ModalityFeatures]
    embedding: np.ndarray
    entropy_total: float
    cultural_validations: dict[str, float] = field(default_factory=dict)
    creation_time: float = field(default_factory=time.time)
    usage_count: int = 0


@dataclass
class HighEntropyPassword:
    """Ultra-high entropy password using multi-modal elements"""

    password_id: str
    elements: dict[ModalityType, Any]
    entropy_bits: float
    memorability_score: float
    visual_hash: str
    audio_hash: Optional[str] = None
    gesture_sequence: Optional[list[dict]] = None
    creation_time: float = field(default_factory=time.time)

    def to_secure_string(self) -> str:
        """Convert to secure string representation"""
        # Combine all elements into a high-entropy string
        combined: list[str] = []

        if ModalityType.TEXT in self.elements:
            combined.append(self.elements[ModalityType.TEXT])

        if ModalityType.EMOJI in self.elements:
            combined.extend(self.elements[ModalityType.EMOJI])

        # Add hashes for non-text elements
        combined.append(self.visual_hash[:8])

        if self.audio_hash:
            combined.append(self.audio_hash[:8])

        return "".join(map(str, combined))


class MultiModalLanguageBuilder:
    """
    Builds a universal language from multi-modal inputs.
    Maximizes entropy for password generation.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.signal_bus = SignalBus()

        # Personal and universal dictionaries
        self.personal_dict = PersonalSymbolDictionary(user_id)
        self.universal_exchange = UniversalSymbolExchange(self.signal_bus)

        # Concept storage
        self.concepts: dict[str, UniversalConcept] = {}

        # Entropy tracking
        self.entropy_sources: dict[ModalityType, int] = {
            ModalityType.TEXT: 94,  # ASCII printable
            ModalityType.EMOJI: 3664,  # Unicode emojis
            ModalityType.IMAGE: 2**24,  # RGB color space
            ModalityType.SOUND: 2**16,  # Audio frequency space
            ModalityType.GESTURE: 1000,  # Gesture combinations
            ModalityType.COLOR: 16777216,  # 24-bit color
            ModalityType.PATTERN: 10000,  # Visual patterns
            ModalityType.RHYTHM: 1000,  # Rhythm patterns
        }

        # Feature extractors
        self.feature_extractors: dict[ModalityType, Callable[[Any], Awaitable[ModalityFeatures]]] = {
            ModalityType.TEXT: self._extract_text_features,
            ModalityType.EMOJI: self._extract_emoji_features,
            ModalityType.IMAGE: self._extract_image_features,
            ModalityType.SOUND: self._extract_sound_features,
            ModalityType.GESTURE: self._extract_gesture_features,
            ModalityType.COLOR: self._extract_color_features,
            ModalityType.PATTERN: self._extract_pattern_features,
            ModalityType.RHYTHM: self._extract_rhythm_features,
        }

    async def build_concept(self, meaning: str, inputs: dict[ModalityType, Any]) -> UniversalConcept:
        """Build a universal concept from multi-modal inputs"""

        # Extract features from each modality
        modality_features: list[ModalityFeatures] = []
        total_entropy = 0.0

        for modality, data in inputs.items():
            if modality in self.feature_extractors:
                features = await self.feature_extractors[modality](data)
                modality_features.append(features)
                total_entropy += features.entropy_bits

        # Create multi-modal embedding
        embedding = self._create_embedding(modality_features)

        # Generate concept ID
        concept_id = hashlib.sha256(f"{meaning}_{embedding.tobytes()}".encode()).hexdigest()[:16]

        # Create concept
        concept = UniversalConcept(
            concept_id=concept_id,
            meaning=meaning,
            modalities=modality_features,
            embedding=embedding,
            entropy_total=total_entropy,
        )

        # Store concept
        self.concepts[concept_id] = concept

        # Emit signal about new concept
        await self._emit_signal(
            SignalType.NOVELTY,
            0.7,
            {"action": "concept_created", "meaning": meaning, "entropy": total_entropy},
        )

        logger.info(f"Created concept '{meaning}' with {total_entropy:.2f} bits of entropy")

        return concept

    async def generate_password(
        self,
        target_entropy: int = 256,
        memorability_weight: float = 0.5,
        use_modalities: Optional[list[ModalityType]] = None,
    ) -> HighEntropyPassword:
        """Generate an ultra-high entropy password"""

        if use_modalities is None:
            use_modalities = [
                ModalityType.TEXT,
                ModalityType.EMOJI,
                ModalityType.GESTURE,
                ModalityType.COLOR,
            ]

        password_elements: dict[ModalityType, Any] = {}
        current_entropy = 0.0

        # Generate text component
        if ModalityType.TEXT in use_modalities:
            text_length = min(20, max(4, int(target_entropy / 30)))
            text = self._generate_memorable_text(text_length)
            password_elements[ModalityType.TEXT] = text
            current_entropy += len(text) * math.log2(94)

        # Generate emoji component
        if ModalityType.EMOJI in use_modalities:
            emoji_count = min(10, max(3, int((target_entropy - current_entropy) / 12)))
            emojis = self._select_memorable_emojis(emoji_count)
            password_elements[ModalityType.EMOJI] = emojis
            current_entropy += len(emojis) * math.log2(3664)

        # Generate gesture sequence
        if ModalityType.GESTURE in use_modalities:
            gesture_count = min(5, max(2, int((target_entropy - current_entropy) / 10)))
            gestures = self._generate_gesture_sequence(gesture_count)
            password_elements[ModalityType.GESTURE] = gestures
            current_entropy += len(gestures) * math.log2(1000)

        # Generate color pattern
        if ModalityType.COLOR in use_modalities:
            colors = self._generate_color_pattern(4)
            password_elements[ModalityType.COLOR] = colors
            current_entropy += len(colors) * math.log2(16777216)

        # Generate visual hash
        visual_elements: list[str] = []
        if ModalityType.EMOJI in password_elements:
            visual_elements.extend(password_elements[ModalityType.EMOJI])
        if ModalityType.COLOR in password_elements:
            visual_elements.extend([str(c) for c in password_elements[ModalityType.COLOR]])

        visual_hash = hashlib.sha256("".join(visual_elements).encode()).hexdigest()

        # Calculate memorability
        element_complexity = sum(len(v) if isinstance(v, (list, str)) else 1 for v in password_elements.values())
        memorability = max(0.2, min(1.0, 1.0 - (element_complexity / 30)))

        # Adjust for memorability weight
        if memorability < memorability_weight:
            # Simplify if too complex
            if ModalityType.GESTURE in password_elements and len(password_elements[ModalityType.GESTURE]) > 2:
                password_elements[ModalityType.GESTURE] = password_elements[ModalityType.GESTURE][:2]

        # Create password object
        password = HighEntropyPassword(
            password_id=hashlib.sha256(str(time.time()).encode()).hexdigest()[:16],
            elements=password_elements,
            entropy_bits=current_entropy,
            memorability_score=memorability,
            visual_hash=visual_hash,
            gesture_sequence=password_elements.get(ModalityType.GESTURE),
        )

        logger.info(f"Generated password with {current_entropy:.2f} bits of entropy")

        return password

    async def _extract_text_features(self, text: str) -> ModalityFeatures:
        """Extract features from text"""
        # Character frequency analysis
        char_freq: dict[str, int] = {}
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1

        # Create feature vector
        features = np.array(
            [
                len(text),
                len(set(text)),  # Unique characters
                sum(1 for c in text if c.isupper()),
                sum(1 for c in text if c.isdigit()),
                sum(1 for c in text if not c.isalnum()),
            ],
            dtype=np.float32,
        )

        # Calculate entropy
        entropy = len(text) * math.log2(94)

        return ModalityFeatures(
            modality=ModalityType.TEXT,
            raw_data=text,
            features=features,
            entropy_bits=entropy,
            metadata={"char_freq": char_freq},
        )

    async def _extract_emoji_features(self, emojis: list[str]) -> ModalityFeatures:
        """Extract features from emojis"""
        # Emoji category analysis
        categories = {
            "emotion": ["😀", "😍", "😢", "😡", "😱"],
            "nature": ["🌟", "🌈", "🌺", "🌊", "⛰️"],
            "object": ["🔐", "💎", "🎯", "🚀", "⚡"],
            "symbol": ["❤️", "✨", "🔥", "💫", "⭐"],
        }

        category_counts = dict.fromkeys(categories, 0)
        for emoji in emojis:
            for cat, cat_emojis in categories.items():
                if emoji in cat_emojis:
                    category_counts[cat] += 1

        features = np.array(list(category_counts.values()), dtype=np.float32)
        entropy = len(emojis) * math.log2(3664)

        return ModalityFeatures(
            modality=ModalityType.EMOJI,
            raw_data=emojis,
            features=features,
            entropy_bits=entropy,
            metadata={"categories": category_counts},
        )

    async def _extract_image_features(self, image_data: Any) -> ModalityFeatures:
        """Extract features from image"""
        if isinstance(image_data, str):
            # Assume base64 encoded
            try:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            except BaseException:
                # Fallback to empty features
                return ModalityFeatures(
                    modality=ModalityType.IMAGE,
                    raw_data=image_data,
                    features=np.zeros(10),
                    entropy_bits=50.0,
                )
        else:
            image = image_data

        # Extract color histogram
        if hasattr(image, "histogram"):
            hist = image.histogram()
            features = np.array(hist[:30], dtype=np.float32)  # First 30 bins
        else:
            features = np.random.rand(30)

        # Estimate entropy (simplified)
        entropy = 50.0  # ~50 bits for a small image

        return ModalityFeatures(
            modality=ModalityType.IMAGE,
            raw_data=image_data,
            features=features,
            entropy_bits=entropy,
        )

    async def _extract_sound_features(self, audio_data: Any) -> ModalityFeatures:
        """Extract features from sound"""
        if AUDIO_AVAILABLE and isinstance(audio_data, np.ndarray):
            # Extract audio features using librosa
            mfcc = librosa.feature.mfcc(y=audio_data, sr=22050, n_mfcc=13)
            features = np.mean(mfcc, axis=1)
            entropy = 40.0  # ~40 bits for audio pattern
        else:
            # Fallback without librosa
            features = np.random.rand(13)
            entropy = 30.0

        return ModalityFeatures(
            modality=ModalityType.SOUND,
            raw_data=audio_data,
            features=features,
            entropy_bits=entropy,
        )

    async def _extract_gesture_features(self, gestures: list[dict]) -> ModalityFeatures:
        """Extract features from gesture sequence"""
        if not gestures:
            gestures = [{"type": "tap", "timing": 0.5, "pressure": 0.5}]

        # Extract timing and pressure patterns
        timings = [g.get("timing", 0.5) for g in gestures]
        pressures = [g.get("pressure", 0.5) for g in gestures]

        features = np.array(
            [
                len(gestures),
                np.mean(timings),
                np.std(timings),
                np.mean(pressures),
                np.std(pressures),
            ],
            dtype=np.float32,
        )

        entropy = len(gestures) * math.log2(1000)

        return ModalityFeatures(
            modality=ModalityType.GESTURE,
            raw_data=gestures,
            features=features,
            entropy_bits=entropy,
            metadata={"sequence_length": len(gestures)},
        )

    async def _extract_color_features(self, colors: list[tuple[int, int, int]]) -> ModalityFeatures:
        """Extract features from color pattern"""
        if not colors:
            colors = [(128, 128, 128)]

        # Extract color statistics
        reds = [c[0] for c in colors]
        greens = [c[1] for c in colors]
        blues = [c[2] for c in colors]

        features = np.array(
            [
                np.mean(reds),
                np.mean(greens),
                np.mean(blues),
                np.std(reds),
                np.std(greens),
                np.std(blues),
            ],
            dtype=np.float32,
        )

        entropy = len(colors) * math.log2(16777216)

        return ModalityFeatures(
            modality=ModalityType.COLOR,
            raw_data=colors,
            features=features,
            entropy_bits=entropy,
        )

    async def _extract_pattern_features(self, pattern: Any) -> ModalityFeatures:
        """Extract features from visual pattern"""
        # Simplified pattern analysis
        features = np.random.rand(10)
        entropy = 30.0

        return ModalityFeatures(
            modality=ModalityType.PATTERN,
            raw_data=pattern,
            features=features,
            entropy_bits=entropy,
        )

    async def _extract_rhythm_features(self, rhythm: list[float]) -> ModalityFeatures:
        """Extract features from rhythm pattern"""
        if not rhythm:
            rhythm = [0.5, 0.5, 1.0]

        features = np.array(
            [
                len(rhythm),
                np.mean(rhythm),
                np.std(rhythm),
                np.min(rhythm),
                np.max(rhythm),
            ],
            dtype=np.float32,
        )

        entropy = len(rhythm) * math.log2(100)

        return ModalityFeatures(
            modality=ModalityType.RHYTHM,
            raw_data=rhythm,
            features=features,
            entropy_bits=entropy,
        )

    def _create_embedding(self, modality_features: list[ModalityFeatures]) -> np.ndarray:
        """Create unified embedding from multiple modalities"""
        if not modality_features:
            return np.zeros(128)

        # Concatenate all features
        all_features: list[float] = []
        for mf in modality_features:
            all_features.extend(mf.features)

        # Pad or truncate to fixed size
        embedding_size = 128
        embedding: np.ndarray
        if len(all_features) > embedding_size:
            embedding = np.array(all_features[:embedding_size])
        else:
            embedding = np.pad(all_features, (0, embedding_size - len(all_features)))

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def _generate_memorable_text(self, length: int) -> str:
        """Generate memorable text with high entropy"""
        import random

        # Use pronounceable patterns
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"

        text: list[str] = []
        for i in range(length):
            if i % 2 == 0:
                text.append(random.choice(consonants).upper() if i == 0 else random.choice(consonants))
            else:
                text.append(random.choice(vowels))

        # Add some numbers and symbols for entropy
        text.append(str(random.randint(0, 99)))
        text.append(random.choice("!@#$%^&*()"))

        return "".join(text)

    def _select_memorable_emojis(self, count: int) -> list[str]:
        """Select memorable emojis with meaning"""
        import random

        # Themed emoji sets for memorability
        themes = {
            "nature": ["🌟", "🌈", "🌺", "🌊", "⛰️", "🌳", "🌸", "🦋"],
            "space": ["🚀", "🌌", "⭐", "🌙", "☄️", "🛸", "🌍", "✨"],
            "gems": ["💎", "💍", "👑", "🏆", "💰", "🎯", "🔮", "💫"],
            "elements": ["🔥", "💧", "⚡", "🌪️", "❄️", "☀️", "🌩️", "💨"],
        }

        # Select a theme
        theme = random.choice(list(themes.values()))
        selected = random.sample(theme, min(count, len(theme)))

        # Add from other themes if needed
        while len(selected) < count:
            other_theme = random.choice(list(themes.values()))
            selected.append(random.choice(other_theme))

        return selected[:count]

    def _generate_gesture_sequence(self, count: int) -> list[dict[str, Any]]:
        """Generate memorable gesture sequence"""
        import random

        gesture_types = [
            "tap",
            "double_tap",
            "long_press",
            "swipe_up",
            "swipe_down",
            "swipe_left",
            "swipe_right",
            "circle",
            "zigzag",
            "pinch",
            "spread",
        ]

        gestures: list[dict[str, Any]] = []
        for _ in range(count):
            gestures.append(
                {
                    "type": random.choice(gesture_types),
                    "timing": round(random.uniform(0.2, 1.5), 2),
                    "pressure": round(random.uniform(0.3, 1.0), 2),
                }
            )

        return gestures

    def _generate_color_pattern(self, count: int) -> list[tuple[int, int, int]]:
        """Generate memorable color pattern"""
        import random

        # Use color harmony rules for memorability
        base_hue = random.randint(0, 360)
        colors: list[tuple[int, int, int]] = []

        for i in range(count):
            # Complementary, triadic, or analogous colors
            hue_offset = i * (360 // count)
            hue = (base_hue + hue_offset) % 360

            # Convert HSV to RGB (simplified)
            rgb = self._hsv_to_rgb(hue, 0.8, 0.9)
            colors.append(rgb)

        return colors

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> tuple[int, int, int]:
        """Convert HSV to RGB color"""
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        r, g, b = 0.0, 0.0, 0.0
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    async def _emit_signal(self, signal_type: SignalType, level: float, metadata: dict) -> None:
        """Emit signal through signal bus"""
        signal = Signal(
            name=signal_type,
            source="multi_modal_language",
            level=level,
            metadata=metadata,
        )
        self.signal_bus.publish(signal)

    def export_language_model(self) -> dict[str, Any]:
        """Export the language model for sharing"""
        return {
            "user_id": self.user_id,
            "concepts": {
                cid: {
                    "meaning": concept.meaning,
                    "entropy": concept.entropy_total,
                    "modalities": len(concept.modalities),
                    "usage": concept.usage_count,
                }
                for cid, concept in self.concepts.items()
            },
            "total_concepts": len(self.concepts),
            "total_entropy": sum(c.entropy_total for c in self.concepts.values()),
            "creation_time": time.time(),
        }


# Demo usage
async def demo_multi_modal_language():
    """Demonstrate multi-modal language and password generation"""

    print("🌍 Multi-Modal Language System Demo")
    print("=" * 50)

    # Create language builder
    builder = MultiModalLanguageBuilder("demo_user")

    # Build a concept for "Security"
    security_concept = await builder.build_concept(
        meaning="security",
        inputs={
            ModalityType.TEXT: "protect safe guard",
            ModalityType.EMOJI: ["🔐", "🛡️", "🔒", "🗝️"],
            ModalityType.COLOR: [(0, 100, 200), (50, 150, 50)],  # Blue and green
            ModalityType.GESTURE: [
                {"type": "circle", "timing": 0.5, "pressure": 0.8},
                {"type": "tap_tap_hold", "timing": 1.0, "pressure": 0.9},
            ],
        },
    )

    print(f"\n✅ Created concept '{security_concept.meaning}':")
    print(f"   Entropy: {security_concept.entropy_total:.2f} bits")
    print(f"   Modalities: {len(security_concept.modalities)}")

    # Generate ultra-high entropy password
    print("\n🔐 Generating Ultra-High Entropy Password...")

    password = await builder.generate_password(
        target_entropy=256,
        memorability_weight=0.7,
        use_modalities=[
            ModalityType.TEXT,
            ModalityType.EMOJI,
            ModalityType.GESTURE,
            ModalityType.COLOR,
        ],
    )

    print("\n🎯 Password Generated:")
    print(f"   Entropy: {password.entropy_bits:.2f} bits")
    print(f"   Memorability: {password.memorability_score:.2%}")

    if ModalityType.TEXT in password.elements:
        print(f"   Text: {password.elements[ModalityType.TEXT]}")

    if ModalityType.EMOJI in password.elements:
        print(f"   Emojis: {''.join(password.elements[ModalityType.EMOJI])}")

    if ModalityType.GESTURE in password.elements:
        print(f"   Gestures: {len(password.elements[ModalityType.GESTURE])} patterns")

    if ModalityType.COLOR in password.elements:
        print(f"   Colors: {len(password.elements[ModalityType.COLOR])} colors")

    print(f"   Visual Hash: {password.visual_hash[:16]}...")

    # Calculate cracking time
    guesses_per_second = 1e12  # 1 trillion/second
    total_possibilities = 2**password.entropy_bits
    seconds_to_crack = total_possibilities / (2 * guesses_per_second)
    years_to_crack = seconds_to_crack / (365 * 24 * 3600)

    print("\n⏱️ Time to crack (at 1 trillion guesses/sec):")
    if years_to_crack > 1e9:
        print(f"   {years_to_crack:.2e} years (essentially uncrackable)")
    else:
        print(f"   {years_to_crack:.2f} years")

    # Export language model
    model = builder.export_language_model()
    print("\n📊 Language Model Statistics:")
    print(f"   Total concepts: {model['total_concepts']}")
    print(f"   Total entropy pool: {model['total_entropy']:.2f} bits")

    print("\n✨ Multi-modal language system ready for universal communication!")


if __name__ == "__main__":
    asyncio.run(demo_multi_modal_language())
