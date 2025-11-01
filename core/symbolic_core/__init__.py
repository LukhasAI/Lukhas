"""Symbolic core bridge for plan_symbolic_core_preservation."""

from __future__ import annotations

import hashlib
import json
from importlib import import_module
from typing import Any

__all__ = ["plan_symbolic_core_preservation"]

for _module in (
    "lukhas_website.core.symbolic_core",
    "labs.core.symbolic_core",
    "core.symbolic_core",
):
    try:
        backend = import_module(_module)
        if hasattr(backend, "plan_symbolic_core_preservation"):
            plan_symbolic_core_preservation = getattr(backend, "plan_symbolic_core_preservation")  # type: ignore
            break
    except Exception:
        continue
else:

    def plan_symbolic_core_preservation(  # type: ignore
        collapse_state: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Provide a deterministic fallback plan for symbolic core preservation."""

        collapse_state = collapse_state or {}
        recommended_actions: list[str] = []

        for node_id, metrics in collapse_state.items():
            drift_score = float(metrics.get("driftScore", metrics.get("drift_score", 0.0)))
            affect_delta = float(metrics.get("affect_delta", metrics.get("affectDelta", 0.0)))

            if drift_score >= 0.6:
                recommended_actions.append(
                    f"Stabilize symbolic drift for {node_id}"
                )
            elif affect_delta >= 0.4:
                recommended_actions.append(
                    f"Harmonize affect_delta for {node_id}"
                )

        if not recommended_actions:
            recommended_actions.append("Maintain symbolic homeostasis protocol")

        collapse_hash = hashlib.sha256(
            json.dumps(collapse_state, sort_keys=True).encode("utf-8")
        ).hexdigest()

        # ΛTAG: collapseHash - deterministic signature for preservation plan lineage
        return {
            "status": "fallback_plan",
            "collapseHash": collapse_hash,
            "recommended_actions": recommended_actions,
            "analysis": {
                "nodes_evaluated": len(collapse_state),
                "drift_alerts": sum(
                    1 for action in recommended_actions if "drift" in action
                ),
                "affect_alerts": sum(
                    1 for action in recommended_actions if "affect_delta" in action
                ),
            },
        }
