"""Tests for :mod:`core.api.api_system`."""

from __future__ import annotations

import logging
import sys
from types import ModuleType
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Provide lightweight shims for optional dependencies when they are absent.
try:  # pragma: no cover - exercised only when structlog is missing
    import structlog  # type: ignore  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    structlog_stub = ModuleType("structlog")
    structlog_stub.get_logger = logging.getLogger
    sys.modules["structlog"] = structlog_stub

core_security_module = sys.modules.setdefault("core.security", ModuleType("core.security"))

if "core.security.auth" not in sys.modules:  # pragma: no cover
    auth_module = ModuleType("core.security.auth")

    class _AuthSystem:
        def verify_user_access(self, *_args, **_kwargs):
            return True

        def log_activity(self, *_args, **_kwargs):
            return None

    def get_auth_system() -> _AuthSystem:
        return _AuthSystem()

    auth_module.get_auth_system = get_auth_system  # type: ignore[attr-defined]
    sys.modules["core.security.auth"] = auth_module
    core_security_module.auth = auth_module  # type: ignore[attr-defined]

if "core.security.security_integration" not in sys.modules:  # pragma: no cover
    integration_module = ModuleType("core.security.security_integration")

    class _SecurityIntegration:
        async def validate_request(self, _request):
            return True, None

        async def create_secure_session(self, *_args, **_kwargs):
            return {"session_id": "stub"}

        async def verify_mfa(self, *_args, **_kwargs):
            return {"verified": True}

    async def get_security_integration() -> _SecurityIntegration:
        return _SecurityIntegration()

    integration_module.get_security_integration = get_security_integration  # type: ignore[attr-defined]
    sys.modules["core.security.security_integration"] = integration_module
    core_security_module.security_integration = integration_module  # type: ignore[attr-defined]

from core.api.api_system import EnhancedAPISystem, create_app


@pytest.fixture()
def api_system() -> EnhancedAPISystem:
    """Return a fresh :class:`EnhancedAPISystem` for each test."""

    return EnhancedAPISystem()


def test_create_app_returns_fastapi_instance() -> None:
    """``create_app`` should return a configured FastAPI application."""

    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "LUKHAS Cognitive AI Enhanced API"


def test_health_endpoint_available_without_startup(api_system: EnhancedAPISystem) -> None:
    """Health route should be accessible even before services are initialized."""

    client = TestClient(api_system.app)
    response = client.get("/api/v2/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert set(payload["services"]) == {
        "symbolic_engine",
        "consciousness",
        "memory",
        "guardian",
        "emotion",
        "dream",
        "coordination",
    }


def test_cors_middleware_is_configured(api_system: EnhancedAPISystem) -> None:
    """The application should include CORS middleware in its stack."""

    has_cors = any("CORSMiddleware" in middleware.cls.__name__ for middleware in api_system.app.user_middleware)
    assert has_cors


@pytest.mark.asyncio()
async def test_validate_auth_delegates_to_security(api_system: EnhancedAPISystem) -> None:
    """``_validate_auth`` should rely on the configured security integration."""

    api_system.security = AsyncMock()
    api_system.security.validate_request.return_value = (True, None)

    result = await api_system._validate_auth("token", "operation")

    api_system.security.validate_request.assert_awaited_once()
    assert result == (True, None)


@pytest.mark.asyncio()
async def test_get_service_metrics_handles_missing_services(api_system: EnhancedAPISystem) -> None:
    """Service metric helper should provide sensible defaults."""

    result = await api_system._get_service_metrics(None)
    assert result == {"status": "unavailable"}

    service = AsyncMock()
    service.get_metrics.return_value = {"status": "ok"}
    result = await api_system._get_service_metrics(service)
    service.get_metrics.assert_awaited_once()
    assert result == {"status": "ok"}
