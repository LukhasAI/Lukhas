#!/usr/bin/env python3
"""
T4/0.01% Vocabulary Validator
==============================

Enforce controlled vocabularies:
- features must be in vocab/features.json
- tags must be in vocab/tags.json

Hard fail on any non-canonical entries.
"""

import json
import sys
from pathlib import Path


def main():
    root = Path(".")

    # Load vocabularies
    features_path = root / "vocab" / "features.json"
    tags_path = root / "vocab" / "tags.json"

    if not features_path.exists() or not tags_path.exists():
        print("❌ Vocabulary files not found", file=sys.stderr)
        sys.exit(1)

    features = set(json.loads(features_path.read_text()).keys())
    allowed_tags = set(json.loads(tags_path.read_text())["allowed"])

    # Find all manifests
    manifests = [
        m
        for m in root.rglob("module.manifest.json")
        if not any(part in m.parts for part in ["node_modules", ".venv", "dist", "__pycache__"])
    ]

    print(f"🔍 Validating vocabularies in {len(manifests)} manifests...")

    errors = []

    for manifest_path in manifests:
        try:
            data = json.loads(manifest_path.read_text())

            # Check features
            manifest_features = data.get("features", [])
            unknown_features = [f for f in manifest_features if f not in features]

            if unknown_features:
                errors.append((manifest_path.parent.name, f"unknown features: {', '.join(unknown_features)}"))

            # Check tags
            manifest_tags = data.get("tags", [])
            invalid_tags = [t for t in manifest_tags if t not in allowed_tags]

            if invalid_tags:
                errors.append((manifest_path.parent.name, f"non-canonical tags: {', '.join(invalid_tags)}"))

        except (json.JSONDecodeError, KeyError) as e:
            errors.append((manifest_path.parent.name, f"error reading: {e}"))

    if errors:
        print(f"\n❌ Vocabulary validation failed ({len(errors)} errors):\n", file=sys.stderr)
        for module, error in errors:
            print(f"  {module}: {error}", file=sys.stderr)
        print("\n💡 Add missing features to vocab/features.json or tags to vocab/tags.json", file=sys.stderr)
        sys.exit(1)

    print("✅ All features and tags are canonical")
    sys.exit(0)


if __name__ == "__main__":
    main()
