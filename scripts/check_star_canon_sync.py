#!/usr/bin/env python3
"""
Check Star Canon Sync Guard

Ensures canon files (star_canon.json) match schema enum to prevent drift.
Used in CI to catch naming inconsistencies before manifest generation.

Exit 0: All canon files synchronized
Exit 1: Canon drift detected
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Canonical sources
CANON_FILES = [
    ROOT / "scripts/star_canon.json",
    ROOT / "packages/star_canon_py/star_canon/star_canon.json",
]
SCHEMA_PATH = ROOT / "schemas/matriz_module_compliance.schema.json"


def load_canon_stars(path):
    """Extract stars array from canon file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("stars", [])


def load_schema_enum():
    """Extract primary_star enum from schema."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    # Navigate to constellation_alignment.properties.primary_star.enum
    constellation = schema.get("properties", {}).get("constellation_alignment", {})
    primary_star = constellation.get("properties", {}).get("primary_star", {})
    return primary_star.get("enum", [])


def main():
    """Validate canon-schema sync."""
    print("🔍 Checking star canon sync...")

    # Load schema enum as source of truth
    schema_enum = load_schema_enum()
    if not schema_enum:
        print("❌ ERROR: Could not load schema enum from", SCHEMA_PATH)
        return 1

    print(f"✅ Schema enum has {len(schema_enum)} entries")

    # Check each canon file
    errors = []
    for canon_path in CANON_FILES:
        if not canon_path.exists():
            errors.append(f"❌ Missing canon file: {canon_path}")
            continue

        canon_stars = load_canon_stars(canon_path)

        # Convert to sets for comparison (excluding "Supporting" if present)
        canon_set = set(s for s in canon_stars if s != "Supporting")
        schema_set = set(s for s in schema_enum if s != "Supporting")

        if canon_set != schema_set:
            errors.append(f"❌ Canon mismatch in {canon_path.relative_to(ROOT)}")

            missing = schema_set - canon_set
            if missing:
                errors.append(f"   Missing in canon: {missing}")

            extra = canon_set - schema_set
            if extra:
                errors.append(f"   Extra in canon: {extra}")
        else:
            print(f"✅ {canon_path.relative_to(ROOT)} synced")

    # Report results
    if errors:
        print("\n".join(errors))
        print("\n💡 Fix: Update canon files to match schema enum")
        return 1

    print("✅ All canon files synchronized with schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
