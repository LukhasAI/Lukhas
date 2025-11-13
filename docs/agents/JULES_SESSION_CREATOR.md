# Jules Session Creator - Step by Step

**Go to**: https://jules.google.com

Follow these steps for each session below. Check off as you create them.

---

## ⚡ Quick Instructions

For each session:
1. Click "New Session" button
2. Copy the prompt below
3. Paste into Jules
4. Click "Create" or "Start"
5. Check the box ✅

---

## 🔴 HIGH PRIORITY (Create These First)

### [ ] SESSION 1: TEST-014 Smoke Tests

**Copy this prompt**:
```
Write comprehensive smoke tests for all critical paths per TEST-014.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-014, write smoke tests for system startup, API availability, core functionality, database connections, create tests/smoke/test_critical_paths.py, ensure all tests run in <10 seconds, target 100% of critical paths covered, validate with make smoke. Report coverage metrics when done.
```

---

### [ ] SESSION 2: TEST-015 Performance Tests

**Copy this prompt**:
```
Write comprehensive performance tests per TEST-015.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-015, write performance tests for load testing, stress testing, benchmarks, memory profiling, create tests/performance/test_*.py, include metrics (latency p95, throughput, memory usage), validate MATRIZ targets (<250ms p95, 50+ ops/sec), validate with pytest tests/performance/ -v. Report metrics when done.
```

---

## 🟡 MEDIUM PRIORITY (Create After High Priority)

### [ ] SESSION 3: TEST-016 Candidate Consciousness

**Copy this prompt**:
```
Write tests for candidate/consciousness/ per TEST-016.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-016, write tests for consciousness research modules in candidate/consciousness/, target 50%+ coverage (lighter coverage for experimental code), focus on core consciousness processing functions, validate with pytest tests/unit/candidate/consciousness/ -v --cov=candidate/consciousness. Report coverage metrics.
```

---

### [ ] SESSION 4: TEST-017 Candidate Bio

**Copy this prompt**:
```
Write tests for candidate/bio/ per TEST-017.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-017, write tests for bio-inspired adaptation modules in candidate/bio/, target 50%+ coverage, validate with pytest tests/unit/candidate/bio/ -v --cov=candidate/bio. Report coverage metrics.
```

---

### [ ] SESSION 5: TEST-018 Candidate Quantum

**Copy this prompt**:
```
Write tests for candidate/quantum/ per TEST-018.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-018, write tests for quantum-inspired algorithms in candidate/quantum/, target 50%+ coverage, validate with pytest tests/unit/candidate/quantum/ -v --cov=candidate/quantum. Report coverage metrics.
```

---

### [ ] SESSION 6: TEST-019 Labs Memory

**Copy this prompt**:
```
Write tests for labs/memory/ per TEST-019.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-019, write tests for memory system prototypes in labs/memory/, target 60%+ coverage, validate with pytest tests/unit/labs/memory/ -v --cov=labs/memory. Report coverage metrics.
```

---

### [ ] SESSION 7: TEST-020 Labs Governance

**Copy this prompt**:
```
Write tests for labs/governance/ per TEST-020.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/testing/TEST_ASSIGNMENT_REPORT.md TEST-020, write tests for governance and ethics modules in labs/governance/, target 60%+ coverage, validate with pytest tests/unit/labs/governance/ -v --cov=labs/governance. Report coverage metrics.
```

---

## ✅ After Creating All Sessions

Run this to verify they were created:
```bash
python3 scripts/list_all_jules_sessions.py
```

You should see 7 new "ACTIVE" sessions.

---

## 🎯 What Happens Next

- Jules will start working on all 7 tasks immediately
- Each task takes 30 minutes - 2 hours
- Jules will create PRs automatically
- You'll get 7 new PRs to review in 2-4 hours

---

## 📊 Expected Results

**In 2-4 hours**:
- 7 new PRs created
- Coverage increases: 38% → 48%+
- ~100+ new tests added
- Critical paths fully smoke tested
- Performance benchmarks established

---

## 🚀 START HERE

1. Open: https://jules.google.com
2. Click: "New Session"
3. Copy first prompt above
4. Paste and create
5. Repeat for all 7 sessions

**Time needed**: ~10 minutes for all 7

Let's go! 🎉
