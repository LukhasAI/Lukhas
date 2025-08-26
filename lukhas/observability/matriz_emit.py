from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, Optional

try:
    from MATRIZ.utils.matriz_validate import validate_node  # adjust path if needed
except Exception:
    def validate_node(_): return None

def make_node(*, ntype: str, state: Dict[str, float], provenance: Dict[str, Any],
              labels: Optional[list[str]]=None, links: Optional[list[dict]]=None,
              evidence: Optional[list[dict]]=None) -> dict:
    node = {
        "$kind": "MATRIZ_NODE",
        "version": 1,
        "schema_ref": "lukhas://schemas/matriz_node_v1.json",
        "id": f"LT-{uuid.uuid4()}",
        "type": ntype,
        "state": state,
        "timestamps": {"created_ts": int(time.time()*1000)},
        "provenance": provenance
    }
    if labels:   node["labels"] = labels[:12]
    if links:    node["links"]  = links
    if evidence: node["evidence"] = evidence
    try: validate_node(node)
    except Exception: pass
    return node

def emit(node: dict) -> None:
    print(json.dumps(node, ensure_ascii=False))
