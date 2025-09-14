# Jules-03 — Ethics/Tiers reconciliation

**Priority**: CRITICAL
**File**: `candidate/consciousness/awareness/awareness_protocol.py`
**Line**: 143

## Goal
Map local "safety boundaries/tier names" to global LUKHAS Tier system.

## Requirements
- Single source of truth import (`lukhas.tiers`)
- Tests asserting mapping
- Typed error for unknown tiers

## Steps
1. **Locate tier usage** around line 143 in `awareness_protocol.py`
2. **Create/import global tiers**:
   - Import from `lukhas.tiers`
   - If not available, create stub `lukhas/tiers.py` with constants
3. **Replace local literals** with global tier constants
4. **Add mapping function**:
   ```python
   def map_local_tier_to_global(local_name: str) -> GlobalTier:
       """Map local tier name to global tier constant."""
   ```
5. **Add validation** that raises `ValueError` or `TierMappingError` for unknown tiers
6. **Write unit tests** covering known mappings and error cases

## Commands
```bash
# Test tier mapping
pytest -q tests/ -k awareness_protocol
python -c "from candidate.consciousness.awareness.awareness_protocol import map_local_tier_to_global; print(map_local_tier_to_global('critical'))"
```

## Acceptance Criteria
- [ ] File imports `lukhas.tiers` as single source of truth
- [ ] At least 3 tier mappings tested
- [ ] Unknown tier names raise typed error
- [ ] Local tier literals replaced with global constants
- [ ] Unit tests cover positive and negative cases

## Implementation Notes
- Keep mapping explicit and documented
- Document where local tier names originate
- Use clear error messages for debugging
- Consider backward compatibility during transition
