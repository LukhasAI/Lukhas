import logging
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

if "_bridgeutils" not in sys.modules:
    bridgeutils = types.ModuleType("_bridgeutils")

    def _bridge_from_candidates(*_args, **_kwargs):
        return [], {}

    bridgeutils.bridge_from_candidates = _bridge_from_candidates
    sys.modules["_bridgeutils"] = bridgeutils

from branding.apis import platform_integrations
from branding.apis.platform_integrations import APICredentials, PlatformAPIManager


@pytest.fixture
def manager(monkeypatch, tmp_path):
    def fake_setup_logging(self):
        logger = logging.getLogger(f"test-platform-integrations-{id(self)}")
        logger.handlers = []
        logger.propagate = False
        logger.addHandler(logging.NullHandler())
        return logger

    monkeypatch.setattr(PlatformAPIManager, "_setup_logging", fake_setup_logging, raising=False)
    monkeypatch.setattr(PlatformAPIManager, "_load_credentials", lambda self: None, raising=False)
    monkeypatch.setattr(PlatformAPIManager, "_initialize_platform_clients", lambda self: None, raising=False)

    manager = PlatformAPIManager(credentials_path=str(tmp_path / "creds.json"))
    manager.credentials = {}
    manager.oauth_tokens = {}
    return manager


@pytest.mark.asyncio
async def test_ensure_oauth_token_without_library(monkeypatch, manager):
    monkeypatch.setattr(platform_integrations, "OAUTH_AVAILABLE", False, raising=False)
    manager.credentials["linkedin"] = APICredentials(
        platform="linkedin",
        api_key="",
        api_secret="",
        client_id="client-id",
        client_secret="client-secret",
        access_token="cached-token",
    )

    token = await manager._ensure_oauth_token("linkedin")

    assert token == "cached-token"
    assert manager.oauth_tokens["linkedin"]["access_token"] == "cached-token"


@pytest.mark.asyncio
async def test_refresh_oauth_token(monkeypatch, manager):
    monkeypatch.setattr(platform_integrations, "OAUTH_AVAILABLE", True, raising=False)

    refreshed_payload = {
        "access_token": "new-access-token",
        "expires_in": 3600,
        "refresh_token": "new-refresh-token",
    }
    captured = {}

    class DummySession:
        def __init__(self, client_id, token):
            captured["init"] = {"client_id": client_id, "token": token}

        def refresh_token(self, token_url, **kwargs):
            captured["request"] = {"token_url": token_url, "kwargs": kwargs}
            return refreshed_payload

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(platform_integrations, "OAuth2Session", DummySession, raising=False)
    monkeypatch.setattr(platform_integrations.asyncio, "to_thread", fake_to_thread, raising=False)

    manager.credentials["linkedin"] = APICredentials(
        platform="linkedin",
        api_key="",
        api_secret="",
        client_id="client-id",
        client_secret="client-secret",
        access_token="old-token",
        refresh_token="refresh-token",
    )
    manager.oauth_tokens["linkedin"] = {
        "access_token": "old-token",
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=10),
    }

    token = await manager._ensure_oauth_token("linkedin")

    assert token == "new-access-token"
    assert manager.credentials["linkedin"].access_token == "new-access-token"
    assert manager.oauth_tokens["linkedin"]["access_token"] == "new-access-token"
    assert captured["request"]["token_url"] == "https://www.linkedin.com/oauth/v2/accessToken"
    assert captured["request"]["kwargs"]["client_id"] == "client-id"
    assert captured["request"]["kwargs"]["client_secret"] == "client-secret"
