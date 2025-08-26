from .providers.null_provider import NullConsentProvider

# Registry is intentionally internal. candidate/* may register via runtime hooks later.
_provider = None

def register(provider) -> None:
    global _provider
    _provider = provider

def get_provider(enabled: bool):
    # If not enabled, force Null provider (no side-effects)
    if not enabled or _provider is None:
        return NullConsentProvider()
    return _provider
