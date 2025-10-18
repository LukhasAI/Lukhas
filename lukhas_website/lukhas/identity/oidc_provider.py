"""
I.3 OIDC Provider & JWT - Complete OAuth2/OpenID Connect implementation
Production-ready OIDC Provider with JWT token management and OAuth2 flows.
"""

import asyncio
import base64
import hashlib
import logging
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlencode

from identity.jwt_utils import JWTManager
from identity.observability import IdentityObservability
from identity.session_manager import SessionManager
from identity.tiers import TierSystem

logger = logging.getLogger(__name__)


class GrantType(Enum):
    """OAuth2 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    RESOURCE_OWNER_PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"


class ResponseType(Enum):
    """OAuth2 response types"""
    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"
    CODE_TOKEN = "code token"
    CODE_ID_TOKEN = "code id_token"
    TOKEN_ID_TOKEN = "token id_token"
    CODE_TOKEN_ID_TOKEN = "code token id_token"


class TokenType(Enum):
    """Token types"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    AUTHORIZATION_CODE = "authorization_code"


@dataclass
class OIDCClient:
    """OIDC Client registration"""
    client_id: str
    client_secret: str
    client_name: str
    redirect_uris: List[str]
    grant_types: List[GrantType]
    response_types: List[ResponseType]
    scope: Set[str]
    token_endpoint_auth_method: str = "client_secret_basic"
    id_token_signed_response_alg: str = "RS256"
    userinfo_signed_response_alg: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizationCode:
    """Authorization code for OAuth2 flow"""
    code: str
    client_id: str
    lambda_id: str
    redirect_uri: str
    scope: Set[str]
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))
    used: bool = False
    session_id: Optional[str] = None


@dataclass
class AccessToken:
    """Access token information"""
    token: str
    client_id: str
    lambda_id: str
    scope: Set[str]
    token_type: str = "Bearer"
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    session_id: Optional[str] = None
    tier_level: int = 1


@dataclass
class RefreshToken:
    """Refresh token information"""
    token: str
    client_id: str
    lambda_id: str
    scope: Set[str]
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    access_token_id: Optional[str] = None


@dataclass
class IDToken:
    """ID Token information"""
    token: str
    client_id: str
    lambda_id: str
    issuer: str
    audience: str
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    issued_at: datetime = field(default_factory=datetime.utcnow)
    auth_time: datetime = field(default_factory=datetime.utcnow)
    nonce: Optional[str] = None
    claims: Dict[str, Any] = field(default_factory=dict)


class OIDCProvider:
    """
    I.3 OIDC Provider & JWT System
    Complete OAuth2/OpenID Connect provider with JWT token management
    """

    def __init__(self,
                 issuer: str,
                 jwt_manager: JWTManager,
                 session_manager: SessionManager,
                 tier_system: TierSystem,
                 observability: IdentityObservability,
                 authorization_code_ttl: int = 600,  # 10 minutes
                 access_token_ttl: int = 3600,       # 1 hour
                 refresh_token_ttl: int = 2592000,   # 30 days
                 id_token_ttl: int = 3600):          # 1 hour
        self.issuer = issuer
        self.jwt_manager = jwt_manager
        self.session_manager = session_manager
        self.tier_system = tier_system
        self.observability = observability
        self.authorization_code_ttl = authorization_code_ttl
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl
        self.id_token_ttl = id_token_ttl

        # Storage (production would use Redis/PostgreSQL)
        self.clients: Dict[str, OIDCClient] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        self.id_tokens: Dict[str, IDToken] = {}

        # OIDC Discovery metadata
        self.discovery_metadata = self._generate_discovery_metadata()

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the OIDC provider"""
        logger.info("🚀 Starting OIDC Provider")

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("✅ OIDC Provider started")

    async def stop(self):
        """Stop the OIDC provider"""
        logger.info("🛑 Stopping OIDC Provider")

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ OIDC Provider stopped")

    async def register_client(self,
                            client_name: str,
                            redirect_uris: List[str],
                            grant_types: List[str],
                            response_types: List[str],
                            scope: List[str]) -> OIDCClient:
        """Register a new OIDC client"""

        client_id = f"client_{uuid.uuid4().hex[:16]}"
        client_secret = secrets.token_urlsafe(32)

        # Convert string enums to enum objects
        grant_type_enums = []
        for gt in grant_types:
            try:
                grant_type_enums.append(GrantType(gt))
            except ValueError:
                logger.warning(f"Unknown grant type: {gt}")

        response_type_enums = []
        for rt in response_types:
            try:
                response_type_enums.append(ResponseType(rt))
            except ValueError:
                logger.warning(f"Unknown response type: {rt}")

        client = OIDCClient(
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name,
            redirect_uris=redirect_uris,
            grant_types=grant_type_enums,
            response_types=response_type_enums,
            scope=set(scope)
        )

        self.clients[client_id] = client

        await self.observability.record_client_registered(client_id, client_name)

        logger.info(f"📝 Registered OIDC client: {client_id} ({client_name})")
        return client

    async def authorize(self,
                       client_id: str,
                       response_type: str,
                       redirect_uri: str,
                       scope: str,
                       state: Optional[str] = None,
                       nonce: Optional[str] = None,
                       code_challenge: Optional[str] = None,
                       code_challenge_method: Optional[str] = None,
                       lambda_id: Optional[str] = None,
                       session_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle OAuth2 authorization request"""

        # Validate client
        client = self.clients.get(client_id)
        if not client or not client.is_active:
            return self._error_response("invalid_client", "Invalid client")

        # Validate redirect URI
        if redirect_uri not in client.redirect_uris:
            return self._error_response("invalid_request", "Invalid redirect URI")

        # Validate response type
        try:
            response_type_enum = ResponseType(response_type)
            if response_type_enum not in client.response_types:
                return self._error_response("unsupported_response_type", "Unsupported response type")
        except ValueError:
            return self._error_response("unsupported_response_type", "Invalid response type")

        # Validate scope
        requested_scopes = set(scope.split())
        if not requested_scopes.issubset(client.scope):
            return self._error_response("invalid_scope", "Invalid scope")

        # Require authentication (lambda_id)
        if not lambda_id:
            return self._authentication_required_response(client_id, response_type, redirect_uri, scope, state)

        # Validate session if provided
        if session_id:
            session = await self.session_manager.validate_session(session_id)
            if not session or session.lambda_id != lambda_id:
                return self._error_response("invalid_request", "Invalid session")

        # Process different response types
        if response_type == "code":
            return await self._handle_authorization_code_flow(
                client, lambda_id, redirect_uri, requested_scopes, state,
                code_challenge, code_challenge_method, session_id, nonce
            )
        elif response_type == "token":
            return await self._handle_implicit_flow(
                client, lambda_id, redirect_uri, requested_scopes, state, session_id
            )
        elif response_type == "id_token":
            return await self._handle_id_token_flow(
                client, lambda_id, redirect_uri, requested_scopes, state, nonce, session_id
            )
        else:
            return self._error_response("unsupported_response_type", "Unsupported response type")

    async def token(self,
                   grant_type: str,
                   client_id: Optional[str] = None,
                   client_secret: Optional[str] = None,
                   code: Optional[str] = None,
                   redirect_uri: Optional[str] = None,
                   refresh_token: Optional[str] = None,
                   code_verifier: Optional[str] = None) -> Dict[str, Any]:
        """Handle OAuth2 token request"""

        # Authenticate client
        client = await self._authenticate_client(client_id, client_secret)
        if not client:
            return self._error_response("invalid_client", "Client authentication failed")

        try:
            grant_type_enum = GrantType(grant_type)
        except ValueError:
            return self._error_response("unsupported_grant_type", "Unsupported grant type")

        if grant_type_enum == GrantType.AUTHORIZATION_CODE:
            return await self._handle_authorization_code_token(client, code, redirect_uri, code_verifier)
        elif grant_type_enum == GrantType.REFRESH_TOKEN:
            return await self._handle_refresh_token(client, refresh_token)
        elif grant_type_enum == GrantType.CLIENT_CREDENTIALS:
            return await self._handle_client_credentials(client)
        else:
            return self._error_response("unsupported_grant_type", "Grant type not supported")

    async def userinfo(self, access_token: str) -> Dict[str, Any]:
        """Handle OpenID Connect userinfo request"""

        # Validate access token
        token_info = await self._validate_access_token(access_token)
        if not token_info:
            return self._error_response("invalid_token", "Invalid access token")

        # Check if openid scope is present
        if "openid" not in token_info.scope:
            return self._error_response("insufficient_scope", "OpenID scope required")

        # Get user information
        userinfo = await self._get_userinfo(token_info.lambda_id, token_info.scope)

        await self.observability.record_userinfo_request(token_info.client_id, token_info.lambda_id)

        return userinfo

    async def introspect(self, token: str, token_type_hint: Optional[str] = None) -> Dict[str, Any]:
        """Handle OAuth2 token introspection"""

        # Try to find token in different stores
        token_info = None
        active = False

        # Check access tokens
        if token in self.access_tokens:
            token_info = self.access_tokens[token]
            active = datetime.utcnow() < token_info.expires_at
            token_type = "access_token"
        # Check refresh tokens
        elif token in self.refresh_tokens:
            token_info = self.refresh_tokens[token]
            active = datetime.utcnow() < token_info.expires_at
            token_type = "refresh_token"

        if not token_info:
            return {"active": False}

        introspection_response = {
            "active": active,
            "client_id": token_info.client_id,
            "username": token_info.lambda_id,
            "scope": " ".join(token_info.scope),
            "exp": int(token_info.expires_at.timestamp()),
            "token_type": token_type
        }

        if hasattr(token_info, 'tier_level'):
            introspection_response["tier_level"] = token_info.tier_level

        return introspection_response

    async def revoke(self, token: str, token_type_hint: Optional[str] = None) -> bool:
        """Handle OAuth2 token revocation"""

        revoked = False

        # Revoke access token
        if token in self.access_tokens:
            del self.access_tokens[token]
            revoked = True

        # Revoke refresh token
        if token in self.refresh_tokens:
            refresh_token_info = self.refresh_tokens[token]
            del self.refresh_tokens[token]

            # Also revoke associated access tokens
            access_tokens_to_revoke = []
            for at_token, at_info in self.access_tokens.items():
                if (at_info.client_id == refresh_token_info.client_id and
                    at_info.lambda_id == refresh_token_info.lambda_id):
                    access_tokens_to_revoke.append(at_token)

            for at_token in access_tokens_to_revoke:
                del self.access_tokens[at_token]

            revoked = True

        if revoked:
            await self.observability.record_token_revoked("manual_revocation")

        return revoked

    def get_discovery_metadata(self) -> Dict[str, Any]:
        """Get OpenID Connect discovery metadata"""
        return self.discovery_metadata.copy()

    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set"""
        return await self.jwt_manager.get_public_keys()

    async def _handle_authorization_code_flow(self,
                                            client: OIDCClient,
                                            lambda_id: str,
                                            redirect_uri: str,
                                            scope: Set[str],
                                            state: Optional[str],
                                            code_challenge: Optional[str],
                                            code_challenge_method: Optional[str],
                                            session_id: Optional[str],
                                            nonce: Optional[str]) -> Dict[str, Any]:
        """Handle authorization code flow"""

        # Generate authorization code
        code = secrets.token_urlsafe(32)

        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            lambda_id=lambda_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            session_id=session_id
        )

        self.authorization_codes[code] = auth_code

        # Build response
        response_params = {"code": code}
        if state:
            response_params["state"] = state

        await self.observability.record_authorization_granted(client.client_id, lambda_id)

        return {
            "success": True,
            "redirect_uri": f"{redirect_uri}?{urlencode(response_params)}"
        }

    async def _handle_implicit_flow(self,
                                  client: OIDCClient,
                                  lambda_id: str,
                                  redirect_uri: str,
                                  scope: Set[str],
                                  state: Optional[str],
                                  session_id: Optional[str]) -> Dict[str, Any]:
        """Handle implicit flow"""

        # Get tier level
        tier_level = await self.tier_system.get_user_tier_level(lambda_id)

        # Generate access token
        access_token = await self._create_access_token(client.client_id, lambda_id, scope, tier_level, session_id)

        # Build response
        response_params = {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": int((access_token.expires_at - datetime.utcnow()).total_seconds())
        }
        if state:
            response_params["state"] = state

        fragment = urlencode(response_params)

        return {
            "success": True,
            "redirect_uri": f"{redirect_uri}#{fragment}"
        }

    async def _handle_id_token_flow(self,
                                  client: OIDCClient,
                                  lambda_id: str,
                                  redirect_uri: str,
                                  scope: Set[str],
                                  state: Optional[str],
                                  nonce: Optional[str],
                                  session_id: Optional[str]) -> Dict[str, Any]:
        """Handle ID token flow"""

        # Generate ID token
        id_token = await self._create_id_token(client.client_id, lambda_id, scope, nonce)

        # Build response
        response_params = {"id_token": id_token.token}
        if state:
            response_params["state"] = state

        fragment = urlencode(response_params)

        return {
            "success": True,
            "redirect_uri": f"{redirect_uri}#{fragment}"
        }

    async def _handle_authorization_code_token(self,
                                             client: OIDCClient,
                                             code: Optional[str],
                                             redirect_uri: Optional[str],
                                             code_verifier: Optional[str]) -> Dict[str, Any]:
        """Handle authorization code token exchange"""

        if not code:
            return self._error_response("invalid_request", "Missing authorization code")

        # Validate authorization code
        auth_code = self.authorization_codes.get(code)
        if not auth_code or auth_code.used or datetime.utcnow() > auth_code.expires_at:
            return self._error_response("invalid_grant", "Invalid authorization code")

        # Validate client and redirect URI
        if auth_code.client_id != client.client_id or auth_code.redirect_uri != redirect_uri:
            return self._error_response("invalid_grant", "Authorization code mismatch")

        # Validate PKCE if present
        if auth_code.code_challenge:
            if not code_verifier:
                return self._error_response("invalid_request", "Code verifier required")

            if not self._verify_pkce(auth_code.code_challenge, auth_code.code_challenge_method, code_verifier):
                return self._error_response("invalid_grant", "PKCE verification failed")

        # Mark code as used
        auth_code.used = True

        # Get tier level
        tier_level = await self.tier_system.get_user_tier_level(auth_code.lambda_id)

        # Generate tokens
        access_token = await self._create_access_token(
            client.client_id, auth_code.lambda_id, auth_code.scope, tier_level, auth_code.session_id
        )

        refresh_token = await self._create_refresh_token(
            client.client_id, auth_code.lambda_id, auth_code.scope, access_token.token
        )

        response = {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": int((access_token.expires_at - datetime.utcnow()).total_seconds()),
            "refresh_token": refresh_token.token
        }

        # Add ID token if openid scope
        if "openid" in auth_code.scope:
            id_token = await self._create_id_token(client.client_id, auth_code.lambda_id, auth_code.scope)
            response["id_token"] = id_token.token

        await self.observability.record_token_issued(client.client_id, "authorization_code")

        return response

    async def _handle_refresh_token(self, client: OIDCClient, refresh_token_str: Optional[str]) -> Dict[str, Any]:
        """Handle refresh token grant"""

        if not refresh_token_str:
            return self._error_response("invalid_request", "Missing refresh token")

        refresh_token = self.refresh_tokens.get(refresh_token_str)
        if not refresh_token or datetime.utcnow() > refresh_token.expires_at:
            return self._error_response("invalid_grant", "Invalid refresh token")

        if refresh_token.client_id != client.client_id:
            return self._error_response("invalid_grant", "Refresh token client mismatch")

        # Get tier level
        tier_level = await self.tier_system.get_user_tier_level(refresh_token.lambda_id)

        # Generate new access token
        access_token = await self._create_access_token(
            client.client_id, refresh_token.lambda_id, refresh_token.scope, tier_level
        )

        response = {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": int((access_token.expires_at - datetime.utcnow()).total_seconds())
        }

        # Optionally issue new refresh token
        if client.grant_types and GrantType.REFRESH_TOKEN in client.grant_types:
            new_refresh_token = await self._create_refresh_token(
                client.client_id, refresh_token.lambda_id, refresh_token.scope, access_token.token
            )
            response["refresh_token"] = new_refresh_token.token

            # Remove old refresh token
            del self.refresh_tokens[refresh_token_str]

        await self.observability.record_token_issued(client.client_id, "refresh_token")

        return response

    async def _handle_client_credentials(self, client: OIDCClient) -> Dict[str, Any]:
        """Handle client credentials grant"""

        # Get tier level for client
        tier_level = 1  # Default tier for client credentials

        # Generate access token
        access_token = await self._create_access_token(
            client.client_id, client.client_id, client.scope, tier_level
        )

        response = {
            "access_token": access_token.token,
            "token_type": access_token.token_type,
            "expires_in": int((access_token.expires_at - datetime.utcnow()).total_seconds())
        }

        await self.observability.record_token_issued(client.client_id, "client_credentials")

        return response

    async def _create_access_token(self,
                                 client_id: str,
                                 lambda_id: str,
                                 scope: Set[str],
                                 tier_level: int,
                                 session_id: Optional[str] = None) -> AccessToken:
        """Create access token"""

        # Generate JWT access token
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self.access_token_ttl)

        claims = {
            "iss": self.issuer,
            "sub": lambda_id,
            "aud": client_id,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "scope": " ".join(scope),
            "tier_level": tier_level,
            "token_type": "access_token"
        }

        if session_id:
            claims["session_id"] = session_id

        token_str = await self.jwt_manager.create_token(claims, expires_at)

        access_token = AccessToken(
            token=token_str,
            client_id=client_id,
            lambda_id=lambda_id,
            scope=scope,
            expires_at=expires_at,
            session_id=session_id,
            tier_level=tier_level
        )

        self.access_tokens[token_str] = access_token
        return access_token

    async def _create_refresh_token(self,
                                  client_id: str,
                                  lambda_id: str,
                                  scope: Set[str],
                                  access_token_id: Optional[str] = None) -> RefreshToken:
        """Create refresh token"""

        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(seconds=self.refresh_token_ttl)

        refresh_token = RefreshToken(
            token=token_str,
            client_id=client_id,
            lambda_id=lambda_id,
            scope=scope,
            expires_at=expires_at,
            access_token_id=access_token_id
        )

        self.refresh_tokens[token_str] = refresh_token
        return refresh_token

    async def _create_id_token(self,
                             client_id: str,
                             lambda_id: str,
                             scope: Set[str],
                             nonce: Optional[str] = None) -> IDToken:
        """Create ID token"""

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self.id_token_ttl)

        # Get user info for ID token claims
        userinfo = await self._get_userinfo(lambda_id, scope)

        claims = {
            "iss": self.issuer,
            "sub": lambda_id,
            "aud": client_id,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "auth_time": int(now.timestamp())
        }

        if nonce:
            claims["nonce"] = nonce

        # Add profile claims based on scope
        if "profile" in scope:
            profile_claims = ["name", "given_name", "family_name", "nickname", "picture", "website"]
            for claim in profile_claims:
                if claim in userinfo:
                    claims[claim] = userinfo[claim]

        if "email" in scope:
            email_claims = ["email", "email_verified"]
            for claim in email_claims:
                if claim in userinfo:
                    claims[claim] = userinfo[claim]

        token_str = await self.jwt_manager.create_token(claims, expires_at)

        id_token = IDToken(
            token=token_str,
            client_id=client_id,
            lambda_id=lambda_id,
            issuer=self.issuer,
            audience=client_id,
            expires_at=expires_at,
            nonce=nonce,
            claims=claims
        )

        self.id_tokens[token_str] = id_token
        return id_token

    async def _authenticate_client(self, client_id: Optional[str], client_secret: Optional[str]) -> Optional[OIDCClient]:
        """Authenticate OIDC client"""

        if not client_id:
            return None

        client = self.clients.get(client_id)
        if not client or not client.is_active:
            return None

        # For public clients, no secret required
        if client.token_endpoint_auth_method == "none":
            return client

        # For confidential clients, verify secret
        if client.token_endpoint_auth_method == "client_secret_basic":
            if not client_secret or client_secret != client.client_secret:
                return None

        return client

    async def _validate_access_token(self, token: str) -> Optional[AccessToken]:
        """Validate access token"""

        token_info = self.access_tokens.get(token)
        if not token_info:
            return None

        if datetime.utcnow() > token_info.expires_at:
            # Token expired - remove it
            del self.access_tokens[token]
            return None

        return token_info

    async def _get_userinfo(self, lambda_id: str, scope: Set[str]) -> Dict[str, Any]:
        """Get user information for userinfo endpoint or ID token"""

        # Basic userinfo
        userinfo = {
            "sub": lambda_id
        }

        # Add profile information if profile scope
        if "profile" in scope:
            userinfo.update({
                "name": f"User {lambda_id[:8]}",
                "preferred_username": lambda_id,
                "updated_at": int(datetime.utcnow().timestamp())
            })

        # Add email information if email scope
        if "email" in scope:
            userinfo.update({
                "email": f"{lambda_id}@ai",
                "email_verified": True
            })

        # Add tier information if lukhas scope
        if "lukhas" in scope:
            tier_level = await self.tier_system.get_user_tier_level(lambda_id)
            userinfo["tier_level"] = tier_level

        return userinfo

    def _verify_pkce(self, code_challenge: str, code_challenge_method: Optional[str], code_verifier: str) -> bool:
        """Verify PKCE code challenge"""

        if code_challenge_method == "S256":
            # SHA256 hash of code_verifier
            digest = hashlib.sha256(code_verifier.encode()).digest()
            computed_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
            return computed_challenge == code_challenge
        elif code_challenge_method == "plain" or code_challenge_method is None:
            # Plain text
            return code_verifier == code_challenge
        else:
            return False

    def _generate_discovery_metadata(self) -> Dict[str, Any]:
        """Generate OpenID Connect discovery metadata"""

        return {
            "issuer": self.issuer,
            "authorization_endpoint": f"{self.issuer}/oauth2/authorize",
            "token_endpoint": f"{self.issuer}/oauth2/token",
            "userinfo_endpoint": f"{self.issuer}/oauth2/userinfo",
            "jwks_uri": f"{self.issuer}/.well-known/jwks.json",
            "registration_endpoint": f"{self.issuer}/oauth2/register",
            "introspection_endpoint": f"{self.issuer}/oauth2/introspect",
            "revocation_endpoint": f"{self.issuer}/oauth2/revoke",
            "response_types_supported": [rt.value for rt in ResponseType],
            "grant_types_supported": [gt.value for gt in GrantType],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256", "ES256"],
            "scopes_supported": ["openid", "profile", "email", "offline_access", "lukhas"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
            "claims_supported": [
                "sub", "iss", "aud", "exp", "iat", "auth_time", "nonce",
                "name", "given_name", "family_name", "email", "email_verified",
                "tier_level", "session_id"
            ],
            "code_challenge_methods_supported": ["plain", "S256"],
            "service_documentation": f"{self.issuer}/docs"
        }

    def _error_response(self, error: str, error_description: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "success": False,
            "error": error,
            "error_description": error_description
        }

    def _authentication_required_response(self,
                                        client_id: str,
                                        response_type: str,
                                        redirect_uri: str,
                                        scope: str,
                                        state: Optional[str]) -> Dict[str, Any]:
        """Create authentication required response"""

        auth_params = {
            "client_id": client_id,
            "response_type": response_type,
            "redirect_uri": redirect_uri,
            "scope": scope
        }
        if state:
            auth_params["state"] = state

        return {
            "success": False,
            "error": "authentication_required",
            "error_description": "User authentication required",
            "login_url": f"{self.issuer}/auth/login?{urlencode(auth_params)}"
        }

    async def _cleanup_loop(self):
        """Background cleanup of expired tokens and codes"""

        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                now = datetime.utcnow()

                # Clean up expired authorization codes
                expired_codes = [
                    code for code, auth_code in self.authorization_codes.items()
                    if auth_code.expires_at < now
                ]
                for code in expired_codes:
                    del self.authorization_codes[code]

                # Clean up expired access tokens
                expired_access_tokens = [
                    token for token, token_info in self.access_tokens.items()
                    if token_info.expires_at < now
                ]
                for token in expired_access_tokens:
                    del self.access_tokens[token]

                # Clean up expired refresh tokens
                expired_refresh_tokens = [
                    token for token, token_info in self.refresh_tokens.items()
                    if token_info.expires_at < now
                ]
                for token in expired_refresh_tokens:
                    del self.refresh_tokens[token]

                # Clean up expired ID tokens
                expired_id_tokens = [
                    token for token, token_info in self.id_tokens.items()
                    if token_info.expires_at < now
                ]
                for token in expired_id_tokens:
                    del self.id_tokens[token]

                if any([expired_codes, expired_access_tokens, expired_refresh_tokens, expired_id_tokens]):
                    total_cleaned = (len(expired_codes) + len(expired_access_tokens) +
                                   len(expired_refresh_tokens) + len(expired_id_tokens))
                    logger.info(f"🧹 Cleaned up {total_cleaned} expired tokens/codes")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Token cleanup error: {e}")
                await asyncio.sleep(60)

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get OIDC provider statistics"""

        now = datetime.utcnow()

        return {
            "clients": {
                "total": len(self.clients),
                "active": sum(1 for c in self.clients.values() if c.is_active)
            },
            "tokens": {
                "authorization_codes": {
                    "total": len(self.authorization_codes),
                    "active": sum(1 for ac in self.authorization_codes.values()
                                if not ac.used and ac.expires_at > now)
                },
                "access_tokens": {
                    "total": len(self.access_tokens),
                    "active": sum(1 for at in self.access_tokens.values() if at.expires_at > now)
                },
                "refresh_tokens": {
                    "total": len(self.refresh_tokens),
                    "active": sum(1 for rt in self.refresh_tokens.values() if rt.expires_at > now)
                },
                "id_tokens": {
                    "total": len(self.id_tokens),
                    "active": sum(1 for it in self.id_tokens.values() if it.expires_at > now)
                }
            },
            "configuration": {
                "issuer": self.issuer,
                "authorization_code_ttl": self.authorization_code_ttl,
                "access_token_ttl": self.access_token_ttl,
                "refresh_token_ttl": self.refresh_token_ttl,
                "id_token_ttl": self.id_token_ttl
            }
        }
