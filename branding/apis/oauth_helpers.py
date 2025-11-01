from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional


class OAuthTokenManager:
    """Small helper to manage OAuth2 token refresh and caching.

    This is intentionally lightweight and uses an injected session factory
    (compatible with requests_oauthlib.OAuth2Session) so tests can inject
    a fake session without importing network libraries at module import time.
    """

    def __init__(self, oauth_session_factory: Optional[Callable[..., Any]] = None, logger: Optional[Any] = None):
        self._factory = oauth_session_factory
        self._logger = logger

    def _should_refresh(self, access_token: Optional[str], expires_at_iso: Optional[str]) -> bool:
        if not access_token:
            return True

        if not expires_at_iso:
            return False

        try:
            expires_at_str = expires_at_iso
            if expires_at_str.endswith("Z"):
                expires_at_str = expires_at_str.replace("Z", "+00:00")
            expires_at = datetime.fromisoformat(expires_at_str)
        except Exception:
            if self._logger:
                self._logger.warning("Unable to parse token expiry, forcing refresh.")
            return True

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Refresh if token expires within 5 minutes
        return expires_at <= datetime.now(timezone.utc) + timedelta(minutes=5)

    def refresh_token_sync(self, *, client_id: str, client_secret: str, refresh_token: str, token_url: str, current_access_token: Optional[str] = None) -> dict[str, Any]:
        """Perform a synchronous refresh_token call via the injected factory.

        Returns the token dict returned by the session.refresh_token call.
        """
        if not self._factory:
            raise RuntimeError("OAuth session factory is not configured for token refresh")

        session = self._factory(
            client_id,
            token={
                "access_token": current_access_token or "",
                "refresh_token": refresh_token,
                "token_type": "Bearer",
            },
            auto_refresh_url=token_url,
            auto_refresh_kwargs={"client_id": client_id, "client_secret": client_secret},
        )

        token = session.refresh_token(
            token_url,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )

        return token

    def get_access_token(self, *, creds: Any, token_url: str) -> str:
        """Ensure access_token in creds is valid; refresh synchronously if needed.

        The creds object is expected to have attributes: access_token, refresh_token, token_expires_at.
        On success the creds object will be updated in-place and the access_token returned.
        """
        if not self._should_refresh(creds.access_token, creds.token_expires_at):
            return creds.access_token

        if not creds.client_id or not creds.client_secret or not creds.refresh_token:
            raise RuntimeError("OAuth refresh requires client_id, client_secret, and refresh_token.")

        token = self.refresh_token_sync(
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            refresh_token=creds.refresh_token,
            token_url=token_url,
            current_access_token=creds.access_token,
        )

        access_token = token.get("access_token")
        if not access_token:
            raise RuntimeError("OAuth refresh did not return an access token.")

        expires_in = token.get("expires_in")
        expires_at = None
        if isinstance(expires_in, (int, float)):
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

        if token.get("refresh_token"):
            creds.refresh_token = token["refresh_token"]

        creds.access_token = access_token
        creds.token_expires_at = expires_at.isoformat() if expires_at else None

        if self._logger:
            self._logger.info("🔄 Refreshed OAuth access token via OAuthTokenManager.")

        return access_token
