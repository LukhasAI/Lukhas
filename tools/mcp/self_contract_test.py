#!/usr/bin/env python3
import json
import pathlib
import sys

required = {
 "manifests.validate","manifests.lock","registry.build","registry.diff",
 "docs.registry.refresh","docs.frontmatter.guard",
 "conveyor.plan","conveyor.execute","sim.schedule","sim.collect","audit.export"
}
cat = json.loads(pathlib.Path("mcp-servers/lukhas-devtools-mcp/tooling/catalog.json").read_text())
names = {f"lukhas.{t['name']}" for t in cat["tools"]}
missing = sorted(required - names)
if missing:
    print("❌ Missing tools:", missing)
    sys.exit(1)
print("✅ MCP tool contract satisfied")
