# GDPR Issue 7: Implement Right to Access API (GDPR Art. 15)

## Priority: P0 - GDPR Core Compliance
## Estimated Effort: 15 days
## Target: Complete Right to Access API

---

## 🎯 Objective

Implement the Right to Access API (GDPR Article 15) allowing users to retrieve all personal data LUKHAS holds about them in a structured, machine-readable format.

## 📊 Current State

- **GDPR Compliance**: 58%
- **Data Subject Rights APIs**: 0/4 implemented
- **Legal Requirement**: GDPR Article 15 mandates this right
- **Target**: 75% GDPR compliance

## 🔍 Background

GDPR Article 15 grants data subjects the right to:
- Obtain confirmation of data processing
- Access their personal data
- Receive information about processing purposes
- Know data retention periods
- Understand data recipients

Failure to provide this can result in fines up to 4% of annual revenue or €20 million.

## 📋 Deliverables

### 1. API Endpoint Implementation

**File**: `lukhas/api/v1/data_rights.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/v1/data-rights", tags=["GDPR"])

@router.get("/users/{user_id}/data")
async def get_user_data(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Right to Access - GDPR Article 15.
    
    Returns all personal data LUKHAS holds about the user:
    - Identity data (ΛID, profile)
    - Memory folds and consciousness states
    - Interaction history
    - Processing purposes
    - Data retention periods
    - Third-party sharing (if any)
    
    Args:
        user_id: User identifier (ΛID)
        current_user: Authenticated user making the request
        
    Returns:
        Complete user data package with metadata
        
    Raises:
        HTTPException 403: If user requests data for another user
        HTTPException 404: If user not found
    """
    # Verify user is requesting their own data or has admin rights
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only access own data")
    
    # Gather all data from all systems
    return {
        "requested_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "identity": await get_identity_data(user_id),
        "memory": await get_memory_data(user_id),
        "consciousness": await get_consciousness_data(user_id),
        "interactions": await get_interaction_history(user_id),
        "processing_purposes": get_processing_purposes(),
        "retention_periods": get_retention_periods(),
        "third_parties": get_third_party_sharing(user_id),
        "export_format": "JSON",
        "controller": "LUKHAS AI Platform",
        "data_protection_officer": "dpo@lukhas.com"
    }
```

### 2. Data Collection Functions

Implement functions to gather all user data:

```python
async def get_identity_data(user_id: str) -> Dict[str, Any]:
    """Gather all identity-related data."""
    # Query identity database
    return {
        "lambda_id": user_id,
        "email": "user@example.com",  # Hashed or actual
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-11-15T00:00:00Z",
        "preferences": {...}
    }

async def get_memory_data(user_id: str) -> Dict[str, Any]:
    """Gather all memory folds and consciousness states."""
    return {
        "memory_folds": [...],
        "consciousness_states": [...],
        "total_folds": 42
    }

async def get_interaction_history(user_id: str) -> List[Dict[str, Any]]:
    """Gather all user interactions."""
    return [
        {
            "timestamp": "2025-11-15T10:00:00Z",
            "action": "reasoning_trace_viewed",
            "details": {...}
        }
    ]
```

### 3. API Documentation

**OpenAPI/Swagger Integration**:
```python
# Add to main FastAPI app
from fastapi import FastAPI
from lukhas.api.v1 import data_rights

app = FastAPI(
    title="LUKHAS Data Rights API",
    description="GDPR-compliant data subject rights endpoints",
    version="1.0.0"
)

app.include_router(data_rights.router)
```

### 4. Testing

**File**: `tests/api/test_data_rights.py`

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_user_can_access_own_data():
    """User can access their own data."""
    response = await client.get(
        "/v1/data-rights/users/user123/data",
        headers={"Authorization": f"Bearer {user123_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user123"
    assert "identity" in data
    assert "memory" in data

@pytest.mark.asyncio
async def test_user_cannot_access_other_data():
    """User cannot access another user's data."""
    response = await client.get(
        "/v1/data-rights/users/user456/data",
        headers={"Authorization": f"Bearer {user123_token}"}
    )
    assert response.status_code == 403
```

### 5. User Dashboard

**Frontend**: `products/frontend/pages/data-rights.tsx`

Simple dashboard for users to request their data:
```typescript
export default function DataRightsPage() {
  const [data, setData] = useState(null);
  
  const requestMyData = async () => {
    const response = await fetch('/v1/data-rights/users/me/data');
    setData(await response.json());
  };
  
  return (
    <div>
      <h1>Your Data Rights</h1>
      <button onClick={requestMyData}>Request My Data</button>
      {data && <DataDisplay data={data} />}
    </div>
  );
}
```

### 6. Documentation

- [ ] Create `docs/gdpr/RIGHT_TO_ACCESS_API.md`
- [ ] API endpoint documentation
- [ ] User guide for data access requests
- [ ] Admin guide for handling requests

## ✅ Acceptance Criteria

- [ ] API endpoint implemented and tested
- [ ] All data sources integrated (identity, memory, consciousness, interactions)
- [ ] Authentication and authorization working
- [ ] OpenAPI documentation generated
- [ ] Unit tests with >80% coverage
- [ ] Integration tests pass
- [ ] User dashboard functional
- [ ] Complete documentation
- [ ] Legal review completed

## 🏷️ Labels: `gdpr`, `compliance`, `p0`, `api`, `data-rights`

---

**Estimated Days**: 15 days | **Phase**: GDPR Phase 2
