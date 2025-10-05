#!/usr/bin/env python3
import hashlib
import os
import pathlib
import sys

cat = pathlib.Path("mcp-servers/lukhas-devtools-mcp/tooling/catalog.json").read_bytes()
sha = hashlib.sha256(cat).hexdigest()[:12]
freeze = pathlib.Path("artifacts/mcp.catalog.sha")
freeze.parent.mkdir(parents=True, exist_ok=True)
if freeze.exists():
    old = freeze.read_text().strip()
    if old != sha and "ALLOW_CATALOG_CHANGE" not in os.environ:
        print(f"❌ catalog changed: {old} -> {sha} (set ALLOW_CATALOG_CHANGE=1 to proceed)")
        sys.exit(1)
freeze.write_text(sha)
print(f"✅ catalog sha: {sha}")
