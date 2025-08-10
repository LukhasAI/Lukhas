"""
GLYPH Engine for Universal Language
====================================

Consolidates GLYPH token processing from /core/glyph/glyphs.py
and various symbolic implementations.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


# Core GLYPH mappings from /core/glyph/glyphs.py
GLYPH_MAP_VERSION = "2.0.0"  # Unified version

GLYPH_MAP: Dict[str, str] = {
    # Core symbolic glyphs
    "☯": "Bifurcation Point / Duality / Choice",
    "🪞": "Symbolic Self-Reflection / Introspection",
    "🌪️": "Collapse Risk / High Instability / Chaotic State",
    "🔁": "Dream Echo Loop / Recursive Feedback / Iterative Refinement",
    "💡": "Insight / Revelation / Novel Idea",
    "🔗": "Symbolic Link / Connection / Dependency",
    "🛡️": "Safety Constraint / Ethical Boundary / Protection",
    "🌱": "Emergent Property / Growth / New Potential",
    "❓": "Ambiguity / Uncertainty / Query Point",
    "👁️": "Observation / Monitoring / Awareness State",
    
    # Navigation and tracking
    "🧭": "Path Tracking / Logic Navigation / Trace Route",
    "🌊": "Entropic Divergence / Gradual Instability / Drift Point",
    "⚠️": "Caution / Potential Risk / Audit Needed",
    "📝": "Developer Note / Insight / Anchor Comment",
    "🤖": "AI Inference / Machine Reasoning / Automated Logic",
    "🏛️": "Core Architecture / Structural Foundation / System Pillar",
    
    # Biological and consciousness
    "🧠": "Consciousness / Cognitive Process / Mental State",
    "💭": "Thought / Mental Process / Cognition",
    "🫀": "Biological Core / Life Process / Vital System",
    "🧬": "Genetic / Evolutionary / Adaptive Process",
    "🦋": "Transformation / Metamorphosis / Evolution",
    
    # Emotional spectrum
    "😊": "Happiness / Joy / Positive Emotion",
    "😢": "Sadness / Sorrow / Negative Emotion",
    "😡": "Anger / Frustration / Intense Emotion",
    "😨": "Fear / Anxiety / Uncertainty",
    "😍": "Love / Affection / Connection",
    "🤔": "Contemplation / Thinking / Processing",
    
    # Action and state
    "✨": "Creation / Generation / Manifestation",
    "🔥": "Energy / Intensity / Active Process",
    "❄️": "Cooling / Slowing / Passive State",
    "⚡": "Sudden Change / Flash / Instant Action",
    "🌟": "Excellence / Peak / Optimal State",
    "🎯": "Target / Goal / Objective",
    
    # System states
    "🟢": "Active / Running / Operational",
    "🟡": "Warning / Caution / Transitional",
    "🔴": "Stop / Error / Critical",
    "🔵": "Information / Neutral / Stable",
    "⚫": "Dormant / Inactive / Null State",
    
    # Quantum and abstract
    "♾️": "Infinity / Unbounded / Eternal",
    "🌀": "Vortex / Spiral / Recursive Pattern",
    "🔮": "Prediction / Future State / Possibility",
    "⚛️": "Quantum / Atomic / Fundamental",
    "🌌": "Universal / Cosmic / All-Encompassing",
    
    # Communication
    "📡": "Transmission / Signal / Communication",
    "📨": "Message / Information / Data",
    "🔊": "Voice / Sound / Audio Signal",
    "👁️‍🗨️": "Visual Communication / Image / Vision",
    "🤝": "Agreement / Consensus / Cooperation",
    
    # Memory and time
    "💾": "Storage / Memory / Persistence",
    "⏰": "Time / Temporal / Schedule",
    "🔄": "Cycle / Repetition / Loop",
    "⏸️": "Pause / Hold / Suspension",
    "▶️": "Play / Continue / Progress"
}


class GLYPHType(Enum):
    """Types of GLYPH tokens"""
    SYMBOLIC = "symbolic"  # Visual symbol
    TEXTUAL = "textual"  # Text representation
    COMPOSITE = "composite"  # Multiple glyphs
    DYNAMIC = "dynamic"  # Changes based on context
    ENCRYPTED = "encrypted"  # Hidden meaning


@dataclass
class GLYPHToken:
    """
    Individual GLYPH token representation.
    
    Represents a single meaningful unit in the GLYPH system.
    """
    glyph: str  # The visual glyph (emoji/symbol)
    meaning: str  # The semantic meaning
    token_type: GLYPHType = GLYPHType.SYMBOLIC
    context: Optional[str] = None
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Auto-populate meaning from GLYPH_MAP if not provided
        if not self.meaning and self.glyph in GLYPH_MAP:
            self.meaning = GLYPH_MAP[self.glyph]
    
    def hash(self) -> str:
        """Generate hash for this GLYPH token"""
        content = f"{self.glyph}:{self.meaning}:{self.context}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "glyph": self.glyph,
            "meaning": self.meaning,
            "type": self.token_type.value,
            "context": self.context,
            "weight": self.weight,
            "metadata": self.metadata
        }


@dataclass
class GLYPHSequence:
    """
    Sequence of GLYPH tokens forming a message or concept.
    """
    tokens: List[GLYPHToken]
    sequence_id: Optional[str] = None
    entropy_bits: float = 0.0
    
    def __post_init__(self):
        if not self.sequence_id:
            self.sequence_id = self.generate_id()
        if self.entropy_bits == 0.0:
            self.entropy_bits = self.calculate_entropy()
    
    def generate_id(self) -> str:
        """Generate unique sequence ID"""
        token_hashes = [t.hash() for t in self.tokens]
        combined = "".join(token_hashes)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def calculate_entropy(self) -> float:
        """Calculate total entropy of the sequence"""
        # Each unique glyph adds entropy
        unique_glyphs = set(t.glyph for t in self.tokens)
        base_entropy = len(unique_glyphs) * 16.0  # 16 bits per unique glyph
        
        # Sequence length adds entropy
        sequence_entropy = len(self.tokens) * 4.0  # 4 bits per position
        
        return base_entropy + sequence_entropy
    
    def to_string(self) -> str:
        """Convert sequence to string representation"""
        return "".join(t.glyph for t in self.tokens)
    
    def to_meaning(self) -> str:
        """Convert sequence to meaning representation"""
        return " → ".join(t.meaning for t in self.tokens if t.meaning)


class GLYPHEngine:
    """
    Main GLYPH processing engine.
    
    Handles GLYPH token creation, parsing, and manipulation.
    """
    
    def __init__(self):
        self.glyph_map = GLYPH_MAP.copy()
        self.custom_glyphs: Dict[str, str] = {}
        self.glyph_cache: Dict[str, GLYPHToken] = {}
        logger.info(f"GLYPH Engine initialized with {len(self.glyph_map)} core glyphs")
    
    def register_custom_glyph(self, glyph: str, meaning: str) -> bool:
        """Register a custom GLYPH mapping"""
        try:
            if glyph in self.glyph_map:
                logger.warning(f"Overriding existing GLYPH: {glyph}")
            
            self.custom_glyphs[glyph] = meaning
            self.glyph_map[glyph] = meaning
            
            # Clear cache for this glyph
            if glyph in self.glyph_cache:
                del self.glyph_cache[glyph]
            
            logger.info(f"Registered custom GLYPH: {glyph} → {meaning}")
            return True
        except Exception as e:
            logger.error(f"Failed to register custom GLYPH: {e}")
            return False
    
    def create_token(self, glyph: str, meaning: Optional[str] = None,
                    context: Optional[str] = None) -> GLYPHToken:
        """Create a GLYPH token"""
        # Check cache first
        cache_key = f"{glyph}:{meaning}:{context}"
        if cache_key in self.glyph_cache:
            return self.glyph_cache[cache_key]
        
        # Look up meaning if not provided
        if not meaning:
            meaning = self.glyph_map.get(glyph, "Unknown")
        
        token = GLYPHToken(
            glyph=glyph,
            meaning=meaning,
            context=context
        )
        
        # Cache the token
        self.glyph_cache[cache_key] = token
        
        return token
    
    def parse_string(self, text: str) -> GLYPHSequence:
        """Parse a string to extract GLYPH tokens"""
        tokens = []
        
        for char in text:
            if char in self.glyph_map:
                token = self.create_token(char)
                tokens.append(token)
            elif len(char) > 1:  # Multi-character emoji
                # Try to find in glyph map
                if char in self.glyph_map:
                    token = self.create_token(char)
                    tokens.append(token)
        
        return GLYPHSequence(tokens=tokens)
    
    def create_sequence(self, glyphs: List[str], 
                       meanings: Optional[List[str]] = None) -> GLYPHSequence:
        """Create a GLYPH sequence from a list of glyphs"""
        tokens = []
        
        for i, glyph in enumerate(glyphs):
            meaning = meanings[i] if meanings and i < len(meanings) else None
            token = self.create_token(glyph, meaning)
            tokens.append(token)
        
        return GLYPHSequence(tokens=tokens)
    
    def translate_to_glyphs(self, concepts: List[str]) -> GLYPHSequence:
        """Translate concepts to GLYPH representation"""
        tokens = []
        
        for concept in concepts:
            # Find matching GLYPH for concept
            glyph = self.find_glyph_for_concept(concept)
            if glyph:
                token = self.create_token(glyph)
                tokens.append(token)
            else:
                # Use a default unknown glyph
                token = GLYPHToken(
                    glyph="❓",
                    meaning=concept,
                    token_type=GLYPHType.TEXTUAL
                )
                tokens.append(token)
        
        return GLYPHSequence(tokens=tokens)
    
    def find_glyph_for_concept(self, concept: str) -> Optional[str]:
        """Find the best matching GLYPH for a concept"""
        concept_lower = concept.lower()
        
        # Direct match
        for glyph, meaning in self.glyph_map.items():
            if concept_lower in meaning.lower():
                return glyph
        
        # Partial match
        for glyph, meaning in self.glyph_map.items():
            meaning_words = meaning.lower().split()
            if any(word in concept_lower for word in meaning_words):
                return glyph
        
        return None
    
    def combine_sequences(self, *sequences: GLYPHSequence) -> GLYPHSequence:
        """Combine multiple GLYPH sequences"""
        all_tokens = []
        for seq in sequences:
            all_tokens.extend(seq.tokens)
        
        return GLYPHSequence(tokens=all_tokens)
    
    def filter_by_type(self, sequence: GLYPHSequence, 
                      token_type: GLYPHType) -> GLYPHSequence:
        """Filter GLYPH sequence by token type"""
        filtered_tokens = [t for t in sequence.tokens if t.token_type == token_type]
        return GLYPHSequence(tokens=filtered_tokens)
    
    def get_entropy(self, sequence: GLYPHSequence) -> float:
        """Calculate entropy of a GLYPH sequence"""
        return sequence.entropy_bits
    
    def export_glyph_map(self) -> Dict[str, Any]:
        """Export the current GLYPH map including custom glyphs"""
        return {
            "version": GLYPH_MAP_VERSION,
            "core_glyphs": {k: v for k, v in GLYPH_MAP.items()},
            "custom_glyphs": self.custom_glyphs,
            "total_glyphs": len(self.glyph_map)
        }
    
    def import_glyph_map(self, glyph_data: Dict[str, Any]) -> bool:
        """Import a GLYPH map"""
        try:
            # Import custom glyphs
            if "custom_glyphs" in glyph_data:
                for glyph, meaning in glyph_data["custom_glyphs"].items():
                    self.register_custom_glyph(glyph, meaning)
            
            logger.info(f"Imported GLYPH map with {len(self.custom_glyphs)} custom glyphs")
            return True
        except Exception as e:
            logger.error(f"Failed to import GLYPH map: {e}")
            return False


# Singleton instance
_glyph_engine_instance = None


def get_glyph_engine() -> GLYPHEngine:
    """Get or create the singleton GLYPH Engine instance"""
    global _glyph_engine_instance
    if _glyph_engine_instance is None:
        _glyph_engine_instance = GLYPHEngine()
    return _glyph_engine_instance


# Export commonly used GLYPH constants
class GLYPHConstants:
    """Common GLYPH constants for easy access"""
    # States
    ACTIVE = "🟢"
    WARNING = "🟡"
    ERROR = "🔴"
    INFO = "🔵"
    DORMANT = "⚫"
    
    # Emotions
    HAPPY = "😊"
    SAD = "😢"
    ANGRY = "😡"
    FEARFUL = "😨"
    LOVING = "😍"
    THINKING = "🤔"
    
    # Actions
    CREATE = "✨"
    LINK = "🔗"
    PROTECT = "🛡️"
    GROW = "🌱"
    OBSERVE = "👁️"
    
    # System
    BRAIN = "🧠"
    QUANTUM = "⚛️"
    INFINITY = "♾️"
    CYCLE = "🔄"
    
    # Risk
    COLLAPSE = "🌪️"
    DRIFT = "🌊"
    CAUTION = "⚠️"