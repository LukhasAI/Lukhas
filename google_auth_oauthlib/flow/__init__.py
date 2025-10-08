"""Submodule shim for google_auth_oauthlib.flow."""

from __future__ import annotations

try:
    from importlib import import_module

    _real = import_module("google_auth_oauthlib.flow")  # type: ignore
    globals().update(vars(_real))
except Exception:  # pragma: no cover - fallback
    from google_auth_oauthlib import flow as _flow  # type: ignore

    InstalledAppFlow = getattr(_flow, "InstalledAppFlow")

    __all__ = ["InstalledAppFlow"]
else:
    __all__ = [name for name in globals() if not name.startswith("_")]
