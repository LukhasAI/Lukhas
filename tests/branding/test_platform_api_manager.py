import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

if "_bridgeutils" not in sys.modules:
    bridgeutils = ModuleType("_bridgeutils")

    def bridge_from_candidates(*_args: Any, **_kwargs: Any) -> tuple[tuple[str, ...], dict[str, Any]]:
        return (), {}

    bridgeutils.bridge_from_candidates = bridge_from_candidates  # type: ignore[attr-defined]
    sys.modules["_bridgeutils"] = bridgeutils

from branding.apis.platform_integrations import PlatformAPIManager


def _write_credentials(path: Path, overrides: dict[str, Any]) -> None:
    credentials = {
        "linkedin": {
            "platform": "linkedin",
            "api_key": "placeholder",
            "api_secret": "placeholder",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "access_token": "initial-token",
            "refresh_token": "refresh-token",
            "token_expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        }
    }
    credentials["linkedin"].update(overrides)

    path.write_text(json.dumps(credentials))


@pytest.mark.asyncio
async def test_ensure_linkedin_access_token_returns_existing_when_not_expiring(tmp_path: Path) -> None:
    creds_path = tmp_path / "creds.json"
    _write_credentials(creds_path, {})

    manager = PlatformAPIManager(credentials_path=str(creds_path))
    linkedin_creds = manager.credentials["linkedin"]

    linkedin_creds.access_token = "stable-token"
    linkedin_creds.token_expires_at = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()

    token = await manager._ensure_linkedin_access_token(linkedin_creds)

    assert token == "stable-token"


@pytest.mark.asyncio
async def test_ensure_linkedin_access_token_refreshes_when_expired(tmp_path: Path) -> None:
    creds_path = tmp_path / "creds.json"
    _write_credentials(
        creds_path,
        {
            "access_token": "expired-token",
            "token_expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        },
    )

    manager = PlatformAPIManager(credentials_path=str(creds_path))
    linkedin_creds = manager.credentials["linkedin"]

    class DummyOAuthSession:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            self.refresh_calls = []

        def refresh_token(self, token_url: str, **kwargs: Any) -> dict[str, Any]:
            self.refresh_calls.append((token_url, kwargs))
            return {
                "access_token": "refreshed-token",
                "expires_in": 900,
                "refresh_token": "new-refresh-token",
            }

    dummy_session = DummyOAuthSession()
    manager.oauth_session_factory = lambda *args, **kwargs: dummy_session

    persisted_states: list[dict[str, Any]] = []

    def fake_persist() -> None:
        persisted_states.append({"access_token": linkedin_creds.access_token, "token": linkedin_creds.token_expires_at})

    manager._persist_credentials = fake_persist  # type: ignore[assignment]

    token = await manager._ensure_linkedin_access_token(linkedin_creds)

    assert token == "refreshed-token"
    assert linkedin_creds.access_token == "refreshed-token"
    assert linkedin_creds.refresh_token == "new-refresh-token"
    assert persisted_states, "Credentials persistence should be triggered after refresh"


@pytest.mark.asyncio
async def test_ensure_linkedin_access_token_requires_oauth_library(tmp_path: Path) -> None:
    creds_path = tmp_path / "creds.json"
    _write_credentials(
        creds_path,
        {
            "access_token": None,
            "token_expires_at": None,
        },
    )

    manager = PlatformAPIManager(credentials_path=str(creds_path))
    manager.oauth_session_factory = None
    linkedin_creds = manager.credentials["linkedin"]

    with pytest.raises(RuntimeError):
        await manager._ensure_linkedin_access_token(linkedin_creds)
