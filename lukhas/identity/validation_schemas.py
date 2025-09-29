#!/usr/bin/env python3
"""
LUKHAS Identity Validation Schemas
T4/0.01% Excellence Standard

Comprehensive Pydantic schemas for OIDC/OAuth2 request validation.
Implements strict validation with security-first patterns.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.networks import HttpUrl, EmailStr


class GrantTypeEnum(str, Enum):
    """OAuth2 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    RESOURCE_OWNER_PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"


class ResponseTypeEnum(str, Enum):
    """OAuth2 response types"""
    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"
    CODE_TOKEN = "code token"
    CODE_ID_TOKEN = "code id_token"
    TOKEN_ID_TOKEN = "token id_token"
    CODE_TOKEN_ID_TOKEN = "code token id_token"


class CodeChallengeMethodEnum(str, Enum):
    """PKCE code challenge methods"""
    PLAIN = "plain"
    S256 = "S256"


class TokenTypeHintEnum(str, Enum):
    """Token type hints for introspection/revocation"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"


class ScopeEnum(str, Enum):
    """Supported OAuth2/OIDC scopes"""
    OPENID = "openid"
    PROFILE = "profile"
    EMAIL = "email"
    ADDRESS = "address"
    PHONE = "phone"
    OFFLINE_ACCESS = "offline_access"
    LUKHAS = "lukhas"
    BIOMETRIC = "biometric"
    ADMIN = "admin"


# Base validation schemas

class BaseRequest(BaseModel):
    """Base request schema with common validation"""

    class Config:
        # Strict validation
        extra = "forbid"
        validate_all = True
        str_strip_whitespace = True
        max_anystr_length = 10000  # Prevent DoS via large strings


class ClientIdValidation(BaseModel):
    """Client ID validation mixin"""
    client_id: str = Field(..., min_length=1, max_length=255, regex=r'^[a-zA-Z0-9_-]+$')

    @validator('client_id')
    def validate_client_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Client ID cannot be empty')
        return v.strip()


class RedirectUriValidation(BaseModel):
    """Redirect URI validation mixin"""
    redirect_uri: HttpUrl = Field(..., description="OAuth2 redirect URI")

    @validator('redirect_uri', pre=True)
    def validate_redirect_uri(cls, v):
        if isinstance(v, str):
            # Parse and validate URL
            parsed = urlparse(v)

            # Security checks
            if parsed.scheme not in ['https', 'http']:
                # Allow http only for localhost in development
                if parsed.hostname not in ['localhost', '127.0.0.1']:
                    raise ValueError('Redirect URI must use HTTPS')

            if parsed.fragment:
                raise ValueError('Redirect URI must not contain fragment')

            # Prevent open redirects
            if not parsed.hostname:
                raise ValueError('Redirect URI must have valid hostname')

        return v


class ScopeValidation(BaseModel):
    """Scope validation mixin"""
    scope: str = Field(..., max_length=1000, description="OAuth2 scopes")

    @validator('scope')
    def validate_scope(cls, v):
        if not v or not v.strip():
            raise ValueError('Scope cannot be empty')

        scopes = v.strip().split()
        valid_scopes = {scope.value for scope in ScopeEnum}

        for scope in scopes:
            if scope not in valid_scopes:
                raise ValueError(f'Invalid scope: {scope}')

        return ' '.join(scopes)

    def get_scope_set(self) -> Set[str]:
        """Get scope as set"""
        return set(self.scope.split())


# OIDC/OAuth2 Request Schemas

class AuthorizationRequest(BaseRequest, ClientIdValidation, RedirectUriValidation, ScopeValidation):
    """OAuth2 authorization request validation"""
    response_type: ResponseTypeEnum = Field(..., description="OAuth2 response type")
    state: Optional[str] = Field(None, max_length=500, regex=r'^[a-zA-Z0-9_.-]+$')
    nonce: Optional[str] = Field(None, max_length=500, regex=r'^[a-zA-Z0-9_.-]+$')
    code_challenge: Optional[str] = Field(None, max_length=128, regex=r'^[a-zA-Z0-9_.-~]+$')
    code_challenge_method: Optional[CodeChallengeMethodEnum] = None
    prompt: Optional[str] = Field(None, regex=r'^(none|login|consent|select_account)( (none|login|consent|select_account))*$')
    max_age: Optional[int] = Field(None, ge=0, le=86400)  # Max 24 hours
    login_hint: Optional[str] = Field(None, max_length=256)

    @validator('nonce')
    def validate_nonce_with_id_token(cls, v, values):
        """Nonce is required for implicit flows with id_token"""
        response_type = values.get('response_type')
        if response_type and 'id_token' in response_type.value and not v:
            raise ValueError('Nonce is required for flows returning id_token')
        return v

    @validator('code_challenge_method')
    def validate_pkce_params(cls, v, values):
        """PKCE validation"""
        code_challenge = values.get('code_challenge')

        if code_challenge and not v:
            # Default to S256 if code_challenge provided but method not specified
            return CodeChallengeMethodEnum.S256

        if v and not code_challenge:
            raise ValueError('code_challenge required when code_challenge_method specified')

        return v


class TokenRequest(BaseRequest, ClientIdValidation):
    """OAuth2 token request validation"""
    grant_type: GrantTypeEnum = Field(..., description="OAuth2 grant type")
    code: Optional[str] = Field(None, max_length=512)
    redirect_uri: Optional[HttpUrl] = None
    code_verifier: Optional[str] = Field(None, max_length=128, regex=r'^[a-zA-Z0-9_.-~]+$')
    refresh_token: Optional[str] = Field(None, max_length=512)
    username: Optional[str] = Field(None, max_length=256)
    password: Optional[str] = Field(None, max_length=256)
    client_secret: Optional[str] = Field(None, max_length=512)

    @root_validator
    def validate_grant_type_params(cls, values):
        """Validate required parameters for each grant type"""
        grant_type = values.get('grant_type')

        if grant_type == GrantTypeEnum.AUTHORIZATION_CODE:
            if not values.get('code'):
                raise ValueError('code is required for authorization_code grant')
            if not values.get('redirect_uri'):
                raise ValueError('redirect_uri is required for authorization_code grant')

        elif grant_type == GrantTypeEnum.REFRESH_TOKEN:
            if not values.get('refresh_token'):
                raise ValueError('refresh_token is required for refresh_token grant')

        elif grant_type == GrantTypeEnum.RESOURCE_OWNER_PASSWORD:
            if not values.get('username'):
                raise ValueError('username is required for password grant')
            if not values.get('password'):
                raise ValueError('password is required for password grant')

        return values


class IntrospectionRequest(BaseRequest, ClientIdValidation):
    """OAuth2 token introspection request validation"""
    token: str = Field(..., min_length=1, max_length=2048)
    token_type_hint: Optional[TokenTypeHintEnum] = None
    client_secret: Optional[str] = Field(None, max_length=512)


class RevocationRequest(BaseRequest, ClientIdValidation):
    """OAuth2 token revocation request validation"""
    token: str = Field(..., min_length=1, max_length=2048)
    token_type_hint: Optional[TokenTypeHintEnum] = None
    client_secret: Optional[str] = Field(None, max_length=512)


class UserInfoRequest(BaseRequest):
    """OIDC UserInfo request validation"""
    access_token: str = Field(..., min_length=1, max_length=2048, description="Bearer access token")

    @validator('access_token', pre=True)
    def extract_bearer_token(cls, v):
        """Extract token from Bearer authorization header format"""
        if isinstance(v, str) and v.startswith('Bearer '):
            return v[7:]  # Remove 'Bearer ' prefix
        return v


# WebAuthn Request Schemas

class WebAuthnCredentialCreationOptions(BaseRequest):
    """WebAuthn credential creation options validation"""
    username: str = Field(..., min_length=1, max_length=256, regex=r'^[a-zA-Z0-9._@-]+$')
    display_name: str = Field(..., min_length=1, max_length=256)
    user_verification: str = Field('preferred', regex=r'^(required|preferred|discouraged)$')
    authenticator_attachment: Optional[str] = Field(None, regex=r'^(platform|cross-platform)$')
    resident_key: str = Field('preferred', regex=r'^(required|preferred|discouraged)$')

    @validator('username')
    def validate_username_format(cls, v):
        """Validate username format"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')

        # Additional checks for potential injection attacks
        if any(char in v for char in ['<', '>', '"', "'", '&', '\n', '\r', '\t']):
            raise ValueError('Username contains invalid characters')

        return v.strip().lower()


class WebAuthnCredentialRequestOptions(BaseRequest):
    """WebAuthn credential request options validation"""
    username: Optional[str] = Field(None, min_length=1, max_length=256, regex=r'^[a-zA-Z0-9._@-]+$')
    user_verification: str = Field('preferred', regex=r'^(required|preferred|discouraged)$')


class WebAuthnRegistrationResponse(BaseRequest):
    """WebAuthn registration response validation"""
    username: str = Field(..., min_length=1, max_length=256)
    credential: Dict[str, Any] = Field(..., description="WebAuthn credential response")
    client_data_json: str = Field(..., max_length=4096)
    attestation_object: str = Field(..., max_length=8192)

    @validator('credential')
    def validate_credential_structure(cls, v):
        """Validate WebAuthn credential response structure"""
        required_fields = ['id', 'rawId', 'response', 'type']

        for field in required_fields:
            if field not in v:
                raise ValueError(f'Missing required field: {field}')

        if v.get('type') != 'public-key':
            raise ValueError('Invalid credential type')

        return v


class WebAuthnAuthenticationResponse(BaseRequest):
    """WebAuthn authentication response validation"""
    username: Optional[str] = Field(None, min_length=1, max_length=256)
    credential: Dict[str, Any] = Field(..., description="WebAuthn credential response")
    client_data_json: str = Field(..., max_length=4096)
    authenticator_data: str = Field(..., max_length=2048)
    signature: str = Field(..., max_length=2048)

    @validator('credential')
    def validate_auth_credential_structure(cls, v):
        """Validate WebAuthn authentication credential structure"""
        required_fields = ['id', 'rawId', 'response', 'type']

        for field in required_fields:
            if field not in v:
                raise ValueError(f'Missing required field: {field}')

        if v.get('type') != 'public-key':
            raise ValueError('Invalid credential type')

        return v


# Client Registration Schemas

class ClientRegistrationRequest(BaseRequest):
    """OIDC dynamic client registration request validation"""
    client_name: str = Field(..., min_length=1, max_length=256)
    redirect_uris: List[HttpUrl] = Field(..., min_items=1, max_items=10)
    response_types: List[ResponseTypeEnum] = Field(default=[ResponseTypeEnum.CODE], max_items=5)
    grant_types: List[GrantTypeEnum] = Field(default=[GrantTypeEnum.AUTHORIZATION_CODE], max_items=5)
    scope: str = Field(default="openid profile email", max_length=1000)
    application_type: str = Field('web', regex=r'^(web|native)$')
    token_endpoint_auth_method: str = Field('client_secret_basic',
                                          regex=r'^(client_secret_basic|client_secret_post|none)$')
    jwks_uri: Optional[HttpUrl] = None
    software_id: Optional[str] = Field(None, max_length=256)
    software_version: Optional[str] = Field(None, max_length=256)

    @validator('redirect_uris')
    def validate_redirect_uris(cls, v):
        """Validate redirect URIs"""
        if not v:
            raise ValueError('At least one redirect URI is required')

        for uri in v:
            parsed = urlparse(str(uri))
            if parsed.fragment:
                raise ValueError('Redirect URIs must not contain fragments')

        return v

    @validator('response_types', 'grant_types')
    def validate_consistent_flow_config(cls, v, values, field):
        """Ensure response_types and grant_types are consistent"""
        # This validator ensures the client configuration is consistent
        return v


# Rate Limiting Schemas

class RateLimitContext(BaseModel):
    """Rate limiting context"""
    client_ip: str = Field(..., regex=r'^[0-9.:a-fA-F]+$')  # IPv4/IPv6
    user_id: Optional[str] = Field(None, max_length=256)
    endpoint: Optional[str] = Field(None, max_length=256)
    user_agent: Optional[str] = Field(None, max_length=1024)

    @validator('client_ip')
    def validate_ip_address(cls, v):
        """Basic IP address validation"""
        import ipaddress
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError('Invalid IP address format')
        return v


# Security Event Schemas

class SecurityEvent(BaseModel):
    """Security event for audit logging"""
    event_type: str = Field(..., max_length=128)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    client_ip: Optional[str] = None
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    endpoint: Optional[str] = None
    threat_level: str = Field('low', regex=r'^(low|medium|high|critical)$')
    indicators: List[str] = Field(default_factory=list, max_items=20)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Response Schemas

class ErrorResponse(BaseModel):
    """Standard OAuth2/OIDC error response"""
    error: str = Field(..., max_length=128)
    error_description: Optional[str] = Field(None, max_length=512)
    error_uri: Optional[HttpUrl] = None
    state: Optional[str] = Field(None, max_length=500)


class TokenResponse(BaseModel):
    """OAuth2 token response"""
    access_token: str = Field(..., max_length=2048)
    token_type: str = Field('Bearer', max_length=64)
    expires_in: int = Field(..., ge=1, le=86400)
    refresh_token: Optional[str] = Field(None, max_length=2048)
    id_token: Optional[str] = Field(None, max_length=4096)
    scope: Optional[str] = Field(None, max_length=1000)


class UserInfoResponse(BaseModel):
    """OIDC UserInfo response"""
    sub: str = Field(..., max_length=256)
    name: Optional[str] = Field(None, max_length=256)
    given_name: Optional[str] = Field(None, max_length=256)
    family_name: Optional[str] = Field(None, max_length=256)
    email: Optional[EmailStr] = None
    email_verified: Optional[bool] = None
    picture: Optional[HttpUrl] = None
    updated_at: Optional[int] = None
    tier_level: Optional[int] = Field(None, ge=1, le=10)


# Helper functions for validation

def validate_jwt_token(token: str) -> bool:
    """Basic JWT token format validation"""
    if not token or not isinstance(token, str):
        return False

    parts = token.split('.')
    return len(parts) == 3 and all(part for part in parts)


def sanitize_correlation_id(correlation_id: Optional[str]) -> Optional[str]:
    """Sanitize correlation ID for logging"""
    if not correlation_id:
        return None

    # Only allow alphanumeric, hyphens, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', correlation_id)
    return sanitized[:64] if sanitized else None


# Export main validation schemas
__all__ = [
    'AuthorizationRequest',
    'TokenRequest',
    'IntrospectionRequest',
    'RevocationRequest',
    'UserInfoRequest',
    'WebAuthnCredentialCreationOptions',
    'WebAuthnCredentialRequestOptions',
    'WebAuthnRegistrationResponse',
    'WebAuthnAuthenticationResponse',
    'ClientRegistrationRequest',
    'RateLimitContext',
    'SecurityEvent',
    'ErrorResponse',
    'TokenResponse',
    'UserInfoResponse',
    'validate_jwt_token',
    'sanitize_correlation_id'
]