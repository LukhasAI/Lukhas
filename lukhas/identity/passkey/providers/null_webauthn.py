from typing import Any, Dict


class NullWebAuthnProvider:
    """Local, deterministic verification; does NOT touch network or PII."""
    def verify(self, assertion: Dict[str, Any]) -> Dict[str, Any]:
        # Always accept in DRY_RUN; include minimal audit info
        return {"ok": True, "provider": "null", "challenge": assertion.get("challenge","dryrun")}
