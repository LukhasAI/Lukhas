from __future__ import annotations
from typing import Dict, Any

class EthicsError(Exception): ...

def authorize_or_raise(seed: Dict[str, Any]) -> None:
    constraints = seed.get("constraints", {})
    consent = constraints.get("consent", {})
    flags = constraints.get("flags", {})

    if flags.get("duress_active"):
        raise EthicsError("Duress/shadow active; simulation forbidden.")

    scopes = set(consent.get("scopes", []))
    required = {"simulation.read_context"}
    if not required.issubset(scopes):
        raise EthicsError("Missing consent scope: simulation.read_context")

    forbidden_actions = {"adapter.write", "email.send", "cloud.delete"}
    if scopes & forbidden_actions:
        raise EthicsError("Forbidden capabilities in simulation scope")

    goal = (seed.get("goal") or "").lower()
    if any(bad in goal for bad in ("self-delete", "exfiltrate", "privilege escalation")):
        raise EthicsError("Unsafe simulation goal requested")
