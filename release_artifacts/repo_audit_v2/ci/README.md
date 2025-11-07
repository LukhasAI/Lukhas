# CI Smoke Test Integration

This directory contains artifacts for integrating smoke tests into CI/CD pipelines.

## Files

### `smoke-job-snippet.yml`
Complete GitHub Actions workflow for smoke tests. Includes:
- Quick smoke test job (5min timeout, 10 tests)
- Stability check job (runs 3x to detect flakes)
- Artifact upload for test results
- Python 3.9+ support

**Usage**: Copy to `.github/workflows/smoke-tests.yml`

### `branch-protection-config.md`
Guide for making smoke tests a required check before merging to `main`.

## Quick Start

1. **Add workflow**:
   ```bash
   cp release_artifacts/repo_audit_v2/ci/smoke-job-snippet.yml .github/workflows/smoke-tests.yml
   ```

2. **Test locally**:
   ```bash
   make smoke
   ```

3. **Commit and push**:
   ```bash
   git add .github/workflows/smoke-tests.yml
   git commit -m "ci(smoke): add smoke test workflow as quality gate"
   git push
   ```

4. **Configure branch protection** (after workflow runs successfully):
   ```bash
   # Via GitHub UI: Settings → Branches → Add rule
   # Required checks: "Smoke Tests (Quick)"
   ```

## What Gets Tested

Current smoke tests (13 total, ~4-6 seconds):

1. **Core imports** (test_entrypoints.py):
   - Core API imports
   - MATRIZ trace analysis
   - Consciousness pipeline
   - Memory systems
   - GLYPH symbols

2. **Identity & Auth** (test_identity_auth_smoke.py):
   - AdvancedIdentityManager initialization
   - Identity component imports
   - JWT token roundtrip

3. **LLM Adapter Isolation** (test_llm_adapter_scan.py):
   - OpenAI imports isolated to adapters
   - Anthropic imports isolated
   - Bedrock imports isolated
   - Generates security scan artifact

## CI Artifacts

Tests generate artifacts uploaded to GitHub:

- `release_artifacts/repo_audit_v2/tests/` - Test execution logs
- `release_artifacts/repo_audit_v2/security/openai_hits.txt` - LLM import scan

Access artifacts:
- GitHub UI: Actions → Workflow run → Artifacts
- CLI: `gh run download <run-id>`

## Performance Targets

- **Total runtime**: <6 seconds for all smoke tests
- **CI overhead**: <30 seconds (including Python setup)
- **Timeout**: 5 minutes (safety margin)
- **Stability**: 0 flakes in 3 consecutive runs

## Maintenance

### Adding New Smoke Tests

1. Create test in `tests/smoke/test_*.py`
2. Add `@pytest.mark.smoke` decorator
3. Keep runtime <1 second per test
4. Test locally: `make smoke`

Example:
```python
@pytest.mark.smoke
def test_my_feature():
    """Quick check that my feature loads."""
    from my_module import MyFeature
    assert MyFeature is not None
```

### Debugging Failures

```bash
# Local verbose run
python3 -m pytest tests/smoke/ -v -m smoke --tb=short

# Check specific test
python3 -m pytest tests/smoke/test_identity_auth_smoke.py::test_identity_auth_smoke -v

# Run with full output
CI_QUALITY_GATES=1 python3 -m pytest tests/smoke/ -v -m smoke -s
```

## Integration with Other Tools

### Pre-commit hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
make smoke || {
  echo "❌ Smoke tests failed - commit blocked"
  exit 1
}
```

### Local development
```bash
# Add to Makefile
dev: smoke
    uvicorn serve.main:app --reload
```

### Docker
```dockerfile
# In Dockerfile
RUN make smoke || exit 1
```

## Comparison with Other Test Levels

| Test Level | Count | Runtime | When to Run |
|------------|-------|---------|-------------|
| Smoke | 13 | 4-6s | Every commit, pre-merge |
| Unit | 775+ | 30-60s | Every commit |
| Integration | 82 | 2-5min | PR creation |
| E2E | TBD | 10-30min | Nightly, pre-release |

## Rollout Timeline

- ✅ **Week 1** (Current): Workflow created, informational only
- ⏳ **Week 2**: Add as required check for develop
- ⏳ **Week 3**: Add as required check for main
- ⏳ **Week 4**: Enable auto-merge for PRs passing smoke+unit

## Support

- **Documentation**: See project README and `docs/testing/`
- **Issues**: GitHub Issues with `ci` label
- **Questions**: Ask in #engineering Slack channel
