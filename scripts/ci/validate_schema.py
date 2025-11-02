#!/usr/bin/env python3
"""
T4/0.01% Schema Validator
==========================

Hard fail on any schema violations.
Used in CI to enforce manifest quality.
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


def main():
    root = Path(".")

    # Load base schema (enrichment adds fields, doesn't replace structure)
    schema_path = root / "schemas" / "module.manifest.schema.json"

    if not schema_path.exists():
        print("❌ Schema file not found", file=sys.stderr)
        sys.exit(1)

    schema = json.loads(schema_path.read_text())
    # Allow additional properties for enriched fields
    schema["additionalProperties"] = True
    validator = Draft202012Validator(schema)

    # Find all manifests
    manifests = [
        m
        for m in root.rglob("module.manifest.json")
        if not any(part in m.parts for part in ["node_modules", ".venv", "dist", "__pycache__"])
    ]

    print(f"🔍 Validating {len(manifests)} manifests...")

    errors = []

    for manifest_path in manifests:
        try:
            data = json.loads(manifest_path.read_text())
            validator.validate(data)
        except ValidationError as e:
            errors.append((manifest_path, str(e.message)))
        except json.JSONDecodeError as e:
            errors.append((manifest_path, f"Invalid JSON: {e}"))

    if errors:
        print(f"\n❌ Schema validation failed ({len(errors)} errors):\n", file=sys.stderr)
        for path, error in errors:
            print(f"  {path.parent.name}: {error}", file=sys.stderr)
        sys.exit(1)

    print("✅ All manifests valid")
    sys.exit(0)


if __name__ == "__main__":
    main()
