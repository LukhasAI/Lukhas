## HANDOFF B→C: GPT-5 Pro → GitHub Copilot

**Status**: ✅ Agent B deliverables complete

**Completed Artifacts**:
- ✅ `docs/reports/schema_audit.md` - 7 findings with actionable schema patches
- ✅ `.github/workflows/pqc-sign-verify.yml` - PQC CI with Dilithium2 + fallback
- ✅ `services/registry/tests/test_noop_guard_integration.py` - Integration test (1/1 passing)
- ✅ `docs/security/MATRIZ_PQC_CHECKLIST.md` - 6-week migration plan
- ✅ MATRIZ-007 updated with precise acceptance criteria

**Validation Results**:
- NodeSpec examples: ✅ Validated successfully
- No-op guard integration test: ✅ 1 passed in 0.67s
- PQC library: ⚠️ Not installed locally (CI will handle)

---

### Agent C (GitHub Copilot) Tasks

**Goal**: Expand tests, create usage documentation, polish README

#### 1. Negative Tests
Create `services/registry/tests/test_registry_negative.py` with:
- Test invalid NodeSpec (missing required fields)
- Test missing GLYMPH provenance (should return HTTP 403)
- Test bad signature/tampering detection (future PQC integration)
- Test malformed JSON in register endpoint
- Test query with non-existent signal/capability

**Expected**: 5+ new tests, all passing

#### 2. Usage Documentation
Create `docs/usage/registry_examples.md` with curl examples:
```bash
# Register a node
curl -X POST http://localhost:8080/api/v1/registry/register \
  -H "Content-Type: application/json" \
  -d @docs/schemas/examples/memory_adapter.json

# Validate a NodeSpec
curl -X POST http://localhost:8080/api/v1/registry/validate \
  -H "Content-Type: application/json" \
  -d '{"node_spec": {...}}'

# Query by signal
curl http://localhost:8080/api/v1/registry/query?signal=memory_stored

# Query by capability
curl http://localhost:8080/api/v1/registry/query?capability=memory/episodic

# Deregister a node
curl -X DELETE http://localhost:8080/api/v1/registry/<registry_id>
```

**Expected**: Complete usage guide with copy-paste examples

#### 3. README Expansion
Update `services/registry/README.md` with:
- Section: "How to test PQC locally"
  - Install liboqs: `sudo apt-get install liboqs-dev` (or build from source)
  - Install python-oqs: `pip install python-oqs`
  - Run PQC smoke test: `python -c "import oqs; print(oqs.sig.algorithms())"`
  - Link to `docs/security/MATRIZ_PQC_CHECKLIST.md`
- Section: "Running tests"
  - Unit tests: `pytest services/registry/tests -v`
  - Integration tests: `pytest services/registry/tests/test_noop_guard_integration.py -v`
- Section: "CI/CD"
  - Link to `.github/workflows/pqc-sign-verify.yml`
  - Explain fallback marker behavior

**Expected**: README updated with PQC dev setup section

---

### Deliverables Summary

**Files to create**:
1. `services/registry/tests/test_registry_negative.py` (5+ tests)
2. `docs/usage/registry_examples.md` (curl examples)
3. Updated `services/registry/README.md` (PQC section)

**Acceptance Criteria**:
- All new tests pass locally: `pytest services/registry/tests -v`
- Documentation contains exact, copy-paste ready commands
- README links to security checklist and CI workflow

---

### Next: HANDOFF C→D

After completing above, hand off to **Agent D (Codex)** for:
- Scripts/Makefile polish
- CI automation (registry-smoke target)
- Final PR comment templates
