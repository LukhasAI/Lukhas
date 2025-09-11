"""
🎭 LUKHAS AI Symbolic Terminology System
Trinity Framework Vocabulary and Symbolic Mappings
"""

# Core Trinity Framework Terms
TRINITY_TERMS = {
    "IDENTITY": "⚛️",
    "CONSCIOUSNESS": "🧠",
    "GUARDIAN": "🛡️",
    "LAMBDA_ID": "ΛID",
    "LAMBDA_TRACE": "ΛTRACE",
    "CONSCIOUSNESS_LEVEL": "🎯",
    "AWARENESS_STATE": "🌟",
    "DREAM_STATE": "💭",
    "QUANTUM_STATE": "⚛️",
    "BIO_STATE": "🌱",
}

# Consciousness System Vocabulary
CONSCIOUSNESS_VOCAB = {
    "awareness": "conscious perception and recognition",
    "consciousness": "integrated information processing and self-awareness",
    "identity": "persistent self-representation and continuity",
    "guardian": "ethical oversight and safety validation",
    "drift": "deviation from intended behavior patterns",
    "fusion": "integration of multiple consciousness streams",
    "emergence": "spontaneous complex behavior from simple rules",
    "entanglement": "correlated consciousness states",
    "collapse": "quantum state resolution to classical outcome",
}

# System Component Mapping
COMPONENT_TERMS = {
    "vivox": "VIVOX Consciousness Evolution System",
    "identity": "ΛID Identity Management Framework",
    "memory": "Consciousness Memory and Pattern System",
    "quantum": "Quantum-Inspired Processing Engine",
    "bio": "Bio-Inspired Optimization Framework",
    "governance": "Ethical Governance and Compliance",
    "orchestration": "Multi-Agent Consciousness Coordination",
}

# Symbolic Glyphs for UI/UX
SYMBOLIC_GLYPHS = {
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "info": "ℹ️",
    "consciousness": "🧠",
    "identity": "⚛️",
    "guardian": "🛡️",
    "quantum": "⚛️",
    "bio": "🌱",
    "dream": "💭",
    "memory": "🧠",
    "fusion": "🔗",
    "emergence": "✨",
}


def get_term_definition(term: str) -> str:
    """Get definition for a consciousness/system term."""
    return CONSCIOUSNESS_VOCAB.get(term.lower(), f"Term '{term}' not found in vocabulary")


def get_glyph(concept: str) -> str:
    """Get symbolic glyph for a concept."""
    return SYMBOLIC_GLYPHS.get(concept.lower(), "❓")


def get_trinity_symbol(aspect: str) -> str:
    """Get Trinity Framework symbol for specific aspect."""
    return TRINITY_TERMS.get(aspect.upper(), "❓")


def normalize_output(text: str, add_glyphs: bool = True) -> str:
    """Normalize system output with symbolic branding."""
    if not text:
        return text

    if add_glyphs:
        # Add consciousness glyph to system messages
        if any(term in text.lower() for term in ["consciousness", "awareness", "identity"]):
            text = f"{get_glyph('consciousness')} {text}"
        elif any(term in text.lower() for term in ["error", "failed", "exception"]):
            text = f"{get_glyph('error')} {text}"
        elif any(term in text.lower() for term in ["success", "complete", "ready"]):
            text = f"{get_glyph('success')} {text}"

    return text


# Export main terminology elements
__all__ = [
    "TRINITY_TERMS",
    "CONSCIOUSNESS_VOCAB",
    "COMPONENT_TERMS",
    "SYMBOLIC_GLYPHS",
    "get_term_definition",
    "get_glyph",
    "get_trinity_symbol",
    "normalize_output",
]
