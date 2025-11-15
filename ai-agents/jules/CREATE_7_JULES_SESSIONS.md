# Create 7 Jules Test Sessions

**Go to**: https://jules.google.com

For each session below:
1. Click "New Session"
2. Copy the prompt
3. Paste and click "Create"
4. Check the box when done

---

## SESSION 1: TEST-014 Smoke Tests (HIGH PRIORITY)

**Prompt**:
```
Write comprehensive smoke tests for all critical paths per TEST-014.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-014, write smoke tests for system startup, API availability, core functionality, database connections, create tests/smoke/test_critical_paths.py, ensure all tests run in <10 seconds, target 100% of critical paths covered, validate with make smoke. Report coverage metrics when done.
```

- [ ] Created

---

## SESSION 2: TEST-015 Performance Tests (HIGH PRIORITY)

**Prompt**:
```
Write comprehensive performance tests per TEST-015.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-015, write performance tests for load testing, stress testing, benchmarks, memory profiling, create tests/performance/test_*.py, include metrics (latency p95, throughput, memory usage), validate MATRIZ targets (<250ms p95, 50+ ops/sec), validate with pytest tests/performance/ -v. Report metrics when done.
```

- [ ] Created

---

## SESSION 3: TEST-016 Candidate Consciousness (MEDIUM)

**Prompt**:
```
Write tests for candidate/consciousness/ per TEST-016.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-016, write tests for consciousness research modules in candidate/consciousness/, target 50%+ coverage (lighter coverage for experimental code), focus on core consciousness processing functions, validate with pytest tests/unit/candidate/consciousness/ -v --cov=candidate/consciousness. Report coverage metrics.
```

- [ ] Created

---

## SESSION 4: TEST-017 Candidate Bio (MEDIUM)

**Prompt**:
```
Write tests for candidate/bio/ per TEST-017.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-017, write tests for bio-inspired adaptation modules in candidate/bio/, target 50%+ coverage, validate with pytest tests/unit/candidate/bio/ -v --cov=candidate/bio. Report coverage metrics.
```

- [ ] Created

---

## SESSION 5: TEST-018 Candidate Quantum (MEDIUM)

**Prompt**:
```
Write tests for candidate/quantum/ per TEST-018.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-018, write tests for quantum-inspired algorithms in candidate/quantum/, target 50%+ coverage, validate with pytest tests/unit/candidate/quantum/ -v --cov=candidate/quantum. Report coverage metrics.
```

- [ ] Created

---

## SESSION 6: TEST-019 Labs Memory (MEDIUM)

**Prompt**:
```
Write tests for labs/memory/ per TEST-019.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-019, write tests for memory system prototypes in labs/memory/, target 60%+ coverage, validate with pytest tests/unit/labs/memory/ -v --cov=labs/memory. Report coverage metrics.
```

- [ ] Created

---

## SESSION 7: TEST-020 Labs Governance (MEDIUM)

**Prompt**:
```
Write tests for labs/governance/ per TEST-020.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-020, write tests for governance and ethics modules in labs/governance/, target 60%+ coverage, validate with pytest tests/unit/labs/governance/ -v --cov=labs/governance. Report coverage metrics.
```

- [ ] Created

---

## After Creating All Sessions

Run this to verify:
```bash
python3 scripts/list_all_jules_sessions.py
```

You should see 7 new "ACTIVE" sessions.

---

## Expected Results

- 7 new sessions created in ~10 minutes
- Jules starts working immediately
- 7 new PRs in 2-4 hours
- Coverage increases: 38% → 48%+
- ~100+ new tests added
