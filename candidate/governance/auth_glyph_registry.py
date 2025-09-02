#!/usr/bin/env python3

"""
⚛️ ΛiD Authentication GLYPH Registry
====================================

Registers authentication-related GLYPHs in the LUKHAS symbolic registry
and provides GLYPH-encoded representations for authentication events,
user identity, and security contexts.

This module provides:
- Authentication GLYPH registration and management
- JWT token GLYPH encoding integration
- Symbolic identity representation
- Cross-module communication via GLYPH protocol
- Trinity Framework symbolic alignment

Author: LUKHAS AI System
Version: 1.0.0
Trinity Framework: ⚛️🧠🛡️
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# LUKHAS imports
try:
    from ..core.glyph.glyph import EmotionVector, GlyphFactory, GlyphType
    from ..core.glyph.glyph_engine import GlyphEngine
    from ..core.symbolic.glyph_engine import GlyphEngine as SymbolicGlyphEngine
except ImportError:
    # Fallback for development
    GlyphEngine = None
    GlyphFactory = None
    GlyphType = None
    EmotionVector = None
    SymbolicGlyphEngine = None


class AuthGlyphCategory(Enum):
    """Categories of authentication GLYPHs"""

    IDENTITY = "identity"  # User identity and persona
    ACCESS = "access"  # Access control and permissions
    SESSION = "session"  # Session management
    SECURITY = "security"  # Security events and threats
    TIER = "tier"  # Tier system and privileges
    AUDIT = "audit"  # Audit trail and compliance
    GUARDIAN = "guardian"  # Guardian system integration
    CONSTITUTIONAL = "constitutional"  # Constitutional AI principles


@dataclass
class AuthGlyph:
    """Authentication GLYPH definition"""

    id: str
    category: AuthGlyphCategory
    symbol: str
    concept: str
    description: str
    tier_level: Optional[str] = None
    security_level: Optional[str] = None
    metadata: dict[str, Any] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class SymbolicIdentity:
    """Symbolic representation of user identity"""

    user_id: str
    tier_glyph: str
    access_glyph: str
    session_glyph: str
    constitutional_glyph: str
    trinity_glyph: str
    composite_glyph: str
    metadata: dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None


class AuthGlyphRegistry:
    """
    ⚛️ Authentication GLYPH Registry

    Manages authentication-related GLYPHs for the LUKHAS symbolic system,
    enabling cross-module communication and Trinity Framework integration.
    """

    def __init__(self):
        """Initialize the authentication GLYPH registry"""
        self.glyph_engine = GlyphEngine() if GlyphEngine else None
        self.glyph_factory = GlyphFactory() if GlyphFactory else None

        # Registry storage
        self.registered_glyphs: dict[str, AuthGlyph] = {}
        self.category_index: dict[AuthGlyphCategory, set[str]] = {
            category: set() for category in AuthGlyphCategory
        }
        self.symbolic_identities: dict[str, SymbolicIdentity] = {}

        # Initialize core authentication GLYPHs
        self._initialize_core_glyphs()

    def _initialize_core_glyphs(self) -> None:
        """Initialize core authentication GLYPHs"""
        # Identity GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="lambda_id_core",
                category=AuthGlyphCategory.IDENTITY,
                symbol="Λ",
                concept="lambda_identity",
                description="Core ΛiD identity representation",
                metadata={"trinity_aspect": "identity", "core": True},
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="user_persona",
                category=AuthGlyphCategory.IDENTITY,
                symbol="👤",
                concept="user_persona",
                description="User persona and profile",
                metadata={"trinity_aspect": "identity"},
            )
        )

        # Access Control GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="access_granted",
                category=AuthGlyphCategory.ACCESS,
                symbol="🟢",
                concept="access_granted",
                description="Access permission granted",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="access_denied",
                category=AuthGlyphCategory.ACCESS,
                symbol="🔴",
                concept="access_denied",
                description="Access permission denied",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="scope_check",
                category=AuthGlyphCategory.ACCESS,
                symbol="🔍",
                concept="scope_validation",
                description="Scope permission validation",
            )
        )

        # Session GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="session_active",
                category=AuthGlyphCategory.SESSION,
                symbol="🔓",
                concept="active_session",
                description="Active authentication session",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="session_expired",
                category=AuthGlyphCategory.SESSION,
                symbol="⏰",
                concept="session_expiry",
                description="Session expiration event",
            )
        )

        # Security GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="security_alert",
                category=AuthGlyphCategory.SECURITY,
                symbol="🚨",
                concept="security_threat",
                description="Security threat detected",
                security_level="high",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="auth_success",
                category=AuthGlyphCategory.SECURITY,
                symbol="✅",
                concept="authentication_success",
                description="Successful authentication",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="auth_failure",
                category=AuthGlyphCategory.SECURITY,
                symbol="❌",
                concept="authentication_failure",
                description="Failed authentication attempt",
            )
        )

        # Tier GLYPHs
        for tier in ["T1", "T2", "T3", "T4", "T5"]:
            self.register_glyph(
                AuthGlyph(
                    id=f"tier_{tier.lower()}",
                    category=AuthGlyphCategory.TIER,
                    symbol=f"🏆{tier[-1]}",
                    concept=f"tier_{tier.lower()}_access",
                    description=f"Tier {tier} access level",
                    tier_level=tier,
                )
            )

        # Guardian GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="guardian_monitoring",
                category=AuthGlyphCategory.GUARDIAN,
                symbol="🛡️",
                concept="guardian_oversight",
                description="Guardian system monitoring",
                metadata={"trinity_aspect": "guardian"},
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="drift_detected",
                category=AuthGlyphCategory.GUARDIAN,
                symbol="⚡",
                concept="ethical_drift",
                description="Ethical drift detection",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="bias_alert",
                category=AuthGlyphCategory.GUARDIAN,
                symbol="⚖️",
                concept="bias_detection",
                description="Bias pattern detected",
            )
        )

        # Constitutional AI GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="constitutional_valid",
                category=AuthGlyphCategory.CONSTITUTIONAL,
                symbol="📜✅",
                concept="constitutional_compliance",
                description="Constitutional AI validation passed",
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="constitutional_violation",
                category=AuthGlyphCategory.CONSTITUTIONAL,
                symbol="📜❌",
                concept="constitutional_violation",
                description="Constitutional AI principle violated",
            )
        )

        # Audit GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="audit_entry",
                category=AuthGlyphCategory.AUDIT,
                symbol="📋",
                concept="audit_logging",
                description="Audit trail entry created",
            )
        )

        # Trinity Framework GLYPHs
        self.register_glyph(
            AuthGlyph(
                id="trinity_identity",
                category=AuthGlyphCategory.IDENTITY,
                symbol="⚛️",
                concept="trinity_identity",
                description="Trinity Framework - Identity aspect",
                metadata={"trinity_core": True, "aspect": "identity"},
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="trinity_consciousness",
                category=AuthGlyphCategory.IDENTITY,
                symbol="🧠",
                concept="trinity_consciousness",
                description="Trinity Framework - Consciousness aspect",
                metadata={"trinity_core": True, "aspect": "consciousness"},
            )
        )

        self.register_glyph(
            AuthGlyph(
                id="trinity_guardian",
                category=AuthGlyphCategory.GUARDIAN,
                symbol="🛡️",
                concept="trinity_guardian",
                description="Trinity Framework - Guardian aspect",
                metadata={"trinity_core": True, "aspect": "guardian"},
            )
        )

    def register_glyph(self, glyph: AuthGlyph) -> bool:
        """Register a new authentication GLYPH"""
        try:
            # Check for duplicates
            if glyph.id in self.registered_glyphs:
                return False

            # Register the GLYPH
            self.registered_glyphs[glyph.id] = glyph
            self.category_index[glyph.category].add(glyph.id)

            return True

        except Exception as e:
            print(f"Error registering GLYPH {glyph.id}: {e}")
            return False

    def get_glyph(self, glyph_id: str) -> Optional[AuthGlyph]:
        """Get a registered GLYPH by ID"""
        return self.registered_glyphs.get(glyph_id)

    def get_glyphs_by_category(self, category: AuthGlyphCategory) -> list[AuthGlyph]:
        """Get all GLYPHs in a specific category"""
        glyph_ids = self.category_index.get(category, set())
        return [self.registered_glyphs[glyph_id] for glyph_id in glyph_ids]

    def get_tier_glyph(self, tier_level: str) -> Optional[AuthGlyph]:
        """Get GLYPH for specific tier level"""
        glyph_id = f"tier_{tier_level.lower()}"
        return self.get_glyph(glyph_id)

    def create_symbolic_identity(
        self,
        user_id: str,
        tier_level: str,
        access_context: dict[str, Any],
        session_context: dict[str, Any],
    ) -> SymbolicIdentity:
        """Create symbolic identity representation for user"""
        try:
            # Get tier GLYPH
            tier_glyph_obj = self.get_tier_glyph(tier_level)
            tier_glyph = (
                tier_glyph_obj.symbol if tier_glyph_obj else f"🏆{tier_level[-1]}"
            )

            # Create access GLYPH based on context
            if access_context.get("granted", False):
                access_glyph = self.get_glyph("access_granted").symbol
            else:
                access_glyph = self.get_glyph("access_denied").symbol

            # Create session GLYPH
            if session_context.get("active", False):
                session_glyph = self.get_glyph("session_active").symbol
            else:
                session_glyph = self.get_glyph("session_expired").symbol

            # Create constitutional GLYPH
            if access_context.get("constitutional_valid", True):
                constitutional_glyph = self.get_glyph("constitutional_valid").symbol
            else:
                constitutional_glyph = self.get_glyph("constitutional_violation").symbol

            # Create Trinity GLYPH
            trinity_glyph = self._create_trinity_glyph(access_context, session_context)

            # Create composite GLYPH
            composite_glyph = self._create_composite_glyph(
                tier_glyph,
                access_glyph,
                session_glyph,
                constitutional_glyph,
                trinity_glyph,
            )

            # Create symbolic identity
            symbolic_identity = SymbolicIdentity(
                user_id=user_id,
                tier_glyph=tier_glyph,
                access_glyph=access_glyph,
                session_glyph=session_glyph,
                constitutional_glyph=constitutional_glyph,
                trinity_glyph=trinity_glyph,
                composite_glyph=composite_glyph,
                metadata={
                    "tier_level": tier_level,
                    "access_context": access_context,
                    "session_context": session_context,
                    "glyph_version": "1.0.0",
                },
                created_at=datetime.now(),
            )

            # Store symbolic identity
            self.symbolic_identities[user_id] = symbolic_identity

            return symbolic_identity

        except Exception as e:
            print(f"Error creating symbolic identity for user {user_id}: {e}")
            # Return minimal symbolic identity
            return SymbolicIdentity(
                user_id=user_id,
                tier_glyph="🏆",
                access_glyph="🔍",
                session_glyph="🔓",
                constitutional_glyph="📜",
                trinity_glyph="⚛️🧠🛡️",
                composite_glyph="GLYPH[🏆🔍🔓📜:ERROR]",
                metadata={"error": str(e)},
                created_at=datetime.now(),
            )

    def _create_trinity_glyph(
        self, access_context: dict[str, Any], session_context: dict[str, Any]
    ) -> str:
        """Create Trinity Framework GLYPH"""
        # Get Trinity symbols
        identity_symbol = self.get_glyph("trinity_identity").symbol
        consciousness_symbol = self.get_glyph("trinity_consciousness").symbol
        guardian_symbol = self.get_glyph("trinity_guardian").symbol

        # Determine emphasis based on context
        if access_context.get("requires_guardian_oversight", False):
            return f"{guardian_symbol}{identity_symbol}{consciousness_symbol}"
        elif session_context.get("consciousness_integration", False):
            return f"{consciousness_symbol}{identity_symbol}{guardian_symbol}"
        else:
            return f"{identity_symbol}{consciousness_symbol}{guardian_symbol}"

    def _create_composite_glyph(self, *glyph_components: str) -> str:
        """Create composite GLYPH from components"""
        try:
            # Combine components
            combined = "".join(glyph_components)

            # Create hash for uniqueness
            glyph_hash = hashlib.sha256(combined.encode()).hexdigest()[:8]

            # Return formatted composite GLYPH
            return f"GLYPH[{combined}:{glyph_hash}]"

        except Exception as e:
            return f"GLYPH[ERROR:{str(e)[:8]}]"

    def encode_jwt_glyph_claims(
        self,
        user_id: str,
        tier_level: str,
        scopes: list[str],
        session_id: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Encode GLYPH claims for JWT token"""
        try:
            # Get or create symbolic identity
            symbolic_identity = self.symbolic_identities.get(user_id)
            if not symbolic_identity:
                # Create access context
                access_context = {
                    "granted": True,
                    "scopes": scopes,
                    "constitutional_valid": metadata.get("constitutional_valid", True),
                }

                # Create session context
                session_context = {
                    "active": True,
                    "session_id": session_id,
                    "consciousness_integration": metadata.get(
                        "consciousness_integration", False
                    ),
                }

                symbolic_identity = self.create_symbolic_identity(
                    user_id, tier_level, access_context, session_context
                )

            # Create GLYPH claims
            glyph_claims = {
                "glyph_identity": symbolic_identity.composite_glyph,
                "glyph_tier": symbolic_identity.tier_glyph,
                "glyph_access": symbolic_identity.access_glyph,
                "glyph_session": symbolic_identity.session_glyph,
                "glyph_constitutional": symbolic_identity.constitutional_glyph,
                "glyph_trinity": symbolic_identity.trinity_glyph,
                "glyph_version": "1.0.0",
                "glyph_created": symbolic_identity.created_at.isoformat(),
                "glyph_registry": "lukhas_auth_v1",
            }

            # Add scope GLYPHs
            scope_glyphs = []
            for scope in scopes:
                scope_glyph = self._create_scope_glyph(scope)
                scope_glyphs.append(scope_glyph)

            glyph_claims["glyph_scopes"] = scope_glyphs

            # Add Guardian GLYPHs if applicable
            if metadata.get("guardian_monitoring", False):
                guardian_glyph = self.get_glyph("guardian_monitoring")
                glyph_claims["glyph_guardian"] = (
                    guardian_glyph.symbol if guardian_glyph else "🛡️"
                )

            if metadata.get("drift_detected", False):
                drift_glyph = self.get_glyph("drift_detected")
                glyph_claims["glyph_drift"] = (
                    drift_glyph.symbol if drift_glyph else "⚡"
                )

            if metadata.get("bias_detected", False):
                bias_glyph = self.get_glyph("bias_alert")
                glyph_claims["glyph_bias"] = bias_glyph.symbol if bias_glyph else "⚖️"

            return glyph_claims

        except Exception as e:
            print(f"Error encoding JWT GLYPH claims: {e}")
            return {
                "glyph_error": str(e),
                "glyph_version": "1.0.0",
                "glyph_registry": "lukhas_auth_v1",
            }

    def _create_scope_glyph(self, scope: str) -> str:
        """Create GLYPH representation for scope"""
        # Map common scopes to symbols
        scope_symbols = {
            "matriz:read": "📖",
            "matriz:write": "✏️",
            "matriz:admin": "⚙️",
            "api:read": "🔍",
            "api:write": "✍️",
            "consciousness:access": "🧠",
            "memory:read": "🧠📚",
            "memory:write": "🧠✏️",
            "guardian:monitor": "🛡️👁",
            "admin:full": "👑",
        }

        return scope_symbols.get(scope, "🔹")

    def decode_glyph_claims(self, glyph_claims: dict[str, Any]) -> dict[str, Any]:
        """Decode GLYPH claims from JWT token"""
        try:
            decoded = {
                "identity_glyph": glyph_claims.get("glyph_identity"),
                "tier_glyph": glyph_claims.get("glyph_tier"),
                "access_glyph": glyph_claims.get("glyph_access"),
                "session_glyph": glyph_claims.get("glyph_session"),
                "constitutional_glyph": glyph_claims.get("glyph_constitutional"),
                "trinity_glyph": glyph_claims.get("glyph_trinity"),
                "scope_glyphs": glyph_claims.get("glyph_scopes", []),
                "guardian_glyph": glyph_claims.get("glyph_guardian"),
                "drift_glyph": glyph_claims.get("glyph_drift"),
                "bias_glyph": glyph_claims.get("glyph_bias"),
                "version": glyph_claims.get("glyph_version"),
                "created": glyph_claims.get("glyph_created"),
                "registry": glyph_claims.get("glyph_registry"),
            }

            # Analyze GLYPHs for security insights
            decoded["security_analysis"] = self._analyze_glyph_security(glyph_claims)

            return decoded

        except Exception as e:
            return {"error": str(e), "decoded": False}

    def _analyze_glyph_security(self, glyph_claims: dict[str, Any]) -> dict[str, Any]:
        """Analyze GLYPH claims for security insights"""
        analysis = {"risk_level": "low", "alerts": [], "recommendations": []}

        # Check for Guardian alerts
        if glyph_claims.get("glyph_drift"):
            analysis["risk_level"] = "high"
            analysis["alerts"].append("Ethical drift detected")
            analysis["recommendations"].append("Review authentication patterns")

        if glyph_claims.get("glyph_bias"):
            analysis["risk_level"] = "medium"
            analysis["alerts"].append("Bias pattern detected")
            analysis["recommendations"].append("Audit access decisions for fairness")

        # Check constitutional compliance
        constitutional_glyph = glyph_claims.get("glyph_constitutional", "")
        if "❌" in constitutional_glyph:
            analysis["risk_level"] = "high"
            analysis["alerts"].append("Constitutional AI violation")
            analysis["recommendations"].append("Review authentication policies")

        # Check access patterns
        access_glyph = glyph_claims.get("glyph_access", "")
        if "🔴" in access_glyph:
            analysis["alerts"].append("Access denied in session")

        return analysis

    def get_cross_module_glyph_message(
        self, target_module: str, message_type: str, auth_context: dict[str, Any]
    ) -> str:
        """Create GLYPH message for cross-module communication"""
        try:
            # Get user symbolic identity
            user_id = auth_context.get("user_id")
            symbolic_identity = (
                self.symbolic_identities.get(user_id) if user_id else None
            )

            # Create message GLYPH
            if target_module == "consciousness":
                module_symbol = "🧠"
            elif target_module == "memory":
                module_symbol = "🧠📚"
            elif target_module == "guardian":
                module_symbol = "🛡️"
            elif target_module == "quantum":
                module_symbol = "⚛️"
            else:
                module_symbol = "🔹"

            # Message type symbols
            type_symbols = {
                "auth_success": "✅",
                "auth_failure": "❌",
                "session_start": "🚀",
                "session_end": "🛑",
                "tier_change": "🔄",
                "access_request": "🔍",
                "guardian_alert": "🚨",
            }

            message_symbol = type_symbols.get(message_type, "💬")

            # Create composite message
            if symbolic_identity:
                identity_glyph = symbolic_identity.composite_glyph
                message_glyph = f"MSG[{module_symbol}{message_symbol}{identity_glyph}]"
            else:
                message_glyph = f"MSG[{module_symbol}{message_symbol}:ANON]"

            return message_glyph

        except Exception as e:
            return f"MSG[ERROR:{str(e)[:8]}]"

    def get_registry_stats(self) -> dict[str, Any]:
        """Get authentication GLYPH registry statistics"""
        stats = {
            "total_glyphs": len(self.registered_glyphs),
            "by_category": {},
            "symbolic_identities": len(self.symbolic_identities),
            "trinity_glyphs": 0,
            "security_glyphs": 0,
            "last_updated": datetime.now().isoformat(),
        }

        # Count by category
        for category in AuthGlyphCategory:
            stats["by_category"][category.value] = len(self.category_index[category])

        # Count special types
        for glyph in self.registered_glyphs.values():
            if glyph.metadata and glyph.metadata.get("trinity_core"):
                stats["trinity_glyphs"] += 1
            if glyph.category == AuthGlyphCategory.SECURITY:
                stats["security_glyphs"] += 1

        return stats


# Global registry instance
auth_glyph_registry = AuthGlyphRegistry()


# Export main classes and instance
__all__ = [
    "AuthGlyph",
    "AuthGlyphCategory",
    "AuthGlyphRegistry",
    "SymbolicIdentity",
    "auth_glyph_registry",
]
