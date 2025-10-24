#!/usr/bin/env python3
"""Convert flat NodeSpec format to nested NodeSpec v1 format.

Usage:
    cat flat_nodespec.json | python3 tools/nodespec_flatmap.py > nested_nodespec.json
"""
import json
import sys
import datetime


def convert_flat_to_nested(flat_spec):
    """Convert flat NodeSpec to nested format."""
    # If already nested (has identity key), return as-is
    if "identity" in flat_spec:
        return flat_spec

    # Build nested structure
    nested = {
        "node_type": flat_spec.get("node_type", "unknown"),
        "metadata": {
            "name": flat_spec.get("name", flat_spec.get("node_type", "unknown").split(".")[-1]),
            "version": flat_spec.get("version", "0.0.1"),
            "schema_version": flat_spec.get("schema_version", "nodespec.v1"),
            "authors": flat_spec.get("authors", ["LUKHAS"]),
            "created_at": flat_spec.get("created_at", datetime.date.today().isoformat())
        },
        "identity": {
            "owner_id": flat_spec.get("owner_id", "GLYMPH:unknown"),
            "lane": flat_spec.get("lane", "core"),
            "tier": flat_spec.get("tier", 3),
            "roles": flat_spec.get("roles", [])
        },
        "interfaces": flat_spec.get("interfaces", {
            "inputs": [],
            "outputs": [],
            "signals": {}
        }),
        "contracts": flat_spec.get("contracts", {}),
        "provenance_manifest": flat_spec.get("provenance_manifest", {}),
        "security": flat_spec.get("security", {}),
        "graceful_degradation": flat_spec.get("graceful_degradation", {}),
        "compatibility": flat_spec.get("compatibility", {}),
        "extraplanetary_policy": flat_spec.get("extraplanetary_policy", {})
    }

    return nested


if __name__ == "__main__":
    try:
        flat_data = json.load(sys.stdin)
        nested_data = convert_flat_to_nested(flat_data)
        json.dump(nested_data, sys.stdout, indent=2)
        print()  # Add newline at end
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
