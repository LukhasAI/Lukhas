# Quick Test Assignment Commands for Jules AI

**Purpose**: One-liner prompts to instantly assign test writing tasks to Jules AI

**Usage**: Copy-paste these commands directly to Jules. Replace `{TEST_NUMBER}` with the specific task.

---

## 🎯 Universal Test Assignment Command

### Standard Template

```
Write comprehensive tests for {MODULE_NAME} per {TEST_NUMBER}.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/TEST_ASSIGNMENT_REPORT.md, find {TEST_NUMBER}, read all context files listed in "Agent Context", read all source files in "Files to Test", write tests following "Test Strategy" examples, target {COVERAGE}%+ coverage, validate with commands in "Validation" section, commit with T4 format including "Closes: {TEST_NUMBER}". Report coverage improvement metrics when done.
```

---

## 🔴 HIGH PRIORITY Test Assignments (TEST-001 through TEST-015)

### TEST-001: Core Orchestration Tests

```
Write comprehensive tests for core orchestration module per TEST-001.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/TEST_ASSIGNMENT_REPORT.md TEST-001, read /Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me and /Users/agi_dev/LOCAL-REPOS/Lukhas/core/orchestration/ context, write tests for all 11 files (orchestrator.py, agent.py, brain.py, flow.py, planner.py, prompt.py, react.py, task.py, tool.py, workflow.py, worker.py), create tests/unit/core/orchestration/test_*.py files, target 75%+ coverage, validate with pytest tests/unit/core/orchestration/ -v --cov=core/orchestration, commit with T4 format. Report coverage: 0% → X%.
```

---

### TEST-002: Core Interfaces Tests

```
Write comprehensive tests for core interfaces per TEST-002.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-002, write tests for all 12 interface files (agents, consciousness, database, event_bus, identity, language_model, logger, memory, monitoring, realtime, storage, task_queue), focus on interface contracts and implementations, create tests/unit/core/interfaces/test_*.py, target 80%+ coverage, validate with pytest tests/unit/core/interfaces/ -v --cov=core/interfaces. Report coverage metrics.
```

---

### TEST-003: LUKHAS Identity System Tests (SECURITY)

```
Write comprehensive SECURITY-focused tests for lukhas identity per TEST-003.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-003, read /Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/identity/claude.me, write tests for token_types.py, webauthn_credential.py, webauthn_verify.py, include token validation, expiration, signature verification, tampering detection, edge cases (malformed, empty, null), create tests/unit/lukhas/identity/test_*.py, target 80%+ coverage, run make security-scan after tests, validate with pytest tests/unit/lukhas/identity/ -v --cov=lukhas/identity. Report security validation results.
```

---

### TEST-004: LUKHAS Memory System Tests (Vector Indexing)

```
Write comprehensive tests for lukhas memory including NEW vector indexing per TEST-004.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-004, write tests for lukhas/memory/index.py (EmbeddingIndex, IndexManager from PR #963), include vector addition, search accuracy, persistence, edge cases (empty index, invalid dimensions), performance tests (1000+ vectors), create tests/unit/lukhas/memory/test_*.py, target 80%+ coverage, should unblock 17 skipped tests from ISSUE-021, validate with pytest tests/unit/lukhas/memory/ -v --cov=lukhas/memory. Report coverage: 50% → X%.
```

---

### TEST-005: Core Blockchain Tests

```
Write comprehensive tests for core blockchain per TEST-005.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-005, write tests for core/blockchain/state.py and utils.py, include blockchain state initialization, block addition, chain validation, immutability tests, consensus mechanisms, create tests/unit/core/blockchain/test_*.py, target 75%+ coverage, validate with pytest tests/unit/core/blockchain/ -v --cov=core/blockchain. Report coverage: 0% → X%.
```

---

### TEST-006: Core Emotion Tests

```
Write comprehensive tests for core emotion per TEST-006.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-006, write tests for core/emotion/emotion_models.py, include emotion state modeling, transitions, intensity calculations, create tests/unit/core/emotion/test_*.py, target 75%+ coverage, validate with pytest tests/unit/core/emotion/ -v --cov=core/emotion.
```

---

### TEST-007: API Endpoints Integration Tests

```
Write comprehensive integration tests for all API endpoints per TEST-007.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-007, write tests for /v1/models, /v1/chat/completions, /v1/embeddings, /v1/dreams (NEW from PR #965), /healthz, /readyz, /metrics endpoints, use FastAPI TestClient, include auth requirements, error cases, OpenAI compatibility, streaming responses, create tests/integration/api/test_api_endpoints.py, target 85%+ coverage, validate with pytest tests/integration/api/ -v --cov=serve. Report coverage: 40% → X%.
```

---

### TEST-008: Fix Collection Errors (CRITICAL)

```
Fix all 223 pytest collection errors per TEST-008.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-008, run pytest --co -q 2>&1 | grep "ERROR" to identify all errors, group by type (ModuleNotFoundError, RecursionError, ImportError), fix each category systematically: add missing __init__.py, fix circular imports, update import paths, skip broken tests with pytest.mark.skip, validate with pytest --co -q (must show 0 errors), commit each category separately with descriptive messages. Report: 223 errors → 0 errors.
```

**Priority**: CRITICAL - Must be done FIRST before accurate coverage measurement

---

### TEST-009: Core Memory Tests

```
Write comprehensive tests for core memory per TEST-009.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-009, write tests for 5 files in core/memory/, include memory storage, retrieval, search, persistence, create tests/unit/core/memory/test_*.py, target 75%+ coverage, validate with pytest tests/unit/core/memory/ -v --cov=core/memory.
```

---

### TEST-010: Core Quantum Financial Tests

```
Write comprehensive tests for core quantum_financial per TEST-010.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-010, write tests for 3 files in core/quantum_financial/, include quantum-inspired algorithms, financial modeling, create tests/unit/core/quantum_financial/test_*.py, target 75%+ coverage, validate with pytest tests/unit/core/quantum_financial/ -v --cov=core/quantum_financial.
```

---

### TEST-011: Core Colonies Tests

```
Write comprehensive tests for core colonies per TEST-011.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-011, write tests for 5 files in core/colonies/, include agent colonies, coordination, task distribution, create tests/unit/core/colonies/test_*.py, target 75%+ coverage, validate with pytest tests/unit/core/colonies/ -v --cov=core/colonies.
```

---

### TEST-012: Serve API Complete Coverage

```
Write comprehensive tests for serve API achieving full coverage per TEST-012.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-012, write tests for serve/main.py and all routers, include all endpoints, middleware, error handling, streaming, WebSocket support, create tests/integration/serve/test_*.py, target 90%+ coverage, validate with pytest tests/integration/serve/ -v --cov=serve.
```

---

### TEST-013: Integration Tests (Cross-Component)

```
Write comprehensive integration tests per TEST-013.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-013, write tests validating workflows across multiple components (MATRIZ + Memory, Identity + API, Orchestration + Consciousness), create tests/integration/test_cross_component.py, target 60%+ coverage of critical paths, validate with pytest tests/integration/ -v.
```

---

### TEST-014: Smoke Tests (All Critical Paths)

```
Write comprehensive smoke tests for all critical paths per TEST-014.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-014, write smoke tests for system startup, API availability, core functionality, database connections, create tests/smoke/test_critical_paths.py, ensure all tests run in <10 seconds, target 100% of critical paths covered, validate with make smoke.
```

---

### TEST-015: Performance Tests

```
Write comprehensive performance tests per TEST-015.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-015, write performance tests for load testing, stress testing, benchmarks, memory profiling, create tests/performance/test_*.py, include metrics (latency p95, throughput, memory usage), validate MATRIZ targets (<250ms p95, 50+ ops/sec), validate with pytest tests/performance/ -v.
```

---

## 🟡 MEDIUM PRIORITY Test Assignments (TEST-016 through TEST-035)

### TEST-016: Candidate Consciousness Tests

```
Write tests for candidate/consciousness/ per TEST-016.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-016, write tests for consciousness research modules, target 50%+ coverage (lighter coverage for experimental code), validate with pytest tests/unit/candidate/consciousness/ -v --cov=candidate/consciousness.
```

---

### TEST-017: Candidate Bio Tests

```
Write tests for candidate/bio/ per TEST-017.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-017, write tests for bio-inspired adaptation modules, target 50%+ coverage, validate with pytest tests/unit/candidate/bio/ -v --cov=candidate/bio.
```

---

### TEST-018: Candidate Quantum Tests

```
Write tests for candidate/quantum/ per TEST-018.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-018, write tests for quantum-inspired algorithms, target 50%+ coverage, validate with pytest tests/unit/candidate/quantum/ -v --cov=candidate/quantum.
```

---

### TEST-019: Labs Memory Tests

```
Write tests for labs/memory/ per TEST-019.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-019, write tests for memory system prototypes, target 60%+ coverage, validate with pytest tests/unit/labs/memory/ -v --cov=labs/memory.
```

---

### TEST-020: Labs Governance Tests

```
Write tests for labs/governance/ per TEST-020.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-020, write tests for governance and ethics modules, target 60%+ coverage, validate with pytest tests/unit/labs/governance/ -v --cov=labs/governance.
```

---

### TEST-021 through TEST-035: Additional Medium Priority

(See TEST_ASSIGNMENT_REPORT.md for complete list)

---

## 🟢 LOW PRIORITY Test Assignments (TEST-036 through TEST-050)

### TEST-036: Legacy Code Tests

```
Write tests for legacy modules per TEST-036.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-036, write minimal tests for deprecated/legacy code, target 30%+ coverage (lower priority), validate with pytest tests/unit/legacy/ -v.
```

---

### TEST-037: Example Code Tests

```
Write tests for example code per TEST-037.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-037, write tests validating examples work correctly, create tests/examples/test_*.py, ensure all examples run without errors.
```

---

### TEST-038: Documentation Tests

```
Write documentation tests per TEST-038.

Context: Read TEST_ASSIGNMENT_REPORT.md TEST-038, write tests ensuring code examples in docs work, use doctest or manual tests, validate with pytest --doctest-modules.
```

---

## 🚀 Batch Assignment Commands

### Assign All HIGH Priority Tests

```
Complete all HIGH priority test tasks (TEST-001 through TEST-015).

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/TEST_ASSIGNMENT_REPORT.md, work through all 15 HIGH priority tasks sequentially, start with TEST-008 (fix collection errors) FIRST, then tackle TEST-001 through TEST-015 in order, for each task: read context files, write comprehensive tests, achieve coverage targets (75-85%), validate with pytest, commit with T4 format, report progress after each task. Target: achieve 60%+ overall coverage after completing all HIGH tasks.
```

---

### Assign Week 1 Foundation Tasks

```
Complete Week 1 foundation tasks per TEST_ASSIGNMENT_REPORT.md.

Context: Read TEST_ASSIGNMENT_REPORT.md "Getting Started Guide for Jules" Week 1 section, fix all collection errors (TEST-008), write tests for 2 high-priority modules (recommend TEST-001 and TEST-003), validate coverage improvements, report final metrics: collection errors (223 → 0), coverage (30% → X%).
```

---

## 📋 Assignment with Custom Parameters

### Template for Custom Module

```
Write comprehensive tests for {MODULE_PATH}.

Context: Read /Users/agi_dev/LOCAL-REPOS/Lukhas/TEST_ASSIGNMENT_REPORT.md, find the relevant TEST-XXX section, read {MODULE_PATH}/ source files, read relevant context files, write tests/unit/{module}/test_*.py, include initialization/happy-path/error/edge case tests, target {COVERAGE}%+ coverage, validate with pytest tests/unit/{module}/ -v --cov={module}, commit with T4 format. Report coverage metrics.
```

**Usage**: Fill in `{MODULE_PATH}` and `{COVERAGE}` with your values.

---

## 🔧 Troubleshooting Assignments

### If Tests Are Failing

```
Debug failing tests in {MODULE}.

Context: Run pytest tests/unit/{module}/ -v, read error messages, check if module behavior was misunderstood, verify imports are correct, check if external dependencies need mocking, re-read /Users/agi_dev/LOCAL-REPOS/Lukhas/{module}/claude.me for architectural insights, fix tests, re-run validation.
```

---

### If Coverage Target Not Met

```
Improve coverage for {MODULE} from {X}% to {Y}%.

Context: Run pytest tests/unit/{module}/ -v --cov={module} --cov-report=term-missing, identify uncovered lines, write additional tests for uncovered code paths, focus on error handling and edge cases, validate coverage improved, commit with updated metrics.
```

---

## 📊 Progress Tracking Commands

### Check Overall Progress

```
Report current test coverage progress.

Context: Run pytest tests/ -v --cov=. --cov-report=term, report overall coverage %, lukhas/ coverage %, core/ coverage %, collection errors count (pytest --co -q 2>&1 | grep -c "ERROR"), passing tests count, compare to targets (75% overall, 80% lukhas/, 65% core/, 0 collection errors).
```

---

### Validate All Tests

```
Validate all tests are passing and coverage targets met.

Context: Run make test to execute full test suite, run make smoke for quick validation, check coverage with pytest --cov=. --cov-report=term, verify no collection errors with pytest --co -q, report: total tests, passing %, coverage %, issues found.
```

---

## 💡 Pro Tips for Jules

1. **Always start with TEST-008** (fix collection errors) - this unblocks accurate coverage measurement

2. **Read context files FIRST** - saves time by understanding architecture before coding

3. **Use existing tests as templates** - copy patterns from tests/unit/core/test_agent_tracer.py

4. **Write tests in batches** - do all tests for one file, then validate, then commit (don't commit after every test)

5. **Mock external dependencies** - keeps tests fast and reliable

6. **Follow AAA pattern** - Arrange, Act, Assert - makes tests readable

7. **Commit frequently** - one commit per module/file is fine

8. **Report metrics** - always include coverage improvement numbers (X% → Y%)

---

## 📚 Additional Resources

- **Full Context**: TEST_ASSIGNMENT_REPORT.md (696 lines, 50+ tasks)
- **Detailed Guide**: AGENT_TEST_TEMPLATE.md (comprehensive 8-step process)
- **Bug Tasks**: bug_report.md (25 functionality issues)
- **Test Examples**: /Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/core/test_agent_tracer.py

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-11-06
**For**: Jules AI Agent (instant task assignment)
**Location**: `/Users/agi_dev/LOCAL-REPOS/Lukhas-test-audit/QUICK_TEST_ASSIGN.md`
**Usage**: Copy-paste commands directly to Jules - no modification needed except {placeholders}
