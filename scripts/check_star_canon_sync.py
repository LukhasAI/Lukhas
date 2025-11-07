#!/usr/bin/env python3
"""Check Star Canon Sync Guard."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

from star_canon_utils import extract_canon_labels, iter_star_definitions

ROOT = Path(__file__).resolve().parents[1]

# Canonical sources
CANON_FILES = [
    ROOT / "scripts/star_canon.json",
    ROOT / "packages/star_canon_py/star_canon/star_canon.json",
]
SCHEMA_PATH = ROOT / "schemas/matriz_module_compliance.schema.json"

# ΛTAG: star_canon

def load_canon_payload(path: Path) -> dict[str, object]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_schema_enum() -> list[str]:
    """Extract primary_star enum from schema."""
    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        schema = json.load(handle)

    constellation = schema.get("properties", {}).get("constellation_alignment", {})
    primary_star = constellation.get("properties", {}).get("primary_star", {})
    return primary_star.get("enum", [])


def _non_supporting(labels: list[str]) -> set[str]:
    return {label for label in labels if "supporting" not in label.lower()}


def main() -> int:
    """Validate canon-schema sync."""
    print("🔍 Checking star canon sync...")

    schema_enum = load_schema_enum()
    if not schema_enum:
        print(f"❌ ERROR: Could not load schema enum from {SCHEMA_PATH}")
        return 1

    print(f"✅ Schema enum has {len(schema_enum)} entries")

    errors: list[str] = []
    labels_ref: list[str] | None = None
    defs_ref: list[dict[str, str]] | None = None

    schema_set = _non_supporting(schema_enum)

    for canon_path in CANON_FILES:
        if not canon_path.exists():
            errors.append(f"❌ Missing canon file: {canon_path}")
            continue

        payload = load_canon_payload(canon_path)
        labels = extract_canon_labels(payload)
        definitions = list(iter_star_definitions(payload))

        if labels_ref is None:
            labels_ref = labels
            defs_ref = definitions
        else:
            if labels != labels_ref:
                errors.append(
                    f"❌ Label drift detected in {canon_path.relative_to(ROOT)}"
                )
            if defs_ref is not None and definitions != defs_ref:
                errors.append(
                    f"❌ Definition drift detected in {canon_path.relative_to(ROOT)}"
                )

        canon_set = _non_supporting(labels)
        if canon_set != schema_set:
            errors.append(
                f"❌ Canon mismatch in {canon_path.relative_to(ROOT)}"
            )
            missing = sorted(schema_set - canon_set)
            extra = sorted(canon_set - schema_set)
            if missing:
                errors.append(f"   Missing in canon: {missing}")
            if extra:
                errors.append(f"   Extra in canon: {extra}")
        else:
            print(f"✅ {canon_path.relative_to(ROOT)} synced")

    if errors:
        print("\n".join(errors))
        print("\n💡 Fix: Update canon files to match schema enum and definitions")
        return 1

    print("✅ All canon files synchronized with schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
