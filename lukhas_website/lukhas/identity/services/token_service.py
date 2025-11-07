"""
LUKHAS Identity Token Service
============================
Dedicated service for JWT token generation, validation, and management.
Implements TokenManagerInterface for T4 architecture compliance.
"""

import hashlib
import json
import logging
import secrets
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

# Conditional JWT import with fallback
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from ..facades.authentication_facade import TokenManagerInterface

logger = logging.getLogger(__name__)


@dataclass
class TokenClaims:
    """Token claims structure"""
    sub: str  # Subject (user_id)
    username: str
    iat: int  # Issued at
    exp: int  # Expires at
    roles: list[str] = None
    scope: str = "user"
    iss: str = "lukhas-ai"  # Issuer

    def __post_init__(self):
        self.roles = self.roles or []


class TokenService(TokenManagerInterface):
    """
    JWT-based token service with fallback capability
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize token service"""
        self.config = config or {}
        self.secret_key = self._get_secret_key()
        self.algorithm = self.config.get("algorithm", "HS256")
        self.default_expiry = self.config.get("token_expiry_seconds", 3600)  # 1 hour
        self.issuer = self.config.get("issuer", "lukhas-ai")

    def _get_secret_key(self) -> str:
        """Get secret key for token signing"""
        # Priority order: config, environment, generated
        secret = self.config.get("secret_key")
        if secret:
            return secret

        import os
        secret = os.getenv("LUKHAS_JWT_SECRET")
        if secret:
            return secret

        # Generate a secure key if none provided
        logger.warning("No JWT secret provided, generating one (not suitable for production)")
        return secrets.token_urlsafe(32)

    async def generate_token(self, user_id: str, username: str, **kwargs) -> str:
        """Generate JWT token for user"""
        try:
            now = int(time.time())
            expiry = now + kwargs.get("expires_in", self.default_expiry)

            claims = TokenClaims(
                sub=user_id,
                username=username,
                iat=now,
                exp=expiry,
                roles=kwargs.get("roles", []),
                scope=kwargs.get("scope", "user"),
                iss=self.issuer
            )

            if JWT_AVAILABLE:
                return jwt.encode(asdict(claims), self.secret_key, algorithm=self.algorithm)
            else:
                # Fallback: create simple token
                return await self._generate_fallback_token(claims)

        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise

    async def validate_token(self, token: str, **kwargs) -> bool:
        """Validate JWT token"""
        try:
            if JWT_AVAILABLE:
                # Decode and validate JWT
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

                # Check expiry
                if payload.get("exp", 0) < time.time():
                    return False

                # Check issuer
                return payload.get("iss") == self.issuer
            else:
                # Fallback validation
                return await self._validate_fallback_token(token)

        except Exception as e:
            logger.debug(f"Token validation failed: {e}")
            return False

    async def refresh_token(self, token: str, **kwargs) -> str:
        """Refresh JWT token"""
        try:
            if JWT_AVAILABLE:
                # Decode existing token (without expiry check)
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})

                # Generate new token with same claims but new expiry
                return await self.generate_token(
                    user_id=payload["sub"],
                    username=payload["username"],
                    roles=payload.get("roles", []),
                    scope=payload.get("scope", "user"),
                    **kwargs
                )
            else:
                # Fallback refresh
                return await self._refresh_fallback_token(token, **kwargs)

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise

    async def decode_token(self, token: str) -> Optional[dict[str, Any]]:
        """Decode token and return claims"""
        try:
            if JWT_AVAILABLE:
                return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            else:
                return await self._decode_fallback_token(token)
        except Exception as e:
            logger.debug(f"Token decode failed: {e}")
            return None

    async def _generate_fallback_token(self, claims: TokenClaims) -> str:
        """Generate fallback token when JWT not available"""
        # Create deterministic token based on claims and secret
        token_data = {
            "claims": asdict(claims),
            "secret_hash": hashlib.sha256(self.secret_key.encode()).hexdigest()[:16]
        }

        token_json = json.dumps(token_data, sort_keys=True)
        encoded = token_json.encode()

        # Simple base64-like encoding
        import base64
        return base64.b64encode(encoded).decode()

    async def _validate_fallback_token(self, token: str) -> bool:
        """Validate fallback token"""
        try:
            import base64
            decoded = base64.b64decode(token.encode())
            token_data = json.loads(decoded.decode())

            claims = token_data.get("claims", {})
            secret_hash = token_data.get("secret_hash", "")

            # Validate secret hash
            expected_hash = hashlib.sha256(self.secret_key.encode()).hexdigest()[:16]
            if secret_hash != expected_hash:
                return False

            # Check expiry
            return not claims.get("exp", 0) < time.time()
        except Exception:
            return False

    async def _refresh_fallback_token(self, token: str, **kwargs) -> str:
        """Refresh fallback token"""
        import base64
        decoded = base64.b64decode(token.encode())
        token_data = json.loads(decoded.decode())

        claims_dict = token_data.get("claims", {})
        claims = TokenClaims(**claims_dict)

        # Update expiry
        now = int(time.time())
        claims.exp = now + kwargs.get("expires_in", self.default_expiry)
        claims.iat = now

        return await self._generate_fallback_token(claims)

    async def _decode_fallback_token(self, token: str) -> Optional[dict[str, Any]]:
        """Decode fallback token"""
        try:
            import base64
            decoded = base64.b64decode(token.encode())
            token_data = json.loads(decoded.decode())
            return token_data.get("claims")
        except Exception:
            return None

    def get_health_status(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "jwt_available": JWT_AVAILABLE,
            "algorithm": self.algorithm,
            "issuer": self.issuer,
            "default_expiry": self.default_expiry,
            "secret_configured": bool(self.secret_key)
        }
