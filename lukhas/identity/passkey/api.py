import os
from typing import Any

from lukhas.observability.matriz_decorators import instrument

from .registry import get_provider
import streamlit as st

FEATURE = os.getenv("FEATURE_IDENTITY_PASSKEY", "false").lower() == "true"


@instrument("DECISION", label="identity:passkey.verify", salience=0.5, urgency=0.8)
def verify_passkey(assertion: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal, safe passkey verify.
    - Works with builtin provider (stub) in DRY_RUN
    - Real WebAuthn provider can be registered via registry when enabled
    """
    provider = get_provider(enabled=FEATURE)
    return provider.verify(assertion)
