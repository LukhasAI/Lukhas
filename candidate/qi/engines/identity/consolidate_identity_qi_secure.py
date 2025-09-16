#!/usr/bin/env python3
"""
LUKHAS 2030 Identity Quantum Secure Consolidation
Quantum-resistant identity and access
"""
import json
from datetime import datetime, timezone


def consolidate_identities(primary, secondary_list, rules=None):
    """Consolidate multiple identities into a single canonical identity.

    Args:
        primary (dict): The primary identity record.
        secondary_list (list[dict]): A list of secondary identity records.
        rules (dict, optional): A dictionary of rules to guide consolidation. Defaults to None.

    Returns:
        tuple[dict, dict]: A tuple containing the merged identity and a report of the consolidation process.
    """
    merged_identity = primary.copy()
    report = {
        "consolidation_start_utc": datetime.now(timezone.utc).isoformat(),
        "primary_source": primary.get("id", "unknown"),
        "secondary_sources": [s.get("id", "unknown") for s in secondary_list],
        "decisions": [],
        "conflicts": [],
        "errors": [],
    }

    # Sort secondary identities by timestamp, newest first
    secondary_list.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    ignore_conflict_fields = ["id", "timestamp"]

    for secondary in secondary_list:
        if not isinstance(secondary, dict):
            report["errors"].append(f"Invalid secondary record format: {secondary}")
            continue

        for key, value in secondary.items():
            if key not in merged_identity:
                merged_identity[key] = value
                report["decisions"].append({
                    "field": key,
                    "action": "added",
                    "source": secondary.get("id", "unknown"),
                    "value_source": str(value)
                })
            elif merged_identity[key] != value and key not in ignore_conflict_fields:
                # Conflict detected. Primary wins by default in this simple implementation.
                report["conflicts"].append({
                    "field": key,
                    "primary_value": merged_identity[key],
                    "secondary_value": value,
                    "resolution": "kept primary",
                    "source": secondary.get("id", "unknown"),
                })

    report["consolidation_end_utc"] = datetime.now(timezone.utc).isoformat()
    return merged_identity, report

if __name__ == "__main__":
    primary_identity = {
        "id": "primary-123",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "timestamp": "2023-01-01T12:00:00Z"
    }

    secondary_identities = [
        {
            "id": "secondary-456",
            "email": "johndoe@work.com",
            "phone": "123-456-7890",
            "timestamp": "2023-01-02T12:00:00Z"
        },
        {
            "id": "secondary-789",
            "address": "123 Main St",
            "timestamp": "2023-01-01T18:00:00Z"
        }
    ]

    merged, report = consolidate_identities(primary_identity, secondary_identities)

    print("--- Merged Identity ---")
    print(json.dumps(merged, indent=2))
    print("\n--- Consolidation Report ---")
    print(json.dumps(report, indent=2))
