#!/usr/bin/env python3
"""
T4 Golden Validator - Golden Artifacts Validation
=================================================

Validates golden JSON artifacts against schemas.
Ensures golden test integrity and consistency.
"""

import json
import jsonschema
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_golden_schema(schema_path: Path) -> Dict[str, Any]:
    """Load the golden artifacts schema."""
    if not schema_path.exists():
        # Create default schema if missing
        default_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["module", "version", "timestamp", "data"],
            "properties": {
                "module": {"type": "string"},
                "version": {"type": "string"},
                "timestamp": {"type": "string"},
                "data": {"type": "object"},
                "metadata": {"type": "object"},
            },
            "additionalProperties": True,
        }

        schema_path.parent.mkdir(parents=True, exist_ok=True)
        with schema_path.open("w", encoding="utf-8") as f:
            json.dump(default_schema, f, indent=2)
        print(f"Created default golden schema at {schema_path}")
        return default_schema

    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_golden_json(golden_path: Path, schema: Dict[str, Any]) -> List[str]:
    """Validate a single golden JSON file against schema."""
    errors = []

    try:
        with golden_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        jsonschema.validate(instance=data, schema=schema)

        # Additional T4-specific validations
        if "tier1" in str(golden_path) and not data.get("metadata", {}).get("critical"):
            errors.append(f"{golden_path}: Tier1 golden missing critical metadata flag")

        if "timestamp" in data and not isinstance(data["timestamp"], str):
            errors.append(f"{golden_path}: timestamp should be string format")

    except json.JSONDecodeError as e:
        errors.append(f"{golden_path}: Invalid JSON - {e}")
    except jsonschema.ValidationError as e:
        errors.append(f"{golden_path}: Schema validation failed - {e.message}")
    except Exception as e:
        errors.append(f"{golden_path}: Validation error - {e}")

    return errors


def find_golden_files(search_dirs: List[Path]) -> List[Path]:
    """Find all golden JSON files in search directories."""
    golden_files = []

    for search_dir in search_dirs:
        if search_dir.exists():
            # Look for files with golden patterns
            for pattern in ["*golden*.json", "*_golden.json", "golden_*.json"]:
                golden_files.extend(search_dir.rglob(pattern))

            # Also check tests/golden/ directory structure
            golden_dir = search_dir / "golden"
            if golden_dir.exists():
                golden_files.extend(golden_dir.rglob("*.json"))

    return list(set(golden_files))  # Remove duplicates


def main():
    """Main golden validator entry point."""
    parser = argparse.ArgumentParser(description="T4 Golden Artifacts Validator")
    parser.add_argument("--schema", default="tests/specs/golden_schema.json", help="Golden schema file")
    parser.add_argument(
        "--dirs", nargs="*", default=["tests/", "tests/golden/"], help="Directories to search for golden files"
    )
    parser.add_argument("--strict", action="store_true", help="Fail on any violations")
    args = parser.parse_args()

    schema_path = Path(args.schema)
    search_dirs = [Path(d) for d in args.dirs]

    schema = load_golden_schema(schema_path)
    golden_files = find_golden_files(search_dirs)

    if not golden_files:
        print("ℹ️  No golden files found")
        return

    all_errors = []

    for golden_file in golden_files:
        errors = validate_golden_json(golden_file, schema)
        all_errors.extend(errors)

    if all_errors:
        print("T4 Golden Validation Errors:")
        for error in all_errors:
            print(f"  ❌ {error}")
        print(f"\nTotal errors: {len(all_errors)}")

        if args.strict:
            sys.exit(1)
    else:
        print(f"✅ All {len(golden_files)} golden files are valid")


if __name__ == "__main__":
    main()
