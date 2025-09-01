from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from .matriz_emit import emit, make_node


def instrument(
    ntype: str,
    *,
    label: str | None = None,
    capability: str = "core:op",
    tenant: str = "default",
    salience: float = 0.4,
    urgency: float = 0.5,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    _ = tenant

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            prov = {
                "producer": f"{fn.__module__}.{fn.__name__}",
                "capabilities": [capability],
                "tenant": kwargs.get("tenant", "default"),
                "trace_id": kwargs.get("trace_id", "LT-local"),
                "consent_scopes": kwargs.get("consent_scopes", ["system:internal"]),
            }
            # Use provided salience/urgency or fallback to kwargs/defaults
            state = kwargs.get(
                "matriz_state",
                {"confidence": 0.8, "salience": salience, "urgency": urgency},
            )
            labels = [label] if label else None
            node = make_node(ntype=ntype, state=state, provenance=prov, labels=labels)
            emit(node)
            return fn(*args, **kwargs)

        return wrapper

    return deco
