# [D5] Schemathesis Advanced Configuration & Property-Based Testing

**Labels**: `enhancement`, `dast`, `fuzzing`, `testing`
**Priority**: Medium
**Milestone**: Q1 2026
**Estimated Effort**: 2-3 days

---

## Problem Statement

Current Schemathesis fuzzing workflow provides basic property-based testing but lacks:
1. **Stateful Testing**: No session/state management (e.g., create → read → update → delete sequences)
2. **Custom Strategies**: Uses default fuzzing strategies, missing edge cases
3. **Performance Testing**: Only tests correctness, not performance under load
4. **Schema Coverage**: No tracking of which schema paths/parameters have been tested
5. **Failure Reproduction**: Hard to reproduce specific failing test cases

## Proposed Solution

### 1. Stateful Testing with Hypothesis
Enable Schemathesis stateful testing for CRUD workflows:

**Example**:
```python
# tests/dast/test_schemathesis_stateful.py
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize(method="POST", endpoint="/v1/users")
@schema.given_and_then(
    # GIVEN: Create user
    create_user=st.strategy_for_user(),
    # THEN: Read user
    check_user=st.check_user_exists()
)
def test_create_then_read_user(case):
    # POST /v1/users (create)
    response = case.call()
    assert response.status_code == 201
    user_id = response.json()["id"]

    # GET /v1/users/{id} (read)
    read_response = requests.get(f"http://localhost:8000/v1/users/{user_id}")
    assert read_response.status_code == 200
    assert read_response.json()["id"] == user_id
```

### 2. Custom Fuzzing Strategies
Define custom Hypothesis strategies for edge cases:

**Example**:
```python
# tests/dast/schemathesis_strategies.py
from hypothesis import strategies as st

# Custom strategy for valid email addresses (avoid default random strings)
@st.composite
def valid_emails(draw):
    username = draw(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=3, max_size=20))
    domain = draw(st.sampled_from(["example.com", "test.com", "lukhas.ai"]))
    return f"{username}@{domain}"

# Custom strategy for SQL injection payloads (deliberately test for vulnerabilities)
@st.composite
def sql_injection_payloads(draw):
    return draw(st.sampled_from([
        "' OR '1'='1",
        "1; DROP TABLE users--",
        "' UNION SELECT * FROM credentials--",
    ]))

# Register strategies with Schemathesis
schemathesis.register_string_format("email", valid_emails())
```

### 3. Performance Fuzzing
Test performance degradation under fuzzed inputs:

**Example**:
```python
@schema.parametrize()
@settings(max_examples=100, deadline=1000)  # 1000ms deadline per test
def test_performance_under_fuzzing(case):
    response = case.call()
    # Assert response time
    assert response.elapsed.total_seconds() < 1.0, "Response too slow under fuzzing"
```

### 4. Coverage Tracking
Track which schema paths/parameters have been tested:

**Implementation**:
```yaml
# .github/workflows/dast-schemathesis.yml (addition)
- name: Generate coverage report
  run: |
    schemathesis run http://localhost:8000/openapi.json \
      --checks all \
      --workers 4 \
      --report coverage.json

    # Upload coverage report
    python3 scripts/analyze_schema_coverage.py coverage.json

    # Fail if coverage <80%
    COVERAGE=$(jq '.coverage_percent' coverage.json)
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "❌ Schema coverage ${COVERAGE}% is below 80% threshold"
      exit 1
    fi
```

### 5. Failure Reproduction
Save failing test cases for debugging:

**Implementation**:
```python
# tests/dast/test_schemathesis_reproducible.py
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize()
@settings(
    database=ExampleDatabase(".hypothesis/examples"),  # Persist examples
    max_examples=200,
    derandomize=True,  # Reproducible across runs
)
def test_with_reproducibility(case):
    response = case.call()
    case.validate_response(response)
```

**CI Integration**:
```yaml
- name: Upload failing examples
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: hypothesis-failing-examples
    path: .hypothesis/examples/
```

## Acceptance Criteria

- [ ] Stateful testing enabled for at least 3 CRUD workflows (users, models, conversations)
- [ ] Custom strategies defined for: emails, UUIDs, SQL injection payloads, XSS payloads
- [ ] Performance fuzzing enabled with 1000ms deadline
- [ ] Schema coverage tracking implemented (target: 80%+ coverage)
- [ ] Failing test cases automatically saved and uploaded as CI artifacts
- [ ] Documentation: `docs/dast/SCHEMATHESIS_ADVANCED.md`
- [ ] At least 10 new vulnerabilities found and fixed

## Implementation Plan

**Phase 1**: Stateful Testing (1 day)
1. Identify CRUD workflows (users, models, conversations)
2. Implement stateful test cases with Hypothesis
3. Verify state transitions work correctly

**Phase 2**: Custom Strategies (1 day)
1. Define strategies for emails, UUIDs, SQL injection, XSS
2. Register with Schemathesis
3. Run fuzzing with custom strategies, verify edge cases tested

**Phase 3**: Coverage Tracking (0.5 days)
1. Implement `scripts/analyze_schema_coverage.py`
2. Integrate with CI workflow
3. Set 80% coverage threshold

**Phase 4**: Failure Reproduction (0.5 days)
1. Enable Hypothesis database persistence
2. Add artifact upload for failing examples
3. Test reproducing a failure locally from CI artifact

## Testing Strategy

```bash
# Run stateful tests
pytest tests/dast/test_schemathesis_stateful.py -v

# Run with custom strategies
schemathesis run http://localhost:8000/openapi.json \
  --hypothesis-seed=12345 \
  --checks all

# Test failure reproduction
pytest tests/dast/test_schemathesis_reproducible.py \
  --hypothesis-seed=12345 \
  --hypothesis-show-statistics
```

## Monitoring & Alerting

**Metrics**:
- `dast_schemathesis_tests_total{result="passed|failed"}`
- `dast_schema_coverage_percent`
- `dast_fuzzing_duration_seconds`

**Alerts**:
```yaml
- alert: SchemaFuzzingFailureRate
  expr: rate(dast_schemathesis_tests_total{result="failed"}[1h]) > 0.05
  annotations:
    summary: "Schemathesis failure rate >5% (API breaking under fuzzing)"
```

## Benefits

1. **Better Bug Detection**: Stateful testing finds bugs that simple fuzzing misses (e.g., create → delete → read returns 200 instead of 404)
2. **Realistic Inputs**: Custom strategies generate valid-looking data (not random garbage)
3. **Performance Validation**: Catch performance regressions under edge case inputs
4. **Reproducibility**: Easy to debug failing tests (saved examples)
5. **Compliance**: Schema coverage tracking ensures all API paths tested

## Related Issues

- #XXX: OpenAPI schema validation improvements
- #XXX: Contract testing with Pact (complement Schemathesis)
- #XXX: Load testing with Locust (complement Schemathesis performance fuzzing)

## References

- [Schemathesis Stateful Testing](https://schemathesis.readthedocs.io/en/stable/stateful.html)
- [Hypothesis Strategies](https://hypothesis.readthedocs.io/en/latest/data.html)
- [Property-Based Testing in Python](https://hypothesis.works/)
- Gonzo Spec: `docs/gonzo/DAST + NIAS + ABAS + Security Headers .yml` (D5 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @qa-team
