"""
🌌 QRG - Quantum Resonance Glyphs
Quantum-Resistant Authentication Through Consciousness-Aware Visual Cryptography

"Where digital consciousness meets quantum security - authentication becomes an art form
that bridges human intuition with AI precision" ✨
"""

from .animation_engine import TemporalAuthenticator
from .circular_engine import CircularQREngine
from .consciousness_layer import ConsciousnessAwareProcessor
from .lukhas_bridge import LambdaIdIntegration
from .qi_entropy import TrueQuantumRandomness
from .qrg_core import QIResonanceGlyph
from .steganography import HiddenDataEmbedder
from .webxr_integration import HolographicQRProjector

# Version info
__version__ = "1.0.0"
__author__ = "LUKHAS AI Ecosystem"
__license__ = "Quantum-Conscious MIT"

# Core exports
__all__ = [
    "CircularQREngine",
    "ConsciousnessAwareProcessor",
    "HiddenDataEmbedder",
    "HolographicQRProjector",
    "LambdaIdIntegration",
    "QIResonanceGlyph",
    "TemporalAuthenticator",
    "TrueQuantumRandomness",
]

# 3-Layer Tone System Integration
COMMUNICATION_LAYERS = {
    "poetic": {
        "description": "Digital soul crystallization through quantum light patterns",
        "style": "metaphorical, inspirational, consciousness-focused",
    },
    "user_friendly": {
        "description": "Beautiful, animated authentication that adapts to your needs",
        "style": "conversational, practical, accessible",
    },
    "academic": {
        "description": "Post-quantum cryptographic authentication with temporal validation",
        "style": "technical, precise, specification-focused",
    },
}


def get_qrg_description(layer="user_friendly"):
    """
    Get QRG description in specified communication layer

    Args:
        layer (str): Communication layer ('poetic', 'user_friendly', 'academic')

    Returns:
        str: Layer-appropriate description
    """
    descriptions = {
        "poetic": "Quantum Resonance Glyphs transform authentication into an artistic dance "
        "between human consciousness and digital reality, where each circular pattern "
        "becomes a unique crystallization of your digital soul ✨",
        "user_friendly": "QRG creates beautiful, circular QR codes that animate and adapt "
        "to your emotional state, making secure authentication as easy as "
        "scanning a living piece of art 🎨",
        "academic": "Quantum Resonance Glyphs implement post-quantum cryptographic protocols "
        "with CRYSTALS-Kyber 768-bit key encapsulation, temporal validation vectors, "
        "and consciousness-aware adaptation mechanisms for enterprise-grade security",
    }

    return descriptions.get(layer, descriptions["user_friendly"])


# Module initialization
def initialize_qrg_system():
    """Initialize the QRG system with optimal defaults"""
    return {
        "qi_entropy": True,
        "consciousness_awareness": True,
        "post_quantum_crypto": True,
        "animation_enabled": True,
        "webxr_ready": True,
        "lukhas_integration": True,
    }


# Export configuration
QRG_CONFIG = initialize_qrg_system()
