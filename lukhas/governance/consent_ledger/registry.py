from typing import Any, Optional

from .providers.null_provider import NullConsentProvider

# Registry is intentionally internal. candidate/* may register via runtime hooks later.
_provider: Optional[Any] = None


def register(provider: Any) -> None:
    global _provider
    _provider = provider


def get_provider(enabled: bool) -> Any:
    # If not enabled, force Null provider (no side-effects)
    if not enabled or _provider is None:
        return NullConsentProvider()
    return _provider
