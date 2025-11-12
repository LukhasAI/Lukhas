# Lane Promotion Checklist

This document outlines the criteria and process for promoting code between development lanes: `candidate` -> `core` -> `lukhas`.

## Promotion Criteria

### 1. Test Coverage
- **Requirement**: Minimum 75% test coverage for the code being promoted.
- **Verification**: Link to the coverage report in the promotion PR.

### 2. Code Review
- **Requirement**: At least one approving review from a core contributor.
- **Verification**: Approval on the promotion PR.

### 3. Security Scan
- **Requirement**: No critical or high-severity vulnerabilities found by the security scanner.
- **Verification**: Link to the security scan results in the promotion PR.

### 4. Performance Validation
- **Requirement**: No performance regressions introduced.
- **Verification**: Link to the performance validation results in the promotion PR.

---

## Promotion PR Template

````markdown
### Promotion Request: [Component Name] to [Target Lane]

**Description:**
[Brief description of the component being promoted and the reason for promotion.]

**Checklist:**
- [ ] Test Coverage (75%+): [Link to report]
- [ ] Code Review: [Link to approving review(s)]
- [ ] Security Scan: [Link to results]
- [ ] Performance Validation: [Link to results]

**Notes:**
[Any additional notes or context for the reviewers.]
````
