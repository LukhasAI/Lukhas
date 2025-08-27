from __future__ import annotations

import contextlib
import json
import time
import uuid
from typing import Any

try:
    from MATRIZ.utils.matriz_validate import validate_node  # adjust path if needed
except Exception:

    def validate_node(_):
        return None


def make_node(
    *,
    ntype: str,
    state: dict[str, float],
    provenance: dict[str, Any],
    labels: list[str] | None = None,
    links: list[dict] | None = None,
    evidence: list[dict] | None = None,
) -> dict:
    node = {
        "$kind": "MATRIZ_NODE",
        "version": 1,
        "schema_ref": "lukhas://schemas/matriz_node_v1.json",
        "id": f"LT-{uuid.uuid4()}",
        "type": ntype,
        "state": state,
        "timestamps": {"created_ts": int(time.time() * 1000)},
        "provenance": provenance,
    }
    if labels:
        node["labels"] = labels[:12]
    if links:
        node["links"] = links
    if evidence:
        node["evidence"] = evidence
    with contextlib.suppress(Exception):
        validate_node(node)
    return node


def emit(node: dict) -> None:
    print(json.dumps(node, ensure_ascii=False))
