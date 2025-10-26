"""Compat shim for tests when google-auth-oauthlib is unavailable."""

from __future__ import annotations

from importlib import import_module

try:
    _real = import_module("google_auth_oauthlib")  # Prefer real package when present
    globals().update(vars(_real))
except Exception:  # pragma: no cover - fallback stub

    class _Credentials:
        """Very small placeholder credentials object."""

        def to_json(self) -> str:
            return "{}"

    class _InstalledAppFlow:
        """Minimal installed app flow stub."""

        @classmethod
        def from_client_secrets_file(cls, *args, **kwargs):
            return cls()

        def run_local_server(self, *args, **kwargs):
            return _Credentials()

    class flow:  # - mimic module attribute
        """Flow namespace compatible with google_auth_oauthlib.flow."""

        InstalledAppFlow = _InstalledAppFlow

    __all__ = ["flow"]
