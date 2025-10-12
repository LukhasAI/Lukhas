#!/usr/bin/env python3
"""
Read docs/audits/compat_alias_hits.json and enforce a max threshold (optional).

Env:
  LUKHAS_COMPAT_MAX_HITS (int, default: -1 = report only)
"""
import json
import os
import sys
from pathlib import Path

path = Path("docs/audits/compat_alias_hits.json")
if not path.exists():
    print("[compat] no alias hits file found (ok on no-alias runs)")
    sys.exit(0)

hits = json.loads(path.read_text(encoding="utf-8") or "{}")
total = sum(hits.values())
print(f"[compat] alias hits total: {total}")
for k, v in sorted(hits.items(), key=lambda kv: kv[1], reverse=True):
    print(f"[compat]  {k}: {v}")

max_hits = int(os.getenv("LUKHAS_COMPAT_MAX_HITS", "-1"))
if max_hits >= 0 and total > max_hits:
    print(f"[compat] FAIL: alias hits {total} > max {max_hits}")
    sys.exit(2)
sys.exit(0)
