from .providers.null_webauthn import NullWebAuthnProvider
_provider = None

def register(provider) -> None:
    global _provider
    _provider = provider

def get_provider(enabled: bool):
    if not enabled or _provider is None:
        return NullWebAuthnProvider()
    return _provider