"""
LUKHAS AI Universal Language - Core Engine
Multi-modal symbolic communication processing
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class ModalityType(Enum):
    """Types of communication modalities"""
    TEXTUAL = "textual"
    VISUAL = "visual"
    SYMBOLIC = "symbolic"
    GESTURAL = "gestural"
    MATHEMATICAL = "mathematical"
    EMOTIONAL = "emotional"
    TEMPORAL = "temporal"

class GlyphCategory(Enum):
    """Categories of glyphs in Universal Language"""
    CONCEPT = "concept"
    ACTION = "action"
    RELATIONSHIP = "relationship"
    MODIFIER = "modifier"
    STRUCTURAL = "structural"
    TEMPORAL = "temporal"
    EMOTIONAL = "emotional"

@dataclass
class ULGlyph:
    """Universal Language glyph representation"""
    symbol: str
    meaning: str
    category: GlyphCategory
    modality: ModalityType
    complexity: float = 0.5  # 0.0 = simple, 1.0 = complex
    frequency: float = 0.5   # Usage frequency
    associations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ULExpression:
    """Complete Universal Language expression"""
    glyphs: List[ULGlyph]
    structure: str  # Grammar structure
    meaning: str
    confidence: float = 0.8
    modalities: List[ModalityType] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class UniversalLanguage:
    """Core Universal Language processing engine"""
    
    def __init__(self):
        self.glyph_vocabulary: Dict[str, ULGlyph] = {}
        self.expression_patterns: Dict[str, str] = {}
        self.translation_cache: Dict[str, str] = {}
        self.active_contexts: List[str] = []
        
        # Trinity integration
        self.trinity_aligned = True
        
        # Initialize with basic vocabulary
        self._initialize_core_vocabulary()
        self._initialize_patterns()
    
    def _initialize_core_vocabulary(self):
        """Initialize core Universal Language vocabulary"""
        core_glyphs = [
            # Trinity Framework glyphs
            ULGlyph("⚛️", "identity", GlyphCategory.CONCEPT, ModalityType.SYMBOLIC, 
                   complexity=0.9, frequency=0.8, associations=["self", "core", "essence"]),
            ULGlyph("🧠", "consciousness", GlyphCategory.CONCEPT, ModalityType.SYMBOLIC,
                   complexity=0.9, frequency=0.8, associations=["awareness", "thought", "mind"]),
            ULGlyph("🛡️", "guardian", GlyphCategory.CONCEPT, ModalityType.SYMBOLIC,
                   complexity=0.8, frequency=0.7, associations=["protection", "ethics", "safety"]),
            
            # Basic concepts
            ULGlyph("◯", "existence", GlyphCategory.CONCEPT, ModalityType.SYMBOLIC,
                   complexity=0.3, frequency=0.9, associations=["being", "presence", "reality"]),
            ULGlyph("→", "causation", GlyphCategory.RELATIONSHIP, ModalityType.SYMBOLIC,
                   complexity=0.4, frequency=0.8, associations=["leads to", "causes", "results"]),
            ULGlyph("△", "change", GlyphCategory.ACTION, ModalityType.SYMBOLIC,
                   complexity=0.5, frequency=0.7, associations=["transform", "evolve", "modify"]),
            
            # Temporal markers
            ULGlyph("↻", "cycle", GlyphCategory.TEMPORAL, ModalityType.SYMBOLIC,
                   complexity=0.4, frequency=0.6, associations=["repeat", "periodic", "rhythm"]),
            ULGlyph("⌛", "duration", GlyphCategory.TEMPORAL, ModalityType.SYMBOLIC,
                   complexity=0.3, frequency=0.7, associations=["time", "span", "period"]),
            
            # Emotional markers
            ULGlyph("♡", "positive_affect", GlyphCategory.EMOTIONAL, ModalityType.EMOTIONAL,
                   complexity=0.2, frequency=0.8, associations=["joy", "love", "happiness"]),
            ULGlyph("⚡", "intensity", GlyphCategory.MODIFIER, ModalityType.EMOTIONAL,
                   complexity=0.3, frequency=0.6, associations=["strong", "powerful", "energetic"]),
            
            # Structural elements
            ULGlyph("｜", "boundary", GlyphCategory.STRUCTURAL, ModalityType.SYMBOLIC,
                   complexity=0.2, frequency=0.8, associations=["separation", "limit", "edge"]),
            ULGlyph("∞", "infinite", GlyphCategory.MODIFIER, ModalityType.MATHEMATICAL,
                   complexity=0.6, frequency=0.4, associations=["endless", "unlimited", "eternal"]),
        ]
        
        for glyph in core_glyphs:
            self.glyph_vocabulary[glyph.symbol] = glyph
    
    def _initialize_patterns(self):
        """Initialize expression patterns"""
        self.expression_patterns = {
            "trinity_declaration": "⚛️ 🧠 🛡️",  # Identity + Consciousness + Guardian
            "causal_chain": "A → B → C",          # Causation sequence
            "temporal_cycle": "A ↻ B ⌛ C",       # Cyclical temporal pattern
            "emotional_intensity": "♡ ⚡ A",      # Positive intense emotion about A
            "bounded_concept": "｜ A ｜",         # Bounded/defined concept
            "infinite_potential": "A ∞ B",       # Infinite relationship
        }
    
    def add_glyph(self, glyph: ULGlyph) -> bool:
        """Add new glyph to vocabulary"""
        if glyph.symbol not in self.glyph_vocabulary:
            self.glyph_vocabulary[glyph.symbol] = glyph
            return True
        return False
    
    def parse_expression(self, expression: str) -> ULExpression:
        """Parse Universal Language expression"""
        # Simple parsing - in production would be much more sophisticated
        symbols = expression.split()
        
        parsed_glyphs = []
        unknown_symbols = []
        
        for symbol in symbols:
            if symbol in self.glyph_vocabulary:
                parsed_glyphs.append(self.glyph_vocabulary[symbol])
            else:
                # Create placeholder for unknown symbol
                unknown_glyph = ULGlyph(
                    symbol=symbol,
                    meaning=f"unknown_{symbol}",
                    category=GlyphCategory.CONCEPT,
                    modality=ModalityType.TEXTUAL,
                    complexity=0.1,
                    frequency=0.1
                )
                parsed_glyphs.append(unknown_glyph)
                unknown_symbols.append(symbol)
        
        # Determine structure
        structure = self._analyze_structure(expression)
        
        # Generate meaning
        meaning = self._generate_meaning(parsed_glyphs, structure)
        
        # Calculate confidence
        confidence = max(0.1, 1.0 - (len(unknown_symbols) / max(len(symbols), 1)) * 0.8)
        
        # Determine modalities
        modalities = list(set(glyph.modality for glyph in parsed_glyphs))
        
        return ULExpression(
            glyphs=parsed_glyphs,
            structure=structure,
            meaning=meaning,
            confidence=confidence,
            modalities=modalities
        )
    
    def _analyze_structure(self, expression: str) -> str:
        """Analyze grammatical structure of expression"""
        # Check against known patterns
        for pattern_name, pattern in self.expression_patterns.items():
            if self._matches_pattern(expression, pattern):
                return pattern_name
        
        # Fallback to simple structure analysis
        symbols = expression.split()
        if len(symbols) == 1:
            return "single_concept"
        elif len(symbols) == 2:
            return "binary_relation"
        elif len(symbols) == 3:
            return "trinity_structure"
        else:
            return "complex_expression"
    
    def _matches_pattern(self, expression: str, pattern: str) -> bool:
        """Check if expression matches a pattern"""
        # Simple pattern matching - in production would use proper grammar
        expr_symbols = set(expression.split())
        pattern_symbols = set(pattern.split())
        
        # Check if pattern symbols are subset of expression symbols
        return pattern_symbols.issubset(expr_symbols)
    
    def _generate_meaning(self, glyphs: List[ULGlyph], structure: str) -> str:
        """Generate semantic meaning from glyphs and structure"""
        if not glyphs:
            return "empty_expression"
        
        if structure == "trinity_declaration":
            return "Trinity Framework alignment: Identity, Consciousness, Guardian"
        elif structure == "single_concept":
            return f"Concept: {glyphs[0].meaning}"
        elif structure == "binary_relation":
            if len(glyphs) >= 2:
                return f"Relationship: {glyphs[0].meaning} relates to {glyphs[1].meaning}"
        elif structure == "causal_chain":
            return "Causal sequence of events"
        
        # Fallback to concatenation
        meanings = [glyph.meaning for glyph in glyphs]
        return f"Expression combining: {', '.join(meanings)}"
    
    def generate_expression(self, intent: str, modality: ModalityType = ModalityType.SYMBOLIC) -> ULExpression:
        """Generate Universal Language expression for given intent"""
        # Simple generation based on intent keywords
        intent_lower = intent.lower()
        
        selected_glyphs = []
        
        # Trinity keywords
        if any(word in intent_lower for word in ["trinity", "framework", "core"]):
            selected_glyphs.extend([
                self.glyph_vocabulary["⚛️"],
                self.glyph_vocabulary["🧠"],
                self.glyph_vocabulary["🛡️"]
            ])
        
        # Causation keywords
        elif any(word in intent_lower for word in ["cause", "leads", "result"]):
            if "→" in self.glyph_vocabulary:
                selected_glyphs.append(self.glyph_vocabulary["→"])
        
        # Temporal keywords
        elif any(word in intent_lower for word in ["time", "cycle", "repeat"]):
            if "↻" in self.glyph_vocabulary:
                selected_glyphs.append(self.glyph_vocabulary["↻"])
        
        # Emotional keywords
        elif any(word in intent_lower for word in ["love", "joy", "positive"]):
            if "♡" in self.glyph_vocabulary:
                selected_glyphs.append(self.glyph_vocabulary["♡"])
        
        # Default to existence
        if not selected_glyphs:
            if "◯" in self.glyph_vocabulary:
                selected_glyphs.append(self.glyph_vocabulary["◯"])
        
        # Create expression
        expression_str = " ".join(glyph.symbol for glyph in selected_glyphs)
        meaning = f"Generated expression for intent: {intent}"
        
        return ULExpression(
            glyphs=selected_glyphs,
            structure=self._analyze_structure(expression_str),
            meaning=meaning,
            confidence=0.7,
            modalities=[modality]
        )
    
    def translate_to_natural(self, ul_expression: ULExpression) -> str:
        """Translate Universal Language to natural language"""
        if ul_expression.structure == "trinity_declaration":
            return "The Trinity Framework encompasses Identity, Consciousness, and Guardian principles."
        
        # Simple translation
        glyph_meanings = [glyph.meaning for glyph in ul_expression.glyphs]
        
        if len(glyph_meanings) == 1:
            return f"This represents {glyph_meanings[0]}."
        elif len(glyph_meanings) == 2:
            return f"This expresses a relationship between {glyph_meanings[0]} and {glyph_meanings[1]}."
        else:
            return f"This is a complex expression involving: {', '.join(glyph_meanings)}."
    
    def translate_from_natural(self, natural_text: str) -> ULExpression:
        """Translate natural language to Universal Language"""
        # Cache check
        if natural_text in self.translation_cache:
            cached_expression = self.translation_cache[natural_text]
            return self.parse_expression(cached_expression)
        
        # Simple keyword-based translation
        text_lower = natural_text.lower()
        
        # Generate expression based on content
        expression = self.generate_expression(natural_text, ModalityType.TEXTUAL)
        
        # Cache result
        expression_str = " ".join(glyph.symbol for glyph in expression.glyphs)
        self.translation_cache[natural_text] = expression_str
        
        return expression
    
    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """Get statistics about current vocabulary"""
        categories = {}
        modalities = {}
        
        for glyph in self.glyph_vocabulary.values():
            cat = glyph.category.value
            mod = glyph.modality.value
            
            categories[cat] = categories.get(cat, 0) + 1
            modalities[mod] = modalities.get(mod, 0) + 1
        
        return {
            "total_glyphs": len(self.glyph_vocabulary),
            "categories": categories,
            "modalities": modalities,
            "avg_complexity": sum(g.complexity for g in self.glyph_vocabulary.values()) / len(self.glyph_vocabulary),
            "trinity_aligned": self.trinity_aligned
        }
    
    def trinity_sync(self) -> Dict[str, Any]:
        """Synchronize with Trinity Framework"""
        return {
            'identity': '⚛️',
            'consciousness': '🧠',
            'guardian': '🛡️',
            'ul_vocabulary_size': len(self.glyph_vocabulary),
            'active_modalities': len(set(g.modality for g in self.glyph_vocabulary.values())),
            'expression_patterns': len(self.expression_patterns)
        }

# Singleton instance
_universal_language = None

def get_universal_language() -> UniversalLanguage:
    """Get or create Universal Language singleton"""
    global _universal_language
    if _universal_language is None:
        _universal_language = UniversalLanguage()
    return _universal_language