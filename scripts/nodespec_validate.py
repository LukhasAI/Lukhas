#!/usr/bin/env python3
"""
Validate NodeSpec example files against the schema.
Prints "NodeSpec examples OK" on success, exits non-zero on failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema  # type: ignore
except Exception as e:  # pragma: no cover
    print("❌ jsonschema not installed. Install requirements-dev or config/requirements.txt", e)
    sys.exit(2)

root = Path(__file__).resolve().parents[1]
schema_path = root / "docs/schemas/nodespec_schema.json"
examples = [
    root / "docs/schemas/examples/memory_adapter.json",
    root / "docs/schemas/examples/dream_processor.json",
]

if not schema_path.exists():  # pragma: no cover
    print(f"❌ Schema not found: {schema_path}")
    sys.exit(3)

schema = json.loads(schema_path.read_text())
for ex in examples:
    if ex.exists():
        jsonschema.validate(json.loads(ex.read_text()), schema)

print("NodeSpec examples OK")
