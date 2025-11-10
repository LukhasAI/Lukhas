"""Tests for routing admin authentication helper."""

import logging
import sys
import types
from importlib import import_module
from typing import List, Optional, Tuple, Dict

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from lukhas_website.lukhas.api.routing_admin import (
    ADMIN_PERMISSION,
    get_admin_user,
)
from starlette.requests import Request

# Provide lightweight bridges by reusing the repository implementation when available.
bridgeutils_module = import_module("scripts.utils._bridgeutils")
sys.modules.setdefault("_bridgeutils", bridgeutils_module)
sys.modules.setdefault(
    "observability.matriz_decorators",
    import_module("lukhas_website.lukhas.observability.matriz_decorators"),
)
structlog_stub = types.ModuleType("structlog")
structlog_stub.get_logger = lambda name=None: logging.getLogger(name or "structlog")
sys.modules.setdefault("structlog", structlog_stub)
identity_pkg = types.ModuleType("identity")
identity_pkg.__path__ = []  # type: ignore[attr-defined]
identity_auth_service = import_module("lukhas_website.lukhas.identity.auth_service")
identity_pkg.auth_service = identity_auth_service
sys.modules.setdefault("identity", identity_pkg)
sys.modules.setdefault("identity.auth_service", identity_auth_service)


# Provide orchestration stubs so the admin router imports without heavy dependencies.
orchestration_pkg = types.ModuleType("orchestration")
orchestration_pkg.__path__ = []  # type: ignore[attr-defined]
sys.modules.setdefault("orchestration", orchestration_pkg)

externalized_module = types.ModuleType("orchestration.externalized_orchestrator")


async def _stub_get_externalized_orchestrator():  # pragma: no cover - stub
    return None


externalized_module.get_externalized_orchestrator = _stub_get_externalized_orchestrator
sys.modules.setdefault("orchestration.externalized_orchestrator", externalized_module)

health_monitor_module = types.ModuleType("orchestration.health_monitor")


class _StubHealthMonitor:  # pragma: no cover - stub
    async def get_all_provider_health(self):
        return {}


async def _stub_get_health_monitor():  # pragma: no cover - stub
    return _StubHealthMonitor()


health_monitor_module.get_health_monitor = _stub_get_health_monitor
sys.modules.setdefault("orchestration.health_monitor", health_monitor_module)

routing_config_module = types.ModuleType("orchestration.routing_config")


class _StubRoutingConfigManager:  # pragma: no cover - stub
    def get_configuration(self):
        return types.SimpleNamespace(
            version="test",  # minimal fields for serialization paths
            default_strategy=types.SimpleNamespace(value="round_robin"),
            default_providers=[],
            rules=[],
            ab_tests=[],
            health_check_interval=30,
            circuit_breaker_threshold=0,
            circuit_breaker_timeout=0,
            context_timeout=0,
            metadata={},
        )

    def get_rule_for_request(self, *_args, **_kwargs):
        return None


async def _stub_get_routing_config_manager():  # pragma: no cover - stub
    return _StubRoutingConfigManager()


routing_config_module.get_routing_config_manager = _stub_get_routing_config_manager
sys.modules.setdefault("orchestration.routing_config", routing_config_module)

routing_strategies_module = types.ModuleType("orchestration.routing_strategies")


class RoutingContext:  # pragma: no cover - stub
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class _StubRoutingEngine:  # pragma: no cover - stub
    async def route_request(self, *_args, **_kwargs):
        return None


def get_routing_engine():  # pragma: no cover - stub
    return _StubRoutingEngine()


routing_strategies_module.RoutingContext = RoutingContext
routing_strategies_module.get_routing_engine = get_routing_engine
sys.modules.setdefault("orchestration.routing_strategies", routing_strategies_module)


def _build_request(headers: Optional[List[Tuple[bytes, bytes]]] = None) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "scheme": "http",
        "query_string": b"",
        "headers": headers or [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "http_version": "1.1",
    }

    async def receive() -> Dict[str, object]:  # pragma: no cover - stub receiver
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)



@pytest.mark.asyncio
async def test_get_admin_user_valid_token(monkeypatch):
    """Valid tokens with admin permissions should return user context."""

    async def mock_verify(token, **kwargs):
        assert token == "valid-token"
        return {
            "sub": "admin-user",
            "permissions": [ADMIN_PERMISSION],
            "claims": {"aud": "lukhas-routing-admin"},
        }

    monkeypatch.setattr(
        "lukhas_website.lukhas.api.routing_admin.verify_token", mock_verify
    )

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")

    admin_user = await get_admin_user(_build_request(), credentials)

    assert admin_user["user_id"] == "admin-user"
    assert ADMIN_PERMISSION in admin_user["permissions"]


@pytest.mark.asyncio
async def test_get_admin_user_missing_permission(monkeypatch):
    """Tokens without routing admin permissions should be rejected."""

    async def mock_verify(token, **kwargs):
        return {
            "sub": "basic-user",
            "permissions": ["routing:read"],
        }

    monkeypatch.setattr(
        "lukhas_website.lukhas.api.routing_admin.verify_token", mock_verify
    )

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")

    with pytest.raises(HTTPException) as exc_info:
        await get_admin_user(_build_request(), credentials)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_admin_user_invalid_token(monkeypatch):
    """Invalid tokens should raise HTTP 401 errors."""

    async def mock_verify(token, **kwargs):
        raise ValueError("invalid token")

    monkeypatch.setattr(
        "lukhas_website.lukhas.api.routing_admin.verify_token", mock_verify
    )

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")

    with pytest.raises(HTTPException) as exc_info:
        await get_admin_user(_build_request(), credentials)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_admin_user_missing_credentials():
    """Missing credentials should result in 401 response."""

    with pytest.raises(HTTPException) as exc_info:
        await get_admin_user(_build_request(), None)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
