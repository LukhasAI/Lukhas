## HANDOFF A→B: Claude→GPT5 (CI + PQC)

**Artifact**: `services/registry/main.py` + tests (6/6 passing)

**Status**: ✅ Registry operational, GLYMPH gating enforced, HMAC checkpoints working

**Required for Agent B (GPT-5 Pro)**:
1. **PQC Migration Planning**: Create MATRIZ-007 ticket or enhance existing
   - ✅ **Already created**: https://github.com/LukhasAI/Lukhas/issues/490
   - Add precise acceptance criteria for Dilithium2 integration
   - Document key generation, rotation, and emergency revocation

2. **CI PQC Verification**: Create `.github/workflows/pqc-sign-verify.yml`
   - Build minimal Dilithium2 sign/verify example (use liboqs-python or pqcrypto)
   - Run registry checkpoint generation → sign → verify sequence
   - Fail CI if signature verification fails
   - Performance assertion: signing overhead ≤10ms

3. **Integration Test**: Add `services/registry/tests/test_checkpoint_signature.py`
   - Test checkpoint signing with deterministic key
   - Test signature verification on load
   - Test signature tampering detection

4. **Security Checklist**: Create `docs/security/MATRIZ_PQC_CHECKLIST.md`
   - Deploy steps (key generation, storage, distribution)
   - Key rotation policy and procedure
   - Emergency revocation (compromised key scenario)
   - Trust anchor lifecycle

**Deliverable**:
- `.github/workflows/pqc-sign-verify.yml` (CI job)
- `services/registry/tests/test_checkpoint_signature.py` (integration test)
- `docs/security/MATRIZ_PQC_CHECKLIST.md` (security guide)
- MATRIZ-007 updated with precise acceptance criteria

**Validation Commands**:
```bash
# Local tests
pytest services/registry/tests -q

# Expected: 6 passed (will be 7+ after checkpoint signature test added)
```

**Next**: `HANDOFF B→C` after PQC CI + security checklist complete
