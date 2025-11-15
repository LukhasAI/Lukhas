# GDPR Issue 11: Implement Automated Data Retention Policy

## Priority: P0 - GDPR Core Compliance
## Estimated Effort: 10 days
## Target: Complete Automated Data Retention System

---

## 🎯 Objective

Implement automated data retention policy system that automatically deletes expired data according to GDPR requirements and business policies.

## 📊 Current State

- **GDPR Compliance**: 58%
- **Data Retention**: Manual, no automation
- **Legal Requirement**: GDPR requires data kept no longer than necessary
- **Target**: 75% GDPR compliance

## 🔍 Background

GDPR requires:
- Data kept no longer than necessary
- Clear retention periods
- Automatic deletion after expiration
- Audit logs retained for legal requirements (6 years)

## 📋 Deliverables

### 1. Retention Policy Configuration

**File**: `lukhas/compliance/data_retention.py`

```python
from datetime import datetime, timedelta
from typing import List, Dict

class DataRetentionPolicy:
    """Automated data retention and cleanup."""
    
    RETENTION_PERIODS = {
        "memory_folds": timedelta(days=90),  # 90 days of inactivity
        "interaction_logs": timedelta(days=180),  # 6 months
        "audit_logs": timedelta(days=2190),  # 6 years (legal requirement)
        "consciousness_states": timedelta(days=30),  # 30 days
        "temporary_data": timedelta(days=1),  # 24 hours
    }
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Run scheduled cleanup of expired data."""
        results = {}
        
        for data_type, retention_period in self.RETENTION_PERIODS.items():
            cutoff_date = datetime.utcnow() - retention_period
            
            if data_type == "memory_folds":
                count = await self.cleanup_memory_folds(cutoff_date)
            elif data_type == "interaction_logs":
                count = await self.cleanup_interaction_logs(cutoff_date)
            elif data_type == "consciousness_states":
                count = await self.cleanup_consciousness_states(cutoff_date)
            elif data_type == "temporary_data":
                count = await self.cleanup_temporary_data(cutoff_date)
            # Note: audit_logs are never auto-deleted (legal requirement)
            
            results[data_type] = count
        
        # Log cleanup results for audit
        await self.log_cleanup_results(results)
        
        return results
```

### 2. Cleanup Functions

```python
async def cleanup_memory_folds(self, cutoff_date: datetime) -> int:
    """Delete memory folds with no activity since cutoff_date."""
    deleted = await memory_db.delete_many({
        "last_accessed": {"$lt": cutoff_date},
        "pinned": False  # Don't delete pinned memories
    })
    return deleted.deleted_count

async def cleanup_interaction_logs(self, cutoff_date: datetime) -> int:
    """Delete old interaction logs."""
    deleted = await interaction_db.delete_many({
        "timestamp": {"$lt": cutoff_date}
    })
    return deleted.deleted_count
```

### 3. Cron Job Setup

**File**: `kubernetes/cronjobs/data-retention.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: lukhas-data-retention
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: retention-cleanup
            image: lukhas/compliance:latest
            command:
            - python
            - -m
            - lukhas.compliance.data_retention
            env:
            - name: DRY_RUN
              value: "false"
          restartPolicy: OnFailure
```

### 4. User Preferences

Allow users to configure retention:

```python
@router.patch("/users/{user_id}/retention-preferences")
async def update_retention_preferences(
    user_id: str,
    preferences: Dict[str, int]  # Days to retain
) -> Dict[str, Any]:
    """Allow users to customize retention periods."""
    # Validate within allowed ranges
    validated = validate_retention_preferences(preferences)
    
    await user_db.update_one(
        {"user_id": user_id},
        {"$set": {"retention_preferences": validated}}
    )
    
    return {"status": "updated", "preferences": validated}
```

### 5. Testing

```python
@pytest.mark.asyncio
async def test_cleanup_deletes_old_data():
    """Verify old data is deleted."""
    # Create old data
    old_date = datetime.utcnow() - timedelta(days=100)
    await create_test_memory(created_at=old_date)
    
    # Run cleanup
    policy = DataRetentionPolicy()
    results = await policy.cleanup_expired_data()
    
    # Verify deleted
    assert results["memory_folds"] > 0

@pytest.mark.asyncio
async def test_pinned_memories_not_deleted():
    """Pinned memories should not be deleted."""
    old_date = datetime.utcnow() - timedelta(days=100)
    await create_test_memory(created_at=old_date, pinned=True)
    
    policy = DataRetentionPolicy()
    await policy.cleanup_expired_data()
    
    # Pinned memory still exists
    memory = await memory_db.find_one({"pinned": True})
    assert memory is not None
```

### 6. Documentation

- [ ] Create `docs/gdpr/DATA_RETENTION_POLICY.md`
- [ ] Document retention periods
- [ ] User configuration guide
- [ ] Audit log policy

## ✅ Acceptance Criteria

- [ ] Automated retention policy implemented
- [ ] Scheduled cleanup job deployed
- [ ] User-configurable retention preferences
- [ ] Audit logging of all deletions
- [ ] Dashboard showing retention status
- [ ] Unit tests with >80% coverage
- [ ] Documentation complete

## 🏷️ Labels: `gdpr`, `compliance`, `p0`, `automation`, `data-retention`

---

**Estimated Days**: 10 days | **Phase**: GDPR Phase 2
