"""
LUKHAS ΛID Core Identity System
Agent 1: Identity & Authentication Specialist Implementation
"""

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt

# Performance target: <100ms p95 latency
PERFORMANCE_TARGET_MS = 100


@dataclass
class LukhasID:
    """LUKHAS Identity with namespace support"""

    lid: str  # Unique LUKHAS ID
    namespace: str  # Identity namespace (user, agent, service)
    created_at: str  # ISO timestamp
    metadata: dict[str, Any]  # Additional identity metadata
    public_key: Optional[str] = None  # For WebAuthn/passkey


class NamespaceSchema:
    """ΛID Namespace Schema Definition"""

    NAMESPACES = {
        "user": {
            "prefix": "USR",
            "required_fields": ["email", "display_name"],
            "capabilities": ["authenticate", "consent", "data_access"],
        },
        "agent": {
            "prefix": "AGT",
            "required_fields": ["agent_type", "version"],
            "capabilities": ["execute", "orchestrate", "audit"],
        },
        "service": {
            "prefix": "SVC",
            "required_fields": ["service_name", "endpoint"],
            "capabilities": ["api_access", "data_process"],
        },
    }

    @classmethod
    def validate_namespace(cls, namespace: str, metadata: dict) -> bool:
        """Validate namespace requirements"""
        if namespace not in cls.NAMESPACES:
            return False

        schema = cls.NAMESPACES[namespace]
        required = schema["required_fields"]

        return all(field in metadata for field in required)


class LambdaIDGenerator:
    """ΛID Generation Engine"""

    def __init__(self):
        self.entropy_pool = secrets.SystemRandom()

    def generate_lid(self, namespace: str, metadata: dict) -> str:
        """
        Generate unique ΛID with namespace prefix
        Format: {PREFIX}-{TIMESTAMP}-{RANDOM}-{CHECKSUM}
        """
        if not NamespaceSchema.validate_namespace(namespace, metadata):
            raise ValueError(f"Invalid namespace or metadata for {namespace}")

        prefix = NamespaceSchema.NAMESPACES[namespace]["prefix"]
        timestamp = str(int(time.time() * 1000))  # Millisecond precision
        random_component = secrets.token_hex(8)

        # Create checksum for integrity
        checksum_input = f"{prefix}{timestamp}{random_component}"
        checksum = hashlib.sha256(checksum_input.encode()).hexdigest()[:8]

        return f"{prefix}-{timestamp}-{random_component}-{checksum}"

    def create_identity(self, namespace: str, metadata: dict) -> LukhasID:
        """Create complete LUKHAS Identity"""
        lid = self.generate_lid(namespace, metadata)

        return LukhasID(
            lid=lid,
            namespace=namespace,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )


class JWTTokenManager:
    """Secure JWT Token Management"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"  # Will upgrade to ES256 with KMS

    def issue_token(self, lid: str, namespace: str, capabilities: list[str], ttl_seconds: int = 3600) -> str:
        """Issue JWT token for authenticated identity"""
        payload = {
            "lid": lid,
            "namespace": namespace,
            "capabilities": capabilities,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
            "iss": "lukhas-identity",
            "aud": "lukhas-services",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str) -> dict:
        """Validate and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="lukhas-services",
                issuer="lukhas-identity",
            )
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": str(e)}


class WebAuthnPasskey:
    """WebAuthn/FIDO2 Passkey Integration"""

    def __init__(self):
        self.challenges = {}  # In production, use Redis/cache

    def generate_registration_challenge(self, lid: str) -> dict:
        """Generate WebAuthn registration challenge"""
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

        self.challenges[lid] = {
            "challenge": challenge,
            "timestamp": time.time(),
            "type": "registration",
        }

        return {
            "challenge": challenge,
            "rp": {"name": "LUKHAS AI", "id": "lukhas.ai"},
            "user": {
                "id": base64.urlsafe_b64encode(lid.encode()).decode(),
                "name": lid,
                "displayName": f"LUKHAS User {lid}",
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},  # ES256
                {"type": "public-key", "alg": -257},  # RS256
            ],
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
            },
            "timeout": 60000,
            "attestation": "direct",
        }

    def generate_login_challenge(self, lid: str) -> dict:
        """Generate WebAuthn login challenge"""
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

        self.challenges[lid] = {
            "challenge": challenge,
            "timestamp": time.time(),
            "type": "authentication",
        }

        return {
            "challenge": challenge,
            "timeout": 60000,
            "userVerification": "required",
            "rpId": "lukhas.ai",
        }

    def verify_response(self, lid: str, response: dict) -> bool:
        """Verify WebAuthn response (simplified for MVP)"""
        # In production, implement full WebAuthn verification
        if lid not in self.challenges:
            return False

        challenge_data = self.challenges[lid]

        # Check challenge age (max 5 minutes)
        if time.time() - challenge_data["timestamp"] > 300:
            del self.challenges[lid]
            return False

        # Simplified verification for MVP
        # In production: verify signature, attestation, etc.
        del self.challenges[lid]
        return True


class IdentityService:
    """Main Identity Service coordinating all components"""

    def __init__(self):
        self.id_generator = LambdaIDGenerator()
        self.token_manager = JWTTokenManager()
        self.passkey_manager = WebAuthnPasskey()
        self.identities = {}  # In production, use database

    def register_user(self, email: str, display_name: str) -> dict:
        """Register new user with ΛID"""
        start_time = time.time()

        # Create identity
        identity = self.id_generator.create_identity(
            namespace="user", metadata={"email": email, "display_name": display_name}
        )

        # Store identity
        self.identities[identity.lid] = identity

        # Generate passkey challenge
        passkey_challenge = self.passkey_manager.generate_registration_challenge(identity.lid)

        # Check performance
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "lid": identity.lid,
            "namespace": identity.namespace,
            "passkey_challenge": passkey_challenge,
            "performance_ms": elapsed_ms,
            "meets_target": elapsed_ms < PERFORMANCE_TARGET_MS,
        }

    def authenticate(self, lid: str, passkey_response: dict) -> dict:
        """Authenticate user with passkey"""
        start_time = time.time()

        # Verify passkey
        if not self.passkey_manager.verify_response(lid, passkey_response):
            return {"success": False, "error": "Invalid passkey"}

        # Get identity
        if lid not in self.identities:
            return {"success": False, "error": "Identity not found"}

        identity = self.identities[lid]

        # Issue token
        capabilities = NamespaceSchema.NAMESPACES[identity.namespace]["capabilities"]
        token = self.token_manager.issue_token(lid=lid, namespace=identity.namespace, capabilities=capabilities)

        # Check performance
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "success": True,
            "lid": lid,
            "token": token,
            "capabilities": capabilities,
            "performance_ms": elapsed_ms,
            "meets_target": elapsed_ms < PERFORMANCE_TARGET_MS,
        }

    def validate_access(self, token: str) -> dict:
        """Validate access token"""
        return self.token_manager.validate_token(token)


# Fallback authentication methods
class FallbackAuth:
    """OTP and recovery codes for fallback authentication"""

    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(secrets.randbelow(900000) + 100000)

    @staticmethod
    def generate_recovery_codes(count: int = 10) -> list[str]:
        """Generate recovery codes"""
        return [secrets.token_urlsafe(12) for _ in range(count)]


if __name__ == "__main__":
    # Demo identity service
    service = IdentityService()

    # Register user
    print("🔑 Registering user...")
    result = service.register_user("demo@lukhas.ai", "Demo User")
    print(f"ΛID: {result['lid']}")
    print(f"Performance: {result['performance_ms']:.2f}ms")
    print(f"Meets <100ms target: {result['meets_target']}")

    # Simulate authentication
    print("\n🔐 Authenticating...")
    auth_result = service.authenticate(result["lid"], {"mock": "response"})
    if auth_result["success"]:
        print(f"Token issued: {auth_result['token'][:50]}...")
        print(f"Capabilities: {auth_result['capabilities']}")
        print(f"Performance: {auth_result['performance_ms']:.2f}ms")