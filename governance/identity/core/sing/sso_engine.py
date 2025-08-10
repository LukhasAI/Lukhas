"""
ΛSING SSO Engine
===============

Core symbolic Single Sign-On engine for LUKHAS ecosystem.
Handles authentication tokens and cross-service authorization.

Supported SSO Methods:
- 🔐 Multi-device symbolic login
- 📱 QR-G + seed phrase + emoji SSO
- 👁️ Biometric fallback across apps
- 🌐 Cross-platform authentication (Web, Mobile, Partner ecosystems)
"""

import hashlib
import json
import secrets
from datetime import datetime, timedelta


class LambdaSSOEngine:
    """Symbolic SSO engine for cross-service authentication with multi-device sync"""

    def __init__(self, config, trace_logger=None, tier_manager=None):
        self.config = config
        self.trace_logger = trace_logger
        self.tier_manager = tier_manager

        # Token management
        self.active_tokens = {}
        self.service_registry = {}
        self.device_registry = {}

        # SSO configuration
        self.token_expiry_hours = config.get("sso_token_expiry_hours", 24)
        self.max_concurrent_sessions = config.get("max_concurrent_sessions", 5)
        self.cross_platform_enabled = config.get("cross_platform_enabled", True)

        # Symbolic authentication methods
        self.auth_methods = {
            "symbolic_pattern": "🎯",
            "qr_glyph": "📱",
            "biometric": "👁️",
            "seed_phrase": "🌱",
            "emoji_sequence": "😀",
            "device_trust": "🔗",
        }

    def generate_sso_token(
        self, user_id: str, service_scope: list[str], device_info: dict = None
    ) -> dict:
        """Generate symbolic SSO token for service access with multi-device support"""

        # Validate user tier permissions for requested scope
        if self.tier_manager:
            user_tier = self.tier_manager.get_user_tier(user_id)
            if not self._validate_scope_access(user_tier, service_scope):
                return {
                    "success": False,
                    "error": "Insufficient tier permissions for requested scope",
                }

        # Check concurrent session limits
        if not self._check_session_limits(user_id):
            return {"success": False, "error": "Maximum concurrent sessions exceeded"}

        # Generate token data
        token_id = self._generate_token_id()
        token_data = {
            "token_id": token_id,
            "user_id": user_id,
            "service_scope": service_scope,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (
                datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            ).isoformat(),
            "device_info": device_info or {},
            "symbolic_signature": self._generate_symbolic_signature(
                user_id, service_scope
            ),
            "platform_compatibility": self._determine_platform_compatibility(
                device_info
            ),
            "biometric_fallback_enabled": self._check_biometric_availability(user_id),
        }

        # Store active token
        self.active_tokens[token_id] = token_data

        # Register device if provided
        if device_info:
            self._register_device(user_id, device_info, token_id)

        # Log SSO creation to ΛTRACE
        if self.trace_logger:
            self.trace_logger.log_activity(
                user_id,
                "sso_token_created",
                {
                    "token_id": token_id,
                    "service_scope": service_scope,
                    "device_type": (
                        device_info.get("device_type") if device_info else "unknown"
                    ),
                    "symbolic_method": token_data["symbolic_signature"][:8],
                },
            )

        # Generate QR-G code for cross-device authentication
        qr_glyph_data = (
            self._generate_qr_glyph(token_data) if self.cross_platform_enabled else None
        )

        return {
            "success": True,
            "token_id": token_id,
            "access_token": self._generate_access_token(token_data),
            "symbolic_signature": token_data["symbolic_signature"],
            "expires_at": token_data["expires_at"],
            "qr_glyph": qr_glyph_data,
            "biometric_fallback": token_data["biometric_fallback_enabled"],
            "platform_support": token_data["platform_compatibility"],
        }

    def validate_token(
        self, token_id: str, service_id: str, validation_context: dict = None
    ) -> dict:
        """Validate SSO token for service access with symbolic verification"""

        if token_id not in self.active_tokens:
            return {"valid": False, "reason": "Token not found"}

        token_data = self.active_tokens[token_id]

        # Check token expiry
        if self._is_token_expired(token_data):
            self._invalidate_token(token_id, "expired")
            return {"valid": False, "reason": "Token expired"}

        # Validate service scope
        if service_id not in token_data.get("service_scope", []):
            return {"valid": False, "reason": "Service not in token scope"}

        # Validate symbolic signature if provided
        if validation_context and "symbolic_challenge" in validation_context:
            if not self._validate_symbolic_challenge(
                token_data, validation_context["symbolic_challenge"]
            ):
                return {"valid": False, "reason": "Symbolic challenge failed"}

        # Check device trust if validation context includes device info
        if validation_context and "device_info" in validation_context:
            device_trust_level = self._validate_device_trust(
                token_data["user_id"], validation_context["device_info"]
            )
            if device_trust_level < 0.5:  # Trust threshold
                return {"valid": False, "reason": "Device trust insufficient"}

        # Log successful validation
        if self.trace_logger:
            self.trace_logger.log_activity(
                token_data["user_id"],
                "sso_token_validated",
                {
                    "token_id": token_id,
                    "service_id": service_id,
                    "validation_method": "symbolic_sso",
                },
            )

        return {
            "valid": True,
            "user_id": token_data["user_id"],
            "service_scope": token_data["service_scope"],
            "symbolic_signature": token_data["symbolic_signature"],
            "device_trusted": validation_context.get("device_info") is not None,
            "remaining_time": self._calculate_remaining_time(token_data),
        }

    def authenticate_with_qr_glyph(self, qr_glyph_data: str, device_info: dict) -> dict:
        """Authenticate using QR-G + symbolic elements"""

        try:
            # Parse QR-G data
            glyph_payload = self._parse_qr_glyph(qr_glyph_data)

            # Validate QR-G signature
            if not self._validate_qr_glyph_signature(glyph_payload):
                return {"success": False, "error": "Invalid QR-G signature"}

            # Extract authentication data
            user_id = glyph_payload.get("user_id")
            symbolic_challenge = glyph_payload.get("symbolic_challenge")

            # Verify symbolic challenge
            if not self._verify_symbolic_challenge(user_id, symbolic_challenge):
                return {
                    "success": False,
                    "error": "Symbolic challenge verification failed",
                }

            # Generate new SSO token for this device
            token_result = self.generate_sso_token(
                user_id, glyph_payload.get("service_scope", ["basic"]), device_info
            )

            if token_result["success"]:
                # Log QR-G authentication
                if self.trace_logger:
                    self.trace_logger.log_activity(
                        user_id,
                        "qr_glyph_auth",
                        {
                            "device_type": device_info.get("device_type"),
                            "symbolic_method": "📱🔐",
                            "new_token_id": token_result["token_id"],
                        },
                    )

            return token_result

        except Exception as e:
            return {"success": False, "error": f"QR-G authentication failed: {str(e)}"}

    def authenticate_with_biometric_fallback(
        self, user_id: str, biometric_data: dict, device_info: dict
    ) -> dict:
        """Biometric fallback authentication across apps"""

        # Validate biometric data
        if not self._validate_biometric_data(user_id, biometric_data):
            return {"success": False, "error": "Biometric validation failed"}

        # Check if user has biometric permissions
        if self.tier_manager:
            if not self.tier_manager.validate_permission(user_id, "biometric_auth"):
                return {
                    "success": False,
                    "error": "Biometric authentication not available for user tier",
                }

        # Generate SSO token with biometric authentication
        token_result = self.generate_sso_token(
            user_id, ["biometric_authenticated"], device_info
        )

        if token_result["success"]:
            # Add biometric authentication marker
            token_data = self.active_tokens[token_result["token_id"]]
            token_data["auth_method"] = "biometric"
            token_data["biometric_confidence"] = biometric_data.get(
                "confidence_score", 1.0
            )

            # Log biometric authentication
            if self.trace_logger:
                self.trace_logger.log_activity(
                    user_id,
                    "biometric_sso_auth",
                    {
                        "device_type": device_info.get("device_type"),
                        "confidence_score": biometric_data.get("confidence_score"),
                        "symbolic_method": "👁️🔐",
                    },
                )

        return token_result

    def sync_tokens_across_devices(
        self, user_id: str, source_device: str, target_devices: list[str]
    ) -> dict:
        """Sync SSO tokens across user's trusted devices"""

        # Get user's active tokens
        user_tokens = {
            tid: token
            for tid, token in self.active_tokens.items()
            if token["user_id"] == user_id
        }

        if not user_tokens:
            return {"success": False, "error": "No active tokens to sync"}

        # Validate device trust
        trusted_devices = self._get_trusted_devices(user_id)
        valid_targets = [
            device for device in target_devices if device in trusted_devices
        ]

        if not valid_targets:
            return {"success": False, "error": "No trusted target devices found"}

        sync_results = {}

        for device_id in valid_targets:
            try:
                # Create device-specific token variant
                sync_token = self._create_device_sync_token(user_tokens, device_id)

                # Register sync token
                sync_token_id = self._register_sync_token(sync_token)

                sync_results[device_id] = {
                    "success": True,
                    "sync_token_id": sync_token_id,
                    "symbolic_signature": sync_token["symbolic_signature"],
                }

            except Exception as e:
                sync_results[device_id] = {"success": False, "error": str(e)}

        # Log cross-device sync
        if self.trace_logger:
            self.trace_logger.log_activity(
                user_id,
                "cross_device_sync",
                {
                    "source_device": source_device,
                    "target_devices": valid_targets,
                    "sync_count": len(
                        [r for r in sync_results.values() if r["success"]]
                    ),
                    "symbolic_method": "🔗📱",
                },
            )

        return {
            "success": True,
            "sync_results": sync_results,
            "synced_devices": len([r for r in sync_results.values() if r["success"]]),
        }

    def revoke_token(
        self, token_id: str, revocation_reason: str = "user_request"
    ) -> dict:
        """Revoke SSO token with audit trail"""

        if token_id not in self.active_tokens:
            return {"success": False, "error": "Token not found"}

        token_data = self.active_tokens[token_id]
        user_id = token_data["user_id"]

        # Log token revocation
        if self.trace_logger:
            self.trace_logger.log_activity(
                user_id,
                "sso_token_revoked",
                {
                    "token_id": token_id,
                    "revocation_reason": revocation_reason,
                    "symbolic_method": "❌🔐",
                },
            )

        # Remove token
        del self.active_tokens[token_id]

        # Notify services about token revocation
        self._notify_services_token_revoked(token_data)

        return {
            "success": True,
            "token_id": token_id,
            "revoked_at": datetime.utcnow().isoformat(),
            "affected_services": token_data.get("service_scope", []),
        }

    def register_service(self, service_id: str, service_config: dict) -> dict:
        """Register a service for SSO integration"""

        self.service_registry[service_id] = {
            "service_id": service_id,
            "service_name": service_config.get("name"),
            "callback_url": service_config.get("callback_url"),
            "required_scopes": service_config.get("required_scopes", []),
            "symbolic_integration": service_config.get("symbolic_integration", False),
            "platform_support": service_config.get("platform_support", ["web"]),
            "registered_at": datetime.utcnow().isoformat(),
        }

        return {
            "success": True,
            "service_id": service_id,
            "integration_ready": True,
            "symbolic_support": service_config.get("symbolic_integration", False),
        }

    def _generate_token_id(self) -> str:
        """Generate unique token ID"""
        return f"ΛSSO_{secrets.token_hex(16)}"

    def _generate_access_token(self, token_data: dict) -> str:
        """Generate secure access token"""
        payload = f"{token_data['user_id']}|{token_data['token_id']}|{token_data['created_at']}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def _generate_symbolic_signature(
        self, user_id: str, service_scope: list[str]
    ) -> str:
        """Generate symbolic signature for token"""
        # Combine user tier symbol with service symbols
        scope_symbols = "".join(
            [self.auth_methods.get(scope, "❓") for scope in service_scope[:3]]
        )
        return f"🔐{scope_symbols}"

    def _generate_qr_glyph(self, token_data: dict) -> dict:
        """Generate QR-G code for cross-device authentication"""
        glyph_payload = {
            "user_id": token_data["user_id"],
            "symbolic_challenge": self._create_symbolic_challenge(token_data),
            "service_scope": token_data["service_scope"],
            "expires_at": token_data["expires_at"],
            "glyph_id": f"QRG_{secrets.token_hex(8)}",
        }

        # Generate dynamic glyph image
        from identity.mobile.qr_code_animator import QRCodeAnimator

        animator = QRCodeAnimator()
        glyph_payload["glyph_image_b64"] = animator.generate_glyph(
            token_data["user_id"], token_data["token_id"]
        )

        # Create QR-G signature
        glyph_signature = self._sign_qr_glyph(glyph_payload)
        glyph_payload["signature"] = glyph_signature

        return glyph_payload

    def _validate_scope_access(self, user_tier: int, service_scope: list[str]) -> bool:
        """Validate if user tier allows access to service scope"""
        # TODO: Implement tier-based scope validation
        return True

    def _check_session_limits(self, user_id: str) -> bool:
        """Check if user hasn't exceeded concurrent session limits"""
        user_tokens = [
            token
            for token in self.active_tokens.values()
            if token["user_id"] == user_id and not self._is_token_expired(token)
        ]
        return len(user_tokens) < self.max_concurrent_sessions

    def _is_token_expired(self, token_data: dict) -> bool:
        """Check if token is expired"""
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        return datetime.utcnow() > expires_at

    def _invalidate_token(self, token_id: str, reason: str):
        """Invalidate token with reason"""
        if token_id in self.active_tokens:
            token_data = self.active_tokens[token_id]
            if self.trace_logger:
                self.trace_logger.log_activity(
                    token_data["user_id"],
                    "sso_token_invalidated",
                    {"token_id": token_id, "reason": reason},
                )
            del self.active_tokens[token_id]

    def _determine_platform_compatibility(self, device_info: dict) -> list[str]:
        """Determine platform compatibility for SSO token"""
        if not device_info:
            return ["web"]

        device_type = device_info.get("device_type", "unknown")
        platforms = ["web"]

        if device_type in ["mobile", "tablet"]:
            platforms.extend(["mobile", "ios", "android"])
        elif device_type == "desktop":
            platforms.extend(["desktop", "windows", "macos", "linux"])

        return platforms

    def _check_biometric_availability(self, user_id: str) -> bool:
        """Check if biometric fallback is available for user"""
        if not self.tier_manager:
            return False
        return self.tier_manager.validate_permission(user_id, "biometric_auth")

    def _register_device(self, user_id: str, device_info: dict, token_id: str):
        """Register device for user"""
        device_id = device_info.get("device_id", f"DEV_{secrets.token_hex(8)}")

        if user_id not in self.device_registry:
            self.device_registry[user_id] = {}

        self.device_registry[user_id][device_id] = {
            "device_info": device_info,
            "first_seen": datetime.utcnow().isoformat(),
            "last_token": token_id,
            "trust_level": 0.5,  # Initial trust level
        }

    def _validate_device_trust(self, user_id: str, device_info: dict) -> float:
        """Validate device trust level"""
        device_id = device_info.get("device_id")
        if not device_id or user_id not in self.device_registry:
            return 0.0

        device_data = self.device_registry[user_id].get(device_id)
        if not device_data:
            return 0.0

        return device_data.get("trust_level", 0.0)

    def _get_trusted_devices(self, user_id: str) -> list[str]:
        """Get list of trusted device IDs for user"""
        if user_id not in self.device_registry:
            return []

        trusted_devices = []
        for device_id, device_data in self.device_registry[user_id].items():
            if device_data.get("trust_level", 0.0) >= 0.7:  # Trust threshold
                trusted_devices.append(device_id)

        return trusted_devices

    def _calculate_remaining_time(self, token_data: dict) -> int:
        """Calculate remaining time in seconds for token"""
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        remaining = expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))

    def _create_symbolic_challenge(self, token_data: dict) -> str:
        """Create symbolic challenge for QR-G authentication"""
        # Generate symbolic pattern based on user and token data
        challenge_elements = [
            token_data["symbolic_signature"],
            secrets.choice(["🎯", "🔮", "✨", "🌟"]),
            str(len(token_data["service_scope"])),
        ]
        return "".join(challenge_elements)

    def _parse_qr_glyph(self, qr_glyph_data: str) -> dict:
        """Parse QR-G data structure"""
        # TODO: Implement QR-G parsing logic
        import json

        return json.loads(qr_glyph_data)

    def _validate_qr_glyph_signature(self, glyph_payload: dict) -> bool:
        """Validate QR-G cryptographic signature"""
        # TODO: Implement signature validation
        return True

    def _verify_symbolic_challenge(self, user_id: str, symbolic_challenge: str) -> bool:
        """Verify symbolic challenge for authentication"""
        # TODO: Implement symbolic challenge verification
        return True

    def _validate_biometric_data(self, user_id: str, biometric_data: dict) -> bool:
        """Validate biometric authentication data"""
        # TODO: Implement biometric validation
        return biometric_data.get("confidence_score", 0.0) > 0.8

    def _sign_qr_glyph(self, glyph_payload: dict) -> str:
        """Sign QR-G payload for security"""
        # TODO: Implement cryptographic signing
        payload_str = json.dumps(glyph_payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def _create_device_sync_token(self, user_tokens: dict, device_id: str) -> dict:
        """Create device-specific sync token"""
        # TODO: Implement device sync token creation
        return {}

    def _register_sync_token(self, sync_token: dict) -> str:
        """Register sync token for cross-device use"""
        # TODO: Implement sync token registration
        return f"SYNC_{secrets.token_hex(8)}"

    def _notify_services_token_revoked(self, token_data: dict):
        """Notify services about token revocation"""
        # TODO: Implement service notification logic
