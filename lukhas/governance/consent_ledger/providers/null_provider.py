from typing import Dict, Any

class NullConsentProvider:
    """Safe, local, ephemeral provider; no network, no PII leaks."""
    def record(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        # Echo entry with ack; real provider plugs in via registry later.
        return {"ok": True, "provider": "null", "entry": entry}