from __future__ import annotations

from typing import Any

from lukhas.observability.matriz_decorators import instrument
import streamlit as st


@instrument("CONTEXT", label="orchestration:entry", capability="orchestrator:context")
def build_context(ctx_in: dict[str, Any], *, mode: str = "dry_run", **kwargs) -> dict[str, Any]:
    if mode != "dry_run":
        _ = kwargs
        pass
    base = {
        "session": {"id": ctx_in.get("session_id", "local")},
        "tenant": ctx_in.get("tenant", "default"),
    }
    base.update({"policy_hints": ctx_in.get("policy_hints", {})})
    return base
