#!/usr/bin/env python3
import json
import pathlib
import sys

import yaml

cfg = yaml.safe_load(pathlib.Path("lukhas-mcp/config.yaml").read_text())
required_tools = {
  "lukhas.manifests.validate",
  "lukhas.manifests.lock",
  "lukhas.registry.build",
  "lukhas.docs.registry.refresh",
  "lukhas.docs.frontmatter.guard",
  "lukhas.conveyor.plan",
  "lukhas.conveyor.execute",
  "lukhas.sim.schedule",
  "lukhas.sim.collect",
  "lukhas.audit.export",
}
names = {t["name"] for t in cfg.get("lukhas.tools", [])}
missing = sorted(list(required_tools - names))
if missing:
    print("❌ MCP config missing tools:", json.dumps(missing, indent=2))
    sys.exit(1)
print("✅ MCP config OK with required tools")
