# Jules-02 — Activity trace persistence & audit chain

**Priority**: CRITICAL
**File**: `candidate/governance/identity/core/trace/activity_logger.py`
**Lines**: 225, 229, 294

## Goal
Implement persistent storage, ΛTIER integration, audit-chain linking for activity traces.

## Requirements
- Persistent sink (file/db write works)
- Chain ID increments
- Minimal test logs 2 chained events
- ΛTIER integration

## Steps
1. **Inspect activity_logger.py** around lines 225, 229, 294 for existing TODO markers
2. **Add persistent storage**:
   - Implement SQLite backend OR append-only JSON file
   - Add environment variable `ACTIVITY_SINK=sqlite|file`
3. **Implement audit chain**:
   - Generate chain hash: `sha256(previous_hash + event_json)`
   - Store chain_id/hash with each event
   - Link events via hash references
4. **Add ΛTIER integration**:
   - Import from `lukhas.tiers` (create stub if needed)
   - Store tier metadata with events
5. **Add readback function** to verify chain continuity

## Commands
```bash
# Test implementation
python -c "from candidate.governance.identity.core.trace.activity_logger import append_event; append_event({'msg':'test1'})"
python -c "from candidate.governance.identity.core.trace.activity_logger import append_event; append_event({'msg':'test2'})"
python -c "from candidate.governance.identity.core.trace.activity_logger import read_chain; print(read_chain(2))"
```

## Acceptance Criteria
- [ ] Two appended events produce new chain hash
- [ ] Chain IDs increment properly
- [ ] Simple readback test passes
- [ ] File/DB write operations work
- [ ] ΛTIER metadata stored with events

## Implementation Notes
- Keep lightweight, use stdlib (sqlite3 + hashlib)
- Add configuration via environment variables
- Include clear docstrings for maintenance
- No external dependencies beyond stdlib
