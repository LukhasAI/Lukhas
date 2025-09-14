# Jules-06 — PQC signer triage

**Priority**: CRITICAL
**File**: `candidate/qi/crypto/pqc_signer.py`
**Line**: 12

## Goal
Wire to MATRIZ or add explicit NotImplementedError + docstring and feature flag.

## Requirements
- No dead imports
- Clear error path
- Feature flag for MATRIZ integration

## Steps
1. **Inspect existing code** in `pqc_signer.py` around line 12
2. **Add feature flag**:
   - Environment variable: `ENABLE_MATRIZ_PQC_SIGNER=true|false`
   - Default to `false` for safety
3. **Implement conditional logic**:
   ```python
   import os

   if os.getenv('ENABLE_MATRIZ_PQC_SIGNER', 'false').lower() == 'true':
       try:
           from matriz_client import PQCClient  # Example
           # Wire to MATRIZ implementation
       except ImportError:
           raise NotImplementedError("MATRIZ client not available")
   else:
       raise NotImplementedError(
           "PQC signer requires MATRIZ integration. "
           "Set ENABLE_MATRIZ_PQC_SIGNER=true to enable."
       )
   ```
4. **Clean up dead imports** and unused code
5. **Add module docstring** describing expected integration
6. **Write unit test** for NotImplementedError path

## Commands
```bash
# Test PQC signer error path
python -c "from candidate.qi.crypto.pqc_signer import sign_message; print('Should raise NotImplementedError')"
ENABLE_MATRIZ_PQC_SIGNER=true python -c "from candidate.qi.crypto.pqc_signer import sign_message"
pytest -q tests/ -k pqc_signer
```

## ✅ STATUS: COMPLETED (2025-09-14)
**Completed By**: Jules + System Integration
**Commit**: `d5d2b2ab8 feat(pqc): triage pqc_signer with feature flag`

## Acceptance Criteria ✅ COMPLETED:
- [x] No dead/unreferenced imports remain
- [x] Clear NotImplementedError when MATRIZ disabled
- [x] Feature flag controls integration attempt
- [x] Unit test covers disabled state
- [x] Module docstring documents expected APIs

## Implementation Notes
- Keep cryptographic usage secure
- Avoid logging private key material
- Document expected MATRIZ client interface
- Consider gradual rollout strategy
- Add clear upgrade path documentation
