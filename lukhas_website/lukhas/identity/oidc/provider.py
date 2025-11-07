#!/usr/bin/env python3
"""
OIDC Provider Core - OpenID Connect 1.0 Provider Implementation

Main OIDC provider class implementing OAuth2 Authorization Code Flow + PKCE.
Integrates with LUKHAS I.2 Tiered Authentication and Guardian system.

T4/0.01% Excellence: Production-ready OIDC provider with comprehensive validation.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, List

from opentelemetry import trace
from prometheus_client import Counter, Histogram

from ..jwt_utils import get_jwt_manager
from .client_registry import ClientRegistry, OIDCClient
from .discovery import DiscoveryProvider
from .tokens import OIDCTokenManager

tracer = trace.get_tracer(__name__)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs): return self
    def inc(self, amount=1): pass
    def observe(self, amount): pass

try:
    oidc_requests_total = Counter(
        'lukhas_oidc_requests_total',
        'Total OIDC requests',
        ['endpoint', 'client_id', 'result']
    )
    oidc_request_latency = Histogram(
        'lukhas_oidc_request_latency_seconds',
        'OIDC request latency',
        ['endpoint'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
except ValueError:
    oidc_requests_total = MockMetric()
    oidc_request_latency = MockMetric()


@dataclass
class AuthorizationRequest:
    """OAuth2 authorization request parameters."""
    response_type: str
    client_id: str
    redirect_uri: str
    scope: str
    state: str | None = None
    nonce: str | None = None
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    prompt: str | None = None
    max_age: int | None = None

    @classmethod
    def from_query_params(cls, params: dict[str, str]) -> AuthorizationRequest:
        """Create from URL query parameters."""
        return cls(
            response_type=params.get("response_type", ""),
            client_id=params.get("client_id", ""),
            redirect_uri=params.get("redirect_uri", ""),
            scope=params.get("scope", ""),
            state=params.get("state"),
            nonce=params.get("nonce"),
            code_challenge=params.get("code_challenge"),
            code_challenge_method=params.get("code_challenge_method"),
            prompt=params.get("prompt"),
            max_age=int(params["max_age"]) if params.get("max_age") else None
        )

    def validate(self) -> list[str]:
        """Validate authorization request parameters."""
        errors = []

        if not self.response_type:
            errors.append("Missing response_type")
        elif self.response_type != "code":
            errors.append("Unsupported response_type (only 'code' supported)")

        if not self.client_id:
            errors.append("Missing client_id")

        if not self.redirect_uri:
            errors.append("Missing redirect_uri")

        if not self.scope:
            errors.append("Missing scope")

        # PKCE validation
        if self.code_challenge:
            if not self.code_challenge_method:
                errors.append("Missing code_challenge_method when code_challenge is present")
            elif self.code_challenge_method not in ["S256", "plain"]:
                errors.append("Invalid code_challenge_method (must be S256 or plain)")

        return errors


@dataclass
class TokenRequest:
    """OAuth2 token request parameters."""
    grant_type: str
    client_id: str
    code: str | None = None
    redirect_uri: str | None = None
    code_verifier: str | None = None
    refresh_token: str | None = None
    client_secret: str | None = None

    @classmethod
    def from_form_data(cls, data: dict[str, str]) -> TokenRequest:
        """Create from form data."""
        return cls(
            grant_type=data.get("grant_type", ""),
            client_id=data.get("client_id", ""),
            code=data.get("code"),
            redirect_uri=data.get("redirect_uri"),
            code_verifier=data.get("code_verifier"),
            refresh_token=data.get("refresh_token"),
            client_secret=data.get("client_secret")
        )

    def validate(self) -> list[str]:
        """Validate token request parameters."""
        errors = []

        if not self.grant_type:
            errors.append("Missing grant_type")
        elif self.grant_type not in ["authorization_code", "refresh_token"]:
            errors.append("Unsupported grant_type")

        if not self.client_id:
            errors.append("Missing client_id")

        if self.grant_type == "authorization_code":
            if not self.code:
                errors.append("Missing code for authorization_code grant")
            if not self.redirect_uri:
                errors.append("Missing redirect_uri for authorization_code grant")

        elif self.grant_type == "refresh_token":
            if not self.refresh_token:
                errors.append("Missing refresh_token for refresh_token grant")

        return errors


class OIDCProvider:
    """OpenID Connect 1.0 Provider with LUKHAS integration."""

    def __init__(self,
                 issuer: str = "https://auth.ai",
                 client_registry: ClientRegistry | None = None,
                 token_manager: OIDCTokenManager | None = None,
                 discovery_provider: DiscoveryProvider | None = None,
                 guardian_client=None):
        """
        Initialize OIDC provider.

        Args:
            issuer: OIDC issuer identifier
            client_registry: OAuth2 client registry
            token_manager: Token management service
            discovery_provider: Discovery document provider
            guardian_client: Guardian system client for validation
        """
        self.issuer = issuer
        self.client_registry = client_registry or ClientRegistry(guardian_client)
        self.token_manager = token_manager or OIDCTokenManager(guardian_client=guardian_client)
        self.discovery_provider = discovery_provider or DiscoveryProvider(issuer)
        self.guardian_client = guardian_client
        self.jwt_manager = get_jwt_manager()

    # Discovery and JWKS endpoints

    def get_discovery_document(self) -> dict[str, Any]:
        """Get OpenID Connect Discovery document."""
        with tracer.start_span("oidc.discovery") as span:
            with oidc_request_latency.labels(endpoint="discovery").time():
                document = self.discovery_provider.get_discovery_document()

                oidc_requests_total.labels(
                    endpoint="discovery",
                    client_id="n/a",
                    result="success"
                ).inc()

                span.set_attribute("oidc.issuer", self.issuer)
                return document.to_dict()

    def get_jwks(self) -> dict[str, Any]:
        """Get JSON Web Key Set."""
        with tracer.start_span("oidc.jwks") as span:
            with oidc_request_latency.labels(endpoint="jwks").time():
                jwks = self.jwt_manager.get_jwks()

                oidc_requests_total.labels(
                    endpoint="jwks",
                    client_id="n/a",
                    result="success"
                ).inc()

                span.set_attribute("oidc.key_count", len(jwks.get("keys", [])))
                return jwks

    # Authorization endpoint

    def handle_authorization_request(self,
                                   params: dict[str, str],
                                   user_authenticated: bool = False,
                                   user_id: str | None = None,
                                   authentication_tier: str | None = None) -> dict[str, Any]:
        """
        Handle OAuth2 authorization request.

        Args:
            params: Query parameters from authorization request
            user_authenticated: Whether user is already authenticated
            user_id: Authenticated user ID
            authentication_tier: LUKHAS authentication tier (T1-T5)

        Returns:
            Dict containing response data or error information
        """
        with tracer.start_span("oidc.authorization_request") as span:
            with oidc_request_latency.labels(endpoint="authorize").time():
                try:
                    # Parse and validate request
                    auth_request = AuthorizationRequest.from_query_params(params)
                    validation_errors = auth_request.validate()

                    if validation_errors:
                        span.set_attribute("oidc.error", "invalid_request")
                        return self._error_response(
                            "invalid_request",
                            f"Validation errors: {', '.join(validation_errors)}",
                            auth_request.state
                        )

                    # Validate client
                    client = self.client_registry.get_client(auth_request.client_id)
                    if not client or not client.is_active:
                        span.set_attribute("oidc.error", "invalid_client")
                        return self._error_response(
                            "invalid_client",
                            "Unknown or inactive client",
                            auth_request.state
                        )

                    # Validate redirect URI
                    if not client.is_redirect_uri_allowed(auth_request.redirect_uri):
                        span.set_attribute("oidc.error", "invalid_redirect_uri")
                        return self._error_response(
                            "invalid_request",
                            "Invalid redirect_uri",
                            auth_request.state
                        )

                    # Validate scopes
                    requested_scopes = set(auth_request.scope.split())
                    if not all(client.is_scope_allowed(scope) for scope in requested_scopes):
                        span.set_attribute("oidc.error", "invalid_scope")
                        return self._redirect_error_response(
                            auth_request.redirect_uri,
                            "invalid_scope",
                            "One or more requested scopes are not allowed",
                            auth_request.state
                        )

                    # Validate PKCE for public clients
                    if client.require_pkce and not auth_request.code_challenge:
                        span.set_attribute("oidc.error", "invalid_request")
                        return self._redirect_error_response(
                            auth_request.redirect_uri,
                            "invalid_request",
                            "PKCE code_challenge is required",
                            auth_request.state
                        )

                    if client.require_pkce_s256 and auth_request.code_challenge_method != "S256":
                        span.set_attribute("oidc.error", "invalid_request")
                        return self._redirect_error_response(
                            auth_request.redirect_uri,
                            "invalid_request",
                            "PKCE S256 method is required",
                            auth_request.state
                        )

                    # Validate authentication tier
                    if authentication_tier and not client.is_tier_allowed(authentication_tier):
                        span.set_attribute("oidc.error", "insufficient_tier")
                        return self._redirect_error_response(
                            auth_request.redirect_uri,
                            "access_denied",
                            f"Authentication tier {authentication_tier} not allowed for this client",
                            auth_request.state
                        )

                    # Check if user needs to authenticate
                    if not user_authenticated or not user_id:
                        span.set_attribute("oidc.action", "authentication_required")
                        return {
                            "action": "authenticate",
                            "login_url": f"/auth/login?{urllib.parse.urlencode(params)}",
                            "client": client.to_dict()
                        }

                    # Check if user needs to consent
                    if auth_request.prompt == "consent" or self._requires_consent(client, requested_scopes):
                        span.set_attribute("oidc.action", "consent_required")
                        return {
                            "action": "consent",
                            "consent_url": f"/auth/consent?{urllib.parse.urlencode(params)}",
                            "client": client.to_dict(),
                            "scopes": list(requested_scopes)
                        }

                    # Generate authorization code
                    auth_code = self.token_manager.create_authorization_code(
                        client_id=auth_request.client_id,
                        user_id=user_id,
                        redirect_uri=auth_request.redirect_uri,
                        scopes=requested_scopes,
                        code_challenge=auth_request.code_challenge,
                        code_challenge_method=auth_request.code_challenge_method,
                        nonce=auth_request.nonce
                    )

                    # Build redirect response
                    redirect_params = {"code": auth_code}
                    if auth_request.state:
                        redirect_params["state"] = auth_request.state

                    redirect_url = f"{auth_request.redirect_uri}?{urllib.parse.urlencode(redirect_params)}"

                    oidc_requests_total.labels(
                        endpoint="authorize",
                        client_id=auth_request.client_id,
                        result="success"
                    ).inc()

                    span.set_attribute("oidc.client_id", auth_request.client_id)
                    span.set_attribute("oidc.user_id", user_id)
                    span.set_attribute("oidc.action", "code_generated")

                    return {
                        "action": "redirect",
                        "redirect_url": redirect_url,
                        "code": auth_code
                    }

                except Exception as e:
                    oidc_requests_total.labels(
                        endpoint="authorize",
                        client_id=params.get("client_id", "unknown"),
                        result="error"
                    ).inc()
                    span.set_attribute("oidc.error", str(e))
                    raise

    # Token endpoint

    def handle_token_request(self, form_data: dict[str, str]) -> dict[str, Any]:
        """
        Handle OAuth2 token request.

        Args:
            form_data: Form data from token request

        Returns:
            Token response or error
        """
        with tracer.start_span("oidc.token_request") as span:
            with oidc_request_latency.labels(endpoint="token").time():
                try:
                    # Parse and validate request
                    token_request = TokenRequest.from_form_data(form_data)
                    validation_errors = token_request.validate()

                    if validation_errors:
                        span.set_attribute("oidc.error", "invalid_request")
                        return self._token_error_response(
                            "invalid_request",
                            f"Validation errors: {', '.join(validation_errors)}"
                        )

                    # Authenticate client
                    client = self.client_registry.authenticate_client(
                        token_request.client_id,
                        token_request.client_secret
                    )

                    if not client:
                        span.set_attribute("oidc.error", "invalid_client")
                        return self._token_error_response(
                            "invalid_client",
                            "Client authentication failed"
                        )

                    # Validate grant type
                    if not client.is_grant_type_allowed(token_request.grant_type):
                        span.set_attribute("oidc.error", "unsupported_grant_type")
                        return self._token_error_response(
                            "unsupported_grant_type",
                            f"Grant type {token_request.grant_type} not allowed for this client"
                        )

                    if token_request.grant_type == "authorization_code":
                        return self._handle_authorization_code_grant(token_request, client, span)
                    elif token_request.grant_type == "refresh_token":
                        return self._handle_refresh_token_grant(token_request, client, span)
                    else:
                        span.set_attribute("oidc.error", "unsupported_grant_type")
                        return self._token_error_response(
                            "unsupported_grant_type",
                            f"Grant type {token_request.grant_type} not supported"
                        )

                except Exception as e:
                    oidc_requests_total.labels(
                        endpoint="token",
                        client_id=form_data.get("client_id", "unknown"),
                        result="error"
                    ).inc()
                    span.set_attribute("oidc.error", str(e))
                    raise

    def _handle_authorization_code_grant(self,
                                       token_request: TokenRequest,
                                       client: OIDCClient,
                                       span) -> dict[str, Any]:
        """Handle authorization code grant flow."""
        try:
            # Exchange authorization code for tokens
            access_token, refresh_token, id_token = self.token_manager.exchange_authorization_code(
                code=token_request.code,
                client_id=token_request.client_id,
                redirect_uri=token_request.redirect_uri,
                code_verifier=token_request.code_verifier
            )

            response = {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": client.access_token_lifetime,
                "refresh_token": refresh_token
            }

            if id_token:
                response["id_token"] = id_token

            oidc_requests_total.labels(
                endpoint="token",
                client_id=token_request.client_id,
                result="success"
            ).inc()

            span.set_attribute("oidc.grant_type", "authorization_code")
            span.set_attribute("oidc.tokens_issued", len([t for t in [access_token, refresh_token, id_token] if t]))

            return response

        except ValueError as e:
            span.set_attribute("oidc.error", "invalid_grant")
            return self._token_error_response("invalid_grant", str(e))

    def _handle_refresh_token_grant(self,
                                  token_request: TokenRequest,
                                  client: OIDCClient,
                                  span) -> dict[str, Any]:
        """Handle refresh token grant flow."""
        try:
            # Refresh tokens
            access_token, new_refresh_token = self.token_manager.refresh_access_token(
                refresh_token=token_request.refresh_token,
                client_id=token_request.client_id
            )

            response = {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": client.access_token_lifetime,
                "refresh_token": new_refresh_token
            }

            oidc_requests_total.labels(
                endpoint="token",
                client_id=token_request.client_id,
                result="success"
            ).inc()

            span.set_attribute("oidc.grant_type", "refresh_token")

            return response

        except ValueError as e:
            span.set_attribute("oidc.error", "invalid_grant")
            return self._token_error_response("invalid_grant", str(e))

    # UserInfo endpoint

    def handle_userinfo_request(self, access_token: str) -> dict[str, Any]:
        """Handle OpenID Connect UserInfo request."""
        with tracer.start_span("oidc.userinfo") as span:
            with oidc_request_latency.labels(endpoint="userinfo").time():
                try:
                    # Verify access token
                    claims = self.jwt_manager.verify_token(access_token, audience=["lukhas-api"])

                    # Build UserInfo response
                    userinfo = {
                        "sub": claims.sub
                    }

                    # Add additional claims based on scope
                    if claims.scope and "profile" in claims.scope:
                        # In production, fetch from user database
                        userinfo.update({
                            "name": f"User {claims.sub}",
                            "given_name": "User",
                            "family_name": claims.sub
                        })

                    if claims.scope and "email" in claims.scope:
                        userinfo["email"] = f"user-{claims.sub}@ai"

                    # Add LUKHAS-specific claims
                    if claims.lukhas_tier:
                        userinfo["lukhas_tier"] = claims.lukhas_tier

                    if claims.permissions:
                        userinfo["permissions"] = claims.permissions

                    oidc_requests_total.labels(
                        endpoint="userinfo",
                        client_id=getattr(claims, "client_id", "unknown"),
                        result="success"
                    ).inc()

                    span.set_attribute("oidc.subject", claims.sub)
                    return userinfo

                except Exception as e:
                    oidc_requests_total.labels(
                        endpoint="userinfo",
                        client_id="unknown",
                        result="error"
                    ).inc()
                    span.set_attribute("oidc.error", str(e))
                    raise

    # Helper methods

    def _requires_consent(self, client: OIDCClient, scopes: set) -> bool:
        """Check if user consent is required."""
        # For development, we can skip consent for trusted clients
        if client.client_id.startswith("lukhas-dev"):
            return False

        # Require consent for sensitive scopes
        sensitive_scopes = {"lukhas:admin", "lukhas:tier"}
        return bool(scopes.intersection(sensitive_scopes))

    def _error_response(self, error: str, description: str, state: str | None = None) -> dict[str, Any]:
        """Create error response for direct errors."""
        response = {
            "error": error,
            "error_description": description
        }
        if state:
            response["state"] = state
        return response

    def _redirect_error_response(self,
                                redirect_uri: str,
                                error: str,
                                description: str,
                                state: str | None = None) -> dict[str, Any]:
        """Create redirect error response."""
        error_params = {
            "error": error,
            "error_description": description
        }
        if state:
            error_params["state"] = state

        redirect_url = f"{redirect_uri}?{urllib.parse.urlencode(error_params)}"

        return {
            "action": "redirect",
            "redirect_url": redirect_url,
            "error": error
        }

    def _token_error_response(self, error: str, description: str) -> dict[str, Any]:
        """Create token endpoint error response."""
        return {
            "error": error,
            "error_description": description
        }


# Global provider instance
_oidc_provider: OIDCProvider | None = None

def get_oidc_provider() -> OIDCProvider:
    """Get the default OIDC provider instance."""
    global _oidc_provider
    if _oidc_provider is None:
        _oidc_provider = OIDCProvider()
    return _oidc_provider
