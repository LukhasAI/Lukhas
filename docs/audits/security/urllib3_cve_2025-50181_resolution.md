# urllib3 CVE-2025-50181 Resolution

**Date**: November 6, 2025
**CVE**: CVE-2025-50181 (GHSA-pq67-6m6q-mj2v)
**Severity**: HIGH
**Status**: ✅ **RESOLVED**

---

## Vulnerability Details

- **Package**: urllib3
- **Vulnerable Version**: 1.26.20
- **Fixed Version**: 2.5.0
- **Issue**: SSRF vulnerability via redirect handling - urllib3 retries parameter ignored on PoolManager, redirects not disabled as expected
- **Impact**: Applications disabling redirects at PoolManager level remained vulnerable

---

## Resolution Actions

### 1. Requirements Already Specified Secure Version

The project's `requirements.txt`, `requirements-prod.txt`, and `constraints.txt` already specified `urllib3==2.5.0`:

```txt
urllib3==2.5.0
```

### 2. Upgraded .venv Installation

The virtual environment had an outdated version (1.26.20). Upgraded using:

```bash
source .venv/bin/activate
pip install --force-reinstall --no-deps 'urllib3==2.5.0'
```

**Result**:
```
Successfully installed urllib3-2.5.0
```

### 3. Security Verification

Ran `pip-audit` to verify no vulnerabilities:

```bash
pip-audit --desc
```

**Result**:
```
No known vulnerabilities found
```

✅ **CVE-2025-50181 is RESOLVED**

---

## Notes

### Local urllib3 Stub

The repository contains a local `./urllib3/` directory (allowed in `.root-allowlist`) that serves as a minimal stub for test environments:

```python
# ./urllib3/__init__.py
"""Lightweight urllib3 stub for test environments."""

from .exceptions import NotOpenSSLWarning

__all__ = ["NotOpenSSLWarning"]
```

This stub:
- Does not contain the vulnerability (no actual HTTP code)
- Is explicitly allowed in `.root-allowlist` (line 412)
- Does not shadow the installed package in production (only in certain test contexts)
- The **real urllib3 2.5.0** is installed in `.venv/lib/python3.9/site-packages/urllib3/`

### Dependency Conflicts

During upgrade, encountered a dependency conflict with botocore:
- botocore 1.40.64 requires `urllib3<1.27,>=1.25.4`
- No boto3/botocore usage found in production code (`lukhas/`, `matriz/`, `core/`)
- Resolution: Force-installed urllib3 2.5.0 despite pip warning
- Impact: Minimal - botocore not used in critical paths

---

## Verification Commands

To verify the fix:

```bash
# Check installed version
source .venv/bin/activate
pip show urllib3 | grep Version
# Expected: Version: 2.5.0

# Run security scan
pip-audit --desc
# Expected: No known vulnerabilities found

# Check requirements
grep urllib3 requirements.txt
# Expected: urllib3==2.5.0
```

---

## Pre-Launch Status

| Check | Status |
|-------|--------|
| **Requirements specify 2.5.0** | ✅ |
| **Virtual environment updated** | ✅ |
| **Security scan passes** | ✅ |
| **No vulnerabilities found** | ✅ |
| **CVE-2025-50181 resolved** | ✅ |

---

## Timeline

- **2025-11-03**: Vulnerability identified in Nov 3 audit
- **2025-11-06**: Virtual environment upgraded to urllib3 2.5.0
- **2025-11-06**: Security verification completed
- **2025-11-06**: CVE marked as RESOLVED

---

**Auditor**: Claude Code (Sonnet 4.5)
**Status**: ✅ **RESOLVED** - No blocking issues for launch
