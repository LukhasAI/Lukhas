# path: qi/docs/jurisdiction_diff.py
from __future__ import annotations

from typing import Any


def _diff_dict(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Structured diff: added/removed/changed (shallow+recursive on dicts)."""
    out = {"added": {}, "removed": {}, "changed": {}}
    ak = set(a.keys())
    bk = set(b.keys())
    for k in sorted(bk - ak):
        out["added"][k] = b[k]
    for k in sorted(ak - bk):
        out["removed"][k] = a[k]
    for k in sorted(ak & bk):
        av = a[k]
        bv = b[k]
        if isinstance(av, dict) and isinstance(bv, dict):
            sub = _diff_dict(av, bv)
            if any(sub.values()):
                out["changed"][k] = sub
        elif av != bv:
            out["changed"][k] = {"from": av, "to": bv}
    return {k: v for k, v in out.items() if v}


def compute_overlay_diff(overlay_mgr, j1: str, j2: str, *, context: str | None = None) -> dict[str, Any]:
    """
    overlay_mgr: RiskOverlayManager instance
    Returns structured diff of merged policies(j1,context) vs (j2,context)
    """
    p1 = overlay_mgr.get_policies(jurisdiction=j1, context=context)
    p2 = overlay_mgr.get_policies(jurisdiction=j2, context=context)
    return _diff_dict(p1, p2)