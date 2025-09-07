from typing import Any, Optional

import streamlit as st

from .providers.null_webauthn import NullWebAuthnProvider

_provider: Optional[Any] = None


def register(provider: Any) -> None:
    global _provider
_provider = provider


def get_provider(enabled: bool) -> Any:
    if not enabled or _provider is None:
        return NullWebAuthnProvider()
return _provider
