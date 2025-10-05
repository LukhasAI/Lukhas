#!/usr/bin/env python3
import json
import pathlib
import sys

required = {
 "lukhas.manifests.validate","lukhas.manifests.lock","lukhas.registry.build","lukhas.registry.diff",
 "lukhas.docs.registry.refresh","lukhas.docs.frontmatter.guard",
 "lukhas.conveyor.plan","lukhas.conveyor.execute","lukhas.sim.schedule","lukhas.sim.collect","lukhas.audit.export"
}
cat = json.loads(pathlib.Path("mcp-servers/lukhas-devtools-mcp/tooling/catalog.json").read_text())
names = {f"lukhas.{t['name']}" for t in cat["tools"]}
missing = sorted(required - names)
if missing:
    print("❌ Missing tools:", missing); sys.exit(1)
print("✅ MCP tool contract satisfied")
