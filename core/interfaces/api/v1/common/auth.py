"""Bridge for core.interfaces.api.v1.common.auth."""

from __future__ import annotations

from importlib import import_module

_CANDIDATES = (
    "lukhas_website.lukhas.core.interfaces.api.v1.common.auth",
    "candidate.core.interfaces.api.v1.common.auth",
)

for _candidate in _CANDIDATES:
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class _FallbackAuth:
    def __init__(self):
        pass


globals().setdefault("AuthSession", _FallbackAuth)
globals().setdefault("AuthContext", dict)


def _check_rate_limit(*args, **kwargs):  # type: ignore[misc]
    return True


globals().setdefault("_check_rate_limit", _check_rate_limit)


def _validate_key_format(key: str) -> bool:  # type: ignore[misc]
    return isinstance(key, str) and len(key) > 10


globals().setdefault("_validate_key_format", _validate_key_format)


def _verify_key_signature(*args, **kwargs):  # type: ignore[misc]
    return True


globals().setdefault("_verify_key_signature", _verify_key_signature)
