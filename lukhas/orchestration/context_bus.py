from __future__ import annotations

from typing import Any, Dict

from lukhas.observability.matriz_decorators import instrument


@instrument("CONTEXT", label="orchestration:entry", capability="orchestrator:context")
def build_context(ctx_in: Dict[str, Any], *, mode: str = "dry_run", **kwargs) -> Dict[str, Any]:
    if mode != "dry_run":
        pass
    base = {"session": {"id": ctx_in.get("session_id","local")}, "tenant": ctx_in.get("tenant","default")}
    base.update({"policy_hints": ctx_in.get("policy_hints", {})})
    return base
