from typing import Any

import streamlit as st


class NullWebAuthnProvider:
    """Local, deterministic verification; does NOT touch network or PII."""

    def verify(self, assertion: dict[str, Any]) -> dict[str, Any]:
        # Always accept in DRY_RUN; include minimal audit info
        return {
            "ok": True,
            "provider": "null",
            "challenge": assertion.get("challenge", "dryrun"),
        }
