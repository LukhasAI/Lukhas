"""
QRG Integration Bridge for LUKHAS Authentication System

This module provides integration between the LUKHAS authentication system
and the Lambda QRG (QR Glyph) core for advanced QR code authentication.

Integration Points:
- qrg_core.py: Core QR glyph generation and validation
- animation_engine.py: Animated QR authentication flows
- steganography.py: Hidden data in QR authentication
- consciousness_layer.py: Consciousness-aware QR patterns
- qi_entropy.py: QI-enhanced QR entropy
"""
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class QRAuthMode(Enum):
    """QR Authentication modes"""

    BASIC = "basic"
    ANIMATED = "animated"
    STEGANOGRAPHIC = "steganographic"
    CONSCIOUSNESS_AWARE = "consciousness_aware"
    QI_ENHANCED = "qi_enhanced"


@dataclass
class QRGAuthIntegration:
    """Configuration for QRG authentication integration"""

    qrg_enabled: bool = True
    animation_enabled: bool = True
    steganography_enabled: bool = True
    consciousness_enabled: bool = True
    qi_entropy_enabled: bool = True
    auth_mode: QRAuthMode = QRAuthMode.CONSCIOUSNESS_AWARE


class AuthQRGBridge:
    """
    Bridge between LUKHAS Auth System and Lambda QRG Core

    Features:
    - Advanced QR glyph authentication
    - Animated QR authentication flows
    - Steganographic QR data embedding
    - Consciousness-aware QR patterns
    - QI-enhanced entropy generation
    """

    def __init__(self, config: QRGAuthIntegration):
        self.config = config
        self.qrg_core = None
        self.animation_engine = None
        self.steganography = None
        self.consciousness_layer = None
        self.qi_entropy = None
        self.initialized = False
        self.component_status: dict[str, Any] = {}
        self._last_qr_payload: Optional[str] = None

    async def initialize(self) -> dict[str, Any]:
        """Initialize QRG integration components"""
        component_flags = {
            "qrg_core": self.config.qrg_enabled,
            "animation_engine": self.config.animation_enabled,
            "steganography": self.config.steganography_enabled,
            "consciousness_layer": self.config.consciousness_enabled,
            "qi_entropy": self.config.qi_entropy_enabled,
        }

        self.component_status = {
            name: {
                "enabled": enabled,
                "status": "virtual_adapter" if enabled else "disabled",
            }
            for name, enabled in component_flags.items()
        }

        self.initialized = True

        # ΛTAG: qrg_init – record deterministic initialization manifest
        return {
            "status": "initialized",
            "qrg_enabled": self.config.qrg_enabled,
            "components": self.component_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_auth_qr(
        self, user_id: str, auth_data: dict[str, Any], mode: QRAuthMode = None
    ) -> dict[str, Any]:
        """Generate authentication QR code with specified mode"""
        if mode is None:
            mode = self.config.auth_mode

        if not self.config.qrg_enabled:
            return {
                "qr_generated": False,
                "mode": mode.value,
                "data_embedded": False,
                "status": "disabled",
            }

        issued_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "user_id": user_id,
            "auth_data": auth_data,
            "mode": mode.value,
            "issued_at": issued_at,
            "component_status": self.component_status,
        }

        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        checksum_seed = f"{user_id}|{mode.value}|{issued_at}"
        checksum = hashlib.sha256((canonical + checksum_seed).encode()).hexdigest()

        qr_blob = base64.urlsafe_b64encode(
            json.dumps({"payload": payload, "checksum": checksum}).encode()
        ).decode()

        self._last_qr_payload = qr_blob

        # ΛTAG: qrg_generate – produce deterministic QR artifact for SSO linking
        return {
            "qr_generated": True,
            "mode": mode.value,
            "data_embedded": bool(auth_data),
            "status": "ready",
            "qr_blob": qr_blob,
            "checksum": checksum,
        }

    async def validate_auth_qr(self, qr_data: str, user_context: dict[str, Any]) -> dict[str, Any]:
        """Validate authentication QR code"""
        if not qr_data:
            return {
                "valid": False,
                "reason": "missing_qr_data",
                "status": "invalid",
                "consciousness_score": 0.0,
                "qi_entropy_verified": False,
            }

        try:
            decoded = base64.urlsafe_b64decode(qr_data.encode()).decode()
            wrapped = json.loads(decoded)
            payload = wrapped["payload"]
            checksum = wrapped["checksum"]
        except (ValueError, KeyError, json.JSONDecodeError):
            return {
                "valid": False,
                "reason": "decode_error",
                "status": "invalid",
                "consciousness_score": 0.0,
                "qi_entropy_verified": False,
            }

        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        recomputed = hashlib.sha256((canonical + f"{payload['user_id']}|{payload['mode']}|{payload['issued_at']}").encode()).hexdigest()

        integrity_ok = hmac.compare_digest(checksum, recomputed)
        context_match = payload.get("user_id") == user_context.get("user_id")
        entropy_verified = self.config.qi_entropy_enabled and integrity_ok

        # ΛTAG: qrg_validate – evaluate symbolic + entropy coherence
        return {
            "valid": bool(integrity_ok and context_match),
            "status": "validated" if integrity_ok and context_match else "mismatch",
            "consciousness_score": 0.9 if context_match else 0.2,
            "qi_entropy_verified": entropy_verified,
            "issued_at": payload.get("issued_at"),
        }

    async def create_animated_auth_flow(self, session_id: str, consciousness_data: dict[str, Any]) -> dict[str, Any]:
        """Create animated QR authentication flow"""
        if not self.config.animation_enabled:
            return {
                "animation_created": False,
                "session_id": session_id,
                "consciousness_integrated": False,
                "status": "disabled",
            }

        frames = []
        symbolic_trace = consciousness_data.get("symbolic_trace", [])
        for index, symbol in enumerate(symbolic_trace or ["⚛️", "🧠", "🛡️"]):
            frames.append(
                {
                    "frame": index,
                    "symbol": symbol,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        entropy_curve = hashlib.sha256(session_id.encode()).hexdigest()[:12]

        # ΛTAG: qrg_animation – simulated consciousness aligned animation trace
        return {
            "animation_created": True,
            "session_id": session_id,
            "consciousness_integrated": bool(symbolic_trace),
            "status": "rendered",
            "frames": frames,
            "entropy_curve": entropy_curve,
        }

    async def embed_steganographic_auth(
        self, base_qr: str, hidden_auth_data: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Embed hidden authentication data in QR code"""
        if not self.config.steganography_enabled:
            return (
                base_qr,
                {
                    "embedded": False,
                    "hidden_data_size": 0,
                    "status": "disabled",
                },
            )

        hidden_blob = base64.urlsafe_b64encode(json.dumps(hidden_auth_data, sort_keys=True).encode()).decode()
        composite = f"{base_qr}::{hidden_blob}"

        # ΛTAG: qrg_steganography – deterministic embedding metadata for audits
        metadata = {
            "embedded": True,
            "hidden_data_size": len(hidden_blob),
            "status": "embedded",
            "checksum": hashlib.sha256(hidden_blob.encode()).hexdigest(),
        }

        return composite, metadata


# Integration factory
def create_qrg_bridge(config: Optional[QRGAuthIntegration] = None) -> AuthQRGBridge:
    """Create QRG authentication bridge"""
    if config is None:
        config = QRGAuthIntegration()

    return AuthQRGBridge(config)


# Export for authentication system
__all__ = ["AuthQRGBridge", "QRAuthMode", "QRGAuthIntegration", "create_qrg_bridge"]
