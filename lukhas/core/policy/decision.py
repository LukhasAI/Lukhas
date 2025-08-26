from __future__ import annotations

from typing import Any, Dict

from lukhas.observability.matriz_decorators import instrument


@instrument("DECISION", label="policy:hotpath", capability="policy:decide")
def decide(policy_input: Dict[str, Any], *, mode: str = "dry_run", **kwargs) -> Dict[str, Any]:
    if mode != "dry_run":
        pass
    return {"decision": "allow", "explain": "dry_run skeleton", "risk": 0.1}
