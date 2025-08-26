"""
LUKHΛS ID (ΛID) Resolver + OIDC Provider
=========================================
System-wide guardrails applied:
1. Canonical identity is ΛID = {namespace?}:{username}; no raw PII as usernames
2. Primary auth = Passkeys/WebAuthn. OAuth aliases are optional convenience
3. Data minimization: metadata-only reads by default
4. Capability tokens: short-lived, least-privilege JWT with caveats
5. Edge first for gesture recognition; store only hashed kinematic features
6. Everything has: logs, audit trail, and revocation paths

ACK GUARDRAILS
"""

import re
import secrets
import time
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator


# ABNF Grammar Implementation for ΛID
class LukhasIDParser:
    """
    ABNF-compliant parser for LukhasID (ΛID) format:
    LUKHASID = [NAMESPACE ":"] USERNAME [SP PROVIDER] [SP LOCALE] [SP EMOJI]
    """

    # Validation regex for canonical core (namespace:username)
    CANONICAL_REGEX = re.compile(r'^(?:(?P<namespace>[a-z0-9_-]{1,48}):)?(?P<username>[a-z0-9_-]{3,32})$')

    # Extended patterns for full ΛID with optional components
    PROVIDER_PATTERN = re.compile(r'@(google|apple|github|microsoft|lukhas|[a-z]+)')
    LOCALE_PATTERN = re.compile(r'~([a-z0-9-]+)')
    EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001FAD6\U00002600-\U000026FF]')

    @classmethod
    def parse_canonical(cls, input_str: str) -> tuple[Optional[str], str]:
        """
        Parse canonical ΛID core: {namespace?}:{username}

        Returns:
            (namespace, username) tuple

        Raises:
            ValueError if format is invalid
        """
        start_time = time.perf_counter()

        # Normalize input
        canonical = input_str.strip().lower()

        # Remove UI affordances if present
        if canonical.startswith('#λid ') or canonical.startswith('#lid '):
            canonical = canonical.split(' ', 1)[1]

        # Extract canonical part (before any @ ~ emoji)
        canonical = canonical.split('@')[0].split('~')[0]
        canonical = re.sub(r'[\U0001F300-\U0001FAD6\U00002600-\U000026FF]', '', canonical).strip()

        # Validate against ABNF
        match = cls.CANONICAL_REGEX.match(canonical)
        if not match:
            raise ValueError(f"Invalid ΛID format: {input_str}")

        namespace = match.group('namespace')
        username = match.group('username')

        # Performance tracking (must be < 2ms per requirements)
        parse_time = (time.perf_counter() - start_time) * 1000
        if parse_time > 2.0:  # Log slow parses
            print(f"SLOW_PARSE: {parse_time:.2f}ms for {input_str}")

        return namespace, username

    @classmethod
    def parse_full(cls, input_str: str) -> dict[str, Optional[str]]:
        """
        Parse full ΛID with optional provider/locale/emoji:
        #ΛID {namespace?}:{username} [@{provider?}] [~{locale?}] [{emoji?}]
        """
        # Parse canonical part first
        namespace, username = cls.parse_canonical(input_str)

        # Extract optional components
        provider = None
        locale = None
        emoji = None

        provider_match = cls.PROVIDER_PATTERN.search(input_str)
        if provider_match:
            provider = provider_match.group(1)

        locale_match = cls.LOCALE_PATTERN.search(input_str)
        if locale_match:
            locale = locale_match.group(1)

        emoji_match = cls.EMOJI_PATTERN.search(input_str)
        if emoji_match:
            emoji = emoji_match.group(0)

        return {
            'namespace': namespace,
            'username': username,
            'provider': provider,
            'locale': locale,
            'emoji': emoji,
            'canonical_lid': f"{namespace}:{username}" if namespace else username
        }


class LukhasIDResolver:
    """
    ΛID Resolver that maps canonical identities to provider authentication flows.
    Acts as OIDC Provider for "Sign in with LUKHΛS" functionality.
    """

    def __init__(self):
        # OAuth provider configurations
        self.oauth_providers = {
            'google': {
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'scopes': ['openid', 'email', 'profile'],
                'client_id': 'your-google-client-id.apps.googleusercontent.com'
            },
            'apple': {
                'auth_url': 'https://appleid.apple.com/auth/authorize',
                'scopes': ['name', 'email'],
                'client_id': 'your.bundle.id'
            },
            'github': {
                'auth_url': 'https://github.com/login/oauth/authorize',
                'scopes': ['user:email'],
                'client_id': 'your-github-client-id'
            },
            'microsoft': {
                'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'scopes': ['openid', 'profile', 'email'],
                'client_id': 'your-microsoft-client-id'
            },
            'lukhas': {
                'auth_url': '/identity/webauthn/challenge',  # First-party WebAuthn
                'scopes': ['identity'],
                'client_id': 'lukhas-webauthn'
            }
        }

        # OIDC configuration for "Sign in with LUKHΛS"
        self.oidc_config = {
            'issuer': 'https://identity.lukhas.com',
            'authorization_endpoint': 'https://identity.lukhas.com/auth',
            'token_endpoint': 'https://identity.lukhas.com/token',
            'userinfo_endpoint': 'https://identity.lukhas.com/userinfo',
            'jwks_uri': 'https://identity.lukhas.com/.well-known/jwks.json',
            'response_types_supported': ['code'],
            'subject_types_supported': ['public'],
            'id_token_signing_alg_values_supported': ['RS256']
        }

        # Reserved namespaces (from seeding script)
        self.reserved_namespaces = {
            'openai': {'verified': True, 'tier': 'T5'},
            'stanford': {'verified': True, 'tier': 'T3'},
            'mit': {'verified': True, 'tier': 'T3'},
            'google': {'verified': True, 'tier': 'T2'},
            'apple': {'verified': True, 'tier': 'T2'},
            'github': {'verified': True, 'tier': 'T2'}
        }

    def resolve_login(self, input_str: str, provider: Optional[str] = None) -> dict[str, str]:
        """
        Core resolution endpoint: POST /identity/resolve-login

        Args:
            input_str: User input like "stanford:alice_smith" or "gonzo"
            provider: Optional provider override (google|apple|github|lukhas)

        Returns:
            {
                "canonical_lid": "stanford:alice_smith",
                "provider": "google",
                "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
                "state": "csrf_nonce"
            }
        """
        start_time = time.perf_counter()

        try:
            # Parse canonical ΛID
            parsed = LukhasIDParser.parse_full(input_str)
            canonical_lid = parsed['canonical_lid']

            # Determine provider
            resolved_provider = provider or parsed.get('provider') or 'lukhas'

            if resolved_provider not in self.oauth_providers:
                raise ValueError(f"Unsupported provider: {resolved_provider}")

            # Generate CSRF state
            state = secrets.token_urlsafe(32)

            # Build auth URL
            if resolved_provider == 'lukhas':
                # First-party WebAuthn flow
                auth_url = f"/identity/webauthn/challenge?lid={canonical_lid}&state={state}"
            else:
                # OAuth provider flow
                provider_config = self.oauth_providers[resolved_provider]
                auth_params = {
                    'client_id': provider_config['client_id'],
                    'response_type': 'code',
                    'scope': ' '.join(provider_config['scopes']),
                    'state': state,
                    'redirect_uri': f'https://identity.lukhas.com/oauth/callback/{resolved_provider}'
                }

                # Add provider-specific parameters
                if resolved_provider == 'apple':
                    auth_params['response_mode'] = 'form_post'
                elif resolved_provider == 'microsoft':
                    auth_params['prompt'] = 'select_account'

                auth_url = f"{provider_config['auth_url']}?{urlencode(auth_params)}"

            # Log resolution (audit trail requirement)
            resolution_time = (time.perf_counter() - start_time) * 1000
            self._log_resolution(canonical_lid, resolved_provider, resolution_time)

            return {
                'canonical_lid': canonical_lid,
                'provider': resolved_provider,
                'auth_url': auth_url,
                'state': state,
                'namespace': parsed['namespace'],
                'username': parsed['username']
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Resolution failed: {str(e)}")

    def _log_resolution(self, lid: str, provider: str, resolution_time_ms: float):
        """Log resolution for audit trail (requirement #6)."""
        # In production: write to audit log table
        print(f"RESOLUTION: {lid} -> {provider} ({resolution_time_ms:.2f}ms)")

    def get_oidc_configuration(self) -> dict:
        """GET /.well-known/openid-configuration"""
        return self.oidc_config

    def get_jwks(self) -> dict:
        """GET /.well-known/jwks.json - JSON Web Key Set for token verification"""
        # In production: use actual RSA keys from KMS/enclave
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "lukhas-2024-1",
                    "alg": "RS256",
                    "n": "example_modulus_base64",
                    "e": "AQAB"
                }
            ]
        }


# Request/Response Models
class ResolveLoginRequest(BaseModel):
    """Request model for /identity/resolve-login"""
    input: str = Field(..., description="ΛID input like 'stanford:alice_smith' or 'gonzo'")
    provider: Optional[str] = Field(None, description="Optional provider override (google|apple|github|lukhas)")

    @validator('input')
    def validate_input(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Input must be at least 3 characters")
        return v.strip().lower()

    @validator('provider')
    def validate_provider(cls, v):
        if v and v not in ['google', 'apple', 'github', 'microsoft', 'lukhas']:
            raise ValueError("Invalid provider")
        return v


class ResolveLoginResponse(BaseModel):
    """Response model for /identity/resolve-login"""
    canonical_lid: str
    provider: str
    auth_url: str
    state: str
    namespace: Optional[str] = None
    username: str


# FastAPI Router
router = APIRouter(prefix="/identity", tags=["ΛID Resolver"])
resolver = LukhasIDResolver()


@router.post("/resolve-login", response_model=ResolveLoginResponse)
async def resolve_login_endpoint(request: ResolveLoginRequest):
    """
    Resolve ΛID to canonical form and provider auth URL.

    Core endpoint that:
    1. Parses ΛID input using ABNF grammar
    2. Resolves canonical namespace:username
    3. Maps to appropriate OAuth provider or first-party WebAuthn
    4. Returns auth URL with CSRF protection

    Examples:
    - `stanford:alice_smith` + `google` → Google OAuth for stanford:alice_smith
    - `gonzo` + `lukhas` → WebAuthn challenge for gonzo
    - `openai:reviewer` + `apple` → Apple Sign-In for openai:reviewer
    """
    result = resolver.resolve_login(request.input, request.provider)
    return ResolveLoginResponse(**result)


@router.get("/.well-known/openid-configuration")
async def oidc_configuration():
    """
    OIDC Discovery endpoint for "Sign in with LUKHΛS" functionality.

    Allows other services to integrate LUKHΛS as an OIDC provider.
    """
    return resolver.get_oidc_configuration()


@router.get("/.well-known/jwks.json")
async def jwks_endpoint():
    """
    JSON Web Key Set for token verification.

    Public keys used to verify JWT tokens issued by LUKHΛS Identity Provider.
    """
    return resolver.get_jwks()


# Validation and testing utilities
def validate_lukhas_id(input_str: str) -> bool:
    """Utility function to validate ΛID format."""
    try:
        LukhasIDParser.parse_canonical(input_str)
        return True
    except ValueError:
        return False


def benchmark_parser():
    """Benchmark parser performance (must be < 2ms per requirements)."""
    test_cases = [
        "gonzo",
        "stanford:alice_smith",
        "openai:reviewer",
        "acme:engineering-johndoe",
        "a" * 32,  # Max username length
        "x" * 48 + ":" + "y" * 32  # Max namespace + username
    ]

    times = []
    for test_input in test_cases:
        start = time.perf_counter()
        try:
            LukhasIDParser.parse_canonical(test_input)
            end = time.perf_counter()
            parse_time = (end - start) * 1000  # Convert to ms
            times.append(parse_time)
            print(f"PARSE: {test_input} -> {parse_time:.3f}ms")
        except ValueError as e:
            print(f"INVALID: {test_input} -> {e}")

    if times:
        p95 = sorted(times)[int(len(times) * 0.95)]
        print(f"P95 parse time: {p95:.3f}ms (requirement: < 2ms)")
        return p95 < 2.0

    return False


if __name__ == "__main__":
    # Run benchmark
    print("🧪 Running ΛID Parser Benchmark...")
    benchmark_parser()

    # Test resolution
    print("\n🔍 Testing Resolution...")
    resolver = LukhasIDResolver()

    test_cases = [
        ("gonzo", None),
        ("stanford:alice_smith", "google"),
        ("openai:reviewer", "apple"),
        ("mit:prof_johnson", "lukhas")
    ]

    for input_str, provider in test_cases:
        try:
            result = resolver.resolve_login(input_str, provider)
            print(f"✅ {input_str} + {provider} -> {result['canonical_lid']} via {result['provider']}")
        except Exception as e:
            print(f"❌ {input_str} + {provider} -> {e}")
