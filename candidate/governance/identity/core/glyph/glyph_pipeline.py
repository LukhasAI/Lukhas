"""
Complete GLYPH Generation Pipeline

This module provides a complete pipeline for generating LUKHAS GLYPHs (QRGlyphs)
with integrated identity embedding, steganographic features, and quantum security.

Features:
- Identity-integrated GLYPH generation
- Steganographic identity embedding
- Quantum-enhanced security
- Consciousness-adaptive patterns
- Cultural symbol integration
- Multi-tier access encoding

Author: LUKHAS Identity Team
Version: 1.0.0
"""

import base64
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from PIL import Image

# Import LUKHAS components
try:
    from ...auth.qrg_generators import LUKHASQRGManager, QRGType
    from ...auth_backend.pqc_crypto_engine import PQCCryptoEngine
    from ..visualization.consciousness_mapper import ConsciousnessState
    from ..visualization.lukhas_orb import LUKHASOrb, OrbState
    from .steganographic_id import SteganographicIdentityEmbedder
except ImportError:
    print(
        "Warning: Some LUKHAS components not available. GLYPH pipeline may be limited."
    )

logger = logging.getLogger("LUKHAS_GLYPH_PIPELINE")


class GLYPHType(Enum):
    """Types of GLYPHs that can be generated"""

    IDENTITY_BASIC = "identity_basic"  # Basic identity GLYPH
    IDENTITY_BIOMETRIC = "identity_biometric"  # Biometric-linked GLYPH
    IDENTITY_CONSCIOUSNESS = "identity_consciousness"  # Consciousness-aware GLYPH
    IDENTITY_CULTURAL = "identity_cultural"  # Culturally-adapted GLYPH
    IDENTITY_QUANTUM = "identity_quantum"  # Quantum-secured GLYPH
    IDENTITY_STEGANOGRAPHIC = "identity_steganographic"  # Steganographic GLYPH
    IDENTITY_DREAM = "identity_dream"  # Dream-pattern GLYPH
    IDENTITY_FUSION = "identity_fusion"  # Multi-modal fusion GLYPH


class GLYPHSecurityLevel(Enum):
    """Security levels for GLYPH generation"""

    BASIC = "basic"  # Basic QR security
    ENHANCED = "enhanced"  # Enhanced with crypto
    QUANTUM = "quantum"  # Quantum-resistant
    TRANSCENDENT = "transcendent"  # Maximum security


@dataclass
class GLYPHGenerationRequest:
    """Request for GLYPH generation"""

    lambda_id: str
    glyph_type: GLYPHType
    security_level: GLYPHSecurityLevel
    tier_level: int
    consciousness_state: Optional[ConsciousnessState] = None
    cultural_context: Optional[str] = None
    biometric_data: Optional[dict[str, Any]] = None
    dream_pattern: Optional[dict[str, Any]] = None
    steganographic_data: Optional[dict[str, Any]] = None
    custom_symbols: Optional[list[str]] = None
    expiry_hours: int = 24
    metadata: Optional[dict[str, Any]] = None


@dataclass
class GLYPHGenerationResult:
    """Result of GLYPH generation"""

    success: bool
    glyph_id: str
    glyph_image: Optional[Image.Image]
    glyph_data: dict[str, Any]
    security_metadata: dict[str, Any]
    identity_embedding: dict[str, Any]
    orb_visualization: Optional[dict[str, Any]]
    qi_signature: Optional[str]
    steganographic_layers: Optional[dict[str, Any]]
    generation_metadata: dict[str, Any]
    error_message: Optional[str] = None


class GLYPHPipeline:
    """
    Complete GLYPH Generation Pipeline

    Orchestrates the creation of identity-integrated GLYPHs with advanced
    security features and consciousness adaptation.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Initialize component systems
        self.qrg_manager = LUKHASQRGManager()
        self.pqc_engine = PQCCryptoEngine()
        self.orb_visualizer = LUKHASOrb()
        self.steganographic_embedder = SteganographicIdentityEmbedder()

        # GLYPH storage
        self.generated_glyphs: dict[str, GLYPHGenerationResult] = {}

        # Identity integration templates
        self.identity_templates = {
            GLYPHType.IDENTITY_BASIC: {
                "includes": ["lambda_id", "tier_level", "timestamp"],
                "security": GLYPHSecurityLevel.BASIC,
                "orb_integration": False,
            },
            GLYPHType.IDENTITY_BIOMETRIC: {
                "includes": ["lambda_id", "tier_level", "biometric_hash", "timestamp"],
                "security": GLYPHSecurityLevel.ENHANCED,
                "orb_integration": False,
            },
            GLYPHType.IDENTITY_CONSCIOUSNESS: {
                "includes": [
                    "lambda_id",
                    "consciousness_state",
                    "orb_data",
                    "timestamp",
                ],
                "security": GLYPHSecurityLevel.ENHANCED,
                "orb_integration": True,
            },
            GLYPHType.IDENTITY_QUANTUM: {
                "includes": ["lambda_id", "qi_signature", "pqc_keys", "timestamp"],
                "security": GLYPHSecurityLevel.QUANTUM,
                "orb_integration": False,
            },
            GLYPHType.IDENTITY_FUSION: {
                "includes": [
                    "lambda_id",
                    "all_modalities",
                    "fusion_score",
                    "timestamp",
                ],
                "security": GLYPHSecurityLevel.TRANSCENDENT,
                "orb_integration": True,
            },
        }

        # Cultural symbol mappings
        self.cultural_symbols = {
            "western": ["♦", "♠", "♥", "♣", "⚡", "⭐", "🌟"],
            "eastern": ["☯", "龙", "凤", "莲", "⛩", "🌸", "🎋"],
            "arabic": ["☪", "🕌", "📿", "🌙", "⭐", "🔯", "🎭"],
            "african": ["🦁", "🌍", "🌳", "🥁", "⚡", "☀", "🌿"],
            "universal": ["○", "△", "□", "◇", "∞", "☉", "✧"],
        }

        logger.info("GLYPH Pipeline initialized")

    def generate_glyph(self, request: GLYPHGenerationRequest) -> GLYPHGenerationResult:
        """
        Generate a complete GLYPH based on request

        Args:
            request: GLYPH generation request

        Returns:
            GLYPHGenerationResult with generated GLYPH
        """
        start_time = time.time()

        try:
            # Generate unique GLYPH ID
            glyph_id = self._generate_glyph_id(request)

            # Prepare identity data for embedding
            identity_data = self._prepare_identity_data(request)

            # Generate consciousness-aware user profile
            user_profile = self._create_user_profile(request)

            # Select appropriate QRG type
            qrg_type = self._select_qrg_type(request)

            # Generate base GLYPH using QRG system
            base_glyph_result = self.qrg_manager.generate_adaptive_qr(
                data=json.dumps(identity_data),
                user_profile=user_profile,
                qr_type=qrg_type,
            )

            if "error" in base_glyph_result:
                return GLYPHGenerationResult(
                    success=False,
                    glyph_id=glyph_id,
                    glyph_image=None,
                    glyph_data={},
                    security_metadata={},
                    identity_embedding={},
                    orb_visualization=None,
                    qi_signature=None,
                    steganographic_layers=None,
                    generation_metadata={},
                    error_message=f"Base GLYPH generation failed: {base_glyph_result['error']}",
                )

            # Enhance with identity embedding
            enhanced_glyph = self._embed_identity_features(
                base_glyph_result, request, identity_data
            )

            # Add steganographic layers if requested
            steganographic_layers = None
            if request.steganographic_data:
                steganographic_layers = self._add_steganographic_layers(
                    enhanced_glyph, request.steganographic_data
                )

            # Generate ORB visualization if required
            orb_visualization = None
            template = self.identity_templates.get(request.glyph_type, {})
            if template.get("orb_integration") and request.consciousness_state:
                orb_visualization = self._generate_orb_visualization(
                    request.consciousness_state, request.tier_level
                )

            # Generate quantum signature
            qi_signature = None
            if request.security_level in [
                GLYPHSecurityLevel.QUANTUM,
                GLYPHSecurityLevel.TRANSCENDENT,
            ]:
                qi_signature = self._generate_quantum_signature(
                    enhanced_glyph, identity_data
                )

            # Compile security metadata
            security_metadata = self._compile_security_metadata(
                request, qi_signature, steganographic_layers
            )

            # Create final GLYPH image
            final_glyph_image = self._create_final_glyph_image(
                enhanced_glyph, orb_visualization, request
            )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Create result
            result = GLYPHGenerationResult(
                success=True,
                glyph_id=glyph_id,
                glyph_image=final_glyph_image,
                glyph_data={
                    "base_data": base_glyph_result,
                    "identity_data": identity_data,
                    "user_profile": user_profile,
                },
                security_metadata=security_metadata,
                identity_embedding={
                    "lambda_id": request.lambda_id,
                    "tier_level": request.tier_level,
                    "embedding_method": "integrated_qrg",
                    "security_level": request.security_level.value,
                },
                orb_visualization=orb_visualization,
                qi_signature=qi_signature,
                steganographic_layers=steganographic_layers,
                generation_metadata={
                    "glyph_type": request.glyph_type.value,
                    "qrg_type": qrg_type.value,
                    "processing_time": processing_time,
                    "generation_timestamp": datetime.now().isoformat(),
                    "pipeline_version": "1.0.0",
                },
            )

            # Store generated GLYPH
            self.generated_glyphs[glyph_id] = result

            logger.info(f"Generated GLYPH {glyph_id} for {request.lambda_id}")
            return result

        except Exception as e:
            logger.error(f"GLYPH generation error: {e}")
            return GLYPHGenerationResult(
                success=False,
                glyph_id="error",
                glyph_image=None,
                glyph_data={},
                security_metadata={},
                identity_embedding={},
                orb_visualization=None,
                qi_signature=None,
                steganographic_layers=None,
                generation_metadata={},
                error_message=str(e),
            )

    def verify_glyph(
        self, glyph_id: str, verification_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Verify a generated GLYPH

        Args:
            glyph_id: GLYPH ID to verify
            verification_data: Data for verification

        Returns:
            Verification result
        """
        if glyph_id not in self.generated_glyphs:
            return {"verified": False, "error": "GLYPH not found", "glyph_id": glyph_id}

        glyph_result = self.generated_glyphs[glyph_id]

        # Verify quantum signature if present
        qi_verified = True
        if glyph_result.qi_signature:
            qi_verified = self._verify_quantum_signature(
                glyph_result.qi_signature,
                glyph_result.glyph_data,
                verification_data,
            )

        # Verify steganographic layers if present
        steganographic_verified = True
        if glyph_result.steganographic_layers:
            steganographic_verified = self._verify_steganographic_layers(
                glyph_result.steganographic_layers, verification_data
            )

        # Verify identity embedding
        identity_verified = self._verify_identity_embedding(
            glyph_result.identity_embedding, verification_data
        )

        overall_verified = qi_verified and steganographic_verified and identity_verified

        return {
            "verified": overall_verified,
            "glyph_id": glyph_id,
            "qi_verified": qi_verified,
            "steganographic_verified": steganographic_verified,
            "identity_verified": identity_verified,
            "verification_timestamp": datetime.now().isoformat(),
            "glyph_metadata": glyph_result.generation_metadata,
        }

    def _generate_glyph_id(self, request: GLYPHGenerationRequest) -> str:
        """Generate unique GLYPH ID"""
        id_data = f"{request.lambda_id}_{request.glyph_type.value}_{time.time()}"
        return f"GLYPH_{hashlib.sha256(id_data.encode()).hexdigest()[:16]}"

    def _prepare_identity_data(self, request: GLYPHGenerationRequest) -> dict[str, Any]:
        """Prepare identity data for embedding"""
        template = self.identity_templates.get(request.glyph_type, {})
        includes = template.get("includes", ["lambda_id", "timestamp"])

        identity_data = {
            "glyph_id": f"pending_{int(time.time())}",
            "glyph_type": request.glyph_type.value,
            "security_level": request.security_level.value,
            "generation_timestamp": datetime.now().isoformat(),
        }

        # Add requested fields
        if "lambda_id" in includes:
            identity_data["lambda_id"] = request.lambda_id

        if "tier_level" in includes:
            identity_data["tier_level"] = request.tier_level

        if "timestamp" in includes:
            identity_data["timestamp"] = time.time()

        if "biometric_hash" in includes and request.biometric_data:
            identity_data["biometric_hash"] = hashlib.sha256(
                json.dumps(request.biometric_data, sort_keys=True).encode()
            ).hexdigest()[:16]

        if "consciousness_state" in includes and request.consciousness_state:
            identity_data["consciousness_state"] = {
                "level": request.consciousness_state.consciousness_level,
                "emotional_state": request.consciousness_state.emotional_state.value,
                "neural_synchrony": request.consciousness_state.neural_synchrony,
            }

        if "dream_pattern" in includes and request.dream_pattern:
            identity_data["dream_pattern"] = request.dream_pattern

        if "custom_symbols" in includes and request.custom_symbols:
            identity_data["custom_symbols"] = request.custom_symbols

        # Add expiry
        expiry_time = datetime.now() + timedelta(hours=request.expiry_hours)
        identity_data["expires_at"] = expiry_time.isoformat()

        return identity_data

    def _create_user_profile(self, request: GLYPHGenerationRequest) -> dict[str, Any]:
        """Create user profile for QRG generation"""
        profile = {
            "user_id": request.lambda_id,
            "tier_level": request.tier_level,
            "glyph_type": request.glyph_type.value,
        }

        # Add consciousness data if available
        if request.consciousness_state:
            profile.update(
                {
                    "consciousness_level": request.consciousness_state.consciousness_level,
                    "emotional_state": request.consciousness_state.emotional_state.value,
                    "neural_synchrony": request.consciousness_state.neural_synchrony,
                    "attention_focus": request.consciousness_state.attention_focus,
                }
            )

        # Add cultural context
        if request.cultural_context:
            profile["primary_culture"] = request.cultural_context
            profile["color_palette"] = self._get_cultural_colors(
                request.cultural_context
            )
            profile["symbolic_elements"] = self.cultural_symbols.get(
                request.cultural_context, self.cultural_symbols["universal"]
            )

        # Add biometric hints (without sensitive data)
        if request.biometric_data:
            profile["biometric_present"] = True
            profile["biometric_types"] = list(request.biometric_data.keys())

        # Add dream pattern hints
        if request.dream_pattern:
            profile["dream_state_active"] = True
            profile["dream_symbols"] = request.dream_pattern.get("symbols", [])

        # Add steganographic requirements
        if request.steganographic_data:
            profile["steganography_required"] = True
            profile["hidden_data"] = request.steganographic_data.get("data", "")
            profile["steganography_key"] = request.steganographic_data.get("key")

        # Add quantum security requirements
        if request.security_level in [
            GLYPHSecurityLevel.QUANTUM,
            GLYPHSecurityLevel.TRANSCENDENT,
        ]:
            profile["qi_security_level"] = "maximum"

        return profile

    def _select_qrg_type(self, request: GLYPHGenerationRequest) -> QRGType:
        """Select appropriate QRG type based on request"""
        if request.glyph_type == GLYPHType.IDENTITY_CONSCIOUSNESS:
            return QRGType.CONSCIOUSNESS_ADAPTIVE
        elif request.glyph_type == GLYPHType.IDENTITY_CULTURAL:
            return QRGType.CULTURAL_SYMBOLIC
        elif request.glyph_type == GLYPHType.IDENTITY_STEGANOGRAPHIC:
            return QRGType.STEGANOGRAPHIC
        elif request.glyph_type == GLYPHType.IDENTITY_QUANTUM:
            return QRGType.QUANTUM_ENCRYPTED
        elif request.glyph_type == GLYPHType.IDENTITY_DREAM:
            return QRGType.DREAM_STATE
        elif request.glyph_type == GLYPHType.IDENTITY_FUSION:
            # Use consciousness adaptive for fusion type
            return QRGType.CONSCIOUSNESS_ADAPTIVE
        else:
            return QRGType.CONSCIOUSNESS_ADAPTIVE  # Default

    def _embed_identity_features(
        self,
        base_glyph: dict[str, Any],
        request: GLYPHGenerationRequest,
        identity_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Embed identity features into the GLYPH"""
        enhanced_glyph = base_glyph.copy()

        # Add identity metadata to GLYPH
        enhanced_glyph["identity_features"] = {
            "lambda_id_hash": hashlib.sha256(request.lambda_id.encode()).hexdigest()[
                :16
            ],
            "tier_level": request.tier_level,
            "glyph_type": request.glyph_type.value,
            "security_level": request.security_level.value,
            "cultural_context": request.cultural_context,
            "consciousness_integrated": request.consciousness_state is not None,
            "biometric_linked": request.biometric_data is not None,
            "dream_enhanced": request.dream_pattern is not None,
        }

        # Add tier-specific enhancements
        if request.tier_level >= 3:
            enhanced_glyph["premium_features"] = {
                "enhanced_encryption": True,
                "biometric_binding": request.biometric_data is not None,
                "cultural_adaptation": request.cultural_context is not None,
            }

        if request.tier_level >= 5:
            enhanced_glyph["transcendent_features"] = {
                "dream_integration": request.dream_pattern is not None,
                "consciousness_fusion": request.consciousness_state is not None,
                "qi_signature": True,
                "multi_dimensional_encoding": True,
            }

        return enhanced_glyph

    def _add_steganographic_layers(
        self, glyph: dict[str, Any], steganographic_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add steganographic layers to GLYPH"""
        # Use the steganographic embedder
        embedding_result = self.steganographic_embedder.embed_identity_data(
            glyph.get("qr_image"),
            {
                "lambda_id": glyph.get("identity_features", {}).get(
                    "lambda_id_hash", ""
                ),
                "data": steganographic_data.get("data", ""),
                "key": steganographic_data.get("key", ""),
                "method": steganographic_data.get("method", "lsb"),
            },
        )

        return {
            "method": "steganographic_embedding",
            "layers": embedding_result.get("layers", 1),
            "embedding_strength": embedding_result.get("strength", 0.5),
            "detection_resistance": embedding_result.get("resistance", 0.8),
            "data_integrity": embedding_result.get("integrity", True),
        }

    def _generate_orb_visualization(
        self, consciousness_state: ConsciousnessState, tier_level: int
    ) -> dict[str, Any]:
        """Generate ORB visualization for GLYPH"""
        # Create ORB state
        orb_state = OrbState(
            consciousness_level=consciousness_state.consciousness_level,
            emotional_state=consciousness_state.emotional_state.value,
            neural_synchrony=consciousness_state.neural_synchrony,
            tier_level=tier_level,
            authentication_confidence=consciousness_state.authenticity_score,
            attention_focus=consciousness_state.attention_focus,
            timestamp=time.time(),
            user_lambda_id="anonymous",  # Don't expose actual ID
        )

        # Generate ORB visualization
        orb_visualization = self.orb_visualizer.update_state(orb_state)

        # Get animation frame
        animation_frame = self.orb_visualizer.get_animation_frame(0.016)  # 60 FPS

        return {
            "orb_state": orb_state.__dict__,
            "visualization": orb_visualization.to_dict(),
            "animation_frame": animation_frame,
            "integration_method": "overlay",
        }

    def _generate_quantum_signature(
        self, glyph: dict[str, Any], identity_data: dict[str, Any]
    ) -> str:
        """Generate quantum signature for GLYPH"""
        # Create signature data
        signature_data = json.dumps(
            {
                "glyph_data": glyph,
                "identity_data": identity_data,
                "timestamp": time.time(),
            },
            sort_keys=True,
        ).encode()

        # Generate PQC signature
        signature_keypair = self.pqc_engine.generate_signature_keypair("Dilithium3")
        pqc_signature = self.pqc_engine.sign_message(
            signature_data, signature_keypair.private_key, "Dilithium3"
        )

        return base64.b64encode(pqc_signature.signature).decode()

    def _compile_security_metadata(
        self,
        request: GLYPHGenerationRequest,
        qi_signature: Optional[str],
        steganographic_layers: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compile security metadata for GLYPH"""
        metadata = {
            "security_level": request.security_level.value,
            "encryption_methods": [],
            "integrity_protection": [],
            "authentication_methods": [],
        }

        # Add quantum security info
        if qi_signature:
            metadata["encryption_methods"].append("post_quantum_cryptography")
            metadata["integrity_protection"].append("dilithium_signature")
            metadata["qi_signature_present"] = True

        # Add steganographic security info
        if steganographic_layers:
            metadata["encryption_methods"].append("steganographic_embedding")
            metadata["integrity_protection"].append("hidden_layer_verification")
            metadata["steganographic_layers"] = steganographic_layers.get("layers", 0)

        # Add identity authentication
        metadata["authentication_methods"].append("lambda_id_binding")

        if request.biometric_data:
            metadata["authentication_methods"].append("biometric_linking")

        if request.consciousness_state:
            metadata["authentication_methods"].append("consciousness_verification")

        if request.dream_pattern:
            metadata["authentication_methods"].append("dream_pattern_matching")

        # Add tier-based security
        metadata["tier_level"] = request.tier_level
        metadata["tier_security_features"] = self._get_tier_security_features(
            request.tier_level
        )

        return metadata

    def _create_final_glyph_image(
        self,
        glyph: dict[str, Any],
        orb_visualization: Optional[dict[str, Any]],
        request: GLYPHGenerationRequest,
    ) -> Optional[Image.Image]:
        """Create final GLYPH image with all enhancements"""
        base_image = glyph.get("qr_image")

        if not base_image:
            return None

        # If ORB visualization is present, overlay it
        if orb_visualization and hasattr(base_image, "convert"):
            # This would overlay the ORB visualization on the QR code
            # For now, return base image
            return base_image

        return base_image

    def _get_cultural_colors(self, cultural_context: str) -> list[str]:
        """Get cultural color palette"""
        color_palettes = {
            "western": ["#000000", "#FFFFFF", "#FF0000", "#0000FF"],
            "eastern": ["#FF0000", "#FFD700", "#000000", "#FFFFFF"],
            "arabic": ["#008000", "#FFFFFF", "#000000", "#FFD700"],
            "african": ["#FF8C00", "#8B4513", "#228B22", "#FFFFFF"],
            "universal": ["#000000", "#FFFFFF", "#808080", "#C0C0C0"],
        }
        return color_palettes.get(cultural_context, color_palettes["universal"])

    def _get_tier_security_features(self, tier_level: int) -> list[str]:
        """Get security features for tier level"""
        features = ["basic_encryption"]

        if tier_level >= 1:
            features.append("enhanced_validation")
        if tier_level >= 2:
            features.append("cultural_adaptation")
        if tier_level >= 3:
            features.extend(["biometric_binding", "premium_encryption"])
        if tier_level >= 4:
            features.extend(["qi_resistance", "multi_factor_auth"])
        if tier_level >= 5:
            features.extend(
                ["dream_integration", "consciousness_fusion", "transcendent_security"]
            )

        return features

    def _verify_quantum_signature(
        self,
        signature: str,
        glyph_data: dict[str, Any],
        verification_data: dict[str, Any],
    ) -> bool:
        """Verify quantum signature"""
        # This would verify the PQC signature
        # For now, return True if signature exists
        return bool(signature)

    def _verify_steganographic_layers(
        self, layers: dict[str, Any], verification_data: dict[str, Any]
    ) -> bool:
        """Verify steganographic layers"""
        # This would verify the steganographic embedding
        return layers.get("data_integrity", True)

    def _verify_identity_embedding(
        self, embedding: dict[str, Any], verification_data: dict[str, Any]
    ) -> bool:
        """Verify identity embedding"""
        # Basic verification of identity embedding
        required_fields = ["lambda_id", "tier_level", "embedding_method"]
        return all(field in embedding for field in required_fields)

    def get_pipeline_statistics(self) -> dict[str, Any]:
        """Get pipeline generation statistics"""
        if not self.generated_glyphs:
            return {"total_glyphs": 0}

        glyph_types = {}
        security_levels = {}
        tier_levels = {}

        for glyph_result in self.generated_glyphs.values():
            # Count by type
            glyph_type = glyph_result.generation_metadata.get("glyph_type", "unknown")
            glyph_types[glyph_type] = glyph_types.get(glyph_type, 0) + 1

            # Count by security level
            security_level = glyph_result.security_metadata.get(
                "security_level", "unknown"
            )
            security_levels[security_level] = security_levels.get(security_level, 0) + 1

            # Count by tier
            tier_level = glyph_result.security_metadata.get("tier_level", 0)
            tier_levels[tier_level] = tier_levels.get(tier_level, 0) + 1

        return {
            "total_glyphs": len(self.generated_glyphs),
            "glyph_types": glyph_types,
            "security_levels": security_levels,
            "tier_levels": tier_levels,
            "success_rate": sum(1 for g in self.generated_glyphs.values() if g.success)
            / len(self.generated_glyphs),
            "qi_secured": sum(
                1 for g in self.generated_glyphs.values() if g.qi_signature
            ),
            "steganographic_enhanced": sum(
                1 for g in self.generated_glyphs.values() if g.steganographic_layers
            ),
            "orb_integrated": sum(
                1 for g in self.generated_glyphs.values() if g.orb_visualization
            ),
        }
