# Create New Jules Sessions (TEST-014 onwards)

**Go to**: https://jules.google.com
**Click**: "New Session" for each task below

Copy and paste these prompts exactly as shown:

---

## 🔴 SESSION 1: TEST-014 Smoke Tests (HIGH PRIORITY)

**Prompt to paste**:
```
Write comprehensive smoke tests for all critical paths per TEST-014.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-014, write smoke tests for system startup, API availability, core functionality, database connections, create tests/smoke/test_critical_paths.py, ensure all tests run in <10 seconds, target 100% of critical paths covered, validate with make smoke. Report coverage metrics when done.
```

---

## 🔴 SESSION 2: TEST-015 Performance Tests (HIGH PRIORITY)

**Prompt to paste**:
```
Write comprehensive performance tests per TEST-015.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-015, write performance tests for load testing, stress testing, benchmarks, memory profiling, create tests/performance/test_*.py, include metrics (latency p95, throughput, memory usage), validate MATRIZ targets (<250ms p95, 50+ ops/sec), validate with pytest tests/performance/ -v. Report metrics when done.
```

---

## 🟡 SESSION 3: TEST-016 Candidate Consciousness (MEDIUM)

**Prompt to paste**:
```
Write tests for candidate/consciousness/ per TEST-016.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-016, write tests for consciousness research modules in candidate/consciousness/, target 50%+ coverage (lighter coverage for experimental code), focus on core consciousness processing functions, validate with pytest tests/unit/candidate/consciousness/ -v --cov=candidate/consciousness. Report coverage metrics.
```

---

## 🟡 SESSION 4: TEST-017 Candidate Bio (MEDIUM)

**Prompt to paste**:
```
Write tests for candidate/bio/ per TEST-017.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-017, write tests for bio-inspired adaptation modules in candidate/bio/, target 50%+ coverage, validate with pytest tests/unit/candidate/bio/ -v --cov=candidate/bio. Report coverage metrics.
```

---

## 🟡 SESSION 5: TEST-018 Candidate Quantum (MEDIUM)

**Prompt to paste**:
```
Write tests for candidate/quantum/ per TEST-018.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-018, write tests for quantum-inspired algorithms in candidate/quantum/, target 50%+ coverage, validate with pytest tests/unit/candidate/quantum/ -v --cov=candidate/quantum. Report coverage metrics.
```

---

## 🟡 SESSION 6: TEST-019 Labs Memory (MEDIUM)

**Prompt to paste**:
```
Write tests for labs/memory/ per TEST-019.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-019, write tests for memory system prototypes in labs/memory/, target 60%+ coverage, validate with pytest tests/unit/labs/memory/ -v --cov=labs/memory. Report coverage metrics.
```

---

## 🟡 SESSION 7: TEST-020 Labs Governance (MEDIUM)

**Prompt to paste**:
```
Write tests for labs/governance/ per TEST-020.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-020, write tests for governance and ethics modules in labs/governance/, target 60%+ coverage, validate with pytest tests/unit/labs/governance/ -v --cov=labs/governance. Report coverage metrics.
```

---

## ✅ Quick Checklist

- [ ] Created SESSION 1: TEST-014 Smoke Tests
- [ ] Created SESSION 2: TEST-015 Performance Tests
- [ ] Created SESSION 3: TEST-016 Candidate Consciousness
- [ ] Created SESSION 4: TEST-017 Candidate Bio
- [ ] Created SESSION 5: TEST-018 Candidate Quantum
- [ ] Created SESSION 6: TEST-019 Labs Memory
- [ ] Created SESSION 7: TEST-020 Labs Governance

**Time estimate**: 10 minutes to create all 7 sessions

**After creating, monitor with**:
```bash
python3 scripts/list_all_jules_sessions.py
```
