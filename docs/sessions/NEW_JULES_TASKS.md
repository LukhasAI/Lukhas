# New Jules Task Assignments (TEST-014 onwards)

**Created**: 2025-11-06
**Source**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/project/QUICK_TEST_ASSIGN.md`

---

## ✅ Completed Sessions with PRs

### Ready for Review:

1. **PR #986**: TEST-005 Blockchain Coverage Verification
   - URL: https://github.com/LukhasAI/Lukhas/pull/986
   - Status: OPEN
   - Action: Review and merge

2. **PR #985**: TEST-013 Cross-Component Integration Tests
   - URL: https://github.com/LukhasAI/Lukhas/pull/985
   - Status: OPEN
   - Action: Review and merge

3. **PR #981**: TEST-011 Core Colonies Tests
   - URL: https://github.com/LukhasAI/Lukhas/pull/981
   - Status: OPEN
   - Action: Review and merge

4. **PR #978**: TEST-010 Quantum Financial Tests
   - URL: https://github.com/LukhasAI/Lukhas/pull/978
   - Status: OPEN
   - Action: Review and merge

**Note**: TEST-012 (Serve API) completed but PR not visible - may need to check session for details

---

## 🆕 New Sessions to Create (TEST-014 onwards)

### Priority Tasks (HIGH):

---

## SESSION 1: TEST-014 Smoke Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write comprehensive smoke tests for all critical paths per TEST-014.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-014, write smoke tests for system startup, API availability, core functionality, database connections, create tests/smoke/test_critical_paths.py, ensure all tests run in <10 seconds, target 100% of critical paths covered, validate with make smoke. Report coverage metrics when done.
```

**Expected Deliverables**:
- tests/smoke/test_critical_paths.py
- All tests complete in <10 seconds
- 100% critical path coverage
- Validation: `make smoke`

**Priority**: 🔴 HIGH

---

## SESSION 2: TEST-015 Performance Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write comprehensive performance tests per TEST-015.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-015, write performance tests for load testing, stress testing, benchmarks, memory profiling, create tests/performance/test_*.py, include metrics (latency p95, throughput, memory usage), validate MATRIZ targets (<250ms p95, 50+ ops/sec), validate with pytest tests/performance/ -v. Report metrics when done.
```

**Expected Deliverables**:
- tests/performance/test_*.py
- Load, stress, benchmark tests
- MATRIZ performance targets validated
- Metrics: p95 latency, throughput, memory

**Priority**: 🔴 HIGH

---

## SESSION 3: TEST-016 Candidate Consciousness Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write tests for candidate/consciousness/ per TEST-016.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-016, write tests for consciousness research modules in candidate/consciousness/, target 50%+ coverage (lighter coverage for experimental code), focus on core consciousness processing functions, validate with pytest tests/unit/candidate/consciousness/ -v --cov=candidate/consciousness. Report coverage metrics.
```

**Expected Deliverables**:
- tests/unit/candidate/consciousness/test_*.py
- 50%+ coverage (experimental code)
- Focus on core processing

**Priority**: 🟡 MEDIUM

---

## SESSION 4: TEST-017 Candidate Bio Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write tests for candidate/bio/ per TEST-017.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-017, write tests for bio-inspired adaptation modules in candidate/bio/, target 50%+ coverage, validate with pytest tests/unit/candidate/bio/ -v --cov=candidate/bio. Report coverage metrics.
```

**Expected Deliverables**:
- tests/unit/candidate/bio/test_*.py
- 50%+ coverage
- Bio-inspired adaptation focus

**Priority**: 🟡 MEDIUM

---

## SESSION 5: TEST-018 Candidate Quantum Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write tests for candidate/quantum/ per TEST-018.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-018, write tests for quantum-inspired algorithms in candidate/quantum/, target 50%+ coverage, validate with pytest tests/unit/candidate/quantum/ -v --cov=candidate/quantum. Report coverage metrics.
```

**Expected Deliverables**:
- tests/unit/candidate/quantum/test_*.py
- 50%+ coverage
- Quantum-inspired algorithm tests

**Priority**: 🟡 MEDIUM

---

## SESSION 6: TEST-019 Labs Memory Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write tests for labs/memory/ per TEST-019.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-019, write tests for memory system prototypes in labs/memory/, target 60%+ coverage, validate with pytest tests/unit/labs/memory/ -v --cov=labs/memory. Report coverage metrics.
```

**Expected Deliverables**:
- tests/unit/labs/memory/test_*.py
- 60%+ coverage
- Memory prototype tests

**Priority**: 🟡 MEDIUM

---

## SESSION 7: TEST-020 Labs Governance Tests

**Create new session at**: https://jules.google.com

**Prompt to paste**:
```
Write tests for labs/governance/ per TEST-020.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-020, write tests for governance and ethics modules in labs/governance/, target 60%+ coverage, validate with pytest tests/unit/labs/governance/ -v --cov=labs/governance. Report coverage metrics.
```

**Expected Deliverables**:
- tests/unit/labs/governance/test_*.py
- 60%+ coverage
- Governance & ethics focus

**Priority**: 🟡 MEDIUM

---

## 📋 Execution Plan

### Step 1: Review & Merge Completed PRs (~10 minutes)
```bash
# Review each PR
gh pr view 986
gh pr view 985
gh pr view 981
gh pr view 978

# Merge if tests pass
gh pr merge 986 --squash
gh pr merge 985 --squash
gh pr merge 981 --squash
gh pr merge 978 --squash
```

### Step 2: Create New Sessions (~10 minutes)

1. Go to: https://jules.google.com
2. Click "New Session"
3. Copy prompts from above (TEST-014 through TEST-020)
4. Create 7 new sessions
5. Jules will start working immediately

### Step 3: Monitor Progress (~ongoing)
```bash
# Check session status
python3 scripts/summarize_waiting_sessions.py

# List all sessions
python3 scripts/list_all_jules_sessions.py

# Check for new PRs
gh pr list --limit 10
```

---

## 🎯 Success Criteria

After completing these tasks:
- ✅ 4 completed PRs reviewed and merged
- ✅ 7 new sessions created and active
- ✅ Test coverage increases by 10-15%
- ✅ All critical paths have smoke tests
- ✅ Performance benchmarks established
- ✅ Experimental code (candidate/) has baseline coverage

---

## ⏱️ Time Estimates

- **PR Review & Merge**: 10 minutes
- **Create New Sessions**: 10 minutes
- **Jules Work Time**: 2-4 hours (automated)
- **PR Review (new PRs)**: 20 minutes later

**Total active time**: ~40 minutes spread across day

---

## 📊 Expected Impact

### Coverage Improvements:
- Current: ~30% overall
- After TEST-014/015: ~40% overall
- After TEST-016/017/018: candidate/ goes from 0% → 50%
- After TEST-019/020: labs/ goes from ~20% → 60%

### Test Suite Growth:
- Current: ~775 tests
- Expected: ~1000+ tests
- New smoke tests: 15-20 critical path tests
- New performance tests: 10-15 benchmark tests

---

## 🚀 Ready to Execute

**Start here**:
1. Review PR #986: https://github.com/LukhasAI/Lukhas/pull/986
2. Create TEST-014 session: https://jules.google.com

All prompts are ready to copy-paste from this file! ✅
