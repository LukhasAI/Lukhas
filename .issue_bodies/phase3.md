# Phase 3 — Fix Test Assertions & API Compatibility

**Goal:** Fix failing smoke tests after collection errors are resolved.

**Scope:**
- Update tests for API shape changes
- Add mocks for external dependencies
- Create fixture stubs where needed
- Document skipped integration tests

**Process:**
1. Run: `pytest -v -m "smoke" --maxfail=1 --tb=short`
2. For each failure, identify:
   - API shape change → adapt test for both formats
   - External dependency → add mock or mark as integration
   - Fixture issue → create minimal placeholder
3. Submit focused PRs with patches

**Example Fix:**
```python
# Before:
assert "output" in data

# After (backwards-compatible):
assert "choices" in data or "output" in data
```

**Deliverables:**
- Patch PRs for `tests/smoke/*`
- `KNOWN_TEST_ISSUES.md` for skipped tests
- Pass rate metrics after each PR

**Acceptance:**
- Collection errors = 0
- 42/42 smoke tests collect
- >90% pass rate (100% for non-integration)

**Current:** 211 errors, 14/42 collecting
**Target:** 0 errors, 42/42 collecting, >90% passing
