# Smoke Test Documentation

## Overview

The `make smoke` target runs core smoke tests - fast sanity checks that validate critical system functionality.

## Command

```bash
make smoke
```

## Implementation

**Makefile target:**
```makefile
smoke:
	CI_QUALITY_GATES=1 python3 -m pytest -q tests/smoke -m "smoke" --maxfail=1 --disable-warnings
```

**Wrapper script:** `scripts/run_smoke_tests.sh`

## What It Does

1. **Sets CI_QUALITY_GATES=1** - Enables strict quality gate enforcement
2. **Runs pytest** with smoke marker (`-m "smoke"`)
3. **Tests location:** `tests/smoke/` directory
4. **Fail fast:** `--maxfail=1` stops on first failure
5. **Quiet mode:** `-q` for cleaner output
6. **No warnings:** `--disable-warnings` for signal vs noise

## Current Test Count

- **10 smoke tests** (all passing ✅)
- Expected runtime: ~15 seconds

## Smoke Tests Included

The smoke marker (`@pytest.mark.smoke`) identifies critical tests:

- Basic imports and module loading
- Core system initialization
- Essential API endpoints (health, status)
- Critical dependencies availability
- Configuration validation

## Usage

### Direct make command:
```bash
make smoke
```

### Via wrapper script:
```bash
./scripts/run_smoke_tests.sh
```

### Manual pytest:
```bash
CI_QUALITY_GATES=1 python3 -m pytest -q tests/smoke -m "smoke" --maxfail=1 --disable-warnings
```

## Distinction from Full Test Suite

- `make smoke` - 10 tests, ~15 seconds, CI quality gates ✅
- `pytest tests/smoke/` - 290 tests, includes integration tests requiring server
- `pytest -m "smoke"` - Broader scope across entire test suite

## CI Integration

The smoke tests are designed as a **required quality gate** for CI/CD:

- Fast feedback (<30 seconds)
- High signal-to-noise ratio
- Fail fast on critical issues
- No external dependencies required
- Can run in isolation

## Artifacts Created

- `release_artifacts/repo_audit_v2/tests/make_smoke_target.txt` - Raw Makefile target
- `release_artifacts/repo_audit_v2/tests/Makefile_head.txt` - Makefile context
- `release_artifacts/repo_audit_v2/tests/smoke_test_documentation.md` - This file
- `scripts/run_smoke_tests.sh` - Wrapper script

## Next Steps

Per smoke test improvement plan:

1. ✅ Document make smoke target
2. ⏳ Add identity auth smoke test
3. ⏳ Add external-LLM adapter scan
4. ⏳ Create CI smoke job snippet
5. ⏳ Add guardian policy test
6. ⏳ Add memory roundtrip test
7. ⏳ Add external dependency checks
8. ⏳ Add secrets health check
9. ⏳ Add ACL tests
10. ⏳ Add routing negative cases
11. ⏳ Add startup/shutdown tests
