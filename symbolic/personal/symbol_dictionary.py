"""
Personal Symbol Dictionary with Gesture Mapping
===============================================
Implements encrypted on-device storage for personal emoji/gesture mappings
with evolution tracking and privacy-preserving features.

Based on GPT5 audit recommendations for personalized symbolic communication.
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Import our vocabularies

logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Types of gestures that can be mapped to symbols"""
    HAND = "hand_gesture"
    FACIAL = "facial_expression"
    BODY = "body_posture"
    EYE = "eye_movement"
    VOICE = "voice_tone"
    TOUCH = "touch_pattern"
    MOVEMENT = "movement_pattern"
    COMPOSITE = "composite_gesture"


@dataclass
class SymbolMapping:
    """A single symbol-to-meaning mapping"""
    symbol: str
    meaning: str
    gesture_type: GestureType
    context: str = ""
    confidence: float = 1.0
    usage_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['gesture_type'] = self.gesture_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolMapping':
        """Create from dictionary"""
        data = data.copy()
        data['gesture_type'] = GestureType(data['gesture_type'])
        return cls(**data)


@dataclass
class GesturePattern:
    """Pattern recognition for gestures"""
    pattern_id: str
    gesture_sequence: List[str]
    timing: List[float]  # Time between gestures
    confidence_threshold: float = 0.8
    matched_symbol: Optional[str] = None

    def matches(self, sequence: List[str], timings: List[float]) -> bool:
        """Check if a sequence matches this pattern"""
        if len(sequence) != len(self.gesture_sequence):
            return False

        # Check gesture sequence
        if sequence != self.gesture_sequence:
            return False

        # Check timing pattern (with tolerance)
        if timings and self.timing:
            tolerance = 0.3  # 300ms tolerance
            for t1, t2 in zip(timings, self.timing):
                if abs(t1 - t2) > tolerance:
                    return False

        return True


class PersonalSymbolDictionary:
    """
    Personal dictionary for mapping symbols to meanings with gesture support.
    Provides encrypted storage and privacy-preserving features.
    """

    def __init__(self, user_id: str, storage_path: Optional[Path] = None):
        self.user_id = user_id
        self.storage_path = storage_path or Path(f".lukhas/personal/{user_id}/symbols.enc")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Symbol mappings
        self.mappings: Dict[str, SymbolMapping] = {}
        self.gesture_patterns: Dict[str, GesturePattern] = {}

        # Privacy settings
        self.encryption_key: Optional[bytes] = None
        self.is_locked = True

        # Evolution tracking
        self.evolution_history: List[Dict[str, Any]] = []
        self.feedback_scores: Dict[str, float] = {}

        # Initialize with base gesture symbols
        self._initialize_base_symbols()

    def _initialize_base_symbols(self):
        """Initialize with common gesture symbols from bio vocabulary"""
        # Add common hand gestures
        base_gestures = {
            "👍": ("approval", GestureType.HAND),
            "👎": ("disapproval", GestureType.HAND),
            "✋": ("stop", GestureType.HAND),
            "👌": ("ok", GestureType.HAND),
            "🤝": ("agreement", GestureType.HAND),
            "👏": ("applause", GestureType.HAND),
            "🙏": ("thanks", GestureType.HAND),
            "🖐️": ("hand_open", GestureType.HAND),
            "✌️": ("peace", GestureType.HAND),
            "🤞": ("hope", GestureType.HAND),
        }

        for symbol, (meaning, gesture_type) in base_gestures.items():
            self.mappings[symbol] = SymbolMapping(
                symbol=symbol,
                meaning=meaning,
                gesture_type=gesture_type,
                context="base_vocabulary",
                confidence=0.9
            )

    def unlock(self, passphrase: str) -> bool:
        """Unlock the dictionary with user passphrase"""
        try:
            # Derive encryption key from passphrase
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.user_id.encode(),
                iterations=100000,
            )
            self.encryption_key = kdf.derive(passphrase.encode())
            self.is_locked = False

            # Try to load existing data
            self._load_encrypted()

            logger.info(f"Dictionary unlocked for user {self.user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to unlock dictionary: {e}")
            self.is_locked = True
            return False

    def lock(self):
        """Lock the dictionary and save encrypted data"""
        if not self.is_locked:
            self._save_encrypted()
            self.encryption_key = None
            self.is_locked = True
            logger.info(f"Dictionary locked for user {self.user_id}")

    def add_symbol(
        self,
        symbol: str,
        meaning: str,
        gesture_type: GestureType,
        context: str = "",
        gesture_sequence: Optional[List[str]] = None
    ) -> bool:
        """Add a new symbol mapping"""
        if self.is_locked:
            logger.warning("Cannot add symbol - dictionary is locked")
            return False

        # Create mapping
        mapping = SymbolMapping(
            symbol=symbol,
            meaning=meaning,
            gesture_type=gesture_type,
            context=context
        )

        # Store mapping
        self.mappings[symbol] = mapping

        # Create gesture pattern if sequence provided
        if gesture_sequence:
            pattern = GesturePattern(
                pattern_id=f"{symbol}_{len(self.gesture_patterns)}",
                gesture_sequence=gesture_sequence,
                timing=[0.2] * (len(gesture_sequence) - 1),  # Default timing
                matched_symbol=symbol
            )
            self.gesture_patterns[pattern.pattern_id] = pattern

        # Track evolution
        self.evolution_history.append({
            'action': 'add_symbol',
            'symbol': symbol,
            'timestamp': time.time()
        })

        logger.info(f"Added symbol mapping: {symbol} -> {meaning}")
        return True

    def get_meaning(self, symbol: str) -> Optional[str]:
        """Get the meaning of a symbol"""
        mapping = self.mappings.get(symbol)
        if mapping:
            # Update usage stats
            mapping.usage_count += 1
            mapping.last_used = time.time()
            return mapping.meaning
        return None

    def detect_gesture(
        self,
        gesture_sequence: List[str],
        timings: Optional[List[float]] = None
    ) -> Optional[str]:
        """Detect symbol from gesture sequence"""
        for pattern in self.gesture_patterns.values():
            if pattern.matches(gesture_sequence, timings or []):
                symbol = pattern.matched_symbol
                if symbol in self.mappings:
                    self.mappings[symbol].usage_count += 1
                    self.mappings[symbol].last_used = time.time()
                    return symbol
        return None

    def evolve_symbol(
        self,
        symbol: str,
        new_meaning: Optional[str] = None,
        feedback_score: float = 0.5
    ):
        """Evolve a symbol based on feedback"""
        if self.is_locked or symbol not in self.mappings:
            return

        mapping = self.mappings[symbol]

        # Track feedback
        if symbol not in self.feedback_scores:
            self.feedback_scores[symbol] = []
        self.feedback_scores[symbol].append(feedback_score)

        # Update confidence based on feedback
        avg_feedback = sum(self.feedback_scores[symbol]) / len(self.feedback_scores[symbol])
        mapping.confidence = 0.7 * mapping.confidence + 0.3 * avg_feedback

        # Update meaning if provided and feedback is positive
        if new_meaning and feedback_score > 0.7:
            old_meaning = mapping.meaning
            mapping.meaning = new_meaning
            mapping.evolution_history.append({
                'old_meaning': old_meaning,
                'new_meaning': new_meaning,
                'timestamp': time.time(),
                'feedback_score': feedback_score
            })

            logger.info(f"Evolved symbol {symbol}: {old_meaning} -> {new_meaning}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for the dictionary"""
        if self.is_locked:
            return {'status': 'locked'}

        total_symbols = len(self.mappings)
        total_usage = sum(m.usage_count for m in self.mappings.values())
        avg_confidence = sum(m.confidence for m in self.mappings.values()) / max(1, total_symbols)

        # Find most used symbols
        most_used = sorted(
            self.mappings.items(),
            key=lambda x: x[1].usage_count,
            reverse=True
        )[:5]

        return {
            'user_id': self.user_id,
            'total_symbols': total_symbols,
            'total_usage': total_usage,
            'average_confidence': avg_confidence,
            'gesture_patterns': len(self.gesture_patterns),
            'most_used_symbols': [
                {
                    'symbol': symbol,
                    'meaning': mapping.meaning,
                    'usage': mapping.usage_count
                }
                for symbol, mapping in most_used
            ],
            'evolution_events': len(self.evolution_history)
        }

    def export_public_symbols(self, confidence_threshold: float = 0.8) -> Dict[str, str]:
        """
        Export high-confidence symbols for universal exchange.
        Only exports symbols above confidence threshold with no personal context.
        """
        public_symbols = {}

        for symbol, mapping in self.mappings.items():
            # Only export high-confidence, non-personal symbols
            if (mapping.confidence >= confidence_threshold and
                mapping.context != "personal" and
                mapping.usage_count > 5):

                # Hash the meaning for privacy
                meaning_hash = hashlib.sha256(
                    f"{self.user_id}:{mapping.meaning}".encode()
                ).hexdigest()[:8]

                public_symbols[symbol] = meaning_hash

        return public_symbols

    def import_universal_symbols(self, universal_symbols: Dict[str, float]):
        """Import symbols from universal exchange with confidence scores"""
        if self.is_locked:
            return

        for symbol, confidence in universal_symbols.items():
            if symbol not in self.mappings and confidence > 0.6:
                # Add as tentative symbol
                self.add_symbol(
                    symbol=symbol,
                    meaning="universal_pending",
                    gesture_type=GestureType.COMPOSITE,
                    context="universal_exchange"
                )
                self.mappings[symbol].confidence = confidence

    def _save_encrypted(self):
        """Save dictionary to encrypted storage"""
        if not self.encryption_key:
            return

        try:
            # Prepare data
            data = {
                'mappings': {
                    symbol: mapping.to_dict()
                    for symbol, mapping in self.mappings.items()
                },
                'gesture_patterns': {
                    pid: asdict(pattern)
                    for pid, pattern in self.gesture_patterns.items()
                },
                'evolution_history': self.evolution_history,
                'feedback_scores': self.feedback_scores
            }

            # Encrypt
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(json.dumps(data).encode())

            # Save
            self.storage_path.write_bytes(encrypted_data)
            logger.info(f"Saved encrypted dictionary to {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to save encrypted dictionary: {e}")

    def _load_encrypted(self):
        """Load dictionary from encrypted storage"""
        if not self.encryption_key or not self.storage_path.exists():
            return

        try:
            # Load and decrypt
            encrypted_data = self.storage_path.read_bytes()
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data)

            # Restore mappings
            self.mappings = {
                symbol: SymbolMapping.from_dict(mapping_data)
                for symbol, mapping_data in data.get('mappings', {}).items()
            }

            # Restore patterns
            self.gesture_patterns = {
                pid: GesturePattern(**pattern_data)
                for pid, pattern_data in data.get('gesture_patterns', {}).items()
            }

            self.evolution_history = data.get('evolution_history', [])
            self.feedback_scores = data.get('feedback_scores', {})

            logger.info(f"Loaded {len(self.mappings)} symbols from encrypted storage")

        except Exception as e:
            logger.error(f"Failed to load encrypted dictionary: {e}")


# Demo usage
def demo_personal_dictionary():
    """Demonstrate personal symbol dictionary features"""

    # Create dictionary for user
    dictionary = PersonalSymbolDictionary("user_123")

    # Unlock with passphrase
    if dictionary.unlock("my_secure_passphrase"):
        print("✅ Dictionary unlocked")

        # Add custom gesture mapping
        dictionary.add_symbol(
            symbol="🎯",
            meaning="focus_mode",
            gesture_type=GestureType.HAND,
            context="productivity",
            gesture_sequence=["👆", "👆", "👏"]
        )

        # Add emotional gesture
        dictionary.add_symbol(
            symbol="💫",
            meaning="excitement",
            gesture_type=GestureType.COMPOSITE,
            context="emotion",
            gesture_sequence=["😊", "🙌", "✨"]
        )

        # Test gesture detection
        detected = dictionary.detect_gesture(["👆", "👆", "👏"])
        if detected:
            print(f"🎯 Detected symbol: {detected} -> {dictionary.get_meaning(detected)}")

        # Evolve symbol based on feedback
        dictionary.evolve_symbol("🎯", new_meaning="deep_focus", feedback_score=0.9)

        # Get statistics
        stats = dictionary.get_statistics()
        print(f"📊 Dictionary stats: {stats['total_symbols']} symbols, "
              f"{stats['total_usage']} total uses")

        # Export public symbols for universal exchange
        public = dictionary.export_public_symbols()
        print(f"🌍 Exported {len(public)} symbols for universal exchange")

        # Lock dictionary
        dictionary.lock()
        print("🔒 Dictionary locked and encrypted")


if __name__ == "__main__":
    demo_personal_dictionary()
