"""Tests for REST API middleware tier enforcement and rate limiting."""

from __future__ import annotations

import time
from dataclasses import dataclass

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from core.interfaces.api.v1.v1.rest import middleware
from core.interfaces.api.v1.v1.rest.middleware import (
    RateLimitConfig,
    RateLimitMiddleware,
    require_tier,
)


@dataclass
class _StubIdentityManager:
    """Simple identity manager stub for deterministic tests."""

    tier: str = "T1"

    def get_user_identity(self, user_id: str) -> dict[str, str]:  # noqa: D401 - simple stub
        return {"user_id": user_id, "tier": self.tier}


@pytest.fixture(autouse=True)
def _patch_identity_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middleware, "IDENTITY_MANAGER", _StubIdentityManager())


def _build_app_for_rate_limit(rate_limiter: RateLimitMiddleware, *, tier: int) -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def _inject_identity(request: Request, call_next):  # noqa: D401 - middleware signature
        request.state.user_id = "user-test"
        request.state.user_tier = tier
        request.state.tier_level = tier
        response = await rate_limiter(request, call_next)
        return response

    @app.get("/ping")
    async def ping() -> JSONResponse:
        return JSONResponse({"ok": True})

    return app


def _build_app_for_tier(required_tier: int, *, user_tier: int) -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def _inject_state(request: Request, call_next):  # noqa: D401 - middleware signature
        request.state.user_id = "user-tier"
        request.state.user_tier = user_tier
        request.state.tier_level = user_tier
        return await call_next(request)

    @app.get("/secure")
    @require_tier(required_tier)
    async def secure_endpoint(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    return app


def test_require_tier_allows_when_tier_sufficient(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middleware, "IDENTITY_MANAGER", _StubIdentityManager(tier="T3"))
    app = _build_app_for_tier(required_tier=2, user_tier=3)
    client = TestClient(app)

    response = client.get("/secure")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_require_tier_blocks_insufficient_tier() -> None:
    app = _build_app_for_tier(required_tier=2, user_tier=1)
    client = TestClient(app)

    response = client.get("/secure")

    assert response.status_code == 403
    assert "Insufficient" in response.json()["detail"]


def test_rate_limit_blocks_after_limit_exceeded() -> None:
    config = {0: RateLimitConfig(limit=2, window_seconds=60)}
    limiter = RateLimitMiddleware(rate_limits=config, time_provider=time.monotonic)
    app = _build_app_for_rate_limit(limiter, tier=0)
    client = TestClient(app)

    resp1 = client.get("/ping")
    assert resp1.status_code == 200

    resp2 = client.get("/ping")
    assert resp2.status_code == 200

    resp3 = client.get("/ping")
    assert resp3.status_code == 429
    assert resp3.headers["X-RateLimit-Limit"] == "2"
    assert resp3.headers["X-RateLimit-Remaining"] == "0"


def test_rate_limit_unlimited_tier_returns_unlimited_headers() -> None:
    config = {0: RateLimitConfig(limit=2, window_seconds=60)}
    limiter = RateLimitMiddleware(rate_limits=config, time_provider=time.monotonic)
    app = _build_app_for_rate_limit(limiter, tier=3)
    client = TestClient(app)

    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.headers["X-RateLimit-Limit"] == "unlimited"
    assert resp.headers["X-RateLimit-Remaining"] == "unlimited"


