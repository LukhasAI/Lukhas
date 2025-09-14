# Jules-04 — Identity consolidation logic

**Priority**: CRITICAL
**File**: `candidate/qi/engines/identity/consolidate_identity_qi_secure.py`
**Line**: 33

## Goal
Implement consolidation logic mirroring what was completed in `governance/oversight/consolidate_guardian_governance.py`.

## Requirements
- Deterministic merge rules
- Report artifact
- Idempotent results

## Steps
1. **Study reference implementation**:
   - Read `governance/oversight/consolidate_guardian_governance.py`
   - Extract consolidation patterns and rules
2. **Implement core function**:
   ```python
   def consolidate_identities(primary, secondary_list, rules=None) -> (merged_identity, report):
       """Consolidate multiple identities into a single canonical identity."""
   ```
3. **Add deterministic rules**:
   - Field precedence (primary > secondary by timestamp/priority)
   - Conflict resolution strategies
   - Data validation and sanitization
4. **Generate report artifact**:
   - JSON/dict describing merge decisions
   - Track which fields came from which source
   - Log conflicts and resolutions
   - Include timestamps and metadata
5. **Ensure idempotency**: Same inputs → same outputs
6. **Add unit tests** for typical merges and edge cases

## Commands
```bash
# Test consolidation
python -c "from candidate.qi.engines.identity.consolidate_identity_qi_secure import consolidate_identities; print('Available')"
pytest -q tests/ -k consolidate_identity
```

## Acceptance Criteria
- [ ] Deterministic merge rules implemented
- [ ] Report artifact generated (JSON/dict format)
- [ ] Idempotent behavior verified in tests
- [ ] Unit tests cover typical and edge cases
- [ ] Mirrors governance consolidation patterns

## Implementation Notes
- Follow privacy rules (no secret logging)
- Use redaction placeholders for sensitive fields
- Document merge precedence clearly
- Consider versioning for future compatibility
- Keep security audit trail
