# Guardian System Example: Consent Management

## Overview
This document provides a practical example of how to use the Guardian system for consent management and policy enforcement in a healthcare application that collects patient data for research.

## Use Case
The application needs to:
-   Define a data usage policy for research purposes.
-   Collect consent from patients to use their data.
-   Enforce the policy to ensure that data is only used for the intended purpose.
-   Maintain an audit trail of all consent-related activities.

## Step-by-Step Implementation

### 1. Define Data Usage Policy
First, we define a `GuardianPolicy` to specify the purpose of data collection, the types of data to be collected, the data retention period, and the jurisdictions where the data can be used.

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any

@dataclass
class GuardianPolicy:
    """Defines a data usage policy."""
    purpose: str
    data_types: List[str]
    retention_days: int
    jurisdictions: List[str]

policy = GuardianPolicy(
    purpose="research",
    data_types=["health_records"],
    retention_days=365,
    jurisdictions=["US", "EU"],
)
```

### 2. Collect User Consent
Next, we simulate collecting user consent for the defined policy. In a real application, this would involve presenting the policy to the user and obtaining their explicit consent.

```python
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

user_id = "patient-123"
consent = collect_user_consent(user_id, policy)
```

### 3. Enforce Policy
Before accessing any data, we must verify that the user has granted consent for the specific data type we want to access.

```python
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
```

### 4. Verify Consent
We can now access the health records, but only if consent is verified.

```python
class ConsentDeniedException(Exception):
    """Raised when consent is not granted for a specific data access."""
    pass

def access_health_records(user_id: str) -> Dict[str, Any]:
    """Simulates accessing health records for a user."""
    if verify_consent(user_id, "health_records"):
        _audit_log.append({"event": "data_accessed", "user_id": user_id, "data_type": "health_records"})
        return {"user_id": user_id, "data": "[mock health data]"}
    else:
        raise ConsentDeniedException("Consent not granted for accessing health records.")

try:
    data = access_health_records(user_id)
    print(f"Successfully accessed health records: {data}")
except ConsentDeniedException as e:
    print(f"Error: {e}")
```

### 5. Access Audit Trail
Finally, we can retrieve the audit trail for a specific user to see all consent-related activities.

```python
def get_audit_trail(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves the audit trail for a specific user."""
    return [log for log in _audit_log if log.get("user_id") == user_id]

audit_trail = get_audit_trail(user_id)
```

## Complete Working Example
The complete working example can be found in `examples/governance/consent_example.py`.

## Testing
To test the example, you can run the following command:

```bash
python -m unittest tests/examples/test_governance_example.py
```
