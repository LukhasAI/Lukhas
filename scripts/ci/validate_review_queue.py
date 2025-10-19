#!/usr/bin/env python3
"""
Module: validate_review_queue.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
T4/0.01% Review Queue CI Validator
===================================

Validates review_queue.json against schema.
Hard fail on schema violations.

Usage:
    python scripts/ci/validate_review_queue.py
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

root = Path(".")
schema_path = root / "schemas" / "review_queue.schema.json"
queue_path = root / "manifests" / "review_queue.json"


def main():
    # No queue file = nothing to validate
    if not queue_path.exists():
        print("✅ no review_queue.json (nothing to validate)")
        sys.exit(0)

    # Load schema
    if not schema_path.exists():
        print(f"❌ schema not found: {schema_path}")
        sys.exit(1)

    try:
        schema = json.loads(schema_path.read_text())
        validator = Draft202012Validator(schema)
    except Exception as e:
        print(f"❌ invalid schema: {e}")
        sys.exit(1)

    # Load queue
    try:
        queue = json.loads(queue_path.read_text())
    except Exception as e:
        print(f"❌ invalid JSON in review_queue.json: {e}")
        sys.exit(1)

    # Validate
    try:
        validator.validate(queue)
    except ValidationError as e:
        print("❌ review_queue.json schema violation:")
        print(f"   {e.message}")
        print(f"   Path: {' -> '.join(str(p) for p in e.path)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ review_queue validation error: {e}")
        sys.exit(1)

    print(f"✅ review_queue.json is valid ({len(queue.get('items', []))} items)")
    sys.exit(0)


if __name__ == "__main__":
    main()
