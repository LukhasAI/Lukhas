from typing import Any


class NullConsentProvider:
    """Safe, local, ephemeral provider; no network, no PII leaks."""
    def record(self, entry: dict[str, Any]) -> dict[str, Any]:
        # Echo entry with ack; real provider plugs in via registry later.
        return {"ok": True, "provider": "null", "entry": entry}
