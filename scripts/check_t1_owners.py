#!/usr/bin/env python3
"""
Module: check_t1_owners.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main():
    root = Path("manifests")
    bad = []
    for p in root.rglob("module.manifest.json"):
        if '/.archive/' in str(p):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        t = (d.get("testing") or {}).get("quality_tier")
        if t == "T1_critical":
            owner = (d.get("metadata") or {}).get("owner")
            if not owner or str(owner).strip().lower() in {"", "todo", "tbd", "unknown"}:
                mod = (d.get("module") or {}).get("name") or (d.get("module") or {}).get("path") or str(p.parent)
                bad.append((mod, str(p)))
    if bad:
        print("[FAIL] T1_critical modules missing metadata.owner:")
        for mod, path in bad:
            print(f"  - {mod} :: {path}")
        sys.exit(1)
    print("[OK] All T1_critical modules have owners.")

if __name__ == "__main__":
    main()
