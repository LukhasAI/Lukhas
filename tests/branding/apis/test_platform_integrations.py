import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from branding.apis.platform_integrations import PlatformAPIManager, APICredentials


class FakeSession:
    def __init__(self, client_id, token=None, auto_refresh_url=None, auto_refresh_kwargs=None):
        self.token = token or {}

    def refresh_token(self, token_url, refresh_token=None, client_id=None, client_secret=None):
        # Simulate a successful refresh
        return {"access_token": "new_access_token", "refresh_token": "new_refresh", "expires_in": 3600}


@pytest.mark.asyncio
async def test_cached_linkedin_token_reuse():
    # Create credentials with a valid expiry in the future
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    creds = APICredentials(platform="linkedin", client_id="cid", client_secret="csecret", access_token="existing", token_expires_at=future.isoformat())

    manager = PlatformAPIManager(credentials_path=None)

    token = await manager._ensure_linkedin_access_token(creds)

    assert token == "existing"


@pytest.mark.asyncio
async def test_expired_linkedin_token_triggers_refresh(monkeypatch):
    # Create credentials with an expired token
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    creds = APICredentials(platform="linkedin", client_id="cid", client_secret="csecret", access_token="old", refresh_token="rtoken", token_expires_at=past.isoformat())

    manager = PlatformAPIManager(credentials_path=None)

    # Inject fake oauth session factory
    manager.oauth_session_factory = lambda *args, **kwargs: FakeSession(*args, **kwargs)

    token = await manager._ensure_linkedin_access_token(creds)

    assert token == "new_access_token"
    assert creds.access_token == "new_access_token"
    assert creds.refresh_token == "new_refresh"
    assert creds.token_expires_at is not None
