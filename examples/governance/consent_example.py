#!/usr/bin/env python3
"""
Guardian System Example: Consent Management

This script provides a mock implementation of the Guardian system for consent management.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock Database
_consent_db: Dict[str, Dict[str, Any]] = {}
_audit_log: List[Dict[str, Any]] = []


class ConsentDeniedException(Exception):
    """Raised when consent is not granted for a specific data access."""
    pass


@dataclass
class GuardianPolicy:
    """Defines a data usage policy."""
    purpose: str
    data_types: List[str]
    retention_days: int
    jurisdictions: List[str]


def collect_user_consent(user_id: str, policy: GuardianPolicy) -> Dict[str, Any]:
    """Simulates collecting user consent for a given policy."""
    consent = {
        "user_id": user_id,
        "policy": policy,
        "granted": True,  # Assume user grants consent in this example
        "timestamp": datetime.utcnow(),
    }
    _consent_db[user_id] = consent
    _audit_log.append({"event": "consent_collected", "user_id": user_id, "policy": policy.purpose})
    return consent


def verify_consent(user_id: str, data_type: str) -> bool:
    """Verifies if the user has granted consent for a specific data type."""
    consent = _consent_db.get(user_id)
    if not consent or not consent["granted"]:
        return False

    policy = consent["policy"]
    if data_type not in policy.data_types:
        return False

    # Check if consent is expired
    if datetime.utcnow() > consent["timestamp"] + timedelta(days=policy.retention_days):
        return False

    _audit_log.append({"event": "consent_verified", "user_id": user_id, "data_type": data_type})
    return True


def access_health_records(user_id: str) -> Dict[str, Any]:
    """Simulates accessing health records for a user."""
    if verify_consent(user_id, "health_records"):
        _audit_log.append({"event": "data_accessed", "user_id": user_id, "data_type": "health_records"})
        return {"user_id": user_id, "data": "[mock health data]"}
    else:
        raise ConsentDeniedException("Consent not granted for accessing health records.")


def get_audit_trail(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves the audit trail for a specific user."""
    return [log for log in _audit_log if log.get("user_id") == user_id]


if __name__ == "__main__":
    # 1. Define policy
    policy = GuardianPolicy(
        purpose="research",
        data_types=["health_records"],
        retention_days=365,
        jurisdictions=["US", "EU"],
    )

    # 2. Collect consent
    user_id = "patient-123"
    consent = collect_user_consent(user_id, policy)
    print(f"Consent collected for user {user_id} for the purpose of {policy.purpose}")

    # 3. Verify before access
    try:
        data = access_health_records(user_id)
        print(f"Successfully accessed health records: {data}")
    except ConsentDeniedException as e:
        print(f"Error: {e}")

    # 4. Audit
    audit_trail = get_audit_trail(user_id)
    print(f"\nAudit trail for user {user_id}:")
    for log in audit_trail:
        print(f"  - {log}")
