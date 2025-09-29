#!/usr/bin/env python3
"""
LUKHAS JWT Utilities - Enhanced JWT Operations

JWT generation and validation with LUKHAS-specific claims.
Integrates with I.1 ΛiD Token System and I.2 Tiered Authentication.

T4/0.01% Excellence: High-performance JWT operations with caching.
"""

from __future__ import annotations
import jwt
import time
import os
import secrets
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from opentelemetry import trace
from prometheus_client import Counter, Histogram

tracer = trace.get_tracer(__name__)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs): return self
    def inc(self, amount=1): pass
    def observe(self, amount): pass

try:
    jwt_operations_total = Counter(
        'lukhas_jwt_operations_total',
        'Total JWT operations',
        ['operation', 'algorithm', 'result']
    )
    jwt_operation_latency = Histogram(
        'lukhas_jwt_operation_latency_seconds',
        'JWT operation latency',
        ['operation'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
except ValueError:
    jwt_operations_total = MockMetric()
    jwt_operation_latency = MockMetric()


class JWTAlgorithm(Enum):
    """Supported JWT signing algorithms."""
    RS256 = "RS256"
    ES256 = "ES256"
    HS256 = "HS256"  # For development only


@dataclass
class JWTClaims:
    """Standard and LUKHAS-specific JWT claims."""

    # Standard JWT claims (RFC 7519)
    iss: str  # Issuer
    sub: str  # Subject
    aud: Union[str, List[str]]  # Audience
    exp: int  # Expiration time
    nbf: int  # Not before
    iat: int  # Issued at
    jti: str  # JWT ID

    # OpenID Connect claims
    nonce: Optional[str] = None
    auth_time: Optional[int] = None
    acr: Optional[str] = None  # Authentication Context Class Reference
    amr: Optional[List[str]] = None  # Authentication Methods References

    # LUKHAS-specific claims
    lukhas_tier: Optional[int] = None
    lukhas_namespace: Optional[str] = None
    permissions: Optional[List[str]] = None
    lid_alias: Optional[str] = None  # ΛiD alias
    guardian_validated: Optional[bool] = None

    # Token metadata
    token_type: str = "Bearer"
    scope: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JWT payload."""
        result = {}

        # Add all non-None values
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JWTClaims':
        """Create from dictionary."""
        # Filter to only known fields
        known_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


class JWTKeyManager:
    """JWT signing key management with rotation support."""

    def __init__(self, algorithm: JWTAlgorithm = JWTAlgorithm.RS256):
        self.algorithm = algorithm
        self._private_key: Optional[Any] = None
        self._public_key: Optional[Any] = None
        self._key_id: Optional[str] = None
        self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        """Load existing keys or generate new ones."""
        if self.algorithm == JWTAlgorithm.HS256:
            # HMAC key from environment or generate
            secret = os.getenv("LUKHAS_JWT_SECRET")
            if not secret:
                secret = secrets.token_urlsafe(32)
                # In production, this should be stored securely
            self._private_key = secret
            self._key_id = "hs256-default"

        elif self.algorithm == JWTAlgorithm.RS256:
            # RSA key pair
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self._public_key = self._private_key.public_key()
            self._key_id = f"rsa-{int(time.time())}"

        elif self.algorithm == JWTAlgorithm.ES256:
            # ECDSA key pair
            self._private_key = ec.generate_private_key(ec.SECP256R1())
            self._public_key = self._private_key.public_key()
            self._key_id = f"ec-{int(time.time())}"

    def get_signing_key(self) -> Any:
        """Get the private key for signing."""
        return self._private_key

    def get_verification_key(self) -> Any:
        """Get the public key for verification."""
        if self.algorithm == JWTAlgorithm.HS256:
            return self._private_key
        return self._public_key

    def get_key_id(self) -> str:
        """Get the key ID for JWKS."""
        return self._key_id or "default"

    def get_jwks_entry(self) -> Dict[str, Any]:
        """Get JWKS (JSON Web Key Set) entry for this key."""
        if self.algorithm == JWTAlgorithm.HS256:
            # HMAC keys are not exposed in JWKS
            return {}

        if self.algorithm == JWTAlgorithm.RS256:
            public_numbers = self._public_key.public_numbers()
            return {
                "kty": "RSA",
                "kid": self.get_key_id(),
                "use": "sig",
                "alg": "RS256",
                "n": self._int_to_base64url(public_numbers.n),
                "e": self._int_to_base64url(public_numbers.e),
            }

        elif self.algorithm == JWTAlgorithm.ES256:
            public_numbers = self._public_key.public_numbers()
            return {
                "kty": "EC",
                "kid": self.get_key_id(),
                "use": "sig",
                "alg": "ES256",
                "crv": "P-256",
                "x": self._int_to_base64url(public_numbers.x, 32),
                "y": self._int_to_base64url(public_numbers.y, 32),
            }

    def _int_to_base64url(self, value: int, byte_length: Optional[int] = None) -> str:
        """Convert integer to base64url encoding."""
        if byte_length:
            byte_value = value.to_bytes(byte_length, byteorder='big')
        else:
            byte_length = (value.bit_length() + 7) // 8
            byte_value = value.to_bytes(byte_length, byteorder='big')

        import base64
        return base64.urlsafe_b64encode(byte_value).decode('ascii').rstrip('=')


class JWTManager:
    """High-level JWT operations manager."""

    def __init__(self,
                 issuer: str = "https://auth.lukhas.ai",
                 algorithm: JWTAlgorithm = JWTAlgorithm.RS256,
                 default_expiry: int = 3600):
        """
        Initialize JWT manager.

        Args:
            issuer: JWT issuer claim
            algorithm: Signing algorithm
            default_expiry: Default token expiry in seconds
        """
        self.issuer = issuer
        self.algorithm = algorithm
        self.default_expiry = default_expiry
        self.key_manager = JWTKeyManager(algorithm)

    def create_token(self,
                    subject: str,
                    audience: Union[str, List[str]],
                    claims: Optional[Dict[str, Any]] = None,
                    expiry: Optional[int] = None) -> str:
        """
        Create a JWT token with LUKHAS claims.

        Args:
            subject: Subject (user ID or service name)
            audience: Token audience
            claims: Additional claims
            expiry: Token expiry in seconds (default: instance default)

        Returns:
            Encoded JWT token
        """
        with tracer.start_span("jwt.create_token") as span:
            current_time = int(time.time())
            expiry_time = current_time + (expiry or self.default_expiry)

            # Build JWT claims
            jwt_claims = JWTClaims(
                iss=self.issuer,
                sub=subject,
                aud=audience,
                exp=expiry_time,
                nbf=current_time,
                iat=current_time,
                jti=secrets.token_urlsafe(16)
            )

            # Add additional claims
            if claims:
                for key, value in claims.items():
                    if hasattr(jwt_claims, key):
                        setattr(jwt_claims, key, value)

            # Create JWT headers
            headers = {
                "alg": self.algorithm.value,
                "typ": "JWT",
                "kid": self.key_manager.get_key_id()
            }

            try:
                with jwt_operation_latency.labels(operation="encode").time():
                    token = jwt.encode(
                        payload=jwt_claims.to_dict(),
                        key=self.key_manager.get_signing_key(),
                        algorithm=self.algorithm.value,
                        headers=headers
                    )

                jwt_operations_total.labels(
                    operation="encode",
                    algorithm=self.algorithm.value,
                    result="success"
                ).inc()

                span.set_attribute("jwt.subject", subject)
                span.set_attribute("jwt.algorithm", self.algorithm.value)
                span.set_attribute("jwt.expiry", expiry_time)

                return token

            except Exception as e:
                jwt_operations_total.labels(
                    operation="encode",
                    algorithm=self.algorithm.value,
                    result="error"
                ).inc()
                span.set_attribute("jwt.error", str(e))
                raise

    def verify_token(self, token: str, audience: Optional[Union[str, List[str]]] = None) -> JWTClaims:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify
            audience: Expected audience (optional)

        Returns:
            Decoded JWT claims

        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        with tracer.start_span("jwt.verify_token") as span:
            try:
                with jwt_operation_latency.labels(operation="decode").time():
                    # Decode and verify token
                    payload = jwt.decode(
                        jwt=token,
                        key=self.key_manager.get_verification_key(),
                        algorithms=[self.algorithm.value],
                        issuer=self.issuer,
                        audience=audience,
                        options={
                            "require": ["exp", "iat", "iss", "sub"],
                            "verify_exp": True,
                            "verify_iat": True,
                            "verify_iss": True,
                            "verify_aud": audience is not None
                        }
                    )

                jwt_operations_total.labels(
                    operation="decode",
                    algorithm=self.algorithm.value,
                    result="success"
                ).inc()

                claims = JWTClaims.from_dict(payload)
                span.set_attribute("jwt.subject", claims.sub)
                span.set_attribute("jwt.valid", True)

                return claims

            except jwt.InvalidTokenError as e:
                jwt_operations_total.labels(
                    operation="decode",
                    algorithm=self.algorithm.value,
                    result="invalid"
                ).inc()
                span.set_attribute("jwt.error", str(e))
                span.set_attribute("jwt.valid", False)
                raise

            except Exception as e:
                jwt_operations_total.labels(
                    operation="decode",
                    algorithm=self.algorithm.value,
                    result="error"
                ).inc()
                span.set_attribute("jwt.error", str(e))
                raise

    def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set for token verification."""
        keys = []

        # Add current signing key
        if jwks_entry := self.key_manager.get_jwks_entry():
            keys.append(jwks_entry)

        return {"keys": keys}

    def create_id_token(self,
                       user_id: str,
                       client_id: str,
                       auth_time: int,
                       nonce: Optional[str] = None,
                       additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an OpenID Connect ID token.

        Args:
            user_id: User identifier
            client_id: OAuth2 client ID
            auth_time: Authentication timestamp
            nonce: Optional nonce from auth request
            additional_claims: Additional user claims

        Returns:
            ID token (JWT)
        """
        claims = {
            "auth_time": auth_time,
            "token_type": "id_token"
        }

        if nonce:
            claims["nonce"] = nonce

        if additional_claims:
            claims.update(additional_claims)

        return self.create_token(
            subject=user_id,
            audience=client_id,
            claims=claims,
            expiry=300  # ID tokens have short expiry (5 minutes)
        )

    def create_access_token(self,
                          user_id: str,
                          client_id: str,
                          scopes: List[str],
                          tier: Optional[str] = None,
                          permissions: Optional[List[str]] = None) -> str:
        """
        Create an OAuth2 access token with LUKHAS claims.

        Args:
            user_id: User identifier
            client_id: OAuth2 client ID
            scopes: Granted scopes
            tier: Authentication tier (T1-T5)
            permissions: User permissions

        Returns:
            Access token (JWT)
        """
        claims = {
            "scope": " ".join(scopes),
            "client_id": client_id,
            "token_type": "access_token"
        }

        if tier:
            claims["lukhas_tier"] = int(tier[1]) if tier.startswith("T") else tier

        if permissions:
            claims["permissions"] = permissions

        return self.create_token(
            subject=user_id,
            audience=["lukhas-api"],
            claims=claims,
            expiry=self.default_expiry
        )


# Global JWT manager instance
_jwt_manager: Optional[JWTManager] = None

def get_jwt_manager() -> JWTManager:
    """Get the default JWT manager instance."""
    global _jwt_manager
    if _jwt_manager is None:
        issuer = os.getenv("LUKHAS_JWT_ISSUER", "https://auth.lukhas.ai")
        algorithm_name = os.getenv("LUKHAS_JWT_ALGORITHM", "RS256")
        algorithm = JWTAlgorithm(algorithm_name)
        _jwt_manager = JWTManager(issuer=issuer, algorithm=algorithm)
    return _jwt_manager