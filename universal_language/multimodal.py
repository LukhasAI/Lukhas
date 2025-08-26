"""
Multimodal Processing for Universal Language
=============================================

Handles multi-modal inputs including text, emoji, images, audio, and gestures.
Based on /symbolic/multi_modal_language.py and Universal Language spec.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

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
    STROKE = "stroke"  # Drawing/writing strokes
    VIDEO = "video"


@dataclass
class ModalityFeatures:
    """Extracted features from a modality"""
    modality: ModalityType
    raw_data: Any
    features: Optional[np.ndarray] = None
    entropy_bits: float = 0.0
    fingerprint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.entropy_bits == 0.0:
            self.entropy_bits = self.calculate_entropy()
        if not self.fingerprint:
            self.fingerprint = self.generate_fingerprint()

    def calculate_entropy(self) -> float:
        """Calculate entropy for this modality"""
        if self.modality == ModalityType.TEXT:
            # Text entropy based on length and uniqueness
            if isinstance(self.raw_data, str):
                unique_chars = len(set(self.raw_data))
                return unique_chars * 4.0  # Approximate bits per unique character

        elif self.modality == ModalityType.EMOJI:
            # Emoji entropy - high due to large Unicode space
            if isinstance(self.raw_data, str):
                return len(self.raw_data) * 16.0  # 16 bits per emoji

        elif self.modality == ModalityType.COLOR:
            # Color entropy from RGB/HSV space
            return 24.0  # 8 bits per channel for RGB

        elif self.modality == ModalityType.GESTURE:
            # Gesture entropy from path complexity
            if isinstance(self.raw_data, list):
                return len(self.raw_data) * 8.0  # 8 bits per gesture point

        # Default entropy
        return 32.0

    def generate_fingerprint(self) -> str:
        """Generate fingerprint for this modality"""
        if self.modality == ModalityType.TEXT:
            # Simple hash for text
            return hashlib.sha256(str(self.raw_data).encode()).hexdigest()[:16]

        elif self.modality == ModalityType.EMOJI:
            # Unicode codepoint sequence
            if isinstance(self.raw_data, str):
                codepoints = [hex(ord(c)) for c in self.raw_data]
                return "_".join(codepoints)

        elif self.modality == ModalityType.COLOR:
            # Normalize color representation
            if isinstance(self.raw_data, (list, tuple)) and len(self.raw_data) >= 3:
                r, g, b = self.raw_data[:3]
                return f"#{r:02x}{g:02x}{b:02x}"

        elif self.modality == ModalityType.GESTURE:
            # Hash of gesture path
            if isinstance(self.raw_data, list):
                path_str = "_".join(str(p) for p in self.raw_data)
                return hashlib.sha256(path_str.encode()).hexdigest()[:16]

        # Default fingerprint
        return hashlib.sha256(str(self.raw_data).encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "modality": self.modality.value,
            "fingerprint": self.fingerprint,
            "entropy_bits": self.entropy_bits,
            "metadata": self.metadata
        }


@dataclass
class MultiModalMessage:
    """A message containing multiple modalities"""
    message_id: str
    modalities: List[ModalityFeatures]
    combined_entropy: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.message_id:
            self.message_id = self.generate_id()
        if self.combined_entropy == 0.0:
            self.combined_entropy = self.calculate_combined_entropy()

    def generate_id(self) -> str:
        """Generate unique message ID"""
        fingerprints = [m.fingerprint for m in self.modalities if m.fingerprint]
        combined = "_".join(fingerprints)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def calculate_combined_entropy(self) -> float:
        """Calculate total entropy across all modalities"""
        # Sum entropy from all modalities
        total = sum(m.entropy_bits for m in self.modalities)

        # Add bonus for multi-modal diversity
        diversity_bonus = len(set(m.modality for m in self.modalities)) * 8.0

        return total + diversity_bonus

    def get_modality(self, modality_type: ModalityType) -> Optional[ModalityFeatures]:
        """Get features for a specific modality"""
        for m in self.modalities:
            if m.modality == modality_type:
                return m
        return None

    def has_modality(self, modality_type: ModalityType) -> bool:
        """Check if message has a specific modality"""
        return any(m.modality == modality_type for m in self.modalities)


class ModalityProcessor:
    """Processes individual modalities"""

    def __init__(self):
        self.processors = {
            ModalityType.TEXT: self.process_text,
            ModalityType.EMOJI: self.process_emoji,
            ModalityType.COLOR: self.process_color,
            ModalityType.GESTURE: self.process_gesture,
            ModalityType.STROKE: self.process_stroke,
            ModalityType.PATTERN: self.process_pattern,
            ModalityType.RHYTHM: self.process_rhythm
        }

    def process(self, raw_data: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Process raw data for a specific modality"""
        processor = self.processors.get(modality_type, self.process_default)
        return processor(raw_data, modality_type)

    def process_text(self, text: str, modality_type: ModalityType) -> ModalityFeatures:
        """Process text modality"""
        # Extract features
        features = {
            "length": len(text),
            "words": len(text.split()),
            "unique_chars": len(set(text)),
            "language": self.detect_language(text)
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=text,
            metadata=features
        )

    def process_emoji(self, emoji: str, modality_type: ModalityType) -> ModalityFeatures:
        """Process emoji modality"""
        # Extract Unicode properties
        codepoints = [ord(c) for c in emoji]

        features = {
            "emoji_count": len(emoji),
            "codepoints": codepoints,
            "categories": self.get_emoji_categories(emoji)
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=emoji,
            metadata=features
        )

    def process_color(self, color: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Process color modality"""
        # Normalize color format
        if isinstance(color, str):
            # Hex color
            if color.startswith("#"):
                rgb = self.hex_to_rgb(color)
            else:
                rgb = (0, 0, 0)  # Default to black
        elif isinstance(color, (list, tuple)) and len(color) >= 3:
            rgb = color[:3]
        else:
            rgb = (0, 0, 0)

        # Calculate color properties
        features = {
            "rgb": rgb,
            "hsv": self.rgb_to_hsv(rgb),
            "luminance": self.calculate_luminance(rgb)
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=color,
            metadata=features
        )

    def process_gesture(self, gesture_data: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Process gesture modality"""
        # Gesture as sequence of points or vectors
        if isinstance(gesture_data, list):
            points = gesture_data
        else:
            points = []

        features = {
            "point_count": len(points),
            "complexity": self.calculate_gesture_complexity(points)
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=gesture_data,
            metadata=features
        )

    def process_stroke(self, stroke_data: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Process drawing/writing stroke"""
        # Similar to gesture but with pressure/velocity
        features = {
            "stroke_type": "drawing",
            "normalized": False
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=stroke_data,
            metadata=features
        )

    def process_pattern(self, pattern_data: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Process visual pattern"""
        features = {
            "pattern_type": "visual",
            "repetitions": 0
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=pattern_data,
            metadata=features
        )

    def process_rhythm(self, rhythm_data: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Process rhythm/temporal pattern"""
        features = {
            "tempo": 0,
            "pattern": []
        }

        return ModalityFeatures(
            modality=modality_type,
            raw_data=rhythm_data,
            metadata=features
        )

    def process_default(self, data: Any, modality_type: ModalityType) -> ModalityFeatures:
        """Default processor for unknown modalities"""
        return ModalityFeatures(
            modality=modality_type,
            raw_data=data
        )

    # Helper methods
    def detect_language(self, text: str) -> str:
        """Detect language of text (simplified)"""
        # TODO: Implement actual language detection
        return "en"

    def get_emoji_categories(self, emoji: str) -> List[str]:
        """Get emoji categories (simplified)"""
        # TODO: Implement emoji categorization
        return ["emotion"]

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hsv(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSV"""
        r, g, b = [x / 255.0 for x in rgb]
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        diff = max_c - min_c

        # Hue
        if diff == 0:
            h = 0
        elif max_c == r:
            h = ((g - b) / diff) % 6
        elif max_c == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4
        h = h * 60

        # Saturation
        s = 0 if max_c == 0 else diff / max_c

        # Value
        v = max_c

        return (h, s, v)

    def calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """Calculate perceived luminance"""
        r, g, b = [x / 255.0 for x in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def calculate_gesture_complexity(self, points: List) -> float:
        """Calculate complexity of a gesture path"""
        if len(points) < 2:
            return 0.0

        # Simple complexity based on path length
        return float(len(points))


class MultiModalProcessor:
    """
    Main processor for multi-modal inputs.

    Handles combination and analysis of multiple modalities.
    """

    def __init__(self):
        self.modality_processor = ModalityProcessor()
        self.message_cache: Dict[str, MultiModalMessage] = {}
        logger.info("MultiModal Processor initialized")

    def create_message(self, inputs: Dict[ModalityType, Any]) -> MultiModalMessage:
        """Create a multi-modal message from inputs"""
        modalities = []

        for modality_type, raw_data in inputs.items():
            if raw_data is not None:
                features = self.modality_processor.process(raw_data, modality_type)
                modalities.append(features)

        message = MultiModalMessage(
            message_id="",  # Will be auto-generated
            modalities=modalities
        )

        # Cache the message
        self.message_cache[message.message_id] = message

        return message

    def extract_dominant_modality(self, message: MultiModalMessage) -> ModalityFeatures:
        """Extract the dominant modality from a message"""
        if not message.modalities:
            return None

        # Find modality with highest entropy
        return max(message.modalities, key=lambda m: m.entropy_bits)

    def combine_modalities(self, message: MultiModalMessage) -> Dict[str, Any]:
        """Combine multiple modalities into unified representation"""
        combined = {
            "message_id": message.message_id,
            "total_entropy": message.combined_entropy,
            "modality_count": len(message.modalities),
            "modalities": {}
        }

        for modality in message.modalities:
            combined["modalities"][modality.modality.value] = {
                "fingerprint": modality.fingerprint,
                "entropy": modality.entropy_bits,
                "metadata": modality.metadata
            }

        return combined

    def calculate_similarity(self, message1: MultiModalMessage,
                           message2: MultiModalMessage) -> float:
        """Calculate similarity between two multi-modal messages"""
        # Find common modalities
        modalities1 = {m.modality for m in message1.modalities}
        modalities2 = {m.modality for m in message2.modalities}
        common_modalities = modalities1 & modalities2

        if not common_modalities:
            return 0.0

        # Calculate similarity for each common modality
        similarities = []
        for modality_type in common_modalities:
            m1 = message1.get_modality(modality_type)
            m2 = message2.get_modality(modality_type)

            if m1 and m2:
                # Simple fingerprint comparison
                if m1.fingerprint == m2.fingerprint:
                    similarities.append(1.0)
                else:
                    # Calculate partial similarity
                    similarities.append(self._calculate_modality_similarity(m1, m2))

        # Average similarity
        return sum(similarities) / len(similarities) if similarities else 0.0

    def _calculate_modality_similarity(self, m1: ModalityFeatures,
                                     m2: ModalityFeatures) -> float:
        """Calculate similarity between two modality features"""
        # Simple implementation - can be enhanced
        if m1.modality != m2.modality:
            return 0.0

        # Compare metadata
        if m1.metadata and m2.metadata:
            common_keys = set(m1.metadata.keys()) & set(m2.metadata.keys())
            if common_keys:
                matches = sum(1 for k in common_keys
                            if m1.metadata[k] == m2.metadata[k])
                return matches / len(common_keys)

        return 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed messages"""
        if not self.message_cache:
            return {"total_messages": 0}

        modality_counts = {}
        total_entropy = 0.0

        for message in self.message_cache.values():
            total_entropy += message.combined_entropy
            for modality in message.modalities:
                modality_type = modality.modality.value
                modality_counts[modality_type] = modality_counts.get(modality_type, 0) + 1

        return {
            "total_messages": len(self.message_cache),
            "average_entropy": total_entropy / len(self.message_cache),
            "modality_distribution": modality_counts,
            "cache_size": len(self.message_cache)
        }


# Singleton instance
_multimodal_processor_instance = None


def get_multimodal_processor() -> MultiModalProcessor:
    """Get or create the singleton MultiModal Processor instance"""
    global _multimodal_processor_instance
    if _multimodal_processor_instance is None:
        _multimodal_processor_instance = MultiModalProcessor()
    return _multimodal_processor_instance
