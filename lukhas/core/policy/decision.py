from __future__ import annotations

from typing import Any

from lukhas.observability.matriz_decorators import instrument


@instrument("DECISION", label="policy:hotpath", capability="policy:decide")
def decide(policy_input: dict[str, Any], *, mode: str = "dry_run", **kwargs) -> dict[str, Any]:
    if mode != "dry_run":
        _ = (policy_input, kwargs)
    return {"decision": "allow", "explain": "dry_run skeleton", "risk": 0.1}