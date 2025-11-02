#!/usr/bin/env python3
import json
import pathlib
import sys

import yaml

cfg = yaml.safe_load(pathlib.Path("lukhas-mcp/config.yaml").read_text())
required_tools = {
    "manifests.validate",
    "manifests.lock",
    "registry.build",
    "docs.registry.refresh",
    "docs.frontmatter.guard",
    "conveyor.plan",
    "conveyor.execute",
    "sim.schedule",
    "sim.collect",
    "audit.export",
}
names = {t["name"] for t in cfg.get("tools", [])}
missing = sorted(list(required_tools - names))
if missing:
    print("❌ MCP config missing tools:", json.dumps(missing, indent=2))
    sys.exit(1)
print("✅ MCP config OK with required tools")
