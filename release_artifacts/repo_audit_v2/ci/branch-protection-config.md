# Branch Protection Configuration for Smoke Tests

## Required Status Checks

Add these status checks to your branch protection rules for `main`:

### Via GitHub UI

1. Go to Settings → Branches → Branch protection rules
2. Edit rule for `main` (or create new)
3. Enable "Require status checks to pass before merging"
4. Add these required checks:
   - `Smoke Tests (Quick)`
   - `Smoke Tests (Stability Check - 3x)`

### Via GitHub CLI

```bash
# Add smoke test as required check
gh api \
  --method PUT \
  /repos/:owner/:repo/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["Smoke Tests (Quick)","Smoke Tests (Stability Check - 3x)"]}'
```

### Via Script

Create `.github/scripts/configure-branch-protection.sh`:

```bash
#!/bin/bash
# Configure branch protection for smoke test requirements

OWNER="your-org"
REPO="lukhas"
BRANCH="main"

# Get current protection settings
CURRENT=$(gh api "/repos/$OWNER/$REPO/branches/$BRANCH/protection")

# Add smoke tests to required checks
gh api \
  --method PUT \
  "/repos/$OWNER/$REPO/branches/$BRANCH/protection/required_status_checks" \
  -f strict=true \
  -f contexts[]="Smoke Tests (Quick)" \
  -f contexts[]="Smoke Tests (Stability Check - 3x)"

echo "✅ Branch protection updated for $BRANCH"
```

## Integration with Existing Workflows

If you already have a `ci.yml` workflow, you can:

### Option 1: Add as separate job

```yaml
# Add to existing .github/workflows/ci.yml
jobs:
  # ... existing jobs ...

  smoke:
    name: Smoke Tests (Quick)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: make smoke
```

### Option 2: Call workflow

```yaml
# In .github/workflows/ci.yml
jobs:
  smoke:
    uses: ./.github/workflows/smoke-tests.yml
```

## Testing the Configuration

```bash
# Local test
make smoke

# Test CI job locally with act
act -j smoke

# Create test PR to verify
gh pr create --title "test: verify smoke tests" --body "Testing smoke test CI"
```

## Rollout Strategy

1. **Week 1**: Add workflow, make it informational (don't fail)
2. **Week 2**: Add as required check for `develop` branch
3. **Week 3**: Add as required check for `main` branch
4. **Ongoing**: Monitor flakes, adjust timeouts if needed

## Troubleshooting

### Smoke tests timing out
- Check timeout in workflow (default: 5min)
- Review slow tests with `pytest --durations=10`

### Flaky tests detected
- Run stability check: `for i in {1..10}; do make smoke || break; done`
- Add `@pytest.mark.flaky` to unstable tests
- Increase timeout for specific tests

### Tests passing locally but failing in CI
- Check Python version (CI uses 3.9)
- Verify dependencies in requirements.txt
- Check environment variables (CI_QUALITY_GATES=1)
