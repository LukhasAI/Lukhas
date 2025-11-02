#!/usr/bin/env python3
import json
import pathlib
import sys

from jsonschema import Draft202012Validator

cat_path = pathlib.Path("mcp-servers/lukhas-devtools-mcp/tooling/catalog.json")
sch_path = pathlib.Path("schemas/mcp.catalog.schema.json")

catalog = json.loads(cat_path.read_text())
schema = json.loads(sch_path.read_text())

errors = sorted(Draft202012Validator(schema).iter_errors(catalog), key=lambda e: e.path)
if errors:
    print("❌ catalog.json violates schema:")
    for e in errors:
        loc = "/".join([str(p) for p in e.path])
        print(f" - {loc}: {e.message}")
    sys.exit(1)

# Assert namespace + names sanity and stable 11 tools
ns = catalog["namespace"]
tools = catalog["tools"]
names = [t["name"] for t in tools]
if len(names) != len(set(names)):
    dupes = {n for n in names if names.count(n) > 1}
    print(f"❌ duplicate tool names: {sorted(dupes)}")
    sys.exit(1)

EXPECTED = {
    "manifests.validate",
    "manifests.lock",
    "registry.build",
    "registry.diff",
    "docs.registry.refresh",
    "docs.frontmatter.guard",
    "conveyor.plan",
    "conveyor.execute",
    "sim.schedule",
    "sim.collect",
    "audit.export",
}
missing = EXPECTED - set(names)
extra = set(names) - EXPECTED
if missing:
    print(f"❌ missing tools: {sorted(missing)}")
    sys.exit(1)
if extra:
    print(f"❌ unexpected tools: {sorted(extra)}")
    sys.exit(1)

print(f"✅ catalog.json valid ({ns}) with {len(names)} tools")
