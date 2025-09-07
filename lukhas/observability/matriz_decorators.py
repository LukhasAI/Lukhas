from __future__ import annotations

from functools import wraps

from .matriz_emit import emit, make_node
import streamlit as st


def instrument(
    ntype: str,
    *,
    label: str | None = None,
    capability: str = "core:op",
    tenant: str = "default",
    salience: float = 0.4,
    urgency: float = 0.5,
):
    _ = tenant

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
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
