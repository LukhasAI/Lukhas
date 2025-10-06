---
module: reports
title: Test Transparency Card
type: documentation
---
# Test Transparency Card

This document outlines the use of test doubles (mocks, stubs, fakes, etc.) in the LUKHAS AI test suite. The project's testing philosophy emphasizes "reality testing," which minimizes the use of mocks to ensure tests are exercising the system with the highest possible fidelity.

## Guardian Module (`lukhas/governance/guardian`)

-   **Test File:** `tests/governance/test_guardian.py`
-   **Test Doubles Used:** **None.**

### Rationale

The tests for the `GuardianSystemImpl` class were written to directly instantiate and test the real implementation. All objects passed to the system, such as `GovernanceAction`, are real data objects, not mocks. This approach was taken to adhere to the project's "reality testing" principle and to ensure that the logic of the Guardian module, including the bug fix that was implemented, is verified against genuine inputs.
