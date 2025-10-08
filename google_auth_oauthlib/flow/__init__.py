"""Submodule shim for google_auth_oauthlib.flow."""

from __future__ import annotations

try:
    from importlib import import_module

    _real = import_module("google_auth_oauthlib.flow")  # type: ignore
    globals().update(vars(_real))
except Exception:  # pragma: no cover - fallback
    from google_auth_oauthlib import flow as _flow  # type: ignore

    InstalledAppFlow = getattr(_flow, "InstalledAppFlow")

    class Flow:  # type: ignore
        InstalledAppFlow = InstalledAppFlow

    __all__ = ["InstalledAppFlow", "Flow"]
else:
    __all__ = [name for name in globals() if not name.startswith("_")]

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = [name for name in globals() if not name.startswith("_")]

if "Flow" not in globals():
    _installed = globals().get("InstalledAppFlow")

    if _installed is not None:

        class Flow:
            """Fallback Flow wrapper delegating to InstalledAppFlow."""

            InstalledAppFlow = _installed

            @staticmethod
            def from_client_secrets_file(*args, **kwargs):
                return _installed.from_client_secrets_file(*args, **kwargs)

            @staticmethod
            def from_client_config(*args, **kwargs):
                return _installed.from_client_config(*args, **kwargs)

    else:

        class Flow:
            """Minimal Flow stub used when google_auth_oauthlib is unavailable."""

            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            @staticmethod
            def from_client_secrets_file(*args, **kwargs):
                return Flow(*args, **kwargs)

            @staticmethod
            def from_client_config(*args, **kwargs):
                return Flow(*args, **kwargs)

    globals()["Flow"] = Flow

if "Flow" not in __all__:
    __all__.append("Flow")
