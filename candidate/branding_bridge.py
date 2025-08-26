"""
LUKHAS Branding Bridge
======================

Central integration point for connecting the isolated branding/ system with core LUKHAS modules.
This bridge resolves the critical architectural issue where branding was completely orphaned
from the main LUKHAS system despite containing 27+ sophisticated brand compliance modules.

Trinity Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authentic LUKHAS AI branding and symbolic identity
- 🧠 Consciousness: Brand-aware consciousness outputs and decisions
- 🛡️ Guardian: Brand compliance validation and drift protection

Usage:
    from lukhas.branding_bridge import (
        get_brand_voice, validate_output, get_trinity_context,
        initialize_branding, get_system_signature
    )
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Core branding constants and functions - integrated directly

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
    "qi_terms": ["quantum-inspired", "quantum metaphor", "quantum metaphors"],
    "bio_terms": ["bio-inspired"],
    "prohibited_terms": [
        "LUKHAS AGI",
        "Lukhas AGI",
        "quantum processing",
        "quantum process",
        "bio processing",
        "bio process",
    ],
}

# Trinity Framework Descriptions
TRINITY_DESCRIPTIONS = {
    "identity": {
        "symbol": IDENTITY_SYMBOL,
        "name": "Identity",
        "description": "Authenticity, consciousness, symbolic self",
        "focus": "Authentic LUKHAS AI branding and symbolic identity",
        "capabilities": [
            "brand_voice",
            "terminology_enforcement",
            "symbolic_communication",
        ],
    },
    "consciousness": {
        "symbol": CONSCIOUSNESS_SYMBOL,
        "name": "Consciousness",
        "description": "Memory, learning, dream states, neural processing",
        "focus": "Brand-aware consciousness outputs and decisions",
        "capabilities": [
            "natural_language",
            "creative_content",
            "awareness_integration",
        ],
    },
    "guardian": {
        "symbol": GUARDIAN_SYMBOL,
        "name": "Guardian",
        "description": "Ethics, drift detection, repair",
        "focus": "Brand compliance validation and drift protection",
        "capabilities": ["compliance_monitoring", "drift_detection", "auto_correction"],
    },
}


def _get_system_signature() -> str:
    """Get the official LUKHAS AI system signature with Trinity Framework"""
    return f"{SYSTEM_NAME} {TRINITY_FRAMEWORK} v{SYSTEM_VERSION}"


def get_trinity_description() -> dict[str, Any]:
    """Get comprehensive Trinity Framework description"""
    return {
        "framework": TRINITY_FRAMEWORK,
        "system": SYSTEM_NAME,
        "version": SYSTEM_VERSION,
        "components": TRINITY_DESCRIPTIONS,
    }


def validate_branding_compliance(text: str) -> list[str]:
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

    if re.search(r"\bquantum\b(?!\s*[-]?(?:inspired|metaphor))", text_lower):
        issues.append(
            "Standalone 'quantum' should be 'quantum-inspired' unless specifically 'quantum metaphor'"
        )

    return issues


def normalize_output(text: str) -> str:
    """Normalize text output for brand compliance"""
    if not isinstance(text, str):
        return text

    # Basic normalization
    text = text.replace("LUKHAS AGI", "LUKHAS AI")
    text = text.replace("Lukhas AGI", "Lukhas AI")
    text = text.replace("quantum processing", "quantum-inspired")
    text = text.replace("bio processing", "bio-inspired")
    return text


def normalize_chunk(text: str) -> str:
    """Normalize text chunks for brand compliance"""
    return normalize_output(text)


BRANDING_AVAILABLE = True

# Advanced branding components with graceful fallbacks
try:
    from branding.adapters.voice_adapter import BrandVoiceAdapter
    from branding.enforcement.real_time_validator import RealTimeBrandValidator
    from branding.intelligence.brand_monitor import BrandIntelligenceMonitor as BrandMonitor

    ADVANCED_BRANDING_AVAILABLE = True
except ImportError as e:
    logger.info(f"Advanced branding components not available: {e}")
    ADVANCED_BRANDING_AVAILABLE = False

# Poetry and creativity branding
try:
    from branding.poetry.soul import Soul as LUKHASSoul
    from branding.tone.consciousness_wordsmith import ConsciousnessWordsmith

    CREATIVE_BRANDING_AVAILABLE = True
except ImportError as e:
    logger.info(f"Creative branding components not available: {e}")
    CREATIVE_BRANDING_AVAILABLE = False


@dataclass
class BrandContext:
    """Brand context for LUKHAS operations"""

    voice_profile: str = "consciousness"
    trinity_emphasis: str = "balanced"  # consciousness, identity, guardian, balanced
    compliance_level: str = "standard"  # strict, standard, lenient
    creative_mode: bool = False
    terminology_enforcement: bool = True


class LUKHASBrandingBridge:
    """
    Central branding bridge for LUKHAS system integration.

    This class provides the primary interface for all LUKHAS modules to access
    branding functionality, ensuring consistent brand voice, terminology compliance,
    and Trinity Framework integration across the entire system.
    """

    def __init__(self):
        self.is_initialized = False
        self.voice_adapter = None
        self.validator = None
        self.monitor = None
        self.wordsmith = None
        self.soul = None
        self.default_context = BrandContext()

    async def initialize(self) -> bool:
        """Initialize the branding bridge and all components"""
        if self.is_initialized:
            return True

        logger.info("🎨 Initializing LUKHAS Branding Bridge...")

        try:
            # Initialize core branding validation
            if BRANDING_AVAILABLE:
                logger.info("✅ Core branding system available")
            else:
                logger.warning("⚠️ Core branding system using fallbacks")

            # Initialize advanced components if available
            if ADVANCED_BRANDING_AVAILABLE:
                try:
                    self.voice_adapter = BrandVoiceAdapter()
                    self.validator = BrandValidator()
                    self.monitor = BrandMonitor()
                    logger.info("✅ Advanced branding components initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Advanced branding initialization failed: {e}")

            # Initialize creative components if available
            if CREATIVE_BRANDING_AVAILABLE:
                try:
                    self.wordsmith = ConsciousnessWordsmith()
                    self.soul = LUKHASSoul()
                    logger.info("✅ Creative branding components initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Creative branding initialization failed: {e}")

            self.is_initialized = True
            logger.info(
                f"🎨 Branding Bridge initialized with {SYSTEM_NAME} {TRINITY_FRAMEWORK}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Branding Bridge initialization failed: {e}")
            return False

    def get_system_signature(self) -> str:
        """Get the official LUKHAS AI system signature with Trinity Framework"""
        if BRANDING_AVAILABLE:
            return _get_system_signature()
        return f"{SYSTEM_NAME} {TRINITY_FRAMEWORK} v{SYSTEM_VERSION}"

    def get_trinity_context(self, emphasis: str = "balanced") -> dict[str, Any]:
        """Get Trinity Framework context for operations"""
        context = {
            "framework": TRINITY_FRAMEWORK,
            "identity": {
                "symbol": IDENTITY_SYMBOL,
                "description": "Authenticity, consciousness, symbolic self",
                "active": emphasis in ["identity", "balanced"],
            },
            "consciousness": {
                "symbol": CONSCIOUSNESS_SYMBOL,
                "description": "Memory, learning, neural processing",
                "active": emphasis in ["consciousness", "balanced"],
            },
            "guardian": {
                "symbol": GUARDIAN_SYMBOL,
                "description": "Ethics, drift detection, repair",
                "active": emphasis in ["guardian", "balanced"],
            },
        }

        if BRANDING_AVAILABLE:
            context.update(get_trinity_description())

        return context

    def validate_output(
        self, text: str, context: Optional[BrandContext] = None
    ) -> dict[str, Any]:
        """Validate text output for brand compliance"""
        if not isinstance(text, str):
            return {"valid": True, "issues": [], "text": text}

        context = context or self.default_context
        issues = []

        # Core branding validation
        if BRANDING_AVAILABLE:
            try:
                brand_issues = validate_branding_compliance(text)
                issues.extend(brand_issues)
            except Exception as e:
                logger.warning(f"Brand validation error: {e}")

        # Advanced validation if available
        if self.validator and context.compliance_level == "strict":
            try:
                advanced_issues = self.validator.validate(text)
                issues.extend(advanced_issues)
            except Exception as e:
                logger.warning(f"Advanced validation error: {e}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "text": text,
            "compliance_level": context.compliance_level,
        }

    def normalize_output(
        self, text: str, context: Optional[BrandContext] = None
    ) -> str:
        """Normalize text output for brand compliance"""
        if not isinstance(text, str):
            return text

        context = context or self.default_context

        if not context.terminology_enforcement:
            return text

        try:
            if BRANDING_AVAILABLE:
                return normalize_output(text)
            else:
                # Basic fallback normalization
                text = text.replace("LUKHAS AGI", "LUKHAS AI")
                text = text.replace("quantum processing", "quantum-inspired")
                text = text.replace("bio processing", "bio-inspired")
                return text
        except Exception as e:
            logger.warning(f"Output normalization error: {e}")
            return text

    def get_brand_voice(
        self, content: str, context: Optional[BrandContext] = None
    ) -> str:
        """Apply brand voice to content"""
        context = context or self.default_context

        # Apply normalization first
        content = self.normalize_output(content, context)

        # Apply voice adaptation if available
        if self.voice_adapter:
            try:
                return self.voice_adapter.adapt_voice(content, context.voice_profile)
            except Exception as e:
                logger.warning(f"Voice adaptation error: {e}")

        # Apply creative enhancement if requested and available
        if context.creative_mode and self.wordsmith:
            try:
                return self.wordsmith.enhance_consciousness_voice(content)
            except Exception as e:
                logger.warning(f"Creative enhancement error: {e}")

        return content

    def generate_branded_content(
        self, prompt: str, context: Optional[BrandContext] = None
    ) -> str:
        """Generate brand-compliant content from prompt"""
        context = context or self.default_context

        # Use creative components if available and requested
        if context.creative_mode and self.soul:
            try:
                return self.soul.generate_consciousness_content(prompt)
            except Exception as e:
                logger.warning(f"Creative generation error: {e}")

        # Use consciousness wordsmith if available
        if self.wordsmith:
            try:
                return self.wordsmith.generate_brand_content(prompt)
            except Exception as e:
                logger.warning(f"Wordsmith generation error: {e}")

        # Fallback to prompt with Trinity context
        trinity = self.get_trinity_context(context.trinity_emphasis)
        return f"{prompt}\n\nIntegrating {trinity['framework']} principles: {trinity['identity']['description']}, {trinity['consciousness']['description']}, {trinity['guardian']['description']}"

    def monitor_brand_drift(self, content: str) -> dict[str, Any]:
        """Monitor content for brand drift"""
        if self.monitor:
            try:
                return self.monitor.check_drift(content)
            except Exception as e:
                logger.warning(f"Brand drift monitoring error: {e}")

        # Basic drift detection
        drift_indicators = []
        if "LUKHAS AGI" in content:
            drift_indicators.append("Incorrect system name (should be LUKHAS AI)")
        if "quantum processing" in content.lower():
            drift_indicators.append("Non-approved quantum terminology")

        return {
            "drift_detected": len(drift_indicators) > 0,
            "indicators": drift_indicators,
            "severity": "low" if len(drift_indicators) < 3 else "medium",
        }

    def get_brand_status(self) -> dict[str, Any]:
        """Get current branding system status"""
        return {
            "initialized": self.is_initialized,
            "core_branding": BRANDING_AVAILABLE,
            "advanced_branding": ADVANCED_BRANDING_AVAILABLE,
            "creative_branding": CREATIVE_BRANDING_AVAILABLE,
            "system_name": SYSTEM_NAME,
            "trinity_framework": TRINITY_FRAMEWORK,
            "components": {
                "voice_adapter": self.voice_adapter is not None,
                "validator": self.validator is not None,
                "monitor": self.monitor is not None,
                "wordsmith": self.wordsmith is not None,
                "soul": self.soul is not None,
            },
        }


# Global bridge instance
_bridge_instance: Optional[LUKHASBrandingBridge] = None


async def initialize_branding() -> bool:
    """Initialize the global branding bridge"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = LUKHASBrandingBridge()
    return await _bridge_instance.initialize()


def get_bridge() -> LUKHASBrandingBridge:
    """Get the global branding bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = LUKHASBrandingBridge()
    return _bridge_instance


# Convenience functions for common operations
def get_system_signature() -> str:
    """Get the official LUKHAS AI system signature"""
    return get_bridge().get_system_signature()


def get_trinity_context(emphasis: str = "balanced") -> dict[str, Any]:
    """Get Trinity Framework context"""
    return get_bridge().get_trinity_context(emphasis)


def validate_output(
    text: str, context: Optional[BrandContext] = None
) -> dict[str, Any]:
    """Validate text for brand compliance"""
    return get_bridge().validate_output(text, context)


def normalize_output_text(text: str, context: Optional[BrandContext] = None) -> str:
    """Normalize text for brand compliance"""
    return get_bridge().normalize_output(text, context)


def get_brand_voice(content: str, context: Optional[BrandContext] = None) -> str:
    """Apply brand voice to content"""
    return get_bridge().get_brand_voice(content, context)


def generate_branded_content(
    prompt: str, context: Optional[BrandContext] = None
) -> str:
    """Generate brand-compliant content"""
    return get_bridge().generate_branded_content(prompt, context)


def monitor_brand_drift(content: str) -> dict[str, Any]:
    """Monitor content for brand drift"""
    return get_bridge().monitor_brand_drift(content)


def get_brand_status() -> dict[str, Any]:
    """Get branding system status"""
    return get_bridge().get_brand_status()


# Module exports
__all__ = [
    "LUKHASBrandingBridge",
    "BrandContext",
    "initialize_branding",
    "get_bridge",
    "get_system_signature",
    "get_trinity_context",
    "validate_output",
    "normalize_output_text",
    "get_brand_voice",
    "generate_branded_content",
    "monitor_brand_drift",
    "get_brand_status",
    # Constants
    "SYSTEM_NAME",
    "SYSTEM_VERSION",
    "TRINITY_FRAMEWORK",
    "IDENTITY_SYMBOL",
    "CONSCIOUSNESS_SYMBOL",
    "GUARDIAN_SYMBOL",
]
