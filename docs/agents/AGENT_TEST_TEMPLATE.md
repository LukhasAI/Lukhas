# Agent Test Assignment Template

**Purpose**: Comprehensive guide for AI agents (especially Jules) to write tests for LUKHAS modules

**Usage**: Replace `{TEST_NUMBER}` with actual test task number (e.g., TEST-001, TEST-008)

---

## 🎯 AGENT TASK: Write Tests for {TEST_NUMBER}

### Step 1: Read the Test Assignment Report

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
cat TEST_ASSIGNMENT_REPORT.md
```

**Action**: Find the section for `{TEST_NUMBER}` and read the complete task description

**What to Extract**:
- Module name and files needing tests
- Current coverage vs target coverage
- Priority level (HIGH/MEDIUM/LOW)
- Test strategy and code examples
- Validation commands

---

### Step 2: Read All Context Files

**CRITICAL**: You MUST read these context files before writing any tests:

1. **Master Context**:
   ```bash
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me
   ```

2. **Module-Specific Context** (listed in TEST-XXX "Agent Context" section):
   ```bash
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/{module}/claude.me
   # OR if directory doesn't have claude.me:
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/{parent_module}/claude.me
   ```

3. **Testing Guide**:
   ```bash
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/tests/README.md
   ls /Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/  # See existing test patterns
   ```

4. **Examine Existing Test Examples**:
   ```bash
   # Good test examples to learn from:
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/core/test_agent_tracer.py
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/tests/smoke/test_api_endpoints.py
   cat /Users/agi_dev/LOCAL-REPOS/Lukhas/tests/integration/test_matriz_integration.py
   ```

**Why This Matters**:
- Context files explain the architecture and design decisions
- Prevents writing tests that misunderstand the module's purpose
- Ensures tests align with LUKHAS lane-based architecture
- Helps you write meaningful test names and assertions

---

### Step 3: Read the Module Implementation

**Action**: Read all source files that need tests

```bash
# For each file listed in TEST-XXX "Files to Test":
cat /Users/agi_dev/LOCAL-REPOS/Lukhas/{module}/{filename}.py

# Example for TEST-001 (Core Orchestration):
cat /Users/agi_dev/LOCAL-REPOS/Lukhas/core/orchestration/orchestrator.py
cat /Users/agi_dev/LOCAL-REPOS/Lukhas/core/orchestration/agent.py
# ... etc for all 11 files
```

**What to Identify**:
- Public functions and classes to test
- Function signatures (parameters, return types)
- Error conditions and edge cases
- Dependencies on other modules
- Configuration requirements
- External services (need mocking)

**Pro Tip**: Run the code if possible to understand behavior:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 -c "from core.orchestration.orchestrator import Orchestrator; print(dir(Orchestrator()))"
```

---

### Step 4: Check Current Test Coverage

**Action**: See what tests already exist and identify gaps

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Check if tests directory exists for this module
ls tests/unit/{module}/

# If tests exist, read them:
cat tests/unit/{module}/test_*.py

# Check current coverage:
pytest tests/unit/{module}/ -v --cov={module} --cov-report=term-missing

# If no tests exist, you'll create from scratch
```

**Coverage Analysis**:
- Lines not covered (shown in `--cov-report=term-missing`)
- Functions without any tests
- Error paths not tested
- Edge cases missing

---

### Step 5: Write Comprehensive Tests

**Test File Naming Convention**:
- Unit tests: `tests/unit/{module}/test_{source_filename}.py`
- Integration tests: `tests/integration/{module}/test_{feature}_integration.py`
- Smoke tests: `tests/smoke/test_{feature}.py`

**Required Test Categories** (for EACH function/class):

1. **Initialization Tests**:
```python
def test_{class}_initialization():
    """Test {Class} initializes with default config"""
    obj = ClassName()
    assert obj is not None
    assert obj.attribute is not None
```

2. **Happy Path Tests**:
```python
def test_{function}_with_valid_input():
    """Test {function} returns expected result with valid input"""
    result = function(valid_input)
    assert result == expected_output
```

3. **Error Handling Tests**:
```python
def test_{function}_raises_error_on_invalid_input():
    """Test {function} raises ValueError for invalid input"""
    with pytest.raises(ValueError, match="Invalid input"):
        function(invalid_input)
```

4. **Edge Case Tests**:
```python
def test_{function}_handles_empty_input():
    """Test {function} handles empty input gracefully"""
    result = function([])
    assert result == default_value

def test_{function}_handles_null_input():
    """Test {function} handles None input"""
    result = function(None)
    assert result is None  # or raises exception
```

5. **Integration Tests** (if applicable):
```python
def test_{module}_integrates_with_{other_module}():
    """Test {module} works correctly with {other_module}"""
    # Setup both modules
    # Test interaction
    # Verify correct behavior
```

**Mocking External Dependencies**:
```python
from unittest.mock import patch, MagicMock

@patch('module.external_service.api_call')
def test_{function}_with_mocked_external(mock_api):
    """Test {function} with mocked external API"""
    mock_api.return_value = {"status": "success"}
    result = function()
    assert result is not None
    mock_api.assert_called_once()
```

**Test Structure (AAA Pattern)**:
```python
def test_{feature}_{scenario}():
    """Test {clear description of what is being tested}"""
    # Arrange - Setup
    test_data = create_test_data()
    obj = initialize_object()

    # Act - Execute
    result = obj.method(test_data)

    # Assert - Verify
    assert result.status == "success"
    assert result.data is not None
    assert no_side_effects_occurred()
```

**Coverage Target**:
- Aim for 75%+ statement coverage
- 100% of public methods must have at least one test
- All error paths must be tested
- All edge cases documented in code must be tested

---

### Step 6: Validate Your Tests

**Action**: Run tests and verify coverage improvements

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Run your new tests
pytest tests/unit/{module}/ -v

# Check coverage
pytest tests/unit/{module}/ -v --cov={module} --cov-report=term-missing

# Verify no new collection errors
pytest --co -q 2>&1 | grep -c "ERROR"  # Should be 0 or reduced from 223

# Run smoke tests to ensure no regressions
make smoke

# Run full test suite (if time permits)
make test
```

**Success Criteria**:
- ✅ Coverage increased from X% to Y% (target met)
- ✅ All new tests passing
- ✅ No new collection errors introduced
- ✅ No regressions in existing tests
- ✅ Code coverage report shows most lines covered

**If Tests Fail**:
- Read error messages carefully
- Check if you misunderstood the module's behavior
- Verify imports are correct
- Check if external dependencies need mocking
- Re-read context files for architectural insights

---

### Step 7: Commit with T4 Standards

**Action**: Commit your tests following LUKHAS T4 commit message format

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git add tests/unit/{module}/
git commit -m "$(cat <<'EOF'
test({module}): add comprehensive test coverage for {component}

Problem:
- {module} had {X}% coverage (target: {Y}%)
- {N} critical functions untested
- Missing edge case validation
- {specific_issue} not validated

Solution:
- Created tests/unit/{module}/test_{file}.py ({N} lines)
- Added {N} test cases covering:
  - Initialization and configuration ({N} tests)
  - Happy path execution ({N} tests)
  - Error handling ({N} tests)
  - Edge cases ({N} tests)
  - Integration scenarios ({N} tests)
- Mocked external dependencies ({list})
- Followed AAA test pattern for readability

Impact:
- Coverage: {X}% → {Y}% (+{improvement}%)
- {N} tests passing (0 failures)
- All critical paths validated
- {feature} now production-ready
- Collection errors: {before} → {after}

Validation:
```bash
pytest tests/unit/{module}/ -v --cov={module}
# Coverage: {Y}%
# Tests: {N} passed
```

Closes: {TEST_NUMBER}

🤖 Generated by Jules AI

Co-Authored-By: Jules <noreply@google.com>
EOF
)"
```

**Commit Message Guidelines**:
- **Type**: `test` (for test additions)
- **Scope**: Module name (e.g., `orchestration`, `identity`, `memory`)
- **Subject**: Brief description (≤72 chars)
- **Body**: Problem/Solution/Impact bullets
- **Trailers**: `Closes: TEST-XXX`
- **Tone**: Humble, academic, factual (no hype words)

---

### Step 8: Report Completion

**Action**: Report back to the requester with results

**Report Template**:

```
✅ Completed {TEST_NUMBER}: Write tests for {module}

**Summary**:
- Created {N} test files with {N} total test cases
- Coverage improved: {X}% → {Y}% (+{improvement}%)
- All tests passing: {N}/{N}
- No new collection errors introduced

**Files Created**:
- tests/unit/{module}/test_{file1}.py ({N} tests)
- tests/unit/{module}/test_{file2}.py ({N} tests)
- [list all new test files]

**Test Breakdown**:
- Initialization tests: {N}
- Happy path tests: {N}
- Error handling tests: {N}
- Edge case tests: {N}
- Integration tests: {N}

**Coverage Details**:
- {module}/file1.py: {X}% → {Y}%
- {module}/file2.py: {X}% → {Y}%
- Overall module: {X}% → {Y}%

**Validation Commands**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
pytest tests/unit/{module}/ -v --cov={module}
```

**Next Steps**:
- Ready for code review
- Can proceed to {NEXT_TEST_NUMBER}
- Recommend testing {related_module} next for integration validation
```

---

## 📋 Quick Reference Checklist

Before committing, verify you've completed:

- [ ] Read TEST_ASSIGNMENT_REPORT.md section for {TEST_NUMBER}
- [ ] Read all context files (master + module-specific)
- [ ] Read existing test examples to learn patterns
- [ ] Read all source files needing tests
- [ ] Checked current coverage baseline
- [ ] Written initialization tests for all classes
- [ ] Written happy path tests for all functions
- [ ] Written error handling tests for all error paths
- [ ] Written edge case tests (empty, null, boundary values)
- [ ] Written integration tests (if applicable)
- [ ] Mocked all external dependencies
- [ ] Followed AAA test pattern (Arrange-Act-Assert)
- [ ] All tests passing locally
- [ ] Coverage target achieved (typically 75%+)
- [ ] No new collection errors introduced
- [ ] No regressions in existing tests
- [ ] Committed with T4 format
- [ ] Reported completion with metrics

---

## 🔧 Troubleshooting Common Issues

### Issue: ModuleNotFoundError in tests

**Solution**:
```python
# Ensure imports use correct paths
# WRONG:
from orchestrator import Orchestrator

# RIGHT:
from core.orchestration.orchestrator import Orchestrator
```

### Issue: Tests fail due to missing dependencies

**Solution**:
```python
# Mock external dependencies
from unittest.mock import patch

@patch('external.dependency')
def test_with_mock(mock_dep):
    mock_dep.return_value = test_data
```

### Issue: Coverage not increasing

**Solution**:
- Check `--cov-report=term-missing` output
- Add tests for uncovered lines
- Ensure tests actually execute the code paths
- Check if code is unreachable (dead code)

### Issue: RecursionError in tests

**Solution**:
- Check for circular imports
- Ensure __init__.py files are correct
- Mock recursive dependencies

---

## 📚 Additional Resources

- **LUKHAS Testing Guide**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/README.md`
- **pytest Documentation**: https://docs.pytest.org/
- **Coverage.py Guide**: https://coverage.readthedocs.io/
- **Mocking Guide**: https://docs.python.org/3/library/unittest.mock.html
- **TEST_ASSIGNMENT_REPORT.md**: Complete list of all test tasks
- **bug_report.md**: Related functionality issues to validate

---

**Template Version**: 1.0
**Last Updated**: 2025-11-06
**For**: Jules AI Agent (and other test-writing agents)
**Location**: `/Users/agi_dev/LOCAL-REPOS/Lukhas-test-audit/AGENT_TEST_TEMPLATE.md`
