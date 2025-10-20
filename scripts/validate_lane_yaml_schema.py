#!/usr/bin/env python3
"""
Validate all module.lane.yaml files against schema/module.lane.schema.json.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator


def main() -> int:
    schema_path = Path("schema/module.lane.schema.json")
    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)
    root = Path(".")
    errors = 0
    for p in root.rglob("module.lane.yaml"):
        try:
            data = yaml.safe_load(p.read_text())
        except Exception as e:
            print(f"[ERROR] {p}: cannot parse YAML: {e}")
            errors += 1
            continue
        for err in validator.iter_errors(data):
            print(f"[SCHEMA] {p}: {err.message}")
            errors += 1
    if errors:
        print(f"Schema validation errors: {errors}")
        return 1
    print("Schema validation passed for all lane YAMLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())

