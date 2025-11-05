# LUKHAS Bug Report and Testing Task Allocation

This report outlines the current known bugs in the LUKHAS system and identifies areas that require additional test coverage. The tasks below are designed to be assigned to agents to improve the overall quality and stability of the codebase.

## Known Bugs Requiring Fixes

This section details existing bugs that have been identified and documented. Agents assigned to these tasks should follow the proposed solutions in `tests/KNOWN_ISSUES.md` to resolve them.

### 1. (P1 High Priority) Fix MCP Server Test Fixture Incompatibility (ISSUE-001)

- **Component:** `tests/integration/tools/test_lukhas_mcp_server.py`
- **Status:** Blocked
- **Description:** The MCP Server tests are failing due to a missing `mcp` library and an incompatible test fixture design. This is a critical issue that blocks all integration tests for the MCP server.
- **Task:**
    - Install the `mcp` library as a development dependency.
    - Refactor the tests to use a proper mocking strategy, as outlined in `tests/KNOWN_ISSUES.md`.
    - Ensure all 6 MCP server tests pass without requiring external dependencies.

### 2. (P2 Medium Priority) Correct Consent Expiration Validation Message (ISSUE-002)

- **Component:** `tests/unit/governance/compliance/test_consent_manager.py`
- **Status:** Active
- **Description:** The `test_consent_expiration_and_cleanup` test is failing because the validation logic returns "No active consent found" instead of the expected "Consent has expired."
- **Task:**
    - Update the `validate_consent()` function to prioritize checking for expiration before checking for the existence of active consent.
    - Alternatively, update the test's expectations to match the current behavior, ensuring the validation logic is semantically correct.

### 3. (P2 Medium Priority) Calibrate Constitutional AI Safety Levels (ISSUE-003)

- **Component:** `tests/unit/governance/ethics/test_constitutional_ai.py`
- **Status:** Active
- **Description:** Multiple tests are failing because the Constitutional AI's safety level assessments do not align with the expected outcomes. The current thresholds may be too conservative, or the test data may be unclear.
- **Task:**
    - Review and adjust the safety thresholds to better align with realistic scenarios.
    - Enhance the test data to provide clearer examples of safe and unsafe content.
    - Consider adding a configuration for thresholds to make the system more flexible for testing.

### 4. (P3 Low Priority) Investigate Bio-Symbolic Integration Coherence Calculation (ISSUE-005)

- **Component:** `tests/unit/bio/core/test_bio_symbolic.py`
- **Status:** Active
- **Description:** The `test_integrate` test is failing because the coherence calculation returns `0.75` instead of the expected `1.0`.
- **Task:**
    - Review the coherence calculation algorithm to determine if the current output is correct.
    - If the algorithm is correct, update the test's expectations to match the actual output.
    - Document the coherence calculation methodology to clarify its expected behavior.

## Areas Requiring New Test Coverage

This section identifies components with low test coverage. Agents assigned to these tasks should create new unit and integration tests to improve the robustness of these areas.

### 5. Improve Test Coverage for Governance/Ethics

- **Component:** `governance/ethics/`
- **Current Coverage:** 60%
- **Status:** Needs Work
- **Description:** The Governance and Ethics component has several failing tests and low overall test coverage. This is a critical area that requires a robust test suite to ensure the system's ethical guidelines are enforced correctly.
- **Task:**
    - Write new unit tests for the modules in `governance/ethics/`, focusing on the `ConstitutionalAI` and `EnhancedEthicalGuardian` components.
    - Add integration tests to verify the interaction between the different modules within the governance component.
    - Aim to increase the test coverage for this component to at least 85%.

### 6. Add Integration Tests for Tools

- **Component:** `tools/`
- **Current Coverage:** 14.3%
- **Status:** Blocked
- **Description:** The Tools integration component has critically low test coverage and is currently blocked by the failing MCP server tests. Once the MCP server tests are fixed, this area needs a comprehensive suite of integration tests.
- **Task:**
    - After `ISSUE-001` is resolved, write new integration tests for all tools in the `tools/` directory.
    - Create tests that verify the correct interaction between the tools and other parts of the LUKHAS system.
    - Ensure that the tests cover both successful and unsuccessful execution paths.
