#!/usr/bin/env python3
"""
OIDC Token Manager - OAuth2/OIDC Token Operations

Manages authorization codes, access tokens, refresh tokens, and ID tokens.
Implements OAuth2 Authorization Code Flow with PKCE support.

T4/0.01% Excellence: High-performance token operations with Guardian integration.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Set, Tuple

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from ..jwt_utils import JWTManager, get_jwt_manager

tracer = trace.get_tracer(__name__)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs): return self
    def inc(self, amount=1): pass
    def observe(self, amount): pass
    def set(self, value): pass

try:
    token_operations_total = Counter(
        'lukhas_oidc_token_operations_total',
        'Total token operations',
        ['operation', 'token_type', 'result']
    )
    active_tokens_gauge = Gauge(
        'lukhas_oidc_active_tokens_total',
        'Active tokens by type',
        ['token_type']
    )
    token_exchange_latency = Histogram(
        'lukhas_oidc_token_exchange_latency_seconds',
        'Token exchange operation latency',
        ['operation'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
except ValueError:
    token_operations_total = MockMetric()
    active_tokens_gauge = MockMetric()
    token_exchange_latency = MockMetric()


class TokenType(Enum):
    """OAuth2 token types."""
    AUTHORIZATION_CODE = "authorization_code"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"


@dataclass
class AuthorizationCode:
    """OAuth2 authorization code data."""
    code: str
    client_id: str
    user_id: str
    redirect_uri: str
    scopes: Set[str]
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    nonce: str | None = None
    created_at: int = field(default_factory=lambda: int(time.time()))
    expires_at: int = field(default_factory=lambda: int(time.time()) + 600)  # 10 minutes
    is_used: bool = False

    def is_expired(self) -> bool:
        """Check if authorization code is expired."""
        return int(time.time()) > self.expires_at

    def is_valid(self) -> bool:
        """Check if authorization code is valid for use."""
        return not self.is_used and not self.is_expired()

    def verify_pkce(self, code_verifier: str) -> bool:
        """Verify PKCE code verifier against stored challenge."""
        if not self.code_challenge:
            return True  # No PKCE required

        if self.code_challenge_method == "S256":
            # SHA256 hash of verifier
            digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
            challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
            return challenge == self.code_challenge
        elif self.code_challenge_method == "plain":
            # Plain text verifier
            return code_verifier == self.code_challenge
        else:
            return False


@dataclass
class RefreshToken:
    """OAuth2 refresh token data."""
    token: str
    client_id: str
    user_id: str
    scopes: Set[str]
    created_at: int = field(default_factory=lambda: int(time.time()))
    expires_at: int | None = None
    last_used_at: int | None = None
    is_revoked: bool = False

    def is_expired(self) -> bool:
        """Check if refresh token is expired."""
        if not self.expires_at:
            return False
        return int(time.time()) > self.expires_at

    def is_valid(self) -> bool:
        """Check if refresh token is valid for use."""
        return not self.is_revoked and not self.is_expired()

    def update_last_used(self):
        """Update last used timestamp."""
        self.last_used_at = int(time.time())


class OIDCTokenManager:
    """OAuth2/OIDC token management with Guardian integration."""

    def __init__(self, jwt_manager: JWTManager | None = None, guardian_client=None):
        """Initialize token manager."""
        self.jwt_manager = jwt_manager or get_jwt_manager()
        self.guardian_client = guardian_client

        # In-memory storage (replace with Redis/database in production)
        self._authorization_codes: Dict[str, AuthorizationCode] = {}
        self._refresh_tokens: Dict[str, RefreshToken] = {}

        # Token cleanup interval
        self._last_cleanup = time.time()
        self._cleanup_interval = 3600  # 1 hour

    def create_authorization_code(self,
                                client_id: str,
                                user_id: str,
                                redirect_uri: str,
                                scopes: Set[str],
                                code_challenge: str | None = None,
                                code_challenge_method: str | None = None,
                                nonce: str | None = None) -> str:
        """Create OAuth2 authorization code."""
        with tracer.start_span("oidc.create_authorization_code") as span:
            # Generate cryptographically secure code
            code = secrets.token_urlsafe(32)

            auth_code = AuthorizationCode(
                code=code,
                client_id=client_id,
                user_id=user_id,
                redirect_uri=redirect_uri,
                scopes=scopes,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                nonce=nonce
            )

            self._authorization_codes[code] = auth_code

            token_operations_total.labels(
                operation="create",
                token_type="authorization_code",
                result="success"
            ).inc()

            span.set_attribute("oidc.client_id", client_id)
            span.set_attribute("oidc.user_id", user_id)
            span.set_attribute("oidc.pkce_used", code_challenge is not None)

            self._maybe_cleanup()
            return code

    def exchange_authorization_code(self,
                                  code: str,
                                  client_id: str,
                                  redirect_uri: str,
                                  code_verifier: str | None = None) -> Tuple[str, str, str | None]:
        """
        Exchange authorization code for tokens.

        Returns:
            Tuple of (access_token, refresh_token, id_token)
        """
        with tracer.start_span("oidc.exchange_authorization_code") as span:
            with token_exchange_latency.labels(operation="code_exchange").time():
                # Validate authorization code
                auth_code = self._authorization_codes.get(code)
                if not auth_code or not auth_code.is_valid():
                    token_operations_total.labels(
                        operation="exchange",
                        token_type="authorization_code",
                        result="invalid_code"
                    ).inc()
                    raise ValueError("Invalid or expired authorization code")

                # Validate client and redirect URI
                if auth_code.client_id != client_id:
                    token_operations_total.labels(
                        operation="exchange",
                        token_type="authorization_code",
                        result="client_mismatch"
                    ).inc()
                    raise ValueError("Client ID mismatch")

                if auth_code.redirect_uri != redirect_uri:
                    token_operations_total.labels(
                        operation="exchange",
                        token_type="authorization_code",
                        result="redirect_mismatch"
                    ).inc()
                    raise ValueError("Redirect URI mismatch")

                # Verify PKCE if present
                if auth_code.code_challenge and not auth_code.verify_pkce(code_verifier or ""):
                    token_operations_total.labels(
                        operation="exchange",
                        token_type="authorization_code",
                        result="pkce_failed"
                    ).inc()
                    raise ValueError("PKCE verification failed")

                # Mark code as used
                auth_code.is_used = True

                # Create access token
                access_token = self.jwt_manager.create_access_token(
                    user_id=auth_code.user_id,
                    client_id=client_id,
                    scopes=list(auth_code.scopes)
                )

                # Create refresh token
                refresh_token = self._create_refresh_token(
                    client_id=client_id,
                    user_id=auth_code.user_id,
                    scopes=auth_code.scopes
                )

                # Create ID token if openid scope requested
                id_token = None
                if "openid" in auth_code.scopes:
                    id_token = self.jwt_manager.create_id_token(
                        user_id=auth_code.user_id,
                        client_id=client_id,
                        auth_time=auth_code.created_at,
                        nonce=auth_code.nonce
                    )

                token_operations_total.labels(
                    operation="exchange",
                    token_type="authorization_code",
                    result="success"
                ).inc()

                span.set_attribute("oidc.tokens_created", 2 if not id_token else 3)
                span.set_attribute("oidc.openid_flow", "openid" in auth_code.scopes)

                return access_token, refresh_token, id_token

    def refresh_access_token(self, refresh_token: str, client_id: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token.

        Returns:
            Tuple of (new_access_token, new_refresh_token)
        """
        with tracer.start_span("oidc.refresh_access_token") as span:
            with token_exchange_latency.labels(operation="token_refresh").time():
                # Validate refresh token
                refresh_data = self._refresh_tokens.get(refresh_token)
                if not refresh_data or not refresh_data.is_valid():
                    token_operations_total.labels(
                        operation="refresh",
                        token_type="refresh_token",
                        result="invalid_token"
                    ).inc()
                    raise ValueError("Invalid or expired refresh token")

                # Validate client
                if refresh_data.client_id != client_id:
                    token_operations_total.labels(
                        operation="refresh",
                        token_type="refresh_token",
                        result="client_mismatch"
                    ).inc()
                    raise ValueError("Client ID mismatch")

                # Update usage
                refresh_data.update_last_used()

                # Create new access token
                new_access_token = self.jwt_manager.create_access_token(
                    user_id=refresh_data.user_id,
                    client_id=client_id,
                    scopes=list(refresh_data.scopes)
                )

                # Create new refresh token (refresh token rotation)
                new_refresh_token = self._create_refresh_token(
                    client_id=client_id,
                    user_id=refresh_data.user_id,
                    scopes=refresh_data.scopes
                )

                # Revoke old refresh token
                refresh_data.is_revoked = True

                token_operations_total.labels(
                    operation="refresh",
                    token_type="refresh_token",
                    result="success"
                ).inc()

                span.set_attribute("oidc.user_id", refresh_data.user_id)

                return new_access_token, new_refresh_token

    def revoke_token(self, token: str, token_type_hint: str | None = None) -> bool:
        """Revoke a token (refresh token or access token)."""
        with tracer.start_span("oidc.revoke_token") as span:
            # For refresh tokens, we can revoke from our storage
            if refresh_data := self._refresh_tokens.get(token):
                refresh_data.is_revoked = True
                token_operations_total.labels(
                    operation="revoke",
                    token_type="refresh_token",
                    result="success"
                ).inc()
                span.set_attribute("oidc.token_type", "refresh_token")
                return True

            # For access tokens (JWTs), we would need a token blacklist
            # This is a simplified implementation
            token_operations_total.labels(
                operation="revoke",
                token_type=token_type_hint or "unknown",
                result="not_found"
            ).inc()
            span.set_attribute("oidc.token_revoked", False)
            return False

    def introspect_token(self, token: str) -> Dict[str, Any]:
        """Introspect a token (RFC 7662)."""
        with tracer.start_span("oidc.introspect_token") as span:
            try:
                # Try to decode as JWT (access token or ID token)
                claims = self.jwt_manager.verify_token(token)

                result = {
                    "active": True,
                    "sub": claims.sub,
                    "iss": claims.iss,
                    "aud": claims.aud,
                    "exp": claims.exp,
                    "iat": claims.iat,
                    "token_type": claims.token_type or "Bearer"
                }

                if claims.scope:
                    result["scope"] = claims.scope

                if claims.lukhas_tier:
                    result["lukhas_tier"] = claims.lukhas_tier

                span.set_attribute("oidc.token_active", True)
                return result

            except Exception:
                # Check if it's a refresh token
                if refresh_data := self._refresh_tokens.get(token):
                    if refresh_data.is_valid():
                        span.set_attribute("oidc.token_active", True)
                        return {
                            "active": True,
                            "sub": refresh_data.user_id,
                            "client_id": refresh_data.client_id,
                            "token_type": "refresh_token",
                            "scope": " ".join(refresh_data.scopes)
                        }

                span.set_attribute("oidc.token_active", False)
                return {"active": False}

    def _create_refresh_token(self, client_id: str, user_id: str, scopes: Set[str]) -> str:
        """Create a refresh token."""
        token = secrets.token_urlsafe(32)

        refresh_data = RefreshToken(
            token=token,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=int(time.time()) + (86400 * 30)  # 30 days
        )

        self._refresh_tokens[token] = refresh_data

        active_tokens_gauge.labels(token_type="refresh_token").set(
            len([t for t in self._refresh_tokens.values() if t.is_valid()])
        )

        return token

    def _maybe_cleanup(self):
        """Clean up expired tokens periodically."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        # Clean up expired authorization codes
        expired_codes = [
            code for code, data in self._authorization_codes.items()
            if data.is_expired()
        ]
        for code in expired_codes:
            del self._authorization_codes[code]

        # Clean up expired refresh tokens
        expired_refresh = [
            token for token, data in self._refresh_tokens.items()
            if data.is_expired()
        ]
        for token in expired_refresh:
            del self._refresh_tokens[token]

        self._last_cleanup = current_time

        # Update metrics
        active_tokens_gauge.labels(token_type="authorization_code").set(
            len([c for c in self._authorization_codes.values() if c.is_valid()])
        )
        active_tokens_gauge.labels(token_type="refresh_token").set(
            len([t for t in self._refresh_tokens.values() if t.is_valid()])
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get token manager statistics."""
        self._maybe_cleanup()

        return {
            "active_authorization_codes": len([c for c in self._authorization_codes.values() if c.is_valid()]),
            "active_refresh_tokens": len([t for t in self._refresh_tokens.values() if t.is_valid()]),
            "total_authorization_codes": len(self._authorization_codes),
            "total_refresh_tokens": len(self._refresh_tokens),
        }


# Singleton instance
_token_manager: OIDCTokenManager | None = None

def get_oidc_token_manager() -> OIDCTokenManager:
    """Get the default OIDC token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = OIDCTokenManager()
    return _token_manager
