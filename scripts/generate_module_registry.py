#!/usr/bin/env python3
"""
Module: generate_module_registry.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""Generate MODULE_REGISTRY.json from all module.manifest.json files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(".")
OUT = ROOT / "docs/_generated/MODULE_REGISTRY.json"


def main():
    manifests = sorted(ROOT.rglob("module.manifest.json"))
    modules = []

    for manifest_path in manifests:
        try:
            data = json.loads(manifest_path.read_text())
            module_dir = manifest_path.parent

            # Find docs and tests
            docs = sorted([str(p.relative_to(ROOT)) for p in module_dir.rglob("*.md")])
            tests = sorted(
                [str(p.relative_to(ROOT)) for p in module_dir.glob("tests/**/*.py")]
            )

            modules.append(
                {
                    "name": data.get("module", module_dir.name),
                    "path": str(module_dir.relative_to(ROOT)),
                    "manifest": str(manifest_path.relative_to(ROOT)),
                    "description": data.get("description", ""),
                    "status": data.get("testing", {}).get("status", "unknown"),
                    "tags": data.get("tags", []),
                    "docs": docs,
                    "tests": tests,
                    "api_count": len(data.get("apis", {})),
                }
            )
        except Exception as e:
            print(f"⚠️  Error processing {manifest_path}: {e}")

    registry = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "module_count": len(modules),
        "modules": modules,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(f"✅ Generated MODULE_REGISTRY.json with {len(modules)} modules")
    print(f"   Location: {OUT}")
    return 0


if __name__ == "__main__":
    exit(main())
