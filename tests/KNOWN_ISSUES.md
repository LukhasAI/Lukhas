---
status: wip
type: documentation
---
# Test Suite Known Issues

> Last Updated: 2024-09-14
> Status: 62/69 tests passing (89.8% pass rate)

## 🔴 Critical Issues (P0)
*None currently - all critical paths functional*

## 🟠 High Priority Issues (P1)

### ISSUE-001: MCP Server Test Fixture Incompatibility
**Component:** `tests/integration/tools/test_lukhas_mcp_server.py`  
**Status:** 🔴 Blocked  
**Assignee:** Unassigned  
**Labels:** `integration`, `external-dependency`

**Description:**  
MCP Server tests fail due to missing MCP library and fixture design issues.

**Error:**
```
TypeError: __init__() got an unexpected keyword argument 'client_factory'
```

**Root Cause:**  
- MCP library not installed (`pip install mcp` required)
- Test assumes injectable client factory pattern not supported by current implementation

**Proposed Solution:**
1. Install MCP library as dev dependency
2. Refactor tests to use proper mocking strategy
3. Consider implementing dependency injection pattern in LUKHASMCPServer

**Acceptance Criteria:**
- [ ] All 6 MCP server tests pass
- [ ] Tests run without external dependencies
- [ ] Mock strategy documented

---

## 🟡 Medium Priority Issues (P2)

### ISSUE-002: Consent Expiration Validation Message Mismatch
**Component:** `tests/unit/governance/compliance/test_consent_manager.py::test_consent_expiration_and_cleanup`  
**Status:** 🟡 Active  
**Assignee:** Unassigned  
**Labels:** `unit-test`, `validation`, `gdpr`

**Description:**  
Test expects "Consent has expired" but receives "No active consent found".

**Error:**
```python
AssertionError: assert 'No active consent found' == 'Consent has expired'
```

**Root Cause:**  
Validation logic checks for active consent before checking expiration status.

**Proposed Solution:**
1. Update `validate_consent()` to check expiration before existence
2. OR update test expectations to match current behavior
3. Add explicit expiration state tracking

**Acceptance Criteria:**
- [ ] Test passes consistently
- [ ] Error messages are semantically correct
- [ ] GDPR compliance maintained

---

### ISSUE-003: Constitutional AI Safety Level Calibration
**Component:** `tests/unit/governance/ethics/test_constitutional_ai.py`  
**Status:** 🟡 Active  
**Assignee:** Unassigned  
**Labels:** `ethics`, `ai-safety`, `calibration`

**Description:**  
Multiple tests fail due to safety level assessment not matching expectations.

**Failures:**
- `test_assess_safe_content` - Returns violations for safe content
- `test_assess_privacy_violation` - Returns SAFE instead of DANGER/WARNING
- `test_drift_score_calculation` - Drift not triggering level change

**Root Cause:**  
Constitutional AI thresholds may be overly conservative or test data insufficiently clear.

**Proposed Solution:**
1. Review and calibrate safety thresholds
2. Enhance test data clarity
3. Add threshold configuration for testing
4. Document expected behavior for edge cases

**Acceptance Criteria:**
- [ ] Safety assessments align with human intuition
- [ ] Clear documentation of threshold rationale
- [ ] Test data represents realistic scenarios

---

### ISSUE-004: Enhanced Ethical Guardian Missing Context Policy
**Component:** `tests/unit/governance/ethics/test_enhanced_ethical_guardian.py`  
**Status:** ✅ Resolved (temporary fix)  
**Assignee:** Completed  
**Labels:** `configuration`, `ethics`

**Description:**  
Tests fail due to missing context policy configuration.

**Temporary Fix Applied:**
Created `config/ethics/context_policy.yaml` with basic structure.

**Follow-up Needed:**
1. Validate policy completeness with product team
2. Add schema validation
3. Create policy management interface

**Acceptance Criteria:**
- [x] Tests run without file errors
- [ ] Policy validated by governance team
- [ ] Schema validation implemented

---

## 🟢 Low Priority Issues (P3)

### ISSUE-005: Bio-Symbolic Integration Coherence Calculation
**Component:** `tests/unit/bio/core/test_bio_symbolic.py::test_integrate`  
**Status:** 🟢 Low Priority  
**Assignee:** Unassigned  
**Labels:** `unit-test`, `bio-quantum`, `calculation`

**Description:**  
Integration coherence calculation returns 0.75 instead of expected 1.0.

**Error:**
```python
assert 0.75 == 1.0 ± 1.0e-06
```

**Root Cause:**  
Coherence algorithm may have different weighting than test expects.

**Proposed Solution:**
1. Review coherence calculation algorithm
2. Update test expectations if algorithm is correct
3. Document coherence calculation methodology

**Acceptance Criteria:**
- [ ] Coherence calculation documented
- [ ] Test reflects actual requirements
- [ ] Edge cases handled

---

### ISSUE-006: Test Return Value Warning
**Component:** `tests/integration/tools/test_dependency_hasher.py`  
**Status:** ✅ Resolved  
**Assignee:** Completed  
**Labels:** `test-pattern`, `pytest`

**Description:**  
Test was returning boolean instead of using assertions.

**Fix Applied:**
Replaced `return True/False` with proper assertions.

---

## 📊 Summary Statistics

| Priority | Total | Resolved | Active | Blocked |
|----------|-------|----------|--------|---------|
| P0       | 0     | 0        | 0      | 0       |
| P1       | 1     | 0        | 0      | 1       |
| P2       | 4     | 1        | 3      | 0       |
| P3       | 2     | 1        | 1      | 0       |
| **Total**| **7** | **2**    | **4**  | **1**   |

## 🎯 Next Actions

1. **Immediate:** Install MCP library and unblock ISSUE-001
2. **This Sprint:** Resolve P2 issues (002, 003)
3. **Next Sprint:** Address P3 issues and enhance test coverage
4. **Ongoing:** Document test patterns and best practices

## 🏷️ Labels Key

- `unit-test`: Unit test issue
- `integration`: Integration test issue  
- `external-dependency`: Requires external library/service
- `validation`: Validation logic issue
- `configuration`: Configuration file issue
- `ai-safety`: AI safety and ethics related
- `gdpr`: GDPR compliance related
- `bio-quantum`: Bio-quantum systems
- `test-pattern`: Test implementation pattern issue
- `calibration`: Threshold/parameter calibration needed

## 👥 Assignment Guide

To claim an issue:
1. Update Assignee field with your identifier
2. Change Status to 🟡 Active
3. Add estimated completion date
4. Create branch: `fix/ISSUE-XXX-brief-description`

## 📝 Resolution Process

1. Fix issue in feature branch
2. Ensure all related tests pass
3. Update this document with resolution
4. Submit PR with reference: "Fixes ISSUE-XXX"
5. Update Status to ✅ Resolved after merge