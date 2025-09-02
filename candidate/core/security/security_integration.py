"""
LUKHAS Security Integration Module
Integrates enhanced security across all modules
"""

import json
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .agi_security import AGISecuritySystem, SecurityContext, SecurityLevel
from .auth import get_auth_system
from .crypto import get_encryption_manager


class SecurityIntegration:
    """
    Central security integration for LUKHAS
    Ensures all modules use proper encryption and authentication
    """

    def __init__(self):
        # Get enhanced security components
        self.crypto = get_encryption_manager()
        self.auth = get_auth_system()
        self.agi_security = AGISecuritySystem()

        # Module encryption hooks
        self.module_hooks: dict[str, Callable] = {}

        # Security policies
        self.policies = {
            "enforce_encryption": True,
            "require_mfa": True,
            "audit_all_operations": True,
            "encrypt_logs": True,
            "secure_module_communication": True,
        }

    async def initialize(self):
        """Initialize security integration"""
        # Initialize core security
        await self.agi_security.initialize()

        # Replace XOR encryption in all modules
        await self._replace_xor_encryption()

        # Setup module communication security
        await self._setup_secure_channels()

        # Initialize audit encryption
        await self._setup_audit_encryption()

    async def _replace_xor_encryption(self):
        """Replace XOR encryption with real crypto"""
        # Memory module encryption
        self.module_hooks["memory"] = self._create_memory_encryption_hook()

        # Identity module encryption
        self.module_hooks["identity"] = self._create_identity_encryption_hook()

        # QIM module encryption
        self.module_hooks["qim"] = self._create_qim_encryption_hook()

        # GLYPH token encryption
        self.module_hooks["glyph"] = self._create_glyph_encryption_hook()

    def _create_memory_encryption_hook(self) -> Callable:
        """Create encryption hook for memory module"""

        async def encrypt_memory_data(data: Any, memory_type: str = "general") -> tuple[bytes, str]:
            """Encrypt memory data with proper crypto"""
            # Serialize data
            data_bytes = json.dumps(data).encode("utf-8") if isinstance(data, dict) else str(data).encode("utf-8")

            # Use appropriate encryption based on memory type
            if memory_type == "personality":
                purpose = "personality"
            elif memory_type in ["critical", "sensitive"]:
                purpose = "data"
            else:
                purpose = "data"

            # Encrypt with metadata
            metadata = {
                "memory_type": memory_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            ciphertext, key_id = await self.crypto.encrypt(
                data_bytes,
                purpose=purpose,
                associated_data=json.dumps(metadata).encode(),
            )

            return ciphertext, key_id

        return encrypt_memory_data

    def _create_identity_encryption_hook(self) -> Callable:
        """Create encryption hook for identity module"""

        async def encrypt_identity_data(
            data: dict[str, Any],
        ) -> tuple[str, str]:
            """Encrypt identity data"""
            # Identity data is always sensitive
            return await self.crypto.encrypt_json(data, purpose="personality")

        return encrypt_identity_data

    def _create_qim_encryption_hook(self) -> Callable:
        """Create encryption hook for QIM module"""

        async def encrypt_qim_state(state_data: bytes) -> tuple[bytes, str]:
            """Encrypt quantum state data"""
            # Quantum states need high security
            return await self.crypto.encrypt(
                state_data,
                purpose="data",
                algorithm="ChaCha20-Poly1305",  # Fast for large states
            )

        return encrypt_qim_state

    def _create_glyph_encryption_hook(self) -> Callable:
        """Create encryption hook for GLYPH tokens"""

        async def encrypt_glyph_token(token: str, recipient_module: str) -> tuple[str, str]:
            """Encrypt GLYPH token for secure module communication"""
            token_data = {
                "token": token,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "recipient": recipient_module,
            }

            # Encrypt with module-specific key
            return await self.crypto.encrypt_json(token_data, purpose="session")

        return encrypt_glyph_token

    async def _setup_secure_channels(self):
        """Setup encrypted channels for module communication"""
        # Create channels for critical module pairs
        critical_channels = [
            ("consciousness", "memory"),
            ("governance", "consciousness"),
            ("identity", "governance"),
            ("orchestration", "all"),
        ]

        for source, target in critical_channels:
            if target == "all":
                # Broadcast channel
                participants = [
                    "orchestration",
                    "consciousness",
                    "memory",
                    "governance",
                    "identity",
                ]
            else:
                participants = [source, target]

            channel_id = f"{source}-{target}"
            await self.agi_security.create_secure_channel(channel_id, participants)

    async def _setup_audit_encryption(self):
        """Setup encrypted audit logging"""
        # All audit logs should be encrypted and signed

        async def encrypt_audit_log(log_entry: dict[str, Any]) -> str:
            """Encrypt and sign audit log entry"""
            # Add metadata
            log_entry["timestamp"] = datetime.now(timezone.utc).isoformat()
            log_entry["node_id"] = "lukhas-main"

            # Encrypt
            encrypted, key_id = await self.crypto.encrypt_json(log_entry, purpose="data")

            # Create signed package
            package = {
                "encrypted_log": encrypted,
                "key_id": key_id,
                "signature": self._sign_log(encrypted),
            }

            return json.dumps(package)

        self.module_hooks["audit"] = encrypt_audit_log

    def _sign_log(self, data: str) -> str:
        """Sign log data (simplified)"""
        # In production, use proper digital signatures
        import hashlib

        return hashlib.sha256(data.encode()).hexdigest()

    # Public API for modules
    async def encrypt_module_data(self, module: str, data: Any, data_type: str = "general") -> tuple[bytes, str]:
        """Encrypt data for a specific module"""
        if module in self.module_hooks:
            hook = self.module_hooks[module]
            return await hook(data, data_type)
        else:
            # Default encryption
            data_bytes = json.dumps(data).encode() if isinstance(data, dict) else str(data).encode()

            return await self.crypto.encrypt(data_bytes, purpose="data")

    async def create_secure_session(self, user_id: str, credentials: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Create secure session with MFA"""
        # Check rate limiting
        if not await self.auth.check_rate_limit(user_id):
            return None

        # Verify primary credentials
        auth_token = credentials.get("auth_token")
        if not auth_token:
            await self.auth.record_failed_attempt(user_id)
            return None

        # Create initial session
        session = await self.auth.create_session(
            user_id=user_id,
            ip_address=credentials.get("ip_address", "unknown"),
            user_agent=credentials.get("user_agent", "unknown"),
        )

        # Check if MFA required
        if self.policies["require_mfa"]:
            # Get user's MFA methods
            user_mfa = self.auth.mfa_setups.get(user_id, {})

            if not user_mfa:
                # Require MFA setup
                return {
                    "session_id": session.session_id,
                    "mfa_required": True,
                    "mfa_setup_required": True,
                }

            # MFA verification required
            return {
                "session_id": session.session_id,
                "mfa_required": True,
                "mfa_methods": list(user_mfa.keys()),
            }

        # Generate JWT
        jwt_token = self.auth.generate_jwt(
            user_id,
            {
                "session_id": session.session_id,
                "mfa_verified": session.mfa_verified,
            },
        )

        # Create security context for AGI security
        context = await self.agi_security.create_session(user_id, auth_token)

        await self.auth.clear_failed_attempts(user_id)

        return {
            "session_id": session.session_id,
            "jwt_token": jwt_token,
            "security_context": context,
            "mfa_verified": session.mfa_verified,
        }

    async def verify_mfa(self, session_id: str, mfa_method: str, mfa_code: str) -> Optional[dict[str, Any]]:
        """Verify MFA for session"""
        session = await self.auth.validate_session(session_id)
        if not session:
            return None

        # Verify based on method
        verified = False

        if mfa_method == "totp":
            verified = await self.auth.verify_totp(session.user_id, mfa_code)
        elif mfa_method == "sms":
            verified = await self.auth.verify_sms_code(session.user_id, mfa_code)
        elif mfa_method == "email":
            verified = await self.auth.verify_email_code(session.user_id, mfa_code)
        elif mfa_method == "backup":
            verified = await self.auth.verify_backup_code(session.user_id, mfa_code)

        if verified:
            session.mfa_verified = True
            session.auth_methods.append(mfa_method)

            # Generate new JWT with MFA claim
            jwt_token = self.auth.generate_jwt(
                session.user_id,
                {
                    "session_id": session.session_id,
                    "mfa_verified": True,
                    "mfa_method": mfa_method,
                },
            )

            return {"mfa_verified": True, "jwt_token": jwt_token}

        return None

    async def validate_request(self, request_data: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate incoming request with full security checks"""
        # Extract auth info
        auth_header = request_data.get("authorization", "")

        # Check JWT
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = self.auth.verify_jwt(token)

            if not payload:
                return False, "Invalid or expired token"

            # Check MFA for sensitive operations
            operation = request_data.get("operation", "")
            if self._is_sensitive_operation(operation) and not payload.get("mfa_verified"):
                return False, "MFA required for this operation"

            # Create security context
            context = SecurityContext(
                user_id=payload["user_id"],
                session_id=payload.get("session_id", ""),
                clearance_level=SecurityLevel.INTERNAL,
                permissions=set(),  # Load from user profile
            )
            # Default to permissive read/execute permissions for authenticated users
            # in this demo
            context.permissions = {"*"}

            # Validate with AGI security
            return await self.agi_security.validate_operation(operation, request_data.get("data"), context)

        # Check API key
        elif auth_header.startswith("ApiKey "):
            parts = auth_header[7:].split(":")
            if len(parts) != 2:
                return False, "Invalid API key format"

            key_id, key_secret = parts
            key_data = await self.auth.verify_api_key(key_id, key_secret)

            if not key_data:
                return False, "Invalid API key"

            # Check scopes
            operation = request_data.get("operation", "")
            required_scope = self._get_required_scope(operation)

            if required_scope not in key_data["scopes"] and "*" not in key_data["scopes"]:
                return (
                    False,
                    f"API key missing required scope: {required_scope}",
                )

            return True, None

        return False, "No valid authentication provided"

    def _is_sensitive_operation(self, operation: str) -> bool:
        """Check if operation is sensitive"""
        sensitive_ops = [
            "personality",
            "consciousness",
            "governance",
            "delete",
            "modify_core",
            "admin",
        ]

        return any(op in operation.lower() for op in sensitive_ops)

    def _get_required_scope(self, operation: str) -> str:
        """Get required scope for operation"""
        # Map operations to scopes
        if "read" in operation.lower():
            return "read"
        elif "write" in operation.lower():
            return "write"
        elif "admin" in operation.lower():
            return "admin"
        else:
            return "execute"


# Global security integration instance
_security_integration = None


async def get_security_integration() -> SecurityIntegration:
    """Get initialized security integration"""
    global _security_integration

    if not _security_integration:
        _security_integration = SecurityIntegration()
        await _security_integration.initialize()

    return _security_integration
