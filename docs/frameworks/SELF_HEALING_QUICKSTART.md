# Self-Healing Test Loop - Quick Start Guide

**Status**: ✅ **DEPLOYED** (commit 3bdfe47ec - 2025-11-10)

## What Is This?

Memory Healix v0.1 - An "agent-ready" self-healing test loop that enables Claude Code, Claude.ai, or any bot to:
1. Run tests and capture failures in structured format
2. Normalize failures to canonical events (NDJSON)
3. Apply policy-as-code guardrails to all PRs
4. Safely propose minimal fixes with automatic rollback

## Quick Commands

```bash
# Bootstrap (first time only)
bash scripts/bootstrap_self_heal.sh

# Run tests with JUnit XML and coverage
make test-heal

# Normalize JUnit failures to events
make heal

# Run smoke tests (canary validation)
make canary

# Validate PR against policy
make policy

# Generate all artifacts at once
make artifacts
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  1. INGEST: pytest --junitxml → reports/junit.xml          │
│  2. NORMALIZE: tools/normalize_junit.py → events.ndjson    │
│  3. TRIAGE: (Future: cluster by signature, risk score)     │
│  4. DECIDE: (Future: playbook fixes or LLM patch plan)     │
│  5. PROPOSE: Open PR with failing test first               │
│  6. GATE: tools/guard_patch.py → enforce policy            │
│  7. LEARN: (Future: record outcome to Memory Healix)       │
└─────────────────────────────────────────────────────────────┘
```

## Policy Guardrails

**Enforced by `tools/guard_patch.py`:**
- ✅ Patch size: ≤40 LOC, ≤2 files
- ✅ Protected files: identity, auth, security modules require two-key approval
- ✅ Risky patterns: No broad `except` clauses
- ✅ Rate limiting: ≤5 auto-PRs/day (future)

**Protected Files** (`.lukhas/protected-files.yml`):
```yaml
- serve/identity_api.py
- serve/middleware/strict_auth.py
- lukhas/identity/**
- core/security/**
```

## Event Format

**Normalized events** (`reports/events.ndjson`):
```json
{
  "ts": "2025-11-10T12:34:56Z",
  "suite": "unit",
  "test_id": "tests.unit.test_foo::test_bar",
  "file": "tests/unit/test_foo.py",
  "time": "0.123",
  "error_class": "AssertionError",
  "message": "assert 1 == 2",
  "stack": "...",
  "repro_cmd": "pytest -q tests/unit/test_foo.py::test_bar",
  "commit": "3bdfe47ec",
  "branch": "main"
}
```

## GitHub Actions Workflow

**Automatic execution on every PR:**
1. Run pytest with JUnit XML and coverage
2. Normalize failures to events.ndjson
3. Run policy guard (fails PR if violations)
4. Upload artifacts (junit.xml, coverage.xml, events.ndjson)

See: [.github/workflows/self_healing.yml](.github/workflows/self_healing.yml)

## Files Created

| File | Purpose |
|------|---------|
| `.lukhas/protected-files.yml` | Define protected surface requiring two-key approval |
| `tools/normalize_junit.py` | Convert JUnit XML → NDJSON events |
| `tools/guard_patch.py` | Enforce PR policy (patch size, protected files, risky patterns) |
| `tools/check_openapi_drift.py` | Detect API schema drift |
| `.github/workflows/self_healing.yml` | CI workflow for test → normalize → guard |
| `scripts/bootstrap_self_heal.sh` | One-command setup |
| `Makefile` | Added targets: test-heal, heal, canary, policy, artifacts |

## Usage Examples

### For Claude Code (CLI)

```bash
# Run full test cycle and check policy
make artifacts && make policy

# If policy passes, create PR
gh pr create --title "fix(tests): resolve 5 failing unit tests" \
  --body "Normalized events attached in reports/events.ndjson"
```

### For Claude.ai (Web)

1. **Copy-paste this prompt:**
   ```
   Read reports/events.ndjson and fix the top 5 most critical test failures.
   For each failure:
   1. Read the failing test file
   2. Understand the assertion
   3. Fix the minimal code needed
   4. Run `make policy` to validate patch size
   5. Create PR with proper commit message
   ```

2. **Claude.ai will:**
   - Parse events.ndjson
   - Fix failures systematically
   - Respect patch size limits
   - Create clean PRs

### For Jules AI

```python
from bridge.llm_wrappers.jules_wrapper import JulesClient

async with JulesClient() as jules:
    session = await jules.create_session(
        prompt="""
        Read reports/events.ndjson and fix failing tests.
        Rules:
        - Max 2 files per PR
        - Max 40 lines per PR
        - Use lukhas.* imports (not candidate.*)
        - Run `make policy` before creating PR
        """,
        source_id="sources/github/LukhasAI/Lukhas",
        automation_mode="AUTO_CREATE_PR"
    )
```

## Next Steps

**Phase 2: Memory Healix Learning**
- [ ] Implement signature clustering (dedupe similar failures)
- [ ] Risk scoring (prioritize critical vs flaky)
- [ ] Playbook learning (record successful fixes)
- [ ] Auto-retry with exponential backoff
- [ ] Canary deployments before merge

**Phase 3: Advanced Guardrails**
- [ ] Two-key approval for protected files
- [ ] Rate limiting (5 PRs/day max)
- [ ] Rollback automation on red canary
- [ ] Integration with MATRIZ consciousness

## Dependencies

**Installed by `scripts/bootstrap_self_heal.sh`:**
- pytest, pytest-xdist, pytest-randomly, pytest-timeout, pytest-rerunfailures
- coverage[toml], mutmut
- ruff, mypy
- Test deps: lz4, fakeredis, aioresponses, mcp, dropbox, slowapi, typing_extensions, freezegun

## Configuration

**Coverage** (`pyproject.toml`):
```toml
[tool.coverage.run]
source = ["lukhas", "matriz", "core"]
branch = true
omit = ["*/tests/*", "*/test_*"]

[tool.coverage.report]
fail_under = 30
show_missing = true
```

**PyTest** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-q --strict-markers --disable-warnings"
asyncio_mode = "auto"
```

## Troubleshooting

**Tests fail during `make test-heal`:**
- Check pytest collection errors: `pytest --collect-only`
- Fix Python 3.9 type annotations: `str | None` → `Optional[str]`
- Install missing deps: `pip install -r requirements.txt`

**Policy guard fails:**
- Check patch size: `git diff --stat origin/main`
- Review protected files: `cat .lukhas/protected-files.yml`
- Remove broad except clauses

**Events not generated:**
- Ensure JUnit XML exists: `ls -lh reports/junit.xml`
- Run normalizer manually: `python tools/normalize_junit.py --in reports/junit.xml --out reports/events.ndjson`

## Related Documentation

- [MISSING_TESTS_DELEGATION_GUIDE.md](MISSING_TESTS_DELEGATION_GUIDE.md) - Test creation batches
- [JULES_API_COMPLETE_REFERENCE.md](JULES_API_COMPLETE_REFERENCE.md) - Jules automation
- [.github/pull_request_template.md](.github/pull_request_template.md) - PR template
- [pyproject.toml](pyproject.toml) - Test configuration

---

**Ready to use!** Run `make artifacts` to start the self-healing loop.
