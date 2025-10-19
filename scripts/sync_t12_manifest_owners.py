#!/usr/bin/env python3
"""
Module: sync_t12_manifest_owners.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Sync owners in module.manifest.json for T1/T2 modules.

For each manifest (excluding .archive):
- If testing.quality_tier is T1_critical or T2_important and metadata.owner is
  missing/unassigned, set owner to triage@lukhas and update last_updated.
"""
from __future__ import annotations

import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def is_archived(path: pathlib.Path) -> bool:
    return any(part == ".archive" for part in path.parts)


def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def main() -> None:
    changed = 0
    for mf in ROOT.rglob("module.manifest.json"):
        if is_archived(mf):
            continue
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        tier = (data.get("testing", {}) or {}).get("quality_tier") or ""
        if tier not in ("T1_critical", "T2_important"):
            continue
        meta = data.setdefault("metadata", {})
        owner = (meta.get("owner") or "").strip().lower()
        if owner in ("", "unassigned", "none", "-"):
            meta["owner"] = "triage@lukhas"
            meta["last_updated"] = now_iso()
            mf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"[OK] owner synced: {mf}")
            changed += 1
    print(f"Changed: {changed}")


if __name__ == "__main__":
    main()

