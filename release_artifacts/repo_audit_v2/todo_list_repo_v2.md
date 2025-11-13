# Repository Audit V2 - Microtask List
**Generated:** 2025-11-03  
**Source:** Comprehensive repo audit findings  
**Priority Levels:** P0 (Critical) → P1 (High) → P2 (Medium)

---

## 🔴 P0 - Critical Issues (Complete First)

### Security & Dependencies

#### TASK-001: Upgrade urllib3 to Fix CVE-2025-50181 [P0]
**Effort:** 15-30 minutes  
**Dependencies:** None  
**Description:** Upgrade urllib3 from 1.26.20 to >=2.5.0 to fix SSRF vulnerability  
**Steps:**
1. Update requirements.txt or pyproject.toml: `urllib3>=2.5.0`
2. Run `pip install --upgrade urllib3` in .venv
3. Run smoke tests: `make smoke`
4. Commit with message: `security(deps): upgrade urllib3 to 2.5.0 for CVE-2025-50181`

**Verification:** `pip show urllib3` should show version >=2.5.0

**Artifact Reference:** [release_artifacts/repo_audit_v2/security/pip_audit_summary.txt](release_artifacts/repo_audit_v2/security/pip_audit_summary.txt)

---

### Testing Infrastructure

#### TASK-002: Investigate API Endpoint Test Failures (test_models.py) [P0]
**Effort:** 2-3 hours  
**Dependencies:** None  
**Description:** 21 tests in test_models.py failing with 401/assertion errors  
**Steps:**
1. Review test_models.py test setup and fixtures
2. Check if API server needs to be started for tests
3. Verify authentication tokens/credentials in test environment
4. Check MATRIZ model registration in test environment
5. Fix authentication setup or test fixtures
6. Re-run: `pytest tests/smoke/test_models.py -v`

**Verification:** All 21 tests should pass

**Artifact Reference:** [release_artifacts/repo_audit_v2/tests/test_results_summary.txt](release_artifacts/repo_audit_v2/tests/test_results_summary.txt)

---

#### TASK-003: Investigate Response Validation Test Failures (test_responses.py) [P0]
**Effort:** 2-3 hours  
**Dependencies:** TASK-002  
**Description:** 18 tests in test_responses.py failing with assertion/KeyError  
**Steps:**
1. Review test_responses.py test expectations
2. Check if response format changed vs test expectations
3. Verify API response schemas match test assertions
4. Fix response validation logic or update tests
5. Re-run: `pytest tests/smoke/test_responses.py -v`

**Verification:** All 18 tests should pass

---

#### TASK-004: Fix MATRIZ Integration Test Failures [P0]
**Effort:** 3-4 hours  
**Dependencies:** None  
**Description:** 10 MATRIZ tests failing in test_matriz_integration.py  
**Steps:**
1. Check if MATRIZ engine is properly initialized in test environment
2. Verify matriz/ components are importable
3. Check for missing MATRIZ dependencies or configuration
4. Review symbolic DNA processing setup
5. Fix MATRIZ initialization or test environment
6. Re-run: `pytest tests/smoke/test_matriz_integration.py -v`

**Verification:** All MATRIZ integration tests should pass

---

#### TASK-005: Fix Rate Limiting Test Failures [P0]
**Effort:** 1-2 hours  
**Dependencies:** TASK-002  
**Description:** 5 rate limiting tests failing  
**Steps:**
1. Review rate limiting configuration in test environment
2. Check if Redis or rate limiter backend is available
3. Verify tenant isolation logic
4. Fix rate limiter initialization or test setup
5. Re-run: `pytest tests/smoke/test_rate_limiting.py -v`

**Verification:** All 5 rate limiting tests should pass

---

#### TASK-006: Fix Streaming Response Test Failures [P0]
**Effort:** 1-2 hours  
**Dependencies:** TASK-002, TASK-003  
**Description:** 5 streaming tests failing in test_responses_stream.py  
**Steps:**
1. Review SSE (Server-Sent Events) protocol implementation
2. Check if streaming endpoints are properly configured
3. Verify backpressure handling for large payloads
4. Fix streaming response logic or test expectations
5. Re-run: `pytest tests/smoke/test_responses_stream.py -v`

**Verification:** All streaming tests should pass

---

#### TASK-007: Investigate Remaining Smoke Test Failures [P0]
**Effort:** 2-3 hours  
**Dependencies:** TASK-002 through TASK-006  
**Description:** Fix remaining ~43 smoke test failures  
**Steps:**
1. Group remaining failures by category (metrics, security, tracing, OpenAI)
2. Investigate each category systematically
3. Fix configuration, imports, or test setup issues
4. Re-run all smoke tests: `make smoke`

**Verification:** <5% failure rate in smoke tests (target: 95%+ pass rate)

---

### Code Quality - Import Structure

#### TASK-008: Fix E402 Violations in lukhas/ (Priority Module) [P0]
**Effort:** 3-4 hours  
**Dependencies:** None  
**Description:** Fix module-import-not-at-top-of-file in production lane  
**Steps:**
1. Run: `ruff check lukhas/ --select E402`
2. Review each E402 violation
3. Move imports to top of file (after module docstring)
4. Handle conditional imports properly (use TYPE_CHECKING)
5. Test affected modules: `pytest tests/unit/lukhas/`
6. Commit changes per subdirectory

**Verification:** `ruff check lukhas/ --select E402` returns 0 violations

---

#### TASK-009: Fix E402 Violations in matriz/ (Priority Module) [P0]
**Effort:** 2-3 hours  
**Dependencies:** None  
**Description:** Fix module-import-not-at-top-of-file in MATRIZ engine  
**Steps:**
1. Run: `ruff check matriz/ --select E402`
2. Review each E402 violation
3. Move imports to top of file
4. Test MATRIZ functionality: `pytest tests/smoke/test_matriz_integration.py`
5. Commit changes

**Verification:** `ruff check matriz/ --select E402` returns 0 violations

---

#### TASK-010: Fix E402 Violations in core/ (Priority Module) [P0]
**Effort:** 2-3 hours  
**Dependencies:** None  
**Description:** Fix module-import-not-at-top-of-file in integration lane  
**Steps:**
1. Run: `ruff check core/ --select E402`
2. Review each E402 violation
3. Move imports to top of file
4. Test core functionality: `pytest tests/unit/core/`
5. Commit changes

**Verification:** `ruff check core/ --select E402` returns 0 violations

---

## 🟡 P1 - High Priority Issues (Address This Sprint)

### Code Quality - Undefined Names

#### TASK-011: Audit and Fix Undefined Name References (F821) [P1]
**Effort:** 4-6 hours  
**Dependencies:** None  
**Description:** Fix 622 undefined name references  
**Steps:**
1. Run: `ruff check . --select F821 --exclude='.venv,archive,quarantine,products'`
2. Export results: `ruff check . --select F821 --output-format=json > f821_audit.json`
3. Group by module/pattern
4. Fix broken imports, typos, missing variables
5. Test affected modules
6. Commit fixes in batches (max 50 files per commit)

**Verification:** `ruff check . --select F821` returns <50 violations (90% reduction)

---

#### TASK-012: Investigate High-Frequency F821 Patterns [P1]
**Effort:** 2-3 hours  
**Dependencies:** TASK-011  
**Description:** Identify and fix systematic undefined name issues  
**Steps:**
1. Analyze f821_audit.json for common patterns
2. Check for missing `from __future__ import annotations`
3. Check for circular import issues
4. Document findings
5. Create targeted fixes

**Verification:** Pattern documentation in release_artifacts/repo_audit_v2/quality/f821_patterns.md

---

### Testing - Coverage

#### TASK-013: Review and Enable Skipped Tests [P1]
**Effort:** 3-4 hours  
**Dependencies:** TASK-007  
**Description:** Reduce 74 skipped tests to <20  
**Steps:**
1. Run: `pytest --collect-only -m skip` to list all skipped tests
2. Review skip reasons (decorators, markers)
3. Identify tests that can be re-enabled
4. Fix blocking issues (missing dependencies, environment setup)
5. Re-enable tests incrementally
6. Re-run test suite

**Verification:** <20 skipped tests (target: 94%+ active test rate)

---

#### TASK-014: Add Coverage Threshold to pyproject.toml [P1]
**Effort:** 30 minutes  
**Dependencies:** TASK-007, TASK-013  
**Description:** Enforce minimum test coverage in CI  
**Steps:**
1. Check current coverage: `pytest --cov --cov-report=term`
2. Set realistic threshold in pyproject.toml: `fail_under = 50`
3. Add coverage reporting to CI workflows
4. Document coverage policy in docs/development/

**Verification:** CI fails on coverage drop below threshold

---

#### TASK-015: Implement 3x Flaky Test Detection [P1]
**Effort:** 1-2 hours  
**Dependencies:** TASK-007  
**Description:** Identify non-deterministic tests  
**Steps:**
1. Run: `pytest --count=3` (requires pytest-repeat or custom script)
2. Identify tests with inconsistent results
3. Document flaky tests
4. Create issues for each flaky test
5. Add xfail markers temporarily

**Verification:** Flaky test report in release_artifacts/repo_audit_v2/tests/flaky_tests.txt

---

### Code Quality - Modernization

#### TASK-016: Fix Deprecated Import Patterns (UP035) [P1]
**Effort:** 2-3 hours  
**Dependencies:** None  
**Description:** Modernize 1,350 deprecated imports  
**Steps:**
1. Run: `ruff check . --select UP035 --fix --unsafe-fixes`
2. Review auto-fixes
3. Run tests: `pytest tests/smoke/`
4. Commit changes: `refactor(imports): modernize deprecated import patterns (UP035)`

**Verification:** `ruff check . --select UP035` returns 0 violations

---

#### TASK-017: Modernize Type Annotations (UP045) [P1]
**Effort:** 2-3 hours  
**Dependencies:** None  
**Description:** Convert 1,109 old-style Optional to PEP 604 syntax  
**Steps:**
1. Run: `ruff check . --select UP045 --fix`
2. Review auto-fixes (Optional[X] → X | None)
3. Run type checking: `mypy lukhas/ matriz/ core/`
4. Commit changes: `refactor(types): modernize to PEP 604 union syntax (UP045)`

**Verification:** `ruff check . --select UP045` returns 0 violations

---

### Async Code Quality

#### TASK-018: Audit Asyncio Dangling Tasks (RUF006) [P1]
**Effort:** 4-6 hours  
**Dependencies:** None  
**Description:** Fix 268 asyncio dangling task warnings  
**Steps:**
1. Run: `ruff check . --select RUF006`
2. Identify high-risk patterns (fire-and-forget tasks)
3. Add task tracking with task groups or task registry
4. Ensure proper cleanup in finally blocks
5. Add structured concurrency patterns
6. Test async code paths

**Verification:** `ruff check . --select RUF006` returns <50 violations (80% reduction)

---

#### TASK-019: Implement Task Monitoring for Async Operations [P1]
**Effort:** 3-4 hours  
**Dependencies:** TASK-018  
**Description:** Add observability for async task lifecycle  
**Steps:**
1. Create AsyncTaskManager utility
2. Add task registration on creation
3. Add task cleanup monitoring
4. Log warnings for dangling tasks
5. Integrate with existing observability stack
6. Document async patterns in docs/

**Verification:** Task manager integrated in lukhas/core/

---

## 🟢 P2 - Medium Priority Issues (Next Sprint)

### Code Quality - Auto-Fixes

#### TASK-020: Fix Unsorted Imports (I001) [P2]
**Effort:** 30 minutes  
**Dependencies:** TASK-008, TASK-009, TASK-010  
**Description:** Auto-fix 244 unsorted import violations  
**Steps:**
1. Run: `ruff check . --select I001 --fix`
2. Review changes
3. Commit: `style(imports): sort imports with ruff auto-fix`

**Verification:** `ruff check . --select I001` returns 0 violations

---

#### TASK-021: Fix Blank Line Whitespace (W293) [P2]
**Effort:** 15 minutes  
**Dependencies:** None  
**Description:** Auto-fix 178 blank-line-with-whitespace violations  
**Steps:**
1. Run: `ruff check . --select W293 --fix`
2. Commit: `style: remove trailing whitespace on blank lines (W293)`

**Verification:** `ruff check . --select W293` returns 0 violations

---

#### TASK-022: Fix Quoted Annotations (UP037) [P2]
**Effort:** 30 minutes  
**Dependencies:** None  
**Description:** Auto-fix 48 quoted annotation violations  
**Steps:**
1. Run: `ruff check . --select UP037 --fix`
2. Commit: `style(types): remove unnecessary quoted annotations (UP037)`

**Verification:** `ruff check . --select UP037` returns 0 violations

---

#### TASK-023: Fix Redundant Open Modes (UP015) [P2]
**Effort:** 15 minutes  
**Dependencies:** None  
**Description:** Auto-fix 11 redundant open mode violations  
**Steps:**
1. Run: `ruff check . --select UP015 --fix`
2. Commit: `style: remove redundant file open modes (UP015)`

**Verification:** `ruff check . --select UP015` returns 0 violations

---

#### TASK-024: Fix Unsorted Dunder All (RUF022) [P2]
**Effort:** 20 minutes  
**Dependencies:** None  
**Description:** Auto-fix 44 unsorted __all__ declarations  
**Steps:**
1. Run: `ruff check . --select RUF022 --fix`
2. Commit: `style: sort __all__ declarations (RUF022)`

**Verification:** `ruff check . --select RUF022` returns 0 violations

---

#### TASK-025: Fix Unused NoQA Comments (RUF100) [P2]
**Effort:** 15 minutes  
**Dependencies:** Previous auto-fixes  
**Description:** Remove 9 unnecessary noqa comments  
**Steps:**
1. Run: `ruff check . --select RUF100 --fix`
2. Commit: `chore: remove unused noqa comments (RUF100)`

**Verification:** `ruff check . --select RUF100` returns 0 violations

---

### CI/CD Improvements

#### TASK-026: Add Artifact Uploads to quality-gates.yml [P2]
**Effort:** 1 hour  
**Dependencies:** None  
**Description:** Persist quality metrics as CI artifacts  
**Steps:**
1. Edit .github/workflows/quality-gates.yml
2. Add actions/upload-artifact@v3 for:
   - Ruff reports (JSON format)
   - mypy reports
   - pytest coverage reports
3. Set retention-days: 30
4. Test workflow run
5. Commit: `ci(quality): add artifact uploads for ruff, mypy, coverage`

**Verification:** Artifacts visible in GitHub Actions run

---

#### TASK-027: Add Coverage Reporting to CI Workflows [P2]
**Effort:** 1-2 hours  
**Dependencies:** TASK-014  
**Description:** Visualize coverage trends in CI  
**Steps:**
1. Add pytest --cov to CI workflow
2. Upload coverage to codecov.io or similar
3. Add coverage badge to README.md
4. Document coverage policy

**Verification:** Coverage badge shows in README

---

#### TASK-028: Document Required CI Checks in README [P2]
**Effort:** 30 minutes  
**Dependencies:** None  
**Description:** Document the 4 required status checks  
**Steps:**
1. Read release_artifacts/repo_audit_v2/ci/required_checks.txt
2. Document each required check in README.md or docs/development/ci.md
3. Explain what each check validates
4. Document how to run checks locally

**Verification:** CI documentation in docs/development/ci.md

---

### Hygiene - File Management

#### TASK-029: Audit Large Files (>5MB) [P2]
**Effort:** 2 hours  
**Dependencies:** None  
**Description:** Review 19 large files for Git LFS migration  
**Steps:**
1. Read release_artifacts/repo_audit_v2/hygiene/large_files.txt
2. Identify binary files (models, datasets, images)
3. Evaluate if files should be in Git LFS
4. Create migration plan if needed
5. Document large file policy

**Verification:** Large file policy documented in docs/development/

---

#### TASK-030: Document Duplicate __init__.py Pattern [P2]
**Effort:** 15 minutes  
**Dependencies:** None  
**Description:** Document why 481 empty __init__.py files is acceptable  
**Steps:**
1. Add note to docs/development/project_structure.md
2. Explain Python package structure requirements
3. Note: This is standard pattern, not a problem

**Verification:** Documentation added

---

### Security - Bandit Findings

#### TASK-031: Review High-Severity Bandit Issues in Application Code [P2]
**Effort:** 2-3 hours  
**Dependencies:** None  
**Description:** Audit high-severity issues outside .venv  
**Steps:**
1. Run: `bandit -r . -f json -o bandit_app_only.json --exclude='.venv'`
2. Review B602 (shell=True), B324 (weak hashes), B608 (SQL injection)
3. Fix legitimate issues in application code
4. Add # nosec comments with justification for false positives
5. Document findings

**Verification:** <10 high-severity issues in application code

---

#### TASK-032: Centralize External LLM API Access [P2]
**Effort:** 3-4 hours  
**Dependencies:** None  
**Description:** Wrap 10 files with direct API usage in adapter layer  
**Steps:**
1. Read release_artifacts/repo_audit_v2/security/external_api_usage.txt
2. Create lukhas/adapters/llm_adapter.py
3. Implement adapter for OpenAI and Anthropic
4. Migrate direct API calls to adapter
5. Add rate limiting, retries, observability

**Verification:** All external API calls go through adapter

---

#### TASK-033: Audit Environment Variable Access [P2]
**Effort:** 2 hours  
**Dependencies:** None  
**Description:** Review 50 files with env access patterns  
**Steps:**
1. Read release_artifacts/repo_audit_v2/security/env_access_patterns.txt
2. Check for hardcoded secret detection
3. Verify secrets are loaded securely (load_dotenv at entry points only)
4. Document secret management policy

**Verification:** Secret management policy in docs/security/

---

### Documentation

#### TASK-034: Validate Docs Build (Sphinx) [P2]
**Effort:** 1 hour  
**Dependencies:** None  
**Description:** Check if documentation builds without errors  
**Steps:**
1. Check if docs/conf.py exists (Sphinx)
2. Run: `cd docs && make html`
3. Fix any build errors
4. Add docs build to CI
5. Document docs workflow

**Verification:** Docs build successfully in CI

---

#### TASK-035: Check for Broken Links in Documentation [P2]
**Effort:** 1 hour  
**Dependencies:** TASK-034  
**Description:** Validate internal and external links  
**Steps:**
1. Install linkchecker: `pip install linkchecker`
2. Run: `linkchecker docs/_build/html/index.html`
3. Fix broken internal links
4. Document external links that need updates

**Verification:** <5 broken internal links

---

### Governance

#### TASK-036: Audit CODEOWNERS File [P2]
**Effort:** 1 hour  
**Dependencies:** None  
**Description:** Review code ownership assignments  
**Steps:**
1. Check if .github/CODEOWNERS exists
2. Verify ownership patterns match current team structure
3. Update CODEOWNERS for critical paths (lukhas/, matriz/, core/)
4. Test with a PR

**Verification:** CODEOWNERS triggers reviewer assignment on PR

---

#### TASK-037: Document Release Process [P2]
**Effort:** 2 hours  
**Dependencies:** None  
**Description:** Formalize release workflow based on v0.9.1-syntax-zero  
**Steps:**
1. Review release_artifacts/v0.9.1-syntax-zero/
2. Document version numbering scheme
3. Document release checklist
4. Document artifact generation process
5. Add to docs/development/releases.md

**Verification:** Release documentation in docs/

---

## 📦 Packaging & Distribution

#### TASK-038: Validate pyproject.toml Structure [P2]
**Effort:** 1 hour  
**Dependencies:** None  
**Description:** Ensure packaging configuration is complete  
**Steps:**
1. Review pyproject.toml for completeness
2. Check entry points configuration
3. Validate dependencies are properly specified
4. Test: `pip install -e .` in fresh venv
5. Fix any installation issues

**Verification:** Editable install works without errors

---

#### TASK-039: Validate Entry Points [P2]
**Effort:** 1 hour  
**Dependencies:** TASK-038  
**Description:** Test all defined entry points work  
**Steps:**
1. List entry points from pyproject.toml
2. Test each entry point command
3. Fix broken entry points
4. Document entry points in README

**Verification:** All entry points execute successfully

---

#### TASK-040: Package Distribution Test [P2]
**Effort:** 1 hour  
**Dependencies:** TASK-038, TASK-039  
**Description:** Test building and installing distribution package  
**Steps:**
1. Run: `python -m build`
2. Install in fresh venv: `pip install dist/lukhas-*.whl`
3. Test imports and entry points
4. Document build process

**Verification:** Wheel installs and imports work

---

## 🎯 Meta Tasks

#### TASK-041: Track Audit Remediation Progress [Meta]
**Effort:** Ongoing  
**Dependencies:** All tasks  
**Description:** Monitor completion of audit tasks  
**Steps:**
1. Create GitHub issues for each task (or use project board)
2. Link issues to this todo list
3. Update completion status weekly
4. Generate progress report after 2 weeks

**Verification:** Progress dashboard showing completion rate

---

#### TASK-042: Schedule Follow-Up Audit [Meta]
**Effort:** 4 hours (in 30 days)  
**Dependencies:** TASK-001 through TASK-040  
**Description:** Re-run audit to measure improvements  
**Steps:**
1. Wait 30 days from initial audit
2. Re-run audit scripts
3. Compare metrics with baseline
4. Generate improvement report
5. Identify remaining issues

**Verification:** Audit V3 report generated

---

## 📈 Success Metrics

### P0 Completion Criteria (Week 1-2)
- ✅ urllib3 upgraded to 2.5.0
- ✅ Test pass rate >95% (currently 54.8%)
- ✅ E402 violations reduced by 50% in lukhas/, matriz/, core/

### P1 Completion Criteria (Week 3-4)
- ✅ F821 violations reduced by 90%
- ✅ Skipped tests <20 (currently 74)
- ✅ Coverage threshold enforced in CI
- ✅ Type annotations modernized (UP035, UP045)
- ✅ RUF006 violations reduced by 80%

### P2 Completion Criteria (Sprint 2)
- ✅ All auto-fixable style issues resolved
- ✅ CI artifact uploads configured
- ✅ Large file policy documented
- ✅ Bandit high-severity issues reviewed
- ✅ Documentation builds successfully

### Overall Success (30 days)
- 🎯 Repository health score: B- → A (72 → 85+)
- 🎯 Test pass rate: 54.8% → 95%+
- 🎯 Ruff violations: 11,000 → <3,000
- 🎯 Security vulnerabilities: 1 → 0
- 🎯 Code coverage: Current → 75%+

---

**Total Tasks:** 42 microtasks  
**Estimated Total Effort:** 80-120 hours (2-3 weeks with 2-3 developers)  
**Priority Breakdown:** 10 P0, 9 P1, 21 P2, 2 Meta

---

**End of Microtask List**  
*Generated from: release_artifacts/repo_audit_v2/full_repo_audit_v2.md*
