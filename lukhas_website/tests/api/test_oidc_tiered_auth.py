"""Tests for OIDC tiered authentication system helper."""

from __future__ import annotations

import pathlib
import sys
import types
from enum import Enum

import pytest
from fastapi import HTTPException, status
from pydantic import BaseModel

from lukhas.api import oidc

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Provide a lightweight opentelemetry stub for environments without the dependency
if "opentelemetry" not in sys.modules:
    otel_module = types.ModuleType("opentelemetry")

    class _DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def set_attribute(self, *args, **kwargs):
            return None

    class _DummyTracer:
        def start_span(self, *args, **kwargs):
            return _DummySpan()

    trace_module = types.ModuleType("opentelemetry.trace")
    trace_module.get_tracer = lambda *args, **kwargs: _DummyTracer()

    otel_module.trace = trace_module
    sys.modules["opentelemetry.trace"] = trace_module
    sys.modules["opentelemetry"] = otel_module

if "_bridgeutils" not in sys.modules:
    bridgeutils_module = types.ModuleType("_bridgeutils")

    def bridge_from_candidates(*candidates):
        return (), {}

    bridgeutils_module.bridge_from_candidates = bridge_from_candidates
    sys.modules["_bridgeutils"] = bridgeutils_module

if "observability" not in sys.modules:
    observability_module = types.ModuleType("observability")
    matriz_decorators_module = types.ModuleType("observability.matriz_decorators")

    def _instrument(func=None, **kwargs):
        if callable(func):
            return func

        def decorator(wrapped):
            return wrapped

        return decorator

    matriz_decorators_module.instrument = _instrument
    observability_module.matriz_decorators = matriz_decorators_module
    sys.modules["observability"] = observability_module
    sys.modules["observability.matriz_decorators"] = matriz_decorators_module

def _ensure_identity_module(module_name: str, **attrs) -> None:
    full_name = f"lukhas.identity.{module_name}"
    if full_name in sys.modules:
        return

    module = types.ModuleType(full_name)
    for attr_name, attr_value in attrs.items():
        setattr(module, attr_name, attr_value)
    sys.modules[full_name] = module


class _StubEnvironmentSecretProvider:  # pragma: no cover - simple stub
    pass


class _StubTokenGenerator:  # pragma: no cover - simple stub
    def __init__(self, provider):
        self.provider = provider


class _StubTokenValidator:  # pragma: no cover - simple stub
    def __init__(self, provider):
        self.provider = provider

    def verify(self, token, context):
        return True


class _StubValidationContext:  # pragma: no cover - simple stub
    pass


class _StubValidationResult:  # pragma: no cover - simple stub
    pass


class _StubTokenStorage:  # pragma: no cover - simple stub
    pass


class _StubWebAuthnService:  # pragma: no cover - simple stub
    pass


def _identity_alias(value: str, *args, **kwargs):  # pragma: no cover - simple stub
    return value


_ensure_identity_module(
    "alias_format",
    make_alias=_identity_alias,
    parse_alias=_identity_alias,
    verify_crc=lambda value: True,
)
_ensure_identity_module(
    "token_generator",
    EnvironmentSecretProvider=_StubEnvironmentSecretProvider,
    TokenGenerator=_StubTokenGenerator,
)
_ensure_identity_module(
    "token_validator",
    TokenValidator=_StubTokenValidator,
    ValidationContext=_StubValidationContext,
    ValidationResult=_StubValidationResult,
)
_ensure_identity_module("token_storage", TokenStorage=_StubTokenStorage)
_ensure_identity_module("webauthn", WebAuthnService=_StubWebAuthnService)
class _StubAuthorizationRequest(BaseModel):  # pragma: no cover - simple stub
    client_id: str | None = None
    redirect_uri: str | None = None


class _StubErrorResponse(BaseModel):  # pragma: no cover - simple stub
    error: str | None = None
    error_description: str | None = None


_ensure_identity_module(
    "validation_schemas",
    AuthorizationRequest=_StubAuthorizationRequest,
    ErrorResponse=_StubErrorResponse,
    sanitize_correlation_id=lambda value: value,
)
_StubSecurityAction = Enum("SecurityAction", "ALLOW BLOCK THROTTLE")


_ensure_identity_module(
    "security_hardening",
    SecurityAction=_StubSecurityAction,
    create_security_hardening_manager=lambda *args, **kwargs: types.SimpleNamespace(
        comprehensive_security_check=lambda **_kw: (
            _StubSecurityAction.ALLOW,
            {"threats_detected": False},
        )
    ),
)

if "structlog" not in sys.modules:
    structlog_module = types.ModuleType("structlog")

    class _StubLogger:  # pragma: no cover - simple stub
        def bind(self, **kwargs):
            return self

        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def error(self, *args, **kwargs):
            return None

        def debug(self, *args, **kwargs):
            return None

    structlog_module.get_logger = lambda *args, **kwargs: _StubLogger()
    sys.modules["structlog"] = structlog_module

if "identity" not in sys.modules:
    identity_module = types.ModuleType("identity")

    class _StubJWTManager:  # pragma: no cover - simple stub
        async def get_public_keys(self):
            return {}

        async def create_token(self, claims, expires_at):
            return "stub-token"

    class _StubIdentityObservability:  # pragma: no cover - simple stub
        async def record_client_registered(self, *args, **kwargs):
            return None

        async def record_userinfo_request(self, *args, **kwargs):
            return None

        async def record_token_revoked(self, *args, **kwargs):
            return None

        async def record_authorization_granted(self, *args, **kwargs):
            return None

        async def record_token_issued(self, *args, **kwargs):
            return None

    class _StubSessionManager:  # pragma: no cover - simple stub
        async def validate_session(self, session_id):
            return {"session_id": session_id, "lambda_id": "test"}

    class _StubTierSystem:  # pragma: no cover - simple stub
        async def get_user_tier_level(self, lambda_id):
            return 2

    jwt_utils_module = types.ModuleType("identity.jwt_utils")
    jwt_utils_module.JWTManager = _StubJWTManager

    observability_module = types.ModuleType("identity.observability")
    observability_module.IdentityObservability = _StubIdentityObservability

    session_manager_module = types.ModuleType("identity.session_manager")
    session_manager_module.SessionManager = _StubSessionManager

    tiers_module = types.ModuleType("identity.tiers")
    tiers_module.TierSystem = _StubTierSystem

    identity_module.jwt_utils = jwt_utils_module
    identity_module.observability = observability_module
    identity_module.session_manager = session_manager_module
    identity_module.tiers = tiers_module

    sys.modules["identity"] = identity_module
    sys.modules["identity.jwt_utils"] = jwt_utils_module
    sys.modules["identity.observability"] = observability_module
    sys.modules["identity.session_manager"] = session_manager_module
    sys.modules["identity.tiers"] = tiers_module

if "multipart" not in sys.modules:
    multipart_module = types.ModuleType("multipart")
    multipart_submodule = types.ModuleType("multipart.multipart")
    multipart_module.__version__ = "0.0.1"
    multipart_submodule.parse_options_header = lambda value: (value, {})
    sys.modules["multipart"] = multipart_module
    sys.modules["multipart.multipart"] = multipart_submodule


pytestmark = pytest.mark.asyncio


async def test_get_tiered_auth_system_returns_cached_instance(monkeypatch):
    """Tiered auth system should initialize once and cache the instance."""
    class _DummyGuardian:
        pass

    class _DummySecurityPolicy:
        pass

    class _DummyAuthenticator:
        pass

    instances = []

    def _create_authenticator(security_policy=None, guardian_system=None):
        instance = _DummyAuthenticator()
        instance.security_policy = security_policy
        instance.guardian_system = guardian_system
        instances.append(instance)
        return instance

    monkeypatch.setattr(oidc, "TIERED_AUTH_SYSTEM_AVAILABLE", True)
    monkeypatch.setattr(oidc, "_tiered_auth_system", None)
    monkeypatch.setattr(oidc, "_guardian_system", None)
    monkeypatch.setattr(oidc, "GuardianSystem", _DummyGuardian)
    monkeypatch.setattr(oidc, "SecurityPolicy", _DummySecurityPolicy)
    monkeypatch.setattr(oidc, "create_tiered_authenticator", _create_authenticator)

    auth_system = await oidc.get_tiered_auth_system()
    assert auth_system is not None

    cached_system = await oidc.get_tiered_auth_system()
    assert cached_system is auth_system
    assert len(instances) == 1


async def test_get_tiered_auth_system_handles_unavailable(monkeypatch):
    """Unavailable tiered auth system should raise a 503 HTTPException."""

    monkeypatch.setattr(oidc, "_tiered_auth_system", None)
    monkeypatch.setattr(oidc, "TIERED_AUTH_SYSTEM_AVAILABLE", False)

    with pytest.raises(HTTPException) as exc_info:
        await oidc.get_tiered_auth_system()

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "unavailable" in exc_info.value.detail.lower()
