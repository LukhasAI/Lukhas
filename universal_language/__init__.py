"""
Universal Language (UL) - Personal Symbol Entropy System
=======================================================
Local secure mapping between personal symbols and Λ-meanings.
Provides additional entropy source for high-risk approvals.

System-wide guardrails applied:
1. All symbol mappings stored locally in encrypted store
2. Server only receives cryptographic proofs, never raw symbols
3. Symbol-meaning bindings use salted hashes for privacy
4. Composition challenges verify knowledge without exposure
5. Combined with GTΨ for multi-factor high-risk approvals

ACK GUARDRAILS
"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class SymbolType(Enum):
    """Types of personal symbols that can be bound"""

    STROKE = "stroke"  # Hand-drawn symbol
    EMOJI = "emoji"  # Unicode emoji or sequence
    WORD = "word"  # Personal word or phrase
    SOUND = "sound"  # Audio pattern (future)
    COLOR = "color"  # Color sequence
    RHYTHM = "rhythm"  # Tap/click rhythm
    GLYPH = "glyph"  # LUKHAS glyph token


class MeaningType(Enum):
    """Types of meanings symbols can represent"""

    EMOTION = "emotion"  # Emotional state (joy, calm, anger)
    ACTION = "action"  # Action concept (approve, reject, pause)
    IDENTITY = "identity"  # Identity aspect (self, work, family)
    CONCEPT = "concept"  # Abstract concept (truth, beauty, strength)
    LAMBDA = "lambda"  # Λ-meaning in LUKHAS system
    UNL = "unl"  # Universal Networking Language token


@dataclass
class PersonalSymbol:
    """A personal symbol bound to meaning (stored locally only)"""

    symbol_id: str
    symbol_type: SymbolType
    symbol_hash: str  # Hashed representation
    salt: str  # Random salt for hashing
    meaning_type: MeaningType
    meaning_value: str  # The actual meaning
    created_at: datetime
    last_used_at: Optional[datetime] = None
    use_count: int = 0
    quality_score: float = 0.0


class SymbolBinding(BaseModel):
    """Request to bind a symbol to meaning"""

    symbol_type: SymbolType = Field(..., description="Type of symbol")
    symbol_data: Any = Field(..., description="Raw symbol data (kept local)")
    meaning_type: MeaningType = Field(..., description="Type of meaning")
    meaning_value: str = Field(..., description="Meaning to bind")

    @validator("meaning_value")
    def validate_meaning(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Meaning value cannot be empty")
        return v.strip()


class CompositionChallenge(BaseModel):
    """Server-generated composition challenge"""

    challenge_id: str = Field(..., description="Unique challenge ID")
    composition: str = Field(..., description="Requested composition (e.g., 'calm + collapse')")
    operators: list[str] = Field(..., description="Operators in composition (+, -, *, /)")
    expected_symbols: int = Field(..., description="Number of symbols expected")
    expires_at: datetime = Field(..., description="Challenge expiration")
    nonce: str = Field(..., description="Cryptographic nonce")


class CompositionProof(BaseModel):
    """Proof of symbol composition knowledge"""

    challenge_id: str = Field(..., description="Challenge being answered")
    proof_hash: str = Field(..., description="Hash proof of composition")
    symbol_count: int = Field(..., description="Number of symbols used")
    computation_time_ms: float = Field(..., description="Time to compute proof")
    quality_score: float = Field(..., description="Quality of composition")


class ULSignature(BaseModel):
    """Universal Language signature for approval"""

    lid: str = Field(..., description="Canonical ΛID")
    action: str = Field(..., description="Action being approved")
    symbol_proofs: list[str] = Field(..., description="Symbol proof hashes")
    composition_proof: Optional[CompositionProof] = Field(
        None, description="Composition proof if challenged"
    )
    timestamp: datetime = Field(..., description="Signature timestamp")
    expires_at: datetime = Field(..., description="Signature expiration")


class SymbolEncoder(ABC):
    """Abstract encoder for different symbol types"""

    @abstractmethod
    def encode(self, symbol_data: Any) -> bytes:
        """Encode symbol data to bytes for hashing"""
        pass

    @abstractmethod
    def extract_features(self, symbol_data: Any) -> list[float]:
        """Extract numerical features for quality scoring"""
        pass


class EmojiEncoder(SymbolEncoder):
    """Encoder for emoji symbols"""

    def encode(self, symbol_data: Any) -> bytes:
        """Encode emoji or emoji sequence"""
        if isinstance(symbol_data, str):
            return symbol_data.encode("utf-8")
        elif isinstance(symbol_data, list):
            # List of emojis
            return "".join(symbol_data).encode("utf-8")
        else:
            raise ValueError("Emoji data must be string or list")

    def extract_features(self, symbol_data: Any) -> list[float]:
        """Extract features from emoji"""
        emoji_str = symbol_data if isinstance(symbol_data, str) else "".join(symbol_data)

        features = [
            len(emoji_str),  # Length
            len(set(emoji_str)),  # Unique characters
            emoji_str.count("😀") / len(emoji_str) if emoji_str else 0,  # Happiness ratio
            1.0 if any(ord(c) > 127462 for c in emoji_str) else 0.0,  # Has complex emoji
        ]

        return features


class WordEncoder(SymbolEncoder):
    """Encoder for word/phrase symbols"""

    def encode(self, symbol_data: Any) -> bytes:
        """Encode word or phrase"""
        if isinstance(symbol_data, str):
            # Normalize: lowercase, strip whitespace
            normalized = symbol_data.lower().strip()
            return normalized.encode("utf-8")
        else:
            raise ValueError("Word data must be string")

    def extract_features(self, symbol_data: Any) -> list[float]:
        """Extract features from word/phrase"""
        text = symbol_data.lower().strip()

        features = [
            len(text),  # Length
            text.count(" ") + 1,  # Word count
            len(set(text)),  # Unique characters
            sum(1 for c in text if c.isalpha()) / len(text) if text else 0,  # Letter ratio
        ]

        return features


class ColorEncoder(SymbolEncoder):
    """Encoder for color sequence symbols"""

    def encode(self, symbol_data: Any) -> bytes:
        """Encode color sequence"""
        if isinstance(symbol_data, list):
            # List of RGB tuples or hex codes
            color_str = json.dumps(symbol_data, sort_keys=True)
            return color_str.encode("utf-8")
        else:
            raise ValueError("Color data must be list of colors")

    def extract_features(self, symbol_data: Any) -> list[float]:
        """Extract features from color sequence"""
        features = [
            len(symbol_data),  # Number of colors
            len(set(map(tuple, symbol_data))),  # Unique colors
            1.0,  # Placeholder for color harmony
            1.0,  # Placeholder for contrast
        ]

        return features


def create_symbol_encoder(symbol_type: SymbolType) -> SymbolEncoder:
    """Factory for symbol encoders"""
    encoders = {
        SymbolType.EMOJI: EmojiEncoder(),
        SymbolType.WORD: WordEncoder(),
        SymbolType.COLOR: ColorEncoder(),
        # Stroke and other types would use their specific encoders
    }

    return encoders.get(symbol_type, WordEncoder())  # Default to word encoder


def hash_symbol(symbol_data: Any, symbol_type: SymbolType, salt: str) -> str:
    """Hash symbol data with salt for privacy"""
    encoder = create_symbol_encoder(symbol_type)
    encoded_data = encoder.encode(symbol_data)

    hasher = hashlib.sha256()
    hasher.update(salt.encode())
    hasher.update(encoded_data)

    return hasher.hexdigest()


def calculate_symbol_quality(symbol_data: Any, symbol_type: SymbolType) -> float:
    """Calculate quality score for symbol"""
    encoder = create_symbol_encoder(symbol_type)
    features = encoder.extract_features(symbol_data)

    if not features:
        return 0.0

    # Simple quality based on complexity
    complexity = sum(features) / len(features)
    quality = min(1.0, complexity / 10.0)  # Normalize to [0, 1]

    return quality


def compose_symbol_proof(symbols: list[PersonalSymbol], operators: list[str], nonce: str) -> str:
    """
    Create cryptographic proof of symbol composition.

    This proves knowledge of symbols without revealing them.
    """
    hasher = hashlib.sha256()
    hasher.update(nonce.encode())

    # Include symbol hashes in order
    for i, symbol in enumerate(symbols):
        hasher.update(symbol.symbol_hash.encode())

        # Include operator if not last symbol
        if i < len(operators):
            hasher.update(operators[i].encode())

    return hasher.hexdigest()


class CompositionOperator(Enum):
    """Operators for symbol composition"""

    ADD = "+"  # Combine/merge meanings
    SUBTRACT = "-"  # Remove/negate meaning
    MULTIPLY = "*"  # Intensify meaning
    DIVIDE = "/"  # Dilute/soften meaning
    TRANSFORM = "~"  # Transform/invert meaning
    SEQUENCE = "→"  # Sequential progression


def parse_composition(composition_str: str) -> tuple[list[str], list[str]]:
    """
    Parse composition string into meanings and operators.

    Example: "calm + collapse" -> (["calm", "collapse"], ["+"])
    """
    # Define operator symbols
    operators = ["+", "-", "*", "/", "~", "→"]

    meanings = []
    ops = []
    current_meaning = ""

    for char in composition_str:
        if char in operators:
            if current_meaning.strip():
                meanings.append(current_meaning.strip())
                current_meaning = ""
            ops.append(char)
        else:
            current_meaning += char

    # Add last meaning
    if current_meaning.strip():
        meanings.append(current_meaning.strip())

    return meanings, ops


# High-risk actions that benefit from ul_entropy
UL_ENHANCED_ACTIONS = {
    "grant_admin_scope": {
        "description": "Grant administrative capabilities",
        "required_symbols": 2,
        "composition_required": True,
    },
    "delete_all_data": {
        "description": "Delete all user data permanently",
        "required_symbols": 3,
        "composition_required": True,
    },
    "transfer_ownership": {
        "description": "Transfer ownership of resources",
        "required_symbols": 2,
        "composition_required": True,
    },
    "emergency_lockdown": {
        "description": "Emergency system lockdown",
        "required_symbols": 1,
        "composition_required": False,
    },
}


def requires_ul_entropy(action: str) -> bool:
    """Check if action benefits from UL entropy"""
    return action in UL_ENHANCED_ACTIONS


def get_required_symbols(action: str) -> int:
    """Get number of symbols required for action"""
    if action in UL_ENHANCED_ACTIONS:
        return UL_ENHANCED_ACTIONS[action]["required_symbols"]
    return 0


def requires_composition(action: str) -> bool:
    """Check if action requires symbol composition"""
    if action in UL_ENHANCED_ACTIONS:
        return UL_ENHANCED_ACTIONS[action]["composition_required"]
    return False


__all__ = [
    "UL_ENHANCED_ACTIONS",
    "ColorEncoder",
    "CompositionChallenge",
    "CompositionOperator",
    "CompositionProof",
    "EmojiEncoder",
    "MeaningType",
    "PersonalSymbol",
    "SymbolBinding",
    "SymbolEncoder",
    "SymbolType",
    "ULSignature",
    "WordEncoder",
    "calculate_symbol_quality",
    "compose_symbol_proof",
    "create_symbol_encoder",
    "get_required_symbols",
    "hash_symbol",
    "parse_composition",
    "requires_composition",
    "requires_ul_entropy",
]
