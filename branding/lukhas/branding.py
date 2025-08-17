"""
LUKHAS Core Branding System
===========================

Central branding constants and functions for the LUKHAS AI system.
Provides the foundational branding elements that the branding bridge expects.

Trinity Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authenticity, consciousness, symbolic self
- 🧠 Consciousness: Memory, learning, dream states, neural processing  
- 🛡️ Guardian: Ethics, drift detection, repair
"""

from typing import Dict, Any, List
import logging

# Import existing functionality
from branding.policy.terminology import normalize_output, normalize_chunk

logger = logging.getLogger(__name__)

# Core System Constants
SYSTEM_NAME = "LUKHAS AI"
SYSTEM_VERSION = "2.0"
TRINITY_FRAMEWORK = "⚛️🧠🛡️"

# Trinity Framework Symbols
IDENTITY_SYMBOL = "⚛️"
CONSCIOUSNESS_SYMBOL = "🧠"
GUARDIAN_SYMBOL = "🛡️"

# Approved Terminology
APPROVED_TERMS = {
    "system_name": ["LUKHAS AI", "Lukhas AI"],
    "quantum_terms": ["quantum-inspired", "quantum metaphor", "quantum metaphors"],
    "bio_terms": ["bio-inspired"],
    "prohibited_terms": ["LUKHAS AGI", "Lukhas AGI", "quantum processing", "quantum process", "bio processing", "bio process"]
}

# Trinity Framework Descriptions
TRINITY_DESCRIPTIONS = {
    "identity": {
        "symbol": IDENTITY_SYMBOL,
        "name": "Identity",
        "description": "Authenticity, consciousness, symbolic self",
        "focus": "Authentic LUKHAS AI branding and symbolic identity",
        "capabilities": ["brand_voice", "terminology_enforcement", "symbolic_communication"]
    },
    "consciousness": {
        "symbol": CONSCIOUSNESS_SYMBOL,
        "name": "Consciousness",
        "description": "Memory, learning, dream states, neural processing",
        "focus": "Brand-aware consciousness outputs and decisions",
        "capabilities": ["natural_language", "creative_content", "awareness_integration"]
    },
    "guardian": {
        "symbol": GUARDIAN_SYMBOL,
        "name": "Guardian",
        "description": "Ethics, drift detection, repair",
        "focus": "Brand compliance validation and drift protection",
        "capabilities": ["compliance_monitoring", "drift_detection", "auto_correction"]
    }
}


def get_system_signature() -> str:
    """Get the official LUKHAS AI system signature with Trinity Framework"""
    return f"{SYSTEM_NAME} {TRINITY_FRAMEWORK} v{SYSTEM_VERSION}"


def get_trinity_description() -> Dict[str, Any]:
    """Get comprehensive Trinity Framework description"""
    return {
        "framework": TRINITY_FRAMEWORK,
        "system": SYSTEM_NAME,
        "version": SYSTEM_VERSION,
        "components": TRINITY_DESCRIPTIONS
    }


def validate_branding_compliance(text: str) -> List[str]:
    """Validate text for basic branding compliance issues"""
    if not isinstance(text, str):
        return []
    
    issues = []
    text_lower = text.lower()
    
    # Check for prohibited terms
    if "lukhas agi" in text_lower:
        issues.append("Use 'LUKHAS AI' instead of 'LUKHAS AGI'")
    
    if "quantum processing" in text_lower or "quantum process" in text_lower:
        issues.append("Use 'quantum-inspired' instead of 'quantum processing/process'")
    
    if "bio processing" in text_lower or "bio process" in text_lower:
        issues.append("Use 'bio-inspired' instead of 'bio processing/process'")
    
    # Check for standalone 'quantum' without qualifier
    import re
    if re.search(r'\bquantum\b(?!\s*[-]?(?:inspired|metaphor))', text_lower):
        issues.append("Standalone 'quantum' should be 'quantum-inspired' unless specifically 'quantum metaphor'")
    
    return issues


def get_brand_voice_context(voice_profile: str = "consciousness") -> Dict[str, Any]:
    """Get brand voice context for specific profile"""
    base_context = {
        "system_name": SYSTEM_NAME,
        "trinity_framework": TRINITY_FRAMEWORK,
        "voice_profile": voice_profile,
        "terminology": APPROVED_TERMS
    }
    
    if voice_profile == "consciousness":
        base_context.update({
            "emphasis": CONSCIOUSNESS_SYMBOL,
            "tone": "thoughtful, introspective, aware",
            "focus": "consciousness and awareness concepts"
        })
    elif voice_profile == "identity":
        base_context.update({
            "emphasis": IDENTITY_SYMBOL,
            "tone": "authentic, symbolic, purposeful",
            "focus": "identity and symbolic communication"
        })
    elif voice_profile == "guardian":
        base_context.update({
            "emphasis": GUARDIAN_SYMBOL,
            "tone": "protective, ethical, monitoring",
            "focus": "ethics and system protection"
        })
    else:
        base_context.update({
            "emphasis": TRINITY_FRAMEWORK,
            "tone": "balanced, comprehensive, integrated",
            "focus": "holistic Trinity Framework approach"
        })
    
    return base_context


def get_approved_terminology() -> Dict[str, List[str]]:
    """Get dictionary of approved vs prohibited terminology"""
    return APPROVED_TERMS.copy()


def check_trinity_integration(text: str) -> Dict[str, Any]:
    """Check if text properly integrates Trinity Framework concepts"""
    trinity_mentions = {
        "identity": IDENTITY_SYMBOL in text or "identity" in text.lower(),
        "consciousness": CONSCIOUSNESS_SYMBOL in text or "consciousness" in text.lower(),
        "guardian": GUARDIAN_SYMBOL in text or "guardian" in text.lower()
    }
    
    framework_mentioned = TRINITY_FRAMEWORK in text or "trinity" in text.lower()
    integration_score = sum(trinity_mentions.values()) / 3.0
    
    return {
        "framework_mentioned": framework_mentioned,
        "components_mentioned": trinity_mentions,
        "integration_score": integration_score,
        "recommendation": "Consider mentioning Trinity Framework components" if integration_score < 0.33 else "Good Trinity integration"
    }


# Export all public functions and constants
__all__ = [
    # Constants
    "SYSTEM_NAME",
    "SYSTEM_VERSION", 
    "TRINITY_FRAMEWORK",
    "IDENTITY_SYMBOL",
    "CONSCIOUSNESS_SYMBOL",
    "GUARDIAN_SYMBOL",
    "APPROVED_TERMS",
    "TRINITY_DESCRIPTIONS",
    
    # Functions
    "get_system_signature",
    "get_trinity_description",
    "validate_branding_compliance",
    "get_brand_voice_context",
    "get_approved_terminology",
    "check_trinity_integration",
    "normalize_output",
    "normalize_chunk"
]